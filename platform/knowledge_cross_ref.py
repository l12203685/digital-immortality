"""Cross-reference new knowledge with existing DNA."""
from __future__ import annotations

import os
import sys
from pathlib import Path

# WSL-safe path translation: Windows C:/ paths resolve to /mnt/c/ under WSL.
IS_WSL = (sys.platform == "linux" and os.path.exists("/mnt/c"))


def _win_to_posix(p: str) -> str:
    """Translate Windows drive paths to /mnt/<drive>/ under WSL."""
    if not IS_WSL or not p:
        return p
    q = p.replace("\\", "/")
    if len(q) >= 2 and q[1] == ":" and q[0].isalpha():
        return f"/mnt/{q[0].lower()}{q[2:]}"
    return q


DNA_PATH = Path(_win_to_posix("C:/Users/admin/LYH/agent/dna_core.md"))
TRADING_MD = Path(_win_to_posix("C:/Users/admin/LYH/systems/trading.md"))


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
