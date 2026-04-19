"""Branch-specific executors for the daemon cycle."""
from pathlib import Path
from typing import Callable
import json
import os
import sys

# WSL-safe path translation: Windows C:/ paths resolve to /mnt/c/ under WSL.
IS_WSL = (sys.platform == "linux" and os.path.exists("/mnt/c"))


def _win_to_posix(p: str) -> str:
    """Translate Windows drive paths to /mnt/<drive>/ under WSL."""
    if not IS_WSL or not p:
        return p
    q = p.replace("\\", "/")
    if len(q) >= 2 and q[1] == ":" and q[0].isalpha():
        return f"/mnt/{q[0].lower()}{q[2:]}"
    return q


RESULTS = Path(_win_to_posix("C:/Users/admin/workspace/digital-immortality/results"))
REPO = RESULTS.parent
DOCS = REPO / "docs"
STAGING = REPO / "staging"


def execute_economic() -> str:
    """Branch 1: Read trading engine status, summarize."""
    status_path = RESULTS / "trading_engine_status.json"
    if not status_path.exists():
        return "Trading engine status file not found."
    data = json.loads(status_path.read_text(encoding="utf-8"))
    return (
        f"Tick {data.get('tick', '?')}, "
        f"PnL {data.get('total_pnl_pct', '?')}%, "
        f"signal {data.get('signal', '?')}"
    )


def execute_behavioral() -> str:
    """Branch 2: Check consistency test status."""
    scorecard = RESULTS / "consistency_scorecard.json"
    if scorecard.exists():
        data = json.loads(scorecard.read_text(encoding="utf-8"))
        return (
            f"Consistency: {data.get('aligned', '?')}/"
            f"{data.get('total', '?')} aligned, "
            f"streak {data.get('clean_streak', '?')}"
        )
    return "No consistency scorecard found."


def execute_learning() -> str:
    """Branch 3: Check distillation progress."""
    distil = RESULTS.parent / "memory" / "recursive_distillation.md"
    if distil.exists():
        lines = distil.read_text(
            encoding="utf-8", errors="replace",
        ).splitlines()
        return f"Distillation: {len(lines)} lines total"
    return "No distillation file found."


def execute_knowledge() -> str:
    """Branch 7: Check knowledge digestion progress."""
    state_path = RESULTS / "digestion_state.json"
    if state_path.exists():
        data = json.loads(state_path.read_text(encoding="utf-8"))
        return (
            f"Knowledge digestion: {data.get('files_digested', 0)}/"
            f"{data.get('total_files_known', '?')} files"
        )
    return "Knowledge digester not initialized."


def execute_social() -> str:
    """Branch 4: Check Discord/organism ecosystem status."""
    try:
        parts: list[str] = []
        diag = DOCS / "discord_distribution_diagnosis.md"
        if diag.exists():
            lines = diag.read_text(encoding="utf-8", errors="replace").splitlines()
            parts.append(f"Distribution diagnosis: {len(lines)} lines")
        outreach = STAGING / "outreach_week1_execution.md"
        if outreach.exists():
            text = outreach.read_text(encoding="utf-8", errors="replace")
            done = text.lower().count("[x]")
            todo = text.lower().count("[ ]")
            parts.append(f"Outreach: {done} done, {todo} pending")
        return "; ".join(parts) if parts else "No social/outreach data found."
    except Exception as e:
        return f"Social check error: {e}"


def execute_distribution() -> str:
    """Branch 5: Check distribution/SOP status."""
    try:
        if not DOCS.exists():
            return "docs/ directory not found."
        sop_files = [
            f for f in os.listdir(DOCS)
            if f.startswith("knowledge_product_") or f.startswith("publish_thread_sop")
        ]
        return f"Distribution: {len(sop_files)} SOPs/knowledge products in docs/"
    except Exception as e:
        return f"Distribution check error: {e}"


def execute_redundancy() -> str:
    """Branch 6: Check system redundancy/anti-fragile status."""
    try:
        parts: list[str] = []
        qs = STAGING / "quick_status.md"
        if qs.exists():
            text = qs.read_text(encoding="utf-8", errors="replace")
            for line in text.splitlines():
                if "daemon:" in line.lower():
                    parts.append(line.strip().lstrip("- "))
                    break
            for line in text.splitlines():
                if "web_scheduled:" in line.lower():
                    parts.append(line.strip().lstrip("- "))
                    break
        else:
            parts.append("quick_status.md not found")
        return "; ".join(parts) if parts else "No redundancy data."
    except Exception as e:
        return f"Redundancy check error: {e}"


def execute_life() -> str:
    """Branch 8: Check life maintenance status."""
    try:
        parts: list[str] = []
        cal = RESULTS / "life_calendar.json"
        if cal.exists():
            data = json.loads(cal.read_text(encoding="utf-8"))
            events = data.get("events", [])
            parts.append(f"Calendar: {len(events)} events, updated {data.get('updated_at', '?')}")
        health = RESULTS / "life_health.jsonl"
        if health.exists():
            lines = [l for l in health.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()]
            if lines:
                last = json.loads(lines[-1])
                metric = last.get("payload", {}).get("metric", "?")
                value = last.get("payload", {}).get("value", "?")
                parts.append(f"Last health: {metric}={value}")
        return "; ".join(parts) if parts else "No life data found."
    except Exception as e:
        return f"Life check error: {e}"


def execute_turing() -> str:
    """Branch 9: Check Turing test progress."""
    try:
        parts: list[str] = []
        gap_path = RESULTS / "turing_test" / "gap_register.jsonl"
        if gap_path.exists():
            lines = gap_path.read_text(encoding="utf-8", errors="replace").splitlines()
            data_lines = [l for l in lines if l.strip() and not l.strip().startswith("#")]
            if data_lines:
                gaps = [json.loads(l) for l in data_lines]
                resolved = sum(1 for g in gaps if g.get("resolved"))
                parts.append(f"Gaps: {resolved}/{len(gaps)} resolved")
            else:
                parts.append("Gap register: no entries yet")
        protocol = DOCS / "turing_test_protocol.md"
        if protocol.exists():
            text = protocol.read_text(encoding="utf-8", errors="replace")
            for line in text.splitlines():
                if "status" in line.lower() or "phase" in line.lower() or "gate" in line.lower():
                    parts.append(line.strip().lstrip("#- "))
                    break
        return "; ".join(parts) if parts else "No Turing test data found."
    except Exception as e:
        return f"Turing check error: {e}"


def execute_l3() -> str:
    """Branch 10: Check L3 self-modification status."""
    try:
        rules_path = RESULTS / "engine_rules.json"
        if not rules_path.exists():
            return "engine_rules.json not found — L3 not initialized."
        data = json.loads(rules_path.read_text(encoding="utf-8"))
        dead_loops = data.get("dead_loop_count", 0)
        evolved = data.get("evolved_at", "?")
        elog = data.get("evolution_log", [])
        last_event = elog[-1].get("event", "?") if elog else "none"
        return (
            f"L3: dead_loops={dead_loops}, evolved_at={evolved}, "
            f"last_event={last_event}, log_entries={len(elog)}"
        )
    except Exception as e:
        return f"L3 check error: {e}"


BRANCH_EXECUTORS: dict[int, Callable[[], str]] = {
    1: execute_economic,
    2: execute_behavioral,
    3: execute_learning,
    4: execute_social,
    5: execute_distribution,
    6: execute_redundancy,
    7: execute_knowledge,
    8: execute_life,
    9: execute_turing,
    10: execute_l3,
}
