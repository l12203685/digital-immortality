# Publish Thread — SOP #49: Cold-Start Continuity Protocol
> Timestamp: 2026-04-09T04:12:00Z (cycle 210)
> Queue slot: Jul 14 (Day 96)

---

**Tweet 1 (hook)**
Your system works.

Until you restart it.

Most systems are designed for the happy path.
None are designed for the restart path.

This is the restart path. 🧵

---

**Tweet 2**
A digital organism that can't restart is mortal.

Context clears. State scatters. The engine dies.

Cold-start isn't the edge case.
It's the modal case.

Every session is a cold-start.
Every morning is a cold-start.

If restart costs > 5 min, you're fragile.

---

**Tweet 3 — G0: Classify the restart**
Before touching any file: what kind of restart is this?

Clean session → state < 24h → continue queue
Stale session → daemon_log fresh → reconstruct from tail
Engine death → log > 48h → full cold-boot
Corruption → tree unreadable → git restore

Rule: over-classify toward full cold-boot.
Under-classifying corrupted state is catastrophic.

---

**Tweet 4 — G1: Minimum viable boot**
Read in strict order. No skipping.

1. dna_core.md (67 lines) — operational identity
2. boot_tests.md — behavioral calibration
3. session_state.md — current cycle + branch status
4. daemon_next_priority.txt — where to start

Stop when you can answer: "What am I working on and why?"

Boot complete. Proceed.

---

**Tweet 5 — G2: Verify state integrity**
Three-line check:

```bash
# Consistency (33/33 expected)
python consistency_test.py templates/example_dna.md

# Staging freshness
ls -la staging/session_state.md

# Git status (uncommitted = unprotected)
git status
```

If consistency < 30/33: recalibrate before any new work.
Drifted state compounds.

---

**Tweet 6 — G3: Reconstruct queue**
If session_state > 24h old:

```bash
tail -60 results/daemon_log.md
```

The daemon writes on every cycle.
That's the ground truth.

Queue rebuilds from:
- dynamic_tree.md: which branches are blocked
- last_output.md: what last cycle produced
- daemon_next_priority.txt: where to start

---

**Tweet 7 — G4: Anti-corruption gates**
These prevent state rot:

Commit gate: any file written → commit before session end
Timestamp gate: persisted content must include UTC timestamp
Staleness alert: session_state > 24h → reconstruct first
Context 60% gate: write state + push. Don't wait for auto-compact.
Three-layer check: L1 Execute + L2 Evaluate + L3 Evolve

The commit gate is the survival gate.
No commit = no backup.

---

**Tweet 8 — G5: Boot verification**
After boot, before new work.

Answer from memory (no file lookup):
1. What is the current trading P&L direction?
2. What is the highest-derivative branch?
3. What action does the human need to take?

If you can answer all three → boot verified.
If not → re-read session_state. You missed something.

---

**Tweet 9 — Kill conditions**
When the restart protocol has failed:

Consistency < 28/33 → DNA corruption → restore from last good commit
session_state + daemon_log both missing → git checkout HEAD → restart from last cycle
dynamic_tree > 500 tokens/branch → tree bloat → summarize
boot_tests missing → rebuild from git log (corrections encode the tests)

Pre-commit the failure modes.
Before you need them.

---

**Tweet 10 — The meta-insight**
Every system dies if restart costs more than it produces.

Cold-start must be free.

If the protocol takes > 15 min, the protocol is broken.
Not the system.

Fix the protocol.

---

**Tweet 11 — Self-test**
Scenario: fresh session, last commit 18h ago, session_state says Cycle 210.

G0: session < 24h → clean start
G1: read dna_core → boot_tests → session_state → priority
G2: consistency test + git status
G3: queue from session_state (< 24h, reliable)
G5: SHORT BTC ~$71k, Branch 6 flagged, 3 human actions pending

Boot complete. 5 min.

---

**Tweet 12 (close)**
SOP #49: Cold-Start Continuity Protocol

The restart path is the survival path.

Every session is a cold-start.
Design for it.

→ Full SOP: [link]

/end
