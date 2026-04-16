"""Tests for the daily loss guard / EMERGENCY_HALT mechanism.

Safety-critical: these tests verify the $5 daily loss cap, halt file
creation/expiry, fail-safe defaults, and auto-resume after 24h.
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from trading.daily_loss_guard import (
    DAILY_LOSS_CAP_USD,
    HALT_DURATION_HOURS,
    DailyLossGuard,
    HaltStatus,
    _taipei_today,
)


@pytest.fixture
def tmp_results(tmp_path: Path) -> Path:
    """Create a temporary results directory."""
    results = tmp_path / "results"
    results.mkdir()
    return results


@pytest.fixture
def guard(tmp_results: Path) -> DailyLossGuard:
    """Create a DailyLossGuard with a temporary results directory."""
    return DailyLossGuard(tmp_results)


class TestTradingAllowed:
    """Test is_trading_allowed() behavior."""

    def test_allowed_when_no_halt_file(self, guard: DailyLossGuard) -> None:
        assert guard.is_trading_allowed() is True

    def test_blocked_when_halt_file_exists(
        self, guard: DailyLossGuard, tmp_results: Path
    ) -> None:
        halt_path = tmp_results / "EMERGENCY_HALT"
        halt_data = {
            "halted_at": datetime.now(timezone.utc).isoformat(),
            "resumes_at": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
            "reason": "test halt",
        }
        halt_path.write_text(json.dumps(halt_data))
        assert guard.is_trading_allowed() is False

    def test_blocked_when_halt_file_corrupt(
        self, guard: DailyLossGuard, tmp_results: Path
    ) -> None:
        """Corrupt halt file = fail-safe = stay halted."""
        halt_path = tmp_results / "EMERGENCY_HALT"
        halt_path.write_text("not valid json {{{")
        assert guard.is_trading_allowed() is False

    def test_blocked_when_halt_file_empty(
        self, guard: DailyLossGuard, tmp_results: Path
    ) -> None:
        """Empty halt file = fail-safe = stay halted."""
        halt_path = tmp_results / "EMERGENCY_HALT"
        halt_path.write_text("")
        assert guard.is_trading_allowed() is False


class TestAutoResume:
    """Test 24-hour auto-resume behavior."""

    def test_auto_resumes_after_24h(
        self, guard: DailyLossGuard, tmp_results: Path
    ) -> None:
        halt_path = tmp_results / "EMERGENCY_HALT"
        past = datetime.now(timezone.utc) - timedelta(hours=25)
        halt_data = {
            "halted_at": past.isoformat(),
            "resumes_at": (past + timedelta(hours=24)).isoformat(),
            "reason": "expired halt",
        }
        halt_path.write_text(json.dumps(halt_data))
        assert guard.is_trading_allowed() is True
        # File should be removed after auto-resume
        assert not halt_path.exists()

    def test_stays_halted_before_24h(
        self, guard: DailyLossGuard, tmp_results: Path
    ) -> None:
        halt_path = tmp_results / "EMERGENCY_HALT"
        recent = datetime.now(timezone.utc) - timedelta(hours=1)
        halt_data = {
            "halted_at": recent.isoformat(),
            "resumes_at": (recent + timedelta(hours=24)).isoformat(),
            "reason": "recent halt",
        }
        halt_path.write_text(json.dumps(halt_data))
        assert guard.is_trading_allowed() is False

    def test_stays_halted_no_resumes_at(
        self, guard: DailyLossGuard, tmp_results: Path
    ) -> None:
        """Missing resumes_at = fail-safe = stay halted forever until manual clear."""
        halt_path = tmp_results / "EMERGENCY_HALT"
        halt_data = {
            "halted_at": datetime.now(timezone.utc).isoformat(),
            "reason": "no resume time",
        }
        halt_path.write_text(json.dumps(halt_data))
        assert guard.is_trading_allowed() is False


class TestRecordPnl:
    """Test PnL recording and daily loss cap triggering."""

    def test_small_loss_does_not_trigger(self, guard: DailyLossGuard) -> None:
        result = guard.record_pnl(pnl_usd=-1.0, strategy="test_strat")
        assert result is True
        assert guard.is_trading_allowed() is True

    def test_profit_does_not_trigger(self, guard: DailyLossGuard) -> None:
        result = guard.record_pnl(pnl_usd=10.0, strategy="test_strat")
        assert result is True

    def test_cumulative_loss_triggers_halt(
        self, guard: DailyLossGuard, tmp_results: Path
    ) -> None:
        # Record multiple small losses that sum to > $5
        guard.record_pnl(pnl_usd=-2.0, strategy="strat_a")
        guard.record_pnl(pnl_usd=-2.0, strategy="strat_b")
        result = guard.record_pnl(pnl_usd=-1.50, strategy="strat_a")
        assert result is False
        assert guard.is_trading_allowed() is False
        assert (tmp_results / "EMERGENCY_HALT").exists()

    def test_single_large_loss_triggers_halt(
        self, guard: DailyLossGuard, tmp_results: Path
    ) -> None:
        result = guard.record_pnl(pnl_usd=-6.0, strategy="big_loss_strat")
        assert result is False
        assert guard.is_trading_allowed() is False

    def test_profits_offset_losses(self, guard: DailyLossGuard) -> None:
        guard.record_pnl(pnl_usd=-4.0, strategy="strat_a")
        guard.record_pnl(pnl_usd=3.0, strategy="strat_b")
        # Net = -1.0, well within cap
        assert guard.is_trading_allowed() is True
        # Another loss bringing net to -4.0
        result = guard.record_pnl(pnl_usd=-3.0, strategy="strat_a")
        assert result is True
        assert guard.is_trading_allowed() is True

    def test_exact_cap_does_not_trigger(self, guard: DailyLossGuard) -> None:
        """Loss of exactly $5 does NOT trigger (only strictly exceeding)."""
        result = guard.record_pnl(pnl_usd=-5.0, strategy="strat")
        assert result is True
        assert guard.is_trading_allowed() is True

    def test_just_over_cap_triggers(self, guard: DailyLossGuard) -> None:
        guard.record_pnl(pnl_usd=-5.0, strategy="strat")
        result = guard.record_pnl(pnl_usd=-0.01, strategy="strat")
        assert result is False


class TestHaltStatus:
    """Test get_status() reporting."""

    def test_status_not_halted(self, guard: DailyLossGuard) -> None:
        status = guard.get_status()
        assert status.is_halted is False
        assert status.remaining_budget_usd == DAILY_LOSS_CAP_USD

    def test_status_after_loss(self, guard: DailyLossGuard) -> None:
        guard.record_pnl(pnl_usd=-2.0, strategy="strat")
        status = guard.get_status()
        assert status.daily_loss_usd == -2.0
        assert status.remaining_budget_usd == 3.0

    def test_status_after_halt(
        self, guard: DailyLossGuard, tmp_results: Path
    ) -> None:
        guard.record_pnl(pnl_usd=-6.0, strategy="strat")
        status = guard.get_status()
        assert status.is_halted is True
        assert "exceeds" in status.reason
        assert status.halted_at is not None
        assert status.resumes_at is not None


class TestHaltFileContents:
    """Test EMERGENCY_HALT file format and contents."""

    def test_halt_file_is_valid_json(
        self, guard: DailyLossGuard, tmp_results: Path
    ) -> None:
        guard.record_pnl(pnl_usd=-6.0, strategy="strat")
        halt_path = tmp_results / "EMERGENCY_HALT"
        data = json.loads(halt_path.read_text())
        assert "halted_at" in data
        assert "resumes_at" in data
        assert "reason" in data
        assert "daily_loss_usd" in data
        assert "cap_usd" in data
        assert data["cap_usd"] == DAILY_LOSS_CAP_USD
        assert data["halt_duration_hours"] == HALT_DURATION_HOURS

    def test_halt_file_has_trigger_info(
        self, guard: DailyLossGuard, tmp_results: Path
    ) -> None:
        guard.record_pnl(pnl_usd=-6.0, strategy="my_strat", trade_id="t123")
        data = json.loads((tmp_results / "EMERGENCY_HALT").read_text())
        assert data["trigger_strategy"] == "my_strat"
        assert data["trigger_trade_id"] == "t123"


class TestLedger:
    """Test the daily_loss_ledger.jsonl append-only log."""

    def test_ledger_records_entries(
        self, guard: DailyLossGuard, tmp_results: Path
    ) -> None:
        guard.record_pnl(pnl_usd=-1.0, strategy="s1")
        guard.record_pnl(pnl_usd=0.5, strategy="s2")
        ledger_path = tmp_results / "daily_loss_ledger.jsonl"
        assert ledger_path.exists()
        lines = ledger_path.read_text().strip().splitlines()
        assert len(lines) == 2
        entry = json.loads(lines[0])
        assert entry["pnl_usd"] == -1.0
        assert entry["strategy"] == "s1"
        assert "ts" in entry
        assert "date" in entry

    def test_daily_pnl_entries(self, guard: DailyLossGuard) -> None:
        guard.record_pnl(pnl_usd=-1.0, strategy="s1")
        guard.record_pnl(pnl_usd=2.0, strategy="s2")
        entries = guard.daily_pnl_entries()
        assert len(entries) == 2


class TestForceHaltResume:
    """Test manual halt/resume."""

    def test_force_halt(
        self, guard: DailyLossGuard, tmp_results: Path
    ) -> None:
        guard.force_halt(reason="manual test halt")
        assert guard.is_trading_allowed() is False
        data = json.loads((tmp_results / "EMERGENCY_HALT").read_text())
        assert data["reason"] == "manual test halt"

    def test_force_resume(
        self, guard: DailyLossGuard, tmp_results: Path
    ) -> None:
        guard.force_halt()
        assert guard.is_trading_allowed() is False
        guard.force_resume()
        assert guard.is_trading_allowed() is True


class TestFailSafe:
    """Test fail-safe behavior (errors default to halted)."""

    def test_is_trading_allowed_returns_false_on_error(
        self, tmp_results: Path
    ) -> None:
        """If internal check raises, default to blocked."""
        guard = DailyLossGuard(tmp_results)
        # Monkey-patch _is_halted to raise
        def _boom() -> bool:
            raise RuntimeError("disk error")
        guard._is_halted = _boom  # type: ignore[assignment]
        assert guard.is_trading_allowed() is False

    def test_get_status_returns_halted_on_error(
        self, tmp_results: Path
    ) -> None:
        guard = DailyLossGuard(tmp_results)
        def _boom() -> bool:
            raise RuntimeError("disk error")
        guard._is_halted = _boom  # type: ignore[assignment]
        status = guard.get_status()
        assert status.is_halted is True
        assert "fail-safe" in status.reason

    def test_record_pnl_triggers_halt_on_error(
        self, tmp_results: Path
    ) -> None:
        guard = DailyLossGuard(tmp_results)
        def _boom(entry: dict) -> None:
            raise IOError("write failed")
        guard._append_ledger = _boom  # type: ignore[assignment]
        result = guard.record_pnl(pnl_usd=-1.0, strategy="s")
        assert result is False
        assert guard.is_trading_allowed() is False


class TestConstants:
    """Verify safety constants are as documented."""

    def test_daily_loss_cap(self) -> None:
        assert DAILY_LOSS_CAP_USD == 5.0

    def test_halt_duration(self) -> None:
        assert HALT_DURATION_HOURS == 24
