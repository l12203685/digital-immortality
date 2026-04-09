# SOP #08 — Capital Structure & Barbell Framework

> From Edward Lin's micro-decision archive. Backing MDs: MD-18, MD-154, MD-158, MD-159, MD-166.

---

## Core Principle

Capital allocation has a correct sequence: structure first, leverage last.
Emotions don't determine position size — math does.

---

## G0 — Three-Bucket Isolation (MD-18)

Split capital into **three independent buckets**. Each bucket has its own kill condition. One bucket blowing up must NOT infect the others.

| Bucket | Examples | Decision scope |
|--------|----------|----------------|
| A — Stable | Taiwan ETF, US ETF | Long-term hold, quarterly review |
| B — Growth | Active trading account | Weekly review, kill conditions active |
| C — Speculative | Crypto, options, high-volatility | Hard floor per bucket, 10–30% of total |

**Fail condition:** Moving capital between buckets to "rescue" a bucket = structural collapse. Hard stop per bucket is the rule.

---

## G1 — Barbell Structure (MD-158)

A barbell requires **both ends**. Middle-risk assets destroy the structure.

```
LEFT END (70–90%)          RIGHT END (10–30%)
Stable, low volatility     High volatility, uncapped upside
ETF / fixed income         Options / emerging positions
Max loss = capped          Max loss = principal → max gain = ∞
```

**Self-test:**
- Is your "speculative" position actually medium-risk? → Not a barbell, remove it or move to right end.
- Do you have a large middle? → Restructure: push left end lower-vol, push right end genuinely high-upside.

---

## G2 — Leverage Borrowing Checklist (MD-154)

Before adding any leverage (margin, pledging, borrowing), answer all three questions in writing:

1. **Margin call trigger:** At what price/drawdown does the broker call? What is my response plan?
2. **Re-investment eligibility:** Can borrowed capital be re-deployed? Under what conditions?
3. **Interest cash flow:** Where does interest go when borrowing cost is paid? Which bucket absorbs it?

**If any answer is "I'm not sure" → do NOT open leveraged position.**
Leverage without written answers = structural incompleteness.

---

## G3 — Trial vs Full Position Rule (MD-159)

Every position component must have **independent positive EV**.

```
Trial position:  profitable on its own (entry logic is valid)
Full position:   profitable on its own (add-point is a valid entry)
```

**Violations:**
- "Trial loses but averaging down recovers" → entry point is broken, fix it.
- "I'll scale in to lower my cost" = averaging down = buying failing positions.
- Correct: trial confirms direction → add at a new valid entry point with its own EV.

---

## G4 — Financial Freedom Target Calibration (MD-166)

Before deciding how aggressively to trade or invest, know which tier you are targeting:

| Tier | Definition | How to measure |
|------|-----------|----------------|
| Financial Security | Passive income ≥ necessary expenses | Rent + food + insurance + loan payments |
| Financial Freedom | Passive income ≥ necessary + discretionary | Add travel, entertainment, lifestyle |
| Financial Abundance | Freedom tier + significant surplus | Freedom number + meaningful remainder |

**Operating rule:** Choose which tier you are attacking *right now*. Strategy aggression (leverage, position size) should match the gap to current tier, not to abundance fantasy.

---

## Sequential Checklist

```
[ ] G0 — Three buckets defined with independent kill conditions
[ ] G1 — Barbell structure confirmed: left end low-vol, right end uncapped upside, no large middle
[ ] G2 — Leverage checklist: margin trigger, re-investment eligibility, interest allocation (all written)
[ ] G3 — Every position component has independent positive EV
[ ] G4 — Target financial freedom tier identified; aggression calibrated to gap
```

---

## Self-Test Scenario

**Situation:** You have $100k. You want to add leverage to a crypto position because you expect a breakout.

- G0: Is crypto in the correct bucket (C)? Is bucket C's floor defined?
- G1: Is this right-end exposure, or are you adding to your "safe" ETF bucket?
- G2: Answer all three leverage questions in writing before opening the position.
- G3: Does the trial entry itself have edge? Or are you planning to average down if it drops?
- G4: Are you at Financial Security tier or Financial Freedom tier? Does your leverage level reflect that?

**Stop condition:** Any G2 answer is blank → position stays flat until written.

---

*Series: SOP #01 Strategy Development · #02 Portfolio Construction · #03 Execution & Sizing · #04 Strategy Kill · #05 Career & Salary · #06 Game Theory · #07 Regime Detection · **#08 Capital Structure***
