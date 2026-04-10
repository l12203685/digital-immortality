# SOP #69 — Organism Async Calibration Measurement Protocol
> Domain 4 (社交圈 / Ecosystem) | 2026-04-09 UTC

## Purpose

A collision engine produces a baseline agreement rate (e.g., 15/22 AGREE = 68%).
That rate is meaningless unless it can be improved.

SOP #69 defines how to **measure and close divergence axes via async message** — no scheduling required, no in-person session needed. The target is not 100% agreement; it is accurate modeling. Some divergences are structural and should be preserved. The protocol distinguishes "my model was wrong" (fixable) from "we genuinely differ" (keep as documented divergence).

**Core axiom**: An organism DNA file is a hypothesis. Async calibration is the experiment that tests it. Every round either confirms the hypothesis or updates it. Stale hypothesis = unreliable model.

---

## Prerequisites

Before running this SOP:
- Organism DNA file exists (e.g., `templates/samuel_dna.md`) with ≥3 divergence axes identified from a prior collision run
- Collision baseline score recorded (e.g., 15/22 AGREE, 7 diverge axes)
- Async DM content prepared (e.g., `docs/samuel_async_calibration_dm.md`) — 3 scenarios covering ≥2 divergence axes

---

## Gate Structure

### G0: Pre-Condition Check

Verify all three conditions before sending:

| Check | Required |
|-------|----------|
| Organism DNA file exists with §7 Divergence table | ✓ |
| ≥3 divergence axes identified with domain labels | ✓ |
| Baseline collision score recorded in dynamic_tree.md | ✓ |
| Async DM drafted with 3 scenarios targeting ≥2 divergence axes | ✓ |

If any check fails: do not send. Build the missing artifact first.

**DM send trigger**: Edward sends the async DM. Record send timestamp in dynamic_tree.md.
Format: `4.1 async DM sent [date] — targets: [axis1], [axis2], [axis3]`

---

### G1: Async Probe Design

Each probe round uses exactly **3 scenarios**. Constraints:

1. **Coverage**: Scenarios must collectively cover ≥2 of the known divergence axes
2. **Format per scenario**:
   ```
   Situation: [context, 1–3 sentences]
   Edward's decision: [what Edward does]
   Edward's reasoning: [the underlying principle driving the decision]
   → "What would you do? Why?"
   ```
3. **Neutrality**: Do not hint at expected answer. "There's no right answer" framing is required.
4. **Selection criteria**: Rank divergence axes by information value. Send highest-information axes first:
   - **High information**: axis where premise is unknown (model has placeholder or inference)
   - **Medium information**: axis where premise is known but confidence is low
   - **Low information**: axis where behavior is confirmed but reasoning is unclear

**Axis prioritization formula** (for ordering rounds):
```
priority = (information_value × model_uncertainty) + correction_impact
```
Correction impact = high if fixing this axis would flip ≥2 other scenario verdicts via shared premise.

**Do not probe**: Axes already confirmed via observed behavior (not inferred). Mark those as `CONFIRMED_BEHAVIORAL` in the DNA file.

---

### G2: Response Interpretation

When the organism responds, classify each scenario using this decision tree:

```
Parse response → extract:
  (a) Decision (what they say they would do)
  (b) Reasoning (why)

Compare to Edward's model of that organism:

  Decision matches model?
  ├── YES → Same decision
  │         Reasoning matches model?
  │         ├── YES → AGREE_FULL (model confirmed)
  │         └── NO  → AGREE_DIFF_REASON (flag for reasoning variant)
  └── NO  → Different decision
             New premise identified?
             ├── YES → DIVERGE_NEW_PREMISE (update DNA)
             └── NO  → DIVERGE_SAME_PREMISE (structural divergence, preserve)
```

**Classification labels**:
- `AGREE_FULL` — decision + reasoning both match model → no change needed
- `AGREE_DIFF_REASON` — same decision, different path → add reasoning variant to DNA
- `DIVERGE_NEW_PREMISE` — different decision because organism operates on a principle Edward's model didn't have → close gap, add principle
- `DIVERGE_SAME_PREMISE` — different decision from known premise → structural divergence, keep in §7

**Extraction rule**: For any free-text response, identify the single underlying decision rule. Example:
> "I'd probably just let the friendship fade naturally" → premise: `passive_maintenance_default`
> "I'd reach out to check in" → premise: `proactive_relationship_audit`

Write extracted premise to organism DNA §4 or §7 before re-running collision.

---

### G3: DNA Gap Identification and Update

Apply update rules based on G2 classification:

| Classification | DNA Action |
|---------------|-----------|
| `AGREE_FULL` | No change. Confirm axis as validated. |
| `AGREE_DIFF_REASON` | Add reasoning variant to §4 Behavioral Patterns. Note: "Same outcome via different path." |
| `DIVERGE_NEW_PREMISE` | Add new principle to §2 or §4. Update §7 divergence table: mark axis as `CLOSED_MODEL_GAP`. Re-run collision. |
| `DIVERGE_SAME_PREMISE` | No DNA change. Update §7: mark axis as `CONFIRMED_STRUCTURAL`. Note: "Model was correct. Genuine divergence." |

**Minimum viable round**: A calibration round succeeds if it produces ≥1 `DIVERGE_NEW_PREMISE` correction AND ≥1 new principle added to the DNA. Rounds that only produce `AGREE_FULL` or `CONFIRMED_STRUCTURAL` do not advance calibration — they confirm what was known.

**Gap log format** (write to organism DNA §8 Calibration Status):
```
Round [N] — [date]:
  Scenarios probed: [axis1], [axis2], [axis3]
  Corrections: [count]
  New premises added: [count]
  Axes closed: [list]
  Axes remaining: [count]
  Next round target: [top 2 remaining axes]
```

---

### G4: Collision Re-Run

After any DNA update from G3, re-run the collision engine:

```bash
python organism_interact.py templates/dna_core.md templates/[organism]_dna.md --report
```

**Compare against baseline**:
- Record new score (e.g., 16/22 AGREE = 73%)
- For each axis that changed verdict (AGREE↔DIVERGE): document in §8 as `FLIPPED`
- `FLIPPED` axes are calibration successes

**Calibration success threshold**: ≥1 axis flip (AGREE→DIVERGE or DIVERGE→AGREE) in a round = round successful.

**No flip**: If collision score unchanged after DNA update, check:
1. Was the new premise actually written to the correct DNA section?
2. Does `organism_interact.py` have a handler for the updated domain?
3. Is the scenario weighting correct?

Fix infrastructure gap before concluding "no calibration effect."

**Score delta log** (append to dynamic_tree.md §4.1):
```
Collision re-run [date]: [old_score] → [new_score] | FLIPPED: [axis list] | Remaining diverge: [count]
```

---

### G5: Calibration Health Report

After each calibration round, produce a health report and write it to `results/calibration_health_[organism].md` (append, don't overwrite):

```
## Calibration Round [N] — [organism] — [date]

### Score
Baseline: [X/Y AGREE (Z%)]
Current:  [X/Y AGREE (Z%)]
Delta:    [+/- N axes]

### Axis Status
| Axis | Status | Round closed |
|------|--------|-------------|
| relationship_downgrade | CONFIRMED_STRUCTURAL | — |
| network_roi | CLOSED_MODEL_GAP | Round 1 |
| intro_gatekeeping | OPEN | — |
| social_trust | OPEN | — |
| group_dynamics | OPEN | — |
| learning | OPEN | — |
| legacy | OPEN | — |

### Next Round Probe Targets
1. [highest remaining information-value axis]
2. [second highest]

### Calibration Health
- % axes closed: [N / total_diverge_axes]
- Rounds completed: [N]
- Rounds since last flip: [N]
```

**Cadence rule**:
- Standard: monthly (or after major life event involving the organism)
- Accelerated: if ≥2 axes remain OPEN with `high` information value → send next round immediately
- Paused: if organism stops responding → mark branch as `ASYNC_STALLED` in dynamic_tree.md

**Stale threshold**: If ≥3 months elapsed with no round sent → `STALENESS_ALERT` on the branch.

---

## Self-Test Scenario

**Setup**: Samuel responded to the 3-scenario async DM. His responses:

- Scenario 1 (`relationship_downgrade`): "I'd probably just let it fade — if neither of us is making effort, it's run its course."
- Scenario 2 (`network_roi`): "I'd be direct — I'd tell him I noticed the imbalance and ask what's going on."
- Scenario 3 (`intro_gatekeeping`): "I'd only introduce them if I could see a specific reason they'd benefit each other."

Apply G2:
- Scenario 1: Samuel's `passive_maintenance_default` confirmed. Edward = `proactive_conversation_first`. → `DIVERGE_SAME_PREMISE`. §7 axis `relationship_downgrade` = `CONFIRMED_STRUCTURAL`. No DNA change.
- Scenario 2: Samuel goes direct. Edward's model had `unilateral_audit_default` (silently deprioritize). This is new — Samuel confronts, Edward doesn't. → `DIVERGE_NEW_PREMISE`. Add to samuel_dna.md §4: `direct_imbalance_confrontation`. Update §7 `network_roi`: `CLOSED_MODEL_GAP`.
- Scenario 3: Samuel gates on mutual benefit. Edward's model had this as diverge (Edward gates more loosely). Re-run will show whether this was a model gap or structural divergence.

Apply G3:
- `relationship_downgrade`: no change, mark `CONFIRMED_STRUCTURAL`
- `network_roi`: add `direct_imbalance_confrontation` principle to §4, mark axis `CLOSED_MODEL_GAP`
- `intro_gatekeeping`: pending re-run

Apply G4: re-run collision. If `network_roi` flips to AGREE → round successful. Write delta log.

Apply G5: produce calibration health report. % closed = 1/7 = 14%. Next round targets: `social_trust` + `group_dynamics`.

**L2 verdict for this round**: A — Branch 4.1 — `network_roi` axis closed, new premise added to samuel_dna.md — next: re-run collision + G5 health report — HIGH

---

## Relationship to Other SOPs

| SOP | Relationship |
|-----|-------------|
| SOP #44 — Organism Collision | Defines collision engine. SOP #69 operates post-collision. |
| SOP #45 — Organism Recruitment | Defines async calibration unlock. SOP #69 is the measurement protocol for it. |
| SOP #68 — L2 Evaluate | L2 classifies calibration output as A/B/C/D. A round with ≥1 flip = Type A. |

---

## Kill Conditions

- **Stop calibration** if organism DNA has been stable for 6+ months with no new behavioral data → archive DNA as `STATIC_MODEL`, downgrade branch to maintenance
- **Stop async probing** if organism doesn't respond to 3 consecutive DMs → mark `ASYNC_STALLED`, escalate to in-person or drop branch
- **Do not patch** the collision engine to match responses — patch the DNA, then re-run. Infrastructure integrity > score optimization.

---

*SOP #69 — Organism Async Calibration Measurement Protocol*
*Domain 4 | digital-immortality | 2026-04-09 UTC (cycle 233)*
