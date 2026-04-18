#!/usr/bin/env python3
"""reclass5_trip_override.py

Cycle475 (2026-04-15): apply TRIP_DATE_OVERRIDES to existing
finance_spending.jsonl. For each row whose `date` falls within a trip
window (inclusive), overwrite `category` to the trip category.

Exception: rows with category == "Poker" are left untouched (privacy).

Backup already taken as finance_spending.jsonl.bak_reclass5.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from spending_csv_ingest import TRIP_DATE_OVERRIDES

REPO = Path("C:/Users/admin/workspace/digital-immortality")
SRC = REPO / "results" / "finance_spending.jsonl"


def _in_any_window(date: str) -> str | None:
    if not date:
        return None
    for start, end, cat in TRIP_DATE_OVERRIDES:
        if start <= date <= end:
            return cat
    return None


def main() -> int:
    lines = SRC.read_text(encoding="utf-8").splitlines()
    changed = 0
    poker_skipped = 0
    before_counts: Counter[str] = Counter()
    after_counts: Counter[str] = Counter()
    window_total = 0
    out_lines: list[str] = []

    for line in lines:
        line = line.strip()
        if not line:
            out_lines.append("")
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            out_lines.append(line)
            continue
        date = str(obj.get("date") or "")
        cat_before = str(obj.get("category") or "")
        target = _in_any_window(date)
        if target is not None:
            window_total += 1
            before_counts[cat_before] += 1
            if cat_before == "Poker":
                poker_skipped += 1
                after_counts[cat_before] += 1
            elif cat_before != target:
                obj["category"] = target
                changed += 1
                after_counts[target] += 1
            else:
                after_counts[cat_before] += 1
        out_lines.append(json.dumps(obj, ensure_ascii=False))

    SRC.write_text("\n".join(out_lines) + ("\n" if lines and lines[-1] == "" else ""), encoding="utf-8")
    # Ensure trailing newline consistent with jsonl:
    if not SRC.read_text(encoding="utf-8").endswith("\n"):
        with SRC.open("a", encoding="utf-8") as f:
            f.write("\n")

    print(f"window rows total: {window_total}")
    print(f"changed (non-Poker reclassified to target): {changed}")
    print(f"poker_skipped: {poker_skipped}")
    print("before (within window):")
    for k, v in sorted(before_counts.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    print("after (within window):")
    for k, v in sorted(after_counts.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
