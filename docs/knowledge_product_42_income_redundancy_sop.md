# SOP #42 — Income Redundancy & Anti-Fragile Income Protocol

**Domain:** 6 — 存活冗餘 (Survival Redundancy / Anti-Fragile)
**Date:** 2026-04-09T UTC (Cycle 195)
**DNA Anchors:** MD-159, MD-79, MD-91, MD-148, MD-186

---

## Introduction

A single income source is not income — it is a job. The distinction is structural, not semantic. A job is a single point of failure: one employer, one contract, one platform, one market. When it fails, the system fails completely. Income is a portfolio: multiple streams, uncorrelated failure modes, where the loss of any one stream leaves the system operational. This SOP formalizes the six-gate protocol for auditing, building, and stress-testing income redundancy so that no single income failure equals total system failure. This is the prerequisite for everything else — trading systems, knowledge products, digital continuity — because none of those survive insolvency.

**Core Claim:** Losing any one income stream must leave you ≥60% operational. This is the anti-fragile income criterion. Below 60% post-loss operability = structural fragility, regardless of how large any single stream is today.

DNA anchors: MD-159 (槓鈴策略=穩健大部位+爆炸小部位 — the barbell requires a stable base before the explosive upside is built), MD-79 (交易員創意×執行兩分法 — creative income design is separated from disciplined execution).

---

## Gate G0 — Income Stream Inventory

**Trigger:** Beginning of protocol. Run quarterly or after any income change.

**Action:** List ALL active and semi-active income streams. For each stream, classify across three dimensions:

**Dimension 1 — Time dependency:**
- **Active:** requires proportional time investment (hourly work, consulting billed by session, salary)
- **Passive:** scales without proportional time input (algorithmic trading, royalties, recurring subscriptions, dividend income)

**Dimension 2 — Correlation:**
- **Correlated:** fails when another stream fails (same employer group, same asset class, same platform risk)
- **Uncorrelated:** independent failure mode (different counterparty, different market, different channel)

**Dimension 3 — Time-to-restart:**
- **Fast restart (<7 days):** can be re-activated with minimal lead time (consulting network is warm, platform account is live)
- **Slow restart (>30 days):** requires setup, re-negotiation, or rebuild before first dollar flows again

**Inventory template (complete for each stream):**

```
Stream name:                     [e.g., Salary / Trading P&L / Gumroad / Consulting]
Type:                            Active | Passive
Correlation:                     Correlated with [stream X] | Uncorrelated
Time-to-restart:                 <7d | 7–30d | >30d
Monthly contribution (3m avg):   $___
% of total income:               ___%
```

**Kill condition — CRITICAL flag:**
Any single stream contributing >80% of total income = CRITICAL. The system is not an income portfolio. It is a job wearing a portfolio costume. Acknowledge this condition and set a 90-day remediation target before proceeding.

**Pass criteria:** Every stream is inventoried, classified, and assigned a percentage share. CRITICAL flag is either absent or explicitly acknowledged with a remediation deadline.

---

## Gate G1 — Survival Threshold

**Trigger:** After G0 inventory is complete.

**Action:** Calculate the minimum viable floor (MVF) — the monthly income required to keep the system alive with no degradation in core operations.

**MVF components (enumerate explicitly — no rounding, no approximations):**

```
Rent / housing:                                    $___/month
Food + utilities:                                  $___/month
Health maintenance:                                $___/month
Core tools (API, platform, trading infrastructure):$___/month
Trading capital maintenance
  (min top-up to avoid forced position reduction): $___/month
Minimum debt service:                              $___/month
                                                   ──────────
MVF TOTAL:                                         $___/month
```

**Stream tier classification:**
- **PRIMARY:** monthly contribution alone covers the full MVF
- **SECONDARY:** covers 30–99% of MVF — valuable but not independently survivable
- **CONTRIBUTION:** covers <30% of MVF — accelerator, not load-bearing

**Target structure:** ≥2 PRIMARY-tier streams. One PRIMARY stream = single point of survival failure. Two PRIMARY streams = any one can fail and the floor holds without activation of backup protocols.

**Pass criteria:** MVF is calculated to the dollar. At least one stream is classified PRIMARY. Flag issued if PRIMARY count < 2.

DNA anchor: MD-148 (基礎設施投資=報酬門檻十倍年成本 — trading capital maintenance and tool costs must be included in the floor calculation; tools that are not covered by income eventually kill the system).

---

## Gate G2 — Correlation Audit

**Trigger:** After G1 classification.

**Action:** Map failure dependencies across all income streams. Income streams that share a common single point of failure are correlated — even when they appear structurally distinct.

**Correlation sources to audit:**

| Shared factor | Example failure | Classification |
|---|---|---|
| Same employer or client | Company lays off → salary + consulting from same firm both collapse | Correlated |
| Same asset class | Trading income (equities) + salary from equity fund manager — both hurt in equity bear | Correlated |
| Same platform | Two income streams both hosted on one platform that deplatforms you | Correlated |
| Same market regime | Momentum strategy income + macro advisory both require trending markets | Correlated |
| Same counterparty | Two "different" consulting clients are subsidiaries of the same holding group | Correlated |

**Rule (MD-159):** No two PRIMARY-tier streams may share the same single point of failure. Each income stream must have independent viability — the same logic that governs trial positions and scaling positions applies here: each component must stand on its own, not rescue the other when both are pressured simultaneously.

**Correlation matrix (fill in):**

```
         Stream A  Stream B  Stream C  Stream D
Stream A    —
Stream B    [C/U]    —
Stream C    [C/U]   [C/U]     —
Stream D    [C/U]   [C/U]    [C/U]     —
```

C = Correlated | U = Uncorrelated

**Kill condition:** Two PRIMARY-tier streams found to be correlated = STRUCTURAL FAILURE. They are not two streams — they are one stream with two payment channels. Treat as a single stream for all survival calculations until decorrelated.

**Pass criteria:** All PRIMARY-tier streams pass the independence test. No two PRIMARY streams share a single point of failure.

---

## Gate G3 — Time-to-Revenue Test

**Trigger:** Evaluating any new income stream candidate, or auditing the current portfolio for emergency activation capability.

**Action:** For each stream in the portfolio — existing and candidate — classify time-to-first-dollar from a standing start:

| Class | Time-to-revenue | Role in portfolio |
|---|---|---|
| FAST | <30 days | Emergency activation layer — deploys when a primary stream fails |
| MEDIUM | 30–180 days | Core building layer — constructed during stability windows |
| SLOW | >180 days | Compounding layer — high-EV, long-duration bets |

**Rule (MD-79):** Building income streams requires separating the creative function (what to build) from the execution function (how to launch and sustain it). FAST streams are typically execution-constrained — the idea is known, the bottleneck is activating an existing network or channel. SLOW streams are typically idea-constrained — they require developing a new offer, building a new audience, or accumulating a new asset base. Identify which bottleneck applies before allocating time.

**Portfolio minimum requirements:**

```
>=1 FAST stream:   [stream name] — can generate $___ within 30 days of activation
>=1 SLOW stream:   [stream name] — compounding, target $___ by [date]
```

**FAST stream examples:**
- Consulting or advisory work on existing skills (warm network can invoice within days)
- Short-term freelance engagements in current domain
- Existing digital product with live sales page (activation = promotion, no new builds)
- Futures or options strategy already running live (size increase within existing infrastructure)

**SLOW stream examples:**
- Algorithmic trading system in development (6–18 months to validated live capital)
- Content-to-revenue funnel (audience to trust to product, typically 6–12 months)
- Dividend income (requires capital accumulation over extended period)
- SaaS or tool product (development plus distribution cycle)

**Kill condition:** Portfolio has zero FAST streams = no emergency activation capability. If any PRIMARY stream fails, there is no rapid-response income replacement. This critical gap takes precedence over any SLOW stream development.

**Pass criteria:** Portfolio contains at least one FAST and one SLOW stream. Both are named with specific dollar targets and activation timelines.

---

## Gate G4 — 60% Survival Test

**Trigger:** After G0–G3 are complete. Run as a stress test.

**Action:** This is the anti-fragile criterion. Execute the following simulation:

**Step 1:** Identify the largest income stream by monthly dollar contribution.

**Step 2:** Remove it from the portfolio entirely. Assume $0 with no recovery for 90 days.

**Step 3:** Sum remaining streams. Does the remaining portfolio cover the MVF?

```
Largest stream removed:       [stream name], $___/month
Remaining portfolio total:    $___/month
MVF (from G1):                $___/month

Remaining / MVF =             ___%

>=100%: Full survival. Largest stream failure is absorbed with no floor breach.
60–99%: Operational but constrained. Survivable; activate FAST stream within 30 days.
<60%:   CRITICAL GAP. System cannot absorb the loss of its largest stream.
```

**Rule (MD-91):** The 60% survival test is only meaningful after the G2 correlation audit has passed. A portfolio of two correlated streams fails this test by construction — remove the largest and the correlated partner degrades with it, producing a far smaller remaining portfolio than the numbers suggest. Validate correlation structure first, then run the survival test.

**Pass criteria:** Remaining portfolio after removing the largest stream covers ≥60% of MVF. If <60%: document the specific dollar gap and assign a 90-day target to close it.

---

## Gate G5 — Recovery Protocol

**Trigger:** Any income stream failure or degradation event.

**Pre-work:** Write these protocols before a crisis occurs. A recovery plan written during a crisis is written under loss aversion and time pressure — it will be improvised, and improvised risk management fails at the worst moment (MD-91).

**Protocol format (complete for each PRIMARY-tier stream):**

```
Stream name:

Failure signal:
  [Specific, observable event. Not "if things feel uncertain."
   Examples: "Invoice unpaid >30 days" / "Monthly P&L < $0 for 2 consecutive months"
             "Platform revenue drops >50% month-over-month"]

72-hour action:
  [Specific action executable within 72h of confirmed failure signal.
   Must not require external permissions to initiate.
   Examples: "Send 5 warm outreach messages to consulting contacts with pre-built scope-of-work"
             "Increase FAST trading strategy to 1.5x current size within kill conditions"
             "Post Gumroad product to Twitter + email list — no new builds required"]

14-day stabilization milestone:
  [Specific, measurable milestone confirming recovery is underway.
   Examples: ">=1 consulting engagement confirmed by day 14"
             "FAST stream generating >=$___ net by day 14"
             "New income source identified; first billable step completed"]

30-day target:
  [Specific income level confirming stabilization.
   Examples: "Consulting at >=50% of lost stream income by day 30"
             "Combined remaining + activated streams >= MVF by day 30"]
```

**Rule (MD-186):** Recovery protocols are asymmetric structures. The 72-hour action is the fast-deployment leg — low cost, immediate activation, covers the most urgent gap. The 14-day and 30-day steps are the compounding legs — they rebuild toward full income capacity. Pre-committing to both ensures the response is structured, not reactive. The asymmetry is intentional: the cheap fast action buys time for the more valuable recovery to complete.

**Kill condition:** If no 72h action can be specified for a PRIMARY-tier stream, that stream has no pre-committed recovery path. Its failure is existential by design. Build the protocol or reclassify the stream before treating it as PRIMARY.

**Pass criteria:** Every PRIMARY-tier stream has a completed recovery protocol with a specific failure signal, a 72h action, a 14-day milestone, and a 30-day target. SECONDARY streams have at minimum a documented 72h action.

---

## Self-Test Scenario: Salary Cut 50%

**Setup:** Three income streams: (A) salary $5,000/month — 80% of total, (B) trading P&L $1,200/month — 19%, (C) Gumroad products $300/month — 5%. MVF = $3,200/month. Employer announces a 50% salary reduction effective next month.

**G0 — Inventory check:**
- Stream A: Active, same-employer-dependent. Contributes 80% of total. CRITICAL flag was already live before the cut was announced.
- Stream B: Passive (algorithmic), uncorrelated to A (different asset class). 19% of total.
- Stream C: Passive, uncorrelated. 5% of total.

**G1 — Survival threshold:**
- Post-cut: A = $2,500, B = $1,200, C = $300. Total = $4,000. MVF = $3,200. Floor is technically covered — only because B and C remain intact.
- PRIMARY classification pre-cut: A alone covered MVF (PRIMARY). B alone ($1,200) does not cover MVF ($3,200). C alone does not.
- Post-cut: A ($2,500) no longer independently covers MVF. PRIMARY count = 0. Critical structural failure exposed.

**G2 — Correlation audit:**
- A and B are uncorrelated (employment market vs. trading market). The salary cut is an isolated employer event; B and C are unaffected. Correlation structure holds for the remaining portfolio.
- Note: if B were equity-market trading and A were an equity-fund salary, both would degrade in the same bear market. That would fail G2.

**G3 — Time-to-revenue:**
- B is live and generating. FAST activation: can increase size within days subject to strategy kill conditions.
- C: can be promoted within 24 hours at no incremental cost. FAST layer exists but at low dollar output.
- Gap: no MEDIUM stream building toward a new PRIMARY-tier level. This is the structural deficit.

**G4 — 60% survival test (pre-cut baseline):**
- Remove largest stream: A = $5,000. Remaining: B + C = $1,500. MVF = $3,200.
- $1,500 / $3,200 = 47%. CRITICAL GAP.
- The salary reduction did not create the fragility. The G4 test reveals it was present before the cut.

**G5 — Recovery protocol:**
- Failure signal: termination or salary reduction notice received.
- 72h action: (1) audit trading strategy capacity — can B scale to $2,000+/month within risk parameters? (2) activate consulting network — send outreach to three former clients with pre-built scope-of-work.
- 14-day milestone: ≥1 consulting call confirmed OR trading size increased 30% within strategy constraints.
- 30-day target: combined income ≥ $3,500/month (MVF + 10% buffer).

**Verdict:** The salary cut exposed pre-existing fragility. Immediate priorities: (1) treat consulting reactivation as a FAST stream build — target PRIMARY tier within 60 days; (2) scale trading within strategy kill conditions; (3) 90-day structural target = ≥2 PRIMARY-tier streams so no single stream exceeds 80% of total.

---

## Kill Conditions

| Condition | Action |
|---|---|
| Any single stream >80% of total income | CRITICAL: set 90-day diversification target. Document the acknowledgment date. |
| PRIMARY count < 2 | Build one additional stream to PRIMARY level before deploying new capital into SLOW streams |
| Two PRIMARY streams fail G2 correlation audit | Treat them as one stream. Portfolio is more concentrated than it appears. |
| No FAST stream in portfolio | Do not let any PRIMARY stream exceed 70% of income until a FAST backup is activated |
| G4 survival test <60% | Halt discretionary spending. Activate FAST stream. No new SLOW stream investment until G4 passes. |
| Recovery protocol missing for any PRIMARY stream | Do not rely on that stream as PRIMARY until the protocol is written |

---

## DNA Backing

| MD | Principle | Application in this SOP |
|----|-----------|--------------------------|
| MD-159 | 試單與加碼單=各自獨立正EV，不能互相依賴才成立 | G2 Correlation Audit: each PRIMARY income stream must have independent survival capacity — no two streams may require the other to remain solvent |
| MD-79 | 交易員=創意×執行兩分法 | G3 Time-to-Revenue: separates creative income design (what to build) from execution (how to activate within 30 days) — identify which bottleneck applies before allocating time |
| MD-91 | DD加碼=穩健性前置條件 | G4 Survival Test: the 60% threshold is only valid after the G2 correlation audit passes — running G4 on unchecked correlated streams produces false safety |
| MD-148 | 基礎設施投資=報酬門檻十倍年成本 | G1 Survival Threshold: trading capital maintenance and infrastructure costs are included in MVF — tools not covered by income eventually kill the system |
| MD-186 | 賭注賠率公式化=先算雙邊賠率再找不對稱套利入口 | G5 Recovery Protocol: pre-commitment to 72h + 14d + 30d actions is a structured asymmetric response — cheap fast activation buys time for the higher-value recovery to complete |

---

## Connection to Other SOPs

- **SOP #36 (Barbell Life Strategy):** The STABLE/EXPLOSIVE classification maps directly onto PRIMARY/SECONDARY/CONTRIBUTION tiers. PRIMARY streams are the STABLE floor. SLOW streams are the EXPLOSIVE compounding layer. Never fund SLOW streams from an undercapitalized PRIMARY base.
- **SOP #21 (Financial Freedom Tier Framework):** MVF in G1 here is the Tier 0 threshold in SOP #21. Achieving ≥2 uncorrelated PRIMARY streams that collectively exceed MVF = Tier 0 funded.
- **SOP #14 (Full-Time Switch Threshold):** The G4 survival test must pass before employment exit is structurally viable. Trading income alone must reach PRIMARY tier before the salary stream is voluntarily removed.
- **SOP #34 (Knowledge Monetization):** Content and product income begins as CONTRIBUTION tier. G1 here defines the exact revenue level required to reach PRIMARY. G3 defines the time structure: Gumroad activation is FAST; audience-to-product funnel is SLOW.

---

## Summary: The Income Redundancy Checklist

```
G0: Inventory all streams. Classify each: Active/Passive, Correlated/Uncorrelated, Restart speed.
    Kill: any single stream >80% of total = CRITICAL.

G1: Calculate MVF to the dollar. Classify each stream: PRIMARY / SECONDARY / CONTRIBUTION.
    Target: >=2 PRIMARY-tier streams.

G2: Correlation audit. No two PRIMARY streams may share a single point of failure.
    Kill: correlated primaries = treat as one stream.

G3: Time-to-revenue classification. Portfolio needs >=1 FAST and >=1 SLOW stream.
    Kill: zero FAST streams = no emergency activation capability.

G4: 60% survival test. Remove largest stream. Remaining >=60% of MVF?
    Kill: <60% = CRITICAL GAP. Fix before adding new SLOW stream bets.

G5: Write recovery protocols before crisis. 72h action + 14d milestone + 30d target.
    Kill: missing protocol for a PRIMARY stream = it is not reliably PRIMARY.
```

If any gate fails: do not proceed. Fix the gate, then re-evaluate.

---

*Series: SOP #01–#42 | Domain: 存活冗餘 | 2026-04-09T UTC (Cycle 195)*
