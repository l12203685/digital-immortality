# SOP #56 — Financial Capital & FIRE Protocol

**Timestamp**: 2026-04-09T UTC (Cycle 217)
**Domain**: 7 (財務/Financial Capital)
**Backing MDs**: MD-89, MD-12, MD-144, MD-48, MD-67
**Series**: Knowledge Product #56 of the Digital Immortality SOP series

---

## What problem this solves

Financial capital determines how long you can survive without income and how quickly you reach independence. Most people track expenses. Almost no one tracks their **FIRE trajectory** — the derivative of net worth relative to the independence threshold. Without a derivative signal, you optimize for the wrong thing: cutting lattes instead of scaling income by 10×.

This SOP converts financial capital from a static balance sheet into a live derivative system.

---

## 5-Gate Framework

### G0: Monthly Financial Audit — 3 signals
Run on the 1st of each month (15 min).

**Signal 1 — Net Worth Delta (ΔNW/month)**
- Measure: end-of-month net worth minus previous month
- Healthy: positive slope, accelerating
- Kill: 3 consecutive negative months → G5

**Signal 2 — FIRE Rate (% of FIRE target achieved)**
- Measure: current net worth ÷ FIRE target × 100
- Track slope not level
- Reference: FIRE target = annual expenses × 25 (4% withdrawal rule baseline)

**Signal 3 — Runway**
- Measure: liquid assets ÷ monthly burn rate = months of survival
- Minimum: 6 months at all times
- Kill: runway < 6 months → G5

---

### G1: Derivative Scan — trajectory not balance
Run alongside G0. Ask:

- ΔNetWorth/month: accelerating or decelerating?
- ΔIncome sources: new stream added this quarter?
- ΔFIRE rate: on track to hit independence by target date?
- ΔRunway: shrinking or stable?

Regime signal:
- Accelerating ΔNW + stable runway → continue current strategy
- Decelerating ΔNW → identify cause: income drop, expense creep, or opportunity cost
- ΔNW negative + runway shrinking → skip to G5

---

### G2: Non-Negotiable Financial Budget
These run regardless of regime. No negotiation on G2 items.

1. **Savings floor**: minimum 20% of gross income saved. Lifestyle creep is the primary enemy — block it structurally, not by willpower.
2. **Asset allocation review**: quarterly check that asset mix matches current risk tolerance and time horizon. No more than 90 days without a review.
3. **Income diversification**: at least 2 income streams active. Single-income dependency = single point of failure. Trading system counts as stream #2 once profitable.
4. **Expense audit**: monthly review of recurring charges. Kill any subscription not used in 30 days. Friction costs compound.
5. **No lifestyle upgrades during runway < 12 months**: constraint is absolute. Upgrade requests defer until runway re-established.

---

### G3: Quarterly FIRE Leverage Scan
Each quarter: identify ONE financial variable with highest derivative impact.

Protocol:
- List top 3 candidates: income increase, expense cut, asset reallocation, tax optimization
- Estimate ΔNW impact per year for each
- Select highest expected value
- Run 90-day trial (isolated single change)
- If ΔFIRE rate ≥ +2% improvement → write to permanent strategy; else discard

Examples of high-leverage changes:
- Tax-advantaged account maximization (asymmetric: same income, lower cost)
- Income source scaling (e.g., content → Gumroad → passive income)
- Trading system activation: $100 → $1,000 → $10,000 as confidence builds (kill conditions enforced)

---

### G4: Weekly Review (Sundays, 10 min)
Lightweight check between monthly G0 audits.

Track Y/N:
- [ ] Savings rate met this week?
- [ ] Any unplanned major expense?
- [ ] Any new income signal detected?
- [ ] Trading system status: any kill condition triggered?

Classify deviations:
- Behavioral (decision error)
- Structural (system design flaw)
- External (market, employer, macro)

Behavioral → modify behavior. Structural → modify system. External → accept and adapt, do not fight.

---

### G5: Financial Emergency
Trigger: runway < 6 months OR 3 consecutive months of negative ΔNW.

**Immediate actions (48 hours):**
1. Freeze all discretionary spending
2. Audit all income sources — anything with positive EV that can be activated?
3. Activate income-first mode: trading system → content → freelance. Priority = cash flow speed.
4. No L3 strategy edits until G0 returns to baseline (runway ≥ 6 months × 2 consecutive months)

**Root cause analysis:**
- If behavioral: identify specific decision that caused deviation → write to DNA
- If structural: fix the system (insufficient savings automation, wrong asset mix)
- If external: scenario plan for 3 durations: 3-month shock, 12-month shock, permanent shift

**Rule**: financial emergencies are highest-derivative events. Everything else pauses. This is the same logic as G5 in health/environment SOPs — system survival precedes system optimization.

---

## Three-Layer Integration

| Layer | FIRE Component | Frequency |
|-------|---------------|-----------|
| **L1 Execute** | Monthly G0 audit + G2 non-negotiables + G4 weekly check | Continuous |
| **L2 Evaluate** | G1 derivative scan + G4 cause classification | Monthly + weekly |
| **L3 Evolve** | G3 quarterly leverage scan → write new strategy to DNA | Quarterly |

Execute without L2+L3 = accumulating money without improving the system. L3 edits during G5 = optimization while the building burns. Gate L3 on G0 baseline.

---

## Metrics

| Metric | Target | Kill |
|--------|--------|------|
| ΔNW/month | Positive, accelerating | Negative × 3 |
| Runway | ≥ 12 months | < 6 months |
| Savings rate | ≥ 20% gross | < 10% |
| FIRE rate slope | Increasing | Flat >6 months |
| Income streams | ≥ 2 | 1 only |

---

## Connection to Trading System

Branch 1.1 (paper-live) is the embryonic second income stream. Activation path:
1. Paper-live confidence (SHORT signal 81 consecutive ticks, P&L +$0.937) ✓
2. Mainnet $100 (pending API keys)
3. Kill conditions enforced: MDD<10%, WR≥35%, PF≥0.85
4. Scale: $100 → $1,000 → $10,000 as drawdown history builds

Trading system profitability before 2026-07-07 = FIRE rate accelerator + proof of self-sustainability.

---

## DNA Anchors

- **MD-89**: Derivative-first thinking — track rate of change, not level
- **MD-12**: Non-negotiable constraints (G2 items)
- **MD-144**: Compounding effects — the FIRE thesis depends on exponential, not linear accumulation
- **MD-48**: Risk management — kill conditions apply to financial systems as to trading strategies
- **MD-67**: Survival first — financial G5 protocol mirrors the core survival rule

---

## Anti-Patterns

| Pattern | Why it fails |
|---------|-------------|
| Tracking expenses only | Misses income derivative — same savings rate at higher income = faster FIRE |
| Optimizing within one domain | Tax optimization alone is a 10× smaller lever than income scaling |
| Lifestyle creep during acceleration | Reduces savings rate precisely when compounding most benefits from it |
| G5 avoidance | Ignoring kill signals until runway hits zero = no recovery time |
| Over-optimization before baseline | Rebalancing portfolio when runway is 2 months is wrong priority order |
