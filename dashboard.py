#!/usr/bin/env python3
"""
dashboard.py — Digital Immortality CLI Health Dashboard

Shows all system metrics in one view.
Usage:
  python dashboard.py           # single snapshot
  python dashboard.py --json    # output as JSON
  python dashboard.py --watch   # refresh every 30s
"""

import json
import os
import sys
import time
import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent
RESULTS = REPO_ROOT / "results"
MEMORY = REPO_ROOT / "memory"
STAGING = REPO_ROOT / "staging"
PLATFORM_EXPORTS = REPO_ROOT / "platform" / "exports"

# ---------------------------------------------------------------------------
# ANSI colour helpers
# ---------------------------------------------------------------------------
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
RED     = "\033[31m"
CYAN    = "\033[36m"
WHITE   = "\033[37m"
MAGENTA = "\033[35m"
BLUE    = "\033[34m"

def ok(msg):    return f"{GREEN}[OK]  {RESET}{msg}"
def warn(msg):  return f"{YELLOW}[WARN]{RESET}{msg}"
def err(msg):   return f"{RED}[ERR] {RESET}{msg}"
def info(msg):  return f"{CYAN}[INFO]{RESET}{msg}"

def section(title):
    width = 60
    bar = "─" * width
    return f"\n{BOLD}{CYAN}{bar}{RESET}\n{BOLD}  {title}{RESET}\n{CYAN}{bar}{RESET}"

# ---------------------------------------------------------------------------
# Safe file utilities
# ---------------------------------------------------------------------------

def read_json(path):
    """Return parsed JSON or None on any error."""
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def read_lines(path):
    """Return list of lines or [] on any error."""
    try:
        with open(path) as f:
            return f.readlines()
    except (FileNotFoundError, OSError):
        return []


def file_exists(path):
    return Path(path).exists()


def dir_exists(path):
    return Path(path).is_dir()

# ---------------------------------------------------------------------------
# Metric collectors
# ---------------------------------------------------------------------------

def collect_boot_test():
    """Read results/example_dna_boot_tests.json.
    The file is a scenario template (no pass/fail flags).
    Cross-reference with consistency_baseline.json for actual alignment.
    """
    data = {}

    # Primary: try consistency_baseline (has actual run results)
    baseline = read_json(RESULTS / "consistency_baseline.json")
    if baseline:
        meta = baseline.get("meta", {})
        results = baseline.get("results", [])
        total = meta.get("scenario_count", len(results))
        organism = meta.get("organism", "?")
        generated_at = meta.get("generated_at", "")
        # Count non-empty responses as "aligned"
        aligned = sum(
            1 for r in results
            if r.get("deterministic_response") or r.get("aligned")
        )
        data["source"] = "consistency_baseline.json"
        data["organism"] = organism
        data["aligned"] = aligned
        data["total"] = total
        data["pass_rate_pct"] = round(aligned / total * 100) if total else 0
        data["generated_at"] = generated_at
        data["status"] = "ok"
        return data

    # Fallback: just confirm template exists
    template = read_json(RESULTS / "example_dna_boot_tests.json")
    if template:
        scenarios = template.get("scenarios", [])
        data["source"] = "example_dna_boot_tests.json (template only)"
        data["total"] = len(scenarios)
        data["aligned"] = None
        data["pass_rate_pct"] = None
        data["status"] = "template_only"
        return data

    data["status"] = "not_found"
    return data


def collect_export_validation():
    """Check platform/exports/ directory."""
    data = {}
    if not dir_exists(PLATFORM_EXPORTS):
        data["status"] = "not_found"
        data["count"] = 0
        return data

    exports = list(PLATFORM_EXPORTS.iterdir())
    data["count"] = len(exports)
    data["files"] = [p.name for p in exports]
    data["status"] = "ok"

    # Try to find a last-validated timestamp from any JSON file there
    latest_mtime = None
    for p in exports:
        try:
            mtime = p.stat().st_mtime
            if latest_mtime is None or mtime > latest_mtime:
                latest_mtime = mtime
        except OSError:
            pass
    if latest_mtime:
        dt = datetime.datetime.fromtimestamp(latest_mtime, tz=datetime.timezone.utc)
        data["last_modified"] = dt.strftime("%Y-%m-%dT%H:%MZ")
    return data


def collect_cold_start():
    """Read consistency_baseline.json or consistency_scorecard.json."""
    data = {}

    # 1. Cross-instance scorecard (best signal)
    cross = read_json(RESULTS / "cross_instance_scorecard.json")
    if cross:
        summary = cross.get("summary", {})
        inter = cross.get("inter_session_agreement", {})
        # e.g. {'S2_vs_S3': {'agreed': 7, 'total': 7, 'rate': '100%'}}
        pairs = list(inter.values())
        if pairs:
            pair = pairs[0]
            agreed = pair.get("agreed", "?")
            total  = pair.get("total", "?")
            rate   = pair.get("rate", "?")
            data["inter_session"] = f"{agreed}/{total} agreed ({rate})"
        baseline_align = cross.get("baseline_alignment", {})
        # summarise each session
        sessions = []
        for sess, val in baseline_align.items():
            sessions.append(f"{sess}: {val.get('rate','?')}")
        data["baseline_sessions"] = sessions
        data["source"] = "cross_instance_scorecard.json"
        data["status"] = "ok"
        return data

    # 2. Fallback: consistency_scorecard
    scorecard = read_json(RESULTS / "consistency_scorecard.json")
    if scorecard:
        summary = scorecard.get("summary", {})
        llm = summary.get("llm_instance_1", {})
        det = summary.get("deterministic_engine", {})
        data["llm_aligned"]  = f"{llm.get('aligned','?')}/{llm.get('total','?')} ({llm.get('score','?')})"
        data["deterministic"] = f"{det.get('aligned','?')}/{det.get('total','?')} ({det.get('score','?')})"
        data["source"] = "consistency_scorecard.json"
        data["status"] = "ok"
        return data

    # 3. Fallback: consistency_baseline pass rate
    baseline = read_json(RESULTS / "consistency_baseline.json")
    if baseline:
        summ = baseline.get("summary", {})
        total = summ.get("total_scenarios", 0) or len(baseline.get("results", []))
        det_pct = summ.get("baseline_match_rate", None)
        data["total"] = total
        data["baseline_match_rate"] = det_pct
        data["source"] = "consistency_baseline.json"
        data["status"] = "ok"
        return data

    data["status"] = "not_found"
    return data


def collect_memory():
    """Read all four memory JSON files and count entries."""
    data = {}
    categories = ["insights", "corrections", "decisions", "calibration"]
    total = 0
    for cat in categories:
        d = read_json(MEMORY / f"{cat}.json")
        if d is None:
            data[cat] = "not_found"
        else:
            count = len(d.get("entries", []))
            data[cat] = count
            total += count
    data["total"] = total
    data["status"] = "ok"
    return data


def collect_daemon():
    """Check staging/engine.pid and last 5 lines of results/daemon_log.md."""
    data = {}
    pid_path = STAGING / "engine.pid"
    if file_exists(pid_path):
        try:
            pid = pid_path.read_text().strip()
            # Check if process is actually alive
            try:
                os.kill(int(pid), 0)
                data["running"] = True
                data["pid"] = pid
            except (ProcessLookupError, ValueError):
                data["running"] = False
                data["pid"] = pid
                data["note"] = "pid file exists but process not running"
        except OSError:
            data["running"] = False
            data["note"] = "pid file unreadable"
    else:
        data["running"] = False
        data["note"] = "no pid file"

    lines = read_lines(RESULTS / "daemon_log.md")
    last5 = [l.rstrip() for l in lines[-5:] if l.strip()]
    data["log_lines"] = last5
    data["log_total_lines"] = len(lines)
    data["status"] = "ok"
    return data


def collect_trading():
    """Read testnet_log.jsonl and strategy_performance.json."""
    data = {}

    # Testnet log
    testnet_path = RESULTS / "testnet_log.jsonl"
    if file_exists(testnet_path):
        raw_lines = read_lines(testnet_path)
        entries = []
        for line in raw_lines:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        data["testnet_count"] = len(entries)
        if entries:
            last = entries[-1]
            data["last_signal"] = last.get("signal", "?")
            data["last_strategy"] = last.get("strategy", "?")
            data["last_action"] = last.get("action", "?")
            data["last_price"] = last.get("price", "?")
            data["last_ts"] = last.get("ts", "?")
            data["last_pnl"] = last.get("pnl_usdt", "?")
            data["dry_run"] = last.get("dry_run", True)
    else:
        data["testnet_count"] = 0
        data["testnet_status"] = "not_found"

    # Strategy performance
    perf = read_json(RESULTS / "strategy_performance.json")
    if perf:
        data["strategy_performance"] = perf
    else:
        data["strategy_performance"] = None

    # Count backtest files
    backtest_files = list(RESULTS.glob("backtest_*.json"))
    data["backtest_count"] = len(backtest_files)
    if backtest_files:
        newest = max(backtest_files, key=lambda p: p.stat().st_mtime)
        data["latest_backtest"] = newest.name

    data["status"] = "ok"
    return data


def collect_dynamic_tree():
    """Read results/dynamic_tree.md, extract last updated line."""
    data = {}
    tree_path = RESULTS / "dynamic_tree.md"
    if not file_exists(tree_path):
        data["status"] = "not_found"
        return data

    lines = read_lines(tree_path)
    last_updated = None
    for line in lines:
        line_s = line.strip()
        if "最後更新" in line_s or "Last Updated" in line_s:
            # Strip markdown prefix
            last_updated = line_s.lstrip("> ").strip()
            break

    data["last_updated"] = last_updated or "unknown"
    data["total_lines"] = len(lines)
    data["status"] = "ok"
    return data


def collect_staging():
    """Check staging/next_input.md and last_output.md, detect cycle numbers."""
    data = {}
    next_input_path  = STAGING / "next_input.md"
    last_output_path = STAGING / "last_output.md"

    data["next_input_exists"]  = file_exists(next_input_path)
    data["last_output_exists"] = file_exists(last_output_path)

    # Try to extract cycle number from next_input.md header
    ni_lines = read_lines(next_input_path)
    lo_lines = read_lines(last_output_path)

    def _extract_cycle(lines):
        for line in lines[:5]:
            line = line.strip()
            if "cycle" in line.lower() or "Cycle" in line:
                # grab digits
                import re
                nums = re.findall(r'\d+', line)
                if nums:
                    return int(nums[0])
        return None

    data["next_cycle"]  = _extract_cycle(ni_lines)
    data["last_cycle"]  = _extract_cycle(lo_lines)
    data["status"] = "ok"
    return data

# ---------------------------------------------------------------------------
# Render functions
# ---------------------------------------------------------------------------

def render_boot_test(d):
    lines = [section("1. BOOT TEST")]
    if d["status"] == "not_found":
        lines.append(f"  {err('Boot test files not found')}")
    elif d["status"] == "template_only":
        n = d["total"]
        lines.append(f"  {warn(f'Template only — {n} scenarios defined, not yet run')}")
    else:
        pct = d.get("pass_rate_pct", 0)
        aligned = d.get("aligned", "?")
        total   = d.get("total", "?")
        org     = d.get("organism", "?")
        ts      = d.get("generated_at", "")[:16]
        tag = ok if pct == 100 else (warn if pct >= 75 else err)
        lines.append(f"  {tag(f'Aligned: {aligned}/{total} ({pct}%)  organism={org}')}")
        if ts:
            lines.append(f"  {DIM}  Last run: {ts}{RESET}")
        lines.append(f"  {DIM}  Source: {d.get('source','')}{RESET}")
    return "\n".join(lines)


def render_export_validation(d):
    lines = [section("2. EXPORT VALIDATION")]
    if d["status"] == "not_found":
        lines.append(f"  {warn('platform/exports/ not found')}")
    else:
        count = d.get("count", 0)
        tag = ok if count > 0 else warn
        lines.append(f"  {tag(f'{count} export(s) found')}")
        for fname in d.get("files", []):
            lines.append(f"  {DIM}    - {fname}{RESET}")
        if "last_modified" in d:
            lines.append(f"  {DIM}  Last modified: {d['last_modified']}{RESET}")
    return "\n".join(lines)


def render_cold_start(d):
    lines = [section("3. COLD START / CONSISTENCY")]
    if d["status"] == "not_found":
        lines.append(f"  {err('No consistency data found')}")
    else:
        src = d.get("source", "")
        if "inter_session" in d:
            inter = d["inter_session"]
            # parse agreed/total
            try:
                frac = inter.split()[0]
                a, t = frac.split("/")
                tag = ok if int(a) == int(t) else (warn if int(a) / int(t) >= 0.7 else err)
            except Exception:
                tag = info
            lines.append(f"  {tag(f'Inter-session agreement: {inter}')}")
            for sess in d.get("baseline_sessions", []):
                lines.append(f"  {DIM}    {sess}{RESET}")
        elif "llm_aligned" in d:
            llm_val = d["llm_aligned"]
            det_val = d["deterministic"]
            lines.append(f"  {ok(f'LLM aligned:  {llm_val}')}")
            lines.append(f"  {info(f'Deterministic: {det_val}')}")
        elif "total" in d:
            total_s = d["total"]
            rate_s  = d.get("baseline_match_rate", "?")
            lines.append(f"  {info(f'{total_s} scenarios — match rate: {rate_s}')}")
        lines.append(f"  {DIM}  Source: {src}{RESET}")
    return "\n".join(lines)


def render_memory(d):
    lines = [section("4. MEMORY")]
    cats = ["insights", "corrections", "decisions", "calibration"]
    for cat in cats:
        val = d.get(cat, "?")
        if val == "not_found":
            lines.append(f"  {warn(f'{cat:<12}: not found')}")
        else:
            tag = ok if val > 0 else warn
            lines.append(f"  {tag(f'{cat:<12}: {val} entries')}")
    total = d.get("total", 0)
    lines.append(f"  {DIM}  Total memory entries: {total}{RESET}")
    return "\n".join(lines)


def render_daemon(d):
    lines = [section("5. DAEMON")]
    if d.get("running"):
        pid_val = d.get("pid", "?")
        lines.append(f"  {ok(f'Daemon RUNNING  pid={pid_val}')}")
    else:
        note = d.get("note", "stopped")
        lines.append(f"  {warn(f'Daemon NOT running  ({note})')}")

    log_total = d.get("log_total_lines", 0)
    lines.append(f"  {DIM}  daemon_log.md: {log_total} lines{RESET}")
    log_lines = d.get("log_lines", [])
    if log_lines:
        lines.append(f"  {DIM}  Last 5 entries:{RESET}")
        for l in log_lines:
            lines.append(f"  {DIM}    {l[:90]}{RESET}")
    return "\n".join(lines)


def render_trading(d):
    lines = [section("6. TRADING")]
    count = d.get("testnet_count", 0)
    if d.get("testnet_status") == "not_found":
        lines.append(f"  {warn('testnet_log.jsonl not found')}")
    else:
        tag = ok if count > 0 else warn
        lines.append(f"  {tag(f'Testnet log entries: {count}')}")
        if count > 0:
            sig   = d.get("last_signal", "?")
            strat = d.get("last_strategy", "?")
            act   = d.get("last_action", "?")
            price = d.get("last_price", "?")
            ts    = str(d.get("last_ts", "?"))[:19]
            pnl   = d.get("last_pnl", "?")
            dry   = d.get("dry_run", True)
            mode  = "DRY_RUN" if dry else "LIVE"
            sig_tag = ok if sig and sig != 0 else info
            lines.append(f"  {sig_tag(f'Last signal: {sig}  strategy={strat}  action={act}  mode={mode}')}")
            lines.append(f"  {DIM}    price={price}  pnl={pnl} USDT  ts={ts}{RESET}")

    if d.get("strategy_performance"):
        lines.append(f"  {ok('strategy_performance.json: present')}")
    else:
        lines.append(f"  {warn('strategy_performance.json: not found')}")

    bt = d.get("backtest_count", 0)
    if bt > 0:
        latest_bt = d.get("latest_backtest", "")
        lines.append(f"  {info(f'Backtest files: {bt}  (latest: {latest_bt})')}")
    else:
        lines.append(f"  {warn('No backtest files found')}")

    return "\n".join(lines)


def render_dynamic_tree(d):
    lines = [section("7. DYNAMIC TREE")]
    if d["status"] == "not_found":
        lines.append(f"  {err('results/dynamic_tree.md not found')}")
    else:
        lu = d.get("last_updated", "unknown")
        lines.append(f"  {ok(f'Last updated: {lu}')}")
        tl = d.get("total_lines", 0)
        lines.append(f"  {DIM}  File size: {tl} lines{RESET}")
    return "\n".join(lines)


def render_staging(d):
    lines = [section("8. STAGING / RECURSIVE ENGINE")]
    ni = d.get("next_input_exists", False)
    lo = d.get("last_output_exists", False)

    ni_tag = ok if ni else err
    lo_tag = ok if lo else err
    ni_state = "present" if ni else "missing"
    lo_state = "present" if lo else "missing"
    lines.append(f"  {ni_tag(f'next_input.md:  {ni_state}')}")
    lines.append(f"  {lo_tag(f'last_output.md: {lo_state}')}")

    nc = d.get("next_cycle")
    lc = d.get("last_cycle")
    if nc is not None:
        lines.append(f"  {info(f'Current cycle: {nc}')}")
    if lc is not None:
        lines.append(f"  {DIM}  Last completed cycle: {lc}{RESET}")
    return "\n".join(lines)

# ---------------------------------------------------------------------------
# Header / footer
# ---------------------------------------------------------------------------

def render_header():
    now = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        f"\n{BOLD}{MAGENTA}"
        f"╔══════════════════════════════════════════════════════════╗\n"
        f"║        DIGITAL IMMORTALITY — SYSTEM HEALTH DASHBOARD     ║\n"
        f"╚══════════════════════════════════════════════════════════╝"
        f"{RESET}\n"
        f"  {DIM}Generated: {now}{RESET}"
    )


def render_footer(metrics):
    """Compute overall status summary."""
    issues = []
    if metrics["boot_test"]["status"] == "not_found":
        issues.append("boot test not run")
    if metrics["daemon"]["running"] is False:
        issues.append("daemon stopped")
    if metrics["staging"]["next_input_exists"] is False:
        issues.append("staging missing")
    if metrics["export_validation"]["count"] == 0:
        issues.append("no exports")

    bar = "─" * 60
    lines = [f"\n{CYAN}{bar}{RESET}"]
    if issues:
        lines.append(f"  {YELLOW}[WARN] Attention needed: {', '.join(issues)}{RESET}")
    else:
        lines.append(f"  {GREEN}[OK]  All systems nominal{RESET}")
    lines.append(f"{CYAN}{bar}{RESET}\n")
    return "\n".join(lines)

# ---------------------------------------------------------------------------
# Full collect + render pipeline
# ---------------------------------------------------------------------------

def collect_all():
    return {
        "generated_at": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
        "boot_test": collect_boot_test(),
        "export_validation": collect_export_validation(),
        "cold_start": collect_cold_start(),
        "memory": collect_memory(),
        "daemon": collect_daemon(),
        "trading": collect_trading(),
        "dynamic_tree": collect_dynamic_tree(),
        "staging": collect_staging(),
    }


def render_all(metrics):
    parts = [
        render_header(),
        render_boot_test(metrics["boot_test"]),
        render_export_validation(metrics["export_validation"]),
        render_cold_start(metrics["cold_start"]),
        render_memory(metrics["memory"]),
        render_daemon(metrics["daemon"]),
        render_trading(metrics["trading"]),
        render_dynamic_tree(metrics["dynamic_tree"]),
        render_staging(metrics["staging"]),
        render_footer(metrics),
    ]
    return "\n".join(parts)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    args = sys.argv[1:]
    json_mode  = "--json"  in args
    watch_mode = "--watch" in args

    if watch_mode and not json_mode:
        try:
            while True:
                # Clear screen
                print("\033[2J\033[H", end="")
                metrics = collect_all()
                print(render_all(metrics))
                print(f"  {DIM}[watch] next refresh in 30s — Ctrl-C to exit{RESET}\n")
                time.sleep(30)
        except KeyboardInterrupt:
            print("\nDashboard stopped.")
        return

    metrics = collect_all()

    if json_mode:
        # Sanitise: remove non-serialisable values (Path objects etc.)
        print(json.dumps(metrics, indent=2, default=str))
    else:
        print(render_all(metrics))


if __name__ == "__main__":
    main()
