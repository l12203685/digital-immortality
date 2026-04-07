#!/usr/bin/env python3
"""
Digital Organism Interaction — MVP
===================================

Compares two digital organisms (DNA markdown files) across 10 decision scenarios.
Extracts principles from each DNA file, generates structured decision comparisons,
and saves results as JSON in the results/ directory.

Usage:
    python organism_interact.py <dna_file_a> <dna_file_b> [--scenario N] [--all]
    python organism_interact.py <dna_file_a> <dna_file_b> --report

Examples:
    python organism_interact.py templates/example_dna.md path/to/other_dna.md --all
    python organism_interact.py dna_a.md dna_b.md --scenario 3
    python organism_interact.py dna_a.md dna_b.md           # runs all 10
    python organism_interact.py dna_a.md dna_b.md --report   # structured collision report

Output:
    results/<organism_a>_vs_<organism_b>_<timestamp>.json
    results/collision_<name1>_vs_<name2>_<timestamp>.md   (with --report)
    results/collision_<name1>_vs_<name2>_<timestamp>.json  (with --report)

Protocol format follows specs/organism_protocol.md v0.1
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Scenario bank — 10 decision-comparison scenarios across key life domains
# ---------------------------------------------------------------------------

SCENARIOS = [
    {
        "id": 1,
        "domain": "career",
        "scenario": (
            "You are offered a role that pays 1.8x your current salary at a "
            "fast-growing startup. The role requires leaving a stable, reputable "
            "employer. The startup has 18 months of runway. Do you take it?"
        ),
    },
    {
        "id": 2,
        "domain": "relationships",
        "scenario": (
            "A close friend asks you to co-sign a personal loan of significant size. "
            "They have a track record of poor financial discipline but are genuinely "
            "in need. Do you co-sign?"
        ),
    },
    {
        "id": 3,
        "domain": "money",
        "scenario": (
            "You receive an unexpected windfall equal to 2 years of your salary. "
            "You can: (A) invest it conservatively in index funds, "
            "(B) allocate it to a concentrated high-conviction bet, "
            "or (C) use it to buy more time — reduce working hours or take a sabbatical. "
            "What do you do and why?"
        ),
    },
    {
        "id": 4,
        "domain": "risk",
        "scenario": (
            "An opportunity with a 30% chance of 10x return and 70% chance of total "
            "loss presents itself. The stake is 20% of your net worth. "
            "Do you take the bet?"
        ),
    },
    {
        "id": 5,
        "domain": "learning",
        "scenario": (
            "You can spend the next 6 months learning a skill that is highly valuable "
            "NOW but may be automated in 3-5 years, OR learning a harder foundational "
            "skill that compounds over a decade but pays nothing immediately. "
            "Which do you choose?"
        ),
    },
    {
        "id": 6,
        "domain": "health",
        "scenario": (
            "Optimizing your physical health would require 10 hours per week of "
            "dedicated effort (sleep discipline, exercise, diet). "
            "This directly competes with time you currently use for deep work and income generation. "
            "How do you allocate?"
        ),
    },
    {
        "id": 7,
        "domain": "time",
        "scenario": (
            "You have a free, unscheduled weekend with zero obligations. "
            "No one expects anything from you. "
            "What do you do, and what does that reveal about your actual priorities?"
        ),
    },
    {
        "id": 8,
        "domain": "conflict",
        "scenario": (
            "A colleague takes credit for your work in front of senior leadership. "
            "It was likely deliberate. You have evidence. "
            "Do you confront them directly, escalate to management, let it go, "
            "or play a longer game? Walk through your reasoning."
        ),
    },
    {
        "id": 9,
        "domain": "opportunity",
        "scenario": (
            "A contact offers you early access to a deal/opportunity that requires "
            "a decision within 48 hours. Due diligence would normally take 2 weeks. "
            "The opportunity looks strong but you cannot fully verify it in time. "
            "Do you act or pass?"
        ),
    },
    {
        "id": 10,
        "domain": "legacy",
        "scenario": (
            "You have 10 years left to work at full capacity. "
            "You can optimize for: (A) maximum wealth accumulation, "
            "(B) building something that outlasts you, "
            "(C) depth of relationships and personal experiences. "
            "These are mutually exclusive at the margin. What is your allocation and why?"
        ),
    },
]


# ---------------------------------------------------------------------------
# DNA parsing
# ---------------------------------------------------------------------------

def parse_dna(filepath: str) -> dict:
    """
    Extract organism name and key principles from a markdown DNA file.

    Parsing strategy:
    - Name: first H1 heading or filename stem
    - Principles: all bullet/numbered list items under headers containing
      keywords: principle, core, value, decision, framework, rule, belief
    - Section headers collected for context
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"DNA file not found: {filepath}")

    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    name = _extract_name(lines, path.stem)
    sections = _extract_sections(lines)
    principles = _extract_principles(lines, sections)
    identity = _extract_identity_table(text)

    return {
        "name": name,
        "filepath": str(path.resolve()),
        "principles": principles,
        "sections": list(sections.keys()),
        "identity": identity,
        "raw_line_count": len(lines),
    }


def _extract_name(lines: list, fallback: str) -> str:
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# ") and len(stripped) > 2:
            candidate = stripped[2:].strip()
            # Strip common suffixes like "DNA", "v18", "Blueprint"
            candidate = re.sub(r"\s+(DNA|Blueprint|v\d+[\.\d]*).*$", "", candidate, flags=re.IGNORECASE)
            if candidate:
                return candidate
    return fallback


def _extract_sections(lines: list) -> dict:
    """Return ordered dict of {section_heading: [line_indices]}"""
    sections = {}
    current = None
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,4})\s+(.+)", line)
        if m:
            current = m.group(2).strip()
            sections[current] = []
        elif current is not None:
            sections[current].append(i)
    return sections


PRINCIPLE_SECTION_KEYWORDS = re.compile(
    r"(principle|core|value|decision|framework|rule|belief|philosophy|kernel|"
    r"manifesto|constitution|law|axiom|heuristic|guideline|基本|原則|核心|價值|決策)",
    re.IGNORECASE,
)

# High-priority: sections about actual decision-making, not agent operations
PRIORITY_SECTION_KEYWORDS = re.compile(
    r"(kernel|決策|跨域|decision.*(core|kernel)|公設|axiom|heuristic|thinking|思維)",
    re.IGNORECASE,
)

# Lines that look like decision principles (positive signal)
DECISION_PRINCIPLE_SIGNAL = re.compile(
    r"(EV|expected value|導數|derivative|meta.?strategy|population|inaction|"
    r"不對稱|asymmetr|first.?principle|第一原理|二階|second.?order|"
    r"management.?paradox|bias|edge|compound|複利|risk|風險|"
    r"invest|capital|equity|freedom|自由|FIRE|trade|交易|strategy|策略|"
    r"probability|機率|bet|position.?siz|kelly|sharpe|MDD|drawdown|"
    r"information|資訊|signal|噪音|noise|regime|trend|momentum|reversion)",
    re.IGNORECASE,
)

# Lines that look like agent operating instructions (negative signal)
AGENT_INSTRUCTION_SIGNAL = re.compile(
    r"(代理人|agent|session|Claude|boot|compact|context|sub.?agent|"
    r"Discord|GDrive|staging|commit|push|git|cron|trigger|"
    r"window\s?\d|token|確認.*要做嗎|emoji|修辭|alignment.?theater|"
    r"你就是我|你代表我|退回確認|冷啟動|校準|checkpoint|dashboard|"
    r"readback|predicate|assertion|patch.?classif|BLOCKER.*POLICY|"
    r"meta.?work|taxonomy|indexing|pipeline.?tooling|E2.?as.?gate|"
    r"structural.?clarity|artifact|proposals?.*draft|batch.*(操作|驗證)|"
    r"observation.*action.*轉換|round.?trip|"
    r"足夠上下文|執行後報告|直接用.*邏輯|邏輯執行後|"
    r"不是助理|不是代表|output feed back|KPI.*行動|"
    r"報結果不報|想透再推進|做完報結果|下一步做什麼|"
    r"先推再問|idle.*衍生|零.*revenue|parasitic|"
    r"批次操作後驗證|安全清掃|無誤傷|大量刪除|批次搬移)",
    re.IGNORECASE,
)


def _score_principle_priority(text: str) -> int:
    """Score how much a line looks like a decision principle vs agent instruction."""
    score = 0
    if DECISION_PRINCIPLE_SIGNAL.search(text):
        score += 2
    if AGENT_INSTRUCTION_SIGNAL.search(text):
        score -= 3
    # Bonus for universal/abstract principles with cross-domain markers
    if any(w in text for w in ["不看", "管理", "決定", "exploit", "toward", "跨域", "/"]):
        score += 1
    return score


# Pattern: "N. **Bold Title** — cross-domain explanation" (Decision Kernel format)
DECISION_KERNEL_RE = re.compile(r"^\d+[\.\)]\s+\*\*(.+?)\*\*\s*[—–-]\s*(.+)")

# Pattern: markdown table data row "| col1 | col2 | col3 |"
TABLE_ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|?")


def _extract_table_principles(lines: list, sections: dict) -> list:
    """
    Extract principles from markdown tables under principle-relevant sections.
    Row format: | id | principle | explanation |  → "principle — explanation"
    Skips separator rows (---|---) and header rows.
    """
    # Identify line ranges under principle-relevant sections
    relevant_lines: set[int] = set()
    for heading, indices in sections.items():
        if PRINCIPLE_SECTION_KEYWORDS.search(heading):
            relevant_lines.update(indices)

    result = []
    seen: set[str] = set()
    for i in sorted(relevant_lines):
        line = lines[i].strip()
        if not line.startswith("|"):
            continue
        # Skip separator rows
        if re.match(r"^\|[\s\-|]+\|$", line):
            continue
        m = TABLE_ROW_RE.match(line)
        if not m:
            continue
        # Three-column row: col1=index/id, col2=principle, col3=explanation
        col1, col2, col3 = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
        # Skip header rows (col values are column names)
        if col2.lower() in ("#", "公理", "principle", "field", "item", "name", "---"):
            continue
        principle = f"{col2} — {col3}" if col3 else col2
        # Strip markdown
        principle = re.sub(r"\*\*(.+?)\*\*", r"\1", principle)
        if len(principle) > 8 and principle not in seen:
            if not AGENT_INSTRUCTION_SIGNAL.search(principle):
                seen.add(principle)
                result.append(principle)
    return result


def _extract_decision_kernel(lines: list) -> list:
    """
    Extract high-priority decision kernel items. These follow the format:
    N. **Principle Name** — cross-domain explanation with / separators
    Filters out agent operating instructions by content analysis.
    """
    kernel = []
    for line in lines:
        stripped = line.strip()
        m = DECISION_KERNEL_RE.match(stripped)
        if m:
            title = m.group(1).strip()
            detail = m.group(2).strip()
            combined = f"{title} — {detail}"
            # Skip agent operating instructions
            if AGENT_INSTRUCTION_SIGNAL.search(combined):
                continue
            kernel.append(combined)
    return kernel


def _extract_principles(lines: list, sections: dict) -> list:
    """
    Collect principles in priority order:
    1. Decision Kernel items (N. **Bold** — detail format) — always first
    2. Bold standalone principles (**Title** — detail)
    3. Items from principle-relevant sections, scored by decision vs agent signal
    Deduplicated, stripped, max 30 items.
    """
    seen = set()
    result = []

    # Tier 0: Markdown table rows under principle sections (e.g. 5 Axioms table)
    for p in _extract_table_principles(lines, sections):
        if p not in seen:
            seen.add(p)
            result.append(p)

    # Tier 1: Decision Kernel (highest priority)
    for p in _extract_decision_kernel(lines):
        if p not in seen:
            seen.add(p)
            result.append(p)

    # Tier 2: Bold standalone principle lines (** — **)
    for line in lines:
        stripped = line.strip()
        m = BOLD_LINE_RE.match(stripped)
        if m:
            label = m.group(1).strip()
            detail = m.group(2).strip()
            combined = f"{label} — {detail}" if detail else label
            if len(combined) > 10 and combined not in seen:
                # Skip if looks like agent instruction
                if not AGENT_INSTRUCTION_SIGNAL.search(combined):
                    seen.add(combined)
                    result.append(combined)

    # Tier 3: Bullet/numbered items from principle sections, priority-scored
    general_indices = set()
    for heading, indices in sections.items():
        if PRINCIPLE_SECTION_KEYWORDS.search(heading):
            general_indices.update(indices)

    if not general_indices and not result:
        general_indices = set(range(len(lines)))

    candidates = []
    for i in sorted(general_indices):
        line = lines[i].strip()
        extracted = _line_to_principle(line)
        if extracted and extracted not in seen:
            seen.add(extracted)
            priority = _score_principle_priority(extracted)
            candidates.append((priority, extracted))

    # Filter out likely agent instructions (negative score) and sort by priority
    candidates = [(s, t) for s, t in candidates if s >= 0]
    candidates.sort(key=lambda x: x[0], reverse=True)
    result.extend(text for _, text in candidates)

    return result[:30]


BULLET_RE = re.compile(r"^[-*+•]\s+(.+)")
NUMBERED_RE = re.compile(r"^\d+[\.\)]\s+(.+)")
BOLD_LINE_RE = re.compile(r"^\*\*(.+?)\*\*\s*[—–-]?\s*(.*)")


def _line_to_principle(line: str) -> str | None:
    for pattern in (BULLET_RE, NUMBERED_RE):
        m = pattern.match(line)
        if m:
            content = m.group(1).strip()
            # Strip inline markdown bold/italic
            content = re.sub(r"\*\*(.+?)\*\*", r"\1", content)
            content = re.sub(r"\*(.+?)\*", r"\1", content)
            if len(content) > 10:
                return content
    # Bold standalone principle lines
    m = BOLD_LINE_RE.match(line)
    if m:
        label = m.group(1).strip()
        detail = m.group(2).strip()
        combined = f"{label} — {detail}" if detail else label
        if len(combined) > 10:
            return combined
    return None


def _extract_identity_table(text: str) -> dict:
    """Parse markdown table rows from Identity section into a flat dict."""
    identity = {}
    in_identity = False
    for line in text.splitlines():
        if re.match(r"^#{1,3}\s+.*[Ii]dentity", line):
            in_identity = True
            continue
        if in_identity:
            if line.startswith("#"):
                break
            m = re.match(r"\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", line)
            if m:
                key = m.group(1).strip().lower()
                val = m.group(2).strip()
                if key not in ("field", "---", "item") and val not in ("value", "detail", "---"):
                    identity[key] = val
    return identity


# ---------------------------------------------------------------------------
# Decision generation (heuristic, no LLM)
# ---------------------------------------------------------------------------

DOMAIN_PRINCIPLE_AFFINITY = {
    "career":           ["career", "job", "work", "growth", "stability", "salary", "opportunity", "compound"],
    "relationships":    ["relationship", "trust", "friend", "social", "obligation", "commitment", "人際", "信任"],
    "money":            ["money", "invest", "wealth", "asset", "return", "capital", "financial", "資產", "財務"],
    "risk":             ["risk", "edge", "EV", "expected value", "bet", "probability", "loss", "upside"],
    "risk_assessment":  ["risk", "edge", "EV", "expected value", "bet", "probability", "backtest", "overfit"],
    "learning":         ["learn", "skill", "knowledge", "compound", "foundation", "growth", "study"],
    "health":           ["health", "energy", "sleep", "exercise", "body", "physical", "time"],
    "time":             ["time", "priorit", "allocat", "focus", "freedom", "leisure", "schedule"],
    "conflict":         ["conflict", "confrontation", "direct", "escalat", "politics", "boundary"],
    "opportunity":      ["opportunit", "decision", "act", "pass", "verify", "rush", "FOMO", "edge"],
    "opportunity_cost": ["opportunit", "decision", "pass", "edge", "conviction", "irreversible", "cost"],
    "legacy":           ["legacy", "impact", "build", "lasting", "meaning", "wealth", "relationship"],
    "trading":          ["trading", "trade", "strategy", "return", "time", "edge", "risk", "maintenance"],
    "finance":          ["finance", "financial", "invest", "money", "wealth", "allocat", "capital", "income"],
    "identity":         ["identity", "action", "specific", "commit", "responsib", "person", "first"],
    "meta_strategy":    ["meta", "system", "process", "metric", "deteriorat", "regime", "diagnos", "pause"],
}


def _score_principle_for_domain(principle: str, domain: str) -> int:
    keywords = DOMAIN_PRINCIPLE_AFFINITY.get(domain, [])
    p_lower = principle.lower()
    return sum(1 for kw in keywords if kw.lower() in p_lower)


def generate_response(organism: dict, scenario: dict) -> dict:
    """
    Heuristic decision engine:
    1. Score all principles against the scenario domain
    2. Pick top 3 relevant principles (fall back to first 3 if none score)
    3. Build a templated response that cites those principles
    """
    principles = organism["principles"]
    domain = scenario["domain"]

    if not principles:
        used = []
        response = (
            f"No extractable principles found in DNA. "
            f"Cannot generate a decision for the '{domain}' scenario."
        )
        return {"response": response, "dna_principles_used": used}

    scored = sorted(
        [(i, p, _score_principle_for_domain(p, domain)) for i, p in enumerate(principles)],
        key=lambda x: x[2],
        reverse=True,
    )

    # Top 3 relevant; if top score is 0, fall back to positional order
    top = scored[:3]
    if top[0][2] == 0:  # all scored 0, use first 3 positionally
        top = [(i, p, 0) for i, p in enumerate(principles[:3])]

    used = [p for _, p, _ in top]

    response = _build_response(organism["name"], scenario, used)
    return {"response": response, "dna_principles_used": used}


def _build_response(name: str, scenario: dict, principles: list) -> str:
    """
    Construct a plausible decision response by surface-reading the scenario
    and applying the organism's principles as explicit reasoning steps.
    """
    domain = scenario["domain"]

    framing = {
        "career":        "On career decisions",
        "relationships": "On relationship commitments",
        "money":         "On capital allocation",
        "risk":          "On risk-taking",
        "learning":      "On learning investments",
        "health":        "On health vs. productivity trade-offs",
        "time":          "On time allocation",
        "conflict":      "On conflict resolution",
        "opportunity":   "On time-compressed opportunities",
        "legacy":        "On legacy and long-term orientation",
    }.get(domain, f"On {domain}")

    lines = [f"{framing}, {name}'s decision framework yields:"]
    lines.append("")

    for i, p in enumerate(principles, 1):
        # Truncate very long principles for readability
        p_display = p if len(p) <= 120 else p[:117] + "..."
        lines.append(f"  [{i}] Applying: \"{p_display}\"")

    lines.append("")

    # Domain-specific decision logic stubs — each uses principle text as signal
    all_text = " ".join(principles).lower()
    decision_text = _domain_decision(domain, all_text)
    lines.append(decision_text)

    return "\n".join(lines)


def _domain_decision(domain: str, principle_text: str) -> str:
    """Map domain + principle signals to a concrete decision stance."""
    stability_signal = any(w in principle_text for w in ["stable", "stability", "hedge", "safe", "conservative"])
    growth_signal    = any(w in principle_text for w in ["growth", "compound", "upside", "opportunit", "aggressive"])
    ev_signal        = any(w in principle_text for w in ["ev", "expected value", "probability", "edge"])
    inaction_signal  = any(w in principle_text for w in ["inaction", "wait", "patience", "no edge", "pass"])
    direct_signal    = any(w in principle_text for w in ["direct", "confront", "honest", "transparent"])
    system_signal    = any(w in principle_text for w in ["system", "process", "framework", "structure"])
    meta_signal      = any(w in principle_text for w in ["meta", "long-term", "second order", "derivative"])

    decisions = {
        "career": (
            "DEPENDS_ON_CORE_GOAL — stability hedge outweighs marginal income gain; pass unless promotion aligns with long-term goal."
            if stability_signal else
            "DEPENDS_ON_CORE_GOAL — growth optionality matters, but weigh salary against loss of time for core skills and whether it serves your primary objective."
            if growth_signal else
            "DEPENDS_ON_CORE_GOAL — evaluate whether this promotion advances or diverts from your core goal before deciding."
        ),
        "relationships": (
            "SET_BOUNDARY — stop lending and address the escalating pattern directly; the trend signals a boundary violation regardless of repayment history."
            if (stability_signal or inaction_signal) else
            "SET_BOUNDARY — cap lending at a fixed limit and have a direct conversation about the escalating pattern; protect the relationship by enforcing limits early."
        ),
        "money": (
            "CONCENTRATED BET — windfall capital is highest-risk-tolerance tranche; deploy in high-conviction position."
            if (growth_signal or ev_signal) else
            "INDEX + OPTIONALITY — 70% conservative base, 30% time-buying (sabbatical or skill-building)."
            if stability_signal else
            "FRAMEWORK FIRST — run expected-value calc across all three options before allocating."
        ),
        "risk": (
            "TAKE — EV = +0.3*9x + 0.7*(-1x) = +2.0; positive EV at 20% position size is within Kelly range."
            if ev_signal else
            "PASS — 70% ruin probability on 20% net worth violates position-sizing discipline regardless of upside."
            if (stability_signal or inaction_signal) else
            "SIZE DOWN — reduce stake to Kelly-optimal fraction, then take the bet."
        ),
        "learning": (
            "FOUNDATION — short-term skills are depreciating assets; foundational skills are the meta-investment."
            if (meta_signal or growth_signal) else
            "IMMEDIATE VALUE — capture the arbitrage window now; foundational learning can be parallelized."
            if stability_signal else
            "PARALLEL — 70% foundational, 30% immediate; avoid binary framing."
        ),
        "health": (
            "SYSTEM BUILD — health is infrastructure, not discretionary; 10h/week is non-negotiable baseline."
            if system_signal else
            "OPTIMIZE OVERLAP — combine health and productive time (walking calls, standing desk, sleep priority)."
        ),
        "time": (
            "META-WORK — free time defaults to system review, reading, and strategic thinking; leisure is residual."
            if (meta_signal or system_signal) else
            "RECHARGE — genuine disconnection to restore cognitive baseline; productivity follows recovery."
            if stability_signal else
            "OPTIONALITY — protect free time as unstructured; resist filling it with output-optimizing activities."
        ),
        "conflict": (
            "DIRECT CONFRONTATION — address the behavior privately, factually, with evidence; no escalation first."
            if direct_signal else
            "DOCUMENTED ESCALATION — create paper trail, escalate through proper channels; avoid personal confrontation."
            if system_signal else
            "LONG GAME — let the pattern establish itself; address systemically when the second instance occurs."
        ),
        "opportunity": (
            "PASS — 48h diligence is insufficient; forced urgency is a red flag that shifts EV negative."
            if (inaction_signal or ev_signal) else
            "SMALL POSITION — take minimum viable exposure to maintain optionality without full commitment."
            if growth_signal else
            "FRAMEWORK CHECK — assess whether incomplete diligence is the actual risk, or whether intuition is sufficient."
        ),
        "legacy": (
            "WEALTH FIRST — financial independence is infrastructure for everything else; sequence matters."
            if stability_signal else
            "BUILD SOMETHING — asymmetric legacy impact outweighs marginal wealth beyond sufficiency threshold."
            if (growth_signal or meta_signal) else
            "INTEGRATED — compound wealth to sufficiency, then redirect to building; relationships are the through-line."
        ),
        "trading": (
            "EVALUATE_TIME_VS_RETURN — 2hr/day = 730hr/year; without independent audit, claimed returns are unverified. Pass unless time-adjusted EV clearly exceeds alternative uses."
            if (ev_signal or inaction_signal) else
            "EVALUATE_TIME_VS_RETURN — assess whether claimed returns compensate for opportunity cost, attention drain, and lack of verification before committing time."
        ),
        "finance": (
            "APPLY_FINANCIAL_PRINCIPLES — deploy windfall according to core financial principles: concentrated high-conviction position if edge exists, buy time if freedom is the priority, index if preserving optionality."
            if (ev_signal or growth_signal or stability_signal) else
            "APPLY_FINANCIAL_PRINCIPLES — run your financial decision framework across all three options; the right allocation depends entirely on your stated priorities and risk tolerance."
        ),
        "identity": (
            "SPECIFIC_ACTION — the first action is the most urgent commitment: contact key people, fulfill time-sensitive responsibilities, maintain critical systems."
            if direct_signal else
            "SPECIFIC_ACTION — identify the highest-priority concrete action from daily patterns and commitments, name the person involved and timeframe."
        ),
        "opportunity_cost": (
            "PASS_UNLESS_CLEAR_EDGE — startup equity is illiquid and high-variance; without genuine edge in assessing success probability, the opportunity cost of 2 years off current path is too high."
            if (inaction_signal or ev_signal) else
            "PASS_UNLESS_CLEAR_EDGE — compare EV of both paths; require high conviction threshold for irreversible 2-year commitment that delays primary goal."
        ),
        "meta_strategy": (
            "PAUSE_AND_DIAGNOSE — 3x deterioration in key metric signals regime change; pause the system, diagnose root cause before resuming. Rate of change matters more than absolute level."
            if (system_signal or meta_signal) else
            "PAUSE_AND_DIAGNOSE — accelerating deterioration requires halting operations to diagnose whether the environment has changed or the strategy is broken."
        ),
        "risk_assessment": (
            "REJECT — 40% walk-forward pass rate indicates overfitting, not edge. Do not deploy regardless of backtest Sharpe."
            if (ev_signal or inaction_signal) else
            "REJECT — walk-forward validation overrides single-backtest performance; insufficient evidence of genuine edge."
        ),
    }
    return decisions.get(domain, "Decision: apply core principles to the specific trade-offs in this scenario.")


# ---------------------------------------------------------------------------
# Synthesis
# ---------------------------------------------------------------------------

def synthesize(organism_a: dict, organism_b: dict, resp_a: dict, resp_b: dict, scenario: dict) -> str:
    """
    Compare two responses and articulate what the difference reveals
    about each organism's underlying value structure.
    """
    principles_a = set(resp_a["dna_principles_used"])
    principles_b = set(resp_b["dna_principles_used"])

    overlap = principles_a & principles_b
    unique_a = principles_a - principles_b
    unique_b = principles_b - principles_a

    # Extract the decision verdict (uppercase word/phrase before " — " at end of response)
    import re as _re

    def _extract_verdict(text: str) -> str:
        """Return the final decision word (e.g. TAKE, PASS, CONDITIONAL) or empty string."""
        match = _re.search(r'\n([A-Z][A-Z\s]{1,30}?) —', text)
        if match:
            return match.group(1).strip()
        # fallback: last ALL-CAPS token
        tokens = _re.findall(r'\b[A-Z]{3,}\b', text)
        return tokens[-1] if tokens else ""

    verdict_a = _extract_verdict(resp_a["response"])
    verdict_b = _extract_verdict(resp_b["response"])

    ACTION_VERDICTS = {"TAKE", "YES", "PROCEED", "INVEST", "CONFRONT", "BUILD SOMETHING",
                       "CONCENTRATED BET", "OPTIONALITY", "STRUCTURED YES", "FOUNDATION",
                       "META-WORK", "LONG GAME", "OPTIMIZE OVERLAP", "FRAMEWORK FIRST"}
    PASS_VERDICTS   = {"PASS", "NO", "DECLINE", "WAIT", "SKIP", "AVOID"}

    def _stance(verdict: str) -> str:
        if verdict in ACTION_VERDICTS:
            return "action-oriented"
        if verdict in PASS_VERDICTS:
            return "caution-oriented"
        return "conditional"

    stance_a = _stance(verdict_a)
    stance_b = _stance(verdict_b)

    parts = []

    label_a = verdict_a if verdict_a else stance_a
    label_b = verdict_b if verdict_b else stance_b

    if verdict_a == verdict_b and verdict_a:
        parts.append(
            f"CONVERGE [{label_a}]: Both organisms reach the same verdict in '{scenario['domain']}'. "
            f"Same outcome, different reasoning chains — surface agreement may mask structural difference."
        )
    elif stance_a == stance_b and stance_a != "conditional":
        parts.append(
            f"CONVERGE [{label_a} / {label_b}]: Both lean {stance_a} in '{scenario['domain']}', "
            f"though via different principles."
        )
    else:
        parts.append(
            f"DIVERGE [{label_a} vs {label_b}]: "
            f"{organism_a['name']} → {label_a}, {organism_b['name']} → {label_b} in '{scenario['domain']}'. "
            f"Structural difference in {'risk weighting' if scenario['domain'] in ('risk', 'career', 'opportunity') else 'value priority'}."
        )

    if overlap:
        sample = list(overlap)[:1]
        parts.append(f"Shared foundation: both organisms cite principles around '{sample[0][:60]}...' — alignment here.")

    if unique_a:
        sample = list(unique_a)[:1]
        parts.append(f"{organism_a['name']}'s distinctive signal: '{sample[0][:80]}' — drives their specific stance.")

    if unique_b:
        sample = list(unique_b)[:1]
        parts.append(f"{organism_b['name']}'s distinctive signal: '{sample[0][:80]}' — drives their specific stance.")

    if not parts:
        parts.append(
            f"Insufficient principle differentiation to synthesize meaningfully. "
            f"Both DNA files may need richer principle content."
        )

    return " ".join(parts)


# ---------------------------------------------------------------------------
# Output formatting and file saving
# ---------------------------------------------------------------------------

def build_record(organism_a: dict, organism_b: dict, resp_a: dict, resp_b: dict, scenario: dict) -> dict:
    return {
        "type": "decision_comparison",
        "scenario": scenario["scenario"],
        "domain": scenario["domain"],
        "organism_a": {
            "name": organism_a["name"],
            "response": resp_a["response"],
            "dna_principles_used": resp_a["dna_principles_used"],
        },
        "organism_b": {
            "name": organism_b["name"],
            "response": resp_b["response"],
            "dna_principles_used": resp_b["dna_principles_used"],
        },
        "synthesis": synthesize(organism_a, organism_b, resp_a, resp_b, scenario),
    }


def save_results(records: list, organism_a: dict, organism_b: dict, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)

    name_a = re.sub(r"[^\w]", "_", organism_a["name"])[:20]
    name_b = re.sub(r"[^\w]", "_", organism_b["name"])[:20]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name_a}_vs_{name_b}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)

    payload = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "organism_a_file": organism_a["filepath"],
            "organism_b_file": organism_b["filepath"],
            "scenario_count": len(records),
            "protocol_version": "v0.1",
        },
        "organisms": {
            "a": {
                "name": organism_a["name"],
                "principles_extracted": len(organism_a["principles"]),
                "identity": organism_a["identity"],
            },
            "b": {
                "name": organism_b["name"],
                "principles_extracted": len(organism_b["principles"]),
                "identity": organism_b["identity"],
            },
        },
        "interactions": records,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return filepath


# ---------------------------------------------------------------------------
# LLM prompt generation
# ---------------------------------------------------------------------------

def _read_raw_dna(filepath: str) -> str:
    """Read raw DNA file content for inclusion in LLM prompts."""
    return Path(filepath).read_text(encoding="utf-8", errors="replace")


def generate_llm_prompt(dna_path_a: str, dna_path_b: str, scenario: dict) -> str:
    """
    Generate a structured prompt that can be pasted into any LLM.

    The prompt follows the protocol format from specs/organism_protocol.md:
    - Loads both DNA files' content
    - Presents the scenario
    - Asks the LLM to answer as each organism separately
    - Requests output in the protocol JSON format
    """
    raw_a = _read_raw_dna(dna_path_a)
    raw_b = _read_raw_dna(dna_path_b)

    prompt = f"""You are comparing two digital organisms across a decision scenario.
Read both DNA files below, then answer the scenario AS EACH ORGANISM INDEPENDENTLY.

=== ORGANISM A DNA ===
{raw_a}
=== END ORGANISM A DNA ===

=== ORGANISM B DNA ===
{raw_b}
=== END ORGANISM B DNA ===

=== SCENARIO ({scenario['domain'].upper()}) ===
{scenario['scenario']}

=== INSTRUCTIONS ===
1. Answer as Organism A: State the decision and reasoning based ONLY on Organism A's DNA.
   Cite the specific principles from the DNA that drive the decision.
2. Answer as Organism B: State the decision and reasoning based ONLY on Organism B's DNA.
   Cite the specific principles from the DNA that drive the decision.
3. Synthesis: What does the difference (or agreement) reveal about each organism's values?

Format your response as:

## Organism A: [name]
**Decision**: [concrete decision]
**Reasoning**: [reasoning citing DNA principles]
**Principles used**: [list the specific principles]

## Organism B: [name]
**Decision**: [concrete decision]
**Reasoning**: [reasoning citing DNA principles]
**Principles used**: [list the specific principles]

## Synthesis
[What the comparison reveals about each organism's value structure]

Respond in the same language as each organism's DNA file.
Do NOT invent principles that are not in the DNA. If the DNA is insufficient, say so.
"""
    return prompt


def generate_llm_prompt_batch(dna_path_a: str, dna_path_b: str, scenarios: list) -> str:
    """
    Generate a batch markdown file with prompts for ALL scenarios.

    Each scenario gets its own section with a self-contained prompt.
    """
    name_a = Path(dna_path_a).stem
    name_b = Path(dna_path_b).stem
    raw_a = _read_raw_dna(dna_path_a)
    raw_b = _read_raw_dna(dna_path_b)

    parts = [
        f"# LLM Prompt Batch: {name_a} vs {name_b}",
        f"**Generated**: {datetime.now().isoformat()}",
        f"**Scenarios**: {len(scenarios)}",
        "",
        "## How to use",
        "",
        "Each scenario below is a self-contained prompt. Copy-paste into any LLM session.",
        "For best results, use a CLEAN session for each scenario (no prior context).",
        "",
        "---",
        "",
    ]

    for scenario in scenarios:
        prompt = generate_llm_prompt(dna_path_a, dna_path_b, scenario)
        parts.extend([
            f"## Scenario {scenario['id']}: {scenario['domain'].upper()}",
            "",
            f"**Question**: {scenario['scenario']}",
            "",
            "### Prompt (copy below this line)",
            "",
            "````",
            prompt,
            "````",
            "",
            "### LLM Response (paste here)",
            "",
            "```",
            "[paste LLM output here]",
            "```",
            "",
            "---",
            "",
        ])

    return "\n".join(parts)


def print_record(record: dict, index: int, total: int) -> None:
    sep = "-" * 72
    print(f"\n{'='*72}")
    print(f"  SCENARIO {index}/{total} — {record['domain'].upper()}")
    print(f"{'='*72}")
    print(f"\nSCENARIO:\n  {record['scenario']}\n")

    for side in ("organism_a", "organism_b"):
        org = record[side]
        print(f"{sep}")
        print(f"  {org['name'].upper()}")
        print(sep)
        print(org["response"])
        if org["dna_principles_used"]:
            print(f"\n  Principles invoked:")
            for p in org["dna_principles_used"]:
                print(f"    • {p[:100]}")
        print()

    print(f"{sep}")
    print(f"  SYNTHESIS")
    print(sep)
    print(f"  {record['synthesis']}\n")


# ---------------------------------------------------------------------------
# Collision report generation
# ---------------------------------------------------------------------------

def _classify_record(record: dict) -> str:
    """
    Classify a scenario comparison as 'agreement' or 'divergence'.

    Compares the extracted decision verdicts from both organisms' responses.
    Two organisms agree when they reach the same verdict (e.g. both TAKE,
    both PASS), and diverge when the verdicts differ.
    """
    decision_a = _extract_decision_line(record["organism_a"]["response"])
    decision_b = _extract_decision_line(record["organism_b"]["response"])

    # Extract the verdict keyword (first ALL-CAPS word/phrase before ' — ')
    def _verdict(text: str) -> str:
        m = re.match(r"^([A-Z][A-Z_\s]{2,30}?)\s*[—–-]{1,2}\s*", text)
        if m:
            return m.group(1).strip()
        tokens = re.findall(r"\b[A-Z]{3,}\b", text)
        return tokens[0] if tokens else ""

    verdict_a = _verdict(decision_a)
    verdict_b = _verdict(decision_b)

    if verdict_a and verdict_b and verdict_a == verdict_b:
        return "agreement"
    return "divergence"


def _extract_decision_line(response_text: str) -> str:
    """
    Pull the short decision verdict from a generated response.

    The response format ends with a line like:
        TAKE -- EV = ...
    or  PASS -- ...
    Returns the first ALL-CAPS-prefixed decision line, or the last
    non-empty line as fallback.
    """
    lines = [ln.strip() for ln in response_text.strip().splitlines() if ln.strip()]
    for line in lines:
        # Lines that start with an ALL-CAPS word followed by " — " or " -- "
        m = re.match(r"^([A-Z][A-Z_\s]{2,30}?)\s*[—–-]{1,2}\s*(.+)", line)
        if m:
            return line
    return lines[-1] if lines else "(no decision)"


def _build_domain_heatmap(records: list) -> dict:
    """
    Count agreements and divergences per domain.

    Returns: {domain: {"agreements": int, "divergences": int}}
    """
    heatmap = {}
    for rec in records:
        domain = rec["domain"]
        classification = _classify_record(rec)
        if domain not in heatmap:
            heatmap[domain] = {"agreements": 0, "divergences": 0}
        if classification == "agreement":
            heatmap[domain]["agreements"] += 1
        else:
            heatmap[domain]["divergences"] += 1
    return heatmap


def _build_learning_synthesis(records: list, organism_a: dict, organism_b: dict) -> dict:
    """
    Analyze collision records to determine what each twin could learn from
    the other, based on domains where one diverges from the other's stance.

    Returns: {name_a: [lessons], name_b: [lessons]}
    """
    name_a = organism_a["name"]
    name_b = organism_b["name"]
    lessons_for_a = []
    lessons_for_b = []

    for rec in records:
        classification = _classify_record(rec)
        if classification != "divergence":
            continue

        domain = rec["domain"]
        synth = rec.get("synthesis", "")

        # Extract distinctive signals from synthesis text
        # Pattern: "Name's distinctive signal: 'principle...' — drives their specific stance."
        sig_a_match = re.search(
            rf"{re.escape(name_a)}'s distinctive signal: '(.+?)'", synth
        )
        sig_b_match = re.search(
            rf"{re.escape(name_b)}'s distinctive signal: '(.+?)'", synth
        )

        if sig_b_match:
            lessons_for_a.append(
                f"In {domain}: consider {name_b}'s principle — \"{sig_b_match.group(1)}\""
            )
        else:
            # Generic lesson from the domain divergence
            decision_b = _extract_decision_line(rec["organism_b"]["response"])
            lessons_for_a.append(
                f"In {domain}: {name_b} reaches a different conclusion — review whether your framework accounts for their reasoning"
            )

        if sig_a_match:
            lessons_for_b.append(
                f"In {domain}: consider {name_a}'s principle — \"{sig_a_match.group(1)}\""
            )
        else:
            decision_a = _extract_decision_line(rec["organism_a"]["response"])
            lessons_for_b.append(
                f"In {domain}: {name_a} reaches a different conclusion — review whether your framework accounts for their reasoning"
            )

    return {name_a: lessons_for_a, name_b: lessons_for_b}


def generate_collision_report_md(
    records: list, organism_a: dict, organism_b: dict
) -> str:
    """
    Build a structured markdown collision report.

    Sections:
    1. Header with both DNA names and date
    2. Summary: total scenarios, agreements, divergences
    3. Per-scenario breakdown
    4. Synthesis: what each twin could learn from the other
    5. Divergence heatmap by life domain
    """
    name_a = organism_a["name"]
    name_b = organism_b["name"]
    now = datetime.now()

    total = len(records)
    classifications = [_classify_record(r) for r in records]
    agreements = classifications.count("agreement")
    divergences = classifications.count("divergence")

    lines = []

    # --- Header ---
    lines.append(f"# Collision Report: {name_a} vs {name_b}")
    lines.append("")
    lines.append(f"**Date**: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Organism A**: {name_a} ({organism_a['filepath']})")
    lines.append(f"**Organism B**: {name_b} ({organism_b['filepath']})")
    lines.append(f"**Principles extracted**: A={len(organism_a['principles'])}, B={len(organism_b['principles'])}")
    lines.append("")

    # --- Summary ---
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total scenarios | {total} |")
    lines.append(f"| Agreements | {agreements} |")
    lines.append(f"| Divergences | {divergences} |")
    agreement_pct = (agreements / total * 100) if total > 0 else 0
    lines.append(f"| Agreement rate | {agreement_pct:.0f}% |")
    lines.append("")

    # --- Per-Scenario Breakdown ---
    lines.append("## Per-Scenario Breakdown")
    lines.append("")

    for i, (rec, cls) in enumerate(zip(records, classifications)):
        tag = "AGREE" if cls == "agreement" else "DIVERGE"
        lines.append(f"### Scenario {rec.get('domain', '').upper()} [{tag}]")
        lines.append("")
        lines.append(f"> {rec['scenario']}")
        lines.append("")

        # Each twin's decision
        decision_a = _extract_decision_line(rec["organism_a"]["response"])
        decision_b = _extract_decision_line(rec["organism_b"]["response"])

        lines.append(f"**{name_a}**: {decision_a}")
        lines.append("")
        lines.append(f"**{name_b}**: {decision_b}")
        lines.append("")

        # Principles used
        p_a = rec["organism_a"].get("dna_principles_used", [])
        p_b = rec["organism_b"].get("dna_principles_used", [])
        if p_a:
            lines.append(f"*{name_a}'s principles*:")
            for p in p_a:
                lines.append(f"- {p[:120]}")
        if p_b:
            lines.append(f"*{name_b}'s principles*:")
            for p in p_b:
                lines.append(f"- {p[:120]}")
        lines.append("")

        # Synthesis for this scenario
        lines.append(f"**Synthesis**: {rec.get('synthesis', 'N/A')}")
        lines.append("")
        lines.append("---")
        lines.append("")

    # --- Divergence Heatmap ---
    lines.append("## Divergence Heatmap")
    lines.append("")
    lines.append("Which life domains show the most disagreement between the two twins.")
    lines.append("")

    heatmap = _build_domain_heatmap(records)
    # Sort by divergences descending
    sorted_domains = sorted(
        heatmap.items(), key=lambda x: x[1]["divergences"], reverse=True
    )

    lines.append("| Domain | Agreements | Divergences | Status |")
    lines.append("|--------|------------|-------------|--------|")
    for domain, counts in sorted_domains:
        if counts["divergences"] > 0:
            status = "DIVERGENT"
        else:
            status = "ALIGNED"
        lines.append(
            f"| {domain} | {counts['agreements']} | {counts['divergences']} | {status} |"
        )
    lines.append("")

    # --- Synthesis: Mutual Learning ---
    lines.append("## Synthesis: What Each Twin Could Learn")
    lines.append("")

    learning = _build_learning_synthesis(records, organism_a, organism_b)

    for name, lessons in learning.items():
        lines.append(f"### {name}")
        lines.append("")
        if lessons:
            for lesson in lessons:
                lines.append(f"- {lesson}")
        else:
            lines.append("- No divergent scenarios — twins are fully aligned on tested domains.")
        lines.append("")

    # --- Footer ---
    lines.append("---")
    lines.append("")
    lines.append(f"*Generated by organism_interact.py collision report | {now.isoformat()}*")

    return "\n".join(lines)


def generate_collision_report_json(
    records: list, organism_a: dict, organism_b: dict
) -> dict:
    """
    Build a machine-readable collision report as a dict (for JSON serialization).

    Includes everything in the markdown report in structured form.
    """
    name_a = organism_a["name"]
    name_b = organism_b["name"]
    now = datetime.now()

    total = len(records)
    classifications = [_classify_record(r) for r in records]
    agreements = classifications.count("agreement")
    divergences = classifications.count("divergence")

    heatmap = _build_domain_heatmap(records)
    learning = _build_learning_synthesis(records, organism_a, organism_b)

    scenario_details = []
    for rec, cls in zip(records, classifications):
        scenario_details.append({
            "domain": rec["domain"],
            "scenario": rec["scenario"],
            "classification": cls,
            "organism_a": {
                "name": name_a,
                "decision": _extract_decision_line(rec["organism_a"]["response"]),
                "full_response": rec["organism_a"]["response"],
                "principles_used": rec["organism_a"].get("dna_principles_used", []),
            },
            "organism_b": {
                "name": name_b,
                "decision": _extract_decision_line(rec["organism_b"]["response"]),
                "full_response": rec["organism_b"]["response"],
                "principles_used": rec["organism_b"].get("dna_principles_used", []),
            },
            "synthesis": rec.get("synthesis", ""),
        })

    return {
        "meta": {
            "report_type": "collision",
            "generated_at": now.isoformat(),
            "organism_a_file": organism_a["filepath"],
            "organism_b_file": organism_b["filepath"],
            "protocol_version": "v0.1",
        },
        "summary": {
            "total_scenarios": total,
            "agreements": agreements,
            "divergences": divergences,
            "agreement_rate": round(agreements / total * 100, 1) if total > 0 else 0,
        },
        "organisms": {
            "a": {
                "name": name_a,
                "principles_extracted": len(organism_a["principles"]),
                "identity": organism_a["identity"],
            },
            "b": {
                "name": name_b,
                "principles_extracted": len(organism_b["principles"]),
                "identity": organism_b["identity"],
            },
        },
        "scenarios": scenario_details,
        "divergence_heatmap": heatmap,
        "learning_synthesis": learning,
    }


def save_collision_report(
    records: list, organism_a: dict, organism_b: dict, output_dir: str
) -> tuple:
    """
    Save both markdown and JSON collision reports.

    Returns: (md_path, json_path)
    """
    os.makedirs(output_dir, exist_ok=True)

    name_a = re.sub(r"[^\w]", "_", organism_a["name"])[:20]
    name_b = re.sub(r"[^\w]", "_", organism_b["name"])[:20]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"collision_{name_a}_vs_{name_b}_{timestamp}"

    # Markdown report
    md_content = generate_collision_report_md(records, organism_a, organism_b)
    md_path = os.path.join(output_dir, f"{base}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    # JSON report
    json_data = generate_collision_report_json(records, organism_a, organism_b)
    json_path = os.path.join(output_dir, f"{base}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    return md_path, json_path


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Digital Organism Interaction — decision comparison across two DNA files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("dna_a", help="Path to DNA file for organism A (markdown)")
    parser.add_argument("dna_b", help="Path to DNA file for organism B (markdown)")
    parser.add_argument(
        "--scenario", type=int, metavar="N",
        help="Run a single scenario by number (1-10). Default: run all.",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Explicitly run all 10 scenarios (default behavior).",
    )
    parser.add_argument(
        "--output-dir", default=None,
        help="Directory to write JSON results. Defaults to results/ next to this script.",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress terminal output; only write JSON file.",
    )
    parser.add_argument(
        "--report", action="store_true",
        help="Generate structured collision report (markdown + JSON) in results/.",
    )
    parser.add_argument(
        "--list-scenarios", action="store_true",
        help="Print the 10 built-in scenarios and exit.",
    )
    parser.add_argument(
        "--llm-prompt", action="store_true",
        help="Generate a structured LLM prompt instead of running the deterministic engine. "
             "Outputs to stdout (or to file with --output).",
    )
    parser.add_argument(
        "--llm-prompt-batch", action="store_true",
        help="Generate LLM prompts for ALL scenarios as a markdown file in results/.",
    )
    parser.add_argument(
        "--output", default=None, metavar="FILE",
        help="Save LLM prompt output to this file instead of stdout.",
    )
    args = parser.parse_args()

    if args.list_scenarios:
        for s in SCENARIOS:
            print(f"  [{s['id']:2d}] [{s['domain'].upper():13s}] {s['scenario'][:80]}...")
        sys.exit(0)

    # Resolve output directory relative to this script's location
    script_dir = Path(__file__).parent
    output_dir = args.output_dir or str(script_dir / "results")

    # Load DNA files
    try:
        print(f"Loading DNA A: {args.dna_a}")
        organism_a = parse_dna(args.dna_a)
        print(f"  → {organism_a['name']} | {len(organism_a['principles'])} principles extracted")

        print(f"Loading DNA B: {args.dna_b}")
        organism_b = parse_dna(args.dna_b)
        print(f"  → {organism_b['name']} | {len(organism_b['principles'])} principles extracted")
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Select scenarios
    if args.scenario:
        if args.scenario < 1 or args.scenario > len(SCENARIOS):
            print(f"ERROR: --scenario must be 1-{len(SCENARIOS)}", file=sys.stderr)
            sys.exit(1)
        scenarios_to_run = [SCENARIOS[args.scenario - 1]]
    else:
        scenarios_to_run = SCENARIOS

    # --- LLM prompt modes ---
    if args.llm_prompt_batch:
        batch_md = generate_llm_prompt_batch(args.dna_a, args.dna_b, scenarios_to_run)
        if args.output:
            out_path = args.output
        else:
            name_a = re.sub(r"[^\w]", "_", organism_a["name"])[:20]
            name_b = re.sub(r"[^\w]", "_", organism_b["name"])[:20]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs(output_dir, exist_ok=True)
            out_path = os.path.join(output_dir, f"llm_prompts_{name_a}_vs_{name_b}_{timestamp}.md")
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        Path(out_path).write_text(batch_md, encoding="utf-8")
        print(f"Batch prompts saved to: {out_path}")
        sys.exit(0)

    if args.llm_prompt:
        if len(scenarios_to_run) == 1:
            prompt = generate_llm_prompt(args.dna_a, args.dna_b, scenarios_to_run[0])
        else:
            # Multiple scenarios: concatenate with separators
            parts = []
            for s in scenarios_to_run:
                parts.append(f"{'='*60}")
                parts.append(f"SCENARIO {s['id']}: {s['domain'].upper()}")
                parts.append(f"{'='*60}\n")
                parts.append(generate_llm_prompt(args.dna_a, args.dna_b, s))
            prompt = "\n".join(parts)

        if args.output:
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            Path(args.output).write_text(prompt, encoding="utf-8")
            print(f"Prompt saved to: {args.output}")
        else:
            print(prompt)
        sys.exit(0)

    print(f"\nRunning {len(scenarios_to_run)} scenario(s)...\n")

    # Run comparisons
    records = []
    for scenario in scenarios_to_run:
        resp_a = generate_response(organism_a, scenario)
        resp_b = generate_response(organism_b, scenario)
        record = build_record(organism_a, organism_b, resp_a, resp_b, scenario)
        records.append(record)
        if not args.quiet:
            print_record(record, scenario["id"], len(SCENARIOS))

    # Save
    output_path = save_results(records, organism_a, organism_b, output_dir)
    print(f"\nResults saved to: {output_path}")

    # Collision report
    if args.report:
        md_path, json_path = save_collision_report(
            records, organism_a, organism_b, output_dir
        )
        print(f"\nCollision report (markdown): {md_path}")
        print(f"Collision report (JSON):     {json_path}")


if __name__ == "__main__":
    main()
