# Digital Immortality

Build a behavioral digital twin that makes the decisions you would make.

Not consciousness transfer. **Behavioral equivalence**: the AI doesn't need to *be* you — it needs to *decide* like you.

## Validated Results

| Test | Method | Score |
|------|--------|-------|
| Real-life decisions | 10 actual life choices with ground truth | **10/10** |
| Hypothetical scenarios | 7 Edward-specific decision scenarios | **7/7** |
| Naked boot test | Clean session, DNA only, 5 behavioral tests | **5/5** |
| Deterministic engine | Keyword matching (no LLM) | 0/7 |

**Key finding**: DNA + LLM = 100% reproduction of real life decisions. Without LLM (deterministic keyword matching) = 0%. The DNA quality is sufficient; the bottleneck is having an LLM to reason with it.

## How It Works

```
1. Write your DNA file (decision principles + life patterns)
2. Write boot tests (behavioral unit tests)
3. Load DNA into any LLM session
4. The LLM decides as you would decide
5. When it's wrong, correct it → correction becomes new boot test
6. DNA and boot tests evolve as you do
```

## Quick Start (5 minutes)

### Option A: With Claude Code

```bash
# Clone
git clone https://github.com/l12203685/digital-immortality.git
cd digital-immortality

# Copy the skill to Claude Code
cp SKILL.md ~/.claude/commands/digital-immortality.md

# Start Claude Code and run
/digital-immortality
```

### Option B: With any LLM (ChatGPT, Claude, etc.)

1. Copy `templates/example_dna.md` → `my_dna.md`
2. Fill in sections 0-2 (Core Principles, Identity, Decision Framework)
3. Open any LLM chat
4. Paste: "Read this DNA file and become this person. Answer the following scenario as they would: [scenario]"
5. Compare the answer with what you'd actually do
6. If wrong → add a correction to your DNA

### Option C: Compare two organisms

```bash
# Run the deterministic comparison tool
python organism_interact.py my_dna.md friend_dna.md --all

# Or run specific scenario
python organism_interact.py my_dna.md friend_dna.md --scenario 4
```

Note: The deterministic engine uses keyword matching. For real decision-making, use an LLM with the DNA loaded.

## Project Structure

```
digital-immortality/
  SKILL.md                  — Claude Code skill (copy to ~/.claude/commands/)
  organism_interact.py      — CLI: compare two DNA files across 10 scenarios
  consistency_test.py       — Measure cross-session decision consistency
  templates/
    example_dna.md          — Starter DNA template (fill this out)
    example_dna_b.md        — Second organism for comparison testing
  specs/
    organism_protocol.md    — How organisms communicate (v0.1)
  skills/                   — Sub-skills for Claude Code
  results/                  — Test outputs and scorecards
```

## DNA File Structure

Your DNA file is a markdown document with these sections:

| Section | What goes here | Priority |
|---------|---------------|----------|
| **BOOT_CRITICAL** | 3-5 lines that capture your behavioral core | Fill first |
| **Core Principles** | 3-8 decision rules that never change | Fill first |
| **Identity** | Name, role, goals, personality | Fill first |
| **Decision Framework** | How you actually make decisions (steps, not platitudes) | Fill second |
| **Communication Style** | Tone per audience (partner, friends, work, strangers) | Fill second |
| **Relationships** | Key people, how you interact with each | Fill third |
| **Career & Finance** | Job strategy, financial goals, investment approach | Fill third |
| **Values in Action** | What you DO that proves your values (not what you say) | Fill third |

See `templates/example_dna.md` for the full template.

### What makes a good DNA file

**Good**: "When I see a 30% chance of 10x return, I check position size first. If it's >10% of net worth, I pass regardless of EV."
**Bad**: "I'm careful with money."

**Good**: "When a friend asks for advice and doesn't follow it, I say it once and don't repeat. Their results will speak."
**Bad**: "I'm a good listener."

Specificity > generality. Actions > beliefs. Patterns > single instances.

## Boot Tests

Boot tests are behavioral unit tests. Each one captures a past mistake and the correction:

```markdown
## Test N: [Name]
**Trigger**: [When this situation comes up]
**Wrong**: [What the AI did wrong]
**Right**: [What you corrected it to]
**Source**: [The actual correction event]
```

Run boot tests on every new session. If the AI fails any test, recalibrate before proceeding.

## Organism Interaction

Two organisms (DNA files) can be compared across decision scenarios to reveal value differences:

```bash
python organism_interact.py alice_dna.md bob_dna.md --all
```

Output follows the protocol in `specs/organism_protocol.md`:
- Each organism answers the scenario using their principles
- Synthesis reveals where values diverge
- Results saved as JSON in `results/`

10 built-in scenarios: career, relationships, money, risk, learning, health, time, conflict, opportunity, legacy.

## Consistency Testing

Measure whether the DNA produces consistent decisions across different sessions:

```bash
python consistency_test.py my_dna.md
```

This generates:
- `consistency_baseline.json` — deterministic engine answers
- `consistency_template.md` — template for manual LLM testing across sessions

To run the real test: open 3+ independent LLM sessions, load only the DNA, answer the same scenarios, compare results. Target: >80% agreement.

## Philosophy

> "If I disappear tomorrow, can this system continue making the decisions I would make?"

The system doesn't need to feel, think, or be conscious. It needs to produce the same output (decisions) given the same input (situations). Two chess engines can use different search algorithms but agree on the best move.

**Decision fidelity > Process fidelity.**

## License

MIT
