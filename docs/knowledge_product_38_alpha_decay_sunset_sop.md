# SOP #38 — Alpha Decay & Strategy Sunset Protocol

> DNA Anchors: MD-26 (Rolling OOS近期偏誤), MD-78 (近期績效比=策略動能加速度), MD-96 (策略失效Loop), MD-14 (策略-Regime配對), MD-143 (WFA全樣本悖論)

**One-line**: Every strategy has a finite lifespan. Know how to detect the decay curve before it kills your account.

---

## Why strategies die

Markets are adaptive systems. When an inefficiency is exploited repeatedly, three forces close it:

1. **Crowding** — more capital chases the same edge → signal degrades
2. **Regime shift** — macro/structural change makes the underlying premise false
3. **Arbitrage** — the specific pattern gets priced away by competing strategies

Strategies don't die instantly. They decay. Most traders hold too long because P&L grief clouds the signal.

---

## The 5-Gate Sunset Protocol

### G0 — Rolling OOS Monitor (weekly)
**Trigger**: Every 7 days, compare last-30-day OOS performance vs. inception OOS baseline.

- Metric: Rolling Sharpe ratio, Win Rate, Profit Factor (3 measures, not 1)
- Baseline: save at strategy go-live (`results/strategy_baselines.json`)
- Alert threshold: any single metric drops below 60% of baseline for 2 consecutive weeks

*DNA: MD-26 (OOS近期偏誤 — recent performance is noisier, not more accurate)*

```
rolling_score = 0.4 × (sharpe_30d / sharpe_baseline)
              + 0.4 × (pf_30d / pf_baseline)
              + 0.2 × (wr_30d / wr_baseline)

if rolling_score < 0.6 for ≥2 weeks → escalate to G1
```

### G1 — Regime Mismatch Check
**Question**: Is the strategy running in its target regime?

- Run `trading_system.py --portfolio` to get current regime label
- If strategy was designed for TRENDING regime but current regime = MEAN_REVERTING → **not a strategy failure, it's a deployment error**
- If regime matches and rolling_score < 0.6 → genuine decay → escalate to G2

*DNA: MD-14 (전략-Regime配對), MD-25 (ATR驅動策略輪換)*

**Decision fork**:
- Regime mismatch → suspend strategy, switch to regime-appropriate strategy (not a sunset)
- Regime match + underperformance → G2

### G2 — Edge Ratio Integrity Test
**Question**: Is the strategy's structural edge (MFE/MAE×√N) still present?

Run `backtest_framework.py` on the last 90 days of live data:

```
edge_ratio = MFE / MAE × sqrt(N_trades)
```

- Healthy: edge_ratio ≥ 3.0
- Warning: 1.5 ≤ edge_ratio < 3.0 → reduce position size 50%
- Dead: edge_ratio < 1.5 → escalate to G3

*DNA: MD-13 (策略品質=MFE/MAE×√N)*

### G3 — Structural Premise Check
**Question**: Is the foundational assumption of the strategy still true?

For each strategy, the premise must be documented at go-live. Example:
- DualMA: *"BTC price momentum persists over 10–30 bar windows"*
- Donchian: *"Breakouts from 20-bar channel produce trending follow-through"*

Test: Can you point to current market data that confirms the premise is still true?
- Yes → strategy is underperforming but premise intact → temporary drawdown, hold
- No → premise falsified → G4 kill

*DNA: MD-4 (前提正確才有策略有效性)*

### G4 — Anti-Capitulation Sanity Check
Before killing: verify you're not capitulating at the bottom of a drawdown cycle.

Run the 3-question pre-kill checklist:
1. Is drawdown within historical max? (if yes → may be normal variance)
2. Is kill decision emotion-driven or metric-driven? (log your emotional state)
3. Has anyone else running the same strategy class reported similar failure? (market-wide vs. strategy-specific)

If ≥2 answers point to "normal variance" → do NOT kill, reduce size 50% and monitor 14 more days.
If ≥2 answers point to "genuine failure" → execute kill protocol.

*DNA: MD-96 (策略失效=先定失效條件再管理), MD-5 (Bias toward inaction)*

### G5 — Kill Protocol & Resurrection Criteria
**Execute kill:**
1. Close all positions immediately (market order, accept slippage)
2. Move capital to lowest-risk strategy or stablecoin
3. Document kill reason in `results/strategy_graveyard.md` (date / regime / rolling_score / edge_ratio / reason)
4. Block strategy from re-deployment for minimum 30 days

**Resurrection criteria** (all 3 required):
- [ ] Root cause identified and documented
- [ ] Regime has changed (if regime was the cause) OR structural premise holds in new backtest (if edge decay was cause)
- [ ] Paper-live test of 20+ ticks shows edge_ratio ≥ 3.0 before re-deploying capital

*DNA: MD-78 (近期績效比=策略動能加速度 — use derivative, not level)*

---

## Implementation Checklist

- [ ] Save strategy baseline metrics at go-live: `results/strategy_baselines.json`
- [ ] Create `results/strategy_graveyard.md` (empty now, fill on first kill)
- [ ] Set weekly G0 monitor reminder (Sunday UTC)
- [ ] Document premise for each active strategy (add to `trading/strategies.py` docstring)

---

## Key Insight

Most traders sunset a strategy because of P&L pain, not because of structural failure. This protocol inverts the order: **identify the structural failure first, then confirm P&L confirms it**. Emotion-driven kills destroy more capital than late kills.

The difference between a drawdown and a dying strategy is whether the premise is still true.

---

*Part of the Digital Immortality SOP series. Edward Lin / dna_core.md*
