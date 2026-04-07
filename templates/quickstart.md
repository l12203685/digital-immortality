# Digital Immortality -- Quick Start

This project builds a behavioral digital twin: an AI that decides like you,
using a DNA file as its core. Not consciousness transfer -- behavioral equivalence.

---

## Step 1: Create your DNA

```bash
python onboard.py --new
```

This walks you through ~5 minutes of questions and generates a personalized
DNA file with your core principles, identity, and decision framework.

Already have a DNA file? Validate it:

```bash
python onboard.py --validate your_dna.md
```

## Step 2: Run boot tests

```bash
python consistency_test.py your_dna.md --output-dir results
```

Boot tests verify that an AI session loaded with your DNA makes the same
decisions you would. If any test fails, update your DNA to be more specific.

## Step 3: Start the recursive engine

```bash
python recursive_engine.py --init       # First-time setup
python recursive_engine.py --prompt     # Generate next cycle prompt
python recursive_engine.py --status     # Check current state
```

The recursive engine keeps your digital twin alive between sessions.
Each cycle reads its previous output and asks: "what advances the goal?"

## After first boot

- **Read results/** for test output and cycle logs.
- **Correct wrong decisions** by updating your DNA. Specificity beats generality.
- **Each correction becomes a boot test** -- the system learns from mistakes.
- **Run `/dna-calibrate` in Claude Code** for guided refinement with targeted questions.
- **Add more DNA sections** over time: Communication Style, Relationships, Career & Finance, Values in Action. See `templates/example_dna.md` for the full template.

## Key files

| File | What it does |
|------|-------------|
| `onboard.py` | Interactive onboarding (you are here) |
| `templates/example_dna.md` | Full DNA template with examples |
| `consistency_test.py` | Cross-session decision consistency |
| `recursive_engine.py` | Recursive loop state management |
| `organism_interact.py` | Compare two DNA files across scenarios |
| `SKILL.md` | Master skill definition |

## One-liner summary

Write who you ARE (not who you want to be), test it against real decisions,
and keep correcting until the AI decides like you.
