"""Rolling performance metrics for the B1 trading engine.

Computes:
    - Rolling Sharpe ratio (configurable window, default 20 trades)
    - Edge ratio (avg win / avg loss)
    - Win rate (rolling and cumulative)
    - Strategy correlation matrix
    - Max drawdown (rolling)
    - Profit factor (gross profit / gross loss)

Reads from:
    results/trading_engine_log.jsonl   — per-tick strategy PnL
    results/trading_engine_status.json — current engine state
    results/paper_live_log.jsonl       — paper-live signals
    results/kill_lessons.jsonl         — kill events

Outputs to:
    results/performance/summary.json   — machine-readable metrics
    results/performance/report.md      — human-readable dashboard

Usage:
    python -m trading.performance_tracker              # generate report
    python -m trading.performance_tracker --json-only  # JSON only, no markdown
    python -m trading.performance_tracker --strategy X  # single strategy
"""
from __future__ import annotations

import json
import statistics
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

_TAIPEI = timezone(timedelta(hours=8))

RESULTS = Path(__file__).resolve().parent.parent / "results"
ENGINE_LOG = RESULTS / "trading_engine_log.jsonl"
STATUS_PATH = RESULTS / "trading_engine_status.json"
PAPER_LIVE_LOG = RESULTS / "paper_live_log.jsonl"
KILLS_LOG = RESULTS / "kill_lessons.jsonl"
PERF_DIR = RESULTS / "performance"

# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------


def _load_jsonl(path: Path) -> List[dict]:
    """Load a JSONL file, skipping malformed lines."""
    if not path.exists():
        return []
    entries: List[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def load_engine_log() -> List[dict]:
    """Load all trading engine log entries."""
    return _load_jsonl(ENGINE_LOG)


def load_paper_log(strategy_type: str = "dual_ma") -> List[dict]:
    """Load paper trading log entries (backward-compatible API).

    If strategy_type is provided and a per-strategy file exists, use that.
    Otherwise falls back to paper_live_log.jsonl.
    """
    per_strategy = RESULTS / f"paper_{strategy_type}.jsonl"
    if per_strategy.exists():
        return _load_jsonl(per_strategy)
    return _load_jsonl(PAPER_LIVE_LOG)


def load_kills() -> List[dict]:
    """Load kill lesson entries."""
    return _load_jsonl(KILLS_LOG)


def _load_status() -> dict:
    """Load current engine status JSON."""
    if not STATUS_PATH.exists():
        return {}
    try:
        return json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


# ---------------------------------------------------------------------------
# Per-strategy PnL extraction
# ---------------------------------------------------------------------------


def extract_strategy_pnl(entries: Sequence[dict]) -> Dict[str, List[float]]:
    """Group engine log entries by strategy, return ordered PnL series.

    Each entry has {"strategy": str, "pnl_pct": float, "tick": int}.
    Returns {strategy_name: [pnl_pct_tick1, pnl_pct_tick2, ...]}.
    """
    by_strategy: Dict[str, List[Tuple[int, float]]] = defaultdict(list)
    for e in entries:
        name = e.get("strategy", "")
        pnl = e.get("pnl_pct", 0.0)
        tick = e.get("tick", 0)
        if name:
            by_strategy[name].append((tick, pnl))

    result: Dict[str, List[float]] = {}
    for name, pairs in by_strategy.items():
        pairs.sort(key=lambda t: t[0])
        result[name] = [p for _, p in pairs]
    return result


# ---------------------------------------------------------------------------
# Metric computation (pure functions, no side effects)
# ---------------------------------------------------------------------------


def compute_rolling_sharpe(pnl_series: List[float], window: int = 20) -> float:
    """Rolling Sharpe ratio over the last `window` trades.

    Annualized assuming daily returns (sqrt(252)).
    Returns 0.0 if insufficient data or zero variance.
    """
    if len(pnl_series) < 2:
        return 0.0
    recent = pnl_series[-window:]
    if len(recent) < 2:
        return 0.0
    mean = statistics.mean(recent)
    std = statistics.stdev(recent)
    if std == 0:
        return 0.0
    return (mean / std) * (252 ** 0.5)


def compute_edge_ratio(pnl_series: List[float]) -> dict:
    """Edge ratio = (avg win / avg loss) × win rate.

    This is the full expectancy-weighted edge ratio:
    - avg_win / avg_loss captures the reward-to-risk per trade.
    - Multiplying by win_rate weights it by how often we win,
      giving the expected edge per trade as a fraction of avg loss.

    A ratio > 1.0 means positive expected value.
    Also returns avg_win, avg_loss, raw_ratio (unweighted) for transparency.
    """
    wins = [p for p in pnl_series if p > 0]
    losses = [p for p in pnl_series if p < 0]
    total = len(pnl_series)

    avg_win = statistics.mean(wins) if wins else 0.0
    avg_loss = abs(statistics.mean(losses)) if losses else 0.0
    win_rate = len(wins) / total if total > 0 else 0.0

    raw_ratio = avg_win / avg_loss if avg_loss > 0 else 0.0
    edge_ratio = raw_ratio * win_rate

    return {
        "edge_ratio": round(edge_ratio, 4),
        "raw_ratio": round(raw_ratio, 4),
        "avg_win": round(avg_win, 6),
        "avg_loss": round(avg_loss, 6),
        "win_rate": round(win_rate, 4),
        "win_count": len(wins),
        "loss_count": len(losses),
    }


def compute_win_rate(pnl_series: List[float],
                     window: Optional[int] = None) -> dict:
    """Win rate: fraction of positive PnL entries.

    Returns both cumulative and rolling (if window is set).
    """
    if not pnl_series:
        return {"cumulative": 0.0, "rolling": 0.0, "total_trades": 0}

    total = len(pnl_series)
    cum_wins = sum(1 for p in pnl_series if p > 0)
    cumulative = cum_wins / total

    rolling = cumulative
    if window and len(pnl_series) >= window:
        recent = pnl_series[-window:]
        rolling = sum(1 for p in recent if p > 0) / len(recent)

    return {
        "cumulative": round(cumulative, 4),
        "rolling": round(rolling, 4),
        "total_trades": total,
    }


def compute_max_drawdown(pnl_series: List[float],
                         window: Optional[int] = None) -> dict:
    """Max drawdown from cumulative PnL curve.

    Returns both all-time and rolling (last `window` entries) MDD.
    """
    def _mdd(series: List[float]) -> float:
        if not series:
            return 0.0
        cum = 0.0
        peak = 0.0
        mdd = 0.0
        for p in series:
            cum += p
            peak = max(peak, cum)
            dd = peak - cum
            mdd = max(mdd, dd)
        return round(mdd, 4)

    all_time = _mdd(pnl_series)
    rolling = all_time
    if window and len(pnl_series) >= window:
        rolling = _mdd(pnl_series[-window:])

    return {
        "all_time": all_time,
        "rolling": rolling,
    }


def compute_profit_factor(pnl_series: List[float]) -> float:
    """Profit factor = gross profit / gross loss.

    Returns inf if no losses, 0.0 if no trades.
    """
    if not pnl_series:
        return 0.0
    gross_profit = sum(p for p in pnl_series if p > 0)
    gross_loss = abs(sum(p for p in pnl_series if p < 0))
    if gross_loss == 0:
        return float("inf") if gross_profit > 0 else 0.0
    return round(gross_profit / gross_loss, 4)


def compute_correlation_matrix(
    strategy_pnls: Dict[str, List[float]],
) -> Dict[str, Dict[str, float]]:
    """Pearson correlation matrix between strategy PnL series.

    Only computes for strategies with overlapping data. Strategies with
    fewer than 5 data points are excluded.
    """
    # Filter to strategies with enough data
    eligible = {
        name: series for name, series in strategy_pnls.items()
        if len(series) >= 5
    }
    if len(eligible) < 2:
        return {}

    # Align series to the same length (truncate to shortest from the end)
    min_len = min(len(s) for s in eligible.values())
    aligned = {
        name: series[-min_len:] for name, series in eligible.items()
    }

    names = sorted(aligned.keys())
    matrix: Dict[str, Dict[str, float]] = {}

    for a in names:
        matrix[a] = {}
        for b in names:
            if a == b:
                matrix[a][b] = 1.0
                continue
            corr = _pearson(aligned[a], aligned[b])
            matrix[a][b] = round(corr, 4)

    return matrix


def rank_strategies_by_risk_adjusted_return(
    strategy_pnls: Dict[str, List[float]],
    sharpe_window: int = 20,
) -> List[Dict]:
    """Rank strategies by risk-adjusted return (composite score).

    Composite score = 0.5 × normalized_sharpe
                    + 0.3 × normalized_edge_ratio
                    + 0.2 × normalized_profit_factor

    All components are min-max normalized across the strategy set so that
    different scales (Sharpe in annualized units, PF dimensionless) are
    comparable.  Returns a list of dicts sorted descending by score.

    Strategies with fewer than 2 trades are excluded (insufficient data).
    """
    if not strategy_pnls:
        return []

    rows = []
    for name, pnl in strategy_pnls.items():
        if len(pnl) < 2:
            continue
        sharpe = compute_rolling_sharpe(pnl, window=sharpe_window)
        edge = compute_edge_ratio(pnl)
        pf_raw = compute_profit_factor(pnl)
        pf = min(pf_raw, 10.0)  # cap inf/huge values for normalization
        rows.append({
            "name": name,
            "sharpe": sharpe,
            "edge_ratio": edge["edge_ratio"],
            "profit_factor": pf,
            "trade_count": len(pnl),
            "cum_pnl": round(sum(pnl), 4),
        })

    if not rows:
        return []

    def _normalize(values: List[float]) -> List[float]:
        lo, hi = min(values), max(values)
        if hi == lo:
            return [1.0] * len(values)
        return [(v - lo) / (hi - lo) for v in values]

    sharpes = _normalize([r["sharpe"] for r in rows])
    edges = _normalize([r["edge_ratio"] for r in rows])
    pfs = _normalize([r["profit_factor"] for r in rows])

    scored = []
    for i, row in enumerate(rows):
        score = 0.5 * sharpes[i] + 0.3 * edges[i] + 0.2 * pfs[i]
        scored.append({**row, "score": round(score, 4), "rank": 0})

    scored.sort(key=lambda r: r["score"], reverse=True)
    for rank_idx, r in enumerate(scored, start=1):
        r["rank"] = rank_idx

    return scored


def _pearson(x: List[float], y: List[float]) -> float:
    """Pearson correlation coefficient between two equal-length series."""
    n = len(x)
    if n < 2:
        return 0.0
    mx = statistics.mean(x)
    my = statistics.mean(y)
    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / (n - 1)
    sx = statistics.stdev(x)
    sy = statistics.stdev(y)
    if sx == 0 or sy == 0:
        return 0.0
    return cov / (sx * sy)


# ---------------------------------------------------------------------------
# Aggregate report builder
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StrategyMetrics:
    """Immutable metrics snapshot for a single strategy."""
    name: str
    trade_count: int
    rolling_sharpe: float
    edge_ratio: float          # (avg_win/avg_loss) × win_rate
    raw_ratio: float           # avg_win / avg_loss (unweighted)
    avg_win: float
    avg_loss: float
    win_rate_cumulative: float
    win_rate_rolling: float
    max_drawdown_all_time: float
    max_drawdown_rolling: float
    profit_factor: float
    cum_pnl: float


@dataclass
class PerformanceReport:
    """Complete performance report across all strategies."""
    generated_at: str
    strategy_metrics: List[StrategyMetrics] = field(default_factory=list)
    correlation_matrix: Dict[str, Dict[str, float]] = field(default_factory=dict)
    strategy_rankings: List[dict] = field(default_factory=list)
    aggregate: dict = field(default_factory=dict)
    kill_count: int = 0
    engine_status: dict = field(default_factory=dict)


def build_report(
    sharpe_window: int = 20,
    wr_window: int = 20,
    mdd_window: int = 50,
    strategy_filter: Optional[str] = None,
) -> PerformanceReport:
    """Build a full performance report from results/ data.

    Args:
        sharpe_window: Rolling window for Sharpe ratio.
        wr_window: Rolling window for win rate.
        mdd_window: Rolling window for max drawdown.
        strategy_filter: If set, only include this strategy.

    Returns:
        PerformanceReport with all metrics computed.
    """
    now = datetime.now(_TAIPEI).isoformat()
    entries = load_engine_log()
    strategy_pnls = extract_strategy_pnl(entries)

    if strategy_filter:
        strategy_pnls = {
            k: v for k, v in strategy_pnls.items()
            if strategy_filter in k
        }

    metrics_list: List[StrategyMetrics] = []
    all_pnl: List[float] = []

    for name in sorted(strategy_pnls.keys()):
        pnl = strategy_pnls[name]
        sharpe = compute_rolling_sharpe(pnl, window=sharpe_window)
        edge = compute_edge_ratio(pnl)
        wr = compute_win_rate(pnl, window=wr_window)
        mdd = compute_max_drawdown(pnl, window=mdd_window)
        pf = compute_profit_factor(pnl)
        cum = round(sum(pnl), 4)
        all_pnl.extend(pnl)

        metrics_list.append(StrategyMetrics(
            name=name,
            trade_count=len(pnl),
            rolling_sharpe=round(sharpe, 4),
            edge_ratio=edge["edge_ratio"],
            raw_ratio=edge["raw_ratio"],
            avg_win=edge["avg_win"],
            avg_loss=edge["avg_loss"],
            win_rate_cumulative=wr["cumulative"],
            win_rate_rolling=wr["rolling"],
            max_drawdown_all_time=mdd["all_time"],
            max_drawdown_rolling=mdd["rolling"],
            profit_factor=pf if pf != float("inf") else 999.0,
            cum_pnl=cum,
        ))

    # Correlation matrix
    corr_matrix = compute_correlation_matrix(strategy_pnls)

    # Aggregate metrics across all strategies
    aggregate = {}
    if all_pnl:
        aggregate = {
            "total_trades": len(all_pnl),
            "total_pnl": round(sum(all_pnl), 4),
            "sharpe": round(compute_rolling_sharpe(all_pnl, window=sharpe_window), 4),
            "win_rate": round(
                sum(1 for p in all_pnl if p > 0) / len(all_pnl), 4
            ),
            "profit_factor": compute_profit_factor(all_pnl),
            "max_drawdown": compute_max_drawdown(all_pnl)["all_time"],
        }

    # Strategy rankings by risk-adjusted return
    rankings = rank_strategies_by_risk_adjusted_return(
        strategy_pnls, sharpe_window=sharpe_window
    )

    kills = load_kills()
    status = _load_status()

    return PerformanceReport(
        generated_at=now,
        strategy_metrics=metrics_list,
        correlation_matrix=corr_matrix,
        strategy_rankings=rankings,
        aggregate=aggregate,
        kill_count=len(kills),
        engine_status=status,
    )


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------


def report_to_json(report: PerformanceReport) -> str:
    """Serialize report to JSON string."""
    data = {
        "generated_at": report.generated_at,
        "aggregate": report.aggregate,
        "kill_count": report.kill_count,
        "strategies": [asdict(m) for m in report.strategy_metrics],
        "correlation_matrix": report.correlation_matrix,
        "strategy_rankings": report.strategy_rankings,
    }
    # Handle inf in profit_factor
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


def report_to_markdown(report: PerformanceReport) -> str:
    """Generate human-readable markdown report."""
    lines: List[str] = [
        "# B1 Trading Performance Report",
        "",
        f"**Generated**: {report.generated_at}",
        f"**Kill events**: {report.kill_count}",
        "",
    ]

    # Aggregate
    agg = report.aggregate
    if agg:
        lines.extend([
            "## Aggregate Metrics",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total trades | {agg.get('total_trades', 0)} |",
            f"| Total PnL | {agg.get('total_pnl', 0):+.4f}% |",
            f"| Sharpe (rolling) | {agg.get('sharpe', 0):.4f} |",
            f"| Win rate | {agg.get('win_rate', 0):.1%} |",
            f"| Profit factor | {agg.get('profit_factor', 0):.4f} |",
            f"| Max drawdown | {agg.get('max_drawdown', 0):.4f}% |",
            "",
        ])

    # Per-strategy table
    if report.strategy_metrics:
        lines.extend([
            "## Per-Strategy Metrics",
            "",
            "| Strategy | Trades | Sharpe | Edge | WR (cum) | WR (roll) | MDD | PF | PnL |",
            "|----------|-------:|-------:|-----:|---------:|----------:|----:|---:|----:|",
        ])
        for m in report.strategy_metrics:
            pf_str = f"{m.profit_factor:.2f}" if m.profit_factor < 999 else "inf"
            lines.append(
                f"| {m.name} | {m.trade_count} | {m.rolling_sharpe:.2f} | "
                f"{m.edge_ratio:.2f} | {m.win_rate_cumulative:.1%} | "
                f"{m.win_rate_rolling:.1%} | {m.max_drawdown_all_time:.2f} | "
                f"{pf_str} | {m.cum_pnl:+.2f} |"
            )
        lines.append("")

    # Strategy rankings
    if report.strategy_rankings:
        lines.extend([
            "## Strategy Rankings (Risk-Adjusted Return)",
            "",
            "Score = 0.5×Sharpe + 0.3×EdgeRatio + 0.2×ProfitFactor (min-max normalized)",
            "",
            "| Rank | Strategy | Score | Sharpe | Edge | PF | Trades | PnL |",
            "|-----:|----------|------:|-------:|-----:|---:|-------:|----:|",
        ])
        for r in report.strategy_rankings:
            pf_str = f"{r['profit_factor']:.2f}" if r["profit_factor"] < 10.0 else "≥10"
            lines.append(
                f"| {r['rank']} | {r['name']} | {r['score']:.4f} | "
                f"{r['sharpe']:.2f} | {r['edge_ratio']:.4f} | "
                f"{pf_str} | {r['trade_count']} | {r['cum_pnl']:+.2f} |"
            )
        lines.append("")

    # Correlation matrix
    if report.correlation_matrix:
        names = sorted(report.correlation_matrix.keys())
        # Abbreviate names for readability
        abbr = {n: n[:20] for n in names}

        lines.extend([
            "## Strategy Correlation Matrix",
            "",
        ])

        header = "| | " + " | ".join(abbr[n] for n in names) + " |"
        sep = "|---|" + "|".join("---:" for _ in names) + "|"
        lines.extend([header, sep])

        for a in names:
            row_vals = " | ".join(
                f"{report.correlation_matrix[a].get(b, 0):.2f}"
                for b in names
            )
            lines.append(f"| {abbr[a]} | {row_vals} |")
        lines.append("")

    # Highly correlated pairs warning
    if report.correlation_matrix:
        high_corr: List[str] = []
        names_sorted = sorted(report.correlation_matrix.keys())
        for i, a in enumerate(names_sorted):
            for b in names_sorted[i + 1:]:
                corr = report.correlation_matrix[a].get(b, 0)
                if abs(corr) > 0.7:
                    high_corr.append(
                        f"- **{a}** / **{b}**: r={corr:.3f}"
                    )
        if high_corr:
            lines.extend([
                "### High Correlation Warnings (|r| > 0.7)",
                "",
                *high_corr,
                "",
            ])

    lines.extend([
        "---",
        "*Generated by trading.performance_tracker*",
        "",
    ])

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Backward-compatible API (used by dashboard, phase gate)
# ---------------------------------------------------------------------------


def compute_strategy_summary(status_path: Optional[Path] = None) -> dict:
    """Compute summary metrics from trading_engine_status.json.

    Backward-compatible with existing callers.
    """
    if status_path is None:
        status_path = STATUS_PATH
    if not status_path.exists():
        return {"error": "Status file not found"}

    data = json.loads(status_path.read_text(encoding="utf-8"))

    summary = {
        "tick": data.get("tick_count", data.get("tick", 0)),
        "total_pnl_pct": data.get("total_pnl_pct", 0),
        "active_strategies": data.get("active_strategies", 0),
        "disabled_strategies": len(data.get("disabled", {})),
        "total_kills": data.get("total_kills", 0),
        "kill_window": data.get("kill_window", 0),
        "regime": data.get("regime", "unknown"),
    }

    # Per-strategy PnL from signals dict
    strategy_pnls: dict = {}
    signals = data.get("signals", {})
    for name, sig in signals.items():
        strategy_pnls[name] = {
            "signal": {1: "LONG", -1: "SHORT", 0: "FLAT"}.get(sig, "FLAT"),
        }
    summary["strategy_details"] = strategy_pnls

    return summary


def check_phase_gate() -> dict:
    """Check Phase 1 pass criteria."""
    status = compute_strategy_summary()

    gate = {
        "clean_ticks_500": status.get("tick", 0) >= 500,
        "kill_window_50": status.get("kill_window", 0) >= 50,
        "strategies_with_trades": len(status.get("strategy_details", {})) >= 3,
        "pnl_positive": status.get("total_pnl_pct", 0) > 0,
    }
    gate["all_pass"] = all(gate.values())
    gate["status"] = status
    return gate


# ---------------------------------------------------------------------------
# File output
# ---------------------------------------------------------------------------


def write_report(report: PerformanceReport) -> Tuple[Path, Path]:
    """Write JSON summary + markdown report to results/performance/."""
    PERF_DIR.mkdir(parents=True, exist_ok=True)

    json_path = PERF_DIR / "summary.json"
    json_path.write_text(report_to_json(report), encoding="utf-8")

    md_path = PERF_DIR / "report.md"
    md_path.write_text(report_to_markdown(report), encoding="utf-8")

    return json_path, md_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="B1 Trading Performance Tracker",
    )
    parser.add_argument(
        "--json-only", action="store_true",
        help="Output JSON only (no markdown)",
    )
    parser.add_argument(
        "--strategy", type=str, default=None,
        help="Filter to a specific strategy name/prefix",
    )
    parser.add_argument(
        "--sharpe-window", type=int, default=20,
        help="Rolling window for Sharpe ratio (default: 20)",
    )
    parser.add_argument(
        "--stdout", action="store_true",
        help="Print to stdout instead of writing files",
    )
    args = parser.parse_args()

    report = build_report(
        sharpe_window=args.sharpe_window,
        strategy_filter=args.strategy,
    )

    if args.stdout:
        if args.json_only:
            print(report_to_json(report))
        else:
            print(report_to_markdown(report))
        return

    json_path, md_path = write_report(report)
    print(f"JSON: {json_path}")
    if not args.json_only:
        print(f"Markdown: {md_path}")

    # Print summary to stdout
    agg = report.aggregate
    if agg:
        print(f"\nTotal PnL: {agg.get('total_pnl', 0):+.4f}%")
        print(f"Sharpe: {agg.get('sharpe', 0):.4f}")
        print(f"Win rate: {agg.get('win_rate', 0):.1%}")
        print(f"Profit factor: {agg.get('profit_factor', 0):.4f}")
        print(f"Max drawdown: {agg.get('max_drawdown', 0):.4f}%")
        print(f"Strategies: {len(report.strategy_metrics)}")
    else:
        print("\nNo trading data found in engine log.")

    print(f"\n=== Phase 1 Gate Check ===")
    gate = check_phase_gate()
    for criterion, passed in gate.items():
        if criterion in ("status", "all_pass"):
            continue
        print(f"  {'PASS' if passed else 'FAIL'}: {criterion}")
    print(f"\n  Overall: {'GO' if gate['all_pass'] else 'NO-GO'}")


if __name__ == "__main__":
    main()
