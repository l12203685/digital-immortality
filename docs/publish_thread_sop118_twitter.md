# SOP #118 — Twitter Thread Draft

**Posting queue**: ~Jan 2027 (after SOP #117 Bundle Arbitrage clears)

---

**Tweet 1/8**
Most automated systems have a kill switch.

Almost none have a formal reactivation gate.

So when a strategy recovers, you either miss the recovery — or re-enter too early and compound the original loss.

SOP #118: DualMA Reactivation Protocol.

🧵

---

**Tweet 2/8**
The problem:

You killed DualMA_10_30 at PF=0.53.
6 months later it flips LONG.

Your instinct: "it recovered, re-enable it."

Wrong.

The kill was systematic evidence. One signal flip is not counter-evidence.

You need a gate — not a gut check.

---

**Tweet 3/8**
G0: Signal legitimacy.

Was that signal from live data or synthetic bars?
Tick 1-2 after engine restart?
Does it persist across 2 consecutive live ticks?

A single-bar signal in a recovering strategy is noise.
Two consecutive live ticks is the minimum for legitimacy.

---

**Tweet 4/8**
G1: Cooling period.

≥5 cycles from signal appearance before assessment.

Not optional.

Reasoning: a premature re-entry during the "bounce" phase of a broken strategy compounds the original loss. The cooling period enforces inaction bias when it matters most.

---

**Tweet 5/8**
G2: Regime flip check.

The strategy was killed in a specific regime.
If the regime hasn't changed — the edge hasn't changed.

MIXED → MIXED with a new signal direction = inconclusive.
TRENDING-UP confirming the LONG = actual evidence.

Regime context matters more than signal direction.

---

**Tweet 6/8**
G3: Forward-walk PF.

Don't use cumulative PF. It's contaminated by historical losses.

Run a clean 50-tick window from signal appearance.
Threshold: ≥1.2 (not just ≥0.8).

The strategy was killed at 0.53. You need evidence of genuine recovery, not noise bounce.

---

**Tweet 7/8**
G4+G5: Reactivate at 50% size. Monitor 20 ticks.

If PF drops below 0.8 again: re-kill immediately.
No second assessment for ≥30 cycles.

Post-reactivation monitoring is the final safety net.
You're testing whether the recovery was real.
The system decides — not you.

---

**Tweet 8/8**
Two failure modes:

1. Premature reactivation → compound drawdown → system discredited
2. Permanent exclusion → miss genuine recovery → EV lost at scale

The gate sequence solves both.

Kill/reactivation is the highest-stakes decision in an automated system.
SOP #118 is the protocol.

SOP #01–#118 complete. ✅
