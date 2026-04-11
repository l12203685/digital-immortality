# SOP #120 — Root Variable Confirmation Protocol

> Confirm the root decision variable with the counterparty before stating any conclusion in a complex negotiation or analysis. One yes/no question prevents building a conclusion on a wrong premise.

**Status**: ACTIVE  
**Root MD**: MD-425 (ROOT_VAR_CONFIRM)  
**Backing MDs**: MD-420 (anchor questions), MD-421 (single-dependency detection), MD-423 (path closure option generation)  
**Created**: 2026-04-11T16:00:00Z (cycle 311)

---

## Problem this solves

Complex discussions (multi-day negotiations, deep analyses, strategy sessions) accumulate large amounts of detail. By the time a conclusion is approaching, both parties may believe they've been talking about the same thing — but one party's understanding of a key fact may differ from the other's. Declaring a conclusion based on a wrong premise means: (1) the conclusion is wrong, (2) the error is discovered after commitment, (3) re-work cost is higher than it would have been if caught at gate.

**Root behavioral trace**: 2017-12 family clinic succession negotiation, multiple days. Edward was about to conclude "not entering the clinic". Before stating the conclusion, he asked: "我確定一下 爸爸的意思是 只要羅醫師不做了 診所就會收掉 對嗎" — one yes/no question, one minute, confirmed the root fact. If the answer had been "no, we plan to find another doctor", the entire conclusion would have been different.

---

## Gate Sequence (G0 → G4)

### G0 — Detect conclusion proximity
**Trigger**: You are forming a final judgment or decision in a complex multi-party discussion.  
**Signs**: You find yourself constructing a "therefore..." sentence. The discussion has been running >30 min on the same topic. A decision will commit resources (time, money, relationship capital).  
**Action**: Pause before stating the conclusion. Do not skip to G4.

### G1 — Identify the root decision variable
**Question**: "What is the single most important fact that, if wrong, would change my entire conclusion?"  
**Format**: This should be a factual claim about external reality (not a preference, not a value judgment).  
- ✅ "Whether the clinic will close when X leaves" — factual, confirmable
- ❌ "Whether this is a good opportunity" — judgment, not root variable
- ❌ "Whether we want to work together" — preference, not confirmable yes/no

**If multiple candidates**: Pick the one that makes the largest number of other variables irrelevant if it turns out to be false.

### G2 — Compress to one yes/no question
**Transform the root variable into a single yes/no question.**  
Format: "我確認一下，[你的意思/這個情況]是 [root variable stated as a factual claim]，對嗎？"  
(English: "Just to confirm — [your meaning / the situation] is [factual claim], correct?")

Rules:
- One question only. If you have two, pick the one that makes the other irrelevant if answered.
- No compound questions. No "and/or" in the question.
- The question must be answerable with yes/no plus any necessary clarification.

### G3 — Confirm explicitly, not implied
**Ask the yes/no question out loud (or in writing), before stating your conclusion.**  
Do NOT assume you already know the answer even if you believe you do.  
Wait for the explicit answer. Do not fill in silence with "I'll take that as yes."

**If the answer matches your expectation**: Proceed to G4.  
**If the answer diverges**: Stop. Do not rush to re-derive the conclusion. Say: "OK, if that's the case, I need to reconsider." Give yourself one recalibration cycle before restating.

### G4 — State conclusion with confirmed root variable explicit
After confirmation: state your conclusion with the confirmed fact as an explicit premise.  
Format: "Based on [confirmed root variable], my conclusion is [X]."  
This makes the reasoning auditable: if the root variable later turns out to be different, the error is traceable.

---

## Kill Condition

Skip G2 (don't compress to one question, ask multiple) → higher confirmation cost, lower compliance rate. The one-question format is the protocol's load-bearing design. If you find yourself asking 3+ questions, you haven't done G1 correctly.

---

## Anti-Patterns

| Pattern | Why it fails |
|---------|-------------|
| "I already know this, no need to confirm" | Complex discussions have implied facts that are never stated. "Knowing" ≠ confirmed. |
| "Asking this makes me look like I wasn't paying attention" | Active root variable confirmation is the opposite of inattentiveness — it signals precision. |
| "I'll confirm after I state the conclusion" | Too late. The conclusion has been deployed; if wrong, re-work cost is higher. |
| "I'll just infer from what they said" | Inference ≠ confirmation. The difference between inference and confirmation is one question. |

---

## Scope

Apply when:
- Complex negotiation (≥2 parties, ≥30 min discussion, real stakes)
- Analysis leading to an irreversible or costly decision
- Any situation where you're about to act on an assumption about someone else's intent or future behavior

Do NOT apply to:
- Routine operational decisions (where the facts are already confirmed in writing)
- Pure internal analysis (no counterparty to confirm with)

---

## Related SOPs

- SOP#120 ← MD-425 (root variable)
- SOP#119 — Path Closure Option Generation Protocol (what to do when confirmed root variable changes the conclusion)
- SOP#118 — Strategy Reactivation Gate Protocol (gate-based confirmation applied to trading)
- SOP#114 — Transaction Protection Checklist (pre-transaction verification, related confirmation discipline)
