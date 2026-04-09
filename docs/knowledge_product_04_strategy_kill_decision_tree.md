# SOP #04 — Strategy Failure & Kill Decision Tree

> Backing MDs: MD-95 (策略管理=先定失效再管理), MD-96 (投組調整=了解特性非情緒驅動),
> MD-13 (edge_ratio≥1.5), MD-157 (失效=知道輸贏條件), MD-133 (風控前置),
> MD-30 (槓桿=歷史R/R不用近30天), MD-66 (策略失效Loop)

---

## Purpose

Prevent the two failure modes that destroy accounts:
1. **Keeping a dead strategy** — emotional attachment, sunk-cost
2. **Killing a live strategy** — noise-triggered, recency bias

The tree forces a structural verdict before any position change.

---

## Node 0 — Trigger Conditions

Run this decision tree when ANY of the following occur:

| Trigger | Threshold |
|---------|-----------|
| Consecutive losing trades | ≥ 5 in live |
| Drawdown from equity peak | ≥ 15% |
| edge_ratio drop (trailing 30 trades) | < 1.2 (was ≥ 1.5) |
| OOS Calmar < 0.3 (trailing 90 days) | below seed threshold |
| Signal frequency collapse | < 30% of historical avg |

If no trigger: **DO NOT RUN this tree.** Resist urge to "review" strategy during normal variance.

---

## Node 1 — Sample Size Check

**Q: How many live trades does this strategy have?**

- **< 30 trades** → SUSPEND JUDGEMENT. Log observation. Come back at 30.
  - *MD-29: short-term sample = variance not technique*
  - Action: reduce position to 25% until sample = 30
- **30–100 trades** → proceed to Node 2 with caution flag
- **> 100 trades** → proceed to Node 2 with full confidence

---

## Node 2 — Regime Match Check

**Q: Has the market regime changed since strategy was built?**

Check:
1. ATR now vs ATR at backtest period (>2× = high-vol regime shift)
2. Trend/MR structure: is this strategy type currently favoured? (MD-53)
3. Correlation to current dominant factor (momentum, carry, mean-rev)

| Verdict | Meaning | Action |
|---------|---------|--------|
| Regime unchanged | Strategy should still work | Proceed to Node 3 |
| Regime shifted temporarily | Pause, do not kill | Reduce to 25%, set calendar trigger 30 days |
| Regime shifted structurally | Strategy premise broken | Proceed to Node 4 (Kill Assessment) |

---

## Node 3 — Edge Integrity Check

**Q: Is the core edge still present in the data?**

Run on most recent 30 live trades:

```
edge_ratio = mean(MFE) / mean(MAE) × sqrt(N)
```

| edge_ratio | Interpretation | Action |
|------------|----------------|--------|
| ≥ 1.5 | Edge intact, results = variance | DO NOT KILL. Log and monitor. |
| 1.2 – 1.5 | Edge degrading | Reduce leverage 50% (MD-30), set 20-trade review |
| < 1.2 | Edge failing | Proceed to Node 4 |

Also check: **Is the L/S balance distorted?** (MD-29)
- If only Long or only Short failing → regime routing issue, not strategy failure
- Fix: adjust regime filter, not kill the strategy

---

## Node 4 — Kill Assessment (Structural Failure Criteria)

**Q: Has the underlying premise been falsified?**

The premise was defined at strategy creation (from SOP #01 Gate 1). Check each:

| Premise Component | How to Test | Falsified If... |
|-------------------|-------------|-----------------|
| Signal captures a real inefficiency | Re-run backtest on last 12 months of OOS data | Calmar < 0.3 |
| Signal is not crowded out | Check if pattern still has positive MFE in IS period | MFE trend declining for 6+ months |
| Execution friction is manageable | Calculate actual slippage vs assumed | Real slippage > 2× modelled |
| Market structure still supports it | Check bid-ask spread, volume trends | Liquidity < 30% of backtest period |

**Count falsified components:**
- **0–1 falsified**: Not a kill. Edge degraded but not dead → reduce size, add filter, retest
- **2–3 falsified**: High-probability kill → proceed to Node 5
- **4 falsified**: Kill immediately, no debate

---

## Node 5 — Pre-Kill Sanity Check (Anti-Capitulation Guard)

Before pulling the trigger, answer these three questions:

1. **Would I build this strategy today given what I know?**
   - YES → Do not kill. The loss is variance. Stick with SOP #03.
   - NO → proceed

2. **Is there a specific, testable fix?** (new filter, regime gate, parameter adjustment)
   - YES → Implement fix first. Give it 30 trades. Kill only if fix fails.
   - NO → proceed

3. **Am I killing because of a bad week, or because the premise is falsified?** (MD-96)
   - Bad week → DO NOT kill. Reset position size only.
   - Premise falsified → Kill confirmed.

---

## Node 6 — Kill Protocol

If kill is confirmed:

1. **Close all positions** in this strategy immediately
2. **Remove from live portfolio** — do not paper-trade "just to watch"
3. **Write post-mortem** (3 sentences): what premise failed, what signal was, what the error was at build time
4. **Update portfolio**: re-run greedy addition (SOP #02) with strategy removed
5. **Archive don't delete**: move to `strategies/archived/` with post-mortem note
6. **Check replacement need**: if portfolio now < 3 uncorrelated strategies, initiate SOP #01 immediately

---

## Node 7 — Resurrection Criteria (Optional)

A killed strategy may be revived IF:

- Market regime returns to original profile (ATR, trend structure)
- Strategy shows positive edge_ratio ≥ 1.5 on fresh 6-month OOS backtest
- No parameter changes allowed — resurrect exact original parameters
- Start at 25% size, graduate to full size after 30 live trades pass Node 3

---

## Quick Reference Card

```
Trigger → Node 1 (sample?) → Node 2 (regime?) → Node 3 (edge?)
                                      ↓                    ↓
                               Node 4 (premise?)     [No kill]
                                      ↓
                               Node 5 (sanity?)
                                      ↓
                               Node 6 (kill protocol)
```

---

## Self-Test Scenario

**Situation**: DualMA strategy, 45 live trades. Last 12 trades = -8 losing. Drawdown 12%. ATR now 1.4× backtest average.

- Node 1: 45 trades → proceed
- Node 2: ATR 1.4× (not 2×), same trend regime → unchanged
- Node 3: edge_ratio on last 30 = 1.35 → degrading. Reduce leverage 50%, set 20-trade review
- **Verdict: DO NOT KILL. Reduce size. Monitor.**

---

*SOP trilogy extended: #01 Strategy Dev → #02 Portfolio → #03 Execution → #04 Kill Decision*
