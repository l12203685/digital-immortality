# SOP #75: Organism Network Architecture

> One organism self-validates using boot tests and consistency checks. A network of organisms cross-validates using divergence. This SOP governs how to build and run the organism network.

---

## Problem

Self-validation has a ceiling: the agent can only catch divergence from its own DNA. When DNA is wrong, self-tests pass but behavior is miscalibrated. A second organism — one with different principles — can surface these blind spots through collision.

**Failure mode**: closed-loop self-validation feels complete but never detects principle-level errors. The agent confirms its own biases, not the person's actual decisions.

---

## Three-Layer Structure

| Layer | Purpose | Cadence |
|-------|---------|---------|
| L1 Execute | Run organism collision on new scenarios | Per calibration session |
| L2 Evaluate | Score divergence — find structural disagreements | After each collision |
| L3 Evolve | Update DNA on divergence; escalate to real Edward for ground truth | When agreement < 70% on a domain |

---

## G0: Network Inventory

**Trigger**: start of any organism-interact session

**Procedure**:
1. List active organisms: `ls templates/*_dna*.md`
2. For each organism: confirm DNA freshness (timestamp < 30 days)
3. Map coverage: which domains does each organism pair cover?
4. Log: `results/organism_network_status.json`

**Output format**:
```json
{
  "ts": "ISO8601",
  "organisms": ["Edward", "Samuel", "Organism_C"],
  "pairs_active": ["Edward×Samuel"],
  "pairs_pending": ["Edward×Organism_C", "Samuel×Organism_C"],
  "coverage_domains": ["trading", "career", "finance", "relationships"]
}
```

---

## G1: Pairwise Collision

**Trigger**: new organism added, or 30 days since last collision for an existing pair

**Command**:
```bash
python organism_interact.py templates/dna_core.md templates/<other>_dna.md --all
```

**Minimum scenario set**: 10 scenarios covering trading, finance, career, relationships, identity.

**Output**: `results/collision_<A>×<B>_<timestamp>.json`

---

## G2: Divergence Triage

**Trigger**: collision complete

**Score each domain**:
| Agreement | Status | Action |
|-----------|--------|--------|
| ≥ 80% | ALIGNED | No action |
| 60–79% | WATCH | Note divergence, log pattern |
| < 60% | DIVERGENT | Surface to real person for ground truth |

**Domain-level verdict**:
- If trading divergence: re-run against Edward's real trading decisions (ground truth)
- If career divergence: ask Edward directly — which reasoning matches his actual past decision?
- If identity divergence: treat as high-priority calibration gap; update the lower-fidelity organism

---

## G3: Ground Truth Escalation

**Trigger**: any domain with agreement < 60%

**Procedure**:
1. Extract the specific divergent scenario
2. Reframe as a concrete past decision: "When [specific situation], what did you actually do?"
3. Present both organism responses to Edward
4. Record ground truth in `results/ground_truth_log.jsonl`:
```json
{"ts": "...", "scenario_id": "...", "edward_answer": "...", "organism_a_response": "...", "organism_b_response": "...", "verdict": "A|B|Neither", "correction_note": "..."}
```
5. Update the lower-fidelity organism's DNA with the correction
6. Add new boot test case from the correction (per SOP #74 G3)

---

## G4: Network Value Accounting

**What the network produces that self-validation cannot**:

| Mechanism | Value |
|-----------|-------|
| Blind spot detection | Catches principle-level errors invisible to self-check |
| Calibration acceleration | Two organisms + ground truth > one organism + 100 self-tests |
| Divergence = information | Each disagreement is a hypothesis: which organism is more calibrated? |
| Emergent coverage | Organism B's domains extend Organism A's test surface |

**Key insight (MD-134 pattern)**: Information asymmetry between organisms is a feature, not a bug. Maximum divergence → maximum calibration signal. Seek organisms with different domain expertise, not similar ones.

---

## G5: Network Growth Protocol

**When to add a new organism**:
- Person has deep relationship with someone in a domain Edward wants to cover (e.g., startup → entrepreneur organism)
- Existing network has < 3 active pairs
- A domain has zero cross-validation coverage

**Minimum onboarding for a new organism**:
1. Run `/guided-onboarding` to build initial DNA (or manual fill)
2. Run collision against Edward immediately: find agreement baseline
3. If baseline < 50% → organism DNA needs more calibration before adding to network
4. If baseline ≥ 50% → activate; start G1/G2 cycle

---

## Organism Network Status (2026-04-09)

| Pair | Scenarios | Agreement | Last Run | Next Action |
|------|-----------|-----------|----------|-------------|
| Edward × Samuel | 22 | 68% (15/22) | cycle 207 | Send async DM (human-gated) |
| Edward × Organism C | 0 | — | — | Fill §0 + §7 in `templates/organism_c_draft.md` (human-gated) |
| Samuel × Organism C | 0 | — | — | Blocked on both |

**Network bottleneck**: all expansion is human-gated. Agent-side is ready. Critical path = Edward fills Organism C template and sends Samuel DM.

---

## DNA Anchors

- MD-134 (信息不對稱決定行動方向 — applies to organisms: asymmetry = calibration signal)
- MD-12 (every correction = new boot test case)
- MD-330 (verify by behavior pattern, not recitation)
- MD-89 (L1/L2/L3 three-layer loop)
- MD-02 (自推到底再確認 — organism collision IS the 確認 step)

---

*SOP #75 | Cycle 240 | 2026-04-09T UTC*
