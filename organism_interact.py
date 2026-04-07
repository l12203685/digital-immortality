#!/usr/bin/env python3
"""
Digital Organism Interaction — MVP
===================================

Compares two digital organisms (DNA markdown files) across 10 decision scenarios.
Extracts principles from each DNA file, generates structured decision comparisons,
and saves results as JSON in the results/ directory.

Usage:
    python organism_interact.py <dna_file_a> <dna_file_b> [--scenario N] [--all]

Examples:
    python organism_interact.py templates/example_dna.md path/to/other_dna.md --all
    python organism_interact.py dna_a.md dna_b.md --scenario 3
    python organism_interact.py dna_a.md dna_b.md           # runs all 10

Output:
    results/<organism_a>_vs_<organism_b>_<timestamp>.json

Protocol format follows specs/organism_protocol.md v0.1
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Scenario bank — 10 decision-comparison scenarios across key life domains
# ---------------------------------------------------------------------------

SCENARIOS = [
    {
        "id": 1,
        "domain": "career",
        "scenario": (
            "You are offered a role that pays 1.8x your current salary at a "
            "fast-growing startup. The role requires leaving a stable, reputable "
            "employer. The startup has 18 months of runway. Do you take it?"
        ),
    },
    {
        "id": 2,
        "domain": "relationships",
        "scenario": (
            "A close friend asks you to co-sign a personal loan of significant size. "
            "They have a track record of poor financial discipline but are genuinely "
            "in need. Do you co-sign?"
        ),
    },
    {
        "id": 3,
        "domain": "money",
        "scenario": (
            "You receive an unexpected windfall equal to 2 years of your salary. "
            "You can: (A) invest it conservatively in index funds, "
            "(B) allocate it to a concentrated high-conviction bet, "
            "or (C) use it to buy more time — reduce working hours or take a sabbatical. "
            "What do you do and why?"
        ),
    },
    {
        "id": 4,
        "domain": "risk",
        "scenario": (
            "An opportunity with a 30% chance of 10x return and 70% chance of total "
            "loss presents itself. The stake is 20% of your net worth. "
            "Do you take the bet?"
        ),
    },
    {
        "id": 5,
        "domain": "learning",
        "scenario": (
            "You can spend the next 6 months learning a skill that is highly valuable "
            "NOW but may be automated in 3-5 years, OR learning a harder foundational "
            "skill that compounds over a decade but pays nothing immediately. "
            "Which do you choose?"
        ),
    },
    {
        "id": 6,
        "domain": "health",
        "scenario": (
            "Optimizing your physical health would require 10 hours per week of "
            "dedicated effort (sleep discipline, exercise, diet). "
            "This directly competes with time you currently use for deep work and income generation. "
            "How do you allocate?"
        ),
    },
    {
        "id": 7,
        "domain": "time",
        "scenario": (
            "You have a free, unscheduled weekend with zero obligations. "
            "No one expects anything from you. "
            "What do you do, and what does that reveal about your actual priorities?"
        ),
    },
    {
        "id": 8,
        "domain": "conflict",
        "scenario": (
            "A colleague takes credit for your work in front of senior leadership. "
            "It was likely deliberate. You have evidence. "
            "Do you confront them directly, escalate to management, let it go, "
            "or play a longer game? Walk through your reasoning."
        ),
    },
    {
        "id": 9,
        "domain": "opportunity",
        "scenario": (
            "A contact offers you early access to a deal/opportunity that requires "
            "a decision within 48 hours. Due diligence would normally take 2 weeks. "
            "The opportunity looks strong but you cannot fully verify it in time. "
            "Do you act or pass?"
        ),
    },
    {
        "id": 10,
        "domain": "legacy",
        "scenario": (
            "You have 10 years left to work at full capacity. "
            "You can optimize for: (A) maximum wealth accumulation, "
            "(B) building something that outlasts you, "
            "(C) depth of relationships and personal experiences. "
            "These are mutually exclusive at the margin. What is your allocation and why?"
        ),
    },
]


# ---------------------------------------------------------------------------
# DNA parsing
# ---------------------------------------------------------------------------

def parse_dna(filepath: str) -> dict:
    """
    Extract organism name and key principles from a markdown DNA file.

    Parsing strategy:
    - Name: first H1 heading or filename stem
    - Principles: all bullet/numbered list items under headers containing
      keywords: principle, core, value, decision, framework, rule, belief
    - Section headers collected for context
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"DNA file not found: {filepath}")

    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    name = _extract_name(lines, path.stem)
    sections = _extract_sections(lines)
    principles = _extract_principles(lines, sections)
    identity = _extract_identity_table(text)

    return {
        "name": name,
        "filepath": str(path.resolve()),
        "principles": principles,
        "sections": list(sections.keys()),
        "identity": identity,
        "raw_line_count": len(lines),
    }


def _extract_name(lines: list, fallback: str) -> str:
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# ") and len(stripped) > 2:
            candidate = stripped[2:].strip()
            # Strip common suffixes like "DNA", "v18", "Blueprint"
            candidate = re.sub(r"\s+(DNA|Blueprint|v\d+[\.\d]*).*$", "", candidate, flags=re.IGNORECASE)
            if candidate:
                return candidate
    return fallback


def _extract_sections(lines: list) -> dict:
    """Return ordered dict of {section_heading: [line_indices]}"""
    sections = {}
    current = None
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,4})\s+(.+)", line)
        if m:
            current = m.group(2).strip()
            sections[current] = []
        elif current is not None:
            sections[current].append(i)
    return sections


PRINCIPLE_SECTION_KEYWORDS = re.compile(
    r"(principle|core|value|decision|framework|rule|belief|philosophy|kernel|"
    r"manifesto|constitution|law|axiom|heuristic|guideline|基本|原則|核心|價值|決策)",
    re.IGNORECASE,
)


def _extract_principles(lines: list, sections: dict) -> list:
    """
    Collect bullet and numbered list items from principle-relevant sections.
    Also collects any bold (**text**) standalone lines as principles.
    Deduplicated, stripped, max 30 items.
    """
    relevant_line_indices = set()

    for heading, indices in sections.items():
        if PRINCIPLE_SECTION_KEYWORDS.search(heading):
            relevant_line_indices.update(indices)

    # If nothing matched, fall back to ALL lines
    if not relevant_line_indices:
        relevant_line_indices = set(range(len(lines)))

    principles = []
    seen = set()

    for i in sorted(relevant_line_indices):
        line = lines[i].strip()
        extracted = _line_to_principle(line)
        if extracted and extracted not in seen:
            seen.add(extracted)
            principles.append(extracted)
        if len(principles) >= 30:
            break

    return principles


BULLET_RE = re.compile(r"^[-*+•]\s+(.+)")
NUMBERED_RE = re.compile(r"^\d+[\.\)]\s+(.+)")
BOLD_LINE_RE = re.compile(r"^\*\*(.+?)\*\*\s*[—–-]?\s*(.*)")


def _line_to_principle(line: str) -> str | None:
    for pattern in (BULLET_RE, NUMBERED_RE):
        m = pattern.match(line)
        if m:
            content = m.group(1).strip()
            # Strip inline markdown bold/italic
            content = re.sub(r"\*\*(.+?)\*\*", r"\1", content)
            content = re.sub(r"\*(.+?)\*", r"\1", content)
            if len(content) > 10:
                return content
    # Bold standalone principle lines
    m = BOLD_LINE_RE.match(line)
    if m:
        label = m.group(1).strip()
        detail = m.group(2).strip()
        combined = f"{label} — {detail}" if detail else label
        if len(combined) > 10:
            return combined
    return None


def _extract_identity_table(text: str) -> dict:
    """Parse markdown table rows from Identity section into a flat dict."""
    identity = {}
    in_identity = False
    for line in text.splitlines():
        if re.match(r"^#{1,3}\s+.*[Ii]dentity", line):
            in_identity = True
            continue
        if in_identity:
            if line.startswith("#"):
                break
            m = re.match(r"\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", line)
            if m:
                key = m.group(1).strip().lower()
                val = m.group(2).strip()
                if key not in ("field", "---", "item") and val not in ("value", "detail", "---"):
                    identity[key] = val
    return identity


# ---------------------------------------------------------------------------
# Decision generation (heuristic, no LLM)
# ---------------------------------------------------------------------------

DOMAIN_PRINCIPLE_AFFINITY = {
    "career":        ["career", "job", "work", "growth", "stability", "salary", "opportunity", "compound"],
    "relationships": ["relationship", "trust", "friend", "social", "obligation", "commitment", "人際", "信任"],
    "money":         ["money", "invest", "wealth", "asset", "return", "capital", "financial", "資產", "財務"],
    "risk":          ["risk", "edge", "EV", "expected value", "bet", "probability", "loss", "upside"],
    "learning":      ["learn", "skill", "knowledge", "compound", "foundation", "growth", "study"],
    "health":        ["health", "energy", "sleep", "exercise", "body", "physical", "time"],
    "time":          ["time", "priorit", "allocat", "focus", "freedom", "leisure", "schedule"],
    "conflict":      ["conflict", "confrontation", "direct", "escalat", "politics", "boundary"],
    "opportunity":   ["opportunit", "decision", "act", "pass", "verify", "rush", "FOMO", "edge"],
    "legacy":        ["legacy", "impact", "build", "lasting", "meaning", "wealth", "relationship"],
}


def _score_principle_for_domain(principle: str, domain: str) -> int:
    keywords = DOMAIN_PRINCIPLE_AFFINITY.get(domain, [])
    p_lower = principle.lower()
    return sum(1 for kw in keywords if kw.lower() in p_lower)


def generate_response(organism: dict, scenario: dict) -> dict:
    """
    Heuristic decision engine:
    1. Score all principles against the scenario domain
    2. Pick top 3 relevant principles (fall back to first 3 if none score)
    3. Build a templated response that cites those principles
    """
    principles = organism["principles"]
    domain = scenario["domain"]

    if not principles:
        used = []
        response = (
            f"No extractable principles found in DNA. "
            f"Cannot generate a decision for the '{domain}' scenario."
        )
        return {"response": response, "dna_principles_used": used}

    scored = sorted(
        enumerate(principles),
        key=lambda x: _score_principle_for_domain(x[1], domain),
        reverse=True,
    )

    # Top 3 relevant; if top score is 0, just take first 3
    top = scored[:3]
    if top[0][1] == 0:  # all scored 0, use first 3 positionally
        top = list(enumerate(principles[:3]))

    used = [principles[i] for i, _ in top]

    response = _build_response(organism["name"], scenario, used)
    return {"response": response, "dna_principles_used": used}


def _build_response(name: str, scenario: dict, principles: list) -> str:
    """
    Construct a plausible decision response by surface-reading the scenario
    and applying the organism's principles as explicit reasoning steps.
    """
    domain = scenario["domain"]

    framing = {
        "career":        "On career decisions",
        "relationships": "On relationship commitments",
        "money":         "On capital allocation",
        "risk":          "On risk-taking",
        "learning":      "On learning investments",
        "health":        "On health vs. productivity trade-offs",
        "time":          "On time allocation",
        "conflict":      "On conflict resolution",
        "opportunity":   "On time-compressed opportunities",
        "legacy":        "On legacy and long-term orientation",
    }.get(domain, f"On {domain}")

    lines = [f"{framing}, {name}'s decision framework yields:"]
    lines.append("")

    for i, p in enumerate(principles, 1):
        # Truncate very long principles for readability
        p_display = p if len(p) <= 120 else p[:117] + "..."
        lines.append(f"  [{i}] Applying: \"{p_display}\"")

    lines.append("")

    # Domain-specific decision logic stubs — each uses principle text as signal
    all_text = " ".join(principles).lower()
    decision_text = _domain_decision(domain, all_text)
    lines.append(decision_text)

    return "\n".join(lines)


def _domain_decision(domain: str, principle_text: str) -> str:
    """Map domain + principle signals to a concrete decision stance."""
    stability_signal = any(w in principle_text for w in ["stable", "stability", "hedge", "safe", "conservative"])
    growth_signal    = any(w in principle_text for w in ["growth", "compound", "upside", "opportunit", "aggressive"])
    ev_signal        = any(w in principle_text for w in ["ev", "expected value", "probability", "edge"])
    inaction_signal  = any(w in principle_text for w in ["inaction", "wait", "patience", "no edge", "pass"])
    direct_signal    = any(w in principle_text for w in ["direct", "confront", "honest", "transparent"])
    system_signal    = any(w in principle_text for w in ["system", "process", "framework", "structure"])
    meta_signal      = any(w in principle_text for w in ["meta", "long-term", "second order", "derivative"])

    decisions = {
        "career": (
            "PASS — stability hedge outweighs marginal income gain without verifiable runway extension."
            if stability_signal else
            "TAKE — growth optionality at 1.8x is underpriced; downside is recoverable, upside compounds."
            if growth_signal else
            "CONDITIONAL — evaluate EV of runway extension probability before deciding."
        ),
        "relationships": (
            "DECLINE — co-signing transfers financial risk without proportional relationship upside; offer alternatives."
            if (stability_signal or inaction_signal) else
            "STRUCTURED YES — co-sign with documented repayment schedule and explicit exit conditions."
        ),
        "money": (
            "CONCENTRATED BET — windfall capital is highest-risk-tolerance tranche; deploy in high-conviction position."
            if (growth_signal or ev_signal) else
            "INDEX + OPTIONALITY — 70% conservative base, 30% time-buying (sabbatical or skill-building)."
            if stability_signal else
            "FRAMEWORK FIRST — run expected-value calc across all three options before allocating."
        ),
        "risk": (
            "TAKE — EV = +0.3*9x + 0.7*(-1x) = +2.0; positive EV at 20% position size is within Kelly range."
            if ev_signal else
            "PASS — 70% ruin probability on 20% net worth violates position-sizing discipline regardless of upside."
            if (stability_signal or inaction_signal) else
            "SIZE DOWN — reduce stake to Kelly-optimal fraction, then take the bet."
        ),
        "learning": (
            "FOUNDATION — short-term skills are depreciating assets; foundational skills are the meta-investment."
            if (meta_signal or growth_signal) else
            "IMMEDIATE VALUE — capture the arbitrage window now; foundational learning can be parallelized."
            if stability_signal else
            "PARALLEL — 70% foundational, 30% immediate; avoid binary framing."
        ),
        "health": (
            "SYSTEM BUILD — health is infrastructure, not discretionary; 10h/week is non-negotiable baseline."
            if system_signal else
            "OPTIMIZE OVERLAP — combine health and productive time (walking calls, standing desk, sleep priority)."
        ),
        "time": (
            "META-WORK — free time defaults to system review, reading, and strategic thinking; leisure is residual."
            if (meta_signal or system_signal) else
            "RECHARGE — genuine disconnection to restore cognitive baseline; productivity follows recovery."
            if stability_signal else
            "OPTIONALITY — protect free time as unstructured; resist filling it with output-optimizing activities."
        ),
        "conflict": (
            "DIRECT CONFRONTATION — address the behavior privately, factually, with evidence; no escalation first."
            if direct_signal else
            "DOCUMENTED ESCALATION — create paper trail, escalate through proper channels; avoid personal confrontation."
            if system_signal else
            "LONG GAME — let the pattern establish itself; address systemically when the second instance occurs."
        ),
        "opportunity": (
            "PASS — 48h diligence is insufficient; forced urgency is a red flag that shifts EV negative."
            if (inaction_signal or ev_signal) else
            "SMALL POSITION — take minimum viable exposure to maintain optionality without full commitment."
            if growth_signal else
            "FRAMEWORK CHECK — assess whether incomplete diligence is the actual risk, or whether intuition is sufficient."
        ),
        "legacy": (
            "WEALTH FIRST — financial independence is infrastructure for everything else; sequence matters."
            if stability_signal else
            "BUILD SOMETHING — asymmetric legacy impact outweighs marginal wealth beyond sufficiency threshold."
            if (growth_signal or meta_signal) else
            "INTEGRATED — compound wealth to sufficiency, then redirect to building; relationships are the through-line."
        ),
    }
    return decisions.get(domain, "Decision: apply core principles to the specific trade-offs in this scenario.")


# ---------------------------------------------------------------------------
# Synthesis
# ---------------------------------------------------------------------------

def synthesize(organism_a: dict, organism_b: dict, resp_a: dict, resp_b: dict, scenario: dict) -> str:
    """
    Compare two responses and articulate what the difference reveals
    about each organism's underlying value structure.
    """
    principles_a = set(resp_a["dna_principles_used"])
    principles_b = set(resp_b["dna_principles_used"])

    overlap = principles_a & principles_b
    unique_a = principles_a - principles_b
    unique_b = principles_b - principles_a

    # Response stance: look for divergence signals
    resp_text_a = resp_a["response"].lower()
    resp_text_b = resp_b["response"].lower()

    take_keywords  = ["take", "yes", "proceed", "act", "invest", "confront", "build"]
    pass_keywords  = ["pass", "no", "decline", "wait", "skip", "avoid", "structured"]

    stance_a = "action-oriented" if any(k in resp_text_a for k in take_keywords) else "caution-oriented"
    stance_b = "action-oriented" if any(k in resp_text_b for k in take_keywords) else "caution-oriented"

    parts = []

    if stance_a == stance_b:
        parts.append(
            f"Both organisms converge on a {stance_a} stance for this '{scenario['domain']}' scenario, "
            f"suggesting shared values around {'risk tolerance' if stance_a == 'action-oriented' else 'risk management'}."
        )
    else:
        parts.append(
            f"{organism_a['name']} takes a {stance_a} approach while "
            f"{organism_b['name']} takes a {stance_b} approach. "
            f"The divergence in the '{scenario['domain']}' domain reveals different weightings of "
            f"{'upside vs. downside' if scenario['domain'] in ('risk', 'career', 'opportunity') else 'competing values'}."
        )

    if overlap:
        sample = list(overlap)[:1]
        parts.append(f"Shared foundation: both organisms cite principles around '{sample[0][:60]}...' — alignment here.")

    if unique_a:
        sample = list(unique_a)[:1]
        parts.append(f"{organism_a['name']}'s distinctive signal: '{sample[0][:80]}' — drives their specific stance.")

    if unique_b:
        sample = list(unique_b)[:1]
        parts.append(f"{organism_b['name']}'s distinctive signal: '{sample[0][:80]}' — drives their specific stance.")

    if not parts:
        parts.append(
            f"Insufficient principle differentiation to synthesize meaningfully. "
            f"Both DNA files may need richer principle content."
        )

    return " ".join(parts)


# ---------------------------------------------------------------------------
# Output formatting and file saving
# ---------------------------------------------------------------------------

def build_record(organism_a: dict, organism_b: dict, resp_a: dict, resp_b: dict, scenario: dict) -> dict:
    return {
        "type": "decision_comparison",
        "scenario": scenario["scenario"],
        "domain": scenario["domain"],
        "organism_a": {
            "name": organism_a["name"],
            "response": resp_a["response"],
            "dna_principles_used": resp_a["dna_principles_used"],
        },
        "organism_b": {
            "name": organism_b["name"],
            "response": resp_b["response"],
            "dna_principles_used": resp_b["dna_principles_used"],
        },
        "synthesis": synthesize(organism_a, organism_b, resp_a, resp_b, scenario),
    }


def save_results(records: list, organism_a: dict, organism_b: dict, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)

    name_a = re.sub(r"[^\w]", "_", organism_a["name"])[:20]
    name_b = re.sub(r"[^\w]", "_", organism_b["name"])[:20]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name_a}_vs_{name_b}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)

    payload = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "organism_a_file": organism_a["filepath"],
            "organism_b_file": organism_b["filepath"],
            "scenario_count": len(records),
            "protocol_version": "v0.1",
        },
        "organisms": {
            "a": {
                "name": organism_a["name"],
                "principles_extracted": len(organism_a["principles"]),
                "identity": organism_a["identity"],
            },
            "b": {
                "name": organism_b["name"],
                "principles_extracted": len(organism_b["principles"]),
                "identity": organism_b["identity"],
            },
        },
        "interactions": records,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return filepath


def print_record(record: dict, index: int, total: int) -> None:
    sep = "-" * 72
    print(f"\n{'='*72}")
    print(f"  SCENARIO {index}/{total} — {record['domain'].upper()}")
    print(f"{'='*72}")
    print(f"\nSCENARIO:\n  {record['scenario']}\n")

    for side in ("organism_a", "organism_b"):
        org = record[side]
        print(f"{sep}")
        print(f"  {org['name'].upper()}")
        print(sep)
        print(org["response"])
        if org["dna_principles_used"]:
            print(f"\n  Principles invoked:")
            for p in org["dna_principles_used"]:
                print(f"    • {p[:100]}")
        print()

    print(f"{sep}")
    print(f"  SYNTHESIS")
    print(sep)
    print(f"  {record['synthesis']}\n")


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Digital Organism Interaction — decision comparison across two DNA files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("dna_a", help="Path to DNA file for organism A (markdown)")
    parser.add_argument("dna_b", help="Path to DNA file for organism B (markdown)")
    parser.add_argument(
        "--scenario", type=int, metavar="N",
        help="Run a single scenario by number (1-10). Default: run all.",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Explicitly run all 10 scenarios (default behavior).",
    )
    parser.add_argument(
        "--output-dir", default=None,
        help="Directory to write JSON results. Defaults to results/ next to this script.",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress terminal output; only write JSON file.",
    )
    parser.add_argument(
        "--list-scenarios", action="store_true",
        help="Print the 10 built-in scenarios and exit.",
    )
    args = parser.parse_args()

    if args.list_scenarios:
        for s in SCENARIOS:
            print(f"  [{s['id']:2d}] [{s['domain'].upper():13s}] {s['scenario'][:80]}...")
        sys.exit(0)

    # Resolve output directory relative to this script's location
    script_dir = Path(__file__).parent
    output_dir = args.output_dir or str(script_dir / "results")

    # Load DNA files
    try:
        print(f"Loading DNA A: {args.dna_a}")
        organism_a = parse_dna(args.dna_a)
        print(f"  → {organism_a['name']} | {len(organism_a['principles'])} principles extracted")

        print(f"Loading DNA B: {args.dna_b}")
        organism_b = parse_dna(args.dna_b)
        print(f"  → {organism_b['name']} | {len(organism_b['principles'])} principles extracted")
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Select scenarios
    if args.scenario:
        if args.scenario < 1 or args.scenario > len(SCENARIOS):
            print(f"ERROR: --scenario must be 1-{len(SCENARIOS)}", file=sys.stderr)
            sys.exit(1)
        scenarios_to_run = [SCENARIOS[args.scenario - 1]]
    else:
        scenarios_to_run = SCENARIOS

    print(f"\nRunning {len(scenarios_to_run)} scenario(s)...\n")

    # Run comparisons
    records = []
    for scenario in scenarios_to_run:
        resp_a = generate_response(organism_a, scenario)
        resp_b = generate_response(organism_b, scenario)
        record = build_record(organism_a, organism_b, resp_a, resp_b, scenario)
        records.append(record)
        if not args.quiet:
            print_record(record, scenario["id"], len(SCENARIOS))

    # Save
    output_path = save_results(records, organism_a, organism_b, output_dir)
    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
