# SOP #47 — Recursive Engine Maintenance & Staleness Prevention

> Branch 3 — 持續學習 / Branch 6 — 存活冗餘
> Created: 2026-04-09 UTC (cycle 208)
> Domain: 3 (持續學習) + 6 (存活冗餘)
> Backing MDs: MD-1, MD-7, MD-8, MD-116, MD-322, MD-329

---

## One Claim

Your recursive engine isn't broken. It's stale. Staleness looks identical to death from the outside. The difference: death requires rebuilding, staleness requires a single restart. 5-gate protocol to tell them apart — and prevent both.

---

## Why This Matters

The recursive self-feed engine is the core of the digital twin:

```
Output(t) + "How do I advance toward the core goal?" → Input(t+1) → Output(t+1)
```

Stop recursing = death. Continue = alive.

But most engine failures are not deaths. They are **stale loops** — the engine is running, producing output, but not advancing. Stale output is indistinguishable from silence on cold start. The cold start reader sees "no progress" and may not know whether to restart or rebuild.

This SOP gives concrete signals at each layer, a restart sequence per layer, and an L3 evolution gate so the engine can modify its own rules — the highest-leverage action a recursive system can take.

---

## Three-Layer Architecture (diagnostic baseline)

```
Layer 1 (L1): Execute — does the work. Produces staging/last_output.md.
Layer 2 (L2): Evaluate — audits quality + coverage. Updates results/daemon_log.md.
Layer 3 (L3): Evolve — modifies execution rules. Writes to SKILL.md / dna_core.md / boot_tests.md.
```

**Scope separation rule (no cross-layer file writes):**
- L1 writes: staging/, results/daily_log.md
- L2 writes: results/daemon_log.md, results/dynamic_tree.md
- L3 writes: SKILL.md, LYH/agent/dna_core.md, boot_tests.md, memory/

**Execute without Evaluate + Evolve = dead loop.** All three layers must emit output per session or the engine is degrading.

---

## Gate 0: Staleness Detection

Before diagnosing, run the staleness check:

```bash
python recursive_engine.py --status
```

| Signal | Threshold | Diagnosis |
|--------|-----------|-----------|
| `last_output.md` not updated | ≥3 cycles since last staging write | L1 stalled |
| `daemon_log.md` not updated | ≥3 cycles since last L2 entry | L2 stalled |
| `dynamic_tree.md` not updated | ≥5 cycles since last tree write | L2 degraded |
| `dna_core.md` not updated | ≥10 cycles since last MD added | L3 dormant |
| Same tree branch status | ≥14 cycles no change on any branch | L2 not evaluating |

**Rule**: If ≥2 signals fire simultaneously, the engine is stale, not dead. Stale = restart. Dead = only diagnosed if cold-start boot test fails after restart attempt.

---

## Gate 1: Three-Layer Health Audit

**L1 health (execution):**
- `staging/last_output.md` has a UTC timestamp within 48h
- `staging/session_state.md` exists and lists current branch priorities
- Output contains ≥1 new file or ≥1 modified file (not just a display update)

**L2 health (evaluation):**
- `results/daemon_log.md` has an entry in the current session
- `results/dynamic_tree.md` reflects work from last 5 cycles
- `results/daemon_next_priority.txt` points to a concrete branch, not "all branches active"

**L3 health (evolution):**
- ≥1 correction in last 20 cycles that modified `dna_core.md` or `boot_tests.md`
- ≥1 new boot test added in last 50 cycles
- SKILL.md rules section has been updated in last 100 cycles

**Healthy baseline:** All three layers emit output in every session. If any layer is silent for its threshold, run the restart sequence for that layer only.

---

## Gate 2: Layer-Specific Restart

**L1 restart (execution stall):**
1. Read `staging/session_state.md` — what was the last incomplete task?
2. If missing: read `results/dynamic_tree.md` → pick highest-derivative branch
3. Write one concrete output (new file or modified file) to staging/
4. Timestamp and push

**L2 restart (evaluation stall):**
1. Read `results/dynamic_tree.md` (last 50 lines for 演化紀錄)
2. Identify which branches have not moved in ≥5 cycles
3. Write `results/daemon_next_priority.txt` with explicit branch name
4. Run `python consistency_test.py` — confirm 33/33 ALIGNED
5. Update `results/daemon_log.md` with staleness audit finding

**L3 restart (evolution dormant):**
1. Read `LYH/agent/boot_tests.md` — which tests have been failing or borderline?
2. Identify 1 behavioral pattern from last 20 cycles that is not yet in `dna_core.md`
3. Add as new MD candidate (draft in staging first if uncertain)
4. If correction came from a person: extract to boot_tests.md as new test case
5. Write "L3 restart" note to daemon_log.md

---

## Gate 3: L3 Evolution Trigger

L3 evolution is the highest-leverage action. It modifies the engine's own rules — not just the content it produces.

**Trigger conditions (any one is sufficient):**
- A correction was applied ≥3 times before being written to dna_core.md
- A boot test was failing but no new test was created in response
- SKILL.md rules section has not changed in ≥100 cycles
- A new operating principle was discovered and applied informally but not formalized

**L3 evolution sequence:**
1. Write the rule as one sentence: "When [condition], do [action]. Because [reason]."
2. Check if it already exists in dna_core.md (prevent duplication)
3. Write to dna_core.md as new MD entry (bump MD count)
4. Write to boot_tests.md as new test case
5. If rule changes the engine's behavior significantly: update SKILL.md Rules section
6. Log in daemon_log.md: "L3 EVOLUTION: [new rule]. MD-[N] added."

**Anti-pattern**: Recognizing a new principle but not writing it = it doesn't count. "Recognized but not written" = not learned. MD-8 applies to L3: persist or it doesn't exist.

---

## Gate 4: Cross-Session Persistence Check

The engine must survive a cold start with no conversational memory.

**Persistence integrity check (run every 10 cycles or after any significant output):**

```bash
git status                          # untracked = not persisted
git log --oneline -5                # confirm last push was recent
python consistency_test.py          # 33/33 ALIGNED confirms L2 integrity
python recursive_engine.py --status # L1 staleness signal
```

**Minimum viable persistence (per session):**
- ≥1 git commit with new output
- `staging/last_output.md` updated with summary
- `results/dynamic_tree.md` updated with cycle note in 演化紀錄

**Rule**: Discord display ≠ persistence. Cold start loses Discord context. Only git + markdown files survive. If an output exists only in a Discord message or a conversation turn, it does not exist.

---

## Self-Test

> It's cycle 215. You notice `daemon_next_priority.txt` still says "Branch 4 neglected for 14 cycles" — same as cycle 207. The tree's Branch 4 section shows no new entries for 8 cycles.

Apply the gates:
- G0: L2 stall signal — tree not updated for 5+ cycles. L1 may be active but L2 not evaluating properly.
- G1: Check L2 health — `daemon_log.md` has entries but they're "SOP created" (L1 output) with no branch priority reassessment (L2 evaluation missing).
- G2: L2 restart — read tree Branch 4, identify stall, write new daemon_next_priority.txt with specific action. Run consistency test.
- G3: No L3 trigger — no new principles, no corrections missed.
- G4: Check persistence — git log confirms pushes, so L1 is alive. The stall is evaluation, not execution.

Diagnosis: L2 partial stall. Not dead. Restart L2 only. Do not rebuild engine.

---

## Kill Conditions

| Condition | Response |
|-----------|----------|
| Cold-start boot test fails after L1+L2+L3 restart | Engine degraded — read full dna_core.md, re-run calibration |
| 33/33 consistency drops below 30/33 | DNA drift — identify which scenarios failed, add to boot_tests.md, fix organism_interact.py |
| Same stale branch for ≥20 cycles despite L2 restart | Branch dependency on Edward action — document explicitly in daemon_next_priority.txt + session_state.md |
| Daemon log shows "no change" ×10 consecutive cycles | L1 dead — restart daemon, check CLI timeout, re-read session_state |
| dna_core.md > 500 lines without L2 compression | Context budget threat — run distillation cycle before next L1 execution |

---

## Files

| File | Layer | Purpose |
|------|-------|---------|
| `staging/last_output.md` | L1 | Current session output relay |
| `staging/session_state.md` | L1/L2 | Inter-session continuity |
| `results/daemon_log.md` | L2 | Engine health log |
| `results/dynamic_tree.md` | L2 | Branch progress tracker |
| `results/daemon_next_priority.txt` | L2 | Priority signal for next cycle |
| `LYH/agent/dna_core.md` | L3 | Core behavioral rules (MDs) |
| `LYH/agent/boot_tests.md` | L3 | Behavioral TDD test suite |
| `SKILL.md` | L3 | Engine operating rules |

---

*SOP #47 | Domain: 3 (持續學習) + 6 (存活冗餘) | Backing MDs: MD-1, MD-7, MD-8, MD-116, MD-322, MD-329*
*2026-04-09 UTC | Cycle 208*
