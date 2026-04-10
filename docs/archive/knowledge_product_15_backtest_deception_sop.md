# SOP #15 — The Backtest Deception Protocol: Why Your Backtest Lies and How to Fix It

> Source MDs: MD-107 (公開指標=邊際edge趨零), MD-143 (WFA全樣本悖論=分段最佳化優於整體), MD-113 (無參數≠免疫過度最佳化), MD-97 (策略=先抽象結構再固定參數), MD-108 (年度風暴比=跨年Regime偵測器)
> One-claim: "Your backtest looks great. That's the problem."

---

## Why This SOP Exists

A backtest that looks too good is a warning signal, not a confirmation. The most dangerous state in strategy development is a beautiful equity curve produced by overfitting. You won't know at deployment — you'll know three months later when drawdown exceeds the maximum you thought possible.

MD-107: Once a signal is publicly known, its edge approaches zero. The backtest was built on historical data that already priced in what others now know.

MD-143: Optimizing over the full sample creates a paradox — the best parameters for the whole period are rarely the best parameters for any sub-period. WFA (Walk-Forward Analysis) on segments beats whole-sample optimization.

---

## Gate Sequence (4 gates)

### G0 — Structure Before Parameters
Before touching any parameter: define what your strategy is doing at the level of market microstructure.

Requirements:
1. Write one sentence: "This strategy profits because ___" (fill in a market mechanism, not a pattern)
2. The mechanism must work in at least 2 of 3 regimes (trending, mean-reverting, mixed)
3. Failure if the answer references a specific indicator — indicators are implementation, not mechanism

**Why (MD-97):** Parameter-first development finds local optima. Structure-first development finds transferable edge.

### G1 — Out-of-Sample Proof
All performance claims must come from data the strategy never touched during development.

Requirements:
1. Reserve ≥30% of historical data as a locked OOS holdout (set aside before any optimization begins)
2. Run optimization on IS data only
3. OOS Sharpe must be ≥60% of IS Sharpe — if it degrades more than 40%, the strategy is overfit (MD-98)
4. OOS max drawdown must be ≤ 1.5× IS max drawdown

Failure mode: running optimization, checking OOS, adjusting, repeating. This makes OOS a second IS dataset. Lock it before you start.

### G2 — Walk-Forward Validation
Segment the IS data into rolling windows. Optimize on each window. Test forward. Aggregate results.

Requirements:
1. Minimum 6 WFA windows (each window: optimize → test next period → move window forward)
2. Winning windows ÷ total windows ≥ 60%
3. Aggregate WFA Sharpe ≥ 0.7

**Why (MD-143):** A strategy robust across multiple time periods has structural edge. A strategy robust only on the full sample is a curve-fit.

### G3 — Regime Decomposition
Split the backtest by regime. Verify the strategy is profitable in its target regime(s).

Requirements:
1. Identify regime for each period (trending / mean-reverting / mixed) using ADX + volatility ratio
2. Calculate Sharpe separately per regime
3. Target regime Sharpe ≥ 1.0
4. Non-target regime: acceptable if Sharpe ≥ 0 (flat is fine, negative is not)

**Why (MD-108):** Annual Sharpe can mask regime-specific failure. A strategy with Sharpe 0.8 on trending + Sharpe -0.3 on mean-reverting will destroy capital in the wrong environment.

---

## Failure Modes

| Signal | Diagnosis | Action |
|--------|-----------|--------|
| IS Sharpe >> OOS Sharpe | Overfit parameters | Return to G0, simplify structure |
| WFA win rate < 50% | No structural edge | Abandon, start new hypothesis |
| Great trending, terrible mean-reverting | Regime mismatch | Accept narrow deployment scope or hedge |
| "No parameters" claim | MD-113: complexity hides in logic | Count decision branches, not parameter counts |

---

## Self-Test (answer before deploying)

1. What market mechanism does your strategy exploit? (Must answer without naming an indicator)
2. What is your OOS Sharpe vs IS Sharpe ratio?
3. What percentage of WFA windows were profitable?
4. What is your strategy's Sharpe in a mean-reverting regime?

If any answer is "I don't know" → do not deploy.

---

## One-Line Summary

The test of a backtest is not how good it looks. It is how much it degrades on data it has never seen.
