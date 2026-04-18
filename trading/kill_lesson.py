"""
Kill-Lesson Extraction System — Virtuous Cycle Component.

Analyzes losing trades from kill_lessons.jsonl to extract:
  - Kill patterns (what went wrong, structural classification)
  - Lesson entries (actionable rules to avoid repetition)
  - ZP principle cross-references (which first principles were violated)

Outputs:
  - results/lessons/<date>_kill_analysis.jsonl   (machine-consumable)
  - results/lessons/<date>_kill_analysis.md       (human-readable summary)

This module is READ-ONLY on existing trading state. It does not modify
engine behavior directly — its output feeds into strategy_generator
params and human review.

Usage:
    python -m trading.kill_lesson                    # analyze all unprocessed kills
    python -m trading.kill_lesson --last N            # analyze last N kills
    python -m trading.kill_lesson --strategy NAME     # filter by strategy
    python -m trading.kill_lesson --dry-run            # print without writing files
"""
from __future__ import annotations

import json
import logging
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

logger = logging.getLogger("trading.kill_lesson")

_TAIPEI = timezone(timedelta(hours=8))

# --- Paths ---
ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
KILLS_LOG = RESULTS / "kill_lessons.jsonl"
ENGINE_LOG = RESULTS / "trading_engine_log.jsonl"
LESSONS_DIR = RESULTS / "lessons"
PROCESSED_SET = LESSONS_DIR / ".processed_kills.json"

# --- ZP Principles Registry ---
# Each principle is a (tag, name, violation_detector) tuple.
# violation_detector: callable(kill_record, context) -> Optional[str]
# Returns explanation if violated, None if not applicable.

ZP_PRINCIPLES_DIR = Path("C:/Users/admin/ZP/building")

# Principle tags mapped to their core assertion + detection heuristic
ZP_PRINCIPLES: Dict[str, Dict[str, str]] = {
    "asymmetric_return": {
        "source": "investment_first_principles.md#3",
        "name": "Asymmetric Return (MDD > target)",
        "rule": "Avoiding fatal loss >> chasing gains. MDD is the primary metric.",
        "detect": "mdd",
    },
    "negative_list_priority": {
        "source": "negative_list_priority.md",
        "name": "Negative List > Positive Target",
        "rule": "Constraints survive pressure; goals evaporate. "
                "The system's stability comes from what it refuses, not what it pursues.",
        "detect": "repeated_kill",
    },
    "entry_diversity_exit_convergence": {
        "source": "entry_diversity_exit_convergence.md",
        "name": "Entry Diversity vs Exit Convergence",
        "rule": "Alpha is in entry divergence; survival is in exit convergence. "
                "Standardize exits, diversify entries.",
        "detect": "exit_failure",
    },
    "optimization_ceiling": {
        "source": "optimization_ceiling_structural_edge.md",
        "name": "Optimization Ceiling vs Structural Edge",
        "rule": "Parameter-optimized strategies collapse under regime shift. "
                "Structural edge (L3/L4) survives; parametric edge (L1) doesn't.",
        "detect": "regime_mismatch",
    },
    "regime_as_input": {
        "source": "regime_as_input_not_background.md",
        "name": "Regime as Input, Not Background",
        "rule": "Strategies that treat regime as background assumption fail "
                "when regime shifts. Regime must be a runtime input.",
        "detect": "regime_mismatch",
    },
    "survival_leverage": {
        "source": "investment_first_principles.md#6",
        "name": "Survival Leverage Principle",
        "rule": "Survival is the precondition for leverage. "
                "Dying from illiquidity, not from asset going to zero.",
        "detect": "daily_cap",
    },
    "risk_control_l3": {
        "source": "risk_control_four_layers.md",
        "name": "L3 Anomaly Compensation / Infrastructure Risk",
        "rule": "Distinguish infrastructure-caused losses from strategy-caused losses. "
                "Don't penalize strategy for exchange/network anomalies.",
        "detect": "infrastructure",
    },
}


# --- Data Structures ---

@dataclass(frozen=True)
class KillRecord:
    """Immutable representation of a single kill event from kill_lessons.jsonl."""
    ts: str
    tick: int
    strategy: str
    kill_reason: str
    cum_pnl: float
    price_at_kill: float
    regime_at_kill: str
    rule_change: str

    @classmethod
    def from_dict(cls, d: Dict) -> "KillRecord":
        return cls(
            ts=d.get("ts", ""),
            tick=d.get("tick", 0),
            strategy=d.get("strategy", ""),
            kill_reason=d.get("kill_reason", ""),
            cum_pnl=d.get("cum_pnl", 0.0),
            price_at_kill=d.get("price_at_kill", 0.0),
            regime_at_kill=d.get("regime_at_kill", "unknown"),
            rule_change=d.get("rule_change", ""),
        )


@dataclass(frozen=True)
class KillPattern:
    """Classified pattern extracted from one or more kills."""
    pattern_id: str
    category: str           # mdd | pf_decay | wr_collapse | regime_mismatch | repeated_restart
    description: str
    severity: str            # critical | high | medium
    affected_strategies: Tuple[str, ...]
    kill_count: int
    avg_cum_pnl: float
    regime_context: str
    tick_range: Tuple[int, int]


@dataclass(frozen=True)
class Lesson:
    """Actionable lesson derived from kill pattern analysis."""
    lesson_id: str
    pattern_id: str
    action: str              # avoid | tighten | monitor | exclude_regime | restructure
    description: str
    constraint_rule: str     # machine-readable constraint for strategy_generator
    zp_principles: Tuple[str, ...]  # which ZP principles this maps to
    confidence: str          # high | medium | low
    expires: Optional[str]   # ISO date after which this lesson should be re-evaluated


@dataclass
class KillAnalysis:
    """Complete analysis output for a batch of kills."""
    generated_at: str
    kill_count: int
    patterns: List[KillPattern] = field(default_factory=list)
    lessons: List[Lesson] = field(default_factory=list)
    zp_cross_refs: List[Dict[str, str]] = field(default_factory=list)
    strategy_summary: Dict[str, Dict] = field(default_factory=dict)


# --- Core Analysis Functions ---

def load_kills(path: Path = KILLS_LOG) -> List[KillRecord]:
    """Load all kill records from JSONL file."""
    if not path.exists():
        return []
    records: List[KillRecord] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(KillRecord.from_dict(json.loads(line)))
        except (json.JSONDecodeError, KeyError) as exc:
            logger.warning("Skipping malformed kill record: %s", exc)
    return records


def load_processed_set() -> set:
    """Load set of already-processed kill timestamps to avoid re-analysis."""
    if not PROCESSED_SET.exists():
        return set()
    try:
        return set(json.loads(PROCESSED_SET.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, OSError):
        return set()


def save_processed_set(processed: set) -> None:
    """Persist the set of processed kill timestamps."""
    LESSONS_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_SET.write_text(
        json.dumps(sorted(processed), ensure_ascii=False),
        encoding="utf-8",
    )


def parse_kill_reason(reason: str) -> Tuple[str, float, float]:
    """Extract kill category and numeric values from kill_reason string.

    Returns (category, actual_value, threshold).
    Examples:
        "PF 0.78 < 0.8"  -> ("pf_decay", 0.78, 0.8)
        "MDD 22.5% > 20%" -> ("mdd", 22.5, 20.0)
        "WR 25.0% < 30%"  -> ("wr_collapse", 25.0, 30.0)
    """
    reason_lower = reason.lower()
    if "pf" in reason_lower:
        match = re.search(r"PF\s+([\d.]+)\s*<\s*([\d.]+)", reason, re.IGNORECASE)
        if match:
            return ("pf_decay", float(match.group(1)), float(match.group(2)))
        return ("pf_decay", 0.0, 0.0)
    if "mdd" in reason_lower:
        match = re.search(r"MDD\s+([\d.]+)%?\s*>\s*([\d.]+)", reason, re.IGNORECASE)
        if match:
            return ("mdd", float(match.group(1)), float(match.group(2)))
        return ("mdd", 0.0, 0.0)
    if "wr" in reason_lower:
        match = re.search(r"WR\s+([\d.]+)%?\s*<\s*([\d.]+)", reason, re.IGNORECASE)
        if match:
            return ("wr_collapse", float(match.group(1)), float(match.group(2)))
        return ("wr_collapse", 0.0, 0.0)
    return ("unknown", 0.0, 0.0)


def classify_kills(kills: Sequence[KillRecord]) -> List[KillPattern]:
    """Group kills into patterns by strategy + category + regime.

    A pattern captures a recurring failure mode. Multiple kills of the
    same strategy for the same reason in the same regime = one pattern
    with higher severity.
    """
    # Group by (strategy_base, category, regime)
    groups: Dict[Tuple[str, str, str], List[KillRecord]] = defaultdict(list)
    for k in kills:
        category, _, _ = parse_kill_reason(k.kill_reason)
        # Normalize generated strategy names: strip hash suffix for grouping
        base_name = re.sub(r"_[0-9a-f]{6}$", "", k.strategy)
        groups[(base_name, category, k.regime_at_kill)].append(k)

    patterns: List[KillPattern] = []
    for (base, cat, regime), group in groups.items():
        count = len(group)
        avg_pnl = sum(k.cum_pnl for k in group) / count
        ticks = [k.tick for k in group]
        strategies = tuple(sorted(set(k.strategy for k in group)))

        # Severity based on count and PnL impact
        if count >= 4 or avg_pnl < -2.0:
            severity = "critical"
        elif count >= 2 or avg_pnl < -1.0:
            severity = "high"
        else:
            severity = "medium"

        # Check for repeated restart pattern (killed multiple times quickly)
        time_sorted = sorted(group, key=lambda k: k.tick)
        rapid_restarts = False
        if len(time_sorted) >= 2:
            tick_gaps = [
                time_sorted[i + 1].tick - time_sorted[i].tick
                for i in range(len(time_sorted) - 1)
            ]
            if any(gap < 100 for gap in tick_gaps):
                rapid_restarts = True
                cat = "repeated_restart"

        pattern_id = f"KP_{base}_{cat}_{regime}_{count}"
        description = _describe_pattern(base, cat, regime, count, avg_pnl, rapid_restarts)

        patterns.append(KillPattern(
            pattern_id=pattern_id,
            category=cat,
            description=description,
            severity=severity,
            affected_strategies=strategies,
            kill_count=count,
            avg_cum_pnl=round(avg_pnl, 4),
            regime_context=regime,
            tick_range=(min(ticks), max(ticks)),
        ))

    # Sort by severity then count
    severity_order = {"critical": 0, "high": 1, "medium": 2}
    patterns.sort(key=lambda p: (severity_order.get(p.severity, 9), -p.kill_count))
    return patterns


def _describe_pattern(base: str, category: str, regime: str,
                      count: int, avg_pnl: float, rapid_restart: bool) -> str:
    """Generate human-readable pattern description."""
    desc_parts = [f"Strategy family '{base}' killed {count}x"]
    if category == "pf_decay":
        desc_parts.append("due to profit factor decay below threshold")
    elif category == "mdd":
        desc_parts.append("due to maximum drawdown breach")
    elif category == "wr_collapse":
        desc_parts.append("due to win rate collapse below minimum")
    elif category == "repeated_restart":
        desc_parts.append("in a restart loop (killed and re-enabled too quickly)")
    else:
        desc_parts.append(f"for reason: {category}")

    desc_parts.append(f"in '{regime}' regime")
    desc_parts.append(f"(avg cumulative PnL: {avg_pnl:+.2f}%)")

    if rapid_restart:
        desc_parts.append(
            "-- WARNING: rapid restart pattern detected, "
            "strategy was re-enabled before conditions changed"
        )
    return ". ".join(desc_parts) + "."


def cross_reference_zp(pattern: KillPattern) -> List[Dict[str, str]]:
    """Match a kill pattern against ZP principles to identify violations.

    Returns list of {principle_tag, principle_name, explanation}.
    """
    refs: List[Dict[str, str]] = []

    for tag, info in ZP_PRINCIPLES.items():
        detect_type = info["detect"]
        explanation: Optional[str] = None

        if detect_type == "mdd" and pattern.category == "mdd":
            explanation = (
                f"Kill triggered by MDD breach. "
                f"'{info['rule']}' — this kill confirms the drawdown "
                f"exceeded survival threshold. Strategy was correctly killed "
                f"but lesson: tighten MDD params or add pre-MDD warning zone."
            )

        elif detect_type == "repeated_kill" and pattern.category == "repeated_restart":
            explanation = (
                f"Strategy killed {pattern.kill_count}x — the constraint "
                f"(kill condition) was correct, but the system kept re-enabling "
                f"the strategy without learning. '{info['rule']}' — "
                f"the negative list (kill condition) worked; the re-entry "
                f"decision ignored it."
            )

        elif detect_type == "repeated_kill" and pattern.kill_count >= 3:
            explanation = (
                f"Strategy killed {pattern.kill_count}x for same reason. "
                f"'{info['rule']}' — recurring kills indicate the constraint "
                f"is correct but the system keeps generating strategies that "
                f"violate it. Add this constraint to strategy_generator params."
            )

        elif detect_type == "exit_failure" and pattern.category == "pf_decay":
            explanation = (
                f"PF decay suggests exit timing is suboptimal. "
                f"'{info['rule']}' — standardize exits (trailing stop, "
                f"fixed stop, time-based exit) rather than optimizing entry "
                f"parameters."
            )

        elif detect_type == "regime_mismatch" and pattern.regime_context in ("mixed", "unknown"):
            explanation = (
                f"Kill occurred in '{pattern.regime_context}' regime. "
                f"'{info['rule']}' — strategy may not have regime-awareness "
                f"built into its logic. Consider adding regime as an explicit "
                f"input variable, not a background assumption."
            )

        elif detect_type == "daily_cap" and pattern.avg_cum_pnl < -2.0:
            explanation = (
                f"Cumulative PnL {pattern.avg_cum_pnl:+.2f}% across "
                f"{pattern.kill_count} kills threatens daily survival budget. "
                f"'{info['rule']}' — aggregate loss from this pattern family "
                f"approaches the $5 daily cap."
            )

        if explanation:
            refs.append({
                "principle_tag": tag,
                "principle_name": info["name"],
                "source": info["source"],
                "explanation": explanation,
            })

    return refs


def generate_lessons(patterns: List[KillPattern],
                     all_zp_refs: Dict[str, List[Dict[str, str]]]) -> List[Lesson]:
    """Generate actionable lessons from classified patterns + ZP cross-refs."""
    lessons: List[Lesson] = []
    now = datetime.now(_TAIPEI)
    expiry_30d = (now + timedelta(days=30)).strftime("%Y-%m-%d")
    expiry_90d = (now + timedelta(days=90)).strftime("%Y-%m-%d")

    for pattern in patterns:
        zp_tags = tuple(
            ref["principle_tag"]
            for ref in all_zp_refs.get(pattern.pattern_id, [])
        )

        if pattern.category == "pf_decay":
            lessons.append(Lesson(
                lesson_id=f"L_{pattern.pattern_id}_exit",
                pattern_id=pattern.pattern_id,
                action="tighten",
                description=(
                    f"PF decay in '{pattern.regime_context}' regime for "
                    f"{', '.join(pattern.affected_strategies)}. "
                    f"Tighten exit conditions: reduce trailing stop distance "
                    f"or add time-based exit. Do NOT re-optimize entry params."
                ),
                constraint_rule=json.dumps({
                    "type": "min_pf_guard",
                    "strategy_family": pattern.affected_strategies[0],
                    "regime": pattern.regime_context,
                    "action": "increase_min_pf_by_0.05",
                    "warn_pf": round(0.8 + 0.05 * min(pattern.kill_count, 4), 2),
                }),
                zp_principles=zp_tags,
                confidence="high" if pattern.kill_count >= 3 else "medium",
                expires=expiry_90d,
            ))

        elif pattern.category == "mdd":
            lessons.append(Lesson(
                lesson_id=f"L_{pattern.pattern_id}_mdd",
                pattern_id=pattern.pattern_id,
                action="tighten",
                description=(
                    f"MDD breach for {', '.join(pattern.affected_strategies)}. "
                    f"Reduce position size or add pre-MDD warning zone at 80% "
                    f"of kill threshold to trigger partial exit before full kill."
                ),
                constraint_rule=json.dumps({
                    "type": "mdd_pre_warning",
                    "strategy_family": pattern.affected_strategies[0],
                    "action": "add_warning_at_80pct_mdd",
                }),
                zp_principles=zp_tags,
                confidence="high",
                expires=expiry_90d,
            ))

        elif pattern.category == "wr_collapse":
            lessons.append(Lesson(
                lesson_id=f"L_{pattern.pattern_id}_wr",
                pattern_id=pattern.pattern_id,
                action="exclude_regime",
                description=(
                    f"Win rate collapsed in '{pattern.regime_context}' regime. "
                    f"Strategy family '{pattern.affected_strategies[0]}' may be "
                    f"structurally unfit for this regime. Consider adding regime "
                    f"filter to disable strategy during '{pattern.regime_context}'."
                ),
                constraint_rule=json.dumps({
                    "type": "regime_exclusion",
                    "strategy_family": pattern.affected_strategies[0],
                    "excluded_regime": pattern.regime_context,
                }),
                zp_principles=zp_tags,
                confidence="medium",
                expires=expiry_30d,
            ))

        elif pattern.category == "repeated_restart":
            lessons.append(Lesson(
                lesson_id=f"L_{pattern.pattern_id}_restart",
                pattern_id=pattern.pattern_id,
                action="avoid",
                description=(
                    f"Restart loop detected: {', '.join(pattern.affected_strategies)} "
                    f"killed {pattern.kill_count}x with rapid re-entry attempts. "
                    f"The kill condition is correct — the re-entry logic is wrong. "
                    f"Enforce minimum cooling period and require regime change "
                    f"before reactivation."
                ),
                constraint_rule=json.dumps({
                    "type": "cooling_period_increase",
                    "strategy_family": pattern.affected_strategies[0],
                    "min_cooling_ticks": max(100, 50 * pattern.kill_count),
                    "require_regime_change": True,
                }),
                zp_principles=zp_tags,
                confidence="high",
                expires=expiry_90d,
            ))

        else:
            lessons.append(Lesson(
                lesson_id=f"L_{pattern.pattern_id}_generic",
                pattern_id=pattern.pattern_id,
                action="monitor",
                description=(
                    f"Unclassified kill pattern for "
                    f"{', '.join(pattern.affected_strategies)} "
                    f"in '{pattern.regime_context}' regime. "
                    f"Monitor for recurrence before taking action."
                ),
                constraint_rule=json.dumps({
                    "type": "monitor",
                    "strategy_family": pattern.affected_strategies[0],
                }),
                zp_principles=zp_tags,
                confidence="low",
                expires=expiry_30d,
            ))

    return lessons


def build_strategy_summary(kills: Sequence[KillRecord]) -> Dict[str, Dict]:
    """Build per-strategy kill summary statistics."""
    summary: Dict[str, Dict] = {}
    for k in kills:
        base = re.sub(r"_[0-9a-f]{6}$", "", k.strategy)
        if base not in summary:
            summary[base] = {
                "kill_count": 0,
                "total_cum_pnl": 0.0,
                "strategies": set(),
                "regimes": Counter(),
                "reasons": Counter(),
                "first_kill_tick": k.tick,
                "last_kill_tick": k.tick,
            }
        s = summary[base]
        s["kill_count"] += 1
        s["total_cum_pnl"] += k.cum_pnl
        s["strategies"].add(k.strategy)
        s["regimes"][k.regime_at_kill] += 1
        cat, _, _ = parse_kill_reason(k.kill_reason)
        s["reasons"][cat] += 1
        s["first_kill_tick"] = min(s["first_kill_tick"], k.tick)
        s["last_kill_tick"] = max(s["last_kill_tick"], k.tick)

    # Convert sets and Counters for serialization
    for base, s in summary.items():
        s["strategies"] = sorted(s["strategies"])
        s["regimes"] = dict(s["regimes"])
        s["reasons"] = dict(s["reasons"])
        s["avg_cum_pnl"] = round(s["total_cum_pnl"] / s["kill_count"], 4)

    return summary


def analyze_kills(kills: Sequence[KillRecord]) -> KillAnalysis:
    """Full analysis pipeline: classify -> cross-reference -> generate lessons."""
    now = datetime.now(_TAIPEI).isoformat()

    patterns = classify_kills(kills)

    all_zp_refs: Dict[str, List[Dict[str, str]]] = {}
    flat_zp_refs: List[Dict[str, str]] = []
    for p in patterns:
        refs = cross_reference_zp(p)
        all_zp_refs[p.pattern_id] = refs
        flat_zp_refs.extend(refs)

    lessons = generate_lessons(patterns, all_zp_refs)
    strategy_summary = build_strategy_summary(kills)

    return KillAnalysis(
        generated_at=now,
        kill_count=len(kills),
        patterns=patterns,
        lessons=lessons,
        zp_cross_refs=flat_zp_refs,
        strategy_summary=strategy_summary,
    )


# --- Output Formatters ---

def to_jsonl(analysis: KillAnalysis) -> str:
    """Serialize analysis to JSONL for machine consumption.

    One line per record: header, then patterns, then lessons, then cross-refs.
    """
    lines: List[str] = []

    # Header
    lines.append(json.dumps({
        "type": "header",
        "generated_at": analysis.generated_at,
        "kill_count": analysis.kill_count,
        "pattern_count": len(analysis.patterns),
        "lesson_count": len(analysis.lessons),
    }, ensure_ascii=False))

    # Patterns
    for p in analysis.patterns:
        lines.append(json.dumps({
            "type": "pattern",
            **{k: v if not isinstance(v, tuple) else list(v)
               for k, v in asdict(p).items()},
        }, ensure_ascii=False))

    # Lessons
    for lesson in analysis.lessons:
        lines.append(json.dumps({
            "type": "lesson",
            **{k: v if not isinstance(v, tuple) else list(v)
               for k, v in asdict(lesson).items()},
        }, ensure_ascii=False))

    # ZP cross-references
    for ref in analysis.zp_cross_refs:
        lines.append(json.dumps({
            "type": "zp_cross_ref",
            **ref,
        }, ensure_ascii=False))

    # Strategy summary
    for name, stats in analysis.strategy_summary.items():
        lines.append(json.dumps({
            "type": "strategy_summary",
            "strategy_family": name,
            **stats,
        }, ensure_ascii=False))

    return "\n".join(lines) + "\n"


def to_markdown(analysis: KillAnalysis) -> str:
    """Generate human-readable markdown summary."""
    now_str = analysis.generated_at
    lines: List[str] = [
        f"# Kill-Lesson Analysis Report",
        f"",
        f"**Generated**: {now_str}",
        f"**Kills analyzed**: {analysis.kill_count}",
        f"**Patterns found**: {len(analysis.patterns)}",
        f"**Lessons extracted**: {len(analysis.lessons)}",
        f"",
    ]

    # Patterns
    if analysis.patterns:
        lines.extend([
            "## Kill Patterns",
            "",
            "| Severity | Category | Strategy Family | Kills | Avg PnL | Regime |",
            "|----------|----------|-----------------|-------|---------|--------|",
        ])
        for p in analysis.patterns:
            strategies_str = ", ".join(p.affected_strategies[:3])
            if len(p.affected_strategies) > 3:
                strategies_str += f" (+{len(p.affected_strategies) - 3})"
            lines.append(
                f"| {p.severity.upper()} | {p.category} | {strategies_str} "
                f"| {p.kill_count} | {p.avg_cum_pnl:+.2f}% | {p.regime_context} |"
            )
        lines.append("")

        for p in analysis.patterns:
            lines.extend([
                f"### {p.pattern_id}",
                f"",
                f"{p.description}",
                f"",
                f"- Tick range: {p.tick_range[0]} - {p.tick_range[1]}",
                f"- Strategies: {', '.join(p.affected_strategies)}",
                f"",
            ])

    # Lessons
    if analysis.lessons:
        lines.extend(["## Actionable Lessons", ""])
        for i, lesson in enumerate(analysis.lessons, 1):
            zp_str = ", ".join(lesson.zp_principles) if lesson.zp_principles else "none"
            lines.extend([
                f"### Lesson {i}: [{lesson.action.upper()}] {lesson.lesson_id}",
                f"",
                f"{lesson.description}",
                f"",
                f"- **Confidence**: {lesson.confidence}",
                f"- **ZP principles**: {zp_str}",
                f"- **Re-evaluate by**: {lesson.expires or 'N/A'}",
                f"- **Constraint**: `{lesson.constraint_rule}`",
                f"",
            ])

    # ZP cross-references
    if analysis.zp_cross_refs:
        lines.extend(["## ZP Principle Cross-References", ""])
        seen: set = set()
        for ref in analysis.zp_cross_refs:
            tag = ref["principle_tag"]
            if tag in seen:
                continue
            seen.add(tag)
            lines.extend([
                f"### {ref['principle_name']}",
                f"",
                f"**Source**: `{ref['source']}`",
                f"",
                f"{ref['explanation']}",
                f"",
            ])

    # Strategy summary
    if analysis.strategy_summary:
        lines.extend([
            "## Strategy Family Summary",
            "",
            "| Family | Kills | Avg PnL | Primary Reason | Primary Regime |",
            "|--------|-------|---------|----------------|----------------|",
        ])
        for name, stats in sorted(
            analysis.strategy_summary.items(),
            key=lambda x: -x[1]["kill_count"],
        ):
            primary_reason = max(stats["reasons"], key=stats["reasons"].get) if stats["reasons"] else "?"
            primary_regime = max(stats["regimes"], key=stats["regimes"].get) if stats["regimes"] else "?"
            lines.append(
                f"| {name} | {stats['kill_count']} "
                f"| {stats['avg_cum_pnl']:+.2f}% | {primary_reason} | {primary_regime} |"
            )
        lines.append("")

    lines.append("---")
    lines.append(f"*Generated by trading.kill_lesson — virtuous cycle component*")
    lines.append("")
    return "\n".join(lines)


# --- Main Entry Point ---

def run_analysis(
    last_n: Optional[int] = None,
    strategy_filter: Optional[str] = None,
    dry_run: bool = False,
    force: bool = False,
) -> KillAnalysis:
    """Run the kill-lesson analysis pipeline.

    Args:
        last_n: Only analyze the last N kills (None = all unprocessed).
        strategy_filter: Only analyze kills for this strategy name/prefix.
        dry_run: Print output but don't write files.
        force: Reanalyze already-processed kills.

    Returns:
        KillAnalysis object with all results.
    """
    all_kills = load_kills()
    if not all_kills:
        logger.warning("No kill records found in %s", KILLS_LOG)
        return KillAnalysis(
            generated_at=datetime.now(_TAIPEI).isoformat(),
            kill_count=0,
        )

    # Filter
    processed = set() if force else load_processed_set()
    kills = [k for k in all_kills if k.ts not in processed]

    if strategy_filter:
        kills = [k for k in kills if strategy_filter in k.strategy]

    if last_n is not None:
        kills = kills[-last_n:]

    if not kills:
        logger.info("No new kills to analyze (all %d already processed)", len(all_kills))
        return KillAnalysis(
            generated_at=datetime.now(_TAIPEI).isoformat(),
            kill_count=0,
        )

    logger.info("Analyzing %d kill records", len(kills))
    analysis = analyze_kills(kills)

    if dry_run:
        print(to_markdown(analysis))
        return analysis

    # Write outputs
    LESSONS_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(_TAIPEI).strftime("%Y-%m-%d_%H%M")

    jsonl_path = LESSONS_DIR / f"{date_str}_kill_analysis.jsonl"
    jsonl_path.write_text(to_jsonl(analysis), encoding="utf-8")
    logger.info("JSONL output: %s", jsonl_path)

    md_path = LESSONS_DIR / f"{date_str}_kill_analysis.md"
    md_path.write_text(to_markdown(analysis), encoding="utf-8")
    logger.info("Markdown output: %s", md_path)

    # Mark kills as processed
    new_processed = processed | {k.ts for k in kills}
    save_processed_set(new_processed)

    return analysis


def main() -> int:
    """CLI entry point."""
    import argparse
    parser = argparse.ArgumentParser(
        description="Kill-Lesson Extraction System — analyze losing trades",
    )
    parser.add_argument("--last", type=int, default=None,
                        help="Analyze only the last N kills")
    parser.add_argument("--strategy", type=str, default=None,
                        help="Filter by strategy name/prefix")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print analysis without writing files")
    parser.add_argument("--force", action="store_true",
                        help="Reanalyze already-processed kills")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    analysis = run_analysis(
        last_n=args.last,
        strategy_filter=args.strategy,
        dry_run=args.dry_run,
        force=args.force,
    )

    if analysis.kill_count == 0:
        print("No kills to analyze.")
        return 0

    print(f"\nAnalysis complete: {len(analysis.patterns)} patterns, "
          f"{len(analysis.lessons)} lessons extracted from "
          f"{analysis.kill_count} kills.")

    if not args.dry_run:
        print(f"Output written to {LESSONS_DIR}/")

    return 0


if __name__ == "__main__":
    sys.exit(main())
