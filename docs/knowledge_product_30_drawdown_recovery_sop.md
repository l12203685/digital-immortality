# SOP #30: Drawdown Recovery Protocol
> How to survive a losing streak without blowing up — and return to full size with evidence, not hope.

**DNA Anchors:** MD-42 (equity curve = leverage trigger) / MD-55 (DD pre-commitment to robustness) / MD-98 (survival rate ≥60% threshold) / MD-32 (leverage = f(regime)) / MD-13 (edge_ratio = MFE/MAE√N) / MD-133 (risk-first sizing: stop → position not P&L → stop)

---

## Why This SOP Exists

Every trader knows how to enter a trade. Almost none have a pre-written protocol for what to do when they're 12% underwater and the next signal fires.

Without a protocol, emotions dictate: revenge trading, averaging down, paralysis, or early full-size return.

This SOP replaces emotion with gates.

---

## The Five-Gate Framework

### G0 — Pre-Commit the Recovery Rules BEFORE Drawdown Begins

*"Define failure mode before first tick." — MD-96*

Drawdown recovery rules have zero value if written during the drawdown. Write them now.

Required pre-commitments:
1. **Drawdown trigger levels** — at what DD% do you reduce size?
2. **Recovery confirmation criteria** — what evidence is required before returning to full size?
3. **Kill threshold** — at what DD% do you stop trading entirely pending review?

**Self-test:** Can you state all three numbers right now, for each active strategy, without looking them up? If not, complete G0 before trading.

---

### G1 — Three-Level Size Reduction Ladder

When drawdown hits defined triggers, cut size mechanically:

| Equity Curve vs MA_20 | Max Allowed Leverage | Action |
|-----------------------|---------------------|--------|
| Above MA_20 | 100% (full size) | No change |
| 3–8% below MA_20 | 50% | Cut half |
| 8–15% below MA_20 | 25% | Cut to quarter |
| >15% below MA_20 | 0% | Stop. G4 review. |

*(Thresholds calibrated per strategy; adjust MA window if strategy frequency differs.)*

**DNA anchor — MD-42:** Equity curve is the leverage trigger. Not P&L narrative. Not gut feeling. The curve.

---

### G2 — Survival Rate Check Before Each Re-Entry

After any size reduction, do not return to full size on the next trade. Run the survival rate check:

```
survival_rate = rolling_30d_Sharpe / historical_OOS_Sharpe
```

- ≥ 1.0 → eligible to restore to previous size tier
- 0.6–1.0 → hold current size tier (on watch)
- < 0.6 → drop one more tier; re-check after 10 trades

**DNA anchor — MD-98:** The 60% survival threshold exists because below it, you are no longer trading your backtest — you are trading a degraded version of it.

---

### G3 — Root-Cause Triage Before Any Size Restoration

Before restoring size after a drawdown, answer the three-question triage:

1. **Regime mismatch?** — Was the strategy running in the wrong regime during the drawdown? Check: regime during drawdown vs. strategy's primary regime from backtest.
2. **Execution drag?** — Was realized slippage higher than the break-even slippage from SOP #28?
3. **Sample noise?** — Is this within the expected max drawdown from OOS testing? Check: drawdown ÷ historical max OOS drawdown.

| Root Cause | Action |
|------------|--------|
| Regime mismatch | Don't restore size. Wait for regime flip. |
| Execution drag | Fix execution first (order type, session, instrument) |
| Sample noise | Restore one tier at a time on 5-trade evidence windows |
| Unknown | Quarantine strategy. Root-cause before trading again. |

---

### G4 — Return-to-Full-Size Gate (Evidence, Not Hope)

Returning to full size requires evidence, not elapsed time.

**Gate criteria (ALL must pass):**
- [ ] Survival rate ≥ 1.0 for 10+ consecutive trades
- [ ] Regime matches strategy's primary regime
- [ ] Last 5 trades: win rate ≥ historical WR × 0.8
- [ ] Realized slippage back within break-even bounds
- [ ] Recovery is within the equity curve's normal noise band (not a lucky spike)

If any criterion fails: remain at 50% size, re-check after 5 more trades.

**One-sentence rule:** You restore size because the evidence supports it — not because you're tired of trading small.

---

### G5 — Drawdown Post-Mortem Documentation

After any drawdown exceeding 8% equity or triggering G1 level 2+:

Write a 5-line post-mortem:
1. **Trigger:** What caused the drawdown?
2. **Detection:** How quickly did G1 fire? What delayed it (if anything)?
3. **Root cause:** Which G3 category?
4. **Recovery path:** What changed before returning to full size?
5. **Protocol update:** What one rule would have reduced the drawdown by ≥30%?

File in: `results/drawdown_postmortems/YYYY-MM.md`

---

## Self-Test Scenario

**Setup:** DualMA BTC, testnet. MA_20 = $98,500 equity. Current equity = $90,200 (8.4% below MA_20).

**G1 check:** 8.4% below MA_20 → cut to 25% size.

**G2 check:** rolling_30d_Sharpe = 0.42, historical_OOS_Sharpe = 0.71 → survival_rate = 0.59 (< 0.6) → drop one more tier → 0% (pause).

**G3 triage:** BTC in low-volatility regime, DualMA is a trend strategy → regime mismatch. Action: do not restore size until regime flips.

**G4:** Not applicable — G3 blocked restoration.

**Verdict:** Pause trading DualMA, monitor regime via ATR percentile (SOP #27). Re-enter when regime = trending AND survival_rate ≥ 0.6.

---

## Integration with Prior SOPs

| Prior SOP | How It Feeds G0-G5 |
|-----------|-------------------|
| #27 Regime Detection | G3 regime mismatch check; G4 regime condition |
| #28 Execution & Slippage | G3 execution drag root cause; G4 slippage criterion |
| #29 Strategy Monitoring | G1 equity curve trigger; survival rate input to G2 |
| #04 Strategy Kill Decision | G4 failure → kill protocol if recovery gate fails repeatedly |

---

## One-Page Summary

```
Pre-commit: define DD triggers, recovery criteria, kill threshold BEFORE trading.
G1: equity curve below MA_20 → 50%/25%/0% size ladder.
G2: survival_rate < 0.6 → drop tier; ≥ 1.0 → eligible to restore.
G3: triage regime / execution / noise BEFORE restoring size.
G4: restore only on evidence (10-trade window + 5-point checklist).
G5: post-mortem every drawdown > 8% or G1 level 2+.
```

Drawdown is not failure. Trading full size through a drawdown without a protocol is.
