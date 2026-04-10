# SOP #75: Strategy Pool Lifecycle Protocol
**Domain 1 — 經濟自給 (Economic Self-Sufficiency)**
**Written**: 2026-04-09T08:38Z (Cycle 238)

---

## Why this SOP exists

After 110 paper-live ticks, one question exposes a critical gap:

> "If DualMA_10_30 flips LONG, what strategy covers the SHORT bias?"

The answer should be: **another validated strategy in the pool**. But for 110 ticks, the concentration log shows 1 active signaling strategy. The pool has 15–18 strategies registered — yet 14/15 to 17/18 are permanently FLAT.

The trading system rule says:
> *"Trading is NOT 'build 10 strategies and stop'. It's a continuous loop: Develop → Backtest → WF Validate → Paper → Kill failing → Live. Repeat forever."*

This SOP operationalizes that loop. Without it, the pool stagnates. With it, the pool is alive.

---

## Input conditions (G0: When to trigger)

Run this protocol when ANY of:
- Consecutive CONCENTRATION_TICK entries ≥ 100 (quarterly threshold: 1,314)
- Regime shift detected (MIXED → TRENDING or MIXED → MEAN_REVERTING)
- Pool drops below 10 registered strategies
- Kill event fires (any strategy removed)
- L3 evolution triggered on Branch 1.1
- Scheduled: once per 30 days minimum

**This cycle trigger**: Concentration tick 110. Pool expansion warranted.

---

## G1: Generate candidates

```bash
python trading/strategy_generator.py --generate 10
```

**What it does**:
- Samples parameter space: DualMA, Donchian, DonchianConfirmed, BollingerMeanReversion
- Wraps with optional RegimeFilter and/or RSIFilter
- Generates unique strategy names (hash-based, deterministic)
- Uses real BTC daily data via yfinance (fallback: synthetic geometric random walk, seed=42)

**Interpret output**:
- `PASS — windows=N/5, sharpe=X.XX, mdd=Y.Y%` → added to `strategies.py`
- `FAIL — skipping` → not registered; recorded in `results/strategy_candidates.json`

**Expected pass rate**: 30–60% of candidates

---

## G2: Walk-forward validation standards

A candidate passes if **≥3/5 windows** satisfy both:
- Sharpe > 0.5 (risk-adjusted return)
- MDD < 25% (per-window drawdown)

Note: Full-backtest MDD may exceed 25% even when WF passes — this is acceptable.
The WF per-window check is the robustness signal; full-backtest MDD is informational.

**Kill threshold** (different from WF threshold):
- MDD > 10% in paper trading → kill
- Win rate < 35% (≥5 trades) → kill
- Profit factor < 0.85 (≥5 trades) → kill

---

## G3: Add to paper trade pool + initial monitoring

After `--generate N`:
1. New strategies are automatically added to `NAMED_STRATEGIES` in `trading/strategies.py`
2. They appear in paper-live logs on the next `--paper-live` tick
3. Monitor for **minimum 30 ticks** before kill conditions apply
4. Log pool expansion to `results/concentration_log.jsonl` (POOL_EXPANSION event type)

**Minimum pool health**:
- ≥ 3 strategies with different base classes (DualMA, Donchian, Bollinger)
- ≥ 1 strategy with RegimeFilter
- ≥ 1 strategy with RSIFilter
- Total ≥ 10 registered

---

## G4: Prune failing strategies

```bash
python trading/strategy_generator.py --prune
```

**Kill conditions check** (from paper_live_log.jsonl):
- Reads all paper-live trades per strategy
- Applies: MDD>10%, WR<35% (≥5 trades), PF<0.85 (≥5 trades)
- Removes killed strategies from `strategies.py`
- Logs removals to `results/strategy_candidates.json`

**Run frequency**: Every 30 ticks minimum; after any regime shift; after each G1 run.

**This cycle (Cycle 238)**:
- Prune result: 0 strategies killed
- `default` strategy (PF=0.72 < 0.85) — not in NAMED_STRATEGIES; auto-removed from tracking
- All 15 NAMED_STRATEGIES: KEEP (MDD=0.6%, WR=54.2%, PF≥0.92)

---

## G5: Pool health report

After any G1+G4 cycle, record state to `results/concentration_log.jsonl`:

```json
{
  "event_type": "POOL_EXPANSION",
  "ts": "<UTC>",
  "strategies_added": 3,
  "strategies_killed": 0,
  "pool_size_before": 15,
  "pool_size_after": 18,
  "strategies_added_list": ["gen_Donchian_RF_5e649e", "gen_Donchian_RSI_d3d59e", "gen_DualMA_RF_eda1cb"],
  "note": "Triggered at concentration tick 110."
}
```

**Pool health verdict format (L2 per cycle)**:
```
B1.1 pool: 18 registered, 1 active (DualMA_10_30 SHORT×110), 17 FLAT.
Concentration event: EXPECTED (regime=MIXED, 8.4% of quarterly threshold).
Last expansion: Cycle 238 (+3). Next trigger: tick 210 (100-tick mark from expansion).
```

---

## This cycle (Cycle 238) self-test

| Step | Action | Result |
|------|--------|--------|
| G0 | Trigger condition | CONCENTRATION_TICK 110 ✅ |
| G1 | `--generate 5` | 5 candidates; 3 passed WF ✅ |
| G2 | WF validation | gen_Donchian_RF: sharpe=1.01, mdd=16.3% (WF 3/5) ✅ |
| G3 | Pool expansion | 15 → 18 strategies in strategies.py ✅ |
| G4 | `--prune` | 0 killed; all 15 KEEP ✅ |
| G5 | Log | concentration_log.jsonl POOL_EXPANSION entry added ✅ |

**New strategies registered**:
1. `gen_Donchian_RF_5e649e` — Donchian + RegimeFilter — WF 3/5, sharpe=1.01, mdd=16.3%
2. `gen_Donchian_RSI_d3d59e` — Donchian + RSIFilter — WF 3/5, sharpe=0.77, mdd=17.1%
3. `gen_DualMA_RF_eda1cb` — DualMA + RegimeFilter — WF 4/5 (full-backtest mdd=48.6%; acceptable at WF level)

---

## Kill conditions for this SOP

This SOP's protocol is healthy if:
- Pool size stays ≥ 10 (after prune)
- At least 1 new strategy passes per 10 candidates tested
- G1+G4 cycle completes in < 30 seconds (synthetic) / < 5 min (yfinance)
- concentration_log.jsonl captures POOL_EXPANSION events

This SOP needs revision (L3) if:
- Pass rate < 10% across 3 consecutive generation runs
- All generated strategies are killed within 50 ticks
- Pool shrinks below 5 despite repeated generation

---

## Twitter thread (Domain 1 — Trading as a living system)

**Tweet 1/11** (hook):
108 ticks. 15 strategies registered. 1 active.

The hardest part of a trading system isn't the strategy.
It's keeping the strategy pool ALIVE.

A dead pool looks like this: 108 ticks / 1 signaling strategy.
Here's the lifecycle protocol. 🧵

**Tweet 2/11**: Most trading systems are built, backtested, deployed. Then forgotten. The market changes. The system doesn't. Signal decays. Fix: treat strategy pool as living organism, not static file.

**Tweet 3/11**: A living strategy pool has 4 states: Candidate (generated, unvalidated) → Paper (validated, observing) → Active (signaling positions) → Dead (killed by kill conditions). No strategy stays Active forever.

**Tweet 4/11**: The continuous loop: Generate → Walk-forward validate → Paper trade → Monitor → Kill → Generate. Stop the loop = the pool dies. The loop has no completion condition. That IS the design.

**Tweet 5/11**: Walk-forward validation gate: 5 windows, each must have Sharpe>0.5 and MDD<25%. Pass ≥3/5 windows → enter paper trade pool. Fail → logged, discarded. Rationale: robust strategies survive across time, not one backtest period.

**Tweet 6/11**: Kill conditions (the immune system): MDD>10% → kill immediately. WR<35% (≥5 trades) → kill. PF<0.85 (≥5 trades) → kill. A killed strategy is removed from the pool. A pruned pool is a healthy pool.

**Tweet 7/11**: The concentration trigger: When 1 strategy is active >100 consecutive ticks, run a generation cycle. Not because the strategy is bad. Because concentration = fragility. If it flips, you need backup. Diversity is resilience infrastructure.

**Tweet 8/11**: This cycle's G1 output: 5 candidates / 3 passed WF. New pool: 18 (was 15). Best: Donchian + RegimeFilter — Sharpe=1.01, MDD=16.3% across 3/5 windows. Not exciting. Reliable.

**Tweet 9/11**: The synthetic fallback: When network is down, generator uses geometric random walk (seed=42). Tests structural robustness, not BTC-specific curve-fitting. Passes both real and synthetic = more likely to generalize.

**Tweet 10/11**: Pool health checklist (monthly): □ ≥10 registered □ ≥3 base classes □ ≥1 RF/RSI □ 0 consecutive kills □ last G1 run <30 days ago. Any box unchecked: run G1+G4 immediately.

**Tweet 11/11**: The insight: Building a strategy is easy. Maintaining a living strategy pool — where signals evolve, underperformers die, new candidates continuously enter — is what separates a trader from a trading system. The loop is the strategy. 🔁 SOP #74

---

*Posting queue: Aug 30, 2026*
*Series: SOP #01–#74 COMPLETE*
