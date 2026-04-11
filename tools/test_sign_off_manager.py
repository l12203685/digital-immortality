"""
Tests for tools/sign_off_manager.py

Stdlib-only — uses unittest + tmp dir monkey-patching.
Run: python -m tools.test_sign_off_manager
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path
from unittest import mock

from tools import sign_off_manager as som
from tools import escalation_batcher as eb

REPO_ROOT = Path(__file__).resolve().parent.parent


class SignOffManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "pending_sign_off.md"
        self.archive = Path(self.tmp.name) / "sign_off_archive.md"
        self._orig_pending = som.PENDING_PATH
        self._orig_archive = som.ARCHIVE_PATH
        som.PENDING_PATH = self.path
        som.ARCHIVE_PATH = self.archive

    def tearDown(self) -> None:
        som.PENDING_PATH = self._orig_pending
        som.ARCHIVE_PATH = self._orig_archive
        self.tmp.cleanup()

    # ----- add / parse --------------------------------------------------- #

    def test_add_and_parse_roundtrip(self) -> None:
        d = som.add_decision(
            title="Ratify SOP 123",
            recommendation="Ratify",
            why="Codifies lesson learned from cycle 341",
            alternatives=["reject", "defer"],
            impact=["new SOP", "memory update"],
            reversibility="high",
            path=self.path,
        )
        self.assertTrue(self.path.exists())
        parsed = som.list_pending(self.path)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0].uid, d.uid)
        self.assertEqual(parsed[0].title, "Ratify SOP 123")
        self.assertEqual(parsed[0].status, "PENDING")
        self.assertEqual(parsed[0].category, "AUTO")
        self.assertEqual(parsed[0].alternatives, ["reject", "defer"])
        self.assertEqual(parsed[0].impact, ["new SOP", "memory update"])
        self.assertEqual(parsed[0].reversibility, "high")

    def test_add_multiple_indices(self) -> None:
        som.add_decision(title="A", recommendation="R1", why="w", path=self.path)
        som.add_decision(title="B", recommendation="R2", why="w", path=self.path)
        text = self.path.read_text(encoding="utf-8")
        self.assertIn("## Decision 1: A", text)
        self.assertIn("## Decision 2: B", text)

    # ----- mark ---------------------------------------------------------- #

    def test_mark_decision_status(self) -> None:
        d = som.add_decision(title="T", recommendation="R", why="w", path=self.path)
        updated = som.mark_decision(d.uid, "APPROVED", who="edward", path=self.path)
        self.assertIsNotNone(updated)
        self.assertEqual(updated.status, "APPROVED")
        self.assertEqual(updated.resolved_by, "edward")
        reparsed = som.list_pending(self.path)[0]
        self.assertEqual(reparsed.status, "APPROVED")
        self.assertEqual(reparsed.resolved_by, "edward")

    def test_mark_nonexistent_uid(self) -> None:
        result = som.mark_decision("nope", "APPROVED", path=self.path)
        self.assertIsNone(result)

    # ----- auto-apply expired -------------------------------------------- #

    def test_auto_apply_expired(self) -> None:
        d = som.add_decision(title="Exp", recommendation="R", why="w",
                             default_hours=24, path=self.path)
        # Rewrite its auto-approve time to 1 hour in the past.
        past = som._now_taipei() - timedelta(hours=1)
        decisions = som.list_pending(self.path)
        decisions[0].auto_approve_at = som._iso(past)
        som._write_file(self.path, decisions)

        applied = som.auto_apply_expired(self.path)
        self.assertEqual(len(applied), 1)
        self.assertEqual(applied[0].uid, d.uid)
        reparsed = som.list_pending(self.path)[0]
        self.assertEqual(reparsed.status, "AUTO_APPLIED")
        self.assertEqual(reparsed.resolved_by, "agent:auto")

    def test_auto_apply_skips_escalate(self) -> None:
        som.add_decision(title="E", recommendation="R", why="w",
                         category="ESCALATE", path=self.path)
        # Force auto-approve time to past — escalate must still NOT be auto-applied.
        past = som._now_taipei() - timedelta(hours=1)
        decisions = som.list_pending(self.path)
        decisions[0].auto_approve_at = som._iso(past)
        som._write_file(self.path, decisions)

        applied = som.auto_apply_expired(self.path)
        self.assertEqual(len(applied), 0)
        reparsed = som.list_pending(self.path)[0]
        self.assertEqual(reparsed.status, "PENDING")
        self.assertEqual(reparsed.category, "ESCALATE")

    # ----- categorization validation ------------------------------------- #

    def test_invalid_category_raises(self) -> None:
        with self.assertRaises(ValueError):
            som.add_decision(title="x", recommendation="r", why="w",
                             category="WEIRD", path=self.path)

    def test_invalid_reversibility_raises(self) -> None:
        with self.assertRaises(ValueError):
            som.add_decision(title="x", recommendation="r", why="w",
                             reversibility="maybe", path=self.path)

    # ----- cleanup / archive --------------------------------------------- #

    def test_cleanup_archives_old_terminal(self) -> None:
        d = som.add_decision(title="Old", recommendation="R", why="w", path=self.path)
        som.mark_decision(d.uid, "APPROVED", path=self.path)
        # Backdate it 30 days.
        old = som._now_taipei() - timedelta(days=30)
        decisions = som.list_pending(self.path)
        decisions[0].posted = som._iso(old)
        som._write_file(self.path, decisions)

        archived = som.cleanup_old(days=14, path=self.path)
        self.assertEqual(len(archived), 1)
        self.assertEqual(som.list_pending(self.path), [])
        self.assertTrue(self.archive.exists())
        archived_parsed = som.list_pending(self.archive)
        self.assertEqual(len(archived_parsed), 1)
        self.assertEqual(archived_parsed[0].uid, d.uid)

    def test_cleanup_keeps_pending(self) -> None:
        som.add_decision(title="Fresh", recommendation="R", why="w", path=self.path)
        archived = som.cleanup_old(days=14, path=self.path)
        self.assertEqual(len(archived), 0)
        self.assertEqual(len(som.list_pending(self.path)), 1)

    # ----- CLI roundtrip ------------------------------------------------- #

    def test_cli_add_and_list(self) -> None:
        rc = som.main([
            "--add",
            "--title", "CLI decision",
            "--recommendation", "Do it",
            "--why", "Because it is reversible",
            "--reversibility", "high",
            "--category", "AUTO",
        ])
        self.assertEqual(rc, 0)
        parsed = som.list_pending(self.path)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0].title, "CLI decision")


class EscalationBatcherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "pending_sign_off.md"
        self.state_path = Path(self.tmp.name) / "escalation_state.json"
        self._orig_pending = som.PENDING_PATH
        self._orig_state = eb.STATE_PATH
        som.PENDING_PATH = self.path
        eb.STATE_PATH = self.state_path

    def tearDown(self) -> None:
        som.PENDING_PATH = self._orig_pending
        eb.STATE_PATH = self._orig_state
        self.tmp.cleanup()

    def test_filter_escalate_only(self) -> None:
        som.add_decision(title="Auto", recommendation="r", why="w",
                         category="AUTO", path=self.path)
        som.add_decision(title="Esc", recommendation="r", why="w",
                         category="ESCALATE", path=self.path)
        decisions = som.list_pending(self.path)
        filtered = eb.filter_escalate_pending(decisions)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].title, "Esc")

    def test_dry_run_no_post(self) -> None:
        som.add_decision(title="Strategic", recommendation="Proceed",
                         why="needs chairman decision",
                         category="ESCALATE", path=self.path)
        result = eb.run_once(cadence_hours=0, force=True, dry_run=True)
        self.assertEqual(result["items"], 1)
        self.assertFalse(result["sent"])
        self.assertIn("你有 1 件事要核章", result["message"])

    def test_no_items_returns_early(self) -> None:
        result = eb.run_once(cadence_hours=0, force=True, dry_run=True)
        self.assertEqual(result["items"], 0)
        self.assertFalse(result["sent"])
        self.assertEqual(result["reason"], "no-escalate-items")


if __name__ == "__main__":
    unittest.main(verbosity=2)
