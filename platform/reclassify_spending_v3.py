#!/usr/bin/env python3
"""reclassify_spending_v3.py  (cycle 473)

Second-round rules (2026-04-15):

  R1. 便利商店 -> 餐飲 (7-11 / SEVEN / 全家 / FamilyMart / 萊爾富 / Hi-Life / OK 超商)
      Applied only when current category in {日用, 購物, 其他, 娛樂, ""} — these are
      the buckets where small convenience-store food buys tend to land.
      Skip if merchant/note clearly signals 充值/繳費/儲值/代收 (leave as-is).
  R2. 康是美 / 屈臣氏 / Watsons / Cosmed -> 醫療
  R3. 青山 (飲料店) -> 餐飲
  R4. 運動 (分類) -> 娛樂   (whole-category merge)
      plus: 健身 / 羽球 / 球拍 / gym / fitness / yoga / 瑜珈 / 球場 merchants
      currently in any non-娛樂/non-Poker cat -> 娛樂
  R5. 禮金 / 紅包 / 白包 / 包禮 / 喜餅 / 奠儀 -> 娛樂
  R6. 訂閱 (分類) -> 其他   (whole-category merge)
      plus Google One / Netflix / Spotify / iCloud / Apple One / YouTube Premium
      / ChatGPT / Claude / Cursor / GitHub / KKBOX / Disney+ currently not
      in 固定費用 -> 其他
  R7. 教育 (分類) -> 娛樂   (whole-category merge)
      plus: 書店 / 博客來 / 金石堂 / 課程 / 補習 / 學費 -> 娛樂

Poker category is NEVER touched (private coding).

Backup -> finance_spending.jsonl.bak_reclass3 (one-shot, not overwritten).
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from collections import Counter
from pathlib import Path

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


JSONL = Path(_win_to_posix(
    "C:/Users/admin/workspace/digital-immortality/results/finance_spending.jsonl"
))
BAK = JSONL.with_suffix(".jsonl.bak_reclass3")

CVS_KEYWORDS: tuple[str, ...] = (
    "7-11", "7-eleven", "seven-eleven", "seven eleven", "seveneleven",
    "統一超商", "全家", "familymart", "family mart", "family-mart",
    "萊爾富", "hi-life", "hilife", "hi life",
    "ok超商", "ok 超商", "ok mart", "ok-mart", "okmart",
)
CVS_SKIP_SIGNALS: tuple[str, ...] = (
    "充值", "儲值", "繳費", "代收", "代繳", "轉帳", "電信費", "水費", "電費",
)

DRUGSTORE_KEYWORDS: tuple[str, ...] = (
    "康是美", "屈臣氏", "cosmed", "watsons", "watson's", "watson ",
)

DRINK_QS_KEYWORDS: tuple[str, ...] = ("青山",)

SPORTS_KEYWORDS: tuple[str, ...] = (
    "羽球", "健身", "gym", "球拍", "fitness", "yoga", "瑜珈",
    "自在生活", "球場",
    # bare "運動" is intentionally NOT here to avoid false hits like
    # "運動飲料"; 原分類為 運動 的 row 全改，靠 R4 whole-category merge。
)

GIFT_KEYWORDS: tuple[str, ...] = (
    "禮金", "紅包", "白包", "包禮", "喜餅", "奠儀",
)

SUBSCRIPTION_KEYWORDS: tuple[str, ...] = (
    "icloud", "google one", "youtube premium", "youtube music",
    "office 365", "dropbox", "notion", "chatgpt", "openai",
    "claude pro", "anthropic", "spotify", "netflix", "apple.com/bill",
    "github", "cursor", "apple one", "disney+", "disney plus", "kkbox",
)

EDU_KEYWORDS: tuple[str, ...] = (
    "書店", "博客來", "金石堂", "誠品書店", "課程", "補習", "學費",
    "tutor", "teachable", "udemy", "coursera",
)


def _has_any(hay: str, kws: tuple[str, ...]) -> bool:
    for kw in kws:
        if kw.lower() in hay:
            return True
    return False


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

    stats: Counter[str] = Counter()
    samples: dict[str, list[str]] = {}

    def _sample(bucket: str, merchant: str) -> None:
        lst = samples.setdefault(bucket, [])
        if len(lst) < 3 and merchant:
            lst.append(merchant)

    for row in rows:
        old = str(row.get("category") or "其他")
        if old == "Poker":
            continue
        merchant = str(row.get("merchant") or "")
        note = str(row.get("note") or "")
        hay = f"{merchant} {note}".lower()

        new = old  # default: no change

        # Whole-category merges first (idempotent, unambiguous).
        if old == "運動":
            new = "娛樂"
            stats["R4a_運動分類→娛樂"] += 1
        elif old == "訂閱":
            new = "其他"
            stats["R6a_訂閱分類→其他"] += 1
        elif old == "教育":
            new = "娛樂"
            stats["R7a_教育分類→娛樂"] += 1
        elif old == "禮金":
            new = "娛樂"
            stats["R5a_禮金分類→娛樂"] += 1

        # R2: drugstore -> 醫療 (always, unless already 醫療/Poker)
        if new != "醫療" and _has_any(hay, DRUGSTORE_KEYWORDS):
            stats[f"R2_藥妝({old})→醫療"] += 1
            _sample("R2", merchant)
            new = "醫療"

        # R3: 青山 -> 餐飲
        elif new != "餐飲" and _has_any(hay, DRINK_QS_KEYWORDS):
            stats[f"R3_青山({old})→餐飲"] += 1
            _sample("R3", merchant)
            new = "餐飲"

        # R5: 禮金 -> 娛樂
        elif new != "娛樂" and _has_any(hay, GIFT_KEYWORDS):
            stats[f"R5_禮金({old})→娛樂"] += 1
            _sample("R5", merchant)
            new = "娛樂"

        # R4b: sports merchants (not already 娛樂)
        elif new != "娛樂" and _has_any(hay, SPORTS_KEYWORDS):
            stats[f"R4b_運動商家({old})→娛樂"] += 1
            _sample("R4b", merchant)
            new = "娛樂"

        # R7b: education merchants -> 娛樂
        elif new != "娛樂" and _has_any(hay, EDU_KEYWORDS):
            stats[f"R7b_教育商家({old})→娛樂"] += 1
            _sample("R7b", merchant)
            new = "娛樂"

        # R6b: subscription merchants -> 其他 (but respect 固定費用)
        elif (
            new not in ("其他", "固定費用")
            and _has_any(hay, SUBSCRIPTION_KEYWORDS)
        ):
            stats[f"R6b_訂閱商家({old})→其他"] += 1
            _sample("R6b", merchant)
            new = "其他"

        # R1: convenience store -> 餐飲
        elif (
            new != "餐飲"
            and _has_any(hay, CVS_KEYWORDS)
            and not _has_any(hay, CVS_SKIP_SIGNALS)
            and new in ("日用", "購物", "其他", "娛樂", "")
        ):
            stats[f"R1_超商({old})→餐飲"] += 1
            _sample("R1", merchant)
            new = "餐飲"

        if new != old:
            row["category"] = new

    with JSONL.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    after = Counter(str(r.get("category") or "其他") for r in rows)

    print("\n=== BEFORE counts ===")
    for cat, n in sorted(before.items(), key=lambda kv: -kv[1]):
        print(f"  {cat:10s} {n}")
    print("\n=== AFTER counts ===")
    for cat, n in sorted(after.items(), key=lambda kv: -kv[1]):
        print(f"  {cat:10s} {n}")
    print("\n=== DELTA (after - before) ===")
    for cat in sorted(set(before) | set(after)):
        d = after[cat] - before[cat]
        if d:
            print(f"  {cat:10s} {d:+d}")

    print("\n=== RULE HITS ===")
    for k, n in stats.most_common():
        print(f"  {k}: {n}")

    print("\n=== SAMPLES ===")
    for bucket, lst in samples.items():
        print(f"  {bucket}: {lst}")

    print("\n=== LEGACY CATEGORY EMPTY CHECK ===")
    for cat in ("運動", "訂閱", "教育"):
        n = after.get(cat, 0)
        flag = "OK" if n == 0 else "STILL PRESENT"
        print(f"  {cat}: {n}  [{flag}]")

    print("\n=== KEY CATEGORY COUNTS (before -> after) ===")
    for cat in ("餐飲", "娛樂", "醫療", "旅遊", "其他", "固定費用",
                "日用", "購物", "交通", "寵物", "運動", "訂閱", "教育",
                "禮金", "Poker"):
        print(f"  {cat:6s}: {before.get(cat,0)} -> {after.get(cat,0)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
