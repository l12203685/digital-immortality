"""Tests for pla_pattern_catalog.py — indicator extraction, frequency, co-occurrence."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import List

import pytest

from trading.pla_pattern_catalog import (
    EXISTING_STRATEGY_TAGS,
    DigestionEntry,
    PatternCatalog,
    StrategyConfig,
    TAG_TO_STRATEGY_SPACE,
    build_catalog,
    build_cooccurrence,
    build_indicator_frequency,
    detect_indicators,
    export_catalog_json,
    export_catalog_markdown,
    extract_parameter_ranges,
    find_untapped_combinations,
    find_untapped_combos,
    generate_strategy_configs_from_catalog,
    load_digestion_log,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_entry(
    summary: str = "",
    category: str = "",
    tags: tuple[str, ...] = (),
    strategy_name: str = "",
    **kwargs: str,
) -> DigestionEntry:
    return DigestionEntry(
        path=kwargs.get("path", "/fake/path.pdf"),
        summary=summary,
        strategy_name=strategy_name,
        category=category,
        family=kwargs.get("family", ""),
        direction=kwargs.get("direction", ""),
        timeframe=kwargs.get("timeframe", ""),
        tags=tags,
        tier=1,
    )


SAMPLE_ENTRIES: List[DigestionEntry] = [
    _make_entry(
        summary="Bollinger Band + RSI + ATR filter. BBLen=19, BBDev=1.5. RSI 14 period.",
        category="Bollinger Band + RSI + ATR filter",
    ),
    _make_entry(
        summary="MACD histogram crossover with EMA 12/26 signal 9. Trend-following.",
        category="MACD trend",
    ),
    _make_entry(
        summary="CCI 20 period breakout when CCI crosses above 100. Day-trade.",
        category="CCI breakout",
    ),
    _make_entry(
        summary="KD stochastic 14 oversold entry. Gap fade on open-gap > 1%.",
        category="KD + gap",
    ),
    _make_entry(
        summary="Dual MA crossover SMA 10 vs SMA 50. ATR trailing stop.",
        category="MA crossover",
    ),
    _make_entry(
        summary="Donchian channel breakout 20 period. ATR 14 stop.",
        category="channel breakout",
    ),
    _make_entry(
        summary="CDP pivot point reversal strategy with ATR filter.",
        category="CDP reversal",
    ),
    _make_entry(
        summary="Parabolic SAR trend follow with ADX filter > 25. DMI direction.",
        category="SAR + DMI",
    ),
    _make_entry(
        summary="Opening range breakout (ORB) on 5-min bars. Keltner channel confirmation.",
        category="ORB + Keltner",
    ),
    _make_entry(
        summary="Williams %R oscillator with Bollinger squeeze entry. BB period 20.",
        category="WilliamsR + BB",
    ),
]


# ---------------------------------------------------------------------------
# detect_indicators
# ---------------------------------------------------------------------------

class TestDetectIndicators:
    def test_empty_string(self) -> None:
        assert detect_indicators("") == []

    def test_single_indicator(self) -> None:
        result = detect_indicators("RSI 14 period oversold")
        assert "RSI" in result

    def test_multiple_indicators(self) -> None:
        result = detect_indicators("MACD histogram with EMA 12/26")
        assert "MA" in result
        assert "MACD" in result

    def test_bollinger_variants(self) -> None:
        for text in ["Bollinger Band", "BBand", "Bval < 0.5"]:
            result = detect_indicators(text)
            assert "Bollinger" in result, f"Failed for: {text}"

    def test_case_insensitive(self) -> None:
        result = detect_indicators("macd signal line crossing")
        assert "MACD" in result

    def test_atr_detection(self) -> None:
        result = detect_indicators("ATR 14 trailing stop with true range filter")
        assert "ATR" in result

    def test_kd_stochastic(self) -> None:
        result = detect_indicators("KD stochastic %K/%D crossover")
        assert "KD" in result

    def test_cdp(self) -> None:
        result = detect_indicators("CDP pivot levels for support/resistance")
        assert "CDP" in result

    def test_sar(self) -> None:
        result = detect_indicators("Parabolic SAR trend reversal")
        assert "SAR" in result

    def test_keltner(self) -> None:
        result = detect_indicators("Keltner Channel KC squeeze")
        assert "Keltner" in result

    def test_returns_sorted(self) -> None:
        result = detect_indicators("RSI 14 with MACD and ATR")
        assert result == sorted(result)

    # Batch 4-6 indicator detection
    def test_shake_filter_detection(self) -> None:
        for text in ["shake-filter oscillation count", "mid direction stable"]:
            result = detect_indicators(text)
            assert "ShakeFilter" in result, f"ShakeFilter not detected in: {text}"

    def test_sqrt_time_trail_detection(self) -> None:
        result = detect_indicators("sqrt-time trailing stop tightens")
        assert "SqrtTimeTrail" in result

    def test_adaptive_multiplier_detection(self) -> None:
        result = detect_indicators("adaptive multiplier doubles after loss")
        assert "AdaptiveMultiplier" in result

    def test_golden_ratio_ma_detection(self) -> None:
        result = detect_indicators("golden-ratio MA pair phi=1.618")
        assert "GoldenRatioMA" in result

    def test_kpower_detection(self) -> None:
        for text in ["KPower buying pressure score", "LPower SPower net"]:
            result = detect_indicators(text)
            assert "KPower" in result, f"KPower not detected in: {text}"

    def test_bar_timing_detection(self) -> None:
        for text in ["Hbar Lbar session timing", "bar-timing when daily L was made"]:
            result = detect_indicators(text)
            assert "BarTiming" in result, f"BarTiming not detected in: {text}"


class TestTagToStrategySpace:
    def test_all_batch46_tags_present(self) -> None:
        """All 6 batch 4-6 indicator types have entries in TAG_TO_STRATEGY_SPACE."""
        for tag in ["ShakeFilter", "SqrtTimeTrail", "AdaptiveMultiplier",
                    "GoldenRatioMA", "KPower", "BarTiming"]:
            assert tag in TAG_TO_STRATEGY_SPACE, f"{tag} missing from TAG_TO_STRATEGY_SPACE"
            assert len(TAG_TO_STRATEGY_SPACE[tag]) >= 1

    def test_golden_ratio_slow_gt_fast(self) -> None:
        """GoldenRatioMA configs must have slow > fast."""
        for entry in TAG_TO_STRATEGY_SPACE["GoldenRatioMA"]:
            assert entry["params"]["slow_period"] > entry["params"]["fast_period"]

    def test_all_batch46_in_existing_tags(self) -> None:
        """Batch 4-6 tags are in EXISTING_STRATEGY_TAGS (covered pool)."""
        for tag in ["ShakeFilter", "SqrtTimeTrail", "AdaptiveMultiplier",
                    "GoldenRatioMA", "KPower", "BarTiming"]:
            assert tag in EXISTING_STRATEGY_TAGS, f"{tag} not in EXISTING_STRATEGY_TAGS"


# ---------------------------------------------------------------------------
# build_indicator_frequency
# ---------------------------------------------------------------------------

class TestBuildIndicatorFrequency:
    def test_counts_across_entries(self) -> None:
        freq = build_indicator_frequency(SAMPLE_ENTRIES)
        assert freq["ATR"] >= 3  # appears in multiple entries
        assert freq["Bollinger"] >= 2
        assert freq["MACD"] >= 1

    def test_empty_entries(self) -> None:
        assert build_indicator_frequency([]) == {}

    def test_no_double_count_per_entry(self) -> None:
        """Each indicator counted at most once per entry."""
        entry = _make_entry(
            summary="RSI RSI RSI RSI RSI RSI",
        )
        freq = build_indicator_frequency([entry])
        assert freq["RSI"] == 1


# ---------------------------------------------------------------------------
# build_cooccurrence
# ---------------------------------------------------------------------------

class TestBuildCooccurrence:
    def test_pairs_detected(self) -> None:
        pairs, _ = build_cooccurrence(SAMPLE_ENTRIES)
        # Bollinger+RSI should appear together
        assert ("ATR", "Bollinger") in pairs or ("Bollinger", "ATR") in pairs

    def test_triples_detected(self) -> None:
        _, triples = build_cooccurrence(SAMPLE_ENTRIES)
        # ATR + Bollinger + RSI should form a triple
        key = ("ATR", "Bollinger", "RSI")
        assert key in triples

    def test_single_indicator_no_pairs(self) -> None:
        entry = _make_entry(summary="CCI only strategy with CCI breakout.")
        pairs, triples = build_cooccurrence([entry])
        assert len(pairs) == 0
        assert len(triples) == 0


# ---------------------------------------------------------------------------
# extract_parameter_ranges
# ---------------------------------------------------------------------------

class TestExtractParameterRanges:
    def test_extracts_ma_period(self) -> None:
        entry = _make_entry(summary="SMA 10 vs SMA 50 crossover")
        ranges = extract_parameter_ranges([entry])
        assert "MA" in ranges
        assert "period" in ranges["MA"]
        assert 10 in ranges["MA"]["period"]["values"]
        assert 50 in ranges["MA"]["period"]["values"]

    def test_extracts_bb_dev(self) -> None:
        entry = _make_entry(summary="Bollinger BBDev=1.5 BBLen=20")
        ranges = extract_parameter_ranges([entry])
        assert "Bollinger" in ranges
        assert "std_dev" in ranges["Bollinger"]

    def test_filters_implausible_values(self) -> None:
        """Values > 500 (likely dates/file names) are filtered out."""
        entry = _make_entry(summary="MA202106 strategy test. EMA 3 period.")
        ranges = extract_parameter_ranges([entry])
        if "MA" in ranges and "period" in ranges["MA"]:
            for val in ranges["MA"]["period"]["values"]:
                assert val <= 500

    def test_empty_entries(self) -> None:
        assert extract_parameter_ranges([]) == {}


# ---------------------------------------------------------------------------
# build_catalog
# ---------------------------------------------------------------------------

class TestBuildCatalog:
    def test_catalog_structure(self) -> None:
        catalog = build_catalog(SAMPLE_ENTRIES)
        assert catalog.total_entries == len(SAMPLE_ENTRIES)
        assert isinstance(catalog.indicator_frequency, dict)
        assert isinstance(catalog.pair_cooccurrence, dict)
        assert isinstance(catalog.parameter_ranges, dict)

    def test_covered_indicators(self) -> None:
        catalog = build_catalog(SAMPLE_ENTRIES, existing_tags=["MA", "RSI"])
        assert "MA" in catalog.covered_indicators
        assert "RSI" in catalog.covered_indicators

    def test_untapped_detected(self) -> None:
        catalog = build_catalog(SAMPLE_ENTRIES, existing_tags=["MA"])
        untapped_names = [t for t, _ in catalog.untapped_indicators]
        # ATR appears in multiple entries and is not in existing
        assert "ATR" in untapped_names


# ---------------------------------------------------------------------------
# find_untapped_combinations / find_untapped_combos
# ---------------------------------------------------------------------------

class TestFindUntapped:
    def test_untapped_single(self) -> None:
        freq = {"MA": 10, "RSI": 8, "CDP": 5, "SAR": 3}
        result = find_untapped_combinations(freq, {}, ["MA", "RSI"])
        tags = [t for t, _ in result]
        assert "CDP" in tags
        assert "SAR" in tags
        assert "MA" not in tags

    def test_untapped_combos(self) -> None:
        combo_freq = {
            ("MA", "RSI"): 5,
            ("CDP", "MA"): 4,
            ("CDP", "SAR"): 3,
        }
        result = find_untapped_combos(combo_freq, ["MA", "RSI"])
        combo_strs = [c for c, _ in result]
        assert ("CDP", "MA") in combo_strs
        assert ("CDP", "SAR") in combo_strs
        assert ("MA", "RSI") not in combo_strs

    def test_threshold_filtering(self) -> None:
        freq = {"Rare": 1, "Common": 5}
        result = find_untapped_combinations(freq, {}, [])
        tags = [t for t, _ in result]
        assert "Rare" not in tags  # count < 2
        assert "Common" in tags


# ---------------------------------------------------------------------------
# generate_strategy_configs_from_catalog
# ---------------------------------------------------------------------------

class TestGenerateStrategyConfigs:
    def test_generates_from_missing_log(self) -> None:
        """When log doesn't exist, falls back to all known spaces."""
        configs = generate_strategy_configs_from_catalog(
            log_path=Path("/nonexistent/digestion_log.jsonl"),
            top_n=5,
        )
        assert len(configs) == 5
        assert all(isinstance(c, StrategyConfig) for c in configs)

    def test_config_immutable(self) -> None:
        configs = generate_strategy_configs_from_catalog(
            log_path=Path("/nonexistent/path.jsonl"),
            top_n=1,
        )
        cfg = configs[0]
        with pytest.raises(AttributeError):
            cfg.priority = 999  # type: ignore[misc]

    def test_deduplication(self) -> None:
        """No duplicate (class, params) in output."""
        configs = generate_strategy_configs_from_catalog(
            log_path=Path("/nonexistent/path.jsonl"),
            top_n=100,
        )
        seen = set()
        for cfg in configs:
            key = (cfg.strategy_class, str(sorted(cfg.params.items())))
            assert key not in seen, f"Duplicate config: {key}"
            seen.add(key)

    def test_backward_compat_index_path(self) -> None:
        """index_path parameter is accepted but ignored."""
        configs = generate_strategy_configs_from_catalog(
            index_path=Path("/some/LOGIC_INDEX.md"),
            log_path=Path("/nonexistent/path.jsonl"),
            top_n=3,
        )
        assert len(configs) == 3


# ---------------------------------------------------------------------------
# load_digestion_log
# ---------------------------------------------------------------------------

class TestLoadDigestionLog:
    def test_load_valid_file(self, tmp_path: Path) -> None:
        log_file = tmp_path / "test.jsonl"
        entries_data = [
            {"path": "/a.pdf", "summary": "RSI strategy with 14 period oversold entry. ATR stop."},
            {"path": "/b.pdf", "summary": "MACD histogram crossover trend following strategy."},
            {"path": "/c.pdf", "summary": ""},  # empty summary, should be skipped
        ]
        log_file.write_text(
            "\n".join(json.dumps(e) for e in entries_data),
            encoding="utf-8",
        )
        result = load_digestion_log(log_file)
        assert len(result) == 2  # one skipped due to short summary
        assert result[0].path == "/a.pdf"

    def test_missing_file_raises(self) -> None:
        with pytest.raises(FileNotFoundError):
            load_digestion_log(Path("/nonexistent/file.jsonl"))


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

class TestExport:
    def test_export_json(self, tmp_path: Path) -> None:
        catalog = build_catalog(SAMPLE_ENTRIES)
        out = tmp_path / "catalog.json"
        export_catalog_json(catalog, out)
        assert out.exists()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert "indicator_frequency" in data
        assert "parameter_ranges" in data
        assert data["total_entries_analyzed"] == len(SAMPLE_ENTRIES)

    def test_export_markdown(self, tmp_path: Path) -> None:
        catalog = build_catalog(SAMPLE_ENTRIES)
        out = tmp_path / "catalog.md"
        export_catalog_markdown(catalog, out)
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "# PLA Pattern Catalog" in content
        assert "Indicator Frequency" in content

    def test_export_creates_parent_dirs(self, tmp_path: Path) -> None:
        catalog = build_catalog(SAMPLE_ENTRIES)
        out = tmp_path / "sub" / "dir" / "catalog.json"
        export_catalog_json(catalog, out)
        assert out.exists()


# ---------------------------------------------------------------------------
# Integration: full pipeline on real log if available
# ---------------------------------------------------------------------------

class TestIntegrationRealLog:
    @pytest.mark.skipif(
        not Path("C:/Users/admin/workspace/digital-immortality/results/digestion_log.jsonl").exists(),
        reason="Real digestion log not available",
    )
    def test_full_pipeline(self, tmp_path: Path) -> None:
        log_path = Path("C:/Users/admin/workspace/digital-immortality/results/digestion_log.jsonl")
        entries = load_digestion_log(log_path)
        assert len(entries) > 100

        catalog = build_catalog(entries)
        assert catalog.total_entries > 100
        assert len(catalog.indicator_frequency) >= 5

        # Export
        json_out = tmp_path / "catalog.json"
        md_out = tmp_path / "catalog.md"
        export_catalog_json(catalog, json_out)
        export_catalog_markdown(catalog, md_out)
        assert json_out.exists()
        assert md_out.exists()

        # Verify JSON roundtrip
        data = json.loads(json_out.read_text(encoding="utf-8"))
        assert data["total_entries_analyzed"] == catalog.total_entries

    @pytest.mark.skipif(
        not Path("C:/Users/admin/workspace/digital-immortality/results/digestion_log.jsonl").exists(),
        reason="Real digestion log not available",
    )
    def test_generate_configs_from_real_log(self) -> None:
        log_path = Path("C:/Users/admin/workspace/digital-immortality/results/digestion_log.jsonl")
        configs = generate_strategy_configs_from_catalog(log_path=log_path, top_n=20)
        assert len(configs) > 0
        assert all(isinstance(c, StrategyConfig) for c in configs)
        # Configs should be sorted by priority descending
        priorities = [c.priority for c in configs]
        assert priorities == sorted(priorities, reverse=True)
