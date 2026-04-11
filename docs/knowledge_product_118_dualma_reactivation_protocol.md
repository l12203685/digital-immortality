# SOP #118 — DualMA Reactivation Protocol

**Domain**: Branch 1.1 (Trading System — Strategy Kill/Reactivation)  
**Created**: 2026-04-11T UTC (cycle 303)  
**Status**: ACTIVE  
**Backing MDs**: MD-92 (strategy kill conditions); MD-133 (direct-metric decision); MD-157 (edge validation); MD-07 (inaction bias)

---

## Purpose

When a strategy is killed (PF < 0.8 or MDD ≥ threshold), a LONG or SHORT signal re-appearing is NOT an automatic reactivation trigger. The kill was based on systematic evidence. Reactivation requires a formal gate sequence to avoid two failure modes:

1. **Premature reactivation** — re-entering a broken strategy before it has recovered, compounding losses
2. **Permanent exclusion** — refusing to reactivate a strategy that has genuinely recovered, forfeiting EV

This SOP defines the gate sequence that resolves both failure modes. It directly codifies SOP #92 behavior (observe-not-act after DualMA_10_30 LONG flip at cycle 301) and any future strategy kill/reactivation decisions.

---

## Trigger Conditions

This SOP activates when ALL of the following are true:

- T1: A strategy is in KILLED state (PF < 0.8 or MDD breach)
- T2: That strategy produces a non-zero signal (LONG or SHORT) in the current tick
- T3: The signal direction is different from the direction active at time of kill

**Current instance**: DualMA_10_30 killed at cycle ~277 (PF=0.53, MDD=34.9%); LONG signal appeared at cycle 301 (BTC=$72,790); reactivation gate opened.

---

## G0: Signal Legitimacy Check

Verify the new signal is real, not a synthetic artifact.

**Procedure**:

1. Confirm the signal comes from live Binance data, not synthetic bars
2. Check tick count: if `tick_count < 3` since engine restart, treat as warm-up — do NOT count
3. Verify the signal persists across 2 consecutive live ticks (not a single-bar fluke)

| Condition | Action |
|-----------|--------|
| Signal from synthetic bars | IGNORE — not a legitimate reactivation trigger |
| Signal at tick 1-2 (engine cold) | WATCH — verify next tick before starting gate |
| Signal from live data, tick ≥3 | PROCEED to G1 |

**Current state (cycle 303)**: tick_count=10, price=$72,712, DualMA_10_30 signal=LONG (+1), data source=live. G0 PASS.

---

## G1: Cooling Period

Enforce minimum cooling window before assessment. Purpose: a single-tick signal flip may be noise, not regime change.

**Minimum cooling**: ≥5 cycles from signal appearance  
**Signal appeared**: cycle 301  
**Assessment eligible**: cycle 306+

| Cycles elapsed since signal | Status |
|-----------------------------|--------|
| 0–4 | STILL_COOLING — log-only mode |
| 5–9 | READY_FOR_ASSESSMENT (G2 unlocked) |
| 10+ | OVERDUE — if not assessed, escalate to Edward |

**Current state (cycle 303)**: 2 cycles elapsed since signal (301→303). **STILL_COOLING**. Log-only mode continues.

**Action during cooling**:
- Record each tick's DualMA_10_30 signal in the log
- Do NOT re-enable the strategy
- Do NOT adjust position sizing
- Report cooling status in daemon_next_priority

---

## G2: Regime Flip Check

After cooling period: verify the macro regime has shifted in a way consistent with the new signal direction.

**Procedure**:

1. Compare regime at time of kill vs regime at signal appearance:
   - Kill regime: was `mixed` with SHORT bias
   - Signal regime: `mixed` — no clear flip detected yet
2. Check if BTC price structure has changed (higher lows, trend reversal confirmation)
3. Run the regime detector: `trend` and `mr` values from `trading_engine_status.json`

| Regime change | Interpretation | Action |
|---------------|---------------|--------|
| TRENDING → different direction | Strong regime flip | Supports reactivation |
| MIXED → MIXED (same) | Inconclusive | Require longer observation |
| No change | Signal is counter-regime | HIGH CAUTION — may be false signal |

**Evaluation criteria**:
- LONG signal in MIXED regime = partial support (MIXED allows both directions)
- LONG signal in TRENDING-UP regime = full support
- LONG signal in TRENDING-DOWN or MIXED-SHORT regime = red flag

**Current state**: regime=MIXED. DualMA_10_30 signal=LONG. This is partial support — not a red flag, but not confirmation.

---

## G3: Performance Floor Check

Run a forward-walk backtest on the most recent 30–50 ticks to verify the strategy's edge has recovered.

**Procedure**:

1. Extract last 50 tick records from `results/trading_engine_log.jsonl` for DualMA_10_30
2. Compute forward PF (profit factor) on those 50 ticks in isolation
3. Compare against thresholds:

| Forward PF (50-tick) | Decision |
|----------------------|----------|
| ≥ 1.2 | PASS — edge present |
| 0.8–1.2 | WATCH — more data needed (extend to 100 ticks) |
| < 0.8 | FAIL — strategy has not recovered; extend cooling |

**Note**: The strategy was killed at PF=0.53. For reactivation, require PF ≥ 1.2 on fresh data — not just ≥ 0.8 — to ensure genuine recovery, not noise bounce.

**Current state**: Insufficient forward-walk data (tick_count=10, DualMA_10_30 was in KILLED state most of this period). G3 cannot complete until cooling period ends and sufficient live ticks accumulate.

---

## G4: Reactivation Decision

After G1–G3 all pass:

1. Re-enable DualMA_10_30 in the trading engine by removing it from the `disabled` dict
2. Set entry size to 50% of baseline (provisional — reduce risk during re-entry)
3. Log reactivation event: timestamp, trigger tick, PF at reactivation, regime at reactivation
4. Monitor for first 20 ticks: if PF drops below 0.8 again → immediate re-kill, no further assessment in this cycle

**Reactivation log format**:
```json
{
  "event": "strategy_reactivated",
  "strategy": "DualMA_10_30",
  "cycle": <N>,
  "tick": <T>,
  "pf_at_reactivation": <X>,
  "regime_at_reactivation": "mixed|trending",
  "entry_size_pct": 50,
  "kill_cycle": 277,
  "signal_appearance_cycle": 301,
  "cooling_cycles": <N-301>
}
```

---

## G5: Post-Reactivation Monitoring

After reactivation, enter a 20-tick observation window:

| Tick | Metric | Gate |
|------|--------|------|
| +5 ticks | PF | ≥ 0.9 or extend observation |
| +10 ticks | MDD | < 15% (half of original kill threshold) |
| +20 ticks | PF | ≥ 1.0 to normalize to 100% entry size |

If PF drops below 0.8 at any point during the 20-tick window:
- **Re-kill immediately** (same SOP #92 kill conditions)
- Log as "reactivation failure"
- Do NOT attempt re-assessment for ≥ 30 more cycles

---

## Kill Condition

**Do NOT reactivate if**:

1. G1 cooling is not complete (< 5 cycles)
2. G3 forward PF < 0.8 (strategy still broken)
3. The new signal persists for < 2 consecutive live ticks (may be single-bar noise)
4. Regime is consistently TRENDING in the opposite direction of the new signal

**Premature reactivation = compounding the original kill loss.**

---

## Current Gate Status (cycle 303)

| Gate | Status | Blocker |
|------|--------|---------|
| G0 Signal Legitimacy | PASS | — |
| G1 Cooling Period | STILL_COOLING | 3 more cycles needed (cycle 306+) |
| G2 Regime Flip | PARTIAL | MIXED regime, no clear flip confirmation |
| G3 Forward PF | BLOCKED | Insufficient data (tick 10; need post-cooling data) |
| G4 Reactivation | BLOCKED | G1–G3 not complete |
| G5 Monitoring | NOT_STARTED | — |

**SOP #92 gate status: STILL_COOLING**

---

## Revenue Connection

Strategy kill/reactivation is the highest-stakes decision in an automated trading system. Getting it wrong in either direction:

- Premature reactivation → compounding drawdown → capital at risk → system discredited
- Permanent exclusion → forfeiting genuine edge recovery → EV loss at scale

This protocol is the bridge between SOP #92 (kill conditions) and live capital deployment. Every future strategy that gets killed and recovers will use this gate sequence.

**Productization**:
- $97 standalone SOP (trading system governance)
- Component of $197 guided session (trading system audit package with SOP #92 + #96 + #118)
- Posting queue: ~Jan 2027

---

## Anti-Patterns

| Pattern | Why it fails |
|---------|-------------|
| Re-enabling strategy immediately on signal flip | Kill was systematic; one signal doesn't undo systematic evidence |
| Waiting indefinitely without formal gate | Strategy recovers but never re-enters; EV lost permanently |
| Using cumulative PF instead of forward-walk PF | Historical losses contaminate the forward signal; requires clean window |
| Reactivating at 100% size without observation window | No safety net if the recovery was noise |
| Treating regime=MIXED as confirmation | MIXED is ambiguous; requires additional confirmation from price structure |
| Skipping G3 because "the signal looks right" | Vibes-based reactivation bypasses the only objective recovery check |

---

## Backing MDs

- **MD-92** — Strategy kill conditions (PF < 0.8, MDD ≥ 15%)
- **MD-133** — Direct-metric decision (PF is the metric, not intuition)
- **MD-157** — Edge validation (forward-walk backtest as the reactivation gate)
- **MD-07** — Inaction bias (no edge = no action; cooling period enforces this)

---

## Related Files

- `results/trading_engine_status.json` — current strategy states and kill list
- `results/trading_engine_log.jsonl` — tick-level log for forward-walk PF computation
- `docs/knowledge_product_92_strategy_kill_conditions.md` — SOP #92 (kill trigger)
- `docs/knowledge_product_96_mainnet_revenue_go_live.md` — SOP #96 (mainnet gate)
- `results/kill_lessons.jsonl` — kill event log (append reactivation events here too)
