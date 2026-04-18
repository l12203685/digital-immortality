#!/usr/bin/env python3
"""reclassify_spending_v2.py  (cycle 472, targeted)

TARGETED re-classification. Preserves manual/ledger categories, only
touches rows that match the two fixes in this cycle:

  FIX 1: 龍角 (飲料店) -> 餐飲  (was 醫療 / 日用)
         Never 醫療 — 龍角 is a drink shop, not a pharmacy.
  FIX 2: 旅遊 (new category) for:
         - 國外交易手續費 / foreign transaction fee / 外幣手續費
         - Expedia / Booking / Agoda / Airbnb / KKday / Klook / Trip.com
         - 航空 / Airlines / Airways / 機票 / 租車 / Rental car
         - 景點門票 / 樂園 / 主題公園 / 博物館門票 / 溫泉
         - 度假村 / Resort / Hotel / 旅館 / 民宿 / Hostel / Ryokan

Poker category is NEVER touched (private coding).

Backup -> finance_spending.jsonl.bak_reclass2 (one-shot, not overwritten).
"""
from __future__ import annotations

import json
import shutil
from collections import Counter
from pathlib import Path

JSONL = Path(
    "C:/Users/admin/workspace/digital-immortality/results/finance_spending.jsonl"
)
BAK = JSONL.with_suffix(".jsonl.bak_reclass2")

TRAVEL_KEYWORDS: tuple[str, ...] = (
    "國外交易手續費", "foreign transaction fee", "外幣手續費",
    "expedia", "booking.com", "agoda", "airbnb", "kkday", "klook",
    "trip.com", "hotels.com",
    "航空", "airlines", "airways", "機票",
    "租車", "rental car", "hertz", "avis",
    "景點門票", "樂園", "主題公園", "博物館門票", "溫泉",
    "度假村", "resort ", "resort-",
    "hotel ", "hotel-", "旅館", "民宿", "hostel", "ryokan", "villa",
)


def _has_travel_signal(merchant: str, note: str) -> bool:
    hay = f"{merchant} {note}".lower()
    return any(kw.lower() in hay for kw in TRAVEL_KEYWORDS)


def main() -> int:
    if not JSONL.exists():
        print(f"missing: {JSONL}")
        return 1
    if not BAK.exists():
        shutil.copy2(JSONL, BAK)
        print(f"backup -> {BAK.name}")
    else:
        print(f"backup exists: {BAK.name} (preserved)")

    rows: list[dict] = []
    with JSONL.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    before = Counter(str(r.get("category") or "其他") for r in rows)

    long_jiao_from_medical = 0
    long_jiao_from_nonfood = 0
    travel_added = 0
    travel_from: Counter[str] = Counter()

    for row in rows:
        old = str(row.get("category") or "其他")
        if old == "Poker":
            continue
        merchant = str(row.get("merchant") or "")
        note = str(row.get("note") or "")

        # --- FIX 1: 龍角 -> 餐飲 ---
        if "龍角" in merchant and old != "餐飲":
            if old == "醫療":
                long_jiao_from_medical += 1
            else:
                long_jiao_from_nonfood += 1
            row["category"] = "餐飲"
            continue

        # --- FIX 2: travel signals -> 旅遊 ---
        if _has_travel_signal(merchant, note) and old != "旅遊":
            # Only reroute from categories where travel mis-classification
            # is plausible: 交通 / 娛樂 / 固定費用 / 其他 / 購物.
            if old in ("交通", "娛樂", "固定費用", "其他", "購物", ""):
                travel_from[old] += 1
                row["category"] = "旅遊"
                travel_added += 1

    with JSONL.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    after = Counter(str(r.get("category") or "其他") for r in rows)

    print("\n=== BEFORE counts ===")
    for cat, n in sorted(before.items(), key=lambda kv: -kv[1]):
        print(f"  {cat:8s} {n}")
    print("\n=== AFTER counts ===")
    for cat, n in sorted(after.items(), key=lambda kv: -kv[1]):
        print(f"  {cat:8s} {n}")
    print("\n=== DELTA (after - before) ===")
    for cat in sorted(set(before) | set(after)):
        d = after[cat] - before[cat]
        if d:
            print(f"  {cat:8s} {d:+d}")

    print("\n=== FIX 1: 龍角 ===")
    print(f"  醫療 -> 餐飲 : {long_jiao_from_medical}")
    print(f"  其他 -> 餐飲 : {long_jiao_from_nonfood}")

    print("\n=== FIX 2: 旅遊 ===")
    print(f"  total newly tagged 旅遊 : {travel_added}")
    print(f"  final 旅遊 count        : {after.get('旅遊', 0)}")
    print("  sources:")
    for src, n in travel_from.most_common():
        print(f"    {src or '(empty)':8s} -> 旅遊 : {n}")

    print("\n=== KEY CATEGORY COUNTS (before -> after) ===")
    for cat in ("餐飲", "交通", "娛樂", "旅遊", "醫療", "其他"):
        print(f"  {cat:4s}: {before.get(cat,0)} -> {after.get(cat,0)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
