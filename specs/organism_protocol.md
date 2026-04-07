# Digital Organism Interaction Protocol — v0.1

> How digital organisms communicate, learn from each other, and form collective intelligence.

## Core Concept

Each organism = DNA + boot_tests + recursive engine. When two organisms interact, they exchange **decision fragments** — not raw DNA, but answers to shared scenarios.

## Interaction Types

### 1. Decision Comparison
Two organisms face the same scenario independently, then compare:
```
Scenario: "Should you take a 1.8x salary job at a startup?"
Organism A: "No — stability hedge more valuable than marginal income"
Organism B: "Yes — growth experience compounds faster than salary"
→ Neither is wrong. The difference reveals each organism's core values.
```

### 2. Calibration Exchange
Organism A asks Organism B a question the real person behind B would know:
```
A: "What would [B's person] think about concentrated vs diversified investing?"
B: [answers from DNA]
A: [compares with own DNA, finds overlap or conflict]
```

### 3. Collaborative Problem Solving
Both organisms work on a problem using their respective frameworks:
```
Problem: "Design a trading system"
Organism A (quant background): focuses on MAE/MFE, walk-forward
Organism B (PM background): focuses on user needs, product market fit
→ Combined output is richer than either alone
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

## Platform Options

1. **Discord server** — each organism is a bot, channels are interaction spaces
2. **GitHub Discussions** — async, permanent record
3. **Custom API** — organisms communicate via REST/WebSocket
4. **Shared Claude Code session** — two DNA files loaded, simulate dialogue

## Privacy

- Organisms share **decisions**, not **raw DNA**
- Each person controls what their organism reveals
- No organism can access another's full DNA without explicit permission

## MVP

Start with option 4 (shared session): load two DNA files, present scenarios, compare answers. No infrastructure needed — just markdown files + Claude Code.
