#!/usr/bin/env python3
"""
Learning Loop — Branch 4: Organism Interaction
================================================

Reads collision results from results/, identifies divergences between organisms,
and generates DNA patch candidates for the losing organism.

Algorithm:
  1. Load all collision JSON files
  2. For each interaction: compare final action tokens (TAKE/PASS/YES/NO/etc.)
  3. Divergence detected → extract what principle organism_a used that organism_b lacked
  4. Generate patch candidate: principle + domain + scenario context
  5. Save to results/learning_patches.json

Output format:
  {
    "patches": [
      {
        "source_file": "...",
        "domain": "risk",
        "scenario_excerpt": "...",
        "organism_a": "Edward",
        "organism_b": "Alex Chen",
        "organism_a_action": "NO",
        "organism_b_action": "YES",
        "organism_a_distinctive_principle": "...",
        "patch_candidate": "...",
        "target_organism": "Alex Chen"
      }
    ],
    "summary": {
      "total_interactions": N,
      "divergences": N,
      "convergences": N
    }
  }

Usage:
    python learning_loop.py [--results-dir results/] [--output results/learning_patches.json]
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


REPO_ROOT = Path(__file__).resolve().parent
RESULTS_DIR = REPO_ROOT / "results"
OUTPUT_PATH = RESULTS_DIR / "learning_patches.json"

# Action tokens — extract the primary decision word from a response
ACTION_PATTERNS = [
    r"\b(TAKE|NO-TAKE|PASS|YES|NO|STAY|LEAVE|CO-SIGN|DECLINE|CONFRONT|ESCALATE|IGNORE|ACT|DEFER|CONDITIONAL)\b",
    r"\b(A|B|C)\s*[-—]\s",  # Multiple-choice fallback
]


def extract_action(text: str) -> Optional[str]:
    """Extract the primary decision token from an organism response."""
    # Normalize
    upper = text.upper()
    # Try explicit tokens first
    for pattern in ACTION_PATTERNS[:1]:
        matches = re.findall(pattern, upper)
        if matches:
            return matches[0]
    # Fallback: first word that is a strong verb
    for word in upper.split():
        word = re.sub(r"[^A-Z\-]", "", word)
        if word in {"TAKE", "PASS", "YES", "NO", "STAY", "LEAVE", "ACT", "DEFER", "ESCALATE"}:
            return word
    return None


def load_collision_files(results_dir: Path) -> list[dict]:
    """Load all JSON collision result files (exclude learning_patches, scorecards)."""
    skip_prefixes = {"learning_patches", "consistency", "cross_instance", "real_scenarios", "out_of_sample", "daily"}
    files = []
    for p in sorted(results_dir.glob("*.json")):
        if any(p.stem.startswith(s) for s in skip_prefixes):
            continue
        if "_vs_" not in p.stem:
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            # Skip placeholder files (organism name contains "[Your Name]")
            orgs = data.get("organisms", {})
            names = [orgs.get("a", {}).get("name", ""), orgs.get("b", {}).get("name", "")]
            if any("[" in n for n in names):
                continue
            data["_source_file"] = p.name
            files.append(data)
        except (json.JSONDecodeError, OSError):
            pass
    return files


def extract_distinctive_principle(organism_data: dict) -> str:
    """Extract the most distinctive principle an organism applied."""
    principles = organism_data.get("dna_principles_used", [])
    if not principles:
        return ""
    # Heuristic: pick the longest/most specific principle
    return max(principles, key=lambda p: len(p), default="")


def generate_patch_candidate(divergence: dict) -> str:
    """
    Generate a natural-language DNA patch candidate.
    The losing organism (b) should add the principle that drove organism_a's decision.
    """
    principle = divergence["organism_a_distinctive_principle"]
    domain = divergence["domain"]
    a_name = divergence["organism_a"]
    a_action = divergence["organism_a_action"]
    b_action = divergence["organism_b_action"]

    if not principle:
        return f"[No distinctive principle extracted for {domain} divergence]"

    return (
        f"In {domain} decisions, consider: \"{principle}\" "
        f"({a_name} → {a_action} vs {b_action}). "
        f"This principle drove a different outcome — evaluate if it should be incorporated."
    )


def analyze_collisions(collision_files: list[dict]) -> dict:
    """Analyze all collision files and extract divergences."""
    patches: list[dict] = []
    total_interactions = 0
    divergences = 0
    convergences = 0

    for collision in collision_files:
        meta = collision.get("meta", {})
        organisms = collision.get("organisms", {})
        interactions = collision.get("interactions", [])

        org_a_name = organisms.get("a", {}).get("name", "A")
        org_b_name = organisms.get("b", {}).get("name", "B")

        for interaction in interactions:
            total_interactions += 1
            domain = interaction.get("domain", "unknown")
            scenario = interaction.get("scenario", "")
            scenario_excerpt = scenario[:120] + "..." if len(scenario) > 120 else scenario

            org_a_data = interaction.get("organism_a", {})
            org_b_data = interaction.get("organism_b", {})

            response_a = org_a_data.get("response", "")
            response_b = org_b_data.get("response", "")

            action_a = extract_action(response_a)
            action_b = extract_action(response_b)

            if action_a and action_b and action_a != action_b:
                divergences += 1
                distinctive = extract_distinctive_principle(org_a_data)
                divergence = {
                    "source_file": collision["_source_file"],
                    "domain": domain,
                    "scenario_excerpt": scenario_excerpt,
                    "organism_a": org_a_name,
                    "organism_b": org_b_name,
                    "organism_a_action": action_a,
                    "organism_b_action": action_b,
                    "organism_a_distinctive_principle": distinctive,
                    "patch_candidate": "",
                    "target_organism": org_b_name,
                }
                divergence["patch_candidate"] = generate_patch_candidate(divergence)
                patches.append(divergence)
            elif action_a and action_b and action_a == action_b:
                convergences += 1
            # If extraction fails, count as unknown — don't patch

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "patches": patches,
        "summary": {
            "collision_files_analyzed": len(collision_files),
            "total_interactions": total_interactions,
            "divergences": divergences,
            "convergences": convergences,
            "divergence_rate": round(divergences / total_interactions, 3) if total_interactions else 0,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Learning Loop — extract DNA patches from organism collisions")
    parser.add_argument("--results-dir", default=str(RESULTS_DIR), help="Directory with collision JSON files")
    parser.add_argument("--output", default=str(OUTPUT_PATH), help="Output path for learning patches")
    parser.add_argument("--verbose", action="store_true", help="Print patches to stdout")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    output_path = Path(args.output)

    collision_files = load_collision_files(results_dir)
    if not collision_files:
        print(f"No collision files found in {results_dir}")
        return

    print(f"Loaded {len(collision_files)} collision file(s)")
    result = analyze_collisions(collision_files)

    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Patches written → {output_path}")

    summary = result["summary"]
    print(
        f"Summary: {summary['total_interactions']} interactions, "
        f"{summary['divergences']} divergences ({summary['divergence_rate']*100:.1f}%), "
        f"{summary['convergences']} convergences"
    )

    if args.verbose and result["patches"]:
        print("\nPatches:")
        for p in result["patches"]:
            print(f"  [{p['domain']}] {p['organism_a']} {p['organism_a_action']} vs "
                  f"{p['organism_b']} {p['organism_b_action']}")
            print(f"  Patch: {p['patch_candidate']}")
            print()


if __name__ == "__main__":
    main()
