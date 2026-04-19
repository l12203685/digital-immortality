#!/usr/bin/env python3
"""Import Edward's weekly TSV export into dashin_weekly_balance.jsonl.

Source: C:/Users/admin/staging/dashin_weekly_raw_from_edward.tsv
Output: C:/Users/admin/workspace/digital-immortality/results/dashin_weekly_balance.jsonl

Each output line:
{
  "date": "2024-09-18",
  "equity": 8159713,
  "assets": 22932287,
  "liabilities": 14772574,
  "leverage": 2.81,
  "dashin": 2865957,
  "stocks": 19736330,
  "bank": 330000,
  "weekly_return_pct": 0.0,
  "cum_return_pct": 0.0,
  "log_return_pct": 0.0,
  "annualized_log_return_pct": 0.0,
  "equity_change": 0,
  "asset_change": 0,
  "liability_change": 0,
  "mortgage": 5480000,
  "credit_loan": 1475985,
  "basai": 716489,
  "family_deposit_pledge": 7100100
}
"""
from __future__ import annotations

import csv
import json
import os
import sys
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


TSV_PATH = Path(_win_to_posix("C:/Users/admin/staging/dashin_weekly_raw_from_edward.tsv"))
OUT_PATH = Path(_win_to_posix("C:/Users/admin/workspace/digital-immortality/results/dashin_weekly_balance.jsonl"))


def _parse_number(s: str) -> float | None:
    """Parse a number that may have commas, percentage signs, or be empty."""
    s = s.strip()
    if not s or s == "-" or s == "—":
        return None
    # Remove percentage sign
    s = s.replace("%", "")
    # Remove commas
    s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def _parse_int(s: str) -> int:
    """Parse an integer with commas."""
    v = _parse_number(s)
    return int(v) if v is not None else 0


def _parse_date(s: str) -> str:
    """Convert 2024/09/18 to 2024-09-18."""
    return s.strip().replace("/", "-")


def main() -> None:
    if not TSV_PATH.exists():
        print(f"ERROR: TSV file not found: {TSV_PATH}", file=sys.stderr)
        sys.exit(1)

    rows: list[dict] = []
    with TSV_PATH.open("r", encoding="utf-8") as fh:
        reader = csv.reader(fh, delimiter="\t")
        header = next(reader)  # skip header row

        # Verify we have the expected columns
        print(f"Header ({len(header)} cols): {header[:5]}...")

        for line_no, fields in enumerate(reader, start=2):
            if len(fields) < 20:
                print(f"  SKIP line {line_no}: only {len(fields)} fields")
                continue

            date_str = _parse_date(fields[0])
            log_pct = _parse_number(fields[1])
            cum_pct = _parse_number(fields[2])
            weekly_pct = _parse_number(fields[3])
            annualized_log_pct = _parse_number(fields[4])
            equity = _parse_int(fields[5])
            leverage = _parse_number(fields[6]) or 0.0
            equity_change = _parse_int(fields[7])
            asset_change = _parse_int(fields[8])
            liability_change = _parse_int(fields[9])
            assets = _parse_int(fields[10])
            bank = _parse_int(fields[11])
            dashin = _parse_int(fields[12])
            stocks = _parse_int(fields[13])
            liabilities = _parse_int(fields[14])
            mortgage = _parse_int(fields[15])
            credit_loan = _parse_int(fields[16])
            basai = _parse_int(fields[17])
            family_bro = _parse_int(fields[18])
            family_deposit_pledge = _parse_int(fields[19])

            rec = {
                "date": date_str,
                "equity": equity,
                "assets": assets,
                "liabilities": liabilities,
                "leverage": round(leverage, 2),
                "dashin": dashin,
                "stocks": stocks,
                "bank": bank,
                "weekly_return_pct": round(weekly_pct or 0.0, 2),
                "cum_return_pct": round(cum_pct or 0.0, 2),
                "log_return_pct": round(log_pct or 0.0, 2),
                "annualized_log_return_pct": round(annualized_log_pct or 0.0, 2),
                "equity_change": equity_change,
                "asset_change": asset_change,
                "liability_change": liability_change,
                "mortgage": mortgage,
                "credit_loan": credit_loan,
                "basai": basai,
                "family_deposit_pledge": family_deposit_pledge,
            }
            rows.append(rec)

    # Sort by date
    rows.sort(key=lambda r: r["date"])

    # Write JSONL
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as fh:
        for rec in rows:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Wrote {len(rows)} rows to {OUT_PATH}")
    print(f"  Date range: {rows[0]['date']} -> {rows[-1]['date']}")
    print(f"  Latest equity: {rows[-1]['equity']:,}")
    print(f"  Latest cum%: {rows[-1]['cum_return_pct']}")


if __name__ == "__main__":
    main()
