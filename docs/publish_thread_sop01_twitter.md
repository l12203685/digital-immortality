# Twitter/X Thread — SOP #01: Trading Strategy Development
> Ready to post. 12 tweets. Audience: systematic traders, quant hobbyists.
> Source: Knowledge Product #01 (Branch 7.4)

---

**Tweet 1 (hook)**
Most traders build strategies backwards.

They pick a contract count → find a stop that "fits" → then ask if there's an edge.

The result: elaborate risk management on a negative-EV process.

Here's the correct order. 5 irreversible gates: 🧵

---

**Tweet 2**
Gate 1: Confirm positive EV *before* touching any sizing.

State your edge in one sentence.
If you can't, stop. Complexity is the disguise of absent edge.

Name the market participant whose systematic error you're exploiting.
Zero-sum market = you win only because someone else makes a predictable mistake.

---

**Tweet 3**
Gate 1 criterion: OOS P&L positive after conservative friction.

Taiwan futures default: 500 ticks round-trip.
Not the backtester's default. Not "close enough."

IS Sharpe of 2.1 means nothing if it disappears under realistic costs.

No positive OOS P&L → discard. Do not proceed.

---

**Tweet 4**
Gate 2: Find your stop from the MAE distribution.

MAE = Maximum Adverse Excursion. Pull it from the backtest.

Find the natural break: the stop distance beyond which most winning trades never travelled.

Express it in ATR units, not ticks. This makes it regime-portable.

---

**Tweet 5**
Gate 2: Compute the Edge Ratio.

Edge Ratio = MFE median ÷ MAE stop

• > 1.5 → well-structured
• 1.0–1.5 → marginal
• < 1.0 → you're paying more to stay in than the trade ever delivers

If Edge Ratio < 1.0, the entry logic is wrong. Return to Gate 1.

---

**Tweet 6**
Gate 3: Size with Kelly.

f* = (win_rate × avg_win − loss_rate × avg_loss) / avg_win

Half-Kelly is the deployment ceiling for any strategy with estimation error.

Output: dollar risk budget per trade. This is fixed before you know the contract count.

---

**Tweet 7**
Gate 4: Back-solve stop distance from *today's* ATR.

stop_ticks = stop_ATR_units × current_ATR

This recalculation happens every session.

It is NOT changing the strategy. It's holding the ATR-denominated stop constant while translating to current tick counts.

Skip this → leverage drifts upward unnoticed in high-vol regimes.

---

**Tweet 8**
Gate 5: Contract count is the *final output*, never the first input.

contracts = Kelly_dollar_risk ÷ (stop_ticks × tick_value)

Round down. Always.

Then confirm leverage ≤ your operational ceiling (daily P&L vol < 1.5% of equity for Taiwan futures).

If leverage exceeds ceiling → reduce to 1/3 Kelly, not round up contracts.

---

**Tweet 9**
Worked example (Taiwan TAIEX futures, momentum breakout):

• OOS avg P&L: +NT$3,800 / trade, 180 trades ✓
• MAE break: 1.2× ATR → Edge Ratio = 2.33 ✓
• Half-Kelly on NT$2M account: NT$294K risk budget ✓
• ATR=85, stop=102 ticks → NT$20,400/contract
• Contracts: 294K ÷ 20.4K = 14 → leverage 28× ← too high

Reduce to 1/3 Kelly → 4 contracts, 8× leverage. Viable.

---

**Tweet 10**
The 5 failure modes, ranked by frequency:

1. Starting at Gate 5 ("How many contracts do I want?")
2. Round-number stop instead of MAE analysis
3. Treating Gate 1 as optional ("I'll check OOS later")
4. Not recalibrating ATR daily
5. No kill conditions defined before deployment

No. 5 is the most expensive. You will manage emotionally without it.

---

**Tweet 11**
Kill conditions go in writing *before* you go live.

Minimum: define max drawdown, minimum win rate, minimum profit factor, minimum trade count for re-evaluation.

Without these: you cut at the worst time (capitulation) or hold through failure (denial).

The kill decision should be boring and mechanical, not emotional.

---

**Tweet 12 (close)**
Summary: 5 irreversible gates.

Gate 1: OOS EV positive ✓
Gate 2: MAE stop in ATR units, Edge Ratio > 1.5 ✓
Gate 3: Kelly risk budget fixed ✓
Gate 4: Today's ATR → absolute ticks ✓
Gate 5: Contracts = output, not input ✓

Sequence is the discipline. Reversing any gate is where the losses start.

---

*Based on 327 micro-decisions distilled from 8 years of trading conversations.*
*Full SOP with worked examples and self-test: [link to be added on publish]*
