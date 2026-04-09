# Twitter Thread — SOP #110: DNA Quality Audit & Expansion Rate Control

> Status: DRAFT | Created: 2026-04-09T16:42Z | Queue: Nov 2026

---

**Tweet 1 (Hook)**
Your AI twin has 372 micro-decisions.

Last month it had 200.

Organism agreement rate: 68% → 27%.

More DNA ≠ better alignment. Here's why that's the signal that matters.

🧵 SOP #110: DNA Expansion Rate Control Protocol

---

**Tweet 2 (The Problem)**
Every JSONL distillation cycle adds 3 micro-decisions.

At scale, this creates:

- Redundant MDs (MD-14 vs MD-370 overlap on stop-loss logic)
- Contradictory MDs (early expansion rules vs late-stage pruning rules)
- Calibration regression in second organisms

More entries ≠ more fidelity.

---

**Tweet 3 (The Signal)**
Branch 4.1 caught this: Samuel organism agreement rate.

Baseline: 68% AGREE across 22 scenarios.
After +157 MDs: 27% AGREE.

That's not more specificity. That's personality noise.

DNA that says too much says nothing.

---

**Tweet 4 (The Gate)**
SOP #110 defines a 5-gate DNA quality audit:

G0: MD count milestone (every +50 MDs)
G1: Redundancy scan (semantic similarity >80% between any 2 MDs)
G2: Contradiction scan (opposite prescriptions for same trigger)
G3: Organism calibration regression test (run before + after expansion block)
G4: Cold-start alignment delta (consistency test before vs after)
G5: Merge/retire decision

---

**Tweet 5 (G0 — Trigger)**
Audit triggers when:

- MD count crosses +50 milestone (200, 250, 300, 350, 400...)
- Organism agreement rate drops >15% in any single calibration
- Cold-start alignment drops below 30/33 deterministic scenarios

This cycle: 372 MDs → G0 triggered (350 checkpoint reached, then 372).

---

**Tweet 6 (G1 — Redundancy)**
Redundancy scan logic:

Read all MDs in a domain cluster (trading / career / learning / relationships).

Flag pairs where:
- Same trigger condition
- Same prescribed action
- Different examples

Result: Merge into one MD with multiple source examples.

---

**Tweet 7 (G2 — Contradiction)**
Contradiction scan is harder.

Example contradiction:
- MD-14: "wrong regime = no edge, accept tiny loss"
- MD-51: "確定不會輸=100%押"

Are these contradictory or complementary?

The test: "What does the twin do when regime is wrong but confidence is 100%?"

If answer is ambiguous → flag for explicit priority ordering.

---

**Tweet 8 (G3 — Organism Test)**
Run calibration test before expansion block begins.

Run same test after 50 MDs added.

Delta threshold: >10% agreement rate drop = expansion paused.

Current state: Branch 4.1 triggered this retroactively.
Fix: Samuel DM with 3 new scenarios (human-gated action).

---

**Tweet 9 (G4 — Cold-Start)**
Consistency test runs every cycle.

But G4 is a retrospective delta:

Take consistency score from before expansion block.
Compare to current.

If deterministic alignment dropped (33→30): investigate.
If expected-MISALIGNED count changed: diagnose which new MD caused it.

---

**Tweet 10 (The Output)**
G5 decision matrix:

| Issue | Action |
|-------|--------|
| Redundant pair | Merge into 1 MD, retire 1 |
| Contradiction | Add explicit priority rule |
| Calibration regression | Pause distillation; recalibrate organism |
| Cold-start regression | Identify trigger MD; rewrite or retire |

Output: a DNA_audit_log entry with timestamp + action taken.

---

**Tweet 11 (Anti-Pattern)**
Anti-pattern: "More MDs = more complete twin."

This assumes quality scales with quantity.

It doesn't.

The twin is complete when it makes the same decisions in the same way — not when it has the most documented rules.

Alignment rate > MD count.

---

**Tweet 12 (Close)**
The paradox of digital immortality:

To preserve yourself perfectly, you must also prune yourself.

Too many rules = personality noise.
Too few rules = behavioral drift.

The goal is the minimum viable DNA that produces maximum decision fidelity.

SOP #110: full audit protocol →
[link]
