#!/usr/bin/env python3
"""
Daily Posting Helper — SOP Series
Run each day to see what to post, confirm after posting, and track signals.
Usage:
  python platform/daily_posting_helper.py           # show today's schedule
  python platform/daily_posting_helper.py --confirm # mark today's SOP as posted
  python platform/daily_posting_helper.py --signal replies=5 saves=12 dms=1  # log engagement
  python platform/daily_posting_helper.py --status  # show full queue status
  python platform/daily_posting_helper.py --evolve saves=12 dms=2 sop=#03  # L3: update execution rules
  python platform/daily_posting_helper.py --l2-audit  # L2: 7-day coverage + anomaly report
"""

import argparse
import json
import re
import sys
from datetime import datetime, date, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).parent.parent
QUEUE_FILE = REPO_ROOT / "docs" / "posting_queue.md"
DOCS_DIR = REPO_ROOT / "docs"
PLATFORM_DIR = Path(__file__).parent
CONTENT_RULES_PATH = PLATFORM_DIR / "content_execution_rules.json"
CONTENT_LESSONS_PATH = PLATFORM_DIR / "content_evolution_log.jsonl"

DEFAULT_CONTENT_RULES: Dict = {
    "version": 1,
    "last_updated": None,
    "rules": {
        "min_post_interval_days": 1,
        "max_post_gap_days": 2,
        "engagement_threshold_saves": 5,
        "engagement_threshold_dms": 1,
        "format_weights": {},
    },
    "evolution_log": [],
}

TODAY = date.today()
TODAY_STR = TODAY.strftime("%b %-d")  # e.g. "Apr 9"


def parse_queue():
    """Parse posting_queue.md table into list of dicts."""
    rows = []
    in_table = False
    text = QUEUE_FILE.read_text()
    for line in text.splitlines():
        if line.startswith("| Date |"):
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and line.startswith("|"):
            cols = [c.strip() for c in line.strip("|").split("|")]
            if len(cols) >= 5:
                rows.append({
                    "date": cols[0],
                    "sop": cols[1],
                    "file": cols[2],
                    "hook": cols[3],
                    "status": cols[4],
                })
        elif in_table and not line.startswith("|"):
            in_table = False
    return rows


def find_today(rows):
    """Find the row scheduled for today."""
    for row in rows:
        if row["date"] == TODAY_STR:
            return row
    return None


def find_next_pending(rows):
    """Find the next pending row."""
    for row in rows:
        if row["status"].lower() == "pending":
            return row
    return None


def show_thread(sop_num: str):
    """Print the thread content for the given SOP number."""
    # sop_num is like "#01"
    num = sop_num.lstrip("#").zfill(2)
    thread_file = DOCS_DIR / f"publish_thread_sop{num}_twitter.md"
    if not thread_file.exists():
        print(f"  [!] Thread file not found: {thread_file.name}")
        return
    content = thread_file.read_text()
    print("\n" + "=" * 60)
    print(f"  THREAD CONTENT — SOP {sop_num}")
    print("=" * 60)
    print(content)
    print("=" * 60)


def mark_posted(sop_num: str):
    """Update posting_queue.md to mark sop_num as posted."""
    text = QUEUE_FILE.read_text()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    # Replace the pending status for this SOP
    pattern = rf"(\| {TODAY_STR} \| {re.escape(sop_num)} \|.*?\| )pending"
    replacement = rf"\1posted {timestamp}"
    new_text = re.sub(pattern, replacement, text)
    if new_text == text:
        print(f"  [!] Could not find '{TODAY_STR} | {sop_num}' as pending in queue.")
        return False
    QUEUE_FILE.write_text(new_text)
    print(f"  [✓] Marked SOP {sop_num} as posted at {timestamp}")
    return True


def log_signal(sop_num: str, replies: int, saves: int, dms: int):
    """Append a row to the Signal Log section of posting_queue.md."""
    text = QUEUE_FILE.read_text()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Determine hook verdict
    if replies == 0 and saves == 0:
        verdict = "WEAK — rewrite hook before next"
    elif dms >= 1:
        verdict = "STRONG — DM received"
    elif saves >= 10:
        verdict = "GOOD — high saves"
    elif replies >= 3:
        verdict = "OK — some replies"
    else:
        verdict = "WEAK — low signal"

    gumroad_action = "WAIT" if dms < 10 else f"TRIGGER GUMROAD — {dms} DMs ≥ 10"

    new_row = f"| {now} | {sop_num} | {replies} | {saves} | {dms} | {verdict} | {gumroad_action} |"

    # Replace the placeholder row if it exists
    placeholder = "| — | — | — | — | — | — | — |"
    if placeholder in text:
        text = text.replace(placeholder, new_row, 1)
    else:
        # Append after last signal log row
        # Find the signal log section
        idx = text.find("## Signal Log")
        if idx == -1:
            print("  [!] Signal Log section not found.")
            return
        # Find end of table in signal log section
        section = text[idx:]
        lines = section.splitlines()
        insert_after = -1
        in_tbl = False
        for i, line in enumerate(lines):
            if line.startswith("| Date |"):
                in_tbl = True
            elif in_tbl and line.startswith("|"):
                insert_after = i
            elif in_tbl:
                break
        if insert_after >= 0:
            lines.insert(insert_after + 1, new_row)
            text = text[:idx] + "\n".join(lines) + text[idx + len(section):]
        else:
            print("  [!] Could not locate signal log table end.")
            return

    QUEUE_FILE.write_text(text)
    print(f"  [✓] Signal logged: SOP {sop_num} | replies={replies} saves={saves} dms={dms}")
    print(f"      Verdict: {verdict}")
    print(f"      Action: {gumroad_action}")

    if dms >= 10:
        print()
        print("  ⚡ GUMROAD TRIGGER REACHED! List workbooks now:")
        print("     → docs/gumroad_listing_draft.md  (copy-paste ready)")


def show_status(rows):
    """Print full queue status summary."""
    posted = [r for r in rows if "posted" in r["status"].lower()]
    pending = [r for r in rows if r["status"].lower() == "pending"]
    print(f"\n  Queue status ({TODAY_STR}):")
    print(f"    Posted:  {len(posted):2d} / {len(rows)}")
    print(f"    Pending: {len(pending):2d} / {len(rows)}")
    print()
    if posted:
        print("  Posted:")
        for r in posted[-5:]:  # last 5
            print(f"    [{r['date']}] {r['sop']} — {r['status']}")
    if pending:
        print("  Next 5 pending:")
        for r in pending[:5]:
            print(f"    [{r['date']}] {r['sop']} — {r['hook'][:60]}...")
    print()


def check_dms_from_signal_log():
    """Count total DMs from signal log rows."""
    text = QUEUE_FILE.read_text()
    idx = text.find("## Signal Log")
    if idx == -1:
        return 0
    section = text[idx:]
    total_dms = 0
    for line in section.splitlines():
        if line.startswith("|") and "DM" not in line and "—" not in line and "Date" not in line and "---" not in line:
            cols = [c.strip() for c in line.strip("|").split("|")]
            if len(cols) >= 5:
                try:
                    total_dms += int(cols[4])
                except ValueError:
                    pass
    return total_dms


# ---------------------------------------------------------------------------
# L3 Evolve — modify content execution rules based on engagement signals
# ---------------------------------------------------------------------------

def load_content_rules() -> Dict:
    """Load content execution rules from disk, falling back to defaults."""
    if CONTENT_RULES_PATH.exists():
        return json.loads(CONTENT_RULES_PATH.read_text())
    return json.loads(json.dumps(DEFAULT_CONTENT_RULES))  # deep copy via json


def save_content_rules(rules: Dict) -> None:
    """Persist updated execution rules to disk."""
    CONTENT_RULES_PATH.write_text(json.dumps(rules, indent=2))


def log_evolution_event(event: Dict) -> None:
    """Append an evolution event to content_evolution_log.jsonl."""
    with open(CONTENT_LESSONS_PATH, "a") as f:
        f.write(json.dumps(event) + "\n")


def evolve_content_rules(saves: int, dms: int, sop: str) -> Dict:
    """L3 Evolve: read engagement signals, update execution rules, log change.

    Rules:
    - saves >= engagement_threshold_saves  → decrease min_post_interval (post more often)
    - dms >= engagement_threshold_dms      → increase format weight for the given SOP type
    """
    rules = load_content_rules()
    r = rules["rules"]
    now_iso = datetime.now(timezone.utc).isoformat()
    changes: List[str] = []

    saves_threshold = r.get("engagement_threshold_saves", 5)
    dms_threshold = r.get("engagement_threshold_dms", 1)

    # Saves signal: high engagement → reduce posting interval (post more frequently)
    if saves >= saves_threshold:
        old_interval = r.get("min_post_interval_days", 1)
        new_interval = max(1, old_interval - 1)
        r["min_post_interval_days"] = new_interval
        changes.append(
            f"min_post_interval_days: {old_interval} → {new_interval} "
            f"(saves={saves} >= threshold={saves_threshold})"
        )

    # DM signal: high intent → boost format weight for this SOP type
    if dms >= dms_threshold:
        sop_key = sop.lstrip("#").lower()
        fw = r.get("format_weights", {})
        old_weight = fw.get(sop_key, 1.0)
        new_weight = round(old_weight + 0.5, 2)
        fw[sop_key] = new_weight
        r["format_weights"] = fw
        changes.append(
            f"format_weights[{sop_key}]: {old_weight} → {new_weight} "
            f"(dms={dms} >= threshold={dms_threshold})"
        )

    if not changes:
        print(f"  [L3] No rule changes — signals below thresholds "
              f"(saves={saves}<{saves_threshold}, dms={dms}<{dms_threshold})")
        return rules

    rules["last_updated"] = now_iso
    evolution_entry = {
        "ts": now_iso,
        "sop": sop,
        "input": {"saves": saves, "dms": dms},
        "changes": changes,
    }
    rules.setdefault("evolution_log", []).append(evolution_entry)

    save_content_rules(rules)
    log_evolution_event(evolution_entry)

    print(f"  [L3 Evolve] Rules updated at {now_iso}")
    for c in changes:
        print(f"    • {c}")
    return rules


# ---------------------------------------------------------------------------
# L2 Audit — 7-day coverage report with anomaly detection
# ---------------------------------------------------------------------------

def read_signal_log_rows() -> List[Dict]:
    """Parse all signal log rows from posting_queue.md."""
    text = QUEUE_FILE.read_text()
    idx = text.find("## Signal Log")
    if idx == -1:
        return []
    section = text[idx:]
    rows = []
    for line in section.splitlines():
        if (line.startswith("|")
                and "Date" not in line
                and "---" not in line
                and "—" not in line
                and "DM" not in line):
            cols = [c.strip() for c in line.strip("|").split("|")]
            if len(cols) >= 5:
                try:
                    rows.append({
                        "date": cols[0],
                        "sop": cols[1],
                        "replies": int(cols[2]),
                        "saves": int(cols[3]),
                        "dms": int(cols[4]),
                        "verdict": cols[5] if len(cols) > 5 else "",
                    })
                except ValueError:
                    pass
    return rows


def l2_audit() -> Dict:
    """L2 Audit: 7-day coverage report on posts shipped, queue compliance, DMs.

    Returns an audit dict and prints a human-readable report.
    """
    cutoff = date.today() - timedelta(days=7)
    rows = parse_queue()
    signals = read_signal_log_rows()
    rules = load_content_rules()
    r = rules["rules"]

    # Posts shipped in last 7 days
    posted_recent: List[Dict] = []
    for row in rows:
        try:
            row_date = datetime.strptime(row["date"] + f" {date.today().year}", "%b %d %Y").date()
        except ValueError:
            continue
        if row_date >= cutoff and "posted" in row["status"].lower():
            posted_recent.append(row)

    posts_shipped = len(posted_recent)

    # Queue compliance: pending rows that are overdue
    overdue: List[Dict] = []
    for row in rows:
        if row["status"].lower() != "pending":
            continue
        try:
            row_date = datetime.strptime(row["date"] + f" {date.today().year}", "%b %d %Y").date()
        except ValueError:
            continue
        if row_date < date.today():
            overdue.append(row)

    # Engagement summary from signal log (last 7 days)
    total_dms = 0
    total_saves = 0
    total_replies = 0
    weak_posts = []
    for sig in signals:
        try:
            sig_date = datetime.strptime(sig["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        if sig_date >= cutoff:
            total_dms += sig["dms"]
            total_saves += sig["saves"]
            total_replies += sig["replies"]
            if "WEAK" in sig.get("verdict", "").upper():
                weak_posts.append(sig["sop"])

    # Anomaly detection
    anomalies: List[str] = []
    max_gap = r.get("max_post_gap_days", 2)
    if overdue:
        anomalies.append(f"{len(overdue)} post(s) overdue (past schedule, still pending)")
    if posts_shipped == 0:
        anomalies.append("No posts shipped in last 7 days — pipeline stalled")
    if weak_posts:
        anomalies.append(f"Weak engagement on: {', '.join(weak_posts)}")
    if total_dms == 0:
        anomalies.append("Zero DMs received in last 7 days — hook strength low")

    audit = {
        "audit_date": date.today().isoformat(),
        "window_days": 7,
        "posts_shipped": posts_shipped,
        "overdue_count": len(overdue),
        "overdue_sops": [r_["sop"] for r_ in overdue],
        "engagement": {
            "total_saves": total_saves,
            "total_replies": total_replies,
            "total_dms": total_dms,
        },
        "weak_posts": weak_posts,
        "anomalies": anomalies,
        "queue_compliance": "OK" if not overdue else "FAIL",
    }

    # Print human-readable report
    print(f"\n  {'=' * 50}")
    print(f"  L2 AUDIT — last 7 days (since {cutoff})")
    print(f"  {'=' * 50}")
    print(f"  Posts shipped:    {posts_shipped}")
    print(f"  Overdue pending:  {len(overdue)}")
    print(f"  Saves:  {total_saves}  Replies: {total_replies}  DMs: {total_dms}")
    print(f"  Queue compliance: {audit['queue_compliance']}")
    if anomalies:
        print(f"\n  ANOMALIES ({len(anomalies)}):")
        for a in anomalies:
            print(f"    [!] {a}")
    else:
        print("\n  No anomalies detected.")
    print()

    return audit


def main():
    parser = argparse.ArgumentParser(description="Daily SOP posting helper")
    parser.add_argument("--confirm", action="store_true", help="Mark today's SOP as posted")
    parser.add_argument("--signal", nargs="*", metavar="KEY=VAL", help="Log engagement: replies=N saves=N dms=N")
    parser.add_argument("--status", action="store_true", help="Show full queue status")
    parser.add_argument("--show-thread", metavar="SOP", help="Print thread content (e.g. #01)")
    parser.add_argument("--evolve", nargs="*", metavar="KEY=VAL",
                        help="L3: update content execution rules from signals (saves=N dms=N sop=#NN)")
    parser.add_argument("--l2-audit", action="store_true",
                        help="L2: 7-day coverage + anomaly report")
    args = parser.parse_args()

    rows = parse_queue()
    today_row = find_today(rows)
    next_row = find_next_pending(rows)

    print(f"\n{'=' * 50}")
    print(f"  DAILY POSTING HELPER — {TODAY_STR}")
    print(f"{'=' * 50}")

    if args.l2_audit:
        l2_audit()
        return

    if args.evolve is not None:
        kv: Dict[str, str] = {}
        for item in (args.evolve or []):
            k, _, v = item.partition("=")
            kv[k.strip()] = v.strip()
        sop = kv.get("sop", today_row["sop"] if today_row else (next_row["sop"] if next_row else "#01"))
        evolve_content_rules(
            saves=int(kv.get("saves", 0)),
            dms=int(kv.get("dms", 0)),
            sop=sop,
        )
        return

    if args.status:
        show_status(rows)
        return

    if args.show_thread:
        show_thread(args.show_thread)
        return

    if args.signal:
        # Parse key=value pairs
        kv = {}
        for item in args.signal:
            k, _, v = item.partition("=")
            kv[k.strip()] = int(v.strip())
        sop = today_row["sop"] if today_row else (next_row["sop"] if next_row else "#01")
        log_signal(sop, kv.get("replies", 0), kv.get("saves", 0), kv.get("dms", 0))
        return

    if args.confirm:
        if today_row:
            ok = mark_posted(today_row["sop"])
            if ok:
                total_dms = check_dms_from_signal_log()
                if total_dms >= 10:
                    print(f"\n  ⚡ GUMROAD TRIGGER: {total_dms} DMs total — list workbooks NOW")
                    print("     → docs/gumroad_listing_draft.md")
        else:
            print(f"  [!] No SOP scheduled for {TODAY_STR}.")
            if next_row:
                print(f"  Next scheduled: [{next_row['date']}] {next_row['sop']}")
        return

    # Default: show what to do today
    if today_row:
        print(f"\n  TODAY'S TASK: Post SOP {today_row['sop']}")
        print(f"  Status: {today_row['status']}")
        print(f"  Hook:   {today_row['hook']}")
        print(f"  File:   docs/{today_row['file']}")
        print()
        print("  Steps:")
        print(f"  1. Open docs/{today_row['file']}")
        print("  2. Copy tweet 1 → post on X")
        print("  3. Reply to tweet 1 with tweets 2–12 in sequence")
        print("  4. Run: python platform/daily_posting_helper.py --confirm")
        print("  5. After 48h: run --signal replies=N saves=N dms=N")
    else:
        print(f"\n  No SOP scheduled for {TODAY_STR}.")
        if next_row:
            print(f"  Next scheduled: [{next_row['date']}] {next_row['sop']} — {next_row['hook'][:55]}...")

    total_dms = check_dms_from_signal_log()
    print(f"\n  DM count: {total_dms}/10 (Gumroad trigger at 10)")
    print(f"  Gumroad: {'⚡ TRIGGER NOW' if total_dms >= 10 else f'{10 - total_dms} more DMs needed'}")
    print()


if __name__ == "__main__":
    main()
