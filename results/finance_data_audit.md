# Finance Data Pipeline Audit

Generated: 2026-04-11 (Asia/Taipei)
Scope: `/api/finance` data path for Mission Control dashboard.

## TL;DR

Edward's question: "finance 裡面的資料庫會存在哪裡? 市場價格資料那些應該是隨時更新?"

1. **Where does the data live?**
   Three local JSON files under
   `C:\Users\admin\workspace\digital-immortality\results\`:
   - `finance_networth.json`
   - `finance_spending.json`
   - `finance_marketcap.json`

   These are produced by `platform/build_finance_dashboards.py`, which
   pulls 7 tabs from a private Google Sheet ("財務管理") via a Google
   service account credential stored under
   `%USERPROFILE%\.claude\credentials\` (gitignored, local-only).
   Raw sheet pulls are cached to `results/.sheet_cache/` with 1h TTL.

   **Source of truth = the Google Sheet.** The JSONs are a derived cache
   intentionally not committed to git (see `.gitignore` and
   `staging/finance_dashboard_privacy_note.md` — they contain absolute NTD
   amounts).

2. **Are market prices auto-refreshing?**
   **No — not until this audit.** Prior to 2026-04-11 18:27 Taipei the only
   way prices got refreshed was whenever Edward (or the recursive daemon)
   happened to re-run `build_finance_dashboards.py`, which pulls price
   columns straight from the CMC tab in the Sheet — which itself was
   hand-edited / manually refreshed. Stale prices were visible (e.g.
   Aramco 2222.SR listed at `7.2485` vs real `~27.20`).

   Fix shipped in this audit: new `platform/market_updater.py` + Windows
   Task Scheduler entry `mc_market_updater` running every 30 minutes.

## File-by-File

### 1. `finance_networth.json` (3,011 bytes)

- **Last modified:** 2026-04-11 17:00:15 Taipei
- **Writer:** `platform/build_finance_dashboards.py` (function
  `build_networth_payload`)
- **Source tabs:** 現狀, 每週紀錄, TOP (holdings)
- **Schema:** equity/assets/liabilities in NTD, 7/30/ytd deltas, sparkline
  of weekly equity checkpoints, `top_holdings` (ticker + NTD amount),
  FIRE target.
- **Freshness mechanism:** manual re-run of the builder. The values are
  NTD book amounts, not live-priced — refreshing tick-by-tick would be
  meaningless since Edward updates the Sheet weekly.
- **Verdict:** **OK as-is.** Market updater should NOT touch this file.

### 2. `finance_spending.json` (2,524 bytes)

- **Last modified:** 2026-04-11 17:00:15 Taipei
- **Writer:** same `build_finance_dashboards.py`
- **Source tabs:** 流水帳, 每月
- **Schema:** month-to-date total, top categories MTD, recent transactions,
  daily last-30, summary periods (1M/3M/6M/12M income/expense/savings-rate).
- **Freshness mechanism:** same as networth — rebuilt on demand by the
  daemon; transactions come from the Sheet's ledger tab.
- **Verdict:** **OK as-is.** Spending is discrete events, not a
  continuous price feed. No market updater role.

### 3. `finance_marketcap.json` (8,676 bytes)

- **Last modified (pre-audit):** 2026-04-11 17:00:15 Taipei
- **Last modified (post-audit):** 2026-04-11 18:27:24 Taipei (market_updater)
- **Writer(s):**
  - `platform/build_finance_dashboards.py` (initial build + Sheet fields)
  - `platform/market_updater.py` (new — price refresh only)
- **Source tabs:** CMC (top 200), Summary (sector %), ETF (IOO/QTOP/TOPT)
- **Schema:** `top10`, `top200_count`, `weekly_gainers`, `weekly_losers`,
  `sector_summary`, `etf_summary`, `owned_in_top200`, plus new
  `updated_at`, `stale`, `price_source` fields added by the updater.
- **Freshness mechanism (new):** `mc_market_updater` scheduled task,
  30-minute cadence, 24/7. Refreshes `price_usd` in every bucket that
  carries a `symbol` field.
- **Verdict:** **was stale (e.g. Aramco price way off), now refreshing
  every 30 min.** Full schema preserved.

## GitHub Actions Workflow

**Status: does not exist.**

Searched `C:\Users\admin\workspace\digital-immortality\.github\workflows\`:

```
daemon_failsafe.yml      (recursive daemon heartbeat)
heartbeat_typeA.yml      (daily cold-start health)
recursive_cycle.yml      (recursive engine tick)
writeback_distillation.yml (memory writeback)
```

No `finance_pull.yml` / `finance_marketcap.yml` / anything finance-related.
Session state mentioned it as "TBD" — confirmed: never committed, never
ran. Moot now because the price refresh is local (GitHub Actions couldn't
reach the local results dir anyway without pushing the files, which the
privacy note forbids).

## Related Scripts Inventory

| Path | Role |
|------|------|
| `platform/build_finance_dashboards.py` | 700-line main builder: Sheets → 3 JSONs. Cache in `results/.sheet_cache/`. |
| `platform/finance_audit.py` | One-shot Sheet introspection (dumps tab headers + samples to `staging/financial_dashboards_audit.json`). |
| `platform/market_updater.py` | **NEW** — price-only refresher; runs every 30 min. |
| `.claude/scripts/mission_control/server.py` `/api/finance` | HTTP endpoint that reads the 3 JSONs and serves them to the dashboard. Not modified in this audit. |
| `results/.sheet_cache/` | 1h TTL cache for raw Sheet pulls. |
| `results/market_updater.log` | **NEW** — append-only log for each updater run. |

No related workflow under `C:\Users\admin\GoogleDrive\staging\`.

## market_updater.py Design Notes

- **Primary source:** `yfinance` (v1.2.0, already installed in user env).
  Uses `Ticker(symbol).history(period='1d')` and takes the last Close.
- **Fallback:** Stooq free CSV at
  `https://stooq.com/q/l/?s={sym}.us&f=sd2t2ohlcv&h&e=csv` for US-only
  symbols. No auth, no key, no credit card — aligned with Edward's
  "minimize external services" rule.
- **Symbols refreshed:** whatever is present in the existing
  `finance_marketcap.json` buckets (`top10`, `weekly_gainers`,
  `weekly_losers`, `owned_in_top200`). First run picked up 15 distinct
  symbols:
  NVDA, AAPL, GOOG, MSFT, AMZN, TSM, AVGO, 2222.SR, META, TSLA, TM,
  COST, 005930.KS, 000660.KS, TCEHY.
- **Resilience:** per-symbol try/except; if everything fails the file is
  re-written with `updated_at` + `stale: true` so the dashboard can render
  a staleness warning without nuking the last-known-good data.
- **Atomic writes:** temp file + `os.replace` so the MC server never
  reads a half-written JSON.
- **Logging:** `logging.FileHandler` → `results/market_updater.log`, no
  stdout/stderr chatter (scheduled-task-friendly).
- **Never touches:** `finance_networth.json`, `finance_spending.json`,
  `server.py`, any running process.

## First-Run Result

```
2026-04-11 18:27:22 === market_updater run start ===
collected 15 distinct symbols
2026-04-11 18:27:24 updated 15 / 15 symbols
  NVDA=188.63 AAPL=260.48 GOOG=315.72 MSFT=370.87 AMZN=238.38
  TSM=370.6  AVGO=371.55 2222.SR=27.2 META=629.86 TSLA=348.95
  TM=210.64  COST=998.47 005930.KS=206000.0 000660.KS=1027000.0
  TCEHY=63.98
updated_entries_in_buckets=20
=== market_updater run end (ok) ===
```

100% success rate on first run.

## Known Caveats

1. **Non-US tickers return native currency.** yfinance returns
   005930.KS (Samsung) in KRW, 000660.KS (SK Hynix) in KRW, 2222.SR
   (Aramco) in SAR. The schema field is named `price_usd` but was
   already storing native-currency values before this audit. Not a new
   bug introduced by the updater. A proper fix is an FX normalization
   step (future work — Stooq has FX pairs, or yfinance `=X` symbols).
2. **Weekly pct fields not updated.** `weekly_pct_recent` /
   `weekly_pct_prev` stay as whatever the Sheet builder last wrote.
   That data lives on the CMC tab and is only valuable at weekly
   cadence, so not worth recomputing every 30 min.
3. **Market cap not updated.** Same reason — updater only refreshes
   price. If Edward wants live market cap it's `price * shares_outstanding`
   which would require another yfinance call per symbol.
4. **Stooq only covers US tickers** via the simple `.us` suffix mapping;
   foreign tickers fall back to yfinance-only (which is the right tool
   for them anyway).

## Scheduler Registration

```
schtasks /Create /SC MINUTE /MO 30 /TN mc_market_updater ^
  /TR "pythonw C:\Users\admin\workspace\digital-immortality\platform\market_updater.py" /F
```

Verified with `schtasks /Query /TN mc_market_updater`:

- Task name: `\mc_market_updater`
- Status: Ready (就緒)
- Schedule: every 30 minutes, 24/7
- Next run: 2026-04-11 18:58 Taipei
- Runs as: `EDWARD-IDC\admin`
- Uses `pythonw` (headless — no console flash on each run)

## Path Forward (Prioritized)

1. **Monitor a few cycles.** Tail `results/market_updater.log` tomorrow
   and confirm the 30-min runs are stable. If yfinance rate-limits,
   switch to Stooq primary for US tickers.
2. **Dashboard freshness badge.** Surface `updated_at` and `stale` in the
   MC UI so at-a-glance you can see when data last moved. (UI-side work,
   no server change needed — `/api/finance` already serves the full JSON.)
3. **FX normalization pass (optional).** Add a ccy map and convert KRW /
   SAR / etc. to USD using yfinance `KRW=X`, `SAR=X`. Until then,
   rename the field to `price_native` in a future Sheet builder refactor
   to stop lying with the name.
4. **Retire the Google Sheet as price source.** The CMC tab is
   hand-maintained; long-term the price columns should be dropped from
   the Sheet and the builder should just emit tickers+names, letting
   market_updater.py be the only authority on prices.
5. **No GitHub Actions workflow needed.** Local Task Scheduler covers it
   and respects the privacy constraint (JSONs never leave the machine).
