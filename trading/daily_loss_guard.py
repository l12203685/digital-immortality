"""
Daily Loss Guard — $5 hard cap + EMERGENCY_HALT mechanism.

Safety-critical module. When daily realized loss exceeds $5, creates
results/EMERGENCY_HALT and blocks all new trades for 24 hours.

Design principles:
    - Fail-safe: any error defaults to HALT (refuse to trade)
    - File-based: EMERGENCY_HALT is a plain file, survives restarts
    - Auto-resume: after 24h, the halt file is removed automatically
    - Idempotent: multiple calls to check/trigger are safe

Usage:
    from trading.daily_loss_guard import DailyLossGuard

    guard = DailyLossGuard(results_dir=Path("results"))
    if not guard.is_trading_allowed():
        return  # halted

    guard.record_loss(pnl_usd=-1.50, strategy="DualMA_10_30")
    # If cumulative daily loss exceeds $5, EMERGENCY_HALT is created automatically.
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger("trading.daily_loss_guard")

# Hard-coded safety constants — intentionally NOT configurable via files
# to prevent accidental loosening. Change requires a code commit.
DAILY_LOSS_CAP_USD: float = 5.0
HALT_DURATION_HOURS: int = 24

# Timezone for "daily" boundary (Taipei +08)
_TAIPEI = timezone(timedelta(hours=8))


@dataclass(frozen=True)
class HaltStatus:
    """Immutable snapshot of halt state."""
    is_halted: bool
    reason: str
    halted_at: Optional[str]  # ISO timestamp or None
    resumes_at: Optional[str]  # ISO timestamp or None
    daily_loss_usd: float
    remaining_budget_usd: float


def _taipei_today() -> str:
    """Return today's date string in Taipei timezone (YYYY-MM-DD)."""
    return datetime.now(_TAIPEI).strftime("%Y-%m-%d")


class DailyLossGuard:
    """Tracks daily realized PnL and enforces the $5 loss cap.

    All state is file-based under results_dir:
        EMERGENCY_HALT          — existence = trading blocked
        daily_loss_ledger.jsonl  — append-only ledger of realized PnL entries
    """

    def __init__(self, results_dir: Path) -> None:
        self._results = Path(results_dir)
        self._halt_path = self._results / "EMERGENCY_HALT"
        self._ledger_path = self._results / "daily_loss_ledger.jsonl"
        self._results.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_trading_allowed(self) -> bool:
        """Check if trading is allowed. Fail-safe: returns False on any error."""
        try:
            return not self._is_halted()
        except Exception as exc:
            logger.error(
                "FAIL-SAFE: error checking halt status (%s), defaulting to HALTED",
                exc,
            )
            return False

    def get_status(self) -> HaltStatus:
        """Return a detailed halt status snapshot."""
        try:
            halted = self._is_halted()
            halt_info = self._read_halt_file() if halted else None
            daily_loss = self._daily_loss_total()
            remaining = max(0.0, DAILY_LOSS_CAP_USD - abs(daily_loss))

            halted_at = halt_info.get("halted_at") if halt_info else None
            resumes_at = halt_info.get("resumes_at") if halt_info else None
            reason = halt_info.get("reason", "unknown") if halt_info else "not halted"

            return HaltStatus(
                is_halted=halted,
                reason=reason,
                halted_at=halted_at,
                resumes_at=resumes_at,
                daily_loss_usd=round(daily_loss, 4),
                remaining_budget_usd=round(remaining, 4),
            )
        except Exception as exc:
            logger.error("FAIL-SAFE: error getting status (%s)", exc)
            return HaltStatus(
                is_halted=True,
                reason=f"fail-safe: {exc}",
                halted_at=None,
                resumes_at=None,
                daily_loss_usd=0.0,
                remaining_budget_usd=0.0,
            )

    def record_pnl(self, pnl_usd: float, strategy: str,
                   trade_id: str = "") -> bool:
        """Record a realized PnL entry. Returns True if trading is still allowed.

        Automatically triggers EMERGENCY_HALT if cumulative daily loss exceeds cap.
        """
        try:
            entry = {
                "ts": datetime.now(_TAIPEI).isoformat(),
                "date": _taipei_today(),
                "strategy": strategy,
                "pnl_usd": round(pnl_usd, 6),
                "trade_id": trade_id,
            }
            self._append_ledger(entry)
            logger.info(
                "PnL recorded: strategy=%s pnl=%.4f USD trade_id=%s",
                strategy, pnl_usd, trade_id,
            )

            # Check if daily loss cap is breached
            daily_loss = self._daily_loss_total()
            if daily_loss < -DAILY_LOSS_CAP_USD:
                self._trigger_halt(
                    reason=(
                        f"Daily loss ${abs(daily_loss):.2f} exceeds "
                        f"${DAILY_LOSS_CAP_USD:.2f} cap"
                    ),
                    daily_loss=daily_loss,
                    trigger_strategy=strategy,
                    trigger_trade_id=trade_id,
                )
                return False
            return True
        except Exception as exc:
            logger.error(
                "FAIL-SAFE: error recording PnL (%s), triggering halt", exc,
            )
            self._trigger_halt(
                reason=f"fail-safe: error recording PnL — {exc}",
                daily_loss=0.0,
                trigger_strategy=strategy,
                trigger_trade_id=trade_id,
            )
            return False

    def force_halt(self, reason: str = "manual halt") -> None:
        """Manually trigger an emergency halt."""
        self._trigger_halt(
            reason=reason,
            daily_loss=self._daily_loss_total(),
            trigger_strategy="manual",
            trigger_trade_id="",
        )

    def force_resume(self) -> None:
        """Manually clear the halt (for admin override). Logged."""
        if self._halt_path.exists():
            logger.warning("MANUAL RESUME: EMERGENCY_HALT cleared by admin")
            self._halt_path.unlink()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _is_halted(self) -> bool:
        """Check if EMERGENCY_HALT file exists. Auto-resumes after 24h."""
        if not self._halt_path.exists():
            return False

        # Check if halt has expired (auto-resume)
        halt_info = self._read_halt_file()
        if halt_info is None:
            # File exists but unreadable — stay halted (fail-safe)
            logger.warning("EMERGENCY_HALT file exists but unreadable — staying halted")
            return True

        resumes_at_str = halt_info.get("resumes_at")
        if not resumes_at_str:
            # No resume time — stay halted (fail-safe)
            return True

        try:
            resumes_at = datetime.fromisoformat(resumes_at_str)
            now = datetime.now(_TAIPEI)
            if now >= resumes_at:
                logger.info(
                    "EMERGENCY_HALT expired (resumes_at=%s, now=%s). "
                    "Auto-resuming trading.",
                    resumes_at_str, now.isoformat(),
                )
                self._halt_path.unlink(missing_ok=True)
                return False
        except (ValueError, OSError) as exc:
            logger.warning("Error parsing resumes_at (%s) — staying halted", exc)
            return True

        return True

    def _read_halt_file(self) -> Optional[dict]:
        """Read and parse the EMERGENCY_HALT JSON file."""
        try:
            return json.loads(self._halt_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    def _trigger_halt(self, reason: str, daily_loss: float,
                      trigger_strategy: str, trigger_trade_id: str) -> None:
        """Create the EMERGENCY_HALT file."""
        now = datetime.now(_TAIPEI)
        resumes_at = now + timedelta(hours=HALT_DURATION_HOURS)

        halt_data = {
            "halted_at": now.isoformat(),
            "resumes_at": resumes_at.isoformat(),
            "reason": reason,
            "daily_loss_usd": round(daily_loss, 4),
            "cap_usd": DAILY_LOSS_CAP_USD,
            "trigger_strategy": trigger_strategy,
            "trigger_trade_id": trigger_trade_id,
            "halt_duration_hours": HALT_DURATION_HOURS,
        }

        self._halt_path.write_text(
            json.dumps(halt_data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        logger.critical(
            "EMERGENCY HALT TRIGGERED: %s | daily_loss=$%.2f | "
            "resumes_at=%s | strategy=%s",
            reason, abs(daily_loss), resumes_at.isoformat(),
            trigger_strategy,
        )

    def _append_ledger(self, entry: dict) -> None:
        """Append a single entry to the daily loss ledger."""
        with open(self._ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def _daily_loss_total(self) -> float:
        """Sum all PnL entries for today (Taipei time). Negative = loss."""
        today = _taipei_today()
        total = 0.0
        for entry in self._load_ledger():
            if entry.get("date") == today:
                total += entry.get("pnl_usd", 0.0)
        return total

    def _load_ledger(self) -> List[dict]:
        """Load all ledger entries."""
        if not self._ledger_path.exists():
            return []
        entries: List[dict] = []
        try:
            for line in self._ledger_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except OSError:
            pass
        return entries

    def daily_pnl_entries(self) -> List[dict]:
        """Return today's PnL entries (for status displays)."""
        today = _taipei_today()
        return [e for e in self._load_ledger() if e.get("date") == today]
