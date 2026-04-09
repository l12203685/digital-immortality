# SOP #74: Boot Test Evolution Protocol

> Boot tests are behavioral TDD. As the DNA grows, boot tests must evolve or they become stale coverage.
> This SOP governs when and how to add, modify, or retire boot test cases.

---

## Problem

DNA currently has 330 MDs. The boot test suite has 14 cases. Gap = 316 MDs with zero behavioral coverage on cold start. If a critical MD is not in `boot_tests.md`, cold-start alignment failure is silent — the system passes 14/14 but behaves wrong on the 15th case.

**Failure mode**: boot tests become a fixed snapshot while DNA evolves. The system self-reports healthy but cold-start diverges on new domains.

---

## Three-Layer Structure

| Layer | Purpose | Cadence |
|-------|---------|---------|
| L1 Execute | Run boot tests on cold start | Every session |
| L2 Evaluate | Audit coverage gaps vs DNA | Monthly or after 30 new MDs |
| L3 Evolve | Add/retire test cases | When gap found or correction received |

---

## G0: Coverage Audit

**Trigger**: any of these conditions
- ≥30 new MDs added since last audit
- New domain added to `organism_interact.py` (`_domain_decision` handler)
- Cold-start correction received (real person said "wrong answer")

**Procedure**:
1. List all domains in `templates/dna_core.md` (§ headers)
2. List all test cases in `templates/boot_tests.md`
3. Flag domains with zero test coverage
4. Score: `coverage_rate = test_domains / dna_domains`

**Kill condition**: coverage_rate < 50% → CRITICAL → add tests before next session

---

## G1: New Test Case Design

**When**: G0 flags uncovered domain OR correction received

**Format for new test case**:
```
Scenario: [one-sentence situation]
Domain: [trading / career / negotiation / social / general]
Expected decision: [ACTION_LABEL from organism_interact decision labels]
DNA anchor: MD-XXX ([principle text])
Behavioral marker: [what does RIGHT behavior look like? one sentence]
Failure mode: [what does WRONG behavior look like? one sentence]
```

**Quality gate**: new case must be
- [ ] Anchored to a specific MD (not abstract)
- [ ] Have a deterministic expected answer (not "depends")
- [ ] Test behavior not knowledge (action, not recitation)
- [ ] Distinguishable from existing cases (no duplicates)

---

## G2: Retirement Criteria

Retire a test case when:
- The underlying MD was superseded by a newer MD that overrides it
- The scenario is no longer realistic (domain obsolete)
- Case duplicates another with higher signal quality

**Never retire based on**: failure rate alone. Failing cases reveal real gaps — fix the DNA, not the test.

---

## G3: Priority Domains for Next Test Cases

Based on MD density vs test coverage (as of cycle 239, 330 MDs, 14 tests):

| Domain | MD count | Tests | Gap |
|--------|----------|-------|-----|
| Trading | ~80 MDs | 2 | HIGH |
| Career/negotiation | ~60 MDs | 2 | HIGH |
| Portfolio/sizing | ~40 MDs | 1 | HIGH |
| Poker/game theory | ~30 MDs | 0 | CRITICAL |
| Social/relationship | ~20 MDs | 2 | MEDIUM |
| Investment/FIRE | ~30 MDs | 2 | MEDIUM |
| Communication | ~10 MDs | 2 | LOW |
| Meta-strategy | ~15 MDs | 3 | LOW |

**Next 3 test cases to add** (highest gap × highest behavioral importance):
1. **Poker domain** — MD-295 (GTO defense rate = 1-α formula): given bluff-catch scenario, derive the correct call frequency, not the "safe" fold
2. **Portfolio sizing** — MD-28 (lots formula = equity×1%/ATR×mult): given capital + ATR, compute correct position size, not intuitive guess
3. **Career negotiation** — MD-1 (calculate floor first, written): given offer scenario, first move = calculate written floor, not negotiate from gut

---

## G4: Integration with Cold-Start Protocol

Boot test evolution connects to:
- **dna_core.md**: new test case → corresponding MD must be in dna_core (cold-start template)
- **boot_tests.md**: test case added here → run consistency_test.py to verify it passes
- **consistency_baseline.json**: update after any test case change
- **session_state.md**: note coverage_rate + last audit date

**Verification sequence** after adding new test:
```bash
python consistency_test.py templates/example_dna.md --output-dir results
# Must pass: X/X ALIGNED (0 MISALIGNED)
```

---

## G5: Emergency (Coverage < 30%)

If coverage_rate < 30% (critical coverage collapse):
1. STOP all other branches
2. Audit which domains have zero coverage
3. Write 3 test cases for the highest-gap domains
4. Run consistency_test.py → must pass before resuming
5. Log in `results/boot_test_audit_log.jsonl`

Coverage collapse can happen when: DNA doubles (micro-decision learning) but test suite is not maintained. Current state (330 MDs / 14 tests) is approaching this threshold.

---

## Self-Test

Given this scenario: *A cold-starting agent reads boot_tests.md, passes all 14 tests, then gives the wrong answer to a trading scenario anchored in MD-175 (MAE/MFE distribution).*

**What went wrong?**
→ MD-175 has no test case. Coverage gap. G0 should have caught it.

**Correct action?**
→ Write test case for MD-175 domain. Run G4 verification. Add to boot_tests.md.

---

## DNA Anchors

- MD-89 (L1/L2/L3 three-layer loop for automated systems)
- MD-12 (every correction = new boot test case)
- MD-319 (output = gap detector)
- MD-321 (SOP → teachable document = refinement)
- MD-330 (verify by behavior pattern, not recitation)

---

*SOP #74 | Cycle 239 | 2026-04-09T UTC*
