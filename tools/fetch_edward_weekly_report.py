"""
Fetch Edward personal weekly report from Google Sheet → jsonl.

Source sheet: 1S0b292zeMVZoK2aItYEyZROnEu5H7OB3Xiah7fYVXtM, tab gid=1655088476 (週報)
Header (row 1, 0-indexed row=1):
  0 日期(日) | 1 log% | 2 cum% | 3 % | 4 年化log% | 5 權益 | ...
Data starts row 2 (0-indexed).

Output: results/edward_weekly_report.jsonl
  { "week_ending": "YYYY-MM-DD", "weekly_return_pct": float, "cum_return_pct": float,
    "weekly_log_pct": float, "annualized_log_pct": float, "equity": int }

Full refresh every run.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = "1S0b292zeMVZoK2aItYEyZROnEu5H7OB3Xiah7fYVXtM"
TAB_GID = 1655088476
SA_CRED = Path(r"C:/Users/admin/.claude/credentials/google_sheets_concise_beanbag.json")

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = REPO_ROOT / "results" / "edward_weekly_report.jsonl"
OUT_PATH_FULL = REPO_ROOT / "results" / "dashin_weekly_balance.jsonl"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def _parse_pct(s: str) -> float | None:
    if s is None:
        return None
    t = s.strip().replace("%", "").replace(",", "")
    if not t or t in {"-", "#N/A", "#DIV/0!"}:
        return None
    try:
        return float(t)
    except ValueError:
        return None


def _parse_int(s: str) -> int | None:
    if s is None:
        return None
    t = s.strip().replace(",", "")
    if not t:
        return None
    try:
        return int(float(t))
    except ValueError:
        return None


def _parse_date(s: str) -> str | None:
    s = (s or "").strip()
    if not s:
        return None
    for fmt in ("%Y/%m/%d", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def fetch() -> tuple[list[dict], list[dict]]:
    """Return (summary_rows, full_rows). Full rows include all 20 columns."""
    if not SA_CRED.exists():
        raise FileNotFoundError(f"Service account credential not found: {SA_CRED}")
    creds = Credentials.from_service_account_file(str(SA_CRED), scopes=SCOPES)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SHEET_ID)
    ws = next((w for w in sh.worksheets() if w.id == TAB_GID), None)
    if ws is None:
        raise RuntimeError(f"Tab gid={TAB_GID} not found in sheet {SHEET_ID}")
    rows = ws.get_all_values()
    # rows[0] = summary, rows[1] = headers, rows[2:] = data
    summary: list[dict] = []
    full: list[dict] = []
    for r in rows[2:]:
        if len(r) < 6:
            continue
        date_iso = _parse_date(r[0])
        if not date_iso:
            continue
        # Pad row to 20 cols for safe indexing
        padded = list(r) + [""] * max(0, 20 - len(r))
        summary.append({
            "week_ending": date_iso,
            "weekly_log_pct": _parse_pct(padded[1]),
            "cum_return_pct": _parse_pct(padded[2]),
            "weekly_return_pct": _parse_pct(padded[3]),
            "annualized_log_pct": _parse_pct(padded[4]),
            "equity": _parse_int(padded[5]),
        })
        # Full record matches dashin_weekly_balance.jsonl schema
        equity = _parse_int(padded[5])
        leverage = _parse_pct(padded[6])  # 槓桿 raw float
        full.append({
            "date": date_iso,
            "equity": equity,
            "assets": _parse_int(padded[10]),
            "liabilities": _parse_int(padded[14]),
            "leverage": round(leverage, 2) if leverage is not None else None,
            "dashin": _parse_int(padded[12]),
            "stocks": _parse_int(padded[13]),
            "bank": _parse_int(padded[11]),
            "weekly_return_pct": _parse_pct(padded[3]),
            "cum_return_pct": _parse_pct(padded[2]),
            "log_return_pct": _parse_pct(padded[1]),
            "annualized_log_return_pct": _parse_pct(padded[4]),
            "equity_change": _parse_int(padded[7]),
            "asset_change": _parse_int(padded[8]),
            "liability_change": _parse_int(padded[9]),
            "mortgage": _parse_int(padded[15]),
            "credit_loan": _parse_int(padded[16]),
            "basai": _parse_int(padded[17]),
            "family_deposit_pledge": _parse_int(padded[19]),
            "source": "google_sheet_live",
        })
    summary.sort(key=lambda x: x["week_ending"])
    full.sort(key=lambda x: x["date"])
    return summary, full


def write_jsonl(records: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".jsonl.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    tmp.replace(path)


def main() -> int:
    try:
        summary, full = fetch()
    except Exception as e:
        sys.stderr.write(f"[edward_weekly_report] FAIL: {type(e).__name__}: {e}\n")
        return 2
    write_jsonl(summary, OUT_PATH)
    write_jsonl(full, OUT_PATH_FULL)
    tpe = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M +08")
    sys.stdout.write(
        f"[edward_weekly_report] {tpe} wrote {len(summary)} summary -> {OUT_PATH}\n"
        f"  + {len(full)} full -> {OUT_PATH_FULL}\n"
    )
    if summary:
        sys.stdout.write(
            f"  first={summary[0]['week_ending']} last={summary[-1]['week_ending']}\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
