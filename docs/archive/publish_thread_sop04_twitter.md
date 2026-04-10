# Publish Thread — SOP #04: Strategy Kill Decision Tree
# Status: READY TO POST
# Platform: Twitter/X
# Format: 12-tweet thread

---

**Tweet 1 (hook)**
Most traders destroy their account one of two ways:

1. Keeping a dead strategy (sunk cost)
2. Killing a live strategy (recency bias)

Both are the same mistake: emotional override of systematic process.

Here's the decision tree that prevents both.

SOP #04: Strategy Kill Decision Tree 🧵

---

**Tweet 2 (Node 0 — triggers)**
First rule: DON'T run this tree unless triggered.

Run only when:
• ≥5 consecutive losing live trades
• Drawdown ≥15% from equity peak
• edge_ratio (trailing 30) drops below 1.2
• OOS Calmar <0.3 (trailing 90 days)
• Signal frequency <30% of historical avg

Resist urge to "review" during normal variance.

---

**Tweet 3 (Node 1 — sample size)**
Node 1: How many live trades?

<30 trades → SUSPEND JUDGEMENT
• Reduce to 25% position
• Come back at 30
• Short-term sample = variance not technique (MD-29)

30–100 → proceed with caution
>100 → proceed with full confidence

Sample size is the precondition to any verdict.

---

**Tweet 4 (Node 2 — regime match)**
Node 2: Has market regime changed since strategy was built?

Check:
• ATR now vs backtest ATR (>2× = high-vol regime shift)
• Is this strategy type (trend/MR) currently favoured?
• Correlation to dominant factor

Regime shifted temporarily → pause 30 days, don't kill
Regime shifted structurally → proceed to kill assessment

---

**Tweet 5 (Node 3 — edge integrity)**
Node 3: Is the edge still in the data?

Run on last 30 live trades:
edge_ratio = mean(MFE) / mean(MAE) × √N

≥1.5 → Edge intact. Results = variance. DO NOT KILL.
1.2–1.5 → Edge degrading. Cut leverage 50%, review in 20 trades.
<1.2 → Proceed to kill assessment.

Also check: is only Long or only Short failing? That's a routing issue, not strategy failure.

---

**Tweet 6 (Node 4 — structural failure)**
Node 4: Has the underlying premise been falsified?

When you built this strategy, you defined what it captures.
Test each component now:

• Does signal still find edge? (re-backtest last 12mo OOS)
• Is pattern still positive in IS period?
• Is real slippage <2× modelled?
• Is liquidity still >30% of backtest period?

---

**Tweet 7 (Node 4 scoring)**
Count falsified premise components:

0–1 falsified → Not a kill. Reduce size, add filter, retest.
2–3 falsified → High-probability kill. Proceed to sanity check.
4 falsified → Kill immediately, no debate.

The tree forces structural reasoning before emotion can enter.

---

**Tweet 8 (Node 5 — anti-capitulation guard)**
Node 5: Pre-kill sanity check. Answer 3 questions:

1. Would I build this strategy TODAY?
   YES → don't kill, it's variance.

2. Is there a specific testable fix?
   YES → implement it, give 30 trades, then re-evaluate.

3. Am I killing because of a bad week, or because the premise is falsified?
   Bad week → reset size only. Premise falsified → kill confirmed.

---

**Tweet 9 (Node 6 — kill protocol)**
Node 6: Kill confirmed. Execute in order:

1. Close all positions immediately
2. Remove from live portfolio (no "paper watch")
3. Write 3-sentence post-mortem: premise failed / signal / build error
4. Re-run greedy portfolio addition (SOP #02) with strategy removed
5. Archive, don't delete → strategies/archived/ + post-mortem note
6. If portfolio now <3 uncorrelated strategies → start SOP #01 immediately

---

**Tweet 10 (Node 7 — resurrection)**
Node 7: Can a killed strategy come back?

Yes, but strict conditions:
• Market regime returns to original profile
• Fresh 6-month OOS backtest shows edge_ratio ≥1.5
• No parameter changes — resurrect exact original parameters
• Start at 25% size, graduate after 30 live trades pass Node 3

Killed ≠ dead forever. Killed = suspended until conditions are met.

---

**Tweet 11 (self-test example)**
Self-test scenario:

DualMA strategy. 45 live trades. Last 12 = losing. Drawdown 12%. ATR now 1.4× backtest.

• Node 1: 45 trades → proceed
• Node 2: ATR 1.4× (not 2×), same regime → unchanged
• Node 3: edge_ratio = 1.35 → degrading

Verdict: DO NOT KILL. Cut leverage 50%. Review in 20 trades.

---

**Tweet 12 (close + series summary)**
The full SOP series is now complete:

#01 Strategy Development — how to build
#02 Portfolio Construction — how to combine
#03 Execution & Sizing — how to enter
#04 Kill Decision Tree — how to exit

Four SOPs. One system. No emotion in the loop.

The tree is free. The discipline to run it when it hurts is not.
