# Twitter/X Thread — SOP #02: Portfolio Construction

> Source: Knowledge Product #02 (Portfolio Construction SOP)
> Status: DRAFTED — ready to post after SOP #01 thread goes live
> Cycle: 112

---

**Tweet 1 (hook)**
Most traders combine strategies the wrong way.

They pick 3–5 strategies they like, allocate equally, and call it "diversified."

That's not a portfolio. That's correlated risk with extra steps.

Here's how to build one properly. 🧵

---

**Tweet 2**
First principle: alpha must exist before you combine anything.

Portfolio construction does NOT create alpha. It manages risk.

If a strategy doesn't pass a full development SOP independently (OOS > IS, edge_ratio > 1.5, sample ≥ 30 trades) — it doesn't enter the candidate list.

---

**Tweet 3**
Step 1: Classify each strategy on a 2×2 grid.

| | Trend-following | Mean-reverting |
|---|---|---|
| Long-biased | Trend-Long | MR-Long |
| Short-biased | Trend-Short | MR-Short |

Two strategies in the same cell = structural redundancy, not diversification.

You need to cover at least 2 cells, ideally all 4.

---

**Tweet 4**
Step 2: Compute pairwise Calmar ratios — on OOS data, equal weight.

Combined_Calmar(A, B) = CAGR(A+B) / MaxDrawdown(A+B)

Rank all pairs. Pick the top pair as your seed portfolio.

Why Calmar, not Sharpe?
Calmar penalises peak-to-trough drawdown — the metric that terminates real accounts.

---

**Tweet 5**
Step 3: Recursive greedy addition.

For each remaining candidate C:
• Add C (equal weight) to current portfolio
• Score = new portfolio Calmar
• Add C if and only if Calmar improves

Stop when no candidate improves it.

Hard limits: max 6–8 strategies. Beyond that, monitoring bandwidth is exceeded.

---

**Tweet 6**
One often-missed hard constraint:

No two strategies with rolling 30-day return correlation > 0.70.

Why? Under regime stress, correlated strategies synchronise drawdowns.
What looks like diversification in normal times becomes concentration in crisis.

Correlation check runs at the portfolio level, not per-strategy.

---

**Tweet 7**
Step 4: Optimise weights via Calmar frontier.

Once the strategy set is fixed:
• Maximise CAGR / MaxDrawdown
• Subject to: weights sum to 1, minimum 5% floor per strategy

The 5% floor prevents zero-weight "ghost" strategies that never trade but inflate your backtest's strategy count.

---

**Tweet 8**
Step 5: Regime routing table.

Not all strategies should run in all regimes.

Build a lookup table:
• Trending regime → activate Trend-Long / Trend-Short
• Mean-reverting regime → activate MR-Long / MR-Short
• Mixed regime → activate overlap strategies only

Regime detector uses ATR percentile + trend structure (Dow Theory confirmation).

---

**Tweet 9**
Step 6: Overnight / cross-session holds need separate edge proof.

If a strategy holds positions overnight, the edge for those overnight returns must be verified independently — not inferred from intraday results.

Overnight = different risk profile, different edge source, different validation required.

---

**Tweet 10**
Portfolio-level kill conditions (separate from per-strategy kills):

• Portfolio MDD > 15% → halt all strategies, review
• Two or more strategies simultaneously in "degrading" zone (edge_ratio 1.2–1.5) → reduce exposure 50%
• Rolling 30-day correlation spike above 0.70 between any pair → investigate regime shift

These trigger even if no individual strategy hits its kill condition.

---

**Tweet 11**
What you've built when this SOP is complete:

✅ A Calmar-optimised allocation vector (not arbitrary equal weight)
✅ A correlation matrix with enforced limits
✅ A regime routing table (strategies activate by market state)
✅ Portfolio-level kill conditions

This is a trading system. Not a collection of bets.

---

**Tweet 12 (close)**
SOP sequence so far:

#01 — Strategy Development (find the edge)
#02 — Portfolio Construction (this thread)
#03 — Execution & Sizing (real-time checklist)
#04 — Strategy Kill Decision Tree (when to quit)

Four SOPs. One complete trading system.

Most people skip #02 and wonder why their "diversified" portfolio blew up.

---

*End of thread.*
