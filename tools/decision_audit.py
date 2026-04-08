#!/usr/bin/env python3
"""
decision_audit.py — Life Decision Frequency Auditor

Implements MD-322: 生活系統=最小決策頻率設計；反覆做同一決策=系統設計失敗
(Life systems = minimum decision frequency design; repeating same decision = system failure)

Principle: Any decision made >3 times is a system failure → automate or default it.
Branch 8.4 priority: audit 1-week recurring decisions → automate top 3.

Usage:
    python tools/decision_audit.py log "what to eat for lunch" --domain food
    python tools/decision_audit.py audit
    python tools/decision_audit.py suggest
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

# --- Config --------------------------------------------------------------- #
MEMORY_DIR = Path(__file__).parent.parent / "memory"
AUDIT_FILE = MEMORY_DIR / "decision_audit.json"
FAILURE_THRESHOLD = 3  # >3 occurrences = system failure per MD-322

VALID_DOMAINS = {"food", "finance", "health", "schedule", "work", "social"}

DOMAIN_LABELS = {
    "food":     "Food / Nutrition",
    "finance":  "Finance / Money",
    "health":   "Health / Body",
    "schedule": "Schedule / Time",
    "work":     "Work / Productivity",
    "social":   "Social / Relationships",
}

# Automation suggestions keyed on (domain, normalized decision text fragments).
# Fallback templates are used when no specific match is found.
SUGGESTION_TEMPLATES = {
    "food": (
        "Pre-commit to a rotating meal schedule (e.g. Sun meal-prep covers Mon–Thu lunch). "
        "Eliminate app-scroll entirely. Default = pre-prepared; override trigger = empty fridge only. "
        "See memory/decisions.json key 'meal_default_rotation' for full protocol."
    ),
    "finance": (
        "Automate via bank standing orders or scheduled transfers. "
        "Set calendar reminders for the one annual review instead of ad-hoc decisions. "
        "Rule: if the same financial choice recurs monthly, it should be a direct debit."
    ),
    "health": (
        "Convert to a fixed weekly schedule (days + times locked in calendar as recurring events). "
        "Remove the daily 'should I exercise?' negotiation entirely. "
        "See memory/decisions.json key 'exercise_schedule_fixed' for full protocol."
    ),
    "schedule": (
        "Block recurring time slots in calendar. "
        "Any repeating scheduling decision becomes a standing appointment — no re-confirmation. "
        "Apply MD-323: peak cognitive hours are pre-reserved for high-value work, not renegotiated daily."
    ),
    "work": (
        "Create a SOP or checklist for this task. "
        "If it is a triage decision, set explicit routing rules (if X, always do Y). "
        "Goal: zero-thought execution on the next occurrence."
    ),
    "social": (
        "Establish a fixed cadence (e.g. call parents every Sunday 19:00, team lunch first Friday of month). "
        "Convert from on-demand to scheduled — remove the 'when should we meet?' loop entirely."
    ),
}


# --- State I/O ------------------------------------------------------------ #

def _load() -> dict:
    """Load audit state from disk, returning an empty structure if not found."""
    if not AUDIT_FILE.exists():
        return {"version": 1, "entries": []}
    with AUDIT_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save(state: dict) -> None:
    """Persist audit state to disk."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    with AUDIT_FILE.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def _normalize(text: str) -> str:
    """Lower-case, strip whitespace — used for grouping similar decisions."""
    return text.strip().lower()


# --- Commands ------------------------------------------------------------- #

def cmd_log(decision: str, domain: str, state: dict) -> None:
    """Append a new decision occurrence to the log."""
    if domain not in VALID_DOMAINS:
        print(f"ERROR: domain '{domain}' not recognised. Valid: {', '.join(sorted(VALID_DOMAINS))}")
        sys.exit(1)

    entry = {
        "decision": decision.strip(),
        "domain": domain,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    state["entries"].append(entry)
    _save(state)

    # Count occurrences of this decision (normalized)
    norm = _normalize(decision)
    count = sum(1 for e in state["entries"] if _normalize(e["decision"]) == norm)

    tag = ""
    if count > FAILURE_THRESHOLD:
        tag = f"  🔴 SYSTEM_FAILURE (occurrence #{count} — automate this now)"
    elif count == FAILURE_THRESHOLD:
        tag = f"  🟡 WARNING (occurrence #{count} — one more = system failure)"

    print(f"Logged [{domain}]: \"{decision}\" (total occurrences: {count}){tag}")


def _group_entries(entries: list) -> dict:
    """
    Group entries by (domain, normalized_decision).
    Returns dict: {(domain, norm_text): {"display": str, "count": int, "domain": str}}
    """
    groups: dict = defaultdict(lambda: {"display": "", "domain": "", "count": 0})
    for e in entries:
        key = (e["domain"], _normalize(e["decision"]))
        if groups[key]["count"] == 0:
            groups[key]["display"] = e["decision"]
            groups[key]["domain"] = e["domain"]
        groups[key]["count"] += 1
    return dict(groups)


def cmd_audit(state: dict) -> None:
    """Print frequency analysis; flag decisions exceeding the failure threshold."""
    entries = state.get("entries", [])
    if not entries:
        print("No decisions logged yet. Use: python tools/decision_audit.py log \"...\" --domain <domain>")
        return

    groups = _group_entries(entries)

    # Sort: highest frequency first
    sorted_groups = sorted(groups.items(), key=lambda kv: kv[1]["count"], reverse=True)

    # Determine column widths
    max_decision_len = max(len(v["display"]) for v in groups.values())
    max_decision_len = max(max_decision_len, len("Decision"))

    header_domain = "Domain"
    header_count = "Count"
    header_status = "Status"

    col_d = max_decision_len + 2
    col_dom = max(len(DOMAIN_LABELS[d]) for d in VALID_DOMAINS) + 2
    col_c = 7
    col_s = 30

    # Header
    print()
    print("=" * 80)
    print("  LIFE DECISION FREQUENCY AUDIT  |  MD-322: >3 occurrences = SYSTEM_FAILURE")
    print("=" * 80)
    print(f"  {'Decision':<{col_d}} {'Domain':<{col_dom}} {'Count':>{col_c}}  {header_status}")
    print(f"  {'-' * col_d} {'-' * col_dom} {'-' * col_c}  {'-' * col_s}")

    failure_count = 0
    warning_count = 0
    for (domain, _norm), info in sorted_groups:
        count = info["count"]
        display = info["display"]
        domain_label = DOMAIN_LABELS.get(domain, domain)

        if count > FAILURE_THRESHOLD:
            status = "🔴 SYSTEM_FAILURE — automate/default"
            failure_count += 1
        elif count == FAILURE_THRESHOLD:
            status = "🟡 AT THRESHOLD — pre-commit now"
            warning_count += 1
        else:
            status = "✅ OK"

        print(f"  {display:<{col_d}} {domain_label:<{col_dom}} {count:>{col_c}}  {status}")

    print()
    total = len(entries)
    unique = len(groups)
    print(f"  Total logged: {total} decisions  |  Unique: {unique}  |  "
          f"Failures: {failure_count}  |  At threshold: {warning_count}")
    print()
    if failure_count:
        print(f"  ACTION REQUIRED: {failure_count} decision(s) exceed the 3-occurrence threshold.")
        print("  Run `python tools/decision_audit.py suggest` for automation recommendations.")
    print("=" * 80)
    print()


def cmd_suggest(state: dict) -> None:
    """For each system-failure decision, output a specific automation suggestion."""
    entries = state.get("entries", [])
    if not entries:
        print("No decisions logged yet.")
        return

    groups = _group_entries(entries)
    failures = {k: v for k, v in groups.items() if v["count"] > FAILURE_THRESHOLD}

    if not failures:
        print("No system failures detected yet (no decision exceeds 3 occurrences).")
        print("Keep logging — run `python tools/decision_audit.py audit` to review status.")
        return

    # Sort by count descending — highest-frequency gets addressed first (highest ROI)
    sorted_failures = sorted(failures.items(), key=lambda kv: kv[1]["count"], reverse=True)

    print()
    print("=" * 80)
    print("  AUTOMATION SUGGESTIONS  |  High-frequency decisions → pre-commit / automate")
    print("  Priority order: highest frequency first (= highest decision-resource ROI)")
    print("=" * 80)

    for rank, ((domain, _norm), info) in enumerate(sorted_failures, start=1):
        count = info["count"]
        display = info["display"]
        domain_label = DOMAIN_LABELS.get(domain, domain)
        suggestion = SUGGESTION_TEMPLATES.get(domain, "Define a default rule and document it in memory/.")

        print()
        print(f"  [{rank}] 🔴 \"{display}\"")
        print(f"      Domain    : {domain_label}")
        print(f"      Frequency : {count} occurrences (failure threshold: >{FAILURE_THRESHOLD})")
        print(f"      Severity  : {'CRITICAL' if count >= FAILURE_THRESHOLD * 2 else 'HIGH'}")
        print()
        print(f"      SUGGESTED DEFAULT:")
        # Wrap suggestion text at ~70 chars for readability
        words = suggestion.split()
        line = "      "
        for word in words:
            if len(line) + len(word) + 1 > 78:
                print(line)
                line = "      " + word + " "
            else:
                line += word + " "
        if line.strip():
            print(line)

    print()
    print("-" * 80)
    print("  NEXT STEPS (MD-322 SOP):")
    print("  1. Pick the top 1–3 failures above.")
    print("  2. Write a default rule (pre-commit, schedule, or automate).")
    print("  3. Log the decision in memory/decisions.json with source='branch_8.4'.")
    print("  4. Stop logging that decision — it is no longer a decision.")
    print("=" * 80)
    print()


# --- Pre-populate realistic seed data ------------------------------------- #

SEED_ENTRIES = [
    # Food decisions — repeated heavily across a week
    {"decision": "What to eat for lunch",       "domain": "food",     "timestamp": "2026-04-01T12:05:00Z"},
    {"decision": "What to eat for lunch",       "domain": "food",     "timestamp": "2026-04-02T12:10:00Z"},
    {"decision": "What to eat for lunch",       "domain": "food",     "timestamp": "2026-04-03T11:58:00Z"},
    {"decision": "What to eat for lunch",       "domain": "food",     "timestamp": "2026-04-04T12:20:00Z"},
    {"decision": "What to eat for lunch",       "domain": "food",     "timestamp": "2026-04-07T12:03:00Z"},
    # Breakfast variation
    {"decision": "Whether to have coffee or tea at breakfast", "domain": "food", "timestamp": "2026-04-01T08:00:00Z"},
    {"decision": "Whether to have coffee or tea at breakfast", "domain": "food", "timestamp": "2026-04-02T07:55:00Z"},
    {"decision": "Whether to have coffee or tea at breakfast", "domain": "food", "timestamp": "2026-04-03T08:10:00Z"},
    {"decision": "Whether to have coffee or tea at breakfast", "domain": "food", "timestamp": "2026-04-04T08:05:00Z"},
    # Exercise decisions
    {"decision": "Whether to exercise today",   "domain": "health",   "timestamp": "2026-04-01T07:00:00Z"},
    {"decision": "Whether to exercise today",   "domain": "health",   "timestamp": "2026-04-02T07:05:00Z"},
    {"decision": "Whether to exercise today",   "domain": "health",   "timestamp": "2026-04-03T06:55:00Z"},
    {"decision": "Whether to exercise today",   "domain": "health",   "timestamp": "2026-04-04T07:10:00Z"},
    {"decision": "Whether to exercise today",   "domain": "health",   "timestamp": "2026-04-05T08:00:00Z"},
    {"decision": "Whether to exercise today",   "domain": "health",   "timestamp": "2026-04-07T07:30:00Z"},
    # Schedule: when to start deep work
    {"decision": "When to start deep work block", "domain": "schedule", "timestamp": "2026-04-01T09:00:00Z"},
    {"decision": "When to start deep work block", "domain": "schedule", "timestamp": "2026-04-02T09:15:00Z"},
    {"decision": "When to start deep work block", "domain": "schedule", "timestamp": "2026-04-03T09:05:00Z"},
    {"decision": "When to start deep work block", "domain": "schedule", "timestamp": "2026-04-04T08:50:00Z"},
    {"decision": "When to start deep work block", "domain": "schedule", "timestamp": "2026-04-07T09:00:00Z"},
    # Finance: checking account balance
    {"decision": "Whether to check portfolio / account balance today", "domain": "finance", "timestamp": "2026-04-01T20:00:00Z"},
    {"decision": "Whether to check portfolio / account balance today", "domain": "finance", "timestamp": "2026-04-02T19:45:00Z"},
    {"decision": "Whether to check portfolio / account balance today", "domain": "finance", "timestamp": "2026-04-03T20:10:00Z"},
    {"decision": "Whether to check portfolio / account balance today", "domain": "finance", "timestamp": "2026-04-04T20:05:00Z"},
    # Social: response time
    {"decision": "When to reply to non-urgent messages", "domain": "social", "timestamp": "2026-04-01T14:00:00Z"},
    {"decision": "When to reply to non-urgent messages", "domain": "social", "timestamp": "2026-04-02T13:55:00Z"},
    {"decision": "When to reply to non-urgent messages", "domain": "social", "timestamp": "2026-04-03T14:30:00Z"},
    # Work: task prioritisation at start of day
    {"decision": "Which task to tackle first this morning", "domain": "work", "timestamp": "2026-04-01T09:02:00Z"},
    {"decision": "Which task to tackle first this morning", "domain": "work", "timestamp": "2026-04-02T09:10:00Z"},
    {"decision": "Which task to tackle first this morning", "domain": "work", "timestamp": "2026-04-03T08:58:00Z"},
    # One-off decisions (no recurrence — these are fine)
    {"decision": "Whether to renew apartment lease",       "domain": "finance",  "timestamp": "2026-04-05T10:00:00Z"},
    {"decision": "Whether to attend optional team meeting", "domain": "work",    "timestamp": "2026-04-03T15:00:00Z"},
]


def cmd_seed(state: dict) -> None:
    """Pre-populate the audit log with a realistic week of Edward's decisions."""
    existing_timestamps = {e["timestamp"] for e in state.get("entries", [])}
    added = 0
    for entry in SEED_ENTRIES:
        if entry["timestamp"] not in existing_timestamps:
            state["entries"].append(dict(entry))
            added += 1
    _save(state)
    print(f"Seed data loaded: {added} entries added ({len(SEED_ENTRIES) - added} already present).")
    print("Run `python tools/decision_audit.py audit` to see the full analysis.")


# --- CLI ------------------------------------------------------------------ #

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="decision_audit.py",
        description=(
            "Life Decision Frequency Auditor — MD-322\n"
            "Any decision made >3 times = system failure → automate/default it."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # log
    p_log = sub.add_parser("log", help="Log a decision occurrence")
    p_log.add_argument("decision", help="Description of the decision made")
    p_log.add_argument("--domain", required=True,
                       choices=sorted(VALID_DOMAINS),
                       help="Life domain: food | finance | health | schedule | work | social")

    # audit
    sub.add_parser("audit", help="Show frequency analysis; flag system failures")

    # suggest
    sub.add_parser("suggest", help="Print automation suggestions for high-frequency decisions")

    # seed (utility — pre-populate realistic data)
    sub.add_parser("seed", help="Pre-populate with a realistic week of sample decisions")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    state = _load()

    if args.command == "log":
        cmd_log(args.decision, args.domain, state)
    elif args.command == "audit":
        cmd_audit(state)
    elif args.command == "suggest":
        cmd_suggest(state)
    elif args.command == "seed":
        cmd_seed(state)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
