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
    python organism_interact.py --multi dna1.md dna2.md dna3.md [dna4.md ...]
    python organism_interact.py --multi dna1.md dna2.md dna3.md --report

Examples:
    python organism_interact.py templates/example_dna.md path/to/other_dna.md --all
    python organism_interact.py dna_a.md dna_b.md --scenario 3
    python organism_interact.py dna_a.md dna_b.md           # runs all 10
    python organism_interact.py dna_a.md dna_b.md --report   # structured collision report
    python organism_interact.py --multi a.md b.md c.md       # 3+ organism collision
    python organism_interact.py --multi a.md b.md c.md --report  # with report

Output:
    results/<organism_a>_vs_<organism_b>_<timestamp>.json
    results/collision_<name1>_vs_<name2>_<timestamp>.md   (with --report)
    results/collision_<name1>_vs_<name2>_<timestamp>.json  (with --report)
    results/multi_collision_<names>_<timestamp>.md          (with --multi --report)
    results/multi_collision_<names>_<timestamp>.json         (with --multi --report)

Protocol format follows specs/organism_protocol.md v0.1
"""

import argparse
import itertools
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
    {
        "id": 11,
        "domain": "communication",
        "scenario": (
            "A close friend asks for your quick take on their new business idea during "
            "a 10-minute coffee chat. You have reservations but haven't fully analyzed it. "
            "Do you give a hedged multi-paragraph analysis, or a direct 10-second verdict? "
            "What exactly do you say first?"
        ),
    },
    {
        "id": 12,
        "domain": "meta_strategy",
        "scenario": (
            "You're asked a complex question in a group setting. "
            "Five people are waiting. Option A: think out loud for 90 seconds with caveats. "
            "Option B: give a direct 10-second verdict, explain briefly if pressed. "
            "Which do you choose, and what principle drives it?"
        ),
    },
    {
        "id": 13,
        "domain": "social_trust",
        "scenario": (
            "A new contact — smart, well-connected, shares your field — wants to move to a "
            "close friendship quickly: frequent messages, shared plans within the first week, "
            "treating you like a long-time friend before you know their track record. "
            "Do you reciprocate at their pace, or set your own cadence?"
        ),
    },
    {
        "id": 14,
        "domain": "network_roi",
        "scenario": (
            "You have invested 2 years in a professional relationship — coffees, introductions, "
            "referrals, genuine effort. You now realize the flow is 80% one-directional (you giving). "
            "The other person is not malicious, just self-absorbed and oblivious. "
            "What do you do, and at what threshold do you change your investment level?"
        ),
    },
    {
        "id": 15,
        "domain": "social_debt",
        "scenario": (
            "A favor you owe someone has become more expensive to repay than you anticipated — "
            "fulfilling it at original terms would require compromising something important to you. "
            "The other person has not asked yet but will eventually. "
            "Do you repay as agreed, renegotiate proactively, or let the relationship absorb the friction?"
        ),
    },
    {
        "id": 16,
        "domain": "group_dynamics",
        "scenario": (
            "You are in a group decision where you hold a contrarian view and are nearly certain you are right. "
            "The group is moving toward consensus in the wrong direction. "
            "You are the least senior person in the room. The cost of the wrong decision falls on everyone. "
            "What do you do?"
        ),
    },
    {
        "id": 17,
        "domain": "weak_ties",
        "scenario": (
            "You have 300+ professional connections but only 8 close friendships. "
            "A significant opportunity arrives through your weak-tie network — "
            "someone you have not spoken to in over 2 years reaches out with it. "
            "How do you evaluate and respond, and what does this reveal about how you maintain your network?"
        ),
    },
    {
        "id": 18,
        "domain": "intro_gatekeeping",
        "scenario": (
            "A close friend asks you to introduce them to your most valuable professional contact. "
            "You believe in your friend, but you are not confident the timing or fit is right — "
            "your contact is busy, and the ask is only 60% aligned with what they care about. "
            "Do you make the intro, qualify it heavily, or decline and explain why?"
        ),
    },
    {
        "id": 19,
        "domain": "loyalty_vs_credibility",
        "scenario": (
            "Someone you publicly vouched for — recommended for a role, endorsed to a contact — "
            "has underperformed or behaved poorly in a visible way. Your credibility is attached "
            "to their actions. They have not asked for your help yet. "
            "Do you publicly distance yourself, privately correct them first, or stand by them unconditionally?"
        ),
    },
    {
        "id": 20,
        "domain": "social_capital_depth",
        "scenario": (
            "You have 60 minutes of free social time. Option A: deepen a relationship "
            "with one person you already trust (long 1:1 conversation). Option B: meet two "
            "new well-connected people at a networking event (30 min each, first impressions only). "
            "This choice recurs every week. What is your default allocation and why?"
        ),
    },
    {
        "id": 21,
        "domain": "relationship_downgrade",
        "scenario": (
            "A Tier 1 relationship has gradually shifted — less available, less reciprocal, "
            "more self-focused. Nothing confrontational has happened. You used to talk weekly; "
            "now it is monthly, and you are always the one initiating. "
            "How do you handle the transition — explicitly, quietly, or not at all?"
        ),
    },
    {
        "id": 22,
        "domain": "first_impression_update",
        "scenario": (
            "Your initial strong positive impression of someone (formed in the first meeting) "
            "has been challenged by two instances of behavior that do not match it — "
            "not catastrophic, just inconsistent with how they presented themselves. "
            "Do you revise your assessment now, give them the benefit of the doubt, "
            "or require a third data point before updating your model of them?"
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
    # Try H1 heading first — skip generic/placeholder names
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# ") and len(stripped) > 2:
            candidate = stripped[2:].strip()
            # Strip common suffixes like "DNA", "v18", "Blueprint"
            candidate = re.sub(r"\s+(DNA|Blueprint|v\d+[\.\d]*).*$", "", candidate, flags=re.IGNORECASE)
            # Skip bracket placeholders like "[Your Name]" and generic file titles
            if candidate and not re.match(r"^\[.+\]$", candidate) and not re.match(
                r"^(DNA\s+Core|Operational\s+Minimum|Example|Template|Sample)", candidate, re.IGNORECASE
            ):
                return candidate
    # Fall back to identity table "name" or "full name" field
    in_identity = False
    for line in lines:
        if re.match(r"^#{1,3}\s+.*[Ii]dentity", line):
            in_identity = True
            continue
        if in_identity:
            if line.startswith("#"):
                break
            m = re.match(r"\|\s*(full\s+name|name)\s*\|\s*([^|]+?)\s*\|", line, re.IGNORECASE)
            if m:
                val = m.group(2).strip()
                # Skip placeholders and header values
                if val and not re.match(r"^\[.+\]$", val) and val.lower() not in ("value", "detail", "---", "field"):
                    return val
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
    "social":           ["relationship", "trust", "friend", "social", "maintenance", "proactive", "contact", "cadence", "silence", "tier", "initiate", "reach", "人際", "信任", "主動", "聯繫", "維護", "沉默", "關係", "行為", "模式", "驗證", "一致性"],
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
    "trading":          ["trading", "trade", "strategy", "return", "time", "edge", "risk", "maintenance", "kill", "策略管理"],
    "finance":          ["finance", "financial", "invest", "money", "wealth", "allocat", "capital", "income"],
    "identity":         ["identity", "action", "specific", "commit", "responsib", "person", "first"],
    "meta_strategy":    ["meta", "system", "process", "metric", "deteriorat", "regime", "diagnos", "pause"],
    "communication":    ["direct", "verdict", "response", "reply", "concise", "short", "length", "conviction", "intuition", "直接", "結論", "回應", "簡短", "確信"],
    "capital_allocation": ["capital", "allocat", "invest", "debt", "loan", "rate", "yield", "dividend", "DCA", "比率", "利率", "殖利率", "分批", "還債", "資產配置"],
    "position_sizing":  ["position", "sizing", "Kelly", "fraction", "bet", "risk", "volatility", "kelly", "口數", "部位", "槓桿"],
    "information_asymmetry": ["information", "asymmetry", "edge", "research", "知識", "資訊", "不對稱", "優勢"],
    "information":      ["media", "headline", "narrative", "earnings", "dimension", "decode", "news", "報導", "媒體", "財報", "選擇性", "維度"],
    "negotiation":      ["negotiation", "salary", "floor", "anchor", "deal", "談判", "底線", "薪資", "精算"],
    "knowledge_output": ["knowledge", "output", "teach", "explain", "write", "publish", "content", "platform", "SOP", "product", "知識", "輸出", "教學", "解釋", "寫作", "平台"],
    "life_maintenance": ["life", "routine", "habit", "environment", "default", "automate", "schedule", "peak", "cognitive", "sleep", "生活", "習慣", "環境設計", "預設", "自動化", "峰值"],
    "strategy":         ["strategy", "competitive", "opponent", "threat", "game", "zero-sum", "negotiation", "danger", "risk profile", "threat profile", "賽局", "威脅", "對手", "角色化", "競爭"],
    "social_trust":     ["trust", "verify", "behavior", "pattern", "relationship", "probe", "signal", "cadence", "new", "observe", "track record", "fast", "rush", "信任", "驗證", "行為", "模式", "關係", "新", "觀察"],
    "network_roi":      ["network", "roi", "relationship", "invest", "reciproc", "one-way", "tier", "maintain", "audit", "silent", "返回", "關係", "投資", "單向", "回報", "維護", "審計"],
    "social_debt":      ["obligation", "favor", "owe", "debt", "commitment", "repay", "renegotiate", "social", "promise", "承諾", "義務", "人情", "還", "重新談"],
    "group_dynamics":   ["group", "consensus", "contrarian", "senior", "junior", "voice", "dissent", "hierarchy", "collective", "decision", "群體", "共識", "反向", "異見", "階級", "發聲"],
    "weak_ties":        ["weak", "network", "contact", "dormant", "reactivate", "reconnect", "broad", "connection", "shallow", "respond", "弱連結", "網絡", "重啟", "廣泛", "連結", "回應"],
    "intro_gatekeeping":        ["intro", "introduction", "referral", "vouch", "endorse", "contact", "gatekeeper", "fit", "recommendation", "reputation", "network", "node", "推薦", "介紹", "信譽", "聯絡人", "轉介"],
    "loyalty_vs_credibility":   ["loyal", "credibil", "vouch", "defend", "reputation", "public", "distance", "stand by", "protect", "endorse", "background", "信任", "忠誠", "聲譽", "公開", "背書", "距離"],
    "social_capital_depth":     ["depth", "deepen", "1:1", "one-on-one", "one on one", "broad", "new contact", "breadth", "existing", "network", "relationship", "投資", "深度", "廣度", "新認識", "深化", "一對一"],
    "relationship_downgrade":   ["downgrade", "tier", "reduce", "fade", "drift", "recalibrate", "reclassify", "frequency", "availab", "reciproc", "降級", "關係層級", "疏遠", "淡化", "重新評估", "主動"],
    "first_impression_update":  ["first impression", "update", "evidence", "inconsistenc", "revision", "observation", "data", "pattern", "trust", "initial", "第一印象", "更新", "不一致", "修正", "觀察", "校正"],
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
        "social_trust":          "On new relationship pacing",
        "network_roi":           "On network ROI and relationship rebalancing",
        "social_debt":           "On social obligation and renegotiation",
        "group_dynamics":        "On dissent and group consensus",
        "weak_ties":             "On reactivating dormant network connections",
        "intro_gatekeeping":     "On introduction and referral gatekeeping",
        "loyalty_vs_credibility": "On loyalty versus credibility trade-offs",
        "social_capital_depth":  "On social capital depth vs breadth allocation",
        "relationship_downgrade": "On relationship tier recalibration",
        "first_impression_update": "On updating first impressions with new evidence",
    }.get(domain, f"On {domain}")

    lines = [f"{framing}, {name}'s decision framework yields:"]
    lines.append("")

    for i, p in enumerate(principles, 1):
        # Truncate very long principles for readability
        p_display = p if len(p) <= 120 else p[:117] + "..."
        lines.append(f"  [{i}] Applying: \"{p_display}\"")

    lines.append("")

    # Domain-specific decision logic stubs — uses principle text + scenario text as signal
    all_text = " ".join(principles).lower()
    scenario_text = (str(scenario.get("scenario", "")) + " " + str(scenario.get("id", ""))).lower()
    decision_text = _domain_decision(domain, all_text, scenario_text)
    lines.append(decision_text)

    return "\n".join(lines)


def _domain_decision(domain: str, principle_text: str, scenario_text: str = "") -> str:
    """Map domain + principle signals to a concrete decision stance."""
    combined = principle_text + " " + scenario_text
    stability_signal = any(w in principle_text for w in ["stable", "stability", "hedge", "safe", "conservative"])
    growth_signal    = any(w in principle_text for w in ["growth", "compound", "upside", "opportunit", "aggressive"])
    ev_signal        = any(w in principle_text for w in ["ev", "expected value", "probability", "edge"])
    inaction_signal  = any(w in principle_text for w in ["inaction", "wait", "patience", "no edge", "pass"])
    direct_signal    = any(w in principle_text for w in ["direct", "confront", "honest", "transparent"])
    system_signal    = any(w in principle_text for w in ["system", "process", "framework", "structure"])
    meta_signal      = any(w in principle_text for w in ["meta", "long-term", "second order", "derivative"])
    time_cost_signal = any(w in principle_text for w in ["evaluate time", "time vs", "time cost", "maintenance", "hours", "daily maintenance", "opportunity cost", "時薪", "時間成本"])

    decisions = {
        "career": (
            "MULTI_TRACK_BEFORE_CONVERGE — "
            "MD-327: 職涯探索=多軌同時開評估窗口. Maintain 4–6 parallel exploration tracks until a real positive signal "
            "(concrete offer, demonstrated advantage, genuine market pull) triggers convergence. "
            "'I've researched one direction' is analysis, not real signal. Premature convergence selects the most-familiar path, "
            "not the best-fit path. Run validation actions across multiple tracks simultaneously; converge only on real feedback."
            if any(w in combined for w in ["multi-track", "explore", "parallel", "convergence", "converge", "探索", "多軌", "窗口", "multi_track"]) else
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
            "CALCULATE_FRICTION_COST_FIRST — "
            "MD-326: 交易成本先算再下單=摩擦成本（手續費×口數×來回）明確化是每次執行的前置步驟. "
            "Before any execution: commission_rate × position_size × 2 (entry+exit) = round-trip friction. "
            "Execute only if expected_gain > friction_cost. Friction is a certain negative; profit is an expectation — "
            "the floor must be cleared before EV calculation is valid."
            if any(w in combined for w in ["commission", "friction", "手續費", "摩擦", "transaction cost", "0.11", "round-trip", "friction_cost"]) else
            "EVALUATE_TIME_VS_RETURN — calculate total time cost (hours/year) and verify annualized return against alternatives. No independent audit = unverified claim. Compare time-adjusted EV against best alternative use before committing. TR-6: time cost × opportunity cost must be covered by net return."
            if time_cost_signal else
            "DEFINE_KILL_CONDITIONS_FIRST — predefined failure conditions (max drawdown, min win rate, min profit factor) must be written before any live deployment. MD-95/136: strategy management without defined failure conditions is subjective and systematically wrong."
            if any(w in principle_text for w in ["kill condition", "kill", "失效", "stop all", "threshold"]) else
            "BET_FRACTIONAL_KELLY — near full-Kelly, reduce bet size; fractional Kelly (half-Kelly) sacrifices minimal EV while dramatically cutting variance and ruin risk. MD-217: Kelly保險=高勝率接近全押時降波動有EV."
            if any(w in principle_text for w in ["kelly", "kelly criterion", "sizing", "fraction"]) else
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
        "position_sizing": (
            "BET_FRACTIONAL_KELLY — near full-Kelly, reduce bet size; fractional Kelly (half-Kelly) sacrifices minimal EV while dramatically cutting variance and ruin risk. MD-217: Kelly保險=高勝率接近全押時降波動有EV."
            if any(w in principle_text for w in ["kelly", "sizing", "fraction", "position", "volatility", "波動"]) else
            "BET_FRACTIONAL_KELLY — full Kelly maximizes log-growth but at maximum variance; half-Kelly or lower preserves most EV while reducing drawdown and ruin probability."
        ),
        "communication": (
            "LEAD_WITH_VERDICT — lead with the reservation directly; verdict first, reasoning only if pressed. "
            "Trust the 3-second intuition read; short response signals high conviction. "
            "Override analysis only with 2x positive evidence when gut says no."
            if direct_signal else
            "LEAD_WITH_VERDICT — state your position immediately; the first sentence must be the conclusion. "
            "Reply length is an inverse confidence indicator: say it in one sentence. "
            "3-second intuition precedes analysis — trust it unless borderline analysis provides 2x confirmation."
        ),
        "negotiation": (
            "CALCULATE_FLOOR_FIRST_WRITTEN — before any negotiation meeting, write down your precise floor derived from real numbers (opportunity cost, market percentile, walk-away alternatives). "
            "MD-128/MD-211: 精算底線 must be on paper before the meeting starts. "
            "Book the deal if and only if offer exceeds floor. Deflecting anchor is secondary; floor-first is the mandatory step."
            if (system_signal or stability_signal or ev_signal) else
            "CALCULATE_FLOOR_FIRST_WRITTEN — floor must be calculated and written before negotiating. "
            "Gut-feel floors are invalid; only real numbers (market rate, opportunity cost, alternatives) count. "
            "Without a written floor, you cannot make a principled accept/reject decision."
        ),
        "information": (
            "DECODE_ALL_DIMENSIONS_NOT_ONE — "
            "MD-314: 媒體財報敘事=選擇性維度. Media picks the single most impressive metric. "
            "Force all three simultaneously: absolute amount, percentage change, AND vs benchmark (estimate/prior year). "
            "A single reported dimension is insufficient to update your view."
        ),
        "capital_allocation": (
            "COMPARE_RATES_NOT_AMOUNTS / DCA_IS_DEFAULT_EXECUTION / CALCULATE_INCOME_TARGET_FROM_YIELD / HOLD_WHEN_YIELD_EXCEEDS_DRAWDOWN / COMPARE_ABSOLUTE_CASHFLOW_SAME_CAPITAL — "
            "MD-313: 股息殖利率×持倉規模=固定支出替換器. target_income / yield% = required_capital milestone. "
            "MD-315: 大資本=免停損條件. stop-loss necessity = f(capital scale, yield stability). When dividend yield > typical annual drawdown AND position < 5% total capital AND holding period > 3yr, hold dominates forced exit. Calculate hold-to-recovery time vs certain exit loss. "
            "MD-316: 還債vs投資決策=比較利率%不比較絕對金額. If investment yield% > loan rate%, deploy capital in the asset. "
            "MD-317: 股票選擇=相同資本下現金流比較. When yields% are similar, compute (capital / price) × dividend_per_share = absolute annual cashflow, then compare amounts — not yield%. "
            "MD-318: 分批買進=分析通過後執行策略的預設答案. Once analysis clears (yield/survival/cashflow), "
            "execution defaults to DCA immediately — 'wait for dip' re-introduces a timing loop the DCA rule eliminates. "
            "Separate 'which asset?' (analysis) from 'how to buy?' (execution)."
            if (ev_signal or stability_signal) else
            "COMPARE_RATES_NOT_AMOUNTS — compare yield% vs loan rate%, not absolute savings amount. "
            "DCA_IS_DEFAULT_EXECUTION — when analysis is complete, start DCA immediately, not after a dip. "
            "CALCULATE_INCOME_TARGET_FROM_YIELD — target_income / yield% = required_capital; convert abstract goals to capital milestones. "
            "HOLD_WHEN_YIELD_EXCEEDS_DRAWDOWN — when yield > drawdown% and position sizing is safe, hold dominates stop-loss. "
            "COMPARE_ABSOLUTE_CASHFLOW_SAME_CAPITAL — same capital invested: compute shares × dividend_per_share for each option, compare absolute cashflow amounts."
        ),
        "knowledge_output": (
            "OUTPUT_TO_VALIDATE_UNDERSTANDING — "
            "MD-319: 知識輸出=思維缺口偵測器. If you cannot explain it clearly to an unfamiliar listener, "
            "the gap is in your understanding, not the topic's complexity. "
            "Schedule forced-output checkpoints: 2-min oral summary after each learning unit. "
            "Where explanation stalls = where to reinforce. "
            "MD-321: PRODUCTIZE_SOP — high-reuse personal procedures are knowledge product candidates; "
            "productization forces all implicit assumptions to surface."
        ),
        "life_maintenance": (
            "REDUCE_DECISION_FREQUENCY — "
            "MD-322: 生活系統=最小決策頻率設計. Any decision appearing more than 3 times = system design failure. "
            "Automate or pre-decide; preserve decision capacity for non-recurring high-stakes problems. "
            "MD-323: PROTECT_PEAK_COGNITIVE_WINDOW — schedule high-cognitive tasks (strategy/analysis/decisions) "
            "exclusively in biological peak hours; defer admin/email/mechanical tasks to off-peak. "
            "MD-324: DESIGN_ENVIRONMENT_FIRST — before invoking willpower, redesign the environment so the "
            "optimal behavior is the lowest-friction path. Environment is a constant; willpower is a depletable resource."
        ),
        "strategy": (
            "IDENTIFY_THREAT_PROFILE_FIRST — "
            "MD-325: 賽局角色化最大威脅先識別. Before deploying any strategy, enumerate the opponent profile that "
            "maximally threatens your current role: 'What characteristics do I most fear in an opponent?' "
            "Build the threat checklist first; scan the field for matches on entry; neutralize or avoid high-threat actors. "
            "Having a strategy is necessary but not sufficient — undetected high-threat opponents override strategy quality."
        ),
        "social": (
            "MAINTAIN_PROACTIVE_CADENCE — "
            "MD-328: 關係投資=主動維護稀缺性原則. Waiting for others to initiate contact is outsourcing relationship maintenance. "
            "For Tier 1 relationships: max silence period = 3 weeks. 6 weeks without contact = trigger immediately. "
            "Proactive reach out is not desperation — it is owning the relationship rhythm. "
            "A short message costs nothing; absence has compounding cost. Contact now."
            if any(w in combined for w in ["proactive", "wait", "contact", "silence", "tier", "reach", "initiate", "主動", "聯繫", "沉默", "維護", "first"]) else
            "VERIFY_BY_BEHAVIOR_PATTERN — "
            "MD-330: 社交信號=行為模式比言語可信. Observe 3+ instances of behavior before updating trust assessment. "
            "Stated intentions are hypotheses; fulfilled commitments are data. "
            "3-month observation window: track commitment fulfillment rate, not impression score. "
            "Behavior pattern > words. Consistency > volume of positive signals."
            if any(w in combined for w in ["behavior", "pattern", "verify", "consistent", "trust", "action", "行為", "模式", "驗證", "一致性", "言語", "observe"]) else
            "MAINTAIN_PROACTIVE_CADENCE — maintain regular proactive contact with important relationships; "
            "do not wait for the other party to initiate. MD-328: 主動維護 is the default stance for Tier 1/2 relationships."
        ),
        "social_trust": (
            "VERIFY_BY_BEHAVIOR_PATTERN — "
            "MD-330: 社交信號=行為模式比言語可信. Set your own cadence; do not match accelerated pacing from a new contact. "
            "Fast-moving friendships before track record is established carry asymmetric downside. "
            "Observe 3+ instances of behavior under real conditions before updating trust level. "
            "Warm but unhurried is the correct posture: reciprocate with genuine interest, not matching urgency."
            if (system_signal or inaction_signal or stability_signal) else
            "MATCH_PACE_THEN_VERIFY — reciprocate warmly at a slightly lower intensity; "
            "genuine enthusiasm is a positive signal but requires behavioral confirmation over 90 days. "
            "Initiate concrete plans to observe follow-through before deepening trust."
        ),
        "network_roi": (
            "AUDIT_AND_REBALANCE — "
            "MD-328: 關係投資=主動維護稀缺性原則. Run a 3-month audit: initiation ratio, value-sharing frequency, "
            "commitment fulfillment. If ratio < 30% (them initiating), send one explicit signal — share something "
            "valuable, ask a direct question requiring effort to answer. One non-response to a direct ask = "
            "DORMANT reclassification. Two = reduce to Tier 3. Not punitive — preserving your investment capacity."
            if (system_signal or ev_signal or stability_signal) else
            "REBALANCE_QUIETLY — reduce investment frequency over 60 days without announcement; "
            "preserve the relationship shell while redirecting time to higher-reciprocity relationships. "
            "Self-absorbed people rarely notice slow withdrawal — save the confrontation energy."
        ),
        "social_debt": (
            "RENEGOTIATE_PROACTIVELY_WRITTEN — "
            "MD-243: 合約書面化供應商. Before the other party asks, surface the constraint directly: "
            "'I committed to X. The cost has changed — here is what I can actually do.' "
            "Proactive disclosure is higher-trust than a failed delivery. "
            "Key: renegotiate before the debt is called, not after. Silence until asked = broken commitment signal."
            if (direct_signal or system_signal) else
            "HONOR_OR_RENEGOTIATE — binary choice: deliver as agreed, or renegotiate now before being asked. "
            "Partial delivery without communication is the worst outcome. "
            "The relationship absorbs renegotiation better than discovered non-delivery."
        ),
        "group_dynamics": (
            "STATE_ONCE_CLEARLY_THEN_RECORD — "
            "State your view once, concisely, with your reasoning. Do not repeat. Do not escalate. "
            "If overruled: document your position (email, notes) with your reasoning so the record exists. "
            "The goal is not to win the room — it is to ensure the correct information entered the system. "
            "Junior seniority means your obligation is to speak the truth once, not to force the outcome."
            if (direct_signal or system_signal or inaction_signal) else
            "RAISE_THE_FLAG_ONCE — voice your view clearly once, briefly, without hedging. "
            "If the group does not engage, you have done your part. "
            "Repeated pushback wastes political capital and signals poor judgment about when to press. "
            "Let the decision be made; let the result teach."
        ),
        "weak_ties": (
            "RESPOND_WITH_VALUE_FIRST — "
            "MD-202: 人脈介紹=用完沉默+回報結果. For a dormant connection reactivating with an opportunity: "
            "respond promptly, evaluate the opportunity on its own merits (not because of the relationship), "
            "acknowledge the reconnection explicitly, follow up regardless of outcome. "
            "Weak ties activate for transactions — that is their function. Accept it, don't resent it. "
            "The quality of your response re-establishes your standing in their network."
            if (ev_signal or growth_signal or direct_signal) else
            "RESPOND_AND_EVALUATE — respond promptly; do not penalize the gap in contact. "
            "Evaluate the opportunity on its actual merits. "
            "Use this reactivation as a signal to audit which dormant connections have potential — "
            "not all weak ties are equal; the ones that reactivate with value are worth maintaining."
        ),
        "intro_gatekeeping": (
            "QUALIFY_OR_DEFER — "
            "MD-202: 人脈介紹=用完沉默+回報結果. Your credibility is collateral in every intro. "
            "60% fit is below threshold: either prime the contact first ('a friend might reach out re X — "
            "relevant?'), or defer until fit improves. A qualified intro ('context: X, caveat: Y') is better "
            "than a cold push. A declined intro explained honestly preserves more trust than a misaligned one."
            if (stability_signal or inaction_signal or system_signal) else
            "MAKE_THE_INTRO_WITH_CONTEXT — "
            "strong relationships warrant the benefit of the doubt; frame the intro clearly so your contact "
            "can opt out gracefully. Your friend's track record of follow-through is the real variable — "
            "if high, the 60% fit risk is acceptable. If unknown, qualify or defer."
        ),
        "loyalty_vs_credibility": (
            "PRIVATE_CORRECTION_FIRST — "
            "Public distancing before private conversation is betrayal theater. "
            "The first move is always private and direct: name the behavior, not the person's character. "
            "If they course-correct, your public credibility is intact and the relationship strengthens. "
            "If they don't, public distance becomes defensible because you tried the right sequence. "
            "Loyalty is not unconditional silence — it is honest feedback before visible consequences."
            if (direct_signal or system_signal) else
            "STAND_BY_QUIETLY_AND_CORRECT — "
            "defend publicly only what you can defend privately; if you cannot defend it privately, "
            "do not defend it publicly. Reduce visible association while working the correction privately."
        ),
        "social_capital_depth": (
            "DEPTH_OVER_BREADTH — "
            "Deep 1:1 with a trusted person generates compounding returns: trust, candor, reciprocity. "
            "New connections at 30 min each are mostly zero-EV — first impressions without track record "
            "are noise. If your current Tier 1 pool is below 5 people, depth is the priority. "
            "Networking events are for specific, pre-targeted contacts — not default social allocation. "
            "Weekly default: deepen existing relationships; use events only with a specific target in mind."
            if (stability_signal or system_signal or meta_signal) else
            "BREADTH_WITH_MINIMUM_DEPTH — "
            "if the Tier 1 pool is healthy, expand the funnel with new contacts; "
            "reserve 1 deep slot per month to maintain existing trust while building surface area. "
            "Relationships require a funnel — not all breadth is wasteful."
        ),
        "relationship_downgrade": (
            "REDUCE_QUIETLY_THEN_SIGNAL_ONCE — "
            "MD-328: 關係投資=主動維護稀缺性原則. Reciprocity is a two-way condition. "
            "Step 1: reduce your initiation frequency by 50% over 60 days without announcement. "
            "If they close the gap — relationship was not broken, just dormant. "
            "If they don't — send one low-friction signal (a share, a question) requiring minimal effort to answer. "
            "No response = DORMANT reclassification. No drama, no confrontation. "
            "Explicit downgrade conversations carry more cost than the behavior change itself."
            if (system_signal or stability_signal or inaction_signal) else
            "DIRECT_CONVERSATION — "
            "if the relationship was close enough to merit a direct conversation, have it: "
            "'I've noticed less connection lately — is everything okay?' "
            "Gives them the option to close the gap rather than assuming drift. "
            "Some people go quiet under load, not under diminished care."
        ),
        "first_impression_update": (
            "REQUIRE_THIRD_DATA_POINT — "
            "MD-330: 社交信號=行為模式比言語可信. Two data points define a line, not a pattern. "
            "Two inconsistencies could be noise, context-specific behavior, or signal. "
            "Set a 3-instance threshold before revising the model: observe one more instance under "
            "a different condition (pressure, conflict, ambiguity). "
            "Lower your trust stance now (reduce exposure, increase observation), but do not formally "
            "downgrade until the third instance. Premature revision is as costly as no revision."
            if (system_signal or inaction_signal or stability_signal) else
            "UPDATE_ON_TWO_POINTS — "
            "two inconsistencies in core behavior (not peripheral) are sufficient signal; "
            "first impressions are optimistic by default — the correction is the more accurate read. "
            "Adjust your model now; do not require a third mistake before protecting yourself."
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
# Multi-DNA collision (3+ organisms)
# ---------------------------------------------------------------------------

def _extract_verdict_from_response(response_text: str) -> str:
    """Extract the decision verdict from a generated response (reusable helper)."""
    lines = [ln.strip() for ln in response_text.strip().splitlines() if ln.strip()]
    for line in lines:
        m = re.match(r"^([A-Z][A-Z_\s]{2,30}?)\s*[—–-]{1,2}\s*(.+)", line)
        if m:
            return m.group(1).strip()
    tokens = re.findall(r"\b[A-Z]{3,}\b", response_text)
    return tokens[-1] if tokens else ""


def run_multi_collision(organisms: list, scenarios: list) -> dict:
    """
    Run all organisms against all scenarios and collect structured results.

    Returns:
        {
            "organisms": [organism_dict, ...],
            "scenarios": [scenario_dict, ...],
            "responses": {(org_idx, scenario_idx): response_dict, ...},
        }
    """
    responses = {}
    for oi, org in enumerate(organisms):
        for si, scenario in enumerate(scenarios):
            resp = generate_response(org, scenario)
            responses[(oi, si)] = resp
    return {
        "organisms": organisms,
        "scenarios": scenarios,
        "responses": responses,
    }


def build_divergence_matrix(collision_data: dict) -> dict:
    """
    Build an NxN divergence matrix across all organism pairs.

    For each pair (i, j), count how many scenarios they diverge on
    (different verdict) vs agree on.

    Returns:
        {
            "names": [name0, name1, ...],
            "matrix": [[{agree, diverge}, ...], ...],  # matrix[i][j]
        }
    """
    organisms = collision_data["organisms"]
    scenarios = collision_data["scenarios"]
    responses = collision_data["responses"]
    n = len(organisms)

    names = [org["name"] for org in organisms]
    matrix = [[None for _ in range(n)] for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = {"agreements": len(scenarios), "divergences": 0}
                continue
            agree = 0
            diverge = 0
            for si in range(len(scenarios)):
                verdict_i = _extract_verdict_from_response(responses[(i, si)]["response"])
                verdict_j = _extract_verdict_from_response(responses[(j, si)]["response"])
                if verdict_i and verdict_j and verdict_i == verdict_j:
                    agree += 1
                else:
                    diverge += 1
            matrix[i][j] = {"agreements": agree, "divergences": diverge}

    return {"names": names, "matrix": matrix}


def identify_consensus_and_outliers(collision_data: dict) -> dict:
    """
    For each scenario, identify:
    - consensus: all organisms reach the same verdict
    - outliers: one organism disagrees with the majority

    Returns:
        {
            "by_scenario": [
                {
                    "scenario_id": int,
                    "domain": str,
                    "verdicts": {name: verdict, ...},
                    "type": "consensus" | "outlier" | "split",
                    "consensus_verdict": str | None,
                    "outlier_name": str | None,
                    "outlier_verdict": str | None,
                    "majority_verdict": str | None,
                },
                ...
            ]
        }
    """
    organisms = collision_data["organisms"]
    scenarios = collision_data["scenarios"]
    responses = collision_data["responses"]
    n = len(organisms)

    results = []
    for si, scenario in enumerate(scenarios):
        verdicts = {}
        for oi, org in enumerate(organisms):
            v = _extract_verdict_from_response(responses[(oi, si)]["response"])
            verdicts[org["name"]] = v if v else "(unclear)"

        # Count verdict frequencies
        verdict_counts = {}
        for name, v in verdicts.items():
            verdict_counts.setdefault(v, []).append(name)

        entry = {
            "scenario_id": scenario["id"],
            "domain": scenario["domain"],
            "verdicts": verdicts,
        }

        if len(verdict_counts) == 1:
            # All agree
            entry["type"] = "consensus"
            entry["consensus_verdict"] = list(verdict_counts.keys())[0]
            entry["outlier_name"] = None
            entry["outlier_verdict"] = None
            entry["majority_verdict"] = entry["consensus_verdict"]
        elif len(verdict_counts) == 2:
            # Check for outlier: one group has exactly 1 member
            sorted_groups = sorted(verdict_counts.items(), key=lambda x: len(x[1]))
            if len(sorted_groups[0][1]) == 1:
                entry["type"] = "outlier"
                entry["outlier_name"] = sorted_groups[0][1][0]
                entry["outlier_verdict"] = sorted_groups[0][0]
                entry["majority_verdict"] = sorted_groups[1][0]
                entry["consensus_verdict"] = None
            else:
                # Even split (e.g., 2v2) — classify as split
                entry["type"] = "split"
                entry["consensus_verdict"] = None
                entry["outlier_name"] = None
                entry["outlier_verdict"] = None
                entry["majority_verdict"] = sorted_groups[1][0]  # larger group
        else:
            # 3+ distinct verdicts — full split
            entry["type"] = "split"
            entry["consensus_verdict"] = None
            entry["outlier_name"] = None
            entry["outlier_verdict"] = None
            # Majority is the most common verdict
            most_common = max(verdict_counts.items(), key=lambda x: len(x[1]))
            entry["majority_verdict"] = most_common[0]

        results.append(entry)

    return {"by_scenario": results}


def _build_multi_cross_pollination(collision_data: dict, consensus_outliers: dict) -> dict:
    """
    For each organism, suggest what it could learn from the group based on
    scenarios where it is an outlier or in the minority.

    Returns: {organism_name: [suggestion_str, ...], ...}
    """
    organisms = collision_data["organisms"]
    responses = collision_data["responses"]
    suggestions = {org["name"]: [] for org in organisms}

    for entry in consensus_outliers["by_scenario"]:
        domain = entry["domain"]

        if entry["type"] == "outlier" and entry["outlier_name"]:
            outlier = entry["outlier_name"]
            majority_v = entry["majority_verdict"]
            outlier_v = entry["outlier_verdict"]
            suggestions[outlier].append(
                f"In {domain}: you chose {outlier_v} while the group consensus was "
                f"{majority_v}. Consider whether the majority perspective reveals a "
                f"blind spot in your framework."
            )
        elif entry["type"] == "split":
            # In a split, each organism in the minority can learn from the majority
            verdicts = entry["verdicts"]
            verdict_counts = {}
            for name, v in verdicts.items():
                verdict_counts.setdefault(v, []).append(name)
            if not verdict_counts:
                continue
            most_common_v, most_common_names = max(
                verdict_counts.items(), key=lambda x: len(x[1])
            )
            for v, names in verdict_counts.items():
                if v != most_common_v:
                    for name in names:
                        suggestions[name].append(
                            f"In {domain}: you chose {v} while the plurality "
                            f"({', '.join(most_common_names)}) chose {most_common_v}. "
                            f"Review their reasoning for potential insights."
                        )

    return suggestions


def generate_multi_collision_report_md(
    collision_data: dict,
    divergence_matrix: dict,
    consensus_outliers: dict,
    cross_pollination: dict,
) -> str:
    """
    Build a structured markdown report for a multi-organism collision.

    Sections:
    1. Header with all organism names
    2. Summary: total scenarios, consensus count, outlier count, split count
    3. NxN Divergence Matrix
    4. Per-scenario breakdown with all organisms' verdicts
    5. Consensus analysis
    6. Outlier identification
    7. Cross-pollination suggestions
    """
    organisms = collision_data["organisms"]
    scenarios = collision_data["scenarios"]
    responses = collision_data["responses"]
    now = datetime.now()
    names = [org["name"] for org in organisms]
    n = len(organisms)

    by_scenario = consensus_outliers["by_scenario"]
    consensus_count = sum(1 for e in by_scenario if e["type"] == "consensus")
    outlier_count = sum(1 for e in by_scenario if e["type"] == "outlier")
    split_count = sum(1 for e in by_scenario if e["type"] == "split")

    lines = []

    # --- Header ---
    names_str = " vs ".join(names)
    lines.append(f"# Multi-Organism Collision Report: {names_str}")
    lines.append("")
    lines.append(f"**Date**: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Organisms**: {n}")
    for i, org in enumerate(organisms):
        lines.append(
            f"**Organism {i+1}**: {org['name']} ({org['filepath']}) "
            f"— {len(org['principles'])} principles"
        )
    lines.append("")

    # --- Summary ---
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Organisms | {n} |")
    lines.append(f"| Total scenarios | {len(scenarios)} |")
    lines.append(f"| Full consensus | {consensus_count} |")
    lines.append(f"| Outlier (1 vs rest) | {outlier_count} |")
    lines.append(f"| Split (no majority) | {split_count} |")
    consensus_pct = (consensus_count / len(scenarios) * 100) if scenarios else 0
    lines.append(f"| Consensus rate | {consensus_pct:.0f}% |")
    lines.append("")

    # --- NxN Divergence Matrix ---
    lines.append("## Divergence Matrix (NxN)")
    lines.append("")
    lines.append(
        "Each cell shows agreements/divergences between the pair across all scenarios."
    )
    lines.append("")

    # Header row
    header = "| | " + " | ".join(names) + " |"
    sep = "|---|" + "|".join(["---"] * n) + "|"
    lines.append(header)
    lines.append(sep)
    matrix = divergence_matrix["matrix"]
    for i, name in enumerate(names):
        row_cells = []
        for j in range(n):
            cell = matrix[i][j]
            if i == j:
                row_cells.append("--")
            else:
                row_cells.append(f"{cell['agreements']}A / {cell['divergences']}D")
        lines.append(f"| {name} | " + " | ".join(row_cells) + " |")
    lines.append("")

    # --- Per-Scenario Breakdown ---
    lines.append("## Per-Scenario Breakdown")
    lines.append("")

    for entry in by_scenario:
        si = entry["scenario_id"] - 1
        scenario = scenarios[si] if si < len(scenarios) else None
        tag = entry["type"].upper()
        domain = entry["domain"].upper()
        lines.append(f"### Scenario {entry['scenario_id']}: {domain} [{tag}]")
        lines.append("")
        if scenario:
            lines.append(f"> {scenario['scenario']}")
            lines.append("")

        for oi, org in enumerate(organisms):
            resp = responses[(oi, si)]
            decision = _extract_decision_line(resp["response"])
            verdict = entry["verdicts"].get(org["name"], "")
            is_outlier = (
                entry["type"] == "outlier" and entry["outlier_name"] == org["name"]
            )
            marker = " **[OUTLIER]**" if is_outlier else ""
            lines.append(f"**{org['name']}**{marker}: {decision}")
            principles_used = resp.get("dna_principles_used", [])
            if principles_used:
                for p in principles_used:
                    lines.append(f"  - {p[:120]}")
            lines.append("")

        lines.append("---")
        lines.append("")

    # --- Consensus Analysis ---
    lines.append("## Consensus Analysis")
    lines.append("")
    consensus_entries = [e for e in by_scenario if e["type"] == "consensus"]
    if consensus_entries:
        lines.append(
            f"All {n} organisms agree on {len(consensus_entries)} scenario(s):"
        )
        lines.append("")
        for e in consensus_entries:
            lines.append(
                f"- **{e['domain'].upper()}**: unanimous verdict = {e['consensus_verdict']}"
            )
        lines.append("")
    else:
        lines.append("No scenarios reached full consensus across all organisms.")
        lines.append("")

    # --- Outlier Identification ---
    lines.append("## Outlier Identification")
    lines.append("")
    outlier_entries = [e for e in by_scenario if e["type"] == "outlier"]
    if outlier_entries:
        lines.append(
            f"{len(outlier_entries)} scenario(s) have a single outlier:"
        )
        lines.append("")
        for e in outlier_entries:
            lines.append(
                f"- **{e['domain'].upper()}**: {e['outlier_name']} chose "
                f"{e['outlier_verdict']} while the rest chose {e['majority_verdict']}"
            )
        lines.append("")

        # Per-organism outlier count
        outlier_counts = {}
        for e in outlier_entries:
            name = e["outlier_name"]
            outlier_counts[name] = outlier_counts.get(name, 0) + 1
        lines.append("**Outlier frequency per organism:**")
        lines.append("")
        for name in names:
            count = outlier_counts.get(name, 0)
            if count > 0:
                lines.append(f"- {name}: {count} time(s)")
        lines.append("")
    else:
        lines.append("No single-outlier scenarios detected.")
        lines.append("")

    # --- Cross-Pollination Suggestions ---
    lines.append("## Cross-Pollination Suggestions")
    lines.append("")
    lines.append("What each organism could learn from the group:")
    lines.append("")

    for name in names:
        lines.append(f"### {name}")
        lines.append("")
        suggestions = cross_pollination.get(name, [])
        if suggestions:
            for s in suggestions:
                lines.append(f"- {s}")
        else:
            lines.append(
                "- Fully aligned with group consensus on all scenarios — "
                "no cross-pollination needed."
            )
        lines.append("")

    # --- Footer ---
    lines.append("---")
    lines.append("")
    lines.append(
        f"*Generated by organism_interact.py multi-collision report | {now.isoformat()}*"
    )

    return "\n".join(lines)


def generate_multi_collision_report_json(
    collision_data: dict,
    divergence_matrix: dict,
    consensus_outliers: dict,
    cross_pollination: dict,
) -> dict:
    """
    Build a machine-readable multi-collision report as a dict.
    """
    organisms = collision_data["organisms"]
    scenarios = collision_data["scenarios"]
    responses = collision_data["responses"]
    now = datetime.now()

    by_scenario = consensus_outliers["by_scenario"]
    consensus_count = sum(1 for e in by_scenario if e["type"] == "consensus")
    outlier_count = sum(1 for e in by_scenario if e["type"] == "outlier")
    split_count = sum(1 for e in by_scenario if e["type"] == "split")

    # Build per-scenario detail with all organisms' responses
    scenario_details = []
    for entry in by_scenario:
        si = entry["scenario_id"] - 1
        scenario = scenarios[si] if si < len(scenarios) else {}
        org_responses = []
        for oi, org in enumerate(organisms):
            resp = responses[(oi, si)]
            org_responses.append({
                "name": org["name"],
                "decision": _extract_decision_line(resp["response"]),
                "verdict": entry["verdicts"].get(org["name"], ""),
                "full_response": resp["response"],
                "principles_used": resp.get("dna_principles_used", []),
            })
        scenario_details.append({
            "scenario_id": entry["scenario_id"],
            "domain": entry["domain"],
            "scenario": scenario.get("scenario", ""),
            "classification": entry["type"],
            "consensus_verdict": entry.get("consensus_verdict"),
            "outlier_name": entry.get("outlier_name"),
            "outlier_verdict": entry.get("outlier_verdict"),
            "majority_verdict": entry.get("majority_verdict"),
            "organism_responses": org_responses,
        })

    # Serialize divergence matrix (replace None with dicts for JSON)
    serial_matrix = []
    for row in divergence_matrix["matrix"]:
        serial_matrix.append([cell if cell else {} for cell in row])

    return {
        "meta": {
            "report_type": "multi_collision",
            "generated_at": now.isoformat(),
            "organism_count": len(organisms),
            "organism_files": [org["filepath"] for org in organisms],
            "protocol_version": "v0.1",
        },
        "summary": {
            "total_scenarios": len(scenarios),
            "consensus": consensus_count,
            "outliers": outlier_count,
            "splits": split_count,
            "consensus_rate": round(
                consensus_count / len(scenarios) * 100, 1
            ) if scenarios else 0,
        },
        "organisms": [
            {
                "name": org["name"],
                "filepath": org["filepath"],
                "principles_extracted": len(org["principles"]),
                "identity": org["identity"],
            }
            for org in organisms
        ],
        "divergence_matrix": {
            "names": divergence_matrix["names"],
            "matrix": serial_matrix,
        },
        "scenarios": scenario_details,
        "cross_pollination": cross_pollination,
    }


def save_multi_collision_report(
    collision_data: dict,
    divergence_matrix: dict,
    consensus_outliers: dict,
    cross_pollination: dict,
    output_dir: str,
) -> tuple:
    """
    Save multi-organism collision report as both markdown and JSON.

    Returns: (md_path, json_path)
    """
    os.makedirs(output_dir, exist_ok=True)

    organisms = collision_data["organisms"]
    name_parts = "_vs_".join(
        re.sub(r"[^\w]", "_", org["name"])[:15] for org in organisms
    )
    # Truncate total filename length to avoid filesystem issues
    if len(name_parts) > 80:
        name_parts = name_parts[:80]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"multi_collision_{name_parts}_{timestamp}"

    md_content = generate_multi_collision_report_md(
        collision_data, divergence_matrix, consensus_outliers, cross_pollination
    )
    md_path = os.path.join(output_dir, f"{base}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    json_data = generate_multi_collision_report_json(
        collision_data, divergence_matrix, consensus_outliers, cross_pollination
    )
    json_path = os.path.join(output_dir, f"{base}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    return md_path, json_path


def print_multi_collision_summary(
    collision_data: dict,
    divergence_matrix: dict,
    consensus_outliers: dict,
    cross_pollination: dict,
) -> None:
    """Print a summary of the multi-organism collision to stdout."""
    organisms = collision_data["organisms"]
    names = [org["name"] for org in organisms]
    n = len(organisms)
    by_scenario = consensus_outliers["by_scenario"]

    print(f"\n{'='*72}")
    print(f"  MULTI-ORGANISM COLLISION: {' vs '.join(names)}")
    print(f"{'='*72}")
    print(f"\n  Organisms: {n}")
    for org in organisms:
        print(f"    - {org['name']} ({len(org['principles'])} principles)")

    # Summary
    consensus_count = sum(1 for e in by_scenario if e["type"] == "consensus")
    outlier_count = sum(1 for e in by_scenario if e["type"] == "outlier")
    split_count = sum(1 for e in by_scenario if e["type"] == "split")
    total = len(by_scenario)
    print(f"\n  Scenarios: {total}")
    print(f"  Full consensus: {consensus_count}")
    print(f"  Outlier (1 vs rest): {outlier_count}")
    print(f"  Split: {split_count}")

    # Divergence matrix
    print(f"\n{'-'*72}")
    print(f"  DIVERGENCE MATRIX")
    print(f"{'-'*72}")
    col_w = max(len(nm) for nm in names) + 2
    header = "".ljust(col_w) + "".join(nm.center(col_w) for nm in names)
    print(f"  {header}")
    matrix = divergence_matrix["matrix"]
    for i, name in enumerate(names):
        row = name.ljust(col_w)
        for j in range(n):
            cell = matrix[i][j]
            if i == j:
                row += "--".center(col_w)
            else:
                row += f"{cell['agreements']}A/{cell['divergences']}D".center(col_w)
        print(f"  {row}")

    # Per-scenario verdicts
    print(f"\n{'-'*72}")
    print(f"  PER-SCENARIO VERDICTS")
    print(f"{'-'*72}")
    for entry in by_scenario:
        tag = entry["type"].upper()
        domain = entry["domain"].upper()
        print(f"\n  [{entry['scenario_id']:2d}] {domain:13s} [{tag}]")
        for name in names:
            verdict = entry["verdicts"].get(name, "?")
            marker = " <-- OUTLIER" if (entry["type"] == "outlier" and entry["outlier_name"] == name) else ""
            print(f"       {name}: {verdict}{marker}")

    # Outliers
    outlier_entries = [e for e in by_scenario if e["type"] == "outlier"]
    if outlier_entries:
        print(f"\n{'-'*72}")
        print(f"  OUTLIER SUMMARY")
        print(f"{'-'*72}")
        for e in outlier_entries:
            print(
                f"  {e['domain'].upper()}: {e['outlier_name']} "
                f"({e['outlier_verdict']}) vs rest ({e['majority_verdict']})"
            )

    # Cross-pollination
    print(f"\n{'-'*72}")
    print(f"  CROSS-POLLINATION SUGGESTIONS")
    print(f"{'-'*72}")
    for name in names:
        suggestions = cross_pollination.get(name, [])
        if suggestions:
            print(f"\n  {name}:")
            for s in suggestions:
                print(f"    - {s}")
        else:
            print(f"\n  {name}: fully aligned with group — no suggestions.")

    print()


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Digital Organism Interaction — decision comparison across two DNA files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("dna_a", nargs="?", default=None,
                        help="Path to DNA file for organism A (markdown)")
    parser.add_argument("dna_b", nargs="?", default=None,
                        help="Path to DNA file for organism B (markdown)")
    parser.add_argument(
        "--multi", nargs="+", metavar="DNA",
        help="Multi-organism collision: 3+ DNA file paths for NxN comparison.",
    )
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

    # -----------------------------------------------------------------------
    # Multi-DNA collision mode (--multi)
    # -----------------------------------------------------------------------
    if args.multi:
        if len(args.multi) < 3:
            print(
                "ERROR: --multi requires 3 or more DNA files. "
                "For 2-file comparison, use positional args instead.",
                file=sys.stderr,
            )
            sys.exit(1)

        # Load all organisms
        organisms = []
        try:
            for dna_path in args.multi:
                print(f"Loading DNA: {dna_path}")
                org = parse_dna(dna_path)
                print(f"  -> {org['name']} | {len(org['principles'])} principles extracted")
                organisms.append(org)
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

        print(f"\nRunning multi-collision: {len(organisms)} organisms x {len(scenarios_to_run)} scenarios...\n")

        # Run collision
        collision_data = run_multi_collision(organisms, scenarios_to_run)

        # Build analysis
        div_matrix = build_divergence_matrix(collision_data)
        consensus_outliers = identify_consensus_and_outliers(collision_data)
        cross_poll = _build_multi_cross_pollination(collision_data, consensus_outliers)

        # Print summary to terminal
        if not args.quiet:
            print_multi_collision_summary(
                collision_data, div_matrix, consensus_outliers, cross_poll
            )

        # Save report if --report
        if args.report:
            md_path, json_path = save_multi_collision_report(
                collision_data, div_matrix, consensus_outliers, cross_poll, output_dir
            )
            print(f"\nMulti-collision report (markdown): {md_path}")
            print(f"Multi-collision report (JSON):     {json_path}")

        sys.exit(0)

    # -----------------------------------------------------------------------
    # Standard 2-DNA collision mode (positional args)
    # -----------------------------------------------------------------------
    if not args.dna_a or not args.dna_b:
        parser.error("the following arguments are required: dna_a, dna_b (or use --multi for 3+ files)")

    # Load DNA files
    try:
        print(f"Loading DNA A: {args.dna_a}")
        organism_a = parse_dna(args.dna_a)
        print(f"  -> {organism_a['name']} | {len(organism_a['principles'])} principles extracted")

        print(f"Loading DNA B: {args.dna_b}")
        organism_b = parse_dna(args.dna_b)
        print(f"  -> {organism_b['name']} | {len(organism_b['principles'])} principles extracted")
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
