# SOP #07: 市場 Regime 偵測與策略路由 (Regime Detection & Strategy Routing)
> UTC: 2026-04-09T UTC | Cycle 131 | Branch 7 (知識輸出)
> Backing MDs: MD-103, MD-104, MD-107, MD-112, MD-116, MD-117

## Overview

市場有三種基本狀態（MD-103：市場三態剪刀石頭布）：
- **趨勢 (Trending)**：動能持續，打趨勢策略
- **均值回歸 (Mean-Reverting)**：波動收斂，打反轉策略
- **混沌 (Mixed/Choppy)**：兩者皆輸，縮倉等待

錯誤：用同一策略應對所有 regime → 在錯誤市場結構中強行交易。
正確：先偵測 regime → 再決定用哪個策略。

本 SOP 是 5 個 Gate 依序執行的 Regime 路由框架。

---

## G0: 計算 Regime 指標

**輸入**：過去 N 根 K 線收盤價

**指標計算（兩個）：**

| 指標 | 計算 | 意義 |
|------|------|------|
| `trend_strength` | `abs(close[-1] - close[-N]) / ATR(N)` | 趨勢動量/波動比 |
| `mr_score` | `stdev(returns, N) / mean(abs(returns), N)` | 波動集中度（高=MR） |

**閾值（從歷史數據校準）：**
- `trend_strength > 0.054` → 傾向趨勢
- `mr_score > 0.25` → 傾向均值回歸
- 兩者皆不滿足 → 混沌

**Gate 通過條件**：兩個指標都計算完成，有具體數值。

---

## G1: 分類 Regime

**決策樹：**

```
trend_strength > 0.054?
├── YES → TRENDING
└── NO → mr_score > 0.25?
         ├── YES → MEAN_REVERTING
         └── NO → MIXED
```

**重要：不要試圖預測 regime 轉換** (MD-116: 複雜度=Edge不足的偽裝)
- 只用當下觀測分類
- Regime 偵測是診斷，不是預測

**Gate 通過條件**：輸出明確的 `TRENDING / MEAN_REVERTING / MIXED`。

---

## G2: 路由策略

**標準路由表（基於 Calmar Ratio + 跨 regime 測試）：**

| Regime | 策略 | 原因 |
|--------|------|------|
| TRENDING | DualMA_10_30 | 移動均線追趨勢，低假信號 |
| MEAN_REVERTING | BollingerMR_loose | 布林帶均值回歸，適度寬帶 |
| MIXED | SKIP (縮倉) | 無邊際 → 不交易 (MD-195: 無edge不動) |

**策略合作條件** (MD-104: 策略合作指標先對齊)：
- 同一 regime 內不放相關策略（相關係數 > 0.6 = 重複曝險）
- 多策略並行時，先確認 regime 一致性

**Gate 通過條件**：有明確的策略選擇，或明確決定 SKIP。

---

## G3: 驗證策略在當前 Regime 的歷史表現

**必查三個數字** (MD-107: 年度風暴比=跨年 Regime 偵測器)：

| 數字 | 標準 | 失敗行動 |
|------|------|----------|
| 年化 Sharpe（當前 regime 子集） | > 0.5 | 降倉或 SKIP |
| Win Rate（≥5 trades） | > 35% | 觸發 Kill 條件 |
| 近期 vs 歷史 Sharpe 比 | > 60% | 降倉等 regime 穩定 |

**不要用全樣本統計** (MD-107: 全樣本掩蓋 regime 切換的降速信號)
- 一定要篩出當前 regime 的子集再看

**Gate 通過條件**：三個數字全過，或有明確的降倉理由。

---

## G4: 設定 Regime 失效條件

**進場前預設退出觸發器** (MD-112: 策略=先定賺什麼賠什麼)：

```
REGIME_FAIL 條件（任一觸發 → 停策略、重新偵測）：
- trend_strength 從 >0.054 跌至 <0.02（趨勢策略用）
- mr_score 從 >0.25 跌至 <0.10（MR 策略用）
- 連續 3 根 K 線信號方向相反
- MDD > 10%（regime 可能已轉換）
```

**Regime 切換時的正確行為** (MD-103: 市場三態剪刀石頭布)：
- 不要在過渡期硬撐
- 偵測到 MIXED → 立刻縮倉，等待 regime 確立再進
- 不要同時押趨勢 + MR（互相抵消，且兩者都在 mixed 表現差）

**Gate 通過條件**：REGIME_FAIL 條件已定義，觸發後的行動已明確。

---

## G5: 執行 + 記錄

**每次 tick 必須記錄：**

```json
{
  "timestamp": "ISO8601",
  "price": 71359.94,
  "trend_strength": 0.082,
  "mr_score": 0.18,
  "regime": "TRENDING",
  "strategy_selected": "DualMA_10_30",
  "signal": "SHORT",
  "skipped_reason": null
}
```

**記錄用途** (MD-104: 策略合作指標先對齊)：
- 事後 regime 分布分析（避免數據窺視）
- Kill 條件觸發的溯源
- 策略切換的決策審計軌跡

---

## 自我測試情境

**情境：** BTC 過去 20 根 K 線計算結果：
- `trend_strength = 0.082`（> 0.054）
- `mr_score = 0.18`（< 0.25）
- 近期 Sharpe = 0.73，歷史（趨勢子集）Sharpe = 0.81

**走過 SOP：**
- G0: 兩個指標計算完成 ✓
- G1: trend_strength > 0.054 → TRENDING ✓
- G2: 路由至 DualMA_10_30 ✓
- G3: Sharpe=0.73/0.81=90% > 60% ✓, WR 假設 55% > 35% ✓ → 通過 ✓
- G4: 設定 REGIME_FAIL: trend_strength < 0.02 → stop ✓
- G5: 記錄 regime=TRENDING, strategy=DualMA_10_30, signal=SHORT ✓

**正確輸出：** 執行 DualMA_10_30 SHORT 信號，REGIME_FAIL 條件已設定。

---

## 常見錯誤

| 錯誤 | 後果 | 修正 |
|------|------|------|
| 用全樣本 Sharpe 評估策略 | 掩蓋 regime 切換的降速 | 永遠用 regime 子集 |
| MIXED 時硬撐一個策略 | 兩種風險都沒對應 | MIXED = SKIP |
| 不設 REGIME_FAIL 條件 | 持倉跨越 regime 切換 | 進場前先設退出觸發 |
| 同時跑趨勢 + MR 策略 | 高相關 = 假分散 | 同一 regime 內確認不相關 |

---

*SOP #07 完成。系列：#01 策略開發 → #02 投組建構 → #03 執行/定位 → #04 策略止損 → #05 職涯/薪資 → #06 賽局決策 → **#07 Regime 偵測路由***
