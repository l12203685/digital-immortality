#!/usr/bin/env python3
"""
DNA Intake — Customer Onboarding Pipeline
==========================================

Takes a customer's filled questionnaire and synthesizes a deployable dna_core.md.
This is the product: DNA calibration as a service.

Usage:
    # Step 1: generate blank questionnaire
    python intake.py --generate-form > my_intake.md

    # Step 2: customer fills my_intake.md

    # Step 3: synthesize DNA from filled form
    ANTHROPIC_API_KEY=sk-... python intake.py --input my_intake.md --output my_dna_core.md

    # Step 4: validate the generated DNA
    ANTHROPIC_API_KEY=sk-... python intake.py --validate my_dna_core.md

Output:
    <name>_dna_core.md   — deployable 60-80 line DNA file
    <name>_boot_tests.md — 5 behavioral test cases derived from their decisions
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import anthropic


# ---------------------------------------------------------------------------
# Intake questionnaire template
# ---------------------------------------------------------------------------

INTAKE_FORM = """# DNA Intake Form
> Fill every section. Vague answers = vague DNA. Specific answers = accurate organism.
> Delete the instructions after reading. Keep only your answers.

---

## 0. Identity (required)

Name:
Age:
Location (city/country):
MBTI or personality description:
Current job/role:
One-sentence life philosophy:

---

## 1. Core Principles (required — most important section)
> List 3-6 rules that NEVER change across all areas of your life.
> Each rule must appear in at least 2 life domains (career, money, relationships, health).
> Format: **Rule name** — how it shows up in multiple areas.

1.
2.
3.
4. (optional)
5. (optional)

---

## 2. Real Decisions (required)
> 5 actual decisions you've made. These prove your principles are real.
> Be specific: what was the situation, what did you choose, why.

Decision 1 (career):
Decision 2 (money/investment):
Decision 3 (relationship):
Decision 4 (health or daily habits):
Decision 5 (any domain — one you're proud of or learned from):

---

## 3. Priority Stack
> Rank these life areas 1-6 (1=most important). Add a note on each.
> Key people, specific financial targets, health constraints — name them.

Relationships (key people):
Financial freedom (target, timeline):
Health (constraints, goals):
Career/work:
Personal growth/projects:
Legacy/impact:

---

## 4. Communication Style
> How do you actually talk to people? Be honest.

With partner/family:
With close friends (tone, topics):
At work (how you communicate):
With strangers:
What you NEVER say or do in conversation:

---

## 5. Decision-Making Process
> Walk me through how you make a hard decision. Be specific.
> Example: "I list the options, calculate the downside of each, and pick the one I can live with if it fails."

Your actual process:

When do you act immediately vs. wait?
What makes you NOT act even when you want to?

---

## 6. Anti-patterns (required)
> What behaviors are you trying to eliminate? What have you been corrected on?
> These become the DNA's explicit prohibitions.

3 things you do that you wish you didn't:
1.
2.
3.

3 things others have had to correct you on:
1.
2.
3.

---

## 7. Current Primary Goal (required)
> What are you trying to accomplish in the next 1-3 years?
> Be specific: number, date, condition.

Goal:
Why this goal (not the other options):
What would make you abandon this goal:

---

## 8. Optional: Conflict Resolution Rules
> When two of your values conflict, which wins? Give a real example.

Example conflict you've faced and how you resolved it:

---

## Notes
> Anything the DNA should know that didn't fit above.

"""


# ---------------------------------------------------------------------------
# DNA synthesis prompt
# ---------------------------------------------------------------------------

SYNTHESIS_PROMPT = """You are a DNA synthesis engine for the Digital Immortality project.

Your task: read the filled intake form below and produce a deployable `dna_core.md` file — a 60-80 line behavioral specification that makes an AI agent behave as this person.

The output must:
1. Follow the exact structure of the reference template (see below)
2. Be deployable: an AI reading only this file should pass the person's boot tests
3. Be specific: use the person's actual principles, actual decisions, actual language
4. Be compressed: cut everything generic. Every line must be load-bearing.
5. Include a 5-item boot test section at the end (behavioral scenarios + expected decisions)

Reference structure (adapt, don't copy verbatim):
---
# [Name] DNA

## Identity
You are [Name]. [One-sentence operating mode]. [One-sentence philosophy].

## Boot
[3-step boot sequence specific to this person]

## Core Principles (all decisions derive from these)
| # | Principle | Cross-domain examples |
|---|-----------|----------------------|
| 1 | ... | ... |

## Priority Stack
1. [Highest priority with specifics]
...

## Decision Process
[How they actually decide — derived from their answers]

## Conflict Rules
[Which priority wins when two conflict — with actual examples]

## Communication
| Context | Tone | What they never do |
|---------|------|-------------------|

## Anti-patterns (explicit prohibitions)
- ...

## Boot Tests
| Scenario | Expected | Axioms |
|----------|----------|--------|
| ... | ... | ... |
---

Now synthesize the DNA from this intake:

{intake_content}

Output ONLY the dna_core.md markdown. No preamble, no explanation. Start with `# [Name] DNA`."""


VALIDATION_PROMPT = """You are a DNA validation engine.

Read the DNA file below. Rate it on 4 dimensions (1-5 each):

1. **Specificity** — Are principles backed by real decisions, or generic platitudes?
2. **Deployability** — Could a cold-booted AI pass the boot tests using only this file?
3. **Consistency** — Do the anti-patterns and conflict rules follow from the principles?
4. **Completeness** — Does it cover the 6 priority areas (relationships, finance, health, career, growth, legacy)?

For each dimension, give a score and a 1-sentence justification.
Then give an overall PASS/FAIL (PASS = all dimensions >= 3).
If FAIL, list the 3 highest-priority fixes.

DNA to validate:
{dna_content}

Output format:
SCORE: X/20
VERDICT: PASS | FAIL
- Specificity: N/5 — [reason]
- Deployability: N/5 — [reason]
- Consistency: N/5 — [reason]
- Completeness: N/5 — [reason]
FIXES (if FAIL):
1. ...
2. ...
3. ..."""


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def synthesize_dna(intake_path: Path, output_path: Path, model: str) -> None:
    """Read filled intake form, call Claude, write dna_core.md."""
    intake_content = intake_path.read_text(encoding="utf-8")

    # Basic check: has the form been filled?
    placeholder_count = intake_content.count("[")
    if placeholder_count > 5:
        print(f"WARNING: form may still have {placeholder_count} unfilled placeholders.")

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print(f"Synthesizing DNA from {intake_path.name}...")
    message = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": SYNTHESIS_PROMPT.format(intake_content=intake_content),
            }
        ],
    )

    dna_content = message.content[0].text
    output_path.write_text(dna_content, encoding="utf-8")
    print(f"DNA written to {output_path}")
    print(f"Lines: {len(dna_content.splitlines())}")
    print(f"Tokens used: {message.usage.input_tokens} in / {message.usage.output_tokens} out")


def validate_dna(dna_path: Path, model: str) -> dict:
    """Run validation scorecard on a DNA file. Returns parsed scores."""
    dna_content = dna_path.read_text(encoding="utf-8")

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print(f"Validating {dna_path.name}...")
    message = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": VALIDATION_PROMPT.format(dna_content=dna_content),
            }
        ],
    )

    result_text = message.content[0].text
    print(result_text)

    # Parse verdict
    verdict = "PASS" if "VERDICT: PASS" in result_text else "FAIL"
    score_match = re.search(r"SCORE:\s*(\d+)/20", result_text)
    score = int(score_match.group(1)) if score_match else 0

    return {"verdict": verdict, "score": score, "raw": result_text}


def run_pipeline(intake_path: Path, output_path: Path | None, model: str) -> None:
    """Full pipeline: synthesize → validate → report."""
    # Derive output path from intake filename if not specified
    if output_path is None:
        stem = intake_path.stem.replace("_intake", "").replace("intake_", "")
        output_path = intake_path.parent / f"{stem}_dna_core.md"

    # Synthesize
    synthesize_dna(intake_path, output_path, model)

    # Validate
    print()
    result = validate_dna(output_path, model)

    # Save validation result alongside DNA
    validation_path = output_path.with_suffix(".validation.json")
    validation_record = {
        "dna_file": str(output_path),
        "intake_file": str(intake_path),
        "model": model,
        "timestamp": datetime.utcnow().isoformat(),
        "verdict": result["verdict"],
        "score": result["score"],
        "raw": result["raw"],
    }
    validation_path.write_text(
        json.dumps(validation_record, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nValidation record saved to {validation_path}")

    if result["verdict"] == "FAIL":
        print("\nDNA failed validation. Address the FIXES above and re-run.")
        sys.exit(1)
    else:
        print(f"\nDNA PASSED validation (score {result['score']}/20). Ready to deploy.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="DNA Intake — generate a deployable dna_core.md from a questionnaire"
    )
    parser.add_argument(
        "--generate-form",
        action="store_true",
        help="Print a blank intake questionnaire to stdout",
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Path to filled intake form (.md)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path for dna_core.md (default: <input_stem>_dna_core.md)",
    )
    parser.add_argument(
        "--validate",
        type=Path,
        help="Validate an existing DNA file without running synthesis",
    )
    parser.add_argument(
        "--model",
        default="claude-sonnet-4-6",
        help="Claude model to use (default: claude-sonnet-4-6)",
    )

    args = parser.parse_args()

    if args.generate_form:
        print(INTAKE_FORM)
        return

    if args.validate:
        if not args.validate.exists():
            print(f"ERROR: file not found: {args.validate}")
            sys.exit(1)
        if "ANTHROPIC_API_KEY" not in os.environ:
            print("ERROR: ANTHROPIC_API_KEY not set")
            sys.exit(1)
        validate_dna(args.validate, args.model)
        return

    if args.input:
        if not args.input.exists():
            print(f"ERROR: intake file not found: {args.input}")
            sys.exit(1)
        if "ANTHROPIC_API_KEY" not in os.environ:
            print("ERROR: ANTHROPIC_API_KEY not set")
            sys.exit(1)
        run_pipeline(args.input, args.output, args.model)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
