# Cold Start Recovery Runbook

> Created 2026-04-09 UTC (cycle 202). Branch 6 存活冗餘.
> Use this when: cold boot fails, session_state is stale/missing, or daemon dies.

## Boot Sequence (canonical, from CLAUDE.md + SKILL.md)

```
1. SKILL.md               → rules (three-layer loop, branches, learn=write)
2. results/dynamic_tree.md → current state of ALL branches
3. results/daemon_log.md   → tail 20 — what happened recently (DON'T repeat)
4. staging/session_state.md → queue + blockers
5. Act — don't ask, don't report. First output = action.
```

**Cold-start kernel** (read dna_core.md only — 330 MDs):
```
templates/dna_core.md → boot_tests.md → session_state.md → queue
```

## Failure Modes + Recovery

### F1: session_state.md missing
**Symptoms**: FileNotFoundError or empty queue on boot.
**Recovery**:
1. Read `results/daemon_log.md` tail 60 to reconstruct state.
2. Identify last completed cycle number and branch statuses.
3. Write new `staging/session_state.md` from reconstructed state.
4. Set cycle = last_cycle + 1.

### F2: session_state.md stale (>24h gap)
**Symptoms**: Staleness alert in daemon_log, or last_cycle timestamp is old.
**Recovery**:
1. Read `results/daemon_log.md` tail 60.
2. Read `results/dynamic_tree.md` tail (branch statuses).
3. Rewrite session_state.md from current state.
4. Continue from highest-derivative branch.

### F3: dynamic_tree.md corrupted or truncated
**Symptoms**: Missing branches, garbled markdown, incomplete status.
**Recovery**:
1. Read `results/daemon_log.md` tail 100 — branches mentioned there.
2. Read `results/consistency_baseline.json` — validation baseline.
3. Reconstruct branch 6 (存活) status from cold_start_test.py output.
4. Rewrite tree section by section, verify against daemon_log.

### F4: paper-live / trading runner import fails
**Symptoms**: `ModuleNotFoundError: No module named 'trading'`
**Fix**: Runners must be invoked from project root:
```bash
cd C:/Users/admin/workspace/digital-immortality
python trading/mainnet_runner.py --paper-live
```
Root cause: `from trading.X import ...` requires project root in sys.path.
Both mainnet_runner.py and testnet_runner.py now include the path fix (cycle 202).

### F5: boot_tests.md missing
**Symptoms**: boot test script fails on file read.
**Recovery**:
1. `templates/example_boot_tests.md` is the canonical template — copy structure.
2. Recreate test cases from last known boot_tests entry in daemon_log.
3. Minimum viable: 14 tests (last known count as of cycle 201).

### F6: dna_core.md too long to cold-read (>500 lines)
**Symptoms**: Context budget exhausted on boot, or agent reads it but can't act.
**Rule**: templates/dna_core.md is the TEMPLATE with 330 MDs (full list).
The personal dna_core.md target is <100 lines (operational kernel only).
**Recovery**:
1. Read templates/dna_core.md §BOOT_CRITICAL (first 10 lines) only.
2. Read templates/dna_core.md §Core Principles + §Decision Engine.
3. Skip all MD-NNN entries until acting, then query specific MDs as needed.

### F7: Daemon dies mid-cycle (no daemon_log entry)
**Symptoms**: Last daemon_log entry is >2 cycles ago, git log shows no recent commit.
**Recovery**:
1. Run `python cold_start_test.py` to verify boot sequence is intact.
2. Run `python trading/mainnet_runner.py --paper-live` for Branch 1.1 tick.
3. Run `python consistency_test.py templates/dna_core.md` to verify 33/33.
4. Write new session_state.md with current state.
5. Append to daemon_log.md, commit, push.

## Minimum Viable Cold-Start Verification

Run these three commands; if all pass, cold-start is healthy:

```bash
cd C:/Users/admin/workspace/digital-immortality

# 1. Boot sequence files + deterministic engine
python cold_start_test.py
# Expected: PASS 5/5, boot time <1s

# 2. Paper-live tick (Branch 1.1)
python trading/mainnet_runner.py --paper-live
# Expected: 15 strategy signals logged, no errors

# 3. Behavioral consistency (Branch 2.3)
python consistency_test.py templates/dna_core.md
# Expected: 33/33 ALIGNED
```

## Branch 6 Health Indicators

| Indicator | Healthy State | Check Command |
|-----------|--------------|---------------|
| Cold-start files | All exist | `python cold_start_test.py` |
| session_state.md | <24h old | Check timestamp in file |
| Behavioral alignment | 33/33 ALIGNED | `python consistency_test.py templates/dna_core.md` |
| Paper-live runner | No import errors | `python trading/mainnet_runner.py --paper-live` |
| Multi-provider | Fallback chain exists | `python platform/multi_provider.py` |
| Daemon log | Entry within last 2 cycles | tail -5 results/daemon_log.md |

## Scope Separation (6.5 — L1/L2/L3 layer boundaries)

Three-layer recursive engine touches different files per layer:

| Layer | Script | Files Written |
|-------|--------|--------------|
| L1 Execute | `trading/mainnet_runner.py` | `results/paper_live_log.jsonl`, `results/mainnet_log.jsonl` |
| L1 Execute | `recursive_engine.py` | `staging/last_output.md`, `staging/next_input.md` |
| L2 Evaluate | daemon cycle (this script) | `results/daemon_log.md`, `results/dynamic_tree.md` |
| L3 Evolve | E0 session (human-in-loop) | `templates/dna_core.md`, `results/consistency_baseline.json` |

No two layers write the same file. Conflict = layer boundary violation.

### F8: All branches at similar derivative — no clear priority signal
**Symptoms**: `daemon_next_priority.txt` reports "All branches covered" or priority is ambiguous; agent idles or asks user instead of acting.
**Recovery**:
1. Default to least-recently-touched branch (daemon_next_priority.txt reports this).
2. Run Branch 1.1 paper-live tick if not done this session — always valid.
3. Run SOP series next (Branch 7) — always has a next SOP to write.
4. If both done: Branch 6 health audit — run cold_start_test.py, verify all health indicators green.
5. If all healthy: write new content (runbook extension, new F-mode, health indicator, or anti-pattern).
**Root cause**: Regime equilibrium. Normal state. Not a bug. Respond with action, not paralysis.

## Recovery Priority Order

1. session_state.md (F1/F2) — without this, cold-start queue is blind
2. Paper-live runner (F4) — Branch 1.1 is highest derivative (DEADLINE 2026-07-07)
3. dynamic_tree.md (F3) — without this, branch navigation is blind
4. boot_tests.md (F5) — behavioral TDD; can reconstruct from daemon_log
5. dna_core.md (F6) — template exists; personal file recoverable from templates/

### F9: Content pipeline stalled — zero posts despite queue existing
**Symptoms**: `docs/posting_queue.md` has ≥3 rows with status=pending AND date is past due; `platform/daily_posting_helper.py --status` shows overdue posts.
**Root cause**: Branch 1.3 revenue path is: post → audience → DMs → Gumroad → revenue. Zero posts = zero audience = zero revenue = survival condition violated.
**Recovery**:
1. Open `docs/posting_queue.md` — find oldest overdue post.
2. Open its thread file (`docs/publish_thread_sop*.md`).
3. Copy thread, paste to X, post. No editing, no perfecting — ship as-is.
4. Run `python platform/daily_posting_helper.py --confirm` to log it.
5. Repeat for next 2 overdue posts (max 3 in one session to avoid spam).
6. Check if ≥10 DMs received → activate Gumroad (see `docs/gumroad_listing_draft.md`).

**Connection to 存活**: SOP #60 G5 emergency protocol. Content shipping = economic self-sufficiency pathway. Stalled pipeline = dead branch 1.3 = survival condition at risk.

### F10: External feedback loop closed — 0 external signals received (backward check gap)
**Symptoms**: SOP #64 G0 status = `PRE_LAUNCH`; `results/external_signal_log.jsonl` missing or empty; posts_published == 0.
**Root cause**: Internal recursion is running but external validation loop is broken. DNA axiom violated: 遞迴 - persist = 自言自語 (recursion without external signal = self-talk, not evolution).
**Recovery**:
1. Check if mainnet is live: `cat staging/session_state.md | grep mainnet`.
2. If mainnet NOT live → this failure is human-gated (Edward must set BINANCE_MAINNET_KEY/SECRET first).
3. If mainnet live AND posts == 0: **Core Principle #5 violated** (Direct action on concrete commitments).
   - Post SOP #01 immediately. No editing. Ship.
   - Log to `memory/dna_violation_log.md` (create if missing): date, violated principle, cause.
4. Once first post live: create `results/external_signal_log.jsonl` and log first entry.
5. Each subsequent cycle: check DM count. ≥1 DM → log it. Any correction/disagreement → calibrate DNA.

**Connection to SOP #64**: G0 (audit state), G2 (minimum post budget), G5 (emergency protocol).
**Connection to SOP #63**: G1 mainnet gate precedes this; G2 launch day batch triggers external loop open.

## Layer-Specific Restart Protocols (from SOP #47 — cycle 208)

Stale loop vs dead engine look identical from outside. Use these signals:

| Layer | Stale Signal | Dead Signal | Restart |
|-------|-------------|-------------|---------|
| L1 Execute | staging/last_output.md unchanged 3+ cycles | missing file | Re-run recursive_engine.py --prompt |
| L2 Evaluate | daemon_log.md no new entry 3+ cycles | daemon process not running | Restart recursive_daemon.py; check daemon_log |
| L3 Evolve | dna_core.md unchanged 10+ cycles | no correction log entries | Run /dna-calibrate; look for missed corrections |

**L3 Evolution Trigger** — run L3 when ALL three are true:
1. ≥3 consecutive cycles produced no new insight (daemon_log shows "no new patterns")
2. A correction was made in the last 5 cycles that isn't yet in dna_core.md or boot_tests.md
3. The correction applies to >1 domain (cross-domain = high distillation value)

**Staleness alarm → restart sequence**:
```bash
# 1. Check last_output.md timestamp
head -2 staging/last_output.md

# 2. Check daemon_log.md last entry
tail -5 results/daemon_log.md

# 3. Force a new prompt cycle
python recursive_engine.py --prompt

# 4. If still stale after 1h: rebuild next_input.md from session_state.md
cat staging/session_state.md | head -20
```

## Related Files

- `cold_start_test.py` — automated boot sequence verification
- `staging/session_state.md` — inter-session relay (update each cycle)
- `results/daemon_log.md` — audit trail for reconstruction
- `templates/dna_core.md` — 330 MD cold-start template
- `platform/multi_provider.py` — Anthropic→OpenAI→Gemini fallback
