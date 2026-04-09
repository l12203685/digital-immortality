# SOP #05 — Career & Salary Decision Making

> **Source MDs**: MD-121, MD-128, MD-129, MD-163, MD-209, MD-210, MD-229, MD-303, MD-309, MD-311, MD-312, MD-327, MD-301, MD-302
> **Domain**: Career, Salary, Professional Path
> **Status**: COMPLETE — cycle 115 (2026-04-08T19:30Z)
> **Applies to**: Any career-direction, job-offer, salary-negotiation, or path-switching decision

---

## Overview

Career decisions have asymmetric outcomes: a bad path can cost 2–5 years; a good one compounds for decades. The failure mode is not "bad decisions" but **wrong sequencing** — anchoring on salary before mapping the path, or evaluating one offer before quantifying alternatives.

**MD-121 (五維框架=完整決策系統)**: Every career decision maps to five dimensions — financial, knowledge, optionality, reputational, and time. A decision that wins on salary but loses on optionality and knowledge may have negative total EV. This SOP sequences the gates so all five dimensions are captured before any commitment.

This SOP is irreversible-gate-ordered. Each gate must pass before the next opens.

---

## Gate Sequence

```
G0: Exploration or Execution?
  ↓ EXECUTION only
G1: Max-Loss Attribution Check
  ↓ PASS
G2: Salary Floor Written (pre-meeting)
  ↓ WRITTEN
G3: Org Type Diagnosis
  ↓ DIAGNOSED
G4: Compound Salary Viability Check
  ↓ VIABLE
G5: Parallel Offer EV Table
  ↓ TABLE BUILT
G6: Knowledge Domain Externality Added
  ↓ COMPLETE
→ DECISION
```

---

## G0 — Exploration vs. Execution Gate

**Trigger**: Any career-direction question ("should I pursue X?")

**Rule** (MD-327: 職涯探索=多軌同時開評估窗口):

- If still in **exploration phase**: open 4–6 parallel tracks simultaneously.
  - "I've researched X enough" is NOT a convergence signal.
  - Convergence signals: concrete offer, demonstrated performance advantage, genuine market pull.
  - Action: run validation moves (apply, contact, prototype) across 3–4 directions simultaneously.
- If in **execution phase** (real offer in hand): proceed to G1.

**Fail condition**: Premature convergence — choosing the most *familiar* path rather than the best-fit path.

---

## G1 — Max-Loss Attribution Check

**Input**: Candidate career path / job offer

**Rule** (MD-309: 職業路徑=最大損失歸屬分析):

Map the worst-case scenario for this path:
1. What is the maximum loss? (financial, reputational, time)
2. Who controls the stop-loss on this path — you or the org?
3. Is the max-loss bounded and predictable?

| Path Type | Max-Loss Controller | Risk Verdict |
|-----------|---------------------|--------------|
| Own capital at risk (trading, own business) | You | Tail risk quantifiable |
| Employee — org capital at risk | Org controls loss scale | Reputational/legal tail risk uncontrolled |
| Hybrid | Shared | Evaluate by % exposure |

**Decision rule**:
- Prefer paths where worst-case loss stays within self-controlled capital.
- If org-controlled: can you set your own exit condition (quit before loss exceeds X months sunk cost)?
- If no personal stop-loss is possible: discount path value by unquantified tail risk.

**Fail action**: If path has unbounded personal liability (e.g. co-signing with personal assets, unlimited liability partnership) → pass unless max-loss is explicitly capped and written.

---

## G2 — Salary Floor Written (Pre-Meeting)

**Trigger**: Any salary discussion, negotiation, or offer evaluation

**Rule** (MD-128: 薪資談判精算底線 / MD-209: 薪資底線=年薪精算+試用期機制書面化):

**Step 1 — Backtrack from take-home target** (MD-301: 薪資目標逆推=從稅後實領出發):
```
target_take_home (annual) → ÷ 0.75 (Taiwan tax+NHI estimate) = required_headline_salary
# Conservative: ÷ 0.75. High-tax jurisdiction: ÷ 0.70. Low-tax: ÷ 0.80
# Never start from headline salary — that number does not reach your account.
```

**Step 2 — Verify ceiling**:
- Query internal sources for the role's actual headline salary ceiling.
- If ceiling < required_headline_salary → path fails before negotiation starts.

**Step 3 — Write the floor** (must be on paper/doc before any negotiation meeting):
```
Floor = MAX(
  opportunity_cost_floor,     # what the best alternative pays
  market_percentile_floor,    # 50th–75th percentile for role/region
  minimum_acceptable_floor    # personal baseline: below this, walk
)
```

**Step 4 — Probation protection** (MD-209):
- If offer includes probation: write minimum terms → salary during probation, conversion conditions, written confirmation of role scope.

**MD-129: Written floor wins anchoring battles (對稱策略多空隱藏相依)**:
When both sides present anchors, the side with the written floor wins — because they cannot be moved by the other side's number. Verbal floors can be rationalised downward under social pressure. Written floors cannot. This is not a negotiation tactic; it is a structural advantage from pre-commitment.

**Decision rule**: Book the deal only if `offer ≥ floor`. Never negotiate without the floor written first. Anchor high as secondary tactic; written floor is primary.

**Fail action**: If floor is not yet written → do not enter the meeting. Floor first, meeting second.

---

## G3 — Org Type Diagnosis

**Input**: The organization offering or considering you

**Rule** (MD-303: 生產力在順從型組織歸組織):

Diagnose org type before deciding personal optimization strategy:

**Test**: Has this org ever responded to individual efficiency gains with:
- Pay increase, or
- Reduced workload, or
- Promoted the individual based on output?

| Org Type | Response to Efficiency Gain | Your Optimal Strategy |
|----------|----------------------------|-----------------------|
| **Meritocratic** | Gain → reward | Maximize output; build visible track record |
| **Compliant (顺从型)** | Gain → "do more" | Maintain acceptable minimum output; find exit |

**Decision rule**:
- In a confirmed compliant org: personal productivity optimization has negative EV. Channel excess capacity into skill-building for exit, not org benefit.
- In a meritocratic org: invest in visible, measurable output — it compounds.

**Fail action**: If org type unclear → assume compliant until proven otherwise. Do not optimize personal output without evidence of meritocratic response.

---

## G4 — Compound Salary Viability Check

**Input**: Target salary + timeline + current salary + promotion assumptions

**Rule** (MD-311: 薪資成長複合計算=升遷加幅×後續年增率):

**Formula**:
```
post_promotion_salary = current_salary × (1 + promotion_raise%)
remaining_gap = target_salary - post_promotion_salary
years_remaining = target_year - promotion_year
required_annual_increase% = (target / post_promotion) ^ (1/years_remaining) - 1
```

**Check**: Is `required_annual_increase%` achievable in this org?
- Query: what has the org's historical annual salary increase been for this role level?
- If `required_increase > historical_max_increase → path eliminated`. Do not wait; reroute.

**MD-163: Learning environment ceiling (學習環境=輸入端品質決定天花板)**:
- Beyond the salary arithmetic: evaluate the quality of the top 10% of peers in this org.
- The top 10% set the effective ceiling of what you can learn, become, and eventually earn.
- A role where top-10% peers earn at your target = ceiling is real and structural.
- A role where top-10% peers earn 3–5× your target = ceiling is not yet binding.
- Choose environments by peer quality; the salary compounds from that selection.

**Example**:
- Target: $1.2M take-home by age 30 (requires ~$1.5M headline)
- Current: $700K headline; promotion adds 20% → $840K
- Years remaining: 3
- Required annual: ($1.5M/$840K)^(1/3) - 1 = 21.3% per year
- Historical org max: 8–10% → **PATH ELIMINATED**

**Fail action**: If required rate > org's achievable rate → document elimination, pursue alternative path immediately (not "wait and see").

---

## G5 — Parallel Offer EV Table

**Input**: Current offer(s) + alternatives

**Rule** (MD-210: 平行offer=決策樹+機會成本精算):

**Never evaluate a single offer in isolation.** Build the full EV table before any response:

```
| Path | Prob(accept) | Expected_salary | Timeline | Risk | EV |
|------|-------------|----------------|----------|------|----|
| Offer A (current) | ... | ... | ... | ... | ... |
| Offer B (alternative) | ... | ... | ... | ... | ... |
| Stay (status quo) | ... | ... | ... | ... | ... |
| Defer 6 months | ... | ... | ... | ... | ... |
```

**Decision rule**:
- Do not accept Offer A until table is complete.
- If Offer A > all alternatives by EV margin > cost of delay → accept.
- If alternatives close or better → negotiate A or pursue B.

**MD-229: Cross-domain precedent check (職涯轉換=先找跨域成功先例)**:
- If any option in the EV table involves a domain switch, add a column: "Cross-domain success cases verified?"
- Before treating a domain switch as a real option, find 3+ verified cases of people who made the same switch and succeeded.
- No verified precedents → domain switch option is EXPLORATION-grade, not EXECUTION-grade. Exclude from EV table until precedents are found or the option becomes concrete.

**Fail action**: "This is the only offer I have" is an information failure, not a constraint. At minimum, estimate opportunity cost of the best alternative even if not formally in hand.

---

## G6 — Knowledge Domain Externality

**Input**: Role/path under consideration

**Rule** (MD-312: 金融領域價值=知識附加工具非薪資本身 / MD-302: 投資ROI評估=先換算年化%):

**MD-302**: Convert all knowledge ROI to annualised % before comparison. Compare against a simple benchmark (S&P500, index ETF equivalent). If domain knowledge ROI < benchmark → it is not a meaningful externality. If domain knowledge ROI > benchmark → it is real additional compensation.

For knowledge-intensive roles (finance, trading, law, engineering, medicine):

```
true_compensation = direct_salary + knowledge_externality_value
knowledge_externality_value = domain_knowledge × personal_capital × holding_years × applicable_leverage
```

**Example** (finance domain):
- Salary: $800K/year
- Knowledge externality: understanding leverage, compounding, yield, risk pricing → applied to $3M personal assets at 3% alpha = $90K/year
- True compensation: $890K/year (not $800K)

**Decision rule**:
- When comparing offers across domains: add knowledge externality before comparing.
- A lower-salary role in a high-knowledge domain may dominate a higher-salary role in a low-knowledge domain once externality is added.

**Fail action**: Never compare across domains on headline salary alone — always compute the implicit knowledge ROI.

---

## Self-Test Scenario

**Setup**: You receive two offers simultaneously.

- **Offer A**: $1.1M headline (take-home ~$850K), quant analyst at a traditional bank. Role is well-defined but in a compliant org (G3 diagnosis: output gains go to org). Promotion track: 10%/year, unlikely to exceed $1.5M in 5 years. Domain: finance/trading (high knowledge externality).

- **Offer B**: $1.3M headline (take-home ~$1.0M), project manager at a tech startup, meritocratic org. High upside but role is cross-domain — no direct trading/financial domain knowledge transfer.

**G0**: Execution phase (real offers) → proceed.
**G1**: Both bounded — A has slight org risk (if project fails, reputational hit capped), B is equity-heavy → preference slight to A.
**G2**: Your floor = $900K take-home → A ($850K) is BELOW FLOOR. Negotiate or reject A.
**G3**: A = compliant, B = meritocratic → B has higher optimization upside.
**G4**: A viability: $1.1M × 10%^5 = $1.77M — technically viable but *ceiling is structural*. B viability: faster if meritocratic promotion fires.
**G5**: EV table: A after negotiation ($950K take-home), B ($1.0M), Status quo ($800K) → B dominates even before externality.
**G6**: A externality: finance knowledge × personal capital = significant. Add $60–90K/year. A adjusted: $910–940K. B: cross-domain, lower externality.

**Verdict**: Negotiate A to $950K+ take-home, then compare. If A cannot clear floor after negotiation → B. Domain externality from A is real value but does not compensate for a below-floor salary in a compliant org.

---

## Quick Reference Card

| Gate | Question | Fail → |
|------|----------|--------|
| G0 | Exploration or execution? | If exploration: multi-track, no convergence yet |
| G1 | Who controls worst-case loss? | If uncontrolled: discount or avoid |
| G2 | Is floor written BEFORE meeting? | If no: write floor first, meeting second |
| G3 | Is org meritocratic or compliant? | If compliant: don't optimize output for org |
| G4 | Can required annual % be achieved? | If no: path eliminated, reroute now |
| G5 | Is EV table built for all options? | If no: build table before responding |
| G6 | Is domain externality included? | If no: add knowledge ROI to true comp |

---

*SOP #05 — Career & Salary Decision Making*
*Based on MD-121/128/129/163/209/210/229/301/302/303/309/311/312/327 from 327 micro-decisions.*
*Cycle 115 — 2026-04-08T19:30Z*
*SOP series: #01 Strategy Dev → #02 Portfolio → #03 Execution → #04 Kill Decision → #05 Career & Salary*
