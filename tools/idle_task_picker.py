"""Idle Task Picker — self-dispatch from the autonomous backlog.

Eliminates the "wait for Edward" failure mode by parsing the backlog file,
scoring tasks by EV + retry cool-down + starvation guard, and returning the
next runnable task. The recursive daemon calls this at the end of each cycle
to pick work when no human-injected priority is present.

CLI:
    python -m tools.idle_task_picker --pick
    python -m tools.idle_task_picker --pick --runnable daemon
    python -m tools.idle_task_picker --list
    python -m tools.idle_task_picker --mark B1.T1 success "wired gate"

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BACKLOG = Path("C:/Users/admin/staging/agent_autonomous_backlog.md")
DEFAULT_STATE = REPO_ROOT / "results" / "idle_task_picker_state.json"
DEFAULT_QUEUE = REPO_ROOT / "results" / "picker_queue.jsonl"

COMPLEXITY_WEIGHT = {"S": 3.0, "M": 2.0, "L": 1.0}
# Exponential cool-down half-life in hours after a failure.
FAILURE_HALF_LIFE_HOURS = 6.0
# Starvation aging: tasks never attempted get a small bonus per day since
# the picker first saw them, so even L tasks eventually get tried.
AGING_BONUS_PER_DAY = 0.05
# Max retry count before a task is de-prioritized heavily.
RETRY_PENALTY = 0.5


@dataclass(frozen=True)
class BacklogTask:
    """A single parsed backlog entry."""

    branch: int
    branch_name: str
    task_id: str  # e.g. "B1.T1"
    complexity: str  # "S" | "M" | "L"
    title: str
    why_autonomous: str
    deps: tuple[str, ...]
    runnable_by: str  # "daemon" | "main_session_subagent" | "human"

    def to_dict(self) -> dict:
        return {
            "branch": self.branch,
            "branch_name": self.branch_name,
            "task_id": self.task_id,
            "complexity": self.complexity,
            "title": self.title,
            "why_autonomous": self.why_autonomous,
            "deps": list(self.deps),
            "runnable_by": self.runnable_by,
        }


@dataclass
class TaskState:
    """Mutable attempt-tracking state for a single task."""

    task_id: str
    attempts: int = 0
    successes: int = 0
    failures: int = 0
    last_attempt_iso: Optional[str] = None
    last_status: Optional[str] = None  # "success" | "failure" | "queued"
    last_message: Optional[str] = None
    first_seen_iso: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "TaskState":
        return cls(**{k: data.get(k) for k in cls.__dataclass_fields__})


# Parsing ------------------------------------------------------------------

_BRANCH_HEADER_RE = re.compile(r"^## Branch\s+(\d+):\s*(.+?)\s*$")
_TASK_HEADER_RE = re.compile(
    r"^\s*(\d+)\.\s*\*\*\[(S|M|L)\]\s*(.+?)\*\*\s*(?:—|--)?\s*(.*)$"
)
_RUNNABLE_RE = re.compile(
    r"(?i)^\s*-?\s*Runnable by:\s*(daemon|main_session_subagent|human)\s*$"
)
_DEPS_RE = re.compile(r"(?i)deps?\s*[:\-]\s*(.+)$")


def _classify_default(title: str, why_autonomous: str) -> str:
    """Heuristic runnable_by classification for tasks without explicit tag.

    Daemon can run: file edits, git operations, local scripts, test runs,
    data extraction from local files, JSON updates.

    Main session subagent needed: anything that requires LLM reasoning beyond
    mechanical transforms — audits, draft writing, semantic analysis.

    Human needed: send DMs, post to X, provision secrets.
    """
    title_l = title.lower()
    why_l = why_autonomous.lower()
    text = f"{title_l} {why_l}"

    human_markers = (
        "send dm", "samuel dm", "outreach dm", "post on x", "post sop",
        "mainnet key", "provision", "human-send", "edward sends",
    )
    if any(m in text for m in human_markers):
        return "human"

    # Daemon markers checked FIRST — mechanical file/git/script operations
    # that can run without LLM reasoning.
    daemon_markers = (
        "append ", "build `tools/", "build `platform/", "wire `",
        "add unit tests", "add `tests/", "file-append", "git push",
        "auto-generate", "run `", "regenerate", "pre-commit", "append line",
        "file edit", "static analysis", "checksum", "pure file-diff",
        "file parse only", "file i/o", "sandbox branch", "code + tests",
        "file existence", "test-only",
    )
    if any(m in text for m in daemon_markers):
        return "daemon"

    # Subagent markers — tasks needing LLM reasoning beyond mechanics.
    subagent_markers = (
        "draft sop", "draft ", "design ", "re-run cycle", "llm",
        "propose ", "evaluation", "pre-generate edward-side",
        "chaos-engineering", "semantic-dedupe", "deep-pass",
        "scenario bank expansion", "cross-instance",
    )
    if any(m in text for m in subagent_markers):
        return "main_session_subagent"

    # Default conservative: subagent (needs reasoning)
    return "main_session_subagent"


def parse_backlog(path: Path) -> list[BacklogTask]:
    """Parse the autonomous backlog markdown into BacklogTask records.

    Robust to both the pre-enrichment format (no runnable_by tag) and the
    enriched format where tasks have a "Runnable by: <role>" sub-bullet.
    """
    if not path.exists():
        return []

    lines = path.read_text(encoding="utf-8").splitlines()
    tasks: list[BacklogTask] = []
    current_branch: Optional[int] = None
    current_branch_name: str = ""
    current_task: Optional[dict] = None
    in_tasks_section = False

    def flush() -> None:
        nonlocal current_task
        if current_task is None or current_branch is None:
            current_task = None
            return
        task_id = f"B{current_branch}.T{current_task['idx']}"
        runnable = current_task.get("runnable_by") or _classify_default(
            current_task["title"], current_task.get("why_autonomous", "")
        )
        tasks.append(
            BacklogTask(
                branch=current_branch,
                branch_name=current_branch_name,
                task_id=task_id,
                complexity=current_task["complexity"],
                title=current_task["title"].strip(),
                why_autonomous=current_task.get("why_autonomous", "").strip(),
                deps=tuple(current_task.get("deps", [])),
                runnable_by=runnable,
            )
        )
        current_task = None

    for raw in lines:
        line = raw.rstrip()
        branch_match = _BRANCH_HEADER_RE.match(line)
        if branch_match:
            flush()
            current_branch = int(branch_match.group(1))
            current_branch_name = branch_match.group(2).strip()
            in_tasks_section = False
            continue

        if line.startswith("## ") and not branch_match:
            # Non-branch H2 (e.g., cross-cutting, anti-tasks) — stop collecting.
            flush()
            current_branch = None
            in_tasks_section = False
            continue

        if "Tasks (EV-ranked)" in line:
            in_tasks_section = True
            continue

        if not in_tasks_section or current_branch is None:
            continue

        task_match = _TASK_HEADER_RE.match(line)
        if task_match:
            flush()
            idx = int(task_match.group(1))
            complexity = task_match.group(2)
            title = task_match.group(3)
            why = task_match.group(4) or ""
            current_task = {
                "idx": idx,
                "complexity": complexity,
                "title": title,
                "why_autonomous": why,
                "deps": [],
                "runnable_by": None,
            }
            continue

        if current_task is None:
            continue

        runnable_match = _RUNNABLE_RE.match(line)
        if runnable_match:
            current_task["runnable_by"] = runnable_match.group(1).lower()
            continue

        deps_match = _DEPS_RE.search(line)
        if deps_match:
            deps_text = deps_match.group(1).strip().rstrip(".")
            current_task["deps"] = [d.strip() for d in deps_text.split(",") if d.strip()]
            continue

        # Continuation text — append to why_autonomous
        stripped = line.strip().lstrip("-").strip()
        if stripped:
            current_task["why_autonomous"] += " " + stripped

    flush()
    return tasks


# State --------------------------------------------------------------------


def load_state(state_path: Path) -> dict[str, TaskState]:
    if not state_path.exists():
        return {}
    try:
        raw = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    out: dict[str, TaskState] = {}
    for task_id, data in raw.items():
        if isinstance(data, dict):
            out[task_id] = TaskState.from_dict({"task_id": task_id, **data})
    return out


def save_state(state: dict[str, TaskState], state_path: Path) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    serializable = {tid: ts.to_dict() for tid, ts in state.items()}
    # Drop task_id key from value since it's the dict key already.
    for v in serializable.values():
        v.pop("task_id", None)
    state_path.write_text(
        json.dumps(serializable, indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )


def mark_attempt(
    state: dict[str, TaskState],
    task_id: str,
    status: str,
    message: str,
    now: Optional[datetime] = None,
) -> dict[str, TaskState]:
    """Record an attempt. Returns a NEW state dict (immutable update)."""
    now = now or datetime.now(timezone.utc)
    iso = now.isoformat()
    new_state = dict(state)
    existing = new_state.get(task_id)
    if existing is None:
        record = TaskState(
            task_id=task_id,
            attempts=1,
            successes=1 if status == "success" else 0,
            failures=1 if status == "failure" else 0,
            last_attempt_iso=iso,
            last_status=status,
            last_message=message,
            first_seen_iso=iso,
        )
    else:
        record = TaskState(
            task_id=task_id,
            attempts=existing.attempts + 1,
            successes=existing.successes + (1 if status == "success" else 0),
            failures=existing.failures + (1 if status == "failure" else 0),
            last_attempt_iso=iso,
            last_status=status,
            last_message=message,
            first_seen_iso=existing.first_seen_iso or iso,
        )
    new_state[task_id] = record
    return new_state


def ensure_seen(
    state: dict[str, TaskState],
    tasks: list[BacklogTask],
    now: Optional[datetime] = None,
) -> dict[str, TaskState]:
    """Stamp first_seen_iso for tasks the picker hasn't recorded yet."""
    now = now or datetime.now(timezone.utc)
    iso = now.isoformat()
    new_state = dict(state)
    for task in tasks:
        if task.task_id not in new_state:
            new_state[task.task_id] = TaskState(
                task_id=task.task_id, first_seen_iso=iso
            )
    return new_state


# Scoring ------------------------------------------------------------------


def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def score_task(
    task: BacklogTask,
    state: dict[str, TaskState],
    now: datetime,
) -> float:
    """Compute the EV score for a task.

    Higher is better. Components:
    - Base: complexity weight (S > M > L) × branch EV proxy (earlier task = higher)
    - Never-attempted bonus: +1.0
    - Failure cool-down: exponential decay since last failure
    - Retry penalty: linear in attempts
    - Starvation aging: +AGING_BONUS_PER_DAY × days since first_seen
    """
    base = COMPLEXITY_WEIGHT.get(task.complexity, 1.0)

    # Earlier tasks (T1) in each branch are the backlog's EV rank — amplify.
    try:
        rank = int(task.task_id.split(".T")[1])
    except (IndexError, ValueError):
        rank = 99
    rank_bonus = max(0.0, 1.5 - 0.2 * (rank - 1))  # T1=+1.5, T5=+0.7

    ts = state.get(task.task_id)
    if ts is None or ts.attempts == 0:
        never_bonus = 1.0
        cooldown = 0.0
        retry_penalty = 0.0
        aging = 0.0
    else:
        never_bonus = 0.0
        retry_penalty = RETRY_PENALTY * ts.attempts

        last_dt = _parse_iso(ts.last_attempt_iso)
        if ts.last_status == "failure" and last_dt is not None:
            hours_since = max(0.0, (now - last_dt).total_seconds() / 3600.0)
            # Decay: starts at -2.0, exponentially returns toward 0.
            cooldown = -2.0 * math.exp(-hours_since / FAILURE_HALF_LIFE_HOURS)
        elif ts.last_status == "success":
            # Recent success: de-prioritize briefly (don't re-run same task).
            last_dt = _parse_iso(ts.last_attempt_iso)
            if last_dt is not None:
                hours_since = max(0.0, (now - last_dt).total_seconds() / 3600.0)
                cooldown = -3.0 * math.exp(-hours_since / 24.0)
            else:
                cooldown = 0.0
        else:
            cooldown = 0.0

        first_dt = _parse_iso(ts.first_seen_iso)
        if first_dt is not None:
            days_since = max(0.0, (now - first_dt).total_seconds() / 86400.0)
            aging = AGING_BONUS_PER_DAY * days_since
        else:
            aging = 0.0

    return base + rank_bonus + never_bonus + cooldown + aging - retry_penalty


def pick_next(
    tasks: list[BacklogTask],
    state: dict[str, TaskState],
    now: datetime,
    runnable_filter: str = "daemon",
) -> Optional[BacklogTask]:
    """Pick the highest-scoring runnable task matching the filter.

    runnable_filter: "daemon" | "main_session_subagent" | "any"
    """
    candidates = [
        t for t in tasks
        if runnable_filter == "any" or t.runnable_by == runnable_filter
    ]
    if not candidates:
        return None
    scored = [(score_task(t, state, now), t) for t in candidates]
    scored.sort(key=lambda x: (-x[0], x[1].task_id))
    return scored[0][1]


def score_all(
    tasks: list[BacklogTask],
    state: dict[str, TaskState],
    now: datetime,
) -> list[tuple[float, BacklogTask]]:
    scored = [(score_task(t, state, now), t) for t in tasks]
    scored.sort(key=lambda x: (-x[0], x[1].task_id))
    return scored


# Queue file ---------------------------------------------------------------


def enqueue_for_main_session(
    task: BacklogTask,
    queue_path: Path = DEFAULT_QUEUE,
    now: Optional[datetime] = None,
) -> None:
    """Log a picked task to the JSONL queue file for main session pickup."""
    now = now or datetime.now(timezone.utc)
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": now.isoformat(),
        "task_id": task.task_id,
        "branch": task.branch,
        "branch_name": task.branch_name,
        "complexity": task.complexity,
        "title": task.title,
        "runnable_by": task.runnable_by,
    }
    with queue_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# CLI ----------------------------------------------------------------------


def _cli(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="idle_task_picker",
        description="Self-derive next agent task from the autonomous backlog.",
    )
    parser.add_argument("--backlog", type=Path, default=DEFAULT_BACKLOG)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument(
        "--runnable",
        default="daemon",
        choices=["daemon", "main_session_subagent", "any"],
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pick", action="store_true", help="Print next task")
    group.add_argument("--list", action="store_true", help="Print all scored tasks")
    group.add_argument(
        "--mark",
        nargs=3,
        metavar=("TASK_ID", "STATUS", "MESSAGE"),
        help="Record attempt status",
    )
    parser.add_argument(
        "--enqueue",
        action="store_true",
        help="On --pick, also append to picker_queue.jsonl",
    )
    args = parser.parse_args(argv)

    tasks = parse_backlog(args.backlog)
    state = load_state(args.state)
    now = datetime.now(timezone.utc)

    if args.mark:
        task_id, status, message = args.mark
        state = mark_attempt(state, task_id, status, message, now=now)
        save_state(state, args.state)
        print(f"marked {task_id} -> {status}: {message}")
        return 0

    state = ensure_seen(state, tasks, now=now)

    if args.list:
        scored = score_all(tasks, state, now)
        for score, task in scored:
            print(
                f"{score:6.2f}  {task.task_id:<8} [{task.complexity}] "
                f"({task.runnable_by:<22}) {task.title[:70]}"
            )
        save_state(state, args.state)
        return 0

    if args.pick:
        task = pick_next(tasks, state, now, runnable_filter=args.runnable)
        save_state(state, args.state)
        if task is None:
            print(json.dumps({"task": None, "reason": "no runnable tasks"}))
            return 1
        payload = task.to_dict()
        payload["runnable_filter"] = args.runnable
        print(json.dumps(payload, ensure_ascii=False))
        if args.enqueue:
            enqueue_for_main_session(task, now=now)
        return 0

    parser.print_help()
    return 2


def main() -> int:  # pragma: no cover - thin wrapper
    return _cli()


if __name__ == "__main__":
    sys.exit(main())
