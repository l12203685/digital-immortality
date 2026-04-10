# SOP #71 — Multi-Strategy Regime Activation Protocol
> Domain 1 (經濟自給 / Economic Self-Sufficiency) | 2026-04-09 UTC

## Purpose

You built 10 strategies. 1 is signaling. 9 are FLAT. Is this concentration risk or correct regime filtering?

**The trap**: Activating all strategies at once inflates position count and dilutes edge. Activating none except DualMA creates single-strategy dependency — 100 ticks, 1 signal, zero regime diversity.

**This SOP answers**: When is regime filter working correctly (expected FLAT) vs. when has the system collapsed to a single-strategy portfolio by default?

**Core axiom (MD-97)**: Strategy selection = first define abstract structure, then fix parameters. A regime filter that always fires the same strategy is not filtering — it has converged to a rule.

**Prerequisite**: SOP #01 (Strategy Development) + SOP #07 (Regime Detection) completed. 2+ strategies backtested with kill conditions documented.

---

## Gate Structure

### G0: Regime Diagnosis
Before activating any additional strategy, confirm the FLAT signals are regime-correct, not model failure.

| Check | Pass | Fail |
|-------|------|------|
| Regime score within expected band? | FLAT is correct regime response | Regime detector miscalibrated |
| Strategy designed for current regime? | FLAT because wrong regime | Strategy has an execution bug |
| Kill conditions not triggered? | Strategy is alive, just waiting | Strategy in kill zone — should already be off |
| Backtested FLAT rate ≥ 60%? | FLAT is normal behavior | Signal too rare — strategy may be overfit |

**Rule (MD-103)**: Market has three states (trend/MR/mixed) — scissors/rock/paper. A strategy designed for one state should be FLAT in the other two. Multiple FLAT signals in mixed regime = system working correctly.

**Concentration alert threshold**: If 1 strategy signals >80% of ticks for 100+ consecutive ticks → flag as concentration event. Not a kill — a diagnostic trigger.

---

### G1: Single-Strategy Dependency Audit
When DualMA_10_30 is the only signaling strategy for 100+ ticks:

1. **Regime distribution check**: Pull last 100 ticks regime labels. If >80% MIXED → DualMA_RSI_filtered should be signaling too. If not → check why.
2. **Strategy-regime matrix audit**: For each of 10 strategies, confirm which regime it's designed for. Map actual regime distribution to expected signal distribution.
3. **Dead strategy detection**: If a strategy has been FLAT for 200+ consecutive ticks across 3+ regime types → may be broken, not filtering. Run backtest on last 30 days.
4. **Correlation check (MD-100)**: Two strategies with >0.85 signal correlation = one is redundant. Don't activate both.

**Decision tree**:
- Regime is MIXED AND DualMA_RSI_filtered is also FLAT → investigate why RSI filter is blocking
- Regime is MIXED AND all trending strategies FLAT → correct behavior, no action
- Regime changed to TRENDING AND DualMA_10_30 still only signal → check if DualMA_filtered is equivalent (may be redundant)

---

### G2: Activation Gate
Before activating a dormant strategy:

| Condition | Required |
|-----------|----------|
| Regime matches strategy design? | ✅ mandatory |
| Kill conditions NOT triggered? | ✅ mandatory |
| OOS backtest pass rate ≥ 60% (MD-97)? | ✅ mandatory |
| Not correlated >0.85 with active strategy? | ✅ mandatory |
| Position capacity available? (MD-100: 2×2 matrix) | ✅ mandatory |

**Activation sequence**: Add strategy to portfolio → paper-live for 5 ticks → if signals behave as expected → confirm active.

**Never activate 2 strategies simultaneously** in live trading. Activate one, observe 5 ticks, then consider the next.

---

### G3: Concentration Risk Protocol
Triggered when: 1 strategy = 100% of signals for 100+ consecutive ticks.

**This is NOT a kill condition** — it is a diagnostic flag.

Actions:
1. Log concentration event to `results/concentration_log.jsonl`: `{ts, strategy, consecutive_ticks, regime_distribution}`
2. Run G1 audit (above)
3. If audit passes (FLAT signals are regime-correct) → log "CONCENTRATION_EXPECTED" + continue
4. If audit fails (inactive strategies should be signaling) → escalate to G2 activation
5. Review quarterly: if 1 strategy = sole signal for 3+ months → this is a portfolio design flaw, not a regime event. Redesign portfolio (SOP #02).

**Axiom (MD-52)**: Genuine diversification = uncorrelated return streams. FLAT is not diversification. Waiting for the right regime is. But if the right regime never arrives for 9 of 10 strategies, the regime classifier is miscalibrated.

---

### G4: Strategy Rotation Protocol
When regime changes signal a new strategy should activate:

1. **Do not exit current active strategy** unless kill conditions triggered — regime change ≠ strategy kill
2. **Add the new strategy** (per G2 gate) while keeping existing
3. **Size both at 50% of normal** until both have ≥5 live ticks
4. **Post-5-tick review**: If both performing — normalize sizes. If new strategy underperforms after 20 ticks — deactivate and log.

**Rule (MD-100)**: Portfolio optimization = recursive pairwise max Calmar ratio. Never add a strategy that lowers the portfolio Calmar. Test this before rotation, not after.

---

### G5: Concentration → Revenue Bridge
Multi-strategy activation is not just a risk management move — it's a revenue signal:

- Single-strategy dependency means single-regime dependency
- If that regime ends → revenue drops to zero
- Diversification = survival across regime transitions

**Target by 2026-07-07 deadline**:
- At least 2 strategies contributing signals across 2 different regimes
- Signal concentration <70% in any single strategy over 30-day window
- Portfolio P&L: both trading source + Gumroad source contributing

**Kill condition for overall trading system**: If concentration stays at 100% for 200 ticks AND regime has rotated at least once during that period → portfolio_selector.py regime thresholds may be stale. Re-calibrate (SOP #07 G3).

---

## Self-Test

**Scenario**: Paper-live tick 106. BTC=$70,981.17. Regime=MIXED. DualMA_10_30=SHORT. 14/15 strategies FLAT. Tick 106 of consecutive SHORT signal.

Apply gates:
- G0: MIXED regime → check if DualMA is designed for MIXED. DualMA portfolio entry = `mixed → DualMA_RSI_filtered`. DualMA_10_30 signals MIXED because it has no regime filter — it's always on. Correct behavior? G0 → borderline. DualMA_RSI_filtered is FLAT — investigate why.
- G1: DualMA_RSI_filtered designed for mixed regime. Currently FLAT. If RSI filter is blocking → regime-correct FLAT. Audit: RSI filter threshold vs current RSI value.
- G2: If DualMA_RSI_filtered should activate → 5-gate G2 check. If kill conditions clean + regime matches → add to paper-live.
- G3: 106 consecutive ticks, 1 strategy = 100% concentration → log concentration event → G1 audit → if audit passes = "CONCENTRATION_EXPECTED".
- G4: No rotation needed until regime flips. When it does → add DualMA_RSI_filtered per 50% sizing protocol.
- G5: Trading = 0 revenue. Gumroad = 0 revenue. Deadline 89 days. Concentration risk is secondary to revenue activation — Edward must post SOP #01.

Expected output: log concentration event, confirm FLAT is regime-correct, continue monitoring. Revenue blocker = first post, not strategy activation.

---

## Connections

- Upstream: SOP #01 (Strategy Development), SOP #02 (Portfolio Construction), SOP #07 (Regime Detection)
- Downstream: SOP #29 (Live Monitoring), SOP #33 (Strategy Regime Change), SOP #38 (Alpha Decay)
- DNA: MD-97 (策略=先抽象結構再固定參數), MD-100 (投組最佳化=遞迴兩兩最高風暴比), MD-52 (真分散=不同架構), MD-103 (市場三態剪刀石頭布)
- Branch: 1.1 (Trading), 1.3 (Revenue)
