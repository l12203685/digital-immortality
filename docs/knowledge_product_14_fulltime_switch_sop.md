# SOP #14 — The Full-Time Switch Threshold: When Trading Income Justifies Leaving Salary

> Source MDs: MD-26 (Alpha vs salary switch threshold), MD-19 (投資公司門檻量化), MD-06 (穩定收入=策略開發認知資源先決), MD-75 (權益曲線=槓桿觸發器), MD-111 (穩定收入=策略開發認知資源先決)
> One-claim: "Most traders quit their job too early or never. Both are wrong."

---

## Why This SOP Exists

The full-time switch is the highest-stakes career decision a trader makes. Most people get it wrong in both directions:
- Too early: live trading income replaces salary before edge is proven at scale → drawdown destroys both income and psychology
- Never: salary security prevents the capital accumulation and focus required to build real edge

The switch is not a feeling. It's a threshold calculation. MD-26 defines it.

---

## Gate Sequence (5 gates)

### G0 — Edge Verification First
Before any income calculation: verify edge exists at production scale.

Requirements (all must pass):
1. ≥200 out-of-sample trades (not in-sample optimization)
2. Sharpe ≥ 1.0 after transaction costs
3. Max drawdown ≤ 25% of allocated capital
4. Edge_ratio (MFE/MAE × √N) ≥ 2.0 (MD-13)

Failure mode: confusing a bull market with personal edge. Run the numbers on a down-regime period specifically.

If G0 fails: do NOT proceed. The rest of this SOP is irrelevant.

### G1 — The Alpha-Salary Crossover Calculation (MD-26)
Calculate when monthly trading alpha (after costs, taxes) exceeds salary × 1.5 consistently.

Formula:
```
Switch threshold = Monthly salary × 1.5 × 12 months
Minimum capital required = Switch threshold / (target_annual_return × (1 - max_drawdown_reserve))
```

The 1.5× multiplier accounts for:
- Benefits (health insurance, pension) lost from salary
- Income variance (trading income is not linear)
- 6-month runway reserve

Example:
- Monthly salary: $5,000
- Switch threshold: $7,500/month = $90,000/year
- Target annual return: 30% on allocated capital
- Capital required: $90,000 / 0.30 = $300,000 minimum allocated capital
- Add 6-month reserve: $90,000 / 2 = $45,000 cash buffer
- Total capital needed: $345,000

This is the number. Not a feeling, not a target — the threshold.

### G2 — Sustained Evidence Window
One good month is not evidence. Required: 12 consecutive months at or above threshold.

Tracking format:
```
Month | Alpha ($) | Threshold ($) | Pass/Fail
2025-01 | $8,200 | $7,500 | PASS
2025-02 | $4,100 | $7,500 | FAIL → restart counter
```

Counter resets on any FAIL month. The 12-month streak must be unbroken.

Why 12 months? Captures at least one full regime cycle (bull + correction or sideways).

Failure mode: cherry-picking 3 good months during a trending market and calling it "12 months equivalent."

### G3 — Cognitive Resource Prerequisite (MD-06, MD-111)
Stable income is the cognitive prerequisite for strategy development — not the reward for it.

Before switching: verify you have ≥18 months of living expenses in non-trading accounts.

This is separate from trading capital. If trading capital and living expenses share the same pool, psychological pressure contaminates decision-making. A $20K drawdown feels different when it's also 3 months of rent.

Rule: trading capital and living capital are structurally isolated. Never touch living capital to add to a drawdown.

### G4 — Equity Curve Leverage Gate (MD-75)
The switch day is not permanent. Build a circuit-breaker back in.

Define in writing BEFORE switching:
```
Normal state: equity curve slope > 0 over 90 days → continue
Warning state: equity curve slope ≤ 0 over 90 days → reduce size 50%, reassess
Return-to-salary trigger: 3 consecutive losing months at full size → update résumé
```

The return-to-salary trigger is not failure. It's the pre-written protocol that makes the switch psychologically executable in the first place. Knowing the exit condition reduces the activation energy to make the switch.

### G5 — The Switch Protocol
When G0–G4 are all green for 12 consecutive months:

1. Do NOT quit immediately. Give 3-month notice (if possible) to maintain income overlap.
2. During overlap: trade at full allocation. Prove nothing changed with salary removed.
3. Month 3: if G1-G4 still green → execute switch.
4. Month 6: first formal review against baseline metrics.

The overlap period is the final filter. Some traders discover that removing salary urgency changes their risk appetite in unexpected ways.

---

## Common Failure Modes

| Failure | Signal | Correction |
|---------|--------|------------|
| Switch too early | G0 has < 200 OOS trades | Wait. No shortcut. |
| Undercount capital needed | 1.5× multiplier skipped | Recalculate. Benefits are real money. |
| Trading + living capital mixed | Same brokerage account | Separate structurally, immediately. |
| No return trigger defined | "I'll know when to stop" | Pre-write it now. |

---

## Edward's Actual Threshold (2026 calibration)

Per MD-26 and personal baseline:
- Monthly baseline salary equivalent: ~$4,500 (after tax)
- Switch threshold: $6,750/month = $81,000/year
- Required capital at 25% annual target: $324,000 allocated
- Living reserve: $40,500 (6 months)
- **Total capital gate: ~$365,000**

G0 status: paper-live validated (dual_ma, BTC). OOS trade count: accumulating.
G2 status: month 1 of 12.

Estimated switch eligibility: earliest 2027 Q1 at current trajectory.
