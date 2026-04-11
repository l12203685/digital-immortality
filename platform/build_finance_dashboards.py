"""Build Edward's 3 financial dashboards from Google Sheet 財務管理.

Reads 7 tabs from the finance Sheet (ID read from ``EDWARD_FINANCE_SHEET_ID``
env var) and writes 3 JSON files consumed by the Mission Control finance UI:

    results/finance_networth.json
    results/finance_spending.json
    results/finance_marketcap.json

Privacy: these JSONs contain absolute NTD amounts. They are written to the
local `results/` folder and are **consumed only by Mission Control
(localhost)**. They are NOT pushed to GitHub.  See
`staging/finance_dashboard_privacy_note.md`.

Cache: raw sheet pulls are cached to `results/.sheet_cache/<tab>.json` with
TTL 1 hour so this can be called by the recursive daemon without hammering
the Sheets API.
"""
from __future__ import annotations

import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("finance_dashboards")

# --- Paths ---------------------------------------------------------------
REPO = Path("C:/Users/admin/workspace/digital-immortality")
RESULTS = REPO / "results"
CACHE_DIR = RESULTS / ".sheet_cache"

# Credential path + Sheet ID come from environment. Fall back to the historical
# local path so existing cron jobs keep running when env is not set.
_DEFAULT_CREDENTIALS = Path.home() / ".claude" / "credentials" / "google_sheets_concise_beanbag.json"
CREDENTIALS = Path(os.environ.get("GOOGLE_SHEETS_CREDENTIALS_PATH", str(_DEFAULT_CREDENTIALS)))
SHEET_ID = os.environ.get("EDWARD_FINANCE_SHEET_ID", "")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

NETWORTH_JSON = RESULTS / "finance_networth.json"
SPENDING_JSON = RESULTS / "finance_spending.json"
MARKETCAP_JSON = RESULTS / "finance_marketcap.json"

CACHE_TTL_SEC = 3600  # 1 hour
TAIPEI_OFFSET = timedelta(hours=8)

# FIRE targets from CLAUDE.md
FIRE_TARGET_NTD = 21_000_000
PASSIVE_INCOME_TARGET_NTD = 5_000_000

# --- Helpers -------------------------------------------------------------

NUM_RE = re.compile(r"[-+]?[\d,]+(?:\.\d+)?")


def parse_number(raw: Any) -> float | None:
    """Parse a sheet cell into a float. Returns None if empty/not numeric."""
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    s = str(raw).strip()
    if not s:
        return None
    # strip percent sign, commas, currency glyphs
    s2 = s.replace(",", "").replace("%", "").replace("$", "").replace("NT", "")
    try:
        return float(s2)
    except ValueError:
        m = NUM_RE.search(s)
        if m:
            try:
                return float(m.group(0).replace(",", ""))
            except ValueError:
                return None
        return None


def parse_percent(raw: Any) -> float | None:
    """Parse a percent-like string ('58.20%' or '0.582') to a float percent."""
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    had_pct = s.endswith("%")
    n = parse_number(s)
    if n is None:
        return None
    if not had_pct and abs(n) < 5:
        # bare decimal; interpret as fraction
        return n * 100.0
    return n


def taipei_now_iso() -> str:
    tz = timezone(TAIPEI_OFFSET)
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S (Taipei, UTC+8)")


# --- Sheet access with cache --------------------------------------------


def _cache_path(tab: str) -> Path:
    safe = re.sub(r"[^0-9A-Za-z]+", "_", tab)
    return CACHE_DIR / f"{safe}.json"


def _load_cache(tab: str) -> list[list[str]] | None:
    p = _cache_path(tab)
    if not p.exists():
        return None
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    if time.time() - obj.get("cached_at", 0) > CACHE_TTL_SEC:
        return None
    return obj.get("rows")


def _save_cache(tab: str, rows: list[list[str]]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {"cached_at": time.time(), "tab": tab, "rows": rows}
    _cache_path(tab).write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )


def fetch_all_tabs(force: bool = False) -> dict[str, list[list[str]]]:
    """Fetch every worksheet's values. Uses 1h disk cache unless `force`."""
    tabs = [
        "週報",
        "AssetManagement",
        "記帳",
        "記帳匯總",
        "ETF data",
        "CMC",
        "Summary",
    ]
    data: dict[str, list[list[str]]] = {}
    need_fetch: list[str] = []
    if not force:
        for t in tabs:
            cached = _load_cache(t)
            if cached is not None:
                data[t] = cached
            else:
                need_fetch.append(t)
    else:
        need_fetch = list(tabs)

    if need_fetch:
        if not SHEET_ID:
            raise SystemExit(
                "EDWARD_FINANCE_SHEET_ID not set. Export it or load "
                "~/.claude/credentials/.env before running this script."
            )
        import gspread  # lazy import
        from google.oauth2.service_account import Credentials

        creds = Credentials.from_service_account_file(str(CREDENTIALS), scopes=SCOPES)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SHEET_ID)
        for tab in need_fetch:
            try:
                ws = sh.worksheet(tab)
                # For CMC we only need top ~220 rows (rank cap).
                if tab == "CMC":
                    rows = ws.get("A1:AB220")
                else:
                    rows = ws.get_all_values()
                data[tab] = rows
                _save_cache(tab, rows)
                logger.info("fetched tab %s rows=%d", tab, len(rows))
            except Exception as exc:
                logger.exception("failed fetching tab %s", tab)
                data[tab] = []
    return data


# --- Derivations ---------------------------------------------------------


@dataclass
class WeeklyRow:
    date: str
    equity: float
    assets: float
    liabilities: float
    leverage: float | None
    weekly_pct: float | None
    annual_log_pct: float | None


def parse_weekly_tab(rows: list[list[str]]) -> list[WeeklyRow]:
    """週報: row 0 = totals, row 1 = header, row 2+ = weekly data."""
    out: list[WeeklyRow] = []
    if len(rows) < 3:
        return out
    for r in rows[2:]:
        if not r or not r[0].strip():
            continue
        date = r[0].strip()
        if not re.match(r"^\d{4}/\d{1,2}/\d{1,2}", date):
            continue
        def cell(i: int) -> str:
            return r[i] if i < len(r) else ""
        equity = parse_number(cell(5)) or 0.0
        assets = parse_number(cell(10)) or 0.0
        liab = parse_number(cell(14)) or 0.0
        lev = parse_number(cell(6))
        weekly = parse_percent(cell(3))
        annual_log = parse_percent(cell(4))
        out.append(WeeklyRow(
            date=date,
            equity=equity,
            assets=assets,
            liabilities=liab,
            leverage=lev,
            weekly_pct=weekly,
            annual_log_pct=annual_log,
        ))
    return out


def parse_asset_management(rows: list[list[str]]) -> dict[str, Any]:
    """AssetManagement: non-tabular layout.

    Col J/K = asset categories + 權益, col L/M = liabilities.
    Rows 7..end col J/K also carry stock holdings breakdown with col I holding
    a "% of portfolio" value.
    """
    result: dict[str, Any] = {
        "as_of": rows[0][0].strip() if rows and rows[0] else "",
        "equity": None,
        "assets": None,
        "liabilities": None,
        "leverage": None,
        "asset_breakdown": [],  # [{name, amount}]
        "liability_breakdown": [],
        "holdings": [],  # [{ticker, amount, pct_of_portfolio}]
    }

    def safe(r: int, c: int) -> str:
        if r < len(rows) and c < len(rows[r]):
            return rows[r][c]
        return ""

    # Row 0: leverage (K0) + equity (M0)
    result["leverage"] = parse_number(safe(0, 10))
    result["equity"] = parse_number(safe(0, 12))
    # Row 1: assets (K1) + liabilities (M1)
    result["assets"] = parse_number(safe(1, 10))
    result["liabilities"] = parse_number(safe(1, 12))

    # Cash/FX breakdown: rows 2..5 columns J (9) / K (10)
    cash_total = 0.0
    for ri in range(2, min(6, len(rows))):
        name = safe(ri, 9).strip()
        amt = parse_number(safe(ri, 10))
        if name and amt is not None:
            cash_total += amt

    # Liability breakdown: rows 2..8 cols L/M (skip header-ish row 1 which is
    # the aggregate "負債" total — we already have it in result["liabilities"]).
    for ri in range(2, min(8, len(rows))):
        name = safe(ri, 11).strip()
        amt = parse_number(safe(ri, 12))
        if name and amt is not None and name not in {"權益", "資產", "負債"}:
            result["liability_breakdown"].append({"name": name, "amount": amt})

    # Holdings: from row 7 onwards.  Column structure is:
    #   col 1 = per-share price, col 2 = shares held, col 8 = 目前比例 (pct),
    #   col 9 = ticker / fund name, col 10 = market value (TWD)
    for ri in range(7, len(rows)):
        ticker = safe(ri, 9).strip()
        amt = parse_number(safe(ri, 10))
        pct = parse_percent(safe(ri, 8))
        if ticker and amt is not None and amt > 0:
            result["holdings"].append({
                "ticker": ticker,
                "amount": amt,
                "pct_of_portfolio": pct,
            })

    # Sort holdings desc by amount
    result["holdings"].sort(key=lambda h: h["amount"], reverse=True)

    # Build a broader asset allocation bucket from holdings + cash + real assets
    BUCKETS = {
        "股票 (個股/基金)": {"達飆", "TPE:2330", "TPE:2412"},
        "美股 ETF": {"TOPT", "QTOP", "QQQ", "IOO"},
        "黃金": {"GLDM"},
        "加密貨幣": {"IBIT"},
        "債券/避險": {"BOXX", "ZROZ", "DBMF", "KMLM", "CTA"},
    }
    bucket_totals: dict[str, float] = {k: 0.0 for k in BUCKETS}
    other_total = 0.0
    for h in result["holdings"]:
        t = h["ticker"]
        placed = False
        for bucket, tickers in BUCKETS.items():
            if t in tickers:
                bucket_totals[bucket] += h["amount"]
                placed = True
                break
        if not placed:
            other_total += h["amount"]
    if other_total > 0:
        bucket_totals["其他資產"] = other_total
    if cash_total > 0:
        bucket_totals["現金"] = cash_total
    result["asset_breakdown"] = [
        {"name": k, "amount": v} for k, v in bucket_totals.items() if v > 0
    ]
    result["asset_breakdown"].sort(key=lambda x: x["amount"], reverse=True)
    return result


def build_networth_payload(
    weekly: list[WeeklyRow],
    am: dict[str, Any],
) -> dict[str, Any]:
    # Pick current equity: prefer AssetManagement (updated daily); fallback to latest weekly
    equity_now = am.get("equity")
    assets_now = am.get("assets")
    liab_now = am.get("liabilities")
    if equity_now is None and weekly:
        equity_now = weekly[-1].equity
        assets_now = weekly[-1].assets
        liab_now = weekly[-1].liabilities

    # deltas from weekly history (not perfectly aligned to calendar day but
    # good enough for at-a-glance)
    def delta(days: int) -> dict[str, float | None]:
        if not weekly or equity_now is None:
            return {"abs": None, "pct": None}
        # find weekly row ~N days ago
        try:
            target_dt = datetime.strptime(weekly[-1].date, "%Y/%m/%d") - timedelta(days=days)
            best = None
            for w in weekly:
                dt = datetime.strptime(w.date, "%Y/%m/%d")
                if dt <= target_dt:
                    best = w
            if best is None:
                best = weekly[0]
            prev = best.equity
            abs_d = equity_now - prev
            pct_d = (abs_d / prev * 100.0) if prev else None
            return {"abs": abs_d, "pct": pct_d, "from": best.date, "from_equity": prev}
        except Exception:
            return {"abs": None, "pct": None}

    ytd_base = None
    if weekly:
        cur_year = weekly[-1].date[:4]
        for w in weekly:
            if w.date[:4] == cur_year:
                ytd_base = w
                break

    ytd = None
    if ytd_base and equity_now is not None:
        ytd_abs = equity_now - ytd_base.equity
        ytd = {
            "abs": ytd_abs,
            "pct": (ytd_abs / ytd_base.equity * 100.0) if ytd_base.equity else None,
            "from": ytd_base.date,
            "from_equity": ytd_base.equity,
        }

    # Weekly sparkline last 12 weeks
    sparkline = [
        {"date": w.date, "equity": w.equity} for w in weekly[-12:]
    ]

    # Top holdings by value
    top_holdings = am.get("holdings", [])[:7]

    # FIRE progress vs NTD 21M equity
    fire_pct = (equity_now / FIRE_TARGET_NTD * 100.0) if equity_now else None

    debt_to_asset = None
    if assets_now and liab_now is not None and assets_now > 0:
        debt_to_asset = (liab_now / assets_now) * 100.0

    return {
        "generated_at": taipei_now_iso(),
        "as_of": am.get("as_of", ""),
        "equity": equity_now,
        "assets": assets_now,
        "liabilities": liab_now,
        "leverage": am.get("leverage"),
        "debt_to_asset_pct": debt_to_asset,
        "delta_7d": delta(7),
        "delta_30d": delta(30),
        "delta_ytd": ytd,
        "sparkline": sparkline,
        "asset_breakdown": am.get("asset_breakdown", []),
        "liability_breakdown": am.get("liability_breakdown", []),
        "top_holdings": top_holdings,
        "fire_target_ntd": FIRE_TARGET_NTD,
        "fire_pct": fire_pct,
        "currency": "NTD",
    }


# --- Spending -----------------------------------------------------------


def parse_transactions(rows: list[list[str]]) -> list[dict[str, Any]]:
    if len(rows) < 2:
        return []
    txns: list[dict[str, Any]] = []
    for r in rows[1:]:
        if not r or not r[0].strip():
            continue
        date = r[0].strip()
        if not re.match(r"^\d{4}/\d{1,2}/\d{1,2}", date):
            continue
        item = r[1] if len(r) > 1 else ""
        category = r[2] if len(r) > 2 else ""
        amount = parse_number(r[3] if len(r) > 3 else 0) or 0.0
        payer = r[5] if len(r) > 5 else ""
        txns.append({
            "date": date,
            "item": item,
            "category": category,
            "amount": amount,
            "payer": payer,
        })
    return txns


def parse_spending_summary(rows: list[list[str]]) -> dict[str, Any]:
    """記帳匯總 aggregate block.

    Row 0 col F..J = label "支出" + 4 period values (likely 1m / 3m / 6m / 12m).
    Row 1 col F..J = label "收入" + 4 period values.
    Row 2 col F..J = label "儲蓄率\\投報率" + 4 period values.
    """

    def safe(r: int, c: int) -> str:
        if r < len(rows) and c < len(rows[r]):
            return rows[r][c]
        return ""

    def parse_row(ri: int) -> list[float | None]:
        return [parse_number(safe(ri, c)) for c in (6, 7, 8, 9)]

    return {
        "expense_periods": parse_row(0),
        "income_periods": parse_row(1),
        "savings_rate_pct": [parse_percent(safe(2, c)) for c in (6, 7, 8, 9)],
        "period_labels": ["1M", "3M", "6M", "12M"],
    }


def build_spending_payload(
    txns: list[dict[str, Any]],
    summary: dict[str, Any],
    equity_now: float | None,
) -> dict[str, Any]:
    # This month totals
    now = datetime.now(timezone(TAIPEI_OFFSET))
    ym = now.strftime("%Y/%m")
    this_month_txns = [t for t in txns if t["date"].startswith(ym)]
    month_total = sum(t["amount"] for t in this_month_txns)
    by_category: dict[str, float] = {}
    for t in this_month_txns:
        by_category[t["category"]] = by_category.get(t["category"], 0.0) + t["amount"]
    top_cats = sorted(
        [{"category": k or "(uncategorized)", "amount": v} for k, v in by_category.items()],
        key=lambda x: x["amount"],
        reverse=True,
    )[:5]

    # Last 30 days daily spending
    cutoff = now - timedelta(days=30)
    daily: dict[str, float] = {}
    for t in txns:
        try:
            dt = datetime.strptime(t["date"], "%Y/%m/%d")
        except ValueError:
            continue
        if dt >= cutoff.replace(tzinfo=None):
            key = dt.strftime("%Y-%m-%d")
            daily[key] = daily.get(key, 0.0) + t["amount"]
    daily_list = sorted(
        [{"date": k, "amount": v} for k, v in daily.items()], key=lambda x: x["date"]
    )

    recent_5 = sorted(txns, key=lambda t: t["date"], reverse=True)[:5]

    # FIRE progress
    fire_pct = (equity_now / FIRE_TARGET_NTD * 100.0) if equity_now else None
    # ETA at current monthly savings rate: use summary 1-month income - 1-month expense
    eta_months = None
    monthly_saving = None
    if summary["income_periods"] and summary["expense_periods"]:
        inc = summary["income_periods"][0]
        exp = summary["expense_periods"][0]
        if inc is not None and exp is not None:
            monthly_saving = inc - exp
            if monthly_saving > 0 and equity_now is not None:
                remaining = FIRE_TARGET_NTD - equity_now
                if remaining > 0:
                    eta_months = remaining / monthly_saving
                else:
                    eta_months = 0

    return {
        "generated_at": taipei_now_iso(),
        "currency": "NTD",
        "month_label": ym,
        "month_total": month_total,
        "month_txn_count": len(this_month_txns),
        "top_categories_mtd": top_cats,
        "recent_transactions": recent_5,
        "daily_last_30": daily_list,
        "summary": summary,
        "fire_target_ntd": FIRE_TARGET_NTD,
        "fire_pct": fire_pct,
        "equity_now": equity_now,
        "monthly_saving_ntd": monthly_saving,
        "fire_eta_months": eta_months,
        "passive_income_target_ntd": PASSIVE_INCOME_TARGET_NTD,
    }


# --- Market cap ---------------------------------------------------------


def parse_cmc_rows(rows: list[list[str]]) -> list[dict[str, Any]]:
    """CMC tab top 200."""
    if len(rows) < 2:
        return []
    out: list[dict[str, Any]] = []
    for r in rows[1:]:
        if not r or not r[0].strip():
            continue
        rank = parse_number(r[0])
        if rank is None:
            continue
        def cell(i: int) -> str:
            return r[i] if i < len(r) else ""
        name = cell(1).strip()
        symbol = cell(2).strip()
        marketcap = parse_number(cell(3))
        price = parse_number(cell(4))
        country = cell(5).strip()
        sector = cell(6).strip()
        industry = cell(7).strip()
        # Weekly % changes: columns 26 and 27 (two most recent weeks)
        wk1 = parse_percent(cell(26))
        wk2 = parse_percent(cell(27))
        out.append({
            "rank": int(rank),
            "name": name,
            "symbol": symbol,
            "marketcap": marketcap,
            "price_usd": price,
            "country": country,
            "sector": sector,
            "industry": industry,
            "weekly_pct_recent": wk2,  # most recent
            "weekly_pct_prev": wk1,
        })
        if len(out) >= 200:
            break
    return out


def parse_summary_tab(rows: list[list[str]]) -> list[dict[str, Any]]:
    out = []
    if len(rows) < 2:
        return out
    for r in rows[1:]:
        if not r or not r[0].strip() or r[0].strip() == "總和":
            continue
        out.append({
            "sector": r[0].strip(),
            "w100_pct": parse_percent(r[1] if len(r) > 1 else ""),
            "zp_pct": parse_percent(r[2] if len(r) > 2 else ""),
            "rs_avg_pct": parse_percent(r[3] if len(r) > 3 else ""),
            "rs_weighted_pct": parse_percent(r[4] if len(r) > 4 else ""),
        })
    return out


def build_marketcap_payload(
    cmc: list[dict[str, Any]],
    summary: list[dict[str, Any]],
    etf_rows: list[list[str]],
    holdings: list[dict[str, Any]],
) -> dict[str, Any]:
    top10 = cmc[:10]

    # Only rank<=200 with a valid weekly_pct_recent
    ranked = [c for c in cmc if c.get("weekly_pct_recent") is not None]
    gainers = sorted(ranked, key=lambda c: c["weekly_pct_recent"], reverse=True)[:5]
    losers = sorted(ranked, key=lambda c: c["weekly_pct_recent"])[:5]

    # ETF summary: count rows per ETF
    etf_summary: dict[str, int] = {}
    for r in etf_rows[1:] if etf_rows else []:
        if len(r) >= 8:
            etf = r[7].strip()
            if etf:
                etf_summary[etf] = etf_summary.get(etf, 0) + 1
    etf_list = [{"etf": k, "holdings": v} for k, v in etf_summary.items()]

    # Cross-reference: which TOP 200 symbols does Edward hold?
    holding_tickers = {h["ticker"].upper() for h in holdings}
    # normalise CMC symbols (AAPL, NVDA, etc.) vs holdings (some are "TPE:2330")
    hold_symbols_clean: set[str] = set()
    for t in holding_tickers:
        if ":" in t:
            hold_symbols_clean.add(t.split(":")[-1])
        hold_symbols_clean.add(t)
    owned_in_top200 = [
        c for c in cmc if c["symbol"].upper() in hold_symbols_clean
        or c["name"].upper() in hold_symbols_clean
    ]

    return {
        "generated_at": taipei_now_iso(),
        "top10": top10,
        "top200_count": len(cmc),
        "weekly_gainers": gainers,
        "weekly_losers": losers,
        "sector_summary": summary,
        "etf_summary": sorted(etf_list, key=lambda x: x["holdings"], reverse=True),
        "owned_in_top200": owned_in_top200,
    }


# --- Main ---------------------------------------------------------------


def build_all(force_refresh: bool = False) -> dict[str, Any]:
    RESULTS.mkdir(parents=True, exist_ok=True)
    tabs = fetch_all_tabs(force=force_refresh)

    weekly = parse_weekly_tab(tabs.get("週報", []))
    am = parse_asset_management(tabs.get("AssetManagement", []))
    networth = build_networth_payload(weekly, am)
    NETWORTH_JSON.write_text(
        json.dumps(networth, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    txns = parse_transactions(tabs.get("記帳", []))
    spend_summary = parse_spending_summary(tabs.get("記帳匯總", []))
    spending = build_spending_payload(txns, spend_summary, networth.get("equity"))
    SPENDING_JSON.write_text(
        json.dumps(spending, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    cmc = parse_cmc_rows(tabs.get("CMC", []))
    sector_summary = parse_summary_tab(tabs.get("Summary", []))
    marketcap = build_marketcap_payload(
        cmc, sector_summary, tabs.get("ETF data", []), am.get("holdings", [])
    )
    MARKETCAP_JSON.write_text(
        json.dumps(marketcap, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return {
        "networth": str(NETWORTH_JSON),
        "spending": str(SPENDING_JSON),
        "marketcap": str(MARKETCAP_JSON),
        "networth_preview": {
            "equity": networth.get("equity"),
            "fire_pct": networth.get("fire_pct"),
        },
        "spending_preview": {
            "month_total": spending.get("month_total"),
            "monthly_saving": spending.get("monthly_saving_ntd"),
        },
        "marketcap_preview": {
            "top10_count": len(marketcap.get("top10", [])),
            "owned_in_top200": len(marketcap.get("owned_in_top200", [])),
        },
    }


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="[finance] %(message)s")
    force = "--force" in sys.argv
    try:
        result = build_all(force_refresh=force)
    except Exception as exc:
        logger.exception("build_all failed: %s", exc)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
