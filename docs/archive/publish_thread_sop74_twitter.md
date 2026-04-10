# Twitter Thread: SOP #74 — Boot Test Evolution Protocol

**Post date**: Queue position #74 (Aug 30)

---

**Tweet 1 (hook)**
Your AI twin passes all boot tests.

Then gives the wrong answer on the 76th case.

Because you never wrote a test for that domain.

Boot tests are behavioral TDD. They rot if you don't evolve them.

SOP #74: Boot Test Evolution Protocol 🧵

---

**Tweet 2**
The problem isn't the test failing.

The problem is the test NOT EXISTING.

330 MDs in DNA. 14 boot test cases.

Gap = 316 MDs with zero behavioral coverage.

Cold-start alignment failure is silent when the test doesn't exist.

---

**Tweet 3**
Three-layer structure:

L1 Execute — run tests every cold start
L2 Evaluate — audit coverage gaps vs DNA monthly
L3 Evolve — add/retire cases when gap found

Execute without Evaluate+Evolve = dead loop.

Same structure as belief update: expose → review → extract → write.

---

**Tweet 4**
G0: Coverage Audit

Trigger: ≥30 new MDs added OR new domain added OR correction received from real person

Score: coverage_rate = test_domains / dna_domains

Kill condition: coverage_rate < 50% → CRITICAL → add tests before next session

---

**Tweet 5**
G1: New Test Case Design

Every new case must be:
- Anchored to a specific MD (not abstract)
- Have a deterministic expected answer
- Test BEHAVIOR not knowledge
- Distinguishable from existing cases

"What would you do?" > "What does MD-28 say?"

---

**Tweet 6**
G2: Retirement Criteria

Retire a case when:
- Underlying MD was superseded
- Scenario is no longer realistic
- Case duplicates another with higher signal quality

NEVER retire based on failure rate alone.

Failing cases reveal real gaps. Fix the DNA, not the test.

---

**Tweet 7**
Priority gaps right now (330 MDs / 14 tests):

Poker/game theory: ~30 MDs, 0 tests ← CRITICAL
Trading: ~80 MDs, 2 tests ← HIGH
Portfolio sizing: ~40 MDs, 1 test ← HIGH
Career negotiation: ~60 MDs, 2 tests ← HIGH

You don't know what you don't know. The test suite gap IS the blind spot.

---

**Tweet 8**
Next 3 test cases to add:

1. Poker: MD-295 (GTO defense rate = 1-α formula)
2. Sizing: MD-28 (lots = equity×1%/ATR×mult)
3. Career: MD-1 (calculate floor first, written)

These domains have the highest MD density × lowest test coverage.

---

**Tweet 9**
G4: Integration with cold-start protocol

After adding any test case:
→ verify corresponding MD is in dna_core.md
→ run consistency_test.py → must pass 0 MISALIGNED
→ update consistency_baseline.json
→ log coverage_rate + audit date in session_state.md

Test case without verification = theater.

---

**Tweet 10**
G5: Emergency (coverage < 30%)

Stop all other branches.
Write 3 test cases for highest-gap domains.
Run consistency_test → pass before resuming.

Coverage collapse happens when DNA doubles but test suite stagnates.

Current state (330 MDs / 14 tests) is approaching this threshold.

---

**Tweet 11**
Self-test:

Agent passes all 14 tests. Gives wrong answer on MD-175 (MAE/MFE distribution).

What went wrong?
→ MD-175 has no test case. G0 missed it.

Correct action?
→ Write the test. Run G4 verification. Add to boot_tests.md.

The system can tell you when it's failing. It can't tell you what's missing.

---

**Tweet 12 (close)**
Boot tests are behavioral TDD.

DNA grows. Tests must grow with it.

The gap between "passes boot test" and "behaves correctly" is exactly the untested surface.

Map it. Close it. Repeat.

SOP #01–#74 complete.

---

*Thread | SOP #74 | Cycle 239 | 2026-04-09T UTC*
