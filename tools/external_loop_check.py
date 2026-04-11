#!/usr/bin/env python3
"""
external_loop_check.py — G0 state machine for external feedback loop
Reads results/external_signal_log.jsonl → outputs loop status + alerts

Usage:
    python tools/external_loop_check.py
    python tools/external_loop_check.py --verbose
    python tools/external_loop_check.py --dna-check  # exit 1 if violation
    python tools/external_loop_check.py --weekly-review  # log G4 entry

States: PRE_LAUNCH → SEEDING → MONETIZING → SUSTAINABLE
DNA Violation: PRE_LAUNCH for >30 days after mainnet GO = system failure
"""

import json
import sys
import argparse
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

TPE = ZoneInfo("Asia/Taipei")
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
LOG_PATH = REPO_ROOT / "results" / "external_signal_log.jsonl"

# State thresholds
POSTS_FOR_SEEDING = 1
DMS_FOR_MONETIZING = 10
REVENUE_FOR_SUSTAINABLE = 1

# DNA violation thresholds (SOP #65 + SOP #63)
PRE_LAUNCH_HARD_LIMIT_DAYS = 30
ZERO_POST_ALERT_DAYS = 14


def load_log():
    if not LOG_PATH.exists():
        return []
    entries = []
    for line in LOG_PATH.read_text(encoding="utf-8").strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def classify_state(entries):
    counts = {"posts": 0, "dms": 0, "revenue": 0.0, "calibrations": 0}
    mainnet_go_ts = None
    last_post_ts = None

    for e in entries:
        etype = e.get("type", "")
        if etype == "POST":
            counts["posts"] += 1
            last_post_ts = e.get("ts")
        elif etype == "DM":
            counts["dms"] += 1
        elif etype == "REVENUE":
            counts["revenue"] += e.get("amount", 0)
        elif etype == "CALIBRATION":
            counts["calibrations"] += 1
        elif etype == "MAINNET_GO":
            mainnet_go_ts = e.get("ts")

    if counts["revenue"] >= REVENUE_FOR_SUSTAINABLE:
        state = "SUSTAINABLE"
    elif counts["dms"] >= DMS_FOR_MONETIZING:
        state = "MONETIZING"
    elif counts["posts"] >= POSTS_FOR_SEEDING:
        state = "SEEDING"
    else:
        state = "PRE_LAUNCH"

    return state, counts, mainnet_go_ts, last_post_ts


def check_dna_violations(state, counts, mainnet_go_ts, last_post_ts):
    violations = []
    warnings = []
    now = datetime.now(timezone.utc)

    if mainnet_go_ts and state == "PRE_LAUNCH":
        go_dt = datetime.fromisoformat(mainnet_go_ts.replace("Z", "+00:00"))
        days_stale = (now - go_dt).days
        if days_stale > PRE_LAUNCH_HARD_LIMIT_DAYS:
            violations.append(
                f"DNA_VIOLATION: PRE_LAUNCH for {days_stale}d after mainnet GO "
                f"(limit={PRE_LAUNCH_HARD_LIMIT_DAYS}d). SOP #63 G1 → post SOP #01 NOW."
            )
        elif days_stale >= 14:
            warnings.append(
                f"WARNING: PRE_LAUNCH for {days_stale}d since mainnet GO. "
                f"If ≥14d → re-read SOP #63 G1 and escalate to Edward."
            )

    if last_post_ts and counts["posts"] > 0:
        last_dt = datetime.fromisoformat(last_post_ts.replace("Z", "+00:00"))
        days_since = (now - last_dt).days
        if days_since > ZERO_POST_ALERT_DAYS:
            violations.append(
                f"DNA_VIOLATION: {days_since}d since last post (limit={ZERO_POST_ALERT_DAYS}d). "
                f"SOP #65 G5 Case A: post oldest unscheduled thread NOW."
            )

    if counts["posts"] >= 20 and counts["dms"] == 0:
        violations.append(
            f"DNA_VIOLATION: {counts['posts']} posts, 0 DMs. "
            f"SOP #65 G5 Case B: pivot to specific claim that invites disagreement."
        )

    return violations, warnings


def print_status(state, counts, violations, warnings, last_post_ts, verbose=False):
    now_str = datetime.now(TPE).strftime("%Y-%m-%d %H:%M (Taipei)")
    print(f"=== External Loop Status [{now_str}] ===")
    print(f"State:        {state}")
    print(f"Posts:        {counts['posts']}")
    print(f"DMs:          {counts['dms']}")
    print(f"Revenue:      ${counts['revenue']:.2f}")
    print(f"Calibrations: {counts['calibrations']}")
    print(f"Last post:    {last_post_ts or 'NONE'}")

    if violations:
        print()
        for v in violations:
            print(f"[!] {v}")
    if warnings and verbose:
        print()
        for w in warnings:
            print(f"[~] {w}")
    if not violations and not warnings:
        print("No violations.")

    print()
    if state == "PRE_LAUNCH":
        print("NEXT: Post SOP #01 on X (docs/x_launch_sequence.md). Zero friction. Do it now.")
    elif state == "SEEDING":
        print(f"NEXT: Post next thread every 48h. Target: {DMS_FOR_MONETIZING} DMs → MONETIZING.")
    elif state == "MONETIZING":
        print("NEXT: Build Gumroad offer (SOP #34 G2). First DM = first offer.")
    elif state == "SUSTAINABLE":
        print("NEXT: Reinvest per SOP #63 G5. Expand format (SOP #65 G3).")


def append_weekly_review(state, counts):
    entry = {
        # intentional UTC for server log (jsonl archive)
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "type": "G4_WEEKLY_REVIEW",
        "content": (
            f"State={state} posts={counts['posts']} DMs={counts['dms']} "
            f"revenue=${counts['revenue']:.2f} calibrations={counts['calibrations']}"
        ),
        "signal": "neutral"
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"G4 weekly review logged to {LOG_PATH}")


def main():
    parser = argparse.ArgumentParser(description="External loop G0 state machine")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--dna-check", action="store_true", help="Exit 1 if DNA violation")
    parser.add_argument("--weekly-review", action="store_true", help="Log G4 weekly review")
    args = parser.parse_args()

    entries = load_log()
    state, counts, mainnet_go_ts, last_post_ts = classify_state(entries)
    violations, warnings = check_dna_violations(state, counts, mainnet_go_ts, last_post_ts)

    print_status(state, counts, violations, warnings, last_post_ts, verbose=args.verbose)

    if args.weekly_review:
        append_weekly_review(state, counts)

    if args.dna_check and violations:
        sys.exit(1)


if __name__ == "__main__":
    main()
