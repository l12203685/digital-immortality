"""Structured cycle protocol dataclasses for the 永生樹 recursive engine."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo
import json

TPE = ZoneInfo("Asia/Taipei")


@dataclass(frozen=True)
class BranchAction:
    branch: int
    name: str
    action: str
    priority: int
    runnable: str  # "llm" | "script" | "read-only"


@dataclass(frozen=True)
class TreeUpdate:
    branch: int
    field: str  # "derivative" | "health" | "last_cycle" | "key_metric"
    value: str


@dataclass(frozen=True)
class CyclePlan:
    branch_actions: tuple[BranchAction, ...]
    tree_updates: tuple[TreeUpdate, ...]
    classification: str  # "root-growth" | "branch-growth" | "neither"


@dataclass
class CycleState:
    cycle_num: int
    timestamp: str
    last_output: str
    tree_state: str
    daemon_log_tail: str
    priority_suggestion: str
    voice_input: str
    trading_status: Optional[dict] = None
    l3_recovery: str = ""

    @classmethod
    def gather(cls, repo_root: Path, cycle_num: int) -> "CycleState":
        """Gather all state sources into a CycleState."""
        def _read(p: Path, limit: int = 3000) -> str:
            if p.exists():
                text = p.read_text(encoding="utf-8", errors="replace")
                return text[-limit:] if len(text) > limit else text
            return ""

        # Trading status
        ts_path = repo_root / "results" / "trading_engine_status.json"
        trading = None
        if ts_path.exists():
            try:
                trading = json.loads(ts_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        # Voice input
        voice_path = Path("C:/Users/admin/GoogleDrive/staging/voice_input.md")
        voice = ""
        if voice_path.exists():
            voice = _read(voice_path, 1000)

        return cls(
            cycle_num=cycle_num,
            timestamp=datetime.now(TPE).isoformat(timespec="seconds"),
            last_output=_read(repo_root / "staging" / "last_output.md"),
            tree_state=_read(repo_root / "results" / "dynamic_tree.md", 5000),
            daemon_log_tail=_read(repo_root / "results" / "daemon_log.md", 1500),
            priority_suggestion=_read(
                repo_root / "results" / "daemon_next_priority.txt", 500,
            ),
            voice_input=voice,
            trading_status=trading,
            l3_recovery=_read(
                repo_root / "staging" / "l3_recovery.md", 800,
            ),
        )

    def to_prompt(self) -> str:
        """Format state as structured prompt for the PLAN step."""
        parts = [
            f"## Cycle {self.cycle_num} — {self.timestamp}",
            f"\n### Previous Output\n{self.last_output[:2000]}",
            f"\n### Tree State\n{self.tree_state}",
        ]
        if self.trading_status:
            parts.append(
                f"\n### Trading\n"
                f"{json.dumps(self.trading_status, indent=2)[:1000]}"
            )
        if self.voice_input:
            parts.append(f"\n### Voice Input\n{self.voice_input}")
        if self.priority_suggestion:
            parts.append(
                f"\n### Suggested Priority\n{self.priority_suggestion}"
            )
        if self.l3_recovery:
            parts.append(
                f"\n### L3 Recovery Signal\n{self.l3_recovery}"
            )
        return "\n".join(parts)


def parse_cycle_plan(raw_json: str) -> CyclePlan:
    """Parse LLM JSON output into a CyclePlan."""
    data = json.loads(raw_json)
    actions = tuple(
        BranchAction(
            branch=a.get("branch", 0),
            name=a.get("name", ""),
            action=a.get("action", ""),
            priority=a.get("priority", 99),
            runnable=a.get("runnable", "read-only"),
        )
        for a in data.get("branch_actions", [])
    )
    updates = tuple(
        TreeUpdate(
            branch=u.get("branch", 0),
            field=u.get("field", ""),
            value=u.get("value", ""),
        )
        for u in data.get("tree_updates", [])
    )
    return CyclePlan(
        branch_actions=actions,
        tree_updates=updates,
        classification=data.get("classification", "neither"),
    )
