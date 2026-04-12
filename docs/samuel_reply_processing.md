# Samuel Reply Processing Protocol

> When Samuel responds to `docs/samuel_async_calibration_dm.md`, run this protocol.
> Target: update samuel_dna.md + re-run collision + update B4 rate in 15 minutes or less.
> Created: 2026-04-13 UTC (cycle 370)

---

## 0. What to expect

The DM has 3 questions. Samuel's replies map directly to 3 known divergences:

| Question | Tests | Current model |
|----------|-------|---------------|
| Q1: Friend quiet 3 months — what do you do? | `RELATIONSHIP_DOWNGRADE` | Samuel: fade naturally (inferred) |
| Q2: Gave 3 intros, got nothing back when you needed help | `NETWORK_ROI` | Samuel: ROI audit, actively downgrade |
| Q3: Best friend asks intro to valued contact, 60% uncertain | `INTRO_GATEKEEPING` | Samuel: trust overrides uncertainty (inferred) |

---

## 1. Map reply to verdict

### Q1 — RELATIONSHIP_DOWNGRADE

Read Samuel's reply. Classify:

| What he says | Verdict | Action |
|--------------|---------|--------|
| "I'd reach out and ask what's up" or "have a direct conversation" | **CORRECTION: DIVERGE→AGREE** | Update §6 rule 5: Samuel does confront, not fade |
| "I'd probably let it fade, wait to see if they re-engage" | **CONFIRMED: DIVERGE** | Keep §6 rule 5 as-is, add quote |
| Mixed / "depends" | **PARTIAL** | Add nuance to §6 rule 5 with his condition |

**DNA update location:** `templates/samuel_dna.md` §6 Social Operating Rules, Rule 5

---

### Q2 — NETWORK_ROI

| What he says | Verdict | Action |
|--------------|---------|--------|
| "I'd write it off" / "stop investing" / "mentally downgrade them" | **CONFIRMED: DIVERGE** | Keep §7 NETWORK_ROI row as-is, add quote |
| "I'd give them benefit of the doubt" / "assume they were just busy" | **CORRECTION** | Revise §7 — NETWORK_ROI may be less pruning-oriented |
| "I'd tell them directly I felt the reciprocity was off" | **NEW BEHAVIOR** | Add direct confrontation variant to §4 conflict resolution |

**DNA update location:** `templates/samuel_dna.md` §7 Known Divergences, NETWORK_ROI row + §0 Principle #7

---

### Q3 — INTRO_GATEKEEPING

| What he says | Verdict | Action |
|--------------|---------|--------|
| "I'd do it — he's my best friend, I trust him" | **CONFIRMED: DIVERGE** | Keep §7 INTRO_GATEKEEPING row. Calibration flag resolved. |
| "I'd check with my contact first before committing" | **PARTIAL CORRECTION** | Update §6 rule 4 with "double-check first" variant |
| "I'd tell my friend I'm not sure the timing is right" | **CORRECTION: DIVERGE→AGREE** | Rewrite §6 rule 4: quality threshold applies even for close friends |

**DNA update location:** `templates/samuel_dna.md` §6 rule 4 + §7 INTRO_GATEKEEPING calibration flag

---

## 2. Execute DNA updates

Open `templates/samuel_dna.md`. For each Q:

1. Update the relevant section with Samuel's actual words in quotes
2. Remove calibration flags for confirmed behaviors
3. Add calibration flags for any new uncertainties
4. Update `§8 Calibration Status` table:
   - Change "in-person correction: NOT DONE" to "async DM: DONE [date]"
   - Note which scenarios were corrected

---

## 3. Re-run collision (35 scenarios)

```bash
cd C:\Users\admin\workspace\digital-immortality
python organism_interact.py templates/dna_core.md templates/samuel_dna.md --report
```

The script will run all 35 scenarios and output:
- `results/collision_dna_core_vs_Samuel_[timestamp].md`
- `results/collision_dna_core_vs_Samuel_[timestamp].json`

---

## 4. Update B4 metrics

After re-run, update `results/dynamic_tree.md` Branch 4 row:
- New agreement rate (X/35)
- New derivative (positive if rate went up vs 64%)
- Note date of Samuel calibration reply

---

## 5. Extract new principles

If Samuel's reply reveals a behavior not in samuel_dna.md §0 Core Principles:

1. Write it as a principle in the format: `**[keyword]** — one-line behavioral rule`
2. Add to §0. Goal: 15+ principles (currently 9).

---

## 6. Commit

```bash
git add templates/samuel_dna.md results/dynamic_tree.md
git commit -m "feat(B4): samuel calibration — async DM reply processed, rate updated"
```

---

## Success criteria

- ≥1 DIVERGE→AGREE or AGREE→DIVERGE correction confirmed
- ≥1 new principle extracted
- Collision re-run at 35 scenarios complete
- B4 rate updated in dynamic_tree.md
- Calibration flags cleared for confirmed items

---

## Post-processing: next calibration gate

After this DM is processed:

- If rate ≥ 70%: proceed to in-person calibration session (5 questions in §9)
- If rate < 60%: re-examine which inference sections need more grounding — prioritize in-person
- Regardless: update `docs/samuel_pilot_dm.md` with latest agreement rate for Turing test context

---

*2026-04-13 UTC (cycle 370)*
