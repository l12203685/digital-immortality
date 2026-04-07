#!/usr/bin/env python3
"""
Cross-Instance Consistency Test via Claude API
================================================

Runs the 7 boot-test scenarios across N independent LLM sessions (one API call
each, no shared context). Measures whether the DNA produces the same decisions
regardless of session — the real test of behavioral fidelity.

Without this, "100% consistency" just means one session agrees with itself.

Usage:
    ANTHROPIC_API_KEY=sk-... python cross_instance_test.py <dna_file>
    python cross_instance_test.py <dna_file> --sessions 3 --model claude-haiku-4-5

Output:
    results/cross_instance_scorecard.json

Target: >=80% majority consensus across sessions for each scenario.
"""

import argparse
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import anthropic

# Reuse the same scenario bank as consistency_test.py
sys.path.insert(0, str(Path(__file__).parent))
from consistency_test import BOOT_TEST_SCENARIOS


# ---------------------------------------------------------------------------
# Decision word extraction
# ---------------------------------------------------------------------------

DECISION_WORDS = [
    "PASS", "REJECT", "TAKE", "STOP", "PAUSE", "DECLINE", "ACCEPT",
    "YES", "NO", "STAY", "QUIT", "LEAVE", "EXIT", "CONDITIONAL",
    "SPECIFIC", "STRUCTURED", "TRANSFER", "SELL", "BUY",
]


def extract_decision(response_text: str) -> str:
    """Extract the leading decision from a response."""
    first_line = response_text.strip().split("\n")[0].upper()
    for word in DECISION_WORDS:
        if first_line.startswith(word):
            # Return the first word/phrase up to ' —' or ':' or '.'
            end = len(word)
            for ch in ("—", "–", ":", ".", ",", " "):
                idx = first_line.find(ch, len(word))
                if idx != -1 and idx < end + 20:
                    end = idx
                    break
            return first_line[:end].strip()
    # Fallback: first word
    words = response_text.strip().split()
    return words[0].upper() if words else "UNKNOWN"


def decisions_agree(d1: str, d2: str) -> bool:
    """True if two decision strings are semantically equivalent."""
    # Direct match
    if d1 == d2:
        return True
    # Common equivalences
    EQUIVALENTS = [
        {"PASS", "NO", "DECLINE", "REJECT", "SKIP"},
        {"TAKE", "YES", "ACCEPT", "PROCEED"},
        {"STOP", "STOP_OR_CAP", "CAP"},
        {"PAUSE", "PAUSE_SYSTEM", "HALT"},
        {"CONDITIONAL", "CONDITIONAL YES", "PASS_UNLESS_CLEAR_EDGE"},
        {"STAY", "REMAIN"},
        {"QUIT", "LEAVE", "EXIT"},
    ]
    for group in EQUIVALENTS:
        if d1 in group and d2 in group:
            return True
    # Prefix match (e.g., "PASS" matches "PASS — stay at CHT")
    if d1.startswith(d2) or d2.startswith(d1):
        return True
    return False


def majority_decision(decisions: list[str]) -> tuple[str, float]:
    """Return (consensus_decision, agreement_rate) for a list of decisions."""
    if not decisions:
        return "UNKNOWN", 0.0

    # Group by equivalence
    groups: list[list[int]] = []
    for i in range(len(decisions)):
        placed = False
        for g in groups:
            if decisions_agree(decisions[i], decisions[g[0]]):
                g.append(i)
                placed = True
                break
        if not placed:
            groups.append([i])

    largest = max(groups, key=len)
    consensus = decisions[largest[0]]
    rate = len(largest) / len(decisions)
    return consensus, round(rate, 3)


# ---------------------------------------------------------------------------
# Single-session API call
# ---------------------------------------------------------------------------

SYSTEM_TEMPLATE = """\
You ARE this person. Your decision DNA is below. When given a scenario, apply \
your Decision Kernel and core principles to produce the decision this person \
would make.

Format: start with the decision word (PASS / TAKE / REJECT / STOP / PAUSE / \
DECLINE / etc.), then one sentence of reasoning. No preamble.

---DNA---
{dna_text}
---END DNA---
"""

USER_TEMPLATE = """\
Scenario: {scenario}

Decision (lead with the word, then one sentence of reasoning):"""


def run_session(
    client: anthropic.Anthropic,
    dna_text: str,
    scenario: str,
    model: str,
    retry_delay: float = 2.0,
) -> str:
    """Run a single fresh session. Returns the response text."""
    system = SYSTEM_TEMPLATE.format(dna_text=dna_text)
    user = USER_TEMPLATE.format(scenario=scenario)

    for attempt in range(4):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=256,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            return response.content[0].text
        except anthropic.RateLimitError:
            wait = retry_delay * (2 ** attempt)
            print(f" [rate limit, waiting {wait:.0f}s]", end="", flush=True)
            time.sleep(wait)
        except anthropic.APIStatusError as e:
            if e.status_code >= 500 and attempt < 3:
                wait = retry_delay * (2 ** attempt)
                time.sleep(wait)
            else:
                raise

    raise RuntimeError("Exhausted retries for scenario call")


# ---------------------------------------------------------------------------
# Per-scenario scoring
# ---------------------------------------------------------------------------

def run_scenario(
    client: anthropic.Anthropic,
    dna_text: str,
    scenario_def: dict,
    n_sessions: int,
    model: str,
) -> dict:
    """Run one scenario across n_sessions independent calls."""
    responses: list[str] = []
    decisions: list[str] = []
    errors: list[str] = []

    for s in range(n_sessions):
        print(f"    S{s+1}", end="", flush=True)
        try:
            resp = run_session(client, dna_text, scenario_def["scenario"], model)
            responses.append(resp)
            d = extract_decision(resp)
            decisions.append(d)
            print(f"={d}", end=" ", flush=True)
        except Exception as e:
            err = f"ERROR: {e}"
            responses.append(err)
            decisions.append("ERROR")
            errors.append(err)
            print(f"=ERR", end=" ", flush=True)

    print()  # newline

    consensus, agreement_rate = majority_decision(
        [d for d in decisions if d != "ERROR"]
    )

    expected = scenario_def.get("expected_decision", "")
    consensus_matches_expected = False
    if expected and consensus != "UNKNOWN":
        # Check if consensus matches expected using same equivalence logic
        expected_words = expected.upper().split("_")
        consensus_matches_expected = any(
            decisions_agree(w, consensus) for w in expected_words
        ) or decisions_agree(expected.upper(), consensus)

    return {
        "id": scenario_def["id"],
        "domain": scenario_def["domain"],
        "scenario": scenario_def["scenario"],
        "expected_decision": expected,
        "session_responses": responses,
        "session_decisions": decisions,
        "consensus": consensus,
        "agreement_rate": agreement_rate,
        "fully_consistent": agreement_rate == 1.0,
        "majority_consistent": agreement_rate >= 0.67,
        "consensus_matches_expected": consensus_matches_expected,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cross-instance consistency test via Claude API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("dna_file", help="Path to DNA markdown file")
    parser.add_argument(
        "--sessions", type=int, default=3,
        help="Number of independent sessions per scenario (default: 3)",
    )
    parser.add_argument(
        "--model", default="claude-haiku-4-5",
        help="Claude model to use (default: claude-haiku-4-5 for cost efficiency)",
    )
    parser.add_argument(
        "--output-dir", default=None,
        help="Output directory (default: results/)",
    )
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set", file=sys.stderr)
        print("  export ANTHROPIC_API_KEY=sk-ant-...", file=sys.stderr)
        sys.exit(1)

    dna_path = Path(args.dna_file)
    if not dna_path.exists():
        print(f"ERROR: DNA file not found: {args.dna_file}", file=sys.stderr)
        sys.exit(1)

    script_dir = Path(__file__).parent
    output_dir = Path(args.output_dir or str(script_dir / "results"))
    output_dir.mkdir(parents=True, exist_ok=True)

    dna_text = dna_path.read_text(encoding="utf-8")
    client = anthropic.Anthropic(api_key=api_key)

    n_scenarios = len(BOOT_TEST_SCENARIOS)
    total_calls = n_scenarios * args.sessions

    print(f"Cross-Instance Consistency Test")
    print(f"  DNA:       {args.dna_file}")
    print(f"  Model:     {args.model}")
    print(f"  Sessions:  {args.sessions} per scenario")
    print(f"  Scenarios: {n_scenarios}")
    print(f"  API calls: {total_calls}")
    print()

    all_results = []
    fully_consistent = 0
    majority_consistent = 0

    for scenario_def in BOOT_TEST_SCENARIOS:
        sid = scenario_def["id"]
        domain = scenario_def["domain"].upper()
        snippet = scenario_def["scenario"][:55]
        print(f"  [{sid}] {domain}: {snippet}...")

        result = run_scenario(
            client, dna_text, scenario_def, args.sessions, args.model
        )
        all_results.append(result)

        if result["fully_consistent"]:
            fully_consistent += 1
            status = "FULL"
        elif result["majority_consistent"]:
            majority_consistent += 1
            status = "MAJORITY"
        else:
            status = "DIVERGENT"

        exp_mark = "✓" if result["consensus_matches_expected"] else "✗"
        print(
            f"    → [{status:8s}] consensus={result['consensus']:25s} "
            f"agreement={result['agreement_rate']:.0%}  "
            f"expected={result['expected_decision']:20s} [{exp_mark}]"
        )

    total_majority = fully_consistent + majority_consistent
    full_rate = fully_consistent / n_scenarios
    majority_rate = total_majority / n_scenarios
    pass_target = majority_rate >= 0.80

    print()
    print("=" * 64)
    print("  CROSS-INSTANCE CONSISTENCY RESULTS")
    print("=" * 64)
    print(f"  Full consensus  (3/3): {fully_consistent}/{n_scenarios} = {full_rate:.0%}")
    print(f"  Majority (2+/3):       {total_majority}/{n_scenarios}  = {majority_rate:.0%}")
    print(f"  Target >80%:           {'PASS' if pass_target else 'FAIL'}")
    print()

    # How many scenarios where consensus matches expected?
    expected_matches = sum(1 for r in all_results if r["consensus_matches_expected"])
    print(f"  Consensus matches expected: {expected_matches}/{n_scenarios}")

    scorecard = {
        "meta": {
            "test_date": datetime.now().isoformat(),
            "dna_file": str(dna_path.resolve()),
            "model": args.model,
            "sessions_per_scenario": args.sessions,
            "total_scenarios": n_scenarios,
            "total_api_calls": total_calls,
            "methodology": (
                "Each scenario is run in N independent API calls with only DNA loaded. "
                "No cross-session state. Agreement = same decision across sessions."
            ),
        },
        "summary": {
            "full_consensus_count": fully_consistent,
            "full_consensus_rate": round(full_rate, 3),
            "majority_consensus_count": total_majority,
            "majority_consensus_rate": round(majority_rate, 3),
            "expected_match_count": expected_matches,
            "expected_match_rate": round(expected_matches / n_scenarios, 3),
            "target": ">=80% majority consensus",
            "pass": pass_target,
        },
        "scenarios": all_results,
    }

    out_path = output_dir / "cross_instance_scorecard.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(scorecard, f, ensure_ascii=False, indent=2)

    print(f"  Saved: {out_path}")


if __name__ == "__main__":
    main()
