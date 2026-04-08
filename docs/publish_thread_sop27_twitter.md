# Twitter Thread — SOP #27: Regime Detection & Strategy Rotation

**Hook:**
> "Your strategy isn't broken. You're running it in the wrong market."
>
> Most traders lose not because their edge disappeared — but because their regime changed and they didn't notice.
>
> Here's the root-level SOP that every other framework depends on 🧵

---

**Tweet 2:**
Markets exist in 3 states. No strategy beats all 3.

🔀 Trend (scissor) → momentum wins
🔀 Ranging-divergent (rock) → breakout/MR edges
🔀 Ranging-convergent (paper) → compression/vol selling

Portfolio audit question: "On what day would ALL my strategies lose simultaneously?"

---

**Tweet 3:**
Gate 0: Label the regime before any decision.

Tool: ATR percentile vs trailing 252 days

• >70% → HIGH volatility → trend window
• 30–70% → NORMAL → balanced sizing
• <30% → LOW → mean-reversion / compression

"Feels like a trending market" doesn't count. The number does.

---

**Tweet 4:**
Gate 1: Strategy–regime match check.

Running mean-reversion in a HIGH-vol regime?
→ Hold. Accept small P&L. Don't force the trade.

Running trend-following in LOW vol compression?
→ Minimize size. Wait for regime change.

No regime signal = leverage amplifies noise, not alpha.

---

**Tweet 5:**
Gate 2: Optimal leverage = f(regime). Not fixed.

| Regime | Leverage |
|--------|----------|
| HIGH (trend confirmed) | 1.0× → 1.5× |
| NORMAL | 1.0× |
| LOW (compression) | 0.5× → 0.8× |

Override: if equity curve drops below 1.5σ Bollinger → force equal-weight regardless of ATR.

The equity curve sometimes knows before ATR does.

---

**Tweet 6:**
Gate 3: Rotate on regime change, not on P&L.

Rotation trigger:
• ATR_pct crosses regime boundary
• AND equity curve not in Warning/Stop state

Do NOT rotate because:
❌ "This strategy has been losing"
❌ Calendar dates
❌ News sentiment

Regime change is the signal. P&L is the noise.

---

**Tweet 7:**
Gate 4: Rolling OOS recalibration.

Rolling WFA over-weights recent data by design.
Mitigation: run 3 different window lengths (60/90/120 days).

All 3 converge? → Regime-robust. Proceed.
All 3 diverge? → Regime in transition. Cut size 30% until convergence.

---

**Tweet 8:**
Annual structural check: storm ratio.

Storm ratio = annual P&L ÷ max drawdown.

If this year's ratio drops >30% below historical mean:
→ Regime has structurally shifted.
→ Recalibrate ALL leverage thresholds.
→ "It's been a hard year" is not a diagnosis. The ratio is.

---

**Tweet 9:**
Self-test:
BTC, ATR_pct = 82%, equity curve +1.2σ, trend-following strategy active.

G0: HIGH vol regime ✓
G1: Trend matches HIGH ✓
G2: Leverage = 1.3× ✓
G3: No rotation trigger ✓
G4: WFA windows converging ✓

→ GO at 1.3× leverage.

Every gate passed = confidence justified, not assumed.

---

**Tweet 10:**
The reason regime detection is SOP #27 (not #1):

You needed the other 26 SOPs to understand WHY this matters.

Now you can see:
Position sizing (SOP #25) uses regime-conditional leverage.
Portfolio construction (SOP #24) routes by regime.
Strategy kill (SOP #04) checks regime-match first.

Regime = root input. Fix this and everything above it sharpens.

---

**Tweet 11:**
DNA anchors for this framework (built from 8+ years of trading conversations):

MD-14 · MD-25 · MD-26 · MD-31 · MD-32 · MD-33 · MD-75 · MD-78 · MD-105 · MD-107 · MD-118 · MD-143 · MD-181

Each one a lesson from a real market situation that left a mark.

---

**Tweet 12 (CTA):**
The full SOP #27 — Regime Detection & Strategy Rotation — is part of an open-source trading system built from 327 micro-decisions distilled from 9 years of trading.

If you want the framework that sits under the framework → follow for SOP #28.

🔁 Retweet if you've ever held a losing trade because you didn't realize the regime had changed.
