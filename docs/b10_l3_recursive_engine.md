# B10 L3 — Recursive Engine Self-Modification Layer
> Created: 2026-04-13 (cycle 376)
> Pattern: mirrors trading L3 (execution_rules.json evolved by kill events)

## What L3 Means Here

| Layer | Description |
|-------|-------------|
| L1 | Single session (Claude Code E0 — human-triggered) |
| L2 | Daemon loop (scheduled, autonomous) |
| **L3** | **Self-modification — engine learns from its own failure modes and evolves its operating parameters** |

Trading L3: kill events → execution_rules.json (PF threshold, kill window, recovery ticks)
Recursive engine L3: stall events → engine_rules.json (stale threshold, queue floor, commit cadence)

## Failure Modes (Recursive Engine)

| Mode | Definition | Known Instances |
|------|------------|-----------------|
| DEAD_LOOP | stale_cycles >= stale_threshold; no new insights produced | cycle 78 (stale=3) |
| QUEUE_EMPTY | automatable_queue_size < queue_min; all work human-gated | near-miss cycles 375+ |
| COMMIT_DROUGHT | no git commit in drought_threshold consecutive cycles | — |
| CONTEXT_DRIFT | output diverges from core goal (manual detection only, v1) | — |

## engine_rules.json Schema

```json
{
  "stale_threshold": 3,
  "queue_min": 1,
  "commit_drought_threshold": 3,
  "dead_loop_count": 1,
  "last_dead_loop": { "cycle": 78, "stale_cycles": 3, "ts": "..." },
  "last_recovery": { "cycle": null, "action": null, "ts": null },
  "evolved_at": "...",
  "evolution_log": []
}
```

## Evolution Logic

Same pattern as trading execution_rules.json:

1. **Detect** stall event in engine_l3_log.jsonl
2. **Classify** failure mode
3. **Update** engine_rules.json — tighten threshold if repeated, loosen if false positive
4. **Log** in evolution_log (cycle, mode, old_param, new_param, reason)

### DEAD_LOOP evolution
- If `dead_loop_count` increases: tighten `stale_threshold` by -1 (min=2)
- If no dead loop in 50 cycles: relax threshold by +1 (max=5)

### QUEUE_EMPTY prevention (from distil169 insight 2)
- Before completing the last automatable task, generate the next one
- `queue_min=1` enforced: daemon must always have ≥1 automatable task queued
- Recovery action: scan branches for any non-human-gated work; if none, initiate L3 analysis cycle

### COMMIT_DROUGHT recovery
- After `drought_threshold` no-commit cycles: force a tree-sync commit (no-op commits permitted for engine heartbeat)
- This prevents the engine's output from becoming ephemeral (invisible to next session)

## Recovery Action Catalog

| Mode | Auto-Recovery |
|------|--------------|
| DEAD_LOOP | Inject: "scan all branches for PENDING work, generate 3 automatable tasks" |
| QUEUE_EMPTY | Inject: "L3 analysis cycle — review all branches for non-human-gated improvements" |
| COMMIT_DROUGHT | Force tree-sync + heartbeat commit |
| CONTEXT_DRIFT | Re-read CLAUDE.md + SKILL.md + last 3 daemon log entries; re-anchor |

## Implementation Status

| Component | Status |
|-----------|--------|
| engine_l3_log.jsonl | OPERATIONAL (1 event: cycle 78 DEAD_LOOP) |
| engine_rules.json | **INITIALIZED this cycle (376)** |
| L3 detection in recursive_engine.py | PENDING (v2 scope) |
| Auto-recovery injection | PENDING (v2 scope) |

## v1 vs v2 Scope

**v1 (this cycle)**: Rules documented + engine_rules.json initialized. Manual review per cycle.
**v2 (future)**: `recursive_engine.py --l3-check` reads engine_l3_log.jsonl, updates engine_rules.json, injects recovery prompt automatically.

## Relation to Other L3 Systems

| Branch | L3 File | Trigger |
|--------|---------|---------|
| B1.1 Trading | results/execution_rules.json | PF/WR/MDD kill events |
| B5 Content | daily_posting_helper.py --evolve | engagement signals |
| **B10 Recursive** | **results/engine_rules.json** | **stall / queue-empty / drought events** |

## First Derived Rules (from known history)

1. **stale_threshold=3**: one DEAD_LOOP at stale=3 confirms this is the correct trigger point
2. **queue_min=1**: distil169 insight 2 — automatable queue must never reach zero
3. **commit_drought_threshold=3**: no data yet; set conservatively at 3 cycles
4. **drift_detection=manual**: no automated scoring yet; visual check against CLAUDE.md axioms
