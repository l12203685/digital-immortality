"""
Extended strategy types derived from PLA logic analysis (950 strategies).

The existing pool (DualMA, Donchian, BollingerMR) covers MA-crossover,
channel-breakout, and BB-mean-reversion. The PLA corpus reveals significant
untapped indicator families:

    CCI  — 14+ strategies in PLA corpus (breakout, day-trade, trend)
    DMI  — 14+ strategies (ADX-filtered directional movement)
    MACD — 13+ strategies (histogram crossover, trend-following)
    ORB  — 10+ strategies (opening-range breakout, intraday)
    KC   — 15+ strategies (Keltner Channel ATR-based bands)

Each class conforms to StrategyFn: (List[Bar]) -> Signal.
"""

import math
from typing import Dict, List

# Re-use framework types
from trading.backtest_framework import Bar, Signal, _mean


# ---------------------------------------------------------------------------
# Helpers (no external TA libraries)
# ---------------------------------------------------------------------------

def _ema(values: List[float], period: int) -> List[float]:
    """Exponential Moving Average. Returns list same length as input.
    First (period-1) entries are SMA-seeded."""
    if not values or period < 1:
        return []
    result: List[float] = []
    k = 2.0 / (period + 1)
    # Seed with SMA of first `period` values
    if len(values) < period:
        sma = sum(values) / len(values)
        return [sma] * len(values)
    sma = sum(values[:period]) / period
    result = [0.0] * (period - 1) + [sma]
    for i in range(period, len(values)):
        ema_val = values[i] * k + result[-1] * (1.0 - k)
        result.append(ema_val)
    return result


def _true_range(bars: List[Bar]) -> List[float]:
    """True Range for each bar. First bar uses high - low."""
    if not bars:
        return []
    tr: List[float] = [bars[0]["high"] - bars[0]["low"]]
    for i in range(1, len(bars)):
        h = bars[i]["high"]
        l = bars[i]["low"]
        pc = bars[i - 1]["close"]
        tr.append(max(h - l, abs(h - pc), abs(l - pc)))
    return tr


def _atr(bars: List[Bar], period: int) -> List[float]:
    """Average True Range (Wilder smoothing via EMA)."""
    tr = _true_range(bars)
    return _ema(tr, period)


def _sma(values: List[float], period: int) -> float:
    """Simple moving average of last `period` values."""
    if len(values) < period:
        return sum(values) / len(values) if values else 0.0
    return sum(values[-period:]) / period


# ---------------------------------------------------------------------------
# CCIStrategy — Commodity Channel Index Crossover
# ---------------------------------------------------------------------------
# PLA sources: Q_CT03_060M_CCI, OSCAR028_TXALL_CCICHANNEL_LO, KCCCI, etc.
# CCI = (TypicalPrice - SMA(TP, n)) / (0.015 * MeanDeviation)
# Entry: CCI > +threshold -> LONG, CCI < -threshold -> SHORT
# Exit: CCI crosses zero -> FLAT

class CCIStrategy:
    """
    CCI crossover strategy.

    Long when CCI crosses above +threshold.
    Short when CCI crosses below -threshold.
    Flat when CCI reverts toward zero (between thresholds).

    Parameters
    ----------
    period : int
        Lookback for CCI calculation (default 20).
    threshold : float
        CCI level for entry signals (default 100).
    """

    def __init__(self, period: int = 20, threshold: float = 100.0):
        if period < 2:
            raise ValueError(f"period must be >= 2, got {period}")
        self.period = period
        self.threshold = threshold

    def _cci(self, bars: List[Bar]) -> float:
        """Compute current CCI value."""
        if len(bars) < self.period:
            return 0.0
        window = bars[-self.period:]
        tp_values = [(b["high"] + b["low"] + b["close"]) / 3.0 for b in window]
        tp_mean = sum(tp_values) / len(tp_values)
        mean_dev = sum(abs(tp - tp_mean) for tp in tp_values) / len(tp_values)
        if mean_dev == 0:
            return 0.0
        current_tp = tp_values[-1]
        return (current_tp - tp_mean) / (0.015 * mean_dev)

    def __call__(self, bars: List[Bar]) -> Signal:
        if len(bars) < self.period:
            return 0
        cci_val = self._cci(bars)
        if cci_val > self.threshold:
            return 1
        if cci_val < -self.threshold:
            return -1
        return 0

    def __repr__(self) -> str:
        return f"CCIStrategy(period={self.period}, threshold={self.threshold})"


# ---------------------------------------------------------------------------
# DMIStrategy — Directional Movement Index with ADX filter
# ---------------------------------------------------------------------------
# PLA sources: CL009_TX_DMIX2_LO, Q_CT07_060M_DMI, 027_TX_MACDADX_L0, etc.
# +DI > -DI AND ADX > threshold -> LONG
# -DI > +DI AND ADX > threshold -> SHORT

class DMIStrategy:
    """
    DMI/ADX directional strategy.

    Long when +DI > -DI and ADX > adx_threshold.
    Short when -DI > +DI and ADX > adx_threshold.
    Flat when ADX < adx_threshold (no trend).

    Parameters
    ----------
    period : int
        Lookback for DI and ADX calculation (default 14).
    adx_threshold : float
        Minimum ADX to confirm trend (default 25.0).
    """

    def __init__(self, period: int = 14, adx_threshold: float = 25.0):
        if period < 2:
            raise ValueError(f"period must be >= 2, got {period}")
        self.period = period
        self.adx_threshold = adx_threshold

    def _compute_dmi(self, bars: List[Bar]) -> tuple:
        """Compute +DI, -DI, ADX from bar data. Returns (plus_di, minus_di, adx)."""
        n = len(bars)
        if n < self.period + 1:
            return (0.0, 0.0, 0.0)

        plus_dm_list: List[float] = []
        minus_dm_list: List[float] = []
        tr_list: List[float] = []

        for i in range(1, n):
            h = bars[i]["high"]
            l = bars[i]["low"]
            ph = bars[i - 1]["high"]
            pl = bars[i - 1]["low"]
            pc = bars[i - 1]["close"]

            up_move = h - ph
            down_move = pl - l
            plus_dm = up_move if (up_move > down_move and up_move > 0) else 0.0
            minus_dm = down_move if (down_move > up_move and down_move > 0) else 0.0
            tr = max(h - l, abs(h - pc), abs(l - pc))

            plus_dm_list.append(plus_dm)
            minus_dm_list.append(minus_dm)
            tr_list.append(tr)

        # Wilder smoothing (same as EMA with period)
        smoothed_plus_dm = _ema(plus_dm_list, self.period)
        smoothed_minus_dm = _ema(minus_dm_list, self.period)
        smoothed_tr = _ema(tr_list, self.period)

        if not smoothed_tr or smoothed_tr[-1] == 0:
            return (0.0, 0.0, 0.0)

        plus_di = 100.0 * smoothed_plus_dm[-1] / smoothed_tr[-1]
        minus_di = 100.0 * smoothed_minus_dm[-1] / smoothed_tr[-1]

        # ADX = smoothed |+DI - -DI| / (+DI + -DI)
        di_sum = plus_di + minus_di
        if di_sum == 0:
            return (plus_di, minus_di, 0.0)

        # Compute DX series for ADX smoothing
        dx_list: List[float] = []
        for i in range(len(smoothed_tr)):
            st = smoothed_tr[i]
            if st == 0:
                dx_list.append(0.0)
                continue
            pdi = 100.0 * smoothed_plus_dm[i] / st
            mdi = 100.0 * smoothed_minus_dm[i] / st
            ds = pdi + mdi
            dx_list.append(100.0 * abs(pdi - mdi) / ds if ds > 0 else 0.0)

        adx_series = _ema(dx_list, self.period)
        adx = adx_series[-1] if adx_series else 0.0

        return (plus_di, minus_di, adx)

    def __call__(self, bars: List[Bar]) -> Signal:
        if len(bars) < self.period * 2 + 1:
            return 0
        plus_di, minus_di, adx = self._compute_dmi(bars)
        if adx < self.adx_threshold:
            return 0
        if plus_di > minus_di:
            return 1
        if minus_di > plus_di:
            return -1
        return 0

    def __repr__(self) -> str:
        return f"DMIStrategy(period={self.period}, adx_threshold={self.adx_threshold})"


# ---------------------------------------------------------------------------
# MACDStrategy — MACD Histogram Crossover
# ---------------------------------------------------------------------------
# PLA sources: 001_TX_MACD_LO, Q_CT06_060M_MACD, CL012_TX_MACD_LO, etc.
# MACD Line = EMA(fast) - EMA(slow)
# Signal Line = EMA(MACD, signal)
# Histogram = MACD - Signal
# Entry: histogram > 0 -> LONG, histogram < 0 -> SHORT

class MACDStrategy:
    """
    MACD histogram crossover.

    Long when MACD histogram > 0 (MACD line above signal line).
    Short when MACD histogram < 0 (MACD line below signal line).

    Parameters
    ----------
    fast : int
        Fast EMA period (default 12).
    slow : int
        Slow EMA period (default 26).
    signal : int
        Signal line EMA period (default 9).
    """

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        if fast >= slow:
            raise ValueError(f"fast ({fast}) must be < slow ({slow})")
        self.fast = fast
        self.slow = slow
        self.signal = signal

    def __call__(self, bars: List[Bar]) -> Signal:
        required = self.slow + self.signal
        if len(bars) < required:
            return 0

        closes = [b["close"] for b in bars]
        fast_ema = _ema(closes, self.fast)
        slow_ema = _ema(closes, self.slow)

        # MACD line = fast EMA - slow EMA
        macd_line = [f - s for f, s in zip(fast_ema, slow_ema)]

        # Signal line = EMA of MACD line
        signal_line = _ema(macd_line, self.signal)

        # Histogram = MACD - Signal
        histogram = macd_line[-1] - signal_line[-1]

        if histogram > 0:
            return 1
        if histogram < 0:
            return -1
        return 0

    def __repr__(self) -> str:
        return f"MACDStrategy(fast={self.fast}, slow={self.slow}, signal={self.signal})"


# ---------------------------------------------------------------------------
# ORBStrategy — Opening Range Breakout (adapted for 24/7 crypto)
# ---------------------------------------------------------------------------
# PLA sources: 064_TXI_ORB_LO, Shuen038_TX_EarlyORB5K_DT, MagicDayTOP10, etc.
# For crypto: use first N bars of each day as "opening range".
# Entry: price breaks above range high -> LONG, below range low -> SHORT.
# Since we operate on bar-level signals (no timestamp), we use the first
# `range_bars` bars of each lookback window as the opening range.

class ORBStrategy:
    """
    Opening Range Breakout adapted for daily bar data.

    Uses the first `range_bars` bars as the opening range.
    Long when price breaks above the range high.
    Short when price breaks below the range low.

    For daily BTC data, range_bars=1 means yesterday's bar defines the range
    and today's breakout triggers entry. For intraday, range_bars is the
    number of initial bars forming the range.

    Parameters
    ----------
    range_bars : int
        Number of bars forming the opening range (default 3).
    atr_filter : float
        Minimum ATR multiple for range width to avoid tight-range noise.
        Set to 0 to disable (default 0.5).
    atr_period : int
        ATR lookback period (default 14).
    """

    def __init__(
        self,
        range_bars: int = 3,
        atr_filter: float = 0.5,
        atr_period: int = 14,
    ):
        if range_bars < 1:
            raise ValueError(f"range_bars must be >= 1, got {range_bars}")
        self.range_bars = range_bars
        self.atr_filter = atr_filter
        self.atr_period = atr_period

    def __call__(self, bars: List[Bar]) -> Signal:
        required = self.range_bars + max(self.atr_period, 1) + 1
        if len(bars) < required:
            return 0

        # Opening range: the `range_bars` bars preceding the current bar
        range_window = bars[-(self.range_bars + 1):-1]
        range_high = max(b["high"] for b in range_window)
        range_low = min(b["low"] for b in range_window)
        range_width = range_high - range_low

        # ATR filter: skip if range is too narrow (likely to produce false breakouts)
        if self.atr_filter > 0:
            atr_values = _atr(bars, self.atr_period)
            current_atr = atr_values[-1] if atr_values else 0.0
            if current_atr > 0 and range_width < self.atr_filter * current_atr:
                return 0

        cur_close = bars[-1]["close"]
        if cur_close > range_high:
            return 1
        if cur_close < range_low:
            return -1
        return 0

    def __repr__(self) -> str:
        return (
            f"ORBStrategy(range_bars={self.range_bars}, "
            f"atr_filter={self.atr_filter}, atr_period={self.atr_period})"
        )


# ---------------------------------------------------------------------------
# KeltnerStrategy — Keltner Channel (EMA +/- ATR * multiplier)
# ---------------------------------------------------------------------------
# PLA sources: 002_TX_Keltner_LO_2010, 016_TX_KCForward_L0, KCCCI,
#              1-003_TXA_30mKeltner_LOS, Q_CT09_060M_KC, Q_CT39_840M_KC, etc.
# Upper = EMA(close, ema_period) + multiplier * ATR(atr_period)
# Lower = EMA(close, ema_period) - multiplier * ATR(atr_period)
# Momentum mode: price > upper -> LONG, price < lower -> SHORT
# Reversion mode: price > upper -> SHORT (overbought), price < lower -> LONG

class KeltnerStrategy:
    """
    Keltner Channel strategy.

    Two modes:
    - momentum: breakout above upper -> LONG, below lower -> SHORT
    - reversion: above upper -> SHORT (overbought), below lower -> LONG

    Parameters
    ----------
    ema_period : int
        Period for center EMA line (default 20).
    atr_period : int
        Period for ATR calculation (default 14).
    multiplier : float
        ATR multiplier for channel width (default 2.0).
    mode : str
        "momentum" or "reversion" (default "momentum").
    """

    def __init__(
        self,
        ema_period: int = 20,
        atr_period: int = 14,
        multiplier: float = 2.0,
        mode: str = "momentum",
    ):
        if ema_period < 2:
            raise ValueError(f"ema_period must be >= 2, got {ema_period}")
        if mode not in ("momentum", "reversion"):
            raise ValueError(f"mode must be 'momentum' or 'reversion', got '{mode}'")
        self.ema_period = ema_period
        self.atr_period = atr_period
        self.multiplier = multiplier
        self.mode = mode

    def __call__(self, bars: List[Bar]) -> Signal:
        required = max(self.ema_period, self.atr_period) + 1
        if len(bars) < required:
            return 0

        closes = [b["close"] for b in bars]
        ema_values = _ema(closes, self.ema_period)
        atr_values = _atr(bars, self.atr_period)

        ema_now = ema_values[-1]
        atr_now = atr_values[-1]

        if atr_now == 0:
            return 0

        upper = ema_now + self.multiplier * atr_now
        lower = ema_now - self.multiplier * atr_now

        cur_close = closes[-1]

        if self.mode == "momentum":
            if cur_close > upper:
                return 1
            if cur_close < lower:
                return -1
        else:  # reversion
            if cur_close > upper:
                return -1  # overbought -> short
            if cur_close < lower:
                return 1   # oversold -> long
        return 0

    def __repr__(self) -> str:
        return (
            f"KeltnerStrategy(ema={self.ema_period}, atr={self.atr_period}, "
            f"mult={self.multiplier}, mode={self.mode})"
        )


# ---------------------------------------------------------------------------
# Convenience: default instances for BTC daily
# ---------------------------------------------------------------------------
cci_btc_daily = CCIStrategy(period=20, threshold=100.0)
dmi_btc_daily = DMIStrategy(period=14, adx_threshold=25.0)
macd_btc_daily = MACDStrategy(fast=12, slow=26, signal=9)
orb_btc_daily = ORBStrategy(range_bars=3, atr_filter=0.5, atr_period=14)
keltner_momentum_btc_daily = KeltnerStrategy(ema_period=20, atr_period=14, multiplier=2.0, mode="momentum")
keltner_reversion_btc_daily = KeltnerStrategy(ema_period=20, atr_period=14, multiplier=2.0, mode="reversion")

# All extended strategies for import
EXTENDED_STRATEGIES: dict[str, object] = {
    "CCI_20_100": cci_btc_daily,
    "DMI_14_25": dmi_btc_daily,
    "MACD_12_26_9": macd_btc_daily,
    "ORB_3": orb_btc_daily,
    "Keltner_momentum_20": keltner_momentum_btc_daily,
    "Keltner_reversion_20": keltner_reversion_btc_daily,
}
