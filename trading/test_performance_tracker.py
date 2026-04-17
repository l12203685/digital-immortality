"""Tests for trading.performance_tracker — rolling performance metrics."""
from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path
from typing import List

import pytest

from trading.performance_tracker import (
    PerformanceReport,
    StrategyMetrics,
    _pearson,
    build_report,
    compute_correlation_matrix,
    compute_edge_ratio,
    compute_max_drawdown,
    compute_profit_factor,
    compute_rolling_sharpe,
    compute_win_rate,
    extract_strategy_pnl,
    rank_strategies_by_risk_adjusted_return,
    report_to_json,
    report_to_markdown,
)


# ---------------------------------------------------------------------------
# compute_rolling_sharpe
# ---------------------------------------------------------------------------


class TestRollingSharpe:
    def test_empty_series(self) -> None:
        assert compute_rolling_sharpe([]) == 0.0

    def test_single_entry(self) -> None:
        assert compute_rolling_sharpe([1.0]) == 0.0

    def test_two_entries(self) -> None:
        result = compute_rolling_sharpe([1.0, 2.0])
        assert result != 0.0

    def test_constant_series_returns_zero(self) -> None:
        """Zero variance -> zero Sharpe."""
        assert compute_rolling_sharpe([1.0, 1.0, 1.0, 1.0]) == 0.0

    def test_window_limits_data(self) -> None:
        """Only last `window` entries are used."""
        long_series = [0.1] * 100 + [10.0, 10.0, 10.0]
        sharpe_3 = compute_rolling_sharpe(long_series, window=3)
        # With all 10.0 values and zero variance -> 0
        assert sharpe_3 == 0.0

    def test_positive_series_positive_sharpe(self) -> None:
        series = [0.5, 1.0, 0.8, 1.2, 0.9, 1.1, 0.7, 1.3, 0.6, 1.4]
        result = compute_rolling_sharpe(series, window=10)
        assert result > 0

    def test_negative_series_negative_sharpe(self) -> None:
        series = [-0.5, -1.0, -0.8, -1.2, -0.9]
        result = compute_rolling_sharpe(series, window=5)
        assert result < 0

    def test_default_window_is_20(self) -> None:
        series = list(range(1, 30))
        # Should use last 20 values
        sharpe_default = compute_rolling_sharpe(series)
        sharpe_20 = compute_rolling_sharpe(series, window=20)
        assert sharpe_default == sharpe_20


# ---------------------------------------------------------------------------
# compute_edge_ratio
# ---------------------------------------------------------------------------


class TestEdgeRatio:
    def test_empty_series(self) -> None:
        result = compute_edge_ratio([])
        assert result["edge_ratio"] == 0.0
        assert result["win_count"] == 0
        assert result["loss_count"] == 0

    def test_all_wins(self) -> None:
        # no losses -> raw_ratio=0, edge_ratio=0
        result = compute_edge_ratio([1.0, 2.0, 3.0])
        assert result["edge_ratio"] == 0.0
        assert result["raw_ratio"] == 0.0
        assert result["win_count"] == 3
        assert result["loss_count"] == 0

    def test_all_losses(self) -> None:
        # no wins -> edge_ratio=0
        result = compute_edge_ratio([-1.0, -2.0])
        assert result["edge_ratio"] == 0.0
        assert result["avg_win"] == 0.0

    def test_balanced(self) -> None:
        # [2.0, -1.0, 2.0, -1.0]: avg_win=2.0, avg_loss=1.0, win_rate=0.5
        # raw_ratio = 2.0, edge_ratio = 2.0 * 0.5 = 1.0
        result = compute_edge_ratio([2.0, -1.0, 2.0, -1.0])
        assert result["raw_ratio"] == 2.0
        assert result["edge_ratio"] == pytest.approx(1.0, abs=1e-6)
        assert result["avg_win"] == 2.0
        assert result["avg_loss"] == 1.0
        assert result["win_rate"] == 0.5

    def test_edge_ratio_includes_win_rate(self) -> None:
        # avg_win=3.0, avg_loss=1.0, win_rate=1/4=0.25
        # raw_ratio=3.0, edge_ratio=3.0*0.25=0.75
        result = compute_edge_ratio([3.0, -1.0, -1.0, -1.0])
        assert result["raw_ratio"] == pytest.approx(3.0, abs=1e-6)
        assert result["edge_ratio"] == pytest.approx(0.75, abs=1e-4)
        assert result["win_rate"] == pytest.approx(0.25, abs=1e-6)

    def test_positive_ev_above_one(self) -> None:
        # avg_win=4.0, avg_loss=1.0, win_rate=3/4=0.75 -> edge=3.0 (>1 = positive EV)
        result = compute_edge_ratio([4.0, 4.0, 4.0, -1.0])
        assert result["edge_ratio"] == pytest.approx(3.0, abs=1e-4)
        assert result["edge_ratio"] > 1.0

    def test_zeros_excluded_from_wins_and_losses(self) -> None:
        result = compute_edge_ratio([0.0, 0.0, 0.0])
        assert result["win_count"] == 0
        assert result["loss_count"] == 0
        assert result["edge_ratio"] == 0.0


# ---------------------------------------------------------------------------
# compute_win_rate
# ---------------------------------------------------------------------------


class TestWinRate:
    def test_empty(self) -> None:
        result = compute_win_rate([])
        assert result["cumulative"] == 0.0
        assert result["total_trades"] == 0

    def test_all_wins(self) -> None:
        result = compute_win_rate([1.0, 2.0, 3.0])
        assert result["cumulative"] == 1.0

    def test_all_losses(self) -> None:
        result = compute_win_rate([-1.0, -2.0])
        assert result["cumulative"] == 0.0

    def test_mixed(self) -> None:
        result = compute_win_rate([1.0, -1.0, 1.0, -1.0])
        assert result["cumulative"] == 0.5

    def test_rolling_window(self) -> None:
        series = [1.0, 1.0, 1.0, -1.0, -1.0]
        result = compute_win_rate(series, window=2)
        # Rolling: last 2 = [-1.0, -1.0] -> 0%
        assert result["rolling"] == 0.0
        # Cumulative: 3/5 = 0.6
        assert result["cumulative"] == 0.6

    def test_rolling_without_enough_data(self) -> None:
        result = compute_win_rate([1.0], window=20)
        # Fallback to cumulative
        assert result["rolling"] == result["cumulative"]


# ---------------------------------------------------------------------------
# compute_max_drawdown
# ---------------------------------------------------------------------------


class TestMaxDrawdown:
    def test_empty(self) -> None:
        result = compute_max_drawdown([])
        assert result["all_time"] == 0.0

    def test_monotonic_increase(self) -> None:
        result = compute_max_drawdown([1.0, 2.0, 3.0])
        assert result["all_time"] == 0.0

    def test_simple_drawdown(self) -> None:
        # cum: 10, 10-3=7 -> dd=3
        result = compute_max_drawdown([10.0, -3.0])
        assert result["all_time"] == 3.0

    def test_complex_drawdown(self) -> None:
        # cum: 5, 8, 3, 6, 1
        # peak: 5, 8, 8, 8, 8
        # dd:   0, 0, 5, 2, 7
        result = compute_max_drawdown([5.0, 3.0, -5.0, 3.0, -5.0])
        assert result["all_time"] == 7.0

    def test_rolling_window(self) -> None:
        series = [10.0, -5.0, -5.0, 1.0, 1.0]
        result = compute_max_drawdown(series, window=2)
        # Last 2: [1.0, 1.0] -> mdd=0
        assert result["rolling"] == 0.0
        # All-time: peak=10, then drops by 10 -> mdd=10
        assert result["all_time"] == 10.0


# ---------------------------------------------------------------------------
# compute_profit_factor
# ---------------------------------------------------------------------------


class TestProfitFactor:
    def test_empty(self) -> None:
        assert compute_profit_factor([]) == 0.0

    def test_no_losses(self) -> None:
        assert compute_profit_factor([1.0, 2.0]) == float("inf")

    def test_no_gains(self) -> None:
        assert compute_profit_factor([-1.0, -2.0]) == 0.0

    def test_equal_gains_losses(self) -> None:
        assert compute_profit_factor([2.0, -2.0]) == 1.0

    def test_profitable(self) -> None:
        # gross_profit=6, gross_loss=2 -> PF=3
        result = compute_profit_factor([3.0, -1.0, 3.0, -1.0])
        assert result == 3.0

    def test_zeros_dont_count(self) -> None:
        # Only 1.0 is profit, only -1.0 is loss
        result = compute_profit_factor([1.0, 0.0, -1.0, 0.0])
        assert result == 1.0


# ---------------------------------------------------------------------------
# compute_correlation_matrix
# ---------------------------------------------------------------------------


class TestCorrelationMatrix:
    def test_empty_input(self) -> None:
        assert compute_correlation_matrix({}) == {}

    def test_single_strategy(self) -> None:
        assert compute_correlation_matrix({"A": [1.0, 2.0, 3.0, 4.0, 5.0]}) == {}

    def test_too_few_data_points(self) -> None:
        result = compute_correlation_matrix({
            "A": [1.0, 2.0],
            "B": [1.0, 2.0],
        })
        assert result == {}

    def test_perfect_positive_correlation(self) -> None:
        result = compute_correlation_matrix({
            "A": [1.0, 2.0, 3.0, 4.0, 5.0],
            "B": [2.0, 4.0, 6.0, 8.0, 10.0],
        })
        assert abs(result["A"]["B"] - 1.0) < 0.001
        assert result["A"]["A"] == 1.0

    def test_perfect_negative_correlation(self) -> None:
        result = compute_correlation_matrix({
            "A": [1.0, 2.0, 3.0, 4.0, 5.0],
            "B": [-1.0, -2.0, -3.0, -4.0, -5.0],
        })
        assert abs(result["A"]["B"] - (-1.0)) < 0.001

    def test_perfectly_anti_alternating(self) -> None:
        """Alternating 1/0 vs 0/1 are perfectly negatively correlated."""
        result = compute_correlation_matrix({
            "A": [1.0, 0.0, 1.0, 0.0, 1.0],
            "B": [0.0, 1.0, 0.0, 1.0, 0.0],
        })
        assert abs(result["A"]["B"] - (-1.0)) < 0.001

    def test_three_strategies(self) -> None:
        result = compute_correlation_matrix({
            "A": [1.0, 2.0, 3.0, 4.0, 5.0],
            "B": [1.0, 2.0, 3.0, 4.0, 5.0],
            "C": [5.0, 4.0, 3.0, 2.0, 1.0],
        })
        assert len(result) == 3
        assert abs(result["A"]["B"] - 1.0) < 0.001
        assert abs(result["A"]["C"] - (-1.0)) < 0.001


# ---------------------------------------------------------------------------
# rank_strategies_by_risk_adjusted_return
# ---------------------------------------------------------------------------


class TestRankStrategies:
    def _pnl(self, wins: int, losses: int, win_size: float = 1.0, loss_size: float = 1.0) -> List[float]:
        return [win_size] * wins + [-loss_size] * losses

    def test_empty_input(self) -> None:
        assert rank_strategies_by_risk_adjusted_return({}) == []

    def test_single_strategy_insufficient_data(self) -> None:
        # Only 1 trade — excluded (< 2)
        result = rank_strategies_by_risk_adjusted_return({"A": [1.0]})
        assert result == []

    def test_single_strategy_enough_data(self) -> None:
        result = rank_strategies_by_risk_adjusted_return({"A": [1.0, -0.5, 1.0]})
        assert len(result) == 1
        assert result[0]["name"] == "A"
        assert result[0]["rank"] == 1
        assert "score" in result[0]

    def test_two_strategies_ranked_correctly(self) -> None:
        # A: high win rate + large wins → should rank above B
        pnl_a = [2.0, 2.0, 2.0, -0.5]   # win_rate=0.75, avg_win=2.0, avg_loss=0.5
        pnl_b = [-1.0, -1.0, -1.0, 0.5]  # win_rate=0.25, avg_win=0.5, avg_loss=1.0
        result = rank_strategies_by_risk_adjusted_return({"A": pnl_a, "B": pnl_b})
        assert len(result) == 2
        assert result[0]["name"] == "A"
        assert result[0]["rank"] == 1
        assert result[1]["rank"] == 2

    def test_score_between_0_and_1(self) -> None:
        pnls = {
            "A": [1.0, 1.0, -0.5, 1.0, 1.0],
            "B": [-0.5, -0.5, 1.0, -0.5, -0.5],
        }
        result = rank_strategies_by_risk_adjusted_return(pnls)
        for r in result:
            assert 0.0 <= r["score"] <= 1.0

    def test_rank_field_is_sequential(self) -> None:
        pnls = {
            f"S{i}": [1.0 * i, -0.5, 1.0, -0.3, 1.0]
            for i in range(1, 5)
        }
        result = rank_strategies_by_risk_adjusted_return(pnls)
        ranks = [r["rank"] for r in result]
        assert sorted(ranks) == list(range(1, len(pnls) + 1))

    def test_result_contains_required_fields(self) -> None:
        result = rank_strategies_by_risk_adjusted_return(
            {"X": [1.0, 1.0, -0.5, 1.0, -0.5]}
        )
        assert len(result) == 1
        r = result[0]
        for key in ("name", "rank", "score", "sharpe", "edge_ratio", "profit_factor",
                    "trade_count", "cum_pnl"):
            assert key in r, f"Missing field: {key}"

    def test_profit_factor_capped_at_10(self) -> None:
        # All wins → raw PF = inf, should be capped at 10.0 for normalization
        result = rank_strategies_by_risk_adjusted_return(
            {
                "AllWin": [1.0, 1.0, 1.0, 1.0, 1.0],
                "Mixed": [1.0, -0.5, 1.0, -0.5, 1.0],
            }
        )
        all_win = next(r for r in result if r["name"] == "AllWin")
        assert all_win["profit_factor"] <= 10.0


# ---------------------------------------------------------------------------
# _pearson
# ---------------------------------------------------------------------------


class TestPearson:
    def test_empty(self) -> None:
        assert _pearson([], []) == 0.0

    def test_single(self) -> None:
        assert _pearson([1.0], [1.0]) == 0.0

    def test_identical(self) -> None:
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        assert abs(_pearson(x, x) - 1.0) < 0.001

    def test_constant_series(self) -> None:
        assert _pearson([1.0, 1.0, 1.0], [1.0, 2.0, 3.0]) == 0.0


# ---------------------------------------------------------------------------
# extract_strategy_pnl
# ---------------------------------------------------------------------------


class TestExtractStrategyPnl:
    def test_empty(self) -> None:
        assert extract_strategy_pnl([]) == {}

    def test_single_strategy(self) -> None:
        entries = [
            {"strategy": "A", "pnl_pct": 1.0, "tick": 2},
            {"strategy": "A", "pnl_pct": -0.5, "tick": 1},
        ]
        result = extract_strategy_pnl(entries)
        assert list(result.keys()) == ["A"]
        # Sorted by tick
        assert result["A"] == [-0.5, 1.0]

    def test_multiple_strategies(self) -> None:
        entries = [
            {"strategy": "A", "pnl_pct": 1.0, "tick": 1},
            {"strategy": "B", "pnl_pct": -1.0, "tick": 1},
            {"strategy": "A", "pnl_pct": 2.0, "tick": 2},
        ]
        result = extract_strategy_pnl(entries)
        assert "A" in result
        assert "B" in result
        assert result["A"] == [1.0, 2.0]
        assert result["B"] == [-1.0]

    def test_missing_fields(self) -> None:
        entries = [
            {"strategy": "", "pnl_pct": 1.0, "tick": 1},  # empty name
            {"pnl_pct": 1.0, "tick": 1},  # no strategy key
        ]
        result = extract_strategy_pnl(entries)
        assert result == {}


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


class TestReportFormatters:
    def _sample_report(self) -> PerformanceReport:
        return PerformanceReport(
            generated_at="2026-04-16T10:00:00+08:00",
            strategy_metrics=[
                StrategyMetrics(
                    name="DualMA_10_30",
                    trade_count=50,
                    rolling_sharpe=1.5,
                    edge_ratio=0.99,
                    raw_ratio=1.8,
                    avg_win=0.02,
                    avg_loss=0.01,
                    win_rate_cumulative=0.55,
                    win_rate_rolling=0.60,
                    max_drawdown_all_time=5.0,
                    max_drawdown_rolling=3.0,
                    profit_factor=1.5,
                    cum_pnl=2.5,
                ),
            ],
            correlation_matrix={},
            aggregate={
                "total_trades": 50,
                "total_pnl": 2.5,
                "sharpe": 1.5,
                "win_rate": 0.55,
                "profit_factor": 1.5,
                "max_drawdown": 5.0,
            },
            kill_count=3,
        )

    def test_json_roundtrip(self) -> None:
        report = self._sample_report()
        json_str = report_to_json(report)
        data = json.loads(json_str)
        assert data["aggregate"]["total_pnl"] == 2.5
        assert len(data["strategies"]) == 1
        assert data["strategies"][0]["name"] == "DualMA_10_30"
        assert data["kill_count"] == 3

    def test_markdown_contains_key_sections(self) -> None:
        report = self._sample_report()
        md = report_to_markdown(report)
        assert "# B1 Trading Performance Report" in md
        assert "Aggregate Metrics" in md
        assert "Per-Strategy Metrics" in md
        assert "DualMA_10_30" in md
        assert "Kill events" in md

    def test_markdown_no_correlation_section_when_empty(self) -> None:
        report = self._sample_report()
        md = report_to_markdown(report)
        assert "Correlation Matrix" not in md

    def test_markdown_with_correlation(self) -> None:
        report = self._sample_report()
        # Replace correlation_matrix with data -- need mutable report
        report.correlation_matrix = {
            "A": {"A": 1.0, "B": 0.8},
            "B": {"A": 0.8, "B": 1.0},
        }
        md = report_to_markdown(report)
        assert "Correlation Matrix" in md
        assert "High Correlation Warnings" in md

    def test_markdown_contains_rankings_section(self) -> None:
        report = self._sample_report()
        report.strategy_rankings = [
            {
                "name": "DualMA_10_30", "rank": 1, "score": 0.85,
                "sharpe": 1.5, "edge_ratio": 0.99, "profit_factor": 1.5,
                "trade_count": 50, "cum_pnl": 2.5,
            }
        ]
        md = report_to_markdown(report)
        assert "Strategy Rankings" in md
        assert "Risk-Adjusted Return" in md
        assert "DualMA_10_30" in md

    def test_json_roundtrip_includes_rankings(self) -> None:
        report = self._sample_report()
        report.strategy_rankings = [
            {
                "name": "DualMA_10_30", "rank": 1, "score": 0.85,
                "sharpe": 1.5, "edge_ratio": 0.99, "profit_factor": 1.5,
                "trade_count": 50, "cum_pnl": 2.5,
            }
        ]
        data = json.loads(report_to_json(report))
        assert "strategy_rankings" in data
        assert data["strategy_rankings"][0]["rank"] == 1

    def test_json_handles_inf_profit_factor(self) -> None:
        report = PerformanceReport(
            generated_at="2026-04-16T10:00:00+08:00",
            strategy_metrics=[],
            aggregate={"profit_factor": float("inf")},
        )
        json_str = report_to_json(report)
        # Python json.dumps outputs Infinity (non-standard but round-trips)
        assert "Infinity" in json_str
        # Verify it round-trips
        data = json.loads(json_str)
        assert data["aggregate"]["profit_factor"] == float("inf")


# ---------------------------------------------------------------------------
# Integration: build_report with mock data
# ---------------------------------------------------------------------------


class TestBuildReportIntegration:
    def test_build_with_no_data(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """build_report returns empty report when no log files exist."""
        monkeypatch.setattr(
            "trading.performance_tracker.ENGINE_LOG",
            tmp_path / "nonexistent.jsonl",
        )
        monkeypatch.setattr(
            "trading.performance_tracker.KILLS_LOG",
            tmp_path / "nonexistent_kills.jsonl",
        )
        monkeypatch.setattr(
            "trading.performance_tracker.STATUS_PATH",
            tmp_path / "nonexistent_status.json",
        )

        report = build_report()
        assert report.strategy_metrics == []
        assert report.aggregate == {}
        assert report.kill_count == 0

    def test_build_with_mock_engine_log(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """build_report computes correct metrics from mock engine log."""
        log_path = tmp_path / "engine_log.jsonl"
        entries = [
            {"strategy": "TestStrat", "pnl_pct": 1.0, "tick": i}
            for i in range(1, 11)
        ] + [
            {"strategy": "TestStrat", "pnl_pct": -0.5, "tick": i}
            for i in range(11, 16)
        ]
        log_path.write_text(
            "\n".join(json.dumps(e) for e in entries),
            encoding="utf-8",
        )

        monkeypatch.setattr("trading.performance_tracker.ENGINE_LOG", log_path)
        monkeypatch.setattr(
            "trading.performance_tracker.KILLS_LOG",
            tmp_path / "kills.jsonl",
        )
        monkeypatch.setattr(
            "trading.performance_tracker.STATUS_PATH",
            tmp_path / "status.json",
        )

        report = build_report(sharpe_window=15)
        assert len(report.strategy_metrics) == 1

        m = report.strategy_metrics[0]
        assert m.name == "TestStrat"
        assert m.trade_count == 15
        assert m.win_rate_cumulative == pytest.approx(10 / 15, abs=0.01)
        # PF = 10.0 / 2.5 = 4.0
        assert m.profit_factor == pytest.approx(4.0, abs=0.01)
        # cum PnL = 10*1.0 + 5*(-0.5) = 7.5
        assert m.cum_pnl == pytest.approx(7.5, abs=0.01)

    def test_strategy_filter(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """build_report with strategy_filter only includes matching strategies."""
        log_path = tmp_path / "engine_log.jsonl"
        entries = [
            {"strategy": "DualMA", "pnl_pct": 1.0, "tick": 1},
            {"strategy": "Donchian", "pnl_pct": -1.0, "tick": 1},
        ]
        log_path.write_text(
            "\n".join(json.dumps(e) for e in entries),
            encoding="utf-8",
        )

        monkeypatch.setattr("trading.performance_tracker.ENGINE_LOG", log_path)
        monkeypatch.setattr(
            "trading.performance_tracker.KILLS_LOG",
            tmp_path / "kills.jsonl",
        )
        monkeypatch.setattr(
            "trading.performance_tracker.STATUS_PATH",
            tmp_path / "status.json",
        )

        report = build_report(strategy_filter="DualMA")
        assert len(report.strategy_metrics) == 1
        assert report.strategy_metrics[0].name == "DualMA"
