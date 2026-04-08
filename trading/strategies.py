"""
Named strategies referenced in the dynamic tree.

DualMA  — dual moving-average crossover (the "momentum" variant with configurable windows).
Donchian — Donchian channel breakout (the "breakout" variant with explicit channel logic).

Both conform to StrategyFn: (List[Bar]) -> Signal.
"""

from typing import List, Dict

# Re-use helpers from the backtest framework
from trading.backtest_framework import Bar, Signal, _mean

# ---------------------------------------------------------------------------
# DualMA — Dual Moving Average Crossover
# ---------------------------------------------------------------------------

class DualMA:
    """
    Long when fast SMA crosses above slow SMA; short when below.
    Default windows tuned for BTC daily: fast=10, slow=30.
    """

    def __init__(self, fast: int = 10, slow: int = 30):
        if fast >= slow:
            raise ValueError(f"fast ({fast}) must be < slow ({slow})")
        self.fast = fast
        self.slow = slow

    def __call__(self, bars: List[Bar]) -> Signal:
        if len(bars) < self.slow:
            return 0
        fast_ma = _mean([b["close"] for b in bars[-self.fast:]])
        slow_ma = _mean([b["close"] for b in bars[-self.slow:]])
        if fast_ma > slow_ma:
            return 1
        if fast_ma < slow_ma:
            return -1
        return 0

    def __repr__(self) -> str:
        return f"DualMA(fast={self.fast}, slow={self.slow})"


# ---------------------------------------------------------------------------
# Donchian — Donchian Channel Breakout
# ---------------------------------------------------------------------------

class Donchian:
    """
    Long when close breaks above the highest high of the last `period` bars.
    Short when close breaks below the lowest low of the last `period` bars.
    Default period=20 (standard Donchian).
    """

    def __init__(self, period: int = 20):
        if period < 2:
            raise ValueError(f"period must be >= 2, got {period}")
        self.period = period

    def __call__(self, bars: List[Bar]) -> Signal:
        if len(bars) < self.period + 1:
            return 0
        # Channel is based on the previous `period` bars (excluding current)
        window = bars[-(self.period + 1):-1]
        upper = max(b["high"] for b in window)
        lower = min(b["low"] for b in window)
        cur = bars[-1]["close"]
        if cur > upper:
            return 1
        if cur < lower:
            return -1
        return 0

    def __repr__(self) -> str:
        return f"Donchian(period={self.period})"


# ---------------------------------------------------------------------------
# RegimeFilter — only signal when trending regime is confirmed
# ---------------------------------------------------------------------------

class RegimeFilter:
    """
    Wraps any StrategyFn with a regime gate.

    Trend regime detection: compares the slope of a long-term MA to a
    threshold. If the long MA is flat (slope ≈ 0), we're likely in a
    mean-reverting or choppy regime — return 0 (flat) regardless of the
    inner strategy's signal.

    Parameters
    ----------
    strategy : callable
        Inner strategy (DualMA, Donchian, etc.).
    trend_period : int
        Lookback for the trend-confirmation MA (default 50).
    slope_bars : int
        How many bars back to measure MA slope (default 5).
    min_slope_pct : float
        Minimum |slope| in % per bar to count as "trending" (default 0.1).
    """

    def __init__(
        self,
        strategy,
        trend_period: int = 50,
        slope_bars: int = 5,
        min_slope_pct: float = 0.10,
    ):
        self.strategy = strategy
        self.trend_period = trend_period
        self.slope_bars = slope_bars
        self.min_slope_pct = min_slope_pct / 100.0  # convert to fraction

    def _is_trending(self, bars: List[Bar]) -> bool:
        """Return True if the long-term MA is sloping significantly."""
        if len(bars) < self.trend_period + self.slope_bars:
            return False
        # Long MA values at current and `slope_bars` ago
        closes = [b["close"] for b in bars]
        ma_now = _mean(closes[-(self.trend_period):])
        ma_old = _mean(closes[-(self.trend_period + self.slope_bars):-self.slope_bars])
        if ma_old == 0:
            return False
        slope = (ma_now - ma_old) / ma_old  # fraction per `slope_bars` bars
        return abs(slope) >= self.min_slope_pct * self.slope_bars

    def __call__(self, bars: List[Bar]) -> Signal:
        if not self._is_trending(bars):
            return 0  # flat during non-trending regime
        return self.strategy(bars)

    def __repr__(self) -> str:
        return f"RegimeFilter({self.strategy}, trend_period={self.trend_period}, min_slope={self.min_slope_pct*100:.2f}%/bar)"


# ---------------------------------------------------------------------------
# DonchianConfirmed — require 2 consecutive closes outside channel
# ---------------------------------------------------------------------------

class DonchianConfirmed(Donchian):
    """
    Variant of Donchian that requires the *previous* bar to have also
    triggered a breakout signal before acting.

    Rationale: In choppy/mixed regimes, single-bar breakouts are mostly
    noise. Two consecutive closes outside the channel is a much higher-
    confidence signal, reducing false-positive rate in mixed conditions.
    """

    def __call__(self, bars: List[Bar]) -> Signal:
        if len(bars) < self.period + 2:
            return 0
        current = super().__call__(bars)
        if current == 0:
            return 0
        # Stateless confirmation: check previous bar had same direction
        prev = super().__call__(bars[:-1])
        return current if current == prev else 0

    def __repr__(self) -> str:
        return f"DonchianConfirmed(period={self.period})"


# ---------------------------------------------------------------------------
# Convenience: default instances for BTC daily
# ---------------------------------------------------------------------------
dual_ma_btc_daily = DualMA(fast=10, slow=30)
donchian_btc_daily = Donchian(period=20)
donchian_confirmed_btc_daily = DonchianConfirmed(period=20)

# Regime-filtered versions (production candidates)
dual_ma_filtered = RegimeFilter(DualMA(fast=10, slow=30), trend_period=50, slope_bars=5, min_slope_pct=0.10)
donchian_filtered = RegimeFilter(Donchian(period=20), trend_period=50, slope_bars=5, min_slope_pct=0.10)
donchian_confirmed_filtered = RegimeFilter(DonchianConfirmed(period=20), trend_period=50, slope_bars=5, min_slope_pct=0.10)

NAMED_STRATEGIES: Dict[str, object] = {
    "DualMA_10_30": dual_ma_btc_daily,
    "Donchian_20": donchian_btc_daily,
    "DonchianConfirmed_20": donchian_confirmed_btc_daily,
    "DualMA_filtered": dual_ma_filtered,
    "Donchian_filtered": donchian_filtered,
    "DonchianConfirmed_filtered": donchian_confirmed_filtered,
}
