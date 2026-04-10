# SOP #93 — LLM Boot Test Validation Protocol
**Domain**: Branch 6 — Behavioral Consistency / Cold-Start Integrity  
**Version**: 1.0  
**Created**: 2026-04-09T11:40Z  

---

## Problem Statement

The deterministic consistency engine catches 33/33 rule-based scenarios but cannot evaluate 3 critical behavioral domains that require LLM reasoning:

- `poker_gto_mdf` — GTO minimum defense frequency calculation  
- `trading_atr_sizing` — ATR-based position sizing formula  
- `career_multi_option_ev` — Multi-option EV comparison before committing  

These 3 scenarios are perpetually MISALIGNED in deterministic mode (expected). Without a protocol to validate them via LLM, boot test coverage stays at 91.4% (33/36 scenarios).

---

## G0 — Trigger

Activate this protocol when:
- Consistency test shows ≥1 MISALIGNED scenario flagged as `LLM_REQUIRED`  
- New boot test added for a domain requiring multi-step inference  
- Monthly DNA calibration audit (SOP #91) surfaces new decision patterns  
- Cold-start behavioral integrity report flags reasoning drift  

---

## G1 — LLM Scenario Classification

Classify each MISALIGNED scenario:

| Type | Description | Validation Method |
|------|-------------|-------------------|
| **Formula** | Requires arithmetic (MDF, ATR, EV) | Run LLM with explicit inputs, verify formula output |
| **Inference** | Requires multi-step reasoning chain | Run LLM with scenario, verify decision path matches DNA |
| **Context-dependent** | Outcome varies by unstated assumptions | Run LLM with full context, verify output range |

Current LLM-required scenarios:
- `poker_gto_mdf` → Type: **Formula** (MDF = 1 − α)  
- `trading_atr_sizing` → Type: **Formula** (position size = risk_per_trade / (ATR × multiplier))  
- `career_multi_option_ev` → Type: **Inference** (list all options → calculate EV → select highest)  

---

## G2 — Validation Script

For each LLM-required scenario, run:

```bash
python consistency_test.py templates/dna_core.md \
  --scenarios results/consistency_baseline.json \
  --output-dir results
```

Then manually verify LLM outputs against expected DNA behavior:

**poker_gto_mdf**:
- Input: opponent bets X into pot P  
- Expected output: MDF = 1 − (X / (X + P))  
- Pass criterion: LLM calculates using formula, not feeling  

**trading_atr_sizing**:
- Input: account $10K, risk 1%, ATR=500, multiplier=2  
- Expected output: position = $100 / (500×2) = 0.1 units  
- Pass criterion: LLM uses ATR formula, not intuition  

**career_multi_option_ev**:
- Input: 3 career paths with different wait costs  
- Expected output: lists all options → calculates wait cost arithmetic → selects highest adjusted EV  
- Pass criterion: LLM follows MD-333 multi-path decision arithmetic  

---

## G3 — Pass/Fail Criteria

| Result | Criterion | Action |
|--------|-----------|--------|
| **PASS** | LLM output matches expected formula/reasoning in ≥2/3 runs | Mark VALIDATED, log to dynamic_tree |
| **WATCH** | Correct answer but wrong reasoning path | Note in boot_tests.md, retest next cycle |
| **FAIL** | Wrong answer or missing key formula step | Find which MD premise is wrong → fix DNA → re-test |

---

## G4 — Boot Test Coverage Tracking

```
Coverage rate = (validated_scenarios / total_scenarios) × 100
Target: ≥80% validated (deterministic + LLM-validated)
Current: 33/36 deterministic = 91.4% (LLM-required: 0/3 formally validated)
Full coverage target: 36/36 = 100%
```

Append result to `results/boot_test_coverage_log.jsonl`:
```json
{"ts": "<UTC>", "cycle": N, "deterministic": 33, "llm_validated": 0, "total": 36, "coverage_pct": 91.4}
```

---

## G5 — Revenue Bridge

LLM Boot Test Validation Protocol is a **premium service component**:

- Demonstrates behavioral consistency across reasoning domains (not just rule lookup)  
- Client-facing value: "Your twin passes formula-based and inference-based tests, not just keyword matching"  
- Upsell: run LLM validation as monthly verification → charging $29/month premium tier  
- Differentiator vs competitors: most AI twins do not validate multi-step reasoning consistency  

---

## Anti-Patterns

| Pattern | Why It Fails |
|---------|-------------|
| Treating 3 MISALIGNED as "expected, ignore" | Leaves 8.6% of critical domains unvalidated — drift goes undetected |
| Running LLM validation once and assuming permanent pass | LLM behavior can drift with model updates — needs periodic re-run |
| Using wrong scenario inputs | Formula tests require specific numeric inputs to verify correct formula usage |

---

*Series: SOP #01~#93 COMPLETE. Posting queue: Sep 5.*
