# SOP #09 — Risk Management & Drawdown Response

> From Edward Lin's micro-decision archive. Backing MDs: MD-27, MD-50, MD-75, MD-91, MD-96, MD-18.

---

## Core Principle

Risk management has one job: keep you alive long enough to be right.
The equity curve is not a performance report — it is a **leverage instruction**.

---

## G0 — Pre-Trade: Write the Kill Condition First (MD-96)

Before opening any position, define:

1. **What does failure look like?** (not "it goes down" — specific falsification)
2. **What is the max loss per trade?** (in dollars, not %)
3. **At what equity level does the strategy stop?**

> Rule: You cannot manage what you haven't pre-defined. Strategy management = failure definition, not real-time reaction.

**Fail condition:** Entering a trade without written stop = you will improvise when emotional. Improvised risk management always fails at the worst moment.

---

## G1 — Daily Loss Limit: Leverage × Daily P&L ≤ 1% Rule (MD-50)

Daily loss limit scales with leverage:

```
max_daily_loss = account_equity × 0.01 / leverage_multiplier
```

| Leverage | Max daily loss (on $100k account) |
|----------|-----------------------------------|
| 1× | $1,000 |
| 3× | $333 |
| 5× | $200 |
| 10× | $100 |

**Stop trading for the day when the limit is hit.** No exceptions. No "one more trade to recover."

> Rationale: High leverage amplifies noise into existential events. The 1% rule converts "I had a bad day" into "the strategy is performing within expected variance."

---

## G2 — Event Risk: Reduce Leverage 50% (MD-27)

When a **known, scheduled event** approaches (FOMC, earnings, elections, expiry), reduce leverage by 50% **before** the event.

Trigger list:
- FOMC/Fed rate decisions
- Taiwan/US elections
- Expiry week (futures/options)
- GDP, CPI releases
- Any event where market gap risk is asymmetric

> Rule: Events are not surprises — they are pre-scheduled regime uncertainty spikes. You don't need to predict direction. You need to not be full leverage when the gap opens.

**After the event:** Re-evaluate regime. Restore leverage only if the post-event regime matches your strategy's target regime.

---

## G3 — Equity Curve as Leverage Trigger (MD-75)

The equity curve is a real-time signal. Define three states:

| Equity curve state | Definition | Leverage action |
|--------------------|------------|----------------|
| **Normal** | Within 1× ATR of 20-day MA | Full leverage |
| **Warning** | 1–2× ATR below 20-day MA | Reduce to 50% |
| **Stop** | >2× ATR below 20-day MA or new N-day low | Stop trading, paper-trade only |

> The equity curve knows before you do that the strategy has entered an unfavorable regime. Waiting until you "know why" costs an additional 30–50% of drawdown.

**Return to full leverage only when:** equity curve recovers above 20-day MA on live trading (not paper).

---

## G4 — Adding to a Losing Position: Pre-Condition Required (MD-91)

Adding to a losing position is NOT a drawdown response — it is a planned action with a pre-condition.

**Required before adding on drawdown:**

- [ ] Strategy is statistically robust (OOS Sharpe > 0.5, N > 30 trades)
- [ ] Current drawdown is within the strategy's historically observed max DD
- [ ] You have written the scale-in levels **before** opening the original position
- [ ] Adding does NOT violate the G1 daily loss limit

**If any condition fails:** Do not add. The trade is at its original size. Period.

> "I'll average down to lower my cost basis" is not a plan — it is capitulation with extra steps. Averaging down without a pre-written plan = structural alpha leak.

---

## G5 — Drawdown Recovery Protocol

When equity curve hits **Stop** state:

1. **Close all positions.** Do not wait for recovery.
2. **Switch to paper trading** for minimum 5 sessions.
3. **Diagnose:** Is this (a) normal strategy variance, (b) regime mismatch, or (c) strategy failure?
   - Use SOP #04 Strategy Kill Decision Tree to classify
   - If regime mismatch → wait for regime to rotate, then resume
   - If strategy failure → kill the strategy
4. **Resume live only when:** paper results are positive AND equity curve is above 20-day MA
5. **Start at 25% leverage.** Scale back to full over 4 weeks if performance holds.

---

## Summary Decision Tree

```
New day →
  G0: Kill conditions written? → NO → Write them first
  G1: Hit daily loss limit? → YES → Stop for the day
  
Event approaching →
  G2: Reduce leverage 50% before event

End of day →
  G3: Equity curve check
    Normal → Full leverage tomorrow
    Warning → 50% leverage tomorrow
    Stop → Close positions, paper mode

Trade going against you →
  G4: Was scale-in pre-planned? → NO → Do NOT add
    YES + all conditions met → Add per plan
    
In drawdown →
  G5: Close → paper → diagnose → scale back slowly
```

---

## Anti-Patterns to Avoid

| Anti-pattern | Why it fails |
|--------------|--------------|
| "I'll stop at the end of the week" | Daily limits exist because intraday leverage kills |
| "This event is different" | All events are asymmetric. The rule doesn't have exceptions. |
| "The strategy is fine, I just had bad luck" | Equity curve doesn't care about luck. |
| "I'll add to average down, it always works" | It works until it doesn't, and when it doesn't, it's terminal. |
| "I'll paper trade until I feel confident" | Confidence is not the return-to-live criterion. Equity curve MA is. |
