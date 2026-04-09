# Twitter Thread — SOP #38: Alpha Decay & Strategy Sunset Protocol

**Hook (Tweet 1)**:
Most traders kill strategies too early. Some hold them too long. Both lose money.

The difference: do you know *why* the strategy is failing?

Here's a 5-gate protocol to detect alpha decay before it kills your account 🧵

---

**Tweet 2**:
Strategies die from 3 forces:
- Crowding → edge compressed
- Regime shift → premise false
- Arbitrage → pattern priced away

They don't die instantly. They *decay*.

The chart looks bad before the reason is clear.

---

**Tweet 3**:
Gate 0: Rolling OOS Monitor (weekly)

Compare last 30d OOS vs. go-live baseline across 3 metrics:
- Sharpe ratio
- Profit Factor
- Win Rate

rolling_score = 0.4×(sharpe_30d/baseline) + 0.4×(pf) + 0.2×(wr)

Score < 0.6 for 2 weeks → escalate

---

**Tweet 4**:
Gate 1: Regime Mismatch Check

Before calling it decay, ask:
Is the strategy running in its *target* regime?

A trending strategy underperforming in a mean-reverting market isn't failing.
It's misdeployed.

Fix: rotate strategy, not kill it.

---

**Tweet 5**:
Gate 2: Edge Ratio Integrity

edge_ratio = MFE / MAE × √N

Healthy: ≥ 3.0
Warning: 1.5–3.0 → reduce size 50%
Dead: < 1.5 → investigate premise

This separates noise from structural failure.
P&L doesn't. Edge ratio does.

---

**Tweet 6**:
Gate 3: Structural Premise Check

Every strategy rests on a falsifiable statement.

DualMA: "BTC momentum persists over 10–30 bars"

Ask: Is that still true in current data?

If yes → drawdown, not death.
If no → the strategy's premise is gone. Kill it.

---

**Tweet 7**:
Gate 4: Anti-Capitulation Sanity Check

Before killing, answer 3 questions:
1. Is DD within historical max?
2. Is the kill emotion-driven or metric-driven?
3. Are other strategies in the same class also failing?

≥2 pointing to "normal variance" → reduce size, wait 14 days.
≥2 pointing to "genuine failure" → kill.

---

**Tweet 8**:
Gate 5: Kill Protocol

1. Close all positions (accept slippage)
2. Document in strategy_graveyard.md: date / regime / edge_ratio / reason
3. Block re-deployment for 30 days minimum

Resurrection requires:
- Root cause identified
- Paper test shows edge_ratio ≥ 3.0 again
- 20+ ticks before re-deploying capital

---

**Tweet 9**:
The core insight:

Most traders sunset strategies because of P&L pain.
This protocol forces you to find the *structural* failure first.

Then P&L confirms it.

Emotion-driven kills destroy more capital than late kills.

---

**Tweet 10**:
The difference between drawdown and dying strategy:

Is the premise still true?

That's the only question that matters.

Everything else is noise.

---

*Thread end. Save this for the next time you're about to kill a strategy at the bottom.*
