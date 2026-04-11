"""Stdlib unit tests for tools.idle_task_picker.

Run:
    python -m tools.test_idle_task_picker
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Allow running as `python -m tools.test_idle_task_picker` from repo root.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.idle_task_picker import (  # noqa: E402
    BacklogTask,
    _classify_default,
    ensure_seen,
    enqueue_for_main_session,
    load_state,
    mark_attempt,
    parse_backlog,
    pick_next,
    save_state,
    score_all,
    score_task,
)


SYNTHETIC_BACKLOG = """# Agent Autonomous Backlog — test

## Branch 1: Trading
- State: paper-live
- Bottleneck: sop
- Tasks (EV-ranked):
  1. **[L] Wire ReactivationGate into engine.py** — doc exists, code missing.
     - Runnable by: daemon
     - Deps: none
  2. **[S] Add unit tests for kill_window floor logic** — test-only.
     - Runnable by: daemon

## Branch 2: DNA
- State: 431 MDs
- Bottleneck: plateau
- Tasks (EV-ranked):
  1. **[M] Deep-pass re-extraction of 201708** — semantic deep-pass yields MDs.
     - Runnable by: main_session_subagent
  2. **[S] Auto-detect MD contradictions** — static analysis only.
     - Runnable by: daemon

## Cross-cutting tasks (span multiple branches)

1. **[L] Build tools/idle_task_picker.py** — ignored, not in branch section.
"""


class ParseTests(unittest.TestCase):
    def _write_backlog(self, content: str) -> Path:
        tmp = Path(tempfile.mkdtemp()) / "backlog.md"
        tmp.write_text(content, encoding="utf-8")
        return tmp

    def test_parse_backlog_basic(self):
        path = self._write_backlog(SYNTHETIC_BACKLOG)
        tasks = parse_backlog(path)
        ids = [t.task_id for t in tasks]
        self.assertEqual(ids, ["B1.T1", "B1.T2", "B2.T1", "B2.T2"])

    def test_parse_respects_runnable_tag(self):
        path = self._write_backlog(SYNTHETIC_BACKLOG)
        tasks = {t.task_id: t for t in parse_backlog(path)}
        self.assertEqual(tasks["B1.T1"].runnable_by, "daemon")
        self.assertEqual(tasks["B2.T1"].runnable_by, "main_session_subagent")
        self.assertEqual(tasks["B1.T1"].complexity, "L")
        self.assertEqual(tasks["B2.T2"].complexity, "S")

    def test_parse_excludes_cross_cutting(self):
        path = self._write_backlog(SYNTHETIC_BACKLOG)
        tasks = parse_backlog(path)
        # Cross-cutting section should NOT be parsed as tasks (no branch header).
        self.assertFalse(any("idle_task_picker" in t.title for t in tasks))

    def test_classify_default_daemon_keywords(self):
        self.assertEqual(
            _classify_default("Build `tools/foo.py`", "local compute only"),
            "daemon",
        )
        self.assertEqual(
            _classify_default("Audit dna_core for drift", "needs llm reasoning"),
            "main_session_subagent",
        )
        self.assertEqual(
            _classify_default("Send Samuel DM", "human-gated"),
            "human",
        )


class ScoringTests(unittest.TestCase):
    def _tasks(self) -> list[BacklogTask]:
        return [
            BacklogTask(1, "Trading", "B1.T1", "S", "quick task", "", (), "daemon"),
            BacklogTask(1, "Trading", "B1.T2", "L", "hard task", "", (), "daemon"),
            BacklogTask(2, "DNA", "B2.T1", "M", "extract", "", (), "main_session_subagent"),
        ]

    def test_never_attempted_scores_higher_than_recent_failure(self):
        now = datetime.now(timezone.utc)
        tasks = self._tasks()
        # Fresh state: B1.T1 recently FAILED
        state: dict = {}
        state = mark_attempt(
            state, "B1.T1", "failure", "boom", now=now - timedelta(minutes=10)
        )
        state = ensure_seen(state, tasks, now=now)
        s_failed = score_task(tasks[0], state, now)
        s_fresh = score_task(tasks[1], state, now)  # L but never attempted
        self.assertLess(s_failed, s_fresh + 5.0)  # cooldown hurts failed task
        self.assertGreater(s_fresh, s_failed)

    def test_failure_cooldown_recovers_over_time(self):
        now = datetime.now(timezone.utc)
        tasks = self._tasks()
        fresh_state = ensure_seen({}, tasks, now=now)
        recent_fail = mark_attempt(
            fresh_state, "B1.T1", "failure", "x", now=now - timedelta(minutes=5)
        )
        old_fail = mark_attempt(
            fresh_state, "B1.T1", "failure", "x", now=now - timedelta(hours=48)
        )
        s_recent = score_task(tasks[0], recent_fail, now)
        s_old = score_task(tasks[0], old_fail, now)
        self.assertGreater(s_old, s_recent)

    def test_pick_next_respects_runnable_filter(self):
        now = datetime.now(timezone.utc)
        tasks = self._tasks()
        state = ensure_seen({}, tasks, now=now)
        picked = pick_next(tasks, state, now, runnable_filter="daemon")
        self.assertIsNotNone(picked)
        self.assertEqual(picked.runnable_by, "daemon")
        # Highest-EV daemon task: B1.T1 is S + rank T1 → beats L B1.T2
        self.assertEqual(picked.task_id, "B1.T1")

    def test_pick_next_subagent_filter(self):
        now = datetime.now(timezone.utc)
        tasks = self._tasks()
        state = ensure_seen({}, tasks, now=now)
        picked = pick_next(tasks, state, now, runnable_filter="main_session_subagent")
        self.assertEqual(picked.task_id, "B2.T1")

    def test_pick_next_returns_none_when_filter_empty(self):
        now = datetime.now(timezone.utc)
        tasks = self._tasks()
        state = ensure_seen({}, tasks, now=now)
        picked = pick_next(tasks, state, now, runnable_filter="human")
        self.assertIsNone(picked)

    def test_starvation_aging_lets_old_l_tasks_eventually_win(self):
        # Two L daemon tasks both never-attempted; the older-seen one wins.
        now = datetime.now(timezone.utc)
        tasks = [
            BacklogTask(1, "A", "B1.T1", "L", "old", "", (), "daemon"),
            BacklogTask(1, "A", "B1.T2", "L", "new", "", (), "daemon"),
        ]
        # Seed state: B1.T1 first-seen 30 days ago
        state: dict = {}
        long_ago = (now - timedelta(days=30)).isoformat()
        from tools.idle_task_picker import TaskState
        state["B1.T1"] = TaskState(task_id="B1.T1", first_seen_iso=long_ago)
        state["B1.T2"] = TaskState(task_id="B1.T2", first_seen_iso=now.isoformat())
        s_old = score_task(tasks[0], state, now)
        s_new = score_task(tasks[1], state, now)
        self.assertGreater(s_old, s_new)


class StateTests(unittest.TestCase):
    def test_mark_and_save_roundtrip(self):
        tmp = Path(tempfile.mkdtemp()) / "state.json"
        now = datetime.now(timezone.utc)
        state: dict = {}
        state = mark_attempt(state, "B1.T1", "success", "ok", now=now)
        state = mark_attempt(state, "B1.T1", "failure", "oops", now=now)
        save_state(state, tmp)
        loaded = load_state(tmp)
        self.assertIn("B1.T1", loaded)
        self.assertEqual(loaded["B1.T1"].attempts, 2)
        self.assertEqual(loaded["B1.T1"].successes, 1)
        self.assertEqual(loaded["B1.T1"].failures, 1)
        self.assertEqual(loaded["B1.T1"].last_status, "failure")

    def test_mark_attempt_is_immutable_returns_new(self):
        now = datetime.now(timezone.utc)
        original: dict = {}
        new = mark_attempt(original, "B1.T1", "success", "x", now=now)
        self.assertNotIn("B1.T1", original)
        self.assertIn("B1.T1", new)

    def test_load_state_handles_missing_file(self):
        tmp = Path(tempfile.mkdtemp()) / "missing.json"
        self.assertEqual(load_state(tmp), {})

    def test_load_state_handles_corrupt_file(self):
        tmp = Path(tempfile.mkdtemp()) / "bad.json"
        tmp.write_text("not-json{", encoding="utf-8")
        self.assertEqual(load_state(tmp), {})


class QueueTests(unittest.TestCase):
    def test_enqueue_appends_jsonl(self):
        tmp = Path(tempfile.mkdtemp()) / "queue.jsonl"
        task = BacklogTask(1, "A", "B1.T1", "S", "hello", "why", (), "daemon")
        enqueue_for_main_session(task, queue_path=tmp)
        enqueue_for_main_session(task, queue_path=tmp)
        lines = tmp.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(lines), 2)
        parsed = json.loads(lines[0])
        self.assertEqual(parsed["task_id"], "B1.T1")
        self.assertEqual(parsed["runnable_by"], "daemon")


class IntegrationTests(unittest.TestCase):
    def test_score_all_real_backlog_if_present(self):
        """Smoke-test against the real backlog file if it exists."""
        real = Path("C:/Users/admin/staging/agent_autonomous_backlog.md")
        if not real.exists():
            self.skipTest("real backlog file not present")
        tasks = parse_backlog(real)
        self.assertGreater(len(tasks), 20)
        now = datetime.now(timezone.utc)
        state = ensure_seen({}, tasks, now=now)
        scored = score_all(tasks, state, now)
        self.assertEqual(len(scored), len(tasks))
        # Top task must have a positive score.
        self.assertGreater(scored[0][0], 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
