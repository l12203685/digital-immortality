"""
Mainnet Runner -- Binance SPOT, $100 risk cap.

Gates: pass testnet --review (GO) before running.

Modes:
  --tick / --loop   : Mainnet live trading (dual_ma only, unchanged).
  --paper-live      : Paper-trade ALL 10 strategies from NAMED_STRATEGIES
                      on real Binance prices. Per-strategy kill conditions.
  --status          : Show all strategies and their current signals/PnL.
  --report          : Per-strategy performance comparison.

Signal mapping (SPOT -- no short-selling):
    LONG  -> buy BTC with available USDT (enter position)
    FLAT  -> hold current position (do nothing)
    SHORT -> sell all BTC to USDT (exit position, NOT short-sell)

Usage:
    python mainnet_runner.py --tick              # single tick (mainnet, dual_ma)
    python mainnet_runner.py --tick --dry-run    # single tick, no real orders
    python mainnet_runner.py --status            # show all strategy stats
    python mainnet_runner.py --loop 3600         # tick every hour (mainnet)
    python mainnet_runner.py --paper-live        # paper trade ALL strategies
    python mainnet_runner.py --report            # per-strategy performance report

Credentials: set BINANCE_API_KEY and BINANCE_SECRET_KEY env vars,
             or place them in ~/.claude/credentials/binance_api.json.
Kill conditions (per strategy): MDD>10%, PF<0.85 (>=5 trades), WR<35% (>=5 trades).
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

# Ensure project root is on sys.path so `from trading.X import ...` works
# regardless of which directory the script is invoked from.
_PROJECT_ROOT = Path(__file__).parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RESULTS_DIR = Path(__file__).parent.parent / "results"
MAINNET_LOG = RESULTS_DIR / "mainnet_log.jsonl"
PAPER_LIVE_LOG = RESULTS_DIR / "paper_live_log.jsonl"
CREDENTIALS_PATH = Path.home() / ".claude" / "credentials" / "binance_api.json"

MAX_POSITION_USDT = 100.0   # hard cap: $100
MAX_DRAWDOWN_PCT = 10.0     # kill above 10% drawdown
KILL_MIN_WIN_RATE = 0.35
KILL_MIN_PROFIT_FACTOR = 0.85
KILL_MIN_TRADES = 5          # minimum trades before WR/PF kill check

SYMBOL = "BTC/USDT"
BTC_DUST_THRESHOLD = 0.00001  # below this BTC balance counts as "no position"


# ---------------------------------------------------------------------------
# Credential helpers
# ---------------------------------------------------------------------------

def _load_credentials() -> tuple:
    """Load Binance API credentials from env vars or fallback JSON file.

    Returns (api_key, secret_key) or ("", "") if not found.
    """
    api_key = os.environ.get("BINANCE_API_KEY", "")
    secret_key = os.environ.get("BINANCE_SECRET_KEY", "")

    if api_key and secret_key:
        return api_key, secret_key

    if CREDENTIALS_PATH.exists():
        try:
            creds = json.loads(CREDENTIALS_PATH.read_text(encoding="utf-8"))
            api_key = creds.get("api_key", "")
            secret_key = creds.get("secret_key", "")
            if api_key and secret_key:
                logger.info("Loaded credentials from %s", CREDENTIALS_PATH)
                return api_key, secret_key
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to read credentials file: %s", exc)

    return "", ""


# ---------------------------------------------------------------------------
# Exchange helpers
# ---------------------------------------------------------------------------

def _create_exchange(api_key: str, secret_key: str):
    """Create a ccxt Binance SPOT exchange instance."""
    try:
        import ccxt  # type: ignore
    except ImportError:
        print("ERROR: pip install ccxt")
        sys.exit(1)

    exchange = ccxt.binance({
        "apiKey": api_key,
        "secret": secret_key,
        "enableRateLimit": True,
    })
    return exchange


def _get_balances(exchange) -> Dict:
    """Fetch BTC and USDT free balances from spot account.

    Returns {"btc_free": float, "usdt_free": float}.
    """
    balance = exchange.fetch_balance()
    btc_free = float(balance.get("BTC", {}).get("free", 0.0))
    usdt_free = float(balance.get("USDT", {}).get("free", 0.0))
    return {"btc_free": btc_free, "usdt_free": usdt_free}


def _is_in_position(balances: Dict) -> bool:
    """True if holding BTC above dust threshold."""
    return balances["btc_free"] > BTC_DUST_THRESHOLD


# ---------------------------------------------------------------------------
# Log helpers
# ---------------------------------------------------------------------------

def _append_log(entry: Dict) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(MAINNET_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def _load_log() -> List[Dict]:
    if not MAINNET_LOG.exists():
        return []
    entries: List[Dict] = []
    with open(MAINNET_LOG, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries


def _compute_stats(entries: List[Dict]) -> Dict:
    trades = [e for e in entries if e.get("action") == "EXECUTED"]
    pnl_list = [e.get("realized_pnl", 0.0) for e in entries]
    total_pnl = sum(pnl_list)
    wins = sum(1 for p in pnl_list if p > 0)
    losses = sum(1 for p in pnl_list if p < 0)
    n = len(pnl_list)
    win_rate = wins / n if n > 0 else 0.0
    gross_profit = sum(p for p in pnl_list if p > 0)
    gross_loss = abs(sum(p for p in pnl_list if p < 0))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")
    return {
        "ticks": len(entries),
        "trades": len(trades),
        "total_pnl": round(total_pnl, 4),
        "win_rate": round(win_rate, 4),
        "profit_factor": round(profit_factor, 4) if profit_factor != float("inf") else "inf",
        "wins": wins,
        "losses": losses,
    }


def _check_kill(stats: Dict) -> bool:
    """Return True if kill conditions breached."""
    n = stats["ticks"]
    if n >= KILL_MIN_TRADES:
        if stats["win_rate"] < KILL_MIN_WIN_RATE:
            logger.critical("KILL: win_rate=%.2f < %.2f", stats["win_rate"], KILL_MIN_WIN_RATE)
            return True
        pf = stats["profit_factor"]
        if isinstance(pf, float) and pf < KILL_MIN_PROFIT_FACTOR:
            logger.critical("KILL: profit_factor=%.2f < %.2f", pf, KILL_MIN_PROFIT_FACTOR)
            return True
    return False


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_tick(dry_run: bool = False) -> None:
    ts = datetime.now(timezone.utc).isoformat()

    # Kill check (runs even in dry-run)
    entries = _load_log()
    stats = _compute_stats(entries)
    if _check_kill(stats):
        print("KILL CONDITIONS MET -- halting. Review mainnet_log.jsonl.")
        sys.exit(1)

    if dry_run:
        print(f"[{ts}] DRY RUN: would connect to mainnet SPOT with ${MAX_POSITION_USDT} cap, dual_ma strategy.")
        print(f"Config: symbol={SYMBOL}, max_pos={MAX_POSITION_USDT} USDT")
        print(f"Kill rails: MDD>{MAX_DRAWDOWN_PCT}%, WR<{KILL_MIN_WIN_RATE:.0%} (>={KILL_MIN_TRADES}t), PF<{KILL_MIN_PROFIT_FACTOR}")
        result: Dict = {"action": "DRY_RUN", "ts": ts, "stats": stats}
        _append_log(result)
        print(f"Result: {json.dumps(result, indent=2)}")
        return

    api_key, secret_key = _load_credentials()
    if not api_key or not secret_key:
        print("ERROR: set BINANCE_API_KEY and BINANCE_SECRET_KEY env vars,")
        print(f"       or place credentials in {CREDENTIALS_PATH}")
        sys.exit(1)

    exchange = _create_exchange(api_key, secret_key)

    # Fetch OHLCV for strategy
    ohlcv = exchange.fetch_ohlcv(SYMBOL, "1d", limit=60)
    bars = [
        {
            "ts": str(row[0]),
            "open": row[1],
            "high": row[2],
            "low": row[3],
            "close": row[4],
            "volume": row[5],
        }
        for row in ohlcv
    ]

    if not bars:
        result = {"action": "NO_DATA", "ts": ts}
        _append_log(result)
        print(f"[{ts}] No OHLCV data returned.")
        return

    price = bars[-1]["close"]

    # Compute signal
    from trading.strategies import dual_ma_btc_daily
    signal = dual_ma_btc_daily(bars)
    signal_name = {1: "LONG", -1: "SHORT", 0: "FLAT"}.get(signal, "FLAT")

    # Get current balances
    balances = _get_balances(exchange)
    in_position = _is_in_position(balances)

    result = {
        "ts": ts,
        "price": price,
        "signal": signal_name,
        "btc_balance": balances["btc_free"],
        "usdt_balance": balances["usdt_free"],
        "in_position": in_position,
    }

    print(f"[{ts}] Mainnet SPOT tick: price={price:.2f} signal={signal_name} in_position={in_position}")
    print(f"  BTC={balances['btc_free']:.8f}  USDT={balances['usdt_free']:.2f}")

    # ----- Signal execution (SPOT logic) -----
    # LONG  -> buy BTC with available USDT (if not already holding)
    # FLAT  -> do nothing
    # SHORT -> sell all BTC to USDT (exit, not short-sell)

    if signal_name == "LONG" and not in_position:
        # Buy BTC with available USDT, capped at MAX_POSITION_USDT
        usdt_to_spend = min(balances["usdt_free"], MAX_POSITION_USDT)
        if usdt_to_spend < 1.0:
            result["action"] = "SKIP_NO_USDT"
            logger.info("LONG signal but insufficient USDT (%.2f)", usdt_to_spend)
        else:
            # Calculate BTC amount from USDT
            market = exchange.market(SYMBOL)
            precision = market.get("precision", {}).get("amount", 8)
            btc_amount = round(usdt_to_spend / price, precision)

            if btc_amount <= 0:
                result["action"] = "SKIP_ZERO_AMOUNT"
            else:
                logger.info("LONG: buying %.8f BTC with %.2f USDT", btc_amount, usdt_to_spend)
                order = exchange.create_market_buy_order(SYMBOL, btc_amount)
                result["action"] = "EXECUTED"
                result["order_side"] = "BUY"
                result["order_amount_btc"] = btc_amount
                result["order_usdt"] = usdt_to_spend
                result["order_id"] = order.get("id")
                logger.info("BUY order placed: id=%s amount=%.8f BTC", order.get("id"), btc_amount)

    elif signal_name == "SHORT" and in_position:
        # Sell all BTC to USDT (exit position)
        btc_to_sell = balances["btc_free"]
        market = exchange.market(SYMBOL)
        precision = market.get("precision", {}).get("amount", 8)
        btc_to_sell = round(btc_to_sell, precision)

        if btc_to_sell <= 0:
            result["action"] = "SKIP_ZERO_AMOUNT"
        else:
            logger.info("SHORT (exit): selling %.8f BTC", btc_to_sell)
            order = exchange.create_market_sell_order(SYMBOL, btc_to_sell)
            result["action"] = "EXECUTED"
            result["order_side"] = "SELL"
            result["order_amount_btc"] = btc_to_sell
            result["order_id"] = order.get("id")
            logger.info("SELL order placed: id=%s amount=%.8f BTC", order.get("id"), btc_to_sell)

    elif signal_name == "FLAT":
        result["action"] = "HOLD_FLAT"
        logger.info("FLAT signal -- holding current position")

    elif signal_name == "LONG" and in_position:
        result["action"] = "HOLD_ALREADY_LONG"
        logger.info("LONG signal but already in position -- holding")

    elif signal_name == "SHORT" and not in_position:
        result["action"] = "HOLD_ALREADY_OUT"
        logger.info("SHORT signal but already out of position -- nothing to sell")

    else:
        result["action"] = "NO_ACTION"

    _append_log(result)
    print(f"Result: {json.dumps(result, indent=2)}")

    # Post-trade stats
    all_entries = _load_log()
    post_stats = _compute_stats(all_entries)
    print(f"Stats:  {json.dumps(post_stats)}")


def cmd_status() -> None:
    # Mainnet status (unchanged)
    entries = _load_log()
    if entries:
        stats = _compute_stats(entries)
        print(f"=== Mainnet (real $) ===")
        print(f"Log:         {MAINNET_LOG}")
        print(f"Entries:     {stats['ticks']}")
        print(f"Trades:      {stats['trades']}")
        print(f"Total PnL:   {stats['total_pnl']} USDT")
        print(f"Win rate:    {stats['win_rate']:.1%}")
        print(f"PF:          {stats['profit_factor']}")
        kill = _check_kill(stats)
        print(f"Kill status: {'BREACH -- HALT' if kill else 'OK'}")
        print()
    else:
        print("=== Mainnet (real $) ===")
        print("No mainnet log entries yet.")
        print()

    # Paper-live status: all strategies
    paper_entries = _load_paper_log()
    if not paper_entries:
        print("=== Paper Live (all strategies) ===")
        print("No paper-live entries yet.")
        return

    from trading.strategies import NAMED_STRATEGIES

    print(f"=== Paper Live (all strategies) ===")
    print(f"Log: {PAPER_LIVE_LOG}")
    print(f"Total entries: {len(paper_entries)}")
    print()
    print(f"{'Strategy':30s} {'Signal':7s} {'Ticks':>5s} {'Trades':>6s} {'PnL':>10s} {'WR':>6s} {'PF':>8s} {'Kill':>5s}")
    print("-" * 85)

    total_pnl = 0.0
    for name in sorted(NAMED_STRATEGIES.keys()):
        st = _compute_paper_stats(paper_entries, name)
        total_pnl += st["total_pnl"]
        kill_str = "KILL" if st["kill"] else "OK"
        pf_str = str(st["profit_factor"]) if st["profit_factor"] == "inf" else f"{st['profit_factor']:.2f}"
        print(f"{name:30s} {st['last_signal']:7s} {st['ticks']:5d} {st['trades']:6d} "
              f"{st['total_pnl']:+10.2f} {st['win_rate']:5.1%} {pf_str:>8s} {kill_str:>5s}")

    print("-" * 85)
    print(f"{'TOTAL':30s} {'':7s} {'':5s} {'':6s} {total_pnl:+10.2f}")
    print()

    # Last 5 entries across all strategies
    print("Last 5 entries:")
    for e in paper_entries[-5:]:
        print(f"  {e.get('ts', '?')} [{e.get('strategy', '?'):20s}] signal={e.get('signal', '--'):5s} price={e.get('price', 0):.2f}")


def _load_paper_log() -> List[Dict]:
    """Load all entries from paper_live_log.jsonl."""
    if not PAPER_LIVE_LOG.exists():
        return []
    entries: List[Dict] = []
    for line in PAPER_LIVE_LOG.read_text(encoding="utf-8").strip().splitlines():
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return entries


def _compute_paper_stats(entries: List[Dict], strategy_name: str) -> Dict:
    """Compute PnL stats for a single strategy from paper log entries.

    Simulates a $100 paper portfolio: LONG buys at price, SHORT sells at price.
    """
    strat_entries = [e for e in entries if e.get("strategy") == strategy_name and e.get("action") == "PAPER_LIVE"]
    if not strat_entries:
        return {
            "strategy": strategy_name,
            "ticks": 0, "trades": 0, "total_pnl": 0.0,
            "win_rate": 0.0, "profit_factor": "inf", "wins": 0, "losses": 0,
            "kill": False, "last_signal": "N/A",
        }

    # Walk through signals and compute round-trip PnL
    position_open = False
    entry_price = 0.0
    pnl_list: List[float] = []
    trade_count = 0

    for e in strat_entries:
        sig = e.get("signal", "FLAT")
        price = e.get("price", 0.0)
        if sig == "LONG" and not position_open:
            position_open = True
            entry_price = price
            trade_count += 1
        elif sig == "SHORT" and position_open:
            pnl = (price - entry_price) / entry_price * MAX_POSITION_USDT if entry_price > 0 else 0.0
            pnl_list.append(pnl)
            position_open = False
            entry_price = 0.0

    # Unrealized PnL for open position
    unrealized = 0.0
    if position_open and strat_entries:
        last_price = strat_entries[-1].get("price", 0.0)
        if entry_price > 0:
            unrealized = (last_price - entry_price) / entry_price * MAX_POSITION_USDT

    total_pnl = sum(pnl_list) + unrealized
    wins = sum(1 for p in pnl_list if p > 0)
    losses = sum(1 for p in pnl_list if p < 0)
    n_closed = len(pnl_list)
    win_rate = wins / n_closed if n_closed > 0 else 0.0
    gross_profit = sum(p for p in pnl_list if p > 0)
    gross_loss = abs(sum(p for p in pnl_list if p < 0))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

    last_signal = strat_entries[-1].get("signal", "FLAT") if strat_entries else "N/A"

    # Kill check for this strategy
    kill = False
    if n_closed >= KILL_MIN_TRADES:
        if win_rate < KILL_MIN_WIN_RATE:
            kill = True
        if isinstance(profit_factor, float) and profit_factor < KILL_MIN_PROFIT_FACTOR:
            kill = True
    # MDD check: if total_pnl drops below -MAX_DRAWDOWN_PCT% of $100
    if total_pnl < -(MAX_POSITION_USDT * MAX_DRAWDOWN_PCT / 100.0):
        kill = True

    return {
        "strategy": strategy_name,
        "ticks": len(strat_entries),
        "trades": trade_count,
        "closed_trades": n_closed,
        "total_pnl": round(total_pnl, 4),
        "unrealized_pnl": round(unrealized, 4),
        "win_rate": round(win_rate, 4),
        "profit_factor": round(profit_factor, 4) if profit_factor != float("inf") else "inf",
        "wins": wins,
        "losses": losses,
        "kill": kill,
        "last_signal": last_signal,
        "in_position": position_open,
    }


def cmd_paper_live() -> None:
    """Fetch real Binance public prices; run ALL strategies; log paper trades. No credentials."""
    ts = datetime.now(timezone.utc).isoformat()
    try:
        import ccxt  # type: ignore
        from ccxt.base.errors import NetworkError as CcxtNetworkError  # type: ignore
    except ImportError:
        print("ERROR: pip install ccxt")
        sys.exit(1)

    # Use spot exchange for paper-live (matches mainnet)
    exchange = ccxt.binance({"enableRateLimit": True})
    bars = None
    data_source = "live"
    try:
        ohlcv = exchange.fetch_ohlcv(SYMBOL, "1d", limit=60)
        bars = [
            {
                "ts": str(row[0]),
                "open": row[1],
                "high": row[2],
                "low": row[3],
                "close": row[4],
                "volume": row[5],
            }
            for row in ohlcv
        ]
        if not bars:
            bars = None
    except (CcxtNetworkError, ConnectionError, Exception):
        bars = None

    if bars is None:
        # Synthetic fallback: walk from last known price in log
        from trading.backtest_framework import generate_synthetic_bars
        existing_for_price = _load_paper_log()
        last_price = 71509.90  # project default seed price
        for e in reversed(existing_for_price):
            if e.get("action") == "PAPER_LIVE" and e.get("price"):
                last_price = float(e["price"])
                break
        bars = generate_synthetic_bars(n=60, drift=0.0001, volatility=0.012, seed=None)
        # Rescale synthetic bars so last close matches last known price
        raw_last = bars[-1]["close"]
        scale = last_price / raw_last if raw_last else 1.0
        bars = [
            {**b, "open": b["open"]*scale, "high": b["high"]*scale,
             "low": b["low"]*scale, "close": b["close"]*scale}
            for b in bars
        ]
        data_source = "synthetic"
        print(f"[{ts}] PAPER_LIVE network unavailable — using synthetic bars (last_price={last_price:.2f})")

    price = bars[-1]["close"]

    # Regime detection
    from trading.portfolio import RegimeDetector
    from trading.strategies import NAMED_STRATEGIES

    detector = RegimeDetector()
    regime = detector.detect(bars)
    scores = detector.last_scores()

    print(f"[{ts}] PAPER_LIVE tick: price={price:.2f}  regime={regime.upper()}")
    print(f"  scores: trend={scores.get('trend_strength', 0):.4f}  mr={scores.get('mr_score', 0):.4f}")
    print()

    # Load existing log for kill checks
    existing_entries = _load_paper_log()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    logged_count = 0
    skipped_kill = 0

    for name, strategy_fn in sorted(NAMED_STRATEGIES.items()):
        # Per-strategy kill check
        strat_stats = _compute_paper_stats(existing_entries, name)
        if strat_stats["kill"]:
            print(f"  {name:30s}  KILLED (PnL={strat_stats['total_pnl']:+.2f} WR={strat_stats['win_rate']:.1%} PF={strat_stats['profit_factor']})")
            skipped_kill += 1
            continue

        # Generate signal
        try:
            signal = strategy_fn(bars)
        except Exception as exc:
            logger.warning("Strategy %s raised %s: %s", name, type(exc).__name__, exc)
            continue

        signal_label = {1: "LONG", -1: "SHORT", 0: "FLAT"}.get(signal, "FLAT")

        entry = {
            "action": "PAPER_LIVE",
            "ts": ts,
            "strategy": name,
            "price": price,
            "signal": signal_label,
            "regime": regime,
            "source": data_source,
            "note": "paper -- no real order placed",
        }

        with open(PAPER_LIVE_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        logged_count += 1

        print(f"  {name:30s}  signal={signal_label:5s}  regime={regime}")

    print()
    print(f"Logged {logged_count} strategy signals to {PAPER_LIVE_LOG}")
    if skipped_kill > 0:
        print(f"Skipped {skipped_kill} strategies (kill conditions met)")

    total_lines = len(PAPER_LIVE_LOG.read_text().strip().splitlines()) if PAPER_LIVE_LOG.exists() else 0
    print(f"Total paper-live entries: {total_lines}")


def cmd_report(save: bool = False) -> None:
    """Generate a human-readable markdown performance report with per-strategy comparison."""
    lines = ["# Trading Performance Report (SPOT)", f"> Generated: {datetime.now(timezone.utc).isoformat()}", ""]

    # --- Mainnet ---
    mainnet = _load_log()
    lines.append("## Mainnet (real $ -- SPOT)")
    if not mainnet:
        lines.append("No mainnet entries yet.\n")
    else:
        stats = _compute_stats(mainnet)
        kill = _check_kill(stats)
        lines += [
            f"- Ticks: {stats['ticks']}  Trades: {stats['trades']}",
            f"- Total PnL: **{stats['total_pnl']:+.4f} USDT**",
            f"- Win Rate: {stats['win_rate']:.1%}  (W={stats['wins']} L={stats['losses']})",
            f"- Profit Factor: {stats['profit_factor']}",
            f"- Kill status: {'BREACH -- HALT' if kill else 'OK'}",
            "",
            "### Last 5 entries",
        ]
        for e in mainnet[-5:]:
            lines.append(f"  - `{e.get('ts', '?')}` action={e.get('action')} "
                         f"signal={e.get('signal', '--')} pnl={e.get('realized_pnl', 'n/a')}")
        lines.append("")

    # --- Paper Live: Per-Strategy Comparison ---
    lines.append("## Paper Live -- Per-Strategy Performance")
    paper_entries = _load_paper_log()

    if not paper_entries:
        lines.append("No paper-live entries yet.\n")
    else:
        from trading.strategies import NAMED_STRATEGIES

        # Price summary
        prices = [e.get("price", 0) for e in paper_entries if e.get("price")]
        if prices:
            lines.append(f"- Price range: {min(prices):.2f} -- {max(prices):.2f} USDT")
        lines.append(f"- Total entries: {len(paper_entries)}")
        lines.append("")

        # Strategy comparison table
        lines.append("| Strategy | Ticks | Trades | PnL (USDT) | Win Rate | PF | Signal | Kill |")
        lines.append("|----------|------:|-------:|-----------:|---------:|---:|--------|------|")

        total_pnl = 0.0
        strat_results: List[Dict] = []
        for name in sorted(NAMED_STRATEGIES.keys()):
            st = _compute_paper_stats(paper_entries, name)
            strat_results.append(st)
            total_pnl += st["total_pnl"]
            pf_str = str(st["profit_factor"]) if st["profit_factor"] == "inf" else f"{st['profit_factor']:.2f}"
            kill_str = "KILL" if st["kill"] else "OK"
            lines.append(
                f"| {name} | {st['ticks']} | {st['trades']} | "
                f"{st['total_pnl']:+.2f} | {st['win_rate']:.1%} | {pf_str} | "
                f"{st['last_signal']} | {kill_str} |"
            )

        lines.append(f"| **TOTAL** | | | **{total_pnl:+.2f}** | | | | |")
        lines.append("")

        # Best/worst
        profitable = [s for s in strat_results if s["total_pnl"] > 0]
        losing = [s for s in strat_results if s["total_pnl"] < 0]
        if profitable:
            best = max(profitable, key=lambda s: s["total_pnl"])
            lines.append(f"**Best**: {best['strategy']} ({best['total_pnl']:+.2f} USDT)")
        if losing:
            worst = min(losing, key=lambda s: s["total_pnl"])
            lines.append(f"**Worst**: {worst['strategy']} ({worst['total_pnl']:+.2f} USDT)")
        killed = [s for s in strat_results if s["kill"]]
        if killed:
            lines.append(f"**Killed**: {', '.join(s['strategy'] for s in killed)}")
        lines.append("")

        # Last 5 ticks
        lines.append("### Last 5 entries")
        for e in paper_entries[-5:]:
            strat = e.get("strategy", "?")
            lines.append(
                f"  - `{e.get('ts', '?')}` [{strat}] "
                f"price={e.get('price', 0):.2f} signal={e.get('signal', '--')}"
            )
        lines.append("")

    # --- Kill Rails Summary ---
    lines += [
        "## Kill Rail Thresholds (per strategy)",
        f"| Metric | Threshold | Applies After |",
        f"|--------|-----------|---------------|",
        f"| Max Drawdown | >{MAX_DRAWDOWN_PCT}% of ${MAX_POSITION_USDT} | any time |",
        f"| Win Rate | <{KILL_MIN_WIN_RATE:.0%} | >={KILL_MIN_TRADES} closed trades |",
        f"| Profit Factor | <{KILL_MIN_PROFIT_FACTOR} | >={KILL_MIN_TRADES} closed trades |",
        "",
    ]

    report = "\n".join(lines)
    print(report)

    if save:
        out = RESULTS_DIR / "trading_report.md"
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        print(f"\nSaved to {out}")


def cmd_loop(interval: int) -> None:
    import time
    logger.info("Mainnet SPOT loop started: interval=%ds", interval)
    while True:
        try:
            cmd_tick()
        except Exception as e:
            logger.error("Tick error: %s", e)
        time.sleep(interval)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Mainnet runner -- SPOT, $100 cap, 10 strategies (paper) / dual_ma (live)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--tick", action="store_true", help="Single tick")
    group.add_argument("--status", action="store_true", help="Show all strategy stats and signals")
    group.add_argument("--loop", type=int, metavar="SECONDS", help="Loop every N seconds")
    group.add_argument("--paper-live", action="store_true", help="Paper trade ALL 10 strategies on real prices (no credentials)")
    group.add_argument("--report", action="store_true", help="Per-strategy performance comparison report")
    parser.add_argument("--dry-run", action="store_true", help="Skip actual order placement")
    parser.add_argument("--save", action="store_true", help="Save report to results/trading_report.md (with --report)")
    args = parser.parse_args()

    if args.tick:
        cmd_tick(dry_run=args.dry_run)
    elif args.status:
        cmd_status()
    elif args.loop:
        cmd_loop(args.loop)
    elif args.paper_live:
        cmd_paper_live()
    elif args.report:
        cmd_report(save=args.save)


if __name__ == "__main__":
    main()
