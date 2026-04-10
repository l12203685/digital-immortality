# Digital Immortality — Repo Index
version: 2.3.0 | read-cost: <400 tokens | updated: 2026-04-12

## Current State → Read This First
staging/quick_status.md   # <200 tokens, daemon auto-updates every cycle

## Task Navigation (read only what you need)
| Task Type | Must Read | Skip |
|-----------|-----------|------|
| Quick confirm (Type A) | quick_status.md | everything else |
| DNA work | templates/dna_boot.md + memory/recursive_distillation.md (tail 5) | dna_core.md full text |
| Trading analysis | trading/paper_trader.py + results/paper_live_log.jsonl (tail) | trading_engine_log.jsonl |
| Dev/maintenance | the specific .py file only | docs/, results/ |
| Strategic L3 (Type C) | CLAUDE.md + staging/session_state.md + memory/ | results/ entirely |
| Outreach | staging/outreach_week1_execution.md | other staging files |

## Directory Map (post-archive sizes)
templates/  ~130K  DNA + boot tests (dna_boot.md = cold-start kernel only)
memory/     ~180K  cross-session persistence (insights.json + distillation)
staging/     ~44K  inter-session relay (daemon updates each cycle)
platform/   ~180K  daemon + Discord + dashboard scripts
trading/    ~208K  paper trader + strategies (fully autonomous)
docs/        ~500K  active SOPs #101-117 + key references
results/     ~4MB  recent cycle logs + live trading data

## Never Load (Claude should skip these entirely)
results/archive/    old cycles, backtests, collision history
docs/archive/       SOP #1-100, old publish threads
__pycache__/        bytecode

## Human-Gated Blockers (check quick_status.md for current state)
- mainnet API keys (Jul 7 deadline)
- Outreach DMs x5 (staging/outreach_week1_execution.md)
- Samuel Turing Test invite
