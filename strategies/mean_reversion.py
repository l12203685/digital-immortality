"""
Mean Reversion Strategy — Bollinger Band Bounce.

Signal logic:
  - Compute Bollinger Bands: SMA +/- k * stdev over lookback period
  - Long when price closes below lower band (oversold)
  - Short when price closes above upper band (overbought)
  - Exit (flat) when price reverts to the mean (crosses SMA)

Regime filter:
  - Measure trend strength via slope of slow SMA
  - If trending strongly (slope > threshold), suppress mean-reversion signals
  - Mean reversion works in ranges, not trends

Conforms to StrategyFn: (List[Bar]) -> Signal
"""

import math
from typing import List, Dict

Bar = Dict[str, float]
Signal = int


def _sma(values: List[float], period: int) -> float:
    """Simple moving average of last `period` values."""
    return sum(values[-period:]) / period


def _std(values: List[float], period: int) -> float:
    """Sample standard deviation of last `period` values."""
    if len(values) < period or period < 2:
        return 0.0
    subset = values[-period:]
    mu = sum(subset) / len(subset)
    variance = sum((x - mu) ** 2 for x in subset) / (len(subset) - 1)
    return math.sqrt(variance)


class BollingerMeanReversion:
    """
    Bollinger Band mean reversion with trend regime filter.

    Parameters:
        lookback: Period for SMA and stdev calculation (default 20)
        num_std: Number of standard deviations for bands (default 2.0)
        trend_lookback: Period for trend slope calculation (default 50)
        trend_threshold: Max absolute slope (as fraction of price) to allow MR signals (default 0.001)
            Set to a very large number to disable the trend filter.
    """

    def __init__(
        self,
        lookback: int = 20,
        num_std: float = 2.0,
        trend_lookback: int = 50,
        trend_threshold: float = 0.001,
    ):
        self.lookback = lookback
        self.num_std = num_std
        self.trend_lookback = trend_lookback
        self.trend_threshold = trend_threshold

    def __call__(self, bars: List[Bar]) -> Signal:
        required = max(self.lookback, self.trend_lookback)
        if len(bars) < required + 1:
            return 0

        closes = [b["close"] for b in bars]
        price = closes[-1]

        # Bollinger Bands
        sma = _sma(closes, self.lookback)
        sd = _std(closes, self.lookback)
        if sd == 0:
            return 0

        upper = sma + self.num_std * sd
        lower = sma - self.num_std * sd

        # Trend regime filter: suppress signals in strong trends
        if self.trend_lookback > 1:
            trend_closes = closes[-self.trend_lookback:]
            # Simple slope: (last - first) / first / periods
            slope = (trend_closes[-1] - trend_closes[0]) / trend_closes[0] / self.trend_lookback
            if abs(slope) > self.trend_threshold:
                return 0  # trending — don't mean-revert

        # Mean reversion signals
        if price < lower:
            return 1   # oversold — go long
        if price > upper:
            return -1  # overbought — go short
        return 0

    def __repr__(self) -> str:
        return (
            f"BollingerMeanReversion(lookback={self.lookback}, "
            f"num_std={self.num_std}, trend_lb={self.trend_lookback})"
        )


# ---------------------------------------------------------------------------
# Functional interface
# ---------------------------------------------------------------------------

_default = BollingerMeanReversion(
    lookback=20, num_std=2.0, trend_lookback=50, trend_threshold=0.001
)


def bollinger_mean_reversion(bars: List[Bar]) -> Signal:
    """Bollinger Band mean reversion with trend filter. Default: 20-period, 2 stdev."""
    return _default(bars)
