# Twitter Thread — SOP #74: Strategy Pool Lifecycle Protocol
**Posting date**: Aug 30, 2026
**Domain**: 1 — 經濟自給 (Trading / Economic Self-Sufficiency)
**Source**: `docs/knowledge_product_75_strategy_pool_lifecycle_sop.md`

---

**Tweet 1/11** (HOOK — copy this first):
```
108 ticks. 15 strategies registered. 1 active.

The hardest part of a trading system isn't the strategy.
It's keeping the strategy pool ALIVE.

Here's the lifecycle protocol. 🧵
```

**Tweet 2/11**:
```
Most trading systems are built, backtested, and deployed.

Then forgotten.

The market changes. The system doesn't. Signal decays.

The fix: treat the strategy pool as a living organism, not a static file.
```

**Tweet 3/11**:
```
A living strategy pool has 4 states:

1. Candidate (generated, not yet validated)
2. Paper (validated, observing real signals)
3. Active (signaling live positions)
4. Dead (killed by kill conditions)

No strategy stays in state 3 forever.
```

**Tweet 4/11**:
```
The continuous loop:

Generate → Walk-forward validate → Paper trade → Monitor → Kill → Generate

Stop the loop = the pool dies.

The loop doesn't have a completion condition. That IS the design.
```

**Tweet 5/11**:
```
Walk-forward validation (the quality gate):

5 windows. Each must have:
- Sharpe > 0.5
- MDD < 25%

Pass ≥3/5 windows → enter paper trade pool.
Fail → logged, discarded.

Robust strategies survive across time, not just one period.
```

**Tweet 6/11**:
```
Kill conditions (the immune system):

- MDD > 10% → kill immediately
- Win rate < 35% (≥5 trades) → kill
- Profit factor < 0.85 (≥5 trades) → kill

A killed strategy is removed from the pool.
A pruned pool is a healthy pool.
```

**Tweet 7/11**:
```
The concentration trigger:

When 1 strategy is active for >100 consecutive ticks, run a generation cycle.

Not because the strategy is bad.
Because concentration = fragility.

If it flips, you need backup. Diversity is resilience infrastructure.
```

**Tweet 8/11**:
```
This cycle's G1 output:

5 candidates generated.
3 passed walk-forward validation.
2 failed.

New pool: 18 strategies (was 15).
Best: Donchian + RegimeFilter — Sharpe=1.01, MDD=16.3%.

Not exciting. Reliable.
```

**Tweet 9/11**:
```
The synthetic data fallback:

When network is down, the generator uses a geometric random walk (seed=42).

Tests structural robustness — not BTC-specific curve-fitting.

A strategy that passes both real and synthetic is more likely to generalize.
```

**Tweet 10/11**:
```
Pool health checklist (monthly):

□ ≥10 strategies registered
□ ≥3 different base classes
□ ≥1 with RegimeFilter, ≥1 with RSIFilter
□ 0 consecutive kills
□ Last generation run < 30 days ago

Any box unchecked: run G1+G4 immediately.
```

**Tweet 11/11** (CTA):
```
The insight:

Building a strategy is easy.

Maintaining a living strategy pool — where signals evolve,
underperformers die, and new candidates continuously enter —
is what separates a trader from a trading system.

The loop is the strategy.

🔁 SOP #74 — Strategy Pool Lifecycle Protocol
```

---

## Post-publish checklist
- [ ] All 11 tweets posted in thread
- [ ] Note time posted in Signal Log (posting_queue.md)
- [ ] After 48h: run `python platform/daily_posting_helper.py --signal replies=N saves=N dms=N`
- [ ] If ≥10 DMs: open `docs/gumroad_listing_checklist.md`
