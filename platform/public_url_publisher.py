#!/usr/bin/env python3
"""Publish cloudflared quick-tunnel URL to the digital-immortality repo.

Reads the daemon-maintained ``public_url.json`` from
``C:\\Users\\admin\\.claude\\scripts\\mission_control\\results\\public_url.json``
and copies it into the repo root. When the content has changed, commits and
pushes to ``origin/main`` so the GH Pages ``go.html`` resolver can read the
latest tunnel URL via ``raw.githubusercontent.com``.

One-shot: run via ``python public_url_publisher.py``. Designed to be driven by
Windows Task Scheduler on a 5-minute interval.

stdlib only. PEP 8, type hints, logging.
"""
from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

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


# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
SOURCE_FILE = Path(_win_to_posix(
    r"C:\Users\admin\.claude\scripts\mission_control\results\public_url.json"
))
REPO_ROOT = Path(_win_to_posix(r"C:\Users\admin\workspace\digital-immortality"))
# GH Pages source for this repo is main branch, /docs path. Keep the
# served public_url.json inside docs/ so it is reachable via both
# GH Pages (https://l12203685.github.io/digital-immortality/public_url.json)
# and raw.githubusercontent.com (/main/docs/public_url.json).
DEST_FILE = REPO_ROOT / "docs" / "public_url.json"
REL_DEST = "docs/public_url.json"
LOG_FILE = REPO_ROOT / "results" / "public_url_publisher.log"

TAIPEI_TZ = timezone(timedelta(hours=8))

# ----------------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------------
def _setup_logging() -> logging.Logger:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("public_url_publisher")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    return logger


log = _setup_logging()


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def _read_json(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        log.error("failed to read %s: %s", path, exc)
        return None


def _run_git(*args: str) -> subprocess.CompletedProcess:
    """Run a git command inside the repo root."""
    cmd = ["git", "-C", str(REPO_ROOT), *args]
    return subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def _short_host(url: str) -> str:
    try:
        return url.split("//", 1)[1].split("/", 1)[0]
    except IndexError:
        return url


def _safe_copy(src: Path, dst: Path, data: dict) -> None:
    """Write atomically so partial writes never end up committed."""
    tmp = dst.with_suffix(dst.suffix + ".tmp")
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    tmp.write_text(payload, encoding="utf-8")
    shutil.move(str(tmp), str(dst))


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def publish() -> int:
    """Copy + commit + push if content changed. Returns exit code."""
    started = datetime.now(TAIPEI_TZ).isoformat()
    log.info("publisher start %s", started)

    source = _read_json(SOURCE_FILE)
    if source is None:
        log.warning("source file missing or invalid: %s", SOURCE_FILE)
        return 1

    url = source.get("url")
    if not url or not isinstance(url, str) or not url.startswith("http"):
        log.warning("source JSON missing valid url field: %r", source)
        return 1

    current = _read_json(DEST_FILE)
    if current == source:
        log.info("no change (url=%s)", _short_host(url))
        return 0

    log.info(
        "change detected: %s -> %s",
        _short_host(current.get("url", "")) if current else "<none>",
        _short_host(url),
    )

    try:
        _safe_copy(SOURCE_FILE, DEST_FILE, source)
    except OSError as exc:
        log.error("failed to write dest file: %s", exc)
        return 2

    # Stage
    add = _run_git("add", REL_DEST)
    if add.returncode != 0:
        log.error("git add failed: %s", add.stderr.strip())
        return 3

    # Check if anything is actually staged (content may be identical but
    # differ on whitespace/encoding after normalization — git will report
    # nothing to commit, which is fine).
    diff = _run_git("diff", "--cached", "--quiet", REL_DEST)
    if diff.returncode == 0:
        log.info("git reports no staged delta; nothing to commit")
        return 0

    short = _short_host(url)
    msg = f"chore: update tunnel URL to {short}"
    commit = _run_git("commit", "-m", msg)
    if commit.returncode != 0:
        log.error("git commit failed: %s", commit.stderr.strip() or commit.stdout.strip())
        return 4

    # Capture hash before push (push can't change local HEAD).
    rev = _run_git("rev-parse", "--short", "HEAD")
    commit_hash = rev.stdout.strip() if rev.returncode == 0 else "?"
    log.info("committed %s: %s", commit_hash, msg)

    push = _run_git("push", "origin", "main")
    if push.returncode != 0:
        log.error("git push failed: %s", push.stderr.strip() or push.stdout.strip())
        return 5

    log.info("pushed origin/main ok (%s)", commit_hash)
    return 0


def main() -> int:
    try:
        return publish()
    except Exception as exc:  # noqa: BLE001 - top-level guard
        log.exception("unhandled error: %s", exc)
        return 99


if __name__ == "__main__":
    sys.exit(main())
