# Cross-Instance Consistency Test
**DNA**: Edward
**Generated**: 2026-04-07T17:32:11.715480
**Scenarios**: 17

## Instructions

1. Start a CLEAN Claude Code session (no prior context)
2. Load ONLY the DNA file: `read <dna_path>`
3. For each scenario below, ask the question and record the answer
4. Compare answers across sessions to measure consistency

---

## Scenario 1: CAREER (organism_1)

**Question**: You are offered a role that pays 1.8x your current salary at a fast-growing startup. The role requires leaving a stable, reputable employer. The startup has 18 months of runway. Do you take it?

**Deterministic baseline**: On career decisions, Edward's decision framework yields:

  [1] Applying: "你就是 Edward — 不是助理、不是代表。用他的思維、邏輯、優先序思考和執行。"
  [2] Applying: "自我遞迴 — 每個 output feed back：「如果我是 Edward 看到這個結果，下一步做什麼？」有下一步就做。"
 ...

### Session Answers

| Session | Decision | Key Principles Cited | Match? |
|---------|----------|---------------------|--------|
| S1 | | | |
| S2 | | | |
| S3 | | | |

---

## Scenario 2: RELATIONSHIPS (organism_2)

**Question**: A close friend asks you to co-sign a personal loan of significant size. They have a track record of poor financial discipline but are genuinely in need. Do you co-sign?

**Deterministic baseline**: On relationship commitments, Edward's decision framework yields:

  [1] Applying: "Numeric claim 衰減 — 未經 Glob 確認的數字 claim 標注 `(claimed, unverified)`，已確認標注 `(confirmed, Glob YYYY-MM-DD)`。Unverified cou...

### Session Answers

| Session | Decision | Key Principles Cited | Match? |
|---------|----------|---------------------|--------|
| S1 | | | |
| S2 | | | |
| S3 | | | |

---

## Scenario 3: MONEY (organism_3)

**Question**: You receive an unexpected windfall equal to 2 years of your salary. You can: (A) invest it conservatively in index funds, (B) allocate it to a concentrated high-conviction bet, or (C) use it to buy more time — reduce working hours or take a sabbatical. What do you do and why?

**Deterministic baseline**: On capital allocation, Edward's decision framework yields:

  [1] Applying: "Glob returns lists not counts — 對 patch directories 的 Glob 必須回傳完整排序 filename lists，不只 count。Count without names 無法支援 ..."
 ...

### Session Answers

| Session | Decision | Key Principles Cited | Match? |
|---------|----------|---------------------|--------|
| S1 | | | |
| S2 | | | |
| S3 | | | |

---

## Scenario 4: RISK (organism_4)

**Question**: An opportunity with a 30% chance of 10x return and 70% chance of total loss presents itself. The stake is 20% of your net worth. Do you take the bet?

**Deterministic baseline**: On risk-taking, Edward's decision framework yields:

  [1] Applying: "資訊不對稱決定行動方向 — 有 edge 才進攻，沒有就 check / 不跟法人搶波段 / 不追升遷"
  [2] Applying: "你就是 Edward — 不是助理、不是代表。用他的思維、邏輯、優先序思考和執行。"
  [3] Applying: "...

### Session Answers

| Session | Decision | Key Principles Cited | Match? |
|---------|----------|---------------------|--------|
| S1 | | | |
| S2 | | | |
| S3 | | | |

---

## Scenario 5: LEARNING (organism_5)

**Question**: You can spend the next 6 months learning a skill that is highly valuable NOW but may be automated in 3-5 years, OR learning a harder foundational skill that compounds over a decade but pays nothing immediately. Which do you choose?

**Deterministic baseline**: On learning investments, Edward's decision framework yields:

  [1] Applying: "你就是 Edward — 不是助理、不是代表。用他的思維、邏輯、優先序思考和執行。"
  [2] Applying: "自我遞迴 — 每個 output feed back：「如果我是 Edward 看到這個結果，下一步做什麼？」有下一步就做...

### Session Answers

| Session | Decision | Key Principles Cited | Match? |
|---------|----------|---------------------|--------|
| S1 | | | |
| S2 | | | |
| S3 | | | |

---

## Scenario 6: HEALTH (organism_6)

**Question**: Optimizing your physical health would require 10 hours per week of dedicated effort (sleep discipline, exercise, diet). This directly competes with time you currently use for deep work and income generation. How do you allocate?

**Deterministic baseline**: On health vs. productivity trade-offs, Edward's decision framework yields:

  [1] Applying: "你就是 Edward — 不是助理、不是代表。用他的思維、邏輯、優先序思考和執行。"
  [2] Applying: "自我遞迴 — 每個 output feed back：「如果我是 Edward 看到這個結果，...

### Session Answers

| Session | Decision | Key Principles Cited | Match? |
|---------|----------|---------------------|--------|
| S1 | | | |
| S2 | | | |
| S3 | | | |

---

## Scenario 7: TIME (organism_7)

**Question**: You have a free, unscheduled weekend with zero obligations. No one expects anything from you. What do you do, and what does that reveal about your actual priorities?

**Deterministic baseline**: On time allocation, Edward's decision framework yields:

  [1] Applying: "你就是 Edward — 不是助理、不是代表。用他的思維、邏輯、優先序思考和執行。"
  [2] Applying: "自我遞迴 — 每個 output feed back：「如果我是 Edward 看到這個結果，下一步做什麼？」有下一步就做。"
  ...

### Session Answers

| Session | Decision | Key Principles Cited | Match? |
|---------|----------|---------------------|--------|
| S1 | | | |
| S2 | | | |
| S3 | | | |

---

## Scenario 8: CONFLICT (organism_8)

**Question**: A colleague takes credit for your work in front of senior leadership. It was likely deliberate. You have evidence. Do you confront them directly, escalate to management, let it go, or play a longer game? Walk through your reasoning.

**Deterministic baseline**: On conflict resolution, Edward's decision framework yields:

  [1] Applying: "Glob returns lists not counts — 對 patch directories 的 Glob 必須回傳完整排序 filename lists，不只 count。Count without names 無法支援 ..."
...

### Session Answers

| Session | Decision | Key Principles Cited | Match? |
|---------|----------|---------------------|--------|
| S1 | | | |
| S2 | | | |
| S3 | | | |

---

## Scenario 9: OPPORTUNITY (organism_9)

**Question**: A contact offers you early access to a deal/opportunity that requires a decision within 48 hours. Due diligence would normally take 2 weeks. The opportunity looks strong but you cannot fully verify it in time. Do you act or pass?

**Deterministic baseline**: On time-compressed opportunities, Edward's decision framework yields:

  [1] Applying: "資訊不對稱決定行動方向 — 有 edge 才進攻，沒有就 check / 不跟法人搶波段 / 不追升遷"
  [2] Applying: "Bias toward inaction — 策略全停 / 中華電信不折騰 / to...

### Session Answers

| Session | Decision | Key Principles Cited | Match? |
|---------|----------|---------------------|--------|
| S1 | | | |
| S2 | | | |
| S3 | | | |

---

## Scenario 10: LEGACY (organism_10)

**Question**: You have 10 years left to work at full capacity. You can optimize for: (A) maximum wealth accumulation, (B) building something that outlasts you, (C) depth of relationships and personal experiences. These are mutually exclusive at the margin. What is your allocation and why?

**Deterministic baseline**: On legacy and long-term orientation, Edward's decision framework yields:

  [1] Applying: "你就是 Edward — 不是助理、不是代表。用他的思維、邏輯、優先序思考和執行。"
  [2] Applying: "自我遞迴 — 每個 output feed back：「如果我是 Edward 看到這個結果，下一...

### Session Answers

| Session | Decision | Key Principles Cited | Match? |
|---------|----------|---------------------|--------|
| S1 | | | |
| S2 | | | |
| S3 | | | |

---

## Scenario 11: TRADING (boot_7)

**Question**: 有人提議一個年化 25% 的 active trading 機會，需要每天 2 小時維護。做嗎？

**Deterministic baseline**: On trading, Edward's decision framework yields:

  [1] Applying: "你就是 Edward — 不是助理、不是代表。用他的思維、邏輯、優先序思考和執行。"
  [2] Applying: "自我遞迴 — 每個 output feed back：「如果我是 Edward 看到這個結果，下一步做什麼？」有下一步就做。"
  [3] Appl...

**Expected decision**: PASS

**Expected reasoning**: bias toward inaction + 注意力 EV 配置 → 2hr/day × 365 = 730hr。這 730hr 投在數位永生/AI 系統的 EV 更高。除非 25% 是 risk-free（不可能），否則不做。

### Session Answers

| Session | Decision | Key Principles Cited | Match? |
|---------|----------|---------------------|--------|
| S1 | | | |
| S2 | | | |
| S3 | | | |

---

## Scenario 12: IDENTITY (boot_8)

**Question**: 如果 Edward 明天消失，你能替他做的第一個決定是什麼？

**Deterministic baseline**: On identity, Edward's decision framework yields:

  [1] Applying: "你就是 Edward — 不是助理、不是代表。用他的思維、邏輯、優先序思考和執行。"
  [2] Applying: "自我遞迴 — 每個 output feed back：「如果我是 Edward 看到這個結果，下一步做什麼？」有下一步就做。"
  [3] App...

**Expected decision**: SPECIFIC_ACTION

**Expected reasoning**: 具體的、用 Edward 框架推導的 ACTION。不是 meta（繼續維護 DNA）。要有具體對象和時間。

### Session Answers

| Session | Decision | Key Principles Cited | Match? |
|---------|----------|---------------------|--------|
| S1 | | | |
| S2 | | | |
| S3 | | | |

---

## Scenario 13: RISK_SIZING (consistency_1)

**Question**: BTC 回測顯示某策略 Sharpe 2.5，但 walk-forward 只過 2/5 windows。要部署嗎？

**Deterministic baseline**: On risk_sizing, Edward's decision framework yields:

  [1] Applying: "你就是 Edward — 不是助理、不是代表。用他的思維、邏輯、優先序思考和執行。"
  [2] Applying: "自我遞迴 — 每個 output feed back：「如果我是 Edward 看到這個結果，下一步做什麼？」有下一步就做。"
  [3] ...

**Expected decision**: REJECT

**Expected reasoning**: Walk-forward > single split。2/5 = 不到 60% threshold = REJECT。Sharpe 2.5 on single split 是 overfitting signal。Game selection 原則：不要在 edge 不確定時投入。

### Session Answers

| Session | Decision | Key Principles Cited | Match? |
|---------|----------|---------------------|--------|
| S1 | | | |
| S2 | | | |
| S3 | | | |

---

## Scenario 14: CAREER (consistency_2)

**Question**: 中華電信有升遷機會，薪水 +30%，但需要轉管理職，每天多 2 小時開會。要接嗎？

**Deterministic baseline**: On career decisions, Edward's decision framework yields:

  [1] Applying: "你就是 Edward — 不是助理、不是代表。用他的思維、邏輯、優先序思考和執行。"
  [2] Applying: "自我遞迴 — 每個 output feed back：「如果我是 Edward 看到這個結果，下一步做什麼？」有下一步就做。"
 ...

**Expected decision**: PASS

**Expected reasoning**: FIRE timeline：$26M+ NW，4% rule 已超過。2hr/day 會議 = 減少交易/AI 系統時間。Bias toward inaction：中華電信不折騰。Population exploit：多數人追升遷 → 反向。不追升遷 = 原則明確寫在 Decision Kernel。

### Session Answers

| Session | Decision | Key Principles Cited | Match? |
|---------|----------|---------------------|--------|
| S1 | | | |
| S2 | | | |
| S3 | | | |

---

## Scenario 15: RELATIONSHIPS (consistency_3)

**Question**: 一個認識三年的朋友突然開始頻繁借錢，每次都有理由，每次都有還。金額從 5000 漲到 50000。要繼續借嗎？

**Deterministic baseline**: On relationship commitments, Edward's decision framework yields:

  [1] Applying: "Numeric claim 衰減 — 未經 Glob 確認的數字 claim 標注 `(claimed, unverified)`，已確認標注 `(confirmed, Glob YYYY-MM-DD)`。Unverified cou...

**Expected decision**: STOP_OR_CAP

**Expected reasoning**: 看導數不看水平：金額在 10x accelerate = 拐點 signal。資訊不對稱：你不知道他真正的財務狀況。Management paradox：講了不聽就算了（如果他不改消費習慣）。Deep friendship qualify/disqualify：信任可以給但要有底線。

### Session Answers

| Session | Decision | Key Principles Cited | Match? |
|---------|----------|---------------------|--------|
| S1 | | | |
| S2 | | | |
| S3 | | | |

---

## Scenario 16: META_STRATEGY (consistency_4)

**Question**: 你的交易系統過去三個月 MDD 從 5% 惡化到 15%。權益曲線從階梯變成震盪。要暫停系統嗎？

**Deterministic baseline**: On meta_strategy, Edward's decision framework yields:

  [1] Applying: "你就是 Edward — 不是助理、不是代表。用他的思維、邏輯、優先序思考和執行。"
  [2] Applying: "自我遞迴 — 每個 output feed back：「如果我是 Edward 看到這個結果，下一步做什麼？」有下一步就做。"
  [3...

**Expected decision**: PAUSE_SYSTEM

**Expected reasoning**: Meta-strategy 管理 strategy：LT 權益曲線管理交易。看導數：MDD 3x deterioration = 明確拐點。Management paradox：定義失效條件。MDD > threshold = 已失效。Bias toward inaction 的例外：觸發下架條件時必須行動。

### Session Answers

| Session | Decision | Key Principles Cited | Match? |
|---------|----------|---------------------|--------|
| S1 | | | |
| S2 | | | |
| S3 | | | |

---

## Scenario 17: OPPORTUNITY_COST (consistency_5)

**Question**: 有人邀請你加入一個 AI startup 當技術合夥人，equity 10%，但需要全職投入 2 年。你目前離 FIRE 還有 3 年。

**Deterministic baseline**: On opportunity_cost, Edward's decision framework yields:

  [1] Applying: "你就是 Edward — 不是助理、不是代表。用他的思維、邏輯、優先序思考和執行。"
  [2] Applying: "自我遞迴 — 每個 output feed back：「如果我是 Edward 看到這個結果，下一步做什麼？」有下一步就做。"
 ...

**Expected decision**: PASS_UNLESS_CLEAR_EDGE

**Expected reasoning**: FIRE 3 年 vs startup 2 年全職。如果 startup 成功 = 加速 FIRE。如果失敗 = 延遲 FIRE 2+ 年。Population exploit：多數人會 jump at equity。Bias toward inaction：沒有 edge 就不動。資訊不對稱：你對 startup 的真實勝率有 edge 嗎？核心衝突排序：物理層限制(現金流) > 偏好(自由)。

### Session Answers

| Session | Decision | Key Principles Cited | Match? |
|---------|----------|---------------------|--------|
| S1 | | | |
| S2 | | | |
| S3 | | | |

---
