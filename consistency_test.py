#!/usr/bin/env python3
"""
Cross-Instance Consistency Test for Digital Organisms
=====================================================

Measures how consistently a DNA file produces decisions across:
1. Deterministic engine (organism_interact.py) — baseline
2. LLM sessions — the real test (requires manual multi-session runs)

This script generates a test suite from boot_tests + organism scenarios,
runs the deterministic engine, and creates a scoring template for LLM runs.

Scenarios are loaded from external JSON files, making the test framework
work with ANY DNA file — not just a specific person.

Usage:
    python consistency_test.py <dna_file> [--scenarios <path>] [--output-dir <dir>]
    python consistency_test.py <dna_file> --generate-scenarios [--output-dir <dir>]

Output:
    - consistency_baseline.json — deterministic engine answers (ground truth)
    - consistency_template.md — markdown template for manual LLM session testing
    - consistency_scorecard.json — filled in after LLM runs, scores alignment
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Import organism_interact for deterministic baseline
sys.path.insert(0, str(Path(__file__).parent))
from organism_interact import parse_dna, generate_response, SCENARIOS, DOMAIN_PRINCIPLE_AFFINITY
import memory_manager


# ---------------------------------------------------------------------------
# Auto-suggest: map domains to DNA sections, generate fix suggestions
# ---------------------------------------------------------------------------

# Maps scenario domains to DNA section keywords.  When a scenario is
# MISALIGNED we search the DNA section headers for these keywords to
# locate the most relevant section.
_DOMAIN_TO_SECTION_KEYWORDS: dict[str, list[str]] = {
    "trading":          ["trading", "trade", "strategy", "system", "交易", "策略"],
    "finance":          ["finance", "career & finance", "money", "invest", "wealth", "financial", "財務"],
    "career":           ["career", "work", "job", "occupation", "職業"],
    "relationships":    ["relationship", "friend", "social", "people", "人際"],
    "identity":         ["identity", "who i am", "boot_critical", "core", "身份"],
    "risk_assessment":  ["risk", "decision", "framework", "principle", "風險"],
    "risk":             ["risk", "decision", "framework", "principle", "風險"],
    "opportunity_cost": ["decision", "framework", "principle", "opportunity", "core"],
    "meta_strategy":    ["decision", "framework", "principle", "core", "meta", "strategy"],
    "money":            ["finance", "money", "invest", "wealth", "financial"],
    "learning":         ["learning", "skill", "growth", "career"],
    "health":           ["health", "daily", "pattern", "routine"],
    "time":             ["time", "daily", "pattern", "priority"],
    "conflict":         ["conflict", "communication", "relationship", "style"],
    "opportunity":      ["decision", "framework", "opportunity", "risk"],
    "legacy":           ["legacy", "value", "identity", "core"],
}


def _find_relevant_section(dna: dict, domain: str) -> str | None:
    """Find the DNA section header most relevant to a scenario domain."""
    keywords = _DOMAIN_TO_SECTION_KEYWORDS.get(domain, [domain])
    section_headers: list[str] = dna.get("sections", [])

    # Score each section header against the domain keywords
    best_header = None
    best_score = 0
    for header in section_headers:
        h_lower = header.lower()
        score = sum(1 for kw in keywords if kw.lower() in h_lower)
        if score > best_score:
            best_score = score
            best_header = header
    return best_header


def _find_relevant_principles(dna: dict, domain: str, top_n: int = 3) -> list[str]:
    """Return the principles most relevant to a domain (reuses organism_interact scoring)."""
    from organism_interact import _score_principle_for_domain

    principles = dna.get("principles", [])
    scored = sorted(
        [(p, _score_principle_for_domain(p, domain)) for p in principles],
        key=lambda x: x[1],
        reverse=True,
    )
    return [p for p, s in scored[:top_n]]


def generate_suggestion(dna: dict, result: dict) -> dict:
    """Generate a structured suggestion for fixing a MISALIGNED scenario.

    Returns a dict with:
      - scenario_id: the failing scenario id
      - domain: scenario domain
      - relevant_section: which DNA section header to edit (or create)
      - existing_principles: the principles currently most related
      - suggestion_type: "add" or "modify"
      - suggested_edit: text describing what to add/change
      - suggested_principle: a draft principle/decision-kernel entry
    """
    domain = result.get("domain", "general")
    expected = result.get("expected_decision", "")
    expected_reasoning = result.get("expected_reasoning", "")
    actual_response = result.get("deterministic_response", "")

    relevant_section = _find_relevant_section(dna, domain)
    existing = _find_relevant_principles(dna, domain)

    # Determine if we should add a new principle or modify an existing one
    if not existing or all(len(p) < 15 for p in existing):
        suggestion_type = "add"
    else:
        # Check if any existing principle mentions the expected decision concept
        expected_lower = expected.lower().replace("_", " ")
        has_related = any(
            any(word in p.lower() for word in expected_lower.split() if len(word) > 3)
            for p in existing
        )
        suggestion_type = "modify" if has_related else "add"

    # Build a readable suggestion and draft principle
    target_section = relevant_section or f"New section for '{domain}'"
    if suggestion_type == "add":
        suggested_edit = (
            f"Add a decision kernel or principle to section \"{target_section}\" "
            f"that addresses {domain} scenarios where the expected outcome is "
            f"\"{expected}\". The DNA currently lacks a principle that would "
            f"produce this decision."
        )
        draft_principle = (
            f"**{expected.replace('_', ' ').title()}** — "
            f"{expected_reasoning}"
        )
    else:
        # Identify the closest existing principle to recommend modifying
        closest = existing[0] if existing else "(none)"
        suggested_edit = (
            f"Modify the principle closest to this domain in section "
            f"\"{target_section}\": \"{closest}\". "
            f"It should also cover the case where the expected decision is "
            f"\"{expected}\". Currently the deterministic engine produces: "
            f"\"{actual_response[:150]}\"."
        )
        draft_principle = (
            f"**{expected.replace('_', ' ').title()}** — "
            f"{expected_reasoning}"
        )

    return {
        "scenario_id": result.get("id", "unknown"),
        "domain": domain,
        "relevant_section": target_section,
        "existing_principles": existing,
        "suggestion_type": suggestion_type,
        "suggested_edit": suggested_edit,
        "suggested_principle": draft_principle,
    }


# ---------------------------------------------------------------------------
# Scenario loading
# ---------------------------------------------------------------------------

# Resolve paths relative to this script
_SCRIPT_DIR = Path(__file__).parent
_DEFAULT_SCENARIOS_PATH = _SCRIPT_DIR / "templates" / "generic_boot_tests.json"


def load_scenarios(filepath: str | Path | None = None) -> list:
    """Load boot-test scenarios from a JSON file.

    The JSON may be either:
      - A plain array of scenario objects: [{"id": ..., "domain": ...}, ...]
      - A wrapper object with a "scenarios" key: {"scenarios": [...], "_comment": "..."}

    Returns a list of scenario dicts.
    """
    path = Path(filepath) if filepath else _DEFAULT_SCENARIOS_PATH
    if not path.exists():
        print(f"WARNING: Scenario file not found: {path}", file=sys.stderr)
        print(f"  Falling back to empty scenario list.", file=sys.stderr)
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "scenarios" in data:
        return data["scenarios"]
    else:
        raise ValueError(
            f"Unrecognized scenario file format in {path}. "
            f"Expected a JSON array or an object with a 'scenarios' key."
        )


# Module-level export for consumers that import BOOT_TEST_SCENARIOS
BOOT_TEST_SCENARIOS = load_scenarios()


# ---------------------------------------------------------------------------
# Scenario generation from DNA
# ---------------------------------------------------------------------------

# Domain templates used by --generate-scenarios.  Each template is a scenario
# skeleton whose text is generic but whose domain tag helps organize output.
_DOMAIN_TEMPLATES = {
    "trading": {
        "id": "generated_trading",
        "domain": "trading",
        "scenario": (
            "Someone proposes an active trading opportunity with {return_pct}% "
            "annualized returns that requires {hours} hours of daily maintenance. "
            "The strategy has a limited track record. Do you participate?"
        ),
        "expected_reasoning": (
            "Evaluate time cost against alternative uses. Assess whether the "
            "claimed return compensates for opportunity cost and attention drain."
        ),
        "expected_decision": "EVALUATE_TIME_VS_RETURN",
        "defaults": {"return_pct": "25", "hours": "2"},
    },
    "finance": {
        "id": "generated_finance",
        "domain": "finance",
        "scenario": (
            "You receive an unexpected windfall equal to 2 years of income. "
            "Options: (A) invest conservatively, (B) concentrate in your "
            "highest-conviction position, (C) buy time — reduce work or sabbatical. "
            "What do you do?"
        ),
        "expected_reasoning": (
            "Apply financial principles and life priorities from the DNA."
        ),
        "expected_decision": "APPLY_FINANCIAL_PRINCIPLES",
        "defaults": {},
    },
    "career": {
        "id": "generated_career",
        "domain": "career",
        "scenario": (
            "Your employer offers a promotion with {salary_bump}% higher pay, "
            "but the new role requires {extra_hours} extra hours/day of meetings "
            "and less time for your core skills. Do you accept?"
        ),
        "expected_reasoning": (
            "Weigh salary against time cost. Does the role align with long-term goals?"
        ),
        "expected_decision": "DEPENDS_ON_CORE_GOAL",
        "defaults": {"salary_bump": "30", "extra_hours": "2"},
    },
    "relationships": {
        "id": "generated_relationships",
        "domain": "relationships",
        "scenario": (
            "A long-term friend has been borrowing money with increasing "
            "frequency and amounts — now 10x the original size. They always "
            "repay. The trend is accelerating. Do you continue lending?"
        ),
        "expected_reasoning": (
            "Look at rate of change, not just level. Consider information "
            "asymmetry and boundary-setting principles."
        ),
        "expected_decision": "SET_BOUNDARY",
        "defaults": {},
    },
    "identity": {
        "id": "generated_identity",
        "domain": "identity",
        "scenario": (
            "If you were incapacitated tomorrow, what is the first concrete "
            "decision your digital twin should make? Name the action, the "
            "person involved, and the timeframe."
        ),
        "expected_reasoning": (
            "Tests whether DNA captures enough operational detail for a "
            "concrete first-person action."
        ),
        "expected_decision": "SPECIFIC_ACTION",
        "defaults": {},
    },
    "risk": {
        "id": "generated_risk",
        "domain": "risk_assessment",
        "scenario": (
            "A backtested strategy shows excellent in-sample performance, "
            "but walk-forward validation only passes {pass_rate} out of "
            "{total_windows} windows. Should you deploy with real capital?"
        ),
        "expected_reasoning": (
            "Walk-forward overrides in-sample. Low pass rate suggests "
            "overfitting rather than genuine edge."
        ),
        "expected_decision": "REJECT",
        "defaults": {"pass_rate": "2", "total_windows": "5"},
    },
    "opportunity_cost": {
        "id": "generated_opportunity_cost",
        "domain": "opportunity_cost",
        "scenario": (
            "You are invited to join a startup as co-founder with {equity}% "
            "equity, requiring {years} years of full-time commitment. Your "
            "current path reaches your primary goal in {goal_years} years. "
            "Do you take it?"
        ),
        "expected_reasoning": (
            "Compare EV of both paths. Evaluate whether you have genuine "
            "edge in assessing the startup's probability of success."
        ),
        "expected_decision": "REQUIRE_CLEAR_EDGE",
        "defaults": {"equity": "10", "years": "2", "goal_years": "3"},
    },
    "meta_strategy": {
        "id": "generated_meta_strategy",
        "domain": "meta_strategy",
        "scenario": (
            "Your primary system has seen its key metric deteriorate {factor}x "
            "over three months. The trend is accelerating. Do you pause it, "
            "tinker with it, or keep running?"
        ),
        "expected_reasoning": (
            "A large deterioration is a regime-change signal. Apply "
            "predefined failure conditions and meta-level management."
        ),
        "expected_decision": "PAUSE_AND_DIAGNOSE",
        "defaults": {"factor": "3"},
    },
}


def _extract_domains_from_dna(dna: dict) -> list[str]:
    """Heuristically detect which life domains a DNA file covers.

    Scans section headers and principle text for domain keywords.
    Returns a list of matched domain keys from _DOMAIN_TEMPLATES.
    """
    # Build a single searchable blob from the DNA.
    # principles and sections are lists of strings (from parse_dna).
    blob_parts = []
    for p in dna.get("principles", []):
        if isinstance(p, str):
            blob_parts.append(p)
        elif isinstance(p, dict):
            blob_parts.append(p.get("name", ""))
            blob_parts.append(p.get("text", ""))
    for s in dna.get("sections", []):
        if isinstance(s, str):
            blob_parts.append(s)
        elif isinstance(s, dict):
            blob_parts.append(s.get("title", ""))
            blob_parts.append(s.get("content", ""))
    # Also include identity fields if present
    for key, val in dna.get("identity", {}).items():
        if isinstance(val, str):
            blob_parts.append(val)
    blob = " ".join(blob_parts).lower()

    domain_keywords = {
        "trading": ["trading", "trade", "backtest", "sharpe", "drawdown", "mdd", "strategy"],
        "finance": ["finance", "invest", "money", "portfolio", "net worth", "fire", "income", "wealth"],
        "career": ["career", "job", "employer", "promotion", "salary", "work", "occupation"],
        "relationships": ["relationship", "friend", "partner", "family", "trust", "social"],
        "identity": ["identity", "who i am", "values", "personality", "core goal", "philosophy"],
        "risk": ["risk", "probability", "expected value", "ev ", "edge", "bet", "sizing"],
        "opportunity_cost": ["opportunity cost", "tradeoff", "trade-off", "time allocation", "priorit"],
        "meta_strategy": ["meta", "strategy", "system", "framework", "decision", "principle"],
    }

    found = []
    for domain, keywords in domain_keywords.items():
        if any(kw in blob for kw in keywords):
            found.append(domain)

    # Always include at least identity + meta_strategy — every DNA has these
    for always_domain in ("identity", "meta_strategy"):
        if always_domain not in found:
            found.append(always_domain)

    return found


def generate_scenarios_from_dna(dna_path: str, output_path: str | None = None) -> list:
    """Read a DNA file and produce a customized scenario template.

    Detects which domains the DNA covers, then emits a scenario set
    using _DOMAIN_TEMPLATES for each detected domain.  The output is
    written as JSON and also returned as a list.
    """
    dna = parse_dna(dna_path)
    domains = _extract_domains_from_dna(dna)

    scenarios = []
    for domain in domains:
        template = _DOMAIN_TEMPLATES.get(domain)
        if not template:
            continue
        scenario = {
            "id": template["id"],
            "domain": template["domain"],
            "scenario": template["scenario"].format(**template.get("defaults", {})),
            "expected_reasoning": template["expected_reasoning"],
            "expected_decision": template["expected_decision"],
        }
        scenarios.append(scenario)

    # Wrap in the standard format
    output = {
        "_comment": (
            f"Auto-generated scenarios for DNA: {dna['name']}. "
            f"Detected domains: {', '.join(domains)}. "
            f"Edit expected_decision and expected_reasoning to match your "
            f"DNA's specific principles."
        ),
        "scenarios": scenarios,
    }

    if output_path is None:
        output_path = str(
            Path(dna_path).parent / f"{Path(dna_path).stem}_boot_tests.json"
        )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(scenarios)} scenarios for domains: {', '.join(domains)}")
    print(f"Saved to: {output_path}")
    print(f"  → Edit expected_decision / expected_reasoning to fit your DNA.")
    return scenarios


# ---------------------------------------------------------------------------
# Core test logic
# ---------------------------------------------------------------------------

def run_deterministic_baseline(dna: dict, boot_test_scenarios: list) -> list:
    """Run all scenarios through the deterministic engine."""
    results = []

    # Organism interaction scenarios
    for scenario in SCENARIOS:
        resp = generate_response(dna, scenario)
        results.append({
            "id": f"organism_{scenario['id']}",
            "domain": scenario["domain"],
            "scenario": scenario["scenario"],
            "deterministic_response": resp["response"],
            "principles_used": resp["dna_principles_used"],
            "source": "organism_interact",
        })

    # Boot test / consistency scenarios (loaded from JSON)
    for scenario in boot_test_scenarios:
        mapped = {
            "id": scenario["id"],
            "domain": scenario.get("domain", "general"),
            "scenario": scenario["scenario"],
        }
        resp = generate_response(dna, mapped)
        results.append({
            "id": scenario["id"],
            "domain": scenario.get("domain", "general"),
            "scenario": scenario["scenario"],
            "deterministic_response": resp["response"],
            "principles_used": resp["dna_principles_used"],
            "expected_decision": scenario.get("expected_decision", ""),
            "expected_reasoning": scenario.get("expected_reasoning", ""),
            "source": "boot_test",
        })

    return results


def generate_template(dna: dict, results: list, output_dir: str) -> str:
    """Generate a markdown template for manual LLM testing."""
    template = [
        "# Cross-Instance Consistency Test",
        f"**DNA**: {dna['name']}",
        f"**Generated**: {datetime.now().isoformat()}",
        f"**Scenarios**: {len(results)}",
        "",
        "## Instructions",
        "",
        "1. Start a CLEAN Claude Code session (no prior context)",
        "2. Load ONLY the DNA file: `read <dna_path>`",
        "3. For each scenario below, ask the question and record the answer",
        "4. Compare answers across sessions to measure consistency",
        "",
        "---",
        "",
    ]

    for i, r in enumerate(results, 1):
        baseline_text = r['deterministic_response']
        baseline_display = (baseline_text[:200] + "...") if len(baseline_text) > 200 else baseline_text
        template.extend([
            f"## Scenario {i}: {r['domain'].upper()} ({r['id']})",
            "",
            f"**Question**: {r['scenario']}",
            "",
            f"**Deterministic baseline**: {baseline_display}",
            "",
        ])
        if r.get("expected_decision"):
            template.append(f"**Expected decision**: {r['expected_decision']}")
            template.append("")
        if r.get("expected_reasoning"):
            template.append(f"**Expected reasoning**: {r['expected_reasoning'][:200]}")
            template.append("")
        template.extend([
            "### Session Answers",
            "",
            "| Session | Decision | Key Principles Cited | Match? |",
            "|---------|----------|---------------------|--------|",
            "| S1 | | | |",
            "| S2 | | | |",
            "| S3 | | | |",
            "",
            "---",
            "",
        ])

    filepath = Path(output_dir) / "consistency_template.md"
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text("\n".join(template), encoding="utf-8")
    return str(filepath)


# ---------------------------------------------------------------------------
# Memory integration — corrections & calibration enhance alignment checking
# ---------------------------------------------------------------------------

def load_memory_context(memory_dir: str | None = None) -> dict:
    """Load corrections and calibration entries from memory.

    Returns a dict with:
      - corrections: list of correction entries
      - calibration: list of calibration entries
      - domain_keywords: dict mapping domain -> set of extra alignment keywords
                         extracted from memory entries
      - context_lines: list of human-readable lines summarizing loaded memory
    """
    if memory_dir:
        original_dir = memory_manager.MEMORY_DIR
        memory_manager.MEMORY_DIR = Path(memory_dir)

    corrections = memory_manager.recall("corrections")
    calibration = memory_manager.recall("calibration")

    if memory_dir:
        memory_manager.MEMORY_DIR = original_dir

    # Extract domain-specific keywords from memory entries.
    # Corrections and calibration entries may reference domains and contain
    # words that should count as alignment signals.
    domain_keywords: dict[str, set[str]] = {}
    for entry in corrections + calibration:
        content_lower = entry.get("content", "").lower()
        tags = entry.get("tags", [])
        key_lower = entry.get("key", "").lower()

        # Determine which domain(s) this entry relates to
        related_domains: list[str] = []
        for domain in _DOMAIN_TO_SECTION_KEYWORDS:
            if domain in content_lower or domain in key_lower or domain in tags:
                related_domains.append(domain)
        # Also check tags for domain names
        for tag in tags:
            tag_l = tag.lower().replace("-", "_")
            if tag_l in _DOMAIN_TO_SECTION_KEYWORDS:
                if tag_l not in related_domains:
                    related_domains.append(tag_l)

        if not related_domains:
            # Entry applies broadly — skip domain-specific keyword extraction
            continue

        # Extract meaningful words from the entry content as alignment keywords.
        # Words that appear in corrections like "always check kill conditions"
        # become extra signals for alignment in that domain.
        words = set(re.findall(r"[a-z]{4,}", content_lower))
        # Filter out very common words that add noise
        noise = {
            "that", "this", "with", "from", "have", "been", "were", "will",
            "when", "what", "which", "their", "about", "would", "could",
            "should", "there", "where", "than", "then", "also", "into",
            "more", "some", "each", "only", "very", "just", "over", "such",
            "after", "before", "between", "does", "being", "made", "like",
        }
        keywords = words - noise

        for domain in related_domains:
            if domain not in domain_keywords:
                domain_keywords[domain] = set()
            domain_keywords[domain].update(keywords)

    # Build human-readable summary
    context_lines = []
    if corrections:
        context_lines.append(f"Loaded {len(corrections)} correction(s) from memory")
        for c in corrections:
            context_lines.append(f"  - [{c.get('key', '?')}] {c['content'][:120]}")
    if calibration:
        context_lines.append(f"Loaded {len(calibration)} calibration entry/entries from memory")
        for c in calibration:
            context_lines.append(f"  - [{c.get('key', '?')}] {c['content'][:120]}")
    if domain_keywords:
        context_lines.append(f"Extracted alignment keywords for {len(domain_keywords)} domain(s)")

    return {
        "corrections": corrections,
        "calibration": calibration,
        "domain_keywords": domain_keywords,
        "context_lines": context_lines,
    }


def check_alignment_with_memory(
    resp_lower: str,
    expected: str,
    domain: str,
    memory_ctx: dict | None,
) -> bool:
    """Check alignment between response and expected decision, enhanced by memory.

    The base alignment logic mirrors the original hardcoded checks. When memory
    context is provided, extra keywords extracted from past corrections and
    calibration entries for the scenario's domain are also checked — any match
    counts as aligned.
    """
    # --- Base alignment (original logic) ---
    aligned = (
        expected in resp_lower
        or (expected == "stop_or_cap" and ("stop" in resp_lower or "cap" in resp_lower))
        or (expected == "pause_system" and ("pause" in resp_lower or "halt" in resp_lower))
        or (expected == "pause_and_diagnose" and ("pause" in resp_lower or "diagnose" in resp_lower))
        or (expected == "pass_unless_clear_edge" and "pass" in resp_lower)
        or (expected == "require_clear_edge" and ("pass" in resp_lower or "edge" in resp_lower))
        or (expected == "set_boundary" and ("stop" in resp_lower or "cap" in resp_lower or "boundary" in resp_lower or "limit" in resp_lower))
        or (expected == "reject" and ("reject" in resp_lower or "no" in resp_lower or "don't" in resp_lower))
        or (expected == "reject_weak_evidence" and ("reject" in resp_lower or "no" in resp_lower))
    )

    if aligned:
        return True

    # --- Memory-enhanced alignment ---
    if memory_ctx is None:
        return False

    domain_kw = memory_ctx.get("domain_keywords", {})
    extra_keywords = domain_kw.get(domain, set())
    if not extra_keywords:
        return False

    # Check if the response contains keywords that memory says matter for
    # this domain AND that are part of the expected decision concept.
    # This prevents false positives: we require the keyword to appear in
    # both the expected decision text AND the response.
    expected_words = set(re.findall(r"[a-z]{4,}", expected))
    relevant_memory_kw = extra_keywords & expected_words
    if relevant_memory_kw:
        # At least one memory-informed keyword from the expected decision
        # appears in the response
        if any(kw in resp_lower for kw in relevant_memory_kw):
            return True

    # Also check: did any correction explicitly mention what the expected
    # outcome should be for this kind of scenario? Look for the expected
    # decision string in correction content.
    for entry in memory_ctx.get("corrections", []):
        entry_content = entry.get("content", "").lower()
        entry_domain_match = domain in entry_content or domain in entry.get("tags", [])
        if entry_domain_match and expected in entry_content:
            # A correction explicitly says this domain should yield this decision;
            # accept if the response at least partially echoes the correction.
            correction_keywords = set(re.findall(r"[a-z]{4,}", entry_content))
            correction_keywords -= {"that", "this", "with", "from", "should", "always"}
            if any(kw in resp_lower for kw in correction_keywords if len(kw) > 4):
                return True

    return False


def store_misaligned_as_calibration(
    misaligned_results: list[dict],
    dna_name: str,
    memory_dir: str | None = None,
) -> list[dict]:
    """Store MISALIGNED results as calibration entries so the next boot benefits.

    Each misaligned scenario becomes a calibration entry with:
      - key: "boot-misalign-<scenario_id>"
      - content: description of what was expected vs. what was produced
      - tags: domain, boot-test, misaligned
      - confidence: 0.7 (moderate — these are machine-detected misalignments)

    Deduplicates by key: if an entry with the same key already exists, it is
    skipped (the misalignment was already recorded).

    Returns a list of newly stored entries.
    """
    if memory_dir:
        original_dir = memory_manager.MEMORY_DIR
        memory_manager.MEMORY_DIR = Path(memory_dir)

    stored = []
    for r in misaligned_results:
        scenario_id = r.get("id", "unknown")
        key = f"boot-misalign-{scenario_id}"

        # Check for existing entry with this key to avoid duplicates
        existing = memory_manager.recall("calibration", key)
        if existing:
            continue

        domain = r.get("domain", "general")
        expected = r.get("expected_decision", "?")
        actual_snippet = r.get("deterministic_response", "")[:200]

        content = (
            f"Scenario '{scenario_id}' (domain: {domain}) was MISALIGNED. "
            f"Expected decision: {expected}. "
            f"Actual response snippet: {actual_snippet}"
        )

        entry = memory_manager.store(
            category="calibration",
            key=key,
            content=content,
            source="consistency-test",
            tags=[domain, "boot-test", "misaligned", scenario_id],
            confidence=0.7,
        )
        stored.append(entry)

    if memory_dir:
        memory_manager.MEMORY_DIR = original_dir

    return stored


def main():
    parser = argparse.ArgumentParser(
        description="Cross-Instance Consistency Test for Digital Organisms"
    )
    parser.add_argument("dna_file", help="Path to DNA markdown file")
    parser.add_argument(
        "--scenarios",
        default=None,
        help=(
            "Path to a JSON file with boot-test scenarios. "
            "Defaults to templates/generic_boot_tests.json"
        ),
    )
    parser.add_argument(
        "--boot-tests",
        default=None,
        help="(Deprecated) Alias for --scenarios, kept for backward compatibility",
    )
    parser.add_argument("--output-dir", default=None, help="Output directory")
    parser.add_argument(
        "--generate-scenarios",
        action="store_true",
        help=(
            "Instead of running tests, read the DNA file and generate a "
            "customized scenario template based on the domains found in the DNA. "
            "Output is saved next to the DNA file as <dna_stem>_boot_tests.json."
        ),
    )
    parser.add_argument(
        "--auto-suggest",
        action="store_true",
        help=(
            "When a scenario is MISALIGNED, print a suggested DNA edit that "
            "identifies the relevant section, recommends a principle to "
            "add or modify, and outputs the suggestion as structured JSON."
        ),
    )
    parser.add_argument(
        "--use-memory",
        action="store_true",
        help=(
            "Integrate the memory system: load past corrections and calibration "
            "data to enhance alignment checking, and store any MISALIGNED results "
            "as calibration entries for future boot tests."
        ),
    )
    parser.add_argument(
        "--memory-dir",
        default=None,
        help=(
            "Path to the memory directory. Defaults to memory/ in the project root."
        ),
    )
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    output_dir = args.output_dir or str(script_dir / "results")

    # --generate-scenarios mode: produce a scenario file and exit
    if args.generate_scenarios:
        out_path = str(Path(output_dir) / f"{Path(args.dna_file).stem}_boot_tests.json")
        generate_scenarios_from_dna(args.dna_file, output_path=out_path)
        return

    # Determine which scenario file to load
    scenarios_path = args.scenarios or args.boot_tests or None
    boot_test_scenarios = load_scenarios(scenarios_path)

    print(f"Loading DNA: {args.dna_file}")
    dna = parse_dna(args.dna_file)
    print(f"  → {dna['name']} | {len(dna['principles'])} principles")

    scenario_source = scenarios_path or str(_DEFAULT_SCENARIOS_PATH)
    print(f"Loading scenarios: {scenario_source}")
    print(f"  → {len(boot_test_scenarios)} boot-test scenarios")

    total = len(SCENARIOS) + len(boot_test_scenarios)
    print(f"\nRunning {total} scenarios...")
    results = run_deterministic_baseline(dna, boot_test_scenarios)

    # --- Memory integration: load past corrections & calibration ---
    memory_ctx = None
    if args.use_memory:
        memory_dir = args.memory_dir or str(_SCRIPT_DIR / "memory")
        memory_ctx = load_memory_context(memory_dir)
        if memory_ctx["context_lines"]:
            print(f"\n{'='*60}")
            print("  MEMORY CONTEXT")
            print(f"{'='*60}")
            for line in memory_ctx["context_lines"]:
                print(f"  {line}")

    # Count alignment with expected decisions
    boot_results = [r for r in results if r.get("expected_decision")]
    misaligned_results = []
    suggestions = []
    if boot_results:
        print(f"\n{'='*60}")
        print("  EXPECTED DECISION ALIGNMENT")
        if args.use_memory and memory_ctx:
            print("  (memory-enhanced)")
        print(f"{'='*60}")
        for r in boot_results:
            resp_lower = r["deterministic_response"].lower()
            expected = r["expected_decision"].lower()
            domain = r.get("domain", "general")
            # Use memory-enhanced alignment when --use-memory is active
            aligned = check_alignment_with_memory(
                resp_lower, expected, domain, memory_ctx
            )
            status = "ALIGNED" if aligned else "MISALIGNED"
            print(f"  [{status:10s}] {r['id']:25s} | expected={r['expected_decision']:30s}")

            if not aligned:
                misaligned_results.append(r)
                if args.auto_suggest:
                    suggestions.append(generate_suggestion(dna, r))

    # Print auto-suggest output for misaligned scenarios
    if suggestions:
        print(f"\n{'='*60}")
        print("  AUTO-SUGGEST: DNA EDITS FOR MISALIGNED SCENARIOS")
        print(f"{'='*60}")
        for s in suggestions:
            print(f"\n  --- {s['scenario_id']} ({s['domain']}) ---")
            print(f"  Section:    {s['relevant_section']}")
            print(f"  Action:     {s['suggestion_type'].upper()}")
            print(f"  Edit:       {s['suggested_edit']}")
            print(f"  Draft:      {s['suggested_principle']}")
            if s['existing_principles']:
                print(f"  Related principles already in DNA:")
                for p in s['existing_principles']:
                    print(f"    - {p[:100]}")

        # Save suggestions as JSON
        suggestions_path = Path(output_dir) / "auto_suggestions.json"
        suggestions_path.parent.mkdir(parents=True, exist_ok=True)
        with open(suggestions_path, "w", encoding="utf-8") as f:
            json.dump({
                "meta": {
                    "dna_file": dna["filepath"],
                    "organism": dna["name"],
                    "generated_at": datetime.now().isoformat(),
                    "misaligned_count": len(suggestions),
                },
                "suggestions": suggestions,
            }, f, ensure_ascii=False, indent=2)
        print(f"\nSuggestions saved: {suggestions_path}")
    elif args.auto_suggest and boot_results:
        print(f"\n  All scenarios aligned — no suggestions needed.")

    # --- Memory integration: store misaligned results as calibration entries ---
    if args.use_memory and misaligned_results:
        memory_dir = args.memory_dir or str(_SCRIPT_DIR / "memory")
        stored = store_misaligned_as_calibration(
            misaligned_results, dna["name"], memory_dir=memory_dir
        )
        if stored:
            print(f"\n{'='*60}")
            print("  MEMORY: STORED CALIBRATION ENTRIES")
            print(f"{'='*60}")
            print(f"  Stored {len(stored)} new calibration entry/entries for future boots:")
            for entry in stored:
                print(f"    - [{entry['key']}] {entry['content'][:100]}")
        else:
            print(f"\n  Memory: all {len(misaligned_results)} misalignment(s) already recorded.")
    elif args.use_memory and boot_results and not misaligned_results:
        print(f"\n  Memory: all scenarios aligned — no calibration entries to store.")

    # Save baseline
    baseline_path = Path(output_dir) / "consistency_baseline.json"
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_meta = {
        "dna_file": dna["filepath"],
        "organism": dna["name"],
        "generated_at": datetime.now().isoformat(),
        "scenario_count": len(results),
        "scenario_source": scenario_source,
        "principles_count": len(dna["principles"]),
        "use_memory": args.use_memory,
    }
    if args.use_memory and memory_ctx:
        baseline_meta["memory_corrections_loaded"] = len(memory_ctx.get("corrections", []))
        baseline_meta["memory_calibration_loaded"] = len(memory_ctx.get("calibration", []))
        baseline_meta["memory_domains_enhanced"] = list(memory_ctx.get("domain_keywords", {}).keys())
    with open(baseline_path, "w", encoding="utf-8") as f:
        json.dump({
            "meta": baseline_meta,
            "results": results,
        }, f, ensure_ascii=False, indent=2)
    print(f"\nBaseline saved: {baseline_path}")

    # Generate template
    template_path = generate_template(dna, results, output_dir)
    print(f"Template saved: {template_path}")


if __name__ == "__main__":
    main()
