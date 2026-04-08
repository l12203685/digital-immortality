# Twitter Thread — SOP #26: Walk-Forward Validation Protocol

**Hook (Tweet 1):**
Your backtest looks great.

But did you test it on data it never saw?

Most traders optimize on 100% of history, then wonder why live results diverge.

Walk-forward validation is the only honest test.

Here's the 5-gate protocol: 🧵

---

**Tweet 2:**
The core mistake: fitting the past instead of surviving the future.

A backtest that only passes in-sample tells you nothing.

You need out-of-sample proof — data the strategy never touched during development.

Walk-forward is how you get it.

---

**Tweet 3:**
G0: Lock structure before optimization.

Write this sentence first:
"This strategy profits by [mechanism] in [regime] using [signal] with [exit]."

Can't write it? Stop.

No optimization until the structure is named. Parameters are variables. Structure is constant.

---

**Tweet 4:**
G1: IS/OOS split.

- IS = first 70% of data (optimize here)
- OOS = last 30% (never touch until final test)
- Walk-forward = 6 rolling windows minimum

Each window: optimize on IS slice → test on next OOS slice → record.

Fewer than 6 windows? Get more data.

---

**Tweet 5:**
G2: The 60% Sharpe gate.

For each walk-forward window:
OOS Sharpe ≥ 60% of IS Sharpe = PASS

Need ≥60% of windows to pass.

4/6 windows pass → CONDITIONAL GO (50% size)
3/6 windows pass → FAIL → examine structure, not parameters

---

**Tweet 6:**
G3: Regime decomposition.

Break OOS results by regime: trending / mean-reverting / event.

Target-regime Sharpe ≥ 1.0 → PASS
Non-target regime degradation → expected, needs regime gate

Minimum 90 trades per regime slice before calling it confirmed.

---

**Tweet 7:**
G4: Parameter stability.

Sweep ±30% from your optimized values. Plot Sharpe.

Stable: <20% Sharpe degradation across the range → PASS
Fragile: cliff-edge at exact parameter → curve-fit → FAIL

A strategy that only works at one parameter set has no structural edge.

---

**Tweet 8:**
G5: Write the deployment contract.

Before the first live tick:
```
Strategy: [name]
Parameters: [list]
Kill conditions: MDD>[X]%, WR<[Y]% after [N] trades
Review date: [90 days]
```

Kill conditions written before entry. Not after the loss.

---

**Tweet 9:**
Self-test: DualMA(10,30) BTC daily.

6 windows. Results: 5/6 pass (83%). Target-regime Sharpe = 1.3. Parameter sweep stable (±15% Sharpe).

Decision: GO at 75% size. Kill: MDD>10%, WR<35% after 20 trades.

Notice — the decision has a number, not a feeling.

---

**Tweet 10:**
What kills most strategies before they should die:

- Optimized on 100% of data
- No regime decomposition
- Parameters cliff-edge (±5% = failure)
- No written kill conditions

These aren't bad luck. They're structural failures you can test for.

---

**Tweet 11:**
The chain:

SOP #01 (structure) → SOP #15 (backtest deception) → SOP #26 (walk-forward) → SOP #04 (kill conditions) → SOP #07 (regime gate)

Each step narrows the gap between backtest and live.

You don't need perfect. You need systematically non-deceptive.

---

**Tweet 12:**
The only honest answer to "does my strategy work?":

Not "my backtest is great."

"5 of 6 walk-forward windows pass. Target-regime Sharpe = 1.3. Parameters stable. Kill conditions written."

That's not pessimism. That's how you stay alive long enough to compound.
