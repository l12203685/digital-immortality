#!/usr/bin/env python3
"""
distil_semantic_dedupe.py — B3 Continuous Learning: Near-Duplicate Detection
Scans distillation memory files, detects near-duplicate entries using
stdlib-only heuristics (no ML/embeddings), and writes a JSON report.

Usage:
    python distil_semantic_dedupe.py [--threshold 0.7] [--output results/distil_dedupe_report.json]
"""

import argparse
import glob
import json
import os
import re
import unicodedata
from collections import defaultdict
from pathlib import Path


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML-like frontmatter block and return (meta, body)."""
    meta = {}
    body = text

    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1].strip()
            body = parts[2].strip()
            for line in fm_text.splitlines():
                if ":" in line:
                    key, _, val = line.partition(":")
                    meta[key.strip()] = val.strip()
    return meta, body


# ---------------------------------------------------------------------------
# Tokenisation (handles CJK + Latin)
# ---------------------------------------------------------------------------

_CJK_RANGES = (
    (0x4E00, 0x9FFF),   # CJK Unified Ideographs
    (0x3400, 0x4DBF),   # Extension A
    (0x20000, 0x2A6DF),  # Extension B
    (0xF900, 0xFAFF),   # Compatibility Ideographs
    (0x2E80, 0x2EFF),   # Radicals Supplement
    (0x31C0, 0x31EF),   # CJK Strokes
    (0x3000, 0x303F),   # CJK Symbols and Punctuation
)


def _is_cjk(char: str) -> bool:
    cp = ord(char)
    return any(lo <= cp <= hi for lo, hi in _CJK_RANGES)


def extract_tokens(text: str) -> set[str]:
    """Return a set of lowercase tokens from text.

    Strategy:
    - Normalise unicode to NFC
    - Split Latin/numeric text on non-alnum boundaries → words
    - Slide a bigram window over runs of CJK characters
    - Filter stopwords and very short tokens
    """
    text = unicodedata.normalize("NFC", text.lower())

    tokens: set[str] = set()

    # Collect CJK runs and non-CJK words in one pass
    cjk_run: list[str] = []
    non_cjk_buf: list[str] = []

    def flush_cjk():
        if len(cjk_run) >= 2:
            for i in range(len(cjk_run) - 1):
                tokens.add(cjk_run[i] + cjk_run[i + 1])
        if cjk_run:
            tokens.update(cjk_run)
        cjk_run.clear()

    def flush_non_cjk():
        segment = "".join(non_cjk_buf)
        words = re.split(r"[^a-z0-9\u00c0-\u024f]+", segment)
        for w in words:
            if len(w) >= 2:
                tokens.add(w)
        non_cjk_buf.clear()

    for ch in text:
        if _is_cjk(ch):
            flush_non_cjk()
            cjk_run.append(ch)
        else:
            flush_cjk()
            non_cjk_buf.append(ch)

    flush_cjk()
    flush_non_cjk()

    # Remove common stopwords (English + Chinese function words)
    stopwords = {
        "the", "a", "an", "is", "in", "on", "at", "to", "of", "and", "or",
        "for", "with", "it", "this", "that", "be", "by", "are", "was", "as",
        "not", "if", "we", "can", "do", "but", "from", "will", "has", "have",
        "が", "は", "の", "に", "を", "も", "や", "と", "で",
    }
    return tokens - stopwords


def normalize_body(body: str) -> str:
    """Collapse whitespace for exact-match comparison."""
    return re.sub(r"\s+", " ", body.strip())


# ---------------------------------------------------------------------------
# Similarity metrics
# ---------------------------------------------------------------------------

def jaccard(set_a: set, set_b: set) -> float:
    if not set_a and not set_b:
        return 1.0
    union = set_a | set_b
    if not union:
        return 0.0
    return len(set_a & set_b) / len(union)


def levenshtein_ratio(s1: str, s2: str) -> float:
    """Normalised Levenshtein similarity (0–1). O(n*m) — only call on short strings."""
    if s1 == s2:
        return 1.0
    len1, len2 = len(s1), len(s2)
    if not len1 or not len2:
        return 0.0
    # Guard against very long name fields causing slowness
    if len1 > 200 or len2 > 200:
        s1, s2 = s1[:200], s2[:200]
        len1, len2 = 200, 200

    # DP table (two rows)
    prev = list(range(len2 + 1))
    for i, c1 in enumerate(s1, 1):
        curr = [i] + [0] * len2
        for j, c2 in enumerate(s2, 1):
            cost = 0 if c1 == c2 else 1
            curr[j] = min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost)
        prev = curr

    distance = prev[len2]
    max_len = max(len1, len2)
    return 1.0 - distance / max_len


# ---------------------------------------------------------------------------
# File scanning
# ---------------------------------------------------------------------------

def load_memory_files(directories: list[str]) -> list[dict]:
    """Scan directories for *.md files and parse them."""
    entries = []
    seen_paths: set[str] = set()

    for directory in directories:
        pattern = os.path.join(directory, "*.md")
        for fpath in sorted(glob.glob(pattern)):
            real_path = str(Path(fpath).resolve())
            if real_path in seen_paths:
                continue
            seen_paths.add(real_path)

            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
            except OSError:
                continue

            meta, body = parse_frontmatter(text)
            tokens = extract_tokens(body)
            entries.append(
                {
                    "path": fpath,
                    "source_dir": directory,
                    "filename": os.path.basename(fpath),
                    "name": meta.get("name", ""),
                    "description": meta.get("description", ""),
                    "type": meta.get("type", ""),
                    "body": body,
                    "body_normalized": normalize_body(body),
                    "tokens": tokens,
                }
            )

    return entries


def load_distil_jsonl(directories: list[str]) -> list[dict]:
    """Load distil*.jsonl / distil*.json files if present."""
    entries = []
    for directory in directories:
        for pattern in ("distil*.jsonl", "distil*.json"):
            for fpath in sorted(glob.glob(os.path.join(directory, pattern))):
                try:
                    with open(fpath, "r", encoding="utf-8", errors="replace") as fh:
                        for lineno, line in enumerate(fh, 1):
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                obj = json.loads(line)
                            except json.JSONDecodeError:
                                # try whole-file JSON on first line
                                if lineno == 1:
                                    try:
                                        obj = json.loads(
                                            open(fpath, encoding="utf-8").read()
                                        )
                                    except Exception:
                                        break
                                else:
                                    continue

                            # Skip non-dict JSON values (strings, lists, etc.)
                            if not isinstance(obj, dict):
                                continue

                            # Normalise to our entry schema
                            body = obj.get("body", obj.get("content", str(obj)))
                            if not isinstance(body, str):
                                body = str(body)
                            tokens = extract_tokens(body)
                            entries.append(
                                {
                                    "path": f"{fpath}:{lineno}",
                                    "filename": f"{os.path.basename(fpath)}:{lineno}",
                                    "name": obj.get("name", obj.get("title", "")),
                                    "description": obj.get("description", ""),
                                    "type": obj.get("type", ""),
                                    "body": body,
                                    "body_normalized": normalize_body(body),
                                    "tokens": tokens,
                                }
                            )
                except OSError:
                    continue
    return entries


# ---------------------------------------------------------------------------
# Pair detection
# ---------------------------------------------------------------------------

DuplicateKind = str  # "EXACT" | "NAME" | "HIGH" | "SAME_TOPIC"


def detect_pairs(
    entries: list[dict],
    jaccard_threshold: float = 0.7,
    name_threshold: float = 0.80,
    same_topic_overlap: float = 0.60,
) -> list[dict]:
    """Compare every pair of entries and collect near-duplicate candidates."""
    pairs = []
    n = len(entries)

    for i in range(n):
        for j in range(i + 1, n):
            a, b = entries[i], entries[j]
            reasons = []
            best_score = 0.0

            # 1. Exact body match
            if a["body_normalized"] and a["body_normalized"] == b["body_normalized"]:
                reasons.append("EXACT")
                best_score = 1.0

            # 2. Title / name similarity
            if a["name"] and b["name"] and "EXACT" not in reasons:
                name_sim = levenshtein_ratio(
                    a["name"].lower(), b["name"].lower()
                )
                if name_sim >= name_threshold:
                    reasons.append("NAME")
                    best_score = max(best_score, name_sim)

            # 3. Keyword (Jaccard) overlap
            j_score = jaccard(a["tokens"], b["tokens"])
            if j_score >= jaccard_threshold and "EXACT" not in reasons:
                reasons.append("HIGH")
                best_score = max(best_score, j_score)

            # 4. Same type + 60% overlap
            if (
                a["type"]
                and a["type"] == b["type"]
                and j_score >= same_topic_overlap
                and "EXACT" not in reasons
                and "HIGH" not in reasons
            ):
                reasons.append("SAME_TOPIC")
                best_score = max(best_score, j_score)

            if reasons:
                # Dominant label: EXACT > NAME > HIGH > SAME_TOPIC
                dominant = (
                    "EXACT"
                    if "EXACT" in reasons
                    else "NAME"
                    if "NAME" in reasons
                    else "HIGH"
                    if "HIGH" in reasons
                    else "SAME_TOPIC"
                )
                is_mirror = (
                    a.get("source_dir", "") != b.get("source_dir", "")
                    and a["filename"] == b["filename"]
                )
                pairs.append(
                    {
                        "kind": dominant,
                        "score": round(best_score, 4),
                        "is_mirror": is_mirror,
                        "file_a": a["filename"],
                        "file_b": b["filename"],
                        "path_a": a["path"],
                        "path_b": b["path"],
                        "name_a": a["name"],
                        "name_b": b["name"],
                        "type_a": a["type"],
                        "type_b": b["type"],
                        "jaccard": round(j_score, 4),
                        "reasons": reasons,
                    }
                )

    # Sort: EXACT first, then by descending score
    kind_order = {"EXACT": 0, "NAME": 1, "HIGH": 2, "SAME_TOPIC": 3}
    pairs.sort(key=lambda p: (kind_order.get(p["kind"], 9), -p["score"]))
    return pairs


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------

KIND_LABELS = {
    "EXACT": "identical body",
    "NAME": "similar name",
    "HIGH": "keyword overlap",
    "SAME_TOPIC": "same type + keyword overlap",
}


def print_report(
    pairs: list[dict], entries: list[dict], skip_mirror: bool = False
) -> None:
    total = len(entries)
    display_pairs = [p for p in pairs if not (skip_mirror and p.get("is_mirror"))]
    mirror_count = sum(1 for p in pairs if p.get("is_mirror"))

    # Count unique files involved in displayed pairs
    files_in_pairs: set[str] = set()
    for p in display_pairs:
        files_in_pairs.add(p["file_a"])
        files_in_pairs.add(p["file_b"])
    unique = total - len(files_in_pairs)

    print("\n=== Near-Duplicate Pairs ===")
    if skip_mirror and mirror_count:
        print(f"  (skipping {mirror_count} cross-directory mirror pairs, use --no-skip-mirror to show)")
    if not display_pairs:
        print("  (none found)")
    for idx, p in enumerate(display_pairs, 1):
        label = KIND_LABELS.get(p["kind"], p["kind"])
        mirror_tag = " [MIRROR]" if p.get("is_mirror") else ""
        print(
            f"{idx:3d}. [{p['kind']}]{mirror_tag} {p['file_a']} <-> {p['file_b']}\n"
            f"       Score: {p['score']:.2f} ({label})  |  Jaccard: {p['jaccard']:.2f}"
        )
        if p["name_a"] or p["name_b"]:
            print(f"       Names: \"{p['name_a']}\" / \"{p['name_b']}\"")

    print("\n=== Summary ===")
    print(f"Total files scanned:  {total}")
    print(f"Unique entries:       {unique}")
    print(f"Near-duplicate pairs: {len(display_pairs)}", end="")
    if skip_mirror and mirror_count:
        print(f"  (+{mirror_count} mirror pairs hidden)")
    else:
        print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Detect near-duplicate distillation entries (stdlib only, dry-run)."
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.7,
        help="Jaccard similarity threshold for keyword overlap (default: 0.7)",
    )
    parser.add_argument(
        "--name-threshold",
        type=float,
        default=0.80,
        dest="name_threshold",
        help="Levenshtein similarity threshold for name matching (default: 0.80)",
    )
    parser.add_argument(
        "--same-topic-threshold",
        type=float,
        default=0.60,
        dest="same_topic_threshold",
        help="Jaccard threshold for same-type detection (default: 0.60)",
    )
    parser.add_argument(
        "--output",
        default="results/distil_dedupe_report.json",
        help="Path for JSON report output (default: results/distil_dedupe_report.json)",
    )
    parser.add_argument(
        "--skip-mirror",
        action="store_true",
        default=True,
        dest="skip_mirror",
        help="Hide cross-directory mirror pairs from the console report (default: on)",
    )
    parser.add_argument(
        "--no-skip-mirror",
        action="store_false",
        dest="skip_mirror",
        help="Show all pairs including cross-directory mirrors",
    )
    args = parser.parse_args()

    # Resolve paths relative to this script's location (project root)
    project_root = Path(__file__).resolve().parent.parent
    user_home = Path.home()

    md_dirs = [
        str(user_home / ".claude/projects/C--Users-admin/memory"),
        str(user_home / "LYH/agent/claude_memory"),
    ]
    jsonl_dirs = [
        str(project_root / "results"),
    ]

    print("Scanning memory directories...")
    for d in md_dirs:
        exists = os.path.isdir(d)
        print(f"  {'[OK]' if exists else '[MISSING]'} {d}")

    print("Scanning results for distil JSONL files...")
    for d in jsonl_dirs:
        exists = os.path.isdir(d)
        print(f"  {'[OK]' if exists else '[MISSING]'} {d}")

    # Load entries
    md_entries = load_memory_files(md_dirs)
    jsonl_entries = load_distil_jsonl(jsonl_dirs)
    all_entries = md_entries + jsonl_entries

    print(f"\nLoaded {len(md_entries)} .md files, {len(jsonl_entries)} JSONL entries "
          f"-> {len(all_entries)} total entries")

    if not all_entries:
        print("No entries found. Exiting.")
        return

    # Detect duplicates
    print(f"\nComparing pairs (threshold={args.threshold}, "
          f"name_threshold={args.name_threshold}, "
          f"same_topic={args.same_topic_threshold})...")

    pairs = detect_pairs(
        all_entries,
        jaccard_threshold=args.threshold,
        name_threshold=args.name_threshold,
        same_topic_overlap=args.same_topic_threshold,
    )

    # Print human report
    print_report(pairs, all_entries, skip_mirror=args.skip_mirror)

    # Build JSON report
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = project_root / args.output

    output_path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "generated_at": _now_taipei(),
        "config": {
            "jaccard_threshold": args.threshold,
            "name_threshold": args.name_threshold,
            "same_topic_threshold": args.same_topic_threshold,
        },
        "summary": {
            "total_files_scanned": len(all_entries),
            "near_duplicate_pairs": len(pairs),
            "mirror_pairs": sum(1 for p in pairs if p.get("is_mirror")),
            "semantic_pairs": sum(1 for p in pairs if not p.get("is_mirror")),
        },
        "pairs": pairs,
        "files_scanned": [
            {
                "filename": e["filename"],
                "path": e["path"],
                "name": e["name"],
                "type": e["type"],
            }
            for e in all_entries
        ],
    }

    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)

    print(f"\nJSON report saved: {output_path}")
    print("(Dry-run only — no files were modified or deleted.)")


def _now_taipei() -> str:
    """Return current datetime as Asia/Taipei string without pytz dependency."""
    import datetime

    try:
        # Python 3.9+ supports zoneinfo
        from zoneinfo import ZoneInfo
        now = datetime.datetime.now(tz=ZoneInfo("Asia/Taipei"))
        return now.strftime("%Y-%m-%d %H:%M %z")
    except ImportError:
        # Fallback: hardcode UTC+8 offset
        utc_now = datetime.datetime.utcnow()
        taipei_now = utc_now + datetime.timedelta(hours=8)
        return taipei_now.strftime("%Y-%m-%d %H:%M +0800")


if __name__ == "__main__":
    main()
