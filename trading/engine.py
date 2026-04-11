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
EXECUTION_RULES_PATH = RESULTS / "execution_rules.json"
KILLS_LOG_PATH = RESULTS / "kill_lessons.jsonl"
DISABLED_PATH = RESULTS / "disabled_strategies.json"
LIVE_GATE_PATH = RESULTS / "live_mode_gate.json"
CREDS_PATH = Path.home() / ".claude" / "credentials" / "binance_api.json"
DISCORD_WEBHOOK = ("https://discord.com/api/webhooks/1491644107788128439/"
                   "Ndafv8puWZKaqHYcp-icHRRWealC0TfrZxO_k9DR1Dj2ANbFx5eyI3Ynvs8M_XO7y3jj")

# SOP#118 ReactivationGate constants
REACTIVATION_COOLING_TICKS = 50
REACTIVATION_FORWARD_WINDOW = 50
REACTIVATION_PF_THRESHOLD = 1.2
REACTIVATION_REENTRY_SIZE = 0.5

# Mainnet safety (first 30 days after live activation)
LIVE_FIRST_N_DAYS_SIZE_CAP_USDT = 100.0
LIVE_FIRST_N_DAYS = 30
LIVE_HUMAN_CONFIRM_HOURS = 72

DEFAULT_EXECUTION_RULES: Dict = {
    "kill_max_dd": 20.0, "kill_min_wr": 0.30, "kill_min_pf": 0.8,
    "kill_window": 50, "kill_window_floor": 20, "kill_window_ceiling": 50,
    "kill_window_recovery_ticks": 100, "kill_count": 0,
    "evolved_at": None, "last_kill": None, "last_recovery": None,
}


def load_execution_rules() -> Dict:
    """L3 Evolve: load mutable execution rules (evolves after each kill)."""
    if EXECUTION_RULES_PATH.exists():
        return json.loads(EXECUTION_RULES_PATH.read_text())
    return dict(DEFAULT_EXECUTION_RULES)


def evolve_execution_rules(killed_strategy: str, kill_reason: str,
                            current_rules: Dict) -> Dict:
    """L3 Evolve: modify execution rules in response to a kill event.

    Each kill tightens the feedback loop (kill_window -5, floor=kill_window_floor) so
    future strategies receive corrective action faster.
    """
    new_rules = dict(current_rules)
    floor = new_rules.get("kill_window_floor", 20)
    new_rules["kill_count"] = new_rules.get("kill_count", 0) + 1
    new_rules["evolved_at"] = datetime.now(timezone.utc).isoformat()
    new_rules["last_kill"] = {"strategy": killed_strategy, "reason": kill_reason,
                              "ts": new_rules["evolved_at"]}
    new_rules["kill_window"] = max(floor, new_rules.get("kill_window", 50) - 5)
    RESULTS.mkdir(parents=True, exist_ok=True)
    EXECUTION_RULES_PATH.write_text(json.dumps(new_rules, indent=2))
    return new_rules


def recover_kill_window(current_rules: Dict, clean_tick_count: int) -> Dict:
    """SOP#118: loosen kill_window after sustained clean performance.

    After `kill_window_recovery_ticks` consecutive ticks with no kill events,
    loosen kill_window by +5 (cap = kill_window_ceiling). Prevents the
    kill_window death-spiral where every kill tightens with no recovery path.
    """
    new_rules = dict(current_rules)
    recovery_ticks = new_rules.get("kill_window_recovery_ticks", 100)
    if clean_tick_count < recovery_ticks:
        return new_rules
    ceiling = new_rules.get("kill_window_ceiling", 50)
    current_window = new_rules.get("kill_window", 50)
    if current_window >= ceiling:
        return new_rules
    new_rules["kill_window"] = min(ceiling, current_window + 5)
    new_rules["last_recovery"] = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "from_window": current_window, "to_window": new_rules["kill_window"],
        "clean_ticks": clean_tick_count,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    EXECUTION_RULES_PATH.write_text(json.dumps(new_rules, indent=2))
    return new_rules


def load_disabled() -> Dict[str, Dict]:
    """Persist disabled strategies across engine restarts (SOP#118 fix).

    Prior behavior: self.disabled was in-memory only, so process restart
    wiped kill memory and re-armed strategies without forward-walk gate.
    """
    if DISABLED_PATH.exists():
        try:
            return json.loads(DISABLED_PATH.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_disabled(disabled: Dict[str, Dict]) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    DISABLED_PATH.write_text(json.dumps(disabled, indent=2))


def log_kill_lesson(killed_strategy: str, kill_reason: str, tick: int,
                    price: float, regime: str, cum_pnl: float,
                    new_window: int) -> None:
    """L3 Evolve: append durable kill lesson with rule change recorded."""
    lesson = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tick": tick, "strategy": killed_strategy, "kill_reason": kill_reason,
        "cum_pnl": round(cum_pnl, 4), "price_at_kill": price,
        "regime_at_kill": regime,
        "rule_change": f"kill_window reduced to {new_window} (faster feedback loop)",
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    with open(KILLS_LOG_PATH, "a") as f:
        f.write(json.dumps(lesson) + "\n")

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

def load_live_gate() -> Dict:
    """SOP#118: live mode safety gate state.

    Tracks activation timestamp so first-72h human confirmation and
    first-30d size cap can be enforced in execute_order().
    """
    if LIVE_GATE_PATH.exists():
        try:
            return json.loads(LIVE_GATE_PATH.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_live_gate(gate: Dict) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    LIVE_GATE_PATH.write_text(json.dumps(gate, indent=2))


def execute_order(exchange, side: str, symbol: str = "BTC/USDT",
                  usdt_amount: float = 100.0, live: bool = False,
                  size_scale: float = 1.0) -> Dict:
    """Place an order. Live mode is gated by SOP#118 live safety protocol.

    size_scale < 1.0 applies a size reduction (used by ReactivationGate
    for 50% re-entry after forward-walk PF confirmation).
    """
    effective_usdt = usdt_amount * size_scale
    if not live:
        return {"paper": True, "side": side, "amount_usdt": effective_usdt,
                "size_scale": size_scale}

    # SOP#118: first-30d size cap — hard floor on live size regardless of caller
    gate = load_live_gate()
    activated_at = gate.get("activated_at")
    if activated_at:
        activated_ts = datetime.fromisoformat(activated_at)
        hours_since = (datetime.now(timezone.utc) - activated_ts).total_seconds() / 3600
        days_since = hours_since / 24
        if days_since < LIVE_FIRST_N_DAYS:
            effective_usdt = min(effective_usdt, LIVE_FIRST_N_DAYS_SIZE_CAP_USDT)
        # SOP#118: first-72h human confirmation
        if hours_since < LIVE_HUMAN_CONFIRM_HOURS and not gate.get("human_confirmed_first_72h"):
            logger.error(
                "LIVE ORDER BLOCKED: first %dh require human confirmation. "
                "Set human_confirmed_first_72h=true in %s to release.",
                LIVE_HUMAN_CONFIRM_HOURS, LIVE_GATE_PATH,
            )
            return {"blocked": True, "reason": "awaiting_first_72h_human_confirm"}
    else:
        # No gate file = live activation not recorded. Block and require setup.
        logger.error(
            "LIVE ORDER BLOCKED: no activation record at %s. "
            "Run `python -m trading.engine --activate-live` first.", LIVE_GATE_PATH,
        )
        return {"blocked": True, "reason": "live_not_activated"}

    price = exchange.fetch_ticker(symbol)["last"]
    qty = effective_usdt / price
    market = exchange.market(symbol)
    qty = round(qty, market.get("precision", {}).get("amount", 6))
    return exchange.create_market_order(symbol, side, qty) if qty > 0 else {}


class ReactivationGate:
    """SOP#118 G0-G5 Strategy Reactivation Gate Protocol.

    Governs whether a killed strategy can re-enter the live pool. Replaces
    the prior implicit "restart wipes disabled dict" behavior which caused
    the DualMA_10_30 restart-loop (killed 4x in 48h, 2026-04-09~11).

    Gates:
        G0 — Kill metadata recorded (strategy, cycle, tick, PF at kill)
        G1 — Cooling period: no re-entry evaluation until cooling_ticks elapsed
        G2 — Regime confirmation: rely on engine.regime_detector in caller
        G3 — Forward-walk PF >= pf_threshold on forward_window fresh ticks
        G4 — Orthogonality: caller must check concentration before re-entry
        G5 — Post-reactivation monitoring at reentry_size (caller-enforced)
    """
    def __init__(self,
                 cooling_ticks: int = REACTIVATION_COOLING_TICKS,
                 forward_window: int = REACTIVATION_FORWARD_WINDOW,
                 pf_threshold: float = REACTIVATION_PF_THRESHOLD,
                 reentry_size: float = REACTIVATION_REENTRY_SIZE):
        self.cooling_ticks = cooling_ticks
        self.forward_window = forward_window
        self.pf_threshold = pf_threshold
        self.reentry_size = reentry_size

    def kill_metadata(self, name: str, reason: str, tick: int,
                      cum_pnl: float, pf_at_kill: float) -> Dict:
        """G0: build persistent kill metadata for the disabled dict."""
        return {
            "reason": reason,
            "killed_at_tick": tick,
            "killed_at_ts": datetime.now(timezone.utc).isoformat(),
            "cum_pnl_at_kill": round(cum_pnl, 4),
            "pf_at_kill": round(pf_at_kill, 4),
            "forward_walk_ticks": [],  # list of pnl_pct, G3 accumulator
            "reentry_size_scale": self.reentry_size,
            "manually_overridden": False,
        }

    def record_forward_walk(self, metadata: Dict, pnl_pct: float) -> Dict:
        """Append a tick's hypothetical pnl to the forward-walk accumulator.

        Caller computes pnl_pct as if the strategy were live (same signal
        logic, no real orders). This is the G3 fresh-data window.
        """
        walk = list(metadata.get("forward_walk_ticks", []))
        walk.append(round(pnl_pct, 4))
        # Keep only last forward_window ticks
        if len(walk) > self.forward_window:
            walk = walk[-self.forward_window:]
        metadata = dict(metadata)
        metadata["forward_walk_ticks"] = walk
        return metadata

    def check_reactivation(self, name: str, metadata: Dict,
                           current_tick: int) -> Optional[str]:
        """Returns None if still gated, or a string reason for reactivation pass.

        Pass conditions (all required):
            G1 cooling: current_tick - killed_at_tick >= cooling_ticks
            G3 forward-walk: len(forward_walk_ticks) >= forward_window
                         AND PF over that window >= pf_threshold
        """
        if metadata.get("manually_overridden"):
            return "manual_override"
        kill_tick = metadata.get("killed_at_tick", 0)
        elapsed = current_tick - kill_tick
        if elapsed < self.cooling_ticks:
            return None
        walk = metadata.get("forward_walk_ticks", [])
        if len(walk) < self.forward_window:
            return None
        gw = sum(p for p in walk if p > 0)
        gl = abs(sum(p for p in walk if p < 0))
        if gl <= 0:
            # Degenerate estimator (distil109 I1) — insufficient loss samples
            # to compute PF. Do NOT treat PF=inf as pass.
            return None
        pf = gw / gl
        if pf < self.pf_threshold:
            return None
        return f"G3 pass: forward PF {pf:.2f} >= {self.pf_threshold} over {len(walk)} ticks"


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
        # SOP#118: disabled now persists across restarts with full metadata
        # (previously in-memory dict wiped on process restart = restart-loop bug)
        self.disabled: Dict[str, Dict] = load_disabled()
        self.strategy_size_scale: Dict[str, float] = {
            name: 1.0 for name in self.strategies
        }
        # Restore size scale for any strategy that was in reentry mode
        for name, meta in self.disabled.items():
            if isinstance(meta, dict) and meta.get("reentry_size_scale"):
                self.strategy_size_scale[name] = meta["reentry_size_scale"]
        self.pnl_tracker: Dict[str, float] = {}
        self.prev_prices: Dict[str, float] = {}
        self.total_pnl, self.tick_count = 0.0, 0
        self.clean_ticks_since_kill = 0
        # L3 Evolve: load mutable execution rules; KillMonitor uses them
        self.execution_rules = load_execution_rules()
        self.kill_monitor = KillMonitor(
            max_dd=self.execution_rules["kill_max_dd"],
            min_wr=self.execution_rules["kill_min_wr"],
            min_pf=self.execution_rules["kill_min_pf"],
            window=self.execution_rules["kill_window"],
        )
        self.reactivation_gate = ReactivationGate()

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

        disabled_dirty = False
        kill_happened_this_tick = False
        for name, strategy in self.strategies.items():
            # SOP#118 G3: for disabled strategies, compute hypothetical pnl on
            # this tick's signal for the forward-walk window (NO real orders).
            if name in self.disabled:
                try:
                    sig_disabled = strategy(bars)
                except Exception as e:
                    logger.warning("Disabled strategy %s forward-walk error: %s", name, e)
                    sig_disabled = 0
                prev_d = self.prev_signals.get(name, 0)
                prev_price_d = self.prev_prices.get(name, 0.0)
                fw_pnl = 0.0
                if prev_d != 0 and prev_price_d > 0:
                    fw_pnl = prev_d * (price - prev_price_d) / prev_price_d * 100
                self.prev_signals[name] = sig_disabled
                self.prev_prices[name] = price
                meta = self.disabled[name]
                if isinstance(meta, dict):
                    self.disabled[name] = self.reactivation_gate.record_forward_walk(meta, fw_pnl)
                    disabled_dirty = True
                    reactivation_reason = self.reactivation_gate.check_reactivation(
                        name, self.disabled[name], self.tick_count)
                    if reactivation_reason:
                        size_scale = self.disabled[name].get("reentry_size_scale", 0.5)
                        logger.info("REACTIVATE %s: %s (size=%.0f%%)",
                                    name, reactivation_reason, size_scale * 100)
                        discord_msgs.append(
                            f"REACTIVATED {name}: {reactivation_reason} @ {size_scale*100:.0f}% size")
                        del self.disabled[name]
                        self.strategy_size_scale[name] = size_scale
                        # Fresh KillMonitor window for re-enabled strategy
                        self.kill_monitor._pnl[name] = []
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

            size_scale = self.strategy_size_scale.get(name, 1.0)
            if sig != prev:
                action = {1: "OPEN_LONG", -1: "OPEN_SHORT", 0: "CLOSE"}[sig]
                if prev != 0:
                    execute_order(self.exchange, "sell" if prev == 1 else "buy",
                                  live=self.live, size_scale=size_scale)
                if sig != 0:
                    execute_order(self.exchange, "buy" if sig == 1 else "sell",
                                  live=self.live, size_scale=size_scale)
                self.prev_signals[name] = sig
                discord_msgs.append(f"{name}: {['FLAT','LONG'][sig] if sig >= 0 else 'SHORT'} @ ${price:,.0f}")

            self.prev_prices[name] = price
            signals_summary[name] = sig

            kill = self.kill_monitor.check(name)
            if kill:
                # G0: compute PF at kill for metadata
                recent = self.kill_monitor._pnl.get(name, [])[-self.kill_monitor.window:]
                gw = sum(p for p in recent if p > 0)
                gl = abs(sum(p for p in recent if p < 0))
                pf_at_kill = gw / gl if gl > 0 else 0.0
                self.disabled[name] = self.reactivation_gate.kill_metadata(
                    name, kill, self.tick_count,
                    self.pnl_tracker.get(name, 0.0), pf_at_kill)
                disabled_dirty = True
                kill_happened_this_tick = True
                # Reset size scale for next reactivation
                self.strategy_size_scale[name] = 1.0
                logger.warning("KILL %s: %s", name, kill)
                discord_msgs.append(f"KILLED {name}: {kill}")
                # L3 Evolve: modify execution rules + log lesson
                self.execution_rules = evolve_execution_rules(
                    name, kill, self.execution_rules)
                log_kill_lesson(name, kill, self.tick_count, price, regime,
                                self.pnl_tracker.get(name, 0.0),
                                self.execution_rules["kill_window"])
                logger.info("L3 Evolve: kill_window → %d", self.execution_rules["kill_window"])

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
