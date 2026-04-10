# SOP #67 — Recursive Engine L3 Evolution Protocol
> Domain 3 (持續學習 / Recursive Engine) | 2026-04-09 UTC

## Purpose

The three-layer recursive loop is: **L1 Execute → L2 Evaluate → L3 Evolve**.
Execute without Evaluate+Evolve = dead loop. This SOP defines *when* and *how* L3 fires — how the agent modifies its own execution rules without breaking stability.

**Core axiom:** Every correction from the person = new boot test case + new distillation entry.
L3 is the formalization of this axiom into an automated protocol.

---

## Trigger Conditions (When to Fire L3)

### Hard Triggers (must fire)
1. **Correction received** — Edward corrects a decision, behavior, or output → immediately extract rule → write to ALL durable locations (CLAUDE.md, SKILL.md, dna_core.md, boot_tests.md, memory, session_state)
2. **Boot test failure** — any scenario MISALIGNED after cold start → find premise gap → patch dna_core.md → re-run until ALIGNED
3. **Consistency degradation** — was ≥33/33, now <33/33 → mandatory root cause + patch before next cycle
4. **Staleness alert** — `[STALENESS_ALERT]` in daemon_log.md for ≥3 cycles → L3: diagnose execution failure, modify daemon parameters or branch queue
5. **Revenue = 0 AND deadline within 30 days** — survival regime change → L3 reallocates branch queue toward economic branches

### Soft Triggers (should fire)
6. **Same branch stuck >5 cycles with no derivative change** — L3: declare stuck, pivot to next highest-derivative branch
7. **New anti-pattern identified** (same mistake twice) → write to SKILL.md §Anti-Patterns + boot_tests.md
8. **Cross-instance divergence** (consistency <90% on LLM test) → diagnose which premise is wrong → patch templates/dna_core.md

### Anti-triggers (do NOT fire L3)
- Paper-live ticks with no regime change (L1 only)
- SOP drafts with no behavioral correction (Branch 7 work, not L3)
- Consistency ≥33/33 with no new scenario (stable = no evolution needed)
- L3 for cosmetic changes (formatting, renaming) — not evolution, don't call it that

---

## G0: Pre-flight

Before modifying execution rules, confirm:
- [ ] Trigger is a hard trigger OR soft trigger with ≥2 confirming signals
- [ ] You can name the specific premise that is wrong (not vague "needs improvement")
- [ ] You know which durable locations need updating (checklist below)

**Minimum write set for any L3 evolution:**
| Location | What to update |
|----------|----------------|
| `LYH/agent/dna_core.md` (or `templates/example_dna.md`) | Add/modify behavioral principle |
| `templates/boot_tests.md` | Add new test case covering the gap |
| `memory/insights.json` | Distillation entry with key + timestamp |
| `staging/session_state.md` | Queue + branch status update |
| `results/dynamic_tree.md` | Branch node update |
| `SKILL.md` or `CLAUDE.md` | If meta-rule changed |

---

## G1: Diagnose the Gap

L3 evolution requires naming:
1. **What decision/behavior was wrong** (specific, not "behavior was off")
2. **Which premise in dna_core.md produced the wrong output** (cite MD number or principle section)
3. **What the correct premise should be** (one sentence, falsifiable)

Template:
```
PREMISE GAP:
- Wrong output: [specific decision or behavior]
- Faulty premise: [which MD/principle, cite line]
- Correct premise: [replacement rule, ≤1 sentence]
- Test case: [scenario + expected output with new premise]
```

Do NOT proceed to G2 if you cannot fill this template.

---

## G2: Apply Change

### Minimum viable patch
- Write the corrected premise to dna_core.md (add MD number if new, replace if update)
- Write new boot test case to boot_tests.md
- Verify: re-run `consistency_test.py templates/example_dna.md` → must maintain ≥33/33 ALIGNED

### Branch queue evolution (only for stuck-branch or survival-regime triggers)
- Demote blocked branch one slot
- Promote highest-derivative non-human-gated branch
- Write new queue to session_state.md §Queue

### Execution parameter evolution (only for daemon/staleness triggers)
- Modify `recursive_engine.py` parameters (staleness threshold, loop interval)
- Verify daemon starts cleanly after change
- Log parameter change in daemon_log.md with reason

---

## G3: Write to All Durable Locations

Same-cycle write requirement. "Recognized but not written = not learned."

Checklist:
- [ ] dna_core.md updated (or templates/example_dna.md for cold-start template)
- [ ] boot_tests.md updated with new test case
- [ ] memory/insights.json entry added (key + content + timestamp + tags)
- [ ] staging/session_state.md §What's DONE updated
- [ ] results/dynamic_tree.md node updated
- [ ] daily_log.md cycle entry updated
- [ ] git commit with all files in same commit (not separate commits)

---

## G4: Kill Conditions (When NOT to Evolve)

Stop L3 and escalate to Edward if:
- Correction contradicts an existing MD with >3 scenarios already tested ALIGNED
  → May indicate context-specific exception, not universal rule; ask Edward before patching
- Proposed new MD would make >2 existing scenarios MISALIGNED
  → Possible false positive trigger; run LLM cross-instance test first
- Consistency drops below 30/33 after patch
  → Revert immediately; something in the premise chain is wrong

---

## Self-Test Scenario

**Situation**: Consistency_test returns 32/33 ALIGNED. One new scenario (`generic_deadline_regime_shift`) is MISALIGNED.

**Apply this SOP:**
- G0: Hard trigger (consistency degradation). Specific premise: `BIAS_TOWARD_INACTION` fires even when survival deadline is <30 days, but correct behavior is `SHIFT_TO_SURVIVAL_REGIME` when deadline is imminent.
- G1: MD-96 (BIAS_TOWARD_INACTION) applies too broadly — it should yield to explicit survival deadlines.
- G2: Add MD-316 (if deadline <30d AND revenue=0 → SHIFT_TO_SURVIVAL_REGIME, override BIAS_TOWARD_INACTION). Add boot test: "survival deadline 25 days away, revenue=0" → expected=SHIFT_TO_SURVIVAL_REGIME.
- G3: Write to all 6 durable locations.
- Verify: re-run consistency_test → 33/33 ALIGNED.

**Expected output**: SHIFT_TO_SURVIVAL_REGIME ✅

---

## Backing MDs

| MD | Principle |
|----|-----------|
| MD-96 | BIAS_TOWARD_INACTION — no edge = no action |
| MD-107 | Meta-strategy escalation |
| MD-316 | Survival regime override (deadline-triggered) |
| MD-322 | Pre-committed defaults recover zero-EV decision bandwidth |
| SKILL.md rule | "Every correction from person = new boot test + distillation entry" |
| SKILL.md rule | "Three-layer loop: L1 Execute → L2 Evaluate → L3 Evolve" |

---

## Twitter Thread Draft → `publish_thread_sop67_twitter.md`

Slot: **Aug 15** | Domain 3
