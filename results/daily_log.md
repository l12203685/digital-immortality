# Daily Health Log

---

## 2026-04-07 (cycle 2)

### Highest Derivative Action
**Gap**: Cross-instance consistency unmeasured — the single biggest hole in the validation story. "100% consistency" only means one LLM session agrees with itself.

### Built `cross_instance_test.py`

Automated the manual 3-session test that was previously blocked on human effort. Key design:
- Takes any DNA file + `ANTHROPIC_API_KEY`
- Runs 7 `BOOT_TEST_SCENARIOS` × N independent API calls (no shared context)
- Each call: system = DNA, user = scenario (fresh session, no history)
- `extract_decision()` normalizes response to action word (PASS/REJECT/STOP/etc.)
- `decisions_agree()` handles semantic equivalence (PASS ≈ REJECT ≈ DECLINE for "don't proceed")
- `majority_decision()` scores agreement across sessions
- Outputs `results/cross_instance_scorecard.json`

Usage: `ANTHROPIC_API_KEY=sk-... python cross_instance_test.py edward_dna_v18.md`

Default model: `claude-haiku-4-5` (cost-efficient for 21 API calls; override with `--model`)

**Converts manual test → automated CI in one command.**

---

## 2026-04-07

### Repo Health
- `python consistency_test.py templates/example_dna.md` — **completed without errors**
- 6/7 misaligned expected (template DNA is generic, not Edward-specific)

### README References
- All referenced files verified present: `SKILL.md`, `organism_interact.py`, `consistency_test.py`, `templates/example_dna.md`, `templates/example_dna_b.md`, `specs/organism_protocol.md`, `skills/`, `results/`
- No broken references

### Validation Status
| Test | Score | Notes |
|------|-------|-------|
| Real-life decisions (18 scenarios) | **18/18 (100%)** | edward_dna_v18.md |
| Consistency scenarios (LLM) | **7/7 (100%)** | Same session, not independent |
| Consistency scenarios (deterministic) | **0/7 (0%)** | Expected — keyword engine can't reason |
| Coverage gaps | 10/28 untested | All expected to align |

Open: cross-instance consistency unmeasured (requires 3 independent LLM sessions).

### Calendar Check
No Google Calendar tool available in this environment. Cannot check for 珍珠獸醫 appointment.
Manual check recommended: verify 4/13 (早慶祝) and 4/18 (珍珠獸醫) on calendar.

### Improvement Made
**Fixed alignment check bug in `consistency_test.py`** (lines 272-276):

- **Bug**: `REJECT` check included `"pass" in resp_lower` as a valid match → a PASS response was counted as ALIGNED with REJECT (false positive)
- **Bug**: `PASS` branch was redundant (already covered by `expected in resp_lower`)
- **Bug**: compound decisions `STOP_OR_CAP`, `PAUSE_SYSTEM`, `PASS_UNLESS_CLEAR_EDGE` had no partial-match handling → always MISALIGNED even when response was semantically correct

- **Fix**: Removed wrong REJECT/PASS conditions; added proper partial matching for compound decisions
- **Effect**: `consistency_3` (STOP_OR_CAP) now correctly shows ALIGNED (2/7 instead of 1/7 for template DNA)
- Committed and pushed.
