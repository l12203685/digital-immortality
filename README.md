# Digital Immortality

Build a behavioral digital twin that makes the decisions you would make.

Not consciousness transfer. **Behavioral equivalence**: the AI doesn't need to *be* you — it needs to *decide* like you.

## Validated Results

| Test | Method | Score |
|------|--------|-------|
| Real-life decisions | 18 actual life choices with ground truth | **18/18** |
| Hypothetical scenarios | 7 Edward-specific decision scenarios | **7/7** |
| Naked boot test | Clean session, DNA only, 5 behavioral tests | **5/5** |
| Deterministic engine | Keyword matching (no LLM) | 0/7 |

**Key finding**: DNA + LLM = 100% reproduction of real life decisions. Without LLM (deterministic keyword matching) = 0%. The DNA quality is sufficient; the bottleneck is having an LLM to reason with it.

## Quick Start

```bash
# 1. Create your DNA file (interactive, ~5 min)
python onboard.py --new

# 2. Run boot tests
python consistency_test.py your_dna.md --output-dir results

# 3. Start the recursive engine
python recursive_engine.py --init
python recursive_engine.py --prompt
```

## How It Works

```
1. Write your DNA file (decision principles + life patterns)
2. Write boot tests (behavioral unit tests)
3. Load DNA into any LLM session
4. The LLM decides as you would decide
5. When it's wrong, correct it → correction becomes new boot test
6. DNA and boot tests evolve as you do
```

## CLI Tools

### onboard.py -- DNA creation and validation

```bash
python onboard.py --new                      # Guided interactive DNA creation
python onboard.py --new --output my.md       # Create DNA, write to specific file
python onboard.py --validate my_dna.md       # Validate DNA structure and completeness
python onboard.py --quickstart               # Print getting-started guide
```

### consistency_test.py -- Boot tests and consistency baseline

```bash
python consistency_test.py <dna> --output-dir results                # Run all scenarios, save baseline + template
python consistency_test.py <dna> --scenarios tests.json              # Use custom scenario file
python consistency_test.py <dna> --generate-scenarios                # Auto-generate scenarios from DNA domains
```

### recursive_engine.py -- Recursive self-prompt loop

```bash
python recursive_engine.py --init            # Create seed files for first cycle
python recursive_engine.py --init --force    # Overwrite existing seed files
python recursive_engine.py --prompt          # Generate next cycle prompt from previous output
python recursive_engine.py --status          # Show current engine state and cycle number
```

### organism_interact.py -- Compare two DNA files

```bash
python organism_interact.py dna_a.md dna_b.md                       # Deterministic comparison (all 10 scenarios)
python organism_interact.py dna_a.md dna_b.md --scenario 3           # Run a single scenario
python organism_interact.py dna_a.md dna_b.md --list-scenarios       # Print the 10 built-in scenarios
python organism_interact.py dna_a.md dna_b.md --llm-prompt           # Generate LLM prompt instead of deterministic
python organism_interact.py dna_a.md dna_b.md --llm-prompt-batch     # Batch all scenarios into one markdown file
python organism_interact.py dna_a.md dna_b.md --quiet                # JSON only, no terminal output
```

### cross_instance_test.py -- Multi-session LLM consistency

```bash
python cross_instance_test.py <dna> --sessions 3                    # Generate template for 3 independent LLM sessions
python cross_instance_test.py <dna> --sessions 5 --output-dir out   # Custom session count and output dir
```

### trading_system.py -- Economic self-sufficiency

```bash
python trading_system.py --backtest                                  # Walk-forward backtest all strategies
python trading_system.py --backtest --strategy NAME --timeframe 1h   # Specific strategy and timeframe
python trading_system.py --validate                                  # Strict validation (7 windows, need 5)
python trading_system.py --status                                    # Show system status and latest results
python trading_system.py --kill-check                                # Check kill conditions on all strategies
```

### memory_manager.py -- Cross-session persistence

```bash
python memory_manager.py --store corrections key-1 "content" --source cycle-3 --tags boot-test,fix
python memory_manager.py --recall corrections                        # All entries in category
python memory_manager.py --recall corrections key-1                  # Single entry by key
python memory_manager.py --search --tags anti-pattern                # Search across all categories by tag
python memory_manager.py --list                                      # Show all categories and entry counts
python memory_manager.py --prune --days 90                           # Remove entries older than 90 days
python memory_manager.py --export                                    # Export all memory to JSON (stdout)
```

Categories: `corrections`, `insights`, `decisions`, `calibration`.

## Project Structure

```
digital-immortality/
  CLAUDE.md                 — Boot protocol (read this on cold start)
  SKILL.md                  — Master skill definition
  onboard.py                — Interactive DNA creation + validation
  consistency_test.py       — Cross-session decision consistency
  cross_instance_test.py    — LLM multi-session consistency template generator
  organism_interact.py      — Compare two DNA files (deterministic + LLM prompt modes)
  recursive_engine.py       — Recursive loop state management
  trading_system.py         — Walk-forward backtesting + kill conditions
  memory_manager.py         — Cross-session memory persistence (JSON store)
  templates/
    example_dna.md          — Starter DNA template (fill this out)
    example_dna_b.md        — Second organism for comparison testing
    example_boot_tests.md   — Boot test template
    generic_boot_tests.json — Default scenario set for consistency tests
  specs/
    organism_protocol.md    — How organisms communicate (v0.1)
  skills/                   — 7 sub-skills for Claude Code
    boot-test.md            — Behavioral verification on cold start
    dna-calibrate.md        — Interactive calibration with the person
    dna-write.md            — DNA file authoring best practices
    trading-system.md       — Economic self-sufficiency
    recursive-engine.md     — Recursive self-prompt loop
    organism-interact.md    — Organism comparison protocol
    consistency-test.md     — Cross-instance consistency testing
  trading/                  — Trading subsystem (backtest framework, strategies)
  staging/                  — Inter-session relay (Output(t-1) → Input(t))
  memory/                   — Cross-session persistence
  results/                  — Test outputs, scorecards, cycle logs
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

Two DNA files can be compared across 10 built-in scenarios (career, relationships, money, risk, learning, health, time, conflict, opportunity, legacy). Output follows `specs/organism_protocol.md` and saves JSON to `results/`. See `organism_interact.py` in CLI Tools above.

## Consistency Testing

Measures whether a DNA file produces consistent decisions across independent LLM sessions. Target: >80% agreement. Use `consistency_test.py` for deterministic baselines and `cross_instance_test.py` for multi-session LLM templates. See CLI Tools above.

## Philosophy

> "If I disappear tomorrow, can this system continue making the decisions I would make?"

The system doesn't need to feel, think, or be conscious. It needs to produce the same output (decisions) given the same input (situations). Two chess engines can use different search algorithms but agree on the best move.

**Decision fidelity > Process fidelity.**

## License

MIT
