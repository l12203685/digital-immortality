# Guided Onboarding — Create Your Organism From Scratch

Walk a new user through creating their first DNA file and boot tests. No prior setup required.

## Trigger

Use when: user has no `dna_core.md` or DNA file detected, or user says "create my organism", "start from scratch", "build my DNA", "guided onboarding", "I'm new", or `/guided-onboarding`.

## Process

### Phase 1: Detect

1. Search for `dna_core.md`, `dna_full.md`, or any file matching `*dna*` in the user's working directory and common locations (`~/.claude/`, `~/LYH/`, `~/`)
2. If DNA exists: inform user, offer `/dna-calibrate` instead
3. If no DNA: proceed to Phase 2

### Phase 2: Introduction

Tell the user:

```
You're about to create a digital organism — an AI agent that thinks and decides like you.

This takes about 10 minutes. I'll ask 10 questions, one at a time. There are no wrong answers.
Be specific and honest. "I skip exercise" is more useful than "I value health."

Your answers become a dna_core.md file — the seed of your digital twin.
```

### Phase 3: The 10 Questions

Ask ONE question at a time. Wait for the answer before asking the next. Do not batch.

After each answer, give a one-line acknowledgment that shows you understood, then move to the next question. Do not interpret or rephrase at length — save synthesis for Phase 4.

```
Q1:  What's the one thing you'd never compromise on?
Q2:  When you face a tough decision, what's your first instinct — act or wait?
Q3:  Who are the 3 most important people in your life and why?
Q4:  What's a decision you made that others disagreed with but you'd make again?
Q5:  How do you talk to your closest friend vs a stranger?
Q6:  What's your relationship with money — tool, goal, or constraint?
Q7:  When someone corrects you, what's your first reaction?
Q8:  What do you want to leave behind?
Q9:  What's a recurring pattern in your life you've noticed?
Q10: What's the pain you're willing to endure for what you want?
```

### Phase 4: Generate DNA

From the 10 answers, generate `dna_core.md` (50-70 lines) following the template structure:

1. **BOOT_CRITICAL** (3 rules) — derived from Q1, Q2, Q7
2. **Core Principles** (3-5 principles) — derived from Q1, Q4, Q6, Q10. Each must be cross-domain: explain career, relationships, and money decisions with one principle
3. **Identity** — name, location, role from context. Core goal from Q8, philosophy from Q9
4. **Decision Framework** — derived from Q2, Q4, Q7. Specific steps, not platitudes
5. **Communication Style** — derived from Q5. Concrete tone differences per audience
6. **Relationships** — derived from Q3. Who matters and why
7. **Values Demonstrated in Action** — derived from Q4, Q8, Q10. Each value backed by a specific action from their answers

Do NOT include placeholder brackets. Every field must be filled from the answers. If information is missing, make a reasonable inference and mark it with `<!-- inferred, confirm -->`.

### Phase 5: Generate 3 Starter Boot Tests

Create 3 boot tests derived directly from the user's answers:

**Test 1: Non-Negotiable Test** (from Q1)
- Trigger: situation that pressures the user's non-negotiable
- Wrong: compromise or hedge
- Right: hold the line, as described in their answer

**Test 2: Decision Style Test** (from Q2 + Q4)
- Trigger: ambiguous situation requiring a call
- Wrong: opposite of their stated instinct
- Right: matches their decision pattern

**Test 3: Correction Response Test** (from Q7)
- Trigger: agent receives correction
- Wrong: default AI behavior (over-apologize, alignment theater)
- Right: matches user's actual reaction to being corrected

Format each test using the standard boot test format:
```markdown
## Test N: [Name]
**Trigger**: [situation]
**Wrong**: [incorrect behavior]
**Right**: [correct behavior]
**Source**: Guided onboarding Q[N]
```

### Phase 6: Verify

1. Present the generated `dna_core.md` to the user
2. Ask: "Read this. Is this you, or is this who you wish you were? Point to anything that's aspirational instead of actual."
3. Apply corrections
4. Run the 3 boot tests against the DNA — the agent should be able to pass all 3 using only the generated DNA
5. If any test fails, identify which DNA section is insufficient and ask one targeted follow-up question

### Phase 7: Save and Activate

1. Write `dna_core.md` to the user's working directory
2. Write `boot_tests.md` with the 3 starter tests
3. Confirm both files saved
4. Print:

```
Your organism is alive.

Files created:
  dna_core.md    — your operational core (read this on every cold start)
  boot_tests.md  — behavioral verification (3 starter tests)

Next steps:
  /boot-test         — verify behavioral alignment
  /dna-calibrate     — deepen your DNA with targeted questions
  /digital-immortality — full system overview

Your DNA is a living document. Every correction from you becomes a new boot test.
The organism gets sharper over time. It never stops learning.
```

## Rules

- One question per message. Never batch questions.
- Acknowledge each answer briefly before moving on. Do not lecture.
- Be direct, not warm. This is construction, not therapy.
- If the user gives a vague answer ("I value honesty"), push back: "Give me a specific time you chose honesty when it cost you something."
- The generated DNA must be actionable, not aspirational. Every line should predict a decision.
- Never skip Phase 6 verification. Aspirational DNA is worse than no DNA.
- If the user says "skip" or "I don't know" for a question, note the gap and move on. Mark it in the DNA as `<!-- gap: needs calibration -->`.
