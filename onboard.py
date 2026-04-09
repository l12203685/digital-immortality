#!/usr/bin/env python3
"""Interactive onboarding for Digital Immortality.

Usage:
    python onboard.py --new              # Guided DNA creation
    python onboard.py --validate DNA.md  # Validate an existing DNA file
    python onboard.py --quickstart       # Print getting-started guide
"""

import argparse
import os
import re
import sys
import textwrap
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = SCRIPT_DIR / "templates" / "example_dna.md"
QUICKSTART_PATH = SCRIPT_DIR / "templates" / "quickstart.md"

# ──────────────────────────────────────────────
#  Required sections for DNA validation
# ──────────────────────────────────────────────

REQUIRED_SECTIONS = [
    "BOOT_CRITICAL",
    "Core Principles",
    "Identity",
    "Decision Framework",
]

ALL_SECTIONS = REQUIRED_SECTIONS + [
    "Communication Style",
    "Relationships",
    "Career & Finance",
    "Values Demonstrated in Action",
]

# ──────────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────────

def _prompt(question: str, *, default: str = "", required: bool = True,
            example: str = "") -> str:
    """Ask the user a question. Repeat until non-empty if required."""
    while True:
        suffix = f" [{default}]" if default else ""
        print(f"\n  {question}{suffix}")
        if example:
            print(f"  {example}")
        answer = input("  > ").strip()
        if not answer and default:
            return default
        if answer or not required:
            return answer
        print("  (This one is required -- please enter something.)")


def _prompt_list(question: str, *, min_count: int = 1, max_count: int = 8,
                 example: str = "") -> list[str]:
    """Collect a list of items one at a time. Empty line finishes."""
    print(f"\n  {question}")
    if example:
        print(f"  Example: {example}")
    print(f"  Enter one per line. Empty line when done (min {min_count}).")
    items: list[str] = []
    while True:
        label = f"  [{len(items) + 1}] > "
        item = input(label).strip()
        if not item:
            if len(items) >= min_count:
                break
            print(f"  (Need at least {min_count}. You have {len(items)}.)")
            continue
        items.append(item)
        if len(items) >= max_count:
            print(f"  (Reached max of {max_count}.)")
            break
    return items


def _header(text: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}")


# ──────────────────────────────────────────────
#  --new: Guided DNA creation
# ──────────────────────────────────────────────

def cmd_new(args: argparse.Namespace) -> None:
    _header("Digital Immortality -- Create Your DNA")
    print(textwrap.dedent("""\
        You are about to create a DNA file -- the behavioral core of your
        digital twin. This takes about 5 minutes.

        We will cover three sections:
          0. Core Principles  -- the rules that never change
          1. Identity         -- who you are
          2. Decision Framework -- how you actually decide

        Be specific and honest. "I skip exercise" is more useful than
        "I value health." There are no wrong answers.
    """))

    input("  Press Enter to begin...")

    # ── Identity ──────────────────────────────
    _header("Section 1: Identity")

    name = _prompt("What is your name?")
    age = _prompt("Age?", required=False)
    location = _prompt("Where do you live? (city, country)", required=False)
    role = _prompt("What do you do? (job, occupation, or however you describe yourself)")
    core_goal = _prompt(
        "What are you working toward right now? Be specific.",
        example="e.g. 'Build a side income that covers rent by end of year'",
    )
    philosophy = _prompt(
        "One sentence that captures how you see life.",
        example="e.g. 'Optimize for freedom, not status.'",
    )

    # ── Core Principles ──────────────────────
    _header("Section 0: Core Principles")
    print(textwrap.dedent("""\
        These are the 3-8 rules that NEVER change across all domains of
        your life -- career, relationships, money, daily behavior.

        Format each as a short name, then explain how it shows up.
    """))
    print("  Examples from the template:")
    print("    EV thinking -- Every decision is an expected value calculation.")
    print("    Bias toward inaction -- No clear edge = no action.")
    print()

    principles = _prompt_list(
        "Enter your core principles (short name -- explanation):",
        min_count=3,
        max_count=8,
        example="Skin in the game -- I don't give advice I wouldn't follow myself.",
    )

    # ── Decision Framework ────────────────────
    _header("Section 2: Decision Framework")
    print(textwrap.dedent("""\
        How do you ACTUALLY make decisions? Not "I think carefully" but
        the specific steps you go through.
    """))

    step1 = _prompt(
        "Step 1 -- How do you identify the real problem?",
        example="e.g. 'Strip away noise. What is the actual decision?'",
    )
    step2 = _prompt(
        "Step 2 -- How do you evaluate options?",
        example="e.g. 'Calculate expected value. Check opportunity cost.'",
    )
    step3 = _prompt(
        "Step 3 -- How do you decide and act?",
        example="e.g. 'If reversible, act fast. If irreversible, sleep on it.'",
    )

    # Ask for a couple of real decision examples
    print("\n  Now give 1-3 real decisions you have made, so the DNA is grounded.")
    print("  Format: situation | what you decided | why")
    print("  Empty line when done (min 1).")
    decisions: list[tuple[str, str, str]] = []
    while len(decisions) < 3:
        raw = input(f"  [{len(decisions) + 1}] > ").strip()
        if not raw:
            if decisions:
                break
            print("  (Need at least one real decision.)")
            continue
        parts = [p.strip() for p in raw.split("|")]
        if len(parts) < 3:
            parts += [""] * (3 - len(parts))
        decisions.append((parts[0], parts[1], parts[2]))

    # ── BOOT_CRITICAL derivation ──────────────
    boot_rules = [
        f"**You are {name}** -- not an assistant, not a representative. Think and act as them.",
        "**Action > Report** -- when you have enough context, do it and report what was done. Don't ask permission for reversible actions.",
        f"**Self-recurse** -- each output feeds back: \"what would {name} do next?\" If there is a next step, do it.",
    ]

    # ── Build the DNA file ────────────────────
    today = date.today().isoformat()
    principles_block = "\n".join(
        f"{i}. **{p.split('--')[0].strip() if '--' in p else p}**"
        f" -- {p.split('--', 1)[1].strip() if '--' in p else '(add cross-domain explanation)'}"
        for i, p in enumerate(principles, 1)
    )

    decisions_rows = "\n".join(
        f"| {d[0]} | {d[1]} | {d[2]} |" for d in decisions
    )

    identity_rows = [
        f"| Full name | {name} |",
        f"| Age | {age or '—'} |",
        f"| Location | {location or '—'} |",
        f"| Current role | {role} |",
        f"| Core goal | {core_goal} |",
        f"| Philosophy | {philosophy} |",
    ]

    dna = f"""\
# {name} DNA

> Generated by onboard.py on {today}.
> This is a living document. Update it as you learn more about yourself.

---

## BOOT_CRITICAL -- Read This First

{chr(10).join(f'{i}. {r}' for i, r in enumerate(boot_rules, 1))}

---

## 0. Core Principles

{principles_block}

---

## 1. Identity

| Field | Value |
|-------|-------|
{chr(10).join(identity_rows)}

---

## 2. Decision Framework

```
Step 1: {step1}

Step 2: {step2}

Step 3: {step3}
```

### Decision examples

| Situation | What you decided | Why (which principles) |
|-----------|-----------------|----------------------|
{decisions_rows}

---

## Next sections to fill in

When you are ready, add these sections (see templates/example_dna.md):
- Communication Style
- Relationships
- Career & Finance
- Values Demonstrated in Action
"""

    # ── Write output ──────────────────────────
    output_path = args.output or f"{name.lower().replace(' ', '_')}_dna.md"
    output_path = os.path.abspath(output_path)

    with open(output_path, "w") as f:
        f.write(dna)

    _header("DNA Created")
    print(f"  Written to: {output_path}")
    print()
    print("  What to do next:")
    print(f"    1. Read through the file and correct anything that feels off.")
    print(f"    2. Run validation:  python onboard.py --validate {output_path}")
    print(f"    3. Run boot test:   python consistency_test.py {output_path} --output-dir results")
    print(f"    4. Start the recursive engine:  python recursive_engine.py --init")
    print()
    print("  Your DNA is a living document. Every correction makes it sharper.")
    print()


# ──────────────────────────────────────────────
#  --validate: Validate an existing DNA file
# ──────────────────────────────────────────────

def cmd_validate(args: argparse.Namespace) -> None:
    filepath = args.file
    if not os.path.isfile(filepath):
        print(f"  Error: file not found: {filepath}")
        sys.exit(1)

    with open(filepath) as f:
        content = f.read()

    _header(f"Validating: {os.path.basename(filepath)}")

    issues: list[str] = []
    warnings: list[str] = []
    sections_found: list[str] = []

    # ── Check required sections ───────────────
    for section in ALL_SECTIONS:
        # Match markdown headings: ## BOOT_CRITICAL or ## 0. Core Principles etc.
        # Be flexible about numbering and formatting
        pattern = re.compile(
            r"^##\s+.*?" + re.escape(section.split("(")[0].strip().replace(" ", r"\s+")),
            re.MULTILINE | re.IGNORECASE,
        )
        # Simpler: just check if the section name appears after ##
        found = False
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("##") and not stripped.startswith("###"):
                # Normalize for comparison
                heading_text = re.sub(r"^##\s*\d*\.?\s*", "", stripped).strip()
                heading_text = re.sub(r"\s*[-—].*", "", heading_text).strip()
                if section.lower().startswith(heading_text.lower()) or \
                   heading_text.lower().startswith(section.lower()):
                    found = True
                    break
                # Also check partial match for things like "BOOT_CRITICAL — Read This First"
                if section.lower().replace(" ", "_") in heading_text.lower().replace(" ", "_"):
                    found = True
                    break
                if section.lower() in stripped.lower():
                    found = True
                    break

        if found:
            sections_found.append(section)
        elif section in REQUIRED_SECTIONS:
            issues.append(f"Missing required section: {section}")
        else:
            warnings.append(f"Optional section not found: {section}")

    # ── Check for unfilled brackets ───────────
    bracket_matches = re.findall(r"\[([^\]]{1,80})\]", content)
    # Filter out markdown link URLs and common false positives
    unfilled = []
    for match in bracket_matches:
        # Skip URLs, image refs, common markdown patterns
        if match.startswith("http") or match.startswith("!") or match == "x":
            continue
        # Flag things that look like placeholders
        if match.startswith("Your ") or match.startswith("your ") or \
           match.startswith("e.g.") or match.startswith("E.g.") or \
           "replace" in match.lower() or \
           match.startswith("Name") or match == "Name" or \
           match.startswith("Age") or \
           re.match(r"^[A-Z][a-z]+ [a-z]", match):  # "Something something" pattern
            unfilled.append(match)

    if unfilled:
        # Deduplicate
        unique = list(dict.fromkeys(unfilled))
        if len(unique) <= 5:
            for u in unique:
                issues.append(f"Unfilled placeholder: [{u}]")
        else:
            issues.append(f"{len(unique)} unfilled placeholders found (e.g. [{unique[0]}], [{unique[1]}])")

    # ── Check principle count ─────────────────
    # Look for numbered items under Core Principles
    in_principles = False
    principle_count = 0
    for line in content.splitlines():
        if "Core Principles" in line and line.strip().startswith("##"):
            in_principles = True
            continue
        if in_principles and line.strip().startswith("##") and "Core Principles" not in line:
            break
        if in_principles and re.match(r"\s*\d+\.\s+\*\*", line):
            # Check it's not just a template placeholder
            if "[Principle" not in line:
                principle_count += 1

    if principle_count < 3:
        issues.append(
            f"Only {principle_count} core principle(s) found (minimum 3 recommended). "
            f"Look for numbered items with **bold names** under Core Principles."
        )

    # ── Check for a real name in Identity ─────
    if re.search(r"\|\s*Full name\s*\|\s*\[", content):
        issues.append("Identity: Full name is still a placeholder.")

    # ── Completeness score ────────────────────
    total_sections = len(ALL_SECTIONS)
    found_count = len(sections_found)
    completeness = int((found_count / total_sections) * 100)

    # Adjust for content quality
    has_decisions = bool(re.search(r"\|[^|]+\|[^|]+\|[^|]+\|", content))
    has_real_principles = principle_count >= 3

    # ── Report ────────────────────────────────
    print()
    print(f"  Sections:     {found_count}/{total_sections} ({completeness}% coverage)")
    print(f"  Principles:   {principle_count}")
    print(f"  Decisions:    {'yes' if has_decisions else 'none found'}")
    print()

    if issues:
        print(f"  Issues ({len(issues)}):")
        for issue in issues:
            print(f"    - {issue}")
        print()

    if warnings:
        print(f"  Notes ({len(warnings)}):")
        for w in warnings:
            print(f"    - {w}")
        print()

    if not issues:
        print("  Result: PASS -- DNA file looks good.")
        if warnings:
            print("  (Optional sections can be added over time.)")
    elif all("Optional" in i or "placeholder" in i.lower() for i in issues):
        print("  Result: PASS with warnings -- functional but could be improved.")
    else:
        print("  Result: NEEDS WORK -- fix the issues above before running boot tests.")

    print()


# ──────────────────────────────────────────────
#  --quickstart: Print getting-started guide
# ──────────────────────────────────────────────

def cmd_quickstart(args: argparse.Namespace) -> None:
    if QUICKSTART_PATH.exists():
        with open(QUICKSTART_PATH) as f:
            print(f.read())
    else:
        # Inline fallback
        print(textwrap.dedent("""\
            Digital Immortality -- Quick Start
            ===================================

            This project builds a behavioral digital twin: an AI that makes
            the decisions you would make, using a DNA file as its core.

            Step 1: Create your DNA
              python onboard.py --new

            Step 2: Validate it
              python onboard.py --validate your_dna.md

            Step 3: Run boot tests
              python consistency_test.py your_dna.md --output-dir results

            Step 4: Start the recursive engine
              python recursive_engine.py --init
              python recursive_engine.py --prompt

            After first boot:
            - Read results/ for test output
            - Correct any wrong decisions by updating your DNA
            - Each correction becomes a new boot test
            - Run /dna-calibrate in Claude Code for guided refinement

            Your DNA is never "done." It evolves as you do.
        """))


# ──────────────────────────────────────────────
#  CLI
# ──────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Digital Immortality onboarding tool.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python onboard.py --new                    Create a new DNA file interactively
              python onboard.py --new --output my.md     Create DNA, write to my.md
              python onboard.py --validate my_dna.md     Validate an existing DNA file
              python onboard.py --quickstart             Print the getting-started guide
        """),
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--new", action="store_true",
                       help="Guided DNA creation (interactive)")
    group.add_argument("--validate", metavar="FILE", dest="file",
                       help="Validate an existing DNA file")
    group.add_argument("--quickstart", action="store_true",
                       help="Print getting-started guide")

    parser.add_argument("--output", "-o",
                        help="Output path for --new mode (default: <name>_dna.md)")

    args = parser.parse_args()

    if args.new:
        cmd_new(args)
    elif args.file:
        cmd_validate(args)
    elif args.quickstart:
        cmd_quickstart(args)


if __name__ == "__main__":
    main()
