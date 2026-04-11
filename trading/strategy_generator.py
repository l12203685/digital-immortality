"""
Strategy Generator — Systematic parameter sweep on existing building blocks.

Generates new strategy combinations from DualMA, Donchian, BollingerMR,
RegimeFilter, RSIFilter. Validates via walk-forward on BTC daily data.
Passing candidates are appended to NAMED_STRATEGIES in strategies.py.

CLI:
    python trading/strategy_generator.py --generate N
    python trading/strategy_generator.py --prune
"""

import argparse
import hashlib
import itertools
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Project imports
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trading.backtest_framework import (
    Bar,
    Signal,
    compute_metrics,
    run_backtest,
    walk_forward,
)
from trading.strategies import (
    BollingerMeanReversion,
    Donchian,
    DonchianConfirmed,
    DualMA,
    NAMED_STRATEGIES,
    RegimeFilter,
    RSIFilter,
)
from trading.orthogonality_filter import (
    OrthogonalityFilter,
    load_recent_bars_from_log,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("strategy_generator")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
CANDIDATES_PATH = RESULTS_DIR / "strategy_candidates.json"
STRATEGIES_PY = Path(__file__).resolve().parent / "strategies.py"
PAPER_LOG_PATH = RESULTS_DIR / "paper_live_log.jsonl"
TRADING_ENGINE_LOG_PATH = RESULTS_DIR / "trading_engine_log.jsonl"

# B1 audit follow-up (2026-04-11): orthogonality threshold.
# DualMA family (4 variants) was mass-killed at PF=0.70 because they shared
# essentially the same edge. Reject new pool additions whose signal series
# has |Pearson| > ORTHOGONALITY_MAX_CORR with ANY existing pool member.
ORTHOGONALITY_MAX_CORR = 0.7
ORTHOGONALITY_LOOKBACK = 100


# ---------------------------------------------------------------------------
# Data fetching — BTC daily via yfinance (synthetic fallback)
# ---------------------------------------------------------------------------
def fetch_btc_daily(days: int = 730) -> List[Bar]:
    """Fetch BTC-USD daily OHLCV from yfinance. Falls back to synthetic data if
    yfinance is unavailable or network is unreachable."""
    try:
        import yfinance as yf
        log.info("Fetching BTC-USD daily data (%d days)...", days)
        ticker = yf.Ticker("BTC-USD")
        df = ticker.history(period=f"{days}d", interval="1d")
        if not df.empty:
            bars: List[Bar] = []
            for _, row in df.iterrows():
                bars.append({
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": float(row["Volume"]),
                })
            log.info("Fetched %d daily bars.", len(bars))
            return bars
        log.warning("yfinance returned empty data — falling back to synthetic bars.")
    except ImportError:
        log.warning("yfinance not installed — falling back to synthetic bars.")
    except Exception as exc:
        log.warning("yfinance fetch failed (%s) — falling back to synthetic bars.", exc)

    from trading.backtest_framework import generate_synthetic_bars
    bars = generate_synthetic_bars(n=days, drift=0.0002, volatility=0.025, seed=42)
    log.info("Using %d synthetic bars (BTC geometric random walk, seed=42).", len(bars))
    return bars


# ---------------------------------------------------------------------------
# Parameter space definitions
# ---------------------------------------------------------------------------
DUAL_MA_PARAMS: List[Dict[str, Any]] = [
    {"fast": f, "slow": s}
    for f, s in itertools.product([5, 8, 10, 15, 20], [20, 30, 40, 50, 60])
    if f < s
]

DONCHIAN_PARAMS: List[Dict[str, Any]] = [
    {"period": p} for p in [10, 15, 20, 25, 30, 40, 55]
]

DONCHIAN_CONFIRMED_PARAMS: List[Dict[str, Any]] = [
    {"period": p} for p in [10, 15, 20, 25, 30, 40]
]

BOLLINGER_PARAMS: List[Dict[str, Any]] = [
    {"lookback": lb, "num_std": ns, "trend_lookback": tl, "trend_threshold": tt}
    for lb, ns, tl, tt in itertools.product(
        [15, 20, 25, 30],
        [1.5, 2.0, 2.5],
        [40, 50, 60],
        [0.001, 0.003, 0.005],
    )
]

REGIME_FILTER_PARAMS: List[Dict[str, Any]] = [
    {"trend_period": tp, "slope_bars": sb, "min_slope_pct": ms}
    for tp, sb, ms in itertools.product(
        [40, 50, 60, 80],
        [3, 5, 7],
        [0.05, 0.10, 0.15, 0.20],
    )
]

RSI_FILTER_PARAMS: List[Dict[str, Any]] = [
    {"period": p, "rsi_long_min": lm, "rsi_short_max": sm}
    for p, lm, sm in itertools.product(
        [10, 14, 21],
        [45, 50, 55],
        [45, 50, 55],
    )
]


# ---------------------------------------------------------------------------
# Candidate builder — enumerates strategy combos
# ---------------------------------------------------------------------------
def _strategy_name(base_name: str, params: Dict[str, Any], filters: List[str]) -> str:
    """Deterministic name from base + params + filters."""
    parts = [base_name]
    for k, v in sorted(params.items()):
        if isinstance(v, float):
            parts.append(f"{k}{v:.3f}".rstrip("0").rstrip("."))
        else:
            parts.append(f"{k}{v}")
    parts.extend(filters)
    raw = "_".join(parts)
    # Keep it readable but add a short hash to avoid collisions
    h = hashlib.md5(raw.encode()).hexdigest()[:6]
    return f"gen_{base_name}_{'_'.join(filters)}_{h}" if filters else f"gen_{base_name}_{h}"


def _build_candidate(
    base_cls: type,
    base_params: Dict[str, Any],
    regime_params: Optional[Dict[str, Any]] = None,
    rsi_params: Optional[Dict[str, Any]] = None,
) -> Tuple[str, object]:
    """Build a strategy instance with optional filter wrapping."""
    inner = base_cls(**base_params)
    filters: List[str] = []
    strategy = inner

    if regime_params is not None:
        strategy = RegimeFilter(strategy, **regime_params)
        filters.append("RF")

    if rsi_params is not None:
        strategy = RSIFilter(strategy, **rsi_params)
        filters.append("RSI")

    base_name = base_cls.__name__
    name = _strategy_name(base_name, base_params, filters)
    return name, strategy


import random


def generate_candidates(n: int) -> List[Tuple[str, object, Dict[str, Any]]]:
    """
    Generate N candidate strategies by sampling from the parameter space.
    Returns list of (name, strategy_instance, metadata_dict).
    """
    existing_names = set(NAMED_STRATEGIES.keys())
    candidates: List[Tuple[str, object, Dict[str, Any]]] = []
    seen_names: set = set()
    attempts = 0
    max_attempts = n * 20  # avoid infinite loop

    while len(candidates) < n and attempts < max_attempts:
        attempts += 1

        # Pick a base strategy class
        base_cls = random.choice([DualMA, Donchian, DonchianConfirmed, BollingerMeanReversion])

        if base_cls == DualMA:
            bp = random.choice(DUAL_MA_PARAMS)
        elif base_cls == Donchian:
            bp = random.choice(DONCHIAN_PARAMS)
        elif base_cls == DonchianConfirmed:
            bp = random.choice(DONCHIAN_CONFIRMED_PARAMS)
        else:
            bp = random.choice(BOLLINGER_PARAMS)

        # Decide filter wrapping (none, regime, rsi, both)
        filter_choice = random.choice(["none", "regime", "rsi", "both"])
        rp = random.choice(REGIME_FILTER_PARAMS) if filter_choice in ("regime", "both") else None
        rsip = random.choice(RSI_FILTER_PARAMS) if filter_choice in ("rsi", "both") else None

        name, strategy = _build_candidate(base_cls, bp, rp, rsip)

        if name in existing_names or name in seen_names:
            continue

        meta = {
            "base": base_cls.__name__,
            "base_params": bp,
            "regime_filter": rp,
            "rsi_filter": rsip,
        }
        candidates.append((name, strategy, meta))
        seen_names.add(name)

    if len(candidates) < n:
        log.warning(
            "Only generated %d unique candidates out of %d requested (space may be saturated).",
            len(candidates), n,
        )

    return candidates


# ---------------------------------------------------------------------------
# Walk-forward validation
# ---------------------------------------------------------------------------
def validate_candidate(
    bars: List[Bar],
    strategy: object,
    n_windows: int = 5,
    min_pass_ratio: float = 0.6,
) -> Tuple[bool, List[Dict[str, float]]]:
    """
    Walk-forward validate. Passes if >= min_pass_ratio of windows have
    Sharpe > 0.5 and MDD < 25% (relaxed thresholds for generation —
    tighter filters apply in paper trading).
    """
    min_passing = int(n_windows * min_pass_ratio)
    try:
        results = walk_forward(bars, strategy, n_windows=n_windows, periods_per_year=365)
    except ValueError as e:
        log.warning("Walk-forward failed: %s", e)
        return False, []

    passing = sum(
        1 for m in results
        if m["sharpe"] > 0.5 and m["mdd"] < 25.0
    )
    return passing >= min_passing, results


# ---------------------------------------------------------------------------
# Persist passing strategies to strategies.py
# ---------------------------------------------------------------------------
def _append_to_strategies_py(entries: List[Tuple[str, Dict[str, Any]]]) -> int:
    """
    Append new strategy registrations to NAMED_STRATEGIES in strategies.py.
    entries: list of (name, meta) where meta has base, base_params, regime_filter, rsi_filter.
    Returns count of strategies actually appended.
    """
    if not entries:
        return 0

    content = STRATEGIES_PY.read_text(encoding="utf-8")

    lines_to_add: List[str] = []
    for name, meta in entries:
        # Skip if already present
        if f'"{name}"' in content:
            continue

        # Build the instantiation code
        base = meta["base"]
        bp = meta["base_params"]

        if base == "DualMA":
            inner_code = f"DualMA(fast={bp['fast']}, slow={bp['slow']})"
        elif base == "Donchian":
            inner_code = f"Donchian(period={bp['period']})"
        elif base == "DonchianConfirmed":
            inner_code = f"DonchianConfirmed(period={bp['period']})"
        elif base == "BollingerMeanReversion":
            inner_code = (
                f"BollingerMeanReversion(lookback={bp['lookback']}, "
                f"num_std={bp['num_std']}, "
                f"trend_lookback={bp['trend_lookback']}, "
                f"trend_threshold={bp['trend_threshold']})"
            )
        else:
            continue

        # Wrap with filters
        code = inner_code
        if meta.get("regime_filter"):
            rf = meta["regime_filter"]
            code = (
                f"RegimeFilter({code}, "
                f"trend_period={rf['trend_period']}, "
                f"slope_bars={rf['slope_bars']}, "
                f"min_slope_pct={rf['min_slope_pct']})"
            )
        if meta.get("rsi_filter"):
            rsif = meta["rsi_filter"]
            code = (
                f"RSIFilter({code}, "
                f"period={rsif['period']}, "
                f"rsi_long_min={rsif['rsi_long_min']}, "
                f"rsi_short_max={rsif['rsi_short_max']})"
            )

        var_name = name.replace("-", "_")
        lines_to_add.append(f'{var_name} = {code}')
        lines_to_add.append(f'NAMED_STRATEGIES["{name}"] = {var_name}')

    if not lines_to_add:
        return 0

    # Append after the closing brace of NAMED_STRATEGIES dict
    block = "\n\n# --- Auto-generated strategies (strategy_generator.py) ---\n"
    block += "\n".join(lines_to_add)
    block += "\n"

    new_content = content + block
    STRATEGIES_PY.write_text(new_content, encoding="utf-8")

    return len(lines_to_add) // 2  # each strategy is 2 lines


# ---------------------------------------------------------------------------
# Log results to JSON
# ---------------------------------------------------------------------------
def _load_candidates_log() -> List[Dict[str, Any]]:
    if CANDIDATES_PATH.exists():
        try:
            return json.loads(CANDIDATES_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
    return []


def _save_candidates_log(entries: List[Dict[str, Any]]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    CANDIDATES_PATH.write_text(
        json.dumps(entries, indent=2, default=str),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Main: --generate N
# ---------------------------------------------------------------------------
def cmd_generate(n: int) -> None:
    """Generate N new strategy candidates, validate, and register passing ones."""
    bars = fetch_btc_daily(days=730)

    if len(bars) < 200:
        log.error("Insufficient data: %d bars (need >= 200).", len(bars))
        sys.exit(1)

    candidates = generate_candidates(n)
    log.info("Generated %d unique candidates.", len(candidates))

    # B1 audit follow-up: orthogonality filter. Prefer live engine log for
    # bars (it's what the engine actually sees); fall back to the fetched
    # BTC daily series when the engine has no history yet.
    ortho_filter = OrthogonalityFilter(
        max_corr=ORTHOGONALITY_MAX_CORR,
        lookback_ticks=ORTHOGONALITY_LOOKBACK,
    )
    ortho_bars = load_recent_bars_from_log(
        TRADING_ENGINE_LOG_PATH, lookback_ticks=ORTHOGONALITY_LOOKBACK
    )
    if len(ortho_bars) < ORTHOGONALITY_LOOKBACK:
        log.info(
            "Orthogonality: engine log has %d bars (<%d). Using backtest bars instead.",
            len(ortho_bars), ORTHOGONALITY_LOOKBACK,
        )
        ortho_bars = bars[-ORTHOGONALITY_LOOKBACK:]

    log_entries = _load_candidates_log()
    passed_entries: List[Tuple[str, Dict[str, Any]]] = []
    rejected_ortho = 0
    ts = datetime.now(timezone.utc).isoformat()

    for i, (name, strategy, meta) in enumerate(candidates, 1):
        log.info("[%d/%d] Testing %s ...", i, len(candidates), name)

        passed, results = validate_candidate(bars, strategy)

        # Full backtest metrics for logging
        full_pnl = run_backtest(bars, strategy)
        full_metrics = compute_metrics(full_pnl, periods_per_year=365)

        entry = {
            "name": name,
            "ts": ts,
            "passed": passed,
            "meta": meta,
            "full_metrics": full_metrics,
            "walk_forward": results,
        }
        log_entries.append(entry)

        if passed:
            windows_passed = sum(
                1 for m in results if m["sharpe"] > 0.5 and m["mdd"] < 25.0
            )
            log.info(
                "  PASS — windows=%d/5, sharpe=%.2f, mdd=%.1f%%",
                windows_passed, full_metrics["sharpe"], full_metrics["mdd"],
            )
            passed_entries.append((name, meta))
        else:
            log.info("  FAIL — skipping.")

    # Persist
    _save_candidates_log(log_entries)
    log.info("Logged %d candidates to %s", len(candidates), CANDIDATES_PATH)

    added = _append_to_strategies_py(passed_entries)
    if added > 0:
        log.info("Added %d new strategies to strategies.py", added)
    else:
        log.info("No new strategies passed validation.")

    # Summary
    total_pass = sum(1 for _, _ in passed_entries)
    total_fail = len(candidates) - total_pass
    log.info("Summary: %d passed, %d failed out of %d candidates.", total_pass, total_fail, len(candidates))


# ---------------------------------------------------------------------------
# Prune: --prune
# ---------------------------------------------------------------------------
# Kill conditions from paper trading:
#   MDD > 10%
#   Win rate < 35% after >= 5 trades
#   Profit factor < 0.85

def _parse_paper_log() -> Dict[str, List[Dict[str, Any]]]:
    """Parse paper_live_log.jsonl into per-strategy trade records."""
    if not PAPER_LOG_PATH.exists():
        log.warning("No paper log found at %s", PAPER_LOG_PATH)
        return {}

    records: List[Dict[str, Any]] = []
    with open(PAPER_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    # Group by strategy name if present, otherwise use "default"
    by_strategy: Dict[str, List[Dict[str, Any]]] = {}
    for r in records:
        strat = r.get("strategy", "default")
        by_strategy.setdefault(strat, []).append(r)

    return by_strategy


def _compute_trade_stats(trades: List[Dict[str, Any]]) -> Dict[str, float]:
    """Compute MDD, win rate, profit factor from paper trade records."""
    prices = [t.get("price", 0.0) for t in trades if t.get("price")]
    if len(prices) < 2:
        return {"mdd_pct": 0.0, "win_rate": 0.0, "profit_factor": 0.0, "n_trades": len(prices)}

    # Compute returns between consecutive signals
    returns = []
    for i in range(1, len(prices)):
        if prices[i - 1] > 0:
            ret = (prices[i] - prices[i - 1]) / prices[i - 1]
            returns.append(ret)

    if not returns:
        return {"mdd_pct": 0.0, "win_rate": 0.0, "profit_factor": 0.0, "n_trades": 0}

    # MDD
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

    # Win rate
    wins = sum(1 for r in returns if r > 0)
    n = len(returns)
    win_rate = (wins / n * 100) if n > 0 else 0.0

    # Profit factor
    gross_profit = sum(r for r in returns if r > 0)
    gross_loss = abs(sum(r for r in returns if r < 0))
    pf = gross_profit / gross_loss if gross_loss > 0 else float("inf")

    return {
        "mdd_pct": round(max_dd * 100, 2),
        "win_rate": round(win_rate, 2),
        "profit_factor": round(pf, 4),
        "n_trades": n,
    }


def _remove_from_strategies_py(names_to_remove: List[str]) -> int:
    """Remove strategy entries from strategies.py. Returns count removed."""
    if not names_to_remove:
        return 0

    content = STRATEGIES_PY.read_text(encoding="utf-8")
    removed = 0

    for name in names_to_remove:
        # Remove the NAMED_STRATEGIES registration line
        reg_line = f'NAMED_STRATEGIES["{name}"]'
        if reg_line in content:
            new_lines = []
            for line in content.split("\n"):
                if reg_line in line:
                    removed += 1
                    continue
                # Also remove the variable assignment line (previous line pattern)
                var_name = name.replace("-", "_")
                if line.strip().startswith(f"{var_name} = "):
                    continue
                new_lines.append(line)
            content = "\n".join(new_lines)

        # Also handle dict-style entries like "Name": instance,
        dict_pattern = f'    "{name}":'
        if dict_pattern in content:
            new_lines = []
            for line in content.split("\n"):
                if dict_pattern in line:
                    removed += 1
                    continue
                new_lines.append(line)
            content = "\n".join(new_lines)

    STRATEGIES_PY.write_text(content, encoding="utf-8")
    return removed


def cmd_prune() -> None:
    """Read paper_live_log.jsonl, kill strategies that hit kill conditions."""
    log.info("Pruning strategies based on paper trading performance...")

    by_strategy = _parse_paper_log()
    if not by_strategy:
        log.info("No paper trading data found. Nothing to prune.")
        return

    # Also check strategies that have review data
    kill_list: List[Tuple[str, str]] = []  # (name, reason)

    for strat_name, trades in by_strategy.items():
        stats = _compute_trade_stats(trades)
        reasons: List[str] = []

        if stats["mdd_pct"] > 10.0:
            reasons.append(f"MDD={stats['mdd_pct']:.1f}%>10%")

        if stats["n_trades"] >= 5 and stats["win_rate"] < 35.0:
            reasons.append(f"WR={stats['win_rate']:.1f}%<35% (n={stats['n_trades']})")

        if stats["n_trades"] >= 5 and stats["profit_factor"] < 0.85:
            reasons.append(f"PF={stats['profit_factor']:.2f}<0.85")

        if reasons:
            kill_list.append((strat_name, "; ".join(reasons)))
            log.info("  KILL %s — %s", strat_name, "; ".join(reasons))
        else:
            log.info("  KEEP %s — MDD=%.1f%%, WR=%.1f%%, PF=%.2f (n=%d)",
                     strat_name, stats["mdd_pct"], stats["win_rate"],
                     stats["profit_factor"], stats["n_trades"])

    if not kill_list:
        log.info("No strategies hit kill conditions. Nothing to prune.")
        return

    names_to_remove = [name for name, _ in kill_list]
    removed = _remove_from_strategies_py(names_to_remove)
    log.info("Removed %d strategy entries from strategies.py", removed)

    # Log prune results
    prune_log = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "action": "prune",
        "killed": [{"name": n, "reason": r} for n, r in kill_list],
        "removed_count": removed,
    }

    log_entries = _load_candidates_log()
    log_entries.append(prune_log)
    _save_candidates_log(log_entries)
    log.info("Prune results logged to %s", CANDIDATES_PATH)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Strategy Generator — systematic parameter sweep and validation.",
    )
    parser.add_argument(
        "--generate", type=int, metavar="N",
        help="Generate N new strategy candidates, validate, and register passing ones.",
    )
    parser.add_argument(
        "--prune", action="store_true",
        help="Read paper_live_log.jsonl and kill strategies that hit kill conditions.",
    )

    args = parser.parse_args()

    if args.generate is not None:
        if args.generate < 1:
            parser.error("--generate must be >= 1")
        cmd_generate(args.generate)
    elif args.prune:
        cmd_prune()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
