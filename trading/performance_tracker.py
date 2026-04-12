"""Rolling performance metrics for the trading engine."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

RESULTS = Path("C:/Users/admin/workspace/digital-immortality/results")

def load_paper_log(strategy_type: str = "dual_ma") -> list[dict]:
    """Load paper trading log entries."""
    log_path = RESULTS / f"paper_{strategy_type}.jsonl"
    if not log_path.exists():
        return []
    entries = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries

def compute_rolling_sharpe(pnl_series: list[float], window: int = 50) -> float:
    """Compute rolling Sharpe ratio over the last N entries."""
    if len(pnl_series) < 2:
        return 0.0
    recent = pnl_series[-window:]
    if len(recent) < 2:
        return 0.0
    import statistics
    mean = statistics.mean(recent)
    std = statistics.stdev(recent)
    if std == 0:
        return 0.0
    # Annualize assuming daily returns
    return (mean / std) * (252 ** 0.5)

def compute_edge_ratio(trades: list[dict]) -> dict:
    """Compute MAE/MFE edge ratio from closed trades."""
    if not trades:
        return {"edge_ratio": 0, "avg_mae": 0, "avg_mfe": 0}

    maes = [t.get("mae", 0) for t in trades if "mae" in t]
    mfes = [t.get("mfe", 0) for t in trades if "mfe" in t]

    avg_mae = sum(maes) / len(maes) if maes else 0
    avg_mfe = sum(mfes) / len(mfes) if mfes else 0

    edge_ratio = avg_mfe / abs(avg_mae) if avg_mae != 0 else 0
    return {"edge_ratio": round(edge_ratio, 3), "avg_mae": round(avg_mae, 4), "avg_mfe": round(avg_mfe, 4)}

def compute_strategy_summary(status_path: Optional[Path] = None) -> dict:
    """Compute summary metrics from trading_engine_status.json."""
    if status_path is None:
        status_path = RESULTS / "trading_engine_status.json"
    if not status_path.exists():
        return {"error": "Status file not found"}

    data = json.loads(status_path.read_text(encoding="utf-8"))

    summary = {
        "tick": data.get("tick", 0),
        "total_pnl_pct": data.get("total_pnl_pct", 0),
        "active_strategies": sum(1 for s in data.get("strategies", {}).values() if s.get("active")),
        "disabled_strategies": sum(1 for s in data.get("strategies", {}).values() if not s.get("active")),
        "total_kills": data.get("total_kills", 0),
        "kill_window": data.get("kill_window", 0),
        "regime": data.get("regime", "unknown"),
    }

    # Per-strategy PnL
    strategy_pnls = {}
    for name, s in data.get("strategies", {}).items():
        if s.get("active"):
            strategy_pnls[name] = {
                "pnl_pct": s.get("pnl_pct", 0),
                "trades": s.get("trade_count", 0),
                "signal": s.get("signal", "FLAT"),
            }
    summary["strategy_details"] = strategy_pnls

    return summary

def check_phase_gate() -> dict:
    """Check Phase 1 pass criteria."""
    status = compute_strategy_summary()

    gate = {
        "clean_ticks_500": status.get("tick", 0) >= 500,
        "kill_window_50": status.get("kill_window", 0) >= 50,
        "strategies_with_trades": sum(
            1 for s in status.get("strategy_details", {}).values()
            if s.get("trades", 0) >= 5
        ) >= 3,
        "pnl_positive": status.get("total_pnl_pct", 0) > 0,
        "no_strategy_below_neg5": all(
            s.get("pnl_pct", 0) > -5
            for s in status.get("strategy_details", {}).values()
        ),
    }
    gate["all_pass"] = all(gate.values())
    gate["status"] = status
    return gate


if __name__ == "__main__":
    print("=== Trading Performance Summary ===\n")
    summary = compute_strategy_summary()
    print(f"Tick: {summary.get('tick', '?')}")
    print(f"Total PnL: {summary.get('total_pnl_pct', '?')}%")
    print(f"Active: {summary.get('active_strategies', '?')}, Disabled: {summary.get('disabled_strategies', '?')}")
    print(f"Kill window: {summary.get('kill_window', '?')}")
    print(f"Regime: {summary.get('regime', '?')}")

    print("\n=== Phase 1 Gate Check ===\n")
    gate = check_phase_gate()
    for criterion, passed in gate.items():
        if criterion in ("status", "all_pass"):
            continue
        print(f"  {'PASS' if passed else 'FAIL'}: {criterion}")
    print(f"\n  Overall: {'GO' if gate['all_pass'] else 'NO-GO'}")
