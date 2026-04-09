# SOP #109 — Strategy Re-Activation Gate Protocol

> Version: 1.0 | Created: 2026-04-10T UTC | Cycle: 281
> Source: MD-133 (risk control first) + MD-107 (incremental performance evaluation) + MD-04 (strategy kill decision tree) + MD-99 (strategy survival: recent vs historical 60% threshold)

---

## Purpose

Define the minimum gate criteria for **re-activating a strategy that was previously killed** by the L2 evaluation layer. Re-activation without gates = ignoring the kill signal. Re-activation too late = missing regime recovery. This SOP defines the equilibrium: re-activate when conditions genuinely reverse, not when you want to recover losses.

**Core principle**: A strategy was killed for a reason. Re-enabling it requires *evidence* that the kill reason no longer holds, not just elapsed time or hope.

---

## When to Apply

- Any strategy in the `disabled` dict of `execution_rules.json` or `trading_engine_status.json`
- After a BTC regime shift (MIXED → TRENDING or TRENDING → MIXED)
- When reviewing trading engine status: `python trading/engine.py --status`
- Triggered by L3 Evolve output suggesting parameter re-calibration

---

## Gate Sequence (G0 → G5)

### G0 — Kill Reason Audit

Before considering re-activation, identify the **exact kill trigger**:

```
Read kill_lessons.jsonl — find the strategy's kill entry
Extract: reason, ts, metric_at_kill, kill_window
```

Kill reason categories:
- `PF < threshold` — Profit Factor below minimum (most common)
- `MDD > threshold` — Max Drawdown exceeded
- `WR < threshold` — Win Rate too low

**Decision**: If kill reason = regime-specific failure (e.g., trending strategy killed in ranging regime) → proceed to G1. If kill reason = structural failure (e.g., logic bug, data error) → fix root cause first, then re-run from G0.

---

### G1 — Regime Alignment Check

Verify the current regime matches the strategy's design:

```python
# From trading_engine_status.json
current_regime = status["regime"]  # "trending" | "mixed" | "ranging"

# Strategy design regimes:
# DualMA family → trending + mixed
# Donchian family → trending
# BollingerMR family → ranging + mixed
```

**Decision**: Strategy regime matches current regime → proceed to G2. Mismatch → do NOT re-activate (wait for regime shift).

---

### G2 — Minimum Recovery Evidence

The strategy must demonstrate recovery on **paper** or in a **shadow run** before going live. Minimum evidence thresholds:

| Metric | Re-activation threshold |
|--------|------------------------|
| Profit Factor | ≥ kill_min_pf × 1.2 (20% margin above kill floor) |
| Win Rate | ≥ kill_min_wr × 1.1 (10% margin above kill floor) |
| Max Drawdown | ≤ kill_max_dd × 0.75 (25% headroom below kill ceiling) |
| Sample size | ≥ 5 trades (minimum credible sample) |

**Decision**: All three metrics pass → proceed to G3. Any metric fails → extend shadow run.

---

### G3 — Kill Window Reset

Before re-activation, reset the kill evaluation window:

```json
// execution_rules.json — verify kill_window is appropriate
{
  "kill_window": 35,  // standard window
  "kill_count": X     // existing kill count preserved (not reset)
}
```

**Critical**: Do NOT reset `kill_count` — it records cumulative structural weakness. Only reset the evaluation *window start* (implicitly done by re-enabling with fresh tick count).

---

### G4 — Capital Floor Check

Verify the account has sufficient capital to absorb another potential kill cycle:

```
Available capital ≥ (max_dd_threshold × position_size) × 2.0
```

Rationale: If re-activated strategy triggers kill again, must have capital to continue other strategies. Factor of 2.0 = buffer for simultaneous kills.

**Decision**: Capital floor met → proceed to G5. Insufficient capital → wait for other strategies to recover capital first (barbell: preserve core, only risk marginal).

---

### G5 — Re-Activation with Monitoring Flag

Re-activate with enhanced monitoring:

```python
# Remove from disabled dict in execution_rules.json
# Add to monitoring_enhanced list with:
{
  "strategy": "DualMA_10_30",
  "reactivated_at": "2026-04-10T00:00:00Z",
  "monitor_until_tick": current_tick + kill_window,
  "kill_threshold_tightened": True  # 80% of standard thresholds for first window
}
```

**Enhanced monitoring rules** (first evaluation window after re-activation):
- Kill thresholds tightened by 20% (stricter than standard)
- Review after half the kill_window (not end) — early-warning checkpoint
- Any NEW kill in first window = strategy marked STRUCTURAL_WEAK → 3-window cooldown before next re-activation attempt

---

## Self-Test Scenario

**Scenario**: DualMA_10_30 was killed (PF=0.53 < 0.8) during BTC ranging phase. BTC shifts to trending regime. Current PF on shadow run = 1.12 after 8 trades.

**Apply gates**:
- G0: Kill reason = PF 0.53 < 0.8 (not structural, regime-related) → proceed
- G1: Current regime = TRENDING, DualMA design = TRENDING → aligned → proceed
- G2: Shadow PF=1.12 ≥ 0.8×1.2=0.96 ✓, sample=8 ≥ 5 ✓ → proceed
- G3: kill_window=35, reset implicitly on re-enable → proceed
- G4: Capital check passes → proceed
- G5: Re-activate with tightened thresholds, monitor until tick+35

**Answer**: Re-activate. Re-activation is evidence-gated, not time-gated.

---

## Kill Lessons Integration

After each re-activation cycle (kill → shadow → re-activate), append to `kill_lessons.jsonl`:

```json
{
  "ts": "2026-04-10T00:00:00Z",
  "strategy": "DualMA_10_30",
  "event": "REACTIVATION",
  "kill_reason": "PF 0.53 < 0.8",
  "shadow_pf": 1.12,
  "shadow_trades": 8,
  "regime_at_kill": "mixed",
  "regime_at_reactivation": "trending",
  "lesson": "regime-specific-kill-recovers-on-regime-shift"
}
```

Pattern: `kill_lessons.jsonl` grows into a **strategy mortality table** — which strategies die from which causes, and which recover.

---

## Anti-Patterns

| Pattern | Why it fails |
|---------|-------------|
| Time-gated re-activation | "It's been 10 cycles, let's try again" — no evidence |
| Hope-gated re-activation | "BTC is going up, maybe DualMA will work" — no data |
| Reset kill_count | Erases evidence of structural weakness |
| Activating during wrong regime | Guarantees immediate re-kill |
| Skip enhanced monitoring | Loses early warning for structural weakness |

---

## Connections

- **SOP #04**: Strategy Kill Decision Tree (kill side of this SOP)
- **SOP #107**: Incremental Performance Evaluation (shadow run methodology)
- **SOP #96**: Mainnet Trading Revenue Go-Live (re-activation in live context)
- **Execution rules**: `execution_rules.json` → `kill_min_pf`, `kill_window`
- **Kill log**: `kill_lessons.jsonl` → mortality table for all strategies

---

## Twitter Thread Outline (12 tweets)

1. **Hook**: "Your trading bot killed a strategy. When do you turn it back on? Most traders guess. Here's the gate protocol."
2. Kill ≠ permanent. Kill = conditions not met. Conditions change → re-activation is possible.
3. G0: Audit the kill reason. PF failure ≠ logic bug. Different causes need different fixes.
4. G1: Regime alignment first. Don't re-activate a trend-following strategy in a ranging market.
5. G2: Paper evidence required. PF must recover to 1.2× the kill floor. Not 1.01×. Buffer matters.
6. G3: Don't reset kill count. It records structural weakness. Window resets; mortality record doesn't.
7. G4: Capital floor before re-activation. Can you absorb another kill cycle? Barbell principle.
8. G5: Re-activate with tightened thresholds. First window is probationary. Early-warning checkpoint at half-window.
9. The self-test: DualMA killed in mixed regime, shadow PF=1.12 after regime shift → re-activate.
10. Anti-pattern: Time-gated re-activation ("it's been 10 cycles"). Time ≠ evidence.
11. Anti-pattern: Hope-gated re-activation. "BTC is going up" = narrative, not data.
12. **Close**: Kill → shadow → gate → re-activate. The cycle that turns kill logs into mortality tables.
