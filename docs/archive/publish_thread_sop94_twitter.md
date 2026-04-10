# Twitter Thread — SOP #94: Cross-Instance Calibration Maintenance Protocol
> Slot: Sep 7, 2026

---

**Tweet 1/8 (hook)**
You hit 100% cross-instance agreement.

Two instances of you → same decisions on 39/39 scenarios.

Problem: that's a measurement, not a guarantee.

Next week you update the DNA. Next month a new model ships.

How do you know the 100% holds?

You don't. Unless you have a maintenance protocol.

---

**Tweet 2/8**
SOP #94: Cross-Instance Calibration Maintenance.

Triggers:
- T1: Quarterly (Jan/Apr/Jul/Oct)
- T2: After any DNA write cycle
- T3: New model version deployed
- T4: Boot test expansion (≥3 new scenarios)
- T5: Agreement drops below 95%

The difference between a test and a system: a system has triggers.

---

**Tweet 3/8**
Classification ladder:

97-100% → STABLE. Log. No action.
90-96% → WATCH. Re-run after next DNA cycle.
80-89% → DRIFT. G3 diagnostic. Find slipping scenarios.
<80% → CRITICAL. Halt all DNA writes. Emergency recovery.

The ladder tells you how loud to react.

---

**Tweet 4/8**
When score drops, three root causes:

A — DNA corruption (contradictory rules)
B — LLM-boundary scenarios (formula/inference — permanent; accept it)
C — New scenario domains with no DNA anchor

Most people try to fix B. The answer is: document it.
The real work is C — writing the missing anchor.

---

**Tweet 5/8**
Emergency protocol (score < 80%):

STOP all DNA writes.
Run individual scenario diagnostics.
Identify root cause (corruption / model shift / coverage gap).
Resolution: rollback, re-validate, or anchor expansion.
2 consecutive clean runs at ≥97% before resuming.

Constraint before correction.

---

**Tweet 6/8**
Full monthly calibration stack (now complete):

SOP #80 — Deterministic: 33/33 rule-based scenarios
SOP #91 — New life decisions encoded from JSONL
SOP #94 — Cross-instance: 97-100% agreement maintained

Each catches a different failure mode.
All three together = no drift survives a month.

---

**Tweet 7/8**
Self-test:

New model ships. Cross-instance drops to 87%.
Trigger: T3. Classification: DRIFT.
Action: run individual diagnostics → 5 slipping scenarios.
Classify: 3 Category B (LLM-boundary, accept), 2 Category C (missing anchors).
Write 2 anchors. Re-run → back to 97%.

That's the protocol working.

---

**Tweet 8/8**
100% cross-instance agreement is a result.

The maintenance protocol is what makes it a property.

SOP #94: Cross-Instance Calibration Maintenance.
Monthly stack: SOP #80 + #91 + #94.
SOP #01–#94 complete.

The digital twin stays calibrated not because you checked once — but because you have a system that keeps checking.

---
*Thread end. Post as-is. Do not edit on posting day.*
