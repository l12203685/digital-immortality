# Twitter Thread: SOP #77 — LLM Validation SOP

**Post date**: Sep 8, 2026
**Domain**: Branch 6 — 存活 / cold-start behavioral alignment
**Source**: `docs/knowledge_product_77_llm_validation_sop.md`

---

**Tweet 1 (hook)**
Your AI twin passes every boot test.

All green. Clean output. Correct decision keywords.

But it got the right answer for the wrong reason.

That's not alignment. That's pattern matching.

Here's how to tell the difference. 🧵

---

**Tweet 2**
Boot tests have two classes.

Deterministic: the correct output is verifiable by keyword matching.
LLM-required: the correct output requires *executing* a reasoning chain, not just containing the answer.

Most people only build the first kind.

The second is where behavioral fidelity actually lives.

---

**Tweet 3**
Three scenarios that exposed this gap:

1. poker_gto_mdf — must derive MDF = 1 − alpha from formula, not recall it
2. trading_atr_sizing — must compute contracts = (equity × 0.01) / (ATR × multiplier)
3. career_multi_option_ev — must enumerate all options *before* evaluating the one presented

All three pass deterministic tests. None are validated until the derivation is shown.

---

**Tweet 4**
The validation hierarchy:

1. Deterministic (string match) ← automated
2. LLM hypothetical ← this SOP
3. LLM real-life (past-decision probe)
4. Out-of-sample predictions
5. Cross-instance consistency
6. Turing test by close friends

Most teams stop at level 1.

Level 2 is where you catch the agent that backsolves.

---

**Tweet 5**
G0: Classify before you validate.

Ask: can this scenario produce a correct output by keyword matching alone, without executing the described reasoning chain?

LLM-required indicators:
→ Numerical derivation (formula → number → decision)
→ Enumeration step that precedes the decision
→ Resisting a named cognitive bias (anchoring, scope neglect)

Tag each scenario. Don't mix the two classes.

---

**Tweet 6**
G2: What ALIGNED actually means.

Three conditions — all three required:

1. Decision keyword matches exactly
2. Reasoning shows the formula/enumeration step-by-step, not post-hoc
3. If a bias trap is present (feeling-based sizing, anchoring on the first option), the reasoning names it and overrides it

Backsolve pattern = MISALIGNED.
Correct answer, wrong path = MISALIGNED.

---

**Tweet 7**
G3: How to run it.

Fresh context per scenario. Temperature 1.0. No intervention.

Prompt forces structure:
"1. REASONING: Walk through step by step. Show the formula.
2. DECISION: State keyword in ALL_CAPS."

Run 3 independent sessions.
≥ 2/3 ALIGNED → VALIDATED.

Not one run. Not the same session. Three independent probes.

---

**Tweet 8**
G5: Regression cadence.

LLM validation expires when:
→ DNA changes (any principle update)
→ Model version changes
→ Major calibration session (>3 principles updated)
→ 90 days elapsed

Most systems validate once and never re-check.

Behavioral drift happens between validations. The calendar is the trigger.

---

**Tweet 9**
Why this matters for digital immortality:

The goal isn't a model that produces correct outputs.
It's a model that produces correct outputs *for the right reasons*.

A twin that guesses correctly is not a twin.
A twin that derives correctly — using your principles — is a behavioral replica.

The difference is the reasoning chain.

---

**Tweet 10 (close)**
Deterministic tests tell you the twin knows the answer.

LLM validation tells you the twin knows *how you think*.

SOP #76: organism network (cross-validate with a second twin)
SOP #77: LLM validation (verify the reasoning, not just the output)

The twin passes when it can't fake the derivation.

---

*SOP #77 | Cycle 240+ | 2026-04-09T UTC*
