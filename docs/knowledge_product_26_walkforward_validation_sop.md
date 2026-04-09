# SOP #26: Walk-Forward Validation Protocol

> "A backtest that fits the past is not evidence. A backtest that survives the future is."

**Core Principle:** Out-of-sample performance is the only real evidence a strategy has edge. Walk-forward validation operationalizes this — every parameter choice must survive unseen data before deployment.

**Backing MDs:** MD-97 (structure before parameters), MD-98 (OOS Sharpe ≥60% IS), MD-143 (WFA ≥6 windows, ≥60% win-rate), MD-107 (escalate to meta-strategy if object-level stuck), MD-108 (regime decomposition), MD-26 (90-trade minimum before regime confirmation)

---

## Decision Framework (5 Gates)

### G0 — Structure Lock Before Optimization
**Before touching parameters, write the strategy in one sentence:**
> "This strategy profits by [mechanism] in [regime] using [signal] with [exit]."

If you cannot write this sentence → **STOP. No optimization permitted.**

Rule: Structure is constant. Parameters are variables. Never optimize structure. (MD-97)

### G1 — In-Sample / Out-of-Sample Split
- Minimum IS period: 3× the strategy's average holding period × 100 trades
- OOS = last 30% of data, never touched during development
- Walk-forward windows: split IS into rolling windows
  - Minimum: **6 windows** (MD-143)
  - Each window = optimize on IS slice → test on next OOS slice → record

**Kill condition:** Fewer than 6 windows available → extend data or abandon strategy.

### G2 — OOS Sharpe Gate
For each walk-forward window:
- OOS Sharpe ≥ **60% of IS Sharpe** → PASS (MD-98)
- OOS Sharpe < 60% IS Sharpe → FAIL window

**Required:** ≥60% of windows must PASS.
- 4/6 windows pass = 67% → CONDITIONAL GO (reduce size 50%)
- 3/6 windows pass = 50% → FAIL → re-examine structure (not parameters)

### G3 — Regime Decomposition
Break OOS performance by regime (trending / mean-reverting / event):
- Target-regime OOS Sharpe ≥ 1.0 → PASS (MD-108)
- Non-target regime: document expected degradation
- If strategy only works in 1 of 3 regimes → portfolio needs regime filter (MD-25)

Minimum trades per regime slice: **90** before confirming regime attribution (MD-26)

### G4 — Parameter Stability Check
Plot Sharpe vs. parameter sweep ±30% from optimized value:
- **Stable:** Sharpe degrades <20% across ±30% range → PASS
- **Fragile:** Sharpe cliff-edge at optimized value → curve-fit, FAIL

A strategy that only works at exact parameters has no structural edge. (MD-97 corollary)

### G5 — Forward Commitment
Write the deployment contract before going live:
```
Strategy: [name]
Deployed parameters: [list]
Kill conditions: OOS MDD>[X]%, WR<[Y]% after [N] trades
Review date: [90 days from deployment]
```
File this before first live tick. (MD-96: kill conditions written before entry)

---

## Self-Test Scenario

**Setup:** DualMA(10,30) on BTC/USDT daily. IS = 2020–2023. OOS = 2024.
Walk-forward: 6 windows of 6 months IS + 2 months OOS each.

**Results:**
- Windows 1–4: OOS Sharpe = 0.82, 0.71, 0.94, 0.68 (all ≥60% of IS avg 1.1 → PASS)
- Window 5: OOS Sharpe = 0.41 (37% — FAIL)
- Window 6: OOS Sharpe = 0.78 (PASS)
- Pass rate: 5/6 = 83% → **CONDITIONAL GO**

G3: Trending regime Sharpe = 1.3 → PASS. Ranging regime = 0.2 → expected, handled by regime gate.
G4: ±30% parameter sweep shows <15% Sharpe degradation → stable.

**Decision: GO at 75% size. Kill: MDD>10%, WR<35% after 20 trades.**

---

## Kill Conditions

| Condition | Action |
|-----------|--------|
| OOS Sharpe < 60% IS in >40% windows | FAIL — re-examine structure |
| Target-regime Sharpe < 1.0 | FAIL — wrong regime, not wrong parameters |
| Parameter cliff-edge ±10% | FAIL — curve-fit |
| Live MDD > deployed kill level | Kill immediately per G5 contract |

---

## Series Connection

- SOP #01: Strategy Development (structure before parameters ← this SOP validates that)
- SOP #04: Strategy Kill Decision Tree (kill conditions ← G5 output feeds this)
- SOP #15: Backtest Deception Protocol (IS/OOS split ← G1 details)
- SOP #07: Regime Detection (regime gate ← G3 output)
