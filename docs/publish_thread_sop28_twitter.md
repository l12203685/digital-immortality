# Twitter Thread — SOP #28: Execution & Slippage Management

**Hook (Tweet 1):**
Your backtest made $50/trade.
Your live account makes $30.

You didn't lose your edge.
You're paying 40% of it to execution.

Here's the system that stops that bleed: 🧵

---

**Tweet 2:**
Most quants backtest at Close price.

But you enter at Stop/Limit orders.
You exit at Market orders.

These two prices have DIFFERENT slippage profiles.
Aggregating them produces a cost model that's wrong by design.

Rule #1: Model entry and exit slippage separately. Always.

---

**Tweet 3:**
Before any strategy goes live, run this math:

Avg_trade_PnL = gross edge ÷ N trades (from OOS)
Break_even_slippage = Avg_trade_PnL × 0.5

If your execution cost > break-even slippage → don't go live.
The market didn't beat you. Friction did.

---

**Tweet 4:**
Not all markets are equal execution environments.

Pre-screen before strategy development:
• Volume > 1,000 contracts/day (futures)
• Bid-ask < 2 ticks at signal time
• Liquidity exists during YOUR trading hours
• Roll cost < 2×/year

One bad instrument selection = 2 years of slippage drag.

---

**Tweet 5:**
Match order type to strategy architecture:

Trend-following → stop-limit (breakout)
Mean-reversion → limit orders
Breakout → stop-market (speed > cost)
Overnight carry → end-of-day limit

If your strategy requires market orders for most exits:
Quantify the urgency premium. If >20% of avg trade → redesign.

---

**Tweet 6:**
Paper trading doesn't model slippage.
Live always costs more.

Set your divergence threshold BEFORE going live:

✓ Acceptable: Live > Paper × 0.75
⚠ Warning: Live = Paper × 0.50–0.75
🔴 Kill: Live < Paper × 0.50

When you hit WARNING: pull execution logs. Which trades have highest slippage?
Fix the execution model. Then re-enter at 25% size.

---

**Tweet 7:**
Run an execution audit every quarter.

Check these 6 things:
1. Entry slippage model vs. actual (within 20%?)
2. Exit slippage model vs. actual (within 20%?)
3. Commission rate changed?
4. Instrument volume dropped >30%?
5. Bid-ask spread widened?
6. Cumulative roll cost this quarter?

If any flag triggers: recalculate break-even. If strategy fails → kill or redesign.

---

**Tweet 8:**
The real cost of poor execution:

Strategy with $50 avg trade PnL
Execution cost: $30/trade

Net: $20/trade
That's 60% of your edge gone to friction.

Same strategy, better execution ($8/trade cost):
Net: $42/trade

The strategy didn't change.
Execution discipline is alpha.

---

**Tweet 9:**
台指期 reference point (MD-83):

Stop-order slippage at volatile opens:
500 TWD per contract = baseline floor

If your strategy edge per trade < 1,500 TWD → review viability before live.

For BTC/USDT:
Budget 0.002% entry + 0.001% exit + 0.001% commission per round trip.

---

**Tweet 10:**
The execution system in 5 gates:

G0: Separate entry/exit slippage models
G1: Break-even slippage calc before live
G2: Instrument selection screen
G3: Order type matched to strategy
G4: Quarterly execution audit
G5: Live vs. paper divergence protocol with kill threshold

Every gate has a number. No "feels ok."

---

**Tweet 11:**
Why execution management is the last thing traders fix:

It's invisible in backtests.
It doesn't show up as a "wrong signal."
It looks like random noise.

But it's structural. Predictable. Fixable.

The best signal in the world is worthless if you can't capture it.

---

**Tweet 12:**
Full framework:

SOP #25: Position Sizing
SOP #26: Walk-Forward Validation
SOP #27: Regime Detection
→ SOP #28: Execution & Slippage Management (this one)

You now have the complete loop:
Size correctly → validate correctly → detect regime → capture the edge cleanly.

The series continues. Follow for the full system.
