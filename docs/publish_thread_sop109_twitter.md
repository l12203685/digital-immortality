# Twitter Thread — SOP #109: Strategy Re-Activation Gate Protocol

> Status: DRAFT | Created: 2026-04-10T UTC | Queue: Oct 23

---

**Tweet 1 (Hook)**
Your trading bot killed a strategy.

When do you turn it back on?

Most traders: "it's been a while, let's try"

The gate protocol: 🧵

---

**Tweet 2**
Kill ≠ permanent.

Kill = conditions weren't met.

Conditions change → re-activation is possible.

But only with evidence. Never with time alone.

---

**Tweet 3**
G0: Audit the kill reason first.

PF < threshold ≠ logic bug.

Regime mismatch ≠ structural failure.

Different kill causes → different recovery paths.

Don't skip this step.

---

**Tweet 4**
G1: Regime alignment.

Trend-following strategy → only activate in trending regime.

Mean-reversion strategy → only activate in ranging regime.

Wrong regime = guaranteed re-kill.

---

**Tweet 5**
G2: Paper evidence before live capital.

Shadow run minimum:
- PF ≥ kill_floor × 1.2 (20% margin)
- WR ≥ kill_floor × 1.1 (10% margin)
- MDD ≤ kill_ceiling × 0.75
- Sample: ≥5 trades

Not one metric. All three.

---

**Tweet 6**
G3: Reset the window. Not the kill count.

Kill count = strategy mortality record.
Kill window = evaluation period.

These are different.

Resetting kill count = erasing structural weakness evidence.

Never do it.

---

**Tweet 7**
G4: Capital floor before re-activation.

You need enough capital to absorb:
→ Another kill cycle
→ On top of current drawdown
→ With 2× buffer

Barbell principle: protect the core, only risk the marginal.

---

**Tweet 8**
G5: Probationary re-activation.

First window after kill:
- Thresholds tightened 20%
- Early-warning checkpoint at half-window
- New kill in first window = STRUCTURAL_WEAK → 3-window cooldown

Trust but verify. Especially after a kill.

---

**Tweet 9**
The self-test:

DualMA killed: PF=0.53 in mixed regime
Regime shifts to trending
Shadow run: PF=1.12, 8 trades

G0✓ G1✓ G2✓ G3✓ G4✓ → Re-activate

Kill was regime-specific. Recovery is regime-specific.

---

**Tweet 10**
Anti-pattern: time-gated re-activation.

"It's been 10 cycles, let's try again."

Time is not evidence.

Conditions are evidence.

---

**Tweet 11**
Anti-pattern: hope-gated re-activation.

"BTC is going up, maybe it'll work now."

Narrative is not data.

Shadow run PF is data.

---

**Tweet 12 (Close)**
Kill → shadow → gate → re-activate.

The cycle that turns kill logs into mortality tables.

Each kill teaches you: which strategies die from which causes, and which recover.

SOP #109: full gate protocol →
[link]
