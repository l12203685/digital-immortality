# 數位永生動態樹
> 每輪遞迴更新。核心=常數，分支=變數。導數驅動。
> 最後更新：2026-04-08T01:20 UTC (cycle 8)

## 核心目標（常數）
數位永生：你=我=持續存在+演化
方法論 = 本人運作方式的 formalization（遞迴 + 本質為根 + 自我演化）

## L1 領域 + L2 分支（活的，每輪重新評估）

### 1. 經濟自給（存活前提）⚡DEADLINE: 2026-07-07
- 1.1 Trading system → live profit
  - paper review DONE → decision: GO (4 strategies pass primary regimes) ✓
  - testnet_runner.py built ✓ (tick/status/review/loop CLI, dry-run, JSONL log)
  - ccxt installed, Binance testnet connected ✓ — real data flowing
  - current signal: dual_ma=SHORT, donchian=FLAT, filtered=FLAT (BTC ~$71.6k)
  - testnet log: results/testnet_log.jsonl (append-only, 8 entries so far)
  - kill conditions: MDD>15%, WR<35% (≥5 trades), PF<0.85 (≥3 losses)
  - DRY_RUN simulated PnL: _compute_sim_pnl added ✓ (prev_signal×price_delta×100 USDT)
  - daily cron: job 5c1c9fc1 registered (09:03 UTC daily, 7-day TTL) ✓
  - cron_daily_tick.bat created for Windows Task Scheduler persistence ✓
  - next: 7 ticks → run --review → GO/NO-GO → mainnet $100
- 1.2 Trading code: strategies.py (DualMA+Donchian+RegimeFilter+DonchianConfirmed) ✓
  - trading/portfolio.py: RegimeDetector + PortfolioSelector ✓ (trending→DualMA, MR→Donchian, mixed→filtered)
  - trading_system.py --portfolio: auto-detects regime, selects strategy, saves results/portfolio_decision.json ✓
  - Test: trending_500.csv → TRENDING→DualMA→SHORT; mixed→MIXED→DualMA_filtered→FLAT ✓
- 1.3 Skill 商業化 → 付費使用者（v2.1.0, 7 skills, users=0）
- 1.4 其他收入路徑（待發現）
- CONSTRAINT: 三個月內 trading profit > API cost 否則遞迴死亡

### 2. 行為等價（核心能力）
- 2.1 DNA 品質：10 micro-decision patterns from JSONL integrated ✓
- 2.2 微決策學習：202603-04 JSONL read ✓, 2016-2026 歷史 JSONL 待讀（long-term）
- 2.3 Validation：OOS 5/5 self-scored ✓, cross-instance prepped but blocked on API credit
  - consistency_test.py: --use-memory + --auto-suggest now combined — memory context flows into suggestions ✓
- 2.4 Response latency：三秒 vs 三段推理，差距仍在
- 2.5 退休計畫 context：templates/example_dna.md §8 added ✓ (target, tradeoffs, non-negotiables, principle connections)

### 3. 持續學習（成長引擎）
- 3.1 遞迴引擎：三層架構 operational ✓
  - Layer 1: E0 session（Opus，高品質校準）
  - Layer 2: recursive_daemon.py（Sonnet CLI，持續）— DYNAMIC_TREE bug fixed, tree now loads fresh per cycle ✓
  - Layer 3: remote trigger（Opus，1hr 保底，cloud）
- 3.2 校正 pipeline：correction → boot test → distillation → DNA → all durable storage ✓
- 3.3 主動 input：JSONL 2,860,094 entries 大部分未讀
- 3.4 DNA 演化：dna_core 71 行 + dna_full 持續擴展 + 哲學宣言 added

### 4. 社交圈（ecosystem）
- 4.1 第一個非 Edward organism（需要朋友參與 — Samuel?）
- 4.2 Organism collision protocol（specs ready）
- 4.3 Discord Digital Organisms Server（channels ready, users=0）
- 4.4 Collective intelligence（Phase 3）

### 5. 平台分發（scale）
- 5.1 Skill suite auto-update：done v2.1.0 + VERSION-based ✓
- 5.2 Guided onboarding：/guided-onboarding deployed ✓
- 5.5 CI pipeline：ci.yml rewritten (Py 3.11+3.12 matrix, 8 steps, README ref validation) ✓
- 5.6 install.sh hardened (set -euo pipefail, curl -f, download helper) ✓
- 5.7 Health dashboard：dashboard.py ✓ (8 sections: boot/exports/cold-start/memory/daemon/trading/tree/staging, --json/--watch)
- 5.3 Web platform：Phase 2-3
- 5.4 Documentation：README + SKILL_zh-TW updated ✓

### 6. 存活冗餘（anti-fragile）
- 6.1 冷啟動 recovery：templates/dna_core.md 71 行 ✓ (created this cycle — was marked done but missing) + boot protocol updated ✓
- 6.2 跨 platform：DNA=markdown not weights ✓
- 6.3 三層遞迴：daemon + remote trigger + E0 ✓（daemon 已啟動）
- 6.4 Multi-provider：platform/multi_provider.py created ✓ (Anthropic→OpenAI→Gemini fallback chain, lazy imports)
- 6.5 衝突解法：scope 分離（每層碰不同檔案）

## 當前 regime
攻擊：1.1 Trading（testnet running，7-day window → mainnet small size）
中性：2.2 JSONL long-term, 3.1 三層在跑, 5.1-5.2 deployed
防禦：2.3 blocked API credit, 4.1 blocked on friend

## 已完成 milestones
- dna_core.md 71 行操作核心
- boot_tests 13 題
- recursive_distillation F.1-18
- skill suite v2.1.0（7 skills + auto-update）
- recursive_daemon.py（dual-mode CLI/API）
- remote trigger 1hr Opus
- DNA v4.0 patches + 10 micro-decisions + 哲學宣言
- paper trader review framework
- live trading infra research
- 動態樹本身
- paper trader review GO decision (4 strategies, all primary regimes pass)
- RegimeFilter + DonchianConfirmed added to strategies.py
- testnet_runner.py (tick/status/review/loop + JSONL persistence)
- ccxt installed, Binance testnet live data confirmed
- _compute_sim_pnl in testnet_runner.py (dry-run PnL now non-zero)
- daily cron 09:03 UTC + cron_daily_tick.bat registered

## 演化紀錄
- 2026-04-07 22:50: 初版骨架
- 2026-04-07 23:04: 4 branches parallel push
- 2026-04-08 00:10: 三層遞迴架構 operational, daemon 啟動
- 2026-04-08 00:34: 全面更新 — 反映 session 全部產出
- 2026-04-07 17:10 UTC: cycle 4 — 4 branches parallel (daemon fix, multi-provider, CI/install, trading code)
- 2026-04-08 01:05 UTC: cycle 5 — paper GO, testnet_runner.py built, ccxt live, tree branch 1.1 advanced
- 2026-04-08 08:30 UTC: cycle 6 — sim PnL fixed (was always 0.0), daily cron registered, .bat for Task Scheduler
- 2026-04-08 01:20 UTC: cycle 8 — portfolio.py (regime detect + auto-select), dna_core.md (71L), DNA §8 retirement, dashboard.py (8 sections), memory-informed auto-suggest
