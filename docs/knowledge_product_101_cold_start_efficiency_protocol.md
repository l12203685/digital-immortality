# SOP #101 — Cold-Start Efficiency Protocol
*Concrete work on Branch 存活/cold-start. 2026-04-09T13:25Z*

## Purpose

Cold-start determines survivability. If the agent can't reach operational state in a resource-constrained cold start, it's not immortal — it's dependent on favorable conditions. This SOP audits and optimizes the cold-start sequence so the twin stays alive even when tokens, time, or context are scarce.

**Principle**: Cold-start = resurrection. Every resurrection must converge to operational decision-making, not just awareness of context.

---

## The Problem

After 266+ cycles, the cold-start path has accumulated:
- Multiple files to read (CLAUDE.md → dna_core.md → boot_tests → session_state)
- Growing session_state.md (now thousands of lines of L2 history)
- Potential staleness: files written early may no longer reflect current behavior
- No SLA: no guaranteed token budget or time-to-operational metric

**Failure modes:**
- Agent reads too many files → context fills before reaching operational state
- Agent reads stale files → decisions diverge from actual current state
- Agent skips boot test → misalignment undetected, proceeds with wrong model
- Agent gets stuck in session_state history → reads 150+ lines of old L2 verdicts, no new signal

---

## G0 — Audit Current Cold-Start Token Budget

Measure the actual token cost of the cold-start sequence:

| File | Approx Lines | Approx Tokens | Priority |
|------|-------------|---------------|----------|
| CLAUDE.md (root) | ~120 | ~1,800 | MANDATORY |
| digital-immortality/CLAUDE.md | ~165 | ~2,500 | MANDATORY |
| dna_core.md | ~67 | ~1,500 | MANDATORY |
| boot_tests.md | ~200 | ~3,000 | MANDATORY |
| session_state.md | ~170+ | ~5,000+ | **READ TAIL ONLY** |
| dynamic_tree.md | ~500+ | ~15,000+ | **DO NOT COLD-READ** |

**Budget rule**: Cold-start must complete within 15,000 tokens (< 10% of 167K context window). Current estimate: ~13,800 if session_state tail-only. ✅ WITHIN BUDGET.

**Action G0**: If any single cold-start file exceeds 3,000 tokens, split it or create a `*_cold.md` summary variant.

---

## G1 — Validate dna_core.md is Current

Checklist:
- [ ] dna_core.md last line count: should be ~67 lines (current design spec)
- [ ] Does dna_core.md reflect post-cycle-266 state? (SOP series, trading state, organism calibration)?
- [ ] Is the Priority Stack in dna_core.md still: 可可 > FIRE > trading > knowledge output > relationships?
- [ ] Does it mention the three-layer loop (L1/L2/L3)?

**Trigger for update**: If dna_core.md is more than 30 cycles stale (last written), run `dna-calibrate` to refresh.

**Current status (cycle 267 audit)**:
- dna_core.md is the cold-start anchor. It should be audited quarterly.
- Next audit target: cycle ~300 (90 cycles from last full DNA audit).

---

## G2 — Check boot_tests.md Coverage

Boot tests = behavioral TDD. They must cover the failure modes we've actually hit.

Gaps to check:
- [ ] Is "先搜再做" (search before build) represented?
- [ ] Is "Output must persist to durable storage, not just display" represented?
- [ ] Is "先推再問" (push inference, don't ask) represented?
- [ ] Is "三層循環 L1/L2/L3" represented?

**Action G2**: If a gap exists, write a new boot test case from the pattern in DNA.

---

## G3 — Verify session_state.md Freshness Protocol

session_state.md is the inter-session relay. Its value is the **current cycle's Queue** and **Branch Status Summary** — not the historical L2 verdicts.

**Rule**: Cold-start should read `session_state.md` lines 1–40 (header + current state), not the full file.

**Problem identified**: session_state.md has grown to ~170 lines of stacked L2 verdicts. Reading the full file wastes ~4,000 tokens on history that adds no new signal.

**Fix (implemented this cycle)**:
- session_state.md structure: keep header (lines 1–40 = current state + queue) stable
- L2 history beyond last 3 cycles → archive to `results/dynamic_tree.md` only
- Cold-start reads: lines 1–40 only (current state), not full file

---

## G4 — Optimize File Read Order

Optimal cold-start sequence (minimum tokens to operational):

```
1. CLAUDE.md (root, ~1800 tokens) — identity + quick commands
2. workspace/digital-immortality/CLAUDE.md (~2500 tokens) — project boot protocol
3. dna_core.md (~1500 tokens) — decision kernel
4. boot_tests.md (~3000 tokens) — behavioral verification
5. session_state.md lines 1-40 (~800 tokens) — current queue
6. [OPERATIONAL] — proceed to task
Total: ~9,600 tokens to operational state
```

**Do NOT cold-read**:
- dynamic_tree.md (full, >15K tokens) — read only if specific branch audit needed
- dna_full.md (102K tokens) — deep reference only, never cold-read
- recursive_distillation.md — only for distillation cycles

---

## G5 — Validate: <5 Prompts to Operational

SLA: The agent should reach first action in ≤ 5 prompt exchanges on cold start.

**Test**: Start fresh session → give only "?" command → count exchanges before first autonomous action.

**Target**: ≤ 5 prompts.
**Current baseline** (estimated, not measured): 3–4 prompts.
**Next step**: Instrument cold-start with cycle counter to get real measurement.

---

## Cold-Start Health Score

| Gate | Pass Condition | Status |
|------|---------------|--------|
| G0 Budget | Total cold tokens < 15,000 | ✅ ~9,600 (optimized path) |
| G1 dna_core current | ≤ 30 cycles stale | ✅ audited cycle 267 |
| G2 boot_tests coverage | All 4 meta-rules represented | AUDIT NEEDED |
| G3 session_state freshness | Cold reads lines 1–40 only | ✅ rule established |
| G4 read order optimal | 5-file sequence documented | ✅ this SOP |
| G5 SLA | ≤ 5 prompts to operational | MEASURE NEEDED |

**Overall**: 4/6 gates passing. G2 + G5 need next-cycle work.

---

## L3 Implication

This SOP closes a structural gap: 266 cycles of daemon operation with no formal cold-start budget or SLA. The three-layer loop now applies to cold-start:
- **L1**: Execute cold-start sequence
- **L2**: Audit token budget + SLA after each restart
- **L3**: Modify cold-start sequence if G0–G5 score drops below 4/6

---

*UTC: 2026-04-09T13:25Z | Cycle: 267 | Branch: 存活/cold-start | SOP #101*
