# 市值 (Market Cap) 欄位定義

Source endpoint: `GET /api/market` (served by `.claude/scripts/mission_control/server.py::build_market_payload`).
Backing file: `workspace/digital-immortality/results/finance_marketcap.json`.
Populated by: `platform/market_updater.py` — scheduled via `/run market_updater`.
Refresh cadence: 市場頁前端每 60 秒呼叫一次 `/api/market`; 來源檔本身由 `market_updater` 依排程覆寫 (一般日內多次)。
Freshness 顯示: header `Fin:<age_min>m` — 由 `data_fresh.finance` 欄位提供。

## Buckets (top-level fields)

| Field | Type | 說明 |
|---|---|---|
| `generated_at` | ISO8601 (Asia/Taipei +08) | 此回應產生時間 |
| `source_generated_at` | ISO8601 | 來源 `finance_marketcap.json` 上次更新時間 |
| `source_exists` | bool | 來源檔是否存在 |
| `top10` | list<Row> | 絕對市值 Top 10 |
| `weekly_gainers` | list<Row> | 本週漲幅榜 |
| `weekly_losers` | list<Row> | 本週跌幅榜 |
| `by_derivative` | list<Row> | 合併以上三桶, 依 \|Δ週變化\| 排序 (導數優先) |
| `sector_summary` | list<Sector> | 產業別小計 |
| `watchlist` | list<WatchRow> | Edward 追蹤個股 |
| `crypto` | list<WatchRow> | 加密貨幣追蹤 |

## Row schema (top10 / gainers / losers / by_derivative)

| 欄位 (key) | 中文名 | 單位 | 資料源 / 計算 |
|---|---|---|---|
| `symbol` | 代碼 | 交易所 ticker | market_updater 抓取 |
| `name` | 公司名 | string | 交易所 metadata |
| `country` | 上市國 | ISO 2-letter 或地區碼 | 資料源標籤 |
| `sector` | 產業 | string | 資料源分類 |
| `marketcap` | 市值 | USD (十億為單位顯示: `$XXX.XB`) | **股價 × 流通股數**, 由資料源提供當日值 |
| `weekly_pct_recent` | 本週變化% | percent (小數, e.g. 0.032 = 3.2%) | (本週收盤 − 上週收盤) / 上週收盤 |
| `weekly_pct_prev` | 上週變化% | percent | 前一週同計算 |
| `rank` | 原排名 | int | 來源桶的原始排序 (top10 內部名次) |

導數 (Δ) 顯示: `weekly_pct_recent − weekly_pct_prev` → 展現本週相對上週的加速/減速。

## WatchRow schema (watchlist)

| 欄位 | 單位 | 說明 |
|---|---|---|
| `symbol` | ticker | e.g. `TSM`, `2330.TW` |
| `label` | string | 顯示名 |
| `category` | string | 分類標籤 (e.g. 半導體 / AI) |
| `price_native` | 原幣別價格 | 依市場本幣 (TWD/USD/...) |
| `price_usd` | USD 價格 | 統一換算 |
| `currency` | ISO 4217 | 原幣別代碼 (`TWD` / `USD` / ...) |
| `weekly_pct` | percent (小數) | 本週變化 |

## CryptoRow schema (crypto bucket)

> 注意: crypto bucket 欄位與 watchlist 不同 — 使用 `weekly_pct_recent` 而非 `weekly_pct`, 且無原幣別欄位 (一律 USD 報價)。

| 欄位 | 單位 | 說明 |
|---|---|---|
| `symbol` | ticker | e.g. `BTC-USD`, `ETH-USD` |
| `label` | string | 顯示名 |
| `price_usd` | USD 價格 | 24/7 即時報價 |
| `weekly_pct_recent` | percent (小數) | 過去 7 日變化 (24/7 市場, 不套週界) |
| `weekly_pct_prev` | percent (小數) | 前一週變化 (若資料源提供) |

## 格式化函式

- `fmtMC(x)` — `market.html:renderRows` 內部, 把 marketcap 數字 (USD) 以 `$X.XB` / `$X.XT` 顯示
- `fmtPct(x)` — 百分比顯示, 加 `+/−` 號與上色 (綠/紅/灰)
- `changeClass(x)` — 依 `x` 判定 `up|down|flat` class, 閾值 ±0.05 (= ±5%)

## 驗證

新增欄位時:
1. 先在此文件加 row + 單位 + 資料源
2. 再改 `build_market_payload` / `renderRows`
3. UI 若加欄位, 加 `title=""` tooltip 點擊顯示本文件摘要

## 已知限制

- `marketcap` 幣別固定 USD; 非美股需 market_updater 端先換算
- `weekly_pct_*` 週界定為資料源日曆週 (通常 Mon→Fri 收盤)
- `crypto` bucket 24/7, 不套用週界; `weekly_pct` = 過去 7 日
