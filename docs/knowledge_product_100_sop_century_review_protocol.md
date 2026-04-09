# SOP #100 — SOP Century Review Protocol
> 百份 SOP 自我稽核協議（L3 for Knowledge Output Branch）
> Created: 2026-04-09 UTC (Cycle 266)
> Backing MDs: MD-07/101/116/133/322/333

---

## Purpose

100 SOPs have been written. Without a meta-audit, the corpus becomes dead weight:
- Outdated SOPs give wrong guidance on cold start
- Duplicate SOPs create contradictions
- Missing gaps accumulate silently
- No pruning = eventual context bloat

This SOP is the **L3 for the SOP series**. It audits the auditors.

**Run trigger**: Every 100 new SOPs OR every 6 months (whichever first).
**Next run**: SOP #200 or 2026-10-09, whichever is earlier.

---

## G0 — Corpus Inventory

**Trigger**: How many SOPs exist? What domains do they cover?

- Run: `ls docs/knowledge_product_*.md | wc -l`
- Categorize by prefix range:
  - #01–#20: Foundation / identity / cold-start
  - #21–#40: Trading system
  - #41–#60: Organism interaction
  - #61–#80: Knowledge output / content
  - #81–#99: Revenue / commercial / consistency
  - #100+: Meta-system

**Output**: `results/sop_century_inventory.md`
**Decision label**: `SOP_INVENTORY_DONE`

---

## G1 — Duplicate Detection

**Trigger**: Are any two SOPs solving the same problem?

Criteria for duplicate:
- >60% topic overlap (same trigger + same G0 step)
- One SOP is a subset of another

For each pair found:
- Mark the older as DEPRECATED
- Add a pointer in the older: `> Superseded by SOP #XXX`
- Do NOT delete — rename history matters

**PASS**: 0 duplicate pairs found → proceed to G2
**FAIL**: ≥1 pair found → resolve before G2; log to `results/sop_deprecation_log.md`

**Decision label**: `SOP_DEDUP_CLEAN` or `SOP_DEDUP_RESOLVED`

---

## G2 — Stale Content Check

**Trigger**: Are any SOPs referencing outdated systems, prices, or file paths?

Check for:
- File paths that no longer exist (`grep -r "file_path" docs/ | xargs -I{} test -f {}`)
- Price thresholds or dates that have passed (e.g., "2026-07-07 deadline" — still live?)
- Tool names that have changed (e.g., `testnet_runner.py` → `mainnet_runner.py`)

For each stale reference:
- Update in-place with current path/threshold
- Append `> Updated: [date] — [what changed]` at bottom of SOP

**PASS**: 0 stale references → proceed to G3
**FAIL**: ≥1 stale → update + re-check → log updates

**Decision label**: `SOP_FRESHNESS_OK` or `SOP_FRESHNESS_UPDATED`

---

## G3 — Gap Analysis

**Trigger**: What life domains have NO SOP coverage?

Reference domains from DNA:
- Identity / values / principles → SOP coverage?
- Relationships / social operating rules → covered?
- Health / physical capital → covered?
- Learning methodology → covered?
- Emergency / crisis decision-making → covered?
- Financial / FIRE tracking → covered?

For each uncovered domain:
- Add to `results/sop_gap_list.md`
- Prioritize by: (domain frequency in decisions) × (risk of wrong action without SOP)

**Output**: Ranked gap list → feeds SOP #101+ backlog
**Decision label**: `SOP_GAP_IDENTIFIED` or `SOP_COVERAGE_COMPLETE`

---

## G4 — Pruning Decision

**Trigger**: Which SOPs should be deprecated and which should be merged?

Pruning rules:
1. **Deprecated**: superseded by newer SOP + never referenced in agent behavior
2. **Merged**: two SOPs with >70% overlap → consolidate into one, retire the other
3. **Promoted**: SOPs with >10 agent invocations/month → promote to `skills/` or DNA layer

Pruning is NOT deletion. Create `docs/deprecated/` folder, move deprecated files there.

**PASS**: corpus reduced or same size; no live contradictions → proceed to G5
**Decision label**: `SOP_PRUNE_DONE`

---

## G5 — Cold Start Validation

**Trigger**: After pruning and updating, can a new agent cold-start with dna_core.md + boot_tests.md and navigate correctly to the right SOP?

Test scenario: agent cold-starts → user asks about consulting revenue → agent should reach SOP #97 without reading all 100 SOPs.

Navigation test:
1. From `dna_core.md` → finds `staging/session_state.md` → reads queue
2. Queue references SOP numbers by name → agent reads correct file
3. Agent applies correct G-steps

**PASS**: navigation succeeds in ≤3 file hops → COMPLETE
**FAIL**: agent reads wrong SOP or too many files → add navigation index

**Output**: If FAIL → create `docs/sop_navigation_index.md` with domain → SOP# mapping

**Decision label**: `SOP_NAVIGATION_VALIDATED`

---

## F1 — Recovery: Too Many Deprecations

If >20% of SOPs marked deprecated in G1:
- Stop. This means the corpus has drifted from current operating reality.
- Run full DNA calibration (SOP #80 + SOP #91) before SOP pruning.
- SOPs should track DNA — if DNA evolved and SOPs didn't, fix DNA first.

---

## Outputs

| Artifact | Location |
|----------|----------|
| Inventory | `results/sop_century_inventory.md` |
| Deprecation log | `results/sop_deprecation_log.md` |
| Gap list | `results/sop_gap_list.md` |
| Navigation index | `docs/sop_navigation_index.md` (if G5 fails) |

---

## Meta-Rule

SOP #100 is the only SOP that audits other SOPs. It does not replace DNA calibration (SOP #80 + #91). The three together form the full maintenance stack:

```
SOP #80  — Monthly: extract new decisions from JSONL
SOP #91  — Monthly: audit DNA for drift
SOP #94  — Quarterly: cross-instance calibration
SOP #100 — Per-100: prune SOP corpus, fill gaps
```

Every 6 months: run all four in order. 90 min total. Skip any = maintenance debt.

---

*2026-04-09 UTC*
