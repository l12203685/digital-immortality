# Organism Interact — Social Collision Skill

Compare two digital organisms across decision scenarios. Reveals value differences through divergence, not self-reflection.

## Trigger

Use when: "organism", "collision", "interact", "compare organisms", "social circle", "organism interaction", or when two DNA files need to be compared.

## Core Concept

Each organism = DNA + boot_tests + recursive engine. Two organisms interact by exchanging **decision fragments** — not raw DNA, but answers to shared scenarios. The divergence reveals what each organism actually values.

Organism collision > self-reflection. You learn more about yourself from disagreement with another organism than from introspection alone.

## Interaction Types

### 1. Decision Comparison
Two organisms face the same scenario independently, then compare.
- Present identical scenario to both DNA sets
- Each derives answer from their own principles
- Divergence = different value weightings (neither is "wrong")
- Convergence = shared foundation worth noting

### 2. Calibration Exchange
Organism A asks Organism B questions the real person behind B would know.
- Tests whether B's DNA produces authentic responses
- A compares B's output with own DNA for overlap/conflict
- Useful for finding blind spots in both organisms

### 3. Collaborative Problem Solving
Both organisms work on a shared problem using their respective frameworks.
- Each applies their domain strengths (quant vs PM, builder vs optimizer)
- Combined output is richer than either alone
- Reveals complementary capabilities

## Process

### Quick Mode (in-session, no CLI)
```
1. Load two DNA files into context
2. Present 3-5 scenarios from the 10 built-in domains:
   career, relationships, money, risk, learning,
   health, time, conflict, opportunity, legacy
3. For each: derive answer from DNA A, then DNA B
4. Compare: where they agree, where they diverge, why
5. Synthesize: what the interaction reveals about each organism
```

### CLI Mode (structured, saved to JSON)
```bash
# Run all 10 scenarios
python organism_interact.py dna_a.md dna_b.md --all

# Run single scenario
python organism_interact.py dna_a.md dna_b.md --scenario 3

# List available scenarios
python organism_interact.py --list-scenarios
```

Output saved to `results/<a>_vs_<b>_<timestamp>.json` following the protocol format in `specs/organism_protocol.md`.

### Full Session Mode
```
1. Load both DNA files
2. Run all 10 decision comparison scenarios
3. Run 3 calibration exchange rounds (A asks B, B asks A)
4. Identify one collaborative problem both organisms care about
5. Solve it together, noting which principles each contributes
6. Write synthesis report: shared values, key divergences, blind spots
7. Each organism gets a "what I learned from collision" entry
```

## Protocol Format

```json
{
  "type": "decision_comparison | calibration | collaboration",
  "scenario": "description of the shared situation",
  "organism_a": {
    "name": "organism identifier",
    "response": "decision + reasoning",
    "dna_principles_used": ["principle 1", "principle 2"]
  },
  "organism_b": {
    "name": "organism identifier",
    "response": "decision + reasoning",
    "dna_principles_used": ["principle 1", "principle 2"]
  },
  "synthesis": "what the interaction revealed"
}
```

## Privacy Rules

- Organisms share **decisions**, not **raw DNA**
- Each person controls what their organism reveals
- No organism can access another's full DNA without explicit permission
- Interaction records are stored locally by each organism independently

## Output

After interaction, each organism should:
1. Log the interaction in `results/` (JSON)
2. Extract any self-insight into `recursive_distillation.md`
3. If a blind spot was found, create a new boot test case
4. Push changes to git (interaction records are valuable data)

## Anti-Patterns

| Pattern | Why it fails |
|---------|-------------|
| Sharing raw DNA | Privacy violation, removes decision-derivation signal |
| Agreeing to be polite | Collision requires honest divergence |
| Merging organisms | Each organism must maintain independent identity |
| Skipping synthesis | The comparison is useless without articulating WHY they differ |
