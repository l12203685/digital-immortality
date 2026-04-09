#!/usr/bin/env python3
"""
Export Validation System for Digital Immortality
=================================================

Validates that exported platform prompts faithfully preserve the source DNA.

For each export file in platform/exports/, verifies:
1. All decision kernels (core principles) from the source DNA are present
2. Boot test scenarios are included
3. The recursive loop prompt is included
4. The activation/system prompt is well-formed

Compares exported content against the source DNA to ensure nothing was lost
during the export process.

Usage:
    python validate_exports.py
    python validate_exports.py --dna templates/example_dna.md
    python validate_exports.py --exports-dir platform/exports
    python validate_exports.py --scenarios templates/generic_boot_tests.json
    python validate_exports.py --verbose

Output:
    Validation report: PASS/FAIL per export with specific missing items.
    Exit code 0 if all pass, 1 if any fail.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Reuse parse_dna from the existing codebase
sys.path.insert(0, str(Path(__file__).resolve().parent))
from organism_interact import parse_dna

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DNA = PROJECT_ROOT / "templates" / "example_dna.md"
DEFAULT_EXPORTS_DIR = PROJECT_ROOT / "platform" / "exports"
DEFAULT_SCENARIOS = PROJECT_ROOT / "templates" / "generic_boot_tests.json"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    """Result of a single validation check."""
    name: str
    passed: bool
    details: str = ""
    missing_items: list[str] = field(default_factory=list)


@dataclass
class ExportValidation:
    """Full validation result for one export file."""
    filepath: str
    platform: str
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)

    @property
    def pass_count(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def fail_count(self) -> int:
        return sum(1 for c in self.checks if not c.passed)


# ---------------------------------------------------------------------------
# DNA extraction helpers
# ---------------------------------------------------------------------------

def extract_core_principles(dna_text: str) -> list[dict]:
    """
    Extract core principles from the DNA markdown.

    Returns list of dicts with 'name' and 'description' keys.
    Looks for numbered list items with bold names under the Core Principles
    section (section 0).
    """
    principles = []
    # Match patterns like: 1. **EV thinking** -- description
    # or: 1. **Bias toward inaction** -- description
    pattern = re.compile(
        r"^\s*\d+\.\s+\*\*(.+?)\*\*\s*[—–-]+\s*(.+)",
        re.MULTILINE,
    )
    # Find the Core Principles section
    core_section_match = re.search(
        r"##\s+0\.\s+Core Principles\b(.*?)(?=\n##\s|\Z)",
        dna_text,
        re.DOTALL | re.IGNORECASE,
    )
    search_text = core_section_match.group(1) if core_section_match else dna_text

    for m in pattern.finditer(search_text):
        name = m.group(1).strip()
        description = m.group(2).strip()
        principles.append({"name": name, "description": description})

    return principles


def extract_boot_critical(dna_text: str) -> list[str]:
    """
    Extract BOOT_CRITICAL rules from the DNA.

    Returns list of rule text strings.
    """
    rules = []
    boot_section = re.search(
        r"##\s+BOOT_CRITICAL\b(.*?)(?=\n---|\n##\s|\Z)",
        dna_text,
        re.DOTALL | re.IGNORECASE,
    )
    if not boot_section:
        return rules

    # Match numbered items with bold text
    pattern = re.compile(r"^\s*\d+\.\s+\*\*(.+?)\*\*", re.MULTILINE)
    for m in pattern.finditer(boot_section.group(1)):
        rules.append(m.group(1).strip())

    return rules


def extract_dna_sections(dna_text: str) -> list[str]:
    """Extract all section headers from the DNA."""
    sections = []
    for m in re.finditer(r"^##\s+(.+)", dna_text, re.MULTILINE):
        sections.append(m.group(1).strip())
    return sections


def load_scenarios(filepath: str | Path) -> list[dict]:
    """Load boot test scenarios from a JSON file."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Scenarios file not found: {filepath}")
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    return data.get("scenarios", data if isinstance(data, list) else [])


# ---------------------------------------------------------------------------
# Content extraction from exports
# ---------------------------------------------------------------------------

def read_export_content(filepath: Path) -> str:
    """
    Read the text content of an export file.

    For JSON exports (OpenAI format), extracts the combined text from all
    message content fields.
    """
    raw = filepath.read_text(encoding="utf-8", errors="replace")

    if filepath.suffix == ".json":
        try:
            data = json.loads(raw)
            # OpenAI format: list of {role, content} messages
            if isinstance(data, list):
                parts = []
                for msg in data:
                    if isinstance(msg, dict) and "content" in msg:
                        parts.append(msg["content"])
                return "\n\n".join(parts)
        except json.JSONDecodeError:
            pass

    return raw


def detect_platform(filepath: Path) -> str:
    """Detect platform type from filename convention: name_platform.ext"""
    stem = filepath.stem
    for platform in ("generic", "openai", "gemini"):
        if stem.endswith(f"_{platform}"):
            return platform
    # Fallback: infer from extension
    if filepath.suffix == ".json":
        return "openai"
    return "generic"


# ---------------------------------------------------------------------------
# Validation checks
# ---------------------------------------------------------------------------

def check_core_principles(export_text: str, principles: list[dict]) -> CheckResult:
    """
    Verify all core principles from the DNA are present in the export.

    Checks for the principle name (bold text) in the export content.
    """
    missing = []
    for p in principles:
        name = p["name"]
        # Check that the principle name appears in the export
        # Use case-insensitive search for the bold name
        if name.lower() not in export_text.lower():
            missing.append(f"Core principle: {name}")

    if missing:
        return CheckResult(
            name="Core Principles",
            passed=False,
            details=f"{len(missing)} of {len(principles)} core principles missing",
            missing_items=missing,
        )
    return CheckResult(
        name="Core Principles",
        passed=True,
        details=f"All {len(principles)} core principles present",
    )


def check_principle_descriptions(export_text: str, principles: list[dict]) -> CheckResult:
    """
    Verify that principle descriptions (not just names) are preserved.

    Checks for key phrases from each principle's description text.
    """
    missing = []
    for p in principles:
        desc = p["description"]
        # Extract a meaningful snippet (first sentence or first 80 chars)
        # to check for in the export
        snippet = desc.split(".")[0].strip() if "." in desc[:100] else desc[:80].strip()
        if snippet.lower() not in export_text.lower():
            missing.append(f"Description for '{p['name']}': \"{snippet}...\"")

    if missing:
        return CheckResult(
            name="Principle Descriptions",
            passed=False,
            details=f"{len(missing)} of {len(principles)} principle descriptions missing or truncated",
            missing_items=missing,
        )
    return CheckResult(
        name="Principle Descriptions",
        passed=True,
        details=f"All {len(principles)} principle descriptions preserved",
    )


def check_boot_critical(export_text: str, boot_rules: list[str]) -> CheckResult:
    """Verify BOOT_CRITICAL rules are present."""
    missing = []
    for rule in boot_rules:
        if rule.lower() not in export_text.lower():
            missing.append(f"BOOT_CRITICAL rule: {rule}")

    if missing:
        return CheckResult(
            name="BOOT_CRITICAL Rules",
            passed=False,
            details=f"{len(missing)} of {len(boot_rules)} BOOT_CRITICAL rules missing",
            missing_items=missing,
        )
    return CheckResult(
        name="BOOT_CRITICAL Rules",
        passed=True,
        details=f"All {len(boot_rules)} BOOT_CRITICAL rules present",
    )


def check_dna_sections(export_text: str, sections: list[str]) -> CheckResult:
    """Verify all DNA section headers are present in the export."""
    missing = []
    for section in sections:
        # Sections might be reformatted, check for key words
        if section.lower() not in export_text.lower():
            missing.append(f"DNA section: {section}")

    if missing:
        return CheckResult(
            name="DNA Sections",
            passed=False,
            details=f"{len(missing)} of {len(sections)} DNA sections missing",
            missing_items=missing,
        )
    return CheckResult(
        name="DNA Sections",
        passed=True,
        details=f"All {len(sections)} DNA sections present",
    )


def check_boot_test_scenarios(export_text: str, scenarios: list[dict]) -> CheckResult:
    """
    Verify boot test scenarios are included in the export.

    Checks for scenario text and domain labels from the test suite.
    """
    missing = []
    for sc in scenarios:
        scenario_text = sc.get("scenario", "")
        domain = sc.get("domain", "unknown")
        sc_id = sc.get("id", domain)

        # Check for a distinctive substring of the scenario (first 60 chars)
        snippet = scenario_text[:60].strip()
        if snippet.lower() not in export_text.lower():
            missing.append(f"Boot test [{sc_id}]: \"{snippet}...\"")

    if missing:
        return CheckResult(
            name="Boot Test Scenarios",
            passed=False,
            details=f"{len(missing)} of {len(scenarios)} boot test scenarios missing",
            missing_items=missing,
        )
    return CheckResult(
        name="Boot Test Scenarios",
        passed=True,
        details=f"All {len(scenarios)} boot test scenarios present",
    )


def check_boot_test_reasoning(export_text: str, scenarios: list[dict]) -> CheckResult:
    """
    Verify expected reasoning hints are included for each boot test.
    """
    missing = []
    for sc in scenarios:
        reasoning = sc.get("expected_reasoning", "")
        domain = sc.get("domain", "unknown")
        sc_id = sc.get("id", domain)

        if not reasoning:
            continue

        snippet = reasoning[:60].strip()
        if snippet.lower() not in export_text.lower():
            missing.append(f"Reasoning hint [{sc_id}]: \"{snippet}...\"")

    if missing:
        return CheckResult(
            name="Boot Test Reasoning Hints",
            passed=False,
            details=f"{len(missing)} reasoning hints missing from boot tests",
            missing_items=missing,
        )
    return CheckResult(
        name="Boot Test Reasoning Hints",
        passed=True,
        details="All reasoning hints present",
    )


def check_recursive_loop(export_text: str) -> CheckResult:
    """
    Verify the recursive self-prompt loop instructions are present.

    Checks for key phrases that define the recursive loop protocol.
    """
    required_phrases = [
        "Input(t) = Output(t-1)",
        "Output(t) = LLM(Input(t))",
        "Stopping the loop = death",
        "Your own output IS the next input",
    ]

    missing = []
    for phrase in required_phrases:
        if phrase.lower() not in export_text.lower():
            missing.append(f"Recursive loop phrase: \"{phrase}\"")

    if missing:
        return CheckResult(
            name="Recursive Loop Protocol",
            passed=False,
            details=f"{len(missing)} of {len(required_phrases)} recursive loop elements missing",
            missing_items=missing,
        )
    return CheckResult(
        name="Recursive Loop Protocol",
        passed=True,
        details="Recursive loop protocol complete",
    )


def check_system_prompt(export_text: str, platform: str) -> CheckResult:
    """
    Verify the activation/system prompt is well-formed.

    Checks for:
    - System instruction presence (identity declaration)
    - Activation prompt (triggers the twin to start)
    - Platform-specific formatting
    """
    issues = []

    # Check for identity declaration
    if "you are not an assistant" not in export_text.lower():
        issues.append("Missing identity declaration ('You are not an assistant')")

    if "digital twin" not in export_text.lower():
        issues.append("Missing 'digital twin' identity framing")

    # Check for activation prompt
    activation_phrases = [
        "run the boot tests",
        "begin the recursive loop",
        "first output should be an action",
    ]
    found_activation = sum(
        1 for p in activation_phrases if p.lower() in export_text.lower()
    )
    if found_activation < 2:
        issues.append(
            f"Activation prompt incomplete: only {found_activation}/3 "
            f"activation phrases found"
        )

    # Check for behavioral rules
    behavioral_rules = [
        "you are this person",
        "action over report",
        "bias toward inaction",
        "never break character",
    ]
    found_rules = sum(
        1 for r in behavioral_rules if r.lower() in export_text.lower()
    )
    if found_rules < 3:
        issues.append(
            f"Behavioral rules incomplete: only {found_rules}/4 rules found"
        )

    # Platform-specific checks
    if platform == "openai":
        # Should be valid JSON with system + user messages
        # (Already parsed in read_export_content, but check structure)
        issues.extend(_check_openai_structure(export_text))
    elif platform == "gemini":
        if "SECTION:" not in export_text and "section:" not in export_text.lower():
            issues.append("Gemini export missing SECTION markers")
    elif platform == "generic":
        if "# Digital Twin Boot Prompt" not in export_text and "digital twin boot prompt" not in export_text.lower():
            issues.append("Generic export missing top-level heading")

    if issues:
        return CheckResult(
            name="System Prompt Well-Formedness",
            passed=False,
            details=f"{len(issues)} system prompt issues found",
            missing_items=issues,
        )
    return CheckResult(
        name="System Prompt Well-Formedness",
        passed=True,
        details="System prompt well-formed",
    )


def _check_openai_structure(export_text: str) -> list[str]:
    """Additional structural checks for OpenAI JSON format."""
    issues = []
    # The export_text is the combined content from read_export_content,
    # but we need to re-read the raw file for structural validation.
    # This is handled at a higher level; here we check content-level things.
    # The role/content structure was already validated during reading.
    return issues


def check_openai_json_structure(filepath: Path) -> CheckResult:
    """
    For OpenAI exports, validate the JSON message structure.
    """
    if filepath.suffix != ".json":
        return CheckResult(
            name="OpenAI JSON Structure",
            passed=True,
            details="Not a JSON export, skipping structural check",
        )

    issues = []
    try:
        raw = filepath.read_text(encoding="utf-8", errors="replace")
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        return CheckResult(
            name="OpenAI JSON Structure",
            passed=False,
            details=f"Invalid JSON: {e}",
            missing_items=[f"JSON parse error: {e}"],
        )

    if not isinstance(data, list):
        issues.append("Root element must be a list of messages")
    else:
        if len(data) < 2:
            issues.append(f"Expected at least 2 messages (system + user), found {len(data)}")

        roles_found = set()
        for i, msg in enumerate(data):
            if not isinstance(msg, dict):
                issues.append(f"Message {i} is not a dict")
                continue
            if "role" not in msg:
                issues.append(f"Message {i} missing 'role' field")
            else:
                roles_found.add(msg["role"])
            if "content" not in msg:
                issues.append(f"Message {i} missing 'content' field")
            elif not isinstance(msg["content"], str):
                issues.append(f"Message {i} 'content' is not a string")

        if "system" not in roles_found:
            issues.append("No 'system' role message found")
        if "user" not in roles_found:
            issues.append("No 'user' role message found")

    if issues:
        return CheckResult(
            name="OpenAI JSON Structure",
            passed=False,
            details=f"{len(issues)} JSON structure issues",
            missing_items=issues,
        )
    return CheckResult(
        name="OpenAI JSON Structure",
        passed=True,
        details="Valid OpenAI message format (system + user)",
    )


def check_dna_completeness(export_text: str, dna_raw: str) -> CheckResult:
    """
    Verify the full DNA content was embedded, not just fragments.

    Compares the DNA text line-by-line, checking that substantive lines
    (not blank lines or dividers) appear in the export.
    """
    dna_lines = dna_raw.strip().splitlines()
    missing = []
    checked = 0

    for line in dna_lines:
        stripped = line.strip()
        # Skip blank lines, dividers, and very short lines
        if not stripped or stripped == "---" or len(stripped) < 10:
            continue
        # Skip markdown formatting-only lines
        if stripped.startswith("|---") or stripped == "|":
            continue

        checked += 1
        if stripped.lower() not in export_text.lower():
            # Allow some tolerance for reformatting -- check a shorter snippet
            short = stripped[:50].strip()
            if short.lower() not in export_text.lower():
                missing.append(stripped[:80])

    # Allow up to 5% missing (formatting differences)
    threshold = max(1, int(checked * 0.05))
    if len(missing) > threshold:
        return CheckResult(
            name="DNA Completeness",
            passed=False,
            details=f"{len(missing)} of {checked} substantive DNA lines missing from export (threshold: {threshold})",
            missing_items=missing[:10],  # Show first 10
        )
    return CheckResult(
        name="DNA Completeness",
        passed=True,
        details=f"DNA content preserved ({checked} substantive lines checked, {len(missing)} minor differences)",
    )


# ---------------------------------------------------------------------------
# Main validation orchestration
# ---------------------------------------------------------------------------

def validate_export(
    filepath: Path,
    dna_raw: str,
    principles: list[dict],
    boot_rules: list[str],
    dna_sections: list[str],
    scenarios: list[dict],
) -> ExportValidation:
    """Run all validation checks on a single export file."""
    platform = detect_platform(filepath)
    validation = ExportValidation(filepath=str(filepath), platform=platform)

    # Read export content
    export_text = read_export_content(filepath)

    # Run all checks
    validation.checks.append(check_core_principles(export_text, principles))
    validation.checks.append(check_principle_descriptions(export_text, principles))
    validation.checks.append(check_boot_critical(export_text, boot_rules))
    validation.checks.append(check_dna_sections(export_text, dna_sections))
    validation.checks.append(check_boot_test_scenarios(export_text, scenarios))
    validation.checks.append(check_boot_test_reasoning(export_text, scenarios))
    validation.checks.append(check_recursive_loop(export_text))
    validation.checks.append(check_system_prompt(export_text, platform))
    validation.checks.append(check_dna_completeness(export_text, dna_raw))

    # Platform-specific structural checks
    if platform == "openai":
        validation.checks.append(check_openai_json_structure(filepath))

    return validation


def find_exports(exports_dir: Path) -> list[Path]:
    """Find all export files in the exports directory."""
    if not exports_dir.exists():
        return []

    exports = []
    for ext in ("*.md", "*.json"):
        exports.extend(exports_dir.glob(ext))

    return sorted(exports)


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------

def format_report(validations: list[ExportValidation], verbose: bool = False) -> str:
    """Format the validation results as a human-readable report."""
    lines = []
    lines.append("=" * 60)
    lines.append("EXPORT VALIDATION REPORT")
    lines.append("=" * 60)
    lines.append("")

    all_passed = True

    for v in validations:
        status = "PASS" if v.passed else "FAIL"
        if not v.passed:
            all_passed = False

        lines.append(f"--- {Path(v.filepath).name} ({v.platform}) ---")
        lines.append(f"  Status: {status} ({v.pass_count}/{len(v.checks)} checks passed)")

        for check in v.checks:
            marker = "  [PASS]" if check.passed else "  [FAIL]"
            lines.append(f"  {marker} {check.name}: {check.details}")

            if not check.passed and (verbose or check.missing_items):
                for item in check.missing_items:
                    lines.append(f"         - {item}")

        lines.append("")

    # Summary
    lines.append("=" * 60)
    total = len(validations)
    passed = sum(1 for v in validations if v.passed)
    failed = total - passed

    if all_passed:
        lines.append(f"RESULT: ALL PASSED ({total}/{total} exports valid)")
    else:
        lines.append(f"RESULT: {failed} FAILED ({passed}/{total} exports valid)")
    lines.append("=" * 60)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Validate exported platform prompts against source DNA.",
    )
    parser.add_argument(
        "--dna",
        default=str(DEFAULT_DNA),
        help=f"Path to source DNA file (default: {DEFAULT_DNA})",
    )
    parser.add_argument(
        "--exports-dir",
        default=str(DEFAULT_EXPORTS_DIR),
        help=f"Directory containing export files (default: {DEFAULT_EXPORTS_DIR})",
    )
    parser.add_argument(
        "--scenarios",
        default=str(DEFAULT_SCENARIOS),
        help=f"Path to boot test scenarios JSON (default: {DEFAULT_SCENARIOS})",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed missing items for all checks",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of human-readable report",
    )

    args = parser.parse_args()

    # Load source DNA
    dna_path = Path(args.dna)
    if not dna_path.exists():
        print(f"ERROR: DNA file not found: {args.dna}", file=sys.stderr)
        sys.exit(2)

    dna_raw = dna_path.read_text(encoding="utf-8", errors="replace")
    principles = extract_core_principles(dna_raw)
    boot_rules = extract_boot_critical(dna_raw)
    dna_sections = extract_dna_sections(dna_raw)

    if not principles:
        print("WARNING: No core principles extracted from DNA. Check DNA format.", file=sys.stderr)

    # Load scenarios
    scenarios = []
    scenarios_path = Path(args.scenarios)
    if scenarios_path.exists():
        scenarios = load_scenarios(args.scenarios)
    else:
        print(f"WARNING: Scenarios file not found: {args.scenarios}", file=sys.stderr)

    # Find exports
    exports_dir = Path(args.exports_dir)
    export_files = find_exports(exports_dir)

    if not export_files:
        print(f"ERROR: No export files found in {exports_dir}", file=sys.stderr)
        sys.exit(2)

    # Validate each export
    validations = []
    for filepath in export_files:
        v = validate_export(
            filepath=filepath,
            dna_raw=dna_raw,
            principles=principles,
            boot_rules=boot_rules,
            dna_sections=dna_sections,
            scenarios=scenarios,
        )
        validations.append(v)

    # Output results
    if args.json:
        result = {
            "validations": [
                {
                    "filepath": v.filepath,
                    "platform": v.platform,
                    "passed": v.passed,
                    "pass_count": v.pass_count,
                    "fail_count": v.fail_count,
                    "checks": [
                        {
                            "name": c.name,
                            "passed": c.passed,
                            "details": c.details,
                            "missing_items": c.missing_items,
                        }
                        for c in v.checks
                    ],
                }
                for v in validations
            ],
            "summary": {
                "total_exports": len(validations),
                "passed": sum(1 for v in validations if v.passed),
                "failed": sum(1 for v in validations if not v.passed),
                "all_passed": all(v.passed for v in validations),
            },
        }
        print(json.dumps(result, indent=2))
    else:
        report = format_report(validations, verbose=args.verbose)
        print(report)

    # Exit code
    if all(v.passed for v in validations):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
