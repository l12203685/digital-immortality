# SOP #29 — Strategy Monitoring & Portfolio Surveillance

> "Strategy management: define failure mode first. Not target, not hope — failure mode." — MD-96

---

## Why This Matters

SOP #04 (Strategy Kill) tells you *when* to kill a strategy.
SOP #26 (Walk-Forward Validation) tells you *whether* to deploy.
SOP #27 (Regime Detection) tells you *which regime* you're in.

This SOP answers: **what do you watch between deployment and kill?**

Most traders monitor P&L. That's the wrong thing to watch — it's a lagging, noisy signal that conflates market luck with strategy edge. Monitoring P&L in real time is the fastest path to discretionary overrides that destroy systematic edge.

**The monitoring gap:** Portfolio size is constrained by monitoring bandwidth, not capital. You can fund 20 strategies. You can only reliably watch 3–5. The rest run unmonitored — which is worse than not running them. (MD-142)

---

## Gate 0 — Define Failure Mode Before First Tick

**Principle: Strategy management starts at failure definition, not profit target (MD-96)**

Before deploying any strategy, write a one-line failure contract:

```
Strategy: [name]
Failure mode: [specific, measurable condition that proves the edge is gone]
Kill trigger: MDD > [X]% OR WR < [Y]% (≥ N trades) OR PF < [Z] (≥ M losses)
Review interval: [weekly / monthly / quarterly]
```

This contract is written **before** first tick. Not after a drawdown. Not after three losing weeks.

The failure mode is not "losing money." It is a specific statistical condition that distinguishes bad luck from edge decay.

**Output:** Failure contract document, signed off before deployment.

---

## Gate 1 — Survival Rate: Near-Term vs. Historical Baseline

**Principle: Strategy survival = near-term Sharpe ≥ 60% of historical Sharpe (MD-98)**

Every review interval, compute:

```
Survival_ratio = Rolling_Sharpe_recent(N_weeks) ÷ Historical_Sharpe_OOS

Thresholds:
  ≥ 1.0  → Healthy. No action.
  0.6–1.0 → Degraded. Monitor weekly, investigate regime fit.
  0.4–0.6 → Quarantine. Reduce size 50%. Root-cause analysis required.
  < 0.4   → Kill candidate. Enter SOP #04 (Strategy Kill Decision Tree).
```

N_weeks = 3× average holding period. Shorter = noise. Longer = too slow to detect decay.

**Why 60%?** Performance degrades continuously, not in discrete jumps. 60% is the threshold where "variance" can no longer explain the gap — structural edge decay becomes the null hypothesis.

---

## Gate 2 — Equity Curve as Leverage Trigger

**Principle: Equity curve = leverage trigger, not just performance record (MD-42)**

The equity curve encodes regime information before the regime detector fires. Use it:

```
Equity curve rule:
  Price(equity_curve) > MA_20 → full leverage
  Price(equity_curve) < MA_20 → reduce leverage 25–50%
  Price(equity_curve) < MA_20 for 3 consecutive reviews → enter quarantine
```

This is a *mechanical* rule — not judgment. The moment you start deciding whether "this drawdown feels different," you've introduced discretionary override that destroys systematic edge.

Equity curve monitoring is not about fear. It is a second-order regime detector that responds to degraded edge before the P&L signal reaches statistical significance.

---

## Gate 3 — Bandwidth Cap: Maximum Portfolio Size

**Principle: Monitoring bandwidth = hard cap on portfolio size (MD-142)**

```
Max_active_strategies = Monitoring_bandwidth ÷ Review_cost_per_strategy

Review_cost:
  Fully automated (runs + alerts only): 1 unit
  Semi-automated (requires weekly manual check): 3 units
  Manual (requires daily review): 8 units

Realistic bandwidth for solo operator: 10–15 units
→ Max 10–15 fully automated, OR 3–5 semi-automated, OR 1–2 manual strategies
```

If you exceed bandwidth, the marginal strategy is unmonitored — meaning failure modes trigger without anyone catching them. An unmonitored strategy with unlimited drawdown is not an asset; it is a liability.

**Rule:** Never deploy strategy N+1 unless you can specify who monitors it, at what frequency, and what triggers the review.

---

## Gate 4 — Rolling OOS Review Cadence

**Principle: Rolling OOS recalibration prevents anchoring to original IS performance (MD-143)**

```
Quarterly review (mandatory):
  1. Re-run walk-forward on expanded dataset (original IS + all live data to date)
  2. Check: does OOS Sharpe still ≥ 60% of IS Sharpe across ≥ 6 windows?
  3. Check: is survival_ratio (G1) above 0.6?
  4. Recalibrate regime thresholds if market structure has shifted (SOP #27)
  5. Update failure contract if parameter assumptions have changed
```

The quarterly review is not an invitation to re-optimize. It is a **contract renewal**: does the original hypothesis still hold in the new data? If yes, continue. If no, enter SOP #04.

---

## Gate 5 — Quarantine vs. Kill Protocol

**Principle: Quarantine buys time for root-cause analysis; kill ends unresolvable edge decay**

```
Quarantine (survival_ratio 0.4–0.6, OR equity_curve below MA_20 for 3+ reviews):
  - Reduce position size 50%
  - Double review frequency
  - Root-cause checklist:
    □ Regime shift? (run SOP #27 — has dominant regime changed?)
    □ Execution drag? (run SOP #28 G4 audit — has slippage increased?)
    □ Parameter drift? (re-run G4 walk-forward on expanded data)
    □ Correlation leak? (has strategy correlation to portfolio changed?)
  - Quarantine max duration: 2 review cycles (then kill or restore)

Kill (survival_ratio < 0.4, OR G0 failure condition met):
  - Enter SOP #04 (Strategy Kill Decision Tree)
  - Remove from portfolio immediately
  - Document cause in strategy log
  - Wait full OOS window before considering re-deployment
```

---

## Self-Test

**Scenario:** DualMA BTC deployed 30 days ago. Historical OOS Sharpe = 0.72. Rolling 4-week Sharpe = 0.38. Equity curve below MA_20 for 2 consecutive weeks.

**Apply gates:**

- G1: Survival ratio = 0.38 / 0.72 = 0.53 → **Quarantine zone (0.4–0.6)**
- G2: Equity curve below MA_20 for 2 weeks → **Reduce leverage 25%**
- G3: 1 fully automated strategy → bandwidth OK
- G5: Root-cause checklist:
  - Regime: run SOP #27 → if regime shifted to MR and DualMA is trend-only → **regime mismatch, not edge decay → hold with rotation**
  - If regime unchanged → **parameter drift candidate → run G4 walk-forward**

**Result:** Quarantine (50% size reduction). Root-cause = regime mismatch. Decision: hold, re-run when trending regime restores. Not a kill.

---

## DNA Anchors

| Gate | MD | Principle |
|------|----|-----------|
| G0 | MD-96 | Strategy management = define failure mode first |
| G1 | MD-98 | Strategy survival = near-term ≥ 60% of historical Sharpe |
| G2 | MD-42 | Equity curve = leverage trigger |
| G3 | MD-142 | Monitoring bandwidth = portfolio size hard cap |
| G4 | MD-143 | Rolling OOS recalibration prevents IS anchoring |
| G5 | MD-96 + SOP #04 | Quarantine vs. kill = root-cause before decision |

---

*Part of the Edward Lin Trading System SOP Series. SOP #01–#29 available.*
