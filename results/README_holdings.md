# holdings.yaml — Edward's Single Source of Truth

## What this is

`holdings.yaml` (this directory) is the **only** file you edit to track your
AssetManagement state. Everything downstream is derived from it.

```
holdings.yaml        <-- you edit (qty, cost_basis, cash, liabilities)
     |
     v
balance_sheet_builder.py  (runs every 30 min via mc_balance_sheet task)
     |  reads holdings.yaml + finance_marketcap.json (fresh prices)
     |  computes: market_value, unrealized_pnl, net_worth, allocations
     v
finance_networth.json   <-- consumed by /api/finance and /finance dashboard
```

The Google Sheet "AssetManagement" tab is now **redundant** for live prices
(market_updater.py owns that every 30 min). Keep the sheet for 本金 / 帳戶結構
reference, but do NOT re-enter prices there.

## Schema (see holdings.yaml for the full skeleton)

```yaml
as_of: "2026-04-11"          # last Edward-edit date (Asia/Taipei)
base_currency: "TWD"          # reporting currency for the balance sheet

cash:
  - account: "國泰台幣"        # human label — free form
    currency: "TWD"            # TWD / USD / USDT / ...
    balance: 123456            # native currency amount

positions:
  - ticker: "2330.TW"          # yfinance / Yahoo symbol
    qty: 100                   # shares or units
    cost_basis: 580            # per-share average, in `currency`
    currency: "TWD"            # native currency of the position
    category: "股票/台股"       # used for asset_allocation_by_category
    account: "永豐台股"         # broker / exchange (reference only)
    note: "台積電"              # optional

liabilities:
  - name: "房貸"
    balance: 0000000           # current outstanding, positive number
    currency: "TWD"
```

### Ticker format rules

| Market | Format | Example |
|---|---|---|
| 台股 | `XXXX.TW` | `2330.TW` |
| 台股 OTC | `XXXX.TWO` | `6488.TWO` |
| 美股 | plain symbol | `NVDA`, `AAPL` |
| 港股 | `XXXX.HK` | `0700.HK` |
| 日股 | `XXXX.T` | `7203.T` |
| 加密貨幣 | `SYM-USD` | `BTC-USD`, `ETH-USD` |

The builder also looks up the ticker in `finance_marketcap.json` first
(already fresh from market_updater). If not found there, it falls back to
live yfinance. Positions with `qty == 0` are kept in the file but contribute
0 to the balance sheet.

## Running manually

```bash
cd C:\Users\admin\workspace\digital-immortality
python platform\balance_sheet_builder.py
```

Writes to `results/finance_networth.json`. Reports total net worth, top
holdings, unrealized P&L, allocation by category + currency.

## Scheduled task

Registered as `mc_balance_sheet` — runs every 30 minutes. Check with:

```bash
schtasks /Query /TN mc_balance_sheet
```

Logs: `results/balance_sheet_builder.log`.

## FX handling

The builder converts everything to `base_currency` (default TWD):
- TWD native -> 1.0
- USD / USDT -> fetches `TWDUSD=X` from yfinance (inverted to get TWD per USD)
- Other currencies: looked up via yfinance `{CCY}TWD=X` pair

FX rates are cached for 60 minutes inside the builder process.

## The new workflow

| Old (manual) | New (pipeline) |
|---|---|
| Hand-type balances into Google Sheet | Edit holdings.yaml |
| Weekly 達飆 estimate manually into Sheet | POST /api/finance/pnl_weekly from UI/Discord |
| CC statement -> manual Sheet entries | Drop CSV in `staging/finance_inbox/` |
| Cash spending -> manual Sheet entries | POST /api/finance/spending from UI/Discord |
| Prices copy-pasted weekly | market_updater.py every 30 min |
