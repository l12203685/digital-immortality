#!/usr/bin/env python3
"""Google Calendar writer — CRUD operations on the primary calendar.

Additive companion to ``calendar_puller.py``. The puller is read-only
(14-day lookahead cache); this module exposes ``create_event``,
``update_event``, ``delete_event``, and ``list_events`` helpers used by
Mission Control's ``/api/calendar`` endpoints.

Auth model mirrors the puller: OAuth 2.0 desktop-app client, token
cached at ``~/.claude/credentials/google_calendar_token.json``. If the
token is missing or the refresh token has been revoked, every function
raises ``CalendarAuthError`` with a message directing Edward to re-run
``python calendar_puller.py --auth``. Callers are expected to catch it
and degrade gracefully (Mission Control queues the operation locally).

All timestamps are Asia/Taipei RFC3339 (``+08:00``) per Edward's
standing timezone rule.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo

TPE = ZoneInfo("Asia/Taipei")
UTC = ZoneInfo("UTC")

CREDENTIALS_DIR = Path("C:/Users/admin/.claude/credentials")
CLIENT_SECRET = Path(os.environ.get(
    "GOOGLE_CALENDAR_CLIENT_SECRET_PATH",
    str(CREDENTIALS_DIR / "google_calendar_client_secret.json"),
))
TOKEN_FILE = Path(os.environ.get(
    "GOOGLE_CALENDAR_TOKEN_PATH",
    str(CREDENTIALS_DIR / "google_calendar_token.json"),
))

# Read-write scope required for create/update/delete. The puller only
# asks for ``calendar.readonly``; when Edward (re-)auths with this
# scope, Google will mint a token that also covers the read path.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

CALENDAR_ID = "primary"
TPE_OFFSET = "+08:00"

logger = logging.getLogger("calendar_writer")


# --------------------------------------------------------------------------- #
# Exceptions
# --------------------------------------------------------------------------- #
class CalendarAuthError(RuntimeError):
    """Raised when OAuth is not ready (missing token or refresh failed)."""


class CalendarWriteError(RuntimeError):
    """Raised when the Google API call fails for non-auth reasons."""


AUTH_HINT = (
    "Google Calendar OAuth not ready. Run "
    "`python C:/Users/admin/workspace/digital-immortality/platform/calendar_puller.py --auth` "
    "once in a desktop session to mint the token."
)


# --------------------------------------------------------------------------- #
# Time helpers
# --------------------------------------------------------------------------- #
def _to_rfc3339_taipei(value: str) -> str:
    """Normalize ``value`` to a RFC3339 timestamp in Asia/Taipei.

    Accepts either a naive ``YYYY-MM-DDTHH:MM[:SS]`` (assumed Taipei
    local) or an already-offset ISO string. Returns a string ending in
    ``+08:00``.
    """
    if not isinstance(value, str) or not value:
        raise CalendarWriteError(f"empty datetime: {value!r}")
    normalized = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise CalendarWriteError(f"invalid datetime {value!r}: {exc}") from exc
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TPE)
    dt = dt.astimezone(TPE)
    return dt.isoformat(timespec="seconds")


# --------------------------------------------------------------------------- #
# Auth + service construction
# --------------------------------------------------------------------------- #
def _load_credentials() -> Any:
    """Load cached OAuth credentials, refreshing if needed.

    Raises ``CalendarAuthError`` on any failure so callers can degrade.
    """
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
    except ImportError as exc:  # noqa: BLE001
        raise CalendarAuthError(
            f"google-auth libraries missing: {exc}. "
            "Install google-api-python-client + google-auth-oauthlib."
        ) from exc

    if not TOKEN_FILE.exists():
        raise CalendarAuthError(AUTH_HINT)

    try:
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    except Exception as exc:  # noqa: BLE001
        raise CalendarAuthError(
            f"cached token at {TOKEN_FILE} unreadable: {exc}. {AUTH_HINT}"
        ) from exc

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as exc:  # noqa: BLE001
            raise CalendarAuthError(
                f"token refresh failed: {exc}. {AUTH_HINT}"
            ) from exc
        try:
            TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
        except OSError as exc:
            logger.warning("could not persist refreshed token: %s", exc)
        return creds

    raise CalendarAuthError(AUTH_HINT)


def _build_service() -> Any:
    """Return an authorized Calendar v3 service handle.

    Raises ``CalendarAuthError`` if auth is not ready, or
    ``CalendarWriteError`` if the client library is unavailable or the
    service build itself fails.
    """
    creds = _load_credentials()
    try:
        from googleapiclient.discovery import build
    except ImportError as exc:  # noqa: BLE001
        raise CalendarWriteError(
            f"google-api-python-client missing: {exc}"
        ) from exc
    try:
        return build("calendar", "v3", credentials=creds, cache_discovery=False)
    except Exception as exc:  # noqa: BLE001
        raise CalendarWriteError(f"failed to build calendar service: {exc}") from exc


# --------------------------------------------------------------------------- #
# Normalization
# --------------------------------------------------------------------------- #
def _normalize_event(raw: dict[str, Any]) -> dict[str, Any]:
    """Flatten a Google event dict into Mission Control's schema."""
    start_block = raw.get("start") or {}
    end_block = raw.get("end") or {}
    attendees = raw.get("attendees") or []
    return {
        "id": raw.get("id") or "",
        "start": _to_rfc3339_taipei(
            start_block.get("dateTime") or start_block.get("date") or ""
        ) if (start_block.get("dateTime") or start_block.get("date")) else "",
        "end": _to_rfc3339_taipei(
            end_block.get("dateTime") or end_block.get("date") or ""
        ) if (end_block.get("dateTime") or end_block.get("date")) else "",
        "title": raw.get("summary") or "(untitled)",
        "location": raw.get("location") or "",
        "description": raw.get("description") or "",
        "attendees": len(attendees) if isinstance(attendees, list) else 0,
        "calendar": "primary",
        "html_link": raw.get("htmlLink") or "",
    }


def _attendee_emails(attendees: Iterable[str] | None) -> list[dict[str, str]]:
    if not attendees:
        return []
    return [{"email": e} for e in attendees if isinstance(e, str) and e.strip()]


# --------------------------------------------------------------------------- #
# CRUD
# --------------------------------------------------------------------------- #
def create_event(
    title: str,
    start_iso: str,
    end_iso: str,
    location: str | None = None,
    description: str | None = None,
    attendees: Iterable[str] | None = None,
) -> str:
    """Create a primary-calendar event and return its Google event ID.

    All datetimes are normalized to Asia/Taipei with ``+08:00`` offset.
    Raises ``CalendarAuthError`` if OAuth is not ready, or
    ``CalendarWriteError`` on API failure.
    """
    if not title or not title.strip():
        raise CalendarWriteError("title is required")
    start_rfc = _to_rfc3339_taipei(start_iso)
    end_rfc = _to_rfc3339_taipei(end_iso)

    body: dict[str, Any] = {
        "summary": title.strip(),
        "start": {"dateTime": start_rfc, "timeZone": "Asia/Taipei"},
        "end": {"dateTime": end_rfc, "timeZone": "Asia/Taipei"},
    }
    if location:
        body["location"] = location
    if description:
        body["description"] = description
    guest_list = _attendee_emails(attendees)
    if guest_list:
        body["attendees"] = guest_list

    service = _build_service()
    try:
        created = (
            service.events()
            .insert(calendarId=CALENDAR_ID, body=body, sendUpdates="none")
            .execute()
        )
    except Exception as exc:  # noqa: BLE001
        raise CalendarWriteError(f"gcal insert failed: {exc}") from exc
    event_id = created.get("id") or ""
    logger.info("created event %s (%s)", event_id, title)
    return event_id


def update_event(event_id: str, **fields: Any) -> dict[str, Any]:
    """Patch a primary-calendar event.

    Accepted keyword fields: ``title``, ``start``, ``end``, ``location``,
    ``description``, ``attendees``. Unknown fields are ignored. Returns
    the normalized post-update event dict.
    """
    if not event_id:
        raise CalendarWriteError("event_id is required")

    body: dict[str, Any] = {}
    if "title" in fields and fields["title"] is not None:
        body["summary"] = str(fields["title"]).strip()
    if "start" in fields and fields["start"] is not None:
        body["start"] = {
            "dateTime": _to_rfc3339_taipei(str(fields["start"])),
            "timeZone": "Asia/Taipei",
        }
    if "end" in fields and fields["end"] is not None:
        body["end"] = {
            "dateTime": _to_rfc3339_taipei(str(fields["end"])),
            "timeZone": "Asia/Taipei",
        }
    if "location" in fields and fields["location"] is not None:
        body["location"] = str(fields["location"])
    if "description" in fields and fields["description"] is not None:
        body["description"] = str(fields["description"])
    if "attendees" in fields and fields["attendees"] is not None:
        body["attendees"] = _attendee_emails(fields["attendees"])

    if not body:
        raise CalendarWriteError("no updatable fields supplied")

    service = _build_service()
    try:
        patched = (
            service.events()
            .patch(
                calendarId=CALENDAR_ID,
                eventId=event_id,
                body=body,
                sendUpdates="none",
            )
            .execute()
        )
    except Exception as exc:  # noqa: BLE001
        raise CalendarWriteError(f"gcal patch failed for {event_id}: {exc}") from exc
    logger.info("updated event %s", event_id)
    return _normalize_event(patched)


def delete_event(event_id: str) -> None:
    """Delete a primary-calendar event.

    Idempotent on 410/404 — a missing event is treated as already-deleted.
    """
    if not event_id:
        raise CalendarWriteError("event_id is required")
    service = _build_service()
    try:
        service.events().delete(
            calendarId=CALENDAR_ID,
            eventId=event_id,
            sendUpdates="none",
        ).execute()
    except Exception as exc:  # noqa: BLE001
        msg = str(exc)
        if "410" in msg or "404" in msg or "notFound" in msg or "deleted" in msg.lower():
            logger.info("event %s already gone (%s)", event_id, msg)
            return
        raise CalendarWriteError(f"gcal delete failed for {event_id}: {exc}") from exc
    logger.info("deleted event %s", event_id)


def list_events(
    time_min_iso: str,
    time_max_iso: str,
    max_results: int = 50,
) -> list[dict[str, Any]]:
    """List primary-calendar events in a time window (inclusive of min).

    Datetimes are accepted in any ISO form and converted to RFC3339.
    """
    time_min = _to_rfc3339_taipei(time_min_iso)
    time_max = _to_rfc3339_taipei(time_max_iso)

    service = _build_service()
    try:
        resp = (
            service.events()
            .list(
                calendarId=CALENDAR_ID,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max(1, min(max_results, 2500)),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
    except Exception as exc:  # noqa: BLE001
        raise CalendarWriteError(f"gcal list failed: {exc}") from exc
    items = resp.get("items") or []
    out: list[dict[str, Any]] = []
    for raw in items:
        if not isinstance(raw, dict):
            continue
        try:
            out.append(_normalize_event(raw))
        except Exception as exc:  # noqa: BLE001
            logger.warning("skipping malformed event: %s", exc)
    out.sort(key=lambda e: e.get("start") or "")
    return out


# --------------------------------------------------------------------------- #
# Introspection
# --------------------------------------------------------------------------- #
def auth_status() -> dict[str, Any]:
    """Return a dict describing current OAuth readiness (never raises)."""
    status: dict[str, Any] = {
        "token_present": TOKEN_FILE.exists(),
        "client_secret_present": CLIENT_SECRET.exists(),
        "ready": False,
        "message": "",
    }
    if not status["token_present"]:
        status["message"] = "token missing; run calendar_puller.py --auth"
        return status
    try:
        _load_credentials()
    except CalendarAuthError as exc:
        status["message"] = str(exc)
        return status
    status["ready"] = True
    status["message"] = "ok"
    return status
