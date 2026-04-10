# Twitter Thread — SOP #09: Risk Management & Drawdown Response

---

**Tweet 1 (hook)**
Most traders lose not because their strategy is wrong — but because they have no protocol for when it's losing.

Here's the 5-gate Risk Management & Drawdown Response SOP I built from 8 years of micro-decisions:

🧵

---

**Tweet 2 — G0: Write the kill condition BEFORE entry**
Risk management doesn't start when you're in a trade.
It starts when you define: "What does failure look like?"

Before every position:
- What's the max loss in dollars?
- At what equity level does the strategy stop?

You can't manage what you haven't pre-defined.

---

**Tweet 3 — G1: Daily loss limit scales with leverage**
Daily max loss = account × 1% ÷ leverage

At 5× leverage: only 0.2% of account per day.

Hit the limit → stop for the day. No recovery trades.

High leverage converts "bad day" into "existential event" if you keep going.

---

**Tweet 4 — G2: Reduce leverage 50% before known events**
FOMC. Elections. Expiry week. GDP/CPI.

These are pre-scheduled regime uncertainty spikes. Not surprises.

You don't need to predict direction. You need to NOT be full leverage when the gap opens.

Reduce 50% before. Restore only if post-event regime matches your strategy.

---

**Tweet 5 — G3: Equity curve IS your leverage instruction**
3 states:
- Normal (within 1× ATR of 20-day MA) → full leverage
- Warning (1–2× ATR below MA) → 50% leverage
- Stop (>2× ATR below MA) → close positions, paper only

The equity curve knows before you do that regime has shifted.
Waiting until you "know why" costs 30–50% more drawdown.

---

**Tweet 6 — G4: Adding to losers requires a pre-written plan**
Before you can add to a losing position, ALL of these must be true:
☑ OOS Sharpe > 0.5, N > 30 trades
☑ DD is within historically observed max
☑ Scale-in levels were written BEFORE original entry
☑ Adding doesn't violate daily loss limit

No pre-written plan = no add. Period.

---

**Tweet 7 — G5: Drawdown recovery protocol**
Equity curve hits Stop state:
1. Close all positions
2. Paper trade for 5 sessions minimum
3. Diagnose: variance / regime mismatch / strategy failure
4. Resume live only when paper is positive AND equity curve > 20-day MA
5. Start at 25% leverage. Scale back over 4 weeks.

---

**Tweet 8 — The anti-patterns**
"I'll stop at the end of the week" → daily limits exist because intraday leverage kills
"This event is different" → no exceptions
"Just bad luck" → equity curve doesn't care
"I'll average down, it always works" → until it doesn't, and then it's terminal

---

**Tweet 9 — Summary**
Risk management has one job: keep you alive long enough to be right.

The equity curve is not a performance report.
It's a leverage instruction.

SOP #09: full doc in thread. Full series (#01–#09) in my GitHub.
