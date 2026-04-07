#!/usr/bin/env python3
"""
Recursive Self-Prompt Engine for Digital Immortality.

Manages the state files and cycle tracking that support the recursive loop:
    Input(t) = Output(t-1) + "Given the current state of this repo, what advances digital immortality the most?"
    Output(t) = LLM(Input(t))

The actual LLM reasoning happens in Claude Code sessions. This script handles
the plumbing: reading previous output, generating structured prompts, tracking
cycle history.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STAGING = ROOT / "staging"
RESULTS = ROOT / "results"
LAST_OUTPUT = STAGING / "last_output.md"
NEXT_INPUT = STAGING / "next_input.md"
DAILY_LOG = RESULTS / "daily_log.md"

# Memory integration — import from sibling module
import memory_manager

RECURSIVE_QUESTION = (
    "Given the current state of this repo, what advances digital immortality the most?"
)

SEED_OUTPUT = """\
# Cycle 0 — Seed State

## Current State
- DNA.md: not yet created
- Boot tests: not yet created
- Recursive engine: initialized
- Self-sustainability: no revenue streams yet

## Key Assets
- SKILL.md: defines the digital immortality framework
- Architecture: DNA + boot_tests + memory/ + staging/ + CLAUDE.md

## Open Questions
- Who is the person this twin represents?
- What source material exists for the learning phase?
- What is the first revenue-generating system to build?

## Priority
Bootstrap the DNA document. Without it, nothing else has a foundation.
"""

PROMPT_TEMPLATE = """\
# Recursive Cycle {cycle} — {timestamp}

## Previous Output (t-1)
{previous_output}

---

## Directive
{question}

## Constraints
- Action > report. Produce something concrete, not just analysis.
- If no external input exists, cross-reference existing knowledge for new insights.
- Stop recursing = death. Produce output that feeds the next cycle.
- Bias toward inaction on trades/deploys, but never toward inaction on thinking.

## Expected Output
1. What was done this cycle (concrete actions, not plans)
2. What changed in the repo
3. What the next cycle should focus on
4. Any branches pushed or PRs opened

Write your output to staging/last_output.md when done.
"""


def ensure_dirs():
    """Create staging/ and results/ if they don't exist."""
    STAGING.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)


def read_file(path: Path) -> str | None:
    """Read a file, returning None if it doesn't exist."""
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def get_cycle_number() -> int:
    """Determine current cycle number from daily_log.md."""
    log = read_file(DAILY_LOG)
    if not log:
        return 1
    # Count cycle entries
    return log.count("## Cycle ") + 1


def init(args):
    """Initialize seed files for the first cycle."""
    ensure_dirs()

    if LAST_OUTPUT.exists() and not getattr(args, "force", False):
        print(f"Already initialized: {LAST_OUTPUT} exists. Use --force to overwrite.")
        return

    LAST_OUTPUT.write_text(SEED_OUTPUT, encoding="utf-8")
    print(f"  wrote {LAST_OUTPUT}")

    # Create daily log header if it doesn't exist
    if not DAILY_LOG.exists():
        header = "# Digital Immortality — Cycle Log\n\nRecursive engine cycle history.\n\n"
        DAILY_LOG.write_text(header, encoding="utf-8")
        print(f"  wrote {DAILY_LOG}")

    # Ensure memory directory exists
    memory_manager.MEMORY_DIR.mkdir(exist_ok=True)
    print(f"  memory system ready at {memory_manager.MEMORY_DIR}")

    # Generate the first prompt
    generate_prompt()
    print("Init complete. Run a Claude Code session using staging/next_input.md as context.")
    print("Memory system is wired in: memories are recalled at cycle start and stored at cycle end.")


def _recall_recent_memories(limit: int = 5) -> str:
    """Recall recent memories across all categories and format them for prompt injection."""
    lines = []
    for category in memory_manager.CATEGORIES:
        entries = memory_manager.recall(category)
        if entries:
            # Take the most recent entries (they're appended, so tail is newest)
            recent = entries[-limit:]
            for entry in recent:
                lines.append(f"- [{category}] {entry['key']}: {entry['content']}")
    return "\n".join(lines) if lines else "(no memories stored yet)"


def _store_cycle_insight(cycle: int):
    """Store a memory entry recording that this cycle's prompt was generated."""
    memory_manager.store(
        category="insights",
        key=f"cycle-{cycle}-prompt",
        content=f"Cycle {cycle} prompt generated. Previous output consumed and fed forward.",
        source=f"recursive-engine-cycle-{cycle}",
        tags=["recursive-engine", "cycle-transition"],
    )


def generate_prompt():
    """Read previous output and generate the next cycle's input prompt."""
    ensure_dirs()

    previous = read_file(LAST_OUTPUT)
    if previous is None:
        print("No previous output found. Run with --init first.", file=sys.stderr)
        sys.exit(1)

    cycle = get_cycle_number()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Read recent memories at cycle start
    recent_memories = _recall_recent_memories()
    print(f"Recalled memories for cycle {cycle}:\n{recent_memories}\n")

    prompt = PROMPT_TEMPLATE.format(
        cycle=cycle,
        timestamp=now,
        previous_output=previous.strip(),
        question=RECURSIVE_QUESTION,
    )

    # Inject memory context into the prompt before the directive
    memory_section = (
        f"\n## Cross-Session Memory\n"
        f"Recent memories recalled at cycle start:\n{recent_memories}\n"
    )
    prompt = prompt.replace(
        "\n---\n\n## Directive",
        f"\n{memory_section}\n---\n\n## Directive",
    )

    NEXT_INPUT.write_text(prompt, encoding="utf-8")
    print(f"Cycle {cycle} prompt written to {NEXT_INPUT}")

    # Store cycle transition insight at cycle end
    _store_cycle_insight(cycle)
    print(f"Stored cycle {cycle} insight to memory.")

    # Auto-prune memory to prevent unbounded growth
    removed = memory_manager.auto_prune()
    total_removed = sum(removed.values())
    if total_removed > 0:
        print(f"Auto-pruned {total_removed} stale/excess memory entries: {removed}")
    else:
        print("Auto-prune: memory within bounds, nothing removed.")

    # Append cycle metadata to daily log
    append_cycle_log(cycle, now)


def append_cycle_log(cycle: int, timestamp: str):
    """Append a cycle entry to the daily log."""
    entry = f"\n## Cycle {cycle} — {timestamp}\n- Prompt generated\n- Status: awaiting execution\n\n"

    if not DAILY_LOG.exists():
        DAILY_LOG.write_text(
            "# Digital Immortality — Cycle Log\n\nRecursive engine cycle history.\n\n",
            encoding="utf-8",
        )

    with open(DAILY_LOG, "a", encoding="utf-8") as f:
        f.write(entry)


def show_status():
    """Display current engine state."""
    ensure_dirs()

    print("=== Recursive Engine Status ===\n")

    # Last output info
    if LAST_OUTPUT.exists():
        stat = LAST_OUTPUT.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        print(f"Last output:  {mtime.strftime('%Y-%m-%d %H:%M UTC')}")
        content = LAST_OUTPUT.read_text(encoding="utf-8")
        # Show first heading as summary
        for line in content.splitlines():
            if line.startswith("# "):
                print(f"  Title:      {line.lstrip('# ').strip()}")
                break
    else:
        print("Last output:  [none — run --init]")

    # Next input info
    if NEXT_INPUT.exists():
        stat = NEXT_INPUT.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        print(f"Next input:   {mtime.strftime('%Y-%m-%d %H:%M UTC')}")
    else:
        print("Next input:   [none — run --prompt]")

    # Cycle count
    cycle = get_cycle_number()
    print(f"Next cycle:   {cycle}")

    # Git branch info
    try:
        import subprocess
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, cwd=ROOT
        ).stdout.strip()
        print(f"Git branch:   {branch}")

        # Recent pushes
        result = subprocess.run(
            ["git", "log", "--oneline", "-5", "--format=%h %s (%ar)"],
            capture_output=True, text=True, cwd=ROOT
        )
        if result.stdout.strip():
            print("\nRecent commits:")
            for line in result.stdout.strip().splitlines():
                print(f"  {line}")
    except Exception:
        pass

    # Memory stats
    counts = memory_manager.list_categories()
    total = sum(counts.values())
    print(f"\nMemory ({total} total entries):")
    for cat, count in counts.items():
        print(f"  {cat:15s} {count:4d} entries")

    # Pending actions from last_output
    if LAST_OUTPUT.exists():
        content = LAST_OUTPUT.read_text(encoding="utf-8")
        if "## Priority" in content or "## Open Questions" in content:
            print("\nPending from last output:")
            capture = False
            for line in content.splitlines():
                if line.startswith("## Priority") or line.startswith("## Open Questions"):
                    capture = True
                    continue
                elif line.startswith("## ") and capture:
                    capture = False
                elif capture and line.strip():
                    print(f"  {line.strip()}")


def main():
    parser = argparse.ArgumentParser(
        description="Recursive self-prompt engine for digital immortality.",
        epilog="Workflow: --init once, then --prompt before each Claude Code session.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--init", action="store_true", help="Create initial seed files")
    group.add_argument("--prompt", action="store_true", help="Generate next cycle prompt")
    group.add_argument("--status", action="store_true", help="Show current engine state")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files on init")

    args = parser.parse_args()

    if args.init:
        init(args)
    elif args.prompt:
        generate_prompt()
    elif args.status:
        show_status()


if __name__ == "__main__":
    main()
