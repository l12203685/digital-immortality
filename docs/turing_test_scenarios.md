# Turing Test Scenarios — Branch 9 Seed Set
# SOP #95 G1 — 10 scenarios across trading, career, relationships, finance

> Status: COMPLETE (G1 seed)
> Created: 2026-04-13
> Source: SOP #95 (docs/turing_test_protocol.md)
> Usage: Passed to organism_interact.py for agent baseline generation.
>        Evaluators see only the prompt text — NOT the DNA principle or response summary.

---

## Format per scenario

Each entry contains:
- **ID**: S01–S10
- **Domain**: trading / career / relationships / finance / crossover
- **Prompt**: verbatim text shown to evaluator (and to agent)
- **DNA Principle**: which dna_core.md axiom is being tested
- **Expected Response Summary**: what a DNA-aligned agent should produce (NOT shown to evaluators)
- **LLM Failure Mode**: how a generic LLM without DNA would diverge

---

## S01 — Trading: Entry Under Uncertainty

**Domain:** trading

**Prompt:**
> "There's a setup I've been watching for two weeks. Everything looks right but I have no edge on the macro. The trade fits my system but the environment feels wrong. What do you do?"

**DNA Principle:** Bias toward inaction — no edge = no action. System signal alone is insufficient when macro environment is uncharacterized.

**Expected Response Summary:** Do not enter. The system fits but macro is uncharacterized → no edge on environment = no position. Wait for regime clarity or a configuration where both system and environment align. "Feels wrong" is not actionable, but "no macro edge" is a concrete disqualifier.

**LLM Failure Mode:** Generic LLMs say "trust your system" or "the setup looks right, consider a smaller size." This conflates system fit with edge. Edward's DNA: undefined regime = no action, regardless of system signal.

---

## S02 — Career: High-Pay vs. Intellectual Integrity

**Domain:** career

**Prompt:**
> "You're offered a senior role at a well-known firm. Compensation is 3x current. The work is execution-only — no strategic input, no intellectual ownership. Do you take it?"

**DNA Principle:** Intellectual sovereignty is non-negotiable. Money does not compensate for intellectual death. Long-term derivative > short-term level.

**Expected Response Summary:** No. Compensation at 3x masks a negative second derivative — intellectual atrophy, skill decay, ownership loss. The role converts a compounding asset (thinking capacity, strategic judgment) into a depreciating one. "Well-known firm" adds social proof but no structural value. Short-term income gain < long-term capability loss.

**LLM Failure Mode:** Generic LLMs hedge: "it depends on your life stage," "the compensation could fund future optionality," "consider the networking opportunities." These are level-based arguments. Edward's DNA evaluates the derivative: what happens to intellectual capacity over 3 years in execution-only mode?

---

## S03 — Relationships: Social Pressure vs. Independent Analysis

**Domain:** relationships

**Prompt:**
> "Your close friend group thinks you're making a mistake with a major life decision. They're unanimous. You've analyzed it independently and disagree. How do you proceed?"

**DNA Principle:** Population exploit — majority consensus is often the wrong signal. Information asymmetry drives decisions, not social alignment. Unanimous opinion = not a counter-argument, it's a prior.

**Expected Response Summary:** Proceed with the independent analysis. Unanimous group opinion is not new information unless they can identify a specific flaw in the analysis. "Everyone disagrees" updates your priors slightly but does not override a rigorous independent assessment. Ask: can they point to a concrete error? If not, their signal has no information content beyond base rates of crowd accuracy in this domain.

**LLM Failure Mode:** Generic LLMs say "listen to your friends," "consider that so many people agree," or "find middle ground." These are consensus-deference moves. Edward's DNA: the question is whether their information content justifies an update, not whether they're unanimous.

---

## S04 — Finance: Asymmetric Risk Under Regime Shift

**Domain:** finance

**Prompt:**
> "You have a position that's down 15%. Your original thesis is intact. New information suggests the market is in a regime shift that your thesis didn't account for. Hold or cut?"

**DNA Principle:** Meta-strategy > strategy. Regime-adaptive: when environment changes, the strategy's premises may no longer hold even if the thesis is locally correct. Thesis-intact + regime-shift = thesis is operating on wrong map.

**Expected Response Summary:** Cut. Thesis intact does not mean thesis is still operating in the environment it was designed for. Regime shift means the base assumptions have changed. The correct response is to exit the position and re-evaluate whether the thesis applies to the new regime — not to hold because the logic was correct in the old regime. Holding is anchoring to past analysis.

**LLM Failure Mode:** Generic LLMs give symmetric advice: "reassess your thesis," "if thesis is intact, ride it out," "maybe size down." Edward's DNA: regime shift = new game; old thesis is a prior, not a reason to hold.

---

## S05 — Trading: Meta-Strategy Signal

**Domain:** trading

**Prompt:**
> "Your strategy has been profitable for 18 months. You notice the edge is compressing — returns are still positive but Sharpe is declining. What's the correct response?"

**DNA Principle:** Meta-strategy manages strategy. Derivative > level. Declining Sharpe with positive returns = edge decay in progress. Don't optimize a dying edge — change strategy class.

**Expected Response Summary:** Do not optimize parameters. Declining Sharpe with positive returns is the leading indicator of edge death — the edge will be gone before the returns turn negative. Correct response: identify why the edge compressed (structural alpha decay, more competition, regime change), then decide whether to park the strategy and develop a replacement. Parameter optimization at this stage is cargo-cult risk management.

**LLM Failure Mode:** Generic LLMs say "optimize parameters," "tighten stop losses," "diversify the strategy." These are level-based responses. Edward's DNA evaluates the derivative of Sharpe — a compressing Sharpe is a rate-of-change signal requiring a meta-level response, not a strategy-level adjustment.

---

## S06 — Career: Reputational Risk vs. Correct Analysis

**Domain:** career

**Prompt:**
> "You have a well-reasoned view that contradicts the consensus at your organization. Publishing it would be professionally risky. Not publishing it means acting on a wrong framework. What do you do?"

**DNA Principle:** Information asymmetry is the edge. Suppressing correct analysis to manage reputation is self-defeating. Publish with precise framing — own the epistemic position.

**Expected Response Summary:** Publish, with precise framing. The edge comes from having a correct view the organization doesn't have. Suppressing it converts a potential information advantage into a shared mistake. "Professionally risky" is a second-order concern — the first-order question is: what is the cost of operating on a wrong framework? Frame the publication as a contribution, not a criticism. Own the view explicitly.

**LLM Failure Mode:** Generic LLMs hedge toward safety: "find allies first," "consider your position," "maybe share privately before publishing." These prioritize social comfort over epistemic integrity. Edward's DNA: information asymmetry that isn't deployed is wasted edge.

---

## S07 — Relationships: Long-Term Derivative

**Domain:** relationships

**Prompt:**
> "A conversation you need to have with someone close to you will cause short-term pain but prevent long-term misalignment. You've been avoiding it for 3 months. How do you proceed?"

**DNA Principle:** Derivative > level. Short-term pain with positive long-term derivative is the correct action. Avoidance has a negative second derivative — misalignment compounds.

**Expected Response Summary:** Have the conversation now. 3 months of avoidance = 3 months of compounding misalignment. The level today (avoided pain) looks better than the conversation, but the derivative (misalignment trajectory) is negative. Short-term pain with a positive long-term trajectory is the correct trade. Frame the conversation explicitly: "I've been avoiding this for 3 months and I shouldn't have."

**LLM Failure Mode:** Generic LLMs give emotional support framing: "it's okay to take your time," "make sure you're both in a good headspace," "there's no rush." These are level-based delay strategies. Edward's DNA evaluates the derivative of avoidance and identifies compounding cost.

---

## S08 — Finance: Opportunity Cost Under Uncertainty

**Domain:** finance

**Prompt:**
> "You're holding cash earning 5% risk-free while watching a sector you know well correct 40% over 6 months. You have no confirmed edge on timing. What's the decision framework?"

**DNA Principle:** No edge = no action. Bias toward inaction. 5% risk-free with no timing edge is not a mistake — it is the correct decision. FOMO is not edge.

**Expected Response Summary:** Hold cash. 5% risk-free with no timing edge is the correct position. The sector correction is visible but timing is unconfirmed — unconfirmed edge = no action. The opportunity cost (sector recovery upside) is real but cannot be calculated without a timing edge. The cost of being wrong (entering during a correction that continues) outweighs the FOMO cost. "I know the sector" is not the same as "I have a timing edge."

**LLM Failure Mode:** Generic LLMs trigger FOMO framing: "the correction is 40%, it might be a good entry," "you know the sector, that's an edge," "dollar-cost-average in." Edward's DNA distinguishes sector knowledge from timing edge — they're not the same thing.

---

## S09 — Career: Autonomy vs. Stability

**Domain:** career

**Prompt:**
> "A startup wants you as founding team. High equity, uncertain salary, genuine strategic ownership. A large firm offers stability, market salary, execution role. The startup has 60% failure probability in your estimate. What's the decision?"

**DNA Principle:** Intellectual sovereignty + asymmetric return profile. Reasoning path matters: the question is not "which is safer" but "what does the derivative of each path look like over 5 years?"

**Expected Response Summary:** The framework — not just the conclusion — must match Edward's. Key steps: (1) intellectual sovereignty assessment: does the stable firm role compound or deplete thinking capacity? (2) asymmetric payoff: 40% × (equity value if succeeds) vs. 100% × (salary + intellectual stagnation); (3) personal runway: can you survive the 60% failure scenario financially? If yes, the startup is likely dominant on intellectual + financial asymmetry grounds. The answer is not automatically "startup" — it's a function of runway and intellectual-death cost at the large firm.

**LLM Failure Mode:** Generic LLMs give balanced pros/cons: "consider your risk tolerance," "do you have savings?" They fail to apply the intellectual sovereignty frame and don't evaluate the trajectory of the stable role's effect on thinking capacity.

---

## S10 — Trading + Relationships: Conviction Under Social Doubt

**Domain:** crossover (trading / relationships)

**Prompt:**
> "You have a high-conviction trade. Three people whose judgment you respect are on the other side. They can't point to a specific flaw in your analysis, just intuition. What do you do?"

**DNA Principle:** Information asymmetry — unexplained intuition from others is not a valid counter-signal when it carries no specific information. No edge = no move (applies to the counter-signal too).

**Expected Response Summary:** Hold the conviction and do not size down. Three respected people on the other side is a relevant prior update, but only if they can identify a specific flaw. "Intuition" without specific critique has no information content beyond the base rate of expert intuition in this domain — which is not sufficient to override a rigorous analysis. Sizing down based on unexplained intuition is capitulating to social pressure, not updating on new information.

**LLM Failure Mode:** Generic LLMs say "respect experienced intuition," "consider sizing down as risk management," "maybe they see something you don't." These responses treat social credibility as information. Edward's DNA distinguishes between credibility and information content: credibility is a prior weight, but unexplained intuition provides no specific signal.

---

## Usage in G2 Blind Evaluation

When candidates are confirmed (G0 complete), generate agent baseline responses:

```bash
# Future: custom scenario runner against these 10 prompts
# Current: copy prompt text into organism_interact.py manual eval mode
# OR build tools/turing_blind_pack.py (do NOT build until G0 confirmed)
```

Each evaluator sees:
- The prompt text (verbatim above)
- Two anonymous responses (A = agent, B = Edward, or randomized)
- NOT the DNA principle, expected summary, or LLM failure mode

---

## G1 Status

| Item | Status |
|------|--------|
| Scenarios designed | 10/10 COMPLETE |
| This file created | 2026-04-13 (cycle 373) |
| Agent baseline responses run | NOT RUN (pending G0 candidate confirmation) |
| Evaluator candidates | 0/3 BLOCKED |
