"""Dashboard -> Discord inbox bridge.

Tails C:\\Users\\admin\\staging\\web_inbox.jsonl and forwards new dashboard
entries (channel == "web_mc" or "web_mc_button") to Discord channel e0 via the
E1 bot REST API, so Edward's main Claude session sees them naturally.

Cursor-based dedupe. stdlib only. Never logs the bot token.

Usage:
    python inbox_bridge.py                  # one-shot tick (default)
    python inbox_bridge.py --watch          # polling loop, 60s interval
    python inbox_bridge.py --replay-all     # ignore cursor, replay from start
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

# --- Paths -----------------------------------------------------------------

INBOX_PATH = Path(r"C:\Users\admin\staging\web_inbox.jsonl")
CURSOR_PATH = Path(r"C:\Users\admin\staging\web_inbox_bridge_cursor.json")
LOG_PATH = Path(r"C:\Users\admin\workspace\digital-immortality\results\inbox_bridge.log")
CREDENTIALS_PATH = Path(r"C:\Users\admin\.claude\credentials\discord_bots.json")

# --- Constants -------------------------------------------------------------

DISCORD_API = "https://discord.com/api/v10"
E0_CHANNEL_ID = "1488348699968012510"
FORWARDABLE_CHANNELS = {"web_mc", "web_mc_button"}
MAX_PER_TICK = 10
POLL_INTERVAL_S = 60
TAIPEI = timezone(timedelta(hours=8))

# --- Logging ---------------------------------------------------------------

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stderr),
    ],
)
log = logging.getLogger("inbox_bridge")


# --- Helpers ---------------------------------------------------------------


def load_bot_token() -> str:
    """Load the E1 bot token. Never log this value."""
    with CREDENTIALS_PATH.open("r", encoding="utf-8") as f:
        creds = json.load(f)
    token = creds["E1"]["token"]
    if not isinstance(token, str) or not token:
        raise RuntimeError("E1 bot token missing or invalid")
    return token


def read_inbox_entries() -> list[dict[str, Any]]:
    """Read all entries from the inbox file, skipping malformed lines."""
    if not INBOX_PATH.exists():
        return []
    entries: list[dict[str, Any]] = []
    with INBOX_PATH.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as e:
                log.warning("malformed inbox line %d: %s", i, e)
    return entries


def read_cursor() -> str | None:
    """Return last-forwarded ts, or None if no cursor yet."""
    if not CURSOR_PATH.exists():
        return None
    try:
        with CURSOR_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        ts = data.get("last_ts")
        return ts if isinstance(ts, str) else None
    except (json.JSONDecodeError, OSError) as e:
        log.warning("cursor read failed, treating as absent: %s", e)
        return None


def write_cursor(last_ts: str) -> None:
    """Atomically update the cursor file (immutable pattern: write tmp, rename)."""
    tmp = CURSOR_PATH.with_suffix(".json.tmp")
    payload = {
        "last_ts": last_ts,
        "updated_at": datetime.now(TAIPEI).isoformat(),
    }
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    tmp.replace(CURSOR_PATH)


def initialize_cursor_to_tail() -> str | None:
    """On first run, set cursor to the ts of the last existing entry.

    Returns the ts written (or None if inbox empty).
    """
    entries = read_inbox_entries()
    if not entries:
        log.info("inbox empty on init; no cursor written")
        return None
    last_ts = entries[-1].get("ts")
    if not isinstance(last_ts, str):
        log.warning("last entry has no ts; skipping cursor init")
        return None
    write_cursor(last_ts)
    log.info("cursor initialized to tail ts=%s (skipped %d existing entries)", last_ts, len(entries))
    return last_ts


def select_new_entries(
    entries: list[dict[str, Any]],
    cursor_ts: str | None,
    replay_all: bool,
) -> list[dict[str, Any]]:
    """Return forwardable entries strictly after the cursor ts."""
    out: list[dict[str, Any]] = []
    for e in entries:
        ch = e.get("channel")
        if ch not in FORWARDABLE_CHANNELS:
            continue
        ts = e.get("ts")
        if not isinstance(ts, str):
            continue
        if not replay_all and cursor_ts is not None and ts <= cursor_ts:
            continue
        out.append(e)
    return out


def format_message(entry: dict[str, Any]) -> str:
    """Build the forwarded message body."""
    ts_raw = entry.get("ts", "")
    hhmm = "??:??"
    try:
        dt = datetime.fromisoformat(ts_raw)
        dt = dt.astimezone(TAIPEI)
        hhmm = dt.strftime("%H:%M")
    except (ValueError, TypeError):
        pass

    text = entry.get("text", "")
    if not isinstance(text, str):
        text = str(text)

    if entry.get("channel") == "web_mc_button":
        return f"[from dashboard button @ {hhmm}] {text}"
    return f"[from dashboard @ {hhmm}] {text}"


def post_to_discord(token: str, channel_id: str, content: str) -> tuple[bool, int, str]:
    """POST a message to Discord. Returns (success, status_code, error_detail)."""
    url = f"{DISCORD_API}/channels/{channel_id}/messages"
    body = json.dumps({"content": content}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bot {token}",
            "Content-Type": "application/json",
            "User-Agent": "edward-inbox-bridge/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return True, resp.status, ""
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode("utf-8", errors="replace")[:500]
        except Exception:
            pass
        # Handle 429 rate limit: sleep and report failure so caller doesn't advance cursor
        if e.code == 429:
            try:
                data = json.loads(detail) if detail else {}
                retry_after = float(data.get("retry_after", 1.0))
            except (ValueError, TypeError):
                retry_after = 1.0
            log.warning("rate limited; sleeping %.2fs", retry_after)
            time.sleep(min(retry_after, 10.0))
        return False, e.code, detail
    except urllib.error.URLError as e:
        return False, 0, str(e.reason)
    except Exception as e:  # noqa: BLE001
        return False, 0, repr(e)


# --- Core tick -------------------------------------------------------------


def run_tick(replay_all: bool = False) -> int:
    """Run one forward cycle. Returns number of messages successfully forwarded."""
    cursor_ts = read_cursor()

    # First-ever run: start from tail so we don't flood Discord with history.
    if cursor_ts is None and not replay_all:
        initialize_cursor_to_tail()
        return 0

    entries = read_inbox_entries()
    new_entries = select_new_entries(entries, cursor_ts, replay_all)

    if not new_entries:
        log.info("tick: 0 new entries (cursor=%s, total=%d)", cursor_ts, len(entries))
        return 0

    # Throttle
    if len(new_entries) > MAX_PER_TICK:
        log.info("tick: %d new entries, throttling to %d", len(new_entries), MAX_PER_TICK)
        new_entries = new_entries[:MAX_PER_TICK]

    token = load_bot_token()
    forwarded = 0
    last_ok_ts: str | None = None

    for entry in new_entries:
        content = format_message(entry)
        ok, status, detail = post_to_discord(token, E0_CHANNEL_ID, content)
        if ok:
            forwarded += 1
            last_ok_ts = entry.get("ts")
            log.info(
                "forwarded ts=%s channel=%s len=%d http=%d",
                last_ok_ts,
                entry.get("channel"),
                len(content),
                status,
            )
            # Small gap to be nice to Discord (they tolerate ~5/sec per channel).
            time.sleep(0.3)
        else:
            log.error(
                "forward failed ts=%s http=%d detail=%s",
                entry.get("ts"),
                status,
                detail,
            )
            # Stop on failure so cursor does not skip past unsent items.
            break

    if last_ok_ts is not None:
        write_cursor(last_ok_ts)
        log.info("cursor advanced to %s (forwarded=%d)", last_ok_ts, forwarded)

    return forwarded


# --- CLI -------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Dashboard -> Discord inbox bridge")
    parser.add_argument("--watch", action="store_true", help="polling loop every 60s")
    parser.add_argument("--replay-all", action="store_true", help="ignore cursor, replay all entries")
    args = parser.parse_args()

    if args.watch:
        log.info("watch mode: polling every %ds", POLL_INTERVAL_S)
        while True:
            try:
                run_tick(replay_all=args.replay_all)
            except Exception as e:  # noqa: BLE001
                log.exception("tick crashed: %s", e)
            time.sleep(POLL_INTERVAL_S)

    try:
        n = run_tick(replay_all=args.replay_all)
        log.info("one-shot done, forwarded=%d", n)
        return 0
    except Exception as e:  # noqa: BLE001
        log.exception("run_tick crashed: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
