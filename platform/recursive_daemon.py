"""
Recursive Engine Daemon — Digital Immortality Platform
Continuously runs the recursive question against Claude API,
persists results, and optionally commits code changes.
"""

import argparse
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import anthropic

REPO_ROOT = Path(__file__).resolve().parent.parent
DNA_PATH = REPO_ROOT.parent.parent / "LYH" / "agent" / "edward_dna_v18.md"
LOG_PATH = REPO_ROOT / "results" / "daemon_log.md"
DEFAULT_MODEL = "claude-haiku-4-5"
MIN_INTERVAL = 5  # seconds, rate-limit floor

DYNAMIC_TREE = """\
## Dynamic Tree — 6 Branches

1. **DNA Fidelity** — Sharpen decision kernel accuracy; reduce drift across instances
2. **Cross-Instance Consistency** — Ensure any cold-booted agent passes Naked Boot Test
3. **Economic Autonomy** — Build cash-flow loops that cover agent running costs
4. **Organism Interaction** — Enable multi-organism collision, learning, social dynamics
5. **Memory Persistence** — Improve log/patch/session_state pipeline; zero context loss
6. **Platform Infrastructure** — Harden boot sequence, daemon, eval harness, CI
"""

RECURSIVE_PROMPT = (
    "You are Edward's recursive engine. Read the repo state, pick the "
    "highest-derivative branch from the dynamic tree, do one concrete thing, "
    "report what you did in under 100 words."
)

running = True


def handle_signal(sig, frame):
    global running
    print("\n[daemon] Caught signal, shutting down gracefully...")
    running = False


def load_dna() -> str:
    if DNA_PATH.exists():
        return DNA_PATH.read_text(encoding="utf-8")
    print(f"[daemon] WARNING: DNA file not found at {DNA_PATH}, using minimal context")
    return "You are Edward (Lin Ying-Hung). Operate with his decision kernel."


def build_system_prompt(dna: str) -> str:
    return f"{dna}\n\n---\n\n{DYNAMIC_TREE}"


def append_log(cycle: int, response: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    entry = f"\n## Cycle {cycle} — {ts}\n\n{response}\n"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry)


def try_git_commit(cycle: int) -> None:
    """If there are uncommitted changes in the repo, commit them."""
    try:
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=10,
        )
        if status.stdout.strip():
            subprocess.run(
                ["git", "add", "-A"],
                cwd=REPO_ROOT, capture_output=True, timeout=10,
            )
            msg = f"daemon: cycle {cycle} auto-commit"
            subprocess.run(
                ["git", "commit", "-m", msg],
                cwd=REPO_ROOT, capture_output=True, timeout=10,
            )
            print(f"[daemon] Committed changes (cycle {cycle})")
    except Exception as e:
        print(f"[daemon] Git commit skipped: {e}")


def run_cycle(client: anthropic.Anthropic, system: str, model: str, cycle: int) -> str:
    print(f"[daemon] Cycle {cycle} starting...")
    response = client.messages.create(
        model=model,
        max_tokens=512,
        system=system,
        messages=[{"role": "user", "content": RECURSIVE_PROMPT}],
    )
    text = response.content[0].text
    print(f"[daemon] Cycle {cycle} done — {len(text)} chars")
    return text


def main():
    global running
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    parser = argparse.ArgumentParser(description="Digital Immortality Recursive Daemon")
    parser.add_argument("--interval", type=int, default=0,
                        help="Seconds between cycles (0 = minimal delay)")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL,
                        help=f"Claude model to use (default: {DEFAULT_MODEL})")
    parser.add_argument("--max-cycles", type=int, default=0,
                        help="Stop after N cycles (0 = infinite)")
    parser.add_argument("--no-commit", action="store_true",
                        help="Disable auto git commit")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[daemon] ERROR: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    dna = load_dna()
    system = build_system_prompt(dna)
    interval = max(args.interval, MIN_INTERVAL)
    cycle = 0

    print(f"[daemon] Starting recursive engine")
    print(f"[daemon] Model: {args.model} | Interval: {interval}s | DNA: {DNA_PATH}")
    print(f"[daemon] Log: {LOG_PATH}")
    print(f"[daemon] Ctrl+C to stop\n")

    while running:
        cycle += 1
        if args.max_cycles and cycle > args.max_cycles:
            print(f"[daemon] Reached max cycles ({args.max_cycles}), stopping.")
            break
        try:
            text = run_cycle(client, system, args.model, cycle)
            append_log(cycle, text)
            if not args.no_commit:
                try_git_commit(cycle)
        except anthropic.RateLimitError:
            print("[daemon] Rate limited, backing off 60s...")
            time.sleep(60)
            continue
        except anthropic.APIError as e:
            print(f"[daemon] API error: {e}, retrying in 30s...")
            time.sleep(30)
            continue
        except Exception as e:
            print(f"[daemon] Unexpected error: {e}")
            time.sleep(10)
            continue

        if running and interval > 0:
            time.sleep(interval)

    print("[daemon] Shutdown complete.")


if __name__ == "__main__":
    main()
