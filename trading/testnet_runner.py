"""
Testnet Runner — Binance USDT-M Futures Testnet

Runs validated strategies on Binance testnet with structured logging.
Serves as the GO/NO-GO gate before mainnet at small size.

Usage:
    python testnet_runner.py --tick                 # single tick, all strategies
    python testnet_runner.py --tick --strategy dual_ma  # single tick, named strategy
    python testnet_runner.py --status              # show current state from log
    python testnet_runner.py --review              # print GO/NO-GO vs kill conditions
    python testnet_runner.py --loop 3600           # loop every 3600s (1h)
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from trading.backtest_framework import Bar
from trading.live_binance import BinanceConfig, LiveExecutor
from trading.strategies import (
    dual_ma_btc_daily,
    donchian_btc_daily,
    dual_ma_filtered,
    donchian_filtered,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RESULTS_DIR = Path(__file__).parent.parent / "results"
TESTNET_LOG = RESULTS_DIR / "testnet_log.jsonl"

STRATEGIES = {
    "dual_ma": dual_ma_btc_daily,
    "donchian": donchian_btc_daily,
    "dual_ma_filtered": dual_ma_filtered,
    "donchian_filtered": donchian_filtered,
}

# Kill conditions (mirror paper_trader_review thresholds)
KILL_MAX_DRAWDOWN_PCT = 15.0   # stricter on testnet (paper was 20%)
KILL_MIN_WIN_RATE = 0.35
KILL_MIN_PROFIT_FACTOR = 0.85
REVIEW_MIN_TICKS = 7           # minimum ticks before issuing GO/NO-GO


# ---------------------------------------------------------------------------
# State persistence (append-only JSONL)
# ---------------------------------------------------------------------------

def _log_tick(entry: Dict) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(TESTNET_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def _load_log() -> List[Dict]:
    if not TESTNET_LOG.exists():
        return []
    entries = []
    with open(TESTNET_LOG, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries


# ---------------------------------------------------------------------------
# Performance tracking
# ---------------------------------------------------------------------------

def _compute_stats(entries: List[Dict], strategy: str) -> Dict:
    """Compute running PnL, drawdown, win rate, and profit factor from log."""
    ticks = [e for e in entries if e.get("strategy") == strategy]
    if not ticks:
        return {"tick_count": 0}

    pnl_series = []
    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    wins = 0
    losses = 0
    gross_profit = 0.0
    gross_loss = 0.0

    for e in ticks:
        pnl = e.get("pnl_usdt", 0.0)
        equity += pnl
        if equity > peak:
            peak = equity
        dd = (peak - equity) / max(peak, 1.0) * 100 if peak > 0 else 0.0
        max_dd = max(max_dd, dd)
        if pnl > 0:
            wins += 1
            gross_profit += pnl
        elif pnl < 0:
            losses += 1
            gross_loss += abs(pnl)
        pnl_series.append(equity)

    total_trades = wins + losses
    win_rate = wins / total_trades if total_trades > 0 else 0.0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

    return {
        "strategy": strategy,
        "tick_count": len(ticks),
        "total_pnl_usdt": round(equity, 4),
        "max_drawdown_pct": round(max_dd, 2),
        "win_rate": round(win_rate, 4),
        "profit_factor": round(profit_factor, 4),
        "wins": wins,
        "losses": losses,
    }


def _check_kills(stats: Dict) -> List[str]:
    kills = []
    if stats.get("max_drawdown_pct", 0) >= KILL_MAX_DRAWDOWN_PCT:
        kills.append(f"MDD {stats['max_drawdown_pct']:.1f}% >= {KILL_MAX_DRAWDOWN_PCT}%")
    if stats.get("win_rate", 1.0) < KILL_MIN_WIN_RATE and stats.get("wins", 0) + stats.get("losses", 0) >= 5:
        kills.append(f"WinRate {stats['win_rate']:.1%} < {KILL_MIN_WIN_RATE:.0%}")
    if stats.get("profit_factor", 999) < KILL_MIN_PROFIT_FACTOR and stats.get("losses", 0) >= 3:
        kills.append(f"PF {stats['profit_factor']:.3f} < {KILL_MIN_PROFIT_FACTOR}")
    return kills


# ---------------------------------------------------------------------------
# Single tick execution
# ---------------------------------------------------------------------------

def _compute_sim_pnl(entries: List[Dict], strategy: str, current_price: float, position_usdt: float) -> float:
    """
    Simulate PnL for dry-run ticks.

    Logic: the position held during [prev_tick → this_tick] was signaled by prev_tick.
    PnL = prev_signal × (current_price − prev_price) / prev_price × position_usdt
    Returns 0.0 if no prior tick or prior price is missing.
    """
    prev = next(
        (e for e in reversed(entries)
         if e.get("strategy") == strategy and e.get("price") and "signal" in e),
        None,
    )
    if prev is None:
        return 0.0
    prev_signal = prev["signal"]      # int: 1=LONG, -1=SHORT, 0=FLAT
    prev_price = float(prev["price"])
    if prev_price <= 0 or prev_signal == 0:
        return 0.0
    pct = (current_price - prev_price) / prev_price
    return round(prev_signal * pct * position_usdt, 4)


def run_tick(strategy_name: str, dry_run: bool = False) -> Dict:
    """Execute one tick for a strategy. Returns the tick result dict."""
    strategy_fn = STRATEGIES[strategy_name]
    position_usdt = 100.0
    config = BinanceConfig(
        testnet=True,
        max_position_usdt=position_usdt,
        max_drawdown_pct=KILL_MAX_DRAWDOWN_PCT,
        leverage=1,
    )

    executor = LiveExecutor(config, strategy_fn, name=strategy_name)

    if dry_run or not config.has_credentials:
        # Dry run: fetch data, compute signal, no orders
        try:
            bars: List[Bar] = executor.client.fetch_ohlcv("1d", 100)
            signal = executor.strategy(bars)
            current_price = bars[-1]["close"] if bars else None
            prior_entries = _load_log()
            sim_pnl = _compute_sim_pnl(prior_entries, strategy_name, current_price, position_usdt) if current_price else 0.0
            result = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "strategy": strategy_name,
                "action": "DRY_RUN",
                "signal": signal,
                "price": current_price,
                "bars_fetched": len(bars),
                "pnl_usdt": sim_pnl,
                "dry_run": True,
            }
        except Exception as e:
            result = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "strategy": strategy_name,
                "action": "ERROR",
                "error": str(e),
                "pnl_usdt": 0.0,
                "dry_run": True,
            }
    else:
        result = executor.tick()
        result["ts"] = datetime.now(timezone.utc).isoformat()
        result.setdefault("pnl_usdt", 0.0)

    _log_tick(result)
    return result


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------

def cmd_tick(strategy_name: Optional[str], dry_run: bool) -> None:
    targets = [strategy_name] if strategy_name else list(STRATEGIES.keys())
    for s in targets:
        result = run_tick(s, dry_run=dry_run)
        ts = result.get("ts", "")[:19]
        signal_map = {1: "LONG", -1: "SHORT", 0: "FLAT"}
        sig = signal_map.get(result.get("signal", 0), "?")
        action = result.get("action", "?")
        price = result.get("price")
        price_str = f"${price:,.0f}" if price else "N/A"
        print(f"[{ts}] {s:25s} signal={sig:5s} action={action:20s} price={price_str}")


def cmd_status(strategy_name: Optional[str]) -> None:
    entries = _load_log()
    if not entries:
        print("No testnet log entries found.")
        return

    targets = [strategy_name] if strategy_name else list(STRATEGIES.keys())
    for s in targets:
        stats = _compute_stats(entries, s)
        if stats["tick_count"] == 0:
            print(f"{s}: no data")
            continue
        kills = _check_kills(stats)
        kill_str = "KILL" if kills else "OK"
        print(
            f"{s:25s} ticks={stats['tick_count']:3d} "
            f"pnl={stats['total_pnl_usdt']:+8.2f} USDT "
            f"mdd={stats['max_drawdown_pct']:5.1f}% "
            f"wr={stats['win_rate']:5.1%} "
            f"pf={stats['profit_factor']:6.3f} "
            f"[{kill_str}]"
        )
        if kills:
            for k in kills:
                print(f"  KILL: {k}")


def cmd_review(strategy_name: Optional[str]) -> None:
    entries = _load_log()
    targets = [strategy_name] if strategy_name else list(STRATEGIES.keys())

    print(f"\n{'='*60}")
    print("Testnet GO/NO-GO Review")
    print(f"{'='*60}")
    print(f"Kill conditions: MDD>{KILL_MAX_DRAWDOWN_PCT}%, WR<{KILL_MIN_WIN_RATE:.0%}, PF<{KILL_MIN_PROFIT_FACTOR}")
    print(f"Min ticks for review: {REVIEW_MIN_TICKS}")
    print()

    go_count = 0
    for s in targets:
        stats = _compute_stats(entries, s)
        tc = stats.get("tick_count", 0)
        if tc < REVIEW_MIN_TICKS:
            print(f"{s:25s} INSUFFICIENT_DATA ({tc}/{REVIEW_MIN_TICKS} ticks)")
            continue
        kills = _check_kills(stats)
        verdict = "GO" if not kills else "NO_GO"
        if verdict == "GO":
            go_count += 1
        print(
            f"{s:25s} {verdict:6s} "
            f"pnl={stats['total_pnl_usdt']:+.2f} USDT "
            f"mdd={stats['max_drawdown_pct']:.1f}% "
            f"wr={stats['win_rate']:.1%} "
            f"pf={stats['profit_factor']:.3f}"
        )
        for k in kills:
            print(f"  -> KILL: {k}")

    print(f"\n{'='*60}")
    if go_count == len(targets):
        print("OVERALL: GO -> Proceed to mainnet small size")
    elif go_count > 0:
        print(f"OVERALL: CONDITIONAL_GO -> {go_count}/{len(targets)} strategies pass")
    else:
        print("OVERALL: NO_GO -> Extend testnet, recalibrate")
    print(f"{'='*60}\n")


def cmd_loop(strategy_name: Optional[str], interval: int, dry_run: bool) -> None:
    print(f"Starting testnet loop: interval={interval}s, strategies={strategy_name or 'all'}")
    targets = [strategy_name] if strategy_name else list(STRATEGIES.keys())
    tick_count = 0
    try:
        while True:
            for s in targets:
                result = run_tick(s, dry_run=dry_run)
                ts = result.get("ts", "")[:19]
                sig = {1: "LONG", -1: "SHORT", 0: "FLAT"}.get(result.get("signal", 0), "?")
                logger.info("[%s] %s signal=%s action=%s", ts, s, sig, result.get("action"))
            tick_count += 1
            logger.info("Sleeping %ds (tick %d)...", interval, tick_count)
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\nLoop stopped after {tick_count} ticks.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    parser = argparse.ArgumentParser(
        description="Testnet runner for Binance USDT-M Futures"
    )
    parser.add_argument("--strategy", choices=list(STRATEGIES.keys()), help="Strategy to run (default: all)")
    parser.add_argument("--tick", action="store_true", help="Execute one tick")
    parser.add_argument("--status", action="store_true", help="Show status from log")
    parser.add_argument("--review", action="store_true", help="GO/NO-GO review")
    parser.add_argument("--loop", type=int, metavar="SECONDS", help="Run in loop with given interval")
    parser.add_argument("--dry-run", action="store_true", default=False,
                        help="Compute signals without placing orders (default when no API keys)")

    args = parser.parse_args()

    if args.tick:
        cmd_tick(args.strategy, dry_run=args.dry_run)
    elif args.status:
        cmd_status(args.strategy)
    elif args.review:
        cmd_review(args.strategy)
    elif args.loop is not None:
        cmd_loop(args.strategy, args.loop, dry_run=args.dry_run)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
