"""
Momentum / Trend-Following Strategy — Dual Moving Average Crossover with ATR Filter.

Signal logic:
  - Compute fast SMA and slow SMA of closing prices
  - Long when fast > slow AND price is above slow (confirming uptrend)
  - Short when fast < slow AND price is below slow (confirming downtrend)
  - Flat when MAs are within an ATR-based dead zone (avoids whipsaw)

ATR filter:
  - If |fast_ma - slow_ma| < atr * dead_zone_factor, stay flat
  - This prevents false signals during consolidation

Conforms to StrategyFn: (List[Bar]) -> Signal
"""

from typing import List, Dict

# Type aliases matching backtest_framework
Bar = Dict[str, float]
Signal = int


def _sma(values: List[float], period: int) -> float:
    """Simple moving average of last `period` values."""
    return sum(values[-period:]) / period


def _atr(bars: List[Bar], period: int = 14) -> float:
    """Average True Range over `period` bars."""
    if len(bars) < 2:
        return 0.0
    trs = []
    for i in range(max(1, len(bars) - period), len(bars)):
        high = bars[i]["high"]
        low = bars[i]["low"]
        prev_close = bars[i - 1]["close"]
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        trs.append(tr)
    return sum(trs) / len(trs) if trs else 0.0


class MomentumCrossover:
    """
    Dual moving average crossover with ATR-based dead zone filter.

    Parameters:
        fast: Fast SMA period (default 10)
        slow: Slow SMA period (default 40)
        atr_period: ATR calculation period (default 14)
        dead_zone_factor: Multiplier on ATR for dead zone width (default 0.5)
            Set to 0 to disable the dead zone filter.
    """

    def __init__(
        self,
        fast: int = 10,
        slow: int = 40,
        atr_period: int = 14,
        dead_zone_factor: float = 0.5,
    ):
        if fast >= slow:
            raise ValueError(f"fast ({fast}) must be < slow ({slow})")
        self.fast = fast
        self.slow = slow
        self.atr_period = atr_period
        self.dead_zone_factor = dead_zone_factor

    def __call__(self, bars: List[Bar]) -> Signal:
        if len(bars) < self.slow + 1:
            return 0

        closes = [b["close"] for b in bars]
        fast_ma = _sma(closes, self.fast)
        slow_ma = _sma(closes, self.slow)

        # ATR dead zone filter
        if self.dead_zone_factor > 0:
            atr = _atr(bars, self.atr_period)
            if atr > 0 and abs(fast_ma - slow_ma) < atr * self.dead_zone_factor:
                return 0

        # Trend confirmation: price must be on the same side as the crossover
        price = bars[-1]["close"]

        if fast_ma > slow_ma and price > slow_ma:
            return 1
        if fast_ma < slow_ma and price < slow_ma:
            return -1
        return 0

    def __repr__(self) -> str:
        return (
            f"MomentumCrossover(fast={self.fast}, slow={self.slow}, "
            f"atr_period={self.atr_period}, dead_zone={self.dead_zone_factor})"
        )


# ---------------------------------------------------------------------------
# Functional interface (for direct registration in STRATEGIES dict)
# ---------------------------------------------------------------------------

# Default instance tuned for crypto daily bars
_default = MomentumCrossover(fast=10, slow=40, atr_period=14, dead_zone_factor=0.5)


def momentum_crossover(bars: List[Bar]) -> Signal:
    """Dual MA crossover with ATR dead zone. Default params: fast=10, slow=40."""
    return _default(bars)
