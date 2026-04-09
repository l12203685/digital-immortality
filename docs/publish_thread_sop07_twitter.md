# Twitter Thread — SOP #07: Regime Detection & Strategy Routing
> Cycle 131 | Branch 7 | Ready to post

---

**Tweet 1 (Hook)**
Most algo traders fail not because their strategy is bad.

They fail because they run a trending strategy in a mean-reverting market.

The market has 3 states. Most people only have 1 strategy.

Here's the 5-gate Regime Detection SOP: 🧵

---

**Tweet 2 (The 3 States)**
Markets exist in exactly 3 regimes:

📈 TRENDING — momentum persists, chase it
🔄 MEAN-REVERTING — prices snap back, fade it
🌀 MIXED/CHOPPY — neither works, sit out

The fatal error: using the same strategy for all 3.

---

**Tweet 3 (G0: Calculate)**
Gate 0: Calculate 2 indicators

trend_strength = |close[-1] - close[-N]| / ATR(N)
→ measures momentum vs noise

mr_score = stdev(returns) / mean(|returns|)
→ measures volatility concentration

No guessing. Just math.

---

**Tweet 4 (G1: Classify)**
Gate 1: Classify the regime

trend_strength > 0.054 → TRENDING
mr_score > 0.25 → MEAN-REVERTING
Neither → MIXED

Critical: don't try to predict regime shifts.
Only diagnose the current state.

Prediction = ego. Diagnosis = edge.

---

**Tweet 5 (G2: Route)**
Gate 2: Route to the right strategy

TRENDING → DualMA (follow momentum)
MEAN-REVERTING → BollingerMR (fade extremes)
MIXED → SKIP

The hardest part: doing nothing in MIXED.

No edge = no action. Inaction IS the trade.

---

**Tweet 6 (G3: Validate)**
Gate 3: Verify historical performance in THIS regime

Check 3 numbers (regime-subset only, not full sample):
• Sharpe ratio > 0.5
• Win rate > 35%
• Recent / historical Sharpe > 60%

Full-sample stats hide regime decay. Always subset.

---

**Tweet 7 (G4: Failure Conditions)**
Gate 4: Define regime failure BEFORE entering

Set hard exit triggers:
• trend_strength drops below 0.02 (trend strategy)
• mr_score drops below 0.10 (MR strategy)
• 3 consecutive opposite signals
• MDD > 10%

Define exit before entry. Always.

---

**Tweet 8 (Regime Shift Behavior)**
When regime shifts mid-trade:

Don't fight it. Don't average down.
Detect MIXED → reduce size → wait for clarity.

Never run trending + MR simultaneously.
They don't diversify. They cancel out.

Fake diversification is worse than concentration.

---

**Tweet 9 (Log Everything)**
Gate 5: Record every tick

{timestamp, price, trend_strength, mr_score,
 regime, strategy_selected, signal, skipped_reason}

Why? Post-hoc regime distribution analysis.
Kill condition audit trails.
Strategy switch decision records.

You can't improve what you don't measure.

---

**Tweet 10 (Common Errors)**
The 4 mistakes that kill accounts:

❌ Full-sample Sharpe (hides regime decay)
❌ Force-trading MIXED (no edge = negative EV)
❌ No regime-fail conditions (rides through shifts)
❌ Trend + MR simultaneously (correlated = fake hedge)

All 4 are solved by following the SOP in order.

---

**Tweet 11 (Self-Test)**
Quick test: BTC data shows

trend_strength = 0.082 (> 0.054)
mr_score = 0.18 (< 0.25)
Recent/historical Sharpe = 90%

Correct routing: TRENDING → DualMA → execute signal
Regime-fail set: trend_strength < 0.02 → stop

---

**Tweet 12 (Close)**
The market doesn't care about your strategy.
It cares about whether your strategy fits its current structure.

Detect first. Route second. Execute third.

SOP #07 complete.

Full series:
#01 Strategy Dev → #02 Portfolio → #03 Execution → #04 Kill Decisions → #05 Career → #06 Game Theory → #07 Regime Detection
