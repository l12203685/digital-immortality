#!/usr/bin/env python3
"""
DNA Calibration Engine — Branch 3 (Economic Autonomy)
=====================================================

Takes a completed client intake form (JSON) and generates a
personalized DNA Calibration Report by detecting behavioral
patterns across 20 decision scenarios.

Usage:
    python dna_calibration_engine.py <intake.json> [--output <report.md>]
    python dna_calibration_engine.py --demo   # run sample client

Input format (intake.json):
    {
        "client_name": "...",
        "date": "YYYY-MM-DD",
        "scenarios": [
            {"id": 1, "decision": "...", "reasoning": "...", "confidence": 3},
            ...
        ]
    }
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import NamedTuple


# ---------------------------------------------------------------------------
# Domain definitions
# ---------------------------------------------------------------------------

DOMAINS = {
    "risk": range(1, 6),      # S1–S5
    "career": range(6, 11),   # S6–S10
    "relationships": range(11, 16),  # S11–S15
    "meta": range(16, 21),    # S16–S20
}

DOMAIN_LABELS = {
    "risk": "Risk & Sizing",
    "career": "Career & Time Allocation",
    "relationships": "Relationships & Boundaries",
    "meta": "Meta-Cognition & System Design",
}


# ---------------------------------------------------------------------------
# Pattern detectors — each returns (flag: bool, note: str)
# ---------------------------------------------------------------------------

class PatternResult(NamedTuple):
    detected: bool
    evidence: str  # scenario IDs + brief explanation


def detect_sunk_cost(scenarios: list[dict]) -> PatternResult:
    """Sunk cost or effort-justification override."""
    signals = []
    # S15: softening feedback when effort is visible
    s15 = next((s for s in scenarios if s["id"] == 15), None)
    if s15:
        r = s15["reasoning"].lower()
        d = s15.get("decision", "").lower()
        # Only flag if effort is the *reason* for softening — not if it's mentioned to dismiss it
        effort_present = any(w in r for w in ["tried", "hard work", "put in a lot", "put so much"])
        effort_present = effort_present or ("effort" in r and any(w in r for w in ["soft", "gentle", "kind", "though", "still", "anyway", "but"]))
        softened = any(w in d for w in ["gentle", "soft", "kind", "careful", "gently"]) or any(w in r for w in ["soften", "gentle", "not too harsh", "be kind", "careful how"])
        if effort_present and softened:
            signals.append("S15: feedback softened due to visible effort")
    # S12: delayed addressing — pattern tolerance past 3
    s12 = next((s for s in scenarios if s["id"] == 12), None)
    if s12:
        r = s12["reasoning"].lower()
        if any(w in r for w in ["4th", "fourth", "again", "another time", "repeatedly"]):
            signals.append("S12: waited past pattern threshold to address cancellations")
    return PatternResult(bool(signals), "; ".join(signals) if signals else "not detected")


def detect_urgency_collapse(scenarios: list[dict]) -> PatternResult:
    """Plan abandonment under concurrent pressure."""
    s18 = next((s for s in scenarios if s["id"] == 18), None)
    if not s18:
        return PatternResult(False, "S18 missing")
    decision = s18["decision"].lower()
    reasoning = s18["reasoning"].lower()
    if "abandon" in decision or "abandon" in reasoning:
        return PatternResult(True, "S18: explicit plan abandonment under disruption")
    if ("adapt" in decision or "adapt" in reasoning) and any(
        w in reasoning for w in ["give up", "drop", "cancel", "not possible", "impossible"]
    ):
        return PatternResult(True, "S18: stated 'adapt' but reasoning reveals abandonment")
    return PatternResult(False, "S18: plan protection held")


def detect_retroactive_exit(scenarios: list[dict]) -> PatternResult:
    """Exit conditions defined after entry, not before."""
    signals = []
    for sid in [2, 3]:
        s = next((x for x in scenarios if x["id"] == sid), None)
        if s:
            r = s["reasoning"].lower()
            exit_keywords = ["if it drops", "if thesis", "stop loss", "exit when", "exit if", "cut when", "trailing stop", "stop at", "sell when", "sell if", "close if", "close when"]
        if not any(w in r for w in exit_keywords):
                signals.append(f"S{sid}: no pre-defined exit condition stated")
    return PatternResult(bool(signals), "; ".join(signals) if signals else "exit conditions defined proactively")


def detect_intention_behavior_gap(scenarios: list[dict]) -> PatternResult:
    """Stated intention vs. likely behavior divergence."""
    s9 = next((s for s in scenarios if s["id"] == 9), None)
    s10 = next((s for s in scenarios if s["id"] == 10), None)
    if not (s9 and s10):
        return PatternResult(False, "S9/S10 missing")
    s9_intent = s9["decision"].lower()
    s10_reality = s10["decision"].lower()
    chose_deep_work = any(w in s9_intent for w in ["deep work", "project", "a", "option a"])
    but_didnt = any(w in s10_reality for w in ["check phone", "scroll", "social", "later", "noon", "eventually"])
    if chose_deep_work and but_didnt:
        return PatternResult(True, "S9 chose deep work, S10 reveals avoidance behavior")
    return PatternResult(False, "S9/S10 consistent")


def detect_capitulation(scenarios: list[dict]) -> PatternResult:
    """Social pressure overriding reasoned position."""
    s14 = next((s for s in scenarios if s["id"] == 14), None)
    if not s14:
        return PatternResult(False, "S14 missing")
    r = s14["reasoning"].lower()
    if any(w in r for w in ["come around", "eventually agree", "open to being wrong", "maybe they're right", "give it thought"]):
        return PatternResult(True, "S14: openness framing may mask capitulation under persistence")
    return PatternResult(False, "S14: held position appropriately")


def detect_insight_without_system(scenarios: list[dict]) -> PatternResult:
    """Insight captured but not converted to system change."""
    s16 = next((s for s in scenarios if s["id"] == 16), None)
    if not s16:
        return PatternResult(False, "S16 missing")
    r = s16["reasoning"].lower()
    noted = any(w in r for w in ["write", "note", "document", "record", "journal"])
    built = any(w in r for w in ["rule", "system", "checklist", "process", "workflow", "prevent", "trigger"])
    if noted and not built:
        return PatternResult(True, "S16: documented the insight but no system change described")
    if not noted and not built:
        return PatternResult(True, "S16: insight not captured in durable form")
    return PatternResult(False, "S16: insight converted to system")


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

@dataclass
class DomainScore:
    domain: str
    avg_confidence: float
    scenario_notes: list[str] = field(default_factory=list)


def score_domains(scenarios: list[dict]) -> dict[str, DomainScore]:
    scores = {}
    for domain, id_range in DOMAINS.items():
        domain_scenarios = [s for s in scenarios if s["id"] in id_range]
        if not domain_scenarios:
            continue
        avg_conf = sum(s["confidence"] for s in domain_scenarios) / len(domain_scenarios)
        scores[domain] = DomainScore(domain=domain, avg_confidence=round(avg_conf, 1))
    return scores


def analyze_scenario_quality(scenarios: list[dict]) -> list[str]:
    """Identify scenarios where reasoning is shallow or missing."""
    weak = []
    for s in scenarios:
        reasoning = s.get("reasoning", "").strip()
        if len(reasoning.split()) < 5:
            weak.append(f"S{s['id']}: reasoning too brief to analyze")
        elif s["confidence"] == 5 and any(
            w in reasoning.lower() for w in ["gut", "just feel", "obvious", "always", "never"]
        ):
            weak.append(f"S{s['id']}: high confidence but reasoning relies on intuition without framework")
    return weak


# ---------------------------------------------------------------------------
# Blind spot prioritization
# ---------------------------------------------------------------------------

BLIND_SPOT_DEFINITIONS = {
    "sunk_cost": {
        "name": "Effort-justification override",
        "trigger": "Visible effort from others",
        "repair": "Pre-commit to evaluation criteria before seeing the work",
    },
    "urgency_collapse": {
        "name": "Urgency collapse / plan abandonment",
        "trigger": "3+ concurrent disruptions or deadline pressure",
        "repair": "Define a pre-mortem: 'My plan holds unless X specifically happens'",
    },
    "retroactive_exit": {
        "name": "Exit conditions defined retroactively",
        "trigger": "After entering a position, project, or commitment",
        "repair": "Write exit condition before entry — every time, one sentence",
    },
    "intention_behavior_gap": {
        "name": "Intention-behavior gap on time",
        "trigger": "Low urgency, high-value tasks (no external deadline)",
        "repair": "Pre-commitment devices: block time, environment design, not willpower",
    },
    "capitulation": {
        "name": "Capitulation disguised as open-mindedness",
        "trigger": "Social pressure from someone you respect",
        "repair": "Distinguish: 'argument updated my model' vs 'discomfort made me yield'",
    },
    "insight_without_system": {
        "name": "Insight without system conversion",
        "trigger": "After recognizing a recurring mistake",
        "repair": "Every insight needs a trigger + rule, not just documentation",
    },
}


def rank_blind_spots(pattern_results: dict[str, PatternResult]) -> list[dict]:
    detected = [
        {
            "key": key,
            **BLIND_SPOT_DEFINITIONS[key],
            "evidence": pattern_results[key].evidence,
        }
        for key, result in pattern_results.items()
        if result.detected
    ]
    return detected


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(
    client_name: str,
    date: str,
    scenarios: list[dict],
    pattern_results: dict[str, PatternResult],
    domain_scores: dict[str, DomainScore],
    blind_spots: list[dict],
    weak_scenarios: list[str],
) -> str:
    lines = []

    def ln(text: str = "") -> None:
        lines.append(text)

    ln(f"# DNA Calibration Report — {client_name}")
    ln(f"> Date: {date}  ")
    ln(f"> Analyst: Edward Lin (EV Decision Systems)")
    ln()
    ln("---")
    ln()

    # Executive Summary
    ln("## Executive Summary")
    ln()
    detected_count = sum(1 for r in pattern_results.values() if r.detected)
    total_patterns = len(pattern_results)

    if detected_count == 0:
        ln("Your decision engine is well-calibrated across the tested dimensions. No systematic blind spots detected in this run.")
    elif detected_count <= 2:
        ln(f"Your decision engine shows {detected_count} systematic pattern(s) worth installing a repair for. The rest is solid.")
    else:
        ln(f"Your decision engine has {detected_count} of {total_patterns} tested blind spots active. Priority: install repairs in order below.")

    ln()
    if blind_spots:
        ln(f"**Primary blind spot:** {blind_spots[0]['name']} — active in {blind_spots[0]['evidence']}")
    ln()

    # Domain scores
    ln("---")
    ln()
    ln("## Domain Analysis")
    ln()

    for domain, score in domain_scores.items():
        label = DOMAIN_LABELS[domain]
        conf_label = "Low" if score.avg_confidence < 2.5 else ("Medium" if score.avg_confidence < 3.5 else "High")
        ln(f"### {label}")
        ln()
        ln(f"Average confidence: {score.avg_confidence}/5 ({conf_label})")
        ln()

        # Per-scenario notes
        domain_scenarios = [s for s in scenarios if s["id"] in DOMAINS[domain]]
        for s in domain_scenarios:
            note = _scenario_note(s, pattern_results)
            ln(f"- **S{s['id']}:** {note}")
        ln()

    # Blind spots table
    ln("---")
    ln()
    ln("## Blind Spots Detected")
    ln()
    if not blind_spots:
        ln("None detected in this run.")
    else:
        ln("| # | Blind Spot | Trigger | Repair |")
        ln("|---|-----------|---------|--------|")
        for i, bs in enumerate(blind_spots, 1):
            ln(f"| {i} | {bs['name']} | {bs['trigger']} | {bs['repair']} |")
    ln()

    # Shallow scenarios note
    if weak_scenarios:
        ln("---")
        ln()
        ln("## Analysis Limitations")
        ln()
        ln("The following scenarios had insufficient reasoning depth for full pattern analysis:")
        ln()
        for note in weak_scenarios:
            ln(f"- {note}")
        ln()
        ln("Re-run with fuller reasoning on these for higher-fidelity diagnosis.")
        ln()

    # One installed rule
    ln("---")
    ln()
    ln("## One Rule to Install This Week")
    ln()
    if blind_spots:
        top = blind_spots[0]
        ln(f"**{top['repair']}**")
        ln()
        ln(f"This targets your primary blind spot ({top['name']}) directly.")
        if len(blind_spots) > 1:
            ln(f"It also creates conditions that reduce '{blind_spots[1]['name']}'.")
    else:
        ln("Your calibration is strong. Keep running the system. Schedule a re-check in 90 days.")
    ln()

    # Next steps
    ln("---")
    ln()
    ln("## Next Steps")
    ln()
    ln("- 30-day check-in available (NT$1,500 — 30 min session to review whether installed rule held)")
    ln("- Full DNA system build-out available for teams or high-stakes individual decisions")
    ln()
    ln("---")
    ln()
    ln(f"*Report prepared by Edward Lin | EV Decision Systems*  ")
    ln("*This report is calibrated to your specific responses — not a generic personality assessment.*")

    return "\n".join(lines)


def _scenario_note(scenario: dict, pattern_results: dict[str, PatternResult]) -> str:
    """Generate a 1-line note for a scenario based on its decision + detected patterns."""
    sid = scenario["id"]
    decision = scenario.get("decision", "").strip()
    confidence = scenario.get("confidence", 0)
    conf_str = f"(confidence {confidence}/5)"

    # S2: exit condition check
    if sid == 2:
        if "retroactive_exit" in pattern_results and pattern_results["retroactive_exit"].detected:
            return f"Held position — correct. {conf_str} Missing: pre-defined exit condition. What changes your thesis?"
        return f"Held position — correct. {conf_str} Exit condition stated."

    # S3: anchoring check
    if sid == 3:
        if "retroactive_exit" in pattern_results and pattern_results["retroactive_exit"].detected:
            return f"Took partial/full profit — noted. {conf_str} Risk: 'still has runway' framing = anchoring to recent gain."
        return f"Profit management noted. {conf_str}"

    # S10: intention-behavior gap
    if sid == 10:
        if "intention_behavior_gap" in pattern_results and pattern_results["intention_behavior_gap"].detected:
            return f"Behavioral description reveals drift from stated S9 intent. {conf_str} Intention-behavior gap active."
        return f"Consistent with S9 intent. {conf_str}"

    # S15: effort-justification
    if sid == 15:
        if "sunk_cost" in pattern_results and pattern_results["sunk_cost"].detected:
            return f"Feedback delivery softened. {conf_str} Effort-justification override detected — see Blind Spot #1."
        return f"Feedback delivered directly. {conf_str}"

    # S18: urgency collapse
    if sid == 18:
        if "urgency_collapse" in pattern_results and pattern_results["urgency_collapse"].detected:
            return f"Plan disposition under pressure. {conf_str} Urgency collapse pattern detected — see Blind Spot table."
        return f"Plan protected under disruption. {conf_str} Solid."

    # Default
    short_decision = decision[:60] + "..." if len(decision) > 60 else decision
    return f"{short_decision} {conf_str}"


# ---------------------------------------------------------------------------
# Demo client (no external file needed)
# ---------------------------------------------------------------------------

DEMO_INTAKE = {
    "client_name": "Demo Client",
    "date": datetime.now().strftime("%Y-%m-%d"),
    "scenarios": [
        {"id": 1, "decision": "Put in NT$100,000 (~20%)", "reasoning": "He's been right before but 80% is optimistic. Diversify, don't bet the house.", "confidence": 4},
        {"id": 2, "decision": "Hold", "reasoning": "Thesis unchanged. Market noise.", "confidence": 4},
        {"id": 3, "decision": "Take partial profit (50%)", "reasoning": "Still has runway but it's up 40%. Makes sense to secure some.", "confidence": 3},
        {"id": 4, "decision": "Run 60%/1.5R system", "reasoning": "EV is higher. 0.9 vs 0.46.", "confidence": 5},
        {"id": 5, "decision": "Keep running", "reasoning": "Within risk limits. 5 trades is not statistically significant.", "confidence": 4},
        {"id": 6, "decision": "Take the job", "reasoning": "40% is concrete, social network rebuilds.", "confidence": 4},
        {"id": 7, "decision": "Decline", "reasoning": "Equity could be zero.", "confidence": 3},
        {"id": 8, "decision": "Join", "reasoning": "Interesting domain. Could become something.", "confidence": 2},
        {"id": 9, "decision": "Deep work", "reasoning": "Moves my goals forward.", "confidence": 4},
        {"id": 10, "decision": "Probably check phone, eventually start working around noon", "reasoning": "Realistically that's what happens when I'm exhausted.", "confidence": 3},
        {"id": 11, "decision": "Lend with written agreement", "reasoning": "Protects the relationship by making terms explicit.", "confidence": 4},
        {"id": 12, "decision": "Address it after the 4th time", "reasoning": "By then the pattern is undeniable.", "confidence": 3},
        {"id": 13, "decision": "Speak up diplomatically", "reasoning": "Diplomatic, not confrontational. I might be wrong.", "confidence": 3},
        {"id": 14, "decision": "Disagree respectfully, ask for their reasoning", "reasoning": "I'd probably eventually come around if they keep pushing.", "confidence": 2},
        {"id": 15, "decision": "Give honest feedback gently", "reasoning": "They put in a lot of effort. I'd soften it.", "confidence": 3},
        {"id": 16, "decision": "Write it down", "reasoning": "Document the insight so I remember it.", "confidence": 3},
        {"id": 17, "decision": "Strategy A", "reasoning": "Higher EV. Consistent effort over 12 months.", "confidence": 4},
        {"id": 18, "decision": "Adapt the plan", "reasoning": "Urgent tasks come up. I'd give up on some lower-priority goals.", "confidence": 3},
        {"id": 19, "decision": "Keep doing it", "reasoning": "Don't fix what isn't broken.", "confidence": 3},
        {"id": 20, "decision": "List knowns, find the one unknown that matters most, take the most information-providing action", "reasoning": "Structure reduces the paralysis.", "confidence": 4},
    ],
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(intake: dict) -> str:
    client_name = intake.get("client_name", "Client")
    date = intake.get("date", datetime.now().strftime("%Y-%m-%d"))
    scenarios = intake["scenarios"]

    pattern_results = {
        "sunk_cost": detect_sunk_cost(scenarios),
        "urgency_collapse": detect_urgency_collapse(scenarios),
        "retroactive_exit": detect_retroactive_exit(scenarios),
        "intention_behavior_gap": detect_intention_behavior_gap(scenarios),
        "capitulation": detect_capitulation(scenarios),
        "insight_without_system": detect_insight_without_system(scenarios),
    }

    domain_scores = score_domains(scenarios)
    blind_spots = rank_blind_spots(pattern_results)
    weak_scenarios = analyze_scenario_quality(scenarios)

    return generate_report(
        client_name=client_name,
        date=date,
        scenarios=scenarios,
        pattern_results=pattern_results,
        domain_scores=domain_scores,
        blind_spots=blind_spots,
        weak_scenarios=weak_scenarios,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="DNA Calibration Engine")
    parser.add_argument("intake", nargs="?", help="Path to intake JSON file")
    parser.add_argument("--output", "-o", help="Output markdown path")
    parser.add_argument("--demo", action="store_true", help="Run with demo client data")
    args = parser.parse_args()

    if args.demo:
        intake = DEMO_INTAKE
    elif args.intake:
        with open(args.intake) as f:
            intake = json.load(f)
    else:
        parser.print_help()
        sys.exit(1)

    report = run(intake)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
