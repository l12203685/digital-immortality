#!/usr/bin/env python3
"""
Trading System CLI — Economic Self-Sufficiency Layer

Top-level entry point that ties together the trading subsystem:
  - Backtest strategies with walk-forward validation
  - Evaluate strategy health via equity curve analysis
  - Run paper trading simulations
  - Check kill conditions

Usage:
    python trading_system.py --backtest [--strategy NAME] [--timeframe TF]
    python trading_system.py --validate [--strategy NAME]
    python trading_system.py --status
    python trading_system.py --kill-check [--strategy NAME]

All strategies are filtered by DNA rules:
  - Walk-forward >= 3/5 windows
  - Sharpe > 1.0 on out-of-sample
  - Max drawdown < 20%
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from trading.backtest_framework import (
    STRATEGIES,
    TIMEFRAMES,
    generate_synthetic_bars,
    run_backtest,
    compute_metrics,
    walk_forward,
    strategy_passes_filter,
    _mean,
    _timeframe_label,
)

RESULTS_DIR = ROOT / "results"
STRATEGIES_DIR = ROOT / "strategies"

# Kill condition defaults (from trading-system.md skill doc)
DEFAULT_KILL_CONDITIONS = {
    "max_drawdown_pct": 20.0,
    "max_consecutive_losses": 8,
    "min_sharpe": 0.5,
    "mdd_deterioration_ratio": 3.0,  # current MDD / baseline MDD
}


def cmd_backtest(args):
    """Run walk-forward backtest for one or all strategies."""
    strategies = {args.strategy: STRATEGIES[args.strategy]} if args.strategy else STRATEGIES
    timeframes = [args.timeframe] if args.timeframe else list(TIMEFRAMES)

    print("=" * 64)
    print("WALK-FORWARD BACKTEST")
    print("=" * 64)
    print(f"Strategies: {list(strategies.keys())}")
    print(f"Timeframes: {timeframes}")
    print(f"Windows: {args.windows} | Min pass: {args.min_pass}/{args.windows}")
    print()

    all_results = []
    for tf in timeframes:
        n_bars = {"1h": 2000, "4h": 1000, "1d": 500}.get(tf, 500)
        ppy = _timeframe_label(tf)
        print(f"--- {tf} ({n_bars} bars) ---")

        bars = generate_synthetic_bars(n=n_bars, drift=0.0, volatility=0.02, seed=42)

        for name, fn in strategies.items():
            passed, window_results = strategy_passes_filter(
                bars, fn, n_windows=args.windows, periods_per_year=ppy,
            )
            wins = sum(1 for m in window_results if m["sharpe"] > 1.0 and m["mdd"] < 20.0)
            avg_sharpe = _mean([m["sharpe"] for m in window_results])
            avg_mdd = _mean([m["mdd"] for m in window_results])
            verdict = "PASS" if passed else "REJECT"

            print(f"  {name:20s} | {verdict:6s} | win={wins}/{args.windows} | "
                  f"sharpe={avg_sharpe:+.2f} | mdd={avg_mdd:.1f}%")

            all_results.append({
                "strategy": name,
                "timeframe": tf,
                "passed": passed,
                "windows_passed": wins,
                "avg_sharpe": round(avg_sharpe, 4),
                "avg_mdd": round(avg_mdd, 2),
                "window_details": window_results,
            })
        print()

    # Save results
    RESULTS_DIR.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = RESULTS_DIR / f"backtest_{ts}.json"
    with open(out_path, "w") as f:
        json.dump({"timestamp": ts, "results": all_results}, f, indent=2)
    print(f"Results saved: {out_path}")

    # Summary
    total = len(all_results)
    passed = sum(1 for r in all_results if r["passed"])
    print(f"\n{passed}/{total} strategy-timeframe pairs passed filter.")
    if passed == 0:
        print("Bias toward inaction: no edge found = no trade.")


def cmd_validate(args):
    """Validate a strategy with stricter walk-forward (more windows)."""
    strategies = {args.strategy: STRATEGIES[args.strategy]} if args.strategy else STRATEGIES

    print("=" * 64)
    print("STRATEGY VALIDATION (strict)")
    print("=" * 64)

    for name, fn in strategies.items():
        print(f"\n--- {name} ---")
        for tf in TIMEFRAMES:
            n_bars = {"1h": 3000, "4h": 1500, "1d": 750}.get(tf, 750)
            ppy = _timeframe_label(tf)
            bars = generate_synthetic_bars(n=n_bars, drift=0.0, volatility=0.02, seed=42)

            # Stricter: 7 windows, need 5 to pass
            passed, results = strategy_passes_filter(
                bars, fn, n_windows=7, min_passing_windows=5, periods_per_year=ppy,
            )
            wins = sum(1 for m in results if m["sharpe"] > 1.0 and m["mdd"] < 20.0)
            verdict = "PASS" if passed else "REJECT"
            print(f"  {tf}: {verdict} ({wins}/7 windows)")


def cmd_status(args):
    """Show current trading system status."""
    print("=" * 64)
    print("TRADING SYSTEM STATUS")
    print("=" * 64)

    print(f"\nAvailable strategies: {list(STRATEGIES.keys())}")
    print(f"Timeframes: {list(TIMEFRAMES)}")
    print(f"Strategies dir: {STRATEGIES_DIR}")

    # Check for recent backtest results
    if RESULTS_DIR.exists():
        backtest_files = sorted(RESULTS_DIR.glob("backtest_*.json"), reverse=True)
        if backtest_files:
            latest = backtest_files[0]
            print(f"\nLatest backtest: {latest.name}")
            with open(latest) as f:
                data = json.load(f)
            for r in data.get("results", []):
                status = "PASS" if r["passed"] else "REJECT"
                print(f"  {r['strategy']:20s} {r['timeframe']:3s} | {status} | "
                      f"sharpe={r['avg_sharpe']:+.2f}")
        else:
            print("\nNo backtests run yet. Use --backtest to start.")
    else:
        print("\nNo results directory. Use --backtest to start.")

    print(f"\nKill conditions: {json.dumps(DEFAULT_KILL_CONDITIONS, indent=2)}")
    print("\nRevenue status: NOT LIVE (synthetic data only)")
    print("Next step: Connect real market data via trading/paper_trader.py")


def cmd_kill_check(args):
    """Check if any strategy should be paused based on kill conditions."""
    strategies = {args.strategy: STRATEGIES[args.strategy]} if args.strategy else STRATEGIES
    kill = DEFAULT_KILL_CONDITIONS

    print("=" * 64)
    print("KILL CONDITION CHECK")
    print("=" * 64)

    for name, fn in strategies.items():
        # Run backtest to get current metrics
        bars = generate_synthetic_bars(n=1000, drift=0.0, volatility=0.02, seed=42)
        pnl = run_backtest(bars, fn)
        metrics = compute_metrics(pnl)

        issues = []
        if metrics["mdd"] > kill["max_drawdown_pct"]:
            issues.append(f"MDD {metrics['mdd']:.1f}% > {kill['max_drawdown_pct']}%")
        if metrics["sharpe"] < kill["min_sharpe"]:
            issues.append(f"Sharpe {metrics['sharpe']:.2f} < {kill['min_sharpe']}")

        # Check consecutive losses
        max_consec = 0
        current_consec = 0
        for r in pnl:
            if r < 0:
                current_consec += 1
                max_consec = max(max_consec, current_consec)
            else:
                current_consec = 0
        if max_consec > kill["max_consecutive_losses"]:
            issues.append(f"{max_consec} consecutive losses > {kill['max_consecutive_losses']}")

        if issues:
            print(f"\n  {name}: KILL — pause this strategy")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print(f"\n  {name}: OK — within all thresholds")
            print(f"    sharpe={metrics['sharpe']:.2f} mdd={metrics['mdd']:.1f}% "
                  f"win_rate={metrics['win_rate']:.1f}%")


def main():
    parser = argparse.ArgumentParser(
        description="Trading System CLI — Economic Self-Sufficiency Layer",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--backtest", action="store_true", help="Run walk-forward backtest")
    group.add_argument("--validate", action="store_true", help="Strict validation (7 windows)")
    group.add_argument("--status", action="store_true", help="Show system status")
    group.add_argument("--kill-check", action="store_true", help="Check kill conditions")

    parser.add_argument("--strategy", choices=list(STRATEGIES.keys()), help="Specific strategy")
    parser.add_argument("--timeframe", choices=list(TIMEFRAMES), help="Specific timeframe")
    parser.add_argument("--windows", type=int, default=5, help="Walk-forward windows (default: 5)")
    parser.add_argument("--min-pass", type=int, default=3, help="Min passing windows (default: 3)")

    args = parser.parse_args()

    if args.backtest:
        cmd_backtest(args)
    elif args.validate:
        cmd_validate(args)
    elif args.status:
        cmd_status(args)
    elif args.kill_check:
        cmd_kill_check(args)


if __name__ == "__main__":
    main()
