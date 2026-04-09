# Organism C — Selection & Fill-In Worksheet

> Branch 4 — 社交/organism
> Created: 2026-04-09 UTC (cycle 208)
> Purpose: Lower friction to zero for Edward to pick Organism C and fill in `templates/organism_c_draft.md`
> Time required: 20–30 min (think through, fill in)
> Prerequisite: `templates/organism_c_draft.md` already exists with scaffold

---

## Why This Worksheet Exists

`organism_c_draft.md` is a complete blank scaffold. That's the right format but the wrong starting point for Edward. A blank template looks like work. This worksheet is a sequence of concrete questions — answer them in order, paste answers into the draft.

The goal: by the end of this worksheet, `organism_c_draft.md §0` (5 principles) + `§7` (3 divergence domains) are filled. That's enough to run the first collision.

---

## Step 1: Pick C (5 min)

The triangle (Edward ↔ Samuel ↔ C) is only valuable if C adds a new axis that neither Edward nor Samuel has.

**Samuel's divergence domains from Edward** (pre-identified, don't repeat these):
- Trust velocity (relationship_downgrade, social_trust)
- Network ROI framing (network_roi, intro_gatekeeping)
- Learning timeline (foundation-first vs parallel 70/30)
- Legacy frame (build something vs wealth to sufficiency)

**C must diverge from Edward in at least one domain NOT already covered by Samuel.**

Strong candidate dimensions to look for in C:
- `health` — someone who systematically de-prioritizes health (vs Edward's health-capital frame)
- `time` — someone who optimizes for relationship density over solitary recovery (vs Edward's deep-work default)
- `information_processing` — someone who leads with social proof or gut rather than EV calculus
- `conflict style` — someone who avoids direct escalation (vs Edward's documented-then-direct)
- `financial philosophy` — someone who spends freely vs Edward's capital accumulation bias

**C qualification checklist (answer these before proceeding):**

| Question | Your answer |
|----------|-------------|
| Who is C? (name + relationship to you) | |
| How long have you known them? (must be ≥1 year) | |
| Name 3 times C surprised you with a decision | |
| Would C correct a wrong inference about them honestly? | |
| One domain where C clearly diverges from Samuel | |
| One domain where C clearly diverges from you | |

**If you can't name 3 surprises → wrong candidate. Pick someone else.**

---

## Step 2: Draft the 5 Principles (10 min)

Don't think abstractly. Think behaviorally. "What do I actually see them do?"

For each principle, complete the sentence: "When [situation], C does [action] because [underlying value]."

Then compress to one rule.

**Prompt sequences:**

1. **Decision under uncertainty** — When C doesn't know what to do, what do they default to? (Do they ask? Research? Act? Wait?)
   → Your observation:
   → Principle 1:

2. **Conflict** — When something is wrong or they disagree, how do C react? (Directly? Indirectly? With silence? Immediately?)
   → Your observation:
   → Principle 2:

3. **Resources (time, money, energy)** — How does C allocate these? What do they over-invest in vs under-invest in?
   → Your observation:
   → Principle 3:

4. **Learning** — How does C approach a new domain? (Frameworks first? Hands-on first? Guided by someone else?)
   → Your observation:
   → Principle 4:

5. **Relationships** — How does C maintain important relationships? (Proactive? Reactive? Event-driven? Need-based?)
   → Your observation:
   → Principle 5:

**Mark any uncertain principles with [INFERRED]. These will be corrected during calibration.**

---

## Step 3: Fill the 3 Divergence Domains (5 min)

Pick 3 domains from the pre-mapped axes. For each, fill the row in `§7`:

```
| domain | C's stance | Edward's stance | Samuel's stance | Triangle type |
```

**Triangle type classification:**
- `new axis` = C diverges from both Edward and Samuel → highest value
- `flip` = C is opposite to Edward but same as Samuel (or vice versa) → useful, documents a split
- `same axis` = C diverges from Edward on the same domain Samuel does → lowest value; consider a different domain

**Recommended domains to fill (start here):**
1. The domain where C most clearly surprised you
2. The domain where C clearly diverges from Samuel
3. A domain where you're genuinely uncertain what C would do (highest information value on first collision)

---

## Step 4: Run First Collision (5 min after filling)

Once §0 and §7 are filled:

```bash
python organism_interact.py templates/dna_core.md templates/organism_c_draft.md --report
```

Interpret the result:
- >75% AGREE → DNA too shallow or wrong candidate (add more divergence domains before proceeding)
- 60–75% AGREE → healthy; proceed to async calibration
- <50% AGREE → deep structural divergence; prioritize an in-person or async calibration session quickly

---

## Step 5: Plan the Async Calibration

Use `docs/samuel_async_calibration_dm.md` as the template.

Adapt the 3 scenarios to target C's specific divergence domains (§7 of organism_c_draft.md).

**Draft the first message to C here before moving on:**

Scenario 1 (C's primary divergence domain):
- Situation: [fill from §7 row 1]
- Ask: "What would you do here, and why?"

Scenario 2 (second divergence domain):
- Situation: [fill from §7 row 2]
- Ask:

Scenario 3 (domain you're most uncertain about):
- Situation: [fill from §7 row 3]
- Ask:

---

## Output Checklist

After completing this worksheet:
- [ ] `templates/organism_c_draft.md §0` — 5 principles filled (uncertain ones marked [INFERRED])
- [ ] `templates/organism_c_draft.md §1` — identity fields filled (name, role, goal)
- [ ] `templates/organism_c_draft.md §7` — 3 divergence domains filled
- [ ] First collision run and agreement rate noted
- [ ] Async DM drafted (3 scenarios ready to send)

---

## Reference

- `templates/organism_c_draft.md` — blank scaffold to fill
- `templates/samuel_dna.md` — filled reference organism
- `docs/second_organism_onboarding.md` — full 5-step process
- `docs/knowledge_product_45_organism_recruitment_sop.md` — selection criteria + async protocol
- `docs/samuel_async_calibration_dm.md` — async DM template (adapt for C)

---

*2026-04-09 UTC | Cycle 208 | Branch 4.1*
