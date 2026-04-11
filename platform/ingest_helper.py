#!/usr/bin/env python3
"""Ingest helper for Edward's life-domain upload plumbing.

Manages the health / diet inbox folders under
``C:\\Users\\admin\\staging\\`` where photos and PDFs land prior to vision
processing by the main Claude session.

Subcommands
-----------
list     : show pending files (both inboxes) sorted by mtime
move     : relocate a misplaced file from one inbox to the other
archive  : move a processed file to ``<inbox>/_processed/YYYY-MM/``
stats    : counts + total size for pending / processed

Stdlib only. Timezone = Asia/Taipei.
"""
from __future__ import annotations

import argparse
import logging
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable
from zoneinfo import ZoneInfo

TPE = ZoneInfo("Asia/Taipei")

STAGING = Path("C:/Users/admin/staging")
INBOXES: dict[str, Path] = {
    "health": STAGING / "health_inbox",
    "diet": STAGING / "diet_inbox",
}
SUPPORTED_EXT = {".pdf", ".jpg", ".jpeg", ".png", ".webp", ".heic"}
MAX_BYTES = 20 * 1024 * 1024  # 20 MB

logger = logging.getLogger("ingest_helper")


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FileInfo:
    """Immutable view of a pending or processed file."""

    domain: str
    path: Path
    size: int
    mtime: float
    processed: bool

    def pretty_mtime(self) -> str:
        return datetime.fromtimestamp(self.mtime, TPE).strftime("%Y-%m-%d %H:%M")

    def pretty_size(self) -> str:
        mb = self.size / (1024 * 1024)
        if mb >= 1:
            return f"{mb:.2f} MB"
        kb = self.size / 1024
        return f"{kb:.1f} KB"


def _ensure_dirs() -> None:
    for domain, inbox in INBOXES.items():
        inbox.mkdir(parents=True, exist_ok=True)
        (inbox / "_processed").mkdir(parents=True, exist_ok=True)
        logger.debug("ensured inbox: %s", inbox)


def _iter_files(inbox: Path, include_processed: bool) -> Iterable[Path]:
    """Yield regular files under *inbox*.

    Pending files live directly in *inbox* (ignoring the ``_processed``
    subtree); processed files live under ``_processed``.
    """
    if not inbox.exists():
        return
    for entry in inbox.iterdir():
        if entry.is_file():
            if entry.suffix.lower() in SUPPORTED_EXT:
                yield entry
        elif entry.is_dir() and entry.name == "_processed" and include_processed:
            for sub in entry.rglob("*"):
                if sub.is_file() and sub.suffix.lower() in SUPPORTED_EXT:
                    yield sub


def _collect(domain: str, *, include_processed: bool) -> list[FileInfo]:
    inbox = INBOXES[domain]
    out: list[FileInfo] = []
    for p in _iter_files(inbox, include_processed=include_processed):
        try:
            st = p.stat()
        except OSError as exc:
            logger.warning("cannot stat %s: %s", p, exc)
            continue
        processed = "_processed" in p.parts
        out.append(
            FileInfo(
                domain=domain,
                path=p,
                size=st.st_size,
                mtime=st.st_mtime,
                processed=processed,
            )
        )
    out.sort(key=lambda f: f.mtime, reverse=True)
    return out


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_list(_: argparse.Namespace) -> int:
    _ensure_dirs()
    any_found = False
    for domain in INBOXES:
        pending = [f for f in _collect(domain, include_processed=False) if not f.processed]
        header = f"[{domain}] pending: {len(pending)}"
        logger.info(header)
        print(header)
        for f in pending:
            any_found = True
            print(f"  {f.pretty_mtime()}  {f.pretty_size():>10}  {f.path.name}")
            if f.size > MAX_BYTES:
                print(f"    ! oversize (>{MAX_BYTES // (1024 * 1024)} MB)")
    if not any_found:
        print("(no pending files)")
    return 0


def cmd_stats(_: argparse.Namespace) -> int:
    _ensure_dirs()
    rows: list[tuple[str, int, int, int, int]] = []
    for domain in INBOXES:
        all_files = _collect(domain, include_processed=True)
        pending = [f for f in all_files if not f.processed]
        processed = [f for f in all_files if f.processed]
        pending_bytes = sum(f.size for f in pending)
        processed_bytes = sum(f.size for f in processed)
        rows.append((domain, len(pending), len(processed), pending_bytes, processed_bytes))

    total_mb = sum(r[3] + r[4] for r in rows) / (1024 * 1024)
    print(f"{'domain':<8} {'pending':>8} {'processed':>10} {'pending_MB':>12} {'processed_MB':>14}")
    for domain, p_count, done_count, p_bytes, done_bytes in rows:
        print(
            f"{domain:<8} {p_count:>8} {done_count:>10} "
            f"{p_bytes / (1024 * 1024):>12.2f} {done_bytes / (1024 * 1024):>14.2f}"
        )
    print(f"total_mb: {total_mb:.2f}")
    return 0


def cmd_move(args: argparse.Namespace) -> int:
    _ensure_dirs()
    src = Path(args.file).resolve()
    dest_domain: str = args.to
    if dest_domain not in INBOXES:
        logger.error("unknown domain: %s", dest_domain)
        return 2
    if not src.exists():
        logger.error("source not found: %s", src)
        return 2
    if src.suffix.lower() not in SUPPORTED_EXT:
        logger.error("unsupported extension: %s", src.suffix)
        return 2
    dest = INBOXES[dest_domain] / src.name
    if dest.exists():
        stem = dest.stem
        suffix = dest.suffix
        ts = datetime.now(TPE).strftime("%Y%m%dT%H%M%S")
        dest = INBOXES[dest_domain] / f"{stem}_{ts}{suffix}"
    shutil.move(str(src), str(dest))
    logger.info("moved %s -> %s", src, dest)
    print(f"moved -> {dest}")
    return 0


def cmd_archive(args: argparse.Namespace) -> int:
    _ensure_dirs()
    src = Path(args.file).resolve()
    if not src.exists():
        logger.error("source not found: %s", src)
        return 2
    # Determine which inbox contains the file
    domain: str | None = None
    for name, inbox in INBOXES.items():
        try:
            src.relative_to(inbox.resolve())
            domain = name
            break
        except ValueError:
            continue
    if domain is None:
        logger.error("file is not inside a known inbox: %s", src)
        return 2
    month = datetime.now(TPE).strftime("%Y-%m")
    dest_dir = INBOXES[domain] / "_processed" / month
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name
    if dest.exists():
        ts = datetime.now(TPE).strftime("%Y%m%dT%H%M%S")
        dest = dest_dir / f"{src.stem}_{ts}{src.suffix}"
    shutil.move(str(src), str(dest))
    logger.info("archived %s -> %s", src, dest)
    print(f"archived -> {dest}")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ingest_helper",
        description="Manage life-domain inbox folders (health + diet).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="enable debug logging",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="list pending files in both inboxes")
    sub.add_parser("stats", help="show counts and total MB per domain")

    p_move = sub.add_parser("move", help="move a misplaced file to another inbox")
    p_move.add_argument("--file", required=True, help="absolute path to source file")
    p_move.add_argument("--to", required=True, choices=sorted(INBOXES.keys()))

    p_arc = sub.add_parser("archive", help="archive a processed file")
    p_arc.add_argument("--file", required=True, help="absolute path to source file")

    return parser


COMMANDS = {
    "list": cmd_list,
    "stats": cmd_stats,
    "move": cmd_move,
    "archive": cmd_archive,
}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    handler = COMMANDS.get(args.command)
    if handler is None:
        parser.print_help()
        return 2
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
