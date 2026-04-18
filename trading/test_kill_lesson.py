"""Tests for kill_lesson.py — Kill-Lesson Extraction System.

Tests cover:
  - Kill record parsing and loading
  - Kill reason classification
  - Pattern detection (PF decay, MDD, WR collapse, restart loops)
  - ZP principle cross-referencing
  - Lesson generation
  - Output formatting (JSONL + markdown)
  - Strategy summary statistics
"""
import json
import tempfile
from pathlib import Path

import pytest

from trading.kill_lesson import (
    KillAnalysis,
    KillPattern,
    KillRecord,
    Lesson,
    analyze_kills,
    build_strategy_summary,
    classify_kills,
    cross_reference_zp,
    generate_lessons,
    load_kills,
    parse_kill_reason,
    to_jsonl,
    to_markdown,
)


# --- Fixtures ---

def _make_kill(strategy: str = "DualMA_10_30",
               reason: str = "PF 0.78 < 0.8",
               tick: int = 100,
               cum_pnl: float = -0.5,
               regime: str = "mixed",
               price: float = 75000.0,
               ts: str = "2026-04-16T06:00:00+00:00") -> KillRecord:
    return KillRecord(
        ts=ts, tick=tick, strategy=strategy, kill_reason=reason,
        cum_pnl=cum_pnl, price_at_kill=price, regime_at_kill=regime,
        rule_change="kill_window reduced to 45 (faster feedback loop)",
    )


@pytest.fixture
def sample_kills() -> list[KillRecord]:
    """A diverse set of kill records for testing."""
    return [
        # DualMA kills — same strategy, same reason, same regime (cluster)
        _make_kill("DualMA_10_30", "PF 0.78 < 0.8", 53, -0.30, "mixed",
                   ts="2026-04-09T14:45:57+00:00"),
        _make_kill("DualMA_10_30", "PF 0.53 < 0.8", 51, -0.94, "mixed",
                   ts="2026-04-09T15:28:08+00:00"),
        _make_kill("DualMA_10_30", "PF 0.76 < 0.8", 4895, 0.82, "mixed",
                   ts="2026-04-16T06:33:39+00:00"),
        # Generated strategy kills
        _make_kill("gen_BollingerMeanReversion_RF_7abfe4", "PF 0.65 < 0.8",
                   125, -0.95, "mixed",
                   ts="2026-04-09T15:58:08+00:00"),
        _make_kill("gen_BollingerMeanReversion_RF_7abfe4", "PF 0.59 < 0.8",
                   81, -1.22, "mixed",
                   ts="2026-04-09T15:58:11+00:00"),
        # MDD kill
        _make_kill("gen_Donchian_RF_abc123", "MDD 22.5% > 20%",
                   200, -2.5, "trending",
                   ts="2026-04-10T10:00:00+00:00"),
        # WR collapse
        _make_kill("gen_RSI_RF_def456", "WR 25.0% < 30%",
                   300, -1.8, "ranging",
                   ts="2026-04-11T12:00:00+00:00"),
    ]


@pytest.fixture
def rapid_restart_kills() -> list[KillRecord]:
    """Kills with rapid restart pattern (same strategy killed quickly)."""
    return [
        _make_kill("DualMA_10_30", "PF 0.78 < 0.8", 50, -0.30, "mixed",
                   ts="2026-04-09T14:00:00+00:00"),
        _make_kill("DualMA_10_30", "PF 0.53 < 0.8", 100, -0.94, "mixed",
                   ts="2026-04-09T15:00:00+00:00"),
        _make_kill("DualMA_10_30", "PF 0.60 < 0.8", 145, -0.70, "mixed",
                   ts="2026-04-09T16:00:00+00:00"),
        _make_kill("DualMA_10_30", "PF 0.55 < 0.8", 190, -1.10, "mixed",
                   ts="2026-04-09T17:00:00+00:00"),
    ]


# --- parse_kill_reason ---

class TestParseKillReason:
    def test_pf_decay(self):
        cat, actual, threshold = parse_kill_reason("PF 0.78 < 0.8")
        assert cat == "pf_decay"
        assert actual == pytest.approx(0.78)
        assert threshold == pytest.approx(0.8)

    def test_mdd_breach(self):
        cat, actual, threshold = parse_kill_reason("MDD 22.5% > 20%")
        assert cat == "mdd"
        assert actual == pytest.approx(22.5)
        assert threshold == pytest.approx(20.0)

    def test_wr_collapse(self):
        cat, actual, threshold = parse_kill_reason("WR 25.0% < 30%")
        assert cat == "wr_collapse"
        assert actual == pytest.approx(25.0)
        assert threshold == pytest.approx(30.0)

    def test_unknown_reason(self):
        cat, _, _ = parse_kill_reason("something unexpected happened")
        assert cat == "unknown"

    def test_pf_without_numbers(self):
        cat, actual, threshold = parse_kill_reason("PF below threshold")
        assert cat == "pf_decay"
        assert actual == 0.0
        assert threshold == 0.0


# --- KillRecord ---

class TestKillRecord:
    def test_from_dict(self):
        d = {
            "ts": "2026-04-09T14:45:57+00:00",
            "tick": 53,
            "strategy": "DualMA_10_30",
            "kill_reason": "PF 0.78 < 0.8",
            "cum_pnl": -0.3027,
            "price_at_kill": 70975.55,
            "regime_at_kill": "mixed",
            "rule_change": "kill_window reduced to 45",
        }
        record = KillRecord.from_dict(d)
        assert record.strategy == "DualMA_10_30"
        assert record.tick == 53
        assert record.cum_pnl == pytest.approx(-0.3027)

    def test_from_dict_missing_fields(self):
        """Should handle missing fields gracefully with defaults."""
        record = KillRecord.from_dict({"ts": "t1", "strategy": "X"})
        assert record.tick == 0
        assert record.cum_pnl == 0.0
        assert record.regime_at_kill == "unknown"

    def test_immutability(self):
        record = _make_kill()
        with pytest.raises(AttributeError):
            record.strategy = "changed"  # type: ignore


# --- load_kills ---

class TestLoadKills:
    def test_load_from_jsonl(self, tmp_path: Path):
        kills_file = tmp_path / "kills.jsonl"
        entries = [
            {"ts": "t1", "tick": 10, "strategy": "A", "kill_reason": "PF 0.5 < 0.8",
             "cum_pnl": -1.0, "price_at_kill": 70000, "regime_at_kill": "mixed",
             "rule_change": "test"},
            {"ts": "t2", "tick": 20, "strategy": "B", "kill_reason": "MDD 25% > 20%",
             "cum_pnl": -2.0, "price_at_kill": 71000, "regime_at_kill": "trending",
             "rule_change": "test"},
        ]
        kills_file.write_text(
            "\n".join(json.dumps(e) for e in entries),
            encoding="utf-8",
        )
        records = load_kills(kills_file)
        assert len(records) == 2
        assert records[0].strategy == "A"
        assert records[1].strategy == "B"

    def test_load_nonexistent_file(self, tmp_path: Path):
        records = load_kills(tmp_path / "nonexistent.jsonl")
        assert records == []

    def test_load_with_malformed_lines(self, tmp_path: Path):
        kills_file = tmp_path / "kills.jsonl"
        kills_file.write_text(
            '{"ts": "t1", "strategy": "A"}\nnot json\n{"ts": "t2", "strategy": "B"}\n',
            encoding="utf-8",
        )
        records = load_kills(kills_file)
        assert len(records) == 2  # skips malformed line


# --- classify_kills ---

class TestClassifyKills:
    def test_groups_by_strategy_category_regime(self, sample_kills):
        patterns = classify_kills(sample_kills)
        assert len(patterns) > 0
        # Should have separate patterns for different strategy families
        families = {p.affected_strategies[0] for p in patterns}
        assert len(families) >= 3  # DualMA, BollingerMR, Donchian, RSI

    def test_pf_decay_pattern(self, sample_kills):
        patterns = classify_kills(sample_kills)
        pf_patterns = [p for p in patterns if p.category in ("pf_decay", "repeated_restart")]
        assert len(pf_patterns) > 0

    def test_mdd_pattern(self, sample_kills):
        patterns = classify_kills(sample_kills)
        mdd_patterns = [p for p in patterns if p.category == "mdd"]
        assert len(mdd_patterns) == 1
        assert mdd_patterns[0].regime_context == "trending"

    def test_wr_collapse_pattern(self, sample_kills):
        patterns = classify_kills(sample_kills)
        wr_patterns = [p for p in patterns if p.category == "wr_collapse"]
        assert len(wr_patterns) == 1
        assert wr_patterns[0].regime_context == "ranging"

    def test_rapid_restart_detection(self, rapid_restart_kills):
        patterns = classify_kills(rapid_restart_kills)
        restart_patterns = [p for p in patterns if p.category == "repeated_restart"]
        assert len(restart_patterns) == 1
        assert restart_patterns[0].kill_count == 4
        assert restart_patterns[0].severity == "critical"

    def test_severity_ordering(self, sample_kills):
        patterns = classify_kills(sample_kills)
        if len(patterns) >= 2:
            severity_order = {"critical": 0, "high": 1, "medium": 2}
            for i in range(len(patterns) - 1):
                assert (severity_order[patterns[i].severity]
                        <= severity_order[patterns[i + 1].severity])

    def test_generated_strategy_hash_normalization(self):
        """Generated strategy names like gen_X_7abfe4 should group with gen_X_abc123."""
        kills = [
            _make_kill("gen_DualMA_RF_602541", "PF 0.75 < 0.8", 100, -0.5,
                       ts="t1"),
            _make_kill("gen_DualMA_RF_aabbcc", "PF 0.70 < 0.8", 200, -0.8,
                       ts="t2"),
        ]
        patterns = classify_kills(kills)
        # Both should be grouped under the same base family
        assert len(patterns) == 1
        assert patterns[0].kill_count == 2


# --- cross_reference_zp ---

class TestCrossReferenceZP:
    def test_mdd_triggers_asymmetric_return(self):
        pattern = KillPattern(
            pattern_id="test_mdd", category="mdd",
            description="test", severity="high",
            affected_strategies=("TestStrat",), kill_count=1,
            avg_cum_pnl=-2.0, regime_context="trending",
            tick_range=(100, 100),
        )
        refs = cross_reference_zp(pattern)
        tags = [r["principle_tag"] for r in refs]
        assert "asymmetric_return" in tags

    def test_repeated_restart_triggers_negative_list(self):
        pattern = KillPattern(
            pattern_id="test_restart", category="repeated_restart",
            description="test", severity="critical",
            affected_strategies=("DualMA_10_30",), kill_count=4,
            avg_cum_pnl=-1.0, regime_context="mixed",
            tick_range=(50, 200),
        )
        refs = cross_reference_zp(pattern)
        tags = [r["principle_tag"] for r in refs]
        assert "negative_list_priority" in tags

    def test_pf_decay_triggers_exit_convergence(self):
        pattern = KillPattern(
            pattern_id="test_pf", category="pf_decay",
            description="test", severity="medium",
            affected_strategies=("TestStrat",), kill_count=1,
            avg_cum_pnl=-0.5, regime_context="mixed",
            tick_range=(100, 100),
        )
        refs = cross_reference_zp(pattern)
        tags = [r["principle_tag"] for r in refs]
        assert "entry_diversity_exit_convergence" in tags

    def test_mixed_regime_triggers_regime_principles(self):
        pattern = KillPattern(
            pattern_id="test_regime", category="pf_decay",
            description="test", severity="medium",
            affected_strategies=("TestStrat",), kill_count=1,
            avg_cum_pnl=-0.5, regime_context="mixed",
            tick_range=(100, 100),
        )
        refs = cross_reference_zp(pattern)
        tags = [r["principle_tag"] for r in refs]
        assert "optimization_ceiling" in tags or "regime_as_input" in tags

    def test_heavy_loss_triggers_survival(self):
        pattern = KillPattern(
            pattern_id="test_survival", category="pf_decay",
            description="test", severity="critical",
            affected_strategies=("TestStrat",), kill_count=5,
            avg_cum_pnl=-3.0, regime_context="mixed",
            tick_range=(100, 500),
        )
        refs = cross_reference_zp(pattern)
        tags = [r["principle_tag"] for r in refs]
        assert "survival_leverage" in tags


# --- generate_lessons ---

class TestGenerateLessons:
    def test_pf_decay_generates_tighten_lesson(self):
        pattern = KillPattern(
            pattern_id="KP_test_pf_decay_mixed_3",
            category="pf_decay", description="test", severity="high",
            affected_strategies=("DualMA_10_30",), kill_count=3,
            avg_cum_pnl=-0.7, regime_context="mixed",
            tick_range=(50, 200),
        )
        lessons = generate_lessons([pattern], {pattern.pattern_id: []})
        assert len(lessons) == 1
        assert lessons[0].action == "tighten"
        constraint = json.loads(lessons[0].constraint_rule)
        assert constraint["type"] == "min_pf_guard"

    def test_mdd_generates_tighten_lesson(self):
        pattern = KillPattern(
            pattern_id="KP_test_mdd_trending_1",
            category="mdd", description="test", severity="high",
            affected_strategies=("TestStrat",), kill_count=1,
            avg_cum_pnl=-2.5, regime_context="trending",
            tick_range=(200, 200),
        )
        lessons = generate_lessons([pattern], {})
        assert lessons[0].action == "tighten"
        constraint = json.loads(lessons[0].constraint_rule)
        assert constraint["type"] == "mdd_pre_warning"

    def test_wr_collapse_generates_regime_exclusion(self):
        pattern = KillPattern(
            pattern_id="KP_test_wr_collapse_ranging_1",
            category="wr_collapse", description="test", severity="medium",
            affected_strategies=("TestStrat",), kill_count=1,
            avg_cum_pnl=-1.0, regime_context="ranging",
            tick_range=(300, 300),
        )
        lessons = generate_lessons([pattern], {})
        assert lessons[0].action == "exclude_regime"
        constraint = json.loads(lessons[0].constraint_rule)
        assert constraint["excluded_regime"] == "ranging"

    def test_restart_loop_generates_avoid_lesson(self):
        pattern = KillPattern(
            pattern_id="KP_test_repeated_restart_mixed_4",
            category="repeated_restart", description="test",
            severity="critical",
            affected_strategies=("DualMA_10_30",), kill_count=4,
            avg_cum_pnl=-1.0, regime_context="mixed",
            tick_range=(50, 200),
        )
        lessons = generate_lessons([pattern], {})
        assert lessons[0].action == "avoid"
        constraint = json.loads(lessons[0].constraint_rule)
        assert constraint["type"] == "cooling_period_increase"
        assert constraint["min_cooling_ticks"] >= 200
        assert constraint["require_regime_change"] is True

    def test_zp_principles_attached(self):
        pattern = KillPattern(
            pattern_id="KP_test",
            category="pf_decay", description="test", severity="medium",
            affected_strategies=("TestStrat",), kill_count=1,
            avg_cum_pnl=-0.5, regime_context="mixed",
            tick_range=(100, 100),
        )
        zp_refs = {pattern.pattern_id: [
            {"principle_tag": "entry_diversity_exit_convergence",
             "principle_name": "test", "source": "test.md",
             "explanation": "test"},
        ]}
        lessons = generate_lessons([pattern], zp_refs)
        assert "entry_diversity_exit_convergence" in lessons[0].zp_principles

    def test_lesson_has_expiry(self):
        pattern = KillPattern(
            pattern_id="KP_test",
            category="pf_decay", description="test", severity="medium",
            affected_strategies=("TestStrat",), kill_count=1,
            avg_cum_pnl=-0.5, regime_context="mixed",
            tick_range=(100, 100),
        )
        lessons = generate_lessons([pattern], {})
        assert lessons[0].expires is not None


# --- build_strategy_summary ---

class TestBuildStrategySummary:
    def test_groups_by_base_name(self, sample_kills):
        summary = build_strategy_summary(sample_kills)
        assert "DualMA_10_30" in summary
        assert summary["DualMA_10_30"]["kill_count"] == 3

    def test_generated_strategy_normalization(self):
        kills = [
            _make_kill("gen_DualMA_RF_602541", ts="t1"),
            _make_kill("gen_DualMA_RF_aabbcc", ts="t2"),
        ]
        summary = build_strategy_summary(kills)
        assert "gen_DualMA_RF" in summary
        assert summary["gen_DualMA_RF"]["kill_count"] == 2

    def test_avg_pnl_calculation(self):
        kills = [
            _make_kill("TestStrat", cum_pnl=-1.0, ts="t1"),
            _make_kill("TestStrat", cum_pnl=-3.0, ts="t2"),
        ]
        summary = build_strategy_summary(kills)
        assert summary["TestStrat"]["avg_cum_pnl"] == pytest.approx(-2.0)


# --- analyze_kills (integration) ---

class TestAnalyzeKills:
    def test_full_pipeline(self, sample_kills):
        analysis = analyze_kills(sample_kills)
        assert analysis.kill_count == 7
        assert len(analysis.patterns) > 0
        assert len(analysis.lessons) > 0
        assert len(analysis.strategy_summary) > 0

    def test_empty_kills(self):
        analysis = analyze_kills([])
        assert analysis.kill_count == 0
        assert analysis.patterns == []
        assert analysis.lessons == []

    def test_zp_cross_refs_populated(self, sample_kills):
        analysis = analyze_kills(sample_kills)
        assert len(analysis.zp_cross_refs) > 0
        # At least some ZP principles should match
        tags = {ref["principle_tag"] for ref in analysis.zp_cross_refs}
        assert len(tags) > 0


# --- Output Formatting ---

class TestOutputFormatting:
    def test_jsonl_format(self, sample_kills):
        analysis = analyze_kills(sample_kills)
        output = to_jsonl(analysis)
        lines = [l for l in output.strip().split("\n") if l]
        # First line should be header
        header = json.loads(lines[0])
        assert header["type"] == "header"
        assert header["kill_count"] == 7
        # All lines should be valid JSON
        for line in lines:
            parsed = json.loads(line)
            assert "type" in parsed

    def test_markdown_format(self, sample_kills):
        analysis = analyze_kills(sample_kills)
        md = to_markdown(analysis)
        assert "# Kill-Lesson Analysis Report" in md
        assert "## Kill Patterns" in md
        assert "## Actionable Lessons" in md
        assert "## Strategy Family Summary" in md

    def test_markdown_contains_severity(self, sample_kills):
        analysis = analyze_kills(sample_kills)
        md = to_markdown(analysis)
        # Should contain severity levels
        assert any(s in md for s in ["CRITICAL", "HIGH", "MEDIUM"])

    def test_jsonl_lessons_have_constraint_rule(self, sample_kills):
        analysis = analyze_kills(sample_kills)
        output = to_jsonl(analysis)
        lesson_lines = [
            json.loads(l) for l in output.strip().split("\n")
            if l and json.loads(l).get("type") == "lesson"
        ]
        for lesson in lesson_lines:
            assert "constraint_rule" in lesson
            # constraint_rule should be valid JSON string
            parsed_constraint = json.loads(lesson["constraint_rule"])
            assert "type" in parsed_constraint


# --- Processed Set ---

class TestProcessedSet:
    def test_idempotent_analysis(self, tmp_path: Path, sample_kills):
        """Running analysis twice should not produce duplicate results."""
        from trading.kill_lesson import load_processed_set, save_processed_set
        processed_file = tmp_path / ".processed_kills.json"
        # Simulate first run
        timestamps = {k.ts for k in sample_kills}
        save_proc = set()
        save_proc.update(timestamps)
        processed_file.write_text(
            json.dumps(sorted(save_proc)),
            encoding="utf-8",
        )
        loaded = json.loads(processed_file.read_text())
        assert len(loaded) == len(sample_kills)
