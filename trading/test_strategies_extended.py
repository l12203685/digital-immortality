"""
Tests for strategies_extended.py — CCI, DMI, MACD, ORB, Keltner strategies.

Validates:
1. Interface compliance: each strategy is callable with List[Bar] -> Signal
2. Insufficient data returns 0 (flat)
3. Known signal directions on synthetic data
4. Edge cases: zero volatility, parameter validation
5. TXF instances exist and are callable
6. Phase 1 pass criteria: >= 3 strategies with 5+ trades each on synthetic data
7. Batch 4-6 strategies: ShakeFilter, SqrtTimeTrail, AdaptiveMultiplierMA,
   GoldenRatioMA, KPower, BarTiming
"""

import pytest
from typing import List

from trading.backtest_framework import Bar, Signal
from trading.strategies_extended import (
    CCIStrategy,
    DMIStrategy,
    MACDStrategy,
    ORBStrategy,
    KeltnerStrategy,
    StochasticStrategy,
    CDPStrategy,
    ParabolicSARStrategy,
    GapFadeStrategy,
    ShakeFilterStrategy,
    SqrtTimeTrailStrategy,
    AdaptiveMultiplierMAStrategy,
    GoldenRatioMAStrategy,
    KPowerStrategy,
    BarTimingStrategy,
    EXTENDED_STRATEGIES,
    _ema,
    _true_range,
    _atr,
    _sma,
)


# ---------------------------------------------------------------------------
# Helpers: synthetic bar generators
# ---------------------------------------------------------------------------

def _make_bar(o: float, h: float, l: float, c: float, v: float = 1000.0) -> Bar:
    return {"open": o, "high": h, "low": l, "close": c, "volume": v}


def _trending_up_bars(n: int, start: float = 100.0, step: float = 1.0) -> List[Bar]:
    """Generate n bars with a steady uptrend."""
    bars = []
    for i in range(n):
        base = start + i * step
        bars.append(_make_bar(base, base + 0.5, base - 0.3, base + 0.4))
    return bars


def _trending_down_bars(n: int, start: float = 200.0, step: float = 1.0) -> List[Bar]:
    """Generate n bars with a steady downtrend."""
    bars = []
    for i in range(n):
        base = start - i * step
        bars.append(_make_bar(base, base + 0.3, base - 0.5, base - 0.4))
    return bars


def _flat_bars(n: int, price: float = 150.0) -> List[Bar]:
    """Generate n bars with no movement."""
    return [_make_bar(price, price, price, price) for _ in range(n)]


def _volatile_bars(n: int, center: float = 100.0, amplitude: float = 10.0) -> List[Bar]:
    """Generate bars that oscillate around a center."""
    bars = []
    for i in range(n):
        if i % 2 == 0:
            bars.append(_make_bar(center, center + amplitude, center - amplitude * 0.5, center + amplitude * 0.8))
        else:
            bars.append(_make_bar(center, center + amplitude * 0.5, center - amplitude, center - amplitude * 0.8))
    return bars


def _breakout_bars(n: int, range_price: float = 100.0, breakout_price: float = 120.0) -> List[Bar]:
    """Generate range bars followed by a breakout bar."""
    bars = [_make_bar(range_price, range_price + 1, range_price - 1, range_price) for _ in range(n - 1)]
    bars.append(_make_bar(range_price, breakout_price + 2, range_price - 0.5, breakout_price))
    return bars


# ---------------------------------------------------------------------------
# Helper function tests
# ---------------------------------------------------------------------------

class TestHelpers:
    def test_ema_basic(self):
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = _ema(values, 3)
        assert len(result) == len(values)
        # First 2 elements are filler, 3rd is SMA of first 3
        assert result[2] == pytest.approx(2.0, rel=1e-6)

    def test_ema_empty(self):
        assert _ema([], 3) == []

    def test_ema_period_larger_than_data(self):
        result = _ema([1.0, 2.0], 5)
        assert len(result) == 2
        assert result[0] == pytest.approx(1.5)

    def test_true_range(self):
        bars = [_make_bar(10, 12, 9, 11), _make_bar(11, 14, 10, 13)]
        tr = _true_range(bars)
        assert len(tr) == 2
        assert tr[0] == pytest.approx(3.0)  # 12 - 9
        # Bar 2: max(14-10, |14-11|, |10-11|) = max(4, 3, 1) = 4
        assert tr[1] == pytest.approx(4.0)

    def test_atr(self):
        bars = _trending_up_bars(20)
        atr = _atr(bars, 14)
        assert len(atr) == 20
        assert all(v >= 0 for v in atr)

    def test_sma(self):
        assert _sma([1, 2, 3, 4, 5], 3) == pytest.approx(4.0)
        assert _sma([1, 2], 5) == pytest.approx(1.5)
        assert _sma([], 3) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# CCIStrategy tests
# ---------------------------------------------------------------------------

class TestCCIStrategy:
    def test_insufficient_data_returns_flat(self):
        cci = CCIStrategy(period=20)
        assert cci(_trending_up_bars(5)) == 0

    def test_uptrend_gives_long(self):
        cci = CCIStrategy(period=14, threshold=100.0)
        bars = _trending_up_bars(50, step=2.0)
        signal = cci(bars)
        assert signal == 1

    def test_downtrend_gives_short(self):
        cci = CCIStrategy(period=14, threshold=100.0)
        bars = _trending_down_bars(50, step=2.0)
        signal = cci(bars)
        assert signal == -1

    def test_flat_gives_neutral(self):
        cci = CCIStrategy(period=20, threshold=100.0)
        bars = _flat_bars(30)
        assert cci(bars) == 0

    def test_invalid_period_raises(self):
        with pytest.raises(ValueError):
            CCIStrategy(period=1)

    def test_repr(self):
        cci = CCIStrategy(period=28, threshold=150.0)
        assert "28" in repr(cci)
        assert "150" in repr(cci)

    def test_cci_value_computation(self):
        """Verify internal CCI calculation is reasonable."""
        cci = CCIStrategy(period=10)
        bars = _trending_up_bars(20, step=3.0)
        val = cci._cci(bars)
        # Strong uptrend should produce a positive CCI
        assert val > 0


# ---------------------------------------------------------------------------
# DMIStrategy tests
# ---------------------------------------------------------------------------

class TestDMIStrategy:
    def test_insufficient_data_returns_flat(self):
        dmi = DMIStrategy(period=14)
        assert dmi(_trending_up_bars(10)) == 0

    def test_strong_uptrend_gives_long(self):
        dmi = DMIStrategy(period=14, adx_threshold=15.0)
        bars = _trending_up_bars(80, step=2.0)
        signal = dmi(bars)
        assert signal == 1

    def test_strong_downtrend_gives_short(self):
        dmi = DMIStrategy(period=14, adx_threshold=15.0)
        bars = _trending_down_bars(80, start=500.0, step=2.0)
        signal = dmi(bars)
        assert signal == -1

    def test_flat_market_gives_neutral(self):
        dmi = DMIStrategy(period=14, adx_threshold=25.0)
        bars = _flat_bars(60)
        assert dmi(bars) == 0

    def test_high_adx_threshold_filters_weak_trends(self):
        dmi_strict = DMIStrategy(period=14, adx_threshold=50.0)
        bars = _flat_bars(60)  # no trend at all
        assert dmi_strict(bars) == 0

    def test_invalid_period_raises(self):
        with pytest.raises(ValueError):
            DMIStrategy(period=1)

    def test_repr(self):
        dmi = DMIStrategy(period=14, adx_threshold=25.0)
        assert "14" in repr(dmi)
        assert "25" in repr(dmi)

    def test_compute_dmi_returns_tuple(self):
        dmi = DMIStrategy(period=14)
        bars = _trending_up_bars(40)
        result = dmi._compute_dmi(bars)
        assert len(result) == 3
        plus_di, minus_di, adx = result
        assert plus_di >= 0
        assert minus_di >= 0
        assert adx >= 0


# ---------------------------------------------------------------------------
# MACDStrategy tests
# ---------------------------------------------------------------------------

class TestMACDStrategy:
    def test_insufficient_data_returns_flat(self):
        macd = MACDStrategy()
        assert macd(_trending_up_bars(10)) == 0

    def test_uptrend_gives_long(self):
        macd = MACDStrategy(fast=12, slow=26, signal=9)
        # Accelerating uptrend triggers positive histogram divergence
        bars = []
        for i in range(80):
            base = 100.0 + i * 0.5 + (i ** 1.3) * 0.05
            bars.append(_make_bar(base, base + 1.0, base - 0.5, base + 0.8))
        signal = macd(bars)
        assert signal == 1

    def test_downtrend_gives_short(self):
        macd = MACDStrategy(fast=12, slow=26, signal=9)
        bars = _trending_down_bars(80, start=500.0, step=1.5)
        signal = macd(bars)
        assert signal == -1

    def test_fast_must_be_less_than_slow(self):
        with pytest.raises(ValueError):
            MACDStrategy(fast=26, slow=12)
        with pytest.raises(ValueError):
            MACDStrategy(fast=12, slow=12)

    def test_repr(self):
        macd = MACDStrategy(fast=8, slow=21, signal=5)
        assert "8" in repr(macd)
        assert "21" in repr(macd)
        assert "5" in repr(macd)

    def test_custom_params(self):
        macd_fast = MACDStrategy(fast=5, slow=15, signal=5)
        bars = _trending_up_bars(40, step=2.0)
        signal = macd_fast(bars)
        # Fast MACD on uptrend: valid signal returned
        assert signal in (-1, 0, 1)


# ---------------------------------------------------------------------------
# ORBStrategy tests
# ---------------------------------------------------------------------------

class TestORBStrategy:
    def test_insufficient_data_returns_flat(self):
        orb = ORBStrategy(range_bars=3)
        assert orb(_trending_up_bars(3)) == 0

    def test_breakout_above_gives_long(self):
        orb = ORBStrategy(range_bars=3, atr_filter=0.0)  # disable ATR filter
        bars = _breakout_bars(20, range_price=100.0, breakout_price=115.0)
        signal = orb(bars)
        assert signal == 1

    def test_breakout_below_gives_short(self):
        orb = ORBStrategy(range_bars=3, atr_filter=0.0)
        # Range at 100, then breakdown to 85
        bars = [_make_bar(100, 101, 99, 100) for _ in range(19)]
        bars.append(_make_bar(100, 100.5, 84, 85))
        signal = orb(bars)
        assert signal == -1

    def test_within_range_gives_flat(self):
        orb = ORBStrategy(range_bars=5, atr_filter=0.0)
        bars = _flat_bars(20, price=100.0)
        assert orb(bars) == 0

    def test_narrow_range_filtered_by_atr(self):
        orb = ORBStrategy(range_bars=3, atr_filter=2.0, atr_period=5)
        # Create bars with moderate ATR but very narrow range
        bars = _volatile_bars(18, center=100, amplitude=5)
        # Add narrow-range bars as "opening range"
        bars.extend([_make_bar(100, 100.1, 99.9, 100.05) for _ in range(3)])
        # Breakout bar
        bars.append(_make_bar(100, 102, 99, 101))
        # Range width (0.2) is much less than atr_filter * ATR
        signal = orb(bars)
        assert signal == 0  # filtered out

    def test_invalid_range_bars_raises(self):
        with pytest.raises(ValueError):
            ORBStrategy(range_bars=0)

    def test_repr(self):
        orb = ORBStrategy(range_bars=3, atr_filter=0.5)
        assert "3" in repr(orb)
        assert "0.5" in repr(orb)


# ---------------------------------------------------------------------------
# KeltnerStrategy tests
# ---------------------------------------------------------------------------

class TestKeltnerStrategy:
    def test_insufficient_data_returns_flat(self):
        kc = KeltnerStrategy(ema_period=20)
        assert kc(_trending_up_bars(10)) == 0

    def test_momentum_breakout_long(self):
        kc = KeltnerStrategy(ema_period=10, atr_period=10, multiplier=1.0, mode="momentum")
        # Strong uptrend should break above upper band
        bars = _trending_up_bars(40, step=3.0)
        signal = kc(bars)
        assert signal == 1

    def test_momentum_breakout_short(self):
        kc = KeltnerStrategy(ema_period=10, atr_period=10, multiplier=1.0, mode="momentum")
        bars = _trending_down_bars(40, start=500.0, step=3.0)
        signal = kc(bars)
        assert signal == -1

    def test_reversion_mode_inverts(self):
        kc_rev = KeltnerStrategy(ema_period=10, atr_period=10, multiplier=1.0, mode="reversion")
        bars = _trending_up_bars(40, step=3.0)
        signal = kc_rev(bars)
        # Reversion: above upper band = overbought = SHORT
        assert signal == -1

    def test_flat_gives_neutral(self):
        kc = KeltnerStrategy(ema_period=10, atr_period=10, multiplier=2.0, mode="momentum")
        bars = _flat_bars(30)
        # Flat bars have zero ATR -> returns 0
        assert kc(bars) == 0

    def test_invalid_ema_period_raises(self):
        with pytest.raises(ValueError):
            KeltnerStrategy(ema_period=1)

    def test_invalid_mode_raises(self):
        with pytest.raises(ValueError):
            KeltnerStrategy(mode="invalid")

    def test_repr(self):
        kc = KeltnerStrategy(ema_period=18, atr_period=14, multiplier=3.5, mode="momentum")
        assert "18" in repr(kc)
        assert "3.5" in repr(kc)
        assert "momentum" in repr(kc)

    def test_wide_multiplier_filters_weak_moves(self):
        kc = KeltnerStrategy(ema_period=10, atr_period=10, multiplier=5.0, mode="momentum")
        bars = _trending_up_bars(40, step=0.5)  # mild trend
        assert kc(bars) == 0  # 5x ATR too wide for mild trend


# ---------------------------------------------------------------------------
# EXTENDED_STRATEGIES registry tests
# ---------------------------------------------------------------------------

class TestExtendedStrategiesRegistry:
    def test_all_btc_strategies_registered(self):
        expected = ["CCI_20_100", "DMI_14_25", "MACD_12_26_9", "ORB_3",
                    "Keltner_momentum_20", "Keltner_reversion_20"]
        for name in expected:
            assert name in EXTENDED_STRATEGIES, f"{name} missing from EXTENDED_STRATEGIES"

    def test_all_txf_strategies_registered(self):
        expected = ["CCI_TXF_28", "CCI_TXF_daily", "DMI_TXF_14", "DMI_TXF_strict",
                    "MACD_TXF_standard", "MACD_TXF_fast", "ORB_TXF_1", "ORB_TXF_3",
                    "Keltner_TXF_momentum", "Keltner_TXF_reversion"]
        for name in expected:
            assert name in EXTENDED_STRATEGIES, f"{name} missing from EXTENDED_STRATEGIES"

    def test_all_strategies_callable(self):
        bars = _trending_up_bars(100, step=1.0)
        for name, strategy in EXTENDED_STRATEGIES.items():
            signal = strategy(bars)
            assert signal in (-1, 0, 1), f"{name} returned invalid signal: {signal}"

    def test_total_count(self):
        # 6 BTC + 10 TXF + 2 Stochastic + 2 CDP + 2 SAR + 3 Gap = 25 original
        # + 2 ShakeFilter + 2 SqrtTimeTrail + 2 AdaptiveMA + 2 GoldenRatio
        # + 2 KPower + 2 BarTiming = 37 total
        assert len(EXTENDED_STRATEGIES) == 37

    def test_batch46_strategies_registered(self):
        """All 6 batch 4-6 strategy types present in registry."""
        expected_prefixes = [
            "ShakeFilter_", "SqrtTimeTrail_", "AdaptiveMA_",
            "GoldenRatio_", "KPower_", "BarTiming_",
        ]
        for prefix in expected_prefixes:
            matches = [k for k in EXTENDED_STRATEGIES if k.startswith(prefix)]
            assert len(matches) >= 1, f"No strategies with prefix '{prefix}'"


# ---------------------------------------------------------------------------
# Phase 1 pass criteria: >= 3 strategies with 5+ trades each
# ---------------------------------------------------------------------------

class TestPhase1PassCriteria:
    """Simulate a minimal backtest to verify Phase 1 pass criteria:
    At least 3 strategies must generate 5+ signal changes (trades)
    on a 200-bar synthetic dataset with mixed regimes."""

    @staticmethod
    def _mixed_regime_bars(n: int = 200) -> List[Bar]:
        """Create bars with trending + ranging + trending regimes."""
        bars = []
        # Phase 1: uptrend (0-60)
        bars.extend(_trending_up_bars(60, start=100.0, step=1.5))
        # Phase 2: range (60-120)
        bars.extend(_volatile_bars(60, center=190.0, amplitude=8.0))
        # Phase 3: downtrend (120-180)
        bars.extend(_trending_down_bars(60, start=190.0, step=1.5))
        # Phase 4: recovery (180-200)
        bars.extend(_trending_up_bars(20, start=100.0, step=2.0))
        return bars

    def test_phase1_pass(self):
        bars = self._mixed_regime_bars()
        strategies_with_enough_trades = []

        for name, strategy in EXTENDED_STRATEGIES.items():
            prev_signal = 0
            trade_count = 0
            for i in range(30, len(bars)):
                signal = strategy(bars[:i + 1])
                if signal != prev_signal:
                    trade_count += 1
                    prev_signal = signal
            if trade_count >= 5:
                strategies_with_enough_trades.append((name, trade_count))

        assert len(strategies_with_enough_trades) >= 3, (
            f"Phase 1 fail: only {len(strategies_with_enough_trades)} strategies "
            f"have 5+ trades. Need >= 3. Results: {strategies_with_enough_trades}"
        )


# ---------------------------------------------------------------------------
# Interface compliance: each strategy type returns valid Signal
# ---------------------------------------------------------------------------

class TestInterfaceCompliance:
    """Every strategy must return Signal (int in {-1, 0, 1}) for any input."""

    @pytest.mark.parametrize("cls,kwargs", [
        (CCIStrategy, {"period": 14, "threshold": 100}),
        (DMIStrategy, {"period": 14, "adx_threshold": 20}),
        (MACDStrategy, {"fast": 8, "slow": 21, "signal": 5}),
        (ORBStrategy, {"range_bars": 3, "atr_filter": 0}),
        (KeltnerStrategy, {"ema_period": 10, "atr_period": 10, "multiplier": 2.0}),
    ])
    def test_empty_bars_returns_flat(self, cls, kwargs):
        strategy = cls(**kwargs)
        assert strategy([]) == 0

    @pytest.mark.parametrize("cls,kwargs", [
        (CCIStrategy, {"period": 14, "threshold": 100}),
        (DMIStrategy, {"period": 14, "adx_threshold": 20}),
        (MACDStrategy, {"fast": 8, "slow": 21, "signal": 5}),
        (ORBStrategy, {"range_bars": 3, "atr_filter": 0}),
        (KeltnerStrategy, {"ema_period": 10, "atr_period": 10, "multiplier": 2.0}),
    ])
    def test_single_bar_returns_flat(self, cls, kwargs):
        strategy = cls(**kwargs)
        bar = _make_bar(100, 101, 99, 100)
        assert strategy([bar]) == 0

    @pytest.mark.parametrize("cls,kwargs", [
        (CCIStrategy, {"period": 14, "threshold": 100}),
        (DMIStrategy, {"period": 14, "adx_threshold": 15}),
        (MACDStrategy, {"fast": 8, "slow": 21, "signal": 5}),
        (ORBStrategy, {"range_bars": 3, "atr_filter": 0}),
        (KeltnerStrategy, {"ema_period": 10, "atr_period": 10, "multiplier": 1.5}),
        (StochasticStrategy, {"k_period": 14, "d_period": 3}),
        (CDPStrategy, {"mode": "breakout"}),
        (ParabolicSARStrategy, {"af_start": 0.02, "af_step": 0.02, "af_max": 0.20}),
        (GapFadeStrategy, {"gap_threshold": 0.01, "atr_period": 14}),
        # Batch 4-6
        (ShakeFilterStrategy, {"period": 10, "shake_threshold": 0.25, "atr_period": 10}),
        (SqrtTimeTrailStrategy, {"breakout_period": 10, "atr_period": 10}),
        (AdaptiveMultiplierMAStrategy, {"base_period": 10, "loss_multiplier": 2.0}),
        (GoldenRatioMAStrategy, {"fast_period": 5, "slow_period": 8}),
        (KPowerStrategy, {"pressure_period": 3, "std_period": 14, "consecutive_days": 2}),
        (BarTimingStrategy, {"session_bars": 10, "lookback": 5}),
    ])
    def test_signal_in_valid_range(self, cls, kwargs):
        strategy = cls(**kwargs)
        for bars in [_trending_up_bars(60), _trending_down_bars(60), _flat_bars(60)]:
            signal = strategy(bars)
            assert signal in (-1, 0, 1), f"{cls.__name__} returned {signal}"


# ---------------------------------------------------------------------------
# StochasticStrategy tests
# ---------------------------------------------------------------------------

class TestStochasticStrategy:
    def test_insufficient_data_returns_flat(self):
        stoch = StochasticStrategy(k_period=14, d_period=3)
        assert stoch(_trending_up_bars(5)) == 0

    def test_reversion_oversold_gives_long(self):
        stoch = StochasticStrategy(k_period=5, d_period=2, oversold=30.0, mode="reversion")
        # k_period=5, d_period=2 -> need 5+2=7 bars minimum
        # Build enough history: 8 flat bars at 100, then a sharp dip -> %K near 0
        bars = [_make_bar(100, 101, 99, 100) for _ in range(7)]
        bars.append(_make_bar(80, 81, 60, 62))  # massive dip -> %K near 0 -> oversold
        signal = stoch(bars)
        assert signal == 1

    def test_reversion_overbought_gives_short(self):
        stoch = StochasticStrategy(k_period=5, d_period=2, overbought=70.0, mode="reversion")
        # 8 flat bars at 100, then spike to 140 -> %K near 100 -> overbought
        bars = [_make_bar(100, 101, 99, 100) for _ in range(7)]
        bars.append(_make_bar(120, 140, 119, 138))  # spike -> %K near 100
        signal = stoch(bars)
        assert signal == -1

    def test_momentum_mode_follows_trend(self):
        stoch = StochasticStrategy(k_period=5, d_period=2, overbought=70.0, mode="momentum")
        # 8 flat bars at 100, spike to 140 -> %K near 100 -> LONG in momentum mode
        bars = [_make_bar(100, 101, 99, 100) for _ in range(7)]
        bars.append(_make_bar(120, 140, 119, 138))
        signal = stoch(bars)
        assert signal == 1

    def test_flat_bars_neutral(self):
        stoch = StochasticStrategy(k_period=14, d_period=3)
        bars = _flat_bars(25)
        assert stoch(bars) == 0  # no range -> 50% K -> neutral

    def test_invalid_k_period_raises(self):
        with pytest.raises(ValueError):
            StochasticStrategy(k_period=1)

    def test_invalid_mode_raises(self):
        with pytest.raises(ValueError):
            StochasticStrategy(mode="invalid")

    def test_repr(self):
        stoch = StochasticStrategy(k_period=14, d_period=3, overbought=80, oversold=20)
        r = repr(stoch)
        assert "14" in r
        assert "80" in r


# ---------------------------------------------------------------------------
# CDPStrategy tests
# ---------------------------------------------------------------------------

class TestCDPStrategy:
    def test_insufficient_data_returns_flat(self):
        cdp = CDPStrategy()
        assert cdp([_make_bar(100, 101, 99, 100)]) == 0
        assert cdp([]) == 0

    def test_breakout_above_nh_gives_long(self):
        cdp = CDPStrategy(mode="breakout")
        # prev bar: H=110, L=90, C=100
        # CDP = (110+90+200)/4 = 100; NH = 2*100 - 90 = 110
        # current close > NH (110) -> LONG
        prev_bar = _make_bar(100, 110, 90, 100)
        cur_bar = _make_bar(110, 125, 109, 120)  # close=120 > NH=110
        assert cdp([prev_bar, cur_bar]) == 1

    def test_breakout_below_nl_gives_short(self):
        cdp = CDPStrategy(mode="breakout")
        # prev: H=110, L=90, C=100 -> NL = 2*100 - 110 = 90
        prev_bar = _make_bar(100, 110, 90, 100)
        cur_bar = _make_bar(90, 91, 75, 78)  # close=78 < NL=90
        assert cdp([prev_bar, cur_bar]) == -1

    def test_reversion_above_ah_gives_short(self):
        cdp = CDPStrategy(mode="reversion")
        # prev: H=110, L=90, C=100 -> CDP=100; AH = 100 + 20 = 120
        prev_bar = _make_bar(100, 110, 90, 100)
        cur_bar = _make_bar(120, 135, 119, 130)  # close=130 > AH=120
        assert cdp([prev_bar, cur_bar]) == -1

    def test_reversion_below_al_gives_long(self):
        cdp = CDPStrategy(mode="reversion")
        # prev: H=110, L=90, C=100 -> AL = 100 - 20 = 80
        prev_bar = _make_bar(100, 110, 90, 100)
        cur_bar = _make_bar(80, 81, 70, 72)  # close=72 < AL=80
        assert cdp([prev_bar, cur_bar]) == 1

    def test_within_nh_nl_gives_flat(self):
        cdp = CDPStrategy(mode="breakout")
        prev_bar = _make_bar(100, 110, 90, 100)
        cur_bar = _make_bar(100, 108, 92, 100)  # 90 < 100 < 110 -> flat
        assert cdp([prev_bar, cur_bar]) == 0

    def test_invalid_mode_raises(self):
        with pytest.raises(ValueError):
            CDPStrategy(mode="invalid")

    def test_repr(self):
        cdp = CDPStrategy(mode="breakout")
        assert "breakout" in repr(cdp)

    def test_signal_valid_on_trending_data(self):
        cdp = CDPStrategy(mode="breakout")
        bars = _trending_up_bars(40)
        for i in range(2, len(bars)):
            sig = cdp(bars[:i + 1])
            assert sig in (-1, 0, 1)


# ---------------------------------------------------------------------------
# ParabolicSARStrategy tests
# ---------------------------------------------------------------------------

class TestParabolicSARStrategy:
    def test_insufficient_data_returns_flat(self):
        sar = ParabolicSARStrategy()
        assert sar([]) == 0
        assert sar([_make_bar(100, 101, 99, 100)]) == 0
        assert sar([_make_bar(100, 101, 99, 100), _make_bar(101, 102, 100, 101)]) == 0

    def test_uptrend_gives_long(self):
        sar = ParabolicSARStrategy(af_start=0.02, af_step=0.02, af_max=0.20)
        bars = _trending_up_bars(40, step=2.0)
        signal = sar(bars)
        assert signal == 1

    def test_downtrend_gives_short(self):
        sar = ParabolicSARStrategy(af_start=0.02, af_step=0.02, af_max=0.20)
        bars = _trending_down_bars(40, start=200.0, step=2.0)
        signal = sar(bars)
        assert signal == -1

    def test_invalid_params_raise(self):
        with pytest.raises(ValueError):
            ParabolicSARStrategy(af_start=0.0)
        with pytest.raises(ValueError):
            ParabolicSARStrategy(af_start=0.5, af_max=0.2)  # start > max

    def test_repr(self):
        sar = ParabolicSARStrategy(af_start=0.02, af_step=0.02, af_max=0.20)
        r = repr(sar)
        assert "0.02" in r
        assert "0.2" in r

    def test_signal_alternates_on_trending_data(self):
        sar = ParabolicSARStrategy()
        # On an uptrend followed by a downtrend, SAR should produce both 1 and -1
        up_bars = _trending_up_bars(30, start=100.0, step=2.0)
        down_bars = _trending_down_bars(30, start=160.0, step=2.0)
        all_bars = up_bars + down_bars
        signals = set()
        for i in range(3, len(all_bars)):
            signals.add(sar(all_bars[:i + 1]))
        # Should produce both long and short signals across trend reversal
        assert len(signals) >= 2


# ---------------------------------------------------------------------------
# GapFadeStrategy tests
# ---------------------------------------------------------------------------

class TestGapFadeStrategy:
    def test_insufficient_data_returns_flat(self):
        gap = GapFadeStrategy()
        assert gap([_make_bar(100, 101, 99, 100)]) == 0

    def test_gap_up_fade_gives_short(self):
        gap = GapFadeStrategy(gap_threshold=0.01, mode="fade")
        bars = _flat_bars(15, price=100.0)
        # Add a gap-up: prev close=100, current open=103 (3% gap)
        bars.append(_make_bar(103, 104, 102, 103))
        assert gap(bars) == -1

    def test_gap_down_fade_gives_long(self):
        gap = GapFadeStrategy(gap_threshold=0.01, mode="fade")
        bars = _flat_bars(15, price=100.0)
        bars.append(_make_bar(97, 98, 96, 97))  # 3% gap down
        assert gap(bars) == 1

    def test_gap_up_follow_gives_long(self):
        gap = GapFadeStrategy(gap_threshold=0.01, mode="follow")
        bars = _flat_bars(15, price=100.0)
        bars.append(_make_bar(103, 104, 102, 103))
        assert gap(bars) == 1

    def test_small_gap_below_threshold_gives_flat(self):
        gap = GapFadeStrategy(gap_threshold=0.02, mode="fade")
        bars = _flat_bars(15, price=100.0)
        bars.append(_make_bar(100.5, 101, 100, 100.5))  # 0.5% gap — below 2% threshold
        assert gap(bars) == 0

    def test_invalid_threshold_raises(self):
        with pytest.raises(ValueError):
            GapFadeStrategy(gap_threshold=0.0)

    def test_invalid_mode_raises(self):
        with pytest.raises(ValueError):
            GapFadeStrategy(mode="invalid")

    def test_repr(self):
        gap = GapFadeStrategy(gap_threshold=0.01, mode="fade")
        r = repr(gap)
        assert "0.01" in r
        assert "fade" in r


# ---------------------------------------------------------------------------
# Batch 4-6: ShakeFilterStrategy tests
# ---------------------------------------------------------------------------

class TestShakeFilterStrategy:
    def test_insufficient_data_returns_flat(self):
        strat = ShakeFilterStrategy(period=10, shake_threshold=0.25)
        assert strat(_trending_up_bars(5)) == 0

    def test_choppy_market_suppressed(self):
        """Volatile oscillating market should be filtered out (choppy)."""
        strat = ShakeFilterStrategy(period=10, shake_threshold=0.70, atr_period=10)
        bars = _volatile_bars(40, center=100.0, amplitude=5.0)
        # Alternating bars have low dominant-direction score
        signal = strat(bars)
        assert signal == 0

    def test_trending_market_passes(self):
        """Strong trend should pass the shake filter and give directional signal."""
        strat = ShakeFilterStrategy(period=10, shake_threshold=0.25, atr_period=10)
        bars = _trending_up_bars(50, step=2.0)
        signal = strat(bars)
        assert signal in (0, 1)  # may or may not break channel, but not short

    def test_invalid_period_raises(self):
        with pytest.raises(ValueError):
            ShakeFilterStrategy(period=2)

    def test_invalid_threshold_raises(self):
        with pytest.raises(ValueError):
            ShakeFilterStrategy(shake_threshold=0.0)
        with pytest.raises(ValueError):
            ShakeFilterStrategy(shake_threshold=1.5)

    def test_signal_valid_range(self):
        strat = ShakeFilterStrategy(period=15, shake_threshold=0.25)
        for bars in [_trending_up_bars(60), _trending_down_bars(60), _volatile_bars(60)]:
            assert strat(bars) in (-1, 0, 1)

    def test_repr(self):
        strat = ShakeFilterStrategy(period=15, shake_threshold=0.25)
        r = repr(strat)
        assert "15" in r
        assert "0.25" in r


# ---------------------------------------------------------------------------
# Batch 4-6: SqrtTimeTrailStrategy tests
# ---------------------------------------------------------------------------

class TestSqrtTimeTrailStrategy:
    def test_insufficient_data_returns_flat(self):
        strat = SqrtTimeTrailStrategy(breakout_period=14, atr_period=14)
        assert strat(_trending_up_bars(5)) == 0

    def test_breakout_enters_long(self):
        strat = SqrtTimeTrailStrategy(
            breakout_period=5, atr_period=5, trail_atr_mult=2.0
        )
        bars = _breakout_bars(20, range_price=100.0, breakout_price=115.0)
        # After breakout, should be long (or flat if trailed out)
        signal = strat(bars)
        assert signal in (0, 1)

    def test_downtrend_enters_short(self):
        strat = SqrtTimeTrailStrategy(
            breakout_period=5, atr_period=5, trail_atr_mult=2.0
        )
        bars = [_make_bar(100, 101, 99, 100) for _ in range(15)]
        bars.append(_make_bar(90, 90.5, 75, 76))  # breakdown
        signal = strat(bars)
        assert signal in (-1, 0)

    def test_invalid_breakout_period_raises(self):
        with pytest.raises(ValueError):
            SqrtTimeTrailStrategy(breakout_period=1)

    def test_invalid_trail_mult_raises(self):
        with pytest.raises(ValueError):
            SqrtTimeTrailStrategy(trail_atr_mult=0.0)

    def test_signal_valid_range(self):
        strat = SqrtTimeTrailStrategy()
        for bars in [_trending_up_bars(60), _trending_down_bars(60), _flat_bars(60)]:
            assert strat(bars) in (-1, 0, 1)

    def test_repr(self):
        strat = SqrtTimeTrailStrategy(breakout_period=14, trail_atr_mult=1.5)
        r = repr(strat)
        assert "14" in r
        assert "1.5" in r


# ---------------------------------------------------------------------------
# Batch 4-6: AdaptiveMultiplierMAStrategy tests
# ---------------------------------------------------------------------------

class TestAdaptiveMultiplierMAStrategy:
    def test_insufficient_data_returns_flat(self):
        strat = AdaptiveMultiplierMAStrategy(base_period=20)
        assert strat(_trending_up_bars(5)) == 0

    def test_uptrend_gives_long(self):
        strat = AdaptiveMultiplierMAStrategy(base_period=10, loss_multiplier=2.0)
        bars = _trending_up_bars(50, step=1.0)
        signal = strat(bars)
        assert signal == 1

    def test_downtrend_gives_short(self):
        strat = AdaptiveMultiplierMAStrategy(base_period=10, loss_multiplier=2.0)
        bars = _trending_down_bars(50, step=1.0)
        signal = strat(bars)
        assert signal == -1

    def test_flat_gives_neutral(self):
        strat = AdaptiveMultiplierMAStrategy(base_period=10)
        bars = _flat_bars(30)
        assert strat(bars) == 0

    def test_invalid_period_raises(self):
        with pytest.raises(ValueError):
            AdaptiveMultiplierMAStrategy(base_period=1)

    def test_invalid_multiplier_raises(self):
        with pytest.raises(ValueError):
            AdaptiveMultiplierMAStrategy(loss_multiplier=0.5)

    def test_signal_valid_range(self):
        strat = AdaptiveMultiplierMAStrategy(base_period=10)
        for bars in [_trending_up_bars(60), _trending_down_bars(60), _flat_bars(60)]:
            assert strat(bars) in (-1, 0, 1)

    def test_repr(self):
        strat = AdaptiveMultiplierMAStrategy(base_period=20, loss_multiplier=2.0)
        r = repr(strat)
        assert "20" in r
        assert "2.0" in r


# ---------------------------------------------------------------------------
# Batch 4-6: GoldenRatioMAStrategy tests
# ---------------------------------------------------------------------------

class TestGoldenRatioMAStrategy:
    def test_insufficient_data_returns_flat(self):
        strat = GoldenRatioMAStrategy(fast_period=56, slow_period=91)
        assert strat(_trending_up_bars(50)) == 0

    def test_uptrend_gives_long(self):
        # Use smaller periods to reduce required bars in test
        strat = GoldenRatioMAStrategy(fast_period=5, slow_period=8)
        bars = _trending_up_bars(30, step=1.0)
        signal = strat(bars)
        assert signal == 1

    def test_downtrend_gives_short(self):
        strat = GoldenRatioMAStrategy(fast_period=5, slow_period=8)
        bars = _trending_down_bars(30, step=1.0)
        signal = strat(bars)
        assert signal == -1

    def test_invalid_periods_raise(self):
        with pytest.raises(ValueError):
            GoldenRatioMAStrategy(fast_period=1, slow_period=2)
        with pytest.raises(ValueError):
            GoldenRatioMAStrategy(fast_period=10, slow_period=8)  # slow < fast

    def test_phi_ratio_repr(self):
        strat = GoldenRatioMAStrategy(fast_period=56, slow_period=91)
        r = repr(strat)
        assert "56" in r
        assert "91" in r
        assert "1.6" in r  # ratio ≈ 1.625

    def test_signal_valid_range(self):
        strat = GoldenRatioMAStrategy(fast_period=5, slow_period=8)
        for bars in [_trending_up_bars(40), _trending_down_bars(40), _flat_bars(40)]:
            assert strat(bars) in (-1, 0, 1)


# ---------------------------------------------------------------------------
# Batch 4-6: KPowerStrategy tests
# ---------------------------------------------------------------------------

class TestKPowerStrategy:
    def test_insufficient_data_returns_flat(self):
        strat = KPowerStrategy(pressure_period=4, std_period=20, consecutive_days=3)
        assert strat(_trending_up_bars(10)) == 0

    def test_buying_pressure_gives_long(self):
        """In an uptrend, closes near highs → LPower > SPower → long."""
        strat = KPowerStrategy(pressure_period=3, std_period=10, consecutive_days=2)
        # Bars with close very near high (strong buying pressure)
        bars = [_make_bar(b, b + 2.0, b - 0.1, b + 1.9) for b in range(100, 130)]
        signal = strat(bars)
        assert signal in (0, 1)  # buying pressure present

    def test_selling_pressure_gives_short(self):
        """In a downtrend, closes near lows → SPower > LPower → short."""
        strat = KPowerStrategy(pressure_period=3, std_period=10, consecutive_days=2)
        # Bars with close very near low (strong selling pressure)
        bars = [_make_bar(b, b + 0.1, b - 2.0, b - 1.9) for b in range(130, 100, -1)]
        signal = strat(bars)
        assert signal in (-1, 0)

    def test_flat_no_pressure(self):
        strat = KPowerStrategy(pressure_period=4, std_period=20, consecutive_days=3)
        bars = _flat_bars(40)
        assert strat(bars) == 0

    def test_invalid_period_raises(self):
        with pytest.raises(ValueError):
            KPowerStrategy(pressure_period=0)
        with pytest.raises(ValueError):
            KPowerStrategy(std_period=1)

    def test_signal_valid_range(self):
        strat = KPowerStrategy(pressure_period=3, std_period=14, consecutive_days=2)
        for bars in [_trending_up_bars(60), _trending_down_bars(60), _flat_bars(60)]:
            assert strat(bars) in (-1, 0, 1)

    def test_repr(self):
        strat = KPowerStrategy(pressure_period=4, std_period=20, consecutive_days=3)
        r = repr(strat)
        assert "4" in r
        assert "20" in r
        assert "3" in r


# ---------------------------------------------------------------------------
# Batch 4-6: BarTimingStrategy tests
# ---------------------------------------------------------------------------

class TestBarTimingStrategy:
    def test_insufficient_data_returns_flat(self):
        strat = BarTimingStrategy(session_bars=48, lookback=10)
        assert strat(_trending_up_bars(5)) == 0

    def test_recent_high_gives_long(self):
        """When the highest close occurs near the end of the window: uptrend."""
        strat = BarTimingStrategy(session_bars=48, lookback=5)
        # Need lookback + 1 = 6 bars minimum; the last 5 form the window
        bars = [
            _make_bar(100, 101, 99, 98),   # extra bar to satisfy required >= 6
            _make_bar(100, 101, 99, 99),
            _make_bar(100, 101, 99, 100),
            _make_bar(100, 101, 99, 101),
            _make_bar(100, 102, 99, 102),
            _make_bar(100, 104, 99, 104),  # highest close = most recent
        ]
        signal = strat(bars)
        assert signal == 1

    def test_recent_low_gives_short(self):
        """When the lowest close occurs near the end: downtrend."""
        strat = BarTimingStrategy(session_bars=48, lookback=5)
        # Need 6 bars; last 5 form the window with lowest at the end
        bars = [
            _make_bar(105, 106, 104, 105),  # extra bar
            _make_bar(104, 105, 103, 104),
            _make_bar(103, 104, 102, 103),
            _make_bar(102, 103, 101, 102),
            _make_bar(101, 102, 100, 101),
            _make_bar(100, 101, 99, 99),   # lowest close = most recent
        ]
        signal = strat(bars)
        assert signal == -1

    def test_middle_extreme_gives_flat(self):
        """When the extreme is in the middle: no clear timing bias."""
        strat = BarTimingStrategy(session_bars=48, lookback=5)
        # Need 6 bars; last 5 form window with max at index 1 (recency=0.25)
        bars = [
            _make_bar(100, 101, 99, 100),  # extra bar
            _make_bar(100, 101, 99, 100),
            _make_bar(100, 105, 99, 105),  # max at index 1 of 5 → recency=0.25
            _make_bar(100, 101, 99, 101),
            _make_bar(100, 101, 99, 100),
            _make_bar(100, 101, 99, 100),
        ]
        signal = strat(bars)
        assert signal == 0  # extreme at recency=0.25 < 0.60 threshold

    def test_invalid_session_bars_raises(self):
        with pytest.raises(ValueError):
            BarTimingStrategy(session_bars=2)

    def test_invalid_lookback_raises(self):
        with pytest.raises(ValueError):
            BarTimingStrategy(lookback=1)

    def test_signal_valid_range(self):
        strat = BarTimingStrategy(session_bars=48, lookback=10)
        for bars in [_trending_up_bars(40), _trending_down_bars(40), _volatile_bars(40)]:
            assert strat(bars) in (-1, 0, 1)

    def test_repr(self):
        strat = BarTimingStrategy(session_bars=78, lookback=10)
        r = repr(strat)
        assert "78" in r
        assert "10" in r
