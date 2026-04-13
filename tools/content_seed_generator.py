"""B7 Content Seed Generator — extract publishable insights from recursive distillation."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DISTILL = ROOT / "memory" / "recursive_distillation.md"
GRAPH = ROOT / "results" / "sop_graph_analysis.md"
OUTPUT = ROOT / "results" / "content_seeds.md"

# --- parsing ---

def parse_insights(text: str) -> list[dict]:
    """Extract all ### Insight blocks with cycle metadata."""
    insights = []
    cycle_pat = re.compile(r"^## Cycle (\d+)", re.MULTILINE)
    insight_pat = re.compile(
        r"### Insight \d+:\s*(.+?)\n\n(.+?)(?=\n\*\*Signal source\*\*)",
        re.DOTALL,
    )
    tag_pat = re.compile(r"\*\*Tags\*\*:\s*(.+)")
    cycles = list(cycle_pat.finditer(text))
    for i, cm in enumerate(cycles):
        end = cycles[i + 1].start() if i + 1 < len(cycles) else len(text)
        block = text[cm.start():end]
        cycle_num = int(cm.group(1))
        for im in insight_pat.finditer(block):
            slug = im.group(1).strip()
            body = im.group(2).strip()
            tags_m = tag_pat.search(block[im.start():im.end() + 300])
            tags = [t.strip() for t in tags_m.group(1).split(",")] if tags_m else []
            insights.append({"cycle": cycle_num, "slug": slug, "body": body, "tags": tags})
    return insights


def parse_graph_hubs(text: str) -> list[str]:
    """Extract hub SOP names from graph analysis."""
    hubs = re.findall(r"\| \d \| (#\d+ .+?) \|", text)
    return hubs


# --- scoring ---

CATEGORY_KEYWORDS = {
    "trading": ["trading", "strategy", "backtest", "WFO", "regime", "entry", "exit",
                 "portfolio", "sizing", "stop-loss", "SBF", "DualMA", "Donchian", "prop-desk"],
    "meta-strategy": ["meta-strategy", "decision-kernel", "derivative", "population",
                      "inaction-bias", "edge", "contrarian", "closed-loop", "lifecycle"],
    "systems": ["architecture", "infrastructure", "daemon", "cold-start", "boot",
                "gate", "protocol", "SOP", "tripwire", "monitoring", "taxonomy"],
    "philosophy": ["immortality", "identity", "DNA", "recursive", "distillation",
                   "zeroth-principles", "convergence", "behavioral-equivalence"],
}

EXCLUDE_SLUGS = {"btc", "tick", "clean-cycle", "human-tick", "paper-live"}


def categorize(insight: dict) -> list[str]:
    combined = " ".join(insight["tags"]) + " " + insight["body"][:200]
    cats = []
    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(kw.lower() in combined.lower() for kw in kws):
            cats.append(cat)
    return cats or ["general"]


def score(insight: dict) -> float:
    body = insight["body"]
    tags = " ".join(insight["tags"])
    s = 0.0
    # Novelty: unique slug words, not routine ticks
    if any(ex in insight["slug"].lower() for ex in EXCLUDE_SLUGS):
        return 0.0  # skip routine tick logs
    s += min(len(insight["slug"].split("-")), 8) * 0.5  # concept density
    # Completeness: longer body with structural language
    s += min(len(body) / 400, 3.0)
    for marker in ["principle", "framework", "transferable", "architecture",
                    "ZP-applicable", "community", "lesson", "design"]:
        if marker.lower() in body.lower() or marker.lower() in tags.lower():
            s += 1.0
    # Public relevance: ZP-applicable or transferable tags
    if "ZP-applicable" in tags or "transferable-framework" in tags:
        s += 3.0
    if "methodology" in tags:
        s += 1.5
    return round(s, 2)


def suggest_format(insight: dict) -> str:
    length = len(insight["body"])
    cats = categorize(insight)
    if length > 1500 and len(cats) > 1:
        return "article"
    if length > 800:
        return "post"
    return "thread"


def make_hook(insight: dict) -> str:
    """Generate a 2-line hook from the body."""
    sentences = re.split(r"(?<=[.!?])\s+", insight["body"])
    first = sentences[0] if sentences else ""
    # Find the "lesson" or "implication" sentence
    for s in sentences[1:]:
        if any(w in s.lower() for w in ["lesson", "principle", "implication", "key",
                                         "transferable", "significance", "insight"]):
            return f"{first}\n{s}"
    second = sentences[1] if len(sentences) > 1 else ""
    return f"{first}\n{second}"


# --- main ---

def main():
    distill_text = DISTILL.read_text(encoding="utf-8")
    graph_text = GRAPH.read_text(encoding="utf-8")

    insights = parse_insights(distill_text)
    hubs = parse_graph_hubs(graph_text)

    scored = [(score(i), i) for i in insights]
    scored.sort(key=lambda x: -x[0])
    top10 = scored[:10]

    lines = [
        "# Content Seeds — B7 Knowledge Output\n",
        f"Generated: 2026-04-14 | Source: {len(insights)} insights from recursive_distillation.md\n",
        f"SOP graph hubs: {', '.join(hubs[:5])}\n",
        "---\n",
    ]
    for rank, (sc, ins) in enumerate(top10, 1):
        cats = categorize(ins)
        hook = make_hook(ins)
        fmt = suggest_format(ins)
        title = ins["slug"].replace("-", " ").title()
        lines.append(f"## {rank}. {title}")
        lines.append(f"**Score**: {sc} | **Cycle**: {ins['cycle']} | **Format**: {fmt}")
        lines.append(f"**Categories**: {', '.join(cats)}\n")
        lines.append(f"> {hook}\n")
        lines.append(f"**Source insight**: `{ins['slug']}` (cycle {ins['cycle']})\n")
        lines.append("---\n")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {len(top10)} content seeds to {OUTPUT}")
    for rank, (sc, ins) in enumerate(top10, 1):
        print(f"  {rank}. [{sc}] {ins['slug'][:60]}")


if __name__ == "__main__":
    main()
