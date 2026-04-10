# Twitter Thread — SOP #24: Portfolio Construction

**Hook:** "You spent 6 months building a great strategy. But you only run one. That's not a portfolio — it's a concentrated bet."

---

**Tweet 1 (Hook)**
You spent 6 months building a great strategy.

But you only run one strategy at 100% allocation.

That's not a portfolio — it's a concentrated bet.

Here's how to build a strategy portfolio that survives drawdowns. 🧵

---

**Tweet 2**
The fundamental mistake:

Most traders think diversification = trading more instruments.

Same strategy, 10 instruments = 1 bet, 10 times over.

Real diversification = different *architectures* running simultaneously.

(MD-120: true diversification ≠ same strategy × N instruments)

---

**Tweet 3**
**Gate 1: Pool Audit**

Before allocating capital, audit your strategy pool:

How many of your strategies can go short?

Rule: ≥30% of your strategies must be short-capable.

Why: In a sustained downtrend, all long-only strategies draw down at the same time. No diversification benefit.

---

**Tweet 4**
**Gate 2: Correlation Filter**

Don't rank strategies by Sharpe ratio.
Rank them by correlation to each other.

Add strategies in order of *lowest* correlation to existing portfolio.

If two strategies have equity curve correlation > 0.7 → they're the same bet with different labels.

Keep one.

---

**Tweet 5**
**Gate 3: Regime-Conditional Allocation**

Static allocation ignores regime.

Trending market (ATR > 30-day MA):
→ Overweight trend strategies +20%
→ Underweight mean-reversion -20%

Ranging market (ATR < MA):
→ Flip the weights

Rebalance max once per week. Not on single-day ATR spikes.

---

**Tweet 6**
**Gate 4: Anti-Martingale Rule**

Never increase allocation to a strategy *because* it's in drawdown.

The implicit assumption: "It's due for a win."

That assumption is only valid if the edge is intact AND the loss is random variance — not regime breakdown.

If you can't prove both, hold allocation flat.

---

**Tweet 7**
**Gate 5: Tail Position Cap**

Hidden risk in every portfolio: outlier position sizes born from "conviction."

Rule: No single position > 2× your average position size over last 90 trades.

Conviction belongs in strategy selection.
Sizing should be mechanical.

---

**Tweet 8**
Self-test:

You run 3 strategies:
- DualMA (long-only, trending)
- RSI Mean-Reversion (neutral, ranging)
- Breakout (long-only, trending)

Pool audit: 0/3 short-capable → FAIL
Correlation: DualMA + Breakout likely >0.7 → FAIL

Do not go live. Fix structure first.

---

**Tweet 9**
The mental model:

The edge lives in the *strategy*.
The survival lives in the *portfolio structure*.

You can have a positive-EV strategy and still blow up your account — if you're over-concentrated in one regime, one direction, one architecture.

---

**Tweet 10**
The 5-gate checklist:

G1: ≥30% short-capable strategies
G2: No strategy pair with correlation >0.7
G3: Regime-conditional allocation (ATR-based)
G4: No size increase during drawdown
G5: No position >2× average size

Pass all 5 before capital deployment.

---

**Tweet 11**
Most people never get to portfolio construction because they're still optimizing their single strategy.

The trap: one more backtest will fix it.

The reality: a mediocre portfolio of 3 uncorrelated strategies beats a perfect single strategy in live markets.

---

**Tweet 12 (CTA)**
This is SOP #24 from my trading system series.

If this was useful:
→ Repost to reach traders still running single-strategy portfolios
→ Follow for SOP #25

Full framework: building the system that runs the strategies.

---

**Metadata:**
- Series: Edward's Trading SOPs
- Backing DNA: MD-35, MD-85, MD-87, MD-120, MD-38, MD-33, MD-28
- Estimated post date: May 25, 2026
- Hook score: TBD after post
