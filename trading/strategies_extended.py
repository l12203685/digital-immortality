"""
Extended strategy types derived from PLA logic analysis (636+ strategies).

The existing pool (DualMA, Donchian, BollingerMR) covers MA-crossover,
channel-breakout, and BB-mean-reversion. The PLA corpus reveals significant
untapped indicator families:

    CCI  — 14+ strategies in PLA corpus (breakout, day-trade, trend)
    DMI  — 14+ strategies (ADX-filtered directional movement)
    MACD — 13+ strategies (histogram crossover, trend-following)
    ORB  — 10+ strategies (opening-range breakout, intraday)
    KC   — 15+ strategies (Keltner Channel ATR-based bands)

Batch 4-6 additions (novel techniques discovered in extended digestion):
    ShakeFilter      — oscillation-count filter from NV2108004_TX15M_Bonny_LT
    SqrtTimeTrail    — sqrt-of-time trailing stop from TXAL_1_007_VCP
    AdaptiveMultiplier — doubles MA period after loss (NV2112008_TX60M_FLT)
    GoldenRatioMA    — phi=1.618 MA period pairs (Drschnabel_TX_trend_oscillation)
    KPower           — buying/selling pressure score (Wesley003_TX_2110KPower_LO)
    BarTiming        — intraday H/L bar-timing analysis (AVgirl_202106_5K)

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

# ---------------------------------------------------------------------------
# TXF (Taiwan Futures) tuned instances
# Derived from PLA corpus patterns (520 strategies digested):
#   CCI: TXAL_028 CCI01 (28-bar period), TXAL_1DK_CCI01 (+/-100 breakout)
#   DMI: CL009_TX_DMIX2, Q_CT07_060M_DMI (14-period, ADX 20-25)
#   MACD: 001_TX_MACD_LO (12/26/9 histogram, hourly), CL012_TX_MACD_LO
#   ORB: 003_HLORB01 (3-min ORB), 123_TX_HLORB (prior H/L breakout)
#   KC: 002_Keltner_LO_2010 (KLen=18, ATR*3.8), 030_KC01 (KLen=19, ATR*3.5)
# ---------------------------------------------------------------------------

# CCI: PLA uses 28-bar period; threshold +/-100 standard; also daily variant
cci_txf_28 = CCIStrategy(period=28, threshold=100.0)
cci_txf_daily = CCIStrategy(period=20, threshold=100.0)

# DMI: PLA uses 14-period; ADX threshold 20 (slightly more permissive for TXF)
dmi_txf_14 = DMIStrategy(period=14, adx_threshold=20.0)
dmi_txf_strict = DMIStrategy(period=14, adx_threshold=30.0)

# MACD: PLA uses standard 12/26/9; histogram count entry pattern
macd_txf_standard = MACDStrategy(fast=12, slow=26, signal=9)
macd_txf_fast = MACDStrategy(fast=8, slow=21, signal=5)

# ORB: PLA uses 3-min bars with prior H/L; range_bars=1 for daily breakout
orb_txf_1 = ORBStrategy(range_bars=1, atr_filter=0.3, atr_period=14)
orb_txf_3 = ORBStrategy(range_bars=3, atr_filter=0.5, atr_period=14)

# Keltner: PLA KLen=18-19, ATR multiplier 3.5-3.8 (wider than BTC default)
keltner_txf_momentum = KeltnerStrategy(
    ema_period=18, atr_period=14, multiplier=3.5, mode="momentum",
)
keltner_txf_reversion = KeltnerStrategy(
    ema_period=19, atr_period=14, multiplier=3.5, mode="reversion",
)

# ---------------------------------------------------------------------------
# StochasticStrategy — Slow Stochastic %K/%D Oscillator
# ---------------------------------------------------------------------------
# PLA sources: CDPKD_D0 (CDP+KD combo), 004_TX_KDHL_LT (KD H/L breakout),
#              SlowKD overbought/oversold strategy on FITX 5-min, etc.
# SlowK = SMA(raw %K, d_period); SlowD = SMA(SlowK, d_period)
# Entry: SlowK > overbought threshold -> LONG (momentum), or
#        reversion mode: SlowK > overbought -> SHORT (overbought)
# The PLA corpus uses 80/20 and 85/15 thresholds most frequently.

class StochasticStrategy:
    """
    Slow Stochastic %K/%D oscillator.

    Two modes:
    - momentum: buy when %K crosses above oversold, sell when overbought crossed
      (simplified: long when %K > overbought, short when %K < oversold)
    - reversion: long when %K < oversold (buy the dip), short when %K > overbought

    Parameters
    ----------
    k_period : int
        Raw %K lookback (default 14).
    d_period : int
        Smoothing period for SlowK and SlowD (default 3).
    overbought : float
        Upper threshold (default 80).
    oversold : float
        Lower threshold (default 20).
    mode : str
        "momentum" or "reversion" (default "reversion" — PLA corpus favors
        mean-reversion usage of stochastic on TXF).
    """

    def __init__(
        self,
        k_period: int = 14,
        d_period: int = 3,
        overbought: float = 80.0,
        oversold: float = 20.0,
        mode: str = "reversion",
    ):
        if k_period < 2:
            raise ValueError(f"k_period must be >= 2, got {k_period}")
        if d_period < 1:
            raise ValueError(f"d_period must be >= 1, got {d_period}")
        if mode not in ("momentum", "reversion"):
            raise ValueError(f"mode must be 'momentum' or 'reversion', got '{mode}'")
        self.k_period = k_period
        self.d_period = d_period
        self.overbought = overbought
        self.oversold = oversold
        self.mode = mode

    def _slow_k(self, bars: List[Bar]) -> List[float]:
        """Compute SlowK series (smoothed raw %K)."""
        n = len(bars)
        if n < self.k_period:
            return []

        raw_k: List[float] = []
        for i in range(self.k_period - 1, n):
            window = bars[i - self.k_period + 1 : i + 1]
            lowest = min(b["low"] for b in window)
            highest = max(b["high"] for b in window)
            span = highest - lowest
            current_close = bars[i]["close"]
            if span == 0:
                raw_k.append(50.0)  # neutral when no range
            else:
                raw_k.append(100.0 * (current_close - lowest) / span)

        # SlowK = SMA of raw_k over d_period
        slow_k: List[float] = []
        for i in range(len(raw_k)):
            window = raw_k[max(0, i - self.d_period + 1) : i + 1]
            slow_k.append(sum(window) / len(window))
        return slow_k

    def __call__(self, bars: List[Bar]) -> Signal:
        required = self.k_period + self.d_period
        if len(bars) < required:
            return 0

        slow_k = self._slow_k(bars)
        if not slow_k:
            return 0

        k_val = slow_k[-1]

        if self.mode == "momentum":
            # Trend-following: long above mid-zone, short below
            if k_val > self.overbought:
                return 1
            if k_val < self.oversold:
                return -1
        else:  # reversion
            # Mean-reversion: buy the oversold dip, sell the overbought peak
            if k_val < self.oversold:
                return 1
            if k_val > self.overbought:
                return -1
        return 0

    def __repr__(self) -> str:
        return (
            f"StochasticStrategy(k={self.k_period}, d={self.d_period}, "
            f"ob={self.overbought}, os={self.oversold}, mode={self.mode})"
        )


# ---------------------------------------------------------------------------
# CDPStrategy — Central Demark Pivot (AH/NH/NL/AL Levels)
# ---------------------------------------------------------------------------
# PLA sources: 13+ CDP strategies in corpus. Formula: CDP = (H+L+2C)/4
#   AH (above-high) = CDP + (H - L)
#   NH (near-high)  = 2*CDP - L
#   NL (near-low)   = 2*CDP - H
#   AL (above-low)  = CDP - (H - L)
# Trend mode: price > NH -> LONG, price < NL -> SHORT
# Reversion mode: price > AH -> SHORT (extreme overbought), price < AL -> LONG

class CDPStrategy:
    """
    Central Demark Pivot strategy.

    CDP = (prev_H + prev_L + 2 * prev_C) / 4
    AH = CDP + (prev_H - prev_L)   [Above High — extreme resistance]
    NH = 2*CDP - prev_L             [Near High — normal resistance]
    NL = 2*CDP - prev_H             [Near Low  — normal support]
    AL = CDP - (prev_H - prev_L)    [Above Low — extreme support]

    Breakout mode:
      - Close > NH -> LONG  (price breaks near-resistance)
      - Close < NL -> SHORT (price breaks near-support)

    Reversion mode:
      - Close > AH -> SHORT (extreme overbought at far resistance)
      - Close < AL -> LONG  (extreme oversold at far support)

    Parameters
    ----------
    mode : str
        "breakout" or "reversion" (default "breakout").
    """

    def __init__(self, mode: str = "breakout"):
        if mode not in ("breakout", "reversion"):
            raise ValueError(f"mode must be 'breakout' or 'reversion', got '{mode}'")
        self.mode = mode

    def _cdp_levels(self, prev_bar: Bar) -> tuple:
        """Compute CDP pivot levels from previous bar's OHLC."""
        h = prev_bar["high"]
        l = prev_bar["low"]
        c = prev_bar["close"]
        cdp = (h + l + 2.0 * c) / 4.0
        spread = h - l
        ah = cdp + spread
        nh = 2.0 * cdp - l
        nl = 2.0 * cdp - h
        al = cdp - spread
        return (cdp, ah, nh, nl, al)

    def __call__(self, bars: List[Bar]) -> Signal:
        if len(bars) < 2:
            return 0

        # Use the second-to-last bar as "previous" bar for pivot calculation
        prev_bar = bars[-2]
        cur_close = bars[-1]["close"]

        _, ah, nh, nl, al = self._cdp_levels(prev_bar)

        if self.mode == "breakout":
            if cur_close > nh:
                return 1
            if cur_close < nl:
                return -1
        else:  # reversion
            if cur_close > ah:
                return -1  # extreme overbought
            if cur_close < al:
                return 1   # extreme oversold
        return 0

    def __repr__(self) -> str:
        return f"CDPStrategy(mode={self.mode})"


# ---------------------------------------------------------------------------
# ParabolicSARStrategy — Parabolic Stop and Reverse
# ---------------------------------------------------------------------------
# PLA sources: TXAL_030_SAR01 (30-bar SAR, Drawdown Control), Kuang SAR,
#              BN_SAR_FDO (SAR + tunnel overlay), SAR + gap-up pre-condition.
# Standard Parabolic SAR: AF starts at af_start, increments by af_step
# each time a new extreme is set, capped at af_max.
# Signal: price > SAR -> LONG; price < SAR -> SHORT.

class ParabolicSARStrategy:
    """
    Parabolic Stop and Reverse (SAR) trend-following strategy.

    Long when price is above the SAR (bullish phase).
    Short when price is below the SAR (bearish phase).

    Parameters
    ----------
    af_start : float
        Initial acceleration factor (default 0.02).
    af_step : float
        AF increment on new extremes (default 0.02).
    af_max : float
        Maximum acceleration factor (default 0.20).
    """

    def __init__(
        self,
        af_start: float = 0.02,
        af_step: float = 0.02,
        af_max: float = 0.20,
    ):
        if af_start <= 0 or af_step <= 0 or af_max <= 0:
            raise ValueError("af_start, af_step, af_max must all be positive")
        if af_start > af_max:
            raise ValueError(f"af_start ({af_start}) must be <= af_max ({af_max})")
        self.af_start = af_start
        self.af_step = af_step
        self.af_max = af_max

    def _compute_sar(self, bars: List[Bar]) -> float:
        """Compute current SAR value by stepping through bar history."""
        if len(bars) < 3:
            return bars[-1]["close"] if bars else 0.0

        # Determine initial trend from first two bars
        is_long = bars[1]["close"] > bars[0]["close"]
        if is_long:
            ep = bars[0]["high"]
            sar = bars[0]["low"]
        else:
            ep = bars[0]["low"]
            sar = bars[0]["high"]

        af = self.af_start

        for i in range(1, len(bars) - 1):
            bar = bars[i]
            # Update SAR
            sar = sar + af * (ep - sar)

            # Clamp SAR: in long mode, SAR <= min of prior two bars' lows
            if is_long:
                sar = min(sar, bars[i - 1]["low"])
                if i >= 2:
                    sar = min(sar, bars[i - 2]["low"])
                # Check reversal
                if bar["low"] < sar:
                    is_long = False
                    sar = ep
                    ep = bar["low"]
                    af = self.af_start
                else:
                    if bar["high"] > ep:
                        ep = bar["high"]
                        af = min(af + self.af_step, self.af_max)
            else:
                sar = max(sar, bars[i - 1]["high"])
                if i >= 2:
                    sar = max(sar, bars[i - 2]["high"])
                # Check reversal
                if bar["high"] > sar:
                    is_long = True
                    sar = ep
                    ep = bar["high"]
                    af = self.af_start
                else:
                    if bar["low"] < ep:
                        ep = bar["low"]
                        af = min(af + self.af_step, self.af_max)

        # Final SAR for the last bar
        sar = sar + af * (ep - sar)
        return sar

    def __call__(self, bars: List[Bar]) -> Signal:
        if len(bars) < 3:
            return 0

        sar = self._compute_sar(bars)
        cur_close = bars[-1]["close"]

        if cur_close > sar:
            return 1
        if cur_close < sar:
            return -1
        return 0

    def __repr__(self) -> str:
        return (
            f"ParabolicSARStrategy(af_start={self.af_start}, "
            f"af_step={self.af_step}, af_max={self.af_max})"
        )


# ---------------------------------------------------------------------------
# GapFadeStrategy — Gap Open Fade / Follow
# ---------------------------------------------------------------------------
# PLA sources: 93 gap-related entries in corpus (gap-up/gap-down entries,
#              gap+CDP combos, gap-fade at session open, SAR+gap pre-condition).
# Logic: compare today's open vs prior day's close.
#   gap_pct = (open - prev_close) / prev_close
# Fade mode: large gap-up -> SHORT (fade); large gap-down -> LONG
# Follow mode: large gap-up -> LONG (momentum); large gap-down -> SHORT
# ATR filter: gap must exceed atr_threshold * ATR to be tradeable.

class GapFadeStrategy:
    """
    Gap open fade or follow strategy.

    Detects a gap between current bar's open and prior bar's close.
    Uses ATR to normalize the gap magnitude.

    Two modes:
    - fade: gap-up is overbought -> SHORT; gap-down is oversold -> LONG
    - follow: gap-up confirms momentum -> LONG; gap-down confirms downtrend -> SHORT

    Parameters
    ----------
    gap_threshold : float
        Minimum gap as fraction of price to trigger a signal (default 0.01 = 1%).
    atr_period : int
        ATR lookback for dynamic threshold adjustment (default 14).
    mode : str
        "fade" or "follow" (default "fade" — dominant in PLA corpus).
    """

    def __init__(
        self,
        gap_threshold: float = 0.01,
        atr_period: int = 14,
        mode: str = "fade",
    ):
        if gap_threshold <= 0:
            raise ValueError(f"gap_threshold must be > 0, got {gap_threshold}")
        if mode not in ("fade", "follow"):
            raise ValueError(f"mode must be 'fade' or 'follow', got '{mode}'")
        self.gap_threshold = gap_threshold
        self.atr_period = atr_period
        self.mode = mode

    def __call__(self, bars: List[Bar]) -> Signal:
        if len(bars) < self.atr_period + 1:
            return 0

        cur_open = bars[-1]["open"]
        prev_close = bars[-2]["close"]

        if prev_close == 0:
            return 0

        gap_pct = (cur_open - prev_close) / prev_close

        # Only fire if gap exceeds threshold
        if abs(gap_pct) < self.gap_threshold:
            return 0

        is_gap_up = gap_pct > 0

        if self.mode == "fade":
            return -1 if is_gap_up else 1
        else:  # follow
            return 1 if is_gap_up else -1

    def __repr__(self) -> str:
        return (
            f"GapFadeStrategy(gap_threshold={self.gap_threshold}, "
            f"atr_period={self.atr_period}, mode={self.mode})"
        )


# ---------------------------------------------------------------------------
# Stochastic KD instances
# PLA patterns: SlowKD 80/20 threshold (FITX 5-min), KD H/L breakout (TX 60min)
# reversion (oversold <20 = long, overbought >80 = short) is primary PLA usage.
# ---------------------------------------------------------------------------
stochastic_txf_reversion = StochasticStrategy(
    k_period=14, d_period=3, overbought=80.0, oversold=20.0, mode="reversion",
)
stochastic_txf_momentum = StochasticStrategy(
    k_period=9, d_period=3, overbought=80.0, oversold=20.0, mode="momentum",
)

# ---------------------------------------------------------------------------
# CDP instances
# PLA: CDP = (H+L+2C)/4, breakout at NH/NL, reversion at AH/AL
# ---------------------------------------------------------------------------
cdp_breakout = CDPStrategy(mode="breakout")
cdp_reversion = CDPStrategy(mode="reversion")

# ---------------------------------------------------------------------------
# Parabolic SAR instances
# PLA SAR01: af_start=0.02, af_step=0.02, af_max=0.20 (standard)
# BN_SAR_FDO: AFStep 0.01-0.03 range; fast variant uses 0.01/0.01/0.10
# ---------------------------------------------------------------------------
sar_std = ParabolicSARStrategy(af_start=0.02, af_step=0.02, af_max=0.20)
sar_fast = ParabolicSARStrategy(af_start=0.01, af_step=0.01, af_max=0.10)

# ---------------------------------------------------------------------------
# Gap Fade / Follow instances
# PLA: 93 gap entries; gap threshold 0.5-2% typical for TXF intraday
# ---------------------------------------------------------------------------
gap_fade_1pct = GapFadeStrategy(gap_threshold=0.01, atr_period=14, mode="fade")
gap_fade_2pct = GapFadeStrategy(gap_threshold=0.02, atr_period=14, mode="fade")
gap_follow_1pct = GapFadeStrategy(gap_threshold=0.01, atr_period=14, mode="follow")


# ---------------------------------------------------------------------------
# ShakeFilterStrategy — Oscillation-count chop filter
# ---------------------------------------------------------------------------
# PLA source: NV2108004_TX15M_Bonny_LT (Bonny strategy).
# "Shake oscillator": counts how many of the last `period` bars the mid-price
# direction is consistent. If the count < period * shake_threshold, the market
# is choppy ("shaking") and entry is suppressed.
# Logic: mid = (H+L)/2. Count bars where mid[i] > mid[i-1].
#   oscillation_score = count_up / period  (or min(count_up, count_dn)/period)
# Entry allowed only when score >= shake_threshold (directional conviction).
# ATR channel breakout is the underlying entry trigger.

class ShakeFilterStrategy:
    """
    ATR channel breakout gated by a shake-filter oscillation score.

    The shake filter counts consecutive mid-price direction bars over `period`.
    Entry is suppressed when the oscillation score < shake_threshold, indicating
    a choppy, non-directional market.

    Parameters
    ----------
    period : int
        Lookback for shake oscillation count and channel (default 20).
    shake_threshold : float
        Minimum fraction of consistent bars required to allow entry (default 0.33).
        Mirrors Bonny's ``Len/4`` threshold (0.25) but allows configuration.
    atr_period : int
        ATR lookback for channel width (default 14).
    """

    def __init__(
        self,
        period: int = 20,
        shake_threshold: float = 0.33,
        atr_period: int = 14,
    ):
        if period < 4:
            raise ValueError(f"period must be >= 4, got {period}")
        if not 0.0 < shake_threshold < 1.0:
            raise ValueError(f"shake_threshold must be in (0, 1), got {shake_threshold}")
        self.period = period
        self.shake_threshold = shake_threshold
        self.atr_period = atr_period

    def _oscillation_score(self, bars: List[Bar]) -> float:
        """Fraction of bars where mid-price moved in dominant direction."""
        window = bars[-self.period:]
        if len(window) < 2:
            return 0.0
        count_up = 0
        count_dn = 0
        for i in range(1, len(window)):
            mid_now = (window[i]["high"] + window[i]["low"]) / 2.0
            mid_prev = (window[i - 1]["high"] + window[i - 1]["low"]) / 2.0
            if mid_now > mid_prev:
                count_up += 1
            elif mid_now < mid_prev:
                count_dn += 1
        total = len(window) - 1
        # Score = dominant direction fraction (how one-sided the oscillation is)
        return max(count_up, count_dn) / total if total > 0 else 0.0

    def __call__(self, bars: List[Bar]) -> Signal:
        required = self.period + self.atr_period + 1
        if len(bars) < required:
            return 0

        # Gate: suppress entry in choppy markets
        if self._oscillation_score(bars) < self.shake_threshold:
            return 0

        # Channel: highest/lowest close over period
        window = bars[-self.period:]
        channel_high = max(b["close"] for b in window[:-1])
        channel_low = min(b["close"] for b in window[:-1])
        cur_close = bars[-1]["close"]

        # ATR-widen channel slightly to reduce false breakouts
        atr_vals = _atr(bars, self.atr_period)
        atr_now = atr_vals[-1] if atr_vals else 0.0

        if cur_close > channel_high + 0.1 * atr_now:
            return 1
        if cur_close < channel_low - 0.1 * atr_now:
            return -1
        return 0

    def __repr__(self) -> str:
        return (
            f"ShakeFilterStrategy(period={self.period}, "
            f"shake_threshold={self.shake_threshold}, atr_period={self.atr_period})"
        )


# ---------------------------------------------------------------------------
# SqrtTimeTrailStrategy — Square-root-of-time tightening trailing stop
# ---------------------------------------------------------------------------
# PLA source: TXAL_1_007_VCP_RangeBreakout.
# Trail formula: exit = entry + max_profit - ATR(period) / sqrt(bars_since_entry)
# As the trade ages, sqrt(bars) grows → ATR/sqrt(bars) shrinks → trail tightens.
# This naturally preserves more profit as a winning trade matures.
# We approximate "bars since entry" using a stateful rolling peak tracker.

class SqrtTimeTrailStrategy:
    """
    Volatility-contraction breakout with square-root-of-time trailing stop.

    Entry: close breaks above rolling `breakout_period` high (long) or
           below rolling low (short).
    Trailing: stop = entry + max_excursion - ATR / sqrt(bars_since_peak)
    The trail tightens as time passes, locking in profit progressively.

    Parameters
    ----------
    breakout_period : int
        Lookback for channel breakout (default 14).
    atr_period : int
        ATR period for trail calculation (default 14).
    trail_atr_mult : float
        ATR multiplier for initial trail distance (default 1.5).
    """

    def __init__(
        self,
        breakout_period: int = 14,
        atr_period: int = 14,
        trail_atr_mult: float = 1.5,
    ):
        if breakout_period < 2:
            raise ValueError(f"breakout_period must be >= 2, got {breakout_period}")
        if trail_atr_mult <= 0:
            raise ValueError(f"trail_atr_mult must be > 0, got {trail_atr_mult}")
        self.breakout_period = breakout_period
        self.atr_period = atr_period
        self.trail_atr_mult = trail_atr_mult
        # State: (direction, entry_price, max_excursion, bars_held)
        self._state: tuple[int, float, float, int] = (0, 0.0, 0.0, 0)

    def _update_state(
        self, signal: int, cur_close: float, atr_now: float
    ) -> Signal:
        """Update trailing state and return final signal."""
        direction, entry_price, max_exc, bars_held = self._state

        if direction == 0 and signal != 0:
            # New entry
            self._state = (signal, cur_close, 0.0, 1)
            return signal

        if direction != 0:
            bars_held += 1
            if direction == 1:
                excursion = cur_close - entry_price
            else:
                excursion = entry_price - cur_close

            new_max = max(max_exc, excursion)
            # Sqrt-of-time trail: tighter as bars_held grows
            trail_dist = self.trail_atr_mult * atr_now / math.sqrt(max(1, bars_held))
            trail_stop = entry_price + direction * (new_max - trail_dist)

            hit_trail = (
                (direction == 1 and cur_close < trail_stop) or
                (direction == -1 and cur_close > trail_stop)
            )

            if hit_trail or (signal != 0 and signal != direction):
                self._state = (0, 0.0, 0.0, 0)
                return 0

            self._state = (direction, entry_price, new_max, bars_held)
            return direction

        return 0

    def __call__(self, bars: List[Bar]) -> Signal:
        required = self.breakout_period + self.atr_period + 1
        if len(bars) < required:
            return 0

        window = bars[-(self.breakout_period + 1):-1]
        channel_high = max(b["high"] for b in window)
        channel_low = min(b["low"] for b in window)

        atr_vals = _atr(bars, self.atr_period)
        atr_now = atr_vals[-1] if atr_vals else 0.0
        cur_close = bars[-1]["close"]

        if cur_close > channel_high:
            raw_signal = 1
        elif cur_close < channel_low:
            raw_signal = -1
        else:
            raw_signal = 0

        return self._update_state(raw_signal, cur_close, atr_now)

    def __repr__(self) -> str:
        return (
            f"SqrtTimeTrailStrategy(breakout_period={self.breakout_period}, "
            f"atr_period={self.atr_period}, trail_atr_mult={self.trail_atr_mult})"
        )


# ---------------------------------------------------------------------------
# AdaptiveMultiplierMAStrategy — doubles MA lookback after a losing trade
# ---------------------------------------------------------------------------
# PLA sources: NV2112008_TX60M_FLT (multiplier=2 after prior loss + sequence),
#              TXF_MAHL_FDT_1 (doubles period: N to 2N after losing trade).
# Concept: when the last trade was a loss, require stronger trend confirmation
# by doubling the MA lookback period. This forces a higher bar for re-entry
# and reduces premature re-entry after whipsaws.

class AdaptiveMultiplierMAStrategy:
    """
    Dual-MA trend strategy with adaptive period after losses.

    Normal mode: MA(base_period) slope for entry.
    Post-loss mode: MA(base_period * loss_multiplier) — doubled lookback
    forces stronger confirmation before the next entry.

    The loss detection is approximated: if the last crossover led to a
    reversal within `base_period` bars, treat it as a loss.

    Parameters
    ----------
    base_period : int
        Normal MA lookback period (default 20).
    loss_multiplier : float
        Factor to scale period after a loss (default 2.0).
    """

    def __init__(
        self,
        base_period: int = 20,
        loss_multiplier: float = 2.0,
    ):
        if base_period < 2:
            raise ValueError(f"base_period must be >= 2, got {base_period}")
        if loss_multiplier < 1.0:
            raise ValueError(f"loss_multiplier must be >= 1.0, got {loss_multiplier}")
        self.base_period = base_period
        self.loss_multiplier = loss_multiplier
        self._last_signal: int = 0
        self._bars_since_entry: int = 0
        self._post_loss: bool = False

    def __call__(self, bars: List[Bar]) -> Signal:
        period = (
            round(self.base_period * self.loss_multiplier)
            if self._post_loss
            else self.base_period
        )
        if len(bars) < period + 1:
            return 0

        closes = [b["close"] for b in bars]
        ma_now = _sma(closes, period)
        ma_prev = _sma(closes[:-1], period)

        # Trend signal: rising MA = long, falling MA = short
        if ma_now > ma_prev and closes[-1] > ma_now:
            new_signal = 1
        elif ma_now < ma_prev and closes[-1] < ma_now:
            new_signal = -1
        else:
            new_signal = 0

        # Detect "loss": if signal reversed quickly (< base_period bars)
        if self._last_signal != 0 and new_signal != self._last_signal:
            self._post_loss = self._bars_since_entry < self.base_period
        elif new_signal != 0:
            if self._last_signal == 0:
                self._bars_since_entry = 0
                self._post_loss = False  # new entry resets post-loss on same direction
            self._bars_since_entry += 1
        else:
            self._bars_since_entry += 1

        self._last_signal = new_signal
        return new_signal

    def __repr__(self) -> str:
        return (
            f"AdaptiveMultiplierMAStrategy(base_period={self.base_period}, "
            f"loss_multiplier={self.loss_multiplier})"
        )


# ---------------------------------------------------------------------------
# GoldenRatioMAStrategy — MA pair with phi=1.618 period relationship
# ---------------------------------------------------------------------------
# PLA source: Drschnabel_TX_trend_oscillation20k_LT.
# Uses MA(56) vs MA(91) where 91/56 ≈ 1.618 (golden ratio / phi).
# When fast MA > slow MA: bullish trend; entry confirmed by KD oscillator.
# We simplify: use the MA crossover direction alone.
# The key insight: golden-ratio periods naturally align with Fibonacci
# retracement cycles, giving harmonically significant support/resistance.

class GoldenRatioMAStrategy:
    """
    MA crossover strategy using golden-ratio (phi=1.618) period relationship.

    Parameters
    ----------
    fast_period : int
        Fast MA lookback. Slow period = round(fast * 1.618) (default 56).
    slow_period : int
        Slow MA lookback. If provided, overrides the phi calculation.
        Allows exact specification of observed PLA pairs like (56, 91).
    """

    def __init__(
        self,
        fast_period: int = 56,
        slow_period: int = 91,
    ):
        if fast_period < 2:
            raise ValueError(f"fast_period must be >= 2, got {fast_period}")
        if slow_period <= fast_period:
            raise ValueError(
                f"slow_period ({slow_period}) must be > fast_period ({fast_period})"
            )
        self.fast_period = fast_period
        self.slow_period = slow_period

    def __call__(self, bars: List[Bar]) -> Signal:
        if len(bars) < self.slow_period + 1:
            return 0

        closes = [b["close"] for b in bars]
        fast_now = _sma(closes, self.fast_period)
        slow_now = _sma(closes, self.slow_period)
        fast_prev = _sma(closes[:-1], self.fast_period)
        slow_prev = _sma(closes[:-1], self.slow_period)

        avg_dif = fast_now - slow_now
        avg_dif_prev = fast_prev - slow_prev

        # Trend: fast MA crossed above/below slow MA
        if avg_dif > 0 and avg_dif_prev <= 0:
            return 1   # golden cross
        if avg_dif < 0 and avg_dif_prev >= 0:
            return -1  # death cross
        # Maintain position when trend is established
        if avg_dif > 0:
            return 1
        if avg_dif < 0:
            return -1
        return 0

    def __repr__(self) -> str:
        ratio = self.slow_period / self.fast_period if self.fast_period else 0
        return (
            f"GoldenRatioMAStrategy(fast={self.fast_period}, "
            f"slow={self.slow_period}, ratio={ratio:.3f})"
        )


# ---------------------------------------------------------------------------
# KPowerStrategy — Buying/Selling pressure score vs StdDev benchmark
# ---------------------------------------------------------------------------
# PLA source: Wesley003_TX_2110KPower_LO.
# LPower = sum(close - low, pressure_period)   → buying pressure
# SPower = sum(high - close, pressure_period)  → selling pressure
# KPower = abs(LPower - SPower)
# Entry when KPower > StdDev(close, std_period) AND directional bias confirmed
# by consecutive N-day higher lows (long) or lower highs (short).

class KPowerStrategy:
    """
    Directional pressure score (KPower) vs volatility benchmark.

    KPower = |sum(C-L, n) - sum(H-C, n)|
    Entry when KPower exceeds StdDev(close) AND N consecutive bars confirm
    the trend direction.

    Parameters
    ----------
    pressure_period : int
        Lookback for LPower/SPower summation (default 4).
    std_period : int
        Lookback for StdDev benchmark (default 20).
    consecutive_days : int
        Minimum consecutive confirming bars required (default 3).
    """

    def __init__(
        self,
        pressure_period: int = 4,
        std_period: int = 20,
        consecutive_days: int = 3,
    ):
        if pressure_period < 1:
            raise ValueError(f"pressure_period must be >= 1, got {pressure_period}")
        if std_period < 2:
            raise ValueError(f"std_period must be >= 2, got {std_period}")
        if consecutive_days < 1:
            raise ValueError(f"consecutive_days must be >= 1, got {consecutive_days}")
        self.pressure_period = pressure_period
        self.std_period = std_period
        self.consecutive_days = consecutive_days

    def _kpower(self, bars: List[Bar]) -> tuple[float, float, float]:
        """Return (l_power, s_power, k_power) from recent bars."""
        window = bars[-self.pressure_period:]
        l_power = sum(b["close"] - b["low"] for b in window)
        s_power = sum(b["high"] - b["close"] for b in window)
        k_power = abs(l_power - s_power)
        return l_power, s_power, k_power

    def _stddev(self, bars: List[Bar]) -> float:
        """Population standard deviation of closes over std_period."""
        window = bars[-self.std_period:]
        closes = [b["close"] for b in window]
        if len(closes) < 2:
            return 0.0
        mean = sum(closes) / len(closes)
        variance = sum((c - mean) ** 2 for c in closes) / len(closes)
        return math.sqrt(variance)

    def _consecutive_confirm(self, bars: List[Bar], direction: int) -> bool:
        """Check N consecutive bars confirm direction (higher lows or lower highs)."""
        n = self.consecutive_days + 1
        if len(bars) < n:
            return False
        window = bars[-n:]
        if direction == 1:
            # Higher lows: each bar's low >= previous bar's low
            return all(
                window[i]["low"] >= window[i - 1]["low"]
                for i in range(1, len(window))
            )
        else:
            # Lower highs
            return all(
                window[i]["high"] <= window[i - 1]["high"]
                for i in range(1, len(window))
            )

    def __call__(self, bars: List[Bar]) -> Signal:
        required = max(self.pressure_period, self.std_period) + self.consecutive_days
        if len(bars) < required:
            return 0

        l_power, s_power, k_power = self._kpower(bars)
        std = self._stddev(bars)

        # KPower must exceed volatility benchmark to confirm conviction
        if std == 0 or k_power <= std:
            return 0

        # Directional bias: which pressure dominates?
        if l_power > s_power:
            # Buying pressure dominant
            if self._consecutive_confirm(bars, 1):
                return 1
        elif s_power > l_power:
            # Selling pressure dominant
            if self._consecutive_confirm(bars, -1):
                return -1
        return 0

    def __repr__(self) -> str:
        return (
            f"KPowerStrategy(pressure_period={self.pressure_period}, "
            f"std_period={self.std_period}, consecutive_days={self.consecutive_days})"
        )


# ---------------------------------------------------------------------------
# BarTimingStrategy — Session H/L bar-timing analysis
# ---------------------------------------------------------------------------
# PLA source: AVgirl_202106_5K (b25b25AVgirl).
# Tracks at which bar within the session the daily High and Low were made.
# Key insight: if the lowest bar is forming LATER than the expected low bar,
# the market is still making new lows → continuation signal.
# We approximate for daily bar data: use the position of the max/min close
# within a rolling lookback window as a proxy for "when the extreme was made".

class BarTimingStrategy:
    """
    Bar-timing analysis: enters when price extremes form later than expected.

    Logic: within a `lookback` window, find the bar-index of the highest
    and lowest closes (equivalent to Hbar/Lbar in the PLA source).
    If the lowest-close bar is in the RECENT half of the window: downtrend
    is still developing → SHORT (for fade variant, LONG).
    If the highest-close bar is in the recent half → uptrend continuing → LONG.

    Parameters
    ----------
    session_bars : int
        Total session length (for PLA: 78 bars on 5-min = ~6.5hr day).
        Used to normalize the "expected" bar position.
    lookback : int
        Rolling window to detect bar-timing position (default 10).
    """

    def __init__(
        self,
        session_bars: int = 48,
        lookback: int = 10,
    ):
        if session_bars < 4:
            raise ValueError(f"session_bars must be >= 4, got {session_bars}")
        if lookback < 2:
            raise ValueError(f"lookback must be >= 2, got {lookback}")
        self.session_bars = session_bars
        self.lookback = lookback

    def _bar_position_scores(
        self, bars: List[Bar]
    ) -> tuple[float, float]:
        """
        Returns (high_recency, low_recency): fraction 0..1 indicating how
        recently (1=most recent) the high/low bar occurred in the window.
        """
        window = bars[-self.lookback:]
        n = len(window)
        if n < 2:
            return 0.5, 0.5

        closes = [b["close"] for b in window]
        high_idx = closes.index(max(closes))
        low_idx = closes.index(min(closes))

        # Recency: index 0 = oldest, n-1 = most recent
        high_recency = high_idx / (n - 1)
        low_recency = low_idx / (n - 1)
        return high_recency, low_recency

    def __call__(self, bars: List[Bar]) -> Signal:
        if len(bars) < self.lookback + 1:
            return 0

        high_recency, low_recency = self._bar_position_scores(bars)

        # If the high occurred in the recent 60% of the window: uptrend
        if high_recency >= 0.60 and high_recency > low_recency:
            return 1
        # If the low occurred in the recent 60%: downtrend
        if low_recency >= 0.60 and low_recency > high_recency:
            return -1
        return 0

    def __repr__(self) -> str:
        return (
            f"BarTimingStrategy(session_bars={self.session_bars}, "
            f"lookback={self.lookback})"
        )


# ---------------------------------------------------------------------------
# Batch 4-6 instances (PLA-derived parameters)
# ---------------------------------------------------------------------------

# ShakeFilter: Bonny uses Len=15, shake threshold Len/4=0.25
shake_txf_15 = ShakeFilterStrategy(period=15, shake_threshold=0.25, atr_period=14)
shake_txf_20 = ShakeFilterStrategy(period=20, shake_threshold=0.33, atr_period=14)

# SqrtTimeTrail: VCP uses 7K bars; trail = mpp - ATR/sqrt(bars)
sqrt_trail_breakout = SqrtTimeTrailStrategy(
    breakout_period=14, atr_period=14, trail_atr_mult=1.5,
)
sqrt_trail_tight = SqrtTimeTrailStrategy(
    breakout_period=10, atr_period=10, trail_atr_mult=1.0,
)

# AdaptiveMultiplier: TXF uses N=20 base, 2x post-loss
adaptive_ma_20 = AdaptiveMultiplierMAStrategy(base_period=20, loss_multiplier=2.0)
adaptive_ma_14 = AdaptiveMultiplierMAStrategy(base_period=14, loss_multiplier=2.0)

# GoldenRatioMA: Drschnabel uses 56/91 (ratio 1.625 ≈ phi)
golden_ratio_56_91 = GoldenRatioMAStrategy(fast_period=56, slow_period=91)
golden_ratio_34_55 = GoldenRatioMAStrategy(fast_period=34, slow_period=55)

# KPower: Wesley003 uses pressure_period=4, std_period=20, 3-day consecutive
kpower_txf_std = KPowerStrategy(pressure_period=4, std_period=20, consecutive_days=3)
kpower_txf_fast = KPowerStrategy(pressure_period=3, std_period=14, consecutive_days=2)

# BarTiming: AVgirl uses 5-min session (~78 bars); lookback captures 10-20 bars
bar_timing_10 = BarTimingStrategy(session_bars=78, lookback=10)
bar_timing_20 = BarTimingStrategy(session_bars=48, lookback=20)


# All extended strategies for import
EXTENDED_STRATEGIES: dict[str, object] = {
    # BTC variants
    "CCI_20_100": cci_btc_daily,
    "DMI_14_25": dmi_btc_daily,
    "MACD_12_26_9": macd_btc_daily,
    "ORB_3": orb_btc_daily,
    "Keltner_momentum_20": keltner_momentum_btc_daily,
    "Keltner_reversion_20": keltner_reversion_btc_daily,
    # TXF variants (PLA-derived parameters)
    "CCI_TXF_28": cci_txf_28,
    "CCI_TXF_daily": cci_txf_daily,
    "DMI_TXF_14": dmi_txf_14,
    "DMI_TXF_strict": dmi_txf_strict,
    "MACD_TXF_standard": macd_txf_standard,
    "MACD_TXF_fast": macd_txf_fast,
    "ORB_TXF_1": orb_txf_1,
    "ORB_TXF_3": orb_txf_3,
    "Keltner_TXF_momentum": keltner_txf_momentum,
    "Keltner_TXF_reversion": keltner_txf_reversion,
    # Stochastic KD variants (PLA: CDPKD, SlowKD 80/20, KD H/L breakout)
    "Stochastic_reversion_14": stochastic_txf_reversion,
    "Stochastic_momentum_14": stochastic_txf_momentum,
    # CDP variants (PLA: 13 strategies; breakout + reversion modes)
    "CDP_breakout": cdp_breakout,
    "CDP_reversion": cdp_reversion,
    # Parabolic SAR (PLA: TXAL_030_SAR01, Kuang SAR, BN_SAR_FDO)
    "ParabolicSAR_std": sar_std,
    "ParabolicSAR_fast": sar_fast,
    # Gap Fade (PLA: 93 gap entries; gap-fade dominant pattern)
    "GapFade_1pct": gap_fade_1pct,
    "GapFade_2pct": gap_fade_2pct,
    "GapFollow_1pct": gap_follow_1pct,
    # Batch 4-6: Novel techniques from extended PLA digestion (636+ strategies)
    # ShakeFilter (NV2108004 Bonny): oscillation-count chop gate
    "ShakeFilter_15_025": shake_txf_15,
    "ShakeFilter_20_033": shake_txf_20,
    # SqrtTimeTrail (TXAL_1_007 VCP): sqrt-of-time tightening trail
    "SqrtTimeTrail_14_15": sqrt_trail_breakout,
    "SqrtTimeTrail_10_10": sqrt_trail_tight,
    # AdaptiveMultiplier (NV2112008 / TXF_MAHL): doubles period after loss
    "AdaptiveMA_20x2": adaptive_ma_20,
    "AdaptiveMA_14x2": adaptive_ma_14,
    # GoldenRatioMA (Drschnabel): phi=1.618 MA period pairs
    "GoldenRatio_56_91": golden_ratio_56_91,
    "GoldenRatio_34_55": golden_ratio_34_55,
    # KPower (Wesley003): buying/selling pressure score vs StdDev
    "KPower_std_4_20_3": kpower_txf_std,
    "KPower_fast_3_14_2": kpower_txf_fast,
    # BarTiming (AVgirl): intraday H/L bar-position timing
    "BarTiming_78_10": bar_timing_10,
    "BarTiming_48_20": bar_timing_20,
}
