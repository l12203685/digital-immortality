# Second Organism Onboarding Guide
> Branch 4 — 社交圈 scale-up path: users=0 → users=N
> Created: 2026-04-09 UTC (cycle 204)

---

## Purpose

This guide enables anyone to create a digital organism for a friend, partner, or colleague.
It is the generalized version of what was done with samuel_dna.md.

Samuel is Organism C. This guide produces Organism D, E, F…

**When to use**: You have a relationship close enough that the person would honestly correct wrong inferences about them. If they'd only give polished answers, the organism will be hollow.

---

## Prerequisites

| Item | Check |
|------|-------|
| You know this person well enough to write 5 behavioral observations | ✓ before starting |
| They are willing to participate (even 30 min async) | ✓ before starting |
| You have access to `templates/samuel_dna.md` as reference format | ✓ already exists |

---

## Step 1: Draft Before Meeting (1–2 hours)

Write a first-pass DNA file using this template:

```
templates/[firstname]_dna.md
```

Sections to fill before any conversation:

1. **§0 Core Principles** — write 5–8 from your observation
2. **§1 Identity** — basic facts (role, age, goals)
3. **§4 Behavioral Patterns** — what you've actually seen them do under pressure
4. **§7 Known Divergences from You** — where do you know you think differently?

Explicitly mark anything uncertain with `[INFERRED]`. Samuel's DNA has ~60% inferred content before correction.

---

## Step 2: Run the Collision (Before Meeting)

```bash
python organism_interact.py templates/dna_core.md templates/[firstname]_dna.md --report
```

This surfaces:
- Where the two organisms agree (75%+ = healthy friendship)
- Where they diverge (3+ divergences = distinct value system)
- Which principles are driving the divergence

The collision report becomes the agenda for Step 3.

---

## Step 3: Calibration Session (30–60 min)

Frame: *"I built a model of how you think. Your job is to break it."*

#### Opening move (5 min)
Show them their §0 Core Principles. Ask:
> "Read these. Mark anything that doesn't match how you actually behave — not how you want to behave, but what you actually do."

Corrections > confirmations. Silence = close enough.

#### Core scenarios (20–30 min)
Run 4–5 scenarios from the collision divergence domains. Each scenario:
1. Read it aloud
2. Let them answer (2–3 min)
3. One follow-up: "What principle drove that?"
4. Note exact language — their words, not your paraphrase

**Scenario bank for common divergence domains:**

*Time allocation*:
> "You have a free Saturday with no obligations. Walk me through what actually happens."

*Risk tolerance*:
> "You put 20% of your net worth into something you believed in. It's down 50% at month 3. Thesis unchanged. What's your process?"

*Relationship boundary*:
> "A friend you've invested heavily in for 2 years keeps taking without reciprocating. How long before you reduce investment, and what triggers that?"

*Information edge*:
> "You get a tip from someone you trust. You can't verify it yourself in time. Do you act?"

*Conflict*:
> "Someone takes credit for your work publicly. Deliberate. You have evidence. What do you do?"

#### Close (5 min)
Three questions:
1. "What did I get most wrong?"
2. "What surprised you about where we agree?"
3. "What principle am I missing entirely?"

---

## Step 4: Correct and Commit (Same Day)

1. Update `[firstname]_dna.md`:
   - Remove or correct wrong §0 principles
   - Add new principles with their exact language
   - Update §4 with real examples from session
   - Mark §8 calibration status: correction date + method

2. Run consistency test:
   ```bash
   python consistency_test.py templates/[firstname]_dna.md --output-dir results
   ```

3. Re-run collision report with corrected DNA

4. Commit:
   ```bash
   git add templates/[firstname]_dna.md
   git commit -m "feat: [firstname] DNA corrected after calibration session"
   ```

---

## Step 5: Maintenance Cadence

Organisms decay. Life changes → DNA changes. Maintenance schedule:

| Event | Action |
|-------|--------|
| Major life event (job change, relationship change) | Update §1 Identity + §5 Career |
| Observed behavior that contradicts DNA | Add to §4 with date |
| Quarterly | Re-run collision report; check if divergences have shifted |
| Annual | Full calibration session — repeat Step 3 |

---

## Quality Checklist

Before marking an organism as validated:

- [ ] §0 Core Principles: 10+ principles (not just aspirational — behaviorally verified)
- [ ] §4 Behavioral Patterns: each pattern has at least one real example
- [ ] §7 Divergences: at least 3 documented divergences from your own DNA (generic "ALIGNED" is a red flag)
- [ ] In-person correction: at least one session done (async is acceptable fallback)
- [ ] Consistency test: run and score recorded
- [ ] Collision report: agreement rate documented

---

## What Makes a Good Organism

**Good**: DNA captures how they actually behave, including their blind spots and inconsistencies.

**Bad**: DNA captures how they describe themselves. This is an idealized self-portrait, not an organism.

The difference: "Samuel prioritizes relationships above health" vs "Samuel says he values health but in observed behavior, health is the first tradeoff he makes when schedule is full."

**Rule**: If there's nothing embarrassing or unflattering in the DNA, it's not accurate.

---

## Scale Path: users=0 → users=N

Current status: 1 organism in progress (Samuel, Organism C).

Path to N organisms:

1. **Samuel validates** — becomes reference implementation; shows it works for non-Edward
2. **Samuel refers** — his network is the acquisition channel (his principle: *network density compounds*)
3. **Guided onboarding** — `/guided-onboarding` skill enables self-service DNA creation
4. **Discord server** — organisms interact in channels; network effects kick in
5. **Collision becomes product** — paid service: "run a collision between you and your co-founder"

Each organism added increases value for all existing organisms: more divergences to explore, more cross-organism pattern recognition.

---

*See also: `docs/organism_session_prep.md` (Samuel-specific session plan), `organism_interact.py --report`*
