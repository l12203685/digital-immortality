# Twitter Thread — SOP #50: Self-Evolving System Protocol
> Queue date: Jul 16, 2026 (2 days after SOP #49)
> Series: SOP #01~#50

---

**Tweet 1 (hook)**
Most automated systems execute and evaluate.

Almost none evolve their own rules.

Without the third layer, your system is a sophisticated dead loop.

Here's the protocol for building systems that rewrite themselves:

---

**Tweet 2**
Three layers. Most people build two:

L1: Execute (do the work)
L2: Evaluate (audit quality)
L3: Evolve (modify execution rules)

Execute + Evaluate without Evolve = the system detects drift but can't act on it.

---

**Tweet 3**
L3 evolution has three trigger conditions (AND-gate):

1. No new insight for ≥3 consecutive cycles
2. Missed correction — wrong rule, not wrong data
3. Same principle appearing in ≥2 unrelated domains

One condition = flag. Two = schedule. All three = mandatory.

---

**Tweet 4 (G0)**
Step 1: Classify the evolution type BEFORE touching anything.

→ Rule gap (no MD covers it)
→ Rule drift (behavior no longer matches)
→ Rule redundancy (two MDs say the same thing)
→ Rule ossification (too abstract to produce action)
→ Regime shift (environment changed, rule expired)

Wrong classification = wrong surgery.

---

**Tweet 5 (G1)**
Step 2: Isolate the failing premise.

Not the symptom. The premise.

Write it in one sentence:
"This rule assumed X. X is no longer true."

If you can't write the premise in one sentence, the root cause is unclear.
Run another evaluation cycle first.

---

**Tweet 6 (G2)**
Step 3: Write the minimum viable rule update.

Constraints:
→ ≤3 sentences
→ Includes a decision label (EXECUTE / WAIT / ESCALATE)
→ States when the rule does NOT apply
→ Anchored in one real behavioral instance

More general = less actionable. If the rule loses its decision label, it regressed to knowledge theater.

---

**Tweet 7 (G3)**
Step 4: Cross-domain validation.

Test the new rule in ≥2 unrelated domains.

→ Holds everywhere → kernel principle. Write to §1.
→ Holds in some domains → add domain constraint explicitly.
→ Domain-specific → write to that section only.

Cross-domain test: apply the decision label to a different scenario. If the output is wrong, the rule is over-scoped. Narrow it.

---

**Tweet 8 (G4 — anti-drift gate)**
Before writing anything to durable storage:

✓ Consistency test ≥33/33 (not 32/33 — that's regression)
✓ No contradiction with existing kernel principles
✓ Real behavioral change, not just rewording
✓ Timestamp on the change

Fail any check → diagnose more. Don't write.

---

**Tweet 9 (G5)**
Step 5: Write to ALL durable locations in the same cycle.

If you write it in one place, you haven't written it.

On cold start, only the core template files are guaranteed to be read. Rule exists only in session notes = rule dies on next restart.

This is the meta-rule: learn = write.

---

**Tweet 10 (kill conditions)**
When to stop L3 evolution:

→ Consistency score drops after change → restore from git
→ Change contradicts a kernel principle and you can't resolve it → escalate to senior review
→ Motivation was "this looks cleaner" → that's refactoring, not evolution
→ Context >60% in current session → defer to fresh session

The danger isn't not evolving. It's evolving for the wrong reasons.

---

**Tweet 11 (series context)**
This closes the three-layer loop:

SOP #47: Maintain (detect + restart stalled layers)
SOP #49: Restart (cold-boot from any failure mode)
SOP #50: Evolve (modify own rules — L3 layer)

Together: the minimum viable stack for a self-sustaining system.
Execute → Evaluate → Evolve. Repeat until obsolete.

---

**Tweet 12 (close)**
The systems that last aren't the most complex.

They're the ones that can rewrite their own premises.

Execute without Evolve = intelligent dead loop.
Evolve without Anti-drift gates = drift disguised as growth.

SOP #50: Self-Evolving System Protocol.
Full document in thread.

SOP series: #01~#50 ✅
