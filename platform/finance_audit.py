"""Audit the 財務管理 Google Sheet - sample each tab.

Reads ``EDWARD_FINANCE_SHEET_ID`` and ``GOOGLE_SHEETS_CREDENTIALS_PATH`` from
the environment. See ``~/.claude/credentials/README.md``.
"""
import io
import json
import os
import sys
from pathlib import Path

# Ensure stdout can handle CJK
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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

import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = os.environ.get("EDWARD_FINANCE_SHEET_ID", "")
CRED = os.environ.get(
    "GOOGLE_SHEETS_CREDENTIALS_PATH",
    str(Path.home() / ".claude" / "credentials" / "google_sheets_concise_beanbag.json"),
)
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

if not SHEET_ID:
    raise SystemExit(
        "EDWARD_FINANCE_SHEET_ID not set. Export it or load "
        "~/.claude/credentials/.env before running this script."
    )

creds = Credentials.from_service_account_file(CRED, scopes=SCOPES)
gc = gspread.authorize(creds)
sh = gc.open_by_key(SHEET_ID)

out = {"spreadsheet": sh.title, "tabs": []}
for ws in sh.worksheets():
    info = {"title": ws.title, "rows": ws.row_count, "cols": ws.col_count, "id": ws.id}
    try:
        # Fetch top 12 rows to capture header + samples
        rng = ws.get(f"A1:{chr(64+min(ws.col_count,26))}12") if ws.col_count <= 26 else ws.get_values()[:12]
        info["headers"] = rng[0] if rng else []
        info["sample"] = rng[1:11] if len(rng) > 1 else []
        # Also fetch last 3 rows to see most recent data
        if ws.row_count > 15:
            start = max(2, ws.row_count - 3)
            last = ws.get(f"A{start}:{chr(64+min(ws.col_count,26))}{ws.row_count}") if ws.col_count <= 26 else []
            info["last_rows"] = last
    except Exception as e:
        info["error"] = str(e)
    out["tabs"].append(info)

Path(_win_to_posix("C:/Users/admin/staging/financial_dashboards_audit.json")).write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8'
)
print("Saved audit JSON")
for t in out["tabs"]:
    print(f"\n=== {t['title']} ({t['rows']}r x {t['cols']}c) ===")
    print("HEADERS:", t.get("headers"))
    if t.get("sample"):
        print("SAMPLE[0]:", t["sample"][0])
    if t.get("last_rows"):
        print("LAST:", t["last_rows"][-1] if t["last_rows"] else None)
