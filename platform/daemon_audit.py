"""
Daemon Audit — Self-evaluation and branch coverage tracking for the recursive daemon.

Reads results/daemon_log.md, analyzes branch coverage per cycle,
flags neglected branches, detects stuck/stale/low-quality cycles,
and generates a next-priority suggestion for the daemon to consume.
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = REPO_ROOT / "results" / "daemon_log.md"
PRIORITY_PATH = REPO_ROOT / "results" / "daemon_next_priority.txt"

# Domain branch definitions: branch name -> keyword patterns to detect
BRANCH_KEYWORDS: dict[str, list[str]] = {
    "經濟/trading": [
        "經濟", "trading", "trade", "backtest", "paper", "mainnet",
        "testnet", "策略", "strategy", "pnl", "P&L", "BTC", "signal",
        "regime", "portfolio", "tick", "revenue",
    ],
    "行為/DNA": [
        "行為", "DNA", "dna", "MD-", "micro-decision", "calibrat",
        "consistency", "aligned", "misaligned", "boot test",
    ],
    "學習/daemon": [
        "學習", "daemon", "trigger", "recursive", "engine", "staleness",
        "遞迴", "cycle", "loop",
    ],
    "社交/organism": [
        "社交", "organism", "collision", "samuel", "discord", "social",
        "relationship",
    ],
    "平台/skill": [
        "平台", "skill", "install", "onboard", "dashboard", "CI",
        "pipeline", "deploy", "export", "web platform",
    ],
    "存活/cold-start": [
        "存活", "cold-start", "cold start", "multi-provider",
        "anti-fragile", "recovery", "冗餘", "fallback",
    ],
    "知識/SOP": [
        "知識", "SOP", "workbook", "knowledge", "publish", "thread",
        "content", "monetiz",
    ],
    "生活/health": [
        "生活", "calendar", "health", "morning", "exercise",
        "cognitive", "peak", "routine",
    ],
}

NEGLECT_THRESHOLD = 3  # cycles without touch = neglected
STUCK_THRESHOLD = 3    # consecutive cycles on same branch = stuck


@dataclass(frozen=True)
class CycleEntry:
    """Immutable representation of a single daemon log cycle."""
    cycle_num: int
    timestamp: str
    content: str


@dataclass(frozen=True)
class BranchStatus:
    """Immutable status of a single branch."""
    name: str
    last_touched_cycle: int
    cycles_since_touched: int
    neglected: bool


@dataclass(frozen=True)
class AuditResult:
    """Immutable audit output."""
    total_cycles: int
    max_cycle: int
    branch_statuses: tuple[BranchStatus, ...]
    stuck_branch: Optional[str]
    stuck_count: int
    stale_tree_cycles: int
    low_quality_cycles: int
    suggestion: str


def parse_cycles(log_text: str) -> list[CycleEntry]:
    """Parse daemon_log.md into individual cycle entries."""
    pattern = re.compile(
        r"^## Cycle (\d+)\s*[—\-]\s*(.+?)$\n(.*?)(?=^## Cycle |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    entries: list[CycleEntry] = []
    for match in pattern.finditer(log_text):
        cycle_num = int(match.group(1))
        timestamp = match.group(2).strip()
        content = match.group(3).strip()
        entries.append(CycleEntry(
            cycle_num=cycle_num,
            timestamp=timestamp,
            content=content,
        ))
    return entries


def detect_branches_in_text(text: str) -> set[str]:
    """Detect which branches are mentioned in a piece of text."""
    text_lower = text.lower()
    touched: set[str] = set()
    for branch_name, keywords in BRANCH_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                touched.add(branch_name)
                break
    return touched


def compute_branch_coverage(
    cycles: list[CycleEntry],
) -> dict[str, int]:
    """Return {branch_name: last_cycle_num_touched} across all cycles."""
    last_touched: dict[str, int] = {name: 0 for name in BRANCH_KEYWORDS}
    for entry in cycles:
        touched = detect_branches_in_text(entry.content)
        for branch in touched:
            if entry.cycle_num > last_touched[branch]:
                last_touched[branch] = entry.cycle_num
    return last_touched


def detect_stuck(cycles: list[CycleEntry]) -> tuple[Optional[str], int]:
    """Detect if the daemon is stuck on one branch for too many consecutive cycles.

    Returns (branch_name, consecutive_count) or (None, 0).
    """
    if not cycles:
        return None, 0

    # Look at the last N cycles
    recent = cycles[-10:]
    # For each recent cycle, find the dominant branch (most keywords matched)
    dominant_sequence: list[Optional[str]] = []
    for entry in recent:
        touched = detect_branches_in_text(entry.content)
        if len(touched) == 1:
            dominant_sequence.append(next(iter(touched)))
        elif len(touched) == 0:
            dominant_sequence.append(None)
        else:
            # Multiple branches touched = not stuck on one
            dominant_sequence.append(None)

    # Count consecutive same-branch from the end
    if not dominant_sequence or dominant_sequence[-1] is None:
        return None, 0

    current = dominant_sequence[-1]
    count = 0
    for branch in reversed(dominant_sequence):
        if branch == current:
            count += 1
        else:
            break

    if count >= STUCK_THRESHOLD:
        return current, count
    return None, 0


def count_stale_tree_cycles(cycles: list[CycleEntry]) -> int:
    """Count cycles where the tree was not updated (no mention of tree/update/branch change)."""
    tree_keywords = ["tree", "branch", "update", "added", "removed", "modified", "pushed"]
    stale = 0
    for entry in cycles:
        text_lower = entry.content.lower()
        if not any(kw in text_lower for kw in tree_keywords):
            stale += 1
    return stale


def count_low_quality_cycles(cycles: list[CycleEntry]) -> int:
    """Count cycles where the log entry is very short (<50 chars)."""
    return sum(1 for entry in cycles if len(entry.content) < 50)


def generate_suggestion(
    branch_statuses: list[BranchStatus],
    stuck_branch: Optional[str],
    stuck_count: int,
    stale_tree_cycles: int,
    low_quality_cycles: int,
    total_cycles: int,
) -> str:
    """Generate a one-line priority suggestion for the next daemon cycle."""
    # Priority 1: neglected branches
    neglected = [b for b in branch_statuses if b.neglected]
    if neglected:
        worst = max(neglected, key=lambda b: b.cycles_since_touched)
        return (
            f"PRIORITY: Branch '{worst.name}' neglected for {worst.cycles_since_touched} cycles. "
            f"Do concrete work on this branch next cycle."
        )

    # Priority 2: stuck on one branch
    if stuck_branch is not None:
        return (
            f"PRIORITY: Stuck on '{stuck_branch}' for {stuck_count} consecutive cycles. "
            f"Switch to a different branch next cycle."
        )

    # Priority 3: stale tree
    if total_cycles > 0 and stale_tree_cycles / max(total_cycles, 1) > 0.3:
        return (
            "PRIORITY: Tree updates are sparse. "
            "Update results/dynamic_tree.md with concrete status changes next cycle."
        )

    # Priority 4: low quality
    if total_cycles > 0 and low_quality_cycles / max(total_cycles, 1) > 0.2:
        return (
            "PRIORITY: Too many low-quality log entries. "
            "Write substantive per-branch reports (>50 chars) each cycle."
        )

    # Priority 5: discovery mode — don't just maintain, grow
    # If all branches report OK, the system is stagnating. Push it to discover new needs.
    discovery_prompts = [
        "All branches maintained but no new growth. Ask: what NEW branch should exist that doesn't yet? Read dynamic_tree.md and find gaps.",
        "System stable. Backward check: what did Edward ask for in recent sessions that hasn't been built into an always-on system yet?",
        "No neglected branches but are any branches fake-healthy? Check: did last 5 cycles produce real git diffs or just log entries?",
        "Stable state. Push growth: read SKILL.md rules, find one rule the system violates, fix it.",
        "Discovery mode: read results/daemon_log.md last 20 entries. Are they diverse or repetitive? If repetitive, do something completely different.",
    ]
    import random
    return random.choice(discovery_prompts)


def run_audit() -> AuditResult:
    """Run the full audit and return structured results."""
    if not LOG_PATH.exists():
        return AuditResult(
            total_cycles=0,
            max_cycle=0,
            branch_statuses=(),
            stuck_branch=None,
            stuck_count=0,
            stale_tree_cycles=0,
            low_quality_cycles=0,
            suggestion="No daemon_log.md found. Run the daemon first.",
        )

    log_text = LOG_PATH.read_text(encoding="utf-8")
    cycles = parse_cycles(log_text)

    if not cycles:
        return AuditResult(
            total_cycles=0,
            max_cycle=0,
            branch_statuses=(),
            stuck_branch=None,
            stuck_count=0,
            stale_tree_cycles=0,
            low_quality_cycles=0,
            suggestion="No cycle entries found in daemon_log.md.",
        )

    max_cycle = max(entry.cycle_num for entry in cycles)
    last_touched = compute_branch_coverage(cycles)

    branch_statuses: list[BranchStatus] = []
    for name, last_cycle in sorted(last_touched.items()):
        gap = max_cycle - last_cycle
        branch_statuses.append(BranchStatus(
            name=name,
            last_touched_cycle=last_cycle,
            cycles_since_touched=gap,
            neglected=gap > NEGLECT_THRESHOLD,
        ))

    stuck_branch, stuck_count = detect_stuck(cycles)
    stale_tree_count = count_stale_tree_cycles(cycles)
    low_quality_count = count_low_quality_cycles(cycles)

    suggestion = generate_suggestion(
        branch_statuses=branch_statuses,
        stuck_branch=stuck_branch,
        stuck_count=stuck_count,
        stale_tree_cycles=stale_tree_count,
        low_quality_cycles=low_quality_count,
        total_cycles=len(cycles),
    )

    return AuditResult(
        total_cycles=len(cycles),
        max_cycle=max_cycle,
        branch_statuses=tuple(branch_statuses),
        stuck_branch=stuck_branch,
        stuck_count=stuck_count,
        stale_tree_cycles=stale_tree_count,
        low_quality_cycles=low_quality_count,
        suggestion=suggestion,
    )


def format_report(result: AuditResult) -> str:
    """Format the audit result as a human-readable report."""
    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("DAEMON AUDIT REPORT")
    lines.append("=" * 60)
    lines.append(f"Total cycle entries parsed: {result.total_cycles}")
    lines.append(f"Max cycle number: {result.max_cycle}")
    lines.append("")

    # Branch coverage
    lines.append("--- Branch Coverage ---")
    lines.append(f"{'Branch':<25} {'Last Cycle':>10} {'Gap':>5} {'Status':>10}")
    lines.append("-" * 55)
    for b in result.branch_statuses:
        status = "NEGLECTED" if b.neglected else "ok"
        lines.append(
            f"{b.name:<25} {b.last_touched_cycle:>10} {b.cycles_since_touched:>5} {status:>10}"
        )
    lines.append("")

    # Quality flags
    lines.append("--- Quality Flags ---")
    if result.stuck_branch:
        lines.append(
            f"[STUCK] On '{result.stuck_branch}' for {result.stuck_count} consecutive cycles"
        )
    else:
        lines.append("[STUCK] Not stuck (good)")

    stale_pct = (
        result.stale_tree_cycles / max(result.total_cycles, 1) * 100
    )
    lines.append(
        f"[STALE TREE] {result.stale_tree_cycles}/{result.total_cycles} "
        f"cycles without tree update ({stale_pct:.0f}%)"
    )

    lq_pct = (
        result.low_quality_cycles / max(result.total_cycles, 1) * 100
    )
    lines.append(
        f"[LOW QUALITY] {result.low_quality_cycles}/{result.total_cycles} "
        f"cycles with <50 char entries ({lq_pct:.0f}%)"
    )
    lines.append("")

    # Suggestion
    lines.append("--- Next Priority ---")
    lines.append(result.suggestion)
    lines.append("=" * 60)

    return "\n".join(lines)


def write_suggestion(suggestion: str) -> None:
    """Write the suggestion to results/daemon_next_priority.txt."""
    PRIORITY_PATH.parent.mkdir(parents=True, exist_ok=True)
    PRIORITY_PATH.write_text(suggestion, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Daemon Audit — self-evaluation and branch coverage tracking"
    )
    parser.add_argument(
        "--suggest",
        action="store_true",
        help="Only print the next priority suggestion (and write to file)",
    )
    args = parser.parse_args()

    result = run_audit()

    if args.suggest:
        print(result.suggestion)
        write_suggestion(result.suggestion)
    else:
        report = format_report(result)
        print(report)
        write_suggestion(result.suggestion)


if __name__ == "__main__":
    main()
