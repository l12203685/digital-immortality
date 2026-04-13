#!/usr/bin/env python3
"""
SOP Graph Builder — B7 Knowledge Productization Tool
Builds a cross-reference dependency graph for the digital-immortality SOP series.

Usage:
    python tools/sop_graph_builder.py
    python tools/sop_graph_builder.py --dot          # also write Graphviz DOT
    python tools/sop_graph_builder.py --search-path  # show discovered paths
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"

SOP_SEARCH_DIRS: List[Path] = [
    PROJECT_ROOT / "docs",
    PROJECT_ROOT / "docs" / "archive",
    PROJECT_ROOT / "systems",
    Path.home() / "ZP",
    Path.home() / "ZP" / "thinking",
    Path.home() / "ZP" / "building",
]

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------
# Matches the SOP number declared in the file header.
# Handles: "SOP #42", "SOP#42", "Knowledge Product #42", "#42 —"
HEADER_RE = re.compile(
    r"(?:Knowledge\s+Product\s+#|SOP\s*#|^#\s+SOP\s+#)(\d+)",
    re.IGNORECASE | re.MULTILINE,
)

# Filename pattern: knowledge_product_NNN_*.md  (NNN may be 1–3 digits)
FILENAME_NUM_RE = re.compile(r"knowledge_product_0*(\d+)[_.]", re.IGNORECASE)

# Title extraction — first line starting with "# "
TITLE_LINE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)

# References inside a file body: "SOP #42", "SOP#42"
# We deliberately NOT match the file's own header declaration (handled separately)
REF_RE = re.compile(r"\bSOP\s*#(\d+)\b", re.IGNORECASE)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_sop_files() -> List[Path]:
    """Return all markdown files that look like SOP knowledge products."""
    found: List[Path] = []
    seen: Set[Path] = set()

    for search_dir in SOP_SEARCH_DIRS:
        if not search_dir.exists():
            continue
        for md_file in search_dir.glob("*.md"):
            resolved = md_file.resolve()
            if resolved in seen:
                continue
            # Must match the knowledge_product_NNN naming convention
            if FILENAME_NUM_RE.search(md_file.name):
                seen.add(resolved)
                found.append(md_file)

    found.sort(key=lambda p: _filename_number(p.name) or 9999)
    return found


def _filename_number(filename: str) -> Optional[int]:
    m = FILENAME_NUM_RE.search(filename)
    return int(m.group(1)) if m else None


def extract_sop_number(filename: str, content: str) -> Optional[int]:
    """
    Best-effort: prefer the canonical number embedded in the filename,
    falling back to the header declaration.
    """
    n = _filename_number(filename)
    if n is not None:
        return n

    # Try header declaration
    m = HEADER_RE.search(content[:400])   # only look in first ~400 chars
    if m:
        return int(m.group(1))
    return None


def extract_title(content: str) -> str:
    m = TITLE_LINE_RE.search(content[:600])
    if m:
        raw = m.group(1).strip()
        # Trim markdown emphasis characters
        raw = re.sub(r"[*_`]", "", raw)
        return raw[:120]
    return "(untitled)"


def extract_references(sop_number: int, content: str) -> Set[int]:
    """
    Extract all SOP numbers referenced in the body.
    Excludes the file's own self-reference from its header.
    """
    refs: Set[int] = set()
    for m in REF_RE.finditer(content):
        ref_num = int(m.group(1))
        if ref_num != sop_number:
            refs.add(ref_num)
    return refs


# ---------------------------------------------------------------------------
# Graph
# ---------------------------------------------------------------------------

class SOPGraph:
    def __init__(self) -> None:
        # sop_num -> {"title": str, "file": str, "refs_out": set[int]}
        self.nodes: Dict[int, dict] = {}
        # sop_num -> set of sop nums that reference IT (in-edges)
        self.in_edges: Dict[int, Set[int]] = defaultdict(set)

    def add_node(self, num: int, title: str, filepath: str) -> None:
        if num not in self.nodes:
            self.nodes[num] = {"title": title, "file": filepath, "refs_out": set()}

    def add_edge(self, from_num: int, to_num: int) -> None:
        self.nodes[from_num]["refs_out"].add(to_num)
        self.in_edges[to_num].add(from_num)

    def all_numbers(self) -> Set[int]:
        referenced = set()
        for n in self.nodes.values():
            referenced.update(n["refs_out"])
        return set(self.nodes.keys()) | referenced

    def in_degree(self, num: int) -> int:
        return len(self.in_edges.get(num, set()))

    def out_degree(self, num: int) -> int:
        return len(self.nodes.get(num, {}).get("refs_out", set()))

    def find_clusters(self, min_size: int = 3) -> List[List[int]]:
        """
        Simple connected-components clustering treating edges as undirected.
        Returns groups of size >= min_size, sorted by descending size.
        """
        adj: Dict[int, Set[int]] = defaultdict(set)
        for num, node in self.nodes.items():
            for ref in node["refs_out"]:
                adj[num].add(ref)
                adj[ref].add(num)

        visited: Set[int] = set()
        clusters: List[List[int]] = []

        for start in sorted(adj.keys()):
            if start in visited:
                continue
            component: List[int] = []
            stack = [start]
            while stack:
                cur = stack.pop()
                if cur in visited:
                    continue
                visited.add(cur)
                component.append(cur)
                stack.extend(adj[cur] - visited)
            if len(component) >= min_size:
                clusters.append(sorted(component))

        clusters.sort(key=len, reverse=True)
        return clusters


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build_graph(sop_files: List[Path]) -> SOPGraph:
    graph = SOPGraph()
    skipped: List[str] = []

    for filepath in sop_files:
        try:
            content = filepath.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            skipped.append(f"{filepath.name}: {exc}")
            continue

        num = extract_sop_number(filepath.name, content)
        if num is None:
            skipped.append(f"{filepath.name}: cannot determine SOP number")
            continue

        title = extract_title(content)
        graph.add_node(num, title, str(filepath))

    # Second pass: extract cross-references (all nodes registered first)
    for filepath in sop_files:
        try:
            content = filepath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        num = extract_sop_number(filepath.name, content)
        if num is None or num not in graph.nodes:
            continue

        refs = extract_references(num, content)
        for ref_num in refs:
            graph.add_edge(num, ref_num)

    if skipped:
        print(f"[WARN] Skipped {len(skipped)} file(s):")
        for s in skipped:
            print(f"  • {s}")

    return graph


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def print_adjacency_list(graph: SOPGraph) -> None:
    print("\n" + "=" * 70)
    print("ADJACENCY LIST")
    print("=" * 70)
    for num in sorted(graph.nodes.keys()):
        node = graph.nodes[num]
        refs_out = sorted(node["refs_out"])
        refs_in = sorted(graph.in_edges.get(num, set()))
        # Strip non-ASCII from title for safe console output
        short_title = node["title"][:60].encode("ascii", "replace").decode("ascii")
        print(f"\nSOP #{num:03d}  {short_title}")
        if refs_out:
            print(f"  -> references: {', '.join(f'#{n}' for n in refs_out)}")
        else:
            print(f"  -> references: (none)")
        if refs_in:
            print(f"  <- referenced by: {', '.join(f'#{n}' for n in refs_in)}")
        else:
            print(f"  <- referenced by: (none)")


def print_top_referenced(graph: SOPGraph, top_n: int = 10) -> None:
    print("\n" + "=" * 70)
    print(f"TOP {top_n} MOST-REFERENCED SOPs  (highest in-degree = most foundational)")
    print("=" * 70)

    # Collect in-degree for all SOPs that appear in refs (even if no file found)
    all_nums = graph.all_numbers()
    ranked = sorted(all_nums, key=lambda n: graph.in_degree(n), reverse=True)[:top_n]

    for rank, num in enumerate(ranked, 1):
        indeg = graph.in_degree(num)
        outdeg = graph.out_degree(num)
        if num in graph.nodes:
            title = graph.nodes[num]["title"][:55].encode("ascii", "replace").decode("ascii")
            status = ""
        else:
            title = "(file not found)"
            status = " [ref-only]"
        print(f"  {rank:2d}. SOP #{num:03d}  in={indeg}  out={outdeg}  {title}{status}")


def print_orphans(graph: SOPGraph) -> None:
    print("\n" + "=" * 70)
    print("ORPHAN SOPs  (no in-edges AND no out-edges)")
    print("=" * 70)
    orphans = []
    for num in sorted(graph.nodes.keys()):
        if graph.in_degree(num) == 0 and graph.out_degree(num) == 0:
            orphans.append(num)

    if orphans:
        for num in orphans:
            title = graph.nodes[num]["title"][:60].encode("ascii", "replace").decode("ascii")
            print(f"  SOP #{num:03d}  {title}")
    else:
        print("  (none - all SOPs have at least one connection)")


def print_clusters(graph: SOPGraph) -> None:
    print("\n" + "=" * 70)
    print("CLUSTERS  (connected components, size >= 3)")
    print("=" * 70)
    clusters = graph.find_clusters(min_size=3)

    if not clusters:
        print("  (no clusters with 3+ members found)")
        return

    for i, cluster in enumerate(clusters, 1):
        print(f"\n  Cluster {i}  ({len(cluster)} SOPs):")
        nums_str = ", ".join(f"#{n}" for n in cluster)
        # Wrap at ~70 chars
        line = "    "
        for token in nums_str.split(", "):
            if len(line) + len(token) + 2 > 72:
                print(line.rstrip(", "))
                line = "    "
            line += token + ", "
        if line.strip().rstrip(","):
            print(line.rstrip(", "))


# ---------------------------------------------------------------------------
# DOT output
# ---------------------------------------------------------------------------

def build_dot(graph: SOPGraph) -> str:
    lines = ['digraph sop_graph {', '  rankdir=LR;', '  node [shape=box fontsize=10];', '']

    for num in sorted(graph.nodes.keys()):
        title = graph.nodes[num]["title"]
        # Escape quotes
        safe_title = title.replace('"', '\\"')[:50]
        indeg = graph.in_degree(num)
        # Color nodes by in-degree quintile
        if indeg >= 30:
            color = "#d73027"   # red — very foundational
        elif indeg >= 15:
            color = "#fc8d59"   # orange
        elif indeg >= 5:
            color = "#fee090"   # yellow
        else:
            color = "#e0f3f8"   # light blue — leaf
        lines.append(f'  n{num} [label="#{num}\\n{safe_title}" style=filled fillcolor="{color}"];')

    lines.append('')
    for num in sorted(graph.nodes.keys()):
        for ref in sorted(graph.nodes[num]["refs_out"]):
            lines.append(f'  n{num} -> n{ref};')

    lines.append('}')
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# JSON serialisation
# ---------------------------------------------------------------------------

def build_json_payload(graph: SOPGraph) -> dict:
    nodes_payload = {}
    for num, node in graph.nodes.items():
        nodes_payload[str(num)] = {
            "sop_number": num,
            "title": node["title"],
            "file": node["file"],
            "refs_out": sorted(node["refs_out"]),
            "refs_in": sorted(graph.in_edges.get(num, set())),
            "in_degree": graph.in_degree(num),
            "out_degree": graph.out_degree(num),
        }

    # Also record referenced-only SOPs (mentioned but no file)
    ghost_nodes = {}
    for num in graph.all_numbers():
        if num not in graph.nodes:
            ghost_nodes[str(num)] = {
                "sop_number": num,
                "title": None,
                "file": None,
                "refs_out": [],
                "refs_in": sorted(graph.in_edges.get(num, set())),
                "in_degree": graph.in_degree(num),
                "out_degree": 0,
            }

    top10 = sorted(
        graph.all_numbers(),
        key=lambda n: graph.in_degree(n),
        reverse=True,
    )[:10]

    orphans = [
        n for n in sorted(graph.nodes.keys())
        if graph.in_degree(n) == 0 and graph.out_degree(n) == 0
    ]

    clusters = graph.find_clusters(min_size=3)

    return {
        "meta": {
            "total_sop_files": len(graph.nodes),
            "total_references": sum(
                len(n["refs_out"]) for n in graph.nodes.values()
            ),
            "total_unique_sops_referenced": len(graph.all_numbers()),
            "ghost_sops_referenced_but_no_file": len(ghost_nodes),
        },
        "nodes": nodes_payload,
        "ghost_nodes": ghost_nodes,
        "top10_most_referenced": [
            {
                "sop_number": n,
                "in_degree": graph.in_degree(n),
                "title": graph.nodes[n]["title"] if n in graph.nodes else None,
            }
            for n in top10
        ],
        "orphans": orphans,
        "clusters": clusters,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a cross-reference graph for the digital-immortality SOP series."
    )
    parser.add_argument(
        "--dot",
        action="store_true",
        help="Also write a Graphviz DOT file to results/sop_graph.dot",
    )
    parser.add_argument(
        "--search-path",
        action="store_true",
        help="Print the directories that will be searched and exit",
    )
    args = parser.parse_args()

    if args.search_path:
        print("Search directories:")
        for d in SOP_SEARCH_DIRS:
            status = "EXISTS" if d.exists() else "missing"
            print(f"  [{status}]  {d}")
        return 0

    # --- Discover files ---
    sop_files = find_sop_files()
    if not sop_files:
        print("[ERROR] No SOP files found. Searched:")
        for d in SOP_SEARCH_DIRS:
            print(f"  {d}")
        print("\nExpected filename pattern: knowledge_product_NNN_*.md")
        return 1

    print(f"[INFO] Found {len(sop_files)} SOP file(s) across {len(SOP_SEARCH_DIRS)} search paths.")

    # --- Build graph ---
    graph = build_graph(sop_files)
    print(
        f"[INFO] Graph: {len(graph.nodes)} nodes, "
        f"{sum(len(n['refs_out']) for n in graph.nodes.values())} directed edges."
    )

    # --- Console report ---
    # Force UTF-8 output on Windows to avoid cp950 codec errors
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    print_adjacency_list(graph)
    print_top_referenced(graph, top_n=10)
    print_orphans(graph)
    print_clusters(graph)

    # --- Save JSON ---
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = RESULTS_DIR / "sop_graph.json"
    payload = build_json_payload(graph)
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    print(f"\n[SAVED] {json_path}")

    # --- Optional DOT ---
    if args.dot:
        dot_path = RESULTS_DIR / "sop_graph.dot"
        dot_content = build_dot(graph)
        with open(dot_path, "w", encoding="utf-8") as fh:
            fh.write(dot_content)
        print(f"[SAVED] {dot_path}  (render with: dot -Tpng {dot_path} -o sop_graph.png)")

    # --- Summary ---
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    meta = payload["meta"]
    print(f"  SOP files parsed       : {meta['total_sop_files']}")
    print(f"  Total reference edges  : {meta['total_references']}")
    print(f"  Unique SOPs referenced : {meta['total_unique_sops_referenced']}")
    print(f"  Ghost SOPs (ref-only)  : {meta['ghost_sops_referenced_but_no_file']}")
    print(f"  Orphan SOPs            : {len(payload['orphans'])}")
    print(f"  Clusters (size ≥ 3)    : {len(payload['clusters'])}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
