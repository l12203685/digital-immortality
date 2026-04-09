"""
Portfolio regime detection and strategy selection.

Classifies recent bars as TRENDING, MEAN_REVERTING, or MIXED, then maps
each regime to the best-suited strategy from trading/strategies.py.

Classes
-------
RegimeDetector  — detect(bars) -> str ("trending"/"mean_reverting"/"mixed")
PortfolioSelector — select(bars) -> (regime_str, strategy_fn)
PortfolioResult — dataclass holding one portfolio decision snapshot
"""

import math
from dataclasses import dataclass
from typing import List, Tuple, Callable

from trading.backtest_framework import Bar, Signal, _mean, _std


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _linear_regression_slope(values: List[float]) -> float:
    """Return the slope of a simple OLS regression line through `values`."""
    n = len(values)
    if n < 2:
        return 0.0
    xs = list(range(n))
    mean_x = _mean(xs)
    mean_y = _mean(values)
    num = sum((xs[i] - mean_x) * (values[i] - mean_y) for i in range(n))
    den = sum((xs[i] - mean_x) ** 2 for i in range(n))
    return num / den if den != 0 else 0.0


def _count_ma_crossings(closes: List[float], period: int) -> int:
    """
    Count how many times the close price crosses its simple moving average.
    Each crossing (close goes from above-to-below or below-to-above the MA)
    increments the counter.
    """
    if len(closes) < period + 1:
        return 0

    crossings = 0
    # Compute MA for each bar that has enough history
    prev_side = None
    for i in range(period - 1, len(closes)):
        window = closes[i - period + 1: i + 1]
        ma = _mean(window)
        side = 1 if closes[i] > ma else -1
        if prev_side is not None and side != prev_side:
            crossings += 1
        prev_side = side
    return crossings


# ---------------------------------------------------------------------------
# RegimeDetector
# ---------------------------------------------------------------------------

class RegimeDetector:
    """
    Classify a bar series as TRENDING, MEAN_REVERTING, or MIXED.

    Algorithm (two independent scores, each normalised):

    1. trend_strength = |slope of linear regression on closes| / std_dev(closes)
       High → price is directionally drifting → TRENDING

    2. mean_revert_score = ma_crossings / (len(window) - ma_period)
       High → price oscillates around its moving average → MEAN_REVERTING

    If trend_strength > trend_threshold  → "trending"
    If mean_revert_score > mr_threshold  → "mean_reverting"
    else                                  → "mixed"

    Parameters
    ----------
    lookback : int
        Number of recent bars to analyse (default 60).
    ma_period : int
        MA period used for crossing-count (default 20).
    trend_threshold : float
        Normalised slope threshold for trending classification (default 0.05).
    mr_threshold : float
        Crossing-rate threshold for mean-reverting classification (default 0.30).
    """

    def __init__(
        self,
        lookback: int = 60,
        ma_period: int = 20,
        trend_threshold: float = 0.054,
        mr_threshold: float = 0.25,
    ):
        self.lookback = lookback
        self.ma_period = ma_period
        self.trend_threshold = trend_threshold
        self.mr_threshold = mr_threshold

    def detect(self, bars: List[Bar]) -> str:
        """
        Classify recent bars.

        Returns
        -------
        "trending" | "mean_reverting" | "mixed"
        """
        if len(bars) < max(self.lookback, self.ma_period + 1):
            # Not enough data — default to mixed (safest assumption)
            return "mixed"

        window = bars[-self.lookback:]
        closes = [b["close"] for b in window]

        # --- Trend strength score ---
        slope = _linear_regression_slope(closes)
        std = _std(closes, ddof=1)
        if std == 0:
            trend_strength = 0.0
        else:
            # Normalise by std so it's scale-agnostic.
            # Further divide by average close to make it a per-bar % move.
            avg_close = _mean(closes)
            trend_strength = abs(slope) / std if std > 0 else 0.0
            # Also compute as % slope per bar for interpretability (used in rationale)
            self._pct_slope_per_bar = abs(slope) / avg_close * 100 if avg_close > 0 else 0.0

        # --- Mean-reversion score: normalised crossing rate ---
        crossings = _count_ma_crossings(closes, self.ma_period)
        possible_crossings = len(closes) - self.ma_period
        mr_score = crossings / possible_crossings if possible_crossings > 0 else 0.0

        # Store computed scores for rationale reporting
        self._last_trend_strength = trend_strength
        self._last_mr_score = mr_score
        self._last_crossings = crossings

        # --- Decision ---
        if trend_strength > self.trend_threshold:
            return "trending"
        if mr_score > self.mr_threshold:
            return "mean_reverting"
        return "mixed"

    def last_scores(self) -> dict:
        """Return the last computed scores (call after detect())."""
        return {
            "trend_strength": getattr(self, "_last_trend_strength", None),
            "mr_score": getattr(self, "_last_mr_score", None),
            "ma_crossings": getattr(self, "_last_crossings", None),
            "pct_slope_per_bar": getattr(self, "_pct_slope_per_bar", None),
        }


# ---------------------------------------------------------------------------
# PortfolioSelector
# ---------------------------------------------------------------------------

# Lazy imports of strategies to avoid circular dependencies at module load.
# Resolved on first call to PortfolioSelector.select().
_STRATEGY_CACHE: dict = {}


def _get_strategies() -> dict:
    """Return {regime: (strategy_name, strategy_fn)} mapping."""
    global _STRATEGY_CACHE
    if _STRATEGY_CACHE:
        return _STRATEGY_CACHE

    from trading.strategies import (
        DualMA,
        dual_ma_rsi_filtered,
        bollinger_mr_loose,
    )

    # Regime → strategy mapping validated by walk-forward backtest (results/strategy_comparison.json):
    #   trending      → DualMA_10_30        sh=+5.30 er=7.8   [GO on trending]
    #   mean_reverting→ BollingerMR_loose   sh=+3.40 er=16.5  [GO on mean_reverting; only passer]
    #   mixed         → DualMA_RSI_filtered sh=+1.74 er=9.9   [GO on mixed; best edge ratio]
    # Previous bug: DonchianConfirmed used for mean_reverting — it's a breakout strat, NO on all regimes.
    _STRATEGY_CACHE = {
        "trending": ("DualMA_10_30", DualMA(fast=10, slow=30)),
        "mean_reverting": ("BollingerMR_loose", bollinger_mr_loose),
        "mixed": ("DualMA_RSI_filtered", dual_ma_rsi_filtered),
    }
    return _STRATEGY_CACHE


class PortfolioSelector:
    """
    Map detected regime to the best strategy and produce a Signal.

    Regime → Strategy rationale (validated by walk-forward, results/strategy_comparison.json)
    ---------------------------
    trending       → DualMA_10_30: sh=+5.30 er=7.8 — momentum follows trend cleanly.
    mean_reverting → BollingerMR_loose: sh=+3.40 er=16.5 — Bollinger bounce; only
                     strategy that passes in oscillating markets (MD-175: regime fit).
    mixed          → DualMA_RSI_filtered: sh=+1.74 er=9.9 — best edge ratio on mixed
                     data; RSI gate eliminates counter-trend entries at exhaustion.
    """

    def __init__(self, detector: RegimeDetector = None):
        self.detector = detector or RegimeDetector()

    def select(self, bars: List[Bar]) -> Tuple[str, str, Callable]:
        """
        Detect regime, pick strategy, and return a signal.

        Returns
        -------
        (regime_str, strategy_name, strategy_fn)
        """
        regime = self.detector.detect(bars)
        strategies = _get_strategies()
        strategy_name, strategy_fn = strategies[regime]
        return regime, strategy_name, strategy_fn


# ---------------------------------------------------------------------------
# PortfolioResult
# ---------------------------------------------------------------------------

@dataclass
class PortfolioResult:
    """One complete portfolio decision snapshot."""
    regime: str                  # "trending" | "mean_reverting" | "mixed"
    strategy_name: str           # e.g. "DualMA_10_30"
    signal: int                  # +1 LONG, -1 SHORT, 0 FLAT
    bars_analyzed: int           # number of bars fed to the detector
    trend_strength: float        # normalised slope score
    mr_score: float              # mean-reversion crossing rate
    pct_slope_per_bar: float     # % price movement per bar (readability)
    ma_crossings: int            # raw count of MA crossings in lookback window

    @property
    def signal_label(self) -> str:
        return {1: "LONG", -1: "SHORT", 0: "FLAT"}.get(self.signal, "UNKNOWN")

    def rationale(self) -> str:
        """One-line human-readable rationale for the decision."""
        regime_reasons = {
            "trending": (
                f"trend_strength={self.trend_strength:.4f} > threshold; "
                f"slope={self.pct_slope_per_bar:.4f}%/bar — directional drift detected"
            ),
            "mean_reverting": (
                f"ma_crossings={self.ma_crossings} (rate={self.mr_score:.2f}) > threshold; "
                f"price oscillates around MA — breakout filter applied"
            ),
            "mixed": (
                f"neither strong trend nor clear oscillation "
                f"(trend={self.trend_strength:.4f}, mr={self.mr_score:.2f}) — "
                f"regime-filtered momentum used"
            ),
        }
        base = regime_reasons.get(self.regime, "unknown regime")
        return f"Regime: {self.regime.upper()} | {base} | Signal: {self.signal_label}"

    def to_dict(self) -> dict:
        return {
            "regime": self.regime,
            "strategy_name": self.strategy_name,
            "signal": self.signal,
            "signal_label": self.signal_label,
            "bars_analyzed": self.bars_analyzed,
            "scores": {
                "trend_strength": self.trend_strength,
                "mr_score": self.mr_score,
                "pct_slope_per_bar": self.pct_slope_per_bar,
                "ma_crossings": self.ma_crossings,
            },
            "rationale": self.rationale(),
        }


# ---------------------------------------------------------------------------
# Convenience: run a full portfolio decision in one call
# ---------------------------------------------------------------------------

def run_portfolio_decision(bars: List[Bar]) -> PortfolioResult:
    """
    Convenience wrapper: detect regime, select strategy, compute signal.

    Parameters
    ----------
    bars : List[Bar]
        Historical bars (at least 60 recommended).

    Returns
    -------
    PortfolioResult
    """
    detector = RegimeDetector()
    selector = PortfolioSelector(detector=detector)

    regime, strategy_name, strategy_fn = selector.select(bars)
    signal: Signal = strategy_fn(bars)
    scores = detector.last_scores()

    return PortfolioResult(
        regime=regime,
        strategy_name=strategy_name,
        signal=signal,
        bars_analyzed=len(bars),
        trend_strength=scores.get("trend_strength") or 0.0,
        mr_score=scores.get("mr_score") or 0.0,
        pct_slope_per_bar=scores.get("pct_slope_per_bar") or 0.0,
        ma_crossings=scores.get("ma_crossings") or 0,
    )
