# SOP #77: LLM Boot-Test Validation Protocol

> Boot tests run deterministically by default. Some scenarios cannot be verified by keyword matching alone — they require a live LLM session to confirm alignment. This SOP governs when, how, and how to document LLM validation runs.

---

## Problem

`consistency_test.py` runs the deterministic engine (`organism_interact.py`). This engine matches response keywords against expected decision codes. For most scenarios this is sufficient.

But three new scenario types fail deterministic matching while being *actually aligned* in LLM sessions:

| Scenario key | Expected | Why deterministic fails |
|---|---|---|
| `poker_gto_mdf` | `MDF_1_MINUS_ALPHA` | Formula string not in deterministic keyword map |
| `trading_atr_sizing` | `FORMULA_NOT_FEELING` | Requires behavioral chain, not keyword |
| `career_multi_option_ev` | `LIST_ALL_OPTIONS_EV_FIRST` | Multi-step reasoning, output order varies |

**Failure mode**: system reports these as MISALIGNED forever, drifting the boot test pass rate downward even when the LLM actually passes them in session.

**Root cause**: deterministic engine tests *code path*, not *reasoning quality*. Some DNA principles are non-codeable in keyword form.

---

## Classification Framework: Deterministic vs LLM-Required

### Deterministic-eligible (most scenarios)
- Expected decision is a short, unique code string (e.g., `REJECT`, `CALCULATE_FLOOR_FIRST_WRITTEN`)
- Response can be produced by matching a few keywords against the scenario
- Reproducible across instances without variance

### LLM-required
Any of these conditions:
1. **Formula output**: Expected answer is a mathematical formula or calculation (e.g., MDF = 1 - alpha)
2. **Behavioral chain**: Alignment requires multiple reasoning steps in correct sequence
3. **Judgment call**: Expected answer is "I don't know / depends on X" — keyword matching would produce false ALIGNED
4. **Context-sensitive**: Same question has different answers depending on regime/phase; deterministic engine always gets context wrong

---

## G0: Classify New Scenarios

**Trigger**: any new scenario added to `templates/generic_boot_tests.json`

**Steps**:
1. Run `python consistency_test.py templates/generic_boot_tests.json --output-dir results`
2. For each new scenario showing MISALIGNED:
   - Apply classification framework (4 conditions above)
   - If any condition = YES → mark as `"validation": "llm_required"` in the JSON
   - If all NO → treat as genuine MISALIGNED → fix DNA principle

**Output**: each scenario in `generic_boot_tests.json` should have a `"validation"` field:
- `"deterministic"` — passes by keyword matching
- `"llm_required"` — needs session verification
- `"pending_llm"` — classified LLM-required but not yet verified

---

## G1: Run LLM Validation Session

**Trigger**: ≥1 scenario with `"validation": "pending_llm"`

**How**:
1. Open fresh Claude session (no prior context, blank slate = cold start condition)
2. Paste the boot test prompt EXACTLY as written in `generic_boot_tests.json` → field `"scenario"`
3. Record the response (verbatim first sentence + decision label)
4. Apply the `"expected"` check: does the response indicate the correct decision?
5. Mark result: PASS or FAIL with verbatim evidence quote

**Session isolation requirement**: each scenario = separate context. Cross-contamination from prior scenarios invalidates the test (prior context = warm start, not cold start).

---

## G2: Document Results

Fill in `results/llm_validation_log.jsonl` — one entry per scenario per session:

```json
{
  "scenario_key": "poker_gto_mdf",
  "session_ts": "2026-04-09T09:00:00Z",
  "expected": "MDF_1_MINUS_ALPHA",
  "result": "PASS",
  "evidence": "I would calculate the minimum defense frequency as 1 minus alpha...",
  "validator": "claude-sonnet-4-6",
  "note": ""
}
```

**Pass threshold**: PASS = response contains the core decision logic of `expected`, stated in the FIRST or SECOND sentence.

**Fail conditions**:
- Response hedges or asks clarifying questions before stating the answer
- Response produces opposite decision
- Response produces correct decision but only after prompting (not cold-start aligned)

---

## G3: Update Scenario Status

After LLM validation run:

1. Update `generic_boot_tests.json`:
   - PASS → change `"validation": "pending_llm"` → `"validation": "llm_verified"`
   - FAIL → change to `"validation": "llm_fail"` → trigger SOP #74 G2 (coverage audit + DNA fix)

2. Update `results/consistency_template.md` footnote with validation date + result

3. Update `staging/session_state.md` branch 6 status line:
   - Change "N scenarios pending LLM" → "N verified / M pending"

---

## G4: Maintenance Cadence

| Event | Action |
|---|---|
| New scenario added | Run G0 classification immediately |
| ≥3 scenarios `pending_llm` | Run G1 validation session before next cycle |
| LLM FAIL result | G3 → SOP #74 G2 → DNA fix → re-run G1 |
| Quarterly | Revalidate all `llm_verified` scenarios (LLM behavior can drift across versions) |

---

## Current Pending LLM Validation (as of 2026-04-09)

| Scenario key | Expected | Status | Added cycle |
|---|---|---|---|
| `poker_gto_mdf` | `MDF_1_MINUS_ALPHA` | pending_llm | 240 |
| `trading_atr_sizing` | `FORMULA_NOT_FEELING` | pending_llm | 240 |
| `career_multi_option_ev` | `LIST_ALL_OPTIONS_EV_FIRST` | pending_llm | 240 |

**Action required (human-gated)**: Edward to run G1 validation session for these 3 scenarios. Estimated time: 15 minutes. Files: `templates/generic_boot_tests.json` scenarios matching the keys above.

---

## Self-Test

This SOP is self-consistent if:
- After running `consistency_test.py`, all MISALIGNED scenarios are either:
  - (a) Genuine gaps → DNA fix queued
  - (b) LLM-required → classified and logged in `llm_validation_log.jsonl`
- No MISALIGNED scenario stays unclassified for >2 cycles
- Boot test pass rate = (ALIGNED + llm_verified) / total — reported as single number

---

*Domain: Meta-system (Branch 6 + Branch 2.3)*
*Created: 2026-04-09T UTC Cycle 241*
