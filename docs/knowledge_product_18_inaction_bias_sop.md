# SOP #18 — Bias Toward Inaction: The Idle Capital Protocol

> Operationalizes Kernel 5: "Bias toward inaction — 沒有 edge 就不動。但不動 ≠ 不思考"
> Backing MDs: MD-96 / MD-108 / MD-326 / MD-141 / MD-112 / MD-104

---

## Core Principle

Most traders lose money by trading too much, not too little.
Idle capital is not dead capital — it is preserved optionality.
The protocol forces explicit justification for action. Absence of justification = stay idle.

**Default state: IDLE**
You must earn the right to trade. Not the other way around.

---

## Protocol Gates (Sequential)

### G0 — Name the Edge (Pre-condition)
**Question:** Can you name the specific, structural reason this trade has positive EV?

- Structural edge: market mechanism that persists (liquidity gaps, regime mismatch, institutional flow)
- Temporal edge: time-limited window before adoption (MD-141: public signals decay once adoption ≥50%)
- Interpretive edge: you see information others misread (MD-142: thinking level L+1 required)

**Rules:**
- If you cannot name the edge in one sentence → IDLE
- "I think it will go up" is not an edge
- "CT consensus is bullish + funding is extreme + OI at ATH = crowd overextended → structural contrarian edge" IS an edge

**Outcome:** Named edge identified → proceed to G1 | Unnamed → IDLE

---

### G1 — Asymmetry Check
**Question:** Is the reward/risk asymmetry ≥ 2.0?

**Formula:**
```
asymmetry = expected_move_to_target / distance_to_stop
```

- asymmetry ≥ 2.0 → proceed
- asymmetry 1.0–2.0 → REDUCE SIZE 50%, require G2+G3 both pass
- asymmetry < 1.0 → IDLE regardless of conviction

**Reference:** MD-104 (Population exploit asymmetry gate), MD-298 (river exploit asymmetry), MD-96 (kill condition pre-write)

**Outcome:** Asymmetry ≥ 2.0 → proceed to G2 | Below → IDLE or reduced

---

### G2 — Friction Cost Pre-Calculation
**Question:** Have you modeled all friction before entry?

**Checklist:**
- [ ] Spread cost estimated
- [ ] Slippage estimated (especially for size >0.5% ADV)
- [ ] Funding rate cost if holding overnight
- [ ] Tax/fee drag if high turnover
- [ ] Execution timing risk (illiquid hours)

**Rules:**
- If net EV after friction < 1.5× risk → IDLE
- "I'll figure it out after" = IDLE (MD-326: friction cost must be pre-modeled, not post-rationalized)

**Outcome:** Net EV ≥ 1.5× after friction → proceed to G3 | Below → IDLE

---

### G3 — Regime Alignment
**Question:** Does the strategy match the current regime?

- Trend strategy in trending regime → ALIGNED
- Mean-reversion strategy in trending regime → MISALIGNED → IDLE
- Any strategy in UNDEFINED regime → 50% size maximum

**Reference:** MD-107 (regime detection gates strategy routing), MD-112 (strategy fails = first check regime change)

**Rules:**
- MISALIGNED → IDLE, no exceptions
- UNDEFINED regime + weak edge → IDLE
- UNDEFINED regime + strong edge (G0+G1+G2 all strong) → 50% size maximum

**Outcome:** ALIGNED → proceed to G4 | MISALIGNED → IDLE

---

### G4 — Inaction Opportunity Cost
**Final gate — bias check:**

Before executing, ask: "What am I losing by NOT trading?"

- If answer is "nothing concrete" → IDLE is correct
- If answer is "a named, time-limited structural edge expires" → EXECUTE at pre-calculated size
- If answer is "fear of missing out / impatience / boredom" → IDLE (these are not costs, they are noise)

**Default rule:** When in doubt between IDLE and EXECUTE → IDLE
**Overrule condition:** All 4 prior gates passed AND edge has explicit time decay → EXECUTE

---

## Self-Test Scenario

**Situation:** BTC ranging sideways for 3 days. You feel urge to trade. Dual-MA signal = FLAT.

- G0: Name the edge → "I'm bored and BTC might break out" → UNNAMED → **IDLE**
- Result: IDLE is correct. No edge = no trade.

---

**Situation:** BTC at $85k. CT 70% bearish. Funding negative. OI declining. Trend_strength = 0.08 (trending). Dual-MA = LONG signal.

- G0: Named edge → structural crowd-fade + regime-aligned momentum → NAMED ✓
- G1: Target $88k, stop $83k → asymmetry = 3/2 = 1.5 → REDUCED SIZE (50%)
- G2: Friction: 0.04% fee × 2 = $68 on $85k position → net EV = +$1,432 vs -$1,068 after friction → 1.34× ✓ (marginal)
- G3: Trending regime → DualMA ALIGNED ✓
- G4: Edge is regime-aligned momentum with crowd-fade overlay → not FOMO, is structural → EXECUTE at 50% size
- Result: **CONDITIONAL GO — 50% size**

---

## Summary

| Gate | Question | Pass Condition | Fail Action |
|------|----------|----------------|-------------|
| G0 | Name the edge | One-sentence structural reason | IDLE |
| G1 | Asymmetry ≥ 2.0 | reward/risk ratio | IDLE or 50% size |
| G2 | Friction pre-modeled | Net EV ≥ 1.5× after costs | IDLE |
| G3 | Regime aligned | Strategy matches regime | IDLE |
| G4 | Real opportunity cost | Time-limited structural edge | IDLE (default) |

**Default state: IDLE. Earn the right to trade.**

---

*Backing MDs: MD-96 (kill condition pre-write) / MD-108 (regime-subset Sharpe) / MD-326 (friction cost pre-model) / MD-141 (thinking level delta) / MD-112 (regime change = first diagnosis) / MD-104 (population exploit asymmetry)*
