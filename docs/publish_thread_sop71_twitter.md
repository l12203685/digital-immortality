# Twitter Thread — SOP #71: Multi-Strategy Regime Activation Protocol

> One-claim hook: "You built 10 strategies. 1 is signaling. 9 are FLAT. Is this a feature or a bug?"

---

**Tweet 1 (hook)**
You built 10 trading strategies.

After 100 live ticks, only 1 is signaling.

The other 9 are FLAT.

Is this your regime filter working correctly?

Or have you quietly collapsed to a single-strategy portfolio?

5-gate diagnostic →

---

**Tweet 2 (the trap)**
Most traders treat ALL FLAT signals as "the market is quiet."

But there are two very different reasons a strategy goes FLAT:

1. Regime doesn't match its design → correct behavior
2. Something is broken → execution bug, dead strategy

You cannot optimize what you can't diagnose.

---

**Tweet 3 (G0 — Regime Diagnosis)**
Gate 0: Confirm FLAT is regime-correct, not model failure.

Check:
→ Is the regime score within expected band?
→ Was this strategy designed for the current regime?
→ Have kill conditions triggered? (If yes: it's already off)
→ Does its backtest FLAT rate ≥ 60%?

Scissors doesn't beat paper. That's not failure — that's design.

---

**Tweet 4 (G1 — Single-strategy audit)**
Gate 1: Single-strategy dependency audit.

If 1 strategy = 100%+ of signals for 100 consecutive ticks:

→ Pull regime distribution for those 100 ticks
→ Map each strategy's designed regime to actual regime
→ Check if uncorrelated strategies are alive but waiting
→ Flag dead strategies (FLAT across ALL regime types)

FLAT is not diversification. Waiting is. But waiting forever = broken.

---

**Tweet 5 (G2 — Activation gate)**
Gate 2: Before activating a dormant strategy, 5 conditions must pass:

1. Regime matches strategy design ✅
2. Kill conditions not triggered ✅
3. OOS backtest pass rate ≥ 60% ✅
4. Correlation with active strategy < 0.85 ✅
5. Position capacity available ✅

Never activate 2 strategies simultaneously. Activate one → observe 5 ticks → confirm → continue.

---

**Tweet 6 (G3 — Concentration protocol)**
Gate 3: Concentration Risk Protocol.

Trigger: 1 strategy = 100% of signals for 100+ consecutive ticks.

This is NOT a kill. It's a diagnostic.

→ Log the event (strategy, tick count, regime distribution)
→ Run G1 audit
→ If audit passes → "CONCENTRATION_EXPECTED" — continue
→ If audit fails → escalate to G2 activation

Quarterly: If same concentration for 3+ months → portfolio design flaw, not regime event.

---

**Tweet 7 (G4 — Rotation protocol)**
Gate 4: When regime flips, how to rotate.

Do NOT exit the current strategy. Regime change ≠ kill signal.

→ Add new strategy at 50% of normal size
→ Keep existing at 50% of normal size
→ After 5 ticks: both clean → normalize
→ After 20 ticks underperforming → deactivate + log

Rule: Only add a strategy that raises portfolio Calmar ratio. Test before rotation, not after.

---

**Tweet 8 (G5 — Revenue bridge)**
Gate 5: Why concentration risk isn't just about risk.

Single-strategy → single-regime → if that regime ends, revenue = 0.

Target:
→ 2+ strategies signaling across 2+ regimes
→ Signal concentration < 70% in any strategy (30-day window)
→ Both trading + Gumroad contributing before deadline

Diversification = survival across regime transitions.

---

**Tweet 9 (self-test)**
Self-test: Tick 106. BTC=$70,981. Regime=MIXED. DualMA=SHORT. 14/15 FLAT.

→ G0: DualMA has no regime filter (always on). FLAT from others = possibly correct.
→ G1: DualMA_RSI_filtered designed for MIXED but FLAT. Investigate RSI threshold.
→ G3: 100% concentration → log event → G1 audit → if RSI is blocking correctly → CONCENTRATION_EXPECTED
→ G5: Revenue = $0. First post is the blocker, not strategy count.

Diagnosis: System working. External loop broken.

---

**Tweet 10 (close)**
10 strategies. 9 FLAT. 1 signaling.

That's not concentration risk — that's the regime filter earning its keep.

Unless the regime has rotated and your dormant strategies haven't noticed.

5-gate check: G0 diagnose → G1 audit → G2 activate → G3 log → G4 rotate → G5 survive.

SOP #71 →
