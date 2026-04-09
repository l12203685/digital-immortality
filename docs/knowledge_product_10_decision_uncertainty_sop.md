# SOP #10 — Decision-Making Under Uncertainty
## Information Asymmetry Edge Framework

**Version:** 1.0 | **Author:** Edward Lin | **Backing MDs:** MD-141, MD-140, MD-1, MD-298, MD-96, MD-141, MD-326

---

## Purpose

Most decisions fail not from lack of information but from misreading *what kind* of information matters. This SOP operationalizes the 5 Edward kernel principles into a 5-gate decision checklist that works in any domain: trading, career, negotiation, investment.

---

## The 5-Gate Checklist

### G0 — Read Rate of Change, Not Level
**Kernel 1: 看導數不看水平**

- Ask: "What is the *trend* of this variable, not its current value?"
- Ignore absolute levels; map the first derivative (speed) and second derivative (acceleration)
- **Signal:** Acceleration > deceleration > flat level (flat level = stale information)
- MD-1: Decisions anchored to level rather than direction contain no edge
- Fail condition: If your analysis only describes *where* things are, restart — describe *where* they are going and how fast

### G1 — Map Your Information Asymmetry
**Kernel 2: 資訊不對稱決定行動方向**

- Ask: "What do I know that most participants do not, or what do I know *earlier*?"
- MD-141: Thinking one level above the opponent = the only durable edge
- MD-140: Price = sufficient statistic of all public information → public data has zero edge; act only on *structural* or *temporal* asymmetry
- Classify your information:
  - **Structural edge** — access to data others cannot get (skin-in-the-game knowledge, MD-135)
  - **Temporal edge** — same data, read faster (regime shift detection, MD-103)
  - **Interpretive edge** — same data, better model (population behavior, MD-298)
- Fail condition: If you cannot name your edge type, no position / no action

### G2 — Escalate to Meta-Strategy if Object-Level Is Stuck
**Kernel 3: Meta-strategy 管理 strategy**

- Ask: "Is this a problem with my strategy, or with my *choice* of strategy?"
- Object-level: individual trade/decision parameters
- Meta-level: the framework that selects which strategy to apply (regime detection, MD-107)
- MD-112: Strategy = first define what it makes money from AND what it loses to
- Rule: If object-level iteration > 3 cycles without improvement → escalate one level up
- Fail condition: Continuing to optimize within a broken framework

### G3 — Check Population Behavior for Contrarian EV
**Kernel 4: Population exploit**

- Ask: "What is the consensus action? Does exploiting the opposite have positive EV?"
- MD-298: Population river exploit = asymmetric payoff in both directions (fold-equity vs value)
- MD-104: Market has 3 states (TRENDING/MR/MIXED) — majority crowds into one; edge = reading the transition
- Process:
  1. Identify the modal population action (what are most people doing?)
  2. Calculate EV of the counter-action
  3. Apply only if EV > 0 AND you have an edge from G1 — contrarian without edge = noise
- Fail condition: Contrarian position with no structural reason for population error

### G4 — Default to Inaction Without Edge
**Kernel 5: Bias toward inaction**

- Ask: "If I do nothing, what is the cost?"
- No action = preserve optionality; action without edge = negative-EV by definition
- MD-96: Strategy management = failure definition written *before* entry — same logic: if you cannot define what would make you *wrong*, you do not understand the position
- MD-326: Calculate friction cost first — inaction is only free if you include opportunity cost correctly (MD-150)
- **Inaction ≠ no thinking.** Actively accumulate information while holding no position.
- Fail condition: Acting because "doing nothing feels wrong" — that is loss-aversion, not edge

---

## Self-Test Scenario

**Context:** BTC has been sideways for 3 weeks. Volume compressed. Most retail traders are calling for a breakout up. Your model shows SHORT signal for 30 consecutive ticks.

| Gate | Check | Result |
|------|-------|--------|
| G0 | Trend: volatility *declining* (compression), momentum *flat* → regime is ambiguous | ⚠️ No clear rate of change signal |
| G1 | Edge: 30-tick SHORT consistency from model (temporal edge) vs. public consensus (bullish) | ✅ Interpretive asymmetry present |
| G2 | Object strategy (dual_ma SHORT) running; regime-routing meta-layer says MR → check BollingerMR | ✅ Meta-strategy engaged |
| G3 | Population: majority bullish → contrarian = SHORT has positive EV if regime = MR | ✅ Contrarian with structural reason |
| G4 | Inaction cost: no position = 0; but 30-tick edge signal = cost of waiting is accumulated negative EV | ✅ Edge present → action justified |

**Decision:** Enter SHORT at $100 trial size; write kill condition before entry (MDD 10%, WR<35%).

---

## Kill Conditions for This SOP

- You cannot answer G1 (no edge identified) → ABORT
- G0 shows deceleration of your edge signal → reduce size 50%
- Population crowded to your side (not contra) → exit or hold, do not add

---

## Series Context

| # | SOP | Core Skill |
|---|-----|-----------|
| 01 | Strategy Development | Build + validate a strategy |
| 02 | Portfolio Construction | Combine strategies |
| 03 | Execution & Sizing | Real-time checklist |
| 04 | Strategy Kill Decision Tree | When to stop |
| 05 | Career & Salary | Negotiation |
| 06 | Game Theory Framework | Strategic interaction |
| 07 | Regime Detection | Market classification |
| 08 | Capital Structure | Money architecture |
| 09 | Risk & Drawdown Response | Protect capital |
| **10** | **Decision Under Uncertainty** | **Core kernel: 5 principles** |
