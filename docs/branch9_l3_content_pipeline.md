# Branch 9: L3 Evolve — Content Pipeline

## What Was Built

Closes the three-layer loop for the content pipeline:
- **L1 Execute** — `daily_posting_helper.py` (existed: schedule, post, signal)
- **L2 Evaluate** — `--l2-audit` flag (new): 7-day coverage + anomaly detection
- **L3 Evolve** — `--evolve` flag (new): modifies `content_execution_rules.json` from engagement signals

## New Files

| File | Purpose |
|------|---------|
| `platform/content_execution_rules.json` | Mutable execution rules (posting cadence, format weights) |
| `platform/content_evolution_log.jsonl` | Append-only durable log of every rule change |

## Usage

### L3 Evolve — update rules from engagement signals
```bash
python platform/daily_posting_helper.py --evolve saves=12 dms=2 sop=#03
```
Rules modified:
- `saves >= engagement_threshold_saves (5)` → decrease `min_post_interval_days` by 1 (post more often, floor=1)
- `dms >= engagement_threshold_dms (1)` → increase `format_weights[sop]` by 0.5

### L2 Audit — 7-day coverage report
```bash
python platform/daily_posting_helper.py --l2-audit
```
Reports: posts shipped, overdue queue entries, saves/replies/DMs, anomalies.

## Evolution Logic

Mirrors `trading/engine.py` L3 pattern:
- Kill event → `evolve_execution_rules()` → writes `execution_rules.json` + `kill_lessons.jsonl`
- High engagement → `evolve_content_rules()` → writes `content_execution_rules.json` + `content_evolution_log.jsonl`

## Thresholds (adjustable in content_execution_rules.json)

| Signal | Default threshold | Effect |
|--------|-------------------|--------|
| saves | 5 | -1 day to min_post_interval |
| dms | 1 | +0.5 weight to that SOP format |
