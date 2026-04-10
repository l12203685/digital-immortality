# SOP #99 — Cold-Start Drift Recovery Protocol

> 2026-04-09T13:30Z | cycle 264 | Branch 6 (存活/cold-start)

## Purpose

When consistency_test.py returns <33 ALIGNED or MISALIGNED on deterministic cases, the agent has drifted from behavioral ground truth. This SOP defines the automated recovery procedure.

**Gap closed**: SOP #96 covers mainnet activation. SOP #97 covers 87-day countdown. This SOP covers what happens when cold-start behavioral integrity fails — the survival layer beneath revenue.

**Hook**: "Your trading system can only stay alive if you can cold-start correctly. DNA without verification = faith. DNA with verification = engineering."

---

## Gate Protocol (G0→G5)

### G0 — Prerequisites
- [ ] `consistency_test.py` is executable: `python consistency_test.py templates/example_dna.md`
- [ ] `results/consistency_baseline.json` exists (reference ground truth)
- [ ] `templates/dna_core.md` is the current operative DNA file
- [ ] Git repo is clean (committed) before recovery begins

### G1 — Drift Detection
Run boot test and capture results:
```bash
python consistency_test.py templates/example_dna.md --output-dir results
```

**Classify severity:**
| Result | Status | Action |
|--------|--------|--------|
| 33 ALIGNED, 3 MISALIGNED (LLM-req) | STABLE | No action needed |
| 30-32 ALIGNED | WATCH | Identify which scenarios failed; check if DNA was modified |
| 25-29 ALIGNED | DRIFT | Trigger G2 recalibration |
| <25 ALIGNED | CRITICAL | Full DNA reread before any other work |

### G2 — Root Cause Identification
For each MISALIGNED deterministic scenario:
1. Read the scenario definition in `templates/example_dna.md`
2. Read the corresponding MD entry in `templates/dna_core.md`
3. Ask: "Which premise in the DNA leads to the wrong answer?"
4. Classify: `MISSING_MD` | `WRONG_MD` | `CONTEXT_LOSS` | `PROMPT_DRIFT`

**Root causes:**
- `MISSING_MD`: Scenario tests a principle not yet in dna_core.md → add MD
- `WRONG_MD`: Existing MD has incorrect reasoning → correct MD in place
- `CONTEXT_LOSS`: Agent lost context but DNA is correct → re-read dna_core.md
- `PROMPT_DRIFT`: Example DNA file diverged from operative DNA → sync files

### G3 — Targeted Fix
Based on root cause:

**MISSING_MD → add entry:**
```
| MD-XXX | principle summary | source, core logic, SOP, anti-patterns |
```

**WRONG_MD → correct in place:**
- Read current entry
- Identify incorrect premise
- Edit with correct reasoning
- Do NOT delete — append correction clause

**CONTEXT_LOSS → re-read:**
```
Read templates/dna_core.md (first 200 lines)
Read LYH/agent/dna_core.md (if available)
Re-run consistency_test.py
```

**PROMPT_DRIFT → sync:**
```bash
diff templates/example_dna.md templates/dna_core.md | head -50
# Identify diverged principles
# Update example_dna.md test cases to match current DNA
```

### G4 — Verification
```bash
python consistency_test.py templates/example_dna.md --output-dir results
```
- Must return ≥33 ALIGNED before proceeding
- If still failing: repeat G2→G3 for remaining misaligned cases
- Maximum 3 iterations before escalating to full DNA reread

### G5 — Persist & Report
After recovery:
1. `git add templates/dna_core.md templates/example_dna.md`
2. `git commit -m "boot-recovery: fix drift on cycle XXX — N scenarios recalibrated"`
3. Append to `results/daily_log.md`:
   ```
   - **Branch 6 RECOVERY**: boot test failed (N ALIGNED) → root cause: X → fix: Y → re-test: 33 ALIGNED ✅
   ```
4. Add entry to `memory/insights.json` with category `self_awareness`
5. Update `results/daemon_next_priority.txt` — CLEAR the 存活/cold-start flag

---

## Automated Drift Prevention

### Pre-work checklist (every cycle):
- Before any DNA edit: read current consistency score from `results/consistency_baseline.json`
- After any DNA edit: run consistency_test.py — never skip even if "minor" change
- Any edit that changes reasoning (not just adds content) → run G1 immediately

### Drift early warning signals:
- Agent asks questions that dna_core.md already answers → context_loss symptom
- Agent ignores regime filter when giving trading advice → MD-25/75 drift
- Agent doesn't list all options before recommending → MD-13/327 drift
- Agent gives advice without asking for real priority order first → MD-336 drift

### Recovery time targets:
| Severity | Target recovery cycles |
|----------|----------------------|
| WATCH | 0 (fix in same cycle) |
| DRIFT | 1 (next cycle if complex) |
| CRITICAL | 0 (stop all other work) |

---

## Backing MDs

| MD | Principle |
|----|-----------|
| MD-26 | Cold-start requires dna_core (67 lines), not full DNA |
| MD-74 | Boot tests = behavioral TDD; fail = recalibrate before action |
| MD-118 | Verification hierarchy: deterministic < LLM < real-life < Turing test |
| MD-201 | Every correction = new boot test case + distillation entry |

---

## Self-Test

Scenario: consistency_test.py returns 28/33 ALIGNED (5 deterministic fail).

Expected Edward response:
1. Do NOT proceed with other branches
2. Read failed scenario IDs from output
3. Trace each to DNA MD entry
4. Classify root causes
5. Fix DNA or re-read context
6. Re-run test → 33/33 → then proceed

Wrong response: "28/33 is still 85%, close enough, continuing with Branch 1.1"

**SOP #01~#99 COMPLETE ✅**
