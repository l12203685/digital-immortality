# Twitter Thread — SOP #15: The Backtest Deception Protocol

**Hook tweet:**
Your backtest looks great.

That's the problem.

A beautiful equity curve is a warning, not a confirmation.

Here's the 4-gate protocol for catching overfitting before it costs you real money:

---

**Tweet 2:**
Gate 0: Structure before parameters.

Before you touch a single parameter, finish this sentence:

"This strategy profits because ___"

The blank must name a market mechanism — not an indicator.

Indicators are implementation. Mechanism is edge. (MD-97)

---

**Tweet 3:**
If you can't finish that sentence without saying "RSI" or "moving average" — stop.

You don't have a strategy. You have a pattern.

Patterns are found by looking backward. Mechanisms are validated by logic.

---

**Tweet 4:**
Gate 1: Out-of-sample proof.

Lock 30% of your historical data before any optimization begins.

Never touch it. Not even to "check."

After optimization: OOS Sharpe must be ≥60% of IS Sharpe.

If it degrades more than 40% → overfit. (MD-98)

---

**Tweet 5:**
The most common mistake:

Run optimization → check OOS → adjust → check OOS again.

You just made OOS a second in-sample dataset.

Lock it before you start. One look only.

---

**Tweet 6:**
Gate 2: Walk-forward validation.

Divide your data into rolling windows.

Optimize on each window. Test on the next period. Move forward. Repeat.

≥6 windows. Win rate ≥60%.

A strategy that works only on the full sample is a curve-fit. (MD-143)

---

**Tweet 7:**
Gate 3: Regime decomposition.

Split the backtest by market regime: trending, mean-reverting, mixed.

Calculate Sharpe separately for each.

Annual Sharpe 0.8 can hide: trending +1.3, mean-reverting -0.4.

That negative will kill you in the wrong environment. (MD-108)

---

**Tweet 8:**
The 4 self-test questions before any deployment:

1. What mechanism does your strategy exploit? (No indicators allowed)
2. OOS Sharpe ÷ IS Sharpe = ?
3. Walk-forward win rate = ?
4. Sharpe in non-target regime = ?

"I don't know" on any answer = don't deploy.

---

**Tweet 9:**
The test of a backtest is not how good it looks.

It's how much it degrades on data it has never seen.

Beautiful IS performance + poor OOS degradation = evidence of structural edge.

Beautiful IS + same OOS = you got lucky once.

4 gates. One rule: prove it on data the strategy never touched.

[SOP #15 full doc: link]
