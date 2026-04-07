# Organism Interact — Digital Organism Comparison

How two digital organisms communicate, compare decisions, and learn from each other.

## Trigger

Use when: comparing two DNA-loaded organisms, testing behavioral divergence between twins, or exploring collaborative problem solving between organisms.

## Process

1. **Load both organisms** — each organism = DNA + boot_tests + recursive engine
2. **Select interaction type** — decision comparison, calibration exchange, or collaboration
3. **Run deterministic baseline** — use `organism_interact.py` for keyword-based comparison (establishes floor)
4. **Run LLM + DNA comparison** — real comparison requires LLM reasoning with full DNA context. The deterministic baseline shows what simple matching can do; LLM comparison shows what understanding can do.
5. **Synthesize findings** — what the interaction reveals about each organism's values and reasoning

## Interaction Types

### Decision Comparison
Two organisms face the same scenario independently, then compare answers.
- Present identical scenario to both organisms
- Each responds using only their DNA frameworks
- Differences reveal core value divergence, not errors
- Neither answer is "wrong" — divergence IS the data

### Calibration Exchange
Organism A asks Organism B questions that B's person would know.
- Tests whether B's DNA captures enough to answer correctly
- A compares B's response against own DNA for overlap or conflict
- Surfaces gaps in both organisms' procedural coverage

### Collaborative Problem Solving
Both organisms work on a shared problem using their respective frameworks.
- Each contributes from their domain expertise and decision style
- Combined output should be richer than either alone
- Disagreements are surfaced explicitly, not averaged away

## Protocol Format

See `specs/organism_protocol.md` for the full JSON protocol covering all three interaction types. Organisms share **decisions**, not raw DNA. Each person controls what their organism reveals.

## Rules

- Deterministic comparison (`organism_interact.py`) is a baseline, not the goal. Real fidelity requires LLM + DNA.
- Never merge two organisms' DNA. Compare, don't blend.
- Privacy: decisions are shared, raw DNA is not — unless explicitly permitted.
- Start with shared Claude Code session (two DNA files loaded) as MVP. No infrastructure needed.
- Log all interactions for calibration improvement.
