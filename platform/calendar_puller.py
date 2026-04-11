#!/usr/bin/env python3
"""Google Calendar puller — authenticated 14-day lookahead.

Pulls upcoming events from the primary calendar via the Google Calendar
API (not the MCP surface, which is unavailable to subagents) and writes
them to ``results/life_calendar.json`` in the schema Mission Control's
``/api/life`` endpoint expects.

Auth model: OAuth 2.0 Desktop-app client. Token is cached under
``~/.claude/credentials/google_calendar_token.json`` and refreshed
automatically. First run needs ``--auth`` so Edward can click "Allow"
once in a browser window.

CLI:
    python calendar_puller.py            # pull + write cache
    python calendar_puller.py --auth     # interactive OAuth flow
    python calendar_puller.py --days 7   # custom window

Cache schema:
    {
      "updated_at": "2026-04-11T09:00:00+08:00",
      "source":     "gcal_primary",
      "events": [
        {
          "start":     "2026-04-11T10:00:00+08:00",
          "end":       "2026-04-11T11:00:00+08:00",
          "title":     "Dr. Wang follow-up",
          "location":  "Taipei Veterans General Hospital",
          "attendees": 0,
          "calendar":  "primary"
        }
      ]
    }

All timestamps are Asia/Taipei per Edward's standing rule.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

TPE = ZoneInfo("Asia/Taipei")
UTC = ZoneInfo("UTC")

REPO = Path("C:/Users/admin/workspace/digital-immortality")
CALENDAR_CACHE = REPO / "results" / "life_calendar.json"

CREDENTIALS_DIR = Path("C:/Users/admin/.claude/credentials")
CLIENT_SECRET = CREDENTIALS_DIR / "google_calendar_client_secret.json"
TOKEN_FILE = CREDENTIALS_DIR / "google_calendar_token.json"
README = CREDENTIALS_DIR / "README_calendar_oauth.md"

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
DEFAULT_DAYS = 14

logger = logging.getLogger("calendar_puller")


# --------------------------------------------------------------------------- #
# Time helpers
# --------------------------------------------------------------------------- #
def _now_iso_tpe() -> str:
    return datetime.now(TPE).isoformat(timespec="seconds")


def _to_tpe_iso(value: str | None) -> str:
    """Convert an RFC3339 timestamp (or YYYY-MM-DD all-day) to Asia/Taipei ISO."""
    if not value:
        return ""
    try:
        if len(value) == 10 and value.count("-") == 2:
            # All-day event. Treat as local date at 00:00 Taipei.
            dt = datetime.fromisoformat(value).replace(tzinfo=TPE)
        else:
            # RFC3339: 2026-04-11T10:00:00+08:00 or ...Z
            normalized = value.replace("Z", "+00:00")
            dt = datetime.fromisoformat(normalized)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
        return dt.astimezone(TPE).isoformat(timespec="seconds")
    except ValueError:
        return value


# --------------------------------------------------------------------------- #
# OAuth
# --------------------------------------------------------------------------- #
def _abort_missing_client_secret() -> None:
    logger.error("client_secret.json missing at %s", CLIENT_SECRET)
    logger.error("See setup instructions: %s", README)
    sys.stderr.write(
        "\n[calendar_puller] OAuth client secret missing.\n"
        f"Expected: {CLIENT_SECRET}\n"
        f"Setup guide: {README}\n"
    )


def _load_credentials(interactive: bool) -> Any | None:
    """Load or mint user credentials for the Calendar API.

    Returns None if auth is impossible (missing client_secret, or token
    absent and ``interactive`` is False).
    """
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds: Credentials | None = None
    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        except Exception as exc:  # noqa: BLE001
            logger.warning("cached token unreadable: %s", exc)
            creds = None

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            _save_token(creds)
            return creds
        except Exception as exc:  # noqa: BLE001
            logger.warning("token refresh failed: %s", exc)
            creds = None

    if not interactive:
        logger.error(
            "no valid token and --auth not supplied; re-run with --auth once",
        )
        return None

    if not CLIENT_SECRET.exists():
        _abort_missing_client_secret()
        return None

    logger.info("starting interactive OAuth flow (browser will open)")
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
    creds = flow.run_local_server(
        port=0,
        prompt="consent",
        access_type="offline",
        open_browser=True,
    )
    _save_token(creds)
    return creds


def _save_token(creds: Any) -> None:
    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    logger.info("token cached at %s", TOKEN_FILE)


# --------------------------------------------------------------------------- #
# Calendar pull
# --------------------------------------------------------------------------- #
def _normalize_event(raw: dict[str, Any]) -> dict[str, Any]:
    start_block = raw.get("start") or {}
    end_block = raw.get("end") or {}
    start = start_block.get("dateTime") or start_block.get("date")
    end = end_block.get("dateTime") or end_block.get("date")
    attendees = raw.get("attendees") or []
    return {
        "start": _to_tpe_iso(start),
        "end": _to_tpe_iso(end),
        "title": raw.get("summary") or "(untitled)",
        "location": raw.get("location") or "",
        "attendees": len(attendees) if isinstance(attendees, list) else 0,
        "calendar": "primary",
    }


def fetch_events(days: int) -> list[dict[str, Any]]:
    """Pull upcoming events from primary calendar. Empty list on failure."""
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    creds = _load_credentials(interactive=False)
    if creds is None:
        return []

    try:
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
    except Exception as exc:  # noqa: BLE001
        logger.error("failed to build calendar service: %s", exc)
        return []

    now_utc = datetime.now(UTC)
    horizon_utc = now_utc + timedelta(days=days)
    time_min = now_utc.isoformat(timespec="seconds").replace("+00:00", "Z")
    time_max = horizon_utc.isoformat(timespec="seconds").replace("+00:00", "Z")

    try:
        resp = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                maxResults=250,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
    except HttpError as exc:
        logger.error("calendar api error: %s", exc)
        return []
    except Exception as exc:  # noqa: BLE001
        logger.error("calendar fetch failed: %s", exc)
        return []

    items = resp.get("items") or []
    events = [_normalize_event(e) for e in items if isinstance(e, dict)]
    events = [e for e in events if e["start"]]
    events.sort(key=lambda e: e["start"])
    logger.info("fetched %d events (window=%d days)", len(events), days)
    return events


def write_cache(events: list[dict[str, Any]]) -> dict[str, Any]:
    payload = {
        "updated_at": _now_iso_tpe(),
        "source": "gcal_primary",
        "events": events,
    }
    CALENDAR_CACHE.parent.mkdir(parents=True, exist_ok=True)
    CALENDAR_CACHE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("wrote %s", CALENDAR_CACHE)
    return payload


# --------------------------------------------------------------------------- #
# Read-only helpers (kept for backward compatibility with server.py)
# --------------------------------------------------------------------------- #
def load_calendar() -> dict[str, Any]:
    """Read the calendar cache. Returns a stub if missing or malformed."""
    if not CALENDAR_CACHE.exists():
        return {
            "updated_at": _now_iso_tpe(),
            "source": "gcal_primary",
            "events": [],
            "note": "life_calendar.json not populated yet; run calendar_puller.py",
        }
    try:
        data = json.loads(CALENDAR_CACHE.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        logger.warning("calendar cache unreadable: %s", exc)
        return {
            "updated_at": _now_iso_tpe(),
            "source": "gcal_primary",
            "events": [],
        }
    if not isinstance(data, dict):
        return {
            "updated_at": _now_iso_tpe(),
            "source": "gcal_primary",
            "events": [],
        }
    data.setdefault("updated_at", _now_iso_tpe())
    data.setdefault("source", "gcal_primary")
    data.setdefault("events", [])
    if not isinstance(data["events"], list):
        data["events"] = []
    return data


def upcoming_events(days: int = DEFAULT_DAYS) -> list[dict[str, Any]]:
    """Filter the cached events to the next `days` days, sorted by start."""
    data = load_calendar()
    events = data.get("events") or []
    now = datetime.now(TPE)
    horizon = now + timedelta(days=days)
    out: list[dict[str, Any]] = []
    for e in events:
        if not isinstance(e, dict):
            continue
        start_raw = e.get("start")
        if not isinstance(start_raw, str) or not start_raw:
            continue
        try:
            start_dt = datetime.fromisoformat(start_raw)
        except ValueError:
            continue
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=TPE)
        if start_dt < now - timedelta(hours=1):
            continue
        if start_dt > horizon:
            continue
        out.append(e)
    out.sort(key=lambda x: str(x.get("start", "")))
    return out


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--auth",
        action="store_true",
        help="run interactive OAuth flow (opens browser once)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=DEFAULT_DAYS,
        help=f"lookahead window in days (default {DEFAULT_DAYS})",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    args = _parse_args(argv)

    if args.auth:
        creds = _load_credentials(interactive=True)
        if creds is None:
            return 2
        logger.info("auth OK; running a test pull")

    if not CLIENT_SECRET.exists() and not TOKEN_FILE.exists():
        _abort_missing_client_secret()
        return 2

    events = fetch_events(args.days)
    if not events and not TOKEN_FILE.exists():
        logger.error(
            "no token cached and fetch returned empty; run with --auth first",
        )
        return 2

    payload = write_cache(events)
    logger.info(
        "events=%d updated=%s",
        len(payload["events"]),
        payload["updated_at"],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
