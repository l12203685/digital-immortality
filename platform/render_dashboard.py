"""render_dashboard.py — Plain-language dashboard renderer.

Reads results/dashboard_state.json and emits docs/dashboard.html.
Design goals (2026-04-11 redesign):

- **Hero metrics** — 3 big numbers answer "is everything OK?" before scrolling.
- **Plain Chinese** — every user-facing string in Traditional Chinese.
  Technical jargon (kill_window/PF/WR/MDD/commit SHA/etc.) is hidden or
  folded into collapsed details.
- **Mobile-first** — single-column on narrow viewports, readable font sizes,
  no fixed min-widths that cause horizontal scroll.
- **Fresh data** — meta refresh every 30 seconds (down from 300).
- **Consistent colors** — ok=green, warn=yellow, alert=red, muted=grey.

Stdlib only. No external CSS, no JS frameworks. Output stays under 200 KB.
"""

from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from pretty_translate import (
    daemon_health_zh,
    engine_status_zh,
    friendly_branch_first_line,
    hide_technical,
    label_zh,
    pending_count_color,
    pnl_color,
    to_plain_zh,
)

TPE = ZoneInfo("Asia/Taipei")

REPO_ROOT = Path(__file__).resolve().parent.parent
IN_PATH = REPO_ROOT / "results" / "dashboard_state.json"
OUT_PATH = REPO_ROOT / "docs" / "dashboard.html"

REFRESH_SECONDS = 30  # Edward complained dashboard was not real-time (was 300).

README_COMMENT = """<!--
  Digital Immortality Dashboard (plain-language redesign 2026-04-11)
  =====================================================
  URL:     https://l12203685.github.io/digital-immortality/dashboard.html
  Refresh: meta http-equiv=refresh every 30s.
           Manual rebuild: python platform/build_dashboard.py && python platform/render_dashboard.py

  Design principles:
    1. Hero metrics (3 big numbers) answer "is everything OK?" at a glance.
    2. Plain Traditional Chinese — no commit SHAs, no PF/WR/MDD, no raw log dumps.
    3. Mobile-first — 375px viewport with no horizontal scroll.
    4. Color code: green=ok, yellow=warn, red=alert, grey=muted.

  Shared vocabulary: platform/pretty_translate.py
-->"""

# ---------------------------------------------------------------------------
# CSS — mobile-first, large touch targets, generous whitespace
# ---------------------------------------------------------------------------
CSS = """
:root{
  --bg:#0d1117;--panel:#161b22;--panel2:#0b1017;--border:#30363d;
  --text:#e6edf3;--muted:#8b949e;
  --ok:#3fb950;--warn:#d29922;--alert:#f85149;--accent:#58a6ff;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:var(--bg);color:var(--text);
  font-family:-apple-system,"PingFang TC","Noto Sans TC","Microsoft JhengHei",
    "Helvetica Neue",Arial,sans-serif;
  font-size:16px;line-height:1.55;-webkit-font-smoothing:antialiased}
.wrap{max-width:1100px;margin:0 auto;padding:16px}
h1{font-size:22px;margin:0 0 4px 0;color:var(--text);font-weight:700;letter-spacing:0.02em}
h2{font-size:16px;margin:0 0 12px 0;color:var(--accent);font-weight:600;
  border-bottom:1px solid var(--border);padding-bottom:6px}
h3{font-size:14px;margin:0 0 8px 0;color:var(--accent);font-weight:600}
.subtitle{color:var(--muted);font-size:13px;margin:0 0 16px 0}
.subtitle .live{color:var(--ok);font-weight:600}

/* Hero metrics — 3 big numbers */
.hero{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:18px}
.hero .card{background:var(--panel);border:1px solid var(--border);
  border-radius:10px;padding:14px 12px;text-align:center;min-height:96px;
  display:flex;flex-direction:column;justify-content:center}
.hero .card .label{color:var(--muted);font-size:13px;margin-bottom:6px}
.hero .card .value{font-size:28px;font-weight:700;line-height:1.1}
.hero .card.ok{border-color:var(--ok)}.hero .card.ok .value{color:var(--ok)}
.hero .card.warn{border-color:var(--warn)}.hero .card.warn .value{color:var(--warn)}
.hero .card.alert{border-color:var(--alert)}.hero .card.alert .value{color:var(--alert)}
.hero .card.muted{border-color:var(--border)}.hero .card.muted .value{color:var(--muted)}

/* Alert banner (red) */
.banner{background:rgba(248,81,73,0.12);border:1px solid var(--alert);
  border-radius:8px;padding:12px 14px;margin-bottom:16px;color:var(--alert);
  font-weight:600;font-size:15px}
.banner ul{margin:6px 0 0 0;padding-left:20px;font-weight:400;color:var(--text)}

/* Mission Control */
.mc-wrap{background:var(--panel);border:1px solid var(--border);
  border-radius:10px;padding:14px 16px;margin-bottom:18px}
.mc-header{display:flex;align-items:center;justify-content:space-between;
  margin-bottom:12px;flex-wrap:wrap;gap:8px}
.mc-title{font-size:16px;color:var(--text);font-weight:700;margin:0}
.mc-online{font-size:13px;color:var(--muted)}
.mc-dot{display:inline-block;width:10px;height:10px;border-radius:50%;
  margin-right:6px;vertical-align:middle}
.mc-dot.ok{background:var(--ok);box-shadow:0 0 6px var(--ok)}
.mc-dot.warn{background:var(--warn);box-shadow:0 0 6px var(--warn)}
.mc-dot.alert{background:var(--alert);box-shadow:0 0 6px var(--alert)}
.mc-dot.muted{background:var(--muted)}
.mc-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}
.mc-card{background:var(--panel2);border:1px solid var(--border);
  border-radius:8px;padding:12px 14px;min-height:120px}
.mc-item{padding:8px 0;border-bottom:1px dotted #1f2633;font-size:14px}
.mc-item:last-child{border-bottom:none}
.mc-time{color:var(--muted);font-size:12px;margin-right:6px}
.mc-actor{color:var(--accent);font-size:12px;margin-right:6px}
.mc-decision-card{background:rgba(210,153,34,0.08);
  border:1px solid var(--warn);border-radius:8px;padding:12px 14px;
  margin-bottom:10px;min-height:48px}
.mc-decision-card summary{cursor:pointer;color:var(--text);font-size:14px;
  list-style:none;outline:none;line-height:1.5}
.mc-decision-card summary::-webkit-details-marker{display:none}
.mc-decision-card summary::before{content:"▶ ";color:var(--warn);font-size:12px}
.mc-decision-card[open] summary::before{content:"▼ "}
.mc-decision-body{margin-top:8px;padding-top:8px;border-top:1px dashed var(--border);
  color:var(--muted);font-size:13px}
.mc-decision-body button{background:var(--accent);color:#0b1017;border:none;
  padding:10px 18px;border-radius:6px;font-size:14px;cursor:pointer;
  margin-top:8px;font-weight:600;min-height:44px;min-width:48px}
.mc-blocker{color:var(--alert)}.mc-done{color:var(--ok)}.mc-progress{color:var(--warn)}
.mc-empty{color:var(--muted);font-style:italic;font-size:13px}

/* Panel grid */
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}
.panel{background:var(--panel);border:1px solid var(--border);
  border-radius:10px;padding:14px 16px;min-width:0}
.kv{display:grid;grid-template-columns:max-content 1fr;gap:6px 14px;font-size:14px}
.kv .k{color:var(--muted)}.kv .v{color:var(--text);word-break:break-word}
.kv .v.ok{color:var(--ok)}.kv .v.warn{color:var(--warn)}.kv .v.alert{color:var(--alert)}

/* Branch list */
.branch{border-left:3px solid var(--border);padding:8px 12px;margin-bottom:8px}
.branch .num{color:var(--accent);font-weight:700}
.branch .title{color:var(--text);font-size:14px}
.branch .first{color:var(--muted);font-size:12px;margin-top:3px}
.branch.deadline{border-left-color:var(--alert)}

/* Collapsed technical details */
details.tech{background:var(--panel2);border:1px solid var(--border);
  border-radius:6px;padding:8px 12px;margin-top:10px;font-size:13px}
details.tech summary{cursor:pointer;color:var(--muted);font-size:12px;
  outline:none;list-style:none;padding:4px 0;min-height:32px}
details.tech summary::-webkit-details-marker{display:none}
details.tech summary::before{content:"▶ ";color:var(--muted);font-size:10px}
details.tech[open] summary::before{content:"▼ "}
details.tech pre{background:#080d12;border:1px solid var(--border);
  border-radius:4px;padding:8px;overflow:auto;max-height:200px;
  font-size:11px;color:#9aa4ae;white-space:pre-wrap;word-break:break-word}

ul{margin:0;padding-left:20px}li{margin-bottom:4px}
.pill{display:inline-block;padding:2px 10px;border-radius:12px;
  font-size:12px;font-weight:600}
.pill.ok{background:rgba(63,185,80,0.15);color:var(--ok)}
.pill.warn{background:rgba(210,153,34,0.15);color:var(--warn)}
.pill.alert{background:rgba(248,81,73,0.15);color:var(--alert)}
.muted{color:var(--muted)}
footer{margin:20px 0 8px 0;color:var(--muted);font-size:11px;text-align:center}

/* Mobile: stack hero, collapse gaps */
@media (max-width:600px){
  .wrap{padding:12px}
  body{font-size:15px}
  h1{font-size:19px}
  .hero{grid-template-columns:1fr;gap:8px}
  .hero .card{min-height:80px;padding:12px}
  .hero .card .value{font-size:26px}
  .mc-grid,.grid{grid-template-columns:1fr}
}
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def esc(value: Any) -> str:
    if value is None:
        return "N/A"
    return html.escape(str(value), quote=True)


def _kv_row(pairs: list[tuple[str, str, str]]) -> str:
    """Build a <div class='kv'> from (label, value_html, value_css_cls) tuples."""
    rows = "".join(
        f"<div class='k'>{esc(k)}</div>"
        f"<div class='v{(' ' + c) if c else ''}'>{v}</div>"
        for k, v, c in pairs
    )
    return f"<div class='kv'>{rows}</div>"


def load_state() -> dict[str, Any]:
    try:
        return json.loads(IN_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _fmt_ts_taipei(ts_str: Any) -> str:
    if not ts_str or ts_str == "N/A":
        return "N/A"
    try:
        ts = datetime.fromisoformat(str(ts_str).replace("Z", "+00:00"))
    except ValueError:
        return str(ts_str)
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=TPE)
    return ts.astimezone(TPE).strftime("%Y-%m-%d %H:%M (Taipei)")


def _rel_time(ts_str: str) -> str:
    if not ts_str:
        return ""
    try:
        ts = datetime.fromisoformat(str(ts_str).replace("Z", "+00:00"))
    except ValueError:
        return ""
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=TPE)
    secs = int((datetime.now(TPE) - ts).total_seconds())
    if secs < 60:
        return "剛剛"
    if secs < 3600:
        return f"{secs // 60} 分鐘前"
    if secs < 86400:
        return f"{secs // 3600} 小時前"
    return f"{secs // 86400} 天前"


# ---------------------------------------------------------------------------
# Hero metrics — 3 big numbers at the top
# ---------------------------------------------------------------------------


def _compute_hero(state: dict[str, Any]) -> list[tuple[str, str, str]]:
    """Return three (label, value, color_cls) tuples for hero cards.

    Card 1: 永生狀態 (overall health)
    Card 2: 主腦在線 (daemon online?)
    Card 3: 待你動作 (pending human decisions)
    """
    daemon = state.get("daemon") or {}
    b6 = state.get("b6_streak") or {}
    mc = state.get("mission_control") or {}
    blockers = state.get("blockers") or []

    # Card 2: daemon
    daemon_ok = bool(daemon.get("available"))
    daemon_label = "在線" if daemon_ok else "離線"
    daemon_cls = "ok" if daemon_ok else "alert"

    # Card 3: pending
    pending_items = (mc.get("pending") or [])
    approval_items = (mc.get("pending_approval") or [])
    pending_n = len(pending_items) + len(approval_items) + len(blockers)
    pending_value = f"{pending_n} 件" if pending_n > 0 else "0"
    pending_cls = pending_count_color(pending_n)

    # Card 1: overall — synthesise from daemon + trading + blockers
    trading = state.get("trading_engine") or {}
    trading_ok = bool(trading.get("available"))
    pnl = trading.get("total_pnl_pct")
    has_alert = (not daemon_ok) or (isinstance(pnl, (int, float)) and pnl < -1.0)
    if has_alert:
        overall_label, overall_cls = "異常", "alert"
    elif not daemon_ok or not trading_ok:
        overall_label, overall_cls = "注意", "warn"
    elif pending_n > 5:
        overall_label, overall_cls = "要你看", "warn"
    else:
        _ = b6.get("streak") if isinstance(b6, dict) else None
        overall_label, overall_cls = "健康", "ok"

    return [
        ("數位永生狀態", overall_label, overall_cls),
        ("主腦", daemon_label, daemon_cls),
        ("待你動作", pending_value, pending_cls),
    ]


def render_hero(state: dict[str, Any]) -> str:
    cards = _compute_hero(state)
    parts = [
        f"<div class='card {cls}'><div class='label'>{esc(label)}</div>"
        f"<div class='value'>{esc(value)}</div></div>"
        for label, value, cls in cards
    ]
    return f"<div class='hero'>{''.join(parts)}</div>"


# ---------------------------------------------------------------------------
# Red alert banner
# ---------------------------------------------------------------------------


def render_alert_banner(state: dict[str, Any]) -> str:
    alerts: list[str] = []
    daemon = state.get("daemon") or {}
    if not daemon.get("available"):
        alerts.append("主腦離線 — 請檢查 daemon 是否還活著")
    trading = state.get("trading_engine") or {}
    pnl = trading.get("total_pnl_pct")
    if isinstance(pnl, (int, float)) and pnl < -1.0:
        alerts.append(f"交易損益 {pnl:+.2f}% — 超過警戒線")
    if not alerts:
        return ""
    items = "".join(f"<li>{esc(a)}</li>" for a in alerts)
    return f"<div class='banner'>⚠ 需要立刻注意<ul>{items}</ul></div>"


# ---------------------------------------------------------------------------
# 永生樹
# ---------------------------------------------------------------------------


def render_tree(state: dict[str, Any]) -> str:
    branches = (state.get("tree") or {}).get("branches") or []
    if not branches:
        return "<p class='muted'>永生樹尚未載入</p>"
    out = []
    for b in branches:
        title = str(b.get("title") or "")
        cls = "branch deadline" if "DEADLINE" in title else "branch"
        clean_first = friendly_branch_first_line(str(b.get("first") or ""))
        out.append(
            f"<div class='{cls}'><div><span class='num'>{esc(b.get('num'))}.</span> "
            f"<span class='title'>{esc(title)}</span></div>"
            f"<div class='first'>{esc(clean_first)}</div></div>"
        )
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 交易狀態 (plain language)
# ---------------------------------------------------------------------------


def render_trading(state: dict[str, Any]) -> str:
    engine = state.get("trading_engine") or {}
    if not engine.get("available"):
        return "<p class='muted'>交易引擎：休眠中</p>"

    status_line = engine_status_zh(engine)
    pnl_val = engine.get("total_pnl_pct", 0)
    pairs = [
        (label_zh("mode") or "模式",
         esc(to_plain_zh("mode", engine.get("mode"))), ""),
        (label_zh("regime") or "市場狀態",
         esc(to_plain_zh("regime", engine.get("regime"))), ""),
        (label_zh("price") or "BTC 現價",
         esc(to_plain_zh("price", engine.get("price"))), ""),
        (label_zh("active_strategies") or "運作策略",
         esc(engine.get("active_strategies")), ""),
        (label_zh("total_pnl_pct") or "今日損益",
         esc(to_plain_zh("total_pnl_pct", pnl_val)), pnl_color(pnl_val)),
        (label_zh("last_tick") or "最後心跳",
         esc(_rel_time(str(engine.get("last_tick") or "")))
         or esc(engine.get("last_tick")),
         "muted"),
    ]
    main_kv = _kv_row(pairs)

    d = engine.get("disabled") or {}
    if d:
        n = len(d)
        reasons = sorted({str(v).split("<")[0].strip() for v in d.values()})
        reason_text = "、".join(reasons) if reasons else "獲利不達標"
        disabled_block = (
            f"<details class='tech'><summary>{n} 個策略休眠中（{esc(reason_text)}）</summary>"
            "<ul>"
            + "".join(
                f"<li class='muted'>{esc(k)}：{esc(v)}</li>" for k, v in d.items()
            )
            + "</ul></details>"
        )
    else:
        disabled_block = ""

    paper = state.get("paper_pnl") or {}
    if paper.get("available"):
        paper_block = (
            "<div class='kv' style='margin-top:10px'>"
            "<div class='k'>模擬交易損益</div>"
            f"<div class='v ok'>{esc(paper.get('pnl'))}</div></div>"
        )
    else:
        paper_block = ""

    rules = state.get("execution_rules") or {}
    kill_block = ""
    if rules.get("available"):
        lk = rules.get("last_kill") or {}
        kill_rows = [
            ("停用門檻：獲利因子", esc(rules.get("kill_min_pf", "-"))),
            ("停用門檻：勝率", esc(rules.get("kill_min_wr", "-"))),
            ("停用門檻：最大回撤",
             esc(rules.get("kill_max_dd", "-")) + "%"),
            ("累計停用次數", esc(rules.get("kill_count", "-"))),
            ("最近停用",
             f"{esc(lk.get('strategy'))}（{esc(lk.get('reason'))}）"),
        ]
        inner_kv = "".join(
            f"<div class='k'>{k}</div><div class='v'>{v}</div>"
            for k, v in kill_rows
        )
        kill_block = (
            "<details class='tech'><summary>技術細節：停用規則</summary>"
            f"<div class='kv' style='margin-top:6px'>{inner_kv}</div></details>"
        )

    return (
        f"<p style='margin:0 0 10px 0;font-size:14px;color:var(--text)'>"
        f"{esc(status_line)}</p>"
        + main_kv + paper_block + disabled_block + kill_block
    )


# ---------------------------------------------------------------------------
# 主腦健康 (daemon)
# ---------------------------------------------------------------------------


def render_daemon(state: dict[str, Any]) -> str:
    daemon = state.get("daemon") or {}
    streak = state.get("b6_streak") or {}
    insights = state.get("insight_count", 0)
    label, cls = daemon_health_zh(daemon, streak)
    last_cycle = daemon.get("last_cycle") if daemon.get("available") else None

    pairs = [
        ("主腦健康",
         f"<span class='pill {cls}'>{esc(label)}</span>", ""),
        ("今天更新次數",
         esc(last_cycle) if last_cycle is not None else "N/A", ""),
        ("累積心得", f"{esc(insights)} 條", ""),
    ]
    head = _kv_row(pairs)

    tail = daemon.get("tail") or []
    tail_text = "\n".join(tail[-15:]) if tail else ""
    tail_html = (
        "<details class='tech'><summary>技術細節：主腦執行紀錄</summary>"
        f"<pre>{esc(tail_text)}</pre></details>"
        if tail_text else ""
    )
    return head + tail_html


# ---------------------------------------------------------------------------
# 主腦負載 (agent metrics — collapsed by default)
# ---------------------------------------------------------------------------


def render_agent(state: dict[str, Any]) -> str:
    m = state.get("agent_metrics") or {}
    if not m.get("available"):
        return "<p class='muted'>主腦負載資料尚未載入</p>"
    ctx = m.get("context_pct", 0)
    ram = m.get("ram_used_pct", 0)
    cost = m.get("cost_usd", 0)

    def _thresh(v: Any, good: float, warn: float) -> str:
        if not isinstance(v, (int, float)):
            return ""
        return "ok" if v < good else ("warn" if v < warn else "alert")

    pairs = [
        (label_zh("model") or "主腦型號", esc(m.get("model")), ""),
        (label_zh("context_pct") or "記憶使用",
         esc(to_plain_zh("context_pct", ctx)), _thresh(ctx, 60, 85)),
        (label_zh("ram_used_pct") or "記憶體",
         esc(to_plain_zh("ram_used_pct", ram)), _thresh(ram, 70, 90)),
        (label_zh("cost_usd") or "今日花費",
         esc(to_plain_zh("cost_usd", cost)), ""),
    ]
    pairs = [p for p in pairs if p[0]]
    main_kv = _kv_row(pairs)

    extras = {
        k: v
        for k, v in m.items()
        if k
        not in ("available", "model", "context_pct", "ram_used_pct", "cost_usd")
        and not hide_technical(k)
    }
    if extras:
        rows = "".join(
            f"<div class='k'>{esc(k)}</div><div class='v'>{esc(v)}</div>"
            for k, v in extras.items()
        )
        tech = (
            "<details class='tech'><summary>技術細節：主腦原始指標</summary>"
            f"<div class='kv' style='margin-top:6px'>{rows}</div></details>"
        )
    else:
        tech = ""
    return main_kv + tech


# ---------------------------------------------------------------------------
# Recent updates (replaces raw commit SHA dump)
# ---------------------------------------------------------------------------


def render_recent_updates(state: dict[str, Any]) -> str:
    git = state.get("git") or {}
    repos = [
        ("digital-immortality", "數位永生主專案"),
        ("LYH", "DNA / 身份"),
        ("ZP", "知識庫"),
    ]
    items: list[str] = []
    for repo, pretty in repos:
        commits = git.get(repo) or []
        if commits:
            first = str(commits[0])
            parts = first.split(" ", 1)
            desc = parts[1] if len(parts) > 1 else first
            items.append(
                f"<li><strong>{esc(pretty)}</strong>："
                f"{esc(desc[:80])}{'…' if len(desc) > 80 else ''}</li>"
            )
        else:
            items.append(
                f"<li><strong>{esc(pretty)}</strong>："
                "<span class='muted'>尚無更新</span></li>"
            )
    return f"<ul>{''.join(items)}</ul>"


# ---------------------------------------------------------------------------
# 卡住項目 (blockers)
# ---------------------------------------------------------------------------


def render_blockers(state: dict[str, Any]) -> str:
    blockers = state.get("blockers") or []
    if not blockers:
        return "<p class='muted'>目前沒有卡住的事項 ✅</p>"
    lis = "".join(f"<li class='mc-blocker'>⚠ {esc(b)}</li>" for b in blockers)
    return f"<ul>{lis}</ul>"


# ---------------------------------------------------------------------------
# Mission Control (decisions, progress)
# ---------------------------------------------------------------------------


def _mc_pending_card(evt: dict[str, Any]) -> str:
    pretty = esc(evt.get("pretty_msg") or "(無描述)")
    when = esc(_rel_time(evt.get("ts", "")))
    return (
        "<details class='mc-decision-card'>"
        f"<summary>{pretty} <span class='mc-time'>（{when}）</span></summary>"
        "<div class='mc-decision-body'>這件事需要你點頭或給方向。<br>"
        "<form onsubmit='return false'>"
        "<button type='submit' onclick='this.closest(\"details\").open=false'>"
        "我知道了</button>"
        "</form></div></details>"
    )


def _mc_approval_card(item: dict[str, Any]) -> str:
    label_s, title, essence = (
        esc(item.get("label", "")),
        esc(item.get("title", "")),
        esc(item.get("essence", "")),
    )
    return (
        "<details class='mc-decision-card'>"
        f"<summary><strong>{label_s}</strong> — {title}</summary>"
        f"<div class='mc-decision-body'>{essence}<br>"
        "<form onsubmit='return false'>"
        "<button type='submit' onclick='this.closest(\"details\").open=false'>"
        "稍後再看</button>"
        "</form></div></details>"
    )


def _mc_feed_line(evt: dict[str, Any], cls: str, prefix: str = "") -> str:
    when = esc(_rel_time(evt.get("ts", "")))
    actor = esc(evt.get("pretty_actor") or "")
    msg = esc(evt.get("pretty_msg") or "")
    actor_html = f"<span class='mc-actor'>{actor}</span>" if actor else ""
    return (
        f"<div class='mc-item {cls}'><span class='mc-time'>{when}</span>"
        f"{actor_html}{prefix}{msg}</div>"
    )


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
    header = (
        "<div class='mc-header'>"
        "<h2 class='mc-title'>現在發生什麼事</h2>"
        f"<div class='mc-online'><span class='mc-dot {dot_cls}'></span>"
        f"主腦：{esc(online.get('label') or '狀態不明')} {esc(age_str)}</div></div>"
    )
    if (
        not mc.get("available")
        and not mc.get("backlog")
        and not mc.get("pending_approval")
    ):
        return (
            "<section class='mc-wrap'>"
            + header
            + "<p class='mc-empty'>尚無活動 — 主腦還沒寫入任何事件</p></section>"
        )
    pending = mc.get("pending") or []
    in_progress = (mc.get("recent_feed") or mc.get("in_progress") or [])[:8]
    done = (mc.get("done") or [])[:5]
    backlog = (mc.get("backlog") or [])[:5]
    pending_approval = mc.get("pending_approval") or []
    approval_block = (
        (
            "<h3 style='margin-top:14px'>等你批准</h3>"
            + "\n".join(_mc_approval_card(i) for i in pending_approval)
        )
        if pending_approval
        else ""
    )
    backlog_html = (
        "\n".join(
            f"<div class='mc-item'>{i}. {esc(x.get('text', ''))}</div>"
            for i, x in enumerate(backlog, 1)
        )
        if backlog
        else "<p class='mc-empty'>尚未產生</p>"
    )

    def card(title: str, body: str) -> str:
        return f"<div class='mc-card'><h3>{title}</h3>{body}</div>"

    cards = [
        card(
            "待你決策",
            _mc_section(pending, "目前沒有需要你決定的事項 ✅", _mc_pending_card)
            + approval_block,
        ),
        card(
            "進行中",
            _mc_section(
                in_progress,
                "目前沒有進行中的任務",
                lambda e: _mc_feed_line(e, "mc-progress"),
            ),
        ),
        card(
            "剛完成",
            _mc_section(
                done,
                "尚無已完成的任務",
                lambda e: _mc_feed_line(e, "mc-done", "✓ "),
            ),
        ),
        card("自動 backlog", backlog_html),
    ]
    return (
        "<section class='mc-wrap'>"
        + header
        + "<div class='mc-grid'>"
        + "\n".join(cards)
        + "</div></section>"
    )


# ---------------------------------------------------------------------------
# Page assembly
# ---------------------------------------------------------------------------


def render_page(state: dict[str, Any]) -> str:
    updated = state.get("updated_taipei") or state.get("updated_utc") or "unknown"
    if updated and "Taipei" not in str(updated) and "+08" not in str(updated):
        updated = f"{updated} (Taipei, UTC+8)"

    body = f"""
<div class='wrap'>
<h1>數位永生 · 主控台</h1>
<div class='subtitle'>
  更新於 <span class='live'>{esc(updated)}</span>
  · 所有時間 Asia/Taipei (UTC+8)
  · 每 {REFRESH_SECONDS} 秒自動刷新
</div>

{render_hero(state)}
{render_alert_banner(state)}
{render_mission_control(state)}

<div class='grid'>
  <section class='panel'>
    <h2>永生樹 · 7 大分支</h2>
    {render_tree(state)}
  </section>
  <section class='panel'>
    <h2>交易狀態</h2>
    {render_trading(state)}
  </section>
  <section class='panel'>
    <h2>主腦健康</h2>
    {render_daemon(state)}
  </section>
  <section class='panel'>
    <h2>主腦負載</h2>
    {render_agent(state)}
  </section>
  <section class='panel'>
    <h2>最近更新</h2>
    {render_recent_updates(state)}
  </section>
  <section class='panel'>
    <h2>卡住 · 等你動作</h2>
    {render_blockers(state)}
  </section>
</div>

<footer>
  plain-language redesign · mobile-first · stdlib only
  · 翻譯表 platform/pretty_translate.py
</footer>
</div>
"""
    return (
        '<!DOCTYPE html>\n<html lang="zh-Hant">\n<head>\n'
        '<meta charset="utf-8">\n'
        f'<meta http-equiv="refresh" content="{REFRESH_SECONDS}">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>數位永生 · 主控台</title>\n'
        f"<style>{CSS}</style>\n"
        "</head>\n<body>\n"
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
