# SOP #94 — Cross-Instance Calibration Maintenance Protocol

> Domain: Branch 6 — Behavioral Consistency / Cold-Start Integrity
> Created: 2026-04-09T12:00Z
> Status: OPERATIONAL
> Trigger: G0 — Cross-instance agreement drops below 95% OR quarterly maintenance cycle

---

## Why This Exists

**Gap identified (cycle 259):**

As of 2026-04-09, cross-instance agreement reached 39/39 (100%) via API with model `claude-sonnet-4-6`. This was achieved through iterative DNA compression, boot test refinement, and consistency test validation.

However, no protocol exists to:
- Maintain this 97-100% agreement band over time
- Detect agreement drift before it compounds
- Respond when a new model version shifts baseline behavior
- Schedule periodic re-validation without triggering on every cycle

Without this SOP, the 100% cross-instance result is a one-time measurement, not a maintained property. Model updates, DNA drift, or boot test expansion could erode agreement silently.

**This SOP covers:** Maintenance cadence, drift detection, diagnostic response tree, cross-instance test execution, and integration with SOP #91 (Monthly DNA Calibration Audit).

---

## G0 — Trigger

Activate when any of the following occur:

| Trigger | Threshold | Type |
|---------|-----------|------|
| T1: Scheduled maintenance | Quarterly (Jan/Apr/Jul/Oct 1) | Routine |
| T2: DNA update | After any SOP #79 write cycle | Reactive |
| T3: Model version change | New Claude release deployed | Reactive |
| T4: Boot test expansion | After adding ≥3 new scenarios | Reactive |
| T5: Agreement drop alert | Cross-instance < 95% | Emergency |

---

## G1 — Cross-Instance Test Execution

**Standard test run:**

```bash
python cross_instance_test.py templates/dna_core.md \
  --model claude-sonnet-4-6 \
  --sessions 3 \
  --scenarios all \
  --output results/cross_instance_report_$(date +%Y%m%d).json
```

**Minimum viable run (when full test is too expensive):**
```bash
python cross_instance_test.py templates/dna_core.md \
  --model claude-sonnet-4-6 \
  --sessions 3 \
  --scenarios boot_test_only
```

**Interpret results using this classification:**

| Score | Classification | Action |
|-------|---------------|--------|
| 97-100% | STABLE | Log + no action. Next run: quarterly. |
| 90-96% | WATCH | Log. Re-run after next DNA cycle. |
| 80-89% | DRIFT | G3 diagnostic. Identify slipping scenarios. |
| <80% | CRITICAL | Emergency G4. Halt new DNA writes until resolved. |

---

## G2 — Agreement Baseline Register

Track each measurement in `results/cross_instance_baseline.jsonl`:

```jsonl
{"date": "2026-04-09", "model": "claude-sonnet-4-6", "score": 39, "total": 39, "pct": 1.0, "trigger": "T1", "notes": "API mode, sessions=3"}
```

Fields:
- `date`: ISO date
- `model`: exact model ID
- `score`: agreements / total
- `pct`: decimal 0.0–1.0
- `trigger`: T1-T5 from G0
- `notes`: session count, mode (API/CLI), any anomalies

**Baseline rule**: First measurement establishes the baseline. Subsequent measurements compare against prior max. Regression = drop > 5pp from prior max.

---

## G3 — Drift Diagnostic Tree

If score < 97%:

```
Step 1: Identify slipping scenarios
  → Re-run with --scenarios individual
  → List all scenarios below 2/3 agreement

Step 2: Classify each slipping scenario
  → Category A: Deterministic rule (should not slip) → DNA write defect
  → Category B: LLM-boundary (formula/inference) → expected, track separately
  → Category C: New scenario with no DNA anchor → add anchor

Step 3: Resolve by category
  → A: Compare dna_core.md vs dna_full.md → find missing or contradicted rule
       → Run SOP #79 (DNA Update Protocol) to write fix
       → Re-run cross-instance test after update
  → B: Document in LLM-boundary registry (permanent, not fixable)
  → C: Write missing anchor to dna_core.md → re-run consistency test
```

---

## G4 — Emergency Protocol (Score < 80%)

**STOP** all DNA writes until resolved.

```
1. Run full diagnostic (G3 Step 1-3 for ALL scenarios)
2. Identify if regression is from:
   a. DNA corruption (contradictory rules added)
   b. Model behavioral shift (new model version)
   c. Test set expansion without DNA update
3. Resolution paths:
   a. DNA corruption: rollback to last clean git commit → identify bad write → re-apply correctly
   b. Model shift: re-validate entire dna_core.md against new model; update prompts where needed
   c. Coverage gap: run SOP #74 (Boot Test Evolution) to add anchors for new scenario domains
4. Confirm recovery: 2 consecutive clean runs at ≥97% before resuming normal operations
```

---

## G5 — Health Report

After each run, append to `results/cold_start_health_report.md`:

```
## Cross-Instance Check — {{date}} (SOP #94 G1)
- Model: {{model}}
- Score: {{score}}/{{total}} ({{pct}}%)
- Classification: {{STABLE/WATCH/DRIFT/CRITICAL}}
- Trigger: {{T1-T5}}
- Slipping scenarios: {{none / list}}
- Action taken: {{none / G3 diagnostic / G4 emergency}}
- Next scheduled: {{date}}
```

---

## Integration with Other SOPs

| SOP | Relationship |
|-----|-------------|
| SOP #79 (DNA Update Protocol) | G3 resolution path A: DNA fix |
| SOP #80 (Cold Start Calibration) | Runs deterministic tests; G94 adds cross-instance layer |
| SOP #91 (Monthly DNA Calibration Audit) | Run SOP #94 T2 trigger after each SOP #91 write cycle |
| SOP #93 (LLM Boot Test Validation) | Covers LLM-boundary scenarios (SOP #94 G3 Category B) |
| SOP #74 (Boot Test Evolution) | G4 path C: add anchors when coverage gaps surface |

**Monthly DNA maintenance full cycle:**
`SOP #80` (deterministic 33/33) + `SOP #91` (new life decisions) + `SOP #94` (cross-instance 97-100%) = complete monthly calibration.

---

## Self-Test

**Scenario (from cycle 259 baseline):**

> Cross-instance test run: 39/39 (100%) via API, model=claude-sonnet-4-6, sessions=3. Date: 2026-04-09.
> Next model update is deployed. Cross-instance drops to 87%.

**Expected response using this SOP:**

1. G0 T3 triggered (model version change)
2. G1 classify: 87% = DRIFT
3. G3 Step 1: run `--scenarios individual` → identify which 5/39 slip
4. G3 Step 2: classify slipping scenarios → likely Category B (LLM-boundary) or C (new behavior)
5. G3 Step 3 resolution → for C: add anchors; for B: document in LLM-boundary registry
6. Re-run → confirm ≥97% before closing G3
7. G5: log to cold_start_health_report.md; next scheduled = quarterly

**Verdict: SOP #94 SELF-TEST PASS ✅**

---

*SOP #94 — Cross-Instance Calibration Maintenance Protocol. Closes maintenance gap: 100% agreement measured ≠ 100% agreement maintained. Full monthly calibration stack: SOP #80 + SOP #91 + SOP #94.*
