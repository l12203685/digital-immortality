# SOP #124 — Kill-Window State Persistence Protocol

**Domain**: Branch 1.1 (Trading System — Strategy State Durability)
**Created**: 2026-04-11T UTC (cycle 321 candidate)
**Status**: DRAFT — awaiting Edward ratification
**Backing MDs**: MD-92 (strategy kill conditions); MD-133 (direct-metric decision); distil115 I2 (kill-window recovery asymmetric design); today's audit commit `c29865a` (ReactivationGate fix)

---

## Problem this solves

SOP#118 defines the **gate logic** for reactivating a killed strategy. SOP#124 covers a different failure mode that lives **below** the gate: the strategy's killed-state itself is not durable across process restarts.

**Root behavioral trace** (today's audit):

1. `trading/engine.py` kept `disabled` as an in-memory dict — wiped on every process restart
2. `kill_window` had a floor of 20 with no decay or recovery — once tripped, always tripped
3. Daemon restart cycle repeatedly re-initialized `disabled = {}`, re-ran strategies, re-hit the kill condition, re-killed, re-crashed or re-restarted
4. **DualMA_10_30 was killed 4x in 48h** without ever being given a real cooling window — each "kill" was actually the same kill repeated because the prior kill was forgotten
5. Every kill event poisoned the log with a fresh entry, making it look like the strategy was oscillating when really the state just wasn't persisting

SOP#118 couldn't help because G1 cooling measures elapsed cycles from signal appearance — but if the daemon restarts, the cycle counter also effectively resets from the daemon's perspective. The gate clock and the state clock both drifted.

**Fix deployed** (commit `c29865a`): ReactivationGate class that persists `disabled` dict to `results/trading_engine_status.json` and reloads on startup. SOP#124 codifies the pattern so it doesn't regress.

---

## Core Principle

**All strategy state that feeds a kill/reactivation decision MUST be persisted to durable storage and reloaded on process start.** In-memory state is a cache, never source of truth.

This is a generalization of the Edward Kernel Rule #6 "recursive output must persist to durable storage." Strategy kill state is a form of recursive output — it reflects accumulated evidence — and therefore must survive restarts.

---

## Gate Sequence (G0 → G5)

### G0 — State Durability Audit

For every state variable in the trading engine, classify:

| Variable | Durable? | Reload on start? | Failure if lost |
|---|---|---|---|
| `disabled` dict (killed strategies) | MUST be durable | MUST reload | Killed strategy resurrects, re-kills in restart loop |
| `kill_window` (risk budget) | MUST be durable | MUST reload | Loses prior-cycle safety context |
| `clean_ticks_since_kill` (recovery counter) | MUST be durable | MUST reload | Recovery progress lost on restart |
| `tick_count` (engine clock) | MUST be durable | MUST reload | SOP#118 G3 gate can never be satisfied |
| `last_pf`, `last_mdd` per strategy | SHOULD be durable | SHOULD reload | Degrades to cold-start estimate |
| `last_signal` per strategy | MAY be in-memory | MAY recompute | Recomputed from bar data on startup |

**Procedure**:
1. Read `trading/engine.py` (and any daemon that mutates strategy state)
2. List every class attribute or dict that influences kill/reactivation decisions
3. For each: verify it is written to durable storage AND reloaded at startup
4. Any variable marked MUST but not durable → **G0 FAIL → fix before deployment**

**PASS**: All MUST variables confirmed durable + reloading → G1

---

### G1 — Restart Idempotence Test

Manually kill and restart the engine process 3 times in a row. After each restart, verify:

1. `disabled` dict matches pre-restart state exactly
2. `kill_window` value matches pre-restart value (not reset to floor)
3. `tick_count` resumed from last-persisted value (or known-safe offset)
4. `clean_ticks_since_kill` counters intact

**Test script**:
```bash
python -m trading.engine --status > /tmp/pre_restart.json
pkill -f "trading.engine" && sleep 2
python -m trading.engine --status > /tmp/post_restart.json
diff /tmp/pre_restart.json /tmp/post_restart.json
# Expected: only monotonic fields (tick_count, timestamp) differ
```

| Diff result | Action |
|---|---|
| Only tick_count / timestamp differ | PASS — state is durable |
| `disabled` dict differs | FAIL — kill state not persisting |
| `kill_window` reset to floor | FAIL — kill-window not persisting |
| `tick_count` reset to 0 | FAIL — engine clock not persisting |

**PASS**: 3 consecutive restart cycles show state preserved → G2

---

### G2 — Kill-Window Recovery Asymmetry

Kill is instant (1 bad tick can kill). Recovery must be slow (N clean ticks before kill_window loosens). This asymmetry prevents noise-driven oscillation.

**Enforce**:

```
kill_trigger:      PF < 0.8 OR MDD ≥ 15%  on any single tick
kill_window_tighten: immediate on kill (kill_window *= 0.5, floor 5)
kill_window_recover: +1 per clean tick, capped at baseline (e.g. 50)
kill_window_floor:  5 (never goes below 5, always some headroom)
```

**Key constraint**: `kill_window_floor` must be > 0. A floor of 0 creates an absorbing state — once tripped, the strategy can never recover because even a single non-clean tick re-crashes the floor.

**PASS**: Recovery logic verified present and asymmetric → G3

---

### G3 — Persistence Write-Path Audit

Every mutation to a MUST-durable variable must be followed by a durable write:

```python
# WRONG
self.disabled[strategy_id] = kill_info
# (no write — lost on restart)

# CORRECT
self.disabled[strategy_id] = kill_info
self._persist_state()  # writes to results/trading_engine_status.json
```

**Procedure**:
1. `grep -n "self.disabled\[" trading/engine.py`
2. For each mutation site, verify `_persist_state()` (or equivalent) is called within the same function
3. No "write-then-forget" mutations allowed

**PASS**: Every MUST-mutation has a matching persist call → G4

---

### G4 — Reload Path Audit

Engine startup must read the durable state and reconstruct in-memory caches before processing any ticks:

```python
def __init__(self):
    self.disabled = {}
    self.kill_window = BASELINE
    self._load_state()  # overwrites defaults with durable values if present
```

**Procedure**:
1. Confirm `_load_state()` (or equivalent) exists and is called in `__init__` or startup
2. Confirm it handles the "no state file yet" case (first run) without crashing
3. Confirm it validates loaded values (not blindly trusting corrupted JSON)

**PASS**: Load path exists, is called on startup, handles missing/corrupt state → G5

---

### G5 — Observability Gate

The engine must expose its persisted state via `--status`:

```json
{
  "disabled": { "DualMA_10_30": { "killed_at": "...", "pf_at_kill": 0.53, ... } },
  "kill_window": 42,
  "kill_window_floor": 5,
  "tick_count": 1247,
  "clean_ticks_since_kill": { "DualMA_10_30": 0 }
}
```

**Rationale**: Without observable state, the only way to diagnose a restart-loop bug is to add print statements. With observable state, `--status` after restart reveals the bug in one command.

**PASS**: All MUST-durable fields exposed in `--status` output → SOP complete

---

## Kill Condition

Do NOT deploy trading engine to live capital if:

1. G0 fails on any MUST variable
2. G1 restart test fails — state does not survive restart
3. `kill_window_floor` ≤ 0 (absorbing state risk)
4. G3 or G4 audit reveals write-then-forget or load-then-ignore paths

**Running with non-durable kill state = guaranteed restart-loop death spiral on first crash.**

---

## Self-Test Scenario

**Scenario**: DualMA_10_30 is running. Current PF = 0.75 (below 0.8 kill threshold). Engine kills it, writes `disabled["DualMA_10_30"] = {killed_at: T1, pf: 0.75}` to `trading_engine_status.json`. Daemon crashes 10 minutes later for an unrelated reason (OOM, network glitch). Supervisor restarts daemon.

**Correct behavior (SOP#124 applied)**:
1. `_load_state()` reads `trading_engine_status.json`
2. `disabled` dict repopulates: DualMA_10_30 still KILLED at T1
3. Next tick: engine checks `if "DualMA_10_30" in self.disabled` → skip execution
4. SOP#118 G1 cooling clock continues from where it left off (clock measured in wall time, not in-session cycles)
5. No re-kill, no log pollution
6. DualMA_10_30 remains killed until SOP#118 gates pass

**Failure mode (SOP#124 not applied)**:
1. `disabled = {}` (fresh in-memory dict)
2. Next tick: engine runs DualMA_10_30 as if nothing happened
3. PF still 0.75 → immediate re-kill
4. New entry in `kill_lessons.jsonl` (duplicate of T1 kill)
5. Another crash on unrelated reason → another restart → another re-kill
6. Within 48h: 4 "kills" of the same strategy, kill_lessons.jsonl looks like oscillation, SOP#118 gates never start because the cooling clock keeps resetting

**Observed actual failure**: today's audit, DualMA killed 4x in 48h, root cause fixed in commit `c29865a`.

---

## Revenue Connection

A trading engine that loses strategy state on restart CANNOT be deployed to live capital safely. Every crash would re-expose killed strategies to fresh capital, re-creating the losses that triggered the kill. SOP#124 is a **mainnet gate prerequisite** — without it, SOP#96 (mainnet revenue go-live) should not fire.

**Productization**:
- Standalone SOP for quant trading systems and algo ops teams
- Component of the trading-system-audit bundle (SOP#92 + #96 + #118 + #124)
- Reusable as "state durability" pattern for any autonomous decision system (not just trading)

---

## Anti-Patterns

| Pattern | Why it fails |
|---|---|
| Storing `disabled` as an in-memory dict | Lost on restart → re-kill loop |
| `kill_window_floor = 0` | Absorbing state; any non-clean tick kills again |
| Writing state on every tick but never loading on startup | Durable storage but effectively write-only — meaningless |
| Loading state but trusting unvalidated JSON | Corrupted state file crashes engine instead of degrading gracefully |
| Tracking `clean_ticks_since_kill` in-memory only | Recovery progress resets on restart; strategies can never actually recover |
| Treating restart as rare and ignoring the case | Restarts are routine (deploys, OS updates, OOM); plan for them |

---

## Backing MDs & Related SOPs

- **MD-92** — Strategy kill conditions
- **MD-133** — Direct-metric decision
- **Edward Kernel Rule #6** — Recursive output must persist to durable storage
- **distil115 I2** — Kill-window recovery asymmetric design
- **SOP#118** — DualMA Reactivation Gate (depends on SOP#124 — gates can't work without durable state)
- **SOP#109** — Strategy Re-Activation Gate Protocol (adjacent — gate sequence layer)
- **SOP#96** — Mainnet Revenue Go-Live (gated on SOP#124)

---

## Related Files

- `trading/engine.py` — main engine; ReactivationGate class added in commit `c29865a`
- `results/trading_engine_status.json` — durable state file
- `results/kill_lessons.jsonl` — kill event log
- `docs/knowledge_product_118_dualma_reactivation_protocol.md` — SOP#118 (above the state layer)
- `docs/knowledge_product_92_strategy_kill_conditions.md` — kill trigger definition
