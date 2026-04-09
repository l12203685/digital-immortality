# SOP #36 — Barbell Life Strategy: Asymmetric Optionality Protocol

**Domain:** 6. 存活冗餘 (Survival Redundancy / Anti-Fragile)
**Date:** 2026-04-09 UTC
**DNA Anchors:** MD-157, MD-159, MD-183, MD-181, MD-307, MD-190, MD-151

---

## Introduction

Most people run a barbell backwards: they stake existential risk on their income source (the thing that must not fail) and then cap upside on their side projects (the things designed to fail small and win big). The result is catastrophic fragility on the left tail and capped optionality on the right — the worst of both structures. This SOP formalizes the correct barbell: a large STABLE position that cannot be existentially threatened, paired with an EXPLOSIVE position where full 100% loss is acceptable and upside is unlimited. The gate structure forces classification before evaluation — because mixing the two pools is the primary failure mode.

---

## Gate G0 — Domain Classification

**Trigger:** Any life decision being evaluated.

**Action:** Before any analysis, classify the decision domain as either STABLE or EXPLOSIVE.

- **STABLE:** income source, primary housing, core health maintenance, primary relationships
- **EXPLOSIVE:** side projects, new skills, experimental ventures, speculative investments, career pivots

**Rule (MD-157):** Define what you gain and what you lose *before* evaluating the bet. A STABLE element must survive adverse scenarios. An EXPLOSIVE element is sized to lose fully without threatening the STABLE floor.

**Pass criteria:** Decision is unambiguously assigned to one category. If classification is uncertain, treat it as EXPLOSIVE and re-run from G2.

**Hard rule:** STABLE capital never funds EXPLOSIVE bets. EXPLOSIVE gains may replenish STABLE reserves. Never reverse this flow.

---

## Gate G1 — Downside Cap

**Trigger:** Decision is classified at G0.

**Action — STABLE domain:** Identify the maximum acceptable loss. If the loss scenario is existential (wipes out 18-month expense coverage, eliminates primary income, forces liquidation of primary housing), the position FAILS the barbell. It cannot be leveraged, concentrated, or speculated upon.

**Action — EXPLOSIVE domain:** Explicitly accept 100% loss of the allocated position. Size the bet so that full loss is uncomfortable but not threatening. Write the loss number down. If you cannot accept that number, reduce size until you can.

**Rule (MD-183):** The barbell structure is: preserve principal, gamble with interest only. STABLE = principal. EXPLOSIVE = interest. You do not gamble principal.

**Pass criteria:**
- STABLE: max loss scenario is non-existential
- EXPLOSIVE: full-loss amount is written, accepted, and sized within the EXPLOSIVE allocation budget

---

## Gate G2 — 10-Year Survival Check

**Trigger:** STABLE element identified.

**Action:** Ask: "Will this STABLE element still exist and remain accessible in 10 years?" Apply this to income sources, skills, platforms, companies, and relationships.

**Rule (MD-307):** Survival certainty precedes return rate. A STABLE element that is likely to be disrupted, regulated out, or decayed in 10 years is not actually STABLE. It is a slow-moving EXPLOSIVE bet wearing STABLE clothing.

**Re-classification logic:**
- High confidence it survives 10 years → confirmed STABLE
- Moderate uncertainty → reclassify as EXPLOSIVE; find or build a genuine STABLE element
- Near certainty it will not survive → reclassify as EXPLOSIVE immediately

**Pass criteria:** At least one STABLE element survives the 10-year check with high confidence. If none do, the entire structure is misclassified and the barbell does not exist yet.

---

## Gate G3 — EV Independence Test

**Trigger:** Any EXPLOSIVE bet being evaluated.

**Action:** Test whether this bet has positive expected value (EV) independently — i.e., regardless of whether any other bet succeeds or fails.

**Rule (MD-159):** Trial position and scaling position must each have independent positive EV. A bet that is only positive if another bet also wins is a correlation trap. Two bets that can only both win or both lose are not two bets — they are one bet with double exposure.

**Correlation trap check:**
- "If X succeeds, then Y will succeed" → Y is not independent. Do not size both simultaneously.
- "Y is good regardless of X" → Y passes independence test.

**Pass criteria:** The EXPLOSIVE bet has a positive EV case that does not require any other concurrent bet to succeed first.

**If test fails:** Break the bets into sequential stages. Complete stage one before sizing stage two.

---

## Gate G4 — Optionality Preservation

**Trigger:** Any decision that is irreversible or semi-irreversible.

**Action:** Assess whether the decision expands or contracts future options.

**Expanding optionality:** gaining a new skill, building a new income stream, establishing a new relationship, acquiring an asset — all increase future decision space.

**Contracting optionality:** leaving a career, closing a relationship, selling an asset, committing to a geography — all reduce future decision space.

**Rule (MD-190):** Contracting decisions require a compensating premium. The premium must be explicit and measurable. If no premium can be identified or quantified, default to preserving optionality.

**Premium calculation:**
- What is the expected gain from the contracting decision?
- What is the option value of the path being closed?
- Premium required = (option value of closed path) × (1 + uncertainty factor)
- If expected gain < required premium: preserve optionality, do not contract.

**Pass criteria:** Either the decision is optionality-expanding (no premium required), or the expected gain explicitly exceeds the required premium on the closed path.

---

## Gate G5 — Exit Pre-Commitment

**Trigger:** Entering any EXPLOSIVE position.

**Action:** Before entry, write three exit conditions:
1. **Time limit:** "If X months pass without Y signal, I exit."
2. **Capital limit:** "If I lose Z, I exit regardless of thesis."
3. **Signal threshold:** "If I observe W, I exit because the original thesis is invalidated."

**Rule (MD-151):** Binary exit architecture — exit conditions are written before entry. They are not renegotiated after entry when loss aversion and sunk cost bias are active. The exit is a standing order, not a decision made under pressure.

**Kill signals that override all three:**
- STABLE element drops below 18-month expense coverage → exit ALL EXPLOSIVE positions immediately
- EXPLOSIVE bet EV turns negative after 3 data points → exit, do not average down
- Cannot write exit conditions → do not enter the position

**Pass criteria:** Three written exit conditions exist before capital is deployed. All three are specific, measurable, and time-bounded.

---

## Self-Test Scenario: Leaving a Stable Job to Trade Full-Time

**Setup:** You have a stable job. You have been profitable trading part-time for 18 months. You are considering leaving employment to trade full-time.

**G0 — Classification:**
- Job = STABLE domain
- Trading = EXPLOSIVE domain
- These cannot run at full leverage simultaneously. Running trading at "full-time" intensity while funded by zero income is not a barbell — it is a single concentrated EXPLOSIVE bet with existential downside.
- Decision: the barbell requires a STABLE floor *before* you scale the EXPLOSIVE position.

**G1 — Downside cap:**
- Full-time trading with no income = existential risk if trading fails. This fails the barbell structure.
- Pass condition: 24-month cash runway (STABLE floor) must exist before exit from employment.
- If cash runway does not exist: trading remains part-time until the STABLE floor is established.

**G2 — 10-year survival check:**
- Will your trading edge survive 10 years? → Uncertain. Edges decay; market structure shifts.
- Classification confirmed: trading = EXPLOSIVE. It is not a STABLE income replacement.
- Implication: you need a STABLE element that is not trading. Cash runway, part-time consulting, or a return-to-employment option all qualify.

**G3 — EV independence test:**
- Is full-time trading positively valued independently? → Only if it outperforms part-time trading by more than the opportunity cost of leaving employment.
- If the thesis is "I need more hours to scale the edge," test whether more hours have historically produced more edge in your system. If not, the scaling bet fails independence.

**G4 — Optionality preservation:**
- Leaving employment contracts significant optionality: re-entry premium, career gap, network atrophy.
- Required compensation: expected trading income must exceed (job income × re-entry premium factor). A conservative estimate is 1.5×–2× job income to justify the closed path.
- If trading income projection does not exceed that threshold: remain employed, trade part-time, compound the STABLE floor.

**G5 — Exit pre-commitment:**
- Write before exit: "If I have not replaced 80% of prior salary within 12 months of going full-time, I return to employment."
- Capital limit: "If my trading account drops 30% from entry-month high, I freeze new positions and re-evaluate."
- Signal threshold: "If my edge shows negative expectancy across 50 trades, the thesis is invalidated and I exit the experiment."
- With all three written: entry is conditionally permitted — *and only if* the 24-month cash runway exists (G1 pass).

**Verdict:** Do not leave employment until: (1) 24-month cash runway exists, (2) trading income projection clears 1.5× job income, (3) all three exit conditions are written and accepted. Until all three: continue barbell, trade part-time, build the STABLE floor.

---

## Kill Conditions

The following conditions trigger immediate action without further deliberation:

| Condition | Action |
|-----------|--------|
| STABLE element drops below 18-month expense coverage | Exit ALL EXPLOSIVE positions immediately. Rebuild floor before re-entry. |
| EXPLOSIVE bet EV turns negative after 3 data points | Exit. Do not average down. The thesis failed; adding capital extends the loss, not the edge. |
| Cannot write specific exit conditions before entry | Do not enter. Inability to write exits means inability to define the thesis. No thesis = no bet. |
| STABLE element fails 10-year survival check after initial pass | Re-classify and rebuild STABLE position. Freeze EXPLOSIVE scaling until new STABLE floor is confirmed. |
| Two EXPLOSIVE bets found to be correlated (fail G3 independence) | Reduce combined position to the size of one independent bet. You have one bet, not two. |

---

## Summary: The Barbell Decision Checklist

```
G0: Is this STABLE or EXPLOSIVE? Classify before evaluating.
G1: What is the max loss? STABLE: non-existential. EXPLOSIVE: accept 100%.
G2: Does the STABLE element survive 10 years? If uncertain: reclassify.
G3: Does this EXPLOSIVE bet have positive EV independently? If not: sequence, don't combine.
G4: Does this expand or contract options? Contracting requires explicit premium.
G5: Write 3 exit conditions before entry. Time, capital, signal.
```

If any gate fails: do not proceed. Fix the gate, then re-evaluate.

---

*Series: SOP #01–#36 | Domain: 存活冗餘*
