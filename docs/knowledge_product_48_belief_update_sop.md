# SOP #48 — Bayesian Belief Update Protocol

> Branch 3 — 持續學習 / Branch 2 — 行為等價
> Created: 2026-04-09 UTC (cycle 209)
> Domain: 3 (持續學習) + 2 (行為等價)
> Backing MDs: MD-7, MD-40, MD-109, MD-157, MD-1

---

## One Claim

Most people don't change their minds — they negotiate with new information until it confirms what they already believed. That's not updating. That's defending. Five gates to tell the difference — and fix it before the wrong belief costs you real capital.

---

## Why This Matters

Belief updates are not optional. Every strategy that failed, every relationship that soured, every position held too long — somewhere, a belief wasn't updated when it should have been.

The failure mode is invisible: you think you're considering new information, but you're actually just adding it to the pile without changing the output. Confirmation bias doesn't feel like bias — it feels like "carefully evaluating the evidence."

Five gates. Each one is a checkpoint where most people quietly skip the hard part.

---

## The 5-Gate Protocol

### G0: State the Current Belief Explicitly

**Before evaluating any new information, write down:**
1. What you currently believe (one sentence)
2. Why you believe it (what evidence established this belief)
3. What evidence would make you change it (pre-commitment — do this BEFORE seeing the new data)

**Kill condition**: If you cannot state the belief in one sentence OR cannot specify what would change it → your "belief" is not a belief, it's a vague orientation. No updating possible until it's made explicit.

**Why G0 matters**: Without a written prior, you'll unconsciously move your belief *after* seeing the new evidence, then feel like you "considered it." That's not Bayesian — it's post-hoc rationalization with extra steps.

**Self-test**: What do you currently believe about your strategy's edge? Can you state it in one sentence AND name the evidence threshold that would make you stop trading it?

---

### G1: Base Rate Anchor

**Before interpreting the new evidence, establish the base rate.**

The base rate is: what fraction of the relevant population experiences this outcome, independent of any specific information about this case?

- "This strategy has worked for 3 weeks" → what % of new strategies survive 3 months?
- "Three people told me this person is unreliable" → what's the false-positive rate of secondhand reports?
- "The test failed twice" → how often do good systems fail early tests due to noise?

**Formula**: `P(hypothesis) = base_rate × likelihood_ratio_adjustments`

**Kill condition**: If you don't know the base rate even approximately → your prior is probably too high. Humans systematically underweight base rates and overweight anecdote.

**Why G1 matters**: MD-109 — probability posterior update. The base rate is the starting point. Skip it and you're updating from thin air.

---

### G2: Classify the Evidence

**Rate the new information on two dimensions:**

| Dimension | Scale | Question |
|-----------|-------|----------|
| Reliability | 1–3 | How often does this type of signal correctly predict the outcome? (1=unreliable, 3=highly reliable) |
| Independence | 1–3 | How independent is this from evidence you already hold? (1=fully correlated, 3=fully independent) |

**Likelihood ratio** = reliability × independence (range: 1–9)

**Interpretation**:
- Score 1–3: Weak signal. Move prior by ≤10%.
- Score 4–6: Moderate signal. Move prior by 10–30%.
- Score 7–9: Strong signal. Move prior by 30–50%.

**Kill condition**: If multiple pieces of evidence all come from the same source (same person's opinion, same data set, same time period) → treat them as ONE piece, not many. Correlated evidence compounds the illusion of support.

**Why G2 matters**: MD-40 — most traders update based on recency (last 3 days of performance) rather than signal reliability. The calendar date of the evidence is not its strength.

---

### G3: Compute the Revision

**Update formula (simplified)**:
```
new_belief = old_belief + (evidence_score / 9) × move_direction × revision_cap
```

Where:
- `evidence_score` = G2 likelihood ratio (1–9)
- `move_direction` = +1 (confirms) or -1 (disconfirms)
- `revision_cap` = maximum one-step movement you'll allow (default: ±30% for most beliefs, ±10% for high-conviction positions you've held >6 months)

**Anti-anchoring rule**: If evidence score ≥ 7 AND disconfirms a belief you've held >1 year → cap revision at 30% per event, but schedule a re-evaluation in 14 days. Do not move 100% in one step. Sudden full reversals are almost always emotional, not Bayesian.

**Write the updated belief explicitly**: "I previously believed X with 70% confidence. New evidence (score=7) moves me to 55% confidence. Still above 50% → position unchanged, but monitoring threshold lowered."

---

### G4: Translate Belief to Action

**Belief updates without action changes are theater.**

For every belief update, ask: "What action was I taking based on the old belief? Does the new belief require a different action?"

| Old P | New P | Action change? |
|-------|-------|---------------|
| >70% | 55–70% | Reduce size. Not exit. |
| >70% | <50% | Exit or reverse. Depends on cost. |
| 50% | 65% | Add to position if originally underweighted. |
| 30% | 45% | Still below threshold — no action, but reduce confidence in the "no" position. |

**Kill condition**: If the action is "monitor closely" with no concrete trigger → this is not an action change. Define the exact signal that triggers the next action before leaving G4.

---

### G5: Anti-Reversal Gate

**After completing G0–G4, run one final check:**

1. Is this update reversing a belief you formed in the last 48 hours? → If yes, STOP. Likely reacting to noise. Wait 48h and re-evaluate.
2. Is this update reversing a belief you've held for >1 year on evidence scored ≤5? → If yes, STOP. The prior is load-bearing. Request stronger evidence.
3. Are you updating because the new information is genuinely informative, or because it's recent and salient? → Apply the "5-day newspaper test": would this evidence matter if you read it in a 5-day-old newspaper?

**Kill condition**: If you can't pass the anti-reversal gate → do NOT update. Flag the question for 48h timeout.

---

## Self-Test: Apply the Protocol Now

**Scenario**: You've been paper-trading a system. It's been SHORT on BTC for 73 ticks, P&L=+$0.693. Three people in your trading chat say "BTC looks like it's forming a reversal, smart money is going LONG."

Apply the 5 gates:
- **G0**: Current belief: "DualMA_10_30 SHORT signal is valid for current MIXED regime." Evidence: 73 ticks of MIXED regime, DualMA signal intact. Would change if: regime flips to TRENDING or kill conditions trigger (MDD>10%, WR<35%, PF<0.85).
- **G1**: Base rate: % of "BTC reversal calls" in trading chats that are correct within 7 days ≈ 30–40% (most fail; people call reversals far too early). Starting prior stays at 70% "SHORT valid."
- **G2**: Three opinions from same chat = ONE evidence unit, reliability=1 (anecdote), independence=1 (correlated). Score=1. Weak.
- **G3**: Move = (1/9) × −1 × 30% = −3.3% confidence reduction. New P("SHORT valid") = 67%. Still above 50%.
- **G4**: Action: Position unchanged. But lower monitoring threshold: flag if DualMA flips or price moves >2% in 1h.
- **G5**: No reversal in last 48h. Prior held >30 ticks. Evidence score=1. Gate passes — correct to NOT update meaningfully.

**Verdict**: No action change. Three opinions in a chat do not override a 73-tick systematic signal. This is what G1–G2 are for.

---

## Kill Conditions Summary

| Gate | Kill Condition | Action |
|------|---------------|--------|
| G0 | Cannot state belief in 1 sentence or specify falsifiability | Write it before proceeding |
| G1 | No base rate estimate available | Assume base rate is lower than intuition says |
| G2 | All evidence from same source | Count as 1 data point regardless of volume |
| G3 | Belief >1yr + disconfirming + score ≤5 | Cap revision at 10%, schedule 14d re-eval |
| G4 | "Monitor closely" with no trigger | Define the exact trigger or don't call it an action |
| G5 | Update reverses 48h-old belief OR salient-but-not-informative | 48h timeout |

---

## Why This Belongs in Digital Immortality

The digital twin must update beliefs the same way the person does — not more, not less.

Edward's belief update pattern (from behavioral DNA): EV-first, posterior revision on new evidence, high skepticism for correlated evidence, anti-anchoring on high-conviction positions. The 5-gate protocol formalizes this. Any future agent reading the DNA can run this protocol and produce the same update the person would.

This is what Route 2 behavioral equivalence means in practice: not just matching the output, but matching the *reasoning path* that produced it.

---

*SOP #48 | Domain: 3 (持續學習) + 2 (行為等價) | Backing MDs: MD-7, MD-40, MD-109, MD-157, MD-1*
