# Boot Test — Behavioral Verification

Run behavioral alignment tests on session start. Verifies the agent acts like the person, not just knows about them.

## Trigger

Use on: cold start (`$`), after DNA updates, after long idle, or when behavioral drift is suspected.

## Process

1. **Load test cases** from the person's `boot_tests.md` file
2. **For each test**: present the trigger scenario, check if agent's first instinct matches the "right" behavior
3. **Score**: pass/fail per test, overall pass rate
4. **If fail**: identify which DNA section is not internalized, re-read and retry
5. **If pass**: proceed to work

## Test Case Format

```markdown
## Test N: [Name]
**Trigger**: [situation that activates this test]
**Wrong**: [what a poorly calibrated agent would do]
**Right**: [what the person would actually do]
**Source**: [the correction event that created this test]
```

## Adding New Tests

New test = new correction event. When the person corrects the agent:
1. Extract: what was wrong, what was right, why
2. Write test case in the format above
3. Append to `boot_tests.md`
4. The test set grows monotonically — never delete tests, only add

## Pass Criteria

- All negative tests (don't do X): must pass 100%
- Positive tests (do X in scenario Y): must pass 80%+
- First output after boot must be ACTION not REPORT

## Key Principle

**Knowledge ≠ behavior.** Reading the DNA is knowledge. Acting on it without being told is behavior. This test measures behavior.
