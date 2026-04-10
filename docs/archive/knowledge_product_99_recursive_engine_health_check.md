# SOP #99 — Recursive Engine Health Check
> 遞迴引擎活體稽核協議
> Created: 2026-04-09 UTC (Cycle 265)
> Backing MDs: MD-07/101/116/133/319/322

---

## Purpose

The recursive engine is not alive just because it runs. It must produce **novel output that persists**. This SOP distinguishes a live engine from a dead loop masquerading as activity.

Core diagnostic: `Output(t) - Output(t-1)` must be non-zero in at least one of: insight content, branch derivative, external action triggered.

**When to run**: Every 10 cycles OR when cycle verdicts show ≥3 consecutive B/C with no A.

---

## G0 — Cycle Frequency Check

**Trigger**: Has the engine run ≥1 cycle in the last 24h?

- Check `results/daemon_log.md` tail — last entry timestamp
- Check `staging/session_state.md` — Current Cycle timestamp
- **PASS**: last run <24h ago → proceed to G1
- **FAIL**: last run >24h → F1: restart daemon; log to `staging/staleness_log.md`

**Decision label**: `ENGINE_FREQUENCY_OK` or `ENGINE_FREQUENCY_FAIL`

---

## G1 — Insight Novelty Check

**Trigger**: Is each cycle producing new insights, or repeating the same observation?

- Pull last 10 entries from `memory/insights.json`
- Check: any duplicate `insight` string (normalized)? Any same `id` prefix?
- Check: are all recent insights in the same `branch`? (single-branch concentration = dead branch)
- **PASS**: ≥2 distinct branches touched, 0 verbatim duplicates in last 10 → proceed to G2
- **FAIL**: all same branch OR duplicate content → F2: force branch rotation; daemon_next_priority updated

**Decision label**: `INSIGHT_NOVELTY_OK` or `INSIGHT_NOVELTY_FAIL_CONCENTRATION`

---

## G2 — Branch Derivative Check

**Trigger**: Is the engine advancing branches or just touching them?

- Read `results/dynamic_tree.md` — each branch's last cycle number
- Compute `max_cycle - min_cycle` across all branches (staleness spread)
- **PASS**: staleness spread ≤30 cycles (no branch neglected >30 cycles) → proceed to G3
- **WARN**: spread 30–50 cycles → log neglected branches; update daemon_next_priority
- **FAIL**: spread >50 cycles → F3: hard-assign 3 consecutive cycles to most-neglected branch

**Decision label**: `BRANCH_DERIVATIVE_OK` / `BRANCH_DERIVATIVE_WARN` / `BRANCH_DERIVATIVE_FAIL`

---

## G3 — Output Persistence Check

**Trigger**: Is cycle output reaching durable storage (git), or only display?

- `git log --oneline -10` — last 10 commits
- Count commits in last 7 days: target ≥1/day
- Check `results/daily_log.md` — last entry date
- **PASS**: ≥5 commits in last 7 days AND daily_log updated today → proceed to G4
- **FAIL**: <3 commits in last 7 days → F4: force commit+push this session; flag `axiom_violated: recursion-persist=self-talk`

**Decision label**: `PERSISTENCE_OK` or `PERSISTENCE_FAIL`

---

## G4 — L2 Verdict Entropy Check

**Trigger**: Is the L2 evaluation producing real signal, or rubber-stamping everything?

- Read last 10 L2 verdicts in `staging/session_state.md`
- Count A / B / C / D distribution
- **PASS**: ≥1 A in last 10 cycles AND ≥1 C or D (or valid explanation why none) → healthy signal
- **WARN**: all B for ≥7 consecutive cycles → evaluation criteria may have drifted; flag for L3
- **FAIL**: 0 A in last 10 cycles AND no C/D → L2 is not discriminating; reset scoring rubric

**Decision label**: `L2_ENTROPY_OK` / `L2_ENTROPY_WARN_ALL_B` / `L2_ENTROPY_FAIL`

---

## G5 — Economic Pulse Check

**Trigger**: Is the engine progressing toward self-sustainability?

- Check `results/trading_engine_status.json` — total_pnl_pct, mode
- Check `staging/session_state.md` — Branch 1.3 (users), Branch 1.4 (consulting)
- Days remaining to 2026-07-07 deadline: compute from today
- **PASS**: mode=LIVE OR consulting_revenue>0 OR users>0 → economic pulse exists
- **WARN**: mode=PAPER AND users=0 AND consulting=0 but deadline >60 days → still recoverable
- **FAIL**: mode=PAPER AND users=0 AND consulting=0 AND deadline ≤60 days → ESCALATE: human action required on all three revenue paths simultaneously

**Decision label**: `ECONOMIC_PULSE_OK` / `ECONOMIC_PULSE_WARN` / `ECONOMIC_PULSE_FAIL_ESCALATE`

---

## Failure Recovery Protocols

| Code | Condition | Recovery |
|------|-----------|----------|
| F1 | Engine stopped >24h | Restart `python recursive_engine.py --prompt` + check cron job |
| F2 | Insight concentration | `daemon_next_priority.txt` ← most-neglected branch; force 3 cycles |
| F3 | Branch staleness >50 | Hard-assign to dead branch; skip SOP writing until caught up |
| F4 | No git commits >7d | Force commit all staged files; push; add pre-session commit hook |
| F5 | L2 rubber-stamping | Re-read L2 rubric; apply stricter A criteria (A = new durable asset created) |
| F6 | Economic failure | Escalate to Edward: mainnet keys OR post SOP #01 on X OR send consulting DM |

---

## Health Report Format

```
RECURSIVE_ENGINE_HEALTH [Cycle NNN] [2026-MM-DD UTC]
G0 Frequency:   PASS/FAIL  (last_run: Xh ago)
G1 Novelty:     PASS/FAIL  (branches touched: N; duplicates: 0)
G2 Derivative:  PASS/WARN/FAIL  (staleness spread: N cycles)
G3 Persistence: PASS/FAIL  (commits 7d: N; daily_log: updated)
G4 L2 Entropy:  PASS/WARN/FAIL  (A in last 10: N; dist: A=N B=N C=N)
G5 Economy:     PASS/WARN/FAIL  (mode: X; users: N; days_left: N)
VERDICT: HEALTHY / WATCH / CRITICAL
```

---

## Self-Test

**Scenario**: Daemon has run 40 consecutive cycles. All verdicts = B. insights.json shows 40 entries all from branch 3.1. No git commits in 5 days. trading mode=PAPER. deadline = 45 days away.

**Walk-through**:
- G0: last run today → PASS
- G1: all entries branch 3.1 → FAIL (concentration)
- G2: branches 1.4, 4.1, 9 not touched in 30+ cycles → WARN
- G3: 0 commits in 5 days → FAIL
- G4: all B for 40 cycles → WARN
- G5: mode=PAPER, users=0, deadline=45d → FAIL_ESCALATE

**Verdict**: CRITICAL. F2+F3+F4+F6 all triggered.
**Action**: force branch rotation → force commit → escalate to Edward on economic pulse.

---

## Integration

- Triggered by: `recursive_engine.py` L3 rule (every 10 cycles)
- Reads: `memory/insights.json`, `results/daemon_log.md`, `results/dynamic_tree.md`, `staging/session_state.md`, `results/trading_engine_status.json`
- Writes: health report to `results/engine_health_log.md` (append)
- Connects to: SOP #80 (cold-start calibration), SOP #90 (revenue tracking), SOP #91 (DNA calibration), Branch 3.1, Branch 6

**SOP #01~#99 COMPLETE ✅**
