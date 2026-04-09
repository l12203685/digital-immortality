# SOP #95 — Organism Network Effect Protocol

> Branch 4 — 社交圈 / collective intelligence
> Created: 2026-04-09T00:00Z (cycle 260)
> Domain: Social intelligence / emergent network
> Backing MDs: MD-327, MD-328, MD-330, MD-202, MD-120, MD-319, MD-55
> Decision label: EXTRACT_COLLECTIVE_INTELLIGENCE

---

## One Claim

One collision finds blindspots. Two collisions find principles. Three collisions find what is structurally true about how people differ — and that is the insight no single relationship can produce.

---

## Why This Works

A single organism collision (SOP #44) tells you where two decision frameworks diverge. That is useful. But it cannot tell you whether a divergence is idiosyncratic — specific to that one person — or structural — a recurring axis where humans consistently split.

Network collision solves this. When you run three or more organisms against the same scenario set:

- A divergence that appears in only one pair → possibly idiosyncratic
- A divergence that appears in two or more pairs, on the same axis → structural split
- Three+ organisms agreeing on something counterintuitive → high-confidence principle
- Three+ organisms diverging on the same axis → population-level insight worth publishing

The signal is in the pattern across pairs, not in any single pair.

**Math:**
- 2 organisms: 1 pair collision (A↔B)
- 3 organisms: 3 pair collisions (A↔B, A↔C, B↔C) + 1 triangle
- 4 organisms: 6 pair collisions + 4 triangles
- N organisms: N(N-1)/2 pair collisions

Each organism added multiplies the collision surface. The triangle is the richest unit: A diverges from B on axis X; C agrees with A. You now know X is a value split, not a style difference.

**Current status**: Edward (A) + Samuel (B) = 1 pair operational. This SOP activates at ≥2 organisms. Target: Organism C to enter triangle phase.

---

## Gates

### G0 — Network Size Check + Collision Coverage Audit

Before running network analysis, verify the organism pool is sufficient and current.

**Minimum viable network:**

| Organisms | Collision pairs | Triangle collisions | Minimum for network effect |
|-----------|----------------|--------------------|-----------------------------|
| 2 | 1 | 0 | Pair analysis only |
| 3 | 3 | 1 | Minimum triangle — network effect begins |
| 4 | 6 | 4 | Full divergence mapping possible |
| 5+ | 10+ | 10+ | Population-level signal extraction |

**Coverage audit — run before analysis:**

```bash
# Check all organism DNA files exist and are calibrated
ls templates/*_dna.md

# Verify each organism has been collision-tested at least once
grep -r "calibration_status" templates/*_dna.md

# Check last collision date per organism
grep -r "last_collision" results/
```

**Kill conditions (do not proceed):**
- Organism pool < 2 → no network exists; return to SOP #44
- Any organism DNA last calibrated > 90 days ago → stale; re-run calibration before network analysis
- Any organism has < 5 principles in §0 → too thin; collision produces noise

**Coverage matrix output:**

After audit, build a coverage matrix: rows = scenarios, columns = organisms. Mark each cell as tested/untested. Network analysis requires ≥80% coverage per organism pair.

---

### G1 — Emergent Pattern Detection

Run all-pairs collision. Identify divergence axes that are structural vs. idiosyncratic.

**Step 1: Run all-pairs collision**

```bash
# For each pair of organisms, run collision and save report
python organism_interact.py templates/dna_core.md templates/samuel_dna.md --report > results/collision_AB.txt
python organism_interact.py templates/dna_core.md templates/organism_c_dna.md --report > results/collision_AC.txt
python organism_interact.py templates/samuel_dna.md templates/organism_c_dna.md --report > results/collision_BC.txt
```

**Step 2: Extract divergence axes from each report**

For each collision report, list:
- Scenario ID
- Domain (social_trust, network_roi, learning, legacy, etc.)
- Organism pair
- Divergence direction (e.g., A→explicit / B→implicit)

**Step 3: Classify each axis as STRUCTURAL or IDIOSYNCRATIC**

| Classification | Criterion | Action |
|---------------|-----------|--------|
| STRUCTURAL | Axis appears in ≥2 organism pairs | Extract as candidate principle; publish |
| IDIOSYNCRATIC | Axis appears in only 1 pair | Note; do not generalize |
| UNKNOWN | Only 1 pair tested on this axis | Flag for next organism addition |

**Output:** A divergence axis table with classification. Example:

```
Axis: relationship_downgrade_style
  - A↔B: diverge (explicit vs quiet withdrawal) ✓
  - A↔C: diverge (explicit vs. gradual distance) ✓
  - B↔C: agree (quiet withdrawal)
  → Classification: STRUCTURAL (2 pairs diverge on same axis)
  → Finding: explicit renegotiation is a minority policy; quiet withdrawal is the default
```

---

### G2 — Collective Intelligence Extraction

The non-obvious output. Patterns that only emerge from multi-organism data.

**Rule 1: High-confidence principle (3+ organisms agree on something unusual)**

If three organisms all make the same counterintuitive call on a scenario, and it contradicts common advice, you have a high-confidence principle.

Unusual = contradicts what most people say they would do.
High-confidence = not a social desirability artifact; three independent models converging.

Write this to `memory/insights.json` as a new principle with evidence:

```json
{
  "principle": "...",
  "evidence": "organisms A, B, C all chose X on scenario Y despite domain default being Z",
  "confidence": "high",
  "date": "YYYY-MM-DD",
  "source": "network_collision_G2"
}
```

**Rule 2: Population insight worth publishing (3+ organisms diverge on same axis)**

If three organisms all diverge on the same axis, you have found a domain where humans have genuinely different policies — not wrong ones, just different.

This is more valuable to publish than any single organism's view, because the insight is:
*"On [axis], people systematically differ. Here are the 2–3 policies and their underlying premises."*

This is a thread, not an opinion. Write the draft to `staging/` for the content pipeline.

**Rule 3: Triangle confirmation (A↔B diverge, C agrees with A)**

When A and B diverge on axis X, and C agrees with A:
- X is a value split, not a style difference (confirmed by triangulation)
- A's policy is not idiosyncratic — at least one other organism independently converged on it
- B's policy is the minority; worth understanding why

Write the confirmed axis to your own DNA as a principle clarification: not a new principle, a sharpened one.

---

### G3 — Network Expansion Trigger

When to add Organism C (or D, E...): use collision rate as the signal.

**Expansion logic:**

| Current collision rate (all pairs) | Signal | Action |
|------------------------------------|--------|--------|
| < 75% AGREE | Calibration not complete | Do NOT add new organism yet; calibrate existing ones first |
| 75–90% AGREE | Healthy divergence band | OK to add new organism; divergence surface is productive |
| > 90% AGREE | Low signal | SHOULD add new organism; network is too homogeneous, not generating insight |

**Organism C selection criteria:**

The goal is to maximize structural divergence surface without adding noise. Select a candidate who:

1. You have ≥18 months of behavioral observation
2. Has at least 2 known domains where they think differently from existing organisms
3. Is willing to run a calibration session (SOP #44 G2)
4. Is NOT a close ideological mirror of any existing organism (check §7 before building DNA)

**When NOT to add:**
- Current network has unresolved calibration debt (any organism > 90 days since collision)
- You cannot write ≥5 behavioral principles from observation alone
- The candidate is going through a major life transition (DNA will be stale immediately)

---

### G4 — Quality Decay Prevention

Organisms decay. Networks decay faster, because staleness compounds across pairs.

**Staleness rules:**

| Condition | Staleness level | Action |
|-----------|----------------|--------|
| Any organism DNA untouched > 90 days | STALE | Re-run collision; calibrate before network analysis |
| Major life event for any organism (job, city, relationship) | LIKELY STALE | Update §1 + §5; re-run collision immediately |
| Quarterly maintenance | ROUTINE | Re-run all-pairs collision; check divergence drift |
| Agreement rate on any axis shifts > 15pp | DRIFT DETECTED | Identify which organism changed; run SOP #44 G3 on that organism |

**Staleness detection script:**

```bash
# Check last_calibrated dates across all organisms
python organism_interact.py --status-all
# Output: organism name, last_calibrated date, days_since_calibration
```

**What to do when staleness is detected:**

1. Do NOT run network analysis on stale data — results are meaningless
2. Run SOP #44 (single organism calibration) for the stale organism first
3. After calibration, re-run only the pairs that include the updated organism
4. Check if divergence axes shifted — if yes, re-classify structural/idiosyncratic

**Network kill condition:**

If all organisms are uncalibrated > 90 days AND no calibration sessions are schedulable within 30 days → archive the network state to git, note the last valid measurement date, and restart from SOP #44 with the highest-priority organism.

---

## Self-Test

> You have 3 organisms: A (yourself), B (Samuel), C (new person added last week). You run all-pairs collision.
>
> Results:
> - A↔B: 68% agree; diverge on relationship_downgrade, learning, legacy
> - A↔C: 71% agree; diverge on relationship_downgrade, trust_velocity, network_roi
> - B↔C: 82% agree; diverge on network_roi
>
> Apply the gates. What is the output?

**G0 check:** 3 organisms, all calibrated within 90 days, all ≥5 principles. Network viable.

**G1 — divergence axis classification:**

```
relationship_downgrade: appears in A↔B and A↔C → STRUCTURAL
  (A is the outlier: 2/2 pairs where A appears, A diverges from the other)
network_roi: appears in A↔C and B↔C → STRUCTURAL
  (C is the outlier: 2/2 pairs where C appears, C diverges from the other)
learning: appears in A↔B only → IDIOSYNCRATIC (for now)
legacy: appears in A↔B only → IDIOSYNCRATIC (for now)
trust_velocity: appears in A↔C only → IDIOSYNCRATIC (for now)
```

**G2 — collective intelligence:**

- A↔B and A↔C both diverge on `relationship_downgrade`, with B and C both choosing quiet withdrawal vs A choosing explicit renegotiation → A's explicit policy confirmed structural minority
- B↔C high agreement (82%) combined with both diverging from A on this axis → triangle confirmation: A's explicit renegotiation is a distinct value system, not idiosyncratic error

**G3 — expansion trigger:**

- Overall network: (68+71+82)/3 = 74% → just below 75% threshold
- Decision: do NOT add Organism D yet; complete calibration of A↔B and A↔C first (especially the structural divergence axes)

**G4 — staleness:** C calibrated last week; A and B within 90 days. No action needed.

**Output written to:**
- `memory/insights.json`: structural finding on relationship_downgrade
- `staging/`: draft thread: "On [relationship downgrade], 2 of 3 organisms choose quiet withdrawal. Here's why the explicit minority exists."

**Verdict: EXTRACT_COLLECTIVE_INTELLIGENCE — structural pattern confirmed.**

---

## Decision Label

**EXTRACT_COLLECTIVE_INTELLIGENCE**

Apply when: ≥2 organisms, ≥1 all-pairs collision complete, ≥1 structural divergence axis confirmed.

Do not apply when: organism pool < 2, any organism stale > 90 days, collision coverage < 80%.

---

## Files

| File | Purpose |
|------|---------|
| `organism_interact.py` | Collision engine (any two DNA files) |
| `templates/organism_template.md` | Scaffold for new organisms |
| `templates/samuel_dna.md` | Organism B reference implementation |
| `templates/dna_core.md` | Organism A (self) |
| `memory/insights.json` | Collective intelligence accumulation |
| `results/` | Collision reports, divergence logs |
| `docs/knowledge_product_44_organism_collision_sop.md` | Single-pair collision (prerequisite) |
| `docs/knowledge_product_45_organism_recruitment_sop.md` | Organism recruitment protocol |

---

## Integration with Other SOPs

| SOP | Relationship |
|-----|-------------|
| SOP #44 (Organism Collision) | Prerequisite: single-pair collision must pass before network analysis |
| SOP #45 (Organism Recruitment) | Feeds G3: use recruitment SOP to select and onboard Organism C+ |
| SOP #80 (Cold Start Calibration) | Self-organism quality gate; self must be calibrated before network runs |
| SOP #91 (Monthly DNA Calibration) | Maintenance cadence integration: run network collision after each monthly audit |

---

*SOP #95 | Domain: Branch 4 社交圈 | Backing MDs: MD-327, MD-328, MD-330, MD-202, MD-120, MD-319, MD-55*
*2026-04-09T00:00Z*
