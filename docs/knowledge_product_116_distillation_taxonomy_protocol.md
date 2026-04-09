# SOP #116 — Recursive Distillation Taxonomy Protocol

**Domain**: Branch 3.1 (Recursive Distillation)  
**Created**: 2026-04-10T UTC (cycle 298)  
**Status**: ACTIVE  
**Backing MDs**: SKILL.md §Recursive Distillation Phase; MD-01 (meta-rule: learn=write); MD-133 (direct-metric principle)  

---

## Purpose

The recursive distillation taxonomy is a living system — categories evolve as insights accumulate. Without a formal protocol, the tag system drifts into ad-hoc labels (branch-X, SOP-XX) that prevent cross-category analysis and make cold-start taxonomy recovery expensive.

This SOP defines when and how to evolve the taxonomy, classify insights, and detect drift.

---

## G0: Trigger Conditions

Run this protocol when ANY of the following:

- T1: Insight count since last taxonomy audit > 50
- T2: New insight does not fit any existing category (no-fit event)
- T3: Any category exceeds 10 insights (split candidate)
- T4: Two categories share >50% of semantic content (merge candidate)
- T5: daemon_next_priority flags taxonomy as neglected

Current audit cycle: **T1 triggered** (113 insights since last narrative batch, cycle 297)

---

## G1: Canonical Category Framework

Every insight is assigned exactly ONE top-level category:

| Category | Definition | Examples |
|----------|-----------|---------|
| `behavioral-patterns` | How Edward decides, acts, prioritizes in specific domains | inaction-bias, information-asymmetry-first, population-exploit |
| `self-awareness` | Meta-cognition, blind spots, error patterns, corrections recognized | priority-signal-decay, alignment-theater-detection, idle-vs-dead distinction |
| `methodology` | Process, systems, protocols that operationalize thinking | G0-G5 gates, L1-L2-L3 loop, cold-start protocol, distillation cadence |
| `domain-knowledge` | Facts, patterns, models specific to a domain | BTC regime detection, poker ICM, career employer-cost-down, ETF selection |
| `hypotheses` | Untested predictions, emerging beliefs not yet validated | new signal patterns, behavioral hypotheses about future scenarios |

Subcategories (use as secondary tag, not primary):

```
methodology/
  protocol-design       — SOP creation, G0-G5 architecture
  system-maintenance    — cold-start, consistency, calibration, branch decay
  knowledge-extraction  — MD extraction, archive processing, distillation

domain/
  trading               — BTC signals, strategy lifecycle, regime
  career                — job market, negotiation, employer dynamics  
  finance               — investing, bankroll, EV calculation
  poker                 — GTO, ICM, table selection, bankroll
  relationships         — social dynamics, organism collision, trust
```

---

## G2: Classification Procedure

For each new insight:

1. **State the core claim in one sentence** — strip the example, keep the principle
2. **Ask**: Does this tell us *how Edward thinks* (behavioral-patterns) or *what Edward knows* (domain-knowledge)?
3. **Ask**: Is this about the system monitoring itself (self-awareness) or a process it uses (methodology)?
4. **Ask**: Is this a prediction without evidence yet (hypotheses)?
5. **Assign primary category + subcategory** — if ambiguous between two, pick the one that enables the most useful cross-query

**Structural metadata (NOT taxonomy tags)**:
- `source.branch` — branch-1.1, branch-2.2, etc.
- `source.sop` — SOP number if relevant
- `source.cycle` — already in timestamp

---

## G3: Split/Merge Rules

**Split** when a category exceeds 10 insights:
- Create two named subcategories with non-overlapping definitions
- Reassign existing insights to subcategories
- Update SKILL.md taxonomy section

**Merge** when two categories share >50% semantic content:
- Define the merged category
- Migrate all insights from both into merged category
- Remove the merged-from categories

**New category** when:
- At least 3 insights don't fit any existing category
- The proposed new category has a crisp, non-overlapping definition
- No existing category can be expanded to absorb it

---

## G4: Drift Detection

Run taxonomy health check at every 50-insight milestone:

```
taxonomy_health = {
  "category_counts": {<category>: <count>},
  "no_category_insights": [<key>, ...],
  "split_candidates": [<category> for cat if count > 10],
  "structural_tag_in_taxonomy": [<tag> for tag if "branch-" in tag or "SOP-" in tag],
  "narrative_gap": len(insights.json) - len(recursive_distillation.md entries)
}
```

**Health thresholds**:
- HEALTHY: 0 no_category, 0 split_candidates with >15, narrative_gap < 30
- WATCH: 1-5 no_category, any category 10-15 insights, narrative_gap 30-60
- DRIFT: >5 no_category, any category >15, narrative_gap >60
- CRITICAL: no canonical category applied to any insight, narrative_gap >100

**Current status**: DRIFT (narrative_gap=113, structural tags in taxonomy, 0 canonical categories applied)

---

## G5: Persist and Evolve

After each taxonomy evolution:

1. Update `SKILL.md` §Recursive Distillation Phase with new category list
2. Write taxonomy health metric to `results/taxonomy_health.json`
3. Append evolution event to `recursive_distillation.md`
4. Apply new categories retroactively to insights.json if > 10 reclassified
5. Update daemon_next_priority: next milestone = when insight count crosses next 50-threshold

---

## Anti-Patterns

| Pattern | Why it fails |
|---------|-------------|
| Branch labels as categories | `branch-1.1` is provenance, not meaning — useless for cross-domain search |
| SOP numbers as categories | SOP-92 is a pointer, not a concept — breaks when SOPs are renumbered |
| "domain-knowledge" catchall | Catches everything → searchable for nothing |
| Taxonomy by vibes | No crisp definition → different agents classify the same insight differently |
| Audit without reclassification | Knowing drift exists but not fixing it = alignment theater |

---

## Related Files

- `SKILL.md` — canonical taxonomy definition (§Recursive Distillation Phase)
- `memory/recursive_distillation.md` — narrative insight log (append-only)
- `memory/insights.json` — structured insight store (209 entries)
- `results/taxonomy_audit_cycle298.md` — this cycle's full audit report

---

## Revenue Bridge

This SOP is part of the knowledge product series. It operationalizes a core intellectual challenge (keeping a living knowledge taxonomy from decaying) that any individual building a personal knowledge management or digital twin system will face.

**Tier**: $97 async audit / $197 guided session component (taxonomy design consultation)  
**Posting queue**: ~Dec 2026
