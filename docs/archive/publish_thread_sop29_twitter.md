# Twitter Thread — SOP #29: Strategy Monitoring & Portfolio Surveillance

**Hook tweet:**
Your strategy is live. Now what do you watch?

Not P&L. P&L is noise. Here's the monitoring framework that tells you the difference between a bad week and a dead strategy.

SOP #29: Strategy Monitoring & Portfolio Surveillance 🧵

---

**Tweet 2:**
Most traders monitor P&L in real time.

That's the wrong signal. It's lagging, noisy, and triggers discretionary overrides that destroy systematic edge.

What you should monitor: survival rate, equity curve shape, and bandwidth utilization.

---

**Tweet 3:**
G0: Write the failure contract BEFORE first tick.

Not profit target. Failure mode.

"Kill if MDD > 15% OR WR < 35% (≥5 trades) OR PF < 0.85 (≥3 losses)"

Specific. Measurable. Signed off before deployment. Not after the drawdown.

(MD-96)

---

**Tweet 4:**
G1: Survival rate = Rolling Sharpe ÷ Historical OOS Sharpe

≥ 1.0 → Healthy
0.6–1.0 → Degraded, monitor weekly
0.4–0.6 → Quarantine, cut size 50%
< 0.4 → Kill candidate

60% threshold: below it, "variance" no longer explains the gap. Edge decay is now the null hypothesis.

(MD-98)

---

**Tweet 5:**
G2: Equity curve = leverage trigger.

Price(equity curve) > MA_20 → full leverage
Price(equity curve) < MA_20 → reduce 25–50%
Below MA_20 for 3 consecutive reviews → quarantine

This is mechanical. The moment you decide "this drawdown feels different," you've gone discretionary. That's how systematic edges die.

(MD-42)

---

**Tweet 6:**
G3: Bandwidth cap.

Portfolio size is limited by monitoring bandwidth, not capital.

Solo operator realistic bandwidth: 10–15 units
- Fully automated: 1 unit each
- Semi-automated: 3 units each
- Manual: 8 units each

An unmonitored strategy with unlimited drawdown isn't an asset. It's a liability.

(MD-142)

---

**Tweet 7:**
The math is brutal:

15 bandwidth units
÷ 3 units per semi-automated strategy
= 5 strategies max

Most retail quants fund 20 strategies. 15 run unmonitored.

Every unmonitored strategy is a ticking clock waiting to hit its failure condition with nobody watching.

---

**Tweet 8:**
G4: Quarterly rolling OOS review.

Not re-optimization. Contract renewal.

Expand the dataset. Re-run walk-forward. Does OOS Sharpe still ≥ 60% of IS Sharpe across ≥ 6 windows?

If yes: continue.
If no: enter Kill Decision Tree (SOP #04).

(MD-143)

---

**Tweet 9:**
G5: Quarantine vs. Kill.

Quarantine (survival ratio 0.4–0.6):
- Cut size 50%
- Root-cause checklist: regime shift? Slippage increase? Parameter drift?
- Max 2 review cycles — then kill or restore

Kill (survival ratio < 0.4 OR G0 triggered):
- Enter SOP #04 immediately
- Wait full OOS window before re-deployment

---

**Tweet 10:**
Self-test: DualMA BTC, 30 days live.

Historical OOS Sharpe: 0.72
Rolling 4-week Sharpe: 0.38
Equity curve below MA_20 for 2 weeks

G1: 0.38/0.72 = 0.53 → Quarantine
G2: Below MA_20 → Reduce leverage 25%
Root cause: Regime shifted to MR → not edge decay, strategy mismatch

Decision: hold, don't kill. Wait for trending regime.

---

**Tweet 11:**
The 5-gate loop:

G0: Define failure mode → G1: Survival rate → G2: Equity curve leverage → G3: Bandwidth cap → G4: Quarterly OOS → G5: Quarantine vs. kill

Repeat every review cycle. Pre-committed. Mechanical. No exceptions for "this one feels different."

---

**Tweet 12:**
SOP #29 completes the monitoring layer of the trading system:

#04 Kill decisions
#26 Walk-forward validation
#27 Regime detection
#28 Execution & slippage
#29 Strategy monitoring ← you are here

The full system: know when to build, validate, detect regime, execute, monitor, and kill.
