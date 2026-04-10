# Twitter/X Thread — SOP #03: Execution & Sizing Real-Time Checklist

> Source: Knowledge Product #03 (Execution & Sizing SOP)
> Status: DRAFTED — ready to post after SOP #02 thread goes live
> Cycle: 113

---

**Tweet 1 (hook)**
Most traders have a decent strategy.

They still lose money.

Why? Because between "signal fires" and "order submitted," they make 5 silent errors.

Here's an 8-gate checklist that removes all of them. 🧵

---

**Tweet 2**
Before the session opens — two mandatory checks:

Gate 0: L/S pool balance audit
Count long-biased vs short-biased strategies.
If longs > shorts × 2, you have a regime blindspot, not diversification.

Don't trade a structurally one-sided pool without acknowledging this in writing.

---

**Tweet 3**
Gate 1: Set leverage from historical data, not recent performance.

Pull Calmar/Sharpe from your full backtest.
Use that ratio to cap leverage for today.

Recent performance = use only to detect failure.
Never use it to increase leverage.

Mixing these two inputs is the source of most blowups.

---

**Tweet 4**
Now a signal fires.

Gate 2: edge_ratio check

edge_ratio = avg(MFE/ATR) / avg(MAE/ATR) × √N

Threshold: ≥1.5 for trend, ≥1.2 for mean reversion

Small N + high edge_ratio = small-sample overfit. Not edge.

Below threshold: log as SKIPPED_QUALITY. Move on.

---

**Tweet 5**
Gate 3: First-principles coherence

Ask: "What is this strategy extracting from the market? Who is on the other side?"

If you can't answer in one sentence, the edge is borrowed, not owned.

Borrowed edges disappear when regime changes.
Owned edges can be regime-conditioned.

---

**Tweet 6**
Gate 4: Stop-loss FIRST, size second.

Step 1: max risk = equity × 1%
Step 2: identify stop level (structural, not arbitrary)
Step 3: stop distance in points
Step 4: back-calculate max entry = stop + (1% equity / lot_size / multiplier)

If current price > max_entry → no trade.

Never: "Enter, then find a stop."

---

**Tweet 7**
Gate 5: Position size formula

lots = (equity × 0.01) / (ATR × contract_multiplier)

That's it.

Any deviation requires a written reason in the trade log before execution.

"The signal feels strong" is not a valid reason.

---

**Tweet 8**
Gate 6: Trial vs full position

edge_ratio 1.2–2.0 or conditions uncertain → enter 50% (trial)

The trial must have positive EV on its own. Not as a placeholder.

Full add: only if (a) price action confirms AND (b) stop can move to entry.

Trial stopped out → log it. Never average down.

---

**Tweet 9**
Gate 7: Final order checklist before submitting

- Entry price: within G4 range
- Stop: pre-set, not mental
- Size: from formula, not rounded for convenience
- Target: p75 of MFE distribution
- Leverage: within G1 cap

If any box is unchecked: wait.

---

**Tweet 10**
Gate 8: Correlation check

Is this trade correlated >0.7 with an existing open position?

If yes → reduce new position to 50% OR trim existing to make room.

Portfolio-level risk = sum of correlated exposures.
Not sum of individual stops.

Most traders calculate this wrong.

---

**Tweet 11 (kill conditions)**
When to stop mid-session:

Per-trade: edge_ratio <0.8 over 10 trades → pause that strategy
Per-session: 3× stop hit same strategy → halt for the day
Intraday: account DD >3% → close all, no new entries

Gate 0 or G1 fail at open → max 50% size all day.

---

**Tweet 12 (close)**
The checklist:

G0: L/S pool balance
G1: Leverage from historical R/R
G2: edge_ratio gate
G3: First-principles coherence
G4: Stop-first sizing
G5: Position formula
G6: Trial vs full
G7: Order parameters
G8: Correlation check

8 gates. No skipping.

SOP series: #01 Strategy Dev → #02 Portfolio → #03 Execution ✓
