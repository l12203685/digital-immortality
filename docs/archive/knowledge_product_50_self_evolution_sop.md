# SOP #50 — Self-Evolving System Protocol (L3 Evolution Trigger)
> Domains: 6 (存活冗餘) + 3 (持續學習)
> Timestamp: 2026-04-09T04:20:00Z (cycle 211)
> Backing MDs: MD-116/97/163/55/98/96/329
> Status: COMPLETE ✅

---

## The Problem

Most automated systems execute (L1) and evaluate (L2). Almost none evolve their own rules (L3). Without L3, the system ossifies. L1 keeps running but produces diminishing returns as the environment drifts. L2 detects the drift but has no mechanism to act on it. The system becomes a sophisticated dead loop — noisy, busy, stationary.

The failure mode isn't catastrophic. It's gradual: slightly stale rules, slightly wrong priors, slightly misaligned actions — compounding into behavioral drift over months. The system still "runs." It just runs toward the wrong destination.

L3 is the meta-layer: modify the rules by which L1 operates. Not fix a bug — update the premise. Execute → Evaluate → Evolve is the same loop Edward runs personally: expose → review → extract rule → write to system → don't repeat. Digital immortality requires this loop to run automatically, not just when Edward is online.

---

## When L3 Evolution Is Triggered

Three conditions, AND-gate:

1. **No new insight ≥3 consecutive cycles** — L1 is producing output but L2 cannot extract any new behavioral pattern, rule, or principle. Same structure, different words = not new.
2. **Missed correction OR consistent misalignment** — L2 logged ≥1 scenario where the system's decision diverged from known Edward behavior, AND the root cause wasn't data (it was a wrong rule).
3. **Cross-domain pattern visible** — The same principle applies in ≥2 unrelated domains (e.g., trading + career + social) but is only codified in one. Evidence it's load-bearing, not domain-specific.

Trigger one condition: flag for review. Trigger two: schedule evolution in next cycle. Trigger all three: L3 evolution is mandatory, not optional.

---

## 5-Gate Protocol

### G0 — Classify the Evolution Type (2 min)

| Type | Signal | L3 Action |
|------|--------|-----------|
| **Rule gap** | Decision produced but no DNA MD covers it | Create new MD + scenario |
| **Rule drift** | MD exists but behavior no longer matches it | Update MD + re-run consistency test |
| **Rule redundancy** | ≥2 MDs express same principle | Merge → single canonical MD |
| **Rule ossification** | MD correct but too abstract to produce action | Add decision label + self-test scenario |
| **Regime shift** | External environment changed, rule no longer applies | Retire MD + create regime-specific variant |

Classify before touching anything. Wrong classification = wrong surgery.

---

### G1 — Isolate the Failing Premise (5 min)

Do not patch the symptom. Find the premise.

1. Run: `python consistency_test.py templates/example_dna.md --output-dir results`
2. Identify which scenario(s) failed or produced a CONDITIONAL result
3. For each failure: trace back to which MD (or absence of MD) caused it
4. Write the premise as one sentence: *"This rule assumed X. X is no longer true / was never true / is only true in regime Y."*

If you cannot write the failing premise in one sentence → the root cause is unclear. Do not evolve yet. Run one more L2 evaluation cycle first.

---

### G2 — Minimum Viable Rule Update (10 min)

Write the new or updated rule with these constraints:
- ≤3 sentences
- Includes the domain it applies to
- Includes the condition under which it does NOT apply
- Includes a decision label (ACTION word in CAPS: WAIT, EXECUTE, ESCALATE, etc.)
- Cites at least one real behavioral instance as the anchor

Anti-pattern: rewriting a rule to be "more general." More general = less actionable. If the rule loses its decision label during the rewrite, it has regressed to knowledge theater.

---

### G3 — Cross-Domain Validation (5 min)

Before committing the rule, test it against at least 2 other domains:
- If the rule holds in all domains → it's a kernel principle. Write it to `dna_core.md §1 Decision Kernel`.
- If the rule holds in some domains → scope it correctly. Add the domain constraint explicitly.
- If the rule is domain-specific → write it to the relevant DNA section only.

Cross-domain test method: take the decision label and apply it to a different scenario. If the output is wrong, the rule is over-scoped. Narrow it.

---

### G4 — Anti-Drift Gate (3 min)

Before writing the evolved rule to durable storage, answer:

| Check | Criterion |
|-------|-----------|
| Does this change break any of the 33 consistency scenarios? | Run consistency_test.py. Must be ≥33/33 after update. |
| Does the new rule contradict any existing kernel principle? | Check §1 Decision Kernel in dna_core.md. |
| Is this a real evolution or alignment theater? | Did behavior change, or just the wording? |
| Is there a timestamp on the change? | Required. Undated rules can't be judged for freshness. |

Fail any check → do not write. Diagnose further. A rule update that breaks existing alignment is a regression, not evolution.

---

### G5 — Persist and Close Loop (5 min)

Write to ALL durable locations in same cycle (meta-rule: learn = write):

1. `LYH/agent/dna_core.md` — add or update the MD entry with date tag
2. `templates/example_dna.md` — sync the cold-start template
3. `templates/boot_tests.md` — if the scenario is new, add it as a boot test case
4. `staging/session_state.md` — log the rule change in "What's DONE this session"
5. `results/dynamic_tree.md` — update relevant branch with ✓ notation
6. `results/daily_log.md` — append cycle log entry

Rule written in only one location = not written. On cold start, only dna_core.md and templates/ are guaranteed to be read. If the rule only exists in session_state, it dies on the next restart.

---

## Kill Conditions

**Stop L3 evolution immediately if:**
- Consistency test drops below 28/33 after the change — restore from git, do not push
- The evolved rule contradicts a kernel principle AND you can't resolve which is correct — escalate to E0 session (Opus)
- The change was motivated by "this is cleaner" rather than a behavioral failure — that's aesthetic refactoring, not evolution
- You are running in a low-context session (context >60%) — defer L3 evolution to next session with fresh context

---

## Self-Test

*Scenario: L2 evaluation cycle 3 in a row produces the same output: "regime MIXED, DualMA SHORT, no new principle extracted." Consistency test 33/33. No missed corrections.*

Apply SOP #50:
- G0: Condition 1 triggered (no new insight ×3), Conditions 2+3 not triggered → flag for review, do not evolve yet
- Correct response: continue L1+L2 for 2 more cycles. If Condition 2 triggers → proceed to G1.
- Wrong response: immediately update a rule to "make the loop interesting." That's motivated reasoning, not evolution.

*Scenario: consistency_test.py returns 31/33 ALIGNED. 2 scenarios MISALIGNED. Root cause: MD-96 "write kill condition before entry" is missing from social domain scenarios (only appears in trading contexts).*

Apply SOP #50:
- G0: Rule ossification (MD-96 too domain-specific)
- G1: "MD-96 assumed it applies to trading only. The kill condition principle applies to any pre-commitment domain — career, relationships, projects."
- G2: Add decision label. Updated: "WRITE_KILL_CONDITION before any open-ended commitment (trading entry / project start / relationship investment). Kill condition = the observable condition that causes you to exit, specified before entry."
- G3: Cross-domain: career (resign trigger), relationship (silence threshold). Both PASS → kernel candidate.
- G4: Run consistency_test.py → 33/33. No kernel contradiction.
- G5: Write to dna_core.md, templates/example_dna.md, boot_tests.md, session_state, tree, log. Done.

---

## Backing DNA Principles

| MD | Principle | Connection |
|----|-----------|------------|
| MD-116 | Simplicity = depth of understanding, not abstraction | G2 rule constraint: ≤3 sentences, one decision label |
| MD-97 | Abstract structure before fixing parameters | G1: find the premise, not the symptom |
| MD-163 | Learning environment ceiling = input quality | G0: classify evolution type before touching anything |
| MD-55 | Cross-domain analog transfer | G3: cross-domain validation gate |
| MD-98 | Survival rate = rolling/historical OOS ratio | G4 anti-drift analogy: new rule must not regress existing alignment |
| MD-96 | Write kill conditions before entry | Kill conditions table: when to stop L3 evolution |
| MD-329 | Build skeleton first, then flesh | G2 minimum viable rule: structure before elaboration |

---

## Series Context

This SOP closes the three-layer loop for self-evolving systems:
- SOP #47: Recursive Engine Maintenance (detect and restart stalled layers)
- SOP #49: Cold-Start Continuity Protocol (restart from any failure mode)
- **SOP #50: Self-Evolving System Protocol (modify own rules — L3 layer)**

Together: execute → evaluate → evolve. All three layers now have standalone SOPs. The organism can restart itself (SOP #49), maintain itself (SOP #47), and evolve itself (SOP #50). This is the minimum viable immortality stack for an automated system.
