"""Cloud → LYH distillation write-back bridge (SOP#118 auto-sync).

Reads new distillation cycles from `memory/recursive_distillation.md`
(the cloud daemon's running append log), identifies which cycles have NOT
yet been written to `C:/Users/admin/LYH/agent/recursive_distillation.md`
(the LYH-persistent DNA layer), appends a compact summary block, and
updates `C:/Users/admin/LYH/memory/log.md`.

Why a script: prior state was fully manual. The daemon appends to the
cloud file on every cycle but has no awareness of LYH. This bridge makes
write-back idempotent and runnable from cron or daemon hook.

Usage:
    python -m tools.writeback_distillation --dry-run
    python -m tools.writeback_distillation --commit
"""
from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

CLOUD_DISTIL = Path("C:/Users/admin/workspace/digital-immortality/memory/recursive_distillation.md")
LYH_DISTIL = Path("C:/Users/admin/LYH/agent/recursive_distillation.md")
LYH_LOG = Path("C:/Users/admin/LYH/memory/log.md")
LYH_REPO = Path("C:/Users/admin/LYH")

CYCLE_HEADER = re.compile(r"^## Cycle (\d+)\s*(?:—|-)\s*(\S+)")
# Reject range headers like "## Cycle 262-270" — these are legacy backfill entries
# from a previous daemon numbering scheme. Canonical distil cycles are single ints.
CYCLE_RANGE_HEADER = re.compile(r"^## Cycle \d+\s*-\s*\d+")
INSIGHT_HEADER = re.compile(r"^### Insight (\d+):\s*(.+)$")


@dataclass(frozen=True)
class Insight:
    cycle: int
    index: int
    slug: str
    body: str
    tags: str = ""


@dataclass(frozen=True)
class Cycle:
    number: int
    timestamp: str
    insights: tuple  # tuple[Insight, ...] (hashable)


def parse_cloud(path: Path) -> List[Cycle]:
    """Parse cloud recursive_distillation.md into a list of Cycle objects."""
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    cycles: List[Cycle] = []
    cur_cycle: Optional[int] = None
    cur_ts: str = ""
    cur_insights: List[Insight] = []
    cur_insight_idx: Optional[int] = None
    cur_insight_slug: str = ""
    cur_body: List[str] = []
    cur_tags: str = ""

    def _flush_insight() -> None:
        nonlocal cur_insight_idx, cur_insight_slug, cur_body, cur_tags
        if cur_insight_idx is not None and cur_cycle is not None:
            body_text = "\n".join(cur_body).strip()
            cur_insights.append(Insight(
                cycle=cur_cycle, index=cur_insight_idx,
                slug=cur_insight_slug, body=body_text, tags=cur_tags,
            ))
        cur_insight_idx = None
        cur_insight_slug = ""
        cur_body = []
        cur_tags = ""

    def _flush_cycle() -> None:
        nonlocal cur_cycle, cur_ts, cur_insights
        _flush_insight()
        if cur_cycle is not None:
            cycles.append(Cycle(
                number=cur_cycle, timestamp=cur_ts,
                insights=tuple(cur_insights),
            ))
        cur_cycle = None
        cur_ts = ""
        cur_insights = []

    skip_current = False
    for line in lines:
        # Reject legacy range headers like "## Cycle 262-270 — ..." outright.
        if CYCLE_RANGE_HEADER.match(line):
            _flush_cycle()
            skip_current = True
            continue
        m = CYCLE_HEADER.match(line)
        if m:
            _flush_cycle()
            skip_current = False
            cur_cycle = int(m.group(1))
            cur_ts = m.group(2)
            continue
        if skip_current:
            continue
        mi = INSIGHT_HEADER.match(line)
        if mi:
            _flush_insight()
            cur_insight_idx = int(mi.group(1))
            cur_insight_slug = mi.group(2).strip()
            continue
        if line.startswith("**Tags**:"):
            cur_tags = line[len("**Tags**:"):].strip()
            continue
        if cur_insight_idx is not None and not line.startswith("**Signal source**"):
            cur_body.append(line)

    _flush_cycle()
    return cycles


def tail_distil_series(cycles: List[Cycle]) -> List[Cycle]:
    """Return only the last contiguous monotonically-increasing run.

    The cloud file mixes legacy daemon cycles (241, 243, 244, 257, ...) with
    the current distil series (95, 96, ..., N). When we see a backward jump
    (prev_number > current_number), that's a numbering-scheme reset — discard
    everything seen so far and start a fresh tail from the current cycle.

    This gives us only the genuine distil cycles at the tail of the file.
    """
    tail: List[Cycle] = []
    prev: Optional[int] = None
    for c in cycles:
        if prev is not None and c.number < prev:
            # Backward jump = reset signal. Drop prior accumulated cycles.
            tail = []
        tail.append(c)
        prev = c.number
    return tail


def last_writtenback_cycle(path: Path) -> int:
    """Return the highest cycle number already written back to LYH, or 0."""
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8")
    # Look for explicit write-back markers like "cycles 101–112" or "cycles N-M"
    matches = re.findall(r"cycles?\s*(\d+)[–\-](\d+)", text, re.IGNORECASE)
    if not matches:
        return 0
    return max(int(hi) for _, hi in matches)


def new_cycles_since(cycles: List[Cycle], last_done: int) -> List[Cycle]:
    return [c for c in cycles if c.number > last_done]


def build_writeback_block(new_cycles: List[Cycle]) -> str:
    """Compact summary block for LYH — one line per insight."""
    if not new_cycles:
        return ""
    lo = min(c.number for c in new_cycles)
    hi = max(c.number for c in new_cycles)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [f"## H. Auto write-back cycles {lo}–{hi} ({date})",
             "",
             f"> Auto-generated by `tools/writeback_distillation.py`. "
             f"Source: workspace/digital-immortality/memory/recursive_distillation.md"
             f" cycles {lo}~{hi}.",
             ""]
    for cycle in new_cycles:
        if not cycle.insights:
            continue
        lines.append(f"### Cycle {cycle.number} ({cycle.timestamp})")
        for ins in cycle.insights:
            first_sentence = ins.body.split("。")[0].split(".")[0].strip()[:180]
            if not first_sentence:
                first_sentence = ins.slug
            lines.append(f"- **{ins.slug}**: {first_sentence}")
        lines.append("")
    return "\n".join(lines)


def insert_before_marker(target: Path, block: str, marker: str = "## 分類演化規則") -> bool:
    """Insert block immediately before marker line. Returns True if inserted."""
    text = target.read_text(encoding="utf-8")
    if marker not in text:
        return False
    new_text = text.replace(marker, block + "\n---\n\n" + marker, 1)
    target.write_text(new_text, encoding="utf-8")
    return True


def append_log_entry(log_path: Path, lo: int, hi: int, insight_count: int) -> None:
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    entry = (f"\n## {date} auto write-back cycles {lo}–{hi}\n"
             f"- tools/writeback_distillation.py synced {insight_count} insights "
             f"from cloud → LYH/agent/recursive_distillation.md\n")
    with log_path.open("a", encoding="utf-8") as f:
        f.write(entry)


def git_commit(repo: Path, lo: int, hi: int, insight_count: int) -> None:
    subprocess.run(["git", "-C", str(repo), "add",
                    "agent/recursive_distillation.md", "memory/log.md"],
                   check=True)
    msg = (f"distil: auto write-back cycles {lo}-{hi} ({insight_count} insights)\n\n"
           f"Generated by tools/writeback_distillation.py. "
           f"Source: workspace/digital-immortality/memory/recursive_distillation.md.")
    subprocess.run(["git", "-C", str(repo), "commit", "-m", msg], check=True)


def main() -> None:
    p = argparse.ArgumentParser(description="Cloud → LYH distillation write-back")
    p.add_argument("--dry-run", action="store_true", help="Preview without writing")
    p.add_argument("--commit", action="store_true", help="Git commit after writeback")
    p.add_argument("--cloud", type=Path, default=CLOUD_DISTIL)
    p.add_argument("--lyh", type=Path, default=LYH_DISTIL)
    args = p.parse_args()

    cycles = parse_cloud(args.cloud)
    if not cycles:
        print(f"No cycles parsed from {args.cloud}")
        return
    cycles = tail_distil_series(cycles)
    if not cycles:
        print("No distil cycles found in tail series")
        return
    last_done = last_writtenback_cycle(args.lyh)
    new = new_cycles_since(cycles, last_done)
    if not new:
        print(f"No new cycles to write back. Highest LYH cycle: {last_done}")
        return

    lo = min(c.number for c in new)
    hi = max(c.number for c in new)
    insight_count = sum(len(c.insights) for c in new)
    block = build_writeback_block(new)
    print(f"Detected {len(new)} new cycles ({lo}-{hi}), {insight_count} insights")

    if args.dry_run:
        print("--- DRY RUN ---")
        print(block[:2000])
        if len(block) > 2000:
            print(f"... [{len(block) - 2000} more chars]")
        return

    if not insert_before_marker(args.lyh, block):
        print(f"ERROR: marker '## 分類演化規則' not found in {args.lyh}")
        return
    append_log_entry(LYH_LOG, lo, hi, insight_count)
    print(f"Wrote {insight_count} insights into {args.lyh}")
    print(f"Appended log entry to {LYH_LOG}")

    if args.commit:
        git_commit(LYH_REPO, lo, hi, insight_count)
        print(f"Committed to {LYH_REPO}")


if __name__ == "__main__":
    main()
