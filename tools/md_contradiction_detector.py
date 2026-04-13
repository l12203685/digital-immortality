#!/usr/bin/env python3
"""
md_contradiction_detector.py -- Scan markdown files for contradictions.

Usage:
    python md_contradiction_detector.py [directory] [--output report.md]

Detects:
  - Conflicting boolean statements (always/never, must/must not)
  - Conflicting numeric values for the same parameter keyword
  - Duplicate definitions with different values
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path


# Patterns that signal a claim
CLAIM_PATTERNS = [
    (r"\bMUST\s+NOT\b", "must_not"),
    (r"\bMUST\b", "must"),
    (r"\bNEVER\b", "never"),
    (r"\bALWAYS\b", "always"),
    (r"\bdefault\s+is\s+([^\s,\.]+)", "default"),
    (r"\bdefault:\s*([^\s,\.]+)", "default"),
    (r"^\s*\d+\.\s+(.+)", "numbered_rule"),
]

# Pairs of opposing claim types
OPPOSITES = [
    ("always", "never"),
    ("must", "must_not"),
    ("must", "never"),
    ("always", "must_not"),
]

# Regex to extract numeric param=value pairs (e.g. "timeout: 30", "port=8080")
NUMERIC_PARAM = re.compile(
    r"\b([a-z_][a-z0-9_\-]*)\s*[=:]\s*(\d+(?:\.\d+)?)\b", re.IGNORECASE
)

STRIP_MD = re.compile(r"[`*_~\[\]()]")

STOPWORDS = {
    "the", "and", "for", "are", "this", "that", "with", "from",
    "not", "use", "all", "any", "when", "will", "each", "file",
    "line", "code", "can", "you", "should", "must", "never",
    "always", "default", "note", "see", "add", "set", "per",
}


def extract_keywords(text):
    text = STRIP_MD.sub(" ", text)
    words = re.findall(r"[a-z][a-z0-9_\-]{2,}", text.lower())
    return [w for w in words if w not in STOPWORDS]


def scan_file(path):
    claims = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return claims

    for lineno, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("<!--"):
            continue

        for pattern, claim_type in CLAIM_PATTERNS:
            m = re.search(pattern, line, re.IGNORECASE)
            if m:
                value = m.group(1).strip() if m.lastindex and m.lastindex >= 1 else None
                claims.append({
                    "file": str(path),
                    "lineno": lineno,
                    "line": line[:120],
                    "type": claim_type,
                    "value": value,
                    "keywords": extract_keywords(line),
                })
                break  # one boolean claim type per line

        # Numeric param scan runs independently on every line
        for nm in NUMERIC_PARAM.finditer(line):
            claims.append({
                "file": str(path),
                "lineno": lineno,
                "line": line[:120],
                "type": "numeric_param",
                "param": nm.group(1).lower(),
                "value": nm.group(2),
                "keywords": [nm.group(1).lower()],
            })

    return claims


def find_md_files(directory):
    return sorted(Path(directory).rglob("*.md"))


def detect_contradictions(claims):
    contradictions = []

    # --- Boolean contradictions (always/never/must/must_not) ---
    kw_type = defaultdict(list)
    for c in claims:
        if c["type"] in ("always", "never", "must", "must_not"):
            for kw in c["keywords"]:
                kw_type[(kw, c["type"])].append(c)

    seen = set()
    all_kws = {k for k, _ in kw_type}
    for a_type, b_type in OPPOSITES:
        for kw in all_kws:
            a_list = kw_type.get((kw, a_type), [])
            b_list = kw_type.get((kw, b_type), [])
            if not a_list or not b_list:
                continue
            key = tuple(sorted([a_list[0]["file"], b_list[0]["file"]]) + [kw, a_type, b_type])
            if key in seen:
                continue
            seen.add(key)
            contradictions.append({
                "kind": "boolean_conflict",
                "keyword": kw,
                "a_type": a_type,
                "b_type": b_type,
                "a": a_list,
                "b": b_list,
            })

    # --- Numeric contradictions ---
    num_idx = defaultdict(list)
    for c in claims:
        if c["type"] == "numeric_param":
            num_idx[c["param"]].append(c)

    for param, entries in num_idx.items():
        by_value = defaultdict(list)
        for e in entries:
            by_value[e["value"]].append(e)
        if len(by_value) < 2:
            continue
        all_files = set().union(*(set(e["file"] for e in es) for es in by_value.values()))
        if len(all_files) < 2:
            continue
        contradictions.append({
            "kind": "numeric_conflict",
            "param": param,
            "values": dict(by_value),
        })

    return contradictions


def render_report(contradictions):
    out = ["# Markdown Contradiction Report\n"]
    if not contradictions:
        out.append("No contradictions detected.\n")
        return "\n".join(out)

    out.append(f"**{len(contradictions)} potential contradiction(s) found.**\n")

    for i, c in enumerate(contradictions, start=1):
        if c["kind"] == "boolean_conflict":
            out.append(f"## {i}. Boolean conflict: keyword `{c['keyword']}`")
            out.append(f"- Conflict: `{c['a_type']}` vs `{c['b_type']}`\n")
            out.append(f"**{c['a_type'].upper()} claims:**")
            for e in c["a"][:3]:
                out.append(f"- `{e['file']}` line {e['lineno']}: {e['line']}")
            out.append(f"\n**{c['b_type'].upper()} claims:**")
            for e in c["b"][:3]:
                out.append(f"- `{e['file']}` line {e['lineno']}: {e['line']}")
        elif c["kind"] == "numeric_conflict":
            out.append(f"## {i}. Numeric conflict: parameter `{c['param']}`")
            for val, entries in c["values"].items():
                out.append(f"\n**Value `{val}`:**")
                for e in entries[:3]:
                    out.append(f"- `{e['file']}` line {e['lineno']}: {e['line']}")
        out.append("")

    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(
        description="Scan markdown files for contradicting statements."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to scan (default: current directory)",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="Write report to FILE instead of stdout",
    )
    args = parser.parse_args()

    md_files = find_md_files(args.directory)
    if not md_files:
        print(f"No .md files found in {args.directory}", file=sys.stderr)
        sys.exit(1)

    all_claims = []
    for f in md_files:
        all_claims.extend(scan_file(f))

    contradictions = detect_contradictions(all_claims)
    report = render_report(contradictions)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        print(report)

    print(
        f"\nScanned {len(md_files)} file(s), {len(all_claims)} claim(s), "
        f"{len(contradictions)} contradiction(s).",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
