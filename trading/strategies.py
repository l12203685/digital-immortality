"""
Named strategies referenced in the dynamic tree.

DualMA  — dual moving-average crossover (the "momentum" variant with configurable windows).
Donchian — Donchian channel breakout (the "breakout" variant with explicit channel logic).

Both conform to StrategyFn: (List[Bar]) -> Signal.
"""

from typing import List, Dict
from enum import Enum

# Re-use helpers from the backtest framework
from trading.backtest_framework import Bar, Signal, _mean


# ---------------------------------------------------------------------------
# P1-P3 Threat Classification (藍月 Validation Framework)
# ---------------------------------------------------------------------------
# Source: maemfe.org — Strategy Validation Framework
# Compare live trading results vs backtest projections. The gap IS the work.

class ThreatLevel(Enum):
    """Strategy monitoring threat levels for live vs backtest discrepancy.

    P1 = HALT immediately (program errors, risk control failures)
    P2 = Contingency plan (rare events with available mitigation)
    P3 = Monitor (recurring/occasional instability)
    """
    P1_HALT = "P1"
    P2_CONTINGENCY = "P2"
    P3_MONITOR = "P3"


# Discrepancy sources between backtest and live trading
DISCREPANCY_SOURCES = {
    "recurring_instability": {
        "type": 1,
        "threat": ThreatLevel.P3_MONITOR,
        "examples": ["trading cost changes", "spread widening", "commission changes"],
        "action": "monitor and adjust parameters",
    },
    "occasional_instability": {
        "type": 2,
        "threat": ThreatLevel.P3_MONITOR,
        "examples": ["price gaps", "slippage", "low liquidity episodes"],
        "action": "monitor, consider slippage buffer in backtest",
    },
    "rare_instability": {
        "type": 3,
        "threat": ThreatLevel.P2_CONTINGENCY,
        "examples": ["market closures", "broker failures", "server outages"],
        "action": "activate contingency plan",
    },
    "unexpected_problems": {
        "type": 4,
        "threat": ThreatLevel.P1_HALT,
        "examples": ["large unintended orders", "excessive position opening",
                      "program errors", "risk control failures"],
        "action": "HALT immediately, stop model and related strategies",
    },
}

# Kill conditions: when to halt a strategy (extends DNA trading section)
KILL_CONDITIONS = {
    "p1_trigger": "Any Type-4 discrepancy with escalation risk -> immediate halt",
    "drawdown_breach": "Monthly drawdown exceeds monthlevel or maxDDlevel -> force close all",
    "e_ratio_collapse": "E-Ratio drops below 0.8 for 20+ consecutive trades -> review strategy",
    "win_rate_collapse": "Win rate drops >15pp below backtest baseline over 50+ trades -> review",
    "mae_expansion": "MAE Q3 expands >50% vs backtest baseline -> regime change, pause",
    "correlation_spike": "Portfolio strategy correlation exceeds 0.5 -> reduce exposure",
}

# Re-use BollingerMeanReversion from strategies/
from strategies.mean_reversion import BollingerMeanReversion

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


class MeanReversionFilter:
    """
    Wraps a mean-reversion strategy with a ranging-regime gate.

    Inverse of RegimeFilter: allows signals only when the market is NOT trending
    (flat/choppy). Blocks signals when trending strongly.

    This is correct for BollingerMeanReversion and similar MR strategies which
    perform best in range-bound conditions.

    Parameters
    ----------
    strategy : callable
        Inner mean-reversion strategy.
    trend_period : int
        Lookback for the trend-detection MA (default 50).
    slope_bars : int
        How many bars back to measure MA slope (default 5).
    max_slope_pct : float
        Maximum |slope| in % per bar to allow MR signal (default 0.1).
        If slope exceeds this, market is trending — suppress MR signal.
    """

    def __init__(
        self,
        strategy,
        trend_period: int = 50,
        slope_bars: int = 5,
        max_slope_pct: float = 0.10,
    ):
        self.strategy = strategy
        self.trend_period = trend_period
        self.slope_bars = slope_bars
        self.max_slope_pct = max_slope_pct / 100.0  # convert to fraction

    def _is_ranging(self, bars: List[Bar]) -> bool:
        """Return True if the market is flat/ranging (NOT strongly trending)."""
        if len(bars) < self.trend_period + self.slope_bars:
            return True  # insufficient data → assume ranging (safe for MR)
        closes = [b["close"] for b in bars]
        ma_now = _mean(closes[-(self.trend_period):])
        ma_old = _mean(closes[-(self.trend_period + self.slope_bars):-self.slope_bars])
        if ma_old == 0:
            return True
        slope = (ma_now - ma_old) / ma_old
        return abs(slope) < self.max_slope_pct * self.slope_bars

    def __call__(self, bars: List[Bar]) -> Signal:
        if not self._is_ranging(bars):
            return 0  # flat during trending regime — MR has no edge here
        return self.strategy(bars)

    def __repr__(self) -> str:
        return f"MeanReversionFilter({self.strategy}, trend_period={self.trend_period}, max_slope={self.max_slope_pct*100:.2f}%/bar)"


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
# _rsi — Wilder RSI helper
# ---------------------------------------------------------------------------

def _rsi(closes: List[float], period: int = 14) -> float:
    """Wilder RSI from a sequence of closes. Returns 50.0 if insufficient data."""
    if len(closes) < period + 1:
        return 50.0
    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    recent = deltas[-period:]
    avg_gain = sum(d for d in recent if d > 0) / period
    avg_loss = sum(abs(d) for d in recent if d < 0) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


# ---------------------------------------------------------------------------
# RSIFilter — suppress signals that contradict RSI momentum
# ---------------------------------------------------------------------------

class RSIFilter:
    """
    Suppresses signals that contradict RSI momentum.

    LONG signal kept only when RSI > rsi_long_min (default 50) — momentum up.
    SHORT signal kept only when RSI < rsi_short_max (default 50) — momentum down.
    Eliminates counter-trend entries at exhaustion points.
    """

    def __init__(
        self,
        strategy,
        period: int = 14,
        rsi_long_min: float = 50.0,
        rsi_short_max: float = 50.0,
    ):
        self.strategy = strategy
        self.period = period
        self.rsi_long_min = rsi_long_min
        self.rsi_short_max = rsi_short_max

    def __call__(self, bars: List[Bar]) -> Signal:
        signal = self.strategy(bars)
        if signal == 0:
            return 0
        closes = [b["close"] for b in bars]
        rsi = _rsi(closes, self.period)
        if signal == 1 and rsi < self.rsi_long_min:
            return 0
        if signal == -1 and rsi > self.rsi_short_max:
            return 0
        return signal

    def __repr__(self) -> str:
        return (
            f"RSIFilter({self.strategy}, period={self.period}, "
            f"long_min={self.rsi_long_min}, short_max={self.rsi_short_max})"
        )


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

# RSI-filtered versions
dual_ma_rsi_btc_daily = RSIFilter(DualMA(fast=10, slow=30))
dual_ma_rsi_filtered = RSIFilter(RegimeFilter(DualMA(fast=10, slow=30), trend_period=50, slope_bars=5, min_slope_pct=0.10))

# Bollinger Band mean reversion (MD-175: MAE/MFE fit — MR fits range regimes)
bollinger_mr_btc_daily = BollingerMeanReversion(lookback=20, num_std=2.0, trend_lookback=50, trend_threshold=0.001)
bollinger_mr_loose = BollingerMeanReversion(lookback=20, num_std=2.0, trend_lookback=50, trend_threshold=0.005)

NAMED_STRATEGIES: Dict[str, object] = {
    "DualMA_10_30": dual_ma_btc_daily,
    "Donchian_20": donchian_btc_daily,
    "DonchianConfirmed_20": donchian_confirmed_btc_daily,
    "DualMA_filtered": dual_ma_filtered,
    "Donchian_filtered": donchian_filtered,
    "DonchianConfirmed_filtered": donchian_confirmed_filtered,
    "DualMA_RSI": dual_ma_rsi_btc_daily,
    "DualMA_RSI_filtered": dual_ma_rsi_filtered,
    "BollingerMR_20": bollinger_mr_btc_daily,
    "BollingerMR_loose": bollinger_mr_loose,
}


# --- Auto-generated strategies (strategy_generator.py) ---
gen_DonchianConfirmed_a7186a = DonchianConfirmed(period=15)
NAMED_STRATEGIES["gen_DonchianConfirmed_a7186a"] = gen_DonchianConfirmed_a7186a
gen_DualMA_RF_602541 = RegimeFilter(DualMA(fast=15, slow=20), trend_period=50, slope_bars=5, min_slope_pct=0.2)
NAMED_STRATEGIES["gen_DualMA_RF_602541"] = gen_DualMA_RF_602541
gen_BollingerMeanReversion_f91248 = BollingerMeanReversion(lookback=25, num_std=2.0, trend_lookback=40, trend_threshold=0.005)
NAMED_STRATEGIES["gen_BollingerMeanReversion_f91248"] = gen_BollingerMeanReversion_f91248
gen_BollingerMeanReversion_RF_7abfe4 = MeanReversionFilter(BollingerMeanReversion(lookback=15, num_std=1.5, trend_lookback=60, trend_threshold=0.005), trend_period=60, slope_bars=7, max_slope_pct=0.05)
NAMED_STRATEGIES["gen_BollingerMeanReversion_RF_7abfe4"] = gen_BollingerMeanReversion_RF_7abfe4
gen_BollingerMeanReversion_RF_598b24 = MeanReversionFilter(BollingerMeanReversion(lookback=20, num_std=1.5, trend_lookback=40, trend_threshold=0.005), trend_period=50, slope_bars=3, max_slope_pct=0.2)
NAMED_STRATEGIES["gen_BollingerMeanReversion_RF_598b24"] = gen_BollingerMeanReversion_RF_598b24


# --- Auto-generated strategies (strategy_generator.py) ---
gen_Donchian_RF_5e649e = RegimeFilter(Donchian(period=55), trend_period=50, slope_bars=7, min_slope_pct=0.1)
NAMED_STRATEGIES["gen_Donchian_RF_5e649e"] = gen_Donchian_RF_5e649e
gen_Donchian_RSI_d3d59e = RSIFilter(Donchian(period=55), period=10, rsi_long_min=45, rsi_short_max=50)
NAMED_STRATEGIES["gen_Donchian_RSI_d3d59e"] = gen_Donchian_RSI_d3d59e
gen_DualMA_RF_eda1cb = RegimeFilter(DualMA(fast=5, slow=60), trend_period=40, slope_bars=5, min_slope_pct=0.2)
NAMED_STRATEGIES["gen_DualMA_RF_eda1cb"] = gen_DualMA_RF_eda1cb


# --- Auto-generated strategies (strategy_generator.py) ---
gen_DonchianConfirmed_RSI_9b2bf4 = RSIFilter(DonchianConfirmed(period=10), period=21, rsi_long_min=50, rsi_short_max=50)
NAMED_STRATEGIES["gen_DonchianConfirmed_RSI_9b2bf4"] = gen_DonchianConfirmed_RSI_9b2bf4
