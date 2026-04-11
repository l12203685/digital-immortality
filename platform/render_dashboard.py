"""
render_dashboard.py — Static HTML renderer for dashboard_state.json.

Reads results/dashboard_state.json and emits docs/dashboard.html.
Plain HTML + inline CSS, no JS, no external deps. Safe against
missing inputs (everything falls back to "N/A").

Usage: python platform/render_dashboard.py
"""

from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
IN_PATH = REPO_ROOT / "results" / "dashboard_state.json"
OUT_PATH = REPO_ROOT / "docs" / "dashboard.html"

README_COMMENT = """<!--
  Digital Immortality Dashboard (Phase 2, pull-model)
  =====================================================
  URL:     https://l12203685.github.io/digital-immortality/dashboard.html
  Refresh: auto-reload every 5 minutes (meta http-equiv=refresh).
           Manual refresh: re-run platform/build_dashboard.py and
           platform/render_dashboard.py (or wait for next daemon cycle).

  Sections
  --------
  Tree     : 7 永生樹 branches (1 經濟 to 7 知識輸出).
  Trading  : Engine tick, active/disabled strategies, paper P&L, kill window.
  Daemon   : Last cycle, B6 clean-streak, last 20 log lines, insight count.
  Agent    : Model, tokens, cost, RAM (from R:/agent_metrics.json, runtime only).
  Git      : Last 10 commits from digital-immortality / LYH / ZP.
  Blockers : Human-gated items parsed from staging/quick_status.md.

  Rebuild is wired into platform/recursive_daemon.py (end of each cycle).
  Dashboard failures never kill daemon cycles (subprocess check=False).
-->"""

CSS = """
:root{--bg:#0d1117;--panel:#161b22;--border:#30363d;--text:#c9d1d9;
--muted:#8b949e;--ok:#3fb950;--warn:#d29922;--alert:#f85149;--accent:#58a6ff}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--text);
font-family:"JetBrains Mono","Consolas","Courier New",monospace;
font-size:13px;line-height:1.45;margin:0;padding:16px}
h1{font-size:18px;margin:0 0 4px 0;color:var(--accent)}
h2{font-size:14px;margin:0 0 8px 0;color:var(--accent);
border-bottom:1px solid var(--border);padding-bottom:4px}
.subtitle{color:var(--muted);font-size:11px;margin-bottom:16px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:12px}
.panel{background:var(--panel);border:1px solid var(--border);
border-radius:6px;padding:12px 14px}
.kv{display:grid;grid-template-columns:140px 1fr;gap:4px 12px}
.kv .k{color:var(--muted)}
.kv .v{color:var(--text);word-break:break-word}
.pill{display:inline-block;padding:1px 8px;border-radius:10px;
font-size:11px;font-weight:600}
.ok{color:var(--ok)}.warn{color:var(--warn)}.alert{color:var(--alert)}
.pill.ok{background:rgba(63,185,80,0.15);color:var(--ok)}
.pill.warn{background:rgba(210,153,34,0.15);color:var(--warn)}
.pill.alert{background:rgba(248,81,73,0.15);color:var(--alert)}
ul{margin:0;padding-left:18px}li{margin-bottom:2px}
pre{background:#0b1017;border:1px solid var(--border);border-radius:4px;
padding:8px;overflow-x:auto;white-space:pre-wrap;word-break:break-word;
font-size:11px;color:#b0b9c1;max-height:360px;overflow-y:auto;margin:0}
.branch{border-left:2px solid var(--border);padding:4px 10px;margin-bottom:6px}
.branch .num{color:var(--accent);font-weight:600}
.branch .title{color:var(--text)}
.branch .first{color:var(--muted);font-size:11px;margin-top:2px}
.muted{color:var(--muted)}
footer{margin-top:16px;color:var(--muted);font-size:10px;text-align:center}
.mc-wrap{background:var(--panel);border:2px solid var(--accent);border-radius:8px;
padding:14px 16px;margin-bottom:16px}
.mc-header{display:flex;align-items:center;justify-content:space-between;
margin-bottom:10px;flex-wrap:wrap;gap:8px}
.mc-title{font-size:16px;color:var(--accent);font-weight:700;margin:0}
.mc-dot{display:inline-block;width:10px;height:10px;border-radius:50%;
margin-right:6px;vertical-align:middle}
.mc-dot.ok{background:var(--ok);box-shadow:0 0 6px var(--ok)}
.mc-dot.warn{background:var(--warn);box-shadow:0 0 6px var(--warn)}
.mc-dot.alert{background:var(--alert);box-shadow:0 0 6px var(--alert)}
.mc-dot.muted{background:var(--muted)}
.mc-online{font-size:12px;color:var(--muted)}
.mc-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:10px}
.mc-card{background:#0b1017;border:1px solid var(--border);border-radius:6px;
padding:10px 12px}
.mc-card h3{margin:0 0 8px 0;font-size:13px;color:var(--accent);
border-bottom:1px dashed var(--border);padding-bottom:4px}
.mc-item{padding:6px 0;border-bottom:1px dotted #1f2633;font-size:12px}
.mc-item:last-child{border-bottom:none}
.mc-time{color:var(--muted);font-size:10px;margin-right:6px}
.mc-actor{color:var(--accent);font-size:10px;margin-right:6px}
.mc-decision-card{background:rgba(88,166,255,0.08);border:1px solid var(--accent);
border-radius:5px;padding:8px 10px;margin-bottom:8px}
.mc-decision-card summary{cursor:pointer;color:var(--text);font-size:12px;
list-style:none;outline:none}
.mc-decision-card summary::-webkit-details-marker{display:none}
.mc-decision-card summary::before{content:"▶ ";color:var(--accent);font-size:10px}
.mc-decision-card[open] summary::before{content:"▼ "}
.mc-decision-body{margin-top:6px;padding-top:6px;border-top:1px dashed var(--border);
color:var(--muted);font-size:11px}
.mc-decision-body button{background:var(--accent);color:#0b1017;border:none;
padding:4px 10px;border-radius:4px;font-size:11px;cursor:pointer;margin-top:6px;
font-weight:600}
.mc-decision-body button:hover{opacity:0.85}
.mc-blocker{color:var(--alert)}
.mc-done{color:var(--ok)}
.mc-progress{color:var(--warn)}
.mc-empty{color:var(--muted);font-style:italic;font-size:11px}
.mc-backlog-item{padding:5px 0;border-bottom:1px dotted #1f2633;color:var(--text)}
.mc-backlog-item:last-child{border-bottom:none}
.mc-backlog-num{color:var(--accent);font-weight:600;margin-right:6px}
"""


def esc(value: Any) -> str:
    if value is None:
        return "N/A"
    return html.escape(str(value), quote=True)


def load_state() -> dict[str, Any]:
    try:
        return json.loads(IN_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def render_tree(state: dict[str, Any]) -> str:
    branches = (state.get("tree") or {}).get("branches") or []
    if not branches:
        return "<p class='muted'>N/A — dynamic_tree.md not parseable</p>"
    out = []
    for b in branches:
        out.append(
            f"<div class='branch'><div><span class='num'>{esc(b.get('num'))}.</span> "
            f"<span class='title'>{esc(b.get('title'))}</span></div>"
            f"<div class='first'>{esc(b.get('first'))}</div></div>"
        )
    return "\n".join(out)


def render_trading(state: dict[str, Any]) -> str:
    engine = state.get("trading_engine") or {}
    rules = state.get("execution_rules") or {}
    disabled = state.get("disabled_strategies") or {}
    paper = state.get("paper_pnl") or {}

    if engine.get("available"):
        pnl = engine.get("total_pnl_pct", 0)
        pnl_cls = "ok" if isinstance(pnl, (int, float)) and pnl >= 0 else "alert"
        pnl_str = f"{pnl:+.4f}%" if isinstance(pnl, (int, float)) else esc(pnl)
        d_engine = engine.get("disabled") or {}
        engine_html = (
            "<div class='kv'>"
            f"<div class='k'>mode</div><div class='v'>{esc(engine.get('mode'))}</div>"
            f"<div class='k'>regime</div><div class='v'>{esc(engine.get('regime'))}</div>"
            f"<div class='k'>price</div><div class='v'>${esc(engine.get('price'))}</div>"
            f"<div class='k'>tick_count</div><div class='v'>{esc(engine.get('tick_count'))}</div>"
            f"<div class='k'>active</div><div class='v'>{esc(engine.get('active_strategies'))}</div>"
            f"<div class='k'>disabled</div><div class='v'>{len(d_engine)}</div>"
            f"<div class='k'>total_pnl</div><div class='v {pnl_cls}'>{pnl_str}</div>"
            f"<div class='k'>last_tick</div><div class='v'>{esc(engine.get('last_tick'))}</div>"
            "</div>"
        )
    else:
        engine_html = "<p class='muted'>engine status: N/A</p>"

    if rules.get("available"):
        lk = rules.get("last_kill") or {}
        rules_html = (
            "<div class='kv'>"
            f"<div class='k'>kill_window</div><div class='v'>{esc(rules.get('kill_window'))}</div>"
            f"<div class='k'>kill_count</div><div class='v'>{esc(rules.get('kill_count'))}</div>"
            f"<div class='k'>min_pf</div><div class='v'>{esc(rules.get('kill_min_pf'))}</div>"
            f"<div class='k'>min_wr</div><div class='v'>{esc(rules.get('kill_min_wr'))}</div>"
            f"<div class='k'>max_dd</div><div class='v'>{esc(rules.get('kill_max_dd'))}</div>"
            f"<div class='k'>last_kill</div><div class='v'>{esc(lk.get('strategy'))} — {esc(lk.get('reason'))}</div>"
            f"<div class='k'>evolved_at</div><div class='v'>{esc(rules.get('evolved_at'))}</div>"
            "</div>"
        )
    else:
        rules_html = "<p class='muted'>execution_rules.json: N/A</p>"

    items = disabled.get("items") if disabled.get("available") else None
    if not items:
        items = engine.get("disabled") if engine.get("available") else {}
    if items:
        lis = "".join(
            f"<li><span class='alert'>{esc(k)}</span>: {esc(v)}</li>"
            for k, v in items.items()
        )
        disabled_html = f"<ul>{lis}</ul>"
    else:
        disabled_html = "<p class='muted'>no disabled strategies</p>"

    if paper.get("available"):
        paper_html = (
            "<div class='kv'>"
            f"<div class='k'>tick</div><div class='v'>{esc(paper.get('tick'))}</div>"
            f"<div class='k'>pnl</div><div class='v ok'>{esc(paper.get('pnl'))}</div>"
            "</div>"
        )
    else:
        paper_html = "<p class='muted'>paper P&amp;L: N/A</p>"

    return (
        "<h2>engine</h2>" + engine_html
        + "<h2 style='margin-top:10px'>kill window</h2>" + rules_html
        + "<h2 style='margin-top:10px'>disabled strategies</h2>" + disabled_html
        + "<h2 style='margin-top:10px'>paper live</h2>" + paper_html
    )


def render_daemon(state: dict[str, Any]) -> str:
    daemon = state.get("daemon") or {}
    streak = state.get("b6_streak") or {}
    insights = state.get("insight_count", 0)
    last_cycle = daemon.get("last_cycle", "N/A") if daemon.get("available") else "N/A"
    if streak.get("available"):
        streak_html = f"<span class='pill ok'>B6 {esc(streak.get('streak'))}th clean</span>"
    else:
        streak_html = "<span class='pill warn'>B6 streak N/A</span>"
    tail = daemon.get("tail") or []
    tail_text = "\n".join(tail) if tail else "N/A"
    head = (
        "<div class='kv'>"
        f"<div class='k'>last_cycle</div><div class='v'>{esc(last_cycle)}</div>"
        f"<div class='k'>b6_streak</div><div class='v'>{streak_html}</div>"
        f"<div class='k'>insights</div><div class='v'>{esc(insights)}</div>"
        "</div>"
    )
    return head + "<h2 style='margin-top:10px'>daemon_log tail</h2><pre>" + esc(tail_text) + "</pre>"


def render_agent(state: dict[str, Any]) -> str:
    m = state.get("agent_metrics") or {}
    if not m.get("available"):
        return "<p class='muted'>R:/agent_metrics.json not present — N/A</p>"
    ctx = m.get("context_pct", 0)
    ctx_cls = "ok" if isinstance(ctx, (int, float)) and ctx < 60 else ("warn" if isinstance(ctx, (int, float)) and ctx < 85 else "alert")
    ram = m.get("ram_used_pct", 0)
    ram_cls = "ok" if isinstance(ram, (int, float)) and ram < 70 else ("warn" if isinstance(ram, (int, float)) and ram < 90 else "alert")
    return (
        "<div class='kv'>"
        f"<div class='k'>model</div><div class='v'>{esc(m.get('model'))}</div>"
        f"<div class='k'>git_branch</div><div class='v'>{esc(m.get('git_branch'))}</div>"
        f"<div class='k'>tokens_in</div><div class='v'>{esc(m.get('tokens_in'))}</div>"
        f"<div class='k'>tokens_out</div><div class='v'>{esc(m.get('tokens_out'))}</div>"
        f"<div class='k'>tokens_cached</div><div class='v'>{esc(m.get('tokens_cached'))}</div>"
        f"<div class='k'>context_pct</div><div class='v {ctx_cls}'>{esc(ctx)}%</div>"
        f"<div class='k'>cost_usd</div><div class='v'>${esc(m.get('cost_usd'))}</div>"
        f"<div class='k'>ram_used</div><div class='v {ram_cls}'>{esc(ram)}%</div>"
        f"<div class='k'>ramdisk_free</div><div class='v'>{esc(m.get('ram_disk_free_mb'))} MB</div>"
        f"<div class='k'>metrics_ts</div><div class='v muted'>{esc(m.get('ts'))}</div>"
        "</div>"
    )


def render_git(state: dict[str, Any]) -> str:
    git = state.get("git") or {}
    parts = []
    for repo in ("digital-immortality", "LYH", "ZP"):
        commits = git.get(repo) or []
        if commits:
            lis = "".join(f"<li>{esc(c)}</li>" for c in commits)
            parts.append(f"<h2 style='margin-top:8px'>{esc(repo)}</h2><ul>{lis}</ul>")
        else:
            parts.append(f"<h2 style='margin-top:8px'>{esc(repo)}</h2><p class='muted'>N/A</p>")
    return "\n".join(parts)


def render_blockers(state: dict[str, Any]) -> str:
    blockers = state.get("blockers") or []
    if not blockers:
        return "<p class='muted'>no human-gated blockers listed</p>"
    lis = "".join(f"<li class='alert'>{esc(b)}</li>" for b in blockers)
    return f"<ul>{lis}</ul>"


def _relative_time(ts_str: str) -> str:
    """Return Chinese relative time like '5 分鐘前', '剛剛', '2 小時前'."""
    if not ts_str:
        return ""
    s = str(ts_str).replace("Z", "+00:00")
    try:
        ts = datetime.fromisoformat(s)
    except ValueError:
        return ""
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - ts
    secs = int(delta.total_seconds())
    if secs < 0:
        return "剛剛"
    if secs < 60:
        return "剛剛"
    mins = secs // 60
    if mins < 60:
        return f"{mins} 分鐘前"
    hrs = mins // 60
    if hrs < 24:
        return f"{hrs} 小時前"
    days = hrs // 24
    return f"{days} 天前"


def render_mc_pending(items: list[dict[str, Any]]) -> str:
    """Render pending decisions as expandable cards (needs Edward action)."""
    if not items:
        return "<p class='mc-empty'>目前沒有需要你決定的事項</p>"
    out = []
    for i, evt in enumerate(items):
        pretty = esc(evt.get("pretty_msg") or "(無描述)")
        when = esc(_relative_time(evt.get("ts", "")))
        out.append(
            "<details class='mc-decision-card'>"
            f"<summary>{pretty} <span class='mc-time'>（{when}）</span></summary>"
            "<div class='mc-decision-body'>"
            f"這件事需要你點頭或給方向。點擊下方「我知道了」會暫時收起（Phase 4 會接後端真正處理）。"
            f"<br><form onsubmit='return false'>"
            f"<button type='submit' onclick='this.closest(\"details\").open=false'>我知道了</button>"
            "</form></div></details>"
        )
    return "\n".join(out)


def render_mc_in_progress(items: list[dict[str, Any]]) -> str:
    """Render live feed of in-progress events."""
    if not items:
        return "<p class='mc-empty'>目前沒有進行中的任務</p>"
    out = []
    for evt in items:
        when = esc(_relative_time(evt.get("ts", "")))
        actor = esc(evt.get("pretty_actor") or "")
        msg = esc(evt.get("pretty_msg") or "")
        out.append(
            "<div class='mc-item mc-progress'>"
            f"<span class='mc-time'>{when}</span>"
            f"<span class='mc-actor'>{actor}</span>"
            f"{msg}</div>"
        )
    return "\n".join(out)


def render_mc_done(items: list[dict[str, Any]]) -> str:
    """Render recently completed events with relative time."""
    if not items:
        return "<p class='mc-empty'>尚無已完成的任務</p>"
    out = []
    for evt in items:
        when = esc(_relative_time(evt.get("ts", "")))
        msg = esc(evt.get("pretty_msg") or "")
        out.append(
            "<div class='mc-item mc-done'>"
            f"<span class='mc-time'>{when}</span>"
            f"✓ {msg}</div>"
        )
    return "\n".join(out)


def render_mc_blocked(items: list[dict[str, Any]]) -> str:
    """Render blocked items waiting on external dependency."""
    if not items:
        return "<p class='mc-empty'>目前沒有卡住的事項</p>"
    out = []
    for item in items:
        text = esc(item.get("text", ""))
        out.append(f"<div class='mc-item mc-blocker'>⚠ {text}</div>")
    return "\n".join(out)


def render_mc_backlog(items: list[dict[str, Any]]) -> str:
    """Render top 5 auto backlog items."""
    if not items:
        return "<p class='mc-empty'>自動 backlog 尚未產生（等主腦產出）</p>"
    out = []
    for i, item in enumerate(items, 1):
        text = esc(item.get("text", ""))
        out.append(
            f"<div class='mc-backlog-item'>"
            f"<span class='mc-backlog-num'>{i}.</span>{text}</div>"
        )
    return "\n".join(out)


def render_mc_pending_approval(items: list[dict[str, Any]]) -> str:
    """Render items waiting for Edward ratification (SOP proposals)."""
    if not items:
        return ""
    out = ["<h3 style='margin-top:10px'>📝 等你批准</h3>"]
    for item in items:
        label = esc(item.get("label", ""))
        title = esc(item.get("title", ""))
        essence = esc(item.get("essence", ""))
        out.append(
            "<details class='mc-decision-card'>"
            f"<summary><strong>{label}</strong> — {title}</summary>"
            f"<div class='mc-decision-body'>{essence}<br>"
            "<form onsubmit='return false'>"
            "<button type='submit' onclick='this.closest(\"details\").open=false'>稍後再看</button>"
            "</form></div></details>"
        )
    return "\n".join(out)


def render_mission_control(state: dict[str, Any]) -> str:
    mc = state.get("mission_control") or {}
    if not mc.get("available") and not mc.get("backlog") and not mc.get("pending_approval"):
        online = mc.get("main_session_status") or {}
        dot_cls = esc(online.get("color") or "muted")
        label = esc(online.get("label") or "狀態不明")
        return (
            "<section class='mc-wrap'>"
            "<div class='mc-header'>"
            "<h2 class='mc-title'>🎯 Mission Control — 現在發生什麼事</h2>"
            f"<div class='mc-online'><span class='mc-dot {dot_cls}'></span>"
            f"主腦：{label}</div>"
            "</div>"
            "<p class='mc-empty'>尚無活動 — 主腦還沒寫入任何事件</p>"
            "</section>"
        )

    online = mc.get("main_session_status") or {}
    dot_cls = esc(online.get("color") or "muted")
    label = esc(online.get("label") or "狀態不明")
    age_min = online.get("age_min")
    age_str = f"（{age_min} 分鐘前更新）" if age_min is not None else ""

    pending = mc.get("pending") or []
    in_progress = mc.get("recent_feed") or mc.get("in_progress") or []
    done = mc.get("done") or []
    blocked = mc.get("blocked") or []
    backlog = mc.get("backlog") or []
    pending_approval = mc.get("pending_approval") or []

    header = (
        "<div class='mc-header'>"
        "<h2 class='mc-title'>🎯 Mission Control — 現在發生什麼事</h2>"
        f"<div class='mc-online'><span class='mc-dot {dot_cls}'></span>"
        f"主腦：{label} {esc(age_str)}</div>"
        "</div>"
    )

    cards = [
        "<div class='mc-card'><h3>🎯 待你決策</h3>"
        + render_mc_pending(pending)
        + render_mc_pending_approval(pending_approval)
        + "</div>",
        "<div class='mc-card'><h3>🚀 進行中</h3>"
        + render_mc_in_progress(in_progress)
        + "</div>",
        "<div class='mc-card'><h3>✅ 剛完成</h3>"
        + render_mc_done(done)
        + "</div>",
        "<div class='mc-card'><h3>🚧 卡住</h3>"
        + render_mc_blocked(blocked)
        + "</div>",
        "<div class='mc-card'><h3>📋 自動 backlog top 5</h3>"
        + render_mc_backlog(backlog)
        + "</div>",
    ]
    return (
        "<section class='mc-wrap'>"
        + header
        + "<div class='mc-grid'>"
        + "\n".join(cards)
        + "</div></section>"
    )


def render_page(state: dict[str, Any]) -> str:
    updated = state.get("updated_taipei") or state.get("updated_utc") or "unknown"
    body = f"""
<h1>Digital Immortality — 永生樹 Dashboard</h1>
<div class='subtitle'>updated: {esc(updated)} · pull-model · auto-refresh 5min</div>
{render_mission_control(state)}
<div class='grid'>
  <section class='panel'><h2>永生樹 (7 branches)</h2>{render_tree(state)}</section>
  <section class='panel'><h2>Trading</h2>{render_trading(state)}</section>
  <section class='panel'><h2>Daemon</h2>{render_daemon(state)}</section>
  <section class='panel'><h2>Agent</h2>{render_agent(state)}</section>
  <section class='panel'><h2>Git — last 10 commits</h2>{render_git(state)}</section>
  <section class='panel'><h2>Blockers (human-gated)</h2>{render_blockers(state)}</section>
</div>
<footer>build_dashboard.py + render_dashboard.py · plain HTML · stdlib only</footer>
"""
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta http-equiv=\"refresh\" content=\"300\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<title>Digital Immortality Dashboard</title>\n"
        f"<style>{CSS}</style>\n</head>\n<body>\n"
        f"{README_COMMENT}\n{body}\n</body>\n</html>\n"
    )


def main() -> None:
    state = load_state()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(render_page(state), encoding="utf-8")
    size_kb = OUT_PATH.stat().st_size / 1024
    print(f"[render_dashboard] wrote {OUT_PATH} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
