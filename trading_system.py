#!/usr/bin/env python3
"""
Trading System CLI — Economic Self-Sufficiency Layer

Top-level entry point that ties together the trading subsystem:
  - Backtest strategies with walk-forward validation
  - Evaluate strategy health via equity curve analysis
  - Run paper trading simulations (live data from Binance, no auth)
  - Check kill conditions

Usage:
    python trading_system.py --backtest [--strategy NAME] [--timeframe TF]
    python trading_system.py --validate [--strategy NAME]
    python trading_system.py --paper [--strategy NAME] [--timeframe TF] [--ticks N]
    python trading_system.py --status
    python trading_system.py --kill-check [--strategy NAME]

All strategies are filtered by DNA rules:
  - Walk-forward >= 3/5 windows
  - Sharpe > 1.0 on out-of-sample
  - Max drawdown < 20%
"""

import argparse
import csv
import json
import logging
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
from trading.paper_trader import PaperTrader
from trading.strategies import NAMED_STRATEGIES

# Merge both strategy dicts so --strategy can reference either set.
# NAMED_STRATEGIES keys (e.g. "DualMA_10_30") take precedence on collision.
ALL_STRATEGIES = {**STRATEGIES, **NAMED_STRATEGIES}

RESULTS_DIR = ROOT / "results"
STRATEGIES_DIR = ROOT / "strategies"

# Kill condition defaults (from trading-system.md skill doc)
DEFAULT_KILL_CONDITIONS = {
    "max_drawdown_pct": 20.0,
    "max_consecutive_losses": 8,
    "min_sharpe": 0.5,
    "mdd_deterioration_ratio": 3.0,  # current MDD / baseline MDD
}


# ---------------------------------------------------------------------------
# Real market data loading
# ---------------------------------------------------------------------------

OHLCV_COLUMNS = {"date", "open", "high", "low", "close", "volume"}
CLOSE_ONLY_COLUMNS = {"date", "close"}


def load_market_data(path: str, data_format: str = "ohlcv"):
    """
    Load market data from a CSV file and return a list of Bar dicts.

    Supported formats:
      - "ohlcv": columns date, open, high, low, close, volume
      - "close-only": columns date, close (open/high/low set to close, volume=0)

    Validates:
      - Required columns exist
      - No NaN/empty values in critical fields
      - Dates are in chronological order
    """
    filepath = Path(path)
    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found: {path}")

    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"CSV file is empty or has no header: {path}")

        headers = {h.strip().lower() for h in reader.fieldnames}

        if data_format == "ohlcv":
            required = OHLCV_COLUMNS
        elif data_format == "close-only":
            required = CLOSE_ONLY_COLUMNS
        else:
            raise ValueError(f"Unknown data format: {data_format!r}. Use 'ohlcv' or 'close-only'.")

        missing = required - headers
        if missing:
            raise ValueError(
                f"CSV missing required columns for {data_format!r} format: {sorted(missing)}. "
                f"Found: {sorted(headers)}"
            )

        rows = list(reader)

    if not rows:
        raise ValueError(f"CSV file has no data rows: {path}")

    # Build a column-name mapping (handles whitespace in headers)
    def _col(row, name):
        for k, v in row.items():
            if k.strip().lower() == name:
                return v
        return None

    # Parse and validate rows
    bars = []
    prev_date = None
    for i, row in enumerate(rows, start=2):  # line 2 = first data row
        date_str = _col(row, "date")
        if date_str is None or date_str.strip() == "":
            raise ValueError(f"Row {i}: missing or empty 'date' value")
        date_str = date_str.strip()

        # Chronological order check
        if prev_date is not None and date_str < prev_date:
            raise ValueError(
                f"Row {i}: dates not in chronological order "
                f"({date_str!r} < {prev_date!r}). Sort your CSV by date ascending."
            )
        prev_date = date_str

        if data_format == "ohlcv":
            numeric_fields = ["open", "high", "low", "close", "volume"]
        else:
            numeric_fields = ["close"]

        values = {}
        for field in numeric_fields:
            raw = _col(row, field)
            if raw is None or raw.strip() == "":
                raise ValueError(f"Row {i}: missing or empty '{field}' value")
            try:
                values[field] = float(raw)
            except ValueError:
                raise ValueError(f"Row {i}: '{field}' is not a valid number: {raw!r}")

        if data_format == "close-only":
            c = values["close"]
            bar = {"open": c, "high": c, "low": c, "close": c, "volume": 0.0}
        else:
            bar = {
                "open": values["open"],
                "high": values["high"],
                "low": values["low"],
                "close": values["close"],
                "volume": values["volume"],
            }
        bars.append(bar)

    return bars


def cmd_backtest(args):
    """Run walk-forward backtest for one or all strategies."""
    strategies = {args.strategy: ALL_STRATEGIES[args.strategy]} if args.strategy else STRATEGIES
    timeframes = [args.timeframe] if args.timeframe else list(TIMEFRAMES)

    # Load real data if provided
    real_bars = None
    if args.data:
        real_bars = load_market_data(args.data, args.data_format)
        print(f"Loaded {len(real_bars)} bars from {args.data} (format: {args.data_format})")

    print("=" * 64)
    print("WALK-FORWARD BACKTEST")
    print("=" * 64)
    print(f"Strategies: {list(strategies.keys())}")
    print(f"Timeframes: {timeframes}")
    print(f"Data source: {args.data or 'synthetic'}")
    print(f"Windows: {args.windows} | Min pass: {args.min_pass}/{args.windows}")
    print()

    all_results = []
    for tf in timeframes:
        ppy = _timeframe_label(tf)

        if real_bars is not None:
            bars = real_bars
            print(f"--- {tf} ({len(bars)} bars from file) ---")
        else:
            n_bars = {"1h": 2000, "4h": 1000, "1d": 500}.get(tf, 500)
            bars = generate_synthetic_bars(n=n_bars, drift=0.0, volatility=0.02, seed=42)
            print(f"--- {tf} ({n_bars} bars, synthetic) ---")

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
    strategies = {args.strategy: ALL_STRATEGIES[args.strategy]} if args.strategy else STRATEGIES

    real_bars = None
    if args.data:
        real_bars = load_market_data(args.data, args.data_format)
        print(f"Loaded {len(real_bars)} bars from {args.data} (format: {args.data_format})")

    print("=" * 64)
    print("STRATEGY VALIDATION (strict)")
    print("=" * 64)

    for name, fn in strategies.items():
        print(f"\n--- {name} ---")
        for tf in TIMEFRAMES:
            ppy = _timeframe_label(tf)
            if real_bars is not None:
                bars = real_bars
            else:
                n_bars = {"1h": 3000, "4h": 1500, "1d": 750}.get(tf, 750)
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


def cmd_paper(args):
    """Run paper trading on live Binance data (no auth needed)."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    # Determine which strategies to run
    if args.strategy:
        if args.strategy in ALL_STRATEGIES:
            strats = {args.strategy: ALL_STRATEGIES[args.strategy]}
        else:
            print(f"ERROR: unknown strategy {args.strategy!r}")
            print(f"Available: {sorted(ALL_STRATEGIES.keys())}")
            sys.exit(1)
    else:
        # Default: run the named (paper-ready) strategies
        strats = dict(NAMED_STRATEGIES)

    interval = args.timeframe or "1d"
    ticks = args.ticks

    print("=" * 64)
    print("PAPER TRADING — live data from Binance (no auth)")
    print("=" * 64)
    print(f"Strategies : {list(strats.keys())}")
    print(f"Interval   : {interval}")
    print(f"Ticks      : {ticks}")
    print()

    RESULTS_DIR.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    all_entries = {}  # strategy_name -> list of tick entries

    for name, fn in strats.items():
        log_path = RESULTS_DIR / f"paper_{name}_{ts}.jsonl"
        pt = PaperTrader(
            strategy=fn,
            name=name,
            symbol="BTCUSDT",
            interval=interval,
            log_path=str(log_path),
        )

        print(f"--- {name} ---")
        entries = []
        for tick_num in range(1, ticks + 1):
            try:
                entry = pt.run_once()
            except Exception as exc:
                # Catch network / connection errors gracefully
                exc_name = type(exc).__name__
                print(f"  [tick {tick_num}] OFFLINE — could not reach Binance: {exc_name}: {exc}")
                print("  Paper trader is structurally ready; it needs network access to fetch live klines.")
                print(f"  Hint: ensure api.binance.com is reachable and not blocked by a firewall.")
                break
            else:
                if not entry:
                    print(f"  [tick {tick_num}] No bars returned — skipping.")
                    continue
                entries.append(entry)
                signal_str = {1: "LONG", -1: "SHORT", 0: "FLAT"}.get(entry.get("signal"), "?")
                action = entry.get("action", "?")
                price = entry.get("price", 0)
                pnl = entry.get("pnl")
                capital = entry.get("capital")
                pnl_str = f"  pnl={pnl:+.4f}%" if pnl is not None else ""
                cap_str = f"  capital={capital}" if capital is not None else ""
                print(f"  [tick {tick_num}] price={price:.2f}  signal={signal_str}  "
                      f"action={action}{pnl_str}{cap_str}")
        else:
            # Only reached if the loop completed without break
            print(f"  Log: {log_path}")

        all_entries[name] = entries
        print()

    # Print summary
    print("=" * 64)
    print("SUMMARY")
    print("=" * 64)
    for name, entries in all_entries.items():
        if not entries:
            print(f"  {name}: no data (offline or no bars)")
            continue
        actions = [e.get("action", "?") for e in entries]
        signals = [e.get("signal", 0) for e in entries]
        pnl_vals = [e.get("pnl", 0) for e in entries if "pnl" in e]
        n_trades = sum(1 for a in actions if a not in ("HOLD", "?"))
        last_signal = {1: "LONG", -1: "SHORT", 0: "FLAT"}.get(signals[-1], "?")
        total_pnl = sum(pnl_vals) if pnl_vals else 0.0
        last_capital = entries[-1].get("capital")
        cap_str = f"  capital={last_capital}" if last_capital is not None else ""
        print(f"  {name}: {len(entries)} tick(s) | {n_trades} signal change(s) | "
              f"last_signal={last_signal} | total_pnl={total_pnl:+.4f}%{cap_str}")


def cmd_kill_check(args):
    """Check if any strategy should be paused based on kill conditions."""
    strategies = {args.strategy: ALL_STRATEGIES[args.strategy]} if args.strategy else STRATEGIES
    kill = DEFAULT_KILL_CONDITIONS

    print("=" * 64)
    print("KILL CONDITION CHECK")
    print("=" * 64)

    real_bars = None
    if args.data:
        real_bars = load_market_data(args.data, args.data_format)
        print(f"Loaded {len(real_bars)} bars from {args.data} (format: {args.data_format})")

    for name, fn in strategies.items():
        # Run backtest to get current metrics
        if real_bars is not None:
            bars = real_bars
        else:
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
    group.add_argument("--paper", action="store_true", help="Paper trade on live Binance data (no auth)")
    group.add_argument("--status", action="store_true", help="Show system status")
    group.add_argument("--kill-check", action="store_true", help="Check kill conditions")

    parser.add_argument("--strategy", choices=sorted(ALL_STRATEGIES.keys()), help="Specific strategy")
    parser.add_argument("--timeframe", choices=list(TIMEFRAMES), help="Specific timeframe")
    parser.add_argument("--ticks", type=int, default=1, help="Number of paper trading ticks (default: 1)")
    parser.add_argument("--windows", type=int, default=5, help="Walk-forward windows (default: 5)")
    parser.add_argument("--min-pass", type=int, default=3, help="Min passing windows (default: 3)")
    parser.add_argument("--data", metavar="PATH", help="Path to CSV file with market data (replaces synthetic data)")
    parser.add_argument("--data-format", choices=["ohlcv", "close-only"], default="ohlcv",
                        help="CSV format: 'ohlcv' (date,open,high,low,close,volume) or 'close-only' (date,close). Default: ohlcv")

    args = parser.parse_args()

    if args.backtest:
        cmd_backtest(args)
    elif args.validate:
        cmd_validate(args)
    elif args.paper:
        cmd_paper(args)
    elif args.status:
        cmd_status(args)
    elif args.kill_check:
        cmd_kill_check(args)


if __name__ == "__main__":
    main()
