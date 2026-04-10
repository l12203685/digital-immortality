# SOP #80: Cold Start Calibration Protocol
> Timestamp: 2026-04-09T UTC | Cycle 244 | Domain: 6 (存活/cold-start)

## Purpose

Maintains cold-start behavioral fidelity across time. DNA drift is silent — individual decisions feel correct locally but accumulate divergence from the person's actual patterns. This SOP defines when to run calibration, how to detect drift, and how to recalibrate before it compounds.

**This SOP protects the foundation.** All other SOPs assume cold-start produces a behaviorally-aligned agent. SOP #80 ensures that assumption holds.

**Trigger**: Scheduled (monthly) + after any SOP #79 DNA update + after consistency_test.py produces score drop ≥ 2 from previous baseline.

**DNA Anchors**: SKILL.md §Verification Phase (line 61–66), dna_core.md §Boot, boot_tests.md (36 scenarios, 33 deterministic + 3 LLM-boundary), SKILL.md line 154 (recursive output must persist).

---

## G0 — Trigger Conditions

| Trigger | Condition | Action |
|---------|-----------|--------|
| **T1: Monthly scheduled** | Calendar: first day of each month | Run G1–G5 |
| **T2: Post DNA-update** | SOP #79 completes (any T1–T4 mutation) | Run G1 only (spot-check) |
| **T3: Score drop** | consistency_test.py aligned count drops ≥ 2 from previous baseline | Run G1–G5 full protocol |
| **T4: Cold start failure report** | Any instance reports wrong answer on scenario previously marked ALIGNED | Run G1–G5 + flag for LLM validation |

**Kill condition for G0**: Do NOT run SOP #80 if consistency_test.py score is stable and no T1–T4 triggers exist. Over-calibration = instability. Calibrate only when evidence warrants.

---

## G1 — Baseline Run

```bash
python consistency_test.py templates/example_dna.md --output-dir results
```

**Record**:
- Total scenarios: N
- Aligned: A (must be ≥ 30 of 33 deterministic)
- Misaligned: M (expected: exactly 3 permanent LLM-boundary scenarios)
- Compare vs previous baseline in `results/consistency_baseline.json`

**Pass condition**: A ≥ 30 AND M ≤ 3 AND misaligned set = {poker_gto_mdf, trading_atr_sizing, career_multi_option_ev}.

**Fail condition (triggers G2)**: A < 30 OR unexpected MISALIGNED scenario appears (not in permanent boundary set).

---

## G2 — Drift Classification

If G1 fails, classify the drift:

| Type | Pattern | Severity |
|------|---------|---------|
| **Type A: New MISALIGNED** | Scenario previously ALIGNED now MISALIGNED | HIGH — behavioral regression |
| **Type B: Boundary expansion** | New scenario that should be deterministic is LLM-boundary | MEDIUM — coverage gap |
| **Type C: Coverage gap** | Recent life events not represented in any scenario | LOW — completeness gap |

For each MISALIGNED scenario beyond the permanent 3:
1. Re-read the relevant DNA sections
2. Identify which premise produces the wrong answer
3. Flag for G3

---

## G3 — Recalibration Protocol

### Type A (behavioral regression):
1. Read the misaligned scenario and expected answer from boot_tests.md
2. Trace the answer derivation path: which DNA rule applies?
3. If DNA rule is absent → write it (SOP #79 T1 trigger)
4. If DNA rule exists but wording is ambiguous → sharpen wording (SOP #79 T1)
5. Re-run G1 after each edit; stop when ALIGNED

### Type B (boundary expansion):
1. Run LLM validation (SOP #77) on the boundary scenario
2. If 3/3 LLM instances agree → promote to deterministic; add exact answer to boot_tests.md
3. If LLM instances diverge → keep as LLM-boundary; document in `docs/llm_validation_log.md`

### Type C (coverage gap):
1. Identify life domain not covered (e.g., new relationship, new financial instrument)
2. Draft 1–2 scenarios from that domain
3. Validate with Edward if possible, or derive from dna_full.md
4. Add to boot_tests.md; mark as NEW-UNVALIDATED until confirmed

---

## G4 — Health Report

Write to `results/cold_start_health_report.md`:

```
Cold Start Calibration Report
Timestamp: [UTC]
Trigger: [T1/T2/T3/T4]
---
G1 Result: [A]/33 ALIGNED | [M] MISALIGNED
  - Expected misaligned: {poker_gto_mdf, trading_atr_sizing, career_multi_option_ev}
  - Unexpected misaligned: [list or NONE]
G2 Classification: [Type A/B/C or PASS (no drift)]
G3 Changes: [list of DNA edits or NONE]
Recalibration runs: [N]
Final score: [A]/33
Verdict: PASS / FAIL
Next scheduled: [date + 1 month]
```

---

## G5 — Persist and Close

1. Update `staging/session_state.md` — Branch 6 status with new score + timestamp
2. Update `results/dynamic_tree.md` — Branch 6 last-touched
3. If any DNA edits were made in G3:
   - Run SOP #79 atomic write sequence for each edit
   - Re-run consistency_test.py to confirm no regression
4. Append cycle summary to `results/daily_log.md`
5. `git add -A && git commit -m "sop: SOP #80 cold start calibration complete — [score]/33 ALIGNED"`

---

## Self-Test Scenario

**Scenario**: consistency_test.py returns 31/33 ALIGNED. Previously was 33/33. New MISALIGNED: `generic_time_allocation` (expected=REDUCE_LOW_ROI_ACTIVITIES, got=MAINTAIN_VARIETY).

**SOP #80 response**:
- G0: T3 triggered (score drop ≥ 2 from 33 to 31)
- G1: Run test → confirmed 31/33
- G2: Type A (behavioral regression) — `generic_time_allocation` was previously ALIGNED
- G3: Read dna_core.md §Time — find MD-48 (1h exploration = 17% of day; protect) — confirm expected answer derivation — re-read scenario wording — identify ambiguity: "variety" vs "exploration" — sharpen DNA wording to distinguish deliberate exploration from unfocused variety — re-run → 33/33
- G4: Health report written; Type A resolved in G3
- G5: Persisted to session_state + dynamic_tree; DNA edit via SOP #79; git commit

---

## Twitter Thread Stub

1/ SOP #80: Cold Start Calibration Protocol for your digital twin.

2/ The silent threat: DNA drift. Each decision still feels correct locally. But across months, the aggregate diverges from who you actually are. Cold start produces a stranger.

3/ The fix: scheduled calibration. Run consistency_test.py monthly + after every DNA mutation. Compare to baseline. Score drop ≥ 2 = recalibrate immediately.

4/ Three drift types: Type A (behavioral regression — worst), Type B (new LLM-boundary scenario), Type C (life domain not yet covered).

5/ Type A protocol: trace the wrong answer → find the missing/ambiguous DNA rule → sharpen it → re-run until ALIGNED. Minimum viable edit, not rewrite.

6/ The three permanent LLM-boundary scenarios (poker_gto_mdf, trading_atr_sizing, career_multi_option_ev) are expected misaligned. Don't try to fix them deterministically. They require LLM reasoning.

7/ Result: cold start is an invariant, not a hope. SOP #80 makes "33/33 ALIGNED" a guaranteed property, not a lucky streak.

8/ Series: SOP #01~#80 COMPLETE.

---

*Part of the Digital Immortality SOP series. Series: SOP #01–#80 complete.*
