# Recursive Engine Daemon

Lightweight Python daemon that continuously runs the digital immortality recursive engine against Claude API.

## Prerequisites

- Python 3.10+
- `anthropic` SDK installed (`pip install anthropic`)
- `ANTHROPIC_API_KEY` environment variable set

## Quick Start

```bash
export ANTHROPIC_API_KEY=sk-ant-...
cd C:\Users\admin\workspace\digital-immortality
python platform/recursive_daemon.py --interval 300
```

## Arguments

| Flag | Default | Description |
|------|---------|-------------|
| `--interval` | `0` (5s floor) | Seconds between cycles |
| `--model` | `claude-haiku-4-5` | Claude model ID |
| `--max-cycles` | `0` (infinite) | Stop after N cycles |
| `--no-commit` | off | Disable auto git commit after each cycle |

## How It Works

1. Loads `LYH/agent/edward_dna_v18.md` as system prompt context
2. Injects the 6-branch dynamic tree into the system prompt
3. Each cycle sends the recursive prompt to Claude API:
   > "You are Edward's recursive engine. Read the repo state, pick the highest-derivative branch from the dynamic tree, do one concrete thing, report what you did in under 100 words."
4. Appends the response to `results/daemon_log.md`
5. If there are uncommitted changes in the repo, auto-commits them
6. Waits for `--interval` seconds, then loops

## Output

All cycle outputs are appended to `results/daemon_log.md` with timestamps:

```markdown
## Cycle 1 — 2026-04-07 12:00:00 UTC

[Claude's response here]
```

## Stopping

Press `Ctrl+C` for graceful shutdown. The daemon finishes the current cycle before exiting.

## Cost Estimate

Using `claude-haiku-4-5` at 300s intervals:
- ~288 calls/day
- ~$0.50-1.00/day (depending on DNA size and response length)

## Examples

```bash
# Run with 5-minute interval (recommended for continuous use)
python platform/recursive_daemon.py --interval 300

# Run 10 cycles then stop (for testing)
python platform/recursive_daemon.py --max-cycles 10

# Use a different model
python platform/recursive_daemon.py --model claude-sonnet-4-5-20250514 --interval 600

# Dry run without git commits
python platform/recursive_daemon.py --interval 60 --no-commit
```
