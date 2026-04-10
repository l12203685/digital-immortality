# Workbook #03 — Execution & Sizing Real-Time Checklist
> Based on SOP #03 | Backing MDs: MD-13, MD-28, MD-29, MD-30, MD-133, MD-157, MD-159
> Price: $29 | Format: Fillable PDF / Notion template

---

## What This Workbook Is

You have a strategy. You have a portfolio. Now: does your next signal actually become a correctly-sized live order — or do you wing it?

This workbook converts SOP #03's 8 sequential gates into a hands-on checklist you complete for every live trade session. After one week of use, execution becomes a zero-decision procedure. No gut feel. No size miscalculations.

**Prerequisite:** Completed Workbook #01 (Strategy Development) + Workbook #02 (Portfolio Construction)

---

## Gate 0 — Strategy Pool L/S Balance Audit (MD-29)
*Run once per session open, before scanning for signals.*

| Active Strategy | Direction Bias | Status |
|-----------------|---------------|--------|
| | LONG / SHORT / NEUTRAL | ACTIVE / PAUSED |
| | LONG / SHORT / NEUTRAL | ACTIVE / PAUSED |
| | LONG / SHORT / NEUTRAL | ACTIVE / PAUSED |
| | LONG / SHORT / NEUTRAL | ACTIVE / PAUSED |

**Imbalance check:**
- Long-biased count: ___
- Short-biased count: ___
- Ratio (long÷short): ___

**Rule:** If long > short × 2 → FLAG before proceeding.

Imbalance means: rolling optimisation naturally over-selects longs. Proceeding with structural imbalance = regime blindspot, not edge.

**[ ] G0 PASS** — Pool is balanced OR imbalance acknowledged in writing: _______________

---

## Gate 1 — Leverage Coefficient (MD-30)
*Pull historical performance for each active strategy.*

| Strategy | Historical Calmar | Historical Sharpe | Max Leverage Cap Today |
|----------|------------------|------------------|----------------------|
| | | | |
| | | | |

**Rule:** Leverage cap = HISTORICAL Calmar/Sharpe, not last 30 days.

Using recent performance to set leverage = recency bias amplified by leverage.  
Recent performance is for *failure detection only* (see G2).

**[ ] G1 PASS** — Session leverage cap set using historical R/R: ___

---

## Gate 2 — Strategy Quality Check (MD-13)
*Run for each signal before proceeding.*

Signal source: _______________ | Signal: LONG / SHORT | Instrument: ___

**Edge ratio calculation:**
```
edge_ratio = avg(MFE/ATR) ÷ avg(MAE/ATR) × √N
```

- avg(MFE/ATR): ___
- avg(MAE/ATR): ___
- N (trades in sample): ___
- edge_ratio = ___

**Threshold:**
- Trend strategy → edge_ratio ≥ 1.5
- Mean-reversion strategy → edge_ratio ≥ 1.2
- Below threshold → log as SKIPPED_QUALITY, stop here

**[ ] G2 PASS** — edge_ratio ≥ threshold

*Worked example — DualMA BTC:*
avg(MFE/ATR)=1.8, avg(MAE/ATR)=0.8, N=64 → edge_ratio = (1.8÷0.8)×√64 = 2.25×8 = **18.0 → PASS**

---

## Gate 3 — First-Principles Coherence (MD-157)
*One sentence. No jargon.*

"This strategy extracts profit from: _____________________________________________"

"The counterparty in this trade is: ____________________________________________"

**Rule:** If you cannot complete both sentences without referencing an indicator name or moving average, the edge is borrowed, not owned. Borrowed edges disappear when regime changes.

**[ ] G3 PASS** — Mechanism articulated in plain language

*Worked example — DualMA BTC:*
- Extracts: trend momentum — late trend-followers push price after breakout
- Counterparty: mean-reversion traders who fade early breakout, get stopped out

---

## Gate 4 — Stop-Loss First, Size Second (MD-133)
*Stop before size. Always.*

**Step 1:** Max risk per trade
```
max_risk_USDT = account_equity × 0.01
max_risk_USDT = ___ × 0.01 = ___
```

**Step 2:** Stop-loss price level (structural — support/resistance/ATR multiple)
```
Stop price: ___   Reason: ___________________________
```

**Step 3:** Stop distance
```
stop_distance = |entry_price − stop_price| = |___ − ___| = ___
```

**Step 4:** Max entry check
```
max_entry = stop_price + (max_risk_USDT ÷ lot_size ÷ contract_mult)
max_entry = ___ + (___ ÷ ___ ÷ ___) = ___
```

**Step 5:** Current price ≤ max_entry?
- Current price: ___
- max_entry: ___
- If current price > max_entry → **NO TRADE** (stop is too far; do not move the stop)

**[ ] G4 PASS** — Entry within max_entry range

*Worked example:*
- Equity=$1,000, max_risk=$10
- BTC entry=$71,500, ATR-stop=$71,000 (500 below)
- max_entry = $71,000 + ($10 ÷ 0.01 ÷ 1) = $71,000 + $1,000 = $72,000
- Current=$71,500 < $72,000 → **PASS**

---

## Gate 5 — Position Size Formula (MD-28)

```
lots = (account_equity × risk_pct) ÷ (ATR × contract_multiplier)
```

**Your inputs:**
- account_equity: ___
- risk_pct: 0.01 (never override by feel)
- ATR (14-period, signal timeframe): ___
- contract_multiplier: ___

**Calculation:**
```
lots = (___ × 0.01) ÷ (___ × ___) = ___
```

**Any deviation from this formula requires a written reason before execution:**
Reason (if deviating): _______________________________________________

"The signal feels strong" is NOT a valid reason.

**[ ] G5 PASS** — Lots calculated from formula

*Worked example:*
- Equity=$1,000, ATR=$500, contract_mult=1
- lots = ($1,000 × 0.01) ÷ ($500 × 1) = $10 ÷ $500 = **0.02 BTC**

---

## Gate 6 — Trial vs Full Position (MD-159)
*Each position leg must have positive EV on its own.*

**edge_ratio from G2:** ___

| Condition | Action |
|-----------|--------|
| edge_ratio ≥ 2.0 AND high regime confidence | Full position |
| edge_ratio 1.2–2.0 OR uncertain conditions | Trial position (50% of G5 lots) |
| Below threshold | SKIPPED (already caught in G2) |

**Decision:** TRIAL (50%) / FULL (100%)

**If trial:** Full position add conditions (BOTH required before adding):
- [ ] Price action confirms signal after entry
- [ ] Stop can be moved to entry (breakeven or better)

**[ ] G6 PASS** — Position size decision documented

---

## Gate 7 — Order Parameters Pre-Submission Checklist (final)

Before hitting the order button:

- [ ] Entry price: market/limit within G4 max_entry range
- [ ] Stop-loss: pre-set in platform (NOT mental stop)
- [ ] Size: G5 formula result (not rounded for convenience)
- [ ] Target: p75 MFE from backtest distribution = ___
- [ ] Strategy label logged in trade journal
- [ ] G0–G6 all checked
- [ ] Correlation check: this trade does NOT duplicate existing open position direction in correlated instrument

**[ ] G7 PASS** — All boxes checked → SUBMIT ORDER

---

## Post-Trade Log Template

Copy once per trade into your journal:

```
Date: ___________  Strategy: _______________  Instrument: ___
Direction: LONG / SHORT
Entry: ___  Stop: ___  Target: ___  Size (lots): ___
G0 Pool balance: PASS/FLAG  G1 Leverage cap: ___
G2 edge_ratio: ___  PASS/SKIP
G3 Mechanism: ___________________________________
G4 max_entry: ___  PASS/FAIL
G5 lots formula: ___
G6 Trial/Full: ___
G7 Pre-submission: PASS/FAIL
Exit: ___  P&L: ___
Post-trade note (if any deviation): ___________________________________
```

---

## Kill Conditions (pre-commit before first tick)

Before live trading with any new strategy, sign off:

| Condition | Threshold | My Value | Action |
|-----------|-----------|----------|--------|
| Max drawdown | >10% | ___ | STOP immediately |
| Win rate (≥5 trades) | <35% | ___ | PAUSE, review |
| Profit factor (≥3 losses) | <0.85 | ___ | PAUSE, review |
| Consecutive losses | ≥5 | ___ | REDUCE SIZE 50% |

**Signed pre-deployment:**
Date: ___________ Strategy: _______________ Signature: _______________

---

## Quick Reference Card (print and pin to monitor)

```
SESSION OPEN:
  G0 → L/S pool balance (long > short×2 = FLAG)
  G1 → leverage from historical Calmar/Sharpe, not recent 30d

EACH SIGNAL:
  G2 → edge_ratio ≥ 1.5 (trend) / 1.2 (MR)
  G3 → one sentence: what does it extract? who's the counterparty?
  G4 → stop first → max_entry → is current price ≤ max_entry?
  G5 → lots = (equity × 0.01) ÷ (ATR × mult)
  G6 → edge_ratio ≥ 2.0 = full; 1.2–2.0 = trial (50%)
  G7 → stop in platform, size from formula, target from MFE p75

FAIL ANY GATE = NO TRADE. LOG AS SKIPPED.
```

---

## Gumroad Listing Copy

**Title:** The Execution & Sizing Checklist — 7 Gates Before Every Live Trade

**Short description:**
Stop sizing by gut feel. This 7-gate checklist converts any validated strategy signal into a correctly-sized live order. For traders who already know their edge but keep mis-sizing.

**Long description:**
You did the work. You have a validated strategy (Workbook #01). You built a portfolio (Workbook #02). Now the signal fires — and you need to get the size right, every time, without burning decision capital.

This workbook gives you:
- Gate 0: Pool L/S balance audit (catch systematic regime blindspots before they happen)
- Gate 1: Leverage from historical Calmar/Sharpe — not recent performance
- Gate 2: Edge ratio calculation with pass/fail threshold
- Gate 3: First-principles coherence — own your edge or don't trade it
- Gate 4: Stop-first sizing — back-calculate max entry from stop (not the other way)
- Gate 5: Position formula — lots = (equity × 1%) ÷ (ATR × mult), no gut feel
- Gate 6: Trial vs full position — both must have independent positive EV
- Gate 7: Final pre-submission checklist

Includes: worked DualMA BTC example through all 7 gates, post-trade log template, kill conditions sign-off sheet, quick reference card for monitor.

Format: 7 fillable gate worksheets + quick reference card. Use as Notion template or print as PDF.

**Tags:** trading, position sizing, risk management, execution, systematic trading

**Upsell prompt (in confirmation email):**
→ Already have Workbook #02 (Portfolio Construction)? That builds *what* to run. This workbook ensures every signal from that portfolio translates into a correctly-sized order.
→ Missing Workbook #01 (Strategy Development)? Start there: [link]
→ Missing Workbook #02 (Portfolio Construction)? [link]

**Setup steps (~20 min to list after G2 triggers):**
1. Log in to Gumroad
2. New Product → Digital → Upload this file (PDF or Notion export)
3. Price: $29
4. Title + short desc from above (copy-paste)
5. Tags: trading, position sizing, execution
6. Paste long desc in body
7. Add upsell links to Workbook #01 and #02 in confirmation email
8. Publish
