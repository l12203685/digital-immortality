#!/usr/bin/env python3
"""LINE-bridge Discord feed poller.

Polls the LINE-bridge Discord channels in Edward's Edward AI guild via the
Discord REST API, caches new messages to JSONL, and writes them in a shape
compatible with ``history_indexer.py`` so the FTS index picks them up on the
next run.

Schema written to ``results/line_feed.jsonl``::

    {
        "ts": ISO8601 Taipei,
        "channel_id": str,
        "channel_name": str (LINE bridge display name),
        "author": str (LINE sender name as bot posted it),
        "author_id": str (Discord user id),
        "text": str,
        "attachments_count": int,
        "message_id": str
    }

Additionally each row is written in a **history-indexer compatible** shape to
``C:/Users/admin/GoogleDrive/聊天記錄/jsonl/line_bridge_current.jsonl`` so the
existing ``history_indexer.py`` picks it up (keys: ``ts``, ``g``, ``s``, ``t``).

Cursor is stored in ``results/line_feed_cursor.json`` keyed by channel id.
Re-runs are safe — ``?after=`` is passed to Discord's REST API so only new
messages are fetched.

Usage::

    python line_feed_poller.py              # one poll cycle

Schedule::

    schtasks /Create /SC MINUTE /MO 10 /TN "mc_line_feed" ^
        /TR "pythonw C:\\Users\\admin\\workspace\\digital-immortality\\platform\\line_feed_poller.py" /F
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

# WSL-safe path translation: Windows C:/ paths resolve to /mnt/c/ under WSL.
IS_WSL = (sys.platform == "linux" and os.path.exists("/mnt/c"))


def _win_to_posix(p: str) -> str:
    """Translate Windows drive paths to /mnt/<drive>/ under WSL."""
    if not IS_WSL or not p:
        return p
    q = p.replace("\\", "/")
    if len(q) >= 2 and q[1] == ":" and q[0].isalpha():
        return f"/mnt/{q[0].lower()}{q[2:]}"
    return q


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PLATFORM_DIR = Path(__file__).resolve().parent
REPO_DIR = PLATFORM_DIR.parent
RESULTS_DIR = REPO_DIR / "results"

BOT_TOKEN_FILE = Path(_win_to_posix("C:/Users/admin/.claude/credentials/discord_bots.json"))
CHANNELS_YAML = RESULTS_DIR / "line_feed_channels.yaml"
CURSOR_FILE = RESULTS_DIR / "line_feed_cursor.json"
FEED_JSONL = RESULTS_DIR / "line_feed.jsonl"
LOG_PATH = RESULTS_DIR / "line_feed_poller.log"

# Mirror into the existing JSONL archive so history_indexer.py picks it up
HISTORY_ARCHIVE_DIR = Path(_win_to_posix("C:/Users/admin/GoogleDrive/聊天記錄/jsonl"))
HISTORY_ARCHIVE_FILE = HISTORY_ARCHIVE_DIR / "line_bridge_current.jsonl"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GUILD_ID = "1152835528991981568"
DISCORD_API = "https://discord.com/api/v10"
POLL_LIMIT = 50
TAIPEI = ZoneInfo("Asia/Taipei")
USER_AGENT = "EdwardMissionControl-LineFeedPoller/1.0"

# The 6 LINE-bridge channels Edward wants consolidated.
# Source: workspace/discord_channel_audit_2026-04-11.md
DEFAULT_CHANNELS: list[dict[str, str]] = [
    {"id": "1489808537629753375", "name": "買凹扛神教"},
    {"id": "1489835545554321519", "name": "探險華寶"},
    {"id": "1489942603347660850", "name": "home-家庭"},
    {"id": "1489841737634414802", "name": "羽球筆記"},
    {"id": "1491659901347430431", "name": "阿瓦隆百科"},
    {"id": "1492155205402234880", "name": "一起排擠胖子"},
]


# ---------------------------------------------------------------------------
# Logging (NEVER log the bot token)
# ---------------------------------------------------------------------------


def setup_logging() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------


def load_bot_token() -> str:
    """Read the E1 bot token from the credentials file.

    The file looks like ``{"E1": {"token": "...", ...}, "E2": {...}}``.
    """
    if not BOT_TOKEN_FILE.exists():
        raise FileNotFoundError(f"discord_bots.json not found: {BOT_TOKEN_FILE}")
    data = json.loads(BOT_TOKEN_FILE.read_text(encoding="utf-8"))
    # Prefer E1, then E2, then any first entry with a token field.
    for key in ("E1", "e1", "E2", "e2"):
        entry = data.get(key)
        if isinstance(entry, dict) and entry.get("token"):
            return str(entry["token"])
    for entry in data.values():
        if isinstance(entry, dict) and entry.get("token"):
            return str(entry["token"])
    if isinstance(data.get("bot_token"), str):
        return data["bot_token"]
    raise KeyError("no bot token found in discord_bots.json")


def _write_default_channels_yaml() -> None:
    lines = [
        "# LINE-bridge Discord channels consolidated by line_feed_poller.py",
        "# Autogenerated. Edit to add/remove channels.",
        "channels:",
    ]
    for ch in DEFAULT_CHANNELS:
        lines.append(f"  - id: \"{ch['id']}\"")
        lines.append(f"    name: \"{ch['name']}\"")
    CHANNELS_YAML.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logging.info("wrote default channels yaml: %s", CHANNELS_YAML)


def load_channels() -> list[dict[str, str]]:
    """Load channel list from YAML, falling back to DEFAULT_CHANNELS.

    We parse a tiny YAML subset ourselves to avoid a PyYAML dependency.
    """
    if not CHANNELS_YAML.exists():
        _write_default_channels_yaml()
        return list(DEFAULT_CHANNELS)
    channels: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for raw in CHANNELS_YAML.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- id:"):
            if current:
                channels.append(current)
            current = {"id": line.split(":", 1)[1].strip().strip('"').strip("'")}
        elif line.startswith("id:"):
            current["id"] = line.split(":", 1)[1].strip().strip('"').strip("'")
        elif line.startswith("name:"):
            current["name"] = line.split(":", 1)[1].strip().strip('"').strip("'")
    if current:
        channels.append(current)
    # Drop malformed rows
    channels = [c for c in channels if c.get("id")]
    if not channels:
        logging.warning("channels yaml produced no rows; using defaults")
        return list(DEFAULT_CHANNELS)
    return channels


def load_cursor() -> dict[str, str]:
    if not CURSOR_FILE.exists():
        return {}
    try:
        return json.loads(CURSOR_FILE.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        logging.warning("failed to parse cursor file: %s", exc)
        return {}


def save_cursor(cursor: dict[str, str]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    CURSOR_FILE.write_text(json.dumps(cursor, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Discord REST
# ---------------------------------------------------------------------------


def _discord_get(path: str, token: str) -> tuple[int, bytes, dict[str, str]]:
    url = f"{DISCORD_API}{path}"
    req = Request(
        url,
        headers={
            "Authorization": f"Bot {token}",
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(req, timeout=30) as resp:
            body = resp.read()
            headers = {k.lower(): v for k, v in resp.headers.items()}
            return resp.status, body, headers
    except HTTPError as exc:
        body = exc.read() if hasattr(exc, "read") else b""
        headers = {k.lower(): v for k, v in (exc.headers.items() if exc.headers else [])}
        return exc.code, body, headers


def fetch_messages(
    channel_id: str, token: str, after: str | None
) -> list[dict[str, Any]]:
    """Fetch up to POLL_LIMIT messages newer than ``after`` (Snowflake ID).

    Discord returns messages newest-first by default, but when ``after`` is
    supplied it returns them ordered *oldest* to newest (API quirk). We always
    return the list sorted by message id ascending so we can iterate
    chronologically.
    """
    query = f"?limit={POLL_LIMIT}"
    if after:
        query += f"&after={after}"
    for attempt in range(5):
        status, body, headers = _discord_get(
            f"/channels/{channel_id}/messages{query}", token
        )
        if status == 200:
            rows = json.loads(body.decode("utf-8"))
            rows.sort(key=lambda m: int(m.get("id", 0)))
            return rows
        if status == 429:
            try:
                retry_after = float(json.loads(body.decode("utf-8")).get("retry_after", 1))
            except Exception:  # noqa: BLE001
                retry_after = float(headers.get("retry-after", "1"))
            logging.warning(
                "rate limited on channel %s; sleeping %.2fs", channel_id, retry_after
            )
            time.sleep(min(retry_after + 0.1, 30))
            continue
        if status in (500, 502, 503, 504):
            logging.warning(
                "transient %d on channel %s; backoff", status, channel_id
            )
            time.sleep(2 ** attempt)
            continue
        logging.error(
            "discord GET channel %s failed status=%d body=%s",
            channel_id,
            status,
            body[:200].decode("utf-8", errors="replace"),
        )
        return []
    logging.error("giving up on channel %s after retries", channel_id)
    return []


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


def _to_taipei_iso(discord_ts: str) -> str:
    """Convert Discord ISO8601 timestamp to Taipei ISO8601."""
    try:
        # Discord returns "2024-01-02T03:04:05.123456+00:00"
        dt = datetime.fromisoformat(discord_ts.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(TAIPEI).isoformat(timespec="seconds")
    except Exception:  # noqa: BLE001
        return discord_ts


def _extract_line_author(msg: dict[str, Any]) -> str:
    """The LINE-bridge bot posts each LINE sender as a webhook username.

    Author is always the bot name if we read ``author.username``; the real
    LINE sender lives in ``author.global_name`` / ``author.display_name`` OR
    the text body of the message. We try username first (webhook-style), then
    fall back gracefully.
    """
    author = msg.get("author") or {}
    if not isinstance(author, dict):
        return ""
    # Webhook name typically holds the LINE sender display name.
    return (
        author.get("global_name")
        or author.get("display_name")
        or author.get("username")
        or ""
    )


def build_row(
    msg: dict[str, Any], channel_id: str, channel_name: str
) -> dict[str, Any]:
    content = msg.get("content") or ""
    attachments = msg.get("attachments") or []
    return {
        "ts": _to_taipei_iso(msg.get("timestamp", "")),
        "channel_id": channel_id,
        "channel_name": channel_name,
        "author": _extract_line_author(msg),
        "author_id": str((msg.get("author") or {}).get("id", "")),
        "text": content,
        "attachments_count": len(attachments) if isinstance(attachments, list) else 0,
        "message_id": str(msg.get("id", "")),
    }


def append_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_indexer_rows(rows: list[dict[str, Any]]) -> None:
    """Mirror rows into the history-indexer JSONL archive.

    history_indexer.py uses keys ``ts``, ``g`` (group), ``s`` (sender),
    ``t`` (text). We write a dedicated ``line_bridge_current.jsonl`` file in
    the archive dir so the indexer treats it as a new source file and picks
    it up on the next incremental run.
    """
    if not rows:
        return
    if not HISTORY_ARCHIVE_DIR.exists():
        logging.warning(
            "history archive dir missing, skipping mirror: %s", HISTORY_ARCHIVE_DIR
        )
        return
    with HISTORY_ARCHIVE_FILE.open("a", encoding="utf-8") as f:
        for row in rows:
            mirror = {
                "ts": row["ts"],
                "g": row["channel_name"],
                "s": row["author"],
                "t": row["text"],
            }
            f.write(json.dumps(mirror, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Main poll loop
# ---------------------------------------------------------------------------


def poll_once() -> dict[str, int]:
    channels = load_channels()
    cursor = load_cursor()
    token = load_bot_token()

    stats: dict[str, int] = {}
    total_new = 0

    for ch in channels:
        cid = ch["id"]
        cname = ch.get("name", cid)
        after = cursor.get(cid)
        logging.info("polling channel %s (%s) after=%s", cname, cid, after or "-")
        msgs = fetch_messages(cid, token, after)
        if not msgs:
            stats[cname] = 0
            continue
        rows = [build_row(m, cid, cname) for m in msgs]
        append_jsonl(FEED_JSONL, rows)
        write_indexer_rows(rows)
        # Cursor = highest message id we've seen.
        max_id = max(int(m.get("id", 0)) for m in msgs)
        cursor[cid] = str(max_id)
        stats[cname] = len(rows)
        total_new += len(rows)
        logging.info("  got %d new messages from %s", len(rows), cname)
        # Gentle pacing between channels.
        time.sleep(0.3)

    save_cursor(cursor)
    logging.info("poll complete: total_new=%d per_channel=%s", total_new, stats)
    return stats


def main() -> int:
    setup_logging()
    try:
        poll_once()
    except FileNotFoundError as exc:
        logging.error("config missing: %s", exc)
        return 2
    except URLError as exc:
        logging.error("network error: %s", exc)
        return 3
    except Exception as exc:  # noqa: BLE001
        logging.exception("unexpected error: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
