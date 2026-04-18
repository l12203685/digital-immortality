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
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STAGING = ROOT / "staging"
RESULTS = ROOT / "results"
LAST_OUTPUT = STAGING / "last_output.md"
NEXT_INPUT = STAGING / "next_input.md"
DAILY_LOG = RESULTS / "daily_log.md"
PID_FILE = STAGING / "engine.pid"
DAEMON_LOG = RESULTS / "daemon_log.md"
ENGINE_CONFIG = STAGING / "engine_config.json"
L3_LOG = RESULTS / "engine_l3_log.jsonl"

# --- Graceful shutdown machinery ---

_shutdown_requested = False


def _signal_handler(signum, frame):
    """Handle SIGTERM/SIGINT: set flag so current cycle can finish."""
    global _shutdown_requested
    _shutdown_requested = True
    sig_name = signal.Signals(signum).name
    print(f"\n[engine] Received {sig_name} — will exit after current cycle completes.")


def _install_signal_handlers():
    """Install graceful shutdown handlers for SIGTERM and SIGINT."""
    signal.signal(signal.SIGTERM, _signal_handler)
    signal.signal(signal.SIGINT, _signal_handler)

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


def load_engine_config() -> dict:
    """Load mutable engine config from ENGINE_CONFIG. Returns defaults if missing."""
    defaults = {
        "recursive_question": RECURSIVE_QUESTION,
        "l2_trigger_every_n": 5,
        "staleness_threshold": 3,
        "last_l3_run_cycle": 0,
        "l3_notes": [],
    }
    if not ENGINE_CONFIG.exists():
        return defaults
    try:
        data = json.loads(ENGINE_CONFIG.read_text(encoding="utf-8"))
        return {**defaults, **data}
    except (json.JSONDecodeError, OSError):
        return defaults


def save_engine_config(config: dict) -> None:
    """Persist engine config to ENGINE_CONFIG."""
    ensure_dirs()
    ENGINE_CONFIG.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")


def l2_evaluate(cycle: int) -> dict:
    """L2: Evaluate engine quality. Returns a quality report dict.

    Checks:
    - stale_cycles: how long since last_output was updated by LLM
    - recent_git_commits: commits in last 24h (branch activity proxy)
    - insights_count: total insights stored (growth proxy)
    - dead_loop_flag: True if last N cycle log entries are all 'awaiting execution'
    """
    import subprocess
    import re

    report: dict = {
        "cycle": cycle,
        "stale_cycles": 0,
        "recent_git_commits": 0,
        "insights_count": 0,
        "dead_loop_flag": False,
        "verdict": "OK",
    }

    # Stale cycles: compare last_output mtime vs next_input mtime
    if LAST_OUTPUT.exists() and NEXT_INPUT.exists():
        last_mtime = LAST_OUTPUT.stat().st_mtime
        next_mtime = NEXT_INPUT.stat().st_mtime
        if last_mtime < next_mtime:
            report["stale_cycles"] = _estimate_stale_cycles(last_mtime)

    # Git activity in last 24h
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "--since=24 hours ago"],
            capture_output=True, text=True, cwd=ROOT
        )
        report["recent_git_commits"] = len(result.stdout.strip().splitlines()) if result.stdout.strip() else 0
    except Exception:
        pass

    # Insights count from memory
    try:
        counts = memory_manager.list_categories()
        report["insights_count"] = counts.get("insights", 0)
    except Exception:
        pass

    # Dead loop detection: last 10 cycle log entries all "awaiting execution"?
    log = read_file(DAILY_LOG) or ""
    cycle_statuses = re.findall(r'- Status: (.+)', log)
    recent = cycle_statuses[-10:] if len(cycle_statuses) >= 10 else cycle_statuses
    if recent and all(s.strip() == "awaiting execution" for s in recent):
        report["dead_loop_flag"] = True
        report["verdict"] = "DEAD_LOOP"
    elif report["stale_cycles"] >= 5:
        report["verdict"] = "STALE"
    elif report["recent_git_commits"] == 0 and cycle > 5:
        report["verdict"] = "LOW_ACTIVITY"
    else:
        report["verdict"] = "OK"

    return report


def l3_evolve(cycle: int, l2_report: dict) -> dict:
    """L3: Evolve engine rules based on L2 report. Returns updated config.

    Decision rules:
    - DEAD_LOOP: log alert, shorten interval suggestion, flag in config
    - STALE: log warning, note that LLM is not consuming prompts
    - LOW_ACTIVITY: flag for review but no config change
    - OK: no change needed
    """
    config = load_engine_config()
    now = datetime.now(timezone.utc).isoformat()
    verdict = l2_report["verdict"]

    note = {
        "cycle": cycle,
        "ts": now,
        "verdict": verdict,
        "stale_cycles": l2_report["stale_cycles"],
        "git_commits_24h": l2_report["recent_git_commits"],
        "insights_count": l2_report["insights_count"],
        "action": "none",
    }

    if verdict == "DEAD_LOOP":
        note["action"] = "dead_loop_alert"
        _daemon_log(
            f"[L3] DEAD_LOOP detected at cycle {cycle}: "
            f"last 10 cycle entries all 'awaiting execution'. "
            f"Engine is not consuming prompts. Manual intervention required."
        )
    elif verdict == "STALE":
        note["action"] = "stale_alert"
        _daemon_log(
            f"[L3] STALE detected at cycle {cycle}: "
            f"{l2_report['stale_cycles']} cycles since last_output updated. "
            f"LLM session may not be running."
        )
    elif verdict == "LOW_ACTIVITY":
        note["action"] = "low_activity_flag"
        _daemon_log(
            f"[L3] LOW_ACTIVITY at cycle {cycle}: "
            f"0 git commits in 24h, {l2_report['insights_count']} total insights. "
            f"Consider triggering a manual session."
        )
    else:
        note["action"] = "ok"

    # Persist L3 note
    config["last_l3_run_cycle"] = cycle
    config["l3_notes"] = config.get("l3_notes", [])[-19:] + [note]  # keep last 20
    save_engine_config(config)

    # Append to L3 log
    ensure_dirs()
    with open(L3_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(note, ensure_ascii=False) + "\n")

    print(f"[L3] cycle={cycle} verdict={verdict} action={note['action']}")
    return config


def _estimate_stale_cycles(last_output_mtime: float) -> int:
    """Estimate how many cycles have run since last_output.md was updated."""
    log = read_file(DAILY_LOG)
    if not log:
        return 0
    # Count ## Cycle entries in the log (each is a cycle)
    # last_output_mtime is a unix timestamp; we can count log entries after that
    # Simpler: count total cycles - approximate cycles since file was last modified
    from datetime import datetime, timezone
    last_modified = datetime.fromtimestamp(last_output_mtime, tz=timezone.utc)
    # Each "## Cycle N —" entry has a timestamp. Count how many are after last_modified.
    import re
    cycle_timestamps = re.findall(r'## Cycle \d+ — (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z)', log)
    stale = 0
    for ts_str in cycle_timestamps:
        try:
            ts = datetime.strptime(ts_str, "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)
            if ts > last_modified:
                stale += 1
        except ValueError:
            pass
    return stale


def _check_staging_staleness(cycle: int):
    """Warn if last_output.md has not been updated since the previous prompt was written."""
    if not LAST_OUTPUT.exists() or not NEXT_INPUT.exists():
        return  # Nothing to compare yet

    last_output_mtime = LAST_OUTPUT.stat().st_mtime
    next_input_mtime = NEXT_INPUT.stat().st_mtime

    # If last_output was last modified BEFORE next_input was written,
    # the LLM hasn't consumed the prompt and updated the output
    if last_output_mtime < next_input_mtime:
        # Estimate stale cycles by counting how many cycle entries are in daily_log
        # after the last_output timestamp
        stale_cycles = _estimate_stale_cycles(last_output_mtime)
        if stale_cycles >= 3:  # Only alert after 3+ stale cycles (reduce noise)
            msg = (
                f"[STALENESS_ALERT] Cycle {cycle}: staging/last_output.md not updated "
                f"in ~{stale_cycles} cycles — LLM may not be consuming prompts."
            )
            print(f"\n⚠️  {msg}")
            # Append to daemon log
            with open(DAEMON_LOG, "a", encoding="utf-8") as f:
                now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                f.write(f"[{now}] {msg}\n")


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

    cfg = load_engine_config()
    question = cfg.get("recursive_question", RECURSIVE_QUESTION)
    prompt = PROMPT_TEMPLATE.format(
        cycle=cycle,
        timestamp=now,
        previous_output=previous.strip(),
        question=question,
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

    # Check if staging is stale (LLM not consuming prompts)
    _check_staging_staleness(cycle)

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

    # Daemon status
    daemon_pid = _read_pid_file()
    if daemon_pid is not None:
        if _pid_is_alive(daemon_pid):
            print(f"Daemon:       running (PID {daemon_pid})")
        else:
            print(f"Daemon:       stale PID file (PID {daemon_pid} not running)")
    else:
        print("Daemon:       not running")

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


def _write_pid_file():
    """Write current PID to the PID file."""
    ensure_dirs()
    PID_FILE.write_text(str(os.getpid()), encoding="utf-8")


def _remove_pid_file():
    """Remove the PID file if it exists."""
    try:
        PID_FILE.unlink()
    except FileNotFoundError:
        pass


def _read_pid_file() -> int | None:
    """Read PID from the PID file. Returns None if missing or invalid."""
    try:
        text = PID_FILE.read_text(encoding="utf-8").strip()
        return int(text)
    except (FileNotFoundError, ValueError):
        return None


def _pid_is_alive(pid: int) -> bool:
    """Check if a process with the given PID is running."""
    try:
        os.kill(pid, 0)  # signal 0 = existence check, no actual signal sent
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        # Process exists but we can't signal it
        return True


def _daemon_log(message: str):
    """Append a timestamped line to the daemon log."""
    ensure_dirs()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{now}] {message}\n"
    with open(DAEMON_LOG, "a", encoding="utf-8") as f:
        f.write(line)


def run_loop(interval: int = 3600, loop_count: int | None = None):
    """Run the recursive engine in a continuous loop.

    Args:
        interval: Seconds between cycle starts (default 3600 = 1 hour).
        loop_count: If set, exit after this many cycles. None = infinite.
    """
    global _shutdown_requested

    _install_signal_handlers()
    _write_pid_file()

    ensure_dirs()

    # Initialize if no last_output exists
    if not LAST_OUTPUT.exists():
        print("[engine] No last_output.md found — auto-initializing seed state.")
        _daemon_log("Auto-initialized seed state (no last_output.md found).")
        # Use a simple namespace for args.force
        class _InitArgs:
            force = False
        init(_InitArgs())

    cycles_completed = 0
    print(f"[engine] Starting loop: interval={interval}s, loop_count={loop_count or 'infinite'}, PID={os.getpid()}")
    _daemon_log(f"Loop started: interval={interval}s, loop_count={loop_count or 'infinite'}, PID={os.getpid()}")

    try:
        while True:
            if _shutdown_requested:
                print("[engine] Shutdown requested before cycle start — exiting.")
                _daemon_log("Shutdown requested before cycle start — exiting cleanly.")
                break

            cycle = get_cycle_number()
            now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            print(f"\n[engine] === Cycle {cycle} starting at {now} ===")
            _daemon_log(f"Cycle {cycle} starting.")

            # --- Core cycle ---
            # 1. Read last output from staging
            previous = read_file(LAST_OUTPUT)
            if previous is None:
                print("[engine] WARNING: last_output.md disappeared — re-seeding.")
                _daemon_log("WARNING: last_output.md disappeared — re-seeding.")
                LAST_OUTPUT.write_text(SEED_OUTPUT, encoding="utf-8")
                previous = SEED_OUTPUT

            # 2. Generate the recursive prompt (this writes next_input.md,
            #    appends to daily_log, stores memory, and prunes)
            generate_prompt()

            # 3. Update last_output.md with cycle metadata
            cycle_metadata = (
                f"# Cycle {cycle} — Engine Loop Output\n\n"
                f"## Metadata\n"
                f"- Timestamp: {now}\n"
                f"- Mode: auto-loop\n"
                f"- Interval: {interval}s\n"
                f"- Cycles completed: {cycles_completed + 1}\n"
                f"- PID: {os.getpid()}\n\n"
                f"## Previous Output Summary\n"
                f"{previous.strip()[:500]}\n\n"
                f"## Recursive Prompt\n"
                f"The full prompt for this cycle has been written to staging/next_input.md.\n"
                f"An LLM session should consume it and write results back to staging/last_output.md.\n\n"
                f"## Next Cycle\n"
                f"- Focus: Execute the prompt in staging/next_input.md\n"
                f"- The engine will generate the next prompt in {interval}s\n"
            )
            LAST_OUTPUT.write_text(cycle_metadata, encoding="utf-8")

            # 4. Store a memory entry for this loop iteration
            memory_manager.store(
                category="insights",
                key=f"loop-cycle-{cycle}",
                content=(
                    f"Auto-loop cycle {cycle} completed. "
                    f"Prompt generated and staged for LLM execution. "
                    f"Interval: {interval}s."
                ),
                source="recursive-engine-loop",
                tags=["recursive-engine", "auto-loop", f"cycle-{cycle}"],
            )

            cycles_completed += 1
            print(f"[engine] Cycle {cycle} complete. Cycles run: {cycles_completed}")
            _daemon_log(f"Cycle {cycle} complete. Total cycles run: {cycles_completed}.")

            # --- L2 Evaluate + L3 Evolve (every N cycles) ---
            cfg = load_engine_config()
            l2_every = cfg.get("l2_trigger_every_n", 5)
            if cycles_completed % l2_every == 0:
                print(f"[engine] Running L2 evaluate at cycle {cycle}...")
                l2_report = l2_evaluate(cycle)
                print(f"[engine] L2 report: {l2_report}")
                _daemon_log(f"L2 evaluate: verdict={l2_report['verdict']} stale={l2_report['stale_cycles']} commits={l2_report['recent_git_commits']}")
                l3_evolve(cycle, l2_report)

            # Check loop_count limit
            if loop_count is not None and cycles_completed >= loop_count:
                print(f"[engine] Reached loop_count limit ({loop_count}) — exiting.")
                _daemon_log(f"Reached loop_count limit ({loop_count}) — exiting.")
                break

            # --- Wait for next cycle ---
            print(f"[engine] Sleeping {interval}s until next cycle...")
            # Sleep in 1-second increments to allow responsive shutdown
            for _ in range(interval):
                if _shutdown_requested:
                    print("[engine] Shutdown requested during sleep — exiting.")
                    _daemon_log("Shutdown requested during sleep — exiting cleanly.")
                    break
                time.sleep(1)

            if _shutdown_requested:
                break

    finally:
        _remove_pid_file()
        print(f"[engine] Engine stopped. {cycles_completed} cycles completed.")
        _daemon_log(f"Engine stopped. {cycles_completed} cycles completed total.")


def daemonize(interval: int = 3600, loop_count: int | None = None):
    """Fork to background and run the loop as a daemon.

    Uses a double-fork to fully detach from the controlling terminal.
    Writes PID to staging/engine.pid.
    Redirects stdout/stderr to results/daemon_log.md (plain text append).
    """
    ensure_dirs()

    # Check for existing daemon
    existing_pid = _read_pid_file()
    if existing_pid is not None and _pid_is_alive(existing_pid):
        print(f"Engine daemon already running (PID {existing_pid}). Use --stop first.")
        sys.exit(1)

    # First fork — detach from parent
    pid = os.fork()
    if pid > 0:
        # Parent: wait briefly for child to set up, then report
        time.sleep(0.5)
        child_pid = _read_pid_file()
        if child_pid:
            print(f"Engine daemon started (PID {child_pid}).")
            print(f"  PID file: {PID_FILE}")
            print(f"  Log file: {DAEMON_LOG}")
            print(f"  Interval: {interval}s")
            if loop_count:
                print(f"  Loop count: {loop_count}")
            print(f"  Stop with: python {__file__} --stop")
        else:
            print("Daemon forked but PID file not yet written. Check daemon log.")
        sys.exit(0)

    # Child: create new session
    os.setsid()

    # Second fork — prevent zombie and terminal re-acquisition
    pid2 = os.fork()
    if pid2 > 0:
        sys.exit(0)

    # Grandchild: this is the actual daemon process

    # Redirect stdout and stderr to daemon log
    sys.stdout.flush()
    sys.stderr.flush()
    log_fd = os.open(str(DAEMON_LOG), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    os.dup2(log_fd, sys.stdout.fileno())
    os.dup2(log_fd, sys.stderr.fileno())
    # Redirect stdin from /dev/null
    devnull = os.open(os.devnull, os.O_RDONLY)
    os.dup2(devnull, sys.stdin.fileno())
    os.close(devnull)
    os.close(log_fd)

    _daemon_log(f"Daemon process started (PID {os.getpid()}).")

    # Run the loop (this writes PID file internally)
    run_loop(interval=interval, loop_count=loop_count)


def stop_daemon():
    """Stop a running daemon by reading PID file and sending SIGTERM."""
    pid = _read_pid_file()
    if pid is None:
        print(f"No PID file found at {PID_FILE}. Daemon may not be running.")
        sys.exit(1)

    if not _pid_is_alive(pid):
        print(f"PID {pid} is not running. Cleaning up stale PID file.")
        _remove_pid_file()
        return

    print(f"Sending SIGTERM to PID {pid}...")
    try:
        os.kill(pid, signal.SIGTERM)
    except PermissionError:
        print(f"Permission denied sending signal to PID {pid}.", file=sys.stderr)
        sys.exit(1)

    # Wait for process to exit (up to 30 seconds)
    for i in range(30):
        time.sleep(1)
        if not _pid_is_alive(pid):
            print(f"Engine daemon (PID {pid}) stopped.")
            _remove_pid_file()
            return
        if i == 4:
            print("Waiting for current cycle to complete...")

    # Still alive after 30s — report but don't force
    print(f"PID {pid} still running after 30s. It may be mid-cycle.")
    print("The engine will exit after completing the current cycle.")
    print("If it doesn't stop, you can force kill with: kill -9 " + str(pid))


RULES_FILE = RESULTS / "engine_rules.json"
L3_RECOVERY = STAGING / "l3_recovery.md"


def _load_rules() -> dict:
    """Load engine_rules.json or return empty skeleton."""
    if RULES_FILE.exists():
        try:
            return json.loads(RULES_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"evolution_log": [], "evolved_at": None}


def _save_rules(rules: dict) -> None:
    """Persist engine_rules.json."""
    ensure_dirs()
    RULES_FILE.write_text(
        json.dumps(rules, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _read_recent_l3_log(n: int = 10) -> list[dict]:
    """Read last N entries from engine_l3_log.jsonl."""
    if not L3_LOG.exists():
        return []
    entries: list[dict] = []
    try:
        with open(L3_LOG, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    except OSError:
        pass
    return entries[-n:]


def l3_check() -> dict:
    """L3 v2 auto-detection: run full 3-layer audit, detect anomalies, update rules.

    Returns the audit summary dict.
    """
    # Import l3_audit programmatically (sibling tools/ package)
    sys.path.insert(0, str(ROOT / "tools"))
    import l3_audit

    ensure_dirs()
    now_iso = datetime.now(timezone.utc).isoformat()
    cycle = get_cycle_number()

    # 1. Run 3-layer audit
    l1 = l3_audit.audit_l1()
    l2 = l3_audit.audit_l2()
    l3 = l3_audit.audit_l3()
    cross = l3_audit.audit_cross_layer(l1, l2, l3)
    recs = l3_audit.generate_recommendations(l1, l2, l3, cross)

    healths = {"L1": l1["health"], "L2": l2["health"], "L3": l3["health"]}
    has_red = "RED" in healths.values()
    worst = "RED" if has_red else ("YELLOW" if "YELLOW" in healths.values() else "GREEN")

    # 2. Check recent anomalies from l3 log
    recent_log = _read_recent_l3_log(10)
    recent_red_count = sum(
        1 for e in recent_log
        if e.get("verdict") in ("DEAD_LOOP", "STALE") or e.get("worst") == "RED"
    )

    # 3. Build findings list
    findings: list[str] = []
    for layer_name, layer_result in [("L1", l1), ("L2", l2), ("L3", l3)]:
        status = layer_result["health"]
        issues = layer_result.get("issues", [])
        if issues:
            findings.append(f"{layer_name}={status}: {'; '.join(issues)}")
        else:
            findings.append(f"{layer_name}={status}: OK")
    for pipe, status in cross.get("pipelines", {}).items():
        if not pipe.endswith("_detail") and status != "OK":
            findings.append(f"PIPE {pipe}={status}")

    # 4. Auto-detect new rules from anomalies
    actions_taken: list[str] = []
    rules = _load_rules()

    if has_red:
        # Write recovery prompt
        red_layers = [k for k, v in healths.items() if v == "RED"]
        recovery_lines = [
            f"# L3 Recovery Prompt — {now_iso}",
            f"",
            f"Cycle: {cycle}",
            f"RED layers: {', '.join(red_layers)}",
            f"",
            f"## Issues",
        ]
        all_issues = l1["issues"] + l2["issues"] + l3["issues"] + cross.get("issues", [])
        for issue in all_issues:
            recovery_lines.append(f"- {issue}")
        recovery_lines += ["", "## Recommendations"]
        for rec in recs:
            recovery_lines.append(f"- {rec}")
        recovery_lines += [
            "",
            "## Action Required",
            "Address RED layers before next recursive cycle.",
        ]
        L3_RECOVERY.write_text("\n".join(recovery_lines), encoding="utf-8")
        actions_taken.append(f"wrote recovery prompt to {L3_RECOVERY.name}")
        _daemon_log(f"[L3v2] RED detected in {red_layers} — recovery prompt written")

    if recent_red_count >= 3:
        # Tighten staleness threshold if repeated anomalies
        old_thresh = rules.get("stale_threshold", 3)
        new_thresh = max(1, old_thresh - 1)
        if new_thresh != old_thresh:
            rules["stale_threshold"] = new_thresh
            actions_taken.append(f"tightened stale_threshold {old_thresh}->{new_thresh}")

    # 5. Update engine_rules.json evolution_log
    log_entry = {
        "cycle": cycle,
        "event": "L3_CHECK",
        "findings": findings,
        "actions_taken": actions_taken,
        "ts": now_iso,
    }
    evo_log = rules.get("evolution_log", [])
    evo_log.append(log_entry)
    rules["evolution_log"] = evo_log[-50:]  # keep last 50
    rules["evolved_at"] = now_iso
    _save_rules(rules)

    # 6. Append to engine_l3_log.jsonl
    jsonl_entry = {
        "cycle": cycle,
        "ts": now_iso,
        "worst": worst,
        "healths": healths,
        "findings_count": len(findings),
        "actions_taken": actions_taken,
        "recent_red_count": recent_red_count,
    }
    with open(L3_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(jsonl_entry, ensure_ascii=False) + "\n")

    # Print summary
    print(f"[L3v2] cycle={cycle} worst={worst} healths={healths}")
    for f_line in findings:
        print(f"  {f_line}")
    if actions_taken:
        for a in actions_taken:
            print(f"  -> {a}")
    else:
        print("  -> no corrective actions needed")

    return {"cycle": cycle, "worst": worst, "healths": healths, "findings": findings, "actions": actions_taken}


def main():
    parser = argparse.ArgumentParser(
        description="Recursive self-prompt engine for digital immortality.",
        epilog=(
            "Workflow: --init once, then --prompt before each Claude Code session.\n"
            "Auto-scheduling: --loop for continuous cycling, --daemon for background."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--init", action="store_true", help="Create initial seed files")
    group.add_argument("--prompt", action="store_true", help="Generate next cycle prompt")
    group.add_argument("--status", action="store_true", help="Show current engine state")
    group.add_argument("--loop", action="store_true",
                       help="Run continuous cycles with configurable interval (default 3600s)")
    group.add_argument("--daemon", action="store_true",
                       help="Fork to background and run loop (writes PID to staging/engine.pid)")
    group.add_argument("--stop", action="store_true",
                       help="Stop a running daemon (reads PID from staging/engine.pid)")
    group.add_argument("--l2", action="store_true",
                       help="Run L2 evaluate: audit engine quality and report")
    group.add_argument("--l3", action="store_true",
                       help="Run L2 evaluate then L3 evolve: update engine config based on audit")
    group.add_argument("--l3-check", action="store_true",
                       help="L3 v2: run full 3-layer audit, auto-detect anomalies, update rules")
    group.add_argument("--l3-selfmod", action="store_true",
                       help="L3 v2 self-modification: detect DEAD_LOOP/QUEUE_EMPTY/COMMIT_DROUGHT, inject fixes")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files on init")
    parser.add_argument("--interval", type=int, default=3600,
                        help="Seconds between cycles for --loop/--daemon (default: 3600)")
    parser.add_argument("--loop-count", type=int, default=None,
                        help="Max number of cycles for --loop/--daemon (default: unlimited)")

    args = parser.parse_args()

    if args.init:
        init(args)
    elif args.prompt:
        generate_prompt()
    elif args.status:
        show_status()
    elif args.loop:
        run_loop(interval=args.interval, loop_count=args.loop_count)
    elif args.daemon:
        daemonize(interval=args.interval, loop_count=args.loop_count)
    elif args.stop:
        stop_daemon()
    elif args.l2:
        cycle = get_cycle_number()
        report = l2_evaluate(cycle)
        print(json.dumps(report, indent=2))
    elif args.l3:
        cycle = get_cycle_number()
        report = l2_evaluate(cycle)
        print(f"L2 report: {json.dumps(report, indent=2)}")
        updated_config = l3_evolve(cycle, report)
        print(f"L3 config updated: {json.dumps(updated_config, indent=2)}")
    elif args.l3_check:
        result = l3_check()
        print(json.dumps(result, indent=2))
    elif args.l3_selfmod:
        sys.path.insert(0, str(ROOT / "tools"))
        import l3_selfmod
        result = l3_selfmod.run_l3_selfmod()
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
