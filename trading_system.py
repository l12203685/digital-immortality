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
    python trading_system.py --performance
    python trading_system.py --track

All strategies are filtered by DNA rules:
  - Walk-forward >= 3/5 windows
  - Sharpe > 1.0 on out-of-sample
  - Max drawdown < 20%
"""

import argparse
import csv
import json
import logging
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# Trading module imports are deferred so that commands that only read result
# files (--performance, --track) work even when the trading package is absent.
_trading_loaded = False
STRATEGIES = {}
TIMEFRAMES = ("1h", "4h", "1d")
ALL_STRATEGIES = {}


def _ensure_trading_imports():
    """Import the trading package on first use. Raises if unavailable."""
    global _trading_loaded, STRATEGIES, TIMEFRAMES, ALL_STRATEGIES
    if _trading_loaded:
        return
    from trading.backtest_framework import (
        STRATEGIES as _STRATS,
        TIMEFRAMES as _TFS,
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

    STRATEGIES.update(_STRATS)
    TIMEFRAMES = _TFS
    # Merge both strategy dicts so --strategy can reference either set.
    # NAMED_STRATEGIES keys (e.g. "DualMA_10_30") take precedence on collision.
    ALL_STRATEGIES.update({**STRATEGIES, **NAMED_STRATEGIES})

    # Stash into module globals for cmd_ functions
    import trading_system as _self
    _self.STRATEGIES = STRATEGIES
    _self.TIMEFRAMES = TIMEFRAMES
    _self.ALL_STRATEGIES = ALL_STRATEGIES
    _self.generate_synthetic_bars = generate_synthetic_bars
    _self.run_backtest = run_backtest
    _self.compute_metrics = compute_metrics
    _self.walk_forward = walk_forward
    _self.strategy_passes_filter = strategy_passes_filter
    _self._mean = _mean
    _self._timeframe_label = _timeframe_label
    _self.PaperTrader = PaperTrader
    _self.NAMED_STRATEGIES = NAMED_STRATEGIES

    _trading_loaded = True

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
    _ensure_trading_imports()
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
    _ensure_trading_imports()
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
    _ensure_trading_imports()
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
    _ensure_trading_imports()
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


# ---------------------------------------------------------------------------
# Performance tracking helpers
# ---------------------------------------------------------------------------

def _safe_mean(xs):
    """Mean of a list, returning 0.0 for empty lists."""
    return sum(xs) / len(xs) if xs else 0.0


def _compute_sharpe(returns, periods_per_year=365):
    """Annualised Sharpe ratio from a list of per-period returns."""
    if len(returns) < 2:
        return 0.0
    mu = _safe_mean(returns)
    variance = sum((r - mu) ** 2 for r in returns) / (len(returns) - 1)
    sigma = math.sqrt(variance)
    if sigma == 0:
        return 0.0
    return (mu / sigma) * math.sqrt(periods_per_year)


def _compute_max_drawdown(returns):
    """Max drawdown (as percentage) from a list of per-period returns."""
    if not returns:
        return 0.0
    cumulative = 0.0
    peak = 0.0
    max_dd = 0.0
    for r in returns:
        cumulative += r
        if cumulative > peak:
            peak = cumulative
        dd = peak - cumulative
        if dd > max_dd:
            max_dd = dd
    return round(max_dd * 100, 2)


def _load_backtest_files():
    """Load all backtest result files, returning a list of per-strategy-timeframe records."""
    records = []
    if not RESULTS_DIR.exists():
        return records
    for path in sorted(RESULTS_DIR.glob("backtest_*.json")):
        try:
            with open(path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        timestamp = data.get("timestamp", "")
        for r in data.get("results", []):
            r["source_file"] = path.name
            r["source_timestamp"] = timestamp
            r["source_type"] = "backtest"
            records.append(r)
    return records


def _load_paper_files():
    """Load all paper trading JSONL files, returning entries grouped by strategy name."""
    strategy_entries = {}  # strategy_name -> list of tick entries
    if not RESULTS_DIR.exists():
        return strategy_entries
    for path in sorted(RESULTS_DIR.glob("paper_*.jsonl")):
        try:
            with open(path) as f:
                lines = f.readlines()
        except OSError:
            continue
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            name = entry.get("strategy", "unknown")
            strategy_entries.setdefault(name, []).append(entry)
    return strategy_entries


def _aggregate_backtest_stats(records):
    """
    Aggregate backtest records per strategy.
    Returns dict: strategy_name -> aggregated metrics.
    """
    by_strategy = {}
    for r in records:
        name = r.get("strategy", "unknown")
        by_strategy.setdefault(name, []).append(r)

    aggregated = {}
    for name, runs in by_strategy.items():
        total_sessions = len(runs)
        pass_count = sum(1 for r in runs if r.get("passed", False))

        # Collect all window-level metrics across all sessions
        all_sharpes = []
        all_mdds = []
        all_win_rates = []
        all_profit_factors = []
        for r in runs:
            for w in r.get("window_details", []):
                all_sharpes.append(w.get("sharpe", 0.0))
                all_mdds.append(w.get("mdd", 0.0))
                all_win_rates.append(w.get("win_rate", 0.0))
                all_profit_factors.append(w.get("profit_factor", 0.0))

        aggregated[name] = {
            "source": "backtest",
            "total_sessions": total_sessions,
            "sessions_passed": pass_count,
            "pass_rate": round(pass_count / total_sessions * 100, 1) if total_sessions else 0.0,
            "total_windows": len(all_sharpes),
            "avg_sharpe": round(_safe_mean(all_sharpes), 4),
            "avg_mdd": round(_safe_mean(all_mdds), 2),
            "avg_win_rate": round(_safe_mean(all_win_rates), 2),
            "avg_profit_factor": round(_safe_mean(all_profit_factors), 4),
            "best_sharpe": round(max(all_sharpes), 4) if all_sharpes else 0.0,
            "worst_sharpe": round(min(all_sharpes), 4) if all_sharpes else 0.0,
            "max_mdd": round(max(all_mdds), 2) if all_mdds else 0.0,
        }
    return aggregated


def _aggregate_paper_stats(strategy_entries):
    """
    Aggregate paper trading entries per strategy.
    Returns dict: strategy_name -> aggregated metrics.
    """
    aggregated = {}
    for name, entries in strategy_entries.items():
        # Extract PnL values (as fractional returns for Sharpe/drawdown calc)
        pnl_pcts = [e["pnl"] for e in entries if "pnl" in e]
        # Convert from percentage to fractional for internal math
        pnl_fractions = [p / 100.0 for p in pnl_pcts]

        total_ticks = len(entries)
        trades = sum(1 for e in entries if e.get("action") not in ("HOLD", "?", None))
        wins = sum(1 for p in pnl_pcts if p > 0)
        losses = sum(1 for p in pnl_pcts if p < 0)
        total_return = sum(pnl_pcts)
        avg_return = _safe_mean(pnl_pcts) if pnl_pcts else 0.0

        aggregated[name] = {
            "source": "paper",
            "total_ticks": total_ticks,
            "total_trades": trades,
            "ticks_with_pnl": len(pnl_pcts),
            "wins": wins,
            "losses": losses,
            "win_rate": round(wins / len(pnl_pcts) * 100, 2) if pnl_pcts else 0.0,
            "total_return_pct": round(total_return, 4),
            "avg_return_pct": round(avg_return, 4),
            "sharpe": round(_compute_sharpe(pnl_fractions), 4),
            "max_drawdown_pct": _compute_max_drawdown(pnl_fractions),
            "best_tick_pct": round(max(pnl_pcts), 4) if pnl_pcts else 0.0,
            "worst_tick_pct": round(min(pnl_pcts), 4) if pnl_pcts else 0.0,
        }

        # Include final capital if available
        capitals = [e["capital"] for e in entries if "capital" in e]
        if capitals:
            aggregated[name]["final_capital"] = capitals[-1]

    return aggregated


def cmd_performance(args):
    """Aggregate and display performance across all backtest and paper trading sessions."""
    backtest_records = _load_backtest_files()
    paper_entries = _load_paper_files()

    if not backtest_records and not paper_entries:
        print("No results found. Run --backtest or --paper first.")
        return

    backtest_stats = _aggregate_backtest_stats(backtest_records)
    paper_stats = _aggregate_paper_stats(paper_entries)

    # Collect all strategy names
    all_strategies = sorted(set(list(backtest_stats.keys()) + list(paper_stats.keys())))

    print("=" * 80)
    print("STRATEGY PERFORMANCE SUMMARY")
    print("=" * 80)

    # --- Backtest section ---
    if backtest_stats:
        print("\n--- Backtest Performance ---")
        print(f"  {'Strategy':<22s} {'Sessions':>8s} {'Pass%':>7s} {'AvgSharpe':>10s} "
              f"{'AvgMDD%':>8s} {'WinRate%':>9s} {'ProfitF':>8s}")
        print("  " + "-" * 76)
        for name in sorted(backtest_stats.keys()):
            s = backtest_stats[name]
            print(f"  {name:<22s} {s['total_sessions']:>8d} {s['pass_rate']:>6.1f}% "
                  f"{s['avg_sharpe']:>+10.2f} {s['avg_mdd']:>7.1f}% "
                  f"{s['avg_win_rate']:>8.1f}% {s['avg_profit_factor']:>8.2f}")
        print()
        # Detail: Sharpe range and max drawdown
        print(f"  {'Strategy':<22s} {'BestSharpe':>11s} {'WorstSharpe':>12s} {'MaxMDD%':>8s} {'Windows':>8s}")
        print("  " + "-" * 63)
        for name in sorted(backtest_stats.keys()):
            s = backtest_stats[name]
            print(f"  {name:<22s} {s['best_sharpe']:>+11.2f} {s['worst_sharpe']:>+12.2f} "
                  f"{s['max_mdd']:>7.1f}% {s['total_windows']:>8d}")

    # --- Paper trading section ---
    if paper_stats:
        print("\n--- Paper Trading Performance ---")
        print(f"  {'Strategy':<22s} {'Ticks':>6s} {'Trades':>7s} {'WinRate%':>9s} "
              f"{'TotalRet%':>10s} {'AvgRet%':>8s} {'Sharpe':>7s} {'MaxDD%':>7s}")
        print("  " + "-" * 78)
        for name in sorted(paper_stats.keys()):
            s = paper_stats[name]
            print(f"  {name:<22s} {s['total_ticks']:>6d} {s['total_trades']:>7d} "
                  f"{s['win_rate']:>8.1f}% {s['total_return_pct']:>+9.4f}% "
                  f"{s['avg_return_pct']:>+7.4f}% {s['sharpe']:>+6.2f} "
                  f"{s['max_drawdown_pct']:>6.2f}%")
        print()
        print(f"  {'Strategy':<22s} {'BestTick%':>10s} {'WorstTick%':>11s} {'FinalCap':>10s}")
        print("  " + "-" * 55)
        for name in sorted(paper_stats.keys()):
            s = paper_stats[name]
            cap_str = f"{s['final_capital']:>10.2f}" if "final_capital" in s else "       N/A"
            print(f"  {name:<22s} {s['best_tick_pct']:>+10.4f} {s['worst_tick_pct']:>+11.4f} {cap_str}")

    # --- Combined ranking ---
    if backtest_stats or paper_stats:
        print("\n--- Combined Strategy Ranking (by Sharpe) ---")
        ranking = []
        for name, s in backtest_stats.items():
            ranking.append((name, "backtest", s["avg_sharpe"], s["avg_mdd"], s.get("avg_win_rate", 0)))
        for name, s in paper_stats.items():
            ranking.append((name, "paper", s["sharpe"], s["max_drawdown_pct"], s.get("win_rate", 0)))
        ranking.sort(key=lambda x: x[2], reverse=True)

        print(f"  {'#':>3s} {'Strategy':<22s} {'Source':>8s} {'Sharpe':>8s} {'MDD%':>7s} {'WinRate%':>9s}")
        print("  " + "-" * 59)
        for i, (name, source, sharpe, mdd, wr) in enumerate(ranking, 1):
            print(f"  {i:>3d} {name:<22s} {source:>8s} {sharpe:>+8.2f} {mdd:>6.1f}% {wr:>8.1f}%")

    # Save aggregated stats
    RESULTS_DIR.mkdir(exist_ok=True)
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "backtest": backtest_stats,
        "paper": paper_stats,
    }
    out_path = RESULTS_DIR / "strategy_performance.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nAggregated stats saved: {out_path}")


def cmd_track(args):
    """Append current session metrics to the running performance log."""
    backtest_records = _load_backtest_files()
    paper_entries = _load_paper_files()

    if not backtest_records and not paper_entries:
        print("No results to track. Run --backtest or --paper first.")
        return

    backtest_stats = _aggregate_backtest_stats(backtest_records)
    paper_stats = _aggregate_paper_stats(paper_entries)

    RESULTS_DIR.mkdir(exist_ok=True)
    log_path = RESULTS_DIR / "performance_log.jsonl"

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "backtest_files": len(list(RESULTS_DIR.glob("backtest_*.json"))),
        "paper_files": len(list(RESULTS_DIR.glob("paper_*.jsonl"))),
        "strategies": {},
    }

    # Combine backtest and paper stats into a single per-strategy summary
    all_names = sorted(set(list(backtest_stats.keys()) + list(paper_stats.keys())))
    for name in all_names:
        strat_summary = {}
        if name in backtest_stats:
            bs = backtest_stats[name]
            strat_summary["backtest"] = {
                "sessions": bs["total_sessions"],
                "pass_rate": bs["pass_rate"],
                "avg_sharpe": bs["avg_sharpe"],
                "avg_mdd": bs["avg_mdd"],
                "avg_win_rate": bs["avg_win_rate"],
            }
        if name in paper_stats:
            ps = paper_stats[name]
            strat_summary["paper"] = {
                "ticks": ps["total_ticks"],
                "trades": ps["total_trades"],
                "win_rate": ps["win_rate"],
                "total_return_pct": ps["total_return_pct"],
                "sharpe": ps["sharpe"],
                "max_drawdown_pct": ps["max_drawdown_pct"],
            }
        entry["strategies"][name] = strat_summary

    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"Performance snapshot appended to: {log_path}")
    print(f"Timestamp: {entry['timestamp']}")
    print(f"Strategies tracked: {len(all_names)}")
    for name in all_names:
        parts = []
        if name in backtest_stats:
            bs = backtest_stats[name]
            parts.append(f"backtest: sharpe={bs['avg_sharpe']:+.2f}, pass={bs['pass_rate']:.0f}%")
        if name in paper_stats:
            ps = paper_stats[name]
            parts.append(f"paper: sharpe={ps['sharpe']:+.2f}, ret={ps['total_return_pct']:+.4f}%")
        print(f"  {name}: {' | '.join(parts)}")

    # Show log history count
    try:
        with open(log_path) as f:
            n_entries = sum(1 for line in f if line.strip())
        print(f"\nTotal snapshots in log: {n_entries}")
    except OSError:
        pass


def cmd_kill_check(args):
    """Check if any strategy should be paused based on kill conditions."""
    _ensure_trading_imports()
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
    group.add_argument("--performance", action="store_true",
                       help="Show aggregated performance across all backtest/paper sessions")
    group.add_argument("--track", action="store_true",
                       help="Append current metrics snapshot to performance log")

    parser.add_argument("--strategy", help="Specific strategy name")
    parser.add_argument("--timeframe", choices=["1h", "4h", "1d"], help="Specific timeframe")
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
    elif args.performance:
        cmd_performance(args)
    elif args.track:
        cmd_track(args)


if __name__ == "__main__":
    main()
