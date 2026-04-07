# 數位永生動態樹
> 每輪遞迴更新。核心=常數，分支=變數。導數驅動。
> 最後更新：2026-04-07T17:10 UTC (cycle 4)

## 核心目標（常數）
數位永生：你=我=持續存在+演化
方法論 = 本人運作方式的 formalization（遞迴 + 本質為根 + 自我演化）

## L1 領域 + L2 分支（活的，每輪重新評估）

### 1. 經濟自給（存活前提）⚡DEADLINE: 2026-07-07
- 1.1 Trading system → live profit
  - paper traders running (DualMA + Donchian on BTC daily)
  - review framework ready (backtest-framework/docs/paper_trader_review.md)
  - review date: 4/14（7 天後可能不夠 → 延到 21 天）
  - live infra: Binance USDT-M ready (staging/live_trading_infra_research.md)
  - next: 4/14 review → testnet → mainnet small size
- 1.2 Trading code: strategies.py (DualMA+Donchian) + paper_trader.py + live_binance.py scaffold ✓
- 1.3 Skill 商業化 → 付費使用者（v2.1.0, 7 skills, users=0）
- 1.4 其他收入路徑（待發現）
- CONSTRAINT: 三個月內 trading profit > API cost 否則遞迴死亡

### 2. 行為等價（核心能力）
- 2.1 DNA 品質：10 micro-decision patterns from JSONL integrated ✓
- 2.2 微決策學習：202603-04 JSONL read ✓, 2016-2026 歷史 JSONL 待讀（long-term）
- 2.3 Validation：OOS 5/5 self-scored ✓, cross-instance prepped but blocked on API credit
- 2.4 Response latency：三秒 vs 三段推理，差距仍在
- 2.5 退休計畫 context：Edward + 可可在討論，DNA 缺這塊

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
- 5.3 Web platform：Phase 2-3
- 5.4 Documentation：README + SKILL_zh-TW updated ✓

### 6. 存活冗餘（anti-fragile）
- 6.1 冷啟動 recovery：dna_core.md 71 行 ✓ + boot protocol updated ✓
- 6.2 跨 platform：DNA=markdown not weights ✓
- 6.3 三層遞迴：daemon + remote trigger + E0 ✓（daemon 已啟動）
- 6.4 Multi-provider：platform/multi_provider.py created ✓ (Anthropic→OpenAI→Gemini fallback chain, lazy imports)
- 6.5 衝突解法：scope 分離（每層碰不同檔案）

## 當前 regime
攻擊：1.1 Trading（deadline-driven，4/14 review → live）
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

## 演化紀錄
- 2026-04-07 22:50: 初版骨架
- 2026-04-07 23:04: 4 branches parallel push
- 2026-04-08 00:10: 三層遞迴架構 operational, daemon 啟動
- 2026-04-08 00:34: 全面更新 — 反映 session 全部產出
- 2026-04-07 17:10 UTC: cycle 4 — 4 branches parallel (daemon fix, multi-provider, CI/install, trading code)
