#!/usr/bin/env python3
"""
l3_audit.py — L3 System-Wide Three-Layer Loop Health Audit
B10 branch tool. Audits L1 (Execution), L2 (Learning), L3 (Evolution) layers
and their cross-layer pipelines.

Usage:
    python tools/l3_audit.py           # human-readable report
    python tools/l3_audit.py --json    # machine-readable JSON

Exit codes:
    0 — all GREEN
    1 — any YELLOW (no RED)
    2 — any RED
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Paths (relative to project root)
# ---------------------------------------------------------------------------

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _p(*parts: str) -> str:
    return os.path.join(PROJECT_ROOT, *parts)


PATHS = {
    # L1
    "daemon_log":            _p("results", "daemon_log.md"),
    "session_state":         _p("staging", "session_state.md"),
    "trading_engine_status": _p("results", "trading_engine_status.json"),
    # L2
    "digestion_state":       _p("results", "digestion_state.json"),
    "distil_dedupe_report":  _p("results", "distil_dedupe_report.json"),
    "memory_dir":            os.path.join(
                                 os.path.expanduser("~"),
                                 ".claude", "projects",
                                 "C--Users-admin", "memory"),
    # L3
    "engine_rules":          _p("results", "engine_rules.json"),
    "engine_l3_log":         _p("results", "engine_l3_log.jsonl"),
    "execution_rules":       _p("results", "execution_rules.json"),
    "dna_core":              os.path.join(
                                 os.path.expanduser("~"),
                                 "LYH", "agent", "dna_core.md"),
    "dynamic_tree":          _p("results", "dynamic_tree.md"),
    "dna_evolution_log":     _p("memory", "dna_evolution_log.jsonl"),
}

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

_NOW = time.time()


def file_age_hours(path: str) -> float | None:
    """Return file age in hours, or None if file missing."""
    if not os.path.exists(path):
        return None
    return (_NOW - os.path.getmtime(path)) / 3600.0


def file_mtime_str(path: str) -> str:
    """Return local mtime as 'YYYY-MM-DD HH:MM +08' or 'MISSING'."""
    if not os.path.exists(path):
        return "MISSING"
    ts = os.path.getmtime(path)
    dt = datetime.fromtimestamp(ts)
    return dt.strftime("%Y-%m-%d %H:%M")


def read_json(path: str) -> dict | list | None:
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return None


def read_text(path: str, tail_chars: int = 4000) -> str | None:
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            content = fh.read()
        return content[-tail_chars:] if len(content) > tail_chars else content
    except OSError:
        return None


def count_jsonl_lines(path: str) -> int:
    if not os.path.exists(path):
        return 0
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return sum(1 for _ in fh)
    except OSError:
        return 0


def health_label(value: str) -> str:
    """Return colour-coded label string."""
    labels = {"GREEN": "GREEN", "YELLOW": "YELLOW", "RED": "RED"}
    return labels.get(value, value)


# ---------------------------------------------------------------------------
# L1 Audit — Execution Layer
# ---------------------------------------------------------------------------

def audit_l1() -> dict:
    result = {
        "layer": "L1 Execution",
        "health": "GREEN",
        "details": {},
        "issues": [],
    }

    # --- daemon_log.md ---
    daemon_tail = read_text(PATHS["daemon_log"])
    daemon_age = file_age_hours(PATHS["daemon_log"])

    if daemon_age is None:
        result["issues"].append("daemon_log.md MISSING")
        result["details"]["daemon_log"] = "MISSING"
        result["health"] = "RED"
    else:
        result["details"]["daemon_log_age_h"] = round(daemon_age, 2)
        result["details"]["daemon_log_mtime"] = file_mtime_str(PATHS["daemon_log"])

        # Count cycle markers in tail (e.g. "[cycle NNN]")
        cycle_matches = re.findall(r'\[cycle\s+(\d+)\]', daemon_tail or "")
        result["details"]["daemon_cycles_in_tail"] = len(cycle_matches)
        if cycle_matches:
            result["details"]["daemon_last_cycle"] = int(cycle_matches[-1])

        # Count cycles in last 24h — look for timestamps in daemon_log tail
        # Format seen: "2026-04-14 00:49:35 (Taipei)" or ISO timestamps
        ts_matches = re.findall(
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', daemon_tail or ""
        )
        cycles_24h = 0
        for ts_str in ts_matches:
            try:
                dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                age = (_NOW - dt.timestamp()) / 3600.0
                if age <= 24:
                    cycles_24h += 1
            except ValueError:
                pass
        result["details"]["daemon_cycles_24h_approx"] = cycles_24h

        if daemon_age <= 2:
            pass  # stays GREEN
        elif daemon_age <= 12:
            result["health"] = "YELLOW"
            result["issues"].append(
                f"daemon_log last updated {daemon_age:.1f}h ago (threshold: 2h)"
            )
        else:
            result["health"] = "RED"
            result["issues"].append(
                f"daemon_log stale: {daemon_age:.1f}h ago (threshold: 12h)"
            )

    # --- session_state.md ---
    ss_age = file_age_hours(PATHS["session_state"])
    result["details"]["session_state_mtime"] = file_mtime_str(PATHS["session_state"])
    if ss_age is None:
        result["details"]["session_state"] = "MISSING"
        result["issues"].append("session_state.md MISSING — no carry-over data")
    else:
        result["details"]["session_state_age_h"] = round(ss_age, 2)
        ss_text = read_text(PATHS["session_state"], tail_chars=2000) or ""
        # Check for carry-over markers
        has_carryover = bool(
            re.search(r'carry[\-_]?over|pending|incomplete|blocked', ss_text, re.IGNORECASE)
        )
        result["details"]["session_state_has_carryover"] = has_carryover
        if ss_age > 24:
            if result["health"] == "GREEN":
                result["health"] = "YELLOW"
            result["issues"].append(
                f"session_state.md stale: {ss_age:.1f}h ago (not refreshed in >24h)"
            )

    # --- trading_engine_status.json ---
    te_age = file_age_hours(PATHS["trading_engine_status"])
    result["details"]["trading_engine_mtime"] = file_mtime_str(PATHS["trading_engine_status"])
    if te_age is None:
        result["details"]["trading_engine"] = "MISSING"
    else:
        te_data = read_json(PATHS["trading_engine_status"])
        result["details"]["trading_engine_age_h"] = round(te_age, 2)
        if te_data:
            result["details"]["trading_active_strategies"] = te_data.get("active_strategies")
            result["details"]["trading_tick_count"] = te_data.get("tick_count")
            result["details"]["trading_regime"] = te_data.get("regime")
            result["details"]["trading_total_pnl_pct"] = te_data.get("total_pnl_pct")
            # If engine status is very stale, flag it
            if te_age > 6:
                if result["health"] == "GREEN":
                    result["health"] = "YELLOW"
                result["issues"].append(
                    f"trading_engine_status stale: {te_age:.1f}h ago"
                )

    return result


# ---------------------------------------------------------------------------
# L2 Audit — Learning Layer
# ---------------------------------------------------------------------------

def audit_l2() -> dict:
    result = {
        "layer": "L2 Learning",
        "health": "GREEN",
        "details": {},
        "issues": [],
    }

    # --- digestion_state.json ---
    dig_age = file_age_hours(PATHS["digestion_state"])
    result["details"]["digestion_state_mtime"] = file_mtime_str(PATHS["digestion_state"])
    if dig_age is None:
        result["details"]["digestion_state"] = "MISSING"
        result["health"] = "RED"
        result["issues"].append("digestion_state.json MISSING — L2 pipeline unknown")
    else:
        dig_data = read_json(PATHS["digestion_state"])
        result["details"]["digestion_state_age_h"] = round(dig_age, 2)
        if dig_data:
            total = dig_data.get("total_files_known", 0)
            digested = dig_data.get("files_digested", 0)
            last_at = dig_data.get("last_digested_at", "")
            pct = round(digested / total * 100, 2) if total else 0
            result["details"]["digestion_total_known"] = total
            result["details"]["digestion_files_done"] = digested
            result["details"]["digestion_progress_pct"] = pct
            result["details"]["digestion_last_at"] = last_at
            result["details"]["digestion_current_tier"] = dig_data.get("current_tier")

        if dig_age <= 24:
            pass  # GREEN
        else:
            result["health"] = "YELLOW"
            result["issues"].append(
                f"digestion_state not updated in {dig_age:.1f}h (threshold: 24h)"
            )

    # --- memory/*.md distillation count ---
    memory_dir = PATHS["memory_dir"]
    if os.path.isdir(memory_dir):
        md_files = [
            f for f in os.listdir(memory_dir)
            if f.endswith(".md") and os.path.isfile(os.path.join(memory_dir, f))
        ]
        result["details"]["memory_md_count"] = len(md_files)
        # Find most recently modified
        if md_files:
            latest = max(md_files, key=lambda f: os.path.getmtime(os.path.join(memory_dir, f)))
            latest_age = file_age_hours(os.path.join(memory_dir, latest))
            result["details"]["memory_latest_file"] = latest
            result["details"]["memory_latest_age_h"] = round(latest_age, 2) if latest_age is not None else None
    else:
        result["details"]["memory_md_count"] = 0
        result["issues"].append(f"memory dir not found: {memory_dir}")

    # --- distil_dedupe_report.json ---
    dedup_age = file_age_hours(PATHS["distil_dedupe_report"])
    result["details"]["distil_dedupe_mtime"] = file_mtime_str(PATHS["distil_dedupe_report"])
    if dedup_age is None:
        result["details"]["distil_dedupe_report"] = "MISSING"
    else:
        dedup_data = read_json(PATHS["distil_dedupe_report"])
        result["details"]["distil_dedupe_age_h"] = round(dedup_age, 2)
        if isinstance(dedup_data, dict):
            # Try to extract dupe count
            dup_count = dedup_data.get("duplicate_count") or dedup_data.get("duplicates") or 0
            if isinstance(dup_count, list):
                dup_count = len(dup_count)
            result["details"]["distil_duplicate_count"] = dup_count
        elif isinstance(dedup_data, list):
            result["details"]["distil_duplicate_count"] = len(dedup_data)

    return result


# ---------------------------------------------------------------------------
# L3 Audit — Evolution Layer
# ---------------------------------------------------------------------------

def audit_l3() -> dict:
    result = {
        "layer": "L3 Evolution",
        "health": "GREEN",
        "details": {},
        "issues": [],
    }

    SEVEN_DAYS_H = 7 * 24

    # --- engine_rules.json (primary L3 artifact for recursive engine) ---
    er_age = file_age_hours(PATHS["engine_rules"])
    result["details"]["engine_rules_mtime"] = file_mtime_str(PATHS["engine_rules"])
    engine_rules_data = read_json(PATHS["engine_rules"])
    if er_age is None:
        result["details"]["engine_rules"] = "MISSING"
        result["health"] = "RED"
        result["issues"].append("engine_rules.json MISSING — L3 engine not initialized")
    else:
        result["details"]["engine_rules_age_h"] = round(er_age, 2)
        if engine_rules_data:
            evo_log = engine_rules_data.get("evolution_log", [])
            evolved_at = engine_rules_data.get("evolved_at", "")
            result["details"]["engine_rules_evolved_at"] = evolved_at
            result["details"]["engine_rules_evolution_entries"] = len(evo_log)
            result["details"]["engine_rules_dead_loop_count"] = engine_rules_data.get("dead_loop_count", 0)

            if evo_log:
                last_entry = evo_log[-1]
                result["details"]["engine_rules_last_event"] = last_entry.get("event")
                result["details"]["engine_rules_last_event_ts"] = last_entry.get("ts")

    # --- engine_l3_log.jsonl ---
    l3_log_age = file_age_hours(PATHS["engine_l3_log"])
    result["details"]["engine_l3_log_mtime"] = file_mtime_str(PATHS["engine_l3_log"])
    if l3_log_age is None:
        result["details"]["engine_l3_log"] = "MISSING"
        result["issues"].append("engine_l3_log.jsonl MISSING — no stall events recorded")
    else:
        l3_log_lines = count_jsonl_lines(PATHS["engine_l3_log"])
        result["details"]["engine_l3_log_entries"] = l3_log_lines
        result["details"]["engine_l3_log_age_h"] = round(l3_log_age, 2)

    # --- execution_rules.json (trading L3 artifact) ---
    exec_age = file_age_hours(PATHS["execution_rules"])
    result["details"]["execution_rules_mtime"] = file_mtime_str(PATHS["execution_rules"])
    if exec_age is None:
        result["details"]["execution_rules"] = "MISSING"
    else:
        exec_data = read_json(PATHS["execution_rules"])
        result["details"]["execution_rules_age_h"] = round(exec_age, 2)
        if exec_data:
            result["details"]["execution_rules_kill_count"] = exec_data.get("kill_count")
            result["details"]["execution_rules_evolved_at"] = exec_data.get("evolved_at")

    # --- dna_core.md (LYH agent kernel) ---
    dna_age = file_age_hours(PATHS["dna_core"])
    result["details"]["dna_core_mtime"] = file_mtime_str(PATHS["dna_core"])
    if dna_age is None:
        result["details"]["dna_core"] = "MISSING"
        result["issues"].append("LYH/agent/dna_core.md MISSING")
    else:
        result["details"]["dna_core_age_h"] = round(dna_age, 2)

    # --- dynamic_tree.md (derivative scores) ---
    dt_age = file_age_hours(PATHS["dynamic_tree"])
    result["details"]["dynamic_tree_mtime"] = file_mtime_str(PATHS["dynamic_tree"])
    if dt_age is None:
        result["details"]["dynamic_tree"] = "MISSING"
        result["issues"].append("dynamic_tree.md MISSING — cannot check derivative scores")
    else:
        result["details"]["dynamic_tree_age_h"] = round(dt_age, 2)
        dt_text = read_text(PATHS["dynamic_tree"], tail_chars=3000) or ""
        # Extract derivative scores: "| 1. xxx | 0.0 | ..."
        derivatives = re.findall(r'\|\s*[\d.]+\s*\|', dt_text)
        scores = re.findall(r'Derivative\s*\|\s*([\d.]+)', dt_text)
        if not scores:
            # Try table format: number after branch name column
            scores = re.findall(r'\|\s*([-\d.]+)\s*\|\s*(?:GREEN|YELLOW|RED)', dt_text)
        result["details"]["dynamic_tree_derivative_scores_found"] = len(scores)
        if scores:
            try:
                numeric = [float(s) for s in scores]
                result["details"]["dynamic_tree_scores_sample"] = numeric[:5]
                nonzero = [s for s in numeric if s != 0.0]
                result["details"]["dynamic_tree_nonzero_derivatives"] = len(nonzero)
            except ValueError:
                pass

    # --- dna_evolution_log.jsonl (optional advanced L3) ---
    dna_evo_age = file_age_hours(PATHS["dna_evolution_log"])
    if dna_evo_age is None:
        result["details"]["dna_evolution_log"] = "MISSING"
        # Not a hard RED — this is an optional future artifact
    else:
        result["details"]["dna_evolution_log_age_h"] = round(dna_evo_age, 2)
        result["details"]["dna_evolution_log_entries"] = count_jsonl_lines(
            PATHS["dna_evolution_log"]
        )

    # --- Determine L3 health ---
    # GREEN: engine_rules.json evolved in last 7 days AND has evolution entries
    # YELLOW: exists but stale or minimal entries
    # RED: engine_rules.json missing or never had any evolution events

    if engine_rules_data is None:
        result["health"] = "RED"
        # issue already logged above
    else:
        evo_log = engine_rules_data.get("evolution_log", [])
        evolved_at_str = engine_rules_data.get("evolved_at", "")

        # Try to parse evolved_at
        evolved_age_h = None
        if evolved_at_str:
            for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z",
                        "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
                try:
                    if "+" in evolved_at_str or evolved_at_str.endswith("Z"):
                        dt = datetime.fromisoformat(evolved_at_str.replace("Z", "+00:00"))
                        evolved_age_h = (_NOW - dt.timestamp()) / 3600.0
                    else:
                        dt = datetime.strptime(evolved_at_str[:19], "%Y-%m-%dT%H:%M:%S")
                        evolved_age_h = (_NOW - dt.timestamp()) / 3600.0
                    break
                except (ValueError, AttributeError):
                    continue

        if evolved_age_h is not None:
            result["details"]["engine_rules_evolved_age_h"] = round(evolved_age_h, 2)

        has_real_events = any(
            e.get("event") not in ("INITIALIZED",) for e in evo_log
        )

        if evolved_age_h is not None and evolved_age_h <= SEVEN_DAYS_H and has_real_events:
            result["health"] = "GREEN"
        elif evolved_age_h is not None and evolved_age_h <= SEVEN_DAYS_H:
            result["health"] = "YELLOW"
            result["issues"].append(
                "engine_rules.json exists but evolution_log has no real check events (only INITIALIZED)"
            )
        elif evolved_age_h is not None:
            result["health"] = "YELLOW"
            result["issues"].append(
                f"engine_rules.json evolved_at is {evolved_age_h:.1f}h ago (>7 days threshold)"
            )
        else:
            result["health"] = "YELLOW"
            result["issues"].append(
                "engine_rules.json evolved_at timestamp could not be parsed"
            )

    return result


# ---------------------------------------------------------------------------
# Cross-layer Audit
# ---------------------------------------------------------------------------

def audit_cross_layer(l1: dict, l2: dict, l3: dict) -> dict:
    result = {
        "pipelines": {},
        "issues": [],
    }

    # --- L1→L2: is daemon output feeding digestion? ---
    daemon_age = l1["details"].get("daemon_log_age_h")
    digestion_age = l2["details"].get("digestion_state_age_h")

    if daemon_age is None:
        result["pipelines"]["L1_to_L2"] = "BROKEN"
        result["issues"].append("L1→L2: daemon_log.md missing — cannot verify pipeline")
    elif digestion_age is None:
        result["pipelines"]["L1_to_L2"] = "BROKEN"
        result["issues"].append("L1→L2: digestion_state.json missing — L2 not consuming L1 output")
    elif digestion_age > daemon_age + 12:
        result["pipelines"]["L1_to_L2"] = "DEGRADED"
        result["issues"].append(
            f"L1→L2: digestion ({digestion_age:.1f}h old) lags daemon ({daemon_age:.1f}h old) by >{12}h"
        )
    else:
        result["pipelines"]["L1_to_L2"] = "OK"

    # --- L2→L3: are L2 insights feeding L3 evolution? ---
    engine_rules_data = read_json(PATHS["engine_rules"])
    evo_log = engine_rules_data.get("evolution_log", []) if engine_rules_data else []

    # L3_CHECK events are evidence that L2 insights fed into L3
    l3_check_events = [e for e in evo_log if e.get("event") == "L3_CHECK"]
    memory_count = l2["details"].get("memory_md_count", 0)

    if not engine_rules_data:
        result["pipelines"]["L2_to_L3"] = "BROKEN"
        result["issues"].append("L2→L3: engine_rules.json missing — L3 evolution never initialized")
    elif not l3_check_events:
        result["pipelines"]["L2_to_L3"] = "DEGRADED"
        result["issues"].append(
            "L2→L3: engine_rules.json exists but no L3_CHECK events — "
            "L2 learnings not yet feeding automated L3 evolution"
        )
    else:
        # Check if L3_CHECK events reference insights (loose coupling check)
        result["pipelines"]["L2_to_L3"] = "OK"
        result["details_l3_checks"] = len(l3_check_events)

    # --- L3→L1 feedback: do evolved rules affect execution? ---
    exec_rules_data = read_json(PATHS["execution_rules"])
    engine_rules_evolved_at = (engine_rules_data or {}).get("evolved_at")
    exec_evolved_at = (exec_rules_data or {}).get("evolved_at")

    if exec_rules_data and exec_evolved_at:
        result["pipelines"]["L3_to_L1_feedback"] = "OK"
        result["pipelines"]["L3_to_L1_feedback_detail"] = (
            f"execution_rules.json evolved_at={exec_evolved_at}"
        )
    else:
        result["pipelines"]["L3_to_L1_feedback"] = "DEGRADED"
        result["issues"].append(
            "L3→L1: execution_rules.json missing evolved_at — "
            "cannot confirm L3 rules are feeding back into L1 execution"
        )

    return result


# ---------------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------------

def generate_recommendations(l1: dict, l2: dict, l3: dict, cross: dict) -> list[str]:
    recs = []

    # L1 recs
    if l1["health"] == "RED":
        recs.append("CRITICAL: Restart the recursive daemon — L1 execution is halted")
    elif l1["health"] == "YELLOW":
        recs.append("Investigate L1 slowdown: check daemon process, review last cycle output")

    ss_age = l1["details"].get("session_state_age_h")
    if ss_age and ss_age > 24:
        recs.append(
            "Refresh session_state.md — it is >24h stale; next cold-start will use outdated relay"
        )

    # L2 recs
    if l2["health"] == "RED":
        recs.append("CRITICAL: Digestion pipeline broken — run learning_loop.py to resume L2")
    elif l2["health"] == "YELLOW":
        recs.append("Resume knowledge digestion — progress stalled (check learning_loop.py)")

    dig_pct = l2["details"].get("digestion_progress_pct", 0)
    if dig_pct < 5:
        recs.append(
            f"L2 digestion only {dig_pct:.1f}% complete ({l2['details'].get('digestion_files_done', 0)}"
            f"/{l2['details'].get('digestion_total_known', 0)} files) — "
            "allocate more cycles to learning"
        )

    # L3 recs
    if l3["health"] == "RED":
        recs.append(
            "CRITICAL: L3 evolution layer not initialized — "
            "run recursive_engine.py --l3-check to bootstrap engine_rules.json"
        )
    elif l3["health"] == "YELLOW":
        recs.append(
            "L3 evolution is stale — trigger recursive_engine.py --l3-check "
            "to generate new L3_CHECK event and prove rules are evolving"
        )

    # Cross-layer recs
    if cross["pipelines"].get("L1_to_L2") == "BROKEN":
        recs.append("Wire L1→L2: daemon outputs must feed into digestion_state tracking")
    elif cross["pipelines"].get("L1_to_L2") == "DEGRADED":
        recs.append("Fix L1→L2 lag: digestion is falling behind daemon cycle cadence")

    if cross["pipelines"].get("L2_to_L3") == "BROKEN":
        recs.append(
            "Wire L2→L3 evolution pipeline: "
            "L3_CHECK events in engine_rules.json should reference distillation insights"
        )
    elif cross["pipelines"].get("L2_to_L3") == "DEGRADED":
        recs.append(
            "Automate L2→L3: schedule recursive_engine.py --l3-check every N cycles "
            "so L2 memory insights flow into L3 rule updates automatically"
        )

    if not recs:
        recs.append("All layers healthy — continue current recursive cadence")

    return recs


# ---------------------------------------------------------------------------
# Report Formatting
# ---------------------------------------------------------------------------

_HEALTH_ICONS = {"GREEN": "GREEN ", "YELLOW": "YELLOW", "RED": "RED   "}
_PIPE_ICONS   = {"OK": "OK     ", "DEGRADED": "DEGRADED", "BROKEN": "BROKEN "}


def _health_str(h: str) -> str:
    return _HEALTH_ICONS.get(h, h)


def _pipe_str(p: str) -> str:
    return _PIPE_ICONS.get(p, p)


def format_human(l1: dict, l2: dict, l3: dict, cross: dict, recs: list[str]) -> str:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M +08")
    lines = [
        f"=== L3 System Audit — {now_str} ===",
        "",
    ]

    # Layer summaries
    for layer in (l1, l2, l3):
        h = layer["health"]
        name = layer["layer"]
        details = layer["details"]
        issues = layer["issues"]

        # Build a compact summary line
        if name == "L1 Execution":
            cycles_24h = details.get("daemon_cycles_24h_approx", "?")
            daemon_age = details.get("daemon_log_age_h")
            age_str = f"{daemon_age:.1f}h ago" if daemon_age is not None else "MISSING"
            summary = f"(daemon {age_str}, ~{cycles_24h} timestamps/24h)"

        elif name == "L2 Learning":
            done = details.get("digestion_files_done", "?")
            total = details.get("digestion_total_known", "?")
            dig_age = details.get("digestion_state_age_h")
            age_str = f"{dig_age:.1f}h ago" if dig_age is not None else "MISSING"
            summary = f"(digestion {done}/{total} files, last {age_str})"

        else:  # L3
            evo_entries = details.get("engine_rules_evolution_entries", 0)
            er_evolved = details.get("engine_rules_evolved_at", "unknown")[:16]
            summary = f"(evolution_log {evo_entries} entries, evolved {er_evolved})"

        lines.append(
            f"{name:<20}  {_health_str(h)}  {summary}"
        )
        for issue in issues:
            lines.append(f"  ! {issue}")

    lines.append("")
    lines.append("Cross-layer:")

    pipes = cross["pipelines"]
    for pipe_name, pipe_status in pipes.items():
        if pipe_name.endswith("_detail"):
            continue
        detail = pipes.get(f"{pipe_name}_detail", "")
        detail_str = f" — {detail}" if detail else ""
        lines.append(f"  {pipe_name:<25}  {_pipe_str(pipe_status)}{detail_str}")

    for issue in cross["issues"]:
        lines.append(f"  ! {issue}")

    lines.append("")
    lines.append("Recommendations:")
    for i, rec in enumerate(recs, 1):
        lines.append(f"  {i}. {rec}")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Save report
# ---------------------------------------------------------------------------

def save_report(payload: dict) -> str:
    out_path = _p("results", "l3_audit_report.json")
    try:
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
        return out_path
    except OSError as exc:
        return f"ERROR saving: {exc}"


# ---------------------------------------------------------------------------
# Exit code
# ---------------------------------------------------------------------------

def exit_code(l1: dict, l2: dict, l3: dict) -> int:
    healths = {l1["health"], l2["health"], l3["health"]}
    if "RED" in healths:
        return 2
    if "YELLOW" in healths:
        return 1
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit the L1/L2/L3 three-layer recursive improvement system"
    )
    parser.add_argument(
        "--json", action="store_true", dest="json_output",
        help="Output machine-readable JSON instead of human report"
    )
    parser.add_argument(
        "--no-save", action="store_true",
        help="Skip saving results/l3_audit_report.json"
    )
    args = parser.parse_args()

    l1 = audit_l1()
    l2 = audit_l2()
    l3 = audit_l3()
    cross = audit_cross_layer(l1, l2, l3)
    recs = generate_recommendations(l1, l2, l3, cross)

    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    payload = {
        "audit_ts": now_ts,
        "l1": l1,
        "l2": l2,
        "l3": l3,
        "cross_layer": cross,
        "recommendations": recs,
        "summary": {
            "l1_health": l1["health"],
            "l2_health": l2["health"],
            "l3_health": l3["health"],
            "overall_exit_code": exit_code(l1, l2, l3),
        },
    }

    if args.json_output:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(format_human(l1, l2, l3, cross, recs))

    if not args.no_save:
        saved_path = save_report(payload)
        if not args.json_output:
            print(f"Report saved: {saved_path}")

    sys.exit(exit_code(l1, l2, l3))


if __name__ == "__main__":
    main()
