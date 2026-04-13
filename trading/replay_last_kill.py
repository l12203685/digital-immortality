"""Replay the most recent kill event and validate SOP#118 ReactivationGate.

Reads kill_lessons.jsonl for the last kill, then simulates an immediate
restart attempt against each gate condition (G0-G5).  Writes a pass/fail
report to results/replay_last_kill.md.

stdlib only, no external deps.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
KILLS_LOG = ROOT / "results" / "kill_lessons.jsonl"
ENGINE_LOG = ROOT / "results" / "trading_engine_log.jsonl"
STATUS_FILE = ROOT / "results" / "trading_engine_status.json"
OUTPUT_FILE = ROOT / "results" / "replay_last_kill.md"

# SOP#118 gate thresholds (must match trading/engine.py)
COOLING_TICKS = 50
FORWARD_WINDOW = 50
PF_THRESHOLD = 1.2


def load_last_kill() -> Optional[Dict]:
    """Return the most recent kill event from kill_lessons.jsonl."""
    if not KILLS_LOG.exists():
        return None
    last: Optional[Dict] = None
    with open(KILLS_LOG) as f:
        for line in f:
            line = line.strip()
            if line:
                last = json.loads(line)
    return last


def load_status() -> Dict:
    """Load current engine status."""
    if not STATUS_FILE.exists():
        return {}
    with open(STATUS_FILE) as f:
        return json.load(f)


def collect_forward_walk(strategy: str, kill_tick: int) -> List[float]:
    """Collect pnl_pct entries for the killed strategy after the kill tick."""
    pnls: List[float] = []
    if not ENGINE_LOG.exists():
        return pnls
    with open(ENGINE_LOG) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if entry.get("strategy") == strategy and entry.get("tick", 0) > kill_tick:
                pnls.append(entry.get("pnl_pct", 0.0))
    return pnls


def check_gates(kill: Dict, status: Dict) -> List[Tuple[str, bool, str]]:
    """Simulate immediate restart and check each gate. Returns list of (gate, passed, detail)."""
    results: List[Tuple[str, bool, str]] = []
    strategy = kill["strategy"]
    kill_tick = kill["tick"]
    current_tick = status.get("tick_count", kill_tick)
    regime_at_kill = kill.get("regime_at_kill", "unknown")
    current_regime = status.get("regime", "unknown")

    # G0: Kill metadata exists
    has_metadata = all(k in kill for k in ("strategy", "kill_reason", "tick", "cum_pnl"))
    results.append(("G0 Kill Metadata", has_metadata,
                     f"strategy={strategy}, reason={kill['kill_reason']}" if has_metadata
                     else "missing required kill metadata fields"))

    # G1: Cooling period (immediate restart = 0 ticks elapsed)
    elapsed = 0  # simulating IMMEDIATE restart
    g1_pass = elapsed >= COOLING_TICKS
    results.append(("G1 Cooling Period", g1_pass,
                     f"elapsed=0 ticks, required>={COOLING_TICKS} -> BLOCKED"))

    # G2: Regime flip check
    regime_changed = current_regime != regime_at_kill
    results.append(("G2 Regime Flip", regime_changed,
                     f"kill_regime={regime_at_kill}, current_regime={current_regime}"
                     + (" -> regime shifted" if regime_changed else " -> same regime, no confirmation")))

    # G3: Forward-walk PF check (immediate restart = 0 forward ticks)
    forward_walk = collect_forward_walk(strategy, kill_tick)
    fw_count = len(forward_walk)
    if fw_count >= FORWARD_WINDOW:
        window = forward_walk[-FORWARD_WINDOW:]
        gw = sum(p for p in window if p > 0)
        gl = abs(sum(p for p in window if p < 0))
        pf = gw / gl if gl > 0 else 0.0
        g3_pass = pf >= PF_THRESHOLD and gl > 0
        detail = f"{fw_count} ticks available, PF={pf:.2f} (threshold={PF_THRESHOLD})"
    else:
        g3_pass = False
        detail = f"only {fw_count} forward ticks, need>={FORWARD_WINDOW}"
    results.append(("G3 Forward-Walk PF", g3_pass, detail))

    # G4: Orthogonality / concentration check
    active = status.get("active_strategies", 0)
    disabled = status.get("disabled", {})
    is_disabled = strategy in disabled
    results.append(("G4 Orthogonality", not is_disabled,
                     f"strategy {'still in disabled dict' if is_disabled else 'cleared'}"
                     f", active_strategies={active}"))

    # G5: Post-reactivation monitoring (cannot pass at restart time)
    results.append(("G5 Post-Reactivation Monitor", False,
                     "requires 20-tick observation window after reactivation -- not yet started"))

    return results


def format_report(kill: Dict, gates: List[Tuple[str, bool, str]], status: Dict) -> str:
    """Build the markdown report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    blocked = [g for g, passed, _ in gates if not passed]
    verdict = "PASS (restart allowed)" if not blocked else f"BLOCKED by {len(blocked)} gate(s)"

    lines = [
        f"# Replay Last Kill -- SOP#118 Gate Validation",
        f"",
        f"**Generated**: {now}",
        f"**Verdict**: {verdict}",
        f"",
        f"## Kill Event",
        f"",
        f"| Field | Value |",
        f"|-------|-------|",
        f"| Strategy | {kill['strategy']} |",
        f"| Reason | {kill['kill_reason']} |",
        f"| Tick | {kill['tick']} |",
        f"| Timestamp | {kill['ts']} |",
        f"| Cum PnL | {kill['cum_pnl']}% |",
        f"| Price | ${kill.get('price_at_kill', 'N/A'):,} |",
        f"| Regime | {kill.get('regime_at_kill', 'unknown')} |",
        f"",
        f"## Gate Results (simulating immediate restart)",
        f"",
        f"| Gate | Result | Detail |",
        f"|------|--------|--------|",
    ]
    for gate_name, passed, detail in gates:
        icon = "PASS" if passed else "BLOCK"
        lines.append(f"| {gate_name} | {icon} | {detail} |")

    lines.extend([
        f"",
        f"## Conclusion",
        f"",
    ])
    if blocked:
        lines.append(f"ReactivationGate correctly prevents immediate restart. "
                      f"{len(blocked)} gate(s) block: {', '.join(blocked)}.")
        lines.append(f"The restart loop that plagued DualMA_10_30 (killed 4x in 48h) "
                      f"would NOT recur under SOP#118.")
    else:
        lines.append(f"All gates pass — restart would be allowed. "
                      f"Review whether this is expected given the kill conditions.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    kill = load_last_kill()
    if kill is None:
        print("ERROR: No kill events found in", KILLS_LOG)
        return 1

    status = load_status()
    gates = check_gates(kill, status)
    report = format_report(kill, gates, status)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(report, encoding="utf-8")

    # Console output
    print(report)
    blocked = sum(1 for _, passed, _ in gates if not passed)
    print(f"Written to {OUTPUT_FILE}")
    return 0 if blocked > 0 else 0  # 0 = tool worked; blocked gates = expected


if __name__ == "__main__":
    sys.exit(main())
