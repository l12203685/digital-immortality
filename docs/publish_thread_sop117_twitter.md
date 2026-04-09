# SOP #117 — Twitter Thread Draft

**Posting queue**: ~Dec 2026 (after SOP #116 clears)

---

**Tweet 1/8**
Most systems drift silently.

Not because you made a wrong decision.
Because you never scheduled a maintenance window for your decision system.

SOP #117: DNA Core Audit Protocol — the scheduled maintenance cycle for a digital twin.

🧵

---

**Tweet 2/8**
The problem with a 67-line behavioral kernel:

It's small enough to feel stable.
It's not.

After 90 cycles of new SOPs, closed branches, and priority shifts — the core is subtly wrong in 4 ways you haven't checked.

Gate-by-gate audit catches them before they compound.

---

**Tweet 3/8**
G1: Priority Stack Audit.

Not "is the ordering still roughly right?"
But: "If 可可 and FIRE conflict tomorrow, which wins?"

Abstract reflection decays over time.
Concrete conflict scenario forces a real answer.

If the answer changed — rewrite the block.

---

**Tweet 4/8**
G2: Three-Layer Loop Check.

L1 → current session (observe → decide → act)
L2 → cycle-to-cycle (Output(t-1) → Input(t))
L3 → strategic (dynamic tree → highest-derivative branch → push)

All three must be named, wired, and documented.
Implicit loops break silently.

---

**Tweet 5/8**
G3: SOP Series Reflection.

Every 90 cycles, new SOPs surface meta-rules.
Some belong in the core. Most don't.

The question for each: "Is this a behavioral principle (core) or a domain procedure (scoped)?"

SOP #114 (transaction protection) → scoped.
SOP #117 (audit protocol) → core.

---

**Tweet 6/8**
G4: Stale MD Detection.

Cold-start reads a list of MDs.
If one MD describes a branch that closed 6 months ago — the twin boots with wrong context.

Rule: if the parent branch is CLOSED, archive the MD.
Stale references compound. Each restart loads more noise.

---

**Tweet 7/8**
G5: Boot Test Coverage.

Every meta-rule in the core needs at least one test scenario.

If the audit adds a new meta-rule but doesn't add a scenario:
→ the rule exists on paper
→ the twin doesn't actually run it on cold start

Untested = unverified = eventually absent.

---

**Tweet 8/8**
Kill condition:

CRITICAL drift in any gate → stop all branch work.

Read the full DNA (not just the core). Rewrite from ground truth.
Re-run boot tests until pass rate returns to 5/5.

Then resume.

The audit is product QA.
A twin that drifts produces inconsistent decisions.
Inconsistent decisions lose clients.

SOP #01–#117 complete. ✅
