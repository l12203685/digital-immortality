"""Stale memory detector -- flags memory files unreferenced for 30+ days."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

TPE = ZoneInfo("Asia/Taipei")

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


MEMORY_DIR = Path(_win_to_posix(r"C:\Users\admin\.claude\projects\C--Users-admin\memory"))
MEMORY_INDEX = MEMORY_DIR / "MEMORY.md"
STALE_THRESHOLD_DAYS = 30


def _read_index_references(index_path: Path) -> set[str]:
    """Extract all .md filenames referenced in MEMORY.md."""
    if not index_path.exists():
        return set()
    text = index_path.read_text(encoding="utf-8")
    refs: set[str] = set()
    for line in text.splitlines():
        # Match markdown links like (feedback_foo.md) or (project_bar.md)
        start = 0
        while True:
            open_paren = line.find("(", start)
            if open_paren == -1:
                break
            close_paren = line.find(")", open_paren)
            if close_paren == -1:
                break
            target = line[open_paren + 1 : close_paren].strip()
            if target.endswith(".md"):
                refs.add(target)
            start = close_paren + 1
    return refs


def scan_memory_files(
    memory_dir: Path = MEMORY_DIR,
    index_path: Path = MEMORY_INDEX,
    threshold_days: int = STALE_THRESHOLD_DAYS,
) -> list[dict[str, str | bool]]:
    """Scan memory directory and return a list of file info dicts.

    Each dict has keys: filename, last_modified, referenced, stale.
    """
    if not memory_dir.is_dir():
        raise FileNotFoundError(f"Memory directory not found: {memory_dir}")

    references = _read_index_references(index_path)
    now = datetime.now(tz=TPE)
    cutoff = now - timedelta(days=threshold_days)
    results: list[dict[str, str | bool]] = []

    for md_file in sorted(memory_dir.glob("*.md")):
        if md_file.name == "MEMORY.md":
            continue

        mtime = datetime.fromtimestamp(md_file.stat().st_mtime, tz=TPE)
        referenced = md_file.name in references
        stale = (mtime < cutoff) and not referenced

        results.append({
            "filename": md_file.name,
            "last_modified": mtime.strftime("%Y-%m-%d %H:%M +08"),
            "referenced": referenced,
            "stale": stale,
        })

    return results


def _print_table(results: list[dict[str, str | bool]]) -> None:
    """Print a human-readable table of scan results."""
    stale_items = [r for r in results if r["stale"]]
    ok_items = [r for r in results if not r["stale"]]

    now_str = datetime.now(tz=TPE).strftime("%Y-%m-%d %H:%M +08")
    print(f"Stale Memory Detector  |  scan time: {now_str}")
    print(f"Directory: {MEMORY_DIR}")
    print(f"Threshold: {STALE_THRESHOLD_DAYS} days  |  Total files: {len(results)}")
    print(f"Stale: {len(stale_items)}  |  OK: {len(ok_items)}")
    print()

    if not results:
        print("No memory files found.")
        return

    # Column widths
    name_w = max(len(str(r["filename"])) for r in results)
    name_w = max(name_w, 8)

    header = f"{'Filename':<{name_w}}  {'Last Modified':<20}  {'Ref?':<5}  Status"
    print(header)
    print("-" * len(header))

    for r in results:
        ref_mark = "YES" if r["referenced"] else "NO"
        status = "STALE" if r["stale"] else "OK"
        print(f"{r['filename']:<{name_w}}  {r['last_modified']:<20}  {ref_mark:<5}  {status}")

    if stale_items:
        print()
        print(f"[!] {len(stale_items)} file(s) flagged as stale (>30 days old, not referenced).")
    else:
        print()
        print("All memory files are current or referenced.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan memory files and flag stale ones.")
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output results as JSON",
    )
    args = parser.parse_args()

    try:
        results = scan_memory_files()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.output_json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        _print_table(results)


if __name__ == "__main__":
    main()
