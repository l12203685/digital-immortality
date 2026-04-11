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
from zoneinfo import ZoneInfo

TPE = ZoneInfo("Asia/Taipei")

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

CSS = (
    ":root{--bg:#0d1117;--panel:#161b22;--border:#30363d;--text:#c9d1d9;"
    "--muted:#8b949e;--ok:#3fb950;--warn:#d29922;--alert:#f85149;--accent:#58a6ff}"
    "*{box-sizing:border-box}"
    "body{background:var(--bg);color:var(--text);"
    'font-family:"JetBrains Mono","Consolas","Courier New",monospace;'
    "font-size:13px;line-height:1.45;margin:0;padding:16px}"
    "h1{font-size:18px;margin:0 0 4px 0;color:var(--accent)}"
    "h2{font-size:14px;margin:0 0 8px 0;color:var(--accent);"
    "border-bottom:1px solid var(--border);padding-bottom:4px}"
    ".subtitle{color:var(--muted);font-size:11px;margin-bottom:16px}"
    ".grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:12px}"
    ".panel{background:var(--panel);border:1px solid var(--border);border-radius:6px;padding:12px 14px}"
    ".kv{display:grid;grid-template-columns:140px 1fr;gap:4px 12px}"
    ".kv .k{color:var(--muted)}.kv .v{color:var(--text);word-break:break-word}"
    ".pill{display:inline-block;padding:1px 8px;border-radius:10px;font-size:11px;font-weight:600}"
    ".ok{color:var(--ok)}.warn{color:var(--warn)}.alert{color:var(--alert)}"
    ".pill.ok{background:rgba(63,185,80,0.15);color:var(--ok)}"
    ".pill.warn{background:rgba(210,153,34,0.15);color:var(--warn)}"
    ".pill.alert{background:rgba(248,81,73,0.15);color:var(--alert)}"
    "ul{margin:0;padding-left:18px}li{margin-bottom:2px}"
    "pre{background:#0b1017;border:1px solid var(--border);border-radius:4px;"
    "padding:8px;overflow-x:auto;white-space:pre-wrap;word-break:break-word;"
    "font-size:11px;color:#b0b9c1;max-height:360px;overflow-y:auto;margin:0}"
    ".branch{border-left:2px solid var(--border);padding:4px 10px;margin-bottom:6px}"
    ".branch .num{color:var(--accent);font-weight:600}.branch .title{color:var(--text)}"
    ".branch .first{color:var(--muted);font-size:11px;margin-top:2px}"
    ".muted{color:var(--muted)}"
    "footer{margin-top:16px;color:var(--muted);font-size:10px;text-align:center}"
    ".mc-wrap{background:var(--panel);border:2px solid var(--accent);border-radius:8px;padding:14px 16px;margin-bottom:16px}"
    ".mc-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;flex-wrap:wrap;gap:8px}"
    ".mc-title{font-size:16px;color:var(--accent);font-weight:700;margin:0}"
    ".mc-dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px;vertical-align:middle}"
    ".mc-dot.ok{background:var(--ok);box-shadow:0 0 6px var(--ok)}"
    ".mc-dot.warn{background:var(--warn);box-shadow:0 0 6px var(--warn)}"
    ".mc-dot.alert{background:var(--alert);box-shadow:0 0 6px var(--alert)}"
    ".mc-dot.muted{background:var(--muted)}"
    ".mc-online{font-size:12px;color:var(--muted)}"
    ".mc-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:10px}"
    ".mc-card{background:#0b1017;border:1px solid var(--border);border-radius:6px;padding:10px 12px}"
    ".mc-card h3{margin:0 0 8px 0;font-size:13px;color:var(--accent);border-bottom:1px dashed var(--border);padding-bottom:4px}"
    ".mc-item{padding:6px 0;border-bottom:1px dotted #1f2633;font-size:12px}"
    ".mc-item:last-child{border-bottom:none}.mc-time{color:var(--muted);font-size:10px;margin-right:6px}"
    ".mc-actor{color:var(--accent);font-size:10px;margin-right:6px}"
    ".mc-decision-card{background:rgba(88,166,255,0.08);border:1px solid var(--accent);border-radius:5px;padding:8px 10px;margin-bottom:8px}"
    ".mc-decision-card summary{cursor:pointer;color:var(--text);font-size:12px;list-style:none;outline:none}"
    ".mc-decision-card summary::-webkit-details-marker{display:none}"
    '.mc-decision-card summary::before{content:"▶ ";color:var(--accent);font-size:10px}'
    '.mc-decision-card[open] summary::before{content:"▼ "}'
    ".mc-decision-body{margin-top:6px;padding-top:6px;border-top:1px dashed var(--border);color:var(--muted);font-size:11px}"
    ".mc-decision-body button{background:var(--accent);color:#0b1017;border:none;padding:4px 10px;border-radius:4px;font-size:11px;cursor:pointer;margin-top:6px;font-weight:600}"
    ".mc-decision-body button:hover{opacity:0.85}"
    ".mc-blocker{color:var(--alert)}.mc-done{color:var(--ok)}.mc-progress{color:var(--warn)}"
    ".mc-empty{color:var(--muted);font-style:italic;font-size:11px}"
    ".mc-backlog-item{padding:5px 0;border-bottom:1px dotted #1f2633;color:var(--text)}"
    ".mc-backlog-item:last-child{border-bottom:none}"
    ".mc-backlog-num{color:var(--accent);font-weight:600;margin-right:6px}"
)


def esc(value: Any) -> str:
    if value is None:
        return "N/A"
    return html.escape(str(value), quote=True)


def _kv(pairs: list[tuple[str, str, str]]) -> str:
    """Build a <div class='kv'> block from (key, value, value_cls) tuples."""
    rows = "".join(
        f"<div class='k'>{k}</div><div class='v{(' ' + c) if c else ''}'>{v}</div>"
        for k, v, c in pairs
    )
    return f"<div class='kv'>{rows}</div>"


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
        engine_html = _kv([
            ("mode", esc(engine.get("mode")), ""),
            ("regime", esc(engine.get("regime")), ""),
            ("price", f"${esc(engine.get('price'))}", ""),
            ("tick_count", esc(engine.get("tick_count")), ""),
            ("active", esc(engine.get("active_strategies")), ""),
            ("disabled", str(len(d_engine)), ""),
            ("total_pnl", pnl_str, pnl_cls),
            ("last_tick", esc(_fmt_ts_taipei(engine.get("last_tick"))), ""),
        ])
    else:
        engine_html = "<p class='muted'>engine status: N/A</p>"

    if rules.get("available"):
        lk = rules.get("last_kill") or {}
        rules_html = _kv([
            ("kill_window", esc(rules.get("kill_window")), ""),
            ("kill_count", esc(rules.get("kill_count")), ""),
            ("min_pf", esc(rules.get("kill_min_pf")), ""),
            ("min_wr", esc(rules.get("kill_min_wr")), ""),
            ("max_dd", esc(rules.get("kill_max_dd")), ""),
            ("last_kill", f"{esc(lk.get('strategy'))} — {esc(lk.get('reason'))}", ""),
            ("evolved_at", esc(rules.get("evolved_at")), ""),
        ])
    else:
        rules_html = "<p class='muted'>execution_rules.json: N/A</p>"

    items = disabled.get("items") if disabled.get("available") else None
    if not items:
        items = engine.get("disabled") if engine.get("available") else {}
    if items:
        lis = "".join(f"<li><span class='alert'>{esc(k)}</span>: {esc(v)}</li>"
                      for k, v in items.items())
        disabled_html = f"<ul>{lis}</ul>"
    else:
        disabled_html = "<p class='muted'>no disabled strategies</p>"

    if paper.get("available"):
        paper_html = _kv([
            ("tick", esc(paper.get("tick")), ""),
            ("pnl", esc(paper.get("pnl")), "ok"),
        ])
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
    head = _kv([
        ("last_cycle", esc(last_cycle), ""),
        ("b6_streak", streak_html, ""),
        ("insights", esc(insights), ""),
    ])
    return head + "<h2 style='margin-top:10px'>daemon_log tail</h2><pre>" + esc(tail_text) + "</pre>"


def _thresh_cls(val: Any, good: float, warn: float) -> str:
    if not isinstance(val, (int, float)):
        return ""
    return "ok" if val < good else ("warn" if val < warn else "alert")


def _fmt_ts_taipei(ts_str: Any) -> str:
    """Convert any ISO timestamp to 'YYYY-MM-DD HH:MM (Taipei)' for display.

    Falls back to the raw string if parsing fails.
    """
    if not ts_str or ts_str == "N/A":
        return "N/A"
    try:
        ts = datetime.fromisoformat(str(ts_str).replace("Z", "+00:00"))
    except ValueError:
        return str(ts_str)
    if ts.tzinfo is None:
        # Legacy naive timestamp — treat as Taipei per Edward's rule.
        ts = ts.replace(tzinfo=TPE)
    return ts.astimezone(TPE).strftime("%Y-%m-%d %H:%M (Taipei)")


def render_agent(state: dict[str, Any]) -> str:
    m = state.get("agent_metrics") or {}
    if not m.get("available"):
        return "<p class='muted'>R:/agent_metrics.json not present — N/A</p>"
    ctx, ram = m.get("context_pct", 0), m.get("ram_used_pct", 0)
    return _kv([
        ("model", esc(m.get("model")), ""),
        ("git_branch", esc(m.get("git_branch")), ""),
        ("tokens_in", esc(m.get("tokens_in")), ""),
        ("tokens_out", esc(m.get("tokens_out")), ""),
        ("tokens_cached", esc(m.get("tokens_cached")), ""),
        ("context_pct", f"{esc(ctx)}%", _thresh_cls(ctx, 60, 85)),
        ("cost_usd", f"${esc(m.get('cost_usd'))}", ""),
        ("ram_used", f"{esc(ram)}%", _thresh_cls(ram, 70, 90)),
        ("ramdisk_free", f"{esc(m.get('ram_disk_free_mb'))} MB", ""),
        ("metrics_ts", esc(_fmt_ts_taipei(m.get("ts"))), "muted"),
    ])


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


def _rel_time(ts_str: str) -> str:
    if not ts_str:
        return ""
    try:
        ts = datetime.fromisoformat(str(ts_str).replace("Z", "+00:00"))
    except ValueError:
        return ""
    if ts.tzinfo is None:
        # Legacy naive timestamp — treat as Taipei per Edward's rule.
        ts = ts.replace(tzinfo=TPE)
    secs = int((datetime.now(TPE) - ts).total_seconds())
    if secs < 60:
        return "剛剛"
    if secs < 3600:
        return f"{secs // 60} 分鐘前"
    if secs < 86400:
        return f"{secs // 3600} 小時前"
    return f"{secs // 86400} 天前"


def _mc_pending_card(evt: dict[str, Any]) -> str:
    pretty = esc(evt.get("pretty_msg") or "(無描述)")
    when = esc(_rel_time(evt.get("ts", "")))
    return (
        "<details class='mc-decision-card'>"
        f"<summary>{pretty} <span class='mc-time'>（{when}）</span></summary>"
        "<div class='mc-decision-body'>這件事需要你點頭或給方向。"
        "點擊下方「我知道了」會暫時收起（Phase 4 會接後端真正處理）。<br>"
        "<form onsubmit='return false'>"
        "<button type='submit' onclick='this.closest(\"details\").open=false'>我知道了</button>"
        "</form></div></details>"
    )


def _mc_approval_card(item: dict[str, Any]) -> str:
    label, title, essence = esc(item.get("label", "")), esc(item.get("title", "")), esc(item.get("essence", ""))
    return (
        "<details class='mc-decision-card'>"
        f"<summary><strong>{label}</strong> — {title}</summary>"
        f"<div class='mc-decision-body'>{essence}<br>"
        "<form onsubmit='return false'>"
        "<button type='submit' onclick='this.closest(\"details\").open=false'>稍後再看</button>"
        "</form></div></details>"
    )


def _mc_feed_line(evt: dict[str, Any], cls: str, prefix: str = "") -> str:
    when = esc(_rel_time(evt.get("ts", "")))
    actor = esc(evt.get("pretty_actor") or "")
    msg = esc(evt.get("pretty_msg") or "")
    actor_html = f"<span class='mc-actor'>{actor}</span>" if actor else ""
    return (f"<div class='mc-item {cls}'><span class='mc-time'>{when}</span>"
            f"{actor_html}{prefix}{msg}</div>")


def _mc_section(items: list[Any], empty_msg: str, render_item) -> str:
    if not items:
        return f"<p class='mc-empty'>{empty_msg}</p>"
    return "\n".join(render_item(x) for x in items)


def render_mission_control(state: dict[str, Any]) -> str:
    mc = state.get("mission_control") or {}
    online = mc.get("main_session_status") or {}
    dot_cls = esc(online.get("color") or "muted")
    age_min = online.get("age_min")
    age_str = f"（{age_min} 分鐘前更新）" if age_min is not None else ""
    header = ("<div class='mc-header'>"
        "<h2 class='mc-title'>🎯 Mission Control — 現在發生什麼事</h2>"
        f"<div class='mc-online'><span class='mc-dot {dot_cls}'></span>"
        f"主腦：{esc(online.get('label') or '狀態不明')} {esc(age_str)}</div></div>")
    if not mc.get("available") and not mc.get("backlog") and not mc.get("pending_approval"):
        return ("<section class='mc-wrap'>" + header
                + "<p class='mc-empty'>尚無活動 — 主腦還沒寫入任何事件</p></section>")
    pending = mc.get("pending") or []
    in_progress = mc.get("recent_feed") or mc.get("in_progress") or []
    done = mc.get("done") or []
    blocked = mc.get("blocked") or []
    backlog = mc.get("backlog") or []
    pending_approval = mc.get("pending_approval") or []
    approval_block = (("<h3 style='margin-top:10px'>📝 等你批准</h3>"
                       + "\n".join(_mc_approval_card(i) for i in pending_approval))
                      if pending_approval else "")
    backlog_html = ("\n".join(
            f"<div class='mc-backlog-item'><span class='mc-backlog-num'>{i}.</span>"
            f"{esc(x.get('text', ''))}</div>" for i, x in enumerate(backlog, 1))
        if backlog else "<p class='mc-empty'>自動 backlog 尚未產生（等主腦產出）</p>")
    card = lambda title, body: f"<div class='mc-card'><h3>{title}</h3>{body}</div>"  # noqa: E731
    cards = [
        card("🎯 待你決策", _mc_section(pending, "目前沒有需要你決定的事項", _mc_pending_card) + approval_block),
        card("🚀 進行中", _mc_section(in_progress, "目前沒有進行中的任務", lambda e: _mc_feed_line(e, "mc-progress"))),
        card("✅ 剛完成", _mc_section(done, "尚無已完成的任務", lambda e: _mc_feed_line(e, "mc-done", "✓ "))),
        card("🚧 卡住", _mc_section(blocked, "目前沒有卡住的事項",
            lambda b: f"<div class='mc-item mc-blocker'>⚠ {esc(b.get('text', ''))}</div>")),
        card("📋 自動 backlog top 5", backlog_html),
    ]
    return ("<section class='mc-wrap'>" + header
            + "<div class='mc-grid'>" + "\n".join(cards) + "</div></section>")


def render_page(state: dict[str, Any]) -> str:
    updated = state.get("updated_taipei") or state.get("updated_utc") or "unknown"
    # Ensure Taipei label is explicit even if upstream state is old format.
    if updated and "Taipei" not in str(updated) and "+08" not in str(updated):
        updated = f"{updated} (Taipei, UTC+8)"
    body = f"""
<h1>Digital Immortality — 永生樹 Dashboard</h1>
<div class='subtitle'>updated: {esc(updated)} · 所有時間 Asia/Taipei (UTC+8) · pull-model · auto-refresh 5min</div>
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
    return ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta http-equiv="refresh" content="300">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>Digital Immortality Dashboard</title>\n'
        f'<style>{CSS}</style>\n</head>\n<body>\n{README_COMMENT}\n{body}\n</body>\n</html>\n')


def main() -> None:
    state = load_state()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(render_page(state), encoding="utf-8")
    print(f"[render_dashboard] wrote {OUT_PATH} ({OUT_PATH.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
