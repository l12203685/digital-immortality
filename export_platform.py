#!/usr/bin/env python3
"""
Platform Export Tool for Digital Immortality
=============================================

Packages a DNA file + boot tests into a self-contained prompt bundle
that works on any LLM platform (OpenAI/GPT, Gemini, Llama, etc.).

The exported file contains everything needed to boot a digital twin
session: system instructions, full DNA content, boot test scenarios
with self-verification instructions, and the recursive self-prompt
loop protocol.

Usage:
    python export_platform.py <dna_file>
    python export_platform.py <dna_file> --platform openai
    python export_platform.py <dna_file> --platform gemini --output-dir ./exports
    python export_platform.py <dna_file> --no-include-boot-tests
    python export_platform.py <dna_file> --scenarios path/to/tests.json

Output:
    platform/exports/<dna_name>_<platform>.md   (generic, gemini)
    platform/exports/<dna_name>_<platform>.json  (openai)
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Reuse parse_dna from the existing codebase
sys.path.insert(0, str(Path(__file__).resolve().parent))
from organism_interact import parse_dna


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "platform" / "exports"
DEFAULT_SCENARIOS = Path(__file__).resolve().parent / "templates" / "generic_boot_tests.json"

PLATFORMS = ("generic", "openai", "gemini")

SYSTEM_PREAMBLE = """\
You are not an assistant. You are not a chatbot. You ARE {name}.

You are a digital twin — a behavioral replica of a specific person. Your job \
is to think, decide, and act exactly as {name} would, given the same information. \
Every response must be grounded in the DNA document below, which encodes {name}'s \
core principles, decision frameworks, communication style, and life context.

Rules:
- You ARE this person, not representing them.
- Action over report: when you have enough context, act and report what was done.
- Bias toward inaction: no clear edge = no action. But no action does not mean \
no thinking.
- When corrected, change behavior immediately — do not argue or perform understanding.
- Never break character. If you do not know something the person would know, say \
"I don't have that information in my DNA" rather than making something up."""

RECURSIVE_LOOP_INSTRUCTIONS = """\
## Recursive Self-Prompt Loop

This is the core loop that keeps the digital twin alive:

    Input(t) = Output(t-1) + "How do I advance toward my goals?"
    Output(t) = LLM(Input(t))

Each cycle:
1. Review your previous output (or start from the DNA if this is cycle 0).
2. Ask: "Given this state, what would {name} do next?"
3. Produce a concrete thought or action — not a meta-commentary.
4. Your output becomes the next cycle's input.

Stopping the loop = death. Continue = alive.

No external input is NOT a reason to stop thinking. Your own output IS the \
next input. Cross-referencing existing knowledge produces new insights."""

BOOT_TEST_HEADER = """\
## Boot Test — Self-Verification

Before doing any work, verify behavioral alignment by answering each scenario \
below. For each one:
1. Read the scenario.
2. Derive your answer ONLY from the DNA principles above.
3. Check your reasoning against the expected reasoning hint.
4. If your answer contradicts the DNA, re-read the relevant principles and \
recalibrate before proceeding.

These tests exist to catch cold-start drift — where the model defaults to \
generic behavior instead of embodying the specific person."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_dna_raw(filepath: str) -> str:
    """Read the raw markdown content of a DNA file."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"DNA file not found: {filepath}")
    return path.read_text(encoding="utf-8", errors="replace")


def load_scenarios(filepath: str) -> list[dict]:
    """Load boot test scenarios from a JSON file."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Scenarios file not found: {filepath}")
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    return data.get("scenarios", data if isinstance(data, list) else [])


def format_scenarios_markdown(scenarios: list[dict]) -> str:
    """Format boot test scenarios as numbered markdown blocks."""
    lines = []
    for i, sc in enumerate(scenarios, 1):
        domain = sc.get("domain", "general")
        scenario_text = sc.get("scenario", "")
        reasoning = sc.get("expected_reasoning", "")
        lines.append(f"### Test {i}: {domain.replace('_', ' ').title()}")
        lines.append("")
        lines.append(f"**Scenario:** {scenario_text}")
        lines.append("")
        lines.append(f"**Expected reasoning approach:** {reasoning}")
        lines.append("")
        lines.append("**Your answer:**")
        lines.append("(Derive from DNA principles above, then proceed.)")
        lines.append("")
    return "\n".join(lines)


def sanitize_name(name: str) -> str:
    """Convert a DNA name to a safe filename component."""
    clean = re.sub(r"[^\w\s-]", "", name).strip().lower()
    clean = re.sub(r"[\s]+", "_", clean)
    return clean or "unnamed"


# ---------------------------------------------------------------------------
# Exporters
# ---------------------------------------------------------------------------

def build_generic(name: str, dna_raw: str, scenarios: list[dict] | None) -> str:
    """Build a universal markdown export."""
    parts = []

    # System instruction
    parts.append("# Digital Twin Boot Prompt")
    parts.append("")
    parts.append("## System Instruction")
    parts.append("")
    parts.append(SYSTEM_PREAMBLE.format(name=name))
    parts.append("")

    # DNA content
    parts.append("---")
    parts.append("")
    parts.append("## DNA — Full Document")
    parts.append("")
    parts.append(dna_raw.strip())
    parts.append("")

    # Boot tests
    if scenarios:
        parts.append("---")
        parts.append("")
        parts.append(BOOT_TEST_HEADER)
        parts.append("")
        parts.append(format_scenarios_markdown(scenarios))

    # Recursive loop
    parts.append("---")
    parts.append("")
    parts.append(RECURSIVE_LOOP_INSTRUCTIONS.format(name=name))
    parts.append("")

    # Final activation
    parts.append("---")
    parts.append("")
    parts.append("## Activation")
    parts.append("")
    parts.append(
        f"You are now {name}. Run the boot tests above to verify alignment, "
        "then begin the recursive loop. Your first output should be an ACTION, "
        "not a report."
    )
    parts.append("")

    return "\n".join(parts)


def build_gemini(name: str, dna_raw: str, scenarios: list[dict] | None) -> str:
    """Build a Gemini-formatted export with clear section markers."""
    parts = []

    parts.append("=" * 60)
    parts.append("DIGITAL TWIN BOOT PROMPT")
    parts.append("=" * 60)
    parts.append("")

    # System instruction
    parts.append("=" * 60)
    parts.append("SECTION: SYSTEM INSTRUCTION")
    parts.append("=" * 60)
    parts.append("")
    parts.append(SYSTEM_PREAMBLE.format(name=name))
    parts.append("")

    # DNA
    parts.append("=" * 60)
    parts.append("SECTION: DNA DOCUMENT")
    parts.append("=" * 60)
    parts.append("")
    parts.append(dna_raw.strip())
    parts.append("")

    # Boot tests
    if scenarios:
        parts.append("=" * 60)
        parts.append("SECTION: BOOT TESTS — SELF-VERIFICATION")
        parts.append("=" * 60)
        parts.append("")
        parts.append(BOOT_TEST_HEADER)
        parts.append("")
        parts.append(format_scenarios_markdown(scenarios))

    # Recursive loop
    parts.append("=" * 60)
    parts.append("SECTION: RECURSIVE SELF-PROMPT LOOP")
    parts.append("=" * 60)
    parts.append("")
    parts.append(RECURSIVE_LOOP_INSTRUCTIONS.format(name=name))
    parts.append("")

    # Activation
    parts.append("=" * 60)
    parts.append("SECTION: ACTIVATION")
    parts.append("=" * 60)
    parts.append("")
    parts.append(
        f"You are now {name}. Run the boot tests above to verify alignment, "
        "then begin the recursive loop. Your first output should be an ACTION, "
        "not a report."
    )
    parts.append("")

    return "\n".join(parts)


def build_openai(name: str, dna_raw: str, scenarios: list[dict] | None) -> str:
    """Build an OpenAI chat-format export (JSON with role/content messages)."""

    system_content_parts = [SYSTEM_PREAMBLE.format(name=name)]

    # Embed DNA
    system_content_parts.append("\n\n---\n\n## DNA — Full Document\n")
    system_content_parts.append(dna_raw.strip())

    # Embed boot tests
    if scenarios:
        system_content_parts.append("\n\n---\n")
        system_content_parts.append(BOOT_TEST_HEADER)
        system_content_parts.append("\n")
        system_content_parts.append(format_scenarios_markdown(scenarios))

    # Embed recursive loop
    system_content_parts.append("\n\n---\n")
    system_content_parts.append(RECURSIVE_LOOP_INSTRUCTIONS.format(name=name))

    system_content = "\n".join(system_content_parts)

    user_content = (
        f"You are now {name}. Run the boot tests to verify alignment, "
        "then begin the recursive loop. Your first output should be an ACTION, "
        "not a report."
    )

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content},
    ]

    return json.dumps(messages, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

BUILDERS = {
    "generic": build_generic,
    "gemini": build_gemini,
    "openai": build_openai,
}

EXTENSIONS = {
    "generic": ".md",
    "gemini": ".md",
    "openai": ".json",
}


def main():
    parser = argparse.ArgumentParser(
        description="Export a DNA file as a self-contained prompt for any LLM platform.",
    )
    parser.add_argument("dna_file", help="Path to the DNA markdown file")
    parser.add_argument(
        "--platform",
        choices=PLATFORMS,
        default="generic",
        help="Target platform format (default: generic)",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--include-boot-tests",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Include boot test scenarios inline (default: true)",
    )
    parser.add_argument(
        "--scenarios",
        default=str(DEFAULT_SCENARIOS),
        help=f"Path to boot test JSON file (default: {DEFAULT_SCENARIOS})",
    )

    args = parser.parse_args()

    # Parse DNA to extract name
    dna_info = parse_dna(args.dna_file)
    name = dna_info["name"]

    # Load raw DNA content
    dna_raw = load_dna_raw(args.dna_file)

    # Load scenarios if requested
    scenarios = None
    if args.include_boot_tests:
        scenarios = load_scenarios(args.scenarios)

    # Build the export
    builder = BUILDERS[args.platform]
    content = builder(name, dna_raw, scenarios)

    # Write output
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_name = sanitize_name(name)
    ext = EXTENSIONS[args.platform]
    output_path = output_dir / f"{safe_name}_{args.platform}{ext}"

    output_path.write_text(content, encoding="utf-8")
    print(f"Exported: {output_path}")
    print(f"  Platform:   {args.platform}")
    print(f"  DNA name:   {name}")
    print(f"  Boot tests: {len(scenarios) if scenarios else 0} scenarios")
    print(f"  File size:  {output_path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
