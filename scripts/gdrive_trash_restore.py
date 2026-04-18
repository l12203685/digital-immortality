"""GDrive Trash Restore Utility.

Lists files currently in the authenticated user's Drive trash and optionally
restores them in batch. Defaults to DRY RUN — no mutations happen unless
--apply is passed, and Edward must sign off before that.

Auth model
----------
The vault (`~/.claude/credentials/`) already holds an OAuth installed-app client
(`google_calendar_client_secret.json`) scoped to project
`concise-beanbag-367613`. The existing token (`google_calendar_token.json`) is
`calendar.readonly` only, so a ONE-TIME consent for Drive scope is required.

This script writes / reads its own token file:
    ~/.claude/credentials/google_drive_token.json

Scope requested: https://www.googleapis.com/auth/drive
(needed to list trashed items and untrash them; narrower `drive.file` won't see
trash items the app didn't create).

Usage
-----
    # 1. list everything in trash, filter by delete date, save inventory JSON
    python gdrive_trash_restore.py list \
        --since 2026-04-06 --until 2026-04-07 \
        --out staging/gdrive_trash_inventory.json

    # 2. dry-run restore of everything in the inventory
    python gdrive_trash_restore.py restore \
        --inventory staging/gdrive_trash_inventory.json

    # 3. actually restore (Edward approves)
    python gdrive_trash_restore.py restore \
        --inventory staging/gdrive_trash_inventory.json --apply

The first invocation will open a browser window for OAuth consent. Token is
cached afterwards.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError as exc:  # pragma: no cover
    sys.stderr.write(
        "Missing Google client libs. Install with:\n"
        "  pip install google-api-python-client google-auth-httplib2 "
        "google-auth-oauthlib\n"
        f"Import error: {exc}\n"
    )
    sys.exit(2)


VAULT = Path(os.path.expanduser("~/.claude/credentials"))
CLIENT_SECRET = VAULT / "google_calendar_client_secret.json"
TOKEN_PATH = VAULT / "google_drive_token.json"
SCOPES = ["https://www.googleapis.com/auth/drive"]


def get_service():
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CLIENT_SECRET.exists():
                raise SystemExit(
                    f"Missing OAuth client secret at {CLIENT_SECRET}. "
                    "Cannot bootstrap Drive auth."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRET), SCOPES
            )
            # run_local_server opens browser + catches redirect on localhost.
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
        try:
            os.chmod(TOKEN_PATH, 0o600)
        except OSError:
            pass
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def iso(ts: str | None) -> dt.datetime | None:
    if not ts:
        return None
    # Drive returns RFC3339 like '2026-04-06T01:06:45.123Z'
    return dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))


def cmd_list(args: argparse.Namespace) -> int:
    service = get_service()
    since = dt.datetime.fromisoformat(args.since) if args.since else None
    until = dt.datetime.fromisoformat(args.until) if args.until else None
    if since and since.tzinfo is None:
        since = since.replace(tzinfo=dt.timezone.utc)
    if until and until.tzinfo is None:
        until = until.replace(tzinfo=dt.timezone.utc)

    fields = (
        "nextPageToken, files(id, name, mimeType, size, trashed, "
        "trashedTime, explicitlyTrashed, parents, owners(emailAddress))"
    )
    # q=trashed=true returns items the current user sees in trash.
    q = "trashed = true"
    if args.name_contains:
        q += f" and name contains '{args.name_contains}'"

    items: list[dict] = []
    page_token = None
    while True:
        resp = service.files().list(
            q=q,
            fields=fields,
            pageSize=1000,
            pageToken=page_token,
            spaces="drive",
        ).execute()
        for f in resp.get("files", []):
            t = iso(f.get("trashedTime"))
            if since and t and t < since:
                continue
            if until and t and t > until:
                continue
            items.append(f)
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    out = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "filter": {
            "since": args.since,
            "until": args.until,
            "name_contains": args.name_contains,
        },
        "count": len(items),
        "files": items,
    }
    out_path = Path(args.out) if args.out else None
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"[list] wrote {len(items)} items -> {out_path}")
    else:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    # brief stdout summary
    by_ext: dict[str, int] = {}
    for f in items:
        ext = Path(f.get("name", "")).suffix.lower() or "(none)"
        by_ext[ext] = by_ext.get(ext, 0) + 1
    print(f"[list] total={len(items)}  by_ext={by_ext}")
    return 0


def cmd_restore(args: argparse.Namespace) -> int:
    inv = json.loads(Path(args.inventory).read_text(encoding="utf-8"))
    files = inv.get("files", [])
    if not files:
        print("[restore] inventory empty, nothing to do.")
        return 0
    print(
        f"[restore] {'APPLY' if args.apply else 'DRY RUN'} "
        f"— {len(files)} files"
    )
    if not args.apply:
        for f in files[:10]:
            print(f"  would restore: {f['id']}  {f.get('name')}")
        if len(files) > 10:
            print(f"  ... +{len(files) - 10} more")
        print("[restore] pass --apply to actually restore.")
        return 0

    service = get_service()
    ok, fail = 0, 0
    errors: list[dict] = []
    for f in files:
        fid = f["id"]
        try:
            service.files().update(
                fileId=fid, body={"trashed": False}, fields="id,name,trashed"
            ).execute()
            ok += 1
            if ok % 10 == 0:
                print(f"  restored {ok}/{len(files)}")
        except HttpError as e:
            fail += 1
            errors.append({"id": fid, "name": f.get("name"), "error": str(e)})
    print(f"[restore] done ok={ok} fail={fail}")
    if errors:
        err_path = Path(args.inventory).with_suffix(".errors.json")
        err_path.write_text(
            json.dumps(errors, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"[restore] error log -> {err_path}")
    return 0 if fail == 0 else 1


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("list", help="list items in Drive trash")
    pl.add_argument("--since", help="ISO date, e.g. 2026-04-06")
    pl.add_argument("--until", help="ISO date, e.g. 2026-04-07")
    pl.add_argument("--name-contains", help="substring filter on filename")
    pl.add_argument("--out", help="write JSON inventory here")
    pl.set_defaults(func=cmd_list)

    pr = sub.add_parser("restore", help="restore items from inventory JSON")
    pr.add_argument("--inventory", required=True)
    pr.add_argument("--apply", action="store_true", help="actually restore")
    pr.set_defaults(func=cmd_restore)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
