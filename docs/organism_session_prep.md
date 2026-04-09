# Organism Calibration Session — Samuel
> Branch 4.1 — First non-Edward organism correction
> Created: 2026-04-09 UTC (cycle 204)

---

## Purpose

samuel_dna.md was built by Edward's external inference, not Samuel's self-report. This session exists to:
1. Let Samuel correct wrong inferences
2. Extract behavioral patterns that Edward cannot observe
3. Increase DNA fidelity from ~70% to 90%+
4. Run live consistency test to validate

**Target**: Re-run `python organism_interact.py templates/dna_core.md templates/samuel_dna.md --report` after session. 9 principles → 15+ principles. Agreement rate stays ≥75%, divergences become structurally meaningful.

---

## Format

| Item | Value |
|------|-------|
| Duration | 60 minutes |
| Location | 1:1, no audience |
| Framing | "I built a model of how you think. I want you to break it." |
| Output | Corrected samuel_dna.md pushed to git same day |

---

## Agenda

### 0–5 min: Setup

Show Samuel the current samuel_dna.md. Say:
> "I wrote this based on what I've observed. Your job is to tell me where I'm wrong — not where you wish you were different, but where my model of you is actually wrong."

Key rule: corrections over confirmations. Silence on a section = "close enough."

---

### 5–25 min: Core Principles Review

Walk through Section 0 (9 principles). For each:
- "Does this sound right?"
- "Can you give me a real example where this drove a decision?"
- "Is there a situation where you violate this rule?"

**Watch for:**
- Aspirational answers ("I try to...") vs behavioral answers ("I did...")
- Hesitation on a principle = either wrong or incomplete
- New principles that surface unprompted

**Likely corrections:**
- Principle #3 (EV vs gut) — Samuel may refine when gut overrides
- Principle #7 (reciprocity accounting) — may be more intuitive than systematic
- Principle #9 (first impression) — test with real example

---

### 25–45 min: Live Decision Scenarios

Run 5 scenarios from the calibration questions in samuel_dna.md §9. Read each scenario aloud. Samuel answers verbally. You take notes.

**Scenario 1**: "You've been investing in a relationship — introductions, favors, showing up. After 8 months, you realize they only reach out when they need something. What do you do?"
- Target: tests reciprocity accounting (Principle #7)
- Reveals: threshold for downgrading a relationship

**Scenario 2**: "A deal looks great on the numbers. 2.5x upside, 18-month horizon, solid structure. But the person leading it gives you a bad feeling you can't name. Do you invest?"
- Target: tests EV vs gut tension (Principle #3)
- Reveals: how strong the gut veto actually is

**Scenario 3**: "You put 30% of your liquid net worth into something you believed in. It's down 60% at month 3. The fundamentals haven't changed. What's your actual process?"
- Target: tests 70% drawdown tolerance claim
- Reveals: whether high risk tolerance is real or untested

**Scenario 4**: "Free Saturday, no obligations, no one expecting you anywhere. Walk me through what actually happens — hour by hour."
- Target: tests idle state
- Reveals: whether free time defaults to social or solitude

**Scenario 5**: "Your best friend asks you to introduce them to your most valuable contact. You're not sure the fit is right. Do you make the intro?"
- Target: tests loyalty vs credibility tradeoff
- Reveals: which relationship he protects when they conflict

---

### 45–55 min: Divergence Review

Show Samuel the collision report summary (3 divergences: health/time/legacy). Ask:

> "In these three domains, my model says we'd make different decisions. Does that sound right, or is my model of you wrong?"

- **Health**: "Do you think of your body as something to optimize, or something to not worry about until it breaks?"
- **Time**: "Unstructured time — is that opportunity or discomfort?"
- **Legacy**: "In 20 years, what do you want to have built — and what medium does it take?"

These are not corrections — they're Edward learning what Samuel actually values, even if different.

---

### 55–60 min: Close

Three outputs:
1. "What did I get most wrong about you?"
2. "What surprised you about where we agree?"
3. "What's one principle I should add that I missed entirely?"

---

## Post-Session Protocol

Immediately after (same day):

1. Update `templates/samuel_dna.md`:
   - Correct wrong inferences in §0 (principles)
   - Update §4 (behavioral patterns) with actual examples from session
   - Add new principles if any surfaced
   - Update §8 calibration status: in-person correction date

2. Re-run consistency test:
   ```bash
   python consistency_test.py templates/samuel_dna.md --output-dir results
   ```

3. Re-run collision report:
   ```bash
   python organism_interact.py templates/dna_core.md templates/samuel_dna.md --report
   ```

4. Commit and push.

5. Update dynamic_tree.md Branch 4.1 status.

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| Principles extracted | 15+ (from 9) |
| In-person corrections made | ≥3 (proves session was real, not theater) |
| Post-session collision agreement | ≥75% maintained |
| samuel_dna.md committed | Same day |

---

## Failure Modes

| Failure | Signal | Response |
|---------|--------|----------|
| Samuel gives aspirational answers | "I try to..." "I should..." | Ask: "When did you last actually do this?" |
| Samuel agrees with everything | No corrections in 60 min | Probe harder: "What's the one thing I got most wrong?" |
| Session canceled | — | Send async version via DM: 5 questions, text format |
| Samuel not interested in DNA concept | — | Use samuel_pilot_dm.md framing: "help me test a framework on your real decision" |

---

*After this session, Samuel becomes the first validated non-Edward organism. Branch 4.1 CLOSED.*
