# SOP #31 — Parsimony & Complexity Budget Protocol

> When does a strategy become too complex to survive deployment?
> This SOP answers that question before you lose money finding out.

**Backing MDs:** MD-97 (structure before parameters) / MD-113 (no parameters ≠ immune to overfitting) / MD-114 (parameter count = functional indicator not absolute minimum) / MD-116 (simplicity = depth of understanding) / MD-98 (OOS Sharpe gate) / MD-157 (first-principles structure)

---

## The Gap This Fills

SOP #15 (Backtest Deception) teaches you to distrust in-sample results.
SOP #26 (Walk-Forward Validation) teaches you to validate OOS.
**Neither tells you how to decide if your strategy is structurally too complex to trust.**

Complexity is not the number of parameters. It is the ratio of degrees of freedom to evidence. A strategy with 10 parameters and 2,000 OOS trades is leaner than one with 3 parameters and 15 OOS trades.

---

## Gates

### G0 — Write the Mechanism Sentence (MD-97)

Before any parameter exists, write one sentence:

> "This strategy makes money because ____."

Requirements:
- No numbers
- No indicator names
- Only structural logic (e.g., "momentum persists in trending regimes")

If you cannot write it: **STOP. You have a curve-fit, not a strategy.**

---

### G1 — Degrees of Freedom Audit

Count:
- `P` = tunable numeric parameters
- `B` = conditional branches (if-else logic forks)
- `I` = indicators used (each counts as 1 DoF minimum)

```
DoF = P + B + I
```

Record: `DoF_total` = ___

---

### G2 — Parsimony Gate (MD-113 / MD-114)

Minimum OOS trades required = `DoF × 10`

```
Required OOS trades ≥ DoF × 10
```

| DoF | Min OOS trades |
|-----|---------------|
| 3   | 30            |
| 5   | 50            |
| 10  | 100           |
| 20  | 200           |

If `actual OOS trades < DoF × 10`: **REDUCE complexity or gather more OOS evidence before deploying.**

Note: More is not always worse. MD-114 says parameter count is a *functional* indicator — a strategy with 8 parameters and 1,000 OOS trades may be simpler (relative to evidence) than a 2-parameter strategy with 18 OOS trades.

---

### G3 — Simplicity Stress Test (MD-116)

Remove the least-significant parameter (smallest Sharpe contribution in IS). Re-run OOS.

```
Sharpe degradation = (Sharpe_full - Sharpe_reduced) / Sharpe_full
```

- Degradation < 15%: parameter was **decorative** → remove permanently
- Degradation 15–30%: parameter is **marginal** → mark as conditional
- Degradation > 30%: parameter is **load-bearing** → keep, but document why

If you can explain *why* each parameter exists from the mechanism sentence: **PASS**
If any parameter exists only because it "improved backtest": **FAIL** → G0

---

### G4 — Cross-Regime or Cross-Asset Validation

Run the strategy (same parameters, no refit) on:
- A different time period (non-overlapping), OR
- A correlated asset in the same regime type

```
Regime-subset Sharpe ≥ 0.6 × IS Sharpe  (MD-98 threshold)
```

- Passes on ≥ 2/3 cross-validation sets: **ROBUST**
- Passes on 1/3: **CONDITIONAL** — deploy at 50% size, document the condition
- Fails all: **FRAGILE** — strategy is period-specific → back to G0

---

### G5 — Deployment Contract

Before first tick, write:

```
Mechanism: [G0 sentence]
DoF: [G1 count]
OOS coverage: [G2 ratio]
Removed decorative parameters: [G3 list]
Cross-validation result: [G4 outcome]
Kill condition: [specific, pre-committed — MD-96]
```

If any field is blank: **WAIT**

---

## Self-Test Scenario

**Strategy:** DualMA BTC, SMA(10)/SMA(30) crossover, trend filter, ATR stop

**G0:** "Momentum persists when short-term price trend exceeds long-term trend in trending regimes." ✓

**G1:** P=2 (SMA periods), B=1 (trend filter branch), I=2 (SMA + ATR) → DoF = 5

**G2:** Required OOS = 50 trades; actual OOS = 200 → **PASS** (4× coverage)

**G3:** Remove ATR stop, run OOS → Sharpe 1.2 → 0.6 (50% degradation) → **load-bearing, keep**

**G4:** Run on ETH same period → Sharpe 0.8 vs IS 1.3 (62% coverage) → **ROBUST**

**G5:** All fields fillable → **DEPLOY at full size**

---

## Common Failure Modes

| Symptom | Root cause | Fix |
|---------|-----------|-----|
| Cannot write G0 sentence | No structural logic | Delete strategy |
| G2 fails with "only 3 parameters" | DoF fine, OOS sample too small | Run longer OOS before deploy |
| G3 shows all parameters load-bearing | Overfitted ensemble | Reduce to single mechanism |
| G4 fails on cross-asset | Period-specific artifact | Mark as single-regime conditional |

---

## Relationship to Other SOPs

- SOP #15 (Backtest Deception): catches in-sample overfitting → SOP #31 catches structural complexity
- SOP #26 (Walk-Forward): validates OOS windows → SOP #31 determines if OOS sample is sufficient for complexity level
- SOP #01 (Strategy Development): builds the strategy → SOP #31 stress-tests it before deploy
- SOP #29 (Strategy Monitoring): monitors live → SOP #31 ensures what you monitor was deployable

---

## One-Line Summary

> Complexity is not parameter count. It is the ratio of degrees of freedom to evidence. Earn your parameters with OOS trades before going live.
