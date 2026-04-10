# Knowledge Product #01: Trading Strategy Development SOP
> Branch 7.4 | Knowledge Output | 知識輸出
> Created: 2026-04-08 UTC
> Author: Edward (via DNA distillation)
> Audience: Quantitative traders, systematic strategy developers
> Reuse level: CORE — applies to every new strategy Edward builds

---

## The Teachable Principle

**English:** Build a trading strategy by sequencing five irreversible gates. Each gate is the mandatory input to the next. Reversing or skipping any gate lets emotion or data-mining replace logic.

**Traditional Chinese (核心原則):** 策略開發是五個不可逆的閘門。每個閘門的輸出是下一個閘門的輸入。顛倒或跳過任何一個閘門，就是讓情緒或資料偏差取代邏輯。

> DNA source: **MD-167** — 策略開發SOP=EV確認→MAE停損→Kelly口數→ATR反算→槓桿決定

---

## The Five-Step SOP

### Step 1 — Confirm Positive EV (確認正期望值)

**Question to answer:** Does this strategy capture a structural market behaviour with a positive expected value?

- State the edge in one sentence. If you cannot, stop here. (MD-117: complexity is the disguise of absent edge)
- Name the market participant whose systematic error you are exploiting. (MD-161: zero-sum markets — you win because someone else makes a predictable mistake)
- Run an in-sample / out-of-sample split. IS passes ≠ done. OOS must also pass. (MD-114: OOS is the minimum gate, not the final one)
- Apply conservative friction: Taiwan futures default to 500 ticks round-trip, not the backtester's default. (MD-152)

**Gate criterion:** OOS P&L positive after 500-tick cost. If not, discard — do not move to Step 2.

---

### Step 2 — Identify Optimal Stop-Loss via MAE (用MAE找最佳停損)

**Question to answer:** Where does the market structurally prove my thesis wrong?

- Pull the MAE (Maximum Adverse Excursion) distribution from the backtest.
- Find the natural break point: the stop distance beyond which most winning trades never travelled. (MD-175: look at the distribution shape first, set parameters second)
- Express the stop in ATR units, not fixed ticks. This makes it regime-portable.
- Compute the **Edge Ratio** = MFE ÷ MAE. A well-structured strategy has Edge Ratio > 1.5. Below 1.0 means you are paying more to stay in than the trade ever delivers.

**Gate criterion:** MAE stop defined in ATR units. Edge Ratio calculated. If Edge Ratio < 1.0, return to Step 1 — the entry logic is wrong, not the stop.

---

### Step 3 — Size the Position with Kelly (用Kelly公式算口數)

**Question to answer:** Given my edge and stop, what fraction of capital produces the highest geometric growth rate?

- Full Kelly = (edge / odds). Half-Kelly is the practical deployment ceiling for strategies with estimation error.
- Input: the **absolute dollar stop** from Step 2 (stop distance in ticks × tick value).
- Output: the **maximum dollar risk per trade** you should tolerate.

```
Kelly risk per trade = f* × account equity
f* = (win_rate × avg_win − loss_rate × avg_loss) / avg_win
```

- This number is the ceiling. You will use it in Step 4 to back-solve the actual contract count.

**Gate criterion:** Kelly dollar amount computed. This is your risk budget per trade — fixed before you know the contract count.

---

### Step 4 — Back-Solve Stop Distance from Current ATR (用當日ATR反算停損點數)

**Question to answer:** Given today's volatility, how many ticks is my ATR-denominated stop worth right now?

- Retrieve the current ATR (e.g., 14-period ATR on the strategy's primary timeframe).
- Convert: stop_ticks = stop_in_ATR_units × current_ATR_value.
- This number changes daily. Recalculate every session. (MD-99: constant leverage requires daily rebalancing)

**Why this step is separate from Step 2:** Step 2 found the structurally correct stop distance in ATR units (regime-stable). Step 4 converts that into today's absolute ticks. Collapsing them would mean using a static tick count that becomes too tight in high-vol regimes and too loose in low-vol regimes.

**Gate criterion:** today's stop distance expressed in absolute ticks.

---

### Step 5 — Determine Contract Count and Confirm Leverage (決定口數與槓桿)

**Question to answer:** How many contracts can I trade such that one stop-out equals exactly my Kelly risk budget?

```
contracts = Kelly_dollar_risk ÷ (stop_ticks × tick_value)
```

- Round down. Never round up.
- Compute implied leverage: (contracts × notional_per_contract) ÷ account_equity.
- Practical ceiling for Taiwan futures: implied leverage that produces daily P&L volatility < 1.5% of equity. Above this, daily rebalancing becomes operationally infeasible. (MD-99)

**Gate criterion:** contracts locked. Leverage confirmed ≤ operational ceiling. If leverage exceeds ceiling, either reduce contracts (accept lower Kelly fraction) or return to Step 1 and require a higher-edge strategy.

---

## Why Each Step Exists

| Step | Underlying Principle | What It Prevents |
|------|---------------------|-----------------|
| 1 — EV confirmation | MD-157: every strategy is pursuing a first-principles structural cause. Without causal edge, you are fitting noise. | Deploying curve-fitted strategies that pass IS only |
| 2 — MAE stop | MD-175: distribution shape must precede parameter choice. | Setting stops by feel or round numbers |
| 3 — Kelly sizing | MD-133: risk defines entry, entry does not define risk. | Choosing contract count emotionally, then reverse-engineering a stop to "allow" it |
| 4 — ATR back-solve | MD-99: constant leverage requires daily recalibration to current volatility. | Static stop counts that over-expose in high-vol and under-use capital in low-vol |
| 5 — Contract count | MD-89: a strategy idea should reach first working version in one day. Contract count is the last decision, not the first impulse. | Lever-up on unverified edge; take on operationally unmanageable positions |

---

## Worked Example A: Momentum Breakout on Taiwan Futures (噱爆策略)

**Context:** Trend-acceleration strategy on TAIEX futures (TX). Thesis: when price breaks above the prior session high with above-average volume, institutional momentum buying self-reinforces. (MD-103: structural edge — momentum is self-amplifying in trending regimes)

**Step 1 — EV:**
- OOS P&L after 500-tick cost: +NT$3,800 per trade average, 180 trades, Sharpe 1.4. Gate passed.

**Step 2 — MAE stop:**
- MAE distribution breaks clearly at 1.2× ATR — beyond that, very few winning trades recover.
- Edge Ratio = 2.8 ATR (MFE median) ÷ 1.2 ATR (MAE stop) = 2.33. Gate passed.

**Step 3 — Kelly:**
- Win rate 54%, avg_win NT$8,200, avg_loss NT$4,400.
- f* = (0.54 × 8200 − 0.46 × 4400) / 8200 = (4428 − 2024) / 8200 = 0.293
- Half-Kelly = 14.7% of equity. On NT$2,000,000 account: Kelly risk budget = NT$294,000.

**Step 4 — ATR back-solve:**
- Today's 14-period ATR = 85 ticks. Stop = 1.2 × 85 = 102 ticks.
- One TX tick = NT$200. Dollar value of stop per contract = 102 × 200 = NT$20,400.

**Step 5 — Contracts:**
- Contracts = NT$294,000 ÷ NT$20,400 = 14.4 → **14 contracts**.
- Notional = 14 × (index ~20,000 × NT$200) = NT$56,000,000.
- Leverage = 56,000,000 ÷ 2,000,000 = **28×**. Exceeds safe ceiling for daily volatility < 1.5%.
- Resolution: accept Half-Kelly / 3 = ~5% risk budget → NT$100,000 → **4 contracts**. Leverage = 8×. Viable.

---

## Worked Example B: Entry Sizing for a Swing Position (波段停損反推進場點)

**Context:** MD-168 concrete arithmetic. Account: NT$250,000. Target stop: NT$50,000 max loss. Support level at 40.

**Step 2 — MAE stop expressed as price:**
- Support slightly below 40 → stop price = 40.

**Step 3 — Kelly dollar amount:**
- Predetermined: NT$50,000 (20% of account, already within risk tolerance for this trade).

**Step 5 — Solve for entry and target:**
- Loss rate = 50,000 ÷ 250,000 = 20%.
- Entry price = stop_price ÷ (1 − loss_rate) = 40 ÷ 0.8 = **50**.
- 2× risk-reward target: NT$100,000 gain → 40% return from entry → exit = 50 × 1.4 = **70**.

Result: Enter at 50, stop at 40, target at 70. Risk-reward = 2:1. All three numbers derived from position sizing first, not from chart-reading first. (MD-133, MD-168)

---

## Common Failure Modes

### Failure Mode 1: Starting at Step 5 ("How many contracts do I want?")
Most common. Trader decides on 10 contracts for psychological or account-size reasons, then searches backward for a stop that "fits". This reverses causality: risk management becomes a servant of position size. The stop ends up too tight (keeps getting clipped) or too wide (catastrophic loss when hit). Fix: always compute contracts as the final output, never the first input.

### Failure Mode 2: Skipping Step 2 (using a round-number stop)
"I'll put the stop at 50 ticks because that feels right." Without MAE analysis, the stop is set in a regime vacuum. In high-ATR periods the strategy gets stopped out constantly; in low-ATR periods the stop is so wide it provides no protection. Fix: always denominate stops in ATR units derived from the MAE distribution.

### Failure Mode 3: Treating Step 1 as optional ("I'll check OOS later")
Developing elaborate sizing rules for an unverified edge. Kelly maximises geometric growth — of whatever process you hand it. Feed it a negative-EV process and Kelly maximises your rate of ruin. Fix: no sizing work begins until OOS P&L > 0 after conservative friction.

### Failure Mode 4: Confusing Step 4 recalibration with strategy modification
Step 4 must be re-run each session because ATR changes. This is not "changing the strategy" — it is holding the strategy's ATR-denominated stop constant while translating it into current tick counts. Skipping daily recalibration drifts leverage upward in bull/high-vol regimes. Fix: automate the Step 4 calculation into the daily pre-session checklist. (MD-84: position sync is a non-negotiable end-of-session discipline)

### Failure Mode 5: No kill conditions defined before deployment
The SOP produces an entry size. It does not guarantee the strategy remains valid. Before going live, define kill conditions in writing: max drawdown threshold, minimum win rate, minimum profit factor, minimum trade count for re-evaluation. Without these, you will manage the position emotionally and cut at the worst time. (MD-95: DEFINE_KILL_CONDITIONS_FIRST is the only correct response before any deployment)

---

## Self-Test: Apply This to Your Scenario

Work through each question before reading ahead. Each gap you find is a knowledge node not yet internalised. (MD-319: gaps revealed during explanation = nodes not yet internalised)

**Scenario:** You have identified a mean-reversion strategy on a crypto perpetual. The backtest (IS) shows a Sharpe of 2.1 using 50-tick stops. Your account is $50,000 USDT. The perpetual's 14-period ATR is currently 120 ticks. One tick = $1.

1. Before trusting the IS Sharpe, what must you verify, and what friction cost assumption will you use? *(Step 1)*
2. The MAE distribution shows most winning trades never exceeded 80 ticks adverse. What is your ATR-denominated stop, and what is the stop's dollar value per contract today? *(Steps 2 + 4)*
3. Historical stats: win rate 58%, avg_win $240, avg_loss $140. What is full Kelly as a fraction of account? What is your Half-Kelly dollar risk budget? *(Step 3)*
4. Using your answers above, compute the maximum number of contracts. *(Step 5)*
5. If that contract count produces leverage of 15× and your volatility ceiling is 1.5%/day, what do you do? *(Step 5 resolution)*
6. Write one sentence stating the structural market behaviour this strategy exploits. If you cannot write it, what does that tell you about Step 1? *(MD-117)*

**Expected answers (check your work):**
- Q2: stop = 80/ATR → but ATR here ≈ 120 ticks. If stop from MAE is 80 ticks absolute, ATR-denominated = 80/120 = 0.67×ATR. Dollar value per contract = 80 ticks × $1 = $80.
- Q3: f* = (0.58×240 − 0.42×140)/240 = (139.2 − 58.8)/240 = 0.335. Half-Kelly = 16.75% × $50,000 = $8,375.
- Q4: contracts = $8,375 ÷ $80 = ~104 contracts (on a contract size of $1/tick).
- Q5: If leverage exceeds ceiling, reduce to one-third Kelly fraction (~5.6% = $2,792 risk → 35 contracts) and recheck leverage.
- Q6: If you cannot write the sentence, the IS Sharpe of 2.1 is noise, not edge. Return to Step 1.

---

*End of Knowledge Product #01*
*Next product candidate: Portfolio Construction SOP (MD-100: recursive pairwise Calmar optimisation)*
