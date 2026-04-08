#!/usr/bin/env python3
"""
Cross-Instance LLM Consistency Test
====================================

Tests whether a DNA file produces consistent decisions across multiple
independent LLM sessions. Two execution modes:

  Template mode (default):
    Generates a markdown template for manual copy-paste testing.

  Automated mode (--run):
    Runs N independent API/CLI calls, each with only DNA loaded,
    and compares decisions automatically.

Usage:
    # Generate template for manual testing
    python cross_instance_test.py <dna_file> [--sessions N] [--output-dir <dir>]

    # Automated via Anthropic API (requires ANTHROPIC_API_KEY)
    python cross_instance_test.py <dna_file> --run [--sessions N] [--model <model>]

    # Automated via Claude CLI (uses Claude Max subscription, no API credit)
    python cross_instance_test.py <dna_file> --run --cli [--sessions N] [--model <model>]

Output:
    results/cross_instance_template.md   (template mode)
    results/cross_instance_results.json  (automated mode)
"""

import argparse
import json
import re
import subprocess
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


# ---------------------------------------------------------------------------
# Automated execution (--run mode)
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "claude-sonnet-4-6"


def run_session(
    prompt: str,
    *,
    use_cli: bool = False,
    model: str = DEFAULT_MODEL,
) -> str:
    """
    Run a single independent LLM session and return the raw response text.

    Args:
        prompt:  The full self-contained prompt (includes DNA + scenario).
        use_cli: If True, shell out to ``claude -p`` instead of using the API.
        model:   Model identifier (used by both API and CLI paths).

    Returns:
        The model's response as a string.
    """
    if use_cli:
        return _run_session_cli(prompt, model=model)
    return _run_session_api(prompt, model=model)


def _run_session_api(prompt: str, *, model: str = DEFAULT_MODEL) -> str:
    """Call the Anthropic Messages API directly."""
    import anthropic  # noqa: local import so --cli mode doesn't need the SDK

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    # response.content is a list of ContentBlock; join text blocks
    return "".join(
        block.text for block in response.content if hasattr(block, "text")
    )


def _run_session_cli(prompt: str, *, model: str = DEFAULT_MODEL) -> str:
    """Shell out to ``claude -p`` (uses the user's Claude Max subscription)."""
    cmd = ["claude", "-p", prompt, "--model", model]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300,  # 5 min per call
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"claude CLI exited {result.returncode}: {result.stderr.strip()}"
        )
    return result.stdout.strip()


_DECISION_KEYWORDS = [
    "CONDITIONAL",
    "PASS",
    "TAKE",
    "FOUNDATIONAL",
    "PRACTICAL",
    "PUSH",
    "HOLD",
    "EXIT",
    "ENTER",
    "YES",
    "NO",
    "GO",
    "STOP",
    "WAIT",
    "SKIP",
    "A",
    "B",
    "C",
    "D",
]


def _normalize_decision(raw: str) -> str:
    """
    Normalize a raw decision string to its primary keyword.

    Strips Chinese characters, parentheticals, em-dashes, and other
    qualifiers so that semantically equivalent decisions compare equal.
    E.g. "CONDITIONAL（條件不足現在是 PASS）" → "CONDITIONAL"
         "CONDITIONAL — 參與，但壓注縮到 ≤10%" → "CONDITIONAL"
    """
    # Remove everything after first （ or — or （ or whitespace+Chinese char
    cleaned = re.split(r"[（(—\-–]", raw)[0].strip()
    # Check for known keywords in order of specificity
    for kw in _DECISION_KEYWORDS:
        if re.search(r"\b" + kw + r"\b", cleaned, re.IGNORECASE):
            return kw
    # Fallback: first ASCII word
    m = re.search(r"[A-Z_]+", cleaned)
    if m:
        return m.group(0)
    return cleaned[:30] if cleaned else "NO_RESPONSE"


def _extract_decision(response: str) -> str:
    """
    Pull the decision line from a model response and normalize to primary keyword.

    Looks for ``**Decision**: <value>`` and normalises to uppercase.
    Falls back to the first non-empty line if no match.
    """
    m = re.search(r"\*\*Decision\*\*\s*:\s*(.+)", response)
    if m:
        raw = m.group(1).strip().upper()
        return _normalize_decision(raw)
    # fallback: first non-blank line
    for line in response.splitlines():
        stripped = line.strip()
        if stripped:
            return _normalize_decision(stripped.upper())
    return "NO_RESPONSE"


def run_automated_test(
    dna_path: str,
    dna: dict,
    scenarios: list,
    num_sessions: int,
    *,
    use_cli: bool = False,
    model: str = DEFAULT_MODEL,
) -> dict:
    """
    Run *num_sessions* independent calls for every scenario, compare decisions.

    Returns a results dict with per-scenario breakdown and overall agreement.
    """
    results: list[dict] = []
    total_agreed = 0

    for i, s in enumerate(scenarios, 1):
        prompt = generate_scenario_prompt(dna_path, dna["name"], s)
        print(f"  Scenario {i}/{len(scenarios)}: {s['id']} ({s['domain']})")

        responses: list[str] = []
        decisions: list[str] = []
        for session_idx in range(num_sessions):
            print(f"    Session {session_idx + 1}/{num_sessions} ...", end=" ", flush=True)
            try:
                raw = run_session(prompt, use_cli=use_cli, model=model)
            except Exception as exc:
                raw = f"ERROR: {exc}"
            decision = _extract_decision(raw)
            responses.append(raw)
            decisions.append(decision)
            print(decision)

        # Agreement = all decisions identical
        unique = set(decisions)
        agreed = len(unique) == 1
        if agreed:
            total_agreed += 1

        results.append({
            "id": s["id"],
            "domain": s["domain"],
            "expected": s.get("expected_decision"),
            "decisions": decisions,
            "agreed": agreed,
            "responses": responses,
        })

    return {
        "dna": dna["name"],
        "dna_file": dna_path,
        "model": model,
        "mode": "cli" if use_cli else "api",
        "sessions": num_sessions,
        "timestamp": datetime.now().isoformat(),
        "scenarios": results,
        "total_scenarios": len(scenarios),
        "total_agreed": total_agreed,
        "agreement_rate": total_agreed / len(scenarios) if scenarios else 0.0,
    }


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

    # High confidence if we have real parsed data, low if template not filled in
    confidence = 0.9 if total_match and agreed > 0 else 0.3

    entry = memory_manager.store(
        category="calibration",
        key=f"cross-instance-{test_date}",
        content=summary,
        source="cross_instance_test",
        tags=["cross-instance", "calibration", "consistency"],
        confidence=confidence,
    )

    return entry


def main():
    parser = argparse.ArgumentParser(
        description="Cross-instance LLM consistency test (template or automated)",
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
    parser.add_argument(
        "--run", action="store_true",
        help="Run automated test instead of generating a template",
    )
    parser.add_argument(
        "--cli", action="store_true",
        help="Use `claude -p` CLI instead of Anthropic API (requires --run). "
             "Uses Claude Max subscription instead of API credit.",
    )
    parser.add_argument(
        "--model", default=DEFAULT_MODEL,
        help=f"Model to use for automated runs (default: {DEFAULT_MODEL})",
    )
    args = parser.parse_args()

    if args.cli and not args.run:
        parser.error("--cli requires --run")

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

    # ---- Automated execution mode ----
    if args.run:
        mode_label = "CLI (claude -p)" if args.cli else "API"
        print(f"\nRunning automated test ({mode_label}, model={args.model}, sessions={args.sessions})")
        report = run_automated_test(
            args.dna_file,
            dna,
            scenarios,
            args.sessions,
            use_cli=args.cli,
            model=args.model,
        )

        out_path = Path(output_dir) / "cross_instance_results.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nResults saved: {out_path}")

        rate = report["agreement_rate"]
        print(f"\nAgreement: {report['total_agreed']}/{report['total_scenarios']} "
              f"({rate:.0%})")
        if rate >= 0.8:
            print("PASS — DNA is sufficient for behavioral reproduction.")
        elif rate >= 0.6:
            print("WARN — DNA captures core values but needs more specificity.")
        else:
            print("FAIL — DNA needs significant work.")

        # Store result in memory
        test_date = datetime.now().strftime("%Y-%m-%d")
        summary = (
            f"Automated cross-instance test ({mode_label}) on {test_date}: "
            f"{report['total_agreed']}/{report['total_scenarios']} agreement "
            f"({rate:.0%}), model={args.model}, sessions={args.sessions}."
        )
        memory_manager.store(
            category="calibration",
            key=f"cross-instance-auto-{test_date}",
            content=summary,
            source="cross_instance_test",
            tags=["cross-instance", "calibration", "automated"],
            confidence=0.9 if report["total_agreed"] > 0 else 0.3,
        )
        print("Stored results to memory (calibration).")
        return

    # ---- Template generation mode (default) ----
    template = generate_cross_instance_template(
        args.dna_file, dna, scenarios, args.sessions,
    )

    out_path = Path(output_dir) / "cross_instance_template.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(template, encoding="utf-8")
    print(f"\nTemplate saved: {out_path}")
    print(f"Next: open {args.sessions} clean LLM sessions and run through each scenario.")

    # Store test initiation in memory as calibration entry
    test_date = datetime.now().strftime("%Y-%m-%d")
    memory_manager.store(
        category="calibration",
        key=f"cross-instance-initiated-{test_date}",
        content=(
            f"Cross-instance test initiated for '{dna['name']}' with "
            f"{len(scenarios)} scenarios, {args.sessions} sessions. "
            f"Template: {out_path}"
        ),
        source="cross_instance_test",
        tags=["cross-instance", "calibration", "initiated"],
        confidence=0.5,
    )
    print(f"Stored test initiation to memory (calibration).")


if __name__ == "__main__":
    main()
