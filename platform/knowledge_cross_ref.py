"""Cross-reference new knowledge with existing DNA."""
from __future__ import annotations

from pathlib import Path

DNA_PATH = Path("C:/Users/admin/LYH/agent/dna_core.md")
TRADING_MD = Path("C:/Users/admin/LYH/systems/trading.md")


def cross_reference(insight: str) -> str:
    """Compare insight with DNA content.

    Returns: 'CONFIRM' | 'NEW' | 'CONTRADICT' | 'IRRELEVANT'
    """
    dna_text = ""
    if DNA_PATH.exists():
        dna_text = DNA_PATH.read_text(encoding="utf-8", errors="replace").lower()

    trading_text = ""
    if TRADING_MD.exists():
        trading_text = TRADING_MD.read_text(encoding="utf-8", errors="replace").lower()

    combined = dna_text + "\n" + trading_text
    insight_lower = insight.lower()

    # Simple keyword matching (LLM-based cross-ref would be in daemon cycle)
    # This is a lightweight pre-filter
    trading_keywords = [
        "strategy",
        "trade",
        "position",
        "risk",
        "pnl",
        "stop",
        "entry",
        "exit",
        "策略",
        "交易",
        "部位",
        "風險",
        "停損",
        "進場",
        "出場",
    ]

    is_trading_related = any(kw in insight_lower for kw in trading_keywords)
    has_overlap = any(
        word in combined for word in insight_lower.split() if len(word) > 4
    )

    if not is_trading_related and not has_overlap:
        return "IRRELEVANT"
    elif has_overlap:
        return "CONFIRM"
    else:
        return "NEW"
