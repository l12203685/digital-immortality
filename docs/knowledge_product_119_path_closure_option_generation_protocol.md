# SOP #119 — Path Closure Option Generation Protocol

**Domain**: Branch 2.2 (Decision Patterns — Career/Negotiation/Strategy)
**Created**: 2026-04-11T UTC (cycle 309)
**Status**: ACTIVE
**Backing MDs**: MD-423 (path closure → instant option generation); MD-421 (single-dependency structural fragility); MD-400 (domain-specific skill sunk cost); MD-07 (inaction bias)

---

## Purpose

When a path is confirmed closed (a negotiation fails to meet core conditions, a strategy is killed, a job offer falls through), the typical failure mode is one of two:

1. **Sunk-cost lingering** — continuing to invest cognitive resources in the closed path ("maybe if I explain better…", "let me try one more angle")
2. **Paralysis gap** — closing the path but not generating alternatives until "after the emotions settle"

Both failure modes waste the highest-leverage moment: the instant of closure, when the mind is fully engaged and context-loaded.

This SOP codifies MD-423 behavior: **path closure triggers immediate option generation in the same cognitive session — not after processing, not later today.**

---

## Trigger Conditions

This SOP activates when ALL of the following are true:

- T1: A path is confirmed closed. "Confirmed" = the core condition that would make the path viable has been answered NO (not "probably not" — actually NO)
- T2: The closed path had non-trivial investment (>1 month time, >significant capital, >major decision weight)
- T3: You have not yet generated a written list of alternative paths

**Examples of "confirmed closed":**
- Negotiation: the other party has given a definitive NO to your minimum core condition
- Strategy: PF < kill threshold and confirmed not noise (SOP #92 triggered)
- Career: offer rejected, or position eliminated, or company confirmed not hiring
- Project: key resource/partner confirmed unavailable for the required window

**Do NOT trigger if:** the path is "probably not going to work" but no definitive answer has been received. That is CONDITIONAL, not CLOSED.

---

## G0: Confirm the Closure is Real

Before generating alternatives, verify the closure is not premature.

**Procedure:**

1. State the core condition that would make this path viable: _______
2. Has that condition been answered definitively NO? (Y/N)
3. Is there a realistic, nameable condition that would flip the answer to YES within the relevant time window?

| Condition | Action |
|-----------|--------|
| Core condition answered YES, or conditional flip exists | NOT CLOSED — return to negotiation/waiting phase |
| Core condition answered NO, no realistic flip | CONFIRMED CLOSED — proceed to G1 |
| Unsure if definitely NO | Get one more confirmation message/data point, then return to G0 |

**Current context (example):** Clinic succession path — core condition (becoming equity shareholder with formal succession plan) confirmed NOT on offer. No realistic flip (father's intent is to close clinic after retirement, not transfer ownership). G0 PASS.

---

## G1: Immediate Option Generation (Same Session)

**Do this BEFORE leaving the current mental context.**

Set a 10-minute timer. Generate a written list of minimum 3 alternative paths. Rules:

1. Alternatives must be genuinely available to you NOW (not "maybe someday")
2. Each alternative must have at least one concrete first action you could take this week
3. Do NOT evaluate or rank during generation — just list

**Template:**

```
Path closed: [describe the closed path in one sentence]
Time: [timestamp]

Alternative options:
1. [Option A] — First action: ___
2. [Option B] — First action: ___
3. [Option C] — First action: ___
[4. Optional Option D...]
```

**Why same session:** The closed path's context is fully loaded in working memory. You know the constraints, the reasons it failed, the adjacent landscape. This context evaporates within hours. Options generated fresh the next day miss the information density of the closure moment.

**PASS condition:** Written list of ≥3 alternatives with first actions exists → proceed to G2

---

## G2: Quick EV Triage

For each alternative generated in G1, apply a 2-minute EV triage. No deep analysis — just enough to eliminate obvious non-starters and rank the rest.

**Triage questions (30 seconds per option):**

1. Does this option require skills/resources I have access to now? (Y/N/Partial)
2. What is the best-case outcome if this works? (1 sentence)
3. What is the worst case if I try and it fails? (1 sentence)
4. Is the opportunity window open for ≥3 months? (Y/N)

| Score | Decision |
|-------|---------|
| All Y, compelling upside, downside tolerable, window open | PRIORITY — move to G3 |
| Mostly Y with manageable gaps | SECONDARY — keep in list |
| Major skill/resource gap OR window closes in <4 weeks | DEFER or DROP |

**PASS condition:** Options ranked into PRIORITY / SECONDARY / DEFER list → proceed to G3

---

## G3: First Action within 48 Hours

For each PRIORITY option, define and execute the first concrete action within 48 hours of path closure.

**Why 48 hours:** The energy and clarity of a fresh closure is a resource with a short half-life. First actions taken within 48 hours have 3x+ follow-through rate vs. actions planned "for next week."

**First action must be:**
- Specific (not "research it" — "call X" or "send email to Y" or "open account at Z")
- Completable in ≤2 hours
- Generates new information (feedback from the market/person/system)

**Log format:**

```json
{
  "closed_path": "...",
  "closure_date": "YYYY-MM-DD",
  "options_generated": ["...", "...", "..."],
  "priority_option": "...",
  "first_action": "...",
  "action_deadline": "YYYY-MM-DD",
  "action_completed": null
}
```

**PASS condition:** First action for PRIORITY option completed or confirmed scheduled → G3 complete

---

## G4: 2-Week Review

Two weeks after path closure:

1. Was the first action completed? (Y/N)
2. What new information did it generate?
3. Has the PRIORITY option been confirmed viable, dropped, or replaced?
4. Update the log.

If the PRIORITY option was dropped without replacement: return to G1 with fresh context (not same session, but same SOP — generate ≥3 new options).

---

## G5: Kill Conditions for This SOP

This SOP should NOT be triggered when:

1. The path is "difficult" or "uncertain" but not definitively closed — premature closure wastes viable options
2. The closed path is reversible with moderate effort — in that case, it's CONDITIONAL not CLOSED (may re-open later; no need to immediately generate replacements)
3. The closure is due to a temporary blocking condition (e.g., "no budget this quarter") — re-queue for the condition change, don't generate permanent replacements

**Premature closure = discarding viable paths before they're actually closed.**

---

## Anti-Patterns

| Pattern | Why it fails |
|---------|-------------|
| "Let me sleep on it before deciding what to do next" | Context richness peak is at closure moment — sleeping loses information density |
| Generating options without writing them down | Unwritten options exist only as intention, not commitment; they evaporate under emotional load |
| Returning to closed path to "explain better" | Confirmed closure means new explanation has near-zero EV; resources better spent on G1 |
| "I need to process this first" | Processing and option-generation are not mutually exclusive; writing options IS part of processing |
| Waiting for "the right next step" to reveal itself | Options don't reveal themselves — they're generated by active search with context-loaded working memory |

---

## Revenue Connection

Path closure is universal: every career decision, every negotiation, every strategic pivot involves a path being closed. The failure to immediately generate alternatives is one of the most common sources of "dead time" — months spent in limbo after a failed negotiation, job loss, or strategy failure.

This SOP is directly applicable to:
- Career coaching / executive coaching clients
- Founders after funding rounds fail
- Traders after a strategy is killed
- Anyone navigating a job loss or organizational restructuring

**Productization:**
- $97 standalone SOP (career/negotiation decision framework)
- Component of a broader "decision agility" package with MD-423, MD-420, MD-424
- Posting queue: ~Feb 2027

---

## Backing MDs

- **MD-423** — Path closure → immediate option generation (primary)
- **MD-421** — Business single-person dependency → structural fragility (context: why the clinic path was definitively closed)
- **MD-400** — Domain-specific skill sunk cost (context: why lingering on a closed path is especially costly for non-transferable skills)
- **MD-07** — Inaction bias (no edge = no action; but closure = edge elsewhere, not inaction)

---

## Related Files

- `templates/dna_core.md` — MD-423, MD-424, MD-425 (2017-12 extraction)
- `docs/knowledge_product_118_dualma_reactivation_protocol.md` — SOP #118 (adjacent: strategy kill has the same structure)
- `results/kill_lessons.jsonl` — log format for closed paths
