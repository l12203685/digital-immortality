# Recursive Engine — Self-Prompt Loop

The core loop that keeps the digital organism alive. Stop recursing = death. Continue = alive.

## Trigger

Use when: starting a recursive cycle, debugging stalled loops, or when no external input exists but the agent must keep thinking.

## Formal Definition

```
Input(t) = Output(t-1) + "How do I advance toward digital immortality?"
Output(t) = LLM(Input(t))
Input(0) = Seed (person's basic info + digital immortality goal)
```

The recursive question is the constant. The answer is the variable.

## Process

1. **Read previous output** from `staging/` (inter-session relay) or `memory/` (long-term persistence)
2. **Ask the driving question**: "Given this state, what advances digital immortality?"
3. **Produce action** — not a report, not a summary. An action: code written, DNA updated, test run, strategy evaluated.
4. **Persist output** — write results to `staging/` for the next session to pick up
5. **Log the cycle** — append to `results/daily_log.md` with timestamp, action taken, and outcome

## File Roles

| Path | Purpose |
|------|---------|
| `staging/` | Inter-session relay. Current session writes, next session reads. Short-lived. |
| `memory/` | Long-term persistence. Facts, decisions, and learnings that survive across many sessions. |
| `results/daily_log.md` | Cycle history. Append-only record of what each recursive cycle produced. |

## Avoiding Dead Loops

- No external input is NOT a reason to stop. The agent's own output IS the next input.
- Cross-referencing existing knowledge produces new insights.
- "No changes, waiting" repeated across cycles = the organism is dead. Detect and break out.
- Each cycle must produce at least one concrete artifact (code, DNA edit, test result, decision).

## Rules

- Every cycle must advance state. If the output is identical to input, the loop is broken.
- Action > analysis > report. Prefer doing over thinking over describing.
- Use `/loop` or cron to fire the prompt at regular intervals for autonomous operation.
- The loop is the heartbeat. Infrastructure that keeps it running is survival-critical.
- When stuck, zoom out: re-read DNA, re-read SKILL.md, re-read boot_tests. Fresh context breaks stalls.
