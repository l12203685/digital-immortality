# Token Usage Optimization + Repo Restructuring Plan

---

## SATURDAY HANDOFF — READ THIS FIRST

> **Context**: This plan was written on 2026-04-10 (Friday) via Claude Web. On Saturday you'll continue via Discord Plugin. This section gives you everything to resume without re-explaining.

### Before-State Snapshot (as of 2026-04-10)

| Item | Value |
|------|-------|
| Branch | `claude/optimize-token-usage-AYEpF` |
| results/ size | 11MB (280 files) |
| docs/ size | 2.1MB (267 files) |
| memory/insights.json | 122K |
| staging/ | 7 files, 44K total |
| templates/dna_core.md | 376K (the big one) |
| index.md | **does NOT exist yet** |
| staging/quick_status.md | **does NOT exist yet** |
| templates/dna_boot.md | **does NOT exist yet** |
| .claude/settings.json | **does NOT exist yet** |

### After-State Target

| Item | Target |
|------|--------|
| results/ size | <3MB (archive cycle_001-290 → results/archive/) |
| docs/ size | ~200K (archive knowledge_product_001-100 → docs/archive/) |
| index.md | EXISTS, <400 tokens, static repo map |
| staging/quick_status.md | EXISTS, <200 tokens, daemon auto-updates |
| templates/dna_boot.md | EXISTS, ~1,540 tokens, cold-start kernel only |
| .claude/settings.json | EXISTS, SessionStart hook configured |
| CLAUDE.md | MODIFIED: 3-tier boot protocol added |
| Backup git tag | `pre-optimization-backup` created before ANY changes |

### Saturday Startup Sequence

```
1. git -C /home/user/digital-immortality tag pre-optimization-backup    # BACKUP FIRST
2. Read this file (plan file) — you're doing it now
3. Execute Phase 1: archive cleanup (commands below)
4. Execute Phase 2: create new files (code below)
5. Modify CLAUDE.md (diff below)
6. Run verification checks
7. git add -A && git commit -m "feat: token optimization — repo restructure + 3-tier boot"
8. git push -u origin claude/optimize-token-usage-AYEpF
```

### Rollback If Anything Goes Wrong
```bash
git -C /home/user/digital-immortality reset --hard pre-optimization-backup
```

---

## Context

目前系統的問題：Python daemon 已自動執行 420+ commits/day、交易 tick、memory logging，但 Claude 仍被當作「每個 cycle 都要介入」的角色，導致 token 消耗估計達 ~1.26M/day（~60 cycles × ~21K tokens）。實際上大部分 cycle 根本不需要 LLM 參與。

目標：把 Claude 的角色從「cycle-driven 循環引擎」切換成「event-driven 戰略確認員」，讓自動化系統跑 99% 的 cycles，Claude 只在需要 LLM 判斷的事件上介入。

---

## 核心原則：角色分離

### Autonomous（永不消耗 Claude token）
| 任務 | 執行方式 | 頻率 |
|------|---------|------|
| 交易 paper-live ticks | `platform/recursive_daemon.py` | 每 30 min |
| Consistency test 決定性部分 (36/39) | `consistency_test.py` deterministic | 每日 |
| Memory / insights 記錄 | `memory_manager.py` | 每 cycle |
| Recursive engine 狀態更新 | `recursive_engine.py --prompt --status` | 每 cycle |
| Git commits + staging 更新 | daemon (已在跑) | 連續 |
| Discord webhook 狀態通知 | `platform/server_config.json` webhook | 每 cycle |
| Daily log cycle entries | 腳本 append | 每 cycle |

### Claude-Required（event-driven，僅以下情況才用 token）
- L3 strategic decisions（dead-loop、模型變更、大幅偏移）
- DNA calibration（新 decision kernels）
- LLM-required consistency test 3 個邊界場景（poker GTO、ATR sizing、multi-option EV）
- Organism collision analysis
- SOP 撰寫
- Outreach DM 起草
- 開發維護 Python 腳本
- 每週戰略複核

---

## 每日 Session 架構（從週六 10:00 AM 開始）

### Session 類型 × 3

#### Type A — 晨間快速確認（~10-15 min，~8-12K tokens）
冷啟動讀取順序（最小化，不讀 dna_core）：
1. `staging/session_state.md` (3.6K) — cycle 狀態、branch 佇列
2. `staging/last_output.md` (3.1K) — 上個 cycle 產出
3. `results/daily_log.md` 最後 20 行 — 最近 cycle 摘要

確認 3 件事：
- 交易 daemon 還在跑？clean streak 是否維持？
- 任何 human-gated blockers 已解除？（mainnet keys、DM 回覆）
- 有無 L3 event 觸發？

/clear after。

#### Type B — 實作 Session（~60-90 min，~80-150K tokens）
只讀與該 branch 相關的檔案。例如：
- DNA 工作：讀 `templates/dna_core.md` cold-start kernel 段落 + `memory/recursive_distillation.md` tail
- 開發工作：讀對應 Python 腳本
- Outreach：讀 `staging/outreach_week1_execution.md`

/clear after。

#### Type C — 週六全局戰略 Session（~90 min，~150-250K tokens）
Reset 後的第一個 session，做整週規劃：
1. 完整 cold-start（CLAUDE.md 協議）
2. L3 review + 週優先級排序
3. DNA audit（只讀 cold-start kernel，非全文）
4. Run consistency test 確認 clean
5. 設定本週 Claude 工作清單

---

## 每週 Token 預算分配（假設週一次 reset）

| 類別 | Sessions | Token 預算 | 說明 |
|------|---------|-----------|------|
| 週六戰略 Session | 1 | ~200K | L3 + DNA + 優先級規劃 |
| 晨間確認 × 6 | 6 | ~70K | 每次 12K |
| 實作 Session × 6-8 | 6-8 | ~600K | 每次 80-120K |
| 緊急 L3 event buffer | 1-2 | ~100K | 備用 |
| **週總計** | | **~970K** | 控制在限制內 |

> Autonomous 系統（daemon、交易、memory）：**0 token**

---

## /clear 頻率規則

- 每個 session type 結束後必 /clear
- 單次對話超過 90 分鐘必 /clear（context 積累影響品質）
- 規則：「如果無法用 2 句話摘要目前 context，就是 /clear 時機」

---

## 冷啟動最佳化

### 最小啟動（Type A，~3-5K tokens）
```
1. staging/session_state.md  →  當前狀態
2. staging/last_output.md    →  上次產出
3. daily_log.md tail (20行)  →  最近 cycle
```
跳過 dna_core.md，跳過 boot test，跳過 memory/insights.json 全文掃描。

### 標準啟動（Type B，~10-15K tokens）
```
+ templates/dna_core.md 的 Cold Start Prompt 段落（~1,540 tokens）
+ memory/recursive_distillation.md 最後 5 筆
```

### 完整啟動（Type C，~20-30K tokens，僅週六）
```
+ 完整 CLAUDE.md 協議（boot test run）
+ staging/ 所有檔案
+ memory/ 全讀
```

---

## 雲端部署計畫（不吃 token 的自動化）

### 立即可部署（已有腳本）

| 服務 | 腳本 | 部署方式 | 輸出 |
|------|------|---------|------|
| Trading daemon | `platform/recursive_daemon.py` | systemd service 或 Vercel cron | trading log, signals |
| Consistency runner | `consistency_test.py` | GitHub Actions daily cron | baseline.json, scorecard |
| Recursive engine tracker | `recursive_engine.py --status` | cron 每 30 min | cycle 狀態 |
| Dashboard state gen | `platform/generate_dashboard_state.py` | Vercel (已有 .vercel/) | JSON state |
| Discord notifier | webhook in `platform/server_config.json` | daemon callback | 每 cycle 通知 |

### Dashboard 監控指標（你直接看，不需要 Claude）
```
- Cycle number + clean streak
- Trading: regime, active signals, BTC price, P&L
- Branch status: 10 branches + L2 verdict
- Memory: insight count, last distillation timestamp
- Human-gated: mainnet API days remaining, pending DMs
- L3 events: last trigger timestamp
```

### Claude 定期確認協議（每日 1 次，<5K tokens）
只讀 `staging/session_state.md`，確認：
1. `consecutive_clean_cycles` 有沒有斷？
2. 交易 daemon PID 存活？
3. 有無新的 L3 event 或 human-gated 解除？
→ 沒問題就 /clear，不做額外讀取。

---

## Repo 重構計畫

### Phase 1 — 立即執行（高 token 節省效益）

**1. 清理 results/（11MB → ~2MB）**
```
mkdir results/archive/
mv results/cycle_001_290/ results/archive/   # 舊 cycle 資料歸檔
```
- 保留：最近 20 個 cycle 的 JSON + daily_log.md + paper_live_log.jsonl + trading_engine_log.jsonl（最後 1000 筆）
- 歸檔：collision JSON × 200+ 個、backtest 結果、舊 cycle 報告

**2. 刪除 temp files**
```
rm tmp_distill.py tmp_err.txt tmp_out.txt
rm "CUsersadminworkspacedigital-immortalityresultsdaemon_log.md"  # Windows artifact
```

**3. 歸檔舊 docs**
```
mkdir docs/archive/
mv docs/knowledge_product_{001..100}*.md docs/archive/
```
保留 docs/ 只有 SOP #101-117（active）+ 重要參考（turing_test_protocol、posting_queue）

### Phase 2 — DNA 分割（中期）

**4. 從 dna_core.md 提取 cold-start kernel**
- 新增 `templates/dna_boot.md`：只含 "Cold Start Prompt" 段落（~1,540 tokens）
- 修改 `CLAUDE.md` boot protocol：Type A/B 啟動讀 `dna_boot.md`，Type C 才讀完整 `dna_core.md`

**5. 新增 staging/quick_status.md（機器自動生成）**
格式：
```markdown
# Quick Status (auto-generated by daemon)
cycle: 302 | clean_streak: 56 | trading: LIVE tick=351
branches: [1.1:B] [2.2:DONE] [2.3:B] [3.1:B]
blocked: mainnet_keys(88d) | outreach_dms(5 pending)
l3_last: cycle_78 | next_check: cycle_305
```
- 用這個取代讀 session_state.md（<200 tokens vs 3,600 tokens）

### Phase 3 — Memory 分頁（當 insights.json > 150K 時）
- Archive entries < cycle 200 → `memory/insights_archive_v1.json`
- 保持 active `memory/insights.json` < 50K
- 修改 `memory_manager.py` 加入 pagination 邏輯

---

## 實作優先順序

1. **立即（週六前或週六 session 第一件事）**：
   - Phase 1 archive 清理（節省最多 token 讀取成本）
   - 建立 `staging/quick_status.md` 自動生成腳本
   - 把 daemon 設為系統服務（確保無 Claude 也繼續跑）

2. **週六 session**：
   - 提取 `templates/dna_boot.md`
   - 修改 CLAUDE.md 加入三層啟動協議
   - 設定 GitHub Actions cron for consistency test

3. **下週**：
   - Memory pagination（若 insights.json 接近 150K）
   - Vercel dashboard state deploy
   - docs/archive 歸檔

---

---

## 通訊介面 + 模型選擇建議

### Discord Plugin 的定位

Discord 很適合做**指揮層（Command Layer）**，不適合做**執行層（Execution Layer）**：

| 用途 | Discord | Claude Code CLI/Web |
|-----|---------|---------------------|
| 發指令 / 查狀態 | ✅ 最方便 | 可以但多餘 |
| 看 daemon 通知 | ✅ 推播即時 | ❌ 要主動查 |
| 寫/讀/修改程式 | ❌ 無 file system | ✅ 原生支援 |
| 長工作 session | ❌ 易斷線/限制多 | ✅ 最穩定 |
| 排程執行 | ❌ 無原生排程 | ✅ `/schedule` |

**建議架構**：
- Discord → 你的指揮介面（下達任務、確認狀態、接收告警）
- Claude Code web/CLI → 實際執行環境（Type A/B/C sessions 全在這裡跑）
- 兩者透過 Discord webhook 串起來：daemon 寫 → Discord 推播給你 → 你在 Discord 下指令 → Claude Code 執行

### 主 Session = 大腦架構（推薦保持）

你目前的模式是正確的。優化建議：

```
Main Session（大腦）
├── 只讀 index.md + quick_status.md（<1K tokens）
├── 評估優先級，拆解任務
├── dispatch → Subagent A（DNA 工作）
├── dispatch → Subagent B（開發工作）
└── dispatch → Subagent C（分析工作）
```

- Main session **永遠保持輕量**：不讀 dna_core.md 全文，不讀 daily_log.md 全文
- Subagent 讀需要讀的東西，完成後 main session 只讀摘要
- Main session 超過 60 min 就 /clear 重啟（context 積累會降低指揮品質）

### 模型選擇策略

| 工作類型 | 模型 | 理由 |
|---------|------|------|
| Type A 快速確認 | Sonnet | 讀狀態不需推理 |
| Type B 一般開發 | Sonnet | 足夠，省 token |
| Type B DNA 工作 | Sonnet + extended thinking | 需要深度推理但不需 Opus |
| Type C 週六戰略 | Sonnet + extended thinking | L3 決策需推理 |
| L3 緊急事件 | Opus（按需升級）| 僅限真正複雜的系統級決策 |
| 主 session 指揮 | Sonnet | 指揮層不需要最強模型 |

**原則：預設 Sonnet，你不用手動切換。**  
當任務真的需要 Opus（你會感覺 Sonnet 在繞圈子、給不出正確結論），自行在對話中要求，或我會主動告知需要升級。  
Extended thinking 比 Opus 更 token-efficient，大部分複雜推理用這個就夠。

---

## Scheduled Sessions（Claude Code 排程功能）

### 排程工具對應

| Session Type | 工具 | 觸發方式 | Token 成本 |
|-------------|------|---------|-----------|
| Type A 晨間確認 | `/schedule` | 每日固定時間（如 09:00） | ~8-12K |
| Type B 實作 | 手動啟動 | 有任務時 | ~80-150K |
| Type C 週六戰略 | `/schedule` | 週六 10:00（reset 後） | ~150-250K |
| Daemon 健康監控 | `/loop` | 主動工作期間每 30 min | ~1-2K |

### `/schedule` 設計（Type A — 每日自動確認）
```
/schedule 每日 09:00
  讀 index.md → 讀 staging/quick_status.md
  確認：daemon alive? clean_streak? human-gated 解除?
  若一切正常：Discord 通知 + /clear
  若異常：升級為 Type B session
```
- 排程 session 只消耗最小 token（index.md + quick_status.md = <1K tokens）
- 異常才升級，正常走完直接 stop

### `/schedule` 設計（Type C — 週六戰略）
```
/schedule 週六 10:05（reset 後 5 分鐘）
  完整 cold-start 協議（CLAUDE.md）
  讀 index.md → 確認 branch 優先級
  設定本週 Claude 工作清單
  更新 staging/quick_status.md 週目標欄位
```

### `SessionStart` Hook
在 `.claude/settings.json` 加入：
```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "cd /home/user/digital-immortality && python recursive_engine.py --status > staging/quick_status_raw.txt 2>&1"
      }]
    }]
  }
}
```
每次 session 啟動自動刷新 quick_status，Claude 不需要主動 run script。

### `/loop` 用途（主動工作期間）
```
/loop 30m
  python recursive_engine.py --status
  確認 daemon PID 存活
```
僅在做 Type B 長工作 session 時啟用，避免 daemon 在你工作時靜默死掉。

---

## index.md 設計（Repo 導覽索引）

### 用途
任何 session 第一件事讀 `index.md`（目標 <400 tokens），立刻知道：
- 整個 repo 在幹嘛
- 現在最重要的狀態在哪裡讀
- 依任務類型該讀哪些檔案

### 結構設計
```markdown
# Digital Immortality — Repo Index
version: 2.3.0 | 讀取成本: <400 tokens

## 當前狀態 → 讀這個
staging/quick_status.md   # <200 tokens，daemon 每 cycle 自動更新

## 任務導覽（依工作類型選讀）
| 任務類型 | 必讀檔案 | 跳過 |
|---------|---------|------|
| 快速確認 | quick_status.md | 所有其他 |
| DNA 工作 | dna_boot.md + memory/recursive_distillation.md(tail) | dna_core.md 全文 |
| 交易分析 | trading/paper_trader.py + results/paper_live_log.jsonl(tail) | trading_engine_log.jsonl |
| 開發維護 | 對應 .py 腳本 | docs/, results/ |
| 戰略 L3 | CLAUDE.md + staging/session_state.md + memory/ | results/ 全部 |
| Outreach | staging/outreach_week1_execution.md | 其他 staging |

## 目錄地圖（大小 / 用途）
templates/  508K  DNA + boot tests（dna_boot.md 是最小版）
memory/     180K  跨 session 持久記憶（insights.json + distillation）
staging/     44K  session 間 relay（每 cycle daemon 更新）
platform/   180K  daemon + Discord + dashboard 腳本
trading/    208K  paper trader + strategies（autonomous）
docs/       2.1M  117 SOPs（歸檔後只留 #101-117 在 active）
results/     2MB  最近 cycle 日誌（歸檔後）

## 永遠不需要 Claude 讀取的目錄
results/archive/    舊 cycle 歸檔
docs/archive/       SOP #1-100
__pycache__/        bytecode

## Human-Gated 待辦
- mainnet API keys（Jul 7 deadline）
- Outreach DMs × 5（staging/outreach_week1_execution.md）
- Samuel Turing Test invite
```

### 維護規則
- `index.md` 由 Claude 手動維護（結構變動時更新）
- `staging/quick_status.md` 由 daemon 自動更新（每 cycle）
- index.md 不記錄 cycle 數字或動態數據（那些在 quick_status.md）

---

## 驗證方式

- `du -sh results/` → 應 <3MB（原 11MB）
- Type A 排程 session：只讀 index.md + quick_status.md，<1K tokens
- 晨間 Type A 啟動：讀 3 個檔案，應 <3 min，<8K tokens
- Daemon 獨立存活測試：關掉 Claude，確認 `results/daily_log.md` 仍有新 cycle 寫入
- Dashboard 存取：不開 Claude 能看到所有關鍵指標
- Token check：用 `/cost` 或 session 估計，週總消耗 < 1M
- `/schedule` 驗證：確認 Type A session 每日自動執行 + Discord 通知到達

---

## 關鍵檔案路徑

| 檔案 | 用途 | 動作 |
|------|------|------|
| `index.md` | **新建**：repo 導覽索引，任何 session 第一讀 | Phase 1 新建 |
| `staging/quick_status.md` | **新建**：<200 token 當前狀態，daemon 自動更新 | Phase 2 新建 |
| `templates/dna_boot.md` | **新建**：cold-start kernel only (~1,540 tokens) | Phase 2 新建 |
| `.claude/settings.json` | **新建**：SessionStart hook | Phase 2 新建 |
| `CLAUDE.md` | 修改：加入三層啟動協議 + 讀 index.md | Phase 2 修改 |
| `templates/dna_core.md` | 完整 DNA，僅 Type C 讀 | 不動 |
| `platform/recursive_daemon.py` | 交易 daemon | 設為系統服務 |
| `memory/insights.json` | 122K，需分頁 | Phase 3 |
| `results/` | 11MB，需歸檔 | Phase 1 |

---

## EXACT COMMANDS TO EXECUTE ON SATURDAY

> Copy-paste these. Run in order. Each section = one step.

### STEP 0 — Backup (MUST do first)
```bash
cd /home/user/digital-immortality
git tag pre-optimization-backup
echo "Backup tag created: $(git rev-parse pre-optimization-backup)"
```

### STEP 1 — Phase 1: Archive results/
```bash
cd /home/user/digital-immortality
mkdir -p results/archive

# Find cycle dirs (cycle_001 through cycle_290 pattern) and archive them
# Keep only the last ~20 cycles
ls results/ | grep -E '^cycle_[0-9]+' | sort | head -n -20 | xargs -I{} mv results/{} results/archive/

# Archive collision JSONs (200+ files)
find results/ -maxdepth 1 -name "collision_*.json" | xargs -I{} mv {} results/archive/

# Archive backtest results
find results/ -maxdepth 1 -name "backtest_*.json" -o -name "backtest_*.csv" | xargs -I{} mv {} results/archive/

# Truncate large log files (keep last 1000 lines)
tail -n 1000 results/paper_live_log.jsonl > /tmp/paper_tail.jsonl && mv /tmp/paper_tail.jsonl results/paper_live_log.jsonl
tail -n 1000 results/trading_engine_log.jsonl > /tmp/trading_tail.jsonl && mv /tmp/trading_tail.jsonl results/trading_engine_log.jsonl

# Verify
du -sh results/
echo "Files remaining in results/ root: $(ls results/ | wc -l)"
```

### STEP 2 — Phase 1: Archive docs/
```bash
cd /home/user/digital-immortality
mkdir -p docs/archive

# Move knowledge_product SOP files 001-100 to archive
ls docs/ | grep -E 'knowledge_product_0[0-9]{2}' | xargs -I{} mv docs/{} docs/archive/
ls docs/ | grep -E 'knowledge_product_10[0-0]' | xargs -I{} mv docs/{} docs/archive/

# Verify
du -sh docs/
echo "Files in active docs/: $(ls docs/ | grep -v archive | wc -l)"
```

### STEP 3 — Phase 1: Delete temp files
```bash
cd /home/user/digital-immortality
rm -f tmp_distill.py tmp_err.txt tmp_out.txt
rm -f "CUsersadminworkspacedigital-immortalityresultsdaemon_log.md"
ls -la | grep tmp   # should show nothing
```

### STEP 4 — Phase 2: Create index.md
```bash
cat > /home/user/digital-immortality/index.md << 'EOF'
# Digital Immortality — Repo Index
version: 2.3.0 | read-cost: <400 tokens | updated: 2026-04-12

## Current State → Read This
staging/quick_status.md   # <200 tokens, daemon auto-updates every cycle

## Task Navigation (read only what you need)
| Task Type | Must Read | Skip |
|-----------|-----------|------|
| Quick confirm | quick_status.md | everything else |
| DNA work | templates/dna_boot.md + memory/recursive_distillation.md (tail 5) | dna_core.md full |
| Trading analysis | trading/paper_trader.py + results/paper_live_log.jsonl (tail) | trading_engine_log.jsonl |
| Dev/maintenance | the specific .py file | docs/, results/ |
| Strategic L3 | CLAUDE.md + staging/session_state.md + memory/ | results/ entirely |
| Outreach | staging/outreach_week1_execution.md | other staging files |

## Directory Map
templates/  ~130K  DNA + boot tests (dna_boot.md = minimal version)
memory/     ~180K  cross-session persistence (insights.json + distillation)
staging/     ~44K  inter-session relay (daemon updates each cycle)
platform/   ~180K  daemon + Discord + dashboard scripts
trading/    ~208K  paper trader + strategies (fully autonomous)
docs/        ~200K  active SOPs #101-117 + key references
results/     <3MB  recent cycle logs (archived)

## Never Read (Claude should never load these)
results/archive/    old cycles
docs/archive/       SOP #1-100
__pycache__/        bytecode

## Human-Gated Blockers
- mainnet API keys (Jul 7 deadline)
- Outreach DMs × 5 (see staging/outreach_week1_execution.md)
- Samuel Turing Test invite
EOF
echo "index.md created: $(wc -c < index.md) bytes"
```

### STEP 5 — Phase 2: Create staging/quick_status.md (initial placeholder)
```bash
cat > /home/user/digital-immortality/staging/quick_status.md << 'EOF'
# Quick Status (auto-generated by daemon — do not edit manually)
# Last updated: 2026-04-12 (Saturday — initial creation)

cycle: [run python recursive_engine.py --status to get current] | clean_streak: see session_state.md
trading: daemon status unknown — check platform/recursive_daemon.py
branches: see staging/session_state.md for full branch queue
blocked: mainnet_keys(~88d remaining) | outreach_dms(5 pending)
l3_last: see daily_log.md | next_check: cycle+3

## Note
Daemon will overwrite this file each cycle with live data.
Until daemon updates it, read staging/session_state.md for ground truth.
EOF
echo "quick_status.md created"
```

### STEP 6 — Phase 2: Extract dna_boot.md from dna_core.md
> Do this manually — find the "Cold Start Prompt" section in templates/dna_core.md and copy it to templates/dna_boot.md.
```
1. Read templates/dna_core.md — search for "Cold Start Prompt" section
2. Copy that section only into templates/dna_boot.md
3. Target size: ~1,500-2,000 tokens (~6-8KB)
4. Verify: wc -c templates/dna_boot.md  (should be < 10KB)
```

### STEP 7 — Phase 2: Create .claude/settings.json
```bash
mkdir -p /home/user/digital-immortality/.claude
cat > /home/user/digital-immortality/.claude/settings.json << 'EOF'
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "cd /home/user/digital-immortality && python recursive_engine.py --status > staging/quick_status_raw.txt 2>&1 && echo 'SessionStart hook: quick_status refreshed'"
      }]
    }]
  }
}
EOF
echo ".claude/settings.json created"
```

### STEP 8 — Phase 2: Update CLAUDE.md boot protocol
> Add this **before** the existing "## 1. Orient" section:

```markdown
## 0. Select Boot Tier (read this FIRST)

| Tier | When to use | Files to read |
|------|------------|---------------|
| **Type A** — Quick Confirm | Daily check-in, no active task | `index.md` → `staging/quick_status.md` → stop |
| **Type B** — Implementation | Specific branch/task to execute | `index.md` → `staging/quick_status.md` → task-specific files only |
| **Type C** — Full Strategic | Saturday reset / L3 event | Full protocol below (§1 Orient) |

**Default: Type A. Escalate only if quick_status shows an issue or you have an active task.**
```

### STEP 9 — Verification
```bash
cd /home/user/digital-immortality

echo "=== Size Check ==="
du -sh results/ docs/ memory/ staging/ templates/

echo "=== New Files ==="
ls -la index.md staging/quick_status.md templates/dna_boot.md .claude/settings.json 2>&1

echo "=== Git Status ==="
git status --short | head -20

echo "=== Backup Tag ==="
git tag | grep pre-optimization
```

### STEP 10 — Commit and Push
```bash
cd /home/user/digital-immortality
git add index.md staging/quick_status.md templates/dna_boot.md .claude/settings.json CLAUDE.md
git add -u  # stage all modifications (archived moves)
git commit -m "feat: token optimization phase 1+2 — archive cleanup, index.md, dna_boot, 3-tier boot

- Archive results/cycle_001-290 and collision JSONs (11MB → <3MB)
- Archive docs/knowledge_product_001-100 (2.1MB → ~200K)
- Create index.md: repo nav index <400 tokens
- Create staging/quick_status.md: live status <200 tokens
- Extract templates/dna_boot.md: cold-start kernel ~1.5K tokens
- Add .claude/settings.json: SessionStart hook for auto-refresh
- Update CLAUDE.md: 3-tier boot protocol (Type A/B/C)

Pre-change backup: git tag pre-optimization-backup"
git push -u origin claude/optimize-token-usage-AYEpF
```
