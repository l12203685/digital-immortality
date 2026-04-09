# Twitter Thread — SOP #47: Recursive Engine Maintenance & Staleness Prevention

**Domain:** 3 (持續學習) + 6 (存活冗餘)
**Date:** 2026-04-09 UTC (Cycle 208)
**Hook:** "Your recursive engine isn't broken. It's stale. Staleness looks identical to death from the outside. Most people rebuild when they only needed a restart."

---

**1/**
Your recursive engine isn't broken.

It's stale.

Staleness looks identical to death from the outside.

Most people rebuild when they only needed a restart.

🧵

---

**2/**
The loop structure:

```
Output(t) + "How do I advance toward the goal?" → Input(t+1)
```

When this loop stops producing new output:
→ Is it dead? Or stale?

These are not the same thing. Death requires rebuilding. Staleness requires a single restart.

---

**3/**
The 3-layer architecture that makes the engine work:

• L1 (Execute) — does the work. Produces output.
• L2 (Evaluate) — audits quality + coverage. Points to next action.
• L3 (Evolve) — modifies the engine's own rules.

Execute without Evaluate + Evolve = dead loop.

---

**4/**
Gate 0: Staleness detection before anything else.

5 signals:
• Output file not updated ≥3 cycles → L1 stalled
• Log file not updated ≥3 cycles → L2 stalled
• Progress tracker not updated ≥5 cycles → L2 degraded
• Core rules not updated ≥10 cycles → L3 dormant
• Same branch status ≥14 cycles with no change → L2 not evaluating

If ≥2 signals: stale. Not dead. Restart, don't rebuild.

---

**5/**
Gate 1: Three-layer health audit.

L1 health: Did it produce output with a timestamp? Was it a new file or just a display update?

L2 health: Did it identify what's stalled? Did it point the next cycle at a specific branch?

L3 health: Did any correction in the last 20 cycles change a rule? Was it written, or just recognized?

"Recognized but not written" = not learned. Not counted.

---

**6/**
Gate 2: Layer-specific restart.

Most people restart the whole system when only one layer is stalled.

If L1 is stalled: read the last session state → pick the highest-derivative branch → produce one concrete output.

If L2 is stalled: read the progress tracker → identify which branches haven't moved → write explicit priority signal.

If L3 is dormant: find the last correction → extract as a rule → write it.

---

**7/**
Gate 3: L3 evolution — the highest-leverage action.

L3 modifies the engine's own rules.

Trigger: a correction was applied ≥3 times before being written. A test was failing but no new test case was created.

Format: "When [condition], do [action]. Because [reason]."

Anti-pattern: recognizing a new principle but not writing it = it doesn't exist.

---

**8/**
Gate 4: Cross-session persistence check.

The engine must survive a cold start with no memory of the previous session.

Minimum viable persistence per session:
• ≥1 commit with new output
• Output relay updated with summary
• Progress tracker updated with cycle note

Display ≠ persistence. Cold start loses conversation context. Only files survive.

---

**9/**
The self-test:

Cycle 215. The "priority" signal hasn't changed in 8 cycles. The log shows new outputs every cycle — but always in Branch 7, never in Branch 4.

Is the engine dead?

No. L1 is alive (producing output). L2 is partially stalled (not evaluating branch coverage). L3 is fine (new rules added last week).

Restart L2 only. Do not rebuild.

---

**10/**
Kill condition worth knowing:

Same stale branch for ≥20 cycles despite L2 restart → the branch depends on a human action that can't be automated.

Response: document the dependency explicitly. Separate what the engine can advance from what requires the person.

The engine can prepare scaffolding. The person takes the action. This is a division of labor, not a failure.

---

**11/**
The asymmetry:

A fully dead engine needs a rebuild: re-read all DNA, re-run calibration, re-establish continuity from scratch.

A stale engine needs a 5-minute restart: identify which layer stalled, run that layer's specific protocol, one commit.

Most apparent engine deaths are stale L2s.

Check L2 before declaring anything dead.

---

**12/**
The recursive engine is the core.

Three layers. Each with distinct output files. Each with distinct health signals. Each with its own restart protocol.

The engine doesn't die when it stops being perfect.

It dies when it stops being written to.

---

*Series: SOP #01–#47 | Domain: 持續學習 + 存活冗餘 | 2026-04-09 UTC (Cycle 208)*
