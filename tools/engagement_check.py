"""
engagement_check.py — Branch 5 G3 Kill Condition Monitor
2026-04-09 UTC (cycle 228)

Reads results/engagement_log.md, flags if kill condition is met.

Kill condition: ≥10 rows with Likes=0 AND Replies=0 → re-audit platform fit (SOP #12 G0)
G0 proof-of-trust milestone: ≥3 DMs total
G2 revenue trigger: ≥10 DMs in any 48h window on a single thread

Usage:
    python tools/engagement_check.py
    python tools/engagement_check.py --log results/engagement_log.md
"""

import sys
import re
import argparse
from pathlib import Path


def parse_engagement_log(path: Path) -> list[dict]:
    """Parse the markdown engagement log table into list of row dicts."""
    rows = []
    in_table = False
    header_skipped = False

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("| Date Posted |"):
            in_table = True
            header_skipped = False
            continue
        if in_table and not header_skipped:
            # skip separator line ---|---|---
            if re.match(r"\|[-| ]+\|", line):
                header_skipped = True
                continue
        if in_table and header_skipped:
            if not line.startswith("|"):
                in_table = False
                continue
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) < 6:
                continue
            date, sop, likes, replies, dms, follows = cells[0], cells[1], cells[2], cells[3], cells[4], cells[5]
            rows.append({
                "date": date,
                "sop": sop,
                "likes": _parse_int(likes),
                "replies": _parse_int(replies),
                "dms": _parse_int(dms),
                "follows": _parse_int(follows),
            })
    return rows


def _parse_int(s: str) -> int | None:
    """Return int or None for —/pending/blank."""
    s = s.strip()
    if s in ("—", "-", "", "(pending)"):
        return None
    try:
        return int(s)
    except ValueError:
        return None


def check_kill_condition(rows: list[dict]) -> dict:
    """
    Kill condition: ≥10 rows with Likes=0 AND Replies=0 (logged, not pending).
    """
    logged = [r for r in rows if r["likes"] is not None and r["replies"] is not None]
    zero_engagement = [r for r in logged if r["likes"] == 0 and r["replies"] == 0]
    total_dms = sum(r["dms"] for r in logged if r["dms"] is not None)
    max_dms_single = max((r["dms"] for r in logged if r["dms"] is not None), default=0)

    kill_triggered = len(zero_engagement) >= 10
    proof_of_trust = total_dms >= 3
    g2_triggered = max_dms_single >= 10

    return {
        "total_logged": len(logged),
        "zero_engagement_rows": len(zero_engagement),
        "total_dms": total_dms,
        "max_dms_single_thread": max_dms_single,
        "kill_triggered": kill_triggered,
        "proof_of_trust_milestone": proof_of_trust,
        "g2_revenue_triggered": g2_triggered,
    }


def main():
    parser = argparse.ArgumentParser(description="Engagement kill condition checker (Branch 5 G3)")
    parser.add_argument("--log", default="results/engagement_log.md", help="Path to engagement_log.md")
    args = parser.parse_args()

    log_path = Path(args.log)
    if not log_path.exists():
        print(f"ERROR: Log file not found: {log_path}")
        sys.exit(1)

    rows = parse_engagement_log(log_path)
    result = check_kill_condition(rows)

    print("=== Engagement Kill Condition Check ===")
    print(f"Log: {log_path}")
    print(f"Posts logged (with data): {result['total_logged']}")
    print(f"Zero-engagement rows:     {result['zero_engagement_rows']}/10 (kill threshold)")
    print(f"Total DMs:                {result['total_dms']} (proof-of-trust ≥3: {'✅' if result['proof_of_trust_milestone'] else '❌'})")
    print(f"Max DMs single thread:    {result['max_dms_single_thread']} (G2 trigger ≥10: {'✅' if result['g2_revenue_triggered'] else '❌'})")
    print()

    if result["kill_triggered"]:
        print("🛑 KILL CONDITION TRIGGERED: ≥10 posts with zero engagement.")
        print("   → Run SOP #12 G0 platform-audience fit re-audit.")
        print("   → Do NOT continue posting until re-audit complete.")
        sys.exit(2)
    elif result["g2_revenue_triggered"]:
        print("💰 G2 REVENUE TRIGGER FIRED: ≥10 DMs on a single thread.")
        print("   → Build PDF workbook now (gumroad_listing_checklist.md).")
        print("   → Post Gumroad link in that thread within 24h.")
    elif result["proof_of_trust_milestone"]:
        print("✅ Proof-of-trust milestone reached (≥3 DMs).")
        print("   → Eligible for first offer (SOP #34 G0). Consider soft DM reply with Gumroad link.")
    elif result["total_logged"] == 0:
        print("⏳ No posts logged yet. Post SOP #01 first.")
        print("   → See docs/x_launch_sequence.md for pre-flight checklist.")
    else:
        print(f"✅ OK: {result['zero_engagement_rows']}/10 zero-engagement posts. Kill condition not triggered.")

    sys.exit(0)


if __name__ == "__main__":
    main()
