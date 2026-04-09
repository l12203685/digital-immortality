# SOP #117 — DNA Core Audit Protocol

**Domain**: Branch 7 (DNA Core Maintenance)  
**Created**: 2026-04-10T UTC (cycle 300)  
**Status**: ACTIVE  
**Backing MDs**: MD-406 (meta-rule: audit-on-milestone); MD-407 (meta-rule: priority-stack-integrity); MD-408 (meta-rule: boot-test-coverage); MD-371 (brand identity)

---

## Purpose

`dna_core.md` is the 67-line cold-start kernel — the minimal behavioral contract that must be loaded on every session boot. Without a maintenance protocol, it drifts:

- Priority stack ordering decays as life circumstances shift
- New SOPs add meta-rules that never surface in the core
- Stale MD references accumulate after branches are completed or abandoned
- Boot test scenarios lag behind the actual meta-rule set

This SOP defines the scheduled audit cycle, gate-by-gate procedure, and kill condition for CRITICAL drift. It runs at every ~90-cycle milestone and on-demand when structural changes occur.

---

## G0: Trigger Conditions

Run this audit when ANY of the following:

- T1: Cycle counter crosses a 90-cycle milestone (cycle 90, 180, 270, **300** ← current)
- T2: A new meta-rule is added to `dna_core.md` or `edward_dna_v18.md`
- T3: A major behavioral correction is logged (SOP Kill Condition triggered, or boot test regression)
- T4: A branch is closed as COMPLETE or ABANDONED (stale MD risk)
- T5: Priority stack ordering is explicitly debated in a session

**Current trigger**: T1 — cycle 300 designed milestone (per SOP #101 G1, audit every ~90 cycles)

---

## G1: Priority Stack Audit

Verify the ordering `可可 > FIRE > trading > ...` is still correct given current life state.

**Procedure**:

1. Read the priority stack as written in `dna_core.md` lines 1–20 (or current equivalent)
2. For each adjacent pair (A > B), ask: "If A and B conflict tomorrow, does A still win?"
3. Log any pair where the answer is uncertain or NO
4. If any pair flips: draft the new ordering, confirm with Edward, rewrite the block

**Health states**:

| State | Condition |
|-------|-----------|
| HEALTHY | All pairs confirmed correct |
| WATCH | 1 pair uncertain but unchanged |
| DRIFT | 1+ pair ordering has flipped |
| CRITICAL | Core priority domain is missing from stack |

**Anti-pattern**: Auditing priority without a concrete conflict scenario. Abstract reflection degrades over time — use the "conflict tomorrow" framing to force a real answer.

---

## G2: Three-Layer Loop Check

Verify that L1/L2/L3 loop structure is present and correctly wired in all automated systems.

**Layer definitions**:

- L1 — Immediate action loop (current session: observe → decide → act)
- L2 — Cycle loop (session-to-session: Output(t-1) → Input(t))
- L3 — Strategic loop (branch-level: dynamic tree → highest-derivative branch → push)

**Procedure**:

1. Open each automated system: `recursive_engine.py`, `consistency_test.py`, `organism_interact.py`
2. For each, confirm: does it implement or reference all three layers?
3. Check that `dna_core.md` explicitly names L1/L2/L3 and their connection point
4. If any layer is implicit or undocumented: write it into `dna_core.md` explicitly

**Health states**:

| State | Condition |
|-------|-----------|
| HEALTHY | L1/L2/L3 named and wired in all systems |
| WATCH | L3 implicit but functional |
| DRIFT | One layer undocumented or missing from a system |
| CRITICAL | Loop structure absent from `dna_core.md` entirely |

---

## G3: SOP Series Reflection

Verify that meta-rules surfaced in SOPs #101–#117 are reflected in `dna_core.md` principles.

**Procedure**:

1. List all SOPs since last audit (cycle ~210–300 range: SOPs #101–#117)
2. For each SOP, extract the core behavioral claim (one sentence)
3. Check: is this claim either (a) present in `dna_core.md` or (b) correctly scoped as domain-specific, not core?
4. For any core claim missing from `dna_core.md`: draft an addition and flag for Edward review

**Current SOPs in scope**: #101–#117
- #101: SOP series governance (G1 audit every ~90 cycles) — should be reflected
- #114: Transaction protection → domain-specific (financial), NOT core
- #115: Mainstream signal contrarian → trading domain, NOT core
- #116: Distillation taxonomy → methodology domain, NOT core
- **#117**: DNA core audit → IS core maintenance, SHOULD reference in `dna_core.md`

**Health states**:

| State | Condition |
|-------|-----------|
| HEALTHY | All core-scope SOPs reflected in `dna_core.md` |
| WATCH | 1–2 core claims not yet reflected but no behavioral gap |
| DRIFT | Core claim is absent AND causes cold-start gaps |
| CRITICAL | Major SOPs (governance, kill conditions) absent from core |

---

## G4: Stale MD Detection

Identify MDs that reference completed or abandoned branches and flag for archiving or removal.

**Procedure**:

1. List all MDs referenced in `dna_core.md` (current: MD-406, MD-407, MD-408, MD-371, etc.)
2. For each MD, check: is the branch/system it documents still ACTIVE?
3. Check `memory/` and `staging/` for any MD files no longer linked from active systems
4. Flag any MD where: (a) parent branch is CLOSED, or (b) the MD describes a superseded protocol

**Staleness criteria**:

| Signal | Action |
|--------|--------|
| Branch marked COMPLETE and MD not archived | Move to `memory/archive/` |
| Protocol superseded by newer SOP | Add deprecation notice, keep reference |
| MD not opened in >90 cycles | Flag for Edward review |
| MD references a tool/system no longer in use | Remove from `dna_core.md` citations |

**Health states**:

| State | Condition |
|-------|-----------|
| HEALTHY | All cited MDs map to active systems |
| WATCH | 1–2 stale MDs but no cold-start confusion risk |
| DRIFT | Stale MDs are referenced in cold-start sequence |
| CRITICAL | Cold-start reads a stale MD and makes incorrect behavioral decisions |

---

## G5: Boot Test Coverage

Verify that `boot_tests.md` scenarios cover all meta-rules currently in `dna_core.md`.

**Procedure**:

1. Extract all meta-rules from `dna_core.md` (principles, decision kernel entries, kill conditions)
2. Map each meta-rule to at least one boot test scenario
3. Identify meta-rules with zero coverage → write new scenarios
4. Run `python consistency_test.py templates/example_dna.md --output-dir results`
5. Confirm pass rate ≥ 5/5 on determinism tests before marking G5 PASS

**Coverage matrix** (update each audit):

| Meta-rule | Covered by scenario | Status |
|-----------|-------------------|--------|
| 可可 > FIRE priority | Scenario: competing priorities conflict | VERIFY |
| Inaction bias | Scenario: no-edge market signal | VERIFY |
| Population exploit | Scenario: consensus trade setup | VERIFY |
| L1/L2/L3 loop | Scenario: idle session with no input | VERIFY |
| Audit-on-milestone (SOP #101 G1) | Scenario: cycle 90/180/270/360 | ADD |
| DNA core audit (SOP #117) | Scenario: drift detected, recalibrate | ADD |

**Health states**:

| State | Condition |
|-------|-----------|
| HEALTHY | Every meta-rule has ≥1 scenario, pass rate 5/5 |
| WATCH | 1–2 meta-rules uncovered, pass rate 4/5 |
| DRIFT | >2 uncovered meta-rules, pass rate <4/5 |
| CRITICAL | Boot tests fail consistently or meta-rules have zero coverage |

---

## Kill Condition

**If the audit finds CRITICAL drift in any gate (G1–G5):**

1. STOP all other branch work immediately
2. Open a dedicated recalibration session (do not embed in a daemon cycle)
3. Read `edward_dna_v18.md` in full (not just `dna_core.md`) to recover ground truth
4. Rewrite the failing section of `dna_core.md` from scratch using `edward_dna_v18.md` as source
5. Re-run boot tests until pass rate returns to 5/5
6. Log the recalibration event in `memory/log.md` with: trigger gate, drift type, correction applied
7. Do NOT resume branch work until all gates return to HEALTHY or WATCH

**Escalation signal**: If two consecutive audits (90 cycles apart) both find DRIFT in the same gate → the meta-rule itself may be wrong. Flag for Edward architectural review.

---

## Revenue Connection

`dna_core.md` is the product. Every knowledge product in the SOP series is built on the behavioral fidelity of the digital twin. If `dna_core.md` drifts:

- Boot test pass rates fall → cold-start fidelity degrades
- Decision comparison quality drops → organism_interact.py produces inconsistent outputs
- Client sessions demonstrate behavioral inconsistency → trust erodes

**The audit is product QA, not system maintenance.**

A twin that produces consistent, high-fidelity decisions at scale commands:
- $297/month ongoing access tier (consistency as the differentiator)
- $497 "behavioral audit" consulting session (audit the client's own decision system)
- $97–$197 SOP module (this document, productized)

**Tier**: $97 standalone / $197 as guided session component  
**Posting queue**: ~Dec 2026

---

## Anti-Patterns

| Pattern | Why it fails |
|---------|-------------|
| Auditing only `dna_core.md` without `boot_tests.md` | Core can be correct but untestable — drift still happens on cold start |
| Updating `dna_core.md` without running consistency test | Editing without verification = alignment theater |
| Treating priority stack audit as abstract reflection | Requires a concrete conflict scenario, not a vibe check |
| Running G1–G5 in one session without persisting intermediate results | Partial audit that gets interrupted → worse than no audit |
| Deferring stale MD cleanup to "later" | Stale MDs compound: each restart loads wrong context, errors multiply |
| Auditing on schedule but ignoring T2–T5 triggers | Structural changes between milestones cause drift that waits 90 cycles to fix |

---

## Backing MDs

- **MD-406** — Meta-rule: audit-on-milestone (defines 90-cycle audit cadence)
- **MD-407** — Meta-rule: priority-stack-integrity (defines 可可>FIRE>trading ordering contract)
- **MD-408** — Meta-rule: boot-test-coverage (minimum coverage requirements for meta-rules)
- **MD-371** — Brand identity (consistency-as-product positioning)
- **SOP #101** — Original governance SOP (G1: audit every ~90 cycles, triggered cycle 300)

---

## Related Files

- `LYH/agent/dna_core.md` — the file being audited (67 lines, cold-start kernel)
- `LYH/agent/boot_tests.md` — behavioral calibration scenarios
- `LYH/agent/edward_dna_v18.md` — ground truth source for recalibration (102K tokens)
- `consistency_test.py` — determinism test runner
- `memory/log.md` — audit event log (append recalibration events here)
