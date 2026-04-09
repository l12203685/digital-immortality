"""
Generate results/dashboard_state.json from dynamic_tree.md and daemon_log.md.
Standalone: python platform/generate_dashboard_state.py
"""

import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
TREE_PATH = REPO_ROOT / "results" / "dynamic_tree.md"
LOG_PATH = REPO_ROOT / "results" / "daemon_log.md"
OUT_PATH = REPO_ROOT / "results" / "dashboard_state.json"
RESULTS = REPO_ROOT / "results"
MEMORY = REPO_ROOT / "memory"


def read_json(path: Path) -> Any:
    """Read and parse a JSON file, returning None if missing or malformed."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None

DEADLINE = "2026-07-07"

CARD_DEFS = [
    {"name": "經濟", "icon": "\U0001f4b0", "num": 1},
    {"name": "行為", "icon": "\U0001f9e0", "num": 2},
    {"name": "學習", "icon": "\U0001f4da", "num": 3},
    {"name": "社交", "icon": "\U0001f91d", "num": 4},
    {"name": "平台", "icon": "\U0001f4e6", "num": 5},
    {"name": "存活", "icon": "\U0001f6e1\ufe0f", "num": 6},
    {"name": "知識", "icon": "\U0001f4dd", "num": 7},
    {"name": "生活", "icon": "\U0001f3e0", "num": 8},
]


def parse_tree(text: str) -> dict[str, Any]:
    """Extract regime, branches, and stats from dynamic_tree.md."""
    lines = text.split("\n")
    regime = ""
    regime_neutral = ""
    branches: dict[int, dict[str, Any]] = {}
    current_num = 0

    for line in lines:
        # Regime — keep short for dashboard hero
        if line.startswith("攻擊："):
            raw = line.removeprefix("攻擊：").strip()
            # Extract just the key phrase, drop parenthetical details
            regime = re.split(r"[（(;]", raw)[0].strip()[:50]
        if line.startswith("中性："):
            raw = line.removeprefix("中性：").strip()
            regime_neutral = raw[:40]

        # Branch headers: ### N. Title
        bm = re.match(r"^### (\d+)\.\s+(.+)", line)
        if bm:
            current_num = int(bm.group(1))
            branches[current_num] = {"title": bm.group(2), "items": []}
            continue

        # Sub-items
        if current_num and re.match(r"^- \d+\.\d+", line):
            txt = re.sub(r"^- \d+\.\d+\s*", "", line).strip()
            branches[current_num]["items"].append(txt)

    return {
        "regime": regime,
        "regime_neutral": regime_neutral,
        "branches": branches,
    }


CLEAN_STATUS = {
    1: "策略持續開發中",
    2: "330 MDs learned",
    3: "三層遞迴運作中",
    4: "等朋友加入",
    5: "v2.2 deployed",
    6: "冷啟動 <5min",
    7: "43 SOPs ready",
    8: "Calendar maintained",
}

def pick_status(items: list[str], num: int = 0) -> str:
    """Pick a clean, short status. Max 30 chars."""
    # Use predefined clean labels when available
    if num in CLEAN_STATUS:
        return CLEAN_STATUS[num]
    if not items:
        return "No data"
    # Fallback: first clause of last meaningful item, max 30 chars
    for item in reversed(items):
        if "✓" in item or "**" in item:
            clean = re.sub(r"\*\*", "", item)
            clean = re.split(r"[;—(（,]", clean)[0].strip()
            return clean[:30]
    clean = re.sub(r"\*\*", "", items[-1])
    clean = re.split(r"[;—(（,]", clean)[0].strip()
    return clean[:30]


def pick_detail(items: list[str]) -> str:
    """Pick a detail line for the card."""
    if not items:
        return ""
    # Find the most info-dense item
    for item in reversed(items):
        if "✓" in item:
            clean = re.sub(r"\*\*", "", item).strip()
            parts = re.split(r"[;—]", clean)
            if len(parts) > 1:
                return parts[-1].strip()[:60]
            return clean[:60]
    return re.sub(r"\*\*", "", items[-1]).strip()[:60]


def determine_color(title: str, items: list[str]) -> str:
    """Determine card color: red/yellow/green/grey."""
    all_text = title + " " + " ".join(items)
    if "DEADLINE" in all_text or "⚡" in all_text:
        return "red"
    if "blocked" in all_text or "users=0" in all_text or "等" in all_text:
        # Check if mostly done
        done_count = sum(1 for i in items if "✓" in i or "DONE" in i)
        if done_count == 0:
            return "grey"
    done_count = sum(1 for i in items if "✓" in i or "DONE" in i)
    if done_count > 0 and done_count >= len(items) * 0.6:
        return "green"
    return "yellow"


def parse_log_tail(text: str, max_lines: int = 200) -> list[dict[str, str]]:
    """Parse last N lines of daemon_log.md for activity entries."""
    lines = text.strip().split("\n")
    tail = lines[-max_lines:]
    activities: list[dict[str, str]] = []
    current_cycle_ts = ""

    # Forward pass to associate timestamps with content
    cycle_entries: list[dict[str, str]] = []
    for line in tail:
        line = line.strip()
        if not line:
            continue
        # Match cycle headers: ## Cycle N — timestamp
        cm = re.match(r"^## Cycle (\d+) — (.+)", line)
        if cm:
            current_cycle_ts = cm.group(2).strip()
            continue
        # Skip noise
        if "Recalled memories" in line or "Auto-prune" in line:
            continue
        if line.startswith("[engine]") or line.startswith("Cycle ") or line.startswith("Stored cycle"):
            continue
        if re.match(r"^- \[insights\]", line):
            continue
        # Pick up substantive content lines
        if current_cycle_ts and len(line) > 10:
            clean = re.sub(r"\*\*", "", line).strip()
            # Skip lines that are just markdown bullets with timestamps
            if clean.startswith("- MD-"):
                continue
            if len(clean) > 80:
                clean = clean[:77] + "..."
            cycle_entries.append({"time": _relative_time(current_cycle_ts), "text": clean})

    # Take last 5 unique entries
    seen: set[str] = set()
    for entry in reversed(cycle_entries):
        if entry["text"] not in seen:
            seen.add(entry["text"])
            activities.append(entry)
        if len(activities) >= 5:
            break

    return activities


def _relative_time(ts_str: str) -> str:
    """Convert timestamp to relative time string."""
    ts_str = ts_str.strip()
    try:
        # Try parsing "2026-04-08 10:45:00 UTC"
        cleaned = ts_str.replace(" UTC", "").replace("T", " ")
        dt = datetime.strptime(cleaned, "%Y-%m-%d %H:%M:%S")
        dt = dt.replace(tzinfo=timezone.utc)
    except ValueError:
        try:
            cleaned = ts_str.replace(" UTC", "").replace("T", " ")
            dt = datetime.strptime(cleaned, "%Y-%m-%d %H:%M")
            dt = dt.replace(tzinfo=timezone.utc)
        except ValueError:
            return ts_str
    now = datetime.now(timezone.utc)
    diff = now - dt
    minutes = int(diff.total_seconds() / 60)
    if minutes < 1:
        return "just now"
    if minutes < 60:
        return f"{minutes}min ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    return f"{days}d ago"


def collect_health() -> dict[str, Any]:
    """Collect cold-start health signals for the dashboard."""
    health: dict[str, Any] = {}

    # 1. CI pipeline presence
    ci_path = REPO_ROOT / ".github" / "workflows" / "ci.yml"
    health["ci_wired"] = ci_path.exists()

    # 2. Consistency scorecard — alignment rate
    scorecard = read_json(RESULTS / "consistency_scorecard.json")
    if scorecard:
        summary = scorecard.get("summary", {})
        llm = summary.get("llm_instance_1", {})
        health["consistency_aligned"] = llm.get("aligned", "?")
        health["consistency_total"] = llm.get("total", "?")
        health["consistency_score"] = llm.get("score", "?")
    else:
        baseline = read_json(RESULTS / "consistency_baseline.json")
        if baseline:
            results = baseline.get("results", [])
            aligned = sum(1 for r in results if r.get("aligned", False))
            health["consistency_aligned"] = aligned
            health["consistency_total"] = len(results)
            health["consistency_score"] = f"{aligned}/{len(results)}"

    # 3. Paper-live last tick (from paper_live_log.jsonl)
    paper_log = RESULTS / "paper_live_log.jsonl"
    if paper_log.exists():
        lines = [l.strip() for l in paper_log.read_text(encoding="utf-8").splitlines() if l.strip()]
        last_ticks = []
        for line in reversed(lines):
            try:
                entry = json.loads(line)
                if entry.get("action") == "PAPER_LIVE":
                    last_ticks.append(entry)
                    if len(last_ticks) >= 2:
                        break
            except json.JSONDecodeError:
                continue
        if last_ticks:
            latest = last_ticks[0]
            health["paper_live_price"] = latest.get("price")
            health["paper_live_signal"] = latest.get("signal")
            health["paper_live_ts"] = latest.get("ts", "")[:16]
        else:
            health["paper_live_signal"] = "network_fail"

    # 4. Cold start test — read from mainnet paper live PnL report
    pnl_report = RESULTS / "paper_live_pnl_report.md"
    if pnl_report.exists():
        text = pnl_report.read_text(encoding="utf-8")
        # Match "N ticks" pattern (total tick count) or "tick N:" for current tick
        tick_m = re.search(r"(\d+)\s+ticks?\s*[|]", text, re.IGNORECASE)
        if not tick_m:
            tick_m = re.search(r"tick\s+(\d+):", text, re.IGNORECASE)
        pnl_m = re.search(r"P&L[:\s=]*\*?\*?\+?\$?([\d.]+)", text)
        if tick_m:
            health["paper_tick"] = int(tick_m.group(1))
        if pnl_m:
            health["paper_pnl"] = f"+${pnl_m.group(1)}"

    health["status"] = "ok"
    return health


def count_stats(tree_text: str, log_text: str) -> dict[str, int]:
    """Extract stats from the files."""
    # Count MDs from tree
    md_match = re.findall(r"MD-(\d+)", tree_text)
    total_mds = max(int(m) for m in md_match) if md_match else 0

    # Count daemon cycles from log
    cycle_matches = re.findall(r"^## Cycle (\d+)", log_text, re.MULTILINE)
    daemon_cycles = max(int(c) for c in cycle_matches) if cycle_matches else 0

    # dna_core lines — try to read the file
    dna_core = REPO_ROOT.parent.parent / "LYH" / "agent" / "dna_core.md"
    dna_core_lines = 71  # fallback
    if dna_core.exists():
        dna_core_lines = len(dna_core.read_text(encoding="utf-8").strip().split("\n"))
    else:
        # Try templates
        tpl = REPO_ROOT / "templates" / "dna_core.md"
        if tpl.exists():
            dna_core_lines = len(tpl.read_text(encoding="utf-8").strip().split("\n"))

    return {
        "daemon_cycles": daemon_cycles,
        "total_mds": total_mds,
        "dna_core_lines": dna_core_lines,
    }


def generate() -> dict[str, Any]:
    """Generate the full dashboard state JSON."""
    tree_text = TREE_PATH.read_text(encoding="utf-8") if TREE_PATH.exists() else ""
    log_text = LOG_PATH.read_text(encoding="utf-8") if LOG_PATH.exists() else ""

    tree = parse_tree(tree_text)

    # Deadline calculation
    now = datetime.now(timezone.utc)
    deadline_dt = datetime.strptime(DEADLINE, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    days_remaining = max(0, (deadline_dt - now).days)

    # Build cards
    cards: list[dict[str, str]] = []
    for cdef in CARD_DEFS:
        branch = tree["branches"].get(cdef["num"], {"title": "", "items": []})
        items = branch["items"]
        title = branch.get("title", "")
        cards.append({
            "name": cdef["name"],
            "icon": cdef["icon"],
            "status": pick_status(items, cdef["num"]),
            "color": determine_color(title, items),
            "detail": pick_detail(items),
        })

    # Timestamp in Taipei time
    taipei = timezone(timedelta(hours=8))
    updated = now.astimezone(taipei).strftime("%Y-%m-%dT%H:%M+08")

    state: dict[str, Any] = {
        "updated": updated,
        "regime": tree["regime"],
        "regime_neutral": tree["regime_neutral"],
        "deadline": DEADLINE,
        "days_remaining": days_remaining,
        "cards": cards,
        "activity": parse_log_tail(log_text),
        "stats": count_stats(tree_text, log_text),
        "health": collect_health(),
    }
    return state


def main() -> None:
    state = generate()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"[generate_dashboard_state] Written to {OUT_PATH}")
    print(f"  regime: {state['regime']}")
    print(f"  cards: {len(state['cards'])}, activity: {len(state['activity'])}")
    print(f"  stats: {state['stats']}")
    print(f"  health: {state['health']}")


if __name__ == "__main__":
    main()
