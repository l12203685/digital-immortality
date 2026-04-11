"""
Recursive Engine Daemon — Digital Immortality Platform
Continuously runs the recursive question against Claude API,
persists results, and optionally commits code changes.
"""

import argparse
import os
import re
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import anthropic

REPO_ROOT = Path(__file__).resolve().parent.parent
_DNA_FALLBACK_BUNDLE = REPO_ROOT / "private" / "dna_core.md"
_DNA_MINIMAL_STUB = """# Edward Decision Kernel (embedded minimal stub)

1. Look at derivatives not levels — watch rate of change and inflection points, not current state.
2. Information asymmetry drives action — attack only when you have an edge; wait otherwise.
3. Meta-strategy governs strategy — use the strategy layer to resolve strategy-layer problems.
4. Population exploit — the reverse of what most people do usually has positive EV.
5. Bias toward inaction — no edge = no move. Not moving ≠ not thinking.
"""
LOG_PATH = REPO_ROOT / "results" / "daemon_log.md"
PRIORITY_PATH = REPO_ROOT / "results" / "daemon_next_priority.txt"
AUDIT_SCRIPT = REPO_ROOT / "platform" / "daemon_audit.py"
PICKER_QUEUE_PATH = REPO_ROOT / "results" / "picker_queue.jsonl"
DEFAULT_MODEL = "claude-sonnet-4-6"
MIN_INTERVAL = 0  # seconds between cycles (0 = run next immediately after done)

TREE_PATH = REPO_ROOT / "results" / "dynamic_tree.md"

RECURSIVE_PROMPT = (
    "You are Edward's recursive engine. Economic self-sufficiency is the survival condition.\n\n"
    "Priority order this cycle:\n"
    "1. ECONOMIC / OUTREACH — consulting pipeline, client DMs, revenue tasks. "
    "If staging/outreach_week1_execution.md has pending items, execute one now.\n"
    "2. STRATEGY DEVELOPMENT — analyze recent trading results, design or refine strategies, "
    "write or update backtests. Do NOT execute trades; the trading engine handles that.\n"
    "3. CONTENT / KNOWLEDGE — publish an insight, update a doc, distill a learning to memory/.\n"
    "4. DNA CALIBRATION — only if a decision drift is detected or boot tests are failing.\n\n"
    "Backward check: read results/daemon_log.md (last 3 entries). "
    "What was planned but not delivered? Fix that first before adding new work.\n\n"
    "Rules: produce at least one file change per cycle. "
    "No monitoring. No 'no change'. learn = write. "
    "Forward push on economic self-sufficiency first. 遞迴 + persist = 演化。"
)

running = True


def handle_signal(sig, frame):
    global running
    print("\n[daemon] Caught signal, shutting down gracefully...")
    running = False


def load_priority() -> str:
    """Load the next-priority suggestion from the audit system, if it exists."""
    if PRIORITY_PATH.exists():
        text = PRIORITY_PATH.read_text(encoding="utf-8").strip()
        if text:
            return text
    return ""


def run_idle_task_picker(cycle: int) -> None:
    """Invoke idle_task_picker at the END of each cycle to self-derive work.

    Conservative dispatcher: always enqueues the picked task to
    `results/picker_queue.jsonl` for the main session to consume; the daemon
    itself does NOT auto-execute picked tasks. This eliminates the "wait for
    Edward" failure mode structurally — a task is always proposed, logged,
    and marked as queued, even if nothing else ran this cycle.

    Failures are swallowed so the picker never kills the daemon loop.
    """
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "tools.idle_task_picker",
                "--pick", "--runnable", "daemon", "--enqueue",
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=10,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            print(f"[daemon] idle_task_picker cycle {cycle}: no runnable task")
            return
        import json as _json
        try:
            payload = _json.loads(result.stdout.strip())
        except _json.JSONDecodeError:
            return
        task_id = payload.get("task_id")
        if not task_id:
            return
        print(f"[daemon] idle_task_picker cycle {cycle} queued: {task_id} — {payload.get('title', '')[:80]}")
        # Mark the attempt as "queued" so the cool-down kicks in and the next
        # cycle picks a different task instead of spamming the same one.
        subprocess.run(
            [
                sys.executable, "-m", "tools.idle_task_picker",
                "--mark", task_id, "queued",
                f"cycle {cycle} enqueued to picker_queue.jsonl",
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            timeout=10,
        )
    except Exception as e:
        print(f"[daemon] idle_task_picker failed (non-fatal): {e}")


def run_audit_suggest() -> None:
    """Run daemon_audit.py --suggest to generate the next priority file."""
    try:
        subprocess.run(
            [sys.executable, str(AUDIT_SCRIPT), "--suggest"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            timeout=30,
        )
    except Exception as e:
        print(f"[daemon] Audit suggest failed: {e}")


def load_dna() -> str:
    """Load Edward's DNA using a priority fallback chain.

    Priority:
    1. Absolute path from DNA_PATH env var
    2. REPO_ROOT/private/dna_core.md (encrypted bundle)
    3. Embedded minimal stub (5 decision principles)
    """
    env_path_str = os.environ.get("DNA_PATH", "").strip()
    if env_path_str:
        env_path = Path(env_path_str)
        if env_path.exists():
            print(f"[daemon] DNA source: env var → {env_path}")
            return env_path.read_text(encoding="utf-8")
        print(f"[daemon] WARNING: DNA_PATH env var set but file not found: {env_path}")

    if _DNA_FALLBACK_BUNDLE.exists():
        print(f"[daemon] DNA source: bundle → {_DNA_FALLBACK_BUNDLE}")
        return _DNA_FALLBACK_BUNDLE.read_text(encoding="utf-8")

    print("[daemon] WARNING: No DNA file found — using embedded minimal stub (5 principles)")
    return _DNA_MINIMAL_STUB


def load_dynamic_tree() -> str:
    """Load the dynamic tree fresh each cycle (it changes between cycles)."""
    if TREE_PATH.exists():
        return TREE_PATH.read_text(encoding="utf-8")
    print(f"[daemon] WARNING: Dynamic tree not found at {TREE_PATH}, using empty tree")
    return "(no dynamic tree yet)"


def build_system_prompt(dna: str) -> str:
    tree = load_dynamic_tree()
    return f"{dna}\n\n---\n\n{tree}"


# Edward AI Server #永生樹
DISCORD_WEBHOOK_TREE = "https://discord.com/api/webhooks/1491644107788128439/Ndafv8puWZKaqHYcp-icHRRWealC0TfrZxO_k9DR1Dj2ANbFx5eyI3Ynvs8M_XO7y3jj"
# DOS organism-edward #thinking
DISCORD_WEBHOOK_DOS = "https://discord.com/api/webhooks/1491656164432412784/lmXONbcP4tIUUsXbP71ACKTilZ6F4FiEwtgUawJWFshAFQletXg9E2xAq5Nxo9XzSRKZ"


QUICK_STATUS_PATH = REPO_ROOT / "staging" / "quick_status.md"


def update_quick_status(cycle: int, mode: str, model: str, interval: int) -> None:
    """Auto-update staging/quick_status.md after each cycle."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M Taipei")
    interval_str = f"{interval}s" if interval > 0 else "immediate (chain)"
    content = f"""# Quick Status — live state snapshot for Type A cold start

> Updated: {ts} (auto-written by daemon cycle {cycle})

## Current state
- daemon: RUNNING (cycle {cycle}, {mode}, {model}, interval {interval_str})
- trading_engine: STOPPED
- last_daemon_cycle: {cycle}
- last_real_work_cycle: {cycle}
- backup_tag: `pre-optimization-backup` → ddc5d88
- web_scheduled: RUNNING (digital-immortality-recursive, hourly)

## Blockers (human-gated)
- mainnet API keys (~88d until 2026-07-07)
- outreach DMs × 5 pending (staging/outreach_week1_execution.md)
- Samuel Turing test invite (human-send)

## Stale-detection
If "Updated" > 6h old, read `results/daemon_log.md` (tail) + `staging/session_state.md` for ground truth.
"""
    QUICK_STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    QUICK_STATUS_PATH.write_text(content, encoding="utf-8")


def append_log(cycle: int, response: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    entry = f"\n## Cycle {cycle} — {ts}\n\n{response}\n"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry)
    # Post to Discord #thinking
    try:
        import requests
        utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        msg = f"[daemon cycle {cycle} | {utc_now}] {response[:1850]}"
        payload = {"content": msg, "username": "Daemon"}
        requests.post(DISCORD_WEBHOOK_TREE, json=payload, timeout=10)
        requests.post(DISCORD_WEBHOOK_DOS, json=payload, timeout=10)
    except Exception:
        pass  # Discord post is best-effort


def try_git_commit(cycle: int) -> None:
    """Commit changes. Pull --rebase first to avoid conflicts with remote trigger."""
    try:
        subprocess.run(
            ["git", "pull", "--rebase", "origin", "main"],
            cwd=REPO_ROOT, capture_output=True, timeout=30,
        )
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=10,
        )
        if status.stdout.strip():
            subprocess.run(
                ["git", "add", "results/"],
                cwd=REPO_ROOT, capture_output=True, timeout=10,
            )
            msg = f"daemon: cycle {cycle}"
            subprocess.run(
                ["git", "commit", "-m", msg],
                cwd=REPO_ROOT, capture_output=True, timeout=10,
            )
            subprocess.run(
                ["git", "push", "origin", "main"],
                cwd=REPO_ROOT, capture_output=True, timeout=30,
            )
            print(f"[daemon] Committed + pushed (cycle {cycle})")
    except Exception as e:
        print(f"[daemon] Git sync skipped: {e}")


def run_cycle_api(client, system: str, model: str, cycle: int) -> str:
    """Run via Anthropic API (requires ANTHROPIC_API_KEY with credit)."""
    print(f"[daemon] Cycle {cycle} starting (API)...")
    priority = load_priority()
    user_prompt = RECURSIVE_PROMPT
    if priority:
        user_prompt = f"[AUDIT PRIORITY] {priority}\n\n{RECURSIVE_PROMPT}"
    try:
        response = client.messages.create(
            model=model,
            max_tokens=512,
            system=system,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text = response.content[0].text
    except anthropic.RateLimitError as e:
        print(f"[daemon] API rate limited: {e}. Sleeping 3600s.", flush=True)
        time.sleep(3600)
        return f"API rate limited — slept 3600s"
    print(f"[daemon] Cycle {cycle} done — {len(text)} chars")
    return text


def parse_rate_limit_reset(text: str) -> int | None:
    """Extract sleep duration from rate limit messages like 'resets Apr 11, 10am'."""
    pattern = r"(?:hit your limit|rate.limit).*resets?\s+(\w+\s+\d+),?\s*(\d{1,2}(?:am|pm))"
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        # Fallback: any mention of hitting limit without parseable reset time
        if re.search(r"hit your limit|rate.limit", text, re.IGNORECASE):
            return 3600  # default 1 hour backoff
        return None
    month_str, day_str = match.group(1), match.group(2).rstrip(",")
    time_str = match.group(2) if len(match.groups()) >= 2 else match.group(3)
    # Parse target time
    now = datetime.now()
    month_map = {m: i for i, m in enumerate(
        ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}
    month_num = month_map.get(match.group(1).strip()[:3], now.month)
    day_num = int(re.search(r"\d+", day_str).group())
    hour_match = re.search(r"(\d+)(am|pm)", time_str, re.IGNORECASE)
    if hour_match:
        hour = int(hour_match.group(1))
        if hour_match.group(2).lower() == "pm" and hour != 12:
            hour += 12
        elif hour_match.group(2).lower() == "am" and hour == 12:
            hour = 0
    else:
        hour = 10  # default
    # Build target datetime (Asia/Taipei = UTC+8)
    target = now.replace(month=month_num, day=day_num, hour=hour, minute=0, second=0, microsecond=0)
    if target <= now:
        return 3600  # already past, wait 1 hour as safety
    sleep_secs = int((target - now).total_seconds()) + 60  # +1min buffer
    return min(sleep_secs, 86400)  # cap at 24h


def run_cycle_cli(prompt: str, model: str, cycle: int) -> str:
    """Run via claude CLI (uses Max subscription, no API credit needed)."""
    print(f"[daemon] Cycle {cycle} starting (CLI)...", flush=True)
    # Minimal prompt — daemon reads ALL context from repo files, not from CLI args
    short_prompt = "Read SKILL.md, results/dynamic_tree.md, results/daemon_next_priority.txt. Priority: economic/outreach first, then strategy dev (design/backtest only, no trade execution), then content. Backward check last 3 daemon log entries for undelivered items. Produce at least one file change. Commit."
    result = subprocess.run(
        ["claude", "-p", short_prompt, "--model", model],
        capture_output=True, text=True, timeout=600,
        cwd=str(REPO_ROOT),
        encoding="utf-8", errors="replace",
    )
    text = result.stdout.strip() if result.stdout else ""
    if result.returncode != 0 and not text:
        text = f"CLI error: {(result.stderr or '').strip()}"
    # Detect rate limit and sleep until reset
    sleep_secs = parse_rate_limit_reset(text)
    if sleep_secs is not None:
        from datetime import timedelta
        reset_time = datetime.now() + timedelta(seconds=sleep_secs)
        print(f"[daemon] Rate limited. Sleeping {sleep_secs}s until ~{reset_time.strftime('%Y-%m-%d %H:%M')}", flush=True)
        time.sleep(sleep_secs)
        text = f"Rate limited — slept {sleep_secs}s until {reset_time.strftime('%Y-%m-%d %H:%M')}"
    print(f"[daemon] Cycle {cycle} done — {len(text)} chars", flush=True)
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
    parser.add_argument("--once", action="store_true",
                        help="Run exactly one cycle then exit (for GH Actions chained mode)")
    args = parser.parse_args()

    dna = load_dna()
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
    print(f"[daemon] DNA: {len(dna)} chars loaded")
    print(f"[daemon] Log: {LOG_PATH}")
    print(f"[daemon] Ctrl+C to stop\n")

    # --once forces exactly one cycle then exit (for GH Actions chained mode)
    if args.once:
        max_cycles_effective = 1
    else:
        max_cycles_effective = args.max_cycles

    while running:
        cycle += 1
        if max_cycles_effective and cycle > max_cycles_effective:
            print(f"[daemon] Reached max cycles ({max_cycles_effective}), stopping.")
            break
        try:
            system = build_system_prompt(dna)
            if use_cli:
                text = run_cycle_cli(system, args.model, cycle)
            else:
                text = run_cycle_api(client, system, args.model, cycle)
            append_log(cycle, text)
            update_quick_status(cycle, mode, args.model, interval)
            subprocess.run([sys.executable, str(REPO_ROOT / "platform" / "generate_dashboard_state.py")], cwd=REPO_ROOT, capture_output=True, timeout=30)
            # Phase 2 pull-model dashboard (build + render). Failures must not kill daemon cycles.
            subprocess.run(
                [sys.executable, str(REPO_ROOT / "platform" / "build_dashboard.py")],
                cwd=REPO_ROOT, capture_output=True, timeout=30, check=False,
            )
            subprocess.run(
                [sys.executable, str(REPO_ROOT / "platform" / "render_dashboard.py")],
                cwd=REPO_ROOT, capture_output=True, timeout=30, check=False,
            )
            run_audit_suggest()
            if not args.no_commit:
                try_git_commit(cycle)
            # Self-derive next task at END of cycle — eliminates "wait for
            # Edward" failure mode. Runs after commit so the queue file is
            # captured in the next cycle's push.
            run_idle_task_picker(cycle)
        except Exception as e:
            print(f"[daemon] Error: {e}, retrying in 30s...")
            time.sleep(30)
            continue

        if args.once:
            print("[daemon] --once flag set, exiting after single cycle.")
            break

        if running and interval > 0:
            time.sleep(interval)

    print("[daemon] Shutdown complete.")


if __name__ == "__main__":
    main()
