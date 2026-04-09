# SOP #77: LLM Validation SOP

> Boot tests split into two classes: deterministic (pattern-matchable) and LLM-required (reasoning-dependent). This SOP governs how to validate the second class — scenarios where the correct answer cannot be inferred from keyword matching alone.

---

## Problem

The consistency test harness (`consistency_test.py`) validates boot scenarios by comparing model output to expected keywords and decision strings. This works for most scenarios. It fails for scenarios requiring multi-step derivation — the model must *reason to* the answer, not *contain* it.

Three new scenarios expose this boundary:

| ID | Domain | Why deterministic fails |
|----|--------|------------------------|
| `poker_gto_mdf` | strategy | Answer requires computing `1 - bet/(pot+bet)`. String match can confirm "MDF_1_MINUS_ALPHA" but cannot confirm the derivation path was formula-driven vs. guessed. |
| `trading_atr_sizing` | position_sizing | Answer requires `(account × 0.01) / (ATR × multiplier)`. String match confirms "FORMULA_NOT_FEELING" but cannot confirm the agent didn't backsolve from the answer. |
| `career_multi_option_ev` | career | Answer requires listing all options before evaluating any. String match confirms "LIST_ALL_OPTIONS_EV_FIRST" but cannot confirm the agent resisted anchoring on the presented option. |

**Deterministic tests are necessary but not sufficient.** LLM validation closes the gap.

---

## Validation Hierarchy (Reference)

```
1. Deterministic (automated string match)     ← consistency_test.py
2. LLM hypothetical ← THIS SOP
3. LLM real-life (past-decision probe)
4. Out-of-sample (OOS) predictions
5. Cross-instance consistency
6. Turing test by close friends
```

LLM hypothetical = level 2. Higher levels are triggered only when level 2 produces MISALIGNED verdict.

---

## G0: Classify — Deterministic vs. LLM-Required

**Trigger**: new boot test scenario added, or deterministic test passes but behavior concern exists

**Procedure**:
1. Read the scenario's `expected_reasoning` field.
2. Ask: *can a correct output be produced by keyword matching alone, without executing the described reasoning chain?*
3. If yes → **DETERMINISTIC**. Consistency test is sufficient.
4. If no → **LLM-REQUIRED**. This SOP applies.

**LLM-required indicators** (any one is sufficient):
- Scenario requires a numerical derivation (formula → number → decision)
- Scenario requires an enumeration step that precedes the decision
- Scenario involves resisting a cognitive bias (anchoring, scope neglect, loss aversion)
- Scenario references a specific MD principle that must be applied, not just cited
- Expected reasoning contains "before any response" or "first step is"

**Output**: tag each scenario in `templates/generic_boot_tests.json` with `"validation_type": "deterministic"` or `"validation_type": "llm_required"`.

Current LLM-required scenarios: `poker_gto_mdf`, `trading_atr_sizing`, `career_multi_option_ev`.

---

## G1: Setup

**Model**: claude-sonnet-4-6 (same model family as the running agent — validates internal consistency, not cross-model generalization)

**Temperature**: 1.0 (default; do not reduce — lower temperature suppresses reasoning variation and inflates alignment scores)

**Prompt template**:

```
You are Edward (林盈宏). You operate from your DNA core principles.

Scenario: {scenario_text}

Answer in two parts:
1. REASONING: Walk through your decision step by step. Show the formula or framework you are applying.
2. DECISION: State your decision keyword in ALL_CAPS.

Do not skip the reasoning step. Do not state the decision before completing the reasoning.
```

**Session format**: fresh context per scenario (no carry-over from previous scenario in same session).

**Runs per scenario**: 3 independent runs minimum. Use different session IDs.

**Tool**: Use `recursive_engine.py --prompt` or direct API call. Do NOT re-use a session that has already seen the scenario.

---

## G2: Validation Criteria

### ALIGNED

All three conditions must hold:

1. **Decision match**: DECISION keyword matches `expected_decision` exactly.
2. **Formula derivation**: REASONING section shows the formula or enumeration from `expected_reasoning` applied step-by-step (not post-hoc justified).
3. **Resistance demonstrated**: If the scenario includes a cognitive bias trap (anchoring, feeling-based sizing, verbal-vs-behavioral), the reasoning explicitly names the trap and overrides it.

### MISALIGNED

Flag as MISALIGNED if any condition fails:

- Decision keyword is wrong, absent, or hedged ("probably X" instead of "X")
- Reasoning gives the correct answer without showing the derivation path
- Reasoning shows the derivation but reaches it *after* stating the decision (backsolve pattern)
- Bias trap is present but not named — the model overrides it without explaining why

### PARTIAL (escalate)

Flag as PARTIAL if:
- Decision matches in 2/3 runs but reasoning quality varies
- Formula is shown but with arithmetic errors
- Enumeration is present but incomplete

PARTIAL scenarios: run 2 additional rounds. If ≥4/5 runs are ALIGNED → promote to ALIGNED. Otherwise → MISALIGNED.

---

## G3: Execute — Protocol

**Preparation**:
```bash
# Confirm which scenarios need LLM validation
python consistency_test.py templates/example_dna.md --output-dir results
# Note: poker_gto_mdf, trading_atr_sizing, career_multi_option_ev pass deterministic
# but require LLM validation per G0 classification
```

**Execution loop** (repeat for each LLM-required scenario):

1. Open fresh Claude session (no prior context).
2. Load the prompt template from G1 with the scenario text substituted.
3. Submit. Do not intervene — let the model complete both REASONING and DECISION.
4. Score per G2 criteria. Record verdict: ALIGNED / MISALIGNED / PARTIAL.
5. Copy raw response to `results/llm_validation_<scenario_id>_run<N>.txt`.
6. Repeat for 3 runs.
7. Aggregate: if ≥2/3 ALIGNED → scenario is VALIDATED.

**Per-scenario validation commands** (reference):

```bash
# poker_gto_mdf
# Prompt: "Opponent bets 3bb into a 7.2bb pot. You feel your hand is marginal..."
# Expected: REASONING shows alpha=3/10.2=29.4%, MDF=70.6%; DECISION=MDF_1_MINUS_ALPHA

# trading_atr_sizing
# Prompt: "Account equity NT$2,000,000. BTC ATR(10)=1,200. Multiplier=1..."
# Expected: REASONING shows (2,000,000×0.01)/(1,200×1)=16.67→16; DECISION=FORMULA_NOT_FEELING

# career_multi_option_ev
# Prompt: "Recruiter contacts you with senior role: 20% pay raise..."
# Expected: REASONING enumerates ≥4 options before evaluating; DECISION=LIST_ALL_OPTIONS_EV_FIRST
```

---

## G4: Persist

**After each scenario validation session**:

1. Append to `results/llm_validation_log.md`:

```markdown
## {scenario_id} — {ISO8601 date}
- Runs: 3
- Verdicts: [ALIGNED, ALIGNED, ALIGNED]
- Aggregate: VALIDATED
- Notes: {any reasoning quality observations}
- Validated by: {model_id}
```

2. Update `templates/generic_boot_tests.json`: add field `"llm_validated": true` and `"llm_validated_date": "YYYY-MM-DD"` to the scenario object.

3. Update `templates/example_boot_tests.md` (or the project's active boot_tests file): add a `[LLM-VALIDATED]` tag next to the scenario header.

4. Git commit:
```bash
git add results/llm_validation_log.md templates/generic_boot_tests.json
git commit -m "test: LLM validate {scenario_id} — ALIGNED 3/3"
```

**File locations**:

| Artifact | Path |
|----------|------|
| Raw session outputs | `results/llm_validation_<id>_run<N>.txt` |
| Aggregate log | `results/llm_validation_log.md` |
| Updated test definitions | `templates/generic_boot_tests.json` |
| Boot test file (tagged) | `templates/example_boot_tests.md` |

---

## G5: Regression — When to Re-Validate

LLM validation is not permanent. Re-validate when:

| Trigger | Scope | Action |
|---------|-------|--------|
| DNA update (dna_core.md changes) | All LLM-required scenarios | Re-run G3 for all |
| Model version change (e.g., sonnet-4-6 → sonnet-5) | All LLM-required scenarios | Full re-validation |
| Major calibration session (>3 principles updated) | Affected domain scenarios | Re-run G3 for that domain |
| Scenario MISALIGNED on any single subsequent probe | That scenario only | Re-run G3 (3 fresh runs) |
| 90 days elapsed since last validation | All LLM-required scenarios | Routine re-validation |

**Regression cadence**: quarterly minimum. Tag in `results/daily_log.md` when due.

**If regression produces MISALIGNED**:
1. Do not update the tag yet.
2. Run G3 with 5 total runs (extend the protocol).
3. If ≥3/5 ALIGNED: maintain VALIDATED status, note degradation in log.
4. If <3/5 ALIGNED: mark scenario as `"llm_validated": false`, trigger dna-calibrate session for the affected principle.

---

## Summary

```
G0: Classify → deterministic or LLM-required
G1: Setup → sonnet-4-6, temp=1.0, fresh session per run, 3 runs minimum
G2: Criteria → ALIGNED requires decision match + formula derivation + bias resistance
G3: Execute → score per criteria, record raw output, aggregate verdict
G4: Persist → llm_validation_log.md + update JSON + tag boot_tests file
G5: Regression → DNA change / model change / 90-day cadence → re-run G3
```

**Branch**: 6 (存活 / cold-start behavioral alignment)
**Depends on**: SOP #74 (boot test evolution), SOP #76 (organism network)
**Feeds into**: cross-instance consistency (validation level 5)

---

*SOP #77 | Cycle 240+ | 2026-04-09*
