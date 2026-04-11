"""Unit tests for trading/orthogonality_filter.py (B1 audit follow-up)."""
from __future__ import annotations

import random
from typing import Callable, Dict, List, Mapping

from trading.orthogonality_filter import (
    MIN_SAMPLES_FOR_CORRELATION,
    OrthogonalityFilter,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _make_bars(prices: List[float]) -> List[Dict[str, float]]:
    return [
        {"open": p, "high": p, "low": p, "close": p, "volume": 0.0}
        for p in prices
    ]


def _strategy_from_series(series: List[int]) -> Callable:
    """Return a callable that, given bars, emits series[len(bars)-1]."""
    def _call(bars: List[Dict[str, float]]) -> int:
        idx = max(0, len(bars) - 1)
        if idx >= len(series):
            return series[-1] if series else 0
        return int(series[idx])
    return _call


def _bars_for(n: int) -> List[Dict[str, float]]:
    # Price shape does not matter — the stub strategies above pick signals
    # by bar index, not by price. We only need `len(bars)` to advance.
    return _make_bars([100.0 + i for i in range(n)])


# ---------------------------------------------------------------------------
# correlation() primitive
# ---------------------------------------------------------------------------
def test_correlation_identical_is_one():
    a = [1, 0, -1, 1, 0, -1, 1, 1, 0, -1]
    flt = OrthogonalityFilter()
    assert abs(flt.correlation(a, a) - 1.0) < 1e-9


def test_correlation_anti_is_minus_one():
    a = [1, 0, -1, 1, 0, -1, 1, 1, 0, -1]
    b = [-x for x in a]
    flt = OrthogonalityFilter()
    assert abs(flt.correlation(a, b) - (-1.0)) < 1e-9


def test_correlation_constant_series_returns_zero():
    a = [1, 1, 1, 1, 1, 1]
    b = [0, 1, 0, 1, 0, 1]
    flt = OrthogonalityFilter()
    assert flt.correlation(a, b) == 0.0


def test_correlation_clamped_to_unit_range():
    rng = random.Random(17)
    a = [rng.choice([-1, 0, 1]) for _ in range(200)]
    flt = OrthogonalityFilter()
    r = flt.correlation(a, a)
    assert -1.0 <= r <= 1.0


# ---------------------------------------------------------------------------
# signal_series() windowing
# ---------------------------------------------------------------------------
def test_signal_series_respects_lookback():
    flt = OrthogonalityFilter(max_corr=0.7, lookback_ticks=50)
    series = [1 if i % 3 == 0 else -1 for i in range(200)]
    strat = _strategy_from_series(series)
    out = flt.signal_series(strat, _bars_for(200))
    # Walks from (n - lookback) through n inclusive, so 51 samples.
    assert len(out) in (50, 51)
    # Last value should match the last index of the synthetic series.
    assert out[-1] == series[199]


# ---------------------------------------------------------------------------
# is_orthogonal() decisions
# ---------------------------------------------------------------------------
def test_empty_pool_always_accepted():
    flt = OrthogonalityFilter()
    passed, reason = flt.is_orthogonal(
        candidate_strategy=_strategy_from_series([1] * 200),
        pool_strategies={},
        bars_history=_bars_for(200),
        candidate_name="empty_pool_candidate",
    )
    assert passed is True
    assert reason == "empty_pool"


def test_identical_signal_rejected():
    flt = OrthogonalityFilter(max_corr=0.7, lookback_ticks=100)
    pattern = [1 if i % 4 < 2 else -1 for i in range(200)]
    pool = {"incumbent": _strategy_from_series(pattern)}
    passed, reason = flt.is_orthogonal(
        candidate_strategy=_strategy_from_series(pattern),
        pool_strategies=pool,
        bars_history=_bars_for(200),
        candidate_name="dup_of_incumbent",
    )
    assert passed is False
    assert "rejected" in reason
    assert "incumbent" in reason


def test_anti_correlated_signal_rejected():
    flt = OrthogonalityFilter(max_corr=0.7, lookback_ticks=100)
    pattern = [1 if i % 5 < 2 else -1 for i in range(200)]
    anti = [-x for x in pattern]
    pool = {"incumbent": _strategy_from_series(pattern)}
    passed, reason = flt.is_orthogonal(
        candidate_strategy=_strategy_from_series(anti),
        pool_strategies=pool,
        bars_history=_bars_for(200),
        candidate_name="anti_of_incumbent",
    )
    assert passed is False
    assert "rejected" in reason


def test_orthogonal_random_signal_accepted():
    flt = OrthogonalityFilter(max_corr=0.7, lookback_ticks=150)
    rng_a = random.Random(7)
    rng_b = random.Random(9001)
    pat_a = [rng_a.choice([-1, 0, 1]) for _ in range(200)]
    pat_b = [rng_b.choice([-1, 0, 1]) for _ in range(200)]
    pool = {"incumbent": _strategy_from_series(pat_a)}
    passed, reason = flt.is_orthogonal(
        candidate_strategy=_strategy_from_series(pat_b),
        pool_strategies=pool,
        bars_history=_bars_for(200),
        candidate_name="ortho_random",
    )
    assert passed is True
    assert "accepted" in reason


def test_insufficient_history_accepted_with_warning(caplog=None):
    # No pytest dependency — use stdlib logging capture via a handler.
    import logging
    import io

    flt = OrthogonalityFilter(max_corr=0.7, lookback_ticks=100)
    pool = {"incumbent": _strategy_from_series([1] * 5)}

    buf = io.StringIO()
    handler = logging.StreamHandler(buf)
    handler.setLevel(logging.WARNING)
    log = logging.getLogger("trading.orthogonality_filter")
    log.addHandler(handler)
    try:
        passed, reason = flt.is_orthogonal(
            candidate_strategy=_strategy_from_series([1] * 5),
            pool_strategies=pool,
            bars_history=_bars_for(5),  # far below MIN_SAMPLES_FOR_CORRELATION
            candidate_name="shorty",
        )
    finally:
        log.removeHandler(handler)

    assert passed is True
    assert reason.startswith("insufficient_history")
    assert "shorty" in buf.getvalue()


def test_borderline_below_threshold_accepted():
    """Correlation just below the threshold must pass."""
    flt = OrthogonalityFilter(max_corr=0.7, lookback_ticks=100)
    # Build two partially overlapping patterns so correlation is < 0.7.
    pat_a = [(1 if i % 2 == 0 else -1) for i in range(200)]
    pat_b = [(1 if i % 3 == 0 else -1) for i in range(200)]
    # Verify the correlation is in fact below 0.7
    a_series = flt.signal_series(_strategy_from_series(pat_a), _bars_for(200))
    b_series = flt.signal_series(_strategy_from_series(pat_b), _bars_for(200))
    assert abs(flt.correlation(a_series, b_series)) < 0.7

    pool = {"incumbent": _strategy_from_series(pat_a)}
    passed, reason = flt.is_orthogonal(
        candidate_strategy=_strategy_from_series(pat_b),
        pool_strategies=pool,
        bars_history=_bars_for(200),
        candidate_name="partial_overlap",
    )
    assert passed is True, f"unexpected reject: {reason}"


def test_init_validates_parameters():
    try:
        OrthogonalityFilter(max_corr=1.5)
    except ValueError:
        pass
    else:
        raise AssertionError("max_corr > 1.0 should raise")

    try:
        OrthogonalityFilter(lookback_ticks=5)
    except ValueError:
        pass
    else:
        raise AssertionError("lookback_ticks below min should raise")


def test_log_rejection_writes_jsonl(tmp_path=None):
    import json
    import tempfile
    from pathlib import Path
    from trading import orthogonality_filter as mod

    with tempfile.TemporaryDirectory() as tmp:
        original = mod.REJECTION_LOG_PATH
        original_dir = mod.RESULTS_DIR
        fake_dir = Path(tmp)
        mod.RESULTS_DIR = fake_dir
        mod.REJECTION_LOG_PATH = fake_dir / "orthogonality_rejections.jsonl"
        try:
            OrthogonalityFilter.log_rejection(
                candidate_name="gen_DualMA_9999",
                reason="rejected: max|corr|=0.95 with 'DualMA_10_30'",
                max_corr_with="DualMA_10_30",
                corr=0.95,
                extra={"source": "unit_test"},
            )
            lines = mod.REJECTION_LOG_PATH.read_text(encoding="utf-8").strip().splitlines()
            assert len(lines) == 1
            rec = json.loads(lines[0])
            assert rec["candidate"] == "gen_DualMA_9999"
            assert rec["max_corr_with"] == "DualMA_10_30"
            assert rec["corr"] == 0.95
            assert rec["source"] == "unit_test"
            assert "ts" in rec
        finally:
            mod.REJECTION_LOG_PATH = original
            mod.RESULTS_DIR = original_dir


# ---------------------------------------------------------------------------
# Main: run all tests as a standalone script (no pytest required)
# ---------------------------------------------------------------------------
def _run_all() -> None:
    tests = [
        test_correlation_identical_is_one,
        test_correlation_anti_is_minus_one,
        test_correlation_constant_series_returns_zero,
        test_correlation_clamped_to_unit_range,
        test_signal_series_respects_lookback,
        test_empty_pool_always_accepted,
        test_identical_signal_rejected,
        test_anti_correlated_signal_rejected,
        test_orthogonal_random_signal_accepted,
        test_insufficient_history_accepted_with_warning,
        test_borderline_below_threshold_accepted,
        test_init_validates_parameters,
        test_log_rejection_writes_jsonl,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {t.__name__}: {e}")
            failed += 1
        except Exception as e:  # noqa: BLE001
            print(f"  ERROR {t.__name__}: {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{passed}/{len(tests)} passed, {failed} failed")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    _run_all()
