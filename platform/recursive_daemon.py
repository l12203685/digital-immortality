"""
Recursive Engine Daemon — Digital Immortality Platform

4-step structured cycle protocol: GATHER → PLAN → EXECUTE → PERSIST.
Continuously runs the recursive question against Claude API,
persists results, and optionally commits code changes.
"""

import argparse
import json
import os
import re
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

TPE = ZoneInfo("Asia/Taipei")

import anthropic

from cycle_protocol import CycleState, CyclePlan, parse_cycle_plan
from branch_executors import BRANCH_EXECUTORS
from knowledge_digester import KnowledgeDigester

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
LAST_OUTPUT_PATH = REPO_ROOT / "staging" / "last_output.md"
VOICE_INPUT_PATH = Path("C:/Users/admin/GoogleDrive/staging/voice_input.md")
_DNA_CORE_PATH = Path("C:/Users/admin/LYH/agent/dna_core.md")
CYCLE_COUNTER_PATH = REPO_ROOT / "results" / "cycle_counter.json"

# Timestamp for voice file watcher (tracks last check time across cycles)
_last_voice_check: float = 0.0

# ---------------------------------------------------------------------------
# Plan-step system prompt: asks LLM to output structured JSON
# ---------------------------------------------------------------------------
PLAN_SYSTEM_PROMPT = (
    "You are the 永生樹 recursive planner. Given the current state, output a JSON plan.\n"
    'Format: {"branch_actions": [{"branch": 1, "name": "經濟", "action": "...", '
    '"priority": 1, "runnable": "script"}], '
    '"tree_updates": [{"branch": 1, "field": "key_metric", "value": "..."}], '
    '"classification": "root-growth|branch-growth|neither"}\n'
    "Rules: bias toward inaction on no-edge. Economic branches first. "
    "Check if the last 3 cycles repeated the same action — if so, try a different branch."
)

# ---------------------------------------------------------------------------
# Cycle counter helpers
# ---------------------------------------------------------------------------


def read_cycle_counter() -> dict:
    """Read the unified cycle counter, returning defaults if missing."""
    if CYCLE_COUNTER_PATH.exists():
        try:
            return json.loads(CYCLE_COUNTER_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "global_cycle": 0,
        "daemon_cycles": 0,
        "interactive_cycles": 0,
        "last_updated": "",
    }


def increment_cycle_counter() -> int:
    """Increment daemon_cycles and global_cycle, return new global_cycle."""
    data = read_cycle_counter()
    data["global_cycle"] = data.get("global_cycle", 0) + 1
    data["daemon_cycles"] = data.get("daemon_cycles", 0) + 1
    data["last_updated"] = datetime.now(TPE).isoformat(timespec="seconds")
    CYCLE_COUNTER_PATH.parent.mkdir(parents=True, exist_ok=True)
    CYCLE_COUNTER_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return data["global_cycle"]


# ---------------------------------------------------------------------------
# Execute branch actions from a CyclePlan
# ---------------------------------------------------------------------------


def execute_plan_actions(plan: CyclePlan) -> list[dict]:
    """Run branch executors for each action in the plan. Returns results."""
    results: list[dict] = []
    for action in sorted(plan.branch_actions, key=lambda a: a.priority):
        executor = BRANCH_EXECUTORS.get(action.branch)
        if executor is not None and action.runnable == "script":
            try:
                output = executor()
            except Exception as exc:
                output = f"executor error: {exc}"
            results.append({
                "branch": action.branch,
                "name": action.name,
                "output": output,
            })
            print(f"[daemon]   branch {action.branch} ({action.name}): {output[:120]}")
        elif action.runnable == "read-only":
            results.append({
                "branch": action.branch,
                "name": action.name,
                "output": "(read-only, no executor)",
            })
        else:
            results.append({
                "branch": action.branch,
                "name": action.name,
                "output": f"(no executor for branch {action.branch}, runnable={action.runnable})",
            })
    return results


# ---------------------------------------------------------------------------
# Apply tree updates from a CyclePlan to dynamic_tree.md
# ---------------------------------------------------------------------------


def apply_tree_updates(plan: CyclePlan) -> None:
    """Append tree update notes to dynamic_tree.md (lightweight)."""
    if not plan.tree_updates:
        return
    ts = datetime.now(TPE).strftime("%Y-%m-%d %H:%M:%S (Taipei)")
    lines = [f"\n<!-- cycle update {ts} -->"]
    for u in plan.tree_updates:
        lines.append(f"<!-- branch {u.branch} {u.field} = {u.value} -->")
    try:
        with open(TREE_PATH, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    except Exception as exc:
        print(f"[daemon] tree update write failed: {exc}")


# ---------------------------------------------------------------------------
# Extract JSON from LLM response (handles markdown code fences)
# ---------------------------------------------------------------------------


def extract_json_from_response(text: str) -> str:
    """Extract a JSON object from LLM text that may contain markdown fences."""
    # Try to find ```json ... ``` block first
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        return m.group(1)
    # Try to find raw JSON object
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        return m.group(0)
    return text


RECURSIVE_PROMPT_TEMPLATE = (
    "You are Edward's recursive engine. 數位永生 = 持續遞迴 + persist.\n\n"
    "## Previous cycle output\n{last_output}\n\n"
    "## Current tree state\n{tree_state}\n\n"
    "## Voice input\n{voice_input}\n\n"
    "Given this state, what advances 數位永生?\n"
    "Classify your action: root-growth (本質萃取) or branch-growth (存活系統) or neither.\n\n"
    "Priority order:\n"
    "1. ECONOMIC / OUTREACH — consulting pipeline, client DMs, revenue tasks.\n"
    "2. STRATEGY DEVELOPMENT — design or refine strategies, write or update backtests. "
    "Do NOT execute trades; the trading engine handles that.\n"
    "3. CONTENT / KNOWLEDGE — publish an insight, update a doc, distill a learning.\n"
    "4. DNA CALIBRATION — only if decision drift detected or boot tests failing.\n\n"
    "Backward check: read results/daemon_log.md (last 3 entries). "
    "What was planned but not delivered? Fix that first.\n\n"
    "Rules: produce at least one file change per cycle. "
    "No monitoring. No 'no change'. learn = write. "
    "遞迴 + persist = 演化。遞迴 - persist = 自言自語。"
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


def run_finance_dashboards(cycle: int, every: int = 4) -> None:
    """Rebuild Edward's 3 finance dashboards every ``every`` cycles.

    Uses ``platform/build_finance_dashboards.py`` which has its own 1h cache,
    so calling more often is harmless. Non-fatal.
    """
    if cycle % every != 0:
        return
    try:
        result = subprocess.run(
            ["python", "platform/build_finance_dashboards.py"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            print(f"[daemon] finance dashboards refreshed (cycle {cycle})")
        else:
            print(f"[daemon] finance dashboards failed cycle {cycle}: "
                  f"{result.stderr[-200:]}")
    except Exception as exc:  # pragma: no cover - defensive
        print(f"[daemon] finance dashboards error cycle {cycle}: {exc}")


ENGINE_RULES_PATH = REPO_ROOT / "results" / "engine_rules.json"
DAEMON_NEXT_PRIORITY_PATH = REPO_ROOT / "results" / "daemon_next_priority.txt"


def _text_similarity(a: str, b: str) -> float:
    """Compute a simple Jaccard similarity between two texts (word-level).

    Returns a float in [0.0, 1.0]. 1.0 = identical word sets.
    Non-fatal: returns 0.0 on any error.
    """
    try:
        words_a = set(a.lower().split())
        words_b = set(b.lower().split())
        if not words_a or not words_b:
            return 0.0
        intersection = words_a & words_b
        union = words_a | words_b
        return len(intersection) / len(union)
    except Exception:
        return 0.0


def run_l3_check() -> None:
    """L3 self-modification check: diagnose and auto-correct engine rules.

    Detects three conditions:
      - DEAD_LOOP:      last N cycles produced near-identical output
      - QUEUE_EMPTY:    no picker_queue entries in recent cycles
      - COMMIT_DROUGHT: zero git commits in recent cycle window

    All actions are non-destructive and wrapped in try/except.
    """
    ts_now = datetime.now(TPE).isoformat(timespec="seconds")
    findings: list[str] = []
    actions_taken: list[str] = []

    # ── Load engine_rules.json ───────────────────────────────────────────
    rules: dict = {}
    try:
        if ENGINE_RULES_PATH.exists():
            rules = json.loads(ENGINE_RULES_PATH.read_text(encoding="utf-8"))
        else:
            print("[L3] engine_rules.json not found — creating defaults")
            rules = {
                "stale_threshold": 3,
                "queue_min": 1,
                "commit_drought_threshold": 3,
                "dead_loop_count": 0,
                "last_dead_loop": {},
                "last_recovery": {"cycle": None, "action": None, "ts": None},
                "evolved_at": ts_now,
                "initialized_at_cycle": 0,
                "evolution_log": [],
            }
    except Exception as e:
        print(f"[L3] Failed to read engine_rules.json: {e}")
        return

    stale_threshold = rules.get("stale_threshold", 3)
    queue_min = rules.get("queue_min", 1)
    commit_drought_threshold = rules.get("commit_drought_threshold", 3)

    # ── Read current cycle number ────────────────────────────────────────
    cycle_data = read_cycle_counter()
    current_cycle = cycle_data.get("global_cycle", 0)

    # ── Read daemon_log.md tail (last 20 lines) ─────────────────────────
    daemon_log_tail = ""
    try:
        if LOG_PATH.exists():
            lines = LOG_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
            daemon_log_tail = "\n".join(lines[-20:])
    except Exception as e:
        print(f"[L3] Failed to read daemon_log.md: {e}")

    # ── Read last_output.md ──────────────────────────────────────────────
    last_output = ""
    try:
        if LAST_OUTPUT_PATH.exists():
            last_output = LAST_OUTPUT_PATH.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"[L3] Failed to read last_output.md: {e}")

    # ── Condition 1: DEAD_LOOP ───────────────────────────────────────────
    #    Check if last_output is near-identical to daemon_log tail
    try:
        similarity = _text_similarity(last_output, daemon_log_tail)
        if similarity > 0.85 and len(last_output.strip()) > 50:
            findings.append(
                f"DEAD_LOOP: last_output similarity to daemon_log tail = "
                f"{similarity:.2f} (threshold 0.85)"
            )
            # Increment dead_loop_count
            rules["dead_loop_count"] = rules.get("dead_loop_count", 0) + 1
            rules["last_dead_loop"] = {
                "cycle": current_cycle,
                "stale_cycles": stale_threshold,
                "similarity": round(similarity, 3),
                "ts": ts_now,
            }
            # Write recovery note to staging/last_output.md
            try:
                recovery_note = (
                    f"# L3 DEAD_LOOP Recovery — Cycle {current_cycle}\n\n"
                    f"L3 DEAD_LOOP detected (similarity={similarity:.2f}) — "
                    f"inject variation: try a different branch next cycle.\n"
                    f"Dead loop count: {rules['dead_loop_count']}\n"
                    f"Timestamp: {ts_now}\n"
                )
                LAST_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
                LAST_OUTPUT_PATH.write_text(recovery_note, encoding="utf-8")
                actions_taken.append("DEAD_LOOP: wrote recovery note to staging/last_output.md")
            except Exception as e:
                actions_taken.append(f"DEAD_LOOP: failed to write recovery note: {e}")
        else:
            findings.append(
                f"DEAD_LOOP: OK (similarity={similarity:.2f}, below 0.85)"
            )
    except Exception as e:
        findings.append(f"DEAD_LOOP: check failed — {e}")

    # ── Condition 2: QUEUE_EMPTY ─────────────────────────────────────────
    #    Check if picker_queue.jsonl has entries from recent cycles
    try:
        queue_entries_recent = 0
        if PICKER_QUEUE_PATH.exists():
            queue_lines = PICKER_QUEUE_PATH.read_text(
                encoding="utf-8", errors="replace"
            ).strip().splitlines()
            # Count entries from the last queue_min worth of cycles
            for line in reversed(queue_lines):
                try:
                    entry = json.loads(line)
                    entry_cycle = entry.get("cycle", 0)
                    if current_cycle - entry_cycle <= queue_min:
                        queue_entries_recent += 1
                except (json.JSONDecodeError, TypeError):
                    continue
        if queue_entries_recent == 0:
            findings.append(
                f"QUEUE_EMPTY: no picker_queue entries in last "
                f"{queue_min} cycle(s)"
            )
            # Write suggestion to daemon_next_priority.txt
            try:
                suggestion = (
                    f"[L3 cycle {current_cycle}] Queue empty — "
                    f"idle task picker should re-scan for runnable tasks.\n"
                )
                DAEMON_NEXT_PRIORITY_PATH.parent.mkdir(parents=True, exist_ok=True)
                DAEMON_NEXT_PRIORITY_PATH.write_text(suggestion, encoding="utf-8")
                actions_taken.append(
                    "QUEUE_EMPTY: wrote re-scan suggestion to "
                    "results/daemon_next_priority.txt"
                )
            except Exception as e:
                actions_taken.append(f"QUEUE_EMPTY: failed to write suggestion: {e}")
        else:
            findings.append(
                f"QUEUE_EMPTY: OK ({queue_entries_recent} recent entries)"
            )
    except Exception as e:
        findings.append(f"QUEUE_EMPTY: check failed — {e}")

    # ── Condition 3: COMMIT_DROUGHT ──────────────────────────────────────
    #    Check git log for recent commits
    try:
        # Estimate time window: commit_drought_threshold cycles * ~10 min each
        hours = max(1, commit_drought_threshold)
        result = subprocess.run(
            ["git", "log", f"--since={hours} hours ago", "--oneline"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=10,
            encoding="utf-8",
            errors="replace",
        )
        commit_count = len(result.stdout.strip().splitlines()) if result.stdout.strip() else 0
        if commit_count == 0:
            findings.append(
                f"COMMIT_DROUGHT: 0 commits in last {hours}h "
                f"(threshold={commit_drought_threshold})"
            )
            actions_taken.append(
                "COMMIT_DROUGHT: logged warning (no destructive action)"
            )
        else:
            findings.append(
                f"COMMIT_DROUGHT: OK ({commit_count} commits in last {hours}h)"
            )
    except Exception as e:
        findings.append(f"COMMIT_DROUGHT: check failed — {e}")

    # ── Log to evolution_log ─────────────────────────────────────────────
    if "evolution_log" not in rules:
        rules["evolution_log"] = []
    rules["evolution_log"].append({
        "cycle": current_cycle,
        "event": "L3_CHECK",
        "findings": findings,
        "actions_taken": actions_taken,
        "ts": ts_now,
    })

    # ── Save engine_rules.json ───────────────────────────────────────────
    try:
        ENGINE_RULES_PATH.parent.mkdir(parents=True, exist_ok=True)
        ENGINE_RULES_PATH.write_text(
            json.dumps(rules, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except Exception as e:
        print(f"[L3] Failed to save engine_rules.json: {e}")

    # ── Print summary ────────────────────────────────────────────────────
    print(f"\n[L3] Self-modification check — cycle {current_cycle} — {ts_now}")
    print(f"[L3] Findings ({len(findings)}):")
    for f in findings:
        print(f"  - {f}")
    if actions_taken:
        print(f"[L3] Actions taken ({len(actions_taken)}):")
        for a in actions_taken:
            print(f"  - {a}")
    else:
        print("[L3] No corrective actions needed.")
    print()


def run_knowledge_digestion(cycle: int, client=None, model: str = DEFAULT_MODEL) -> None:
    """Digest one file per cycle from the E: knowledge base. Non-fatal."""
    try:
        digester = KnowledgeDigester()
        # Initialize on first run (sets total_files_known)
        if digester.state.get("total_files_known", 0) == 0:
            total = digester.initialize()
            print(f"[daemon] Knowledge digester initialized: {total} files found")

        next_file = digester.next_file()
        if next_file is None:
            print(f"[daemon] Knowledge digestion: no more files to digest")
            return

        # Read file content (truncate large files)
        try:
            content = next_file.read_text(encoding="utf-8", errors="replace")
            if len(content) > 4000:
                content = content[:4000] + "\n...(truncated)"
        except Exception as e:
            digester.mark_complete(next_file, f"read error: {e}")
            print(f"[daemon] Knowledge digestion: read error for {next_file}: {e}")
            return

        # Use LLM to extract insights (if API client available)
        summary = ""
        if client is not None:
            try:
                resp = client.messages.create(
                    model=model,
                    max_tokens=512,
                    system="Extract 1-3 key insights from this file for a trading system developer. Be concise. One line per insight.",
                    messages=[{"role": "user", "content": f"File: {next_file.name}\n\n{content}"}],
                )
                summary = resp.content[0].text
            except Exception as e:
                summary = f"LLM extraction failed: {e}"
        else:
            # CLI fallback: just record file metadata as summary
            summary = f"[no-llm] {next_file.name} ({len(content)} chars, tier {digester.state.get('current_tier', '?')})"

        digester.mark_complete(next_file, summary)

        # Write insights to memory/insights.json (append)
        insights_path = REPO_ROOT / "memory" / "insights.json"
        insights_path.parent.mkdir(parents=True, exist_ok=True)
        insights = []
        if insights_path.exists():
            try:
                insights = json.loads(insights_path.read_text(encoding="utf-8"))
            except Exception:
                insights = []
        insights.append({
            "file": str(next_file),
            "summary": summary[:500],
            "timestamp": datetime.now(TPE).isoformat(timespec="seconds"),
            "cycle": cycle,
        })
        insights_path.write_text(
            json.dumps(insights, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        print(f"[daemon] Knowledge digestion cycle {cycle}: {next_file.name} → {len(summary)} char summary")
        print(f"[daemon] {digester.status()}")

    except Exception as e:
        print(f"[daemon] Knowledge digestion failed (non-fatal): {e}")


def run_sign_off_apply_expired(cycle: int) -> None:
    """Apply expired AUTO sign-off decisions at end of each cycle.

    Non-fatal — failures are swallowed so the daemon loop never dies because
    of a sign-off manager bug. Writes a jsonl log entry for every invocation
    (success or failure) to results/sign_off_log.jsonl.
    """
    log_path = REPO_ROOT / "results" / "sign_off_log.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "cycle": cycle,
        "ts": datetime.now(TPE).strftime("%Y-%m-%d %H:%M:%S (Taipei)"),
        "ts_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),  # intentional UTC for server log
        "ok": False,
        "applied_count": 0,
        "applied_uids": [],
        "error": None,
    }
    try:
        result = subprocess.run(
            [sys.executable, "-m", "tools.sign_off_manager", "--apply-expired"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=15,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode == 0 and result.stdout.strip():
            import json as _json
            try:
                payload = _json.loads(result.stdout.strip())
                entry["ok"] = True
                entry["applied_count"] = payload.get("applied_count", 0)
                entry["applied_uids"] = [
                    d.get("uid") for d in payload.get("applied", [])
                ]
                if entry["applied_count"]:
                    print(f"[daemon] sign_off cycle {cycle}: "
                          f"auto-applied {entry['applied_count']} decision(s)")
            except _json.JSONDecodeError as e:
                entry["error"] = f"json: {e}"
        else:
            entry["error"] = (result.stderr or "non-zero return").strip()[:200]
    except Exception as e:
        entry["error"] = f"exception: {e}"
    try:
        import json as _json
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(_json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


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


def load_last_output() -> str:
    """Load previous cycle's output from staging/last_output.md."""
    if LAST_OUTPUT_PATH.exists():
        text = LAST_OUTPUT_PATH.read_text(encoding="utf-8").strip()
        if text:
            # Truncate to ~2000 chars to keep prompt manageable
            return text[:2000] if len(text) > 2000 else text
    return "(no previous output)"


def load_voice_input() -> str:
    """Check for voice input from Google Drive staging."""
    global _last_voice_check
    try:
        if VOICE_INPUT_PATH.exists() and VOICE_INPUT_PATH.stat().st_mtime > _last_voice_check:
            content = VOICE_INPUT_PATH.read_text(encoding="utf-8").strip()
            _last_voice_check = time.time()
            if content:
                print(f"[daemon] Voice input detected ({len(content)} chars)")
                return content[:1000] if len(content) > 1000 else content
    except Exception as e:
        print(f"[daemon] Voice input check failed (non-fatal): {e}")
    return "(none)"


def build_user_prompt() -> str:
    """Build the full user prompt from live context sources."""
    last_output = load_last_output()
    tree_state = load_dynamic_tree()
    voice_input = load_voice_input()
    return RECURSIVE_PROMPT_TEMPLATE.format(
        last_output=last_output,
        tree_state=tree_state,
        voice_input=voice_input,
    )


def load_dna_core_for_system() -> str:
    """Load dna_core.md content for use as system prompt context."""
    if _DNA_CORE_PATH.exists():
        try:
            return _DNA_CORE_PATH.read_text(encoding="utf-8")
        except Exception:
            pass
    return ""


def build_system_prompt(dna: str) -> str:
    dna_core = load_dna_core_for_system()
    if dna_core:
        return f"{dna}\n\n---\n\n## dna_core.md\n{dna_core}"
    return dna


# Discord webhooks come from environment. Never hardcode.
# See ~/.claude/credentials/README.md for the env var registry.
# Edward AI Server #永生樹
DISCORD_WEBHOOK_TREE = os.environ.get("DISCORD_WEBHOOK_TREE", "")
# DOS organism-edward #thinking
DISCORD_WEBHOOK_DOS = os.environ.get("DISCORD_WEBHOOK_DOS", "")


QUICK_STATUS_PATH = REPO_ROOT / "staging" / "quick_status.md"


def update_quick_status(cycle: int, mode: str, model: str, interval: int) -> None:
    """Auto-update staging/quick_status.md after each cycle."""
    ts = datetime.now(TPE).strftime("%Y-%m-%d %H:%M (Taipei, UTC+8)")
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
    ts = datetime.now(TPE).strftime("%Y-%m-%d %H:%M:%S (Taipei)")
    entry = f"\n## Cycle {cycle} — {ts}\n\n{response}\n"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry)
    # Post to Discord #thinking (best-effort; skipped if webhooks not configured)
    try:
        import requests
        now_tpe = datetime.now(TPE).strftime("%Y-%m-%d %H:%M (Taipei)")
        msg = f"[daemon cycle {cycle} | {now_tpe}] {response[:1850]}"
        payload = {"content": msg, "username": "Daemon"}
        if DISCORD_WEBHOOK_TREE:
            requests.post(DISCORD_WEBHOOK_TREE, json=payload, timeout=10)
        if DISCORD_WEBHOOK_DOS:
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
    """Run the 4-step structured cycle via Anthropic API.

    Step 1 — GATHER:  CycleState.gather() collects all live sources.
    Step 2 — PLAN:    LLM call with PLAN_SYSTEM_PROMPT, returns JSON plan.
    Step 3 — EXECUTE: Run branch executors for planned actions.
    Step 4 — PERSIST: Apply tree updates, write last_output, log.
    """
    global_cycle = increment_cycle_counter()
    print(f"[daemon] Cycle {cycle} (global {global_cycle}) starting (API)...")

    # --- Step 1: GATHER ---
    state = CycleState.gather(REPO_ROOT, global_cycle)
    user_prompt = state.to_prompt()
    print(f"[daemon]   GATHER done — {len(user_prompt)} chars prompt")

    # --- Step 2: PLAN ---
    plan: CyclePlan | None = None
    try:
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=PLAN_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw_text = response.content[0].text
        raw_json = extract_json_from_response(raw_text)
        plan = parse_cycle_plan(raw_json)
        print(
            f"[daemon]   PLAN done — {len(plan.branch_actions)} actions, "
            f"class={plan.classification}"
        )
    except anthropic.RateLimitError as e:
        print(f"[daemon] API rate limited: {e}. Sleeping 3600s.", flush=True)
        time.sleep(3600)
        return f"API rate limited — slept 3600s"
    except (json.JSONDecodeError, KeyError) as e:
        # Plan parsing failed — fall back to raw LLM text as output
        print(f"[daemon]   PLAN parse failed ({e}), using raw text")
        raw_text = raw_text if "raw_text" in dir() else f"Plan parse error: {e}"
        _persist_last_output(raw_text, global_cycle)
        return raw_text

    # --- Step 3: EXECUTE ---
    exec_results = execute_plan_actions(plan)
    exec_summary = "; ".join(
        f"b{r['branch']}({r['name']}): {r['output'][:80]}"
        for r in exec_results
    )
    print(f"[daemon]   EXECUTE done — {len(exec_results)} branches")

    # --- Step 4: PERSIST ---
    apply_tree_updates(plan)
    # Add knowledge digestion status to output
    try:
        dig_status = KnowledgeDigester().status()
    except Exception:
        dig_status = "digester: N/A"
    output_text = (
        f"[cycle {global_cycle}] classification={plan.classification}\n"
        f"actions: {len(plan.branch_actions)}, updates: {len(plan.tree_updates)}\n"
        f"exec: {exec_summary}\n"
        f"digestion: {dig_status}\n"
        f"plan_raw: {raw_text[:500]}"
    )
    _persist_last_output(output_text, global_cycle)
    print(f"[daemon] Cycle {cycle} (global {global_cycle}) done — {len(output_text)} chars")
    return output_text


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
    # Parse target time (Taipei, per Edward's standing rule)
    now = datetime.now(TPE)
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


def _persist_last_output(text: str, cycle: int) -> None:
    """Write cycle output to staging/last_output.md for next cycle's input."""
    try:
        LAST_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        LAST_OUTPUT_PATH.write_text(
            f"# Cycle {cycle} — {datetime.now(TPE).strftime('%Y-%m-%d %H:%M:%S (Taipei)')}\n\n{text}\n",
            encoding="utf-8",
        )
    except Exception as e:
        print(f"[daemon] Failed to persist last_output.md: {e}")


def run_cycle_cli(prompt: str, model: str, cycle: int) -> str:
    """Run the 4-step structured cycle via claude CLI.

    Step 1 — GATHER:  CycleState.gather() collects all live sources.
    Step 2 — PLAN:    CLI call with PLAN_SYSTEM_PROMPT, returns JSON plan.
    Step 3 — EXECUTE: Run branch executors for planned actions.
    Step 4 — PERSIST: Apply tree updates, write last_output, log.
    """
    global_cycle = increment_cycle_counter()
    print(f"[daemon] Cycle {cycle} (global {global_cycle}) starting (CLI)...", flush=True)

    # --- Step 1: GATHER ---
    state = CycleState.gather(REPO_ROOT, global_cycle)
    user_prompt = state.to_prompt()
    print(f"[daemon]   GATHER done — {len(user_prompt)} chars prompt", flush=True)

    # --- Step 2: PLAN ---
    cli_prompt = (
        f"{PLAN_SYSTEM_PROMPT}\n\n{user_prompt}\n\n"
        "Respond ONLY with valid JSON matching the format above."
    )
    result = subprocess.run(
        ["claude", "-p", cli_prompt, "--model", model],
        capture_output=True, text=True, timeout=600,
        cwd=str(REPO_ROOT),
        encoding="utf-8", errors="replace",
    )
    raw_text = result.stdout.strip() if result.stdout else ""
    if result.returncode != 0 and not raw_text:
        raw_text = f"CLI error: {(result.stderr or '').strip()}"

    # Detect rate limit and sleep until reset
    sleep_secs = parse_rate_limit_reset(raw_text)
    if sleep_secs is not None:
        from datetime import timedelta
        reset_time = datetime.now(TPE) + timedelta(seconds=sleep_secs)
        reset_str = reset_time.strftime('%Y-%m-%d %H:%M (Taipei)')
        print(f"[daemon] Rate limited. Sleeping {sleep_secs}s until ~{reset_str}", flush=True)
        time.sleep(sleep_secs)
        text = f"Rate limited — slept {sleep_secs}s until {reset_str}"
        _persist_last_output(text, global_cycle)
        return text

    plan: CyclePlan | None = None
    try:
        raw_json = extract_json_from_response(raw_text)
        plan = parse_cycle_plan(raw_json)
        print(
            f"[daemon]   PLAN done — {len(plan.branch_actions)} actions, "
            f"class={plan.classification}",
            flush=True,
        )
    except (json.JSONDecodeError, KeyError) as e:
        print(f"[daemon]   PLAN parse failed ({e}), using raw text", flush=True)
        _persist_last_output(raw_text, global_cycle)
        return raw_text

    # --- Step 3: EXECUTE ---
    exec_results = execute_plan_actions(plan)
    exec_summary = "; ".join(
        f"b{r['branch']}({r['name']}): {r['output'][:80]}"
        for r in exec_results
    )
    print(f"[daemon]   EXECUTE done — {len(exec_results)} branches", flush=True)

    # --- Step 4: PERSIST ---
    apply_tree_updates(plan)
    # Add knowledge digestion status to output
    try:
        dig_status = KnowledgeDigester().status()
    except Exception:
        dig_status = "digester: N/A"
    output_text = (
        f"[cycle {global_cycle}] classification={plan.classification}\n"
        f"actions: {len(plan.branch_actions)}, updates: {len(plan.tree_updates)}\n"
        f"exec: {exec_summary}\n"
        f"digestion: {dig_status}\n"
        f"plan_raw: {raw_text[:500]}"
    )
    _persist_last_output(output_text, global_cycle)
    print(
        f"[daemon] Cycle {cycle} (global {global_cycle}) done — "
        f"{len(output_text)} chars",
        flush=True,
    )
    return output_text


def _print_status() -> None:
    """Print daemon health status and exit."""
    ts = datetime.now(TPE).strftime("%Y-%m-%d %H:%M:%S (Taipei)")
    print(f"[daemon status] {ts}")
    print(f"  REPO_ROOT:    {REPO_ROOT}")
    # last_output.md
    if LAST_OUTPUT_PATH.exists():
        mtime = datetime.fromtimestamp(LAST_OUTPUT_PATH.stat().st_mtime, tz=TPE)
        size = LAST_OUTPUT_PATH.stat().st_size
        print(f"  last_output:  {size:,} bytes, modified {mtime.strftime('%Y-%m-%d %H:%M (Taipei)')}")
    else:
        print("  last_output:  MISSING")
    # dynamic_tree.md
    if TREE_PATH.exists():
        size = TREE_PATH.stat().st_size
        print(f"  dynamic_tree: {size:,} bytes ({size/1024:.1f} KB)")
    else:
        print("  dynamic_tree: MISSING")
    # daemon_log.md
    if LOG_PATH.exists():
        size = LOG_PATH.stat().st_size
        print(f"  daemon_log:   {size:,} bytes")
    else:
        print("  daemon_log:   MISSING")
    # DNA
    dna = load_dna()
    print(f"  DNA loaded:   {len(dna):,} chars")
    # dna_core.md
    dna_core = load_dna_core_for_system()
    print(f"  dna_core:     {len(dna_core):,} chars" if dna_core else "  dna_core:     NOT FOUND")
    # voice input
    if VOICE_INPUT_PATH.exists():
        size = VOICE_INPUT_PATH.stat().st_size
        print(f"  voice_input:  {size:,} bytes at {VOICE_INPUT_PATH}")
    else:
        print(f"  voice_input:  not present at {VOICE_INPUT_PATH}")
    # priority
    priority = load_priority()
    print(f"  priority:     {priority[:100]}..." if priority else "  priority:     (none)")
    print("  status:       READY (not running)")


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
    parser.add_argument("--status", action="store_true",
                        help="Print daemon health status and exit")
    parser.add_argument("--l3-check", action="store_true",
                        help="Run L3 self-modification check and exit")
    args = parser.parse_args()

    # --status: print health check and exit
    if args.status:
        _print_status()
        return

    # --l3-check: run self-modification check and exit
    if args.l3_check:
        run_l3_check()
        return

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
            # Auto sign-off: apply any expired AUTO decisions. Non-fatal.
            run_sign_off_apply_expired(cycle)
            # Finance dashboards (localhost Mission Control). Every 4 cycles.
            run_finance_dashboards(cycle, every=4)
            # Knowledge digestion — one file per cycle (non-fatal)
            run_knowledge_digestion(cycle, client=client, model=args.model)
            # L3 self-modification check — every 5 cycles to avoid overhead
            if cycle % 5 == 0:
                try:
                    run_l3_check()
                except Exception as e:
                    print(f"[daemon] L3 check failed (non-fatal): {e}")
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
