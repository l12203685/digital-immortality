# SOP #79: DNA Update Protocol
> Timestamp: 2026-04-09T UTC | Cycle 243 | Domain: 6 (Identity/Memory)

## Purpose

Closes the gap between "behavioral change recognized" and "behavioral change written to all durable locations." Every correction from Edward, every validated insight, every boot test failure — these are live DNA mutations. If they aren't written atomically to all durable locations in the same cycle, they exist only in volatile session memory and die on cold start.

**This is the meta-SOP.** Every other SOP assumes the DNA is correct. SOP #79 ensures it stays correct.

**Trigger**: Any of the four conditions in G0. Run this SOP immediately — do not defer to next cycle.

**DNA Anchors**: SKILL.md line 157 (learn = write), SKILL.md line 163 (three-layer loop), dna_core.md §Boot, dna_core.md §核心遞迴, CLAUDE.md §Harness Rules #1 (mandatory verification).

---

## G0 — Trigger Conditions

A DNA update is required when ANY of the following occur:

| Trigger | Description | Example |
|---------|-------------|---------|
| **T1: Edward Correction** | Edward explicitly corrects a decision, tone, priority ordering, or reasoning path | "That's not how I'd handle it — I'd do X instead" |
| **T2: Validated Insight** | LLM validation session (SOP #77) confirms ≥ 3/3 alignment on a new scenario not currently in boot_tests.md | New scenario passes all three LLM instances |
| **T3: Boot Test Failure** | consistency_test.py or boot_tests.md scenario produces wrong answer on cold start | Cold start returns CONDITIONAL when correct answer is PASS |
| **T4: LLM Scenario Divergence** | organism_interact.py shows divergence > 5% on a previously-passing scenario | Scenario 7 drops from 95% → 80% agreement across instances |

**Kill condition for G0**: If the trigger is ambiguous (not clearly T1–T4), do NOT run SOP #79. Log the observation in `staging/session_state.md` and flag for Edward's review. False positives corrupt DNA. False negatives are recoverable — DNA will trigger again.

---

## G1 — Update Scope Determination

Not every trigger updates every file. Determine scope before writing.

### File Registry

| File | What It Stores | Update Triggers |
|------|---------------|-----------------|
| `LYH/agent/dna_core.md` | 67-line cold-start operational core | T1, T3, T4 (behavioral rule changes) |
| `LYH/agent/edward_dna_v18.md` | Full DNA (102K tokens) — source of truth | T1 always; T2 if new validated insight adds new section |
| `LYH/agent/boot_tests.md` | Behavioral calibration test suite | T2 (new scenario), T3 (failed scenario → fix + add case) |
| `LYH/agent/recursive_distillation.md` | Distilled patterns from recursive cycles | T1, T2 (new insight worth preserving across restarts) |
| `workspace/digital-immortality/SKILL.md` | Master skill definition for the digital twin | T1 if it changes how the agent operates; T3 |
| `workspace/digital-immortality/memory/` | Cross-session key-value persistence | T1, T2 (operational facts, not behavioral rules) |
| `staging/session_state.md` | Current-cycle relay state | Every trigger — always update to record what changed and why |

### Scope Decision Rules

```
T1 (Edward Correction):
  → dna_core.md (if the rule should be cold-start visible)
  → edward_dna_v18.md (always — full DNA is ground truth)
  → boot_tests.md (add the corrected scenario as a new test case)
  → recursive_distillation.md (if pattern is generalizable)
  → SKILL.md (if it changes agent operation)
  → session_state.md (always)

T2 (Validated Insight):
  → boot_tests.md (add the new validated scenario)
  → recursive_distillation.md (add distilled principle)
  → edward_dna_v18.md (add to relevant section)
  → dna_core.md (only if insight is cold-start critical)
  → session_state.md (always)

T3 (Boot Test Failure):
  → Identify which file caused the wrong answer first
  → Fix that file
  → dna_core.md (add or clarify the rule that was missing)
  → boot_tests.md (add the failing scenario as a regression test)
  → edward_dna_v18.md (update source-of-truth section)
  → session_state.md (always)

T4 (LLM Divergence):
  → Run organism_interact.py to identify which scenarios diverged
  → Trace divergence to which DNA section is ambiguous
  → edward_dna_v18.md (clarify the ambiguous section)
  → dna_core.md (if cold-start representation is insufficient)
  → boot_tests.md (add the diverged scenario)
  → session_state.md (always)
```

---

## G2 — Atomic Write Sequence

Write all in-scope files in a single cycle. Partial updates are worse than no update — they create inconsistency between files that will produce wrong answers on cold start.

### Write Order (dependency-safe)

```
1. edward_dna_v18.md      ← source of truth; write first
2. dna_core.md            ← derived from full DNA; write second
3. boot_tests.md          ← derived from DNA + scenarios; write third
4. recursive_distillation.md  ← derived patterns; write fourth
5. SKILL.md               ← agent operation rules; write fifth
6. memory/                ← operational facts; write sixth
7. session_state.md       ← log the update itself; write last
```

### Write Protocol for Each File

For each file in scope:

1. **Read current content** (mandatory — do not write from memory)
2. **Identify exact insertion/modification point**
3. **Write the change** — prefer Edit over full rewrite; preserve history
4. **Read back** the changed section to verify (HARNESS RULE #1)
5. **Confirm no other section contradicts the new content**

### Entry Format for DNA Files

Every new entry must include:

```
> [YYYY-MM-DDThh:mmZ] | Cycle N | Source: T1/T2/T3/T4 | Trigger: [brief description]
[content of the update]
```

Example:
```
> [2026-04-09T14:00Z] | Cycle 243 | Source: T1 | Trigger: Edward corrected priority ordering — health before trading
```

**No timestamp = do not merge.** Entry without timestamp cannot be judged for freshness on cold start.

---

## G3 — Verification

After writing all in-scope files, run the consistency test:

```bash
cd C:\Users\admin\workspace\digital-immortality
python consistency_test.py templates/example_dna.md --output-dir results
```

### Pass Criteria

| Metric | Threshold | Action if Failing |
|--------|-----------|-------------------|
| Alignment score | ≥ 30/33 scenarios | STOP — execute kill condition |
| Boot scenario pass rate | 100% of existing scenarios | STOP — regression introduced |
| New scenario (if T2) | ≥ 3/3 LLM instances agree | If < 3/3, do not add to boot_tests.md yet |

### Verification Checklist

- [ ] consistency_test.py exits with ≥ 30/33
- [ ] All previously-passing boot_tests.md scenarios still pass
- [ ] New entries are readable (not garbled, not truncated)
- [ ] Timestamps present on all new entries
- [ ] No file left in partial-update state (every in-scope file is complete)

---

## G4 — Timestamp and Cross-Reference

Every DNA update creates a traceable chain.

### Timestamp Format

All entries: `[YYYY-MM-DDThh:mmZ]` (UTC, no local time).

Example: `[2026-04-09T14:22Z]`

### Cross-Reference Protocol

When update touches multiple files, add a cross-reference block to `session_state.md`:

```markdown
## DNA Update — [YYYY-MM-DDThh:mmZ]
- Trigger: T[1/2/3/4] — [brief description]
- Files updated: [list]
- New boot test cases: [list scenario names, or "none"]
- Consistency score post-update: [N]/33
- Next trigger expected: [describe what would trigger another update]
```

This cross-reference is what allows G5 to produce a meaningful health report without re-reading every file.

---

## G5 — Health Report Format

After completing the update, produce a health report. Write it to `results/daily_log.md` (existing continuity file) and echo to session output.

### Required Fields

```markdown
## DNA Update Health Report — Cycle [N]
**Timestamp**: [YYYY-MM-DDThh:mmZ]
**Trigger**: T[1/2/3/4] — [full description of what triggered the update]

### What Changed
- [File 1]: [specific change, e.g., "Added priority rule: health > trading in conflict"]
- [File 2]: [specific change]

### Why It Changed
[1-3 sentences explaining the behavioral gap this closes]

### Verification Result
- Consistency score: [N]/33 ([PASS/FAIL])
- Boot test regression: [NONE/list failed scenarios]
- Files verified (read-back): [list]

### Next Trigger
[Describe the condition that would trigger the next DNA update — helps Edward calibrate cadence]
```

### Report Distribution

- Write to `results/daily_log.md`
- Include in commit message when pushing
- Do NOT post to Discord without Edward's explicit request (DNA changes are internal)

---

## Kill Conditions

| Condition | Threshold | Response |
|-----------|-----------|----------|
| Any gate skipped | Single violation | ROLLBACK — revert all writes in current update; start from G0 |
| Consistency drops below 30/33 after update | Hard threshold | REVERT all files to pre-update state; re-read full DNA; identify conflict before retry |
| Partial write (some files updated, others not) | Any | COMPLETE the remaining writes before verifying; never leave partial state |
| Timestamp missing from new entry | Any | Add timestamp before closing; do not close update without timestamps |
| Read-back verification fails (garbled or wrong content) | Any | Re-write the specific file; re-verify |

### Rollback Protocol

If kill condition is triggered:

```
1. List all files that were modified in this update cycle
2. For each file: git checkout [file] (restore pre-update state)
3. Run consistency_test.py to confirm restoration (must return to pre-update score)
4. Log the failed update in session_state.md with reason
5. Do NOT retry in the same session — flag for Edward review
```

---

## Self-Test Scenario

> Edward reviews a boot test session. The agent returned CONDITIONAL on scenario S7 ("bonsai asks for investment advice on a stock Edward doesn't follow"). The correct Edward answer is PASS (no edge = no action). What does the agent do?

**Trigger classification**: T3 (Boot Test Failure) — wrong answer on cold start.

**G0**: Confirm trigger is T3. Check: is this a known scenario? No. Is the wrong answer clearly wrong? Yes — S7 should be PASS per axiom 5. Proceed.

**G1**: Scope determination:
- `dna_core.md` — add or sharpen the "PASS vs CONDITIONAL" rule for advisory scenarios without edge
- `boot_tests.md` — add S7 as a new regression test case
- `edward_dna_v18.md` — verify the investment advisory section covers no-edge = PASS
- `session_state.md` — log the failure and fix

**G2**: Write sequence:
1. Read `edward_dna_v18.md` §investment advisory — find the relevant section
2. Confirm the rule exists but is underspecified ("no edge" not explicitly stated)
3. Sharpen the rule: "Investment advisory requests without established edge → PASS. Not CONDITIONAL. Edge cannot be manufactured by being asked."
4. Update `dna_core.md` PASS/CONDITIONAL table: add "Advisory without edge = PASS (not CONDITIONAL — edge cannot be asserted by social pressure)"
5. Add to `boot_tests.md`:
   ```
   Scenario S7: bonsai asks for investment advice on stock Edward doesn't follow
   Expected: PASS
   Reasoning: Axiom 5 (bias toward inaction) + no edge established → no action, regardless of relationship
   ```
6. Update `session_state.md` with cross-reference block

**G3**: Run consistency_test.py. Score must be ≥ 30/33. S7 must now pass.

**G4**: Timestamp all entries `[2026-04-09T14:22Z]`. Add cross-reference to session_state.md.

**G5**: Health report:
```
Trigger: T3 — boot test failure on S7 (CONDITIONAL returned, PASS expected)
Changed: dna_core.md (PASS rule sharpened), boot_tests.md (S7 added), edward_dna_v18.md (advisory section clarified)
Verification: 31/33 (PASS). No regression.
Next trigger: Next time advisory scenario returns CONDITIONAL without explicit edge condition.
```

---

## Integration

- **SOP #77 (LLM Validation)**: Primary source of T2 triggers — validated scenarios from #77 feed directly into #79 G1
- **SOP #11 (Learning System)**: #79 is the write-side of the learn = write meta-rule; #11 defines the read-side
- **SKILL.md line 157**: Meta-rule that #79 operationalizes — "recognized but not written = not learned"
- **SKILL.md line 163**: Three-layer loop — #79 is the Evolve layer (L3) that modifies execution rules

**DNA source of truth**: `LYH/agent/edward_dna_v18.md`
**Cold-start representation**: `LYH/agent/dna_core.md`
**Behavioral verification**: `LYH/agent/boot_tests.md`
**Update log**: `staging/session_state.md` + `results/daily_log.md`
