"""Branch-specific executors for the daemon cycle."""
from pathlib import Path
from typing import Callable
import json

RESULTS = Path("C:/Users/admin/workspace/digital-immortality/results")


def execute_economic() -> str:
    """Branch 1: Read trading engine status, summarize."""
    status_path = RESULTS / "trading_engine_status.json"
    if not status_path.exists():
        return "Trading engine status file not found."
    data = json.loads(status_path.read_text(encoding="utf-8"))
    return (
        f"Tick {data.get('tick', '?')}, "
        f"PnL {data.get('total_pnl_pct', '?')}%, "
        f"signal {data.get('signal', '?')}"
    )


def execute_behavioral() -> str:
    """Branch 2: Check consistency test status."""
    scorecard = RESULTS / "consistency_scorecard.json"
    if scorecard.exists():
        data = json.loads(scorecard.read_text(encoding="utf-8"))
        return (
            f"Consistency: {data.get('aligned', '?')}/"
            f"{data.get('total', '?')} aligned, "
            f"streak {data.get('clean_streak', '?')}"
        )
    return "No consistency scorecard found."


def execute_learning() -> str:
    """Branch 3: Check distillation progress."""
    distil = RESULTS.parent / "memory" / "recursive_distillation.md"
    if distil.exists():
        lines = distil.read_text(
            encoding="utf-8", errors="replace",
        ).splitlines()
        return f"Distillation: {len(lines)} lines total"
    return "No distillation file found."


def execute_knowledge() -> str:
    """Branch 7: Check knowledge digestion progress."""
    state_path = RESULTS / "digestion_state.json"
    if state_path.exists():
        data = json.loads(state_path.read_text(encoding="utf-8"))
        return (
            f"Knowledge digestion: {data.get('files_digested', 0)}/"
            f"{data.get('total_files_known', '?')} files"
        )
    return "Knowledge digester not initialized."


BRANCH_EXECUTORS: dict[int, Callable[[], str]] = {
    1: execute_economic,
    2: execute_behavioral,
    3: execute_learning,
    7: execute_knowledge,
}
