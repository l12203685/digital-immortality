# SOP #66 — External Signal Log & G0 State Machine Operationalization
> Domain: Distribution + Survival (Branch 5 + Branch 6)
> Created: 2026-04-09 UTC (cycle 230)
> Status: ACTIVE
> Prerequisite: SOP #65 (External Validation & Feedback Loop Protocol)
> Implements: SOP #65 G0 state machine using `results/external_signal_log.jsonl`

---

## Why This SOP Exists

SOP #65 defined the framework (遞迴-persist=演化 vs 遞迴-persist=自言自語). It specified `results/external_signal_log.jsonl` as the G0 state machine data source.

**SOP #66 makes it operational.** Without this SOP:
- The log doesn't exist → state machine has no input
- The DNA violation detector (F10 runbook) has nothing to read
- The external loop is invisible to the recursive engine

This is a **persistence infrastructure SOP**: framework → live audit trail.

---

## G0 — Bootstrap & Schema

**Trigger**: First run, or log absent.

### Schema
Append-only JSONL. Each entry:
```json
{"ts": "2026-04-09T07:10:00Z", "type": "TYPE", "content": "brief", "signal": "positive|neutral|negative|correction"}
```

| Type | When | Signal |
|------|------|--------|
| `SYSTEM_BOOTSTRAP` | First run | `neutral` |
| `MAINNET_GO` | Keys set + first live tick | `positive` |
| `POST` | Thread posted on X | `positive` |
| `DM` | DM received | `positive` or `correction` |
| `CALIBRATION` | DM contradicts an SOP | `correction` |
| `REVENUE` | Gumroad/consulting payment | `positive` (+ `"amount": float`) |
| `G4_WEEKLY_REVIEW` | Every Sunday | `neutral` |
| `KILL_CONDITION` | Platform failure per G5 | `negative` |

**Invariant**: Append only. Never delete. Never backfill. UTC timestamps.

### G0 State Machine
Run: `python tools/external_loop_check.py`

| State | Condition | Next action |
|-------|-----------|-------------|
| `PRE_LAUNCH` | posts=0 | Post SOP #01 on X NOW |
| `SEEDING` | posts≥1, DMs<10 | Post every 48h, watch DMs |
| `MONETIZING` | DMs≥10 | Build Gumroad offer (SOP #34) |
| `SUSTAINABLE` | Revenue>$0 recurring | Reinvest + expand (SOP #63 G5) |

---

## G1 — Log Entry Protocol

For each **POST**:
```bash
echo '{"ts": "UTC_ISO", "type": "POST", "content": "SOP #01 thread on X", "signal": "positive"}' >> results/external_signal_log.jsonl
```

For each **DM**:
```bash
echo '{"ts": "UTC_ISO", "type": "DM", "content": "brief summary", "signal": "positive"}' >> results/external_signal_log.jsonl
```

For **CALIBRATION** (DM contradicts SOP):
```bash
echo '{"ts": "UTC_ISO", "type": "CALIBRATION", "content": "SOP #07 contested: [argument]", "signal": "correction"}' >> results/external_signal_log.jsonl
```

For **MAINNET_GO** (set before posting SOP #01):
```bash
echo '{"ts": "UTC_ISO", "type": "MAINNET_GO", "content": "Keys set, mainnet_runner.py --tick fired", "signal": "positive"}' >> results/external_signal_log.jsonl
```

---

## G2 — DNA Violation Detector

Run: `python tools/external_loop_check.py --dna-check`

| Violation | Condition | Response |
|-----------|-----------|----------|
| STALE_PRE_LAUNCH | PRE_LAUNCH >30d after MAINNET_GO | Post SOP #01. No exceptions. |
| GHOST_POSTING | No post for >14d | Ship oldest thread as-is. |
| INVISIBLE_CONTENT | ≥20 posts + 0 DMs | Controversial claim pivot (SOP #65 G5 Case B). |

**F10 runbook integration**: F10 checks this file on every cold start. If state=PRE_LAUNCH AND MAINNET_GO event exists → escalate immediately to Edward.

---

## G3 — Recursive Engine Integration

Every daemon cycle:
1. `python tools/external_loop_check.py` → read state
2. If state changed → log to daemon_log.md
3. If violations → prepend as CRITICAL to cycle output
4. State feeds into dynamic_tree.md Branch 5 status

**Current state**: PRE_LAUNCH (posts=0, DMs=0, revenue=$0)
**Next state trigger**: Edward posts SOP #01 → log POST → auto-upgrades to SEEDING

---

## G4 — Weekly Review (Every Sunday)

```bash
python tools/external_loop_check.py --weekly-review --verbose
```

Appends G4_WEEKLY_REVIEW entry. Target: ≥3 posts/week, ≥1 DM/week.
If PRE_LAUNCH for ≥2 Sundays after MAINNET_GO: escalate to Edward.

---

## G5 — Kill Conditions

- **Log missing**: G0 bootstrap (already done cycle 230).
- **PRE_LAUNCH >30d post MAINNET_GO**: `--dna-check` exits 1. Escalate.
- **≥20 posts, 0 DMs**: SOP #65 G5 Case B (controversial claim).
- **≥14d no post**: SOP #65 G5 Case A (ship oldest unscheduled thread).

---

## Connected SOPs

| SOP | Connection |
|-----|-----------|
| SOP #65 | Parent framework; defines schema; F10 |
| SOP #63 | 90-day revenue protocol; G1 mainnet gate |
| SOP #34 | Gumroad offer (triggered at MONETIZING) |
| SOP #01 | First post — only action that moves PRE_LAUNCH → SEEDING |

---

## Self-Test

```
$ python tools/external_loop_check.py
State: PRE_LAUNCH, Posts: 0, DMs: 0, Revenue: $0.00
No violations. NEXT: Post SOP #01 on X.
```
Expected: PRE_LAUNCH, no violations (mainnet not yet live). ✅

---

*2026-04-09 UTC — SOP series #01~#66 COMPLETE — posting queue Aug 15, 2026*
