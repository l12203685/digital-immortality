# Publish Thread — SOP #31 Parsimony & Complexity Budget Protocol

**Hook tweet:**

"Your strategy has 4 parameters. Is that too many?

Wrong question.

The right question: how many OOS trades do you have per degree of freedom?

If you can't answer that, your strategy is a curve fit waiting to blow up."

---

**Thread:**

1/ Most traders add parameters to fix backtest problems.
   Each fix adds a degree of freedom.
   Each degree of freedom needs evidence to support it.
   You're borrowing against OOS trades you haven't collected yet.

2/ Complexity ≠ parameter count.
   Complexity = degrees of freedom ÷ OOS trades.
   A 10-parameter strategy with 2,000 OOS trades is leaner than a 3-parameter strategy with 15.

3/ G0: Write the mechanism sentence before any parameter exists.
   "This strategy makes money because ____."
   No numbers. No indicator names. Pure structural logic.
   If you can't write it: you have a curve-fit, not a strategy.

4/ G1: Count your degrees of freedom.
   P = tunable parameters
   B = conditional branches
   I = indicators used
   DoF = P + B + I

5/ G2: Parsimony gate.
   Required OOS trades ≥ DoF × 10.
   5 degrees of freedom = 50 OOS trades minimum.
   10 DoF = 100 trades. 20 DoF = 200 trades.
   Below this ratio? You don't have evidence. You have hope.

6/ G3: Simplicity stress test.
   Remove the weakest parameter. Re-run OOS.
   <15% Sharpe drop = decorative parameter → remove permanently.
   >30% drop = load-bearing → keep, but document exactly why.
   If you can't explain it from your mechanism sentence: delete it.

7/ G4: Cross-regime or cross-asset validation.
   Same parameters. No refit. Different period or correlated asset.
   OOS Sharpe ≥ 60% of IS Sharpe → ROBUST.
   Passes on 1/3 only → CONDITIONAL: 50% size, document the condition.
   Fails all → period-specific artifact → back to G0.

8/ Self-test: DualMA BTC, SMA(10)/SMA(30), ATR stop.
   G0: "Momentum persists when short-term trend exceeds long-term trend." ✓
   G1: DoF = 5. G2: 200 OOS trades = 40× coverage ✓
   G3: ATR stop load-bearing (50% degradation) → keep, documented.
   G4: ETH cross-asset 62% OOS coverage → ROBUST.
   Result: DEPLOY full size.

9/ Common failure: "But I only have 3 parameters."
   Doesn't matter if your OOS sample is 18 trades.
   3 DoF × 10 = 30 minimum. 18 < 30.
   You have insufficient evidence for even a simple strategy.
   Gather more OOS before deploy.

10/ The deployment contract (G5):
    Write before first tick:
    - Mechanism sentence
    - DoF count
    - OOS coverage ratio
    - Removed decorative parameters
    - Kill condition (non-negotiable)
    Any blank field = wait.

11/ Complexity is debt.
    You borrow it from future OOS evidence.
    Most strategies go live before the debt is paid.
    The market collects it for you.

12/ SOP #31 rule:
    Earn your parameters with OOS trades before going live.
    One sentence mechanism. Parsimony gate. Stress test. Cross-validate.
    Then — and only then — first tick.
