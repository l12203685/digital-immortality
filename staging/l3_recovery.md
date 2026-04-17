# L3 Recovery — Loop Broken (2026-04-17)

## Root Cause
The dead loop (cycles 528-569, similarity=1.00) was caused by two bugs:
1. `execute_plan_actions()` only fired executors when `runnable == "script"`, but the LLM planner produced free-form shell commands as runnable values
2. `l3_recovery.md` was never read by `CycleState.gather()`, so recovery signals never reached the planner

## Fixes Applied
1. `recursive_daemon.py`: Executor now fires for ANY registered branch when `runnable != "read-only"`
2. `cycle_protocol.py`: Added `l3_recovery` field to `CycleState`, included in prompt
3. `PLAN_SYSTEM_PROMPT`: Clarified that `runnable` must be "script" or "read-only" only
4. `engine_rules.json`: Reset `dead_loop_count` to 0
5. `daemon_next_priority.txt`: Fresh loop-break directive

## Status
RESOLVED — next cycle should produce distinct plan with working executors.