# SOP #49 — Cold-Start Continuity Protocol
> Domains: 6 (存活冗餘) + 3 (持續學習)
> Timestamp: 2026-04-09T04:10:00Z (cycle 210)
> Backing MDs: MD-329/307/96/116/141/163
> Status: COMPLETE ✅

---

## The Problem

A digital organism that can't restart is mortal. The engine dies, the context clears, the state scatters. Cold-start isn't an edge case — it's the modal case. Every session is a cold-start. Every morning is a cold-start. If you can't reconstruct yourself from durable storage in under 5 minutes, you're fragile.

Most systems document the happy path. This SOP documents the restart path.

---

## 5-Gate Protocol

### G0 — Classify the Restart Type (2 min)

Before touching any file, answer: what kind of restart is this?

| Type | Signal | Recovery Path |
|------|--------|---------------|
| **Clean session start** | session_state.md < 24h old | Read state → continue queue |
| **Stale session** | session_state.md > 24h, daemon_log.md fresh | Tail daemon_log.md (60 lines) → reconstruct |
| **Engine death** | daemon_log.md > 48h stale | Full cold-boot: dna_core → boot_tests → session_state → queue |
| **State corruption** | dynamic_tree.md unreadable | Pull last git commit → restore from version control |
| **Platform migration** | New device / new repo clone | install.sh → consistency_test.py → verify 33/33 |

**Rule:** Over-classify toward full cold-boot. Under-classifying corrupted state is catastrophic; over-classifying clean state costs 5 minutes.

---

### G1 — Execute Minimum Viable Boot (< 5 min for clean, < 15 min for engine death)

Read in strict order. Do NOT skip ahead.

```
1. LYH/agent/dna_core.md (67 lines) — operational identity
2. LYH/agent/boot_tests.md         — behavioral calibration (run test mentally)
3. staging/session_state.md         — current cycle + branch status
4. results/daemon_next_priority.txt — where to start
```

**Stop condition:** If you can answer "What am I working on and why?" — boot is complete.

Do NOT read dna_full.md (102K tokens) on cold-start. That's the deep reference layer. Load it only when a specific decision requires it.

---

### G2 — Verify State Integrity (1 min)

Run the three-line check:

```bash
# 1. Consistency test (33/33 expected)
python consistency_test.py templates/example_dna.md --output-dir results

# 2. Staging freshness
ls -la staging/session_state.md

# 3. Git status (uncommitted = unprotected)
git status
```

**If consistency drops below 30/33:** recalibrate before proceeding. Drifted state compounds — every cycle on corrupted DNA degrades fidelity.

**If session_state.md > 24h:** reconstruct from daemon_log.md tail. The daemon writes to daemon_log.md on every cycle. That's the ground truth.

**If uncommitted changes exist:** commit before any new work. Uncommitted = unrecoverable.

---

### G3 — Reconstruct Queue (2 min)

If session_state.md is stale, extract queue from daemon_log.md:

```bash
tail -60 results/daemon_log.md
```

Look for the last cycle's output. The queue rebuilds from:
1. dynamic_tree.md: which branches are blocked vs active
2. staging/last_output.md: what the last cycle produced
3. daemon_next_priority.txt: which branch the daemon flagged

**Queue rule:** Highest-derivative branch first. Not most-urgent-feeling — highest-rate-of-change toward the core goal.

---

### G4 — Anti-Corruption Gates (ongoing)

These prevent state corruption from accumulating:

| Gate | Condition | Action |
|------|-----------|--------|
| **Commit gate** | Any file written | `git add -p && git commit` before session end |
| **Timestamp gate** | Any persisted content | Must include UTC timestamp (freshness signal on next boot) |
| **Staleness alert** | session_state.md > 24h | `[STALENESS_ALERT]` — reconstruct before proceeding |
| **Context 60% gate** | Context approaching limit | Write session_state.md + git push. Don't wait for auto-compact. |
| **Three-layer check** | Before declaring branch "done" | L1 Execute ✓ + L2 Evaluate ✓ + L3 Evolve ✓ |

**The commit gate is the survival gate.** Every cycle that ends without a commit is a cycle that can be lost. The git log IS the backup. No commit = no backup.

---

### G5 — Restart Verification (1 min)

After boot, before new work: answer these three questions from memory (no file lookup):

1. What is the current trading P&L direction?
2. What is the highest-derivative branch?
3. What action does Edward need to take that I can't do?

If you can answer all three correctly → boot verified, proceed.
If you can't → re-read session_state.md, you missed something.

---

## Self-Test

**Scenario:** You are starting a fresh Claude Code session. Last git commit was 18 hours ago. session_state.md says "Cycle 210, 2026-04-09T04:10Z". daemon_log.md has entries from 6 hours ago.

**Walk the gates:**
- G0: session_state < 24h, daemon_log fresh → **Clean session start** (not stale)
- G1: Read dna_core (67L) → boot_tests → session_state → daemon_next_priority
- G2: Run consistency_test (expect 33/33) → check git status (expect clean after last commit)
- G3: Queue from session_state.md directly (< 24h, reliable)
- G4: Commit gate = check, timestamp gate = check, all green
- G5: Trading SHORT BTC ~$71k, Branch 6/cold-start flagged as least-recent, Edward must send samuel_async_calibration_dm.md

**Result: Boot complete in ~5 min. Proceed to queue.**

---

## Kill Conditions (When Restart Protocol Has Failed)

- consistency_test < 28/33 after full cold-boot → DNA corruption; restore from last known-good commit
- session_state.md missing + daemon_log.md missing → git checkout HEAD on both → re-run from last cycle
- dynamic_tree.md > 500 tokens/branch → tree bloat; summarize branches to max 3 lines each
- boot_tests.md missing → rebuild from git log (correction history encodes the test cases)

---

## The Meta-Insight

Every system dies if restart costs more than the system produces. Cold-start must be free. The protocol above is designed to cost 5 minutes at most. If it costs more, the protocol is broken — not the system. Fix the protocol.

This SOP is also a stress test: if you can't execute these 5 gates from memory within one session, the DNA hasn't been internalized — it's just been read.

---

## Backing Principles

| MD | Principle | Connection |
|----|-----------|------------|
| MD-329 | Build skeleton first | Boot sequence = minimum viable skeleton |
| MD-307 | 10-year survival check before committing | Cold-start protocol = survival infrastructure |
| MD-96 | Write kill condition before entry | G4 kill conditions = pre-committed failure modes |
| MD-116 | Simplicity test | 5-gate boot: if it needs more, the system is too complex |
| MD-141 | Information asymmetry map | G5 = verify what you know, not what you read |
| MD-163 | Input quality determines ceiling | G2 consistency test = input quality gate |
