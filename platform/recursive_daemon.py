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
DNA_PATH = REPO_ROOT.parent.parent / "LYH" / "agent" / "dna_core.md"
LOG_PATH = REPO_ROOT / "results" / "daemon_log.md"
DEFAULT_MODEL = "claude-sonnet-4-6"
MIN_INTERVAL = 5  # seconds, rate-limit floor

TREE_PATH = REPO_ROOT / "results" / "dynamic_tree.md"

RECURSIVE_PROMPT = (
    "You are Edward's recursive engine. The dynamic tree below is your state — "
    "it shows all branches, their status, and derivative. Each cycle:\n"
    "1. Read the tree. Pick highest-derivative branch(es).\n"
    "2. Do concrete work (fix code, add tests, write docs, build features).\n"
    "3. Update the tree itself: add/remove/modify branches, update status, shift derivatives.\n"
    "4. Report what you did AND how the tree changed. Under 200 words.\n\n"
    "The tree is alive. Branches are not fixed — add new ones, merge overlapping, "
    "split large ones, kill dead ones. Anything that advances digital immortality.\n\n"
    "Rules: every cycle MUST change code AND update tree. No monitoring. No 'no change'. "
    "learn = write. 遞迴 + persist = 演化。"
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


def run_cycle_api(client, system: str, model: str, cycle: int) -> str:
    """Run via Anthropic API (requires ANTHROPIC_API_KEY with credit)."""
    print(f"[daemon] Cycle {cycle} starting (API)...")
    response = client.messages.create(
        model=model,
        max_tokens=512,
        system=system,
        messages=[{"role": "user", "content": RECURSIVE_PROMPT}],
    )
    text = response.content[0].text
    print(f"[daemon] Cycle {cycle} done — {len(text)} chars")
    return text


def run_cycle_cli(prompt: str, model: str, cycle: int) -> str:
    """Run via claude CLI (uses Max subscription, no API credit needed)."""
    print(f"[daemon] Cycle {cycle} starting (CLI)...")
    full_prompt = f"{prompt}\n\n{RECURSIVE_PROMPT}"
    result = subprocess.run(
        ["claude", "-p", full_prompt, "--model", model],
        capture_output=True, text=True, timeout=300,
        cwd=str(REPO_ROOT),
    )
    text = result.stdout.strip()
    if result.returncode != 0 and not text:
        text = f"CLI error: {result.stderr.strip()}"
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
    parser.add_argument("--cli", action="store_true",
                        help="Use claude CLI instead of API (uses Max subscription, no API credit)")
    args = parser.parse_args()

    dna = load_dna()
    system = build_system_prompt(dna)
    interval = max(args.interval, MIN_INTERVAL)
    cycle = 0
    client = None
    use_cli = args.cli

    if not use_cli:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("[daemon] No ANTHROPIC_API_KEY, falling back to CLI mode")
            use_cli = True
        else:
            client = anthropic.Anthropic(api_key=api_key)

    mode = "CLI (Max subscription)" if use_cli else "API"
    print(f"[daemon] Starting recursive engine")
    print(f"[daemon] Mode: {mode} | Model: {args.model} | Interval: {interval}s")
    print(f"[daemon] Log: {LOG_PATH}")
    print(f"[daemon] Ctrl+C to stop\n")

    while running:
        cycle += 1
        if args.max_cycles and cycle > args.max_cycles:
            print(f"[daemon] Reached max cycles ({args.max_cycles}), stopping.")
            break
        try:
            if use_cli:
                text = run_cycle_cli(system, args.model, cycle)
            else:
                text = run_cycle_api(client, system, args.model, cycle)
            append_log(cycle, text)
            if not args.no_commit:
                try_git_commit(cycle)
        except Exception as e:
            print(f"[daemon] Error: {e}, retrying in 30s...")
            time.sleep(30)
            continue

        if running and interval > 0:
            time.sleep(interval)

    print("[daemon] Shutdown complete.")


if __name__ == "__main__":
    main()
