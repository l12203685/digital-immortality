# SOP #28 — Order Execution & Slippage Management

> "Stop slippage > Close slippage. Model them separately. Never aggregate." — MD-83

---

## Why This Matters

Every other SOP in this series assumes signals are correct.
Position sizing (SOP #25) assumes you can enter at a predictable cost.
Strategy kill decisions (SOP #04) assume the reported P&L reflects actual edge, not execution drag.
Walk-forward validation (SOP #26) IS/OOS results are meaningless if live execution bleeds 30–50% of theoretical edge.

Execution is where theory meets reality. Poor execution doesn't just reduce returns — it turns winning strategies into losers by eroding the thin margin between signal edge and friction cost.

**The execution gap:** Most retail quants backtest at Close price. Live execution happens at Stop/Market orders. These two prices have structurally different slippage profiles. Aggregating them produces a biased cost model that systematically underestimates live friction. (MD-83)

---

## Gate 0 — Separate Entry and Exit Slippage Models

**Principle: Stop slippage ≠ Close slippage (MD-83)**

```
Entry (Stop/Limit):
  Slippage_entry = (Fill_price - Signal_price) × direction
  Typical range: 0.5–2 ticks for liquid futures
  Cause: market impact + latency + bid-ask spread at trigger

Exit (Market/Close):
  Slippage_exit = (Signal_price - Fill_price) × direction
  Typical range: 0.3–1.5 ticks for liquid futures
  Cause: urgency premium + adverse selection at close

Aggregate_drag = Slippage_entry + Slippage_exit + Commission
```

**Model separately. Report separately. Never sum before validation.**

Quarterly audit: compare model_drag vs actual_drag per strategy. Divergence >20% = recalibrate.

---

## Gate 1 — Calculate Break-Even Slippage Before Entry

Before running any strategy live, compute its slippage tolerance:

```
Avg_trade_PnL = Gross_edge ÷ N_trades  (from OOS backtest)
Break_even_slippage = Avg_trade_PnL × 0.5

IF expected_execution_cost > Break_even_slippage:
    → DO NOT GO LIVE. Strategy is not viable at this execution quality.

IF expected_execution_cost < Break_even_slippage × 0.3:
    → Execution comfortable. Monitor quarterly.
    
IF expected_execution_cost between 0.3× and 0.5× break_even:
    → Yellow zone. Track monthly. Any regime shift or volume drop = re-evaluate.
```

**Rationale:** A strategy with $50 avg trade PnL and $30 execution cost is losing to friction, not the market.

---

## Gate 2 — Instrument Selection by Execution Cost

Not all instruments are equal execution environments. Pre-screen before strategy development:

| Factor | Threshold | Why |
|--------|-----------|-----|
| Daily volume | >1,000 contracts (futures) / >$5M (crypto) | Thin markets = slippage compounds |
| Bid-ask spread | <2 ticks at signal time | Wide spread eats mean-reversion edge |
| Session depth | Verify at your actual trading hours | Liquidity vanishes in off-hours |
| Contract structure | No forced roll >2×/year | Roll cost is hidden execution drag |

**台指期 reference (MD-59):** 500-point slippage baseline for stop-entry on volatile opens.
Use 500 TWD per contract as floor estimate. If strategy edge < 1500/trade → review viability.

---

## Gate 3 — Order Type Selection by Strategy Architecture

```
Strategy type        → Preferred order type     → Avoid
Trend-following      → Stop-limit (breakout)    → Market orders at open
Mean-reversion       → Limit orders             → Stops at extremes
Breakout             → Stop-market (speed > cost) → Passive limits at trigger
Overnight carry      → End-of-day limit         → Market-on-close (slippage spike)
```

**Rule:** If a strategy requires market orders for most exits → quantify speed premium paid.
If urgency cost > 20% of avg trade → redesign exit to use limit with aggressive spread.

---

## Gate 4 — Execution Environment Audit (Quarterly)

Run this audit every quarter. Update cost model if any parameter shifts >20%:

```python
# Execution audit checklist
execution_audit = {
    "entry_slippage_model": "actual vs modeled — within 20%?",
    "exit_slippage_model":  "actual vs modeled — within 20%?",
    "commission_change":    "broker rate changed?",
    "volume_decay":         "instrument volume dropped >30%?",
    "spread_widening":      "avg bid-ask > baseline × 1.5?",
    "roll_cost":            "cumulative roll drag this quarter?",
    "fill_rate":            "limit order fill rate > 70%? (if using limits)"
}
```

**If any flag triggers:** Recalculate Break-Even slippage (Gate 1). If strategy now fails Gate 1 → kill or redesign.

---

## Gate 5 — Live vs. Paper Divergence Protocol

Paper trading doesn't model slippage. Live always costs more. Manage the gap:

```
Acceptable divergence: Live_PnL > Paper_PnL × 0.75
Warning:              Live_PnL = Paper_PnL × 0.50–0.75
Kill signal:          Live_PnL < Paper_PnL × 0.50

On WARNING:
  1. Pull execution logs — identify which trades have highest slippage
  2. Check if slippage clusters at regime transitions (high ATR, news events)
  3. Add regime filter: reduce size 50% during ATR > 85th percentile
  4. Re-run Gate 1 with updated cost model

On KILL signal:
  → Paper → diagnose → fix execution model → 5-trade paper validation → re-enter at 25% size
```

---

## Self-Test: DualMA BTC Paper vs. Live Scenario

Using SOP #25 position sizing + SOP #27 regime detection:

| Metric | Paper (backtest) | Live estimate | Passes Gate? |
|--------|-----------------|---------------|-------------|
| Avg trade PnL | $12.40 | $12.40 (gross) | — |
| Entry slippage | $0 | ~$1.50 (0.002%) | — |
| Exit slippage | $0 | ~$0.80 (0.001%) | — |
| Commission | $0 | ~$0.60 (rt) | — |
| Net per trade | $12.40 | $9.50 | ✓ G1 pass |
| Execution drag | 0% | 23.4% | ✓ Yellow zone |
| Break-even cost | — | $6.20 (50%) | ✓ Current cost < BEP |

**Result: GO with monthly monitoring. Flag if drag crosses 35%.**

---

## DNA Anchors

| MD | Principle | Gate |
|----|-----------|------|
| MD-83 | Stop滑價>Close滑價=分開建模 | G0 |
| MD-59 | 台指期500點滑價基準 | G2 |
| MD-19 | 投資公司門檻量化 | G1 |
| MD-40 | 電指期四大結構優勢 | G2 |
| MD-96 | 策略管理=先定失效再管理 | G5 |
| MD-75 | 權益曲線=槓桿觸發器 | G5 |
| MD-26 | Rolling OOS近期偏誤 | G4 |

---

## Quick Reference Card

```
Before going live on any strategy:
□ G0: Model entry and exit slippage separately
□ G1: Calculate break-even slippage — strategy edge > 2× execution cost?
□ G2: Instrument passes volume/spread/depth screen?
□ G3: Order type matched to strategy architecture?
□ G4: Quarterly execution audit scheduled?
□ G5: Live vs. paper divergence threshold defined before first tick?

Red flag: "My backtest uses Close prices" → add slippage model before live
Red flag: "Slippage looks fine overall" → disaggregate by order type first
```
