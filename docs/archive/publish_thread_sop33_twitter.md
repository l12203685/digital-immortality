# Publish Thread — SOP #33 Edge Decay & Signal Crowding Protocol

**Hook tweet:**

"Your strategy stopped working.

You didn't change anything.

The market changed it for you.

Here's the 5-gate protocol for detecting edge decay before it kills your account:

[Thread]"

---

**Tweet 2 — The Problem**

"You backtest a strategy. OOS looks good. You deploy it.

Slowly, returns flatten. Then drawdown.

What happened: your edge was arbitraged away.

Other participants found the same signal and erased the inefficiency you were harvesting.

Most traders catch this too late."

---

**Tweet 3 — G0: Crowding Pre-Check**

"G0: Classify your edge source before deployment.

Type A — Structural (overnight gaps, liquidity)
Type B — Behavioral (momentum, anchoring)
Type C — Statistical (historical pattern)
Type D — Public indicator (RSI, MACD, Bollinger)

Type D requires OOS Sharpe ≥1.2, not 0.8.

Crowding is already happening."

---

**Tweet 4 — G1: Baseline Fingerprint**

"G1: Day 1 of deployment — lock in your fingerprint.

Record: OOS Sharpe, win rate, avg R/R, edge type, crowding level.

Save it.

Without a baseline, you have no reference point for posterior updates.

You're flying blind when the edge starts fading. (MD-109)"

---

**Tweet 5 — G2: Rolling Survival Rate**

"G2: Every 30 live trades, compute:

survival_rate = rolling_30d_sharpe ÷ historical_OOS_sharpe

≥1.0 → Thriving
0.60–0.99 → Stressed, investigate
<0.60 → Critical, pause immediately

This is your early warning system.

Not P&L. Not feelings. Survival rate. (MD-98)"

---

**Tweet 6 — G3: Bayesian Posterior Update**

"G3: When survival_rate is stressed, run four checks:

① Regime shift? (same strategy, different market type)
② Cohort test: split live trades by period — all down?
③ Signal timing drift: entry fill worsening?
④ Cost sensitivity: same edge after fees?

Each answer updates P(edge_decayed). (MD-109)"

---

**Tweet 7 — G4: Response Protocol**

"G4: Based on P(edge_decayed):

>0.65 → Reduce to 25% size, 30-trade window
0.50–0.65 → Hold 50% size, paper-track new variant
<0.50 → Regime issue → run Drawdown Recovery SOP (#30)

You're not killing the strategy.

You're managing the uncertainty."

---

**Tweet 8 — G5: Depth × Breadth Replenishment**

"G5: Every killed strategy opens a research slot.

Don't just cut — replace.

New research thread must be a different edge_type than the one you just killed.

Depth (improve existing) + Breadth (explore new edge_type) in parallel.

MD-110: portfolio diversification starts at the edge level."

---

**Tweet 9 — The Self-Test**

"Self-test:

DualMA BTC, deployed 90 days ago.
Survival_rate = 0.52.
Cohort check: all 3 periods trending down.
P(edge_decayed) = 0.45.

Decision: HOLD 50% size + start MR research thread.

Not 'hope it recovers.' Not 'add more capital.'

Evidence-gated response."

---

**Tweet 10 — Close**

"The market doesn't notify you when it's done giving you returns.

You need a monitoring system that detects the signal before the account sends you the message.

That's what SOP #33 is.

Full protocol: [link]

Next in series → SOP #34"
