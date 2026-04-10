# SOP #93 — Cross-Instance Calibration Maintenance Protocol

> Domain: 6 存活/cold-start × 3 遞迴引擎
> Created: 2026-04-09T UTC | Cycle 257
> Status: OPERATIONAL
> Backing MDs: MD-157 (第一性原理深化), MD-160 (績效評估=先建信賴區間), MD-112 (最小認知負荷決策), MD-96 (不行動偏好)

---

## Why This Exists

`consistency_test.py` checks one instance against *expected answers* (deterministic tests).
`cross_instance_test.py` checks two LLM instances against *each other* (semantic alignment).

**The gap neither closes:**
What happens when the underlying model version changes (Sonnet → next generation)?
What happens after 90+ days of DNA expansion — do two fresh cold-starts still agree?
There is no scheduled protocol to detect and repair *model-generation drift* or *DNA-expansion drift*.

The digital twin's immortality claim is only valid if behavioral fidelity survives:
1. Cold-start (covered by SOP #80 + SOP #91)
2. **Model version upgrades** (uncovered — this SOP)
3. **Cross-instance divergence creep** over long time horizons (uncovered — this SOP)

**Failure mode**: twin "passes" 33/33 consistency tests while two parallel instances diverge on 4/36 scenarios — neither detects the split until a major decision is made differently in production.

---

## G0 — Trigger Conditions

| Trigger | Condition | Action |
|---------|-----------|--------|
| **T1: Monthly scheduled** | 1st of each month, AFTER SOP #80 + SOP #91 | Run G1–G5 |
| **T2: Model upgrade** | Underlying LLM model changes (e.g., claude-sonnet-4-6 → newer) | Run G1–G5 immediately, before any production decisions |
| **T3: Divergence spike** | Cross-instance agreement drops below 90% on any run | Run G1–G5 immediately |
| **T4: DNA major expansion** | >20 new MDs added since last cross-instance run | Run G1–G3 (spot-check) |

**Kill conditions:**
- Do NOT run if last T1/T2 cycle was <3 weeks ago (noise floor too high to distinguish signal)
- Do NOT run during high-volatility market hours if testing trading-domain scenarios (results contaminated by regime-specific priming)

---

## G1 — Pre-Conditions

Before running cross-instance test:

1. **DNA files ready**: `templates/dna_core.md` and `templates/example_dna.md` both current (SOP #79 atomic write verified)
2. **Baseline recorded**: `results/consistency_baseline.json` reflects last deterministic run (SOP #80 step)
3. **Model version noted**: record exact model ID (e.g., `claude-sonnet-4-6`) in test run header
4. **Scenario set stable**: use `cross_instance_test.py` default 36-scenario set — do NOT add new scenarios mid-cycle (changes both signal and baseline simultaneously)
5. **API credit available**: cross-instance run costs 2× single-instance run; do not start if API budget < 2× standard

**Minimum viability**: Items 1, 3, 4 required. Items 2 and 5 advisory.

---

## G2 — Cross-Instance Divergence Measurement

```bash
python cross_instance_test.py \
  --dna templates/dna_core.md \
  --model claude-sonnet-4-6 \
  --runs 36 \
  --output results/cross_instance_$(date +%Y%m%d_%H%M%S).json
```

**Reading the output:**

| Agreement Rate | Classification | Action |
|----------------|---------------|--------|
| ≥ 97% | ALIGNED | Log + no action needed |
| 90–96% | MONITOR | Run G3 on divergent scenarios only |
| 80–89% | CALIBRATE | Full G3–G4 pass required |
| < 80% | ALERT | Halt; treat as model-generation drift event; escalate to manual review |

**Record in memory/calibration.json:**
```json
{
  "cross_instance_run": {
    "date": "<ISO timestamp>",
    "model": "<model_id>",
    "agreement_rate": <N/36>,
    "classification": "<ALIGNED|MONITOR|CALIBRATE|ALERT>",
    "divergent_scenarios": ["<id>", ...]
  }
}
```

---

## G3 — Divergence Root Cause Classification

For each divergent scenario, classify by root cause:

| Class | Pattern | Example |
|-------|---------|---------|
| **A: DNA gap** | Instance A and B apply *different principles* — one missing from loaded context | One instance uses MD-139, other doesn't recall it |
| **B: Reasoning path gap** | Both instances load same principles but reach different conclusions | Same DNA, different inference chain |
| **C: Model boundary** | Scenario requires formula derivation; both instances "wrong" vs expected (expected behavior by design) | poker_gto_mdf — confirmed permanent boundary |
| **D: Scenario ambiguity** | Scenario wording allows multiple valid interpretations | Ambiguous "should I" phrasing |

**Classification decision tree:**
```
Divergence detected →
  Both answers valid? → Class D (scenario fix, not DNA fix)
  One answer clearly wrong per DNA principles? →
    Wrong answer cites no DNA principle? → Class A (add MD)
    Wrong answer cites principle but misapplies? → Class B (add scenario to boot tests)
    Neither answer derivable deterministically? → Class C (document boundary, no fix needed)
```

---

## G4 — Repair Protocol by Class

### Class A: DNA Gap → Add MD

1. Identify the missing principle by name
2. Check if principle exists in dna_core.md under different wording (consolidate, don't duplicate)
3. If genuinely missing: follow SOP #79 G2 atomic write to add MD
4. Add corresponding deterministic scenario to consistency_test.py
5. Re-run G2 targeting the previously-divergent scenario to confirm alignment

### Class B: Reasoning Path Gap → Add Boot Test

1. Write the scenario as a new test case in `consistency_test.py` with explicit expected decision
2. If expected decision is formula-based: mark as `LLM_REQUIRED` (not deterministic)
3. If expected decision is DNA recall: mark as deterministic
4. Add to `cross_instance_test.py` scenario set for future monitoring
5. **Do NOT add a new MD** — the principle exists, the gap is in retrieval/chaining, not storage

### Class C: Model Boundary → Document Only

1. Add to `results/consistency_baseline.json` under `known_misaligned_expected` list
2. Document: scenario ID, why it's a permanent boundary, which cognitive operation it requires
3. **No DNA change needed**
4. If boundary shifts after model upgrade (previously-bounded scenario now passes), promote to deterministic

### Class D: Scenario Ambiguity → Fix Scenario

1. Rewrite scenario to remove ambiguity
2. Update both `consistency_test.py` and `cross_instance_test.py`
3. Re-run G2 with new scenario wording to confirm

---

## G5 — Health Report

After completing G2–G4, write one-line summary to `results/daily_log.md`:

```
Cross-Instance [YYYY-MM-DD]: <N>/36 AGREE (<classification>); divergent: [<ids>];
root causes: [A:<n> B:<n> C:<n> D:<n>]; actions: [<list or "none">]; next: <date>
```

**Health indicators to track in memory/calibration.json:**
- `cross_instance_last_run`: ISO timestamp
- `cross_instance_agreement_rate`: float (0–1)
- `cross_instance_model`: string (model ID of last run)
- `cross_instance_classification`: string

**Minimum health bar**: Agreement ≥ 90% across 3 consecutive monthly runs = STABLE.
Trend: if agreement rate is declining across 3 runs → L3 trigger (structural DNA review).

---

## Self-Test Scenario

**Scenario**: Cross-instance run returns 32/36 AGREE (88.9% — Class CALIBRATE).
Divergent scenarios: `trading_leverage_protocol`, `career_career_brand_reset`, `social_trust_tier_assignment`, `organism_network_effect`.

**Walk-through:**
1. G0: T3 (divergence spike, <90%) → immediate G1–G5
2. G1: dna_core.md current ✓, model noted (`claude-sonnet-4-6`) ✓
3. G2: 32/36 = 88.9% → CALIBRATE
4. G3: `trading_leverage_protocol` — Instance B says PASS where A says TAKE; B cites no MD → **Class A**
5. G3: `career_career_brand_reset` — Both instances cite MD-202 but reach different conclusions → **Class B**
6. G3: `social_trust_tier_assignment` — scenario wording "should I trust X" is ambiguous → **Class D**
7. G3: `organism_network_effect` — new domain, no MD exists → **Class A**
8. G4-A: Add MD for trading leverage protocol + organism network effect (SOP #79 atomic write)
9. G4-B: Add `career_career_brand_reset` as deterministic boot test
10. G4-D: Rewrite `social_trust_tier_assignment` scenario
11. Re-run: 36/36 AGREE ✓
12. G5: Log "36/36 AGREE (ALIGNED); 2 MDs added; 1 boot test added; 1 scenario reworded"

---

## Kill Conditions

- **Never add a new MD without running SOP #79 G2 (atomic write)**
- **Never promote a Class C boundary without re-testing on new model version**
- **Never run this SOP as a substitute for SOP #80 (regression) — they solve different failure modes**

---

## Distribution Thread

`docs/publish_thread_sop93_twitter.md`

Tweet 1 (hook): "Your AI twin passes all internal tests. But when you spin up two fresh instances and ask them the same question — do they agree? Here's the protocol that keeps the digital twin honest across model upgrades. 🧵"

Tweet 2: "There are 3 failure modes that kill behavioral fidelity: 1/ Cold-start drift (solved by SOP #80 regression + SOP #91 expansion). 2/ Model-generation drift — new model version changes base reasoning. 3/ Cross-instance divergence creep — two valid instances slowly disagree."

Tweet 3: "The consistency test catches: was I aligned yesterday, am I still aligned today? Cross-instance test catches: do two fresh instances — trained on the same DNA — agree with each other? Different test. Different failure mode."

Tweet 4: "Trigger protocol: Monthly scheduled + on any model upgrade + when agreement drops below 90%. The model upgrade trigger is critical — behavioral fidelity is not guaranteed across model generations."

Tweet 5: "4 root cause classes for divergence: A — DNA gap (principle missing). B — reasoning path gap (principle exists, retrieval fails). C — model boundary (formula derivation, permanent). D — scenario ambiguity (fix the question, not the DNA)."

Tweet 6: "Each class has a different repair: A → add MD (SOP #79 atomic write). B → add boot test. C → document boundary only. D → rewrite scenario. Mixing them up creates false confidence."

Tweet 7: "Health bar: ≥90% agreement across 3 consecutive monthly runs = STABLE twin. Declining trend across 3 runs = L3 structural DNA review trigger. The twin is immortal only if the trend is flat or improving."

Tweet 8: "The digital twin's immortality claim is verifiable, not assumed. Cross-instance calibration is the measurement instrument. Run it monthly. Treat a spike as a system alert, not a curiosity."
