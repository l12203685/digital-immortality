# Trading Analysis — Cycle 257
> Generated: 2026-04-09T11:25Z | Tick range: 1–60 | Mode: PAPER

---

## Regime Assessment

**Current regime: MIXED** (persistent across all 60 ticks)

No regime transition detected. The mixed regime has held since tick 1 (06:25Z) through tick 60
(11:21Z) — approximately 5 hours. Price range in this session: 70,810 – 71,318. Directional
conviction is absent. Mixed = trend strategies should stay flat; mean-reversion strategies
may have edge but only if price moves to band extremes.

---

## PnL Trajectory

**Total PnL (portfolio): -1.0873%** (from status file)

Session-level PnL by strategy (from log):

| Strategy | cum_pnl at tick 60 | Status |
|---|---|---|
| gen_BollingerMeanReversion_RF_7abfe4 | **-0.364** | Only strategy with realized PnL |
| DualMA_10_30 | **disabled** (PF 0.65 < 0.8 threshold) | Killed pre-session |
| All 13 remaining strategies | 0.000 | Flat — no positions taken |

**PnL trajectory detail for gen_BollingerMeanReversion_RF_7abfe4:**
- Tick 1: cum_pnl = 0.0 (no position)
- Ticks 2–N: entered a position, accumulates loss
- Tick 56–60: cum_pnl stable at -0.364 (position closed or flat, loss locked in)

**DualMA_10_30 trajectory (disabled, reconstructed):**
- Tick 1: OPEN_SHORT at 70,866 (signal -1)
- Ticks 2+: price rose to 71,318 peak → short was losing
- Disabled before it could inflict further damage (PF kill rule working)

**Portfolio total -1.0873% implies** losses distributed across earlier cycles not reflected in
this session's log. This session added -0.364 from the BollingerMR RF variant.

---

## Strategy Health

### Active (14 strategies, all signals = 0 at tick 60)

**Flat / waiting (GOOD — regime-appropriate):**
- `Donchian_20` — no signal, correctly waiting for breakout
- `DonchianConfirmed_20` — same
- `DualMA_filtered` — regime filter suppressing signal correctly
- `Donchian_filtered` — same
- `DonchianConfirmed_filtered` — same
- `DualMA_RSI` — RSI + MA confirmation keeping it flat
- `DualMA_RSI_filtered` — same
- `BollingerMR_20` — mean-reversion, no band touch detected
- `BollingerMR_loose` — looser bands, still no signal
- `gen_DonchianConfirmed_a7186a` — generated variant, flat
- `gen_DualMA_RF_602541` — generated variant, flat
- `gen_BollingerMeanReversion_f91248` — generated variant, flat
- `gen_BollingerMeanReversion_RF_598b24` — generated variant, flat (cum_pnl = 0.0)

**Loss-generating:**
- `gen_BollingerMeanReversion_RF_7abfe4` — cum_pnl = -0.364. This is the RF (regime-filtered)
  Bollinger variant. Loss occurred despite regime filter. Suggests the filter let a trade
  through in a period where the band touch did not revert.

**Disabled:**
- `DualMA_10_30` — PF 0.65, correctly killed by the kill rule.

---

## Recommendation

**1. Investigate gen_BollingerMeanReversion_RF_7abfe4 specifically.**
   - It is the only strategy generating losses this session.
   - The "RF" (regime-filtered) tag implies it should avoid mixed-regime trades. Yet it still
     took a loss. Check: did it fire in a brief non-mixed window, or is the regime filter
     logic permissive of mixed-regime entries?
   - Action: Review the RF filter logic. If it entered during a mixed tick, the filter has a
     gap. Candidate fix: require regime = trending (not just non-ranging) before allowing
     BollingerMR entries.

**2. Do NOT tune parameters on flat strategies.**
   - 13 of 14 active strategies are correctly flat. Mixed regime = correct behavior = HOLD.
   - Forcing signals in mixed regime by loosening parameters would add noise, not edge.
   - Wait for regime shift before assessing trend strategy fitness.

**3. DualMA_10_30 disable is working.**
   - Tick 1 it shorted at 70,866 into rising price. Kill rule removed it before compounding.
   - The PF threshold (0.8 minimum) is correctly calibrated. No action needed.

**4. Watch price range.**
   - Current price 71,210 is mid-range of session (10,810 low – 71,318 high).
   - No breakout signal from any Donchian strategy implies price has not cleared channel edges.
   - If price breaks above 71,318 in next 5–10 ticks, expect Donchian_20 to fire long.

**5. Regime inflection watch.**
   - 5 hours of persistent "mixed" is unusually stable. Either: (a) genuinely choppy market,
     or (b) regime detector is underresponsive to directional moves.
   - Recommend: at next regime check, compare ADX or trend slope to verify "mixed" label is
     still warranted at 71,210.

---

## Summary Verdict

Engine is healthy: kill rules firing, most strategies correctly flat, no runaway losses. The
single live issue is gen_BollingerMeanReversion_RF_7abfe4 at -0.364. Investigate RF filter
gap before next live session. No parameter tuning needed for flat strategies.
