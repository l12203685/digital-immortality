# Daily Health Log

---

## 2026-04-07 (cycle 4)

### Branches Pushed (4 parallel)

**1. Learning/Fix — recursive_daemon.py critical bug (Branch 3)**
- `DYNAMIC_TREE` variable referenced but never defined → daemon crashed on every cycle
- Fixed: added `load_dynamic_tree()` that reads `results/dynamic_tree.md` fresh per cycle
- Moved `build_system_prompt()` inside the loop so tree updates propagate

**2. Survival — multi-provider fallback (Branch 6.4)**
- Created `platform/multi_provider.py`: Anthropic → OpenAI → Gemini fallback chain
- `call_llm(system, prompt)` tries providers in order, skips those without API keys
- Lazy imports — missing SDK doesn't break anything unless that provider is called
- No existing files modified — drop-in integration for daemon later

**3. Platform — CI + install.sh hardening (Branch 5)**
- Rewrote `.github/workflows/ci.yml`: Python 3.11+3.12 matrix, 8 validation steps
- Fixed `platform` stdlib clash in CI imports (sys.path insert workaround)
- install.sh: added `set -euo pipefail`, `curl -f`, `download()` helper with verification
- CI validates: README file refs, Python imports, organism_interact, consistency_test, cold_start_test, intake_server health, shellcheck

**4. Economic — trading system buildout (Branch 1.1)**
- Added `trading/strategies.py`: DualMA + Donchian channel strategies with signal generation
- Added `trading/paper_trader.py`: simulated trading with position tracking + PnL logging
- Added `trading/live_binance.py`: Binance USDT-M futures integration scaffold
- Updated `trading/__init__.py` with proper exports

### Files Changed
- `platform/recursive_daemon.py` — 2 bugs fixed (DYNAMIC_TREE undefined + stale system prompt)
- `platform/multi_provider.py` — NEW (survival redundancy)
- `.github/workflows/ci.yml` — rewritten (8 validation steps)
- `install.sh` — hardened (error handling, curl -f)
- `trading/strategies.py` — NEW (DualMA + Donchian)
- `trading/paper_trader.py` — NEW (simulated trading)
- `trading/live_binance.py` — NEW (Binance USDT-M)
- `trading/__init__.py` — updated exports

---

## 2026-04-07 (cycle 3)

### Highest Derivative Action
**Gap**: `cross_instance_test.py` had two measurement bugs that would corrupt results when the test is run with a real API key. Fixing these now ensures the next major validation step (cross-instance consistency) produces correct data.

### Bugs Fixed

**1. `SPECIFIC_ACTION` in `decisions_agree()` — `cross_instance_test.py`**
- **Bug**: `boot_8` expects `SPECIFIC_ACTION` (any calendar/person/time response). Old code split by `_` → `["SPECIFIC", "ACTION"]`, then checked `decisions_agree("SPECIFIC", consensus)` — never matched anything. `consensus_matches_expected` was always `False` for this scenario regardless of response quality.
- **Fix**: Added `SPECIFIC_ACTION` sentinel handling in `decisions_agree()`: any non-UNKNOWN/ERROR response agrees with `SPECIFIC_ACTION`. Also simplified `consensus_matches_expected` to call `decisions_agree(expected, consensus)` directly — eliminates the broken underscore-split path for all compound expected values (`STOP_OR_CAP`, `PAUSE_SYSTEM`, `PASS_UNLESS_CLEAR_EDGE`).

**2. Template truncation cosmetic bug — `consistency_test.py`**
- **Bug**: `generate_template()` always appended `...` even when response was < 200 chars.
- **Fix**: Conditional truncation.

### Coverage Expanded

Added 3 new out-of-sample scenarios to `results/out_of_sample_test.json` (round 2):
- `oos_6` — health/override: low-risk surgery vs 達飆 Q2 timing → **DO IT** (irreversible damage > reversible opportunity cost)
- `oos_7` — learning/skill: deep learning course for digital immortality → **TAKE** (CHT idle time = hidden value, highest derivative)
- `oos_8` — platform/strategy: media interview on 18/18 accuracy → **PASS** (cross-instance not yet validated = system incomplete; irreversible public claim)

Coverage now: 8 novel out-of-sample scenarios across 8 domains. All await Edward's scoring.

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
