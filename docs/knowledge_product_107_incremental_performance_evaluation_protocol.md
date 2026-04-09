# SOP #107 — Incremental Performance Evaluation Protocol

> Version: 1.0 | Created: 2026-04-10T UTC | Cycle: 279
> Source: MD-364 (201812 錦標賽分析) — 增量勝率>總勝率

---

## Purpose

Evaluate decisions, strategies, and capabilities using **marginal/incremental metrics** rather than aggregate totals. Aggregate metrics mask recent decay. Marginal metrics reveal current trajectory.

**Core principle**: The last N data points tell you more about current ability than all N total data points averaged together.

---

## When to Apply

- Evaluating trading strategy performance (is it still working?)
- Comparing two candidates with different sample sizes
- Assessing your own skill improvement over time
- Reviewing any time-series metric (conversion rates, win rates, output quality)
- Any situation where "they've done X total" is being used as the deciding factor

---

## The Problem with Aggregate Metrics

**Scenario**: Player A — 70 games, 47% WR. Player B — 58 games, 50% WR.

Naive conclusion: A played more games, B has better WR.

**Incremental analysis**: A's last 12 games (compared to B's 58) → 4 wins / 12 games = **33% marginal WR**.

True conclusion: A is **declining**. B is likely more stable.

**Rule**: Aggregate WR is the average of all periods including the early learning curve. Incremental WR tells you what the person/strategy is doing **now**.

---

## G0 — Sample Size Gate

**Minimum viable N = 50 data points.**

- N < 50: Statistical noise. Do not draw conclusions. Wait or sample more.
- N 50–100: Use with caution. Add confidence intervals.
- N > 100: Incremental analysis is reliable.

**If comparing two entities with different N**: Weight towards the one with more data, but analyze marginals separately.

---

## G1 — Split Analysis

Split the data into two halves (or use a sliding window):

```
First half WR:  wins_1 / N_1
Second half WR: wins_2 / N_2
Marginal WR:    (total wins - first half wins) / (N - N_1)
```

**Interpretation**:
- Second half WR > First half WR → **Improving trend** ✅
- Second half WR < First half WR → **Declining trend** ⚠️
- Second half WR ≈ First half WR → **Stable** (good or bad depending on baseline)

---

## G2 — Trajectory Classification

| Trajectory | Condition | Action |
|------------|-----------|--------|
| IMPROVING | Marginal WR > Total WR + 5% | Invest more. Skill curve still ascending. |
| STABLE_HIGH | Total WR ≥ threshold, Marginal ≈ Total | Maintain. |
| STABLE_LOW | Total WR < threshold, Marginal ≈ Total | Diagnose root cause. May need method change. |
| DECLINING | Marginal WR < Total WR - 5% | Investigate. Possible overfit, fatigue, or changing environment. |
| NOISE | N < 50 | Insufficient data. Reserve judgement. |

---

## G3 — Root Cause for Declining Trajectory

When Marginal WR < Total WR significantly:

1. **Overfitting** — strategy/person optimized for early conditions that no longer hold
2. **Regime change** — environment changed, old approach no longer valid
3. **Fatigue/drift** — gradual decay in execution quality
4. **Sample contamination** — early data was lucky / selection bias

**Diagnostic**: Compare conditions in early period vs. recent period. If conditions changed → regime change. If conditions stable → personal drift or overfitting.

---

## G4 — Application to Trading Strategies

For `--paper-live` strategy evaluation:

```python
# Incremental PF calculation
recent_trades = last 20 trades
recent_gross_profit = sum(t.pnl for t in recent_trades if t.pnl > 0)
recent_gross_loss   = abs(sum(t.pnl for t in recent_trades if t.pnl < 0))
incremental_PF = recent_gross_profit / recent_gross_loss

# Compare vs total PF
if incremental_PF < kill_min_pf * 0.8:
    flag DECLINING_TRAJECTORY
```

Kill decisions should weight **incremental PF** alongside total PF. A strategy with total PF=1.5 but incremental PF=0.6 is degrading.

---

## G5 — Revenue Bridge

**Consulting application**: When evaluating a client's team member or strategy:

- Present the incremental analysis framework as a deliverable
- "Your aggregate metrics look fine, but the last 30 days show X% decline" → diagnostic value clients pay for
- Standard deliverable: **Performance Trajectory Report** ($197 async audit tier)

Teaching this framework = demonstrating an edge clients don't have (they optimize for total, not marginal).

---

## Self-Test

**Scenario**: A trading strategy has 200 total ticks, PF=1.4. Last 40 ticks: 8 wins, 12 losses, PF=0.67.

**G0**: N=200 ✅ (sufficient)
**G1**: Marginal PF=0.67 < Total PF=1.4 → large gap
**G2**: Trajectory=DECLINING ⚠️
**G3**: Check if market regime changed in last 40 ticks → if MIXED regime shifted to TRENDING and strategy is trend-following, that's regime change not strategy failure
**G4**: Apply kill_window to marginal PF; if incremental PF < 0.8 trigger review
**Decision label**: DECLINING_INVESTIGATE_REGIME

---

## Backing MDs

- MD-364: 增量勝率>總勝率 (2018-12 錦標賽分析)
- MD-352: 交易淨報酬=毛報酬-手續費-稅 (track real marginal cost)
- MD-101: 時間指數成本遞減=更高頻的小決策反而更可量化 (incremental beats aggregate)
