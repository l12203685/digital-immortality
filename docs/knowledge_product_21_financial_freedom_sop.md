# SOP #21 — Financial Freedom Tier Framework

> Operationalizes MD-166 (財務自由三層框架), MD-158 (槓鈴策略=穩健大部位+爆炸小部位), MD-154 (槓桿借貸三問清單), MD-168 (停損具體算法反推進場點), MD-139 (一致性缺失=隱性濾網未明言)
> Goal: convert abstract "financial freedom" into a concrete, tiered decision system with hard thresholds

---

## The Core Principle

**"Financial freedom" is not a destination. It is a cascade of three regime-changes, each with a different set of rules.**

Most people conflate all three tiers into one fuzzy goal ("I want to be rich"). This makes every decision feel urgent and nothing feel achievable. The fix: name each tier explicitly, calculate its threshold precisely, and operate under its specific rule set — not the rules of the tier above.

---

## The Three Tiers

### Tier 0 — Defensive Base (存活線)

**Definition:** Monthly passive income ≥ minimum operating costs (rent + food + health insurance + minimum debt service).

**Threshold formula:**
```
Tier 0 capital = (monthly_costs × 12) / safe_withdrawal_rate
```
Default safe withdrawal rate: 3.5% (conservative, 30-year horizon).

**Behavioral rule set:**
- Primary job: protect capital, not grow it
- All new income above minimum costs → allocated to Tier 1 build
- No leverage on Tier 0 assets (barbell: this is the "safe" bucket, MD-158)
- Tier 0 assets: index funds, short-duration bonds, cash equivalents

**You are here until Tier 0 is funded.**

---

### Tier 1 — Operational Freedom (自由線)

**Definition:** Monthly passive income ≥ current lifestyle costs (including discretionary spending, travel, learning budget).

**Threshold formula:**
```
Tier 1 capital = (annual_lifestyle_spend) / safe_withdrawal_rate
```

**Behavioral rule set:**
- Employment becomes optional (but not necessarily dropped — use for optionality and skill compounding)
- Active trading / strategy income allocated to Tier 2 build
- Leverage allowed only on the "explosive" bucket: max 20% of total capital (MD-158)
- Kill condition: if drawdown on leveraged bucket exceeds 50% → liquidate, rebuild from scratch before re-entering
- Decision prompt: "Would I do this job for free? If yes, continue. If no, renegotiate or exit."

---

### Tier 2 — Anti-Fragile Compound (複利線)

**Definition:** Net worth doubles every 7–10 years passively. You can absorb a 50% drawdown and recover within 3 years.

**Threshold formula:**
```
Tier 2 = Tier 1 capital × 3
(3x buffer absorbs sequence-of-returns risk and a full market crash)
```

**Behavioral rule set:**
- Lifestyle is fixed at Tier 1 level (do not inflate with Tier 2 gains)
- All surplus compounds into diversified growth assets
- Trading system runs at maximum size with full kill conditions active
- Annual audit: rebalance barbell back to 80/20 (safe/explosive)

---

## The 5-Gate Decision Protocol

Before any major capital allocation decision, run these gates:

### G0 — Locate Yourself

State which tier you are currently in.

> "I am in Tier 0 funding mode. My defensive capital is 40% funded."

If you don't know your current tier, you cannot apply the right rule set. Stop here and calculate.

### G1 — Apply Tier Rule Set

Each tier has different rules for leverage, risk, and employment (see above). Do not apply Tier 2 rules while in Tier 0 — this is the most common mistake.

> Tier 0: NO leverage on base capital.  
> Tier 1: Leverage only on explosive bucket (≤20% of total).  
> Tier 2: Full system operation.

### G2 — Run Leverage Borrowing Checklist (MD-154)

Before taking any leverage position, answer three questions:

1. **What is the worst-case cost if this position goes to zero?** (Answer must be a specific dollar amount, not "a lot".)
2. **Is that loss amount less than 10% of current Tier N threshold?** If no → do not proceed.
3. **Is the loan/leverage cost already modeled into the expected return?** (Friction first, MD-107.)

### G3 — Calculate Tier Progression Rate

> δ_tier = (current_capital / tier_threshold) − (capital_prior_period / tier_threshold)

You need positive δ for the current tier. If δ ≤ 0 for two consecutive periods, diagnose before continuing (spending leak? strategy underperformance? income plateau?).

### G4 — Barbell Integrity Check (MD-158)

At any tier, the structural rule is:
- **80%+ of capital in stable, durable assets** (survives a 50% equity crash without requiring liquidation)
- **≤20% in high-volatility, explosive assets** (trading capital, single-name equity, crypto)

If barbell ratio drifts outside 70/30 → rebalance before next deployment.

---

## Common Failure Modes

| Mistake | Pattern | Fix |
|---------|---------|-----|
| Tier inflation | "I can afford this, I'm at 80% of Tier 1" | Lock lifestyle costs at current level until tier fully funded |
| Leverage before Tier 0 | Taking margin loans while base is unfunded | Complete G2 checklist — cost floors it |
| Conflating tiers | "I have $500k so I'm free" | Calculate Tier 1 threshold explicitly; number may be $1.2M |
| Ignoring δ | Capital growing but too slowly to reach tier | Run G3 each quarter; if δ stagnates, change income mix |
| Emotional withdrawal | Market drops 30%, pulls from Tier 2 growth assets | Barbell: if 80% is intact, the drop is noise |

---

## Self-Test

**Scenario:** Your current net worth is $320,000. Monthly expenses: $3,500. You have a trading strategy generating avg +$800/month. You are considering quitting your job.

Apply the protocol:

1. **G0:** Tier 1 threshold = ($3,500 × 12) / 0.035 = $1,200,000. You are at 27% of Tier 1. You are in Tier 0 funding mode.
2. **G1:** Tier 0 rules apply. Employment is not optional yet. Trading income → Tier 1 acceleration.
3. **G2:** No new leverage. Base capital must grow, not be risked.
4. **G3:** At +$800/month net savings toward Tier 1: time to Tier 1 ≈ ($1,200,000 − $320,000) / ($800 × 12) ≈ 91 years at current rate. **This is the real number.** The decision is now obvious: job is not optional; income growth is the variable to change.
5. **Verdict:** Do not quit. Increase active income or trading size (within kill conditions) to accelerate δ.

---

## Connections to Other SOPs

- SOP #01 (Strategy Development): your trading system is the Tier 1→Tier 2 engine
- SOP #08 (Capital Structure): the barbell in G4 maps directly to the three-bucket isolation
- SOP #14 (Full-Time Switch Threshold): operationalizes the Tier 1 employment decision
- SOP #18 (Inaction Bias): when Tier 0 is funded, the bias-toward-inaction rule kicks in fully

---

*Backing principles: MD-166 (財務自由三層框架) / MD-158 (槓鈴=穩健+爆炸) / MD-154 (槓桿借貸三問) / MD-107 (工具成本先回收再進攻) / MD-168 (停損反推進場)*
