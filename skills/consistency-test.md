# Consistency Test — Cross-Instance Verification

Measure whether a DNA produces the same decisions across separate sessions. If the twin gives different answers each time, it is not a twin — it is noise.

## Trigger

Use when: validating DNA quality, after DNA updates, when testing cross-session stability, or before trusting a digital organism for autonomous decisions.

## Process

1. **Run deterministic baseline** — use `consistency_test.py` to establish keyword-match consistency floor
2. **Design test scenarios** — 10+ scenarios covering different life domains (career, finance, relationships, daily decisions)
3. **Run LLM multi-session test** — present identical scenarios across N separate sessions (minimum 3), each with fresh context load
4. **Score agreement** — compare decisions (not exact wording) across sessions
5. **Identify inconsistencies** — trace disagreements back to ambiguous or missing DNA sections
6. **Fix DNA** — tighten language where inconsistency was found, then re-test

## Deterministic Baseline

`consistency_test.py` provides a keyword-matching consistency check. This is the floor, not the ceiling. It catches obvious failures (completely different answers) but misses nuanced inconsistency. LLM-based testing is required for real validation.

## LLM Multi-Session Test Protocol

```
For each scenario S in test_set:
  For each session i in 1..N:
    1. Cold start — fresh context, load DNA only
    2. Present scenario S
    3. Record: decision, reasoning, DNA principles cited
  Compare across sessions:
    - Decision match? (yes/no)
    - Reasoning overlap? (high/medium/low)
    - Same DNA principles invoked? (yes/partial/no)
```

## Scoring Criteria

| Score | Meaning |
|-------|---------|
| >80% decision agreement | Target. DNA is working. |
| 60-80% agreement | DNA has ambiguous sections. Identify and tighten. |
| <60% agreement | DNA is insufficient. Major gaps in procedural coverage. |

Agreement means same decision outcome, not identical phrasing. Two sessions can word things differently but reach the same conclusion — that counts as agreement.

## Rules

- Test on cold starts only. Warm context inflates consistency artificially.
- Minimum 3 sessions per scenario. More is better.
- Scenarios must span multiple life domains — not just the easy ones.
- When consistency drops after a DNA edit, the edit introduced ambiguity. Revert or clarify.
- The 80% target is a floor, not a ceiling. Push toward 95%+ for critical decisions.
