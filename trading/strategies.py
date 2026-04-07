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


# Convenience: default instances for BTC daily
dual_ma_btc_daily = DualMA(fast=10, slow=30)
donchian_btc_daily = Donchian(period=20)

NAMED_STRATEGIES: Dict[str, object] = {
    "DualMA_10_30": dual_ma_btc_daily,
    "Donchian_20": donchian_btc_daily,
}
