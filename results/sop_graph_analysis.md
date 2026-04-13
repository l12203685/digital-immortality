# SOP Graph Analysis — Cycle 411
Generated: 2026-04-14 | Source: results/sop_graph.json (124 nodes, 377 edges)

---

## Graph Overview

| Metric | Value |
|--------|-------|
| SOP files parsed | 124 |
| Directed reference edges | 377 |
| Unique SOPs referenced | 125 |
| Ghost SOPs (ref-only, no file) | 1 (#200) |
| Orphan SOPs | 6 |
| Connected clusters (size >= 3) | 1 (119 SOPs) |

Average out-degree: 3.0 refs/SOP. The graph is nearly fully connected — 119 of 124 SOPs form one giant cluster.

---

## Top 5 Hub Nodes (highest in-degree)

| Rank | SOP | In | Out | Role |
|------|-----|----|-----|------|
| 1 | #001 Trading Strategy Development | 51 | 0 | Root anchor — everything cites it, cites nothing |
| 2 | #082 Revenue Activation Milestone Tracker | 14 | 0 | Revenue root — sink node |
| 3 | #083 Daily Posting Execution Ritual | 14 | 0 | Content root — sink node |
| 4 | #070 Revenue Conversion Protocol | 12 | 10 | Hub + connector — high in AND out |
| 5 | #004 Strategy Failure & Kill Decision Tree | 11 | 3 | Core trading governance |

SOP #001 is 4x more referenced than any other node (51 vs 14). It is the gravity well of the entire SOP corpus.

SOP #070 is structurally unique: high in-degree AND high out-degree (12/10). It is the best candidate for a true hub — it both synthesizes upstream knowledge and distributes to downstream SOPs.

---

## Top 5 High-Out Nodes (most cross-references made)

| SOP | Out | In | Role |
|-----|-----|----|------|
| #104 Async Audit Delivery | 15 | 2 | Aggregator — cites 15 SOPs, rarely cited back |
| #066 Distribution Activation | 11 | 5 | Distribution hub |
| #087 Content Repurposing: SOP → X Thread | 11 | 1 | Cites broadly, not recognized back |
| #097 87-Day Mainnet Revenue Countdown | 11 | 8 | Balanced hub |
| #070 Revenue Conversion Protocol | 10 | 12 | Best-balanced hub (see above) |

SOP #104 (out=15, in=2) is undervalued: it aggregates 15 SOPs but only 2 others reference it. Consider elevating it to a standard integration checkpoint.

---

## Orphan SOPs (no incoming or outgoing edges — 6 total)

These are fully disconnected and invisible to the recursive engine:

| SOP | Title | Action |
|-----|-------|--------|
| #022 | Universal Exit Protocol | Should reference #001 and #004 |
| #032 | Cognitive Capital & Peak Performance | Should reference #013 (Personal OS) |
| #040 | Information Asymmetry Edge Protocol | Should reference #006 (Game Theory) |
| #073 | Dynamic Tree Protocol | Should reference #047 (Recursive Engine) |
| #106 | Organism Drift & Recalibration | Should reference #091 (DNA Calibration) |
| #116 | Recursive Distillation Taxonomy | Should reference #047 and #091 |

Priority: #106 and #116 are identity/calibration SOPs — orphaning them means drift detection and distillation are invisible to the graph.

---

## Cluster Analysis

The graph has one dominant connected component (119 SOPs). The 5 isolated nodes are the 6 orphans minus one (SOP #022 appears paired but disconnected). This is a healthy sign — the SOP library is largely self-referential and internally consistent.

No dense sub-clusters were detected algorithmically because the single giant component absorbs all relationships. Thematic sub-domains (trading execution, revenue activation, content distribution) are inferred from the hub analysis rather than graph topology.

---

## Missing Edges (actionable)

High-priority cross-links that should exist but don't:

| Gap | Why it matters |
|-----|----------------|
| #091 (DNA Calibration) not cited by #082, #083, #070, #085, #086, #097 | Revenue execution SOPs should gate on identity calibration |
| #004 (Kill Decision) not cited by #070, #082, #083, #097 | Revenue activation must reference the kill-switch logic |
| #012 (Content Distribution) not cited by #083, #085, #097 | Posting ritual should link to distribution architecture |
| #100 (Century Review) has in=0 | A meta-review protocol that nobody references — it will never be triggered organically |

---

## Actionable Priorities

1. **Wire orphans** — 6 SOPs, estimated 1-2 hrs. Start with #106 and #116 (identity integrity risk).
2. **Elevate #091 (DNA Calibration)** — add a reference to it from all revenue SOPs (#082, #083, #070, #085, #086, #097). Prevents revenue execution from diverging from identity.
3. **Fix SOP #100** — add a reference from a regularly-executed SOP (e.g. #091 or #097) so the century review gets triggered in the recursion cycle.
4. **Review SOP #104** — out=15 but in=2. Either promote it to a standard audit node or absorb its references into a hub SOP.
5. **Ghost #200** — SOP #100 references a non-existent SOP #200. Resolve or create the file.
