# SOP #92 — Strategy Disable & Reactivation Protocol

> Domain: Trading Operations / Strategy Lifecycle
> Created: 2026-04-09T11:25Z
> Status: OPERATIONAL
> Trigger: G0 — Any strategy's Profit Factor drops below kill threshold (PF < 0.8) OR
>           manual disable review requested after N consecutive flat ticks

---

## Why This Exists

SOP #75 (Strategy Pool Lifecycle) defines when to add or retire strategies.
SOP #29 (Strategy Monitoring) defines ongoing health checks.
SOP #04 (Strategy Kill Decision Tree) defines the kill decision.

**Gap identified:**
None of these SOPs close the loop on what happens after a strategy is killed. Specifically:

- When is a disabled strategy eligible for reactivation?
- Under what conditions is reactivation safe vs. premature?
- How do you distinguish "strategy broke" from "regime was wrong for this strategy"?
- What is the minimum cool-down and re-validation sequence before reactivating?

`DualMA_10_30` was disabled this session (PF 0.65). Without this SOP, the question "should
we re-enable it when the regime shifts?" has no procedural answer. Informal reactivation
is how strategies with structural flaws re-enter the pool and compound losses.

**This SOP covers:** Disable trigger, cool-down period, reactivation criteria, validation
sequence, and the go/no-go gate before live re-deployment.

---

## G0 — Disable Trigger

Fire this SOP when ANY of:
- Strategy PF < kill threshold (default 0.8) → auto-disable by engine
- Strategy cum_pnl < drawdown limit AND position count > 3 (manual disable)
- Strategy fires in a regime it is not designed for (regime-filter audit finding)
- Manual disable requested for review (no minimum loss required)

Log entry required at disable:
```
DISABLED | strategy=<name> | reason=<pf_breach|drawdown|regime_mismatch|manual>
         | pf_at_disable=<value> | cum_pnl_at_disable=<value> | tick=<N>
         | regime=<regime> | timestamp=<ISO>
```

---

## G1 — Cool-Down Period

Minimum cool-down before reactivation review is permitted:

| Disable Reason | Minimum Cool-Down |
|---|---|
| PF breach (PF < 0.8) | 48 hours OR regime change, whichever is later |
| Drawdown limit | 72 hours AND regime change required |
| Regime mismatch | Until regime changes + 24 hours |
| Manual (exploratory) | 24 hours |

**During cool-down: no re-enabling, no parameter tweaks, no partial re-entry.**

Cool-down exists to prevent the common failure mode: strategy loses → developer gets nervous
→ tweaks parameters → re-enables immediately → strategy loses again with different parameters.
You need regime evidence before re-enabling, not just time.

---

## G2 — Reactivation Eligibility Check

After cool-down, run this 5-point check. All 5 must pass:

**Check 1 — Regime Alignment**
- What regime is the strategy designed for?
- What is the current regime?
- PASS: current regime matches strategy's target regime
- FAIL: mixed or opposite regime → extend cool-down, retry tomorrow

**Check 2 — Root Cause Identified**
- Why was it disabled? Is the root cause understood?
  - PF breach: was it bad luck (regime mismatch) or structural (strategy logic gap)?
  - Regime mismatch: has the regime filter been patched?
- PASS: root cause documented and confirmed as regime-related (not structural)
- FAIL: root cause unclear or structural → do NOT reactivate, route to SOP #75 (retire)

**Check 3 — Backtest on Recent Data**
- Run strategy on last 30 days of data (paper or backtest)
- Minimum: PF > 1.0 on recent data
- PASS: PF ≥ 1.0 AND win rate ≥ 45%
- FAIL: PF < 1.0 → do not reactivate

**Check 4 — Pool Capacity**
- Current active strategy count?
- Is there capacity to add one more without exceeding max pool size?
- PASS: active count < max pool size (default 15 active)
- FAIL: pool at capacity → must retire another strategy first (SOP #75)

**Check 5 — Parameter Freeze Confirmation**
- CRITICAL: Are the parameters identical to the last validated version?
- If parameters were changed since disable: require full walk-forward validation (SOP #26)
  before this SOP can proceed.
- PASS: parameters unchanged from last validated state
- FAIL: parameters changed → full walk-forward required first

---

## G3 — Paper Re-Entry

Reactivation is NOT immediate live trading. Steps:

1. Re-enable strategy in PAPER mode only
2. Monitor for minimum 10 ticks (or 24 hours, whichever is longer)
3. During paper phase, track:
   - Signal frequency (is it firing appropriately for current regime?)
   - Entry quality (is entry price where backtest expected?)
   - PnL_pct per trade (is each trade within expected range?)

**Paper phase pass criteria:**
- At least 3 trades completed (not just signals)
- PF on paper trades > 0.8
- No anomalous entries (e.g., firing in wrong regime)

If paper phase fails any criterion: return to G1 (cool-down reset).

---

## G4 — Live Reactivation & Monitoring

After passing G3 paper phase:

1. Re-enable in live mode with **reduced position sizing** (50% of normal for first 5 live trades)
2. Monitor for first 5 live trades
3. After 5 trades: if PF > 0.8 → normalize position sizing
4. If PF < 0.8 after 5 live trades → permanent disable, route to SOP #75 retirement

Log entry at reactivation:
```
REACTIVATED | strategy=<name> | paper_pf=<value> | paper_trades=<N>
            | regime=<regime> | sizing=50% | timestamp=<ISO>
```

---

## Self-Test Scenario

**Scenario:** DualMA_10_30 was disabled at tick 1 today (PF 0.65, short into rising price,
regime: mixed). Current time: cycle 257. When is it eligible for reactivation review?

**Walk through the gates:**

- G0: Disabled reason = PF breach. Log entry required. ✓
- G1: Minimum cool-down = 48 hours OR regime change, whichever is later. Regime is still
  "mixed" → cool-down clock does not start until regime changes. Current: NOT eligible.
- G2: Will not run until cool-down completes.

**Correct answer:** DualMA_10_30 is NOT eligible for reactivation today. Regime must change
from "mixed" to "trending" first. Then 48-hour cool-down starts. Then G2 checks run.
If the regime shifts tomorrow (Day +1), earliest eligible review date = Day +3.

**Red flag:** If someone re-enables DualMA_10_30 in today's mixed regime because "the price
looks like it might trend now" → that is a G1 violation. This SOP blocks it.

---

## Integration Points

| SOP | Connection |
|---|---|
| SOP #04 Kill Decision Tree | Triggers G0 of this SOP |
| SOP #26 Walk-Forward Validation | Required if parameters changed before G2 |
| SOP #29 Strategy Monitoring | Feeds ongoing PF data that triggers G0 |
| SOP #75 Strategy Pool Lifecycle | Retirement path if reactivation fails |
| SOP #07 Regime Detection | G1 and G2 depend on regime classification |

---

## Twitter Thread Hook

**Thread: "The most dangerous moment in systematic trading isn't when a strategy fails."**

"It's the 48 hours AFTER it fails.

Here's why most traders give back all their gains trying to 'fix' a broken strategy — and the
5-gate protocol I use to prevent it:

1/ Strategy gets disabled. PF dropped to 0.65. Classic gut reaction: tweak parameters,
re-enable immediately. This is how you compound losses.

2/ Gate 1: Mandatory cool-down. 48 hours minimum. No tweaks. No re-enabling.
You need regime evidence, not time.

3/ Gate 2: Root cause. Was it structural (strategy logic is broken) or environmental
(wrong regime)? Different diagnoses → different treatments.

4/ Gate 3: Backtest on recent data. Parameters unchanged. If PF < 1.0 on recent data,
the strategy is still broken regardless of your gut feel.

5/ Gate 4: Paper re-entry only. 10 ticks minimum. Earn the right to go live again.

6/ Gate 5: Reduced sizing on first 5 live trades. 50% of normal. Let it prove itself again.

The protocol exists because intuition after a loss is the least reliable signal you have.

SOP #92 full writeup in replies."
