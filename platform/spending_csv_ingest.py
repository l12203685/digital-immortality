#!/usr/bin/env python3
"""spending_csv_ingest.py

Watches C:/Users/admin/staging/finance_inbox/ for new *.csv files,
parses common TW bank credit-card statement formats, dedupes against
the existing finance_spending.jsonl, appends new rows, and moves the
processed file to finance_inbox/_processed/.

Supported banks (best-guess by column headers): 國泰世華, 玉山, 中信,
台新, 永豐, 花旗, 渣打. Falls back to a generic column-name guesser.

CLI:
  python spending_csv_ingest.py            # one-shot
  python spending_csv_ingest.py --watch    # poll every 60s

Registered as Windows Task `mc_spending_ingest` — runs every 10 min.

Timezone: Asia/Taipei on every user-facing timestamp.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TPE = ZoneInfo("Asia/Taipei")

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


HOME = Path(_win_to_posix("C:/Users/admin"))
REPO = HOME / "workspace" / "digital-immortality"
INBOX = HOME / "staging" / "finance_inbox"
PROCESSED = INBOX / "_processed"
SPENDING_JSONL = REPO / "results" / "finance_spending.jsonl"
LOG_FILE = REPO / "results" / "spending_csv_ingest.log"

ENCODINGS = ("utf-8-sig", "utf-8", "cp950", "big5", "gbk")

# ---------------------------------------------------------------------------
# Column header aliases (for best-guess parsing). Keys are canonical, values
# are a set of lowercase substrings to match against CSV headers.
# ---------------------------------------------------------------------------
HEADER_ALIASES: dict[str, tuple[str, ...]] = {
    "date": ("交易日期", "消費日期", "日期", "帳單日期", "transaction date", "date"),
    "amount": (
        "消費金額",
        "交易金額",
        "金額",
        "new taiwan dollar",
        "台幣金額",
        "amount",
        "ntd",
    ),
    "merchant": (
        "商店名稱",
        "商店",
        "消費地點",
        "交易說明",
        "說明",
        "摘要",
        "description",
        "merchant",
    ),
    "category": ("分類", "類別", "category"),
    "card": ("卡別", "卡號末四碼", "卡片", "card"),
    "trx_type": ("交易類型", "交易別", "type"),
    "foreign_amount": ("外幣金額", "原幣金額", "foreign amount"),
    "currency": ("幣別", "currency"),
}

# ---------------------------------------------------------------------------
# Bank detection (signature string -> bank label). Purely informational.
# ---------------------------------------------------------------------------
BANK_SIGNATURES = {
    "cathay": ("國泰世華", "cathay united"),
    "esun": ("玉山", "e.sun"),
    "ctbc": ("中國信託", "ctbc"),
    "taishin": ("台新", "taishin"),
    "sinopac": ("永豐", "sinopac"),
    "citi": ("花旗", "citi"),
    "scb": ("渣打", "standard chartered"),
    "fubon": ("富邦", "fubon"),
    "cub": ("兆豐", "mega"),
}

# ---------------------------------------------------------------------------
# DEPRECATED 2026-04-15 cycle476: category keywords moved to reclassify_spending.py
# as single source of truth. _guess_category below delegates there.
# Kept as reference only — not used by the live classifier.
# ---------------------------------------------------------------------------
_LEGACY_CATEGORY_KEYWORDS_UNUSED: tuple[tuple[str, tuple[str, ...]], ...] = (
    # Order matters: more specific categories first.
    # 註：訂閱/運動/教育/禮金 已於 2026-04-15 併入 其他/娛樂/娛樂/娛樂。
    # 註：固定費用 已於 2026-04-15 (cycle474) 併入 其他。
    # 註：購物 已於 2026-04-15 (cycle474) 拆到 餐飲/娛樂/日用，預設落日用。
    # 旅遊：國外交易手續費 + 景點/訂房/機票/租車/度假訊號（優先於交通/娛樂）
    ("旅遊", ("國外交易手續費", "foreign transaction fee", "外幣手續費",
             "expedia", "booking.com", "agoda", "airbnb", "kkday", "klook",
             "trip.com", "hotels.com", "航空", "airlines", "airways",
             "機票", "租車", "rental car", "hertz", "avis",
             "景點門票", "樂園", "主題公園", "博物館門票", "溫泉",
             "度假村", "resort ", "resort-", "hotel ", "hotel-", "旅館",
             "民宿", "hostel", "inn ", "ryokan", "villa")),
    # 醫療：含藥妝店（康是美/屈臣氏/Cosmed/Watsons）
    ("醫療", ("診所", "藥局", "醫院", "藥妝", "clinic", "pharmacy", "hospital",
             "康是美", "屈臣氏", "cosmed", "watsons", "watson's",
             "堂吉訶德", "b群", "c群", "鎂鈣", "止汗", "保健", "維他命")),
    ("交通", ("高鐵", "台鐵", "捷運", "計程車", "uber ", "uber-", "uber*",
             "加油", "停車", "taxi", "gogoro", "etc ", "transport",
             "chargespot", "goshare", "wemo", "irent", "機場",
             "昇?昌", "昇泰昌", "加油站")),
    # 餐飲：含便利商店 + 雜貨/超市（購物類食品拆過來）
    ("餐飲", ("龍角", "餐", "食", "飯", "麵", "壽司", "拉麵", "便當", "咖啡", "星巴克",
             "麥當勞", "肯德基", "subway", "starbucks", "cafe", "restaurant",
             "eats", "foodpanda", "ubereats", "711咖啡", "7-11咖啡",
             "給力餐盒", "milksha", "迷客夏", "炭丼", "仁王家", "雞湯桑",
             "麵魚", "米室", "matcha", "hello!你好", "嵐天", "優格",
             "andoumomofuku", "the matcha", "馬可先生", "騰加數位*馬可",
             "azabudai hills", "rimping", "mjt-central",
             "凍焙茶", "焙茶", "桂花凍", "關東煮", "飲料",
             "青山",
             "7-11", "7-eleven", "seven-eleven", "seven eleven", "統一超商",
             "全家", "familymart", "family mart", "萊爾富", "hi-life",
             "hilife", "ok超商", "ok 超商", "ok mart", "ok-mart",
             # 購物拆來：雜貨超市/食材
             "全聯", "家樂福", "costco", "好市多", "大潤發", "愛買",
             "superstore", "超市", "雜貨", "蔬果", "肉品", "海鮮", "食材",
             "零食", "超商")),
    # 娛樂：原娛樂 + 運動（健身/羽球/球場+運動用品）+ 教育（書店/課程/補習）+ 禮金（紅白包）
    ("娛樂", ("影城", "steam", "game", "kktv", "myvideo", "秀泰", "威秀",
             "電影", "演唱會", "concert", "ktv",
             # 運動併入
             "羽球", "健身", "gym", "球拍", "運動", "fitness", "yoga",
             "瑜珈", "自在生活", "球場",
             # 運動用品（購物拆來）
             "球鞋", "運動服", "nike", "adidas", "asics", "yonex", "victor",
             "迪卡儂", "decathlon",
             # 玩具/遊戲/書/電影/音樂（購物拆來）
             "玩具", "toy", "toys", "遊戲", "boardgame", "桌遊",
             # 教育併入
             "書店", "博客來", "誠品書", "金石堂", "書", "course",
             "課程", "補習", "學費",
             "tutor", "teachable", "udemy", "coursera",
             # 音樂
             "音樂", "music",
             # 禮金併入
             "禮金", "紅包", "白包", "包禮", "喜餅", "奠儀")),
    # 日用：家電/家具/廚具/寢具/清潔/衛生/電池/燈泡/工具/五金 + 百貨/網購預設
    ("日用", ("無印良品", "muji", "ikea", "宜家", "hola", "特力屋", "b&q",
            "家電", "家具", "廚具", "寢具", "清潔", "衛生", "電池", "燈泡",
            "工具", "五金",
            "誠品", "新光三越", "百貨", "統一時代", "雜支", "芯動力",
            # 購物平台預設落日用
            "shopee", "蝦皮", "露天", "pchome", "momo", "amazon", "apple.com",
            "淘寶", "雅虎奇摩", "dfs", "展業儀器",
            "睿鼎數位", "身分轉移", "elementi", "紀念品", "明信片",
            "一般商品買賣", "眼罩", "時鐘", "筆記本", "充電線",
            "日用")),
    # 其他雜支：原訂閱（非固定月費軟體/雲端/串流）+ 原固定費用（稅款/電信/水電/瓦斯/保險/管理費）
    ("其他", ("icloud", "google one", "youtube premium", "office 365", "dropbox",
            "notion", "chatgpt", "claude pro", "openai", "anthropic",
            "spotify", "netflix", "apple.com/bill", "github", "cursor",
            "apple one", "disney+", "disney plus", "kkbox",
            # 原固定費用併入
            "中華電信", "遠傳", "台灣大哥大", "台灣之星", "亞太電信", "hinet",
            "台電", "自來水", "瓦斯", "electricity", "water", "gas",
            "保險", "insurance", "地方稅", "綜所稅", "稅款", "里長伯",
            "管理費", "房租", "電費", "水費")),
)

# Legacy note keywords — see reclassify_spending.py for canonical rules.
_LEGACY_NOTE_KEYWORDS_UNUSED: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("日用", ("購物", "網購")),
    ("餐飲", ("晚餐", "午餐", "早餐")),
)


def _apply_trip_override(date: str, current_category: str) -> str:
    """Delegate to canonical trip-override logic in reclassify_spending."""
    from reclassify_spending import apply_trip_override
    return apply_trip_override(date, current_category)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


def _configure_logging() -> logging.Logger:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("spending_csv_ingest")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    return logger


log = _configure_logging()


def now_iso_tpe() -> str:
    return datetime.now(TPE).isoformat()


# ---------------------------------------------------------------------------
# CSV parsing
# ---------------------------------------------------------------------------


@dataclass
class ParsedRow:
    date: str
    amount: float
    merchant: str
    category: str
    note: str
    bank: str
    source_file: str


def _read_text(path: Path) -> str:
    for enc in ENCODINGS:
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
        except Exception as exc:
            log.warning("failed to read %s with %s: %s", path.name, enc, exc)
    # Binary fallback
    try:
        return path.read_bytes().decode("utf-8", errors="replace")
    except Exception:
        return ""


def _detect_bank(raw_text: str, filename: str) -> str:
    haystack = (raw_text[:4000] + " " + filename).lower()
    for label, tokens in BANK_SIGNATURES.items():
        for tok in tokens:
            if tok.lower() in haystack:
                return label
    return "unknown"


def _header_map(headers: list[str]) -> dict[str, int]:
    """Map canonical field -> header column index."""
    mapping: dict[str, int] = {}
    lower = [h.strip().lower() for h in headers]
    for canonical, aliases in HEADER_ALIASES.items():
        for i, h in enumerate(lower):
            if not h:
                continue
            for alias in aliases:
                if alias in h:
                    mapping.setdefault(canonical, i)
                    break
    return mapping


_DATE_RE = re.compile(r"(\d{4})[/\-.年](\d{1,2})[/\-.月](\d{1,2})")


def _parse_date(raw: str) -> str:
    s = (raw or "").strip()
    if not s:
        return ""
    m = _DATE_RE.search(s)
    if m:
        y, mo, d = m.groups()
        return f"{int(y):04d}-{int(mo):02d}-{int(d):02d}"
    # Short form: MM/DD of current year
    m2 = re.match(r"^(\d{1,2})[/\-](\d{1,2})$", s)
    if m2:
        year = datetime.now(TPE).year
        mo, d = m2.groups()
        return f"{year:04d}-{int(mo):02d}-{int(d):02d}"
    # ROC year: 114/08/01
    m3 = re.match(r"^(\d{2,3})[/\-](\d{1,2})[/\-](\d{1,2})$", s)
    if m3:
        ry, mo, d = m3.groups()
        year = int(ry) + 1911
        return f"{year:04d}-{int(mo):02d}-{int(d):02d}"
    return ""


def _parse_amount(raw: str) -> float | None:
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    # Strip currency symbols, commas, parentheses (neg)
    neg = False
    if s.startswith("(") and s.endswith(")"):
        neg = True
        s = s[1:-1]
    s = s.replace(",", "").replace("NT$", "").replace("$", "").replace(" ", "")
    s = s.replace("元", "")
    try:
        val = float(s)
    except ValueError:
        return None
    return -val if neg else val


def _guess_category(merchant: str, note: str) -> str:
    """Delegate to the canonical 9-category classifier (cycle476).

    The classifier lives in reclassify_spending.py so both the one-shot
    historical reclass and the live CSV ingest share identical rules.
    """
    from reclassify_spending import classify
    return classify(merchant, note, "")


def parse_csv_file(path: Path) -> list[ParsedRow]:
    text = _read_text(path)
    if not text.strip():
        return []
    bank = _detect_bank(text, path.name)

    # Find the best header row: try each line up to line 30, pick the one
    # where DictReader yields the most column alias hits.
    lines = text.splitlines()
    best: tuple[int, dict[str, int]] | None = None
    for i in range(min(30, len(lines))):
        try:
            headers = next(csv.reader(io.StringIO(lines[i])))
        except StopIteration:
            continue
        if not headers or len(headers) < 2:
            continue
        mapping = _header_map(headers)
        if "date" in mapping and "amount" in mapping:
            if best is None or len(mapping) > len(best[1]):
                best = (i, mapping)
    if best is None:
        log.warning("%s: no header with date+amount found", path.name)
        return []

    header_idx, mapping = best
    body = "\n".join(lines[header_idx:])
    reader = csv.reader(io.StringIO(body))
    try:
        _headers = next(reader)
    except StopIteration:
        return []

    rows: list[ParsedRow] = []
    for raw in reader:
        if not raw or not any(c.strip() for c in raw):
            continue
        def _col(key: str) -> str:
            idx = mapping.get(key)
            if idx is None or idx >= len(raw):
                return ""
            return str(raw[idx]).strip()

        date = _parse_date(_col("date"))
        amount = _parse_amount(_col("amount"))
        if not date or amount is None or amount == 0:
            continue
        # Some bank statements use negative amounts for refunds; credit
        # charges come through as positive. Treat amount as absolute-spent.
        spent = abs(amount)
        merchant = _col("merchant") or "(未填)"
        note_bits = []
        if _col("card"):
            note_bits.append(f"卡{_col('card')}")
        if _col("trx_type"):
            note_bits.append(_col("trx_type"))
        if _col("foreign_amount"):
            note_bits.append(f"原幣{_col('foreign_amount')}")
        note = " ".join(note_bits)
        category = _col("category") or _guess_category(merchant, note)
        # Final-step override: trip date windows force category (Poker exempt).
        category = _apply_trip_override(date, category)
        rows.append(
            ParsedRow(
                date=date,
                amount=spent,
                merchant=merchant,
                category=category,
                note=note,
                bank=bank,
                source_file=path.name,
            )
        )
    return rows


# ---------------------------------------------------------------------------
# Dedupe + append
# ---------------------------------------------------------------------------


def _existing_keys() -> set[tuple[str, float, str]]:
    keys: set[tuple[str, float, str]] = set()
    if not SPENDING_JSONL.exists():
        return keys
    try:
        for line in SPENDING_JSONL.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            try:
                amt = float(obj.get("amount") or 0)
            except (TypeError, ValueError):
                amt = 0.0
            keys.add((
                str(obj.get("date") or ""),
                round(amt, 2),
                str(obj.get("merchant") or "").strip(),
            ))
    except Exception as exc:
        log.warning("failed to read existing jsonl: %s", exc)
    return keys


def append_entries(rows: list[ParsedRow]) -> int:
    if not rows:
        return 0
    existing = _existing_keys()
    SPENDING_JSONL.parent.mkdir(parents=True, exist_ok=True)
    added = 0
    with SPENDING_JSONL.open("a", encoding="utf-8") as f:
        for r in rows:
            key = (r.date, round(r.amount, 2), r.merchant.strip())
            if key in existing:
                continue
            existing.add(key)
            entry = {
                "ts": now_iso_tpe(),
                "date": r.date,
                "amount": r.amount,
                "currency": "TWD",
                "method": "credit",
                "category": r.category,
                "merchant": r.merchant,
                "note": r.note,
                "source": "csv_ingest",
                "source_file": r.source_file,
                "bank": r.bank,
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            added += 1
    return added


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def _ensure_dirs() -> None:
    INBOX.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)


def process_once() -> dict:
    _ensure_dirs()
    stats = {"files": 0, "new_entries": 0, "errors": 0, "skipped": 0}
    for csv_path in sorted(INBOX.glob("*.csv")):
        if csv_path.parent == PROCESSED:
            continue
        stats["files"] += 1
        try:
            rows = parse_csv_file(csv_path)
            added = append_entries(rows)
            stats["new_entries"] += added
            log.info(
                "processed %s: parsed=%d added=%d",
                csv_path.name,
                len(rows),
                added,
            )
            target = PROCESSED / (
                datetime.now(TPE).strftime("%Y%m%d_%H%M%S_") + csv_path.name
            )
            csv_path.rename(target)
        except Exception as exc:
            stats["errors"] += 1
            log.exception("failed on %s: %s", csv_path.name, exc)
    return stats


def watch_loop(interval_sec: int = 60) -> None:
    log.info("watch mode: polling every %ds", interval_sec)
    while True:
        try:
            process_once()
        except Exception as exc:
            log.exception("watch cycle failed: %s", exc)
        time.sleep(interval_sec)


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest credit-card CSVs")
    parser.add_argument("--watch", action="store_true", help="poll every 60s")
    parser.add_argument("--interval", type=int, default=60)
    args = parser.parse_args()
    if args.watch:
        watch_loop(args.interval)
        return 0
    stats = process_once()
    log.info("done: %s", stats)
    return 0


if __name__ == "__main__":
    sys.exit(main())
