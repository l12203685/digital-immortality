"""
Always-on trading engine — persistent process independent from the daemon.

Polls BTC/USDT OHLCV, runs all NAMED_STRATEGIES, detects regime,
logs ticks, enforces kill conditions, posts Discord on signal changes.

Usage:
    python -m trading.engine              # paper mode (default)
    python -m trading.engine --live       # real Spot orders
    python -m trading.engine --status     # print status and exit
    python -m trading.engine --interval 30
"""
import argparse, json, logging, os, signal, sys, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger("trading.engine")
REPO = Path(__file__).resolve().parent.parent
RESULTS = REPO / "results"
LOG_PATH = RESULTS / "trading_engine_log.jsonl"
STATUS_PATH = RESULTS / "trading_engine_status.json"
CREDS_PATH = Path.home() / ".claude" / "credentials" / "binance_api.json"
DISCORD_WEBHOOK = ("https://discord.com/api/webhooks/1491644107788128439/"
                   "Ndafv8puWZKaqHYcp-icHRRWealC0TfrZxO_k9DR1Dj2ANbFx5eyI3Ynvs8M_XO7y3jj")

def load_credentials() -> Dict[str, str]:
    if CREDS_PATH.exists():
        creds = json.loads(CREDS_PATH.read_text())
        return {"api_key": creds.get("api_key", ""), "secret": creds.get("secret_key", "")}
    return {"api_key": os.environ.get("BINANCE_API_KEY", ""),
            "secret": os.environ.get("BINANCE_API_SECRET", "")}

def make_exchange(creds: Dict[str, str]):
    import ccxt
    return ccxt.binance({"apiKey": creds["api_key"], "secret": creds["secret"],
                         "enableRateLimit": True, "options": {"defaultType": "spot"}})

def fetch_bars(exchange, symbol: str = "BTC/USDT", tf: str = "1d", limit: int = 100) -> List[Dict]:
    return [{"open": c[1], "high": c[2], "low": c[3], "close": c[4],
             "volume": c[5], "open_time": c[0]}
            for c in exchange.fetch_ohlcv(symbol, tf, limit=limit)]

def post_discord(msg: str) -> None:
    try:
        import requests
        requests.post(DISCORD_WEBHOOK, json={"content": msg, "username": "TradingEngine"}, timeout=10)
    except Exception:
        logger.debug("Discord post failed (non-fatal)")

def append_log(entry: Dict) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

def write_status(status: Dict) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    STATUS_PATH.write_text(json.dumps(status, indent=2))

def execute_order(exchange, side: str, symbol: str = "BTC/USDT",
                  usdt_amount: float = 100.0, live: bool = False) -> Dict:
    if not live:
        return {"paper": True, "side": side, "amount_usdt": usdt_amount}
    price = exchange.fetch_ticker(symbol)["last"]
    qty = usdt_amount / price
    market = exchange.market(symbol)
    qty = round(qty, market.get("precision", {}).get("amount", 6))
    return exchange.create_market_order(symbol, side, qty) if qty > 0 else {}


class KillMonitor:
    """Per-strategy MDD/WR/PF kill conditions."""
    def __init__(self, max_dd: float = 20.0, min_wr: float = 0.30,
                 min_pf: float = 0.8, window: int = 50):
        self.max_dd, self.min_wr, self.min_pf, self.window = max_dd, min_wr, min_pf, window
        self._pnl: Dict[str, List[float]] = {}

    def record(self, name: str, pnl_pct: float) -> None:
        self._pnl.setdefault(name, []).append(pnl_pct)

    def check(self, name: str) -> Optional[str]:
        trades = self._pnl.get(name, [])
        if len(trades) < self.window:
            return None
        recent = trades[-self.window:]
        # MDD
        cum, peak, mdd = 0.0, 0.0, 0.0
        for p in recent:
            cum += p; peak = max(peak, cum); mdd = max(mdd, peak - cum)
        if mdd > self.max_dd:
            return f"MDD {mdd:.1f}% > {self.max_dd}%"
        # Win rate
        wr = sum(1 for p in recent if p > 0) / len(recent)
        if wr < self.min_wr:
            return f"WR {wr:.1%} < {self.min_wr:.0%}"
        # Profit factor
        gw = sum(p for p in recent if p > 0)
        gl = abs(sum(p for p in recent if p < 0))
        pf = gw / gl if gl > 0 else 999.0
        if pf < self.min_pf:
            return f"PF {pf:.2f} < {self.min_pf}"
        return None


class TradingEngine:
    """Persistent polling engine for all NAMED_STRATEGIES."""
    def __init__(self, exchange, live: bool = False, interval: int = 60):
        self.exchange, self.live, self.interval = exchange, live, interval
        self.running = False
        from trading.strategies import NAMED_STRATEGIES
        from trading.portfolio import RegimeDetector
        self.strategies = dict(NAMED_STRATEGIES)
        self.regime_detector = RegimeDetector()
        self.prev_signals: Dict[str, int] = {}
        self.disabled: Dict[str, str] = {}
        self.pnl_tracker: Dict[str, float] = {}
        self.prev_prices: Dict[str, float] = {}
        self.total_pnl, self.tick_count = 0.0, 0
        self.kill_monitor = KillMonitor()

    def tick(self) -> None:
        utc_now = datetime.now(timezone.utc).isoformat()
        self.tick_count += 1
        try:
            bars = fetch_bars(self.exchange)
        except Exception as e:
            logger.error("Fetch bars failed: %s", e); return
        if not bars:
            return
        price = bars[-1]["close"]
        regime = self.regime_detector.detect(bars)
        signals_summary: Dict[str, int] = {}
        discord_msgs: List[str] = []

        for name, strategy in self.strategies.items():
            if name in self.disabled:
                continue
            try:
                sig = strategy(bars)
            except Exception as e:
                logger.warning("Strategy %s error: %s", name, e); sig = 0

            prev = self.prev_signals.get(name, 0)
            action, pnl_pct = "HOLD", 0.0
            prev_price = self.prev_prices.get(name, 0.0)
            if prev != 0 and prev_price > 0:
                pnl_pct = prev * (price - prev_price) / prev_price * 100
                self.pnl_tracker[name] = self.pnl_tracker.get(name, 0.0) + pnl_pct
                self.total_pnl += pnl_pct
                self.kill_monitor.record(name, pnl_pct)

            if sig != prev:
                action = {1: "OPEN_LONG", -1: "OPEN_SHORT", 0: "CLOSE"}[sig]
                if prev != 0:
                    execute_order(self.exchange, "sell" if prev == 1 else "buy", live=self.live)
                if sig != 0:
                    execute_order(self.exchange, "buy" if sig == 1 else "sell", live=self.live)
                self.prev_signals[name] = sig
                discord_msgs.append(f"{name}: {['FLAT','LONG'][sig] if sig >= 0 else 'SHORT'} @ ${price:,.0f}")

            self.prev_prices[name] = price
            signals_summary[name] = sig

            kill = self.kill_monitor.check(name)
            if kill:
                self.disabled[name] = kill
                logger.warning("KILL %s: %s", name, kill)
                discord_msgs.append(f"KILLED {name}: {kill}")

            append_log({"ts": utc_now, "tick": self.tick_count, "strategy": name,
                        "signal": sig, "prev_signal": prev, "price": price,
                        "regime": regime, "action": action,
                        "pnl_pct": round(pnl_pct, 4),
                        "cum_pnl": round(self.pnl_tracker.get(name, 0.0), 4)})

        active = [n for n in self.strategies if n not in self.disabled]
        write_status({"last_tick": utc_now, "tick_count": self.tick_count,
                      "active_strategies": len(active), "disabled": dict(self.disabled),
                      "total_pnl_pct": round(self.total_pnl, 4), "price": price,
                      "regime": regime, "signals": signals_summary,
                      "mode": "LIVE" if self.live else "PAPER"})

        if discord_msgs:
            header = f"[{'LIVE' if self.live else 'PAPER'}] {regime.upper()} | BTC ${price:,.0f}"
            post_discord(header + "\n" + "\n".join(discord_msgs))
        logger.info("tick=%d price=%.0f regime=%s active=%d", self.tick_count, price, regime, len(active))

    def run(self) -> None:
        self.running = True
        def _stop(signum, frame):
            logger.info("Shutdown signal received"); self.running = False
        signal.signal(signal.SIGINT, _stop)
        signal.signal(signal.SIGTERM, _stop)
        mode = "LIVE" if self.live else "PAPER"
        logger.info("Engine started: %s, %d strategies, interval=%ds", mode, len(self.strategies), self.interval)
        post_discord(f"Engine started: {mode}, {len(self.strategies)} strategies, interval={self.interval}s")
        while self.running:
            try:
                self.tick()
            except Exception as e:
                logger.error("Tick error: %s", e, exc_info=True)
            if self.running:
                time.sleep(self.interval)
        logger.info("Engine stopped after %d ticks", self.tick_count)
        post_discord(f"Engine stopped after {self.tick_count} ticks")


def print_status() -> None:
    if not STATUS_PATH.exists():
        print("No status file found. Engine may not have run yet."); return
    print(json.dumps(json.loads(STATUS_PATH.read_text()), indent=2))

def main() -> None:
    p = argparse.ArgumentParser(description="Always-on BTC trading engine")
    p.add_argument("--live", action="store_true", help="Place real Spot orders")
    p.add_argument("--paper", action="store_true", default=True, help="Paper mode (default)")
    p.add_argument("--interval", type=int, default=60, help="Seconds between ticks (default 60)")
    p.add_argument("--status", action="store_true", help="Print current status and exit")
    args = p.parse_args()
    if args.status:
        print_status(); return
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    creds = load_credentials()
    if args.live and not (creds["api_key"] and creds["secret"]):
        logger.error("Live mode requires API credentials"); sys.exit(1)
    exchange = make_exchange(creds)
    TradingEngine(exchange, live=args.live, interval=args.interval).run()

if __name__ == "__main__":
    main()
