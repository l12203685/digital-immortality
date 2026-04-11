"""Orthogonality Filter — prevents correlated strategy mass-kills.

B1 audit (2026-04-11): 4 DualMA variants were mass-killed at PF=0.70 in the
same tick because they shared one edge. This filter computes Pearson |corr|
of a candidate's signal series against every existing pool member over the
last N ticks; candidates above the threshold are rejected and logged.

Stdlib only — cpython 3.14 stripped daemon host (no numpy / no pandas).
"""

from __future__ import annotations

import json
import logging
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

log = logging.getLogger("trading.orthogonality_filter")

REPO = Path(__file__).resolve().parent.parent
RESULTS_DIR = REPO / "results"
REJECTION_LOG_PATH = RESULTS_DIR / "orthogonality_rejections.jsonl"

DEFAULT_MAX_CORR = 0.7
DEFAULT_LOOKBACK_TICKS = 100
# Below this many overlapping samples, correlation is not reliable; the
# candidate is accepted but a warning is logged.
MIN_SAMPLES_FOR_CORRELATION = 20

Bar = Mapping[str, float]
StrategyCallable = Callable[[List[Bar]], int]


class OrthogonalityFilter:
    """Reject new strategy candidates too correlated with existing pool.

    Advisory: only blocks NEW additions. Existing pool members keep running.
    """

    def __init__(
        self,
        max_corr: float = DEFAULT_MAX_CORR,
        lookback_ticks: int = DEFAULT_LOOKBACK_TICKS,
    ) -> None:
        if not 0.0 < max_corr <= 1.0:
            raise ValueError(f"max_corr must be in (0, 1], got {max_corr}")
        if lookback_ticks < MIN_SAMPLES_FOR_CORRELATION:
            raise ValueError(
                f"lookback_ticks must be >= {MIN_SAMPLES_FOR_CORRELATION}, "
                f"got {lookback_ticks}"
            )
        self.max_corr = max_corr
        self.lookback_ticks = lookback_ticks

    def signal_series(
        self,
        strategy_callable: StrategyCallable,
        bars_history: List[Bar],
    ) -> List[int]:
        """Run strategy_callable across successive prefixes of bars_history.

        Produces one signal per tick over the last `lookback_ticks` bars.
        Each tick invokes the strategy with the bar slice up to (and
        including) that tick. Errors in the strategy produce 0 (neutral).
        """
        if not bars_history:
            return []

        # Walk forward one bar at a time, always feeding a "history" slice.
        # Strategies expect a rolling window of bars up to "now".
        series: List[int] = []
        n = len(bars_history)
        start = max(1, n - self.lookback_ticks)
        for i in range(start, n + 1):
            window = bars_history[:i]
            try:
                sig = int(strategy_callable(window))
            except Exception as exc:  # noqa: BLE001 — protective
                log.debug("Strategy raised during signal_series: %s", exc)
                sig = 0
            series.append(sig)
        return series

    @staticmethod
    def correlation(series_a: List[int], series_b: List[int]) -> float:
        """Pearson correlation coefficient in [-1.0, 1.0].

        Returns 0.0 when either series has zero variance (constant signal)
        or when the paired sample is too short for meaningful stdev.
        """
        n = min(len(series_a), len(series_b))
        if n < 2:
            return 0.0
        a = [float(x) for x in series_a[:n]]
        b = [float(x) for x in series_b[:n]]

        mean_a = statistics.fmean(a)
        mean_b = statistics.fmean(b)

        var_a = sum((x - mean_a) ** 2 for x in a)
        var_b = sum((x - mean_b) ** 2 for x in b)
        if var_a == 0.0 or var_b == 0.0:
            return 0.0

        cov = sum((a[i] - mean_a) * (b[i] - mean_b) for i in range(n))
        denom = math.sqrt(var_a * var_b)
        if denom == 0.0:
            return 0.0
        r = cov / denom
        # Clamp to handle floating point drift just outside [-1, 1]
        if r > 1.0:
            return 1.0
        if r < -1.0:
            return -1.0
        return r

    def is_orthogonal(
        self,
        candidate_strategy: StrategyCallable,
        pool_strategies: Mapping[str, StrategyCallable],
        bars_history: List[Bar],
        candidate_name: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """Check that the candidate is orthogonal to every pool member.

        Returns (passed, reason). `reason` is a human-readable explanation
        of the decision — useful for logs and Discord notifications.

        Rules:
        * Empty pool → always accepted.
        * Candidate signal series shorter than MIN_SAMPLES_FOR_CORRELATION
          → accepted, with a warning logged (can't decide reliably).
        * Otherwise, reject if max |corr(candidate, member)| > max_corr.
        """
        cand_label = candidate_name or "candidate"

        if not pool_strategies:
            return True, "empty_pool"

        cand_series = self.signal_series(candidate_strategy, bars_history)
        if len(cand_series) < MIN_SAMPLES_FOR_CORRELATION:
            log.warning(
                "OrthogonalityFilter: %s has insufficient history "
                "(%d samples < %d required) — accepting without correlation check.",
                cand_label, len(cand_series), MIN_SAMPLES_FOR_CORRELATION,
            )
            return True, (
                f"insufficient_history({len(cand_series)}<{MIN_SAMPLES_FOR_CORRELATION})"
            )

        max_abs_corr = 0.0
        max_abs_name = ""
        max_signed_corr = 0.0
        for name, strategy in pool_strategies.items():
            member_series = self.signal_series(strategy, bars_history)
            if len(member_series) < MIN_SAMPLES_FOR_CORRELATION:
                continue
            r = self.correlation(cand_series, member_series)
            if abs(r) > max_abs_corr:
                max_abs_corr = abs(r)
                max_abs_name = name
                max_signed_corr = r

        if max_abs_corr > self.max_corr:
            reason = (
                f"rejected: max|corr|={max_abs_corr:.3f} "
                f"(signed={max_signed_corr:+.3f}) with '{max_abs_name}' "
                f"exceeds threshold {self.max_corr:.2f}"
            )
            return False, reason

        return True, (
            f"accepted: max|corr|={max_abs_corr:.3f} with '{max_abs_name or 'n/a'}' "
            f"<= {self.max_corr:.2f}"
        )

    @staticmethod
    def log_rejection(
        candidate_name: str,
        reason: str,
        max_corr_with: str = "",
        corr: float = 0.0,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Append one JSON line to results/orthogonality_rejections.jsonl."""
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        entry: Dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "candidate": candidate_name,
            "reason": reason,
            "max_corr_with": max_corr_with,
            "corr": round(float(corr), 4),
        }
        if extra:
            entry.update(extra)
        with open(REJECTION_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")


def load_recent_bars_from_log(
    log_path: Path,
    lookback_ticks: int = DEFAULT_LOOKBACK_TICKS,
) -> List[Dict[str, float]]:
    """Reconstruct a bar history from trading_engine_log.jsonl (flat OHLC)."""
    if not log_path.exists():
        return []
    seen_ticks: Dict[int, float] = {}
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            tick = rec.get("tick")
            price = rec.get("price")
            if tick is None or price is None:
                continue
            seen_ticks[int(tick)] = float(price)
    if not seen_ticks:
        return []
    ordered = [seen_ticks[t] for t in sorted(seen_ticks.keys())]
    ordered = ordered[-lookback_ticks:]
    return [
        {"open": p, "high": p, "low": p, "close": p, "volume": 0.0}
        for p in ordered
    ]
