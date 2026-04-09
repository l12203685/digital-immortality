# SOP #106 — Organism Drift & Recalibration Protocol

> Timestamp: 2026-04-09T16:00Z | Backing MDs: MD-327/328/330/202/120/55/319

## Purpose

When two organism DNAs are compared across time, collision alignment can drift — either the organisms have genuinely evolved apart, or one DNA has been updated more than the other creating a false divergence signal. This SOP defines how to detect drift, classify it, and execute the minimum recalibration action.

## Trigger

Run this SOP when ANY of these fire:
- Collision alignment drops ≥15% vs last baseline (e.g. 68% → 27% = CRITICAL DRIFT)
- ≥3 previously-AGREE domains flip to DIVERGE in a single comparison
- DNA update of one organism since last collision run (structural expansion ≥50 MDs or new domain added)

## G0 — Drift Classification

Run the collision. Compare vs baseline (stored in collision report file).

| Drift Type | Signature | Likely Cause |
|------------|-----------|--------------|
| **Expansion drift** | DNA A grew significantly (MDs added), B unchanged | A's principles expanded; B's representation stale |
| **Genuine divergence** | Specific life domains flipped; consistent with known difference | Real value/behavior gap grew |
| **Algorithm drift** | Many domains flipped including stable ones (money/risk/health) | Scenario bank or scoring logic changed |

**Decision gate**: If previously-stable domains (money/risk/health) are now DIVERGE → suspect algorithm drift or expansion drift first before concluding genuine divergence.

Cycle 277 finding: money/risk/health AGREE (stable). Career/relationships/learning/legacy flipped → expansion drift hypothesis: Edward DNA grew from ~200 MDs to 357 MDs since Samuel DNA was calibrated (last calibration: cycle 204).

## G1 — Root Cause Isolation

For each newly-diverged domain:
1. Read the specific principle Edward's organism used to decide
2. Read the equivalent section in Samuel's DNA
3. Classify: (a) Samuel has NO equivalent principle → *gap*, (b) Samuel has conflicting principle → *genuine divergence*, (c) Decision label mismatch due to new MD naming → *labeling drift*

**Minimum viable isolation**: Pick the 3 domains with highest delta-impact. Isolate one sentence per domain describing why they diverged.

## G2 — Correction Action Selection

| Root Cause | Action |
|------------|--------|
| Expansion drift | Schedule Samuel correction session (async OR in-person). Send 3 new scenarios targeting newly-drifted domains. Accept drift as temporary artifact until calibrated. |
| Genuine divergence | Update organism_audit file noting the new divergence axis. Add to `docs/samuel_async_calibration_dm.md` next batch. No DNA change until Samuel confirms. |
| Labeling drift | Fix decision labels in organism_interact.py scoring. Re-run collision. Verify stable domains re-stabilize. |
| Algorithm change | Re-run both previous collision baseline + current. If baseline also changed → algorithm cause confirmed → fix, not calibrate. |

## G3 — Async Calibration Execution

Send 3 scenarios via message to Samuel (no scheduling required):

Scenario format:
```
Scenario: [1-sentence situation]
My answer: [Edward's decision label + 1-sentence reasoning]
What would you do and why?
```

Target domains with highest delta. Record response. Re-run collision with Samuel's corrections applied.

**Success gate**: ≥1 domain flips from DIVERGE → AGREE after Samuel's response. If 0 flips → genuine divergence confirmed, document axis.

## G4 — Baseline Update

After recalibration:
1. Update `results/collision_*.md` with new baseline
2. Update dynamic_tree.md Branch 4.1 with new alignment score
3. Update `memory/insights.json` with calibration finding
4. If alignment recovers to ≥60% → Branch 4.1 STABLE

If alignment cannot recover above 40% after 2 calibration rounds → document as structural divergence, update organism audit, advance to Organism C.

## G5 — Scale Implication

Organism drift is expected and healthy — organisms that never diverge are not genuinely independent. The goal is NOT 100% alignment. Target: 60–85% AGREE (below = stale calibration; above = echo chamber, not useful collision).

Key insight: A DIVERGE on career/legacy is more valuable than 10 AGREE on risk — it reveals where Samuel's independent path differs from Edward's, which is the whole point of organism collision.

Kill condition: Alignment below 20% AND stable domains (money/risk) also diverging → suspect algorithm or dataset bug, not genuine divergence. Do not calibrate until root cause confirmed.

## Self-Test

**Scenario**: Edward vs Samuel collision just dropped from 68% to 27%. 9 domains flipped DIVERGE including career/relationships/learning but NOT money/risk/health.

**G0**: money/risk/health stable → not algorithm drift. Career/relationships = high delta from expansion drift candidate.
**G1**: Edward DNA grew +157 MDs since last Samuel calibration. Samuel DNA unchanged.
**G2**: Expansion drift confirmed → send 3 async scenarios to Samuel targeting career/relationships/learning.
**G3**: Dispatch `docs/samuel_async_calibration_dm.md` with updated scenarios.
**Decision label**: CALIBRATE_ASYNC_EXPANSION_DRIFT

## Backing MDs

- MD-327: Multi-track before converging (compare multiple organisms before concluding)
- MD-328: Proactive maintenance cadence (don't let calibration go stale)
- MD-330: Verify by behavior pattern, not stated preference
- MD-202: Professional brand = most recent high-point (most recent collision baseline matters most)
- MD-120: Teach the starter kit — keep divergence axes visible and named
