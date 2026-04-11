"""
build_dashboard.py — Phase 2 pull-model dashboard aggregator.

Reads live agent state from multiple sources and writes
results/dashboard_state.json. Graceful degradation: every source is
optional and missing files yield "N/A" instead of errors.

Usage: python platform/build_dashboard.py
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS = REPO_ROOT / "results"
STAGING = REPO_ROOT / "staging"
MEMORY = REPO_ROOT / "memory"
OUT_PATH = RESULTS / "dashboard_state.json"

# Runtime-only path; never committed. Read if exists, ignore otherwise.
AGENT_METRICS_PATH = Path("R:/agent_metrics.json")

# Mission Control data sources
PROGRESS_JSONL = RESULTS / "agent_progress.jsonl"
AUTO_BACKLOG_MD = STAGING / "agent_autonomous_backlog.md"
SOP_PROPOSAL_MD = STAGING / "sop_121_plus_proposal.md"

# Plain-language translation table (jargon -> Chinese)
PRETTY_TYPE_MAP = {
    "subagent_complete": "下屬完成任務",
    "decision_change": "方向調整",
    "phase_1": "Phase 1 階段",
    "phase_2": "Phase 2 階段",
    "phase_3": "Phase 3 階段",
    "phase_3_start": "Phase 3 階段",
    "phase_4": "Phase 4 階段",
    "main_session": "主腦",
    "daemon_cycle": "背景循環",
    "commit": "程式已存檔",
    "error": "出錯",
    "blocker": "卡住",
    "decision_needed": "需要你決定",
}

PRETTY_ACTOR_MAP = {
    "main_session": "主腦",
    "daemon": "背景守護",
    "subagent": "下屬",
}

PRETTY_STATUS_MAP = {
    "started": "開始",
    "in_progress": "進行中",
    "completed": "已完成",
    "done": "已完成",
    "pending": "待決定",
    "failure": "失敗",
    "failed": "失敗",
    "blocked": "卡住",
}

TREE_BRANCHES = [
    (1, "經濟自給"),
    (2, "行為等價"),
    (3, "持續學習"),
    (4, "社交圈"),
    (5, "平台分發"),
    (6, "存活冗餘"),
    (7, "知識輸出"),
]


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except (FileNotFoundError, OSError):
        return None


def read_json(path: Path) -> Any:
    text = read_text(path)
    if text is None:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def load_trading_engine() -> dict[str, Any]:
    data = read_json(RESULTS / "trading_engine_status.json")
    if not data:
        return {"available": False}
    return {
        "available": True,
        "last_tick": data.get("last_tick", "N/A"),
        "tick_count": data.get("tick_count", 0),
        "active_strategies": data.get("active_strategies", 0),
        "disabled": data.get("disabled", {}),
        "total_pnl_pct": data.get("total_pnl_pct", 0),
        "price": data.get("price", 0),
        "regime": data.get("regime", "N/A"),
        "mode": data.get("mode", "N/A"),
    }


def load_execution_rules() -> dict[str, Any]:
    data = read_json(RESULTS / "execution_rules.json")
    if not data:
        return {"available": False}
    return {
        "available": True,
        "kill_max_dd": data.get("kill_max_dd"),
        "kill_min_wr": data.get("kill_min_wr"),
        "kill_min_pf": data.get("kill_min_pf"),
        "kill_window": data.get("kill_window"),
        "kill_count": data.get("kill_count", 0),
        "evolved_at": data.get("evolved_at", "N/A"),
        "last_kill": data.get("last_kill", {}),
    }


def load_disabled_strategies() -> dict[str, Any]:
    data = read_json(RESULTS / "disabled_strategies.json")
    if not data:
        return {"available": False, "items": {}}
    return {"available": True, "items": data}


def load_paper_pnl() -> dict[str, Any]:
    report = read_text(RESULTS / "paper_live_pnl_report.md")
    if not report:
        return {"available": False}
    tick_m = re.search(r"tick\s*(\d+)", report, re.IGNORECASE)
    pnl_m = re.search(r"P&L[:\s=*]*\+?\$?([\-\d.]+)", report)
    return {
        "available": True,
        "tick": int(tick_m.group(1)) if tick_m else None,
        "pnl": f"+${pnl_m.group(1)}" if pnl_m else "N/A",
    }


def load_daemon_tail() -> dict[str, Any]:
    text = read_text(RESULTS / "daemon_log.md")
    if not text:
        return {"available": False, "tail": [], "last_cycle": 0}
    lines = [ln for ln in text.splitlines() if ln.strip()]
    cycles = re.findall(r"^## Cycle (\d+)", text, re.MULTILINE)
    return {
        "available": True,
        "tail": lines[-20:],
        "last_cycle": max((int(c) for c in cycles), default=0),
    }


def load_quick_status() -> dict[str, Any]:
    text = read_text(STAGING / "quick_status.md")
    if not text:
        return {"available": False, "head": []}
    return {"available": True, "head": text.splitlines()[:40]}


def load_tree_branches() -> dict[str, Any]:
    text = read_text(RESULTS / "dynamic_tree.md")
    if not text:
        return {"available": False, "branches": []}
    lines = text.splitlines()
    branches: list[dict[str, Any]] = []
    for num, _label in TREE_BRANCHES:
        pattern = re.compile(rf"^### {num}\.\s+(.+)")
        title = ""
        first = ""
        idx = -1
        for i, line in enumerate(lines):
            m = pattern.match(line)
            if m:
                title = m.group(1).strip()
                idx = i
                break
        if idx >= 0:
            for follow in lines[idx + 1 : idx + 15]:
                s = follow.strip()
                if s.startswith("- ") or s.startswith("* "):
                    first = re.sub(r"\*\*", "", s.lstrip("-* ").strip())
                    if len(first) > 140:
                        first = first[:137] + "..."
                    break
        branches.append({"num": num, "title": title or "N/A", "first": first or "N/A"})
    return {"available": True, "branches": branches}


def parse_b6_streak(text: str | None) -> dict[str, Any]:
    if not text:
        return {"available": False}
    best_cycle = 0
    best_streak = 0
    for m in re.finditer(
        r"cycle\s*(\d+)[^\n]{0,80}?B6\s*(\d+)(?:st|nd|rd|th)\s*clean",
        text,
        re.IGNORECASE,
    ):
        c, s = int(m.group(1)), int(m.group(2))
        if c > best_cycle:
            best_cycle, best_streak = c, s
    if best_streak == 0:
        for m in re.finditer(
            r"\*\*(\d+)(?:st|nd|rd|th)\s+consecutive\s+clean\s+cycle\*\*",
            text,
            re.IGNORECASE,
        ):
            best_streak = max(best_streak, int(m.group(1)))
    if best_streak == 0:
        return {"available": False}
    return {"available": True, "cycle": best_cycle, "streak": best_streak}


def load_b6_streak() -> dict[str, Any]:
    result = parse_b6_streak(read_text(STAGING / "quick_status.md"))
    if result.get("available"):
        return result
    return parse_b6_streak(read_text(RESULTS / "dynamic_tree.md"))


def load_agent_metrics() -> dict[str, Any]:
    data = read_json(AGENT_METRICS_PATH)
    if not data:
        return {"available": False}
    keys = [
        "model", "tokens_in", "tokens_out", "tokens_cached", "context_pct",
        "cost_usd", "git_branch", "ram_used_pct", "ram_disk_free_mb", "ts",
    ]
    out: dict[str, Any] = {"available": True}
    for k in keys:
        out[k] = data.get(k, "N/A")
    return out


def git_log(repo: Path, n: int = 10) -> list[str]:
    if not (repo / ".git").exists():
        return []
    try:
        r = subprocess.run(
            ["git", "log", f"-n{n}", "--oneline"],
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=15,
            encoding="utf-8",
            errors="replace",
        )
        if r.returncode != 0:
            return []
        return [ln for ln in r.stdout.splitlines() if ln.strip()]
    except (subprocess.SubprocessError, OSError):
        return []


def load_git_commits() -> dict[str, list[str]]:
    return {
        "digital-immortality": git_log(REPO_ROOT),
        "LYH": git_log(Path("C:/Users/admin/LYH")),
        "ZP": git_log(Path("C:/Users/admin/ZP")),
    }


def count_insights() -> int:
    text = read_text(MEMORY / "recursive_distillation.md")
    if not text:
        return 0
    return sum(1 for ln in text.splitlines() if ln.startswith("### Insight"))


def _scrub_jargon(msg: str) -> str:
    """Remove commit SHAs / paths / line refs from user-facing strings."""
    msg = re.sub(r"\b[0-9a-f]{7,40}\b", "[程式碼變動]", msg)
    msg = re.sub(r"[\w/\\.-]+\.(py|md|json|jsonl|txt|yml|yaml|html|css|js|ts)", "[檔案]", msg)
    msg = re.sub(r"\bline\s+\d+\b", "", msg, flags=re.IGNORECASE)
    msg = re.sub(r"\bL\d+\b", "", msg)
    return msg.strip()


def _pretty_msg(evt: dict[str, Any]) -> str:
    raw = str(evt.get("msg", "") or "")
    tlabel = PRETTY_TYPE_MAP.get(str(evt.get("type", "") or ""), "")
    scrubbed = _scrub_jargon(raw)
    if len(scrubbed) > 220:
        scrubbed = scrubbed[:217] + "..."
    if tlabel and tlabel not in scrubbed:
        return f"{tlabel}：{scrubbed}" if scrubbed else tlabel
    return scrubbed or tlabel or "(無描述)"


def _unknown_session() -> dict[str, Any]:
    return {"state": "unknown", "label": "狀態不明", "color": "muted", "age_min": None}


def load_main_session_status() -> dict[str, Any]:
    data = read_json(AGENT_METRICS_PATH)
    if not data or not data.get("ts"):
        return _unknown_session()
    ts_str = str(data["ts"]).replace("Z", "+00:00")
    try:
        ts = datetime.fromisoformat(ts_str)
    except ValueError:
        return _unknown_session()
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    age_min = (datetime.now(timezone.utc) - ts).total_seconds() / 60.0
    rounded = round(age_min, 1)
    if age_min < 5:
        return {"state": "online", "label": "在線", "color": "ok", "age_min": rounded}
    if age_min < 30:
        return {"state": "idle", "label": "閒置中", "color": "warn", "age_min": rounded}
    return {"state": "offline", "label": "離線", "color": "alert", "age_min": rounded}


def load_auto_backlog() -> list[dict[str, str]]:
    text = read_text(AUTO_BACKLOG_MD)
    if not text:
        return []
    items: list[dict[str, str]] = []
    for line in text.splitlines():
        m = re.match(r"^(?:[-*]|\d+[\.)])\s+(.+)", line.strip())
        if not m:
            continue
        cleaned = _scrub_jargon(re.sub(r"\*\*|`", "", m.group(1).strip()))
        if len(cleaned) > 180:
            cleaned = cleaned[:177] + "..."
        if cleaned:
            items.append({"text": cleaned})
        if len(items) >= 5:
            break
    return items


def load_pending_approval() -> list[dict[str, str]]:
    text = read_text(SOP_PROPOSAL_MD)
    if not text:
        return []
    items: list[dict[str, str]] = []
    for m in re.finditer(r"^###\s+(SOP\s*#?\d+)\s*[—\-–]\s*(.+?)$", text, re.MULTILINE):
        chunk = text[m.end() : m.end() + 800]
        em = re.search(r"\*\*Essence\*\*[:：]?\s*(.+)", chunk)
        essence = _scrub_jargon(re.sub(r"\*\*|`", "", em.group(1).strip())) if em else ""
        if len(essence) > 200:
            essence = essence[:197] + "..."
        items.append({
            "label": m.group(1).strip(),
            "title": m.group(2).strip(),
            "essence": essence or "(草稿待批准)",
        })
        if len(items) >= 5:
            break
    return items


def load_blocker_items() -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for b in extract_blockers()[:8]:
        out.append({"text": _scrub_jargon(b), "source": "quick_status"})
    text = read_text(RESULTS / "dynamic_tree.md")
    if text:
        for m in re.finditer(r"(?:^|\s)BLOCKER[:：]?\s*(.+?)(?:\n|$)", text, re.MULTILINE):
            desc = _scrub_jargon(re.sub(r"\*\*|`", "", m.group(1).strip()))
            if len(desc) > 180:
                desc = desc[:177] + "..."
            if desc:
                out.append({"text": desc, "source": "tree"})
            if len(out) >= 12:
                break
    seen: set[str] = set()
    uniq: list[dict[str, str]] = []
    for b in out:
        key = b["text"][:80]
        if key not in seen:
            seen.add(key)
            uniq.append(b)
    return uniq[:8]


def load_mission_control() -> dict[str, Any]:
    text = read_text(PROGRESS_JSONL)
    events: list[dict[str, Any]] = []
    if text:
        for line in [ln for ln in text.splitlines() if ln.strip()][-100:]:
            try:
                evt = json.loads(line)
            except json.JSONDecodeError:
                continue
            events.append({
                "ts": evt.get("ts", ""),
                "type": evt.get("type", ""),
                "status": evt.get("status", ""),
                "msg": evt.get("msg", ""),
                "actor": evt.get("actor", ""),
                "pretty_msg": _pretty_msg(evt),
                "pretty_actor": PRETTY_ACTOR_MAP.get(str(evt.get("actor", "") or ""), str(evt.get("actor", "") or "")),
                "pretty_status": PRETTY_STATUS_MAP.get(str(evt.get("status", "") or ""), str(evt.get("status", "") or "")),
            })

    def _key(e: dict[str, Any]) -> str:
        return str(e.get("ts", ""))

    pending = sorted([e for e in events if e["status"] == "pending"], key=_key, reverse=True)
    in_progress = sorted([e for e in events if e["status"] in ("in_progress", "started")], key=_key, reverse=True)
    done = sorted([e for e in events if e["status"] in ("done", "completed")], key=_key, reverse=True)
    failure = sorted([e for e in events if e["status"] in ("failure", "failed", "blocked")], key=_key, reverse=True)

    return {
        "available": bool(events),
        "total_events": len(events),
        "pending": pending[:10],
        "in_progress": in_progress[:20],
        "done": done[:10],
        "failure": failure[:10],
        "recent_feed": sorted(events, key=_key, reverse=True)[:20],
        "backlog": load_auto_backlog(),
        "pending_approval": load_pending_approval(),
        "blocked": load_blocker_items(),
        "main_session_status": load_main_session_status(),
    }


def extract_blockers() -> list[str]:
    text = read_text(STAGING / "quick_status.md")
    if not text:
        return []
    blockers: list[str] = []
    in_section = False
    for line in text.splitlines():
        if line.strip().startswith("## Blockers"):
            in_section = True
            continue
        if in_section:
            if line.startswith("##"):
                break
            s = line.strip()
            if s.startswith("- "):
                blockers.append(s.lstrip("- ").strip())
    return blockers


def build_state() -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    taipei = now.astimezone(timezone(timedelta(hours=8)))
    return {
        "updated_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "updated_taipei": taipei.strftime("%Y-%m-%d %H:%M +08"),
        "tree": load_tree_branches(),
        "trading_engine": load_trading_engine(),
        "execution_rules": load_execution_rules(),
        "disabled_strategies": load_disabled_strategies(),
        "paper_pnl": load_paper_pnl(),
        "daemon": load_daemon_tail(),
        "quick_status": load_quick_status(),
        "b6_streak": load_b6_streak(),
        "agent_metrics": load_agent_metrics(),
        "git": load_git_commits(),
        "insight_count": count_insights(),
        "blockers": extract_blockers(),
        "mission_control": load_mission_control(),
    }


def main() -> None:
    state = build_state()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"[build_dashboard] wrote {OUT_PATH}")
    print(f"  tree_branches={len(state['tree'].get('branches', []))}")
    print(f"  daemon_cycle={state['daemon'].get('last_cycle')}")
    print(f"  b6_streak={state['b6_streak']}")
    print(f"  insights={state['insight_count']}")
    print(f"  blockers={len(state['blockers'])}")
    mc = state.get("mission_control") or {}
    print(f"  mission_control events={mc.get('total_events', 0)}")
    print(f"  mc pending={len(mc.get('pending') or [])}")
    print(f"  mc in_progress={len(mc.get('in_progress') or [])}")
    print(f"  mc done={len(mc.get('done') or [])}")
    print(f"  mc blocked={len(mc.get('blocked') or [])}")
    print(f"  main_session={mc.get('main_session_status', {}).get('state')}")


if __name__ == "__main__":
    main()
