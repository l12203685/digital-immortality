#!/usr/bin/env python3
"""
l3_selfmod.py — L3 v2 Self-Modification Loop

Detects unhealthy daemon patterns and injects recovery fixes into engine_rules.json
and results/l3_diagnostics.md.

Detectors:
    1. DEAD_LOOP     — same task cycling without progress (cycle_log repetition)
    2. QUEUE_EMPTY   — no tasks being generated (session_state remaining items)
    3. COMMIT_DROUGHT — no git commits in >24h (git log)
    4. STALE_BRANCH  — branches with >7 days since last_touched (tree_registry)

Usage:
    python tools/l3_selfmod.py              # run all detectors, output diagnostics
    python tools/l3_selfmod.py --json       # machine-readable JSON output
    python tools/l3_selfmod.py --dry-run    # detect but don't modify engine_rules

Can also be invoked from recursive_daemon.py via --l3-check flag.

Exit codes:
    0 — all clear
    1 — warnings detected (YELLOW)
    2 — critical issues detected (RED), recovery injected
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS = PROJECT_ROOT / "results"
STAGING = PROJECT_ROOT / "staging"
CYCLE_LOG_DIR = Path(os.path.expanduser("~")) / "staging" / "cycle_log"
SESSION_STATE = STAGING / "session_state.md"
ENGINE_RULES = RESULTS / "engine_rules.json"
L3_LOG = RESULTS / "engine_l3_log.jsonl"
DIAGNOSTICS_FILE = RESULTS / "l3_diagnostics.md"
DAEMON_LOG = RESULTS / "daemon_log.md"
CYCLE_COUNTER = RESULTS / "cycle_counter.json"
DAEMON_NEXT_PRIORITY = RESULTS / "daemon_next_priority.txt"
L3_RECOVERY = STAGING / "l3_recovery.md"

# ---------------------------------------------------------------------------
# Thresholds (can be overridden by engine_rules.json)
# ---------------------------------------------------------------------------

DEFAULT_THRESHOLDS = {
    # DEAD_LOOP: After a5c45c7 fix, healthy cycles show ~0.4-0.6 similarity.
    # RED at 0.85 catches true loops; YELLOW at 0.72 gives early warning.
    "dead_loop_similarity": 0.85,       # SequenceMatcher ratio — true loop
    "dead_loop_similarity_yellow": 0.72,  # early warning threshold
    "dead_loop_window": 5,              # number of recent cycle logs to compare

    # QUEUE_EMPTY: session_state items, picker_queue activity, priority file
    "queue_empty_threshold": 0,         # min remaining items in session_state
    "queue_empty_picker_hours": 24,     # picker_queue recency window (hours)

    # COMMIT_DROUGHT: expect at least 1 commit per 24h of daemon activity
    "commit_drought_hours": 24,         # hours without commits = drought
    "commit_drought_min_commits": 1,    # at least this many in the window

    # STALE_BRANCH: branches untouched >7 days in tree_registry qualify as stale
    "stale_branch_days": 7,             # days since last_updated to flag YELLOW
    "stale_branch_days_red": 14,        # days since last_updated to flag RED
    "stale_branch_skip_statuses": ["done", "blocked", "dormant"],  # skip these
}

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    """Load JSON file or return empty dict."""
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )


def _get_cycle() -> int:
    """Read current cycle from cycle_counter.json."""
    cc = _load_json(CYCLE_COUNTER)
    return cc.get("global_cycle", 0)


def _get_thresholds() -> dict[str, Any]:
    """Merge default thresholds with any overrides in engine_rules.json.

    Also merges a nested ``l3_thresholds`` key if present, allowing
    engine_rules.json to carry all L3 settings in one sub-object without
    polluting the top-level namespace.
    """
    rules = _load_json(ENGINE_RULES)
    thresholds = dict(DEFAULT_THRESHOLDS)
    # Top-level overrides (legacy/compat)
    for key in DEFAULT_THRESHOLDS:
        if key in rules:
            thresholds[key] = rules[key]
    # Nested l3_thresholds block (preferred going forward)
    nested = rules.get("l3_thresholds", {})
    for key, val in nested.items():
        thresholds[key] = val
    return thresholds


def _daemon_log(msg: str) -> None:
    """Append a line to daemon_log.md."""
    DAEMON_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(DAEMON_LOG, "a", encoding="utf-8") as f:
        f.write(f"\n{msg}\n")


# ---------------------------------------------------------------------------
# Detector 1: DEAD_LOOP
# ---------------------------------------------------------------------------

def _read_recent_cycle_logs(n: int = 5) -> list[dict[str, str]]:
    """Read the N most recent cycle_log files, returning {path, content, what_section}."""
    if not CYCLE_LOG_DIR.exists():
        return []

    files = sorted(
        CYCLE_LOG_DIR.glob("*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    # Skip trivially small files (< 200 bytes = empty template)
    files = [f for f in files if f.stat().st_size > 200]
    files = files[:n]

    entries: list[dict[str, str]] = []
    for fpath in files:
        try:
            content = fpath.read_text(encoding="utf-8")
        except OSError:
            continue
        # Extract the "What" section
        what_match = re.search(
            r"## What.*?\n(.*?)(?=\n## |\Z)", content, re.DOTALL
        )
        what_section = what_match.group(1).strip() if what_match else ""
        entries.append({
            "path": str(fpath.name),
            "content": content,
            "what": what_section,
        })

    return entries


def _text_similarity(a: str, b: str) -> float:
    """Quick similarity ratio between two strings."""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def detect_dead_loop(thresholds: dict[str, Any]) -> dict[str, Any]:
    """Detect if the daemon is cycling the same tasks without progress.

    Checks:
    1. Recent cycle logs' "What" sections are near-identical
    2. Same agent/tool calls repeating across cycles
    """
    window = thresholds["dead_loop_window"]
    sim_threshold = thresholds["dead_loop_similarity"]

    logs = _read_recent_cycle_logs(window)

    result: dict[str, Any] = {
        "detector": "DEAD_LOOP",
        "status": "GREEN",
        "logs_checked": len(logs),
        "details": {},
    }

    if len(logs) < 2:
        result["details"]["note"] = f"Only {len(logs)} cycle logs found, need >=2"
        return result

    # Pairwise similarity of "What" sections
    similarities: list[float] = []
    for i in range(len(logs) - 1):
        sim = _text_similarity(logs[i]["what"], logs[i + 1]["what"])
        similarities.append(round(sim, 3))

    avg_sim = sum(similarities) / len(similarities) if similarities else 0.0
    max_sim = max(similarities) if similarities else 0.0

    result["details"]["pairwise_similarities"] = similarities
    result["details"]["avg_similarity"] = round(avg_sim, 3)
    result["details"]["max_similarity"] = round(max_sim, 3)
    result["details"]["threshold"] = sim_threshold

    # Count repeated action patterns across logs
    action_counter: Counter[str] = Counter()
    for log_entry in logs:
        # Extract agent/tool names from "What" section
        actions = re.findall(r"- (?:Agent: |Read\(|Write\(|Edit\()([^\n)]+)", log_entry["what"])
        for a in actions:
            action_counter[a.strip()] += 1

    # Actions appearing in >80% of logs = repetitive
    repetitive = {
        k: v for k, v in action_counter.items()
        if v >= max(2, int(len(logs) * 0.8))
    }
    result["details"]["repetitive_actions"] = dict(repetitive)

    yellow_threshold = thresholds.get("dead_loop_similarity_yellow", sim_threshold * 0.85)

    if avg_sim >= sim_threshold:
        result["status"] = "RED"
        result["details"]["reason"] = (
            f"Average cycle similarity {avg_sim:.2f} >= {sim_threshold} — "
            f"daemon is repeating the same work across {len(logs)} cycles"
        )
    elif avg_sim >= yellow_threshold:
        result["status"] = "YELLOW"
        result["details"]["reason"] = (
            f"Average cycle similarity {avg_sim:.2f} >= yellow threshold {yellow_threshold:.2f} "
            f"(red at {sim_threshold}) — approaching loop"
        )

    return result


# ---------------------------------------------------------------------------
# Detector 2: QUEUE_EMPTY
# ---------------------------------------------------------------------------

def detect_queue_empty(thresholds: dict[str, Any]) -> dict[str, Any]:
    """Detect if no tasks are being generated / queued.

    Checks:
    1. session_state.md has no remaining carry-over items
    2. daemon_next_priority.txt is empty or stale
    3. picker_queue.jsonl has no recent entries
    """
    result: dict[str, Any] = {
        "detector": "QUEUE_EMPTY",
        "status": "GREEN",
        "details": {},
    }

    # Check session_state.md
    if SESSION_STATE.exists():
        try:
            ss_content = SESSION_STATE.read_text(encoding="utf-8")
            # Look for carry-over / pending / remaining items
            carry_lines = re.findall(
                r"(?:carry-over|pending|remaining|TODO|BLOCKED).*",
                ss_content, re.IGNORECASE
            )
            result["details"]["session_state_carry_items"] = len(carry_lines)

            # Check staleness
            age_h = (
                datetime.now().timestamp() - SESSION_STATE.stat().st_mtime
            ) / 3600.0
            result["details"]["session_state_age_h"] = round(age_h, 1)
            if age_h > 48:
                result["details"]["session_state_stale"] = True
        except OSError:
            result["details"]["session_state_error"] = "read failed"
    else:
        result["details"]["session_state_exists"] = False

    # Check daemon_next_priority.txt
    if DAEMON_NEXT_PRIORITY.exists():
        try:
            priority_content = DAEMON_NEXT_PRIORITY.read_text(encoding="utf-8").strip()
            result["details"]["daemon_next_priority_set"] = bool(priority_content)
            result["details"]["daemon_next_priority_value"] = priority_content[:120]
        except OSError:
            pass
    else:
        result["details"]["daemon_next_priority_exists"] = False

    # Check picker_queue.jsonl
    picker_queue = RESULTS / "picker_queue.jsonl"
    if picker_queue.exists():
        try:
            lines = picker_queue.read_text(encoding="utf-8").strip().splitlines()
            recent_entries = 0
            for line in reversed(lines):
                try:
                    entry = json.loads(line)
                    ts = entry.get("ts", "")
                    if ts:
                        entry_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                        age_h = (
                            datetime.now(timezone.utc) - entry_dt
                        ).total_seconds() / 3600.0
                        if age_h <= 24:
                            recent_entries += 1
                except (json.JSONDecodeError, ValueError):
                    pass
            result["details"]["picker_queue_entries_24h"] = recent_entries
        except OSError:
            pass
    else:
        result["details"]["picker_queue_exists"] = False

    # Determine status
    no_carry = result["details"].get("session_state_carry_items", 0) == 0
    no_priority = not result["details"].get("daemon_next_priority_set", False)
    no_queue = result["details"].get("picker_queue_entries_24h", 0) == 0
    ss_stale = result["details"].get("session_state_stale", False)

    if no_carry and no_priority and no_queue:
        result["status"] = "RED"
        result["details"]["reason"] = (
            "No carry-over items, no daemon priority, no picker queue entries — "
            "the system has no tasks to execute"
        )
    elif (no_carry and no_priority) or ss_stale:
        result["status"] = "YELLOW"
        result["details"]["reason"] = (
            "Task pipeline partially empty or session_state stale"
        )

    return result


# ---------------------------------------------------------------------------
# Detector 3: COMMIT_DROUGHT
# ---------------------------------------------------------------------------

def detect_commit_drought(thresholds: dict[str, Any]) -> dict[str, Any]:
    """Detect if no git commits have been made in >24h.

    Checks git log across the digital-immortality repo.
    """
    hours = thresholds["commit_drought_hours"]
    min_commits = thresholds["commit_drought_min_commits"]

    result: dict[str, Any] = {
        "detector": "COMMIT_DROUGHT",
        "status": "GREEN",
        "details": {},
    }

    try:
        cmd = [
            "git", "-C", str(PROJECT_ROOT),
            "log", f"--since={hours} hours ago",
            "--oneline", "--no-merges",
        ]
        proc = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=15, encoding="utf-8", errors="replace",
        )
        if proc.returncode == 0:
            lines = [l for l in proc.stdout.strip().splitlines() if l.strip()]
            commit_count = len(lines)
            result["details"]["commits_in_window"] = commit_count
            result["details"]["window_hours"] = hours
            result["details"]["min_required"] = min_commits

            if commit_count < min_commits:
                result["status"] = "RED"
                result["details"]["reason"] = (
                    f"Only {commit_count} commits in last {hours}h "
                    f"(minimum: {min_commits})"
                )
            elif commit_count < min_commits * 3:
                result["status"] = "YELLOW"
                result["details"]["reason"] = (
                    f"{commit_count} commits in last {hours}h — low activity"
                )
        else:
            result["details"]["git_error"] = proc.stderr.strip()[:200]
    except subprocess.TimeoutExpired:
        result["details"]["git_error"] = "git log timed out"
    except FileNotFoundError:
        result["details"]["git_error"] = "git not found"

    # Also check LYH repo for broader activity
    lyh_root = Path(os.path.expanduser("~")) / "LYH"
    if lyh_root.exists():
        try:
            cmd_lyh = [
                "git", "-C", str(lyh_root),
                "log", f"--since={hours} hours ago",
                "--oneline", "--no-merges",
            ]
            proc_lyh = subprocess.run(
                cmd_lyh, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                timeout=15, encoding="utf-8", errors="replace",
            )
            if proc_lyh.returncode == 0 and proc_lyh.stdout:
                lyh_commits = len([
                    l for l in proc_lyh.stdout.strip().splitlines() if l.strip()
                ])
                result["details"]["lyh_commits_in_window"] = lyh_commits
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    return result


# ---------------------------------------------------------------------------
# Detector 4: STALE_BRANCH
# ---------------------------------------------------------------------------

TREE_REGISTRY_BRANCHES = Path(os.path.expanduser("~")) / "LYH" / "agent" / "tree_registry" / "branches"


def _parse_branch_frontmatter(content: str) -> dict[str, str]:
    """Extract YAML-like frontmatter fields from a branch .md file.

    Looks for a leading ``---`` block and parses key: value lines inside it.
    Returns a dict of string keys to string values (stripped).
    """
    fm: dict[str, str] = {}
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return fm
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip()
    return fm


def detect_stale_branch(thresholds: dict[str, Any]) -> dict[str, Any]:
    """Detect branches in tree_registry that have not been touched in >7 days.

    Reads every branches/*.md file, parses ``last_updated`` frontmatter field,
    and computes the age in days. Branches with status in skip_statuses are
    excluded — stale is only meaningful for active branches the daemon should
    be progressing.

    Status:
      GREEN  — all active branches touched within stale_branch_days
      YELLOW — ≥1 active branch last touched >stale_branch_days ago
      RED    — ≥1 active branch last touched >stale_branch_days_red ago
    """
    stale_days_yellow = thresholds["stale_branch_days"]
    stale_days_red = thresholds["stale_branch_days_red"]
    skip_statuses = thresholds.get("stale_branch_skip_statuses", ["done", "blocked", "dormant"])

    result: dict[str, Any] = {
        "detector": "STALE_BRANCH",
        "status": "GREEN",
        "details": {
            "registry_path": str(TREE_REGISTRY_BRANCHES),
            "stale_yellow_days": stale_days_yellow,
            "stale_red_days": stale_days_red,
        },
    }

    if not TREE_REGISTRY_BRANCHES.exists():
        result["details"]["note"] = f"tree_registry branches dir not found: {TREE_REGISTRY_BRANCHES}"
        return result

    now = datetime.now(timezone.utc)
    stale_yellow: list[dict[str, Any]] = []  # >7 days but <=14
    stale_red: list[dict[str, Any]] = []     # >14 days
    checked: list[dict[str, Any]] = []

    for md_file in sorted(TREE_REGISTRY_BRANCHES.glob("*.md")):
        try:
            content = md_file.read_text(encoding="utf-8")
        except OSError:
            continue

        fm = _parse_branch_frontmatter(content)
        branch_id = fm.get("id", md_file.stem)
        status = fm.get("status", "unknown").lower()
        last_updated_str = fm.get("last_updated", "").strip()

        # Skip non-active branches
        if status in skip_statuses:
            checked.append({"id": branch_id, "status": status, "skipped": True})
            continue

        # Parse last_updated date
        age_days: float | None = None
        if last_updated_str:
            try:
                # Support YYYY-MM-DD or YYYY-MM-DD HH:MM formats
                dt_str = last_updated_str[:10]  # take date portion
                last_dt = datetime(
                    *[int(x) for x in dt_str.split("-")],
                    tzinfo=timezone.utc,
                )
                age_days = (now - last_dt).total_seconds() / 86400.0
            except (ValueError, TypeError):
                age_days = None

        entry = {
            "id": branch_id,
            "status": status,
            "last_updated": last_updated_str or "(not set)",
            "age_days": round(age_days, 1) if age_days is not None else None,
        }
        checked.append(entry)

        if age_days is None:
            # Missing last_updated on an active branch is suspicious
            stale_yellow.append({**entry, "reason": "missing last_updated field"})
        elif age_days > stale_days_red:
            stale_red.append({**entry, "reason": f"{age_days:.1f}d since last update (>{stale_days_red}d)"})
        elif age_days > stale_days_yellow:
            stale_yellow.append({**entry, "reason": f"{age_days:.1f}d since last update (>{stale_days_yellow}d)"})

    result["details"]["branches_checked"] = len(checked)
    result["details"]["stale_yellow"] = stale_yellow
    result["details"]["stale_red"] = stale_red

    if stale_red:
        result["status"] = "RED"
        ids = [b["id"] for b in stale_red]
        result["details"]["reason"] = (
            f"{len(stale_red)} active branch(es) untouched >{stale_days_red}d: "
            f"{', '.join(ids)}"
        )
    elif stale_yellow:
        result["status"] = "YELLOW"
        ids = [b["id"] for b in stale_yellow]
        result["details"]["reason"] = (
            f"{len(stale_yellow)} active branch(es) untouched >{stale_days_yellow}d: "
            f"{', '.join(ids)}"
        )

    return result


# ---------------------------------------------------------------------------
# Recovery: update engine_rules + inject prompt suggestions
# ---------------------------------------------------------------------------

def _inject_recovery(
    detections: list[dict[str, Any]],
    cycle: int,
    dry_run: bool = False,
) -> list[str]:
    """Update engine_rules.json and write recovery suggestions.

    Returns list of actions taken.
    """
    actions_taken: list[str] = []
    now = _now_iso()
    rules = _load_json(ENGINE_RULES)

    red_detections = [d for d in detections if d["status"] == "RED"]
    yellow_detections = [d for d in detections if d["status"] == "YELLOW"]

    if not red_detections and not yellow_detections:
        return actions_taken

    # --- Engine rules updates ---

    if not dry_run:
        for det in red_detections:
            name = det["detector"]

            if name == "DEAD_LOOP":
                # Increase dead_loop_count, record detection
                rules["dead_loop_count"] = rules.get("dead_loop_count", 0) + 1
                rules["last_dead_loop"] = {
                    "cycle": cycle,
                    "avg_similarity": det["details"].get("avg_similarity", 0),
                    "repetitive_actions": det["details"].get("repetitive_actions", {}),
                    "ts": now,
                }
                # Inject a branch-switch directive so the planner picks it up
                repetitive = det["details"].get("repetitive_actions", {})
                top_repetitive = ", ".join(list(repetitive.keys())[:3]) if repetitive else "unknown"
                DAEMON_NEXT_PRIORITY.parent.mkdir(parents=True, exist_ok=True)
                DAEMON_NEXT_PRIORITY.write_text(
                    f"[L3-DEAD_LOOP cycle {cycle}] FORCE BRANCH SWITCH — "
                    f"daemon has been repeating: {top_repetitive}. "
                    f"Next cycle: pick a different branch from tree_registry INDEX.md. "
                    f"Avoid branches: {top_repetitive}. "
                    f"Prefer: B1 economic tasks or B7 ZP writing.",
                    encoding="utf-8",
                )
                actions_taken.append(
                    f"DEAD_LOOP: incremented dead_loop_count to {rules['dead_loop_count']}; "
                    f"wrote branch-switch directive to daemon_next_priority.txt"
                )

            elif name == "QUEUE_EMPTY":
                rules["queue_empty_count"] = rules.get("queue_empty_count", 0) + 1
                rules["last_queue_empty"] = {"cycle": cycle, "ts": now}
                # Write specific re-scan suggestion
                DAEMON_NEXT_PRIORITY.parent.mkdir(parents=True, exist_ok=True)
                DAEMON_NEXT_PRIORITY.write_text(
                    f"[L3-QUEUE_EMPTY cycle {cycle}] Task pipeline is dry. "
                    f"Action: run 'python -m tools.idle_task_picker --pick --runnable daemon --enqueue' "
                    f"to refill picker_queue. Also re-read staging/session_state.md carry-over items "
                    f"and tree_registry INDEX.md for neglected active branches.",
                    encoding="utf-8",
                )
                actions_taken.append(
                    "QUEUE_EMPTY: wrote idle_task_picker re-scan directive to daemon_next_priority.txt"
                )

            elif name == "COMMIT_DROUGHT":
                rules["commit_drought_count"] = rules.get("commit_drought_count", 0) + 1
                rules["last_commit_drought"] = {"cycle": cycle, "ts": now}
                actions_taken.append(
                    f"COMMIT_DROUGHT: incremented commit_drought_count to {rules['commit_drought_count']}"
                )

            elif name == "STALE_BRANCH":
                rules["stale_branch_count"] = rules.get("stale_branch_count", 0) + 1
                stale_ids = [b["id"] for b in det["details"].get("stale_red", [])]
                rules["last_stale_branch"] = {
                    "cycle": cycle,
                    "stale_ids": stale_ids,
                    "ts": now,
                }
                # Write actionable branch-revival directive
                DAEMON_NEXT_PRIORITY.parent.mkdir(parents=True, exist_ok=True)
                DAEMON_NEXT_PRIORITY.write_text(
                    f"[L3-STALE_BRANCH cycle {cycle}] Branches dormant >14d (active status): "
                    f"{', '.join(stale_ids) if stale_ids else 'see stale_yellow'}. "
                    f"Action: pick ONE stale branch, read its branch md, perform ONE concrete task "
                    f"(write file / update doc / commit), and update its last_updated frontmatter. "
                    f"Priority: B1 or B7 stale items first.",
                    encoding="utf-8",
                )
                actions_taken.append(
                    f"STALE_BRANCH: incremented stale_branch_count to {rules['stale_branch_count']}; "
                    f"wrote branch-revival directive for: {', '.join(stale_ids) if stale_ids else 'YELLOW branches'}"
                )

        # Update evolution log
        evo_log = rules.get("evolution_log", [])
        evo_log.append({
            "cycle": cycle,
            "event": "L3_SELFMOD",
            "detections": [
                {"detector": d["detector"], "status": d["status"]}
                for d in detections
            ],
            "actions_taken": actions_taken,
            "ts": now,
        })
        rules["evolution_log"] = evo_log[-50:]
        rules["evolved_at"] = now
        _save_json(ENGINE_RULES, rules)
        actions_taken.append("Updated engine_rules.json evolution_log")

    # --- Recovery prompt ---

    if red_detections and not dry_run:
        recovery_lines = [
            f"# L3 Self-Modification Recovery — {now}",
            f"",
            f"Cycle: {cycle}",
            f"RED detectors: {', '.join(d['detector'] for d in red_detections)}",
            f"",
            f"## Detected Issues",
        ]
        for det in red_detections:
            recovery_lines.append(f"### {det['detector']}")
            reason = det["details"].get("reason", "unknown")
            recovery_lines.append(f"- {reason}")
            recovery_lines.append("")

        recovery_lines += [
            "## Suggested Recovery Actions",
            "",
        ]

        for det in red_detections:
            name = det["detector"]
            if name == "DEAD_LOOP":
                rep_actions = det["details"].get("repetitive_actions", {})
                top_rep = list(rep_actions.keys())[:3] if rep_actions else []
                avg_sim = det["details"].get("avg_similarity", "?")
                recovery_lines += [
                    "### DEAD_LOOP Recovery",
                    f"Detected avg_similarity={avg_sim} — the daemon is stuck in a loop.",
                    f"Repetitive actions: {', '.join(top_rep) if top_rep else 'see details above'}",
                    "",
                    "Immediate actions (in order):",
                    "1. `cat results/daemon_next_priority.txt` — branch-switch directive already written",
                    "2. Manually verify staging/session_state.md has diverse carry-over items (not same task repeated)",
                    "3. Pick a branch from tree_registry/INDEX.md NOT in the repetitive list above",
                    "4. Write one concrete artifact to that branch (even a doc update) to break the loop",
                    "5. If loop persists after 2 more cycles: increase dead_loop_window threshold in engine_rules.json",
                    "",
                ]
            elif name == "QUEUE_EMPTY":
                recovery_lines += [
                    "### QUEUE_EMPTY Recovery",
                    "The task pipeline is empty — idle_task_picker has no work queued.",
                    "",
                    "Immediate actions (in order):",
                    "1. Run: `python -m tools.idle_task_picker --pick --runnable daemon --enqueue`",
                    "2. Read: `cat staging/session_state.md` — check carry-over section for pending items",
                    "3. Read: `cat LYH/agent/tree_registry/INDEX.md` — identify active branches with pending milestones",
                    "4. Write at least one new task to picker_queue.jsonl for the next cycle",
                    "5. If session_state is empty: re-derive tasks from tree_registry active branches",
                    "",
                ]
            elif name == "COMMIT_DROUGHT":
                hours = det["details"].get("window_hours", 24)
                count = det["details"].get("commits_in_window", 0)
                recovery_lines += [
                    "### COMMIT_DROUGHT Recovery",
                    f"Only {count} commit(s) in last {hours}h — daemon is not persisting work.",
                    "",
                    "Immediate actions (in order):",
                    "1. Check: `cat staging/engine.pid` — is the daemon process running?",
                    "2. Check: `git -C workspace/digital-immortality remote -v` — remote connectivity OK?",
                    "3. Check: `tail -20 results/daemon_log.md` — look for errors or stuck cycles",
                    "4. Force a lightweight commit: update results/dynamic_tree.md or results/l3_diagnostics.md",
                    "5. Run: `git add results/ && git commit -m 'chore: L3 drought recovery force-commit'`",
                    "",
                ]
            elif name == "STALE_BRANCH":
                stale_red = det["details"].get("stale_red", [])
                stale_yellow = det["details"].get("stale_yellow", [])
                all_stale = stale_red + stale_yellow
                recovery_lines += [
                    "### STALE_BRANCH Recovery",
                    f"Active branches with no updates in >{det['details'].get('stale_red_days', 14)}d:",
                    "",
                ]
                for b in stale_red:
                    recovery_lines.append(f"  - **{b['id']}**: {b.get('reason', '?')} (last: {b.get('last_updated', '?')})")
                if stale_yellow:
                    recovery_lines.append(f"\nYELLOW (>{det['details'].get('stale_yellow_days', 7)}d):")
                    for b in stale_yellow:
                        recovery_lines.append(f"  - **{b['id']}**: {b.get('reason', '?')} (last: {b.get('last_updated', '?')})")
                recovery_lines += [
                    "",
                    "Immediate actions (in order):",
                    f"1. Pick ONE stale branch: {all_stale[0]['id'] if all_stale else 'see above'}",
                    f"2. Read its branch md: `cat LYH/agent/tree_registry/branches/<id>.md`",
                    "3. Execute ONE concrete pending milestone (not just a doc update — real work)",
                    "4. Update the branch md `last_updated` frontmatter to today's date",
                    "5. Commit: `git add LYH/agent/tree_registry/branches/<id>.md && git commit -m 'chore: revive stale branch <id>'`",
                    "",
                ]

        recovery_lines += [
            "## Priority",
            "Address RED items before next recursive cycle.",
        ]

        L3_RECOVERY.parent.mkdir(parents=True, exist_ok=True)
        L3_RECOVERY.write_text("\n".join(recovery_lines), encoding="utf-8")
        actions_taken.append(f"Wrote recovery prompt to {L3_RECOVERY.name}")
        _daemon_log(
            f"[L3v2-selfmod] RED detected: "
            f"{', '.join(d['detector'] for d in red_detections)} — "
            f"recovery prompt written"
        )

    # --- Append to L3 log ---

    if not dry_run:
        log_entry = {
            "cycle": cycle,
            "ts": now,
            "source": "l3_selfmod",
            "worst": "RED" if red_detections else "YELLOW",
            "detections": {
                d["detector"]: d["status"] for d in detections
            },
            "actions_taken": actions_taken,
        }
        L3_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(L3_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    return actions_taken


# ---------------------------------------------------------------------------
# Diagnostics output
# ---------------------------------------------------------------------------

def _write_diagnostics(
    detections: list[dict[str, Any]],
    actions: list[str],
    cycle: int,
) -> None:
    """Write human-readable diagnostics to results/l3_diagnostics.md."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M +08")
    worst = "GREEN"
    for d in detections:
        if d["status"] == "RED":
            worst = "RED"
            break
        if d["status"] == "YELLOW":
            worst = "YELLOW"

    lines = [
        f"# L3 Self-Modification Diagnostics",
        f"",
        f"**Generated**: {now_str}",
        f"**Cycle**: {cycle}",
        f"**Overall**: {worst}",
        f"",
        f"## Detector Results",
        f"",
        f"| Detector | Status | Key Finding |",
        f"|----------|--------|-------------|",
    ]

    for det in detections:
        reason = det["details"].get("reason", "OK")
        if len(reason) > 80:
            reason = reason[:77] + "..."
        lines.append(f"| {det['detector']} | {det['status']} | {reason} |")

    lines += ["", "## Details", ""]

    for det in detections:
        lines.append(f"### {det['detector']} ({det['status']})")
        lines.append("")
        for key, val in det["details"].items():
            if key == "pairwise_similarities":
                lines.append(f"- **{key}**: {[round(s, 2) for s in val]}")
            elif isinstance(val, dict):
                lines.append(f"- **{key}**: {json.dumps(val, ensure_ascii=False)}")
            else:
                lines.append(f"- **{key}**: {val}")
        lines.append("")

    if actions:
        lines += ["## Actions Taken", ""]
        for a in actions:
            lines.append(f"- {a}")
        lines.append("")
    else:
        lines += ["## Actions Taken", "", "No corrective actions needed.", ""]

    lines += [
        "---",
        f"*Next run: invoke `python tools/l3_selfmod.py` or `recursive_engine.py --l3-check`*",
    ]

    DIAGNOSTICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    DIAGNOSTICS_FILE.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_l3_selfmod(
    dry_run: bool = False,
    json_output: bool = False,
) -> dict[str, Any]:
    """Run all L3 v2 detectors, inject fixes if needed, output diagnostics.

    Returns summary dict.
    """
    cycle = _get_cycle()
    thresholds = _get_thresholds()

    # Run all detectors
    detections = [
        detect_dead_loop(thresholds),
        detect_queue_empty(thresholds),
        detect_commit_drought(thresholds),
        detect_stale_branch(thresholds),
    ]

    # Inject recovery if needed
    actions = _inject_recovery(detections, cycle, dry_run=dry_run)

    # Write diagnostics file
    _write_diagnostics(detections, actions, cycle)

    # Build summary
    worst = "GREEN"
    for d in detections:
        if d["status"] == "RED":
            worst = "RED"
            break
        if d["status"] == "YELLOW":
            worst = "YELLOW"

    summary = {
        "cycle": cycle,
        "ts": _now_iso(),
        "worst": worst,
        "detections": {d["detector"]: d["status"] for d in detections},
        "actions_taken": actions,
        "diagnostics_file": str(DIAGNOSTICS_FILE),
        "dry_run": dry_run,
    }

    if not json_output:
        print(f"[L3v2-selfmod] cycle={cycle} worst={worst}")
        for det in detections:
            status_icon = {"GREEN": "OK", "YELLOW": "WARN", "RED": "CRIT"}[det["status"]]
            reason = det["details"].get("reason", "OK")
            print(f"  {det['detector']}: {status_icon} — {reason}")
        if actions:
            for a in actions:
                print(f"  -> {a}")
        else:
            print("  -> no corrective actions needed")
        print(f"  diagnostics: {DIAGNOSTICS_FILE}")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="L3 v2 Self-Modification Loop — detect unhealthy daemon patterns",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output machine-readable JSON",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Detect only, don't modify engine_rules or write recovery",
    )
    args = parser.parse_args()

    result = run_l3_selfmod(
        dry_run=args.dry_run,
        json_output=args.json,
    )

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

    # Exit code based on worst status
    if result["worst"] == "RED":
        sys.exit(2)
    elif result["worst"] == "YELLOW":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
