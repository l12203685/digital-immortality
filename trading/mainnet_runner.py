"""
Mainnet Runner — Binance USDT-M Futures, $100 risk cap.

Gates: pass testnet --review (GO) before running.
Strategy: dual_ma_btc_daily (only strategy with 7+ ticks, PF=5.839, WR=60%).

Usage:
    python mainnet_runner.py --tick              # single tick
    python mainnet_runner.py --status            # show log
    python mainnet_runner.py --loop 3600         # tick every hour

Credentials: set BINANCE_MAINNET_KEY and BINANCE_MAINNET_SECRET env vars.
Kill conditions: MDD>10%, PF<0.85 (>=3 losses), WR<35% (>=5 trades).
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from trading.live_binance import BinanceConfig, LiveExecutor, BinanceFuturesClient
from trading.strategies import dual_ma_btc_daily

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RESULTS_DIR = Path(__file__).parent.parent / "results"
MAINNET_LOG = RESULTS_DIR / "mainnet_log.jsonl"
PAPER_LIVE_LOG = RESULTS_DIR / "paper_live_log.jsonl"

MAX_POSITION_USDT = 100.0   # hard cap: $100
MAX_DRAWDOWN_PCT = 10.0     # kill above 10% drawdown
KILL_MIN_WIN_RATE = 0.35
KILL_MIN_PROFIT_FACTOR = 0.85
KILL_MIN_TRADES = 5         # minimum trades before WR/PF kill check


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
    entries = []
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
    pnl_list = [e.get("realized_pnl", 0.0) for e in entries if e.get("action") == "EXECUTED"]
    total_pnl = sum(pnl_list)
    wins = sum(1 for p in pnl_list if p > 0)
    losses = sum(1 for p in pnl_list if p < 0)
    n = len(pnl_list)
    win_rate = wins / n if n > 0 else 0.0
    gross_profit = sum(p for p in pnl_list if p > 0)
    gross_loss = abs(sum(p for p in pnl_list if p < 0))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")
    # MDD as % of $100 initial capital
    cum = 0.0; peak = 0.0; max_dd = 0.0
    for p in pnl_list:
        cum += p
        if cum > peak: peak = cum
        dd = peak - cum
        if dd > max_dd: max_dd = dd
    mdd_pct = (max_dd / 100.0) * 100.0  # % of $100 cap
    return {
        "ticks": len(entries),
        "trades": len(trades),
        "total_pnl": round(total_pnl, 4),
        "win_rate": round(win_rate, 4),
        "profit_factor": round(profit_factor, 4) if profit_factor != float("inf") else "inf",
        "wins": wins,
        "losses": losses,
        "mdd_pct": round(mdd_pct, 2),
    }


def _check_kill(stats: Dict) -> bool:
    """Return True if kill conditions breached."""
    if stats.get("mdd_pct", 0) > MAX_DRAWDOWN_PCT:
        logger.critical("KILL: mdd_pct=%.2f%% > %.2f%%", stats["mdd_pct"], MAX_DRAWDOWN_PCT)
        return True
    n = stats["trades"]
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

    if dry_run:
        # Kill check still runs so dry-run validates the kill-rail logic
        entries = _load_log()
        stats = _compute_stats(entries)
        if _check_kill(stats):
            print("KILL CONDITIONS MET — halting. Review mainnet_log.jsonl.")
            sys.exit(1)
        print(f"[{ts}] DRY RUN: would connect to mainnet with $100 cap, dual_ma strategy.")
        print(f"Config: symbol=BTC/USDT:USDT, leverage=1x, max_pos={MAX_POSITION_USDT} USDT")
        print(f"Kill rails: MDD>{MAX_DRAWDOWN_PCT}%, WR<{KILL_MIN_WIN_RATE:.0%} (≥{KILL_MIN_TRADES}t), PF<{KILL_MIN_PROFIT_FACTOR}")
        result = {"action": "DRY_RUN", "ts": ts, "stats": stats}
        _append_log(result)
        print(f"Result: {json.dumps(result, indent=2)}")
        return

    api_key = os.environ.get("BINANCE_MAINNET_KEY", "")
    api_secret = os.environ.get("BINANCE_MAINNET_SECRET", "")

    if not api_key or not api_secret:
        print("ERROR: set BINANCE_MAINNET_KEY and BINANCE_MAINNET_SECRET")
        sys.exit(1)

    # Kill check before trading
    entries = _load_log()
    stats = _compute_stats(entries)
    if _check_kill(stats):
        print("KILL CONDITIONS MET — halting. Review mainnet_log.jsonl.")
        sys.exit(1)

    config = BinanceConfig(
        api_key=api_key,
        api_secret=api_secret,
        testnet=False,
        symbol="BTC/USDT:USDT",
        leverage=1,
        max_position_usdt=MAX_POSITION_USDT,
        max_drawdown_pct=MAX_DRAWDOWN_PCT,
    )

    executor = LiveExecutor(config, strategy=dual_ma_btc_daily, name="dual_ma_mainnet")

    print(f"[{ts}] Running mainnet tick...")
    result = executor.tick()
    result["ts"] = ts

    _append_log(result)
    print(f"Result: {json.dumps(result, indent=2)}")

    entries = _load_log()
    stats = _compute_stats(entries)
    print(f"Stats:  {json.dumps(stats)}")


def cmd_status() -> None:
    entries = _load_log()
    if not entries:
        print("No mainnet log entries yet.")
        return
    stats = _compute_stats(entries)
    print(f"Mainnet log: {MAINNET_LOG}")
    print(f"Entries:     {stats['ticks']}")
    print(f"Trades:      {stats['trades']}")
    print(f"Total PnL:   {stats['total_pnl']} USDT")
    print(f"MDD:         {stats['mdd_pct']:.2f}%")
    print(f"Win rate:    {stats['win_rate']:.1%}")
    print(f"PF:          {stats['profit_factor']}")
    print()
    kill = _check_kill(stats)
    print(f"Kill status: {'BREACH — HALT' if kill else 'OK'}")
    print()
    print("Last 3 entries:")
    for e in entries[-3:]:
        print(f"  {e.get('ts', '?')} action={e.get('action')} signal={e.get('signal')} pnl={e.get('realized_pnl', 'n/a')}")


def cmd_paper_live() -> None:
    """Fetch real Binance public prices; run dual_ma signal; log paper trade. No credentials."""
    ts = datetime.now(timezone.utc).isoformat()
    try:
        import ccxt  # type: ignore
    except ImportError:
        print("ERROR: pip install ccxt")
        sys.exit(1)

    exchange = ccxt.binanceusdm({"enableRateLimit": True})
    ohlcv = exchange.fetch_ohlcv("BTC/USDT:USDT", "1d", limit=60)
    bars = [{"ts": str(row[0]), "open": row[1], "high": row[2], "low": row[3], "close": row[4], "volume": row[5]} for row in ohlcv]

    from trading.strategies import dual_ma_btc_daily
    signal = dual_ma_btc_daily(bars)

    price = bars[-1]["close"] if bars else 0.0
    entry = {
        "action": "PAPER_LIVE",
        "ts": ts,
        "price": price,
        "signal": {1: "LONG", -1: "SHORT", 0: "FLAT"}.get(signal, "FLAT"),
        "note": "paper — no real order placed",
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(PAPER_LIVE_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"[{ts}] PAPER_LIVE tick: price={price:.2f} signal={entry['signal']}")
    print(f"Logged to {PAPER_LIVE_LOG}")

    # Show last 5
    lines = PAPER_LIVE_LOG.read_text().strip().splitlines() if PAPER_LIVE_LOG.exists() else []
    print(f"Total paper-live ticks: {len(lines)}")


def cmd_report(save: bool = False) -> None:
    """Generate a human-readable markdown performance report for both paper-live and mainnet logs."""
    lines = ["# Trading Performance Report", f"> Generated: {datetime.now(timezone.utc).isoformat()}", ""]

    # --- Mainnet ---
    mainnet = _load_log()
    lines.append("## Mainnet (real $)")
    if not mainnet:
        lines.append("No mainnet entries yet.\n")
    else:
        stats = _compute_stats(mainnet)
        kill = _check_kill(stats)
        lines += [
            f"- Ticks: {stats['ticks']}  Trades: {stats['trades']}",
            f"- Total PnL: **{stats['total_pnl']:+.4f} USDT**",
            f"- MDD: {stats['mdd_pct']:.2f}%",
            f"- Win Rate: {stats['win_rate']:.1%}  (W={stats['wins']} L={stats['losses']})",
            f"- Profit Factor: {stats['profit_factor']}",
            f"- Kill status: {'🔴 BREACH — HALT' if kill else '🟢 OK'}",
            "",
            "### Last 5 entries",
        ]
        for e in mainnet[-5:]:
            lines.append(f"  - `{e.get('ts', '?')}` action={e.get('action')} "
                         f"signal={e.get('signal', '—')} pnl={e.get('realized_pnl', 'n/a')}")
        lines.append("")

    # --- Paper Live ---
    lines.append("## Paper Live (real prices, no real orders)")
    paper_entries: List[Dict] = []
    if PAPER_LIVE_LOG.exists():
        for line in PAPER_LIVE_LOG.read_text().strip().splitlines():
            try:
                paper_entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass

    if not paper_entries:
        lines.append("No paper-live entries yet.\n")
    else:
        prices = [e.get("price", 0) for e in paper_entries]
        signals = [e.get("signal", "FLAT") for e in paper_entries]
        signal_counts = {s: signals.count(s) for s in set(signals)}
        lines += [
            f"- Ticks: {len(paper_entries)}",
            f"- Price range: {min(prices):.2f} – {max(prices):.2f} USDT",
            f"- Signal distribution: {signal_counts}",
            "",
            "### Last 5 ticks",
        ]
        for e in paper_entries[-5:]:
            lines.append(f"  - `{e.get('ts', '?')}` price={e.get('price', '?'):.2f} signal={e.get('signal')}")
        lines.append("")

    # --- Kill Rails Summary ---
    lines += [
        "## Kill Rail Thresholds",
        f"| Metric | Threshold | Applies After |",
        f"|--------|-----------|---------------|",
        f"| Max Drawdown | >{MAX_DRAWDOWN_PCT}% | any time |",
        f"| Win Rate | <{KILL_MIN_WIN_RATE:.0%} | ≥{KILL_MIN_TRADES} trades |",
        f"| Profit Factor | <{KILL_MIN_PROFIT_FACTOR} | ≥{KILL_MIN_TRADES} trades |",
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
    logger.info("Mainnet loop started: interval=%ds", interval)
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
    parser = argparse.ArgumentParser(description="Mainnet runner — $100 cap, dual_ma")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--tick", action="store_true", help="Single tick")
    group.add_argument("--status", action="store_true", help="Show log stats")
    group.add_argument("--loop", type=int, metavar="SECONDS", help="Loop every N seconds")
    group.add_argument("--paper-live", action="store_true", help="Paper trade on real prices (no credentials)")
    group.add_argument("--report", action="store_true", help="Print markdown performance report")
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
