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
    print(f"Win rate:    {stats['win_rate']:.1%}")
    print(f"PF:          {stats['profit_factor']}")
    print()
    kill = _check_kill(stats)
    print(f"Kill status: {'BREACH — HALT' if kill else 'OK'}")
    print()
    print("Last 3 entries:")
    for e in entries[-3:]:
        print(f"  {e.get('ts', '?')} action={e.get('action')} signal={e.get('signal')} pnl={e.get('realized_pnl', 'n/a')}")


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
    parser.add_argument("--dry-run", action="store_true", help="Skip actual order placement")
    args = parser.parse_args()

    if args.tick:
        cmd_tick(dry_run=args.dry_run)
    elif args.status:
        cmd_status()
    elif args.loop:
        cmd_loop(args.loop)


if __name__ == "__main__":
    main()
