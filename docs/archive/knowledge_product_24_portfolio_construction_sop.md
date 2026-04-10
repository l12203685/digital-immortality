# SOP #24 — Portfolio Construction: Building a Strategy Portfolio, Not Just a Strategy

**Series:** Edward Lin's Trading System SOPs  
**Backing DNA:** MD-35, MD-38, MD-85, MD-87, MD-120, MD-33, MD-28, MD-79  
**Domain:** Trading System Design

---

## The Core Problem

Most traders build one good strategy and run it at 100% allocation.  
That's not a portfolio — that's a single bet with a leash.

When the strategy enters drawdown, you have two choices: endure it (emotionally costly) or stop it (permanently miss recovery).  
Both are worse than the alternative: a portfolio where drawdown in one strategy is offset by flat or positive performance in another.

**MD-120:** True diversification = different architectures, not the same strategy on different instruments.  
**MD-85:** Portfolio construction = greedy complementarity algorithm (add what reduces variance most, not what performs best in isolation).

---

## The 5-Gate Portfolio Construction SOP

### G0 — Define Strategy Taxonomy First

Before combining strategies, classify each one along two axes:

| Axis | Options |
|------|---------|
| **Direction bias** | Long-only / Short-only / Neutral |
| **Regime dependency** | Trending / Ranging / Neutral |

**MD-38:** Portfolio architecture must be layered:
- Layer 1: Core position (index-based, macro exposure)
- Layer 2: Active alpha strategies (systematic, tested)
- Layer 3: Tactical overlays (event-driven, short-duration)

Do not mix layers when evaluating performance. A Layer 3 overlay failing doesn't mean Layer 2 is broken.

---

### G1 — Pool Audit: Long/Short Balance

Run the pool audit before allocating capital.

**MD-35:** Strategy pool must have ≥30% short-capable strategies.  
Why: In a sustained downtrend, long-only strategies all draw down simultaneously. Short-capable strategies provide non-correlated returns.

**Audit format:**
```
Total strategies: N
Long-only: X (X/N %)
Short-capable: Y (Y/N %)
Neutral: Z (Z/N %)

Pass criteria: Y/N ≥ 30%
```

If pool fails audit: do NOT add more long-only strategies. Develop or import short-capable strategies first.

---

### G2 — Correlation Filter (Greedy Complementarity)

When selecting strategies to combine, use correlation as the primary filter — not Sharpe ratio.

**MD-85:** Portfolio construction = complementarity, not performance stacking.

**Process:**
1. Run all candidate strategies on the same historical period
2. Compute pairwise equity curve correlation
3. Add strategies in order of lowest correlation to existing portfolio
4. Stop when adding a new strategy increases portfolio correlation (diminishing returns)

**Hard rule:** If two strategies have equity curve correlation > 0.7, they are the same bet with different labels. Keep only the better one.

---

### G3 — Regime-Conditional Allocation

Static allocation (strategy A = 50%, strategy B = 50% always) ignores that strategies have regime-dependent performance.

**MD-25:** ATR(14) vs 30-day MA determines regime state.  
**MD-75:** Equity curve 3-state trigger controls leverage, not just individual strategy sizing.

**Dynamic allocation logic:**
```
Trending regime (ATR > MA):
  → Overweight trend-following strategies (+20% allocation)
  → Underweight mean-reversion strategies (-20% allocation)

Ranging regime (ATR < MA):
  → Overweight mean-reversion strategies (+20% allocation)
  → Underweight trend-following strategies (-20% allocation)

Transition / Uncertain:
  → Equal-weight all strategies
  → Reduce total leverage by 20%
```

Rebalance regime allocation at most once per week. Do not react to single-day ATR moves.

---

### G4 — Anti-Martingale Sizing (No Double-Down on Losers)

**MD-87:** Martingale = self-negating premise. It assumes the next trade is more likely to win after a loss — which is only true if the losing strategy's edge is intact and the loss is random variance.

**Portfolio rule:**
- Never increase allocation to a strategy because it is in drawdown
- Reduce allocation only when drawdown exceeds the pre-written kill threshold (from SOP #04)
- Increase allocation only when equity curve returns to Normal state AND new trades are confirming the edge

Inverse corollary: **MD-28:** Scale up only on confirmed edge. If you can't articulate *why* the edge is intact, do not scale.

---

### G5 — Position-Level Tail Minimization

Individual position tails (outlier position sizes) are the hidden risk in any portfolio.

**MD-33:** Minimize tail positions. Maximum position size for any single trade = 2× average position size.

**Implementation:**
```
avg_pos = mean(position_sizes over last 90 trades)
max_pos = 2 × avg_pos
Hard stop: reject any signal that would create position > max_pos
```

This rule prevents "conviction" from becoming "concentration." Conviction belongs in strategy selection; sizing should be mechanical.

---

## Self-Test: Apply the SOP

**Scenario:** You run 3 strategies: DualMA (long-only, trending), RSI Mean-Reversion (neutral, ranging), Breakout (long-only, trending).

- Pool audit: 0/3 short-capable → **FAIL G1**. Must add short-capable strategy before going live.
- Correlation: DualMA and Breakout likely correlated (both trend-following, long-only) → **FAIL G2**. Run correlation check; likely need to remove one.
- Regime allocation: Both trending strategies draw down simultaneously in ranging markets → concentrated regime risk.

**Decision:** Do not allocate capital to this portfolio in current form. Fix G1 first (add short-capable strategy), then re-run G2.

---

## Summary

| Gate | Check | Pass Criteria |
|------|-------|---------------|
| G0 | Taxonomy classified | All strategies labeled by direction + regime |
| G1 | Pool audit | ≥30% short-capable |
| G2 | Correlation filter | No pair > 0.7 correlation |
| G3 | Regime allocation | Dynamic weights by ATR state |
| G4 | Anti-martingale | No size increase during drawdown |
| G5 | Tail minimization | No position > 2× average |

**Bottom line:** The edge is in the strategy. The survival is in the portfolio structure.
