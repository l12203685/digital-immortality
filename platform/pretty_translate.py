"""pretty_translate.py — Technical-to-plain-Chinese translation layer.

Shared vocabulary between render_dashboard.py (GitHub Pages) and the Local
Mission Control web (index.html mirrors a subset of this in JS).

Core idea: Edward's mom should understand every string on the dashboard.
No English technical terms, no commit SHAs, no PF/WR/MDD, no kill_window.

Usage:
    from pretty_translate import to_plain_zh, label_zh, hide_technical

    label_zh("kill_window")      -> None   (hidden)
    label_zh("total_pnl_pct")    -> "今日損益"
    to_plain_zh("mode", "PAPER") -> "模擬（未實單）"
"""
from __future__ import annotations

from typing import Any

# --- Field label translation ------------------------------------------------
# Maps technical field name -> plain Chinese label.
# Returns None means: HIDE this field (too technical for the dashboard).

LABELS_ZH: dict[str, str | None] = {
    # trading engine
    "mode": "模式",
    "regime": "市場狀態",
    "price": "BTC 現價",
    "tick_count": "累計心跳",
    "active": "運作策略",
    "active_strategies": "運作策略",
    "disabled": "休眠策略",
    "total_pnl": "今日損益",
    "total_pnl_pct": "今日損益",
    "last_tick": "最後心跳",
    "pnl": "損益",
    "tick": "模擬次數",
    # kill-window internals — all hidden
    "kill_window": None,
    "kill_count": None,
    "min_pf": None,
    "min_wr": None,
    "max_dd": None,
    "kill_min_pf": None,
    "kill_min_wr": None,
    "kill_max_dd": None,
    "last_kill": None,
    "evolved_at": None,
    # daemon
    "last_cycle": "今天更新次數",
    "cycle_count": "今天更新次數",
    "b6_streak": "DNA 一致性",
    "insights": "累積心得",
    "insight_count": "累積心得",
    # agent metrics — mostly hidden, only a few exposed
    "model": "主腦型號",
    "git_branch": None,
    "tokens_in": None,
    "tokens_out": None,
    "tokens_cached": None,
    "context_pct": "記憶使用",
    "cost_usd": "今日花費",
    "ram_used": "記憶體",
    "ram_used_pct": "記憶體",
    "ramdisk_free": None,
    "ram_disk_free_mb": None,
    "metrics_ts": None,
    "ts": None,
}

# Fields that should be hidden entirely from the main view.
HIDDEN_FIELDS = frozenset(k for k, v in LABELS_ZH.items() if v is None)


def label_zh(key: str) -> str | None:
    """Translate a technical field name to plain Chinese.

    Returns None if the field is marked as technical/hidden.
    Unknown keys fall through unchanged (so we never silently drop data).
    """
    if key in LABELS_ZH:
        return LABELS_ZH[key]
    return key


def hide_technical(key: str) -> bool:
    """True if this field should NOT appear on the main dashboard."""
    return key in HIDDEN_FIELDS


# --- Value translation ------------------------------------------------------

_MODE_ZH = {
    "PAPER": "模擬（未實單）",
    "LIVE": "真金實彈",
    "DRY": "乾跑",
    "DRY_RUN": "乾跑",
}

_REGIME_ZH = {
    "mixed": "混亂",
    "trend": "趨勢",
    "range": "盤整",
    "volatile": "高波動",
    "calm": "平穩",
}


def to_plain_zh(key: str, value: Any) -> str:
    """Translate a value given its key's semantics.

    Used for enum-like fields (mode, regime) and number formatting.
    """
    if value is None:
        return "N/A"
    if key == "mode":
        return _MODE_ZH.get(str(value).upper(), str(value))
    if key == "regime":
        return _REGIME_ZH.get(str(value).lower(), str(value))
    if key in ("total_pnl", "total_pnl_pct"):
        if isinstance(value, (int, float)):
            return f"{value:+.2f}%"
        return str(value)
    if key == "price":
        if isinstance(value, (int, float)):
            return f"${value:,.0f}"
        return f"${value}"
    if key == "cost_usd":
        if isinstance(value, (int, float)):
            return f"${value:.2f}"
        return f"${value}"
    if key in ("context_pct", "ram_used", "ram_used_pct"):
        if isinstance(value, (int, float)):
            return f"{value}%"
        return str(value)
    return str(value)


# --- High-level status translation -----------------------------------------

def engine_status_zh(engine: dict) -> str:
    """One-line plain-Chinese summary of the trading engine state."""
    if not engine or not engine.get("available"):
        return "交易策略：休眠中"
    active = engine.get("active_strategies", 0)
    if active == 0:
        return "交易策略：全部休眠"
    mode = _MODE_ZH.get(str(engine.get("mode", "")).upper(), "運作中")
    return f"交易策略：{mode}（{active} 個運作中）"


def daemon_health_zh(daemon: dict, b6_streak: dict) -> tuple[str, str]:
    """Returns (plain_label, color_class) describing daemon health.

    color_class is one of: 'ok' | 'warn' | 'alert'.
    """
    if not daemon or not daemon.get("available"):
        return ("主腦：離線", "alert")
    streak = (b6_streak or {}).get("streak")
    if streak and isinstance(streak, int) and streak >= 1:
        return (f"主腦：健康（DNA 連續 {streak} 次正常）", "ok")
    return ("主腦：在線", "ok")


def pending_count_color(n: int) -> str:
    if n <= 0:
        return "ok"
    if n <= 3:
        return "warn"
    return "alert"


def pnl_color(pnl: Any) -> str:
    if not isinstance(pnl, (int, float)):
        return "muted"
    if pnl > 0:
        return "ok"
    if pnl < -0.5:
        return "alert"
    return "warn"


# --- Commit / log line translation -----------------------------------------

def friendly_branch_first_line(first: str) -> str:
    """Drop parenthesized raw blobs from `first` lines so Edward sees intent.

    Example:
      "1.1 Trading system → live profit (cycle 201: header updated ... )"
      -> "1.1 Trading system → live profit"
    """
    if not first:
        return ""
    cut = first.find("(")
    if 0 <= cut <= 80:
        return first[:cut].rstrip(" -—·")
    # Also truncate very long first-lines
    if len(first) > 80:
        return first[:77] + "…"
    return first
