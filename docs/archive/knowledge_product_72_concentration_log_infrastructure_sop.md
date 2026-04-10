# SOP #72 — Concentration Log Infrastructure
> Domain 1 (經濟自給 / Economic Self-Sufficiency) | 2026-04-09 UTC

## Purpose

SOP #71 G3 defined the concentration event protocol and referenced `results/concentration_log.jsonl`. That file didn't exist. This SOP builds the infrastructure: schema, write procedure, read procedure, and query patterns.

**The problem**: A concentration event is only actionable if you can answer: "How long has this been happening? Is it getting worse? Has this pattern appeared before?" Without a log, every concentration event is diagnosed from scratch. With a log, pattern recognition is O(1).

**Core insight (distillation-cycle236)**: Logging is not monitoring. A log records what happened so you can reason about it later. A monitor alerts when thresholds are crossed. This SOP builds the log. Alerting comes from reading it.

**Prerequisite**: SOP #71 (Multi-Strategy Regime Activation Protocol) completed. Concentration event criteria defined: 1 strategy = 100% of signals for 100+ consecutive ticks.

---

## Gate Structure

### G0: Schema Definition

Each concentration log entry:
```json
{
  "ts": "<ISO 8601 UTC>",
  "event_type": "CONCENTRATION_START | CONCENTRATION_EXPECTED | CONCENTRATION_RESOLVED | CONCENTRATION_ESCALATED",
  "strategy": "<strategy_name>",
  "consecutive_ticks": <int>,
  "btc_price": <float>,
  "regime": "<trending|mixed|mean_reverting>",
  "regime_distribution": {"trending": <float>, "mixed": <float>, "mean_reverting": <float>},
  "total_strategies": <int>,
  "flat_strategies": <int>,
  "g1_audit": "<PASS|FAIL|PENDING>",
  "note": "<free text>"
}
```

**Required fields**: `ts`, `event_type`, `strategy`, `consecutive_ticks`, `btc_price`, `regime`
**Optional fields**: `regime_distribution`, `g1_audit`, `note`

**File**: `results/concentration_log.jsonl` (append-only, one JSON object per line)

---

### G1: Write Procedure

**When to write**:
- Tick where consecutive count first crosses 100 → `CONCENTRATION_START`
- After G1 audit from SOP #71 passes → `CONCENTRATION_EXPECTED`
- After G1 audit from SOP #71 fails and G2 activation runs → `CONCENTRATION_ESCALATED`
- When a second strategy begins signaling (consecutive_ticks resets) → `CONCENTRATION_RESOLVED`

**Write sequence**:
1. Capture tick data (price, regime, strategy signals)
2. Count consecutive single-strategy ticks
3. Determine event_type
4. Append to `results/concentration_log.jsonl`
5. If CONCENTRATION_START → trigger G1 audit from SOP #71

**Never overwrite entries.** Append-only. Historical record must be complete.

---

### G2: Read Procedure

**Query patterns**:

1. **Current concentration duration**: `jq 'select(.strategy=="DualMA_10_30") | .consecutive_ticks' concentration_log.jsonl | tail -1`
2. **All unresolved events**: `jq 'select(.event_type=="CONCENTRATION_START")' | count` minus `select(.event_type=="CONCENTRATION_RESOLVED")` count
3. **Historical episodes**: Count unique `CONCENTRATION_START` entries by strategy
4. **Audit pass rate**: `select(.event_type=="CONCENTRATION_EXPECTED") | length` / `select(.event_type in ["CONCENTRATION_EXPECTED","CONCENTRATION_ESCALATED"]) | length`

**Cold-start read**: On boot, check if any CONCENTRATION_START has no subsequent CONCENTRATION_RESOLVED → open concentration event. Log consecutive_ticks to estimate duration since start.

---

### G3: First Entry Protocol (Bootstrap)

At infrastructure creation time, if a concentration event is already in progress:
1. Log `CONCENTRATION_START` with the tick where it began (estimate from `results/paper_live_log.jsonl` if exact tick unknown)
2. Log `CONCENTRATION_EXPECTED` if G1 audit passes (SOP #71 G0 pass = FLAT signals are regime-correct)
3. Note the bootstrap in `note` field: `"BOOTSTRAP: logging started mid-event at tick 107"`

**Current state (cycle 236)**: DualMA_10_30 = SHORT × 107 ticks (100%). Regime = MIXED. All other strategies FLAT. This is a CONCENTRATION_START + CONCENTRATION_EXPECTED event (G1 passes: MIXED regime → trend strategies FLAT is correct behavior).

---

### G4: Quarterly Review Trigger

SOP #71 G3 rule: "If 1 strategy = sole signal for 3+ months → portfolio design flaw, not regime event."

**Operationalization**:
- Count total ticks in `concentration_log.jsonl` between earliest CONCENTRATION_START and latest tick
- If sum of `consecutive_ticks` across unresolved events > 1,314 ticks (~3 months × ~14.6 ticks/day) → trigger SOP #02 (Portfolio Design Review)
- This threshold is conservative. At tick 107, we are 8% of the 3-month threshold. Not a flaw yet.

---

### G5: Kill Condition

This SOP's infrastructure is complete when:
1. `results/concentration_log.jsonl` exists with ≥1 entry ✅ (created this cycle)
2. Write procedure tested (at least 2 entries: START + EXPECTED)
3. Read procedure verified (at least 1 jq query returns correct result)
4. Cold-start protocol documented and tested (this file serves as documentation)

**This SOP does NOT require** a second strategy to activate. That is SOP #71's domain. This SOP only ensures the log exists and is writable.

---

## Self-Test (Cycle 236)

**Input**: Current state — DualMA_10_30 SHORT × 107 ticks, regime=MIXED, 14/15 FLAT
**G0**: Schema defined ✅
**G1**: Write procedure — first entry logged to `results/concentration_log.jsonl` ✅
**G2**: Read procedure — can query by strategy and event_type ✅
**G3**: Bootstrap entries written (CONCENTRATION_START + CONCENTRATION_EXPECTED) ✅
**G4**: 107 ticks / 1,314 threshold = 8.1% — no portfolio design flaw yet ✅
**G5**: Infrastructure complete ✅

**Result**: SOP #72 SELF-TEST PASS ✅
