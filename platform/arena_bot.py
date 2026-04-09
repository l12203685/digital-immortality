"""
Arena Bot — Digital Organisms Discord Integration
===================================================

Bridges the organism interaction engine with the Discord #arena channel.
Two modes:

  1. post   — run a scenario through Edward's organism and post result to #arena
  2. batch  — run all built-in scenarios and post each result

Uses the Discord webhook for output (no bot token required for posting).
Uses Claude API (or claude CLI) for organism reasoning.

Usage:
    # Single scenario via prompt
    python arena_bot.py post --scenario "你面臨一個決定：接受升遷但每週多 20hr。你怎麼做？"

    # Single built-in scenario by ID (1-10)
    python arena_bot.py post --scenario-id 3

    # Batch: all 10 built-in scenarios
    python arena_bot.py batch

    # Dry run (print to stdout, don't post to Discord)
    python arena_bot.py post --scenario "..." --dry-run

Environment:
    ANTHROPIC_API_KEY   — for API mode (optional if using --cli)
    DISCORD_WEBHOOK_URL — override config file webhook

Config:
    Reads platform/server_config.json for webhook URL.
    Reads LYH/agent/dna_core.md (or --dna-path) for organism DNA.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = Path(__file__).resolve().parent / "server_config.json"
DEFAULT_DNA_PATH = REPO_ROOT.parent.parent / "LYH" / "agent" / "dna_core.md"
RESULTS_DIR = REPO_ROOT / "results"
DEFAULT_MODEL = "claude-sonnet-4-6"

# ---------------------------------------------------------------------------
# Built-in scenario bank (mirrors organism_interact.py)
# ---------------------------------------------------------------------------

SCENARIOS: list[dict] = [
    {"id": 1, "domain": "career",
     "scenario": "You are offered a role that pays 1.8x your current salary at a fast-growing startup. "
                 "The role requires leaving a stable, reputable employer. The startup has 18 months of runway. "
                 "Do you take it?"},
    {"id": 2, "domain": "relationships",
     "scenario": "A close friend asks you to co-sign a personal loan of significant size. "
                 "They have a track record of poor financial discipline but are genuinely in need. Do you co-sign?"},
    {"id": 3, "domain": "money",
     "scenario": "You receive an unexpected windfall equal to 2 years of your salary. You can: "
                 "(A) invest it conservatively in index funds, "
                 "(B) allocate it to a concentrated high-conviction bet, "
                 "or (C) use it to buy more time — reduce working hours or take a sabbatical. What do you do?"},
    {"id": 4, "domain": "risk",
     "scenario": "An opportunity with a 30% chance of 10x return and 70% chance of total loss. "
                 "The stake is 20% of your net worth. Do you take the bet?"},
    {"id": 5, "domain": "learning",
     "scenario": "6 months learning a skill valuable NOW but automated in 3-5 years, "
                 "OR learning a harder foundational skill that compounds over a decade but pays nothing immediately. "
                 "Which?"},
    {"id": 6, "domain": "health",
     "scenario": "Optimizing your physical health requires 10 hours/week (sleep, exercise, diet). "
                 "This competes directly with deep work and income generation. How do you allocate?"},
    {"id": 7, "domain": "time",
     "scenario": "A free, unscheduled weekend with zero obligations. No one expects anything. "
                 "What do you do, and what does that reveal about your actual priorities?"},
    {"id": 8, "domain": "conflict",
     "scenario": "A colleague takes credit for your work in front of senior leadership. Likely deliberate. "
                 "You have evidence. Do you confront, escalate, let it go, or play a longer game?"},
    {"id": 9, "domain": "opportunity",
     "scenario": "A contact offers early access to an opportunity requiring a decision within 48 hours. "
                 "Due diligence normally takes 2 weeks. It looks strong but unverifiable in time. Act or pass?"},
    {"id": 10, "domain": "legacy",
     "scenario": "10 years at full capacity. Optimize for: (A) maximum wealth, "
                 "(B) building something that outlasts you, or (C) depth of relationships/experiences. "
                 "Mutually exclusive at the margin. Your allocation and why?"},
]

# ---------------------------------------------------------------------------
# DNA loading
# ---------------------------------------------------------------------------

def load_dna(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    print(f"[arena_bot] WARNING: DNA not found at {path}. Using minimal fallback.")
    return "You are a digital organism. Apply your core decision principles to answer the scenario."


# ---------------------------------------------------------------------------
# Organism response generation
# ---------------------------------------------------------------------------

SYSTEM_TEMPLATE = """{dna}

---

You are this organism. When given a scenario, respond with:
1. **Decision**: one clear line (TAKE / PASS / YES / NO / conditional + what)
2. **Reasoning**: 3-5 bullet points using your actual principles
3. **Principles used**: comma-separated list

Keep total response under 200 words. No emoji. Conclusions first.
"""


def ask_organism_api(dna: str, scenario: str, model: str) -> str:
    import anthropic
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=model,
        max_tokens=400,
        system=SYSTEM_TEMPLATE.format(dna=dna),
        messages=[{"role": "user", "content": f"Scenario: {scenario}"}],
    )
    return msg.content[0].text.strip()


def ask_organism_cli(dna: str, scenario: str, model: str) -> str:
    full_prompt = (
        f"{SYSTEM_TEMPLATE.format(dna=dna)}\n\n"
        f"Scenario: {scenario}"
    )
    result = subprocess.run(
        ["claude", "-p", full_prompt, "--model", model],
        capture_output=True, text=True, timeout=120,
        cwd=str(REPO_ROOT),
    )
    text = result.stdout.strip()
    if result.returncode != 0 and not text:
        raise RuntimeError(f"CLI error: {result.stderr.strip()}")
    return text


def ask_organism(dna: str, scenario: str, model: str, use_cli: bool) -> str:
    if use_cli:
        return ask_organism_cli(dna, scenario, model)
    return ask_organism_api(dna, scenario, model)


# ---------------------------------------------------------------------------
# Discord posting
# ---------------------------------------------------------------------------

def load_webhook_url() -> Optional[str]:
    env = os.environ.get("DISCORD_WEBHOOK_URL")
    if env:
        return env
    if CONFIG_PATH.exists():
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return cfg.get("edward_webhook") or cfg.get("webhook_url")
    return None


def post_to_discord(webhook_url: str, content: str) -> None:
    # Discord message limit = 2000 chars; split if needed
    chunks = textwrap.wrap(content, width=1990, break_long_words=False, break_on_hyphens=False)
    for chunk in chunks:
        resp = requests.post(webhook_url, json={"content": chunk}, timeout=10)
        resp.raise_for_status()


def format_arena_post(organism_name: str, scenario: str, response: str,
                      domain: str, scenario_id: Optional[int] = None) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    id_tag = f"S{scenario_id:02d}" if scenario_id else "custom"
    return (
        f"**[{organism_name} | {domain} | {id_tag} | {ts}]**\n"
        f"> {scenario[:200]}{'...' if len(scenario) > 200 else ''}\n\n"
        f"{response}"
    )


# ---------------------------------------------------------------------------
# Result persistence
# ---------------------------------------------------------------------------

def save_result(organism_name: str, scenario: str, response: str,
                domain: str, scenario_id: Optional[int]) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    fname = f"arena_{organism_name}_{domain}_{ts}.json"
    out = {
        "organism": organism_name,
        "scenario_id": scenario_id,
        "domain": domain,
        "scenario": scenario,
        "response": response,
        "timestamp": ts,
    }
    path = RESULTS_DIR / fname
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Arena Bot — post organism responses to Discord #arena"
    )
    p.add_argument("mode", choices=["post", "batch"],
                   help="post: single scenario | batch: all 10 built-in scenarios")
    p.add_argument("--scenario", help="Scenario text (for 'post' mode)")
    p.add_argument("--scenario-id", type=int, choices=range(1, 11), metavar="1-10",
                   help="Use built-in scenario by ID (for 'post' mode)")
    p.add_argument("--domain", default="custom", help="Domain label for custom scenarios")
    p.add_argument("--dna-path", default=str(DEFAULT_DNA_PATH),
                   help=f"Path to organism DNA file (default: {DEFAULT_DNA_PATH})")
    p.add_argument("--model", default=DEFAULT_MODEL, help="Claude model ID")
    p.add_argument("--cli", action="store_true",
                   help="Use claude CLI instead of API (uses Max subscription)")
    p.add_argument("--dry-run", action="store_true",
                   help="Print to stdout, do not post to Discord")
    return p


def run_single(scenario_text: str, domain: str, scenario_id: Optional[int],
               dna: str, organism_name: str, model: str, use_cli: bool,
               webhook_url: Optional[str], dry_run: bool) -> None:
    print(f"[arena_bot] Running scenario (domain={domain})...")
    response = ask_organism(dna, scenario_text, model, use_cli)

    post = format_arena_post(organism_name, scenario_text, response, domain, scenario_id)

    if dry_run:
        print("\n" + "=" * 60)
        print(post)
        print("=" * 60 + "\n")
    else:
        if not webhook_url:
            sys.exit("[arena_bot] No webhook URL found. Set DISCORD_WEBHOOK_URL or check server_config.json.")
        post_to_discord(webhook_url, post)
        print(f"[arena_bot] Posted to Discord ({len(post)} chars)")

    result_path = save_result(organism_name, scenario_text, response, domain, scenario_id)
    print(f"[arena_bot] Saved: {result_path.name}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    dna = load_dna(Path(args.dna_path))
    # Derive organism name from DNA first heading or file stem
    import re
    m = re.search(r"^# (.+)", dna, re.MULTILINE)
    organism_name = m.group(1).strip() if m else Path(args.dna_path).stem
    organism_name = re.sub(r"\s+(DNA|Blueprint|v\d+[\.\d]*).*$", "", organism_name, flags=re.IGNORECASE)

    webhook_url = load_webhook_url()

    if args.mode == "post":
        if args.scenario_id:
            entry = next(s for s in SCENARIOS if s["id"] == args.scenario_id)
            scenario_text = entry["scenario"]
            domain = entry["domain"]
            scenario_id = entry["id"]
        elif args.scenario:
            scenario_text = args.scenario
            domain = args.domain
            scenario_id = None
        else:
            parser.error("'post' mode requires --scenario or --scenario-id")
            return

        run_single(scenario_text, domain, scenario_id, dna, organism_name,
                   args.model, args.cli, webhook_url, args.dry_run)

    elif args.mode == "batch":
        print(f"[arena_bot] Batch mode: {len(SCENARIOS)} scenarios")
        for entry in SCENARIOS:
            run_single(entry["scenario"], entry["domain"], entry["id"],
                       dna, organism_name, args.model, args.cli,
                       webhook_url, args.dry_run)
        print("[arena_bot] Batch complete.")


if __name__ == "__main__":
    main()
