#!/usr/bin/env python3
"""
Memory Manager for Digital Immortality — Cross-Session Persistence Layer.

Manages JSON-based memory files in memory/. Each category (corrections, insights,
decisions, calibration) has its own file. Entries are timestamped, tagged, and
queryable.

Usage:
    python memory_manager.py --store corrections boot-test-001 "Agent asked known question instead of acting" --source cycle-3 --tags boot-test,anti-pattern
    python memory_manager.py --recall corrections
    python memory_manager.py --recall corrections boot-test-001
    python memory_manager.py --search --tags anti-pattern
    python memory_manager.py --list
    python memory_manager.py --prune --days 90
    python memory_manager.py --export
"""

import argparse
import json
import os
import sys
import tempfile
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MEMORY_DIR = ROOT / "memory"

CATEGORIES = ("corrections", "insights", "decisions", "calibration")


def _memory_path(category: str) -> Path:
    """Return the JSON file path for a category."""
    return MEMORY_DIR / f"{category}.json"


def _load(category: str) -> dict:
    """Load a category file. Returns the parsed JSON dict."""
    path = _memory_path(category)
    if not path.exists():
        return {"category": category, "description": "", "entries": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(category: str, data: dict) -> None:
    """Atomic write: write to temp file then rename, so a crash never corrupts the file."""
    path = _memory_path(category)
    # Write to a temp file in the same directory (same filesystem) for atomic rename
    fd, tmp_path = tempfile.mkstemp(dir=MEMORY_DIR, suffix=".tmp", prefix=f".{category}_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp_path, path)
    except Exception:
        # Clean up temp file on failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def store(category: str, key: str, content: str, source: str = "manual",
          tags: list[str] | None = None, confidence: float | None = None) -> dict:
    """Store a new memory entry. Returns the created entry.

    Args:
        confidence: Optional float 0.0-1.0. Entries with confidence >= 0.8 are
                    protected from cap-based pruning in auto_prune().
    """
    if category not in CATEGORIES:
        print(f"Error: unknown category '{category}'. Must be one of: {', '.join(CATEGORIES)}", file=sys.stderr)
        sys.exit(1)

    data = _load(category)

    entry = {
        "id": str(uuid.uuid4()),
        "key": key,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "tags": tags or [],
    }
    if confidence is not None:
        entry["confidence"] = max(0.0, min(1.0, confidence))

    data["entries"].append(entry)
    _save(category, data)
    return entry


def recall(category: str, key: str | None = None) -> list[dict]:
    """Retrieve entries from a category, optionally filtered by key."""
    if category not in CATEGORIES:
        print(f"Error: unknown category '{category}'. Must be one of: {', '.join(CATEGORIES)}", file=sys.stderr)
        sys.exit(1)

    data = _load(category)
    entries = data.get("entries", [])

    if key is not None:
        entries = [e for e in entries if e.get("key") == key]

    return entries


def search_by_tags(tags: list[str], category: str | None = None) -> list[dict]:
    """Search entries that have ANY of the given tags. Optionally filter by category."""
    cats = [category] if category and category in CATEGORIES else list(CATEGORIES)
    tag_set = set(tags)
    results = []

    for cat in cats:
        data = _load(cat)
        for entry in data.get("entries", []):
            entry_tags = set(entry.get("tags", []))
            if entry_tags & tag_set:
                # Add category info for cross-category searches
                result = dict(entry)
                result["_category"] = cat
                results.append(result)

    return results


def list_categories() -> dict[str, int]:
    """Return a dict of category -> entry count."""
    counts = {}
    for cat in CATEGORIES:
        data = _load(cat)
        counts[cat] = len(data.get("entries", []))
    return counts


def prune(days: int, category: str | None = None) -> int:
    """Remove entries older than `days` days. Returns count of pruned entries."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    cats = [category] if category and category in CATEGORIES else list(CATEGORIES)
    total_pruned = 0

    for cat in cats:
        data = _load(cat)
        original_count = len(data.get("entries", []))
        data["entries"] = [
            e for e in data.get("entries", [])
            if datetime.fromisoformat(e["timestamp"]) >= cutoff
        ]
        pruned = original_count - len(data["entries"])
        if pruned > 0:
            _save(cat, data)
            total_pruned += pruned

    return total_pruned


DEFAULT_MAX_ENTRIES = 100


def auto_prune(max_entries: int = DEFAULT_MAX_ENTRIES, max_age_days: int = 30) -> dict[str, int]:
    """
    Enforce bounded memory: for each category, remove old entries and cap total count.

    Strategy:
    1. Remove entries older than max_age_days (via prune_old).
    2. If still over max_entries, keep the most recent entries up to the limit.
       Entries with a 'confidence' field >= 0.8 are protected and kept preferentially.

    Returns a dict of category -> number of entries removed.
    """
    removed = {}

    # Phase 1: age-based pruning
    prune_old(max_age_days=max_age_days)

    # Phase 2: cap-based pruning
    for cat in CATEGORIES:
        data = _load(cat)
        entries = data.get("entries", [])
        original_count = len(entries)

        if original_count <= max_entries:
            removed[cat] = 0
            continue

        # Split into high-confidence (protected) and normal
        high_conf = [e for e in entries if e.get("confidence", 0) >= 0.8]
        normal = [e for e in entries if e.get("confidence", 0) < 0.8]

        # If high-confidence entries alone exceed the limit, keep most recent of those
        if len(high_conf) >= max_entries:
            high_conf.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
            data["entries"] = high_conf[:max_entries]
        else:
            # Keep all high-confidence, fill remaining slots with most recent normal
            remaining_slots = max_entries - len(high_conf)
            normal.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
            data["entries"] = high_conf + normal[:remaining_slots]

        pruned = original_count - len(data["entries"])
        if pruned > 0:
            _save(cat, data)
        removed[cat] = pruned

    return removed


def prune_old(max_age_days: int = 30, category: str | None = None) -> int:
    """Remove entries older than max_age_days. Returns count of pruned entries."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    cats = [category] if category and category in CATEGORIES else list(CATEGORIES)
    total_pruned = 0

    for cat in cats:
        data = _load(cat)
        original_count = len(data.get("entries", []))
        data["entries"] = [
            e for e in data.get("entries", [])
            if datetime.fromisoformat(e["timestamp"]) >= cutoff
        ]
        pruned = original_count - len(data["entries"])
        if pruned > 0:
            _save(cat, data)
            total_pruned += pruned

    return total_pruned


def export_all() -> dict:
    """Export all memory categories into a single dict."""
    result = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "categories": {},
    }
    for cat in CATEGORIES:
        data = _load(cat)
        result["categories"][cat] = data
    return result


def _format_entry(entry: dict, show_category: bool = False) -> str:
    """Format a single entry for display."""
    lines = []
    prefix = f"[{entry.get('_category', '')}] " if show_category and "_category" in entry else ""
    lines.append(f"  {prefix}{entry['key']}")
    lines.append(f"    content:   {entry['content']}")
    lines.append(f"    timestamp: {entry['timestamp']}")
    lines.append(f"    source:    {entry['source']}")
    if entry.get("tags"):
        lines.append(f"    tags:      {', '.join(entry['tags'])}")
    if "confidence" in entry:
        lines.append(f"    confidence: {entry['confidence']:.2f}")
    lines.append(f"    id:        {entry['id']}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Memory persistence manager for Digital Immortality.",
        epilog="Categories: corrections, insights, decisions, calibration",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--store", nargs=3, metavar=("CATEGORY", "KEY", "VALUE"),
        help="Store a memory entry: --store <category> <key> <content>",
    )
    group.add_argument(
        "--recall", nargs="+", metavar="ARG",
        help="Recall entries: --recall <category> [key]",
    )
    group.add_argument(
        "--search", action="store_true",
        help="Search entries by tags (use with --tags)",
    )
    group.add_argument(
        "--list", action="store_true",
        help="List all categories and entry counts",
    )
    group.add_argument(
        "--prune", action="store_true",
        help="Remove entries older than N days (use with --days)",
    )
    group.add_argument(
        "--export", action="store_true",
        help="Export all memory to JSON (stdout)",
    )
    group.add_argument(
        "--auto-prune", action="store_true",
        help="Enforce max entries per category and remove stale entries",
    )
    group.add_argument(
        "--prune-old", action="store_true",
        help="Remove entries older than --max-age-days (default: 30)",
    )

    parser.add_argument("--source", default="manual", help="Source label for --store (e.g. 'cycle-5', 'boot-test')")
    parser.add_argument("--tags", default="", help="Comma-separated tags for --store or --search")
    parser.add_argument("--days", type=int, default=180, help="Days threshold for --prune (default: 180)")
    parser.add_argument("--category", default=None, help="Filter --search or --prune to a specific category")
    parser.add_argument("--max-entries", type=int, default=DEFAULT_MAX_ENTRIES, help=f"Max entries per category for --auto-prune (default: {DEFAULT_MAX_ENTRIES})")
    parser.add_argument("--max-age-days", type=int, default=30, help="Max age in days for --auto-prune (default: 30)")
    parser.add_argument("--confidence", type=float, default=None, help="Confidence score 0.0-1.0 for --store (entries >= 0.8 are protected from pruning)")

    args = parser.parse_args()

    if args.store:
        cat, key, value = args.store
        tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
        entry = store(cat, key, value, source=args.source, tags=tags, confidence=args.confidence)
        print(f"Stored in {cat}:")
        print(_format_entry(entry))

    elif args.recall is not None:
        if len(args.recall) < 1 or len(args.recall) > 2:
            print("Usage: --recall <category> [key]", file=sys.stderr)
            sys.exit(1)
        cat = args.recall[0]
        key = args.recall[1] if len(args.recall) > 1 else None
        entries = recall(cat, key)
        if not entries:
            print(f"No entries found in '{cat}'" + (f" with key '{key}'" if key else "") + ".")
        else:
            print(f"{cat} ({len(entries)} entries):")
            for e in entries:
                print(_format_entry(e))
                print()

    elif args.search:
        if not args.tags:
            print("Error: --search requires --tags", file=sys.stderr)
            sys.exit(1)
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]
        results = search_by_tags(tags, category=args.category)
        if not results:
            print(f"No entries found with tags: {', '.join(tags)}")
        else:
            print(f"Found {len(results)} entries matching tags: {', '.join(tags)}")
            for e in results:
                print(_format_entry(e, show_category=True))
                print()

    elif args.list:
        counts = list_categories()
        total = sum(counts.values())
        print(f"Memory categories ({total} total entries):")
        for cat, count in counts.items():
            print(f"  {cat:15s} {count:4d} entries")

    elif args.prune:
        pruned = prune(args.days, category=args.category)
        scope = args.category if args.category else "all categories"
        print(f"Pruned {pruned} entries older than {args.days} days from {scope}.")

    elif args.export:
        data = export_all()
        print(json.dumps(data, indent=2, ensure_ascii=False))

    elif args.auto_prune:
        removed = auto_prune(max_entries=args.max_entries, max_age_days=args.max_age_days)
        total = sum(removed.values())
        print(f"Auto-prune complete (max_entries={args.max_entries}, max_age_days={args.max_age_days}):")
        for cat, count in removed.items():
            print(f"  {cat:15s} {count:4d} removed")
        print(f"  {'total':15s} {total:4d} removed")

    elif args.prune_old:
        pruned = prune_old(max_age_days=args.max_age_days, category=args.category)
        scope = args.category if args.category else "all categories"
        print(f"Pruned {pruned} entries older than {args.max_age_days} days from {scope}.")


if __name__ == "__main__":
    main()
