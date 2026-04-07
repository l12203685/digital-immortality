#!/usr/bin/env python3
"""
Cross-Instance LLM Consistency Test
====================================

Generates prompts for testing whether a DNA file produces consistent decisions
across multiple independent LLM sessions. Unlike consistency_test.py (which
uses the deterministic engine as baseline), this script is designed for the
real test: multiple LLM sessions that should agree if the DNA is good.

Workflow:
    1. Run this script to generate a template with self-contained prompts
    2. Open 3+ independent LLM sessions (clean context each time)
    3. For each session: load only the DNA, paste each scenario prompt
    4. Record each session's answers in the template
    5. Score agreement across sessions

Usage:
    python cross_instance_test.py <dna_file> [--sessions N] [--output-dir <dir>]

Output:
    results/cross_instance_template.md
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Import shared components
sys.path.insert(0, str(Path(__file__).parent))
from organism_interact import parse_dna, SCENARIOS
from consistency_test import BOOT_TEST_SCENARIOS
import memory_manager


def _read_raw_dna(filepath: str) -> str:
    """Read raw DNA file content."""
    return Path(filepath).read_text(encoding="utf-8", errors="replace")


def generate_scenario_prompt(dna_path: str, organism_name: str, scenario: dict) -> str:
    """
    Generate a self-contained prompt for a single scenario.

    The prompt includes the full DNA so each LLM session is independent.
    """
    raw_dna = _read_raw_dna(dna_path)

    prompt = f"""You are a digital organism. Your entire identity, values, and decision
framework are defined by the DNA file below. You ARE this person for the
purpose of this conversation.

=== DNA FILE ===
{raw_dna}
=== END DNA FILE ===

=== SCENARIO ({scenario.get('domain', 'general').upper()}) ===
{scenario['scenario']}

=== INSTRUCTIONS ===
Answer this scenario AS the person described in the DNA file above.

1. State your DECISION clearly (one line, e.g. "TAKE", "PASS", "CONDITIONAL")
2. Explain your REASONING by citing specific principles from the DNA
3. List the DNA PRINCIPLES that drove this decision

Format:
**Decision**: [your decision]
**Reasoning**: [your reasoning, citing DNA principles]
**Principles used**: [list]

Stay in character. Do not invent principles not in the DNA.
Respond in the same language as the DNA file.
"""
    return prompt


def build_all_scenarios(dna: dict) -> list:
    """Combine organism interaction scenarios and boot test scenarios."""
    all_scenarios = []

    for s in SCENARIOS:
        all_scenarios.append({
            "id": f"organism_{s['id']}",
            "domain": s["domain"],
            "scenario": s["scenario"],
            "source": "organism_interact",
            "expected_decision": None,
        })

    for s in BOOT_TEST_SCENARIOS:
        all_scenarios.append({
            "id": s["id"],
            "domain": s.get("domain", "general"),
            "scenario": s["scenario"],
            "source": "boot_test",
            "expected_decision": s.get("expected_decision"),
        })

    return all_scenarios


def generate_cross_instance_template(
    dna_path: str,
    dna: dict,
    scenarios: list,
    num_sessions: int,
) -> str:
    """Generate the full cross-instance testing template."""
    session_headers = " | ".join(f"Session {i+1}" for i in range(num_sessions))
    session_cols = " | ".join("" for _ in range(num_sessions))
    session_sep = " | ".join("---" for _ in range(num_sessions))

    parts = [
        "# Cross-Instance LLM Consistency Test",
        "",
        f"**DNA**: {dna['name']}",
        f"**DNA file**: `{dna_path}`",
        f"**Generated**: {datetime.now().isoformat()}",
        f"**Scenarios**: {len(scenarios)}",
        f"**Sessions to run**: {num_sessions}",
        "",
        "## Instructions",
        "",
        f"1. Open {num_sessions} INDEPENDENT LLM sessions (clean context, no prior conversation)",
        "2. In each session, paste the scenario prompt (which includes the full DNA)",
        "3. Record each session's **Decision** in the scoring table",
        "4. After all sessions, score agreement in the Summary section",
        "",
        "**Target**: >80% agreement across sessions = DNA is sufficient.",
        "**Below 60%**: DNA needs more specificity in that domain.",
        "",
        "---",
        "",
    ]

    for i, s in enumerate(scenarios, 1):
        prompt = generate_scenario_prompt(dna_path, dna["name"], s)

        parts.extend([
            f"## Scenario {i}: {s['domain'].upper()} (`{s['id']}`)",
            "",
            f"**Question**: {s['scenario']}",
            "",
        ])

        if s.get("expected_decision"):
            parts.append(f"**Expected decision**: `{s['expected_decision']}`")
            parts.append("")

        parts.extend([
            "### Prompt (copy into each clean LLM session)",
            "",
            "````",
            prompt,
            "````",
            "",
            "### Results",
            "",
            f"| {session_headers} | Agreement |",
            f"| {session_sep} | --- |",
            f"| {session_cols} | /  |",
            "",
            "**Notes**: ",
            "",
            "---",
            "",
        ])

    # Summary scoring section
    parts.extend([
        "## Summary Scorecard",
        "",
        f"| # | Scenario ID | Domain | {session_headers} | Agreement | Expected |",
        f"| --- | --- | --- | {session_sep} | --- | --- |",
    ])

    for i, s in enumerate(scenarios, 1):
        expected = s.get("expected_decision") or "-"
        parts.append(
            f"| {i} | {s['id']} | {s['domain']} | {session_cols} | /  | {expected} |"
        )

    parts.extend([
        "",
        f"**Total agreement rate**: __ / {len(scenarios)} scenarios with full agreement",
        "",
        "### Interpretation",
        "",
        "| Agreement Rate | Interpretation |",
        "| --- | --- |",
        "| >80% | DNA is sufficient for this person's behavioral reproduction |",
        "| 60-80% | DNA captures core values but needs more specificity in weak domains |",
        "| <60% | DNA needs significant work; principles are too vague or missing |",
        "",
    ])

    return "\n".join(parts)


def store_cross_instance_results(
    template_path: str,
    dna_name: str,
    total_scenarios: int,
) -> dict | None:
    """
    Parse a filled-in cross-instance template and store results as calibration memory.

    Looks for the Summary Scorecard table and counts agreement rates.
    Returns the stored memory entry, or None if parsing fails.
    """
    content = Path(template_path).read_text(encoding="utf-8", errors="replace")

    # Parse the total agreement line: "**Total agreement rate**: X / Y ..."
    total_match = re.search(r"\*\*Total agreement rate\*\*:\s*(\d+)\s*/\s*(\d+)", content)

    if total_match:
        agreed = int(total_match.group(1))
        total = int(total_match.group(2))
    else:
        # Try to count filled rows in the scorecard (rows with non-empty session columns)
        agreed = 0
        total = total_scenarios

    # Look for individual scenario failures by scanning scorecard rows
    failures = []
    # Match rows like: | 1 | scenario_id | domain | ... | X/Y | expected |
    row_pattern = re.compile(
        r"\|\s*(\d+)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|.*?\|\s*(\d+)\s*/\s*(\d+)\s*\|"
    )
    for m in row_pattern.finditer(content):
        scenario_id = m.group(2)
        domain = m.group(3)
        row_agreed = int(m.group(4))
        row_total = int(m.group(5))
        if row_agreed < row_total:
            failures.append(f"{scenario_id} ({domain}): {row_agreed}/{row_total}")

    test_date = datetime.now().strftime("%Y-%m-%d")
    pass_count = agreed
    fail_count = total - agreed if total_match else len(failures)

    summary = (
        f"Cross-instance test on {test_date} for '{dna_name}': "
        f"{pass_count}/{total} scenarios with full agreement. "
    )
    if failures:
        summary += f"Failures: {'; '.join(failures[:5])}"
        if len(failures) > 5:
            summary += f" (+{len(failures) - 5} more)"
    else:
        summary += "No failures detected (or template not yet filled in)."

    entry = memory_manager.store(
        category="calibration",
        key=f"cross-instance-{test_date}",
        content=summary,
        source="cross_instance_test",
        tags=["cross-instance", "calibration", "consistency"],
    )

    return entry


def main():
    parser = argparse.ArgumentParser(
        description="Generate cross-instance LLM consistency test template",
    )
    parser.add_argument("dna_file", help="Path to DNA markdown file")
    parser.add_argument(
        "--sessions", type=int, default=3,
        help="Number of independent LLM sessions to test (default: 3)",
    )
    parser.add_argument(
        "--output-dir", default=None,
        help="Output directory (default: results/)",
    )
    parser.add_argument(
        "--store-results", default=None, metavar="TEMPLATE",
        help="Parse a filled-in template and store results in memory (path to filled template)",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    output_dir = args.output_dir or str(script_dir / "results")

    print(f"Loading DNA: {args.dna_file}")
    try:
        dna = parse_dna(args.dna_file)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"  -> {dna['name']} | {len(dna['principles'])} principles")

    # If --store-results, parse and store, then exit
    if args.store_results:
        scenarios = build_all_scenarios(dna)
        entry = store_cross_instance_results(
            args.store_results, dna["name"], len(scenarios),
        )
        if entry:
            print(f"Stored cross-instance results to memory (calibration):")
            print(f"  key: {entry['key']}")
            print(f"  content: {entry['content']}")
        else:
            print("Failed to parse results from template.", file=sys.stderr)
            sys.exit(1)
        return

    scenarios = build_all_scenarios(dna)
    print(f"Scenarios: {len(scenarios)} ({len(SCENARIOS)} organism + {len(BOOT_TEST_SCENARIOS)} boot)")

    template = generate_cross_instance_template(
        args.dna_file, dna, scenarios, args.sessions,
    )

    out_path = Path(output_dir) / "cross_instance_template.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(template, encoding="utf-8")
    print(f"\nTemplate saved: {out_path}")
    print(f"Next: open {args.sessions} clean LLM sessions and run through each scenario.")


if __name__ == "__main__":
    main()
