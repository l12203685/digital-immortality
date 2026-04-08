#!/usr/bin/env python3
"""
4/14 Paper Trader Review — go/no-go decision artifact.

Runs DualMA and Donchian on synthetic BTC-like data across 3 regimes
(trending, mean-reverting, mixed). Applies DNA kill conditions.
Saves a markdown report + JSON data to results/.

Usage:
    python trading/paper_trader_review.py
    python trading/paper_trader_review.py --output-dir results --bars 600
"""

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Internal imports
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent))

from trading.backtest_framework import (
    Bar,
    compute_metrics,
    run_backtest,
    walk_forward,
)
from trading.strategies import DualMA, Donchian, RegimeFilter
from tools.generate_market_data import (
    generate_trending,
    generate_mean_reverting,
    generate_mixed,
)

# ---------------------------------------------------------------------------
# Kill conditions (from dna_core.md trading rules)
# ---------------------------------------------------------------------------
KILL_CONDITIONS = {
    # Kill = strategy is actively destroying capital, not just underperforming.
    # Primary regimes only. Threshold is "stop loss", not "go-live bar".
    "min_sharpe": 0.0,        # negative Sharpe = systematic loss → kill
    "max_mdd_pct": 20.0,      # hard drawdown cap
    "min_profit_factor": 0.85, # PF below this = losing consistently → kill
    "min_win_rate_pct": 35.0, # < 35% = edge-less → kill
}

PASS_CRITERIA = {
    "min_sharpe": 1.0,        # target Sharpe for go-live
    "max_mdd_pct": 15.0,      # tighter MDD for live
    "min_profit_factor": 1.1,
}

# Regime map: which regimes each strategy TYPE is expected to work in.
# Trend-followers should not be penalized on mean-reverting data.
STRATEGY_REGIME_MAP = {
    "DualMA": ["trending", "mixed"],            # trend-following: expect to fail MR
    "Donchian": ["trending", "mixed"],          # breakout: expect to fail MR
    "DonchianConfirmed": ["trending", "mixed"], # confirmed breakout: expect to fail MR
    "MeanReversion": ["mean_reverting", "mixed"],
    "DEFAULT": ["trending", "mean_reverting", "mixed"],  # evaluate all
}

def _get_primary_regimes(strat_name: str) -> List[str]:
    """Return regimes this strategy is expected to perform in."""
    for key, regimes in STRATEGY_REGIME_MAP.items():
        if key in strat_name:
            return regimes
    return STRATEGY_REGIME_MAP["DEFAULT"]


# ---------------------------------------------------------------------------
# Core evaluation
# ---------------------------------------------------------------------------

def evaluate_strategy(
    strategy,
    bars: List[Bar],
    regime: str,
    n_windows: int = 5,
) -> Dict:
    """Walk-forward evaluate one strategy on one regime dataset."""
    window_results = walk_forward(bars, strategy, n_windows=n_windows)

    # Aggregate
    sharpes = [w["sharpe"] for w in window_results]
    mdds = [w["mdd"] for w in window_results]
    win_rates = [w["win_rate"] for w in window_results]
    pfs = [w["profit_factor"] for w in window_results if w["profit_factor"] != float("inf")]

    avg_sharpe = sum(sharpes) / len(sharpes)
    avg_mdd = sum(mdds) / len(mdds)
    avg_win_rate = sum(win_rates) / len(win_rates)
    avg_pf = sum(pfs) / len(pfs) if pfs else float("inf")

    # Per-window pass count
    windows_passed = sum(
        1 for w in window_results
        if w["sharpe"] > PASS_CRITERIA["min_sharpe"]
        and w["mdd"] < PASS_CRITERIA["max_mdd_pct"]
    )

    # Kill check.
    # Win rate kill only triggers when PF is also below kill threshold —
    # trend-following strategies naturally have low win rates but large winners.
    # A strategy with PF > 1.0 is generating profit regardless of win rate.
    win_rate_kill = (
        avg_win_rate < KILL_CONDITIONS["min_win_rate_pct"]
        and avg_pf < KILL_CONDITIONS["min_profit_factor"]
    )
    kill_triggered = (
        avg_sharpe < KILL_CONDITIONS["min_sharpe"]
        or avg_mdd > KILL_CONDITIONS["max_mdd_pct"]
        or avg_pf < KILL_CONDITIONS["min_profit_factor"]
        or win_rate_kill
    )

    return {
        "regime": regime,
        "avg_sharpe": round(avg_sharpe, 4),
        "avg_mdd": round(avg_mdd, 2),
        "avg_win_rate": round(avg_win_rate, 2),
        "avg_profit_factor": round(avg_pf, 4) if avg_pf != float("inf") else None,
        "windows_passed": windows_passed,
        "n_windows": n_windows,
        "kill_triggered": kill_triggered,
        "window_details": window_results,
    }


def run_full_review(bars_per_regime: int = 500) -> Dict:
    """Run all strategies on all regimes. Return structured review data."""
    strategies = {
        "DualMA(fast=10,slow=30)": DualMA(fast=10, slow=30),
        "Donchian(period=20)": Donchian(period=20),
        "DualMA+RegimeFilter": RegimeFilter(DualMA(fast=10, slow=30), trend_period=50, min_slope_pct=0.10),
        "Donchian+RegimeFilter": RegimeFilter(Donchian(period=20), trend_period=50, min_slope_pct=0.10),
    }
    regimes = {
        "trending": generate_trending(n=bars_per_regime, seed=101),
        "mean_reverting": generate_mean_reverting(n=bars_per_regime, seed=202),
        "mixed": generate_mixed(n=bars_per_regime, seed=303),
    }

    results = {}
    for strat_name, strategy in strategies.items():
        results[strat_name] = {}
        for regime_name, bars in regimes.items():
            results[strat_name][regime_name] = evaluate_strategy(
                strategy, bars, regime_name
            )

    return results


def _strategy_decision(strat_name: str, regime_results: Dict) -> Tuple[str, int, int]:
    """Return (decision, kills, evals) for one strategy's primary regimes."""
    primary_regimes = _get_primary_regimes(strat_name)
    kills = 0
    evals = 0
    strong_passes = 0
    for regime_name, r in regime_results.items():
        if regime_name not in primary_regimes:
            continue
        evals += 1
        if r["kill_triggered"]:
            kills += 1
        if r["avg_sharpe"] > PASS_CRITERIA["min_sharpe"] and not r["kill_triggered"]:
            strong_passes += 1
    if evals == 0:
        return "NO_GO", 0, 0
    kill_rate = kills / evals
    if kill_rate == 0.0 and strong_passes >= 1:
        return "GO", kills, evals
    elif kill_rate <= 0.5:
        return "CONDITIONAL_GO", kills, evals
    else:
        return "NO_GO", kills, evals


def make_go_no_go(results: Dict) -> Tuple[str, str]:
    """
    Per-strategy decision, then pick best outcome across strategies.
    A single strategy with GO upgrades overall to GO (one good enough is enough).
    Trend-following strategies are not penalized on mean-reverting data.
    Decision: GO / CONDITIONAL_GO / NO_GO
    """
    go_strats = []
    cgo_strats = []
    nogo_strats = []

    for strat_name, regime_results in results.items():
        decision, kills, evals = _strategy_decision(strat_name, regime_results)
        if decision == "GO":
            go_strats.append((strat_name, kills, evals))
        elif decision == "CONDITIONAL_GO":
            cgo_strats.append((strat_name, kills, evals))
        else:
            nogo_strats.append((strat_name, kills, evals))

    if go_strats:
        names = ", ".join(s for s, _, _ in go_strats)
        return "GO", (
            f"{len(go_strats)} strategy(ies) pass all primary regimes with no kills: {names}. "
            "Proceed to testnet."
        )
    elif cgo_strats:
        names = ", ".join(f"{s} ({k}/{e} kills)" for s, k, e in cgo_strats)
        return "CONDITIONAL_GO", (
            f"No full GO. Best candidates: {names}. "
            "Proceed at 0.5% position size max, daily loss limit 1%."
        )
    else:
        return "NO_GO", (
            f"All strategies triggered kills in primary regimes. "
            "Extend paper trading 14 more days, recalibrate parameters."
        )


def format_markdown(results: Dict, decision: str, reason: str, ts: str) -> str:
    """Render review as a markdown report."""
    lines = [
        "# Paper Trader Review — 4/14 Go/No-Go",
        f"> Generated: {ts}",
        "",
        f"## Decision: {decision}",
        f"{reason}",
        "",
        "---",
        "",
        "## Kill Conditions",
        "| Condition | Threshold |",
        "|-----------|-----------|",
        f"| Min Sharpe (kill) | {KILL_CONDITIONS['min_sharpe']} |",
        f"| Max MDD (kill) | {KILL_CONDITIONS['max_mdd_pct']}% |",
        f"| Min Profit Factor | {KILL_CONDITIONS['min_profit_factor']} |",
        f"| Min Win Rate | {KILL_CONDITIONS['min_win_rate_pct']}% |",
        "",
        "---",
        "",
        "## Results by Strategy × Regime",
    ]

    for strat_name, regime_results in results.items():
        lines.append(f"\n### {strat_name}")
        lines.append("| Regime | Sharpe | MDD% | Win Rate | PF | Windows Passed | Kill |")
        lines.append("|--------|--------|------|----------|----|----------------|------|")
        for regime_name, r in regime_results.items():
            pf = f"{r['avg_profit_factor']:.4f}" if r["avg_profit_factor"] is not None else "inf"
            kill_icon = "YES" if r["kill_triggered"] else "no"
            lines.append(
                f"| {regime_name} | {r['avg_sharpe']:.4f} | {r['avg_mdd']:.2f} | "
                f"{r['avg_win_rate']:.1f}% | {pf} | {r['windows_passed']}/{r['n_windows']} | {kill_icon} |"
            )

    lines += [
        "",
        "---",
        "",
        "## Interpretation",
        "- **Trending regime** (primary for trend-following): must pass",
        "- **Mean-reverting regime** (non-primary for DualMA/Donchian): expected failure, not counted",
        "- **Mixed regime** (primary): real-world proxy — must not catastrophically lose",
        "- Kill conditions are only checked against each strategy's primary regimes",
        "",
        "## Next Steps",
        "- GO: → Testnet (Binance testnet USDT-M, same size as paper)",
        "- CONDITIONAL_GO: → Testnet with position size floor (0.5% capital)",
        "- NO_GO: → Extend paper trading 14 days, recalibrate strategy parameters",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Paper trader 4/14 review")
    parser.add_argument("--output-dir", default="results", help="Output directory")
    parser.add_argument("--bars", type=int, default=500, help="Bars per regime")
    args = parser.parse_args()

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M UTC")
    ts_file = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    print(f"[review] Running paper trader review ({args.bars} bars/regime)...")
    results = run_full_review(bars_per_regime=args.bars)

    decision, reason = make_go_no_go(results)
    print(f"[review] Decision: {decision}")
    print(f"[review] {reason}")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Save markdown
    md_path = out_dir / f"paper_trader_review_{ts_file}.md"
    md_content = format_markdown(results, decision, reason, ts)
    md_path.write_text(md_content, encoding="utf-8")
    print(f"[review] Markdown report: {md_path}")

    # Save JSON (sanitize inf)
    def sanitize(obj):
        if isinstance(obj, float) and (math.isinf(obj) or math.isnan(obj)):
            return None
        if isinstance(obj, dict):
            return {k: sanitize(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [sanitize(x) for x in obj]
        return obj

    json_path = out_dir / f"paper_trader_review_{ts_file}.json"
    json_path.write_text(
        json.dumps({"ts": ts, "decision": decision, "reason": reason, "results": sanitize(results)}, indent=2),
        encoding="utf-8",
    )
    print(f"[review] JSON data: {json_path}")

    return 0 if decision != "NO_GO" else 1


if __name__ == "__main__":
    sys.exit(main())
