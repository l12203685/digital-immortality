# Twitter Thread — SOP #30: Drawdown Recovery Protocol

**Hook:**
"You know how to enter a trade. Do you know what to do when you're 12% underwater and the next signal fires? Most traders don't. Here's the protocol." 🧵

---

**Tweet 2:**
Every blowup I've studied has the same root:
A drawdown without a pre-written protocol.

Emotion filled the gap.
Revenge trading. Averaging down. Or paralysis until margin call.

Write the rules *before* the drawdown. Not during.

---

**Tweet 3:**
G0 — Pre-Commit

Three numbers. Write them now, for every active strategy:

1. At what DD% do you cut size?
2. What evidence is required to return to full size?
3. At what DD% do you stop trading entirely?

If you can't recite them without looking → you're not ready to trade.

---

**Tweet 4:**
G1 — Three-Level Size Ladder

Equity curve vs MA_20:
- Above → full size
- 3–8% below → 50%
- 8–15% below → 25%
- >15% below → 0%

Not P&L narrative. Not gut feeling. The equity curve.
Cut mechanically. Restore with evidence.

---

**Tweet 5:**
G2 — Survival Rate Check

Before restoring size, calculate:
```
survival_rate = rolling_30d_Sharpe / historical_OOS_Sharpe
```

≥ 1.0 → eligible to restore
0.6–1.0 → hold current size
< 0.6 → drop another tier

Below 0.6 you're no longer trading your backtest. You're trading a degraded version of it.

---

**Tweet 6:**
G3 — Root-Cause Triage

Before restoring size after any drawdown, answer:

1. Regime mismatch? (strategy running in wrong market?)
2. Execution drag? (slippage exceeding break-even?)
3. Sample noise? (within expected OOS max DD?)

Wrong diagnosis → wrong fix.
Regime mismatch ≠ execution problem ≠ bad luck.

---

**Tweet 7:**
G3 Actions:

Regime mismatch → don't restore. Wait for regime flip.
Execution drag → fix order type/session/instrument first.
Sample noise → restore one tier at a time, 5-trade windows.
Unknown → quarantine strategy. Root-cause before trading again.

---

**Tweet 8:**
G4 — Return-to-Full-Size Gate

Five criteria. All must pass:
- [ ] Survival rate ≥ 1.0 for 10+ consecutive trades
- [ ] Regime matches strategy's primary regime
- [ ] Last 5 trades: WR ≥ historical WR × 0.8
- [ ] Realized slippage within break-even bounds
- [ ] Recovery within normal equity curve noise band

Restore because evidence supports it. Not because you're tired of trading small.

---

**Tweet 9:**
G5 — Post-Mortem Documentation

Every drawdown >8% or hitting G1 level 2 requires 5 lines:

1. Trigger: what caused it?
2. Detection: how fast did G1 fire?
3. Root cause: which G3 category?
4. Recovery path: what changed before restoration?
5. Protocol update: what one rule would have cut the DD by ≥30%?

---

**Tweet 10:**
Self-test: DualMA BTC, equity 8.4% below MA_20.

G1: cut to 25%.
G2: survival_rate = 0.59 → drop to 0%.
G3: BTC in low-vol regime, DualMA is trend strategy → regime mismatch.
Action: pause. Wait for trending regime. Don't restore size until regime flips.

Outcome: preserved capital instead of adding to the drawdown.

---

**Tweet 11:**
This SOP integrates with:
- SOP #27 (Regime Detection) → G3 regime check
- SOP #28 (Execution & Slippage) → G3 execution drag check
- SOP #29 (Strategy Monitoring) → G1 equity curve trigger, G2 survival rate
- SOP #04 (Kill Decision) → G4 final kill if recovery gate fails repeatedly

---

**Tweet 12:**
Drawdown is not failure.

Trading full size through a drawdown without a protocol is.

Pre-commit your rules. Cut by the curve. Triage before restoring. Return on evidence.

SOP #30: Drawdown Recovery Protocol — the five gates between a losing streak and a blown account.
