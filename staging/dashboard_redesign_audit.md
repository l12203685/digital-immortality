# Dashboard Redesign Audit — 2026-04-11

> Edward 抱怨：「github 上的 dashboard 很不即時欸 呈現上也一點都不白話不直觀 主力機上的 dashboard 也是 你要不要參考一下 UIUX 的那個 skill」

## 核心問題

1. **不即時** — GitHub Pages meta refresh=300s（5 分鐘），daemon rebuild 有延遲 → 看到的永遠是舊資料。
2. **不白話** — 整排 key-value 全是英文技術字：`kill_window`, `PF`, `WR`, `MDD`, `B6`, `cycle`, `insight_count`, `commit SHA`, `RAM`, `context_pct`。非工程師完全看不懂。
3. **沒層次** — 全部 panel 同一個 size、同一個顏色、同一個密度。看了不知道哪個該先看、哪個可以忽略。
4. **行動不明確** — 沒有「你現在該動什麼」的單一出口。Edward 一打開 dashboard 不知道要幹嘛。
5. **行動電話不能看** — `minmax(420px,1fr)` grid 在手機上會橫向捲動。

---

## 目前 GitHub Dashboard — 逐區稽核

### Section 1: 頂部 Hero（不存在）
- ❌ **缺** 三個大字狀態：永生是否健康 / 主腦在線 / 待動作數
- 目前只有一行小字 `updated: ...`

### Section 2: Mission Control (`.mc-wrap`)
已有的內容（先前 subagent 加的）：
| 欄位 | Edward 看得懂? | 可動作? |
|------|----------------|---------|
| 主腦：在線 （0.4 分鐘前） | ✅ | ambient |
| 🎯 待你決策 卡片 ×5 | 🟡 （技術動詞） | ✅ |
| 📝 等你批准 SOP 卡片 | ❌ 標題像 `SOP #122 — Gate-Constrained Regime Operating Protocol` | ✅ |
| 🚀 進行中 | 🟡 | ambient |
| ✅ 剛完成 | ✅ | ambient |
| 🚧 卡住 | ✅ | ✅ |
| 📋 自動 backlog top 5 | ✅ | ambient |

**問題**：decision 卡片文字太長、混中英、有 `reframed`, `migration`, `cadence` 等字。

### Section 3: 永生樹 (7 branches)
- 欄位：`num`, `title`, `first`
- Edward 看得懂? ✅ 但 `first` 行塞了技術細節 `DNA v3.63 + 330 MDs + DIF`
- 可改進：每條 branch 只顯示一行白話進度，不要 dump raw text。

### Section 4: Trading
**engine 區：**
| 欄位 | 翻譯 |
|------|------|
| mode PAPER | 模式：模擬（未實單） |
| regime mixed | 市場狀態：混亂 |
| price $72770.73 | BTC 現價 $72,770 |
| tick_count 237 | 累計跑了 237 次 |
| active 13 | 策略：13 個運作中 |
| disabled 6 | 策略：6 個休眠 |
| total_pnl -0.1865% | 今日損益：-0.19% |
| last_tick 2026-... | 最後心跳：4 分鐘前 |

**kill window 區（整塊技術術語）：**
| 欄位 | 該不該顯示 |
|------|------------|
| kill_window 20 | ❌ 隱藏 |
| kill_count 12 | ❌ 隱藏 |
| min_pf 0.8 | ❌ 隱藏 |
| min_wr 0.3 | ❌ 隱藏 |
| max_dd 20.0 | ❌ 隱藏 |
| last_kill DualMA_RSI_filtered — PF 0.70 < 0.8 | ❌ 隱藏 |
| evolved_at | ❌ 隱藏 |

→ 全部折進「進階細節」details 展開，預設收起。

**disabled strategies**：策略名 `gen_BollingerMeanReversion_RF_7abfe4` 完全不白話 → 改顯示「6 個策略休眠中，原因：獲利不達標」

**paper live 區：**
- `tick 1 / pnl +$0.668` → 「模擬交易損益：+$0.67」

### Section 5: Daemon
| 欄位 | 翻譯 |
|------|------|
| last_cycle 165 | 今天第 165 次自我更新 |
| b6_streak B6 93th clean | DNA 一致性 ✅ 連續 93 次正常 |
| insights 184 | 累積心得：184 條 |
| daemon_log tail | ❌ 隱藏（全是 raw log line） |

### Section 6: Agent
全部技術指標（model, tokens_in, tokens_out, context_pct, cost_usd, ram, ramdisk）→ 對 Edward 完全 noise。改折進 details，預設收起，只留「主腦健康：✅」。

### Section 7: Git — last 10 commits
10 個 commit SHA per repo → **全部刪掉**。Edward 抱怨過 commit SHA 沒意義。只留「最後更新：N 分鐘前」。

### Section 8: Blockers
已經夠白話。保留。但改成紅色卡片，放頂部 hero 下面。

---

## 設計原則（套到兩個 dashboard）

### A. Hero metrics — 1-3 個大字在最上方
```
┌──────────────────────────────────────┐
│  永生狀態         主腦在線    待你動作 │
│    健康             是          3 件  │
│  （綠大字）       （綠）      （黃）  │
└──────────────────────────────────────┘
```

### B. 翻譯對照表（見 platform/pretty_translate.py）
約 50 個技術詞 → 繁中白話。

### C. 視覺層次
- 紅色 banner 頂部：異常警示（daemon 掛了、策略爆虧）
- 黃色卡片：待你動作
- 綠色小點：健康狀態
- 灰色 details：技術細節（預設收起）

### D. 自動更新
- **GitHub Pages**：`<meta refresh="30">` 從 300 改 30 秒
- **Local MC**：已有 JS 5s polling，加「更新於 N 秒前」活時鐘 + 手動刷新鈕

### E. 手機優先
- 改用 `minmax(300px, 1fr)`，375px viewport 不會橫捲
- 主要字體 ≥16px，hero 數字 ≥32px
- Tap target ≥48px

### F. 顏色一致
- 綠 = 健康 / 完成
- 黃 = 進行中 / 注意
- 紅 = 異常 / 卡住 / 待動作
- 灰 = 閒置 / 技術細節

---

## 套到兩個 dashboard 的改動

**`platform/render_dashboard.py`**
1. 加 Hero Metrics 區（3 big numbers）
2. 加翻譯層 `pretty_translate.to_plain_zh()`
3. Trading 區：hide kill_window + rename fields
4. Daemon 區：hide raw log tail，改「健康摘要」
5. Agent 區：折進 details
6. Git 區：改成「最後更新 N 分鐘前」一行
7. 手機 friendly CSS
8. `meta refresh=30`

**`~/.claude/scripts/mission_control/index.html`**
1. 加 Hero Metrics 區（用 `/api/state` 的 dashboard + metrics 算）
2. 翻譯技術欄位名（複製 pretty_translate 的對照到 JS）
3. 手機 friendly grid
4. 加活時鐘「更新於 N 秒前」
5. 加手動刷新鈕
6. 保留現有 polling 5s

---

## 對 parallel subagents 的提醒
- **Finance subagent**：我沒碰 `finance.html` / `/api/finance` endpoint，但 Mission Control `index.html` 我會改 — 請把 finance 看作獨立頁面。
- **Timezone subagent**：我會保留現有的 `_fmt_ts_taipei()` helper，只改呼叫方。
