# Recursive Distillation Taxonomy Audit — Cycle 298

**Timestamp**: 2026-04-10T UTC  
**Auditor**: daemon (Branch 3.1 priority)  
**Source**: recursive_distillation.md (93 narrative insights, cycles 241–297) + insights.json (206 entries)

---

## Finding 1: Tag System Diverged from Canonical Taxonomy

SKILL.md defines 5 canonical categories:
1. `behavioral-patterns` — how Edward decides, acts, prioritizes
2. `self-awareness` — meta-cognition, blind spots, corrections
3. `methodology` — process, systems, protocols
4. `domain-knowledge` — trading, poker, career, finance, relationships
5. `hypotheses` — predictions, untested beliefs

**Current state**: Tags are ad-hoc mixture of:
- Branch labels (branch-1.1, branch-2.2, branch-6, branch-7) — structural metadata, not taxonomy
- SOP numbers (SOP-76, SOP-92, etc.) — operational references, not semantic categories
- Semantic tags (trading, cold-start, DNA-hygiene, etc.) — correct signal, inconsistently applied
- No insight has a top-level canonical category assignment

**Impact**: Cold-start taxonomy recovery requires reading all 206 entries. Cannot answer "how many behavioral-pattern insights exist?" without full scan. Taxonomy has decayed into a flat tag list.

---

## Finding 2: Gap Between insights.json and recursive_distillation.md

- `recursive_distillation.md` has narrative entries through cycle 257 + daemon cycle 95 (93 insights)
- `insights.json` has 206 entries — the 113-insight gap (94–206) has no narrative in recursive_distillation.md
- insights.json entries 1–25 are recursive-engine noise (cycle-transition, auto-loop — no semantic content)
- Substantive insights: ~181 entries (206 minus ~25 noise entries)
- Narrative coverage: 93 / 181 = **51% narrative gap**

---

## Finding 3: Semantic Cluster Analysis

Scanning tags across all recursive_distillation.md entries:

| Cluster | Tags | Est. Count | Status |
|---------|------|-----------|--------|
| trading/execution | trading, paper-live, branch-1.1, signal-persistence, regime | ~40 | SPLIT candidate (>10) |
| system-maintenance | cold-start, branch-6, consistency, calibration, boot-test | ~25 | SPLIT candidate (>10) |
| sop-protocol-design | branch-7, sop, methodology, protocol-design | ~30 | SPLIT candidate (>10) |
| dna-methodology | branch-2.2, md-extraction, DNA-hygiene, archive-method | ~20 | OK within methodology |
| organism-network | organism-network, cross-instance, divergence | ~8 | OK (under 10) |
| meta-system | daemon, meta-system, signal-decay, priority-signal | ~5 | MERGE → self-awareness |
| domain-career | career, negotiation, poker, investing, contrarian | ~15 | SPLIT candidate (>10) |

---

## Taxonomy Evolution Proposals

### A. Formalize Top-Level Category Assignment

Every insight must carry one canonical top-level category:

```
behavioral-patterns | self-awareness | methodology | domain-knowledge | hypotheses
```

### B. Split `methodology` into Subcategories

- `methodology/protocol-design` — SOP creation, G0-G5 gate architecture
- `methodology/system-maintenance` — cold-start, consistency, calibration, L1-L2-L3 loops
- `methodology/knowledge-extraction` — MD extraction, archive, distillation process

### C. Split `domain-knowledge` into Subcategories

- `domain/trading` — BTC signals, regime detection, strategy lifecycle
- `domain/career` — job market, negotiation, employer dynamics
- `domain/finance` — investing, bankroll management, EV calculation
- `domain/poker` — GTO, ICM, table selection

### D. Demote Structural Tags to Metadata

- `branch-X` → move to `source.branch` field, not a taxonomy tag
- `SOP-XX` → move to `source.sop` field, not a taxonomy tag
- `cycle-N` → already in `timestamp`; remove from tags

### E. Add `system-evolution` Category

For L3 insights about the digital immortality system evolving its own rules:
- Currently has no home in the 5-category taxonomy
- Distinct from `methodology` (which is about process) and `self-awareness` (which is about cognition)
- `system-evolution` = insights that change how the system operates, not just what it knows

---

## Action Items

1. **Apply taxonomy to recursive_distillation.md** — add `category:` field to each insight entry (priority: behavioral-patterns, self-awareness)
2. **Prune noise from insights.json** — remove 25 recursive-engine cycle-transition entries (add to noise_archive)
3. **Write SOP #116** — Recursive Distillation Taxonomy Protocol: when to evolve categories, how to classify, split/merge rules
4. **Next narrative batch** — write recursive_distillation.md entries for insights 94–206 (deferred; 113-insight gap)
5. **daemon_next_priority** → taxonomy backfill (after SOP #116)

---

## Verdict

Taxonomy is alive but has drifted. Structure is intact (SKILL.md defines the rules); execution has not followed the rules for 116 insights. SOP #116 formalizes the protocol so drift is detectable and correctable at each cycle, not just at audit cycles.
