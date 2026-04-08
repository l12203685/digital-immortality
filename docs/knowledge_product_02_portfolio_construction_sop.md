# Knowledge Product #02 — Portfolio Construction SOP
> **Source MDs:** MD-100 (recursive pairwise Calmar optimisation), MD-52 (投組最佳化=遞迴兩兩最高風暴比), MD-53 (策略分類=多空×類型二維最細分), MD-54 (跨Session留倉=需獨立Edge), MD-02 (多方案並列), MD-13 (edge_ratio=MFE/MAE×√N), MD-157 (策略=第一性原理追求)
>
> **Prerequisite:** Knowledge Product #01 (Strategy Development SOP). Each strategy entering the portfolio must have passed Steps 1–5 of that SOP individually.

---

## What This SOP Produces

A ranked, weighted portfolio of strategies with:
1. A Calmar-optimised allocation vector (not equal weight)
2. A correlation matrix used to reject redundant strategies
3. A regime routing table (which strategies run in which market state)
4. Kill conditions at the portfolio level (distinct from per-strategy kill conditions)

The SOP does **not** produce alpha. Alpha must already exist in each strategy before portfolio construction begins.

---

## Step 1 — Classify Each Strategy on the 2×2 Grid

Before combining anything, sort strategies by:

| | **Trend-following** | **Mean-reverting** |
|---|---|---|
| **Long-biased** | Trend-Long | MR-Long |
| **Short-biased** | Trend-Short | MR-Short |

**Why this matters (MD-53):** Strategies in the same cell are structurally redundant — they exploit the same market behaviour. Combining two Trend-Long strategies does not diversify risk; it amplifies it. Your portfolio must span at least 2 cells, ideally all 4.

**Rule:** Before adding any strategy to the candidate list, assign it a cell. If it lands in an occupied cell, you need a strong reason (e.g., different instrument, different timeframe) to keep both candidates in contention.

---

## Step 2 — Compute Pairwise Calmar Ratios

For every pair of strategies (A, B) in your candidate list, compute:

```
Combined_Calmar(A, B) = CAGR(A+B, equal weight) / Max_Drawdown(A+B, equal weight)
```

Run this on your OOS data (not IS). Equal weight is the starting hypothesis — you are measuring structural fit, not optimising weights yet.

**Ranking rule (MD-100):** Sort all pairs by Combined_Calmar descending. Pick the top pair. This becomes your seed portfolio.

**Why Calmar (not Sharpe)?** Calmar penalises peak-to-trough drawdown, which is the metric that terminates real accounts. Sharpe rewards volatility averaging, which can mask correlated drawdowns. (MD-93: system design = positive-sum game with external capital — Calmar communicates survivability to allocators.)

---

## Step 3 — Recursive Greedy Addition

Starting from your seed pair, add strategies one at a time using the greedy criterion:

```
For each candidate strategy C:
  temp_portfolio = current_portfolio + C (equal weight for now)
  score(C) = Combined_Calmar(temp_portfolio)

Add the C with the highest score(C) IF score(C) > current_portfolio Calmar.
```

Stop when no candidate improves portfolio Calmar. This is the **structural composition** decision.

**Hard limits:**
- Max 6–8 strategies. Beyond this, per-strategy monitoring bandwidth is exceeded (MD-107: strategy count ≤ bandwidth capacity).
- Minimum 2 cells covered on the 2×2 grid.
- No two strategies with rolling 30-day return correlation > 0.70 (they are effectively one strategy under regime stress).

---

## Step 4 — Optimise Weights via Calmar Frontier

Once the strategy set is fixed, optimise allocation weights. The objective function:

```
Maximise: CAGR(w) / MaxDrawdown(w)
Subject to: Σwᵢ = 1, wᵢ ≥ 0.05 (minimum 5% floor to prevent zero-weight exclusions)
```

Use grid search over 5% increments, not continuous optimisation. Continuous optimisation on ≤8 strategies with ≤5% granularity has 19^7 ≈ 893M combinations for 7 strategies — use random sampling (10,000 draws) as an approximation.

**Overfitting guard:** If the optimal weights differ from equal weight by more than 3× on any single strategy, the result is likely data-fitting, not structural advantage. Cap at 3× equal weight (e.g., equal=12.5% → max allocation 37.5%).

---

## Step 5 — Regime Routing Table

Strategies do not run at full weight in all regimes. Build a routing table:

| Regime | Active Strategies | Weight Adjustment |
|--------|------------------|-------------------|
| Trending (ATR > threshold) | Trend-Long, Trend-Short | ×1.0 |
| Mean-reverting (ATR < threshold) | MR-Long, MR-Short | ×1.0 |
| Mixed / transition | All | ×0.5 (half allocation) |
| High-vol shock (ATR > 2× 20-day avg) | None | Flat — no new positions |

**Rule (MD-54):** Cross-session carry positions require independent edge verification. A strategy that generates edge in trending regime does not automatically carry that edge overnight during a regime shift. When regime is ambiguous, reduce, do not hold.

Calibrate ATR thresholds from your OOS data, not IS. Record the threshold values in a config file — they are not constants, they are regime-specific parameters to be reviewed quarterly.

---

## Step 6 — Portfolio-Level Kill Conditions

Distinct from per-strategy kill conditions. If **any** of these trigger, halt all strategies simultaneously:

| Metric | Kill Threshold |
|--------|---------------|
| Portfolio MDD (peak-to-trough) | > 15% of total capital |
| 5-day rolling loss | > 6% of capital |
| 3 strategies simultaneously in individual kill zone | Any 3 of N hit their own MDD limit |
| Drawdown rate > 1% per day for 5 consecutive days | Sustained bleed, not spike |

After a portfolio kill: wait minimum 5 trading days before restarting any strategy. Use the pause to review correlation matrix — correlated drawdown implies the 2×2 cell classification or the routing table has a structural flaw.

---

## Failure Modes

### Failure Mode 1: Adding strategies until Calmar appears good
Greedy addition can produce a statistically significant improvement on a limited OOS window by chance. A real test: hold out the last 20% of your OOS data entirely (do not use it in Step 3). After finalising the portfolio, apply it to this holdout. If Calmar degrades by > 30%, the portfolio is overfit to the OOS window.

### Failure Mode 2: Treating correlation as stable
Rolling 30-day correlation is measured in normal regimes. In tail events (VIX > 35, crypto spot-perp funding > 3%), correlation between all trend-following strategies collapses to ~1.0. Your portfolio's "diversification" disappears exactly when you need it. The high-vol routing row in Step 5 is the structural fix — not a hedge, a halt.

### Failure Mode 3: Ignoring transaction costs across the portfolio
Each strategy has its own cost structure from SOP #01 Step 1. Portfolio rebalancing adds a second layer: when you adjust weights after regime change, you pay slippage on all positions simultaneously. Estimate quarterly rebalancing cost as a drag on CAGR before committing to any weight optimisation. If drag > 20bps/quarter, use wider rebalancing bands (only rebalance when drift exceeds 5% from target weight).

### Failure Mode 4: Starting with more than 4 strategies
More strategies = more parameters in the routing table = more places to hide overfitting. Start with 2–3. Earn the right to add complexity by surviving a full out-of-sample calendar quarter. (MD-117: complexity = disguised insufficient edge)

---

## Self-Test: Apply This to Your Portfolio

**Scenario:** You have 4 strategies that each passed SOP #01:
- Strategy A: Trend-Long, CAGR=18%, MDD=8% (Calmar=2.25)
- Strategy B: Trend-Short, CAGR=12%, MDD=6% (Calmar=2.0)
- Strategy C: MR-Long, CAGR=14%, MDD=10% (Calmar=1.4)
- Strategy D: Trend-Long (different instrument), CAGR=22%, MDD=15% (Calmar=1.47)

1. Plot all 4 on the 2×2 grid. Which cell is over-represented? *(Step 1)*
2. Compute pairwise Calmar for A+B, A+C, A+D using the equal-weight formula. Assume combining A+B gives CAGR=15% MDD=4%, A+C gives CAGR=16% MDD=9%, A+D gives CAGR=20% MDD=12%. Which is the seed pair? *(Step 2)*
3. D has rolling 30-day correlation of 0.82 with A. What is your decision and why? *(Step 3 hard limits)*
4. Your routing table shows that in a high-vol shock regime, you go flat. A colleague argues "D has higher CAGR so we should keep it running." What is the structural error in this argument? *(Step 5 + MD-117)*

**Expected answers:**
- Q1: Trend-Long has A and D (2 occupants). The cell is over-represented.
- Q2: A+B Calmar = 15/4 = 3.75. A+C = 16/9 = 1.78. A+D = 20/12 = 1.67. Seed pair = A+B.
- Q3: Reject D from the portfolio. Correlation 0.82 > 0.70 limit. A+D is structurally one strategy during stress. The higher CAGR does not compensate for the diversification failure.
- Q4: CAGR is a normal-regime metric. In high-vol shock, the assumption underlying D's edge (trending behaviour) breaks down. Running it violates the regime-edge independence principle (MD-54). The CAGR argument is irrelevant — it is measured on different market conditions than the one you are currently in.

---

*End of Knowledge Product #02*
*Next product candidate: Execution & Sizing Real-Time Checklist (MD-13 edge_ratio + MD-28~30 position sizing operationalised as a live decision checklist)*
