"""Distillation writeback tool -- diffs and syncs Claude memory ↔ LYH repo mirror.

Source of truth: Claude memory dir
Mirror target:   LYH agent/claude_memory dir

Run without flags for a dry-run report.
Run with --sync to copy drifted/missing files from source → mirror.
Files only in the mirror (not in source) are flagged for manual review; never auto-deleted.

Exit codes:
  0  -- all files in sync
  1  -- drift detected (missing or differing files)
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TPE = ZoneInfo("Asia/Taipei")

CLAUDE_MEMORY_DIR = Path(r"C:\Users\admin\.claude\projects\C--Users-admin\memory")
LYH_MIRROR_DIR = Path(r"C:\Users\admin\LYH\agent\claude_memory")

# Files that live only in the mirror and should not be synced back or flagged
MIRROR_ONLY_SKIP = frozenset({"LAST_SYNCED", "LAST_SYNCED.md"})


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FileState:
    name: str
    in_source: bool
    in_mirror: bool
    content_match: bool  # only meaningful when both exist
    source_hash: str
    mirror_hash: str


@dataclass
class DiffResult:
    source_only: list[str] = field(default_factory=list)   # in source, missing from mirror
    mirror_only: list[str] = field(default_factory=list)   # in mirror, missing from source
    drifted: list[str] = field(default_factory=list)       # in both but content differs
    in_sync: list[str] = field(default_factory=list)       # in both, identical
    source_total: int = 0
    mirror_total: int = 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read_bytes(path: Path) -> bytes:
    """Read file bytes, stripping UTF-8 BOM if present."""
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
    return data


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _collect_md_files(directory: Path) -> dict[str, Path]:
    """Return {filename: path} for all .md files in directory."""
    if not directory.is_dir():
        raise FileNotFoundError(f"Directory not found: {directory}")
    return {p.name: p for p in sorted(directory.glob("*.md"))}


# ---------------------------------------------------------------------------
# Core diff logic
# ---------------------------------------------------------------------------


def compute_diff(
    source_dir: Path = CLAUDE_MEMORY_DIR,
    mirror_dir: Path = LYH_MIRROR_DIR,
) -> DiffResult:
    """Compare source and mirror directories; return a DiffResult."""
    source_files = _collect_md_files(source_dir)
    mirror_files = _collect_md_files(mirror_dir)

    # Remove known mirror-only housekeeping files from consideration
    mirror_files = {k: v for k, v in mirror_files.items() if k not in MIRROR_ONLY_SKIP}

    result = DiffResult(
        source_total=len(source_files),
        mirror_total=len(mirror_files),
    )

    all_names = sorted(set(source_files) | set(mirror_files))

    for name in all_names:
        in_src = name in source_files
        in_mir = name in mirror_files

        if in_src and not in_mir:
            result.source_only.append(name)
        elif in_mir and not in_src:
            result.mirror_only.append(name)
        else:
            src_data = _read_bytes(source_files[name])
            mir_data = _read_bytes(mirror_files[name])
            if src_data == mir_data:
                result.in_sync.append(name)
            else:
                result.drifted.append(name)

    return result


# ---------------------------------------------------------------------------
# Sync logic
# ---------------------------------------------------------------------------


def sync_files(
    diff: DiffResult,
    source_dir: Path = CLAUDE_MEMORY_DIR,
    mirror_dir: Path = LYH_MIRROR_DIR,
) -> list[str]:
    """Copy source-only and drifted files from source → mirror.

    Returns list of filenames actually written.
    """
    written: list[str] = []
    to_copy = sorted(set(diff.source_only) | set(diff.drifted))

    for name in to_copy:
        src_path = source_dir / name
        dst_path = mirror_dir / name
        shutil.copy2(src_path, dst_path)
        written.append(name)

    return written


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _print_report(diff: DiffResult, synced: list[str] | None = None) -> None:
    now_str = datetime.now(tz=TPE).strftime("%Y-%m-%d %H:%M +08")
    is_sync_run = synced is not None

    print(f"Distillation Writeback  |  {now_str}  |  mode: {'SYNC' if is_sync_run else 'DRY-RUN'}")
    print(f"Source : {CLAUDE_MEMORY_DIR}  ({diff.source_total} .md files)")
    print(f"Mirror : {LYH_MIRROR_DIR}  ({diff.mirror_total} .md files)")
    print()

    # In sync
    sync_count = len(diff.in_sync)
    drift_count = len(diff.drifted)
    source_only_count = len(diff.source_only)
    mirror_only_count = len(diff.mirror_only)

    print(f"  In sync            : {sync_count}")
    print(f"  Drifted (differ)   : {drift_count}")
    print(f"  Source-only (new)  : {source_only_count}")
    print(f"  Mirror-only (extra): {mirror_only_count}")
    print()

    if diff.source_only:
        label = "Source-only (will copy)" if is_sync_run else "Source-only (not in mirror)"
        print(f"[{label}]")
        for name in sorted(diff.source_only):
            marker = "  COPIED" if (synced and name in synced) else ""
            print(f"  + {name}{marker}")
        print()

    if diff.drifted:
        label = "Drifted (will overwrite mirror)" if is_sync_run else "Drifted (content differs)"
        print(f"[{label}]")
        for name in sorted(diff.drifted):
            marker = "  UPDATED" if (synced and name in synced) else ""
            print(f"  ~ {name}{marker}")
        print()

    if diff.mirror_only:
        print("[Mirror-only — manual review needed, NOT auto-deleted]")
        for name in sorted(diff.mirror_only):
            print(f"  ? {name}")
        print()

    # Summary line
    total_drift = drift_count + source_only_count
    if is_sync_run and synced is not None:
        print(f"Summary: {sync_count} files in sync, {total_drift} drifted/missing -> {len(synced)} written, {mirror_only_count} manual-review")
    else:
        print(f"Summary: {sync_count} files in sync, {total_drift} drifted/missing, {mirror_only_count} mirror-only")

    if total_drift == 0 and mirror_only_count == 0:
        print("Status : OK -- no drift detected")
    else:
        print("Status : DRIFT DETECTED")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Diff and optionally sync Claude memory distillation entries with LYH mirror.",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Copy missing/drifted files from source to mirror (source is authoritative).",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=CLAUDE_MEMORY_DIR,
        help="Override source directory (default: Claude memory dir).",
    )
    parser.add_argument(
        "--mirror",
        type=Path,
        default=LYH_MIRROR_DIR,
        help="Override mirror directory (default: LYH claude_memory dir).",
    )
    args = parser.parse_args()

    try:
        diff = compute_diff(source_dir=args.source, mirror_dir=args.mirror)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    synced: list[str] | None = None
    if args.sync:
        synced = sync_files(diff, source_dir=args.source, mirror_dir=args.mirror)

    _print_report(diff, synced=synced)

    total_drift = len(diff.drifted) + len(diff.source_only)
    has_mirror_only = len(diff.mirror_only) > 0
    sys.exit(0 if (total_drift == 0 and not has_mirror_only) else 1)


if __name__ == "__main__":
    main()
