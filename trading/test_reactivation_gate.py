"""Unit tests for SOP#118 ReactivationGate (trading/engine.py)."""
from trading.engine import ReactivationGate


def _build_walk(pnls):
    meta = {"killed_at_tick": 0, "forward_walk_ticks": []}
    gate = ReactivationGate()
    for p in pnls:
        meta = gate.record_forward_walk(meta, p)
    return gate, meta


def test_cooling_period_blocks_early_reactivation():
    gate = ReactivationGate(cooling_ticks=50, forward_window=50)
    meta = gate.kill_metadata("dualma", "PF 0.70 < 0.8", tick=10,
                              cum_pnl=-0.04, pf_at_kill=0.70)
    # Fresh kill, no forward walk yet, only 30 ticks since kill
    assert gate.check_reactivation("dualma", meta, current_tick=40) is None


def test_cooling_elapsed_but_insufficient_forward_window():
    gate = ReactivationGate(cooling_ticks=50, forward_window=50)
    meta = gate.kill_metadata("dualma", "PF 0.70", tick=0,
                              cum_pnl=0.0, pf_at_kill=0.70)
    # Only 20 forward ticks recorded — below forward_window=50
    for _ in range(20):
        meta = gate.record_forward_walk(meta, 0.5)
    assert gate.check_reactivation("dualma", meta, current_tick=100) is None


def test_forward_pf_below_threshold_blocks():
    gate, meta = _build_walk([0.5] * 25 + [-0.6] * 25)  # PF ≈ 0.83
    meta["killed_at_tick"] = 0
    assert gate.check_reactivation("dualma", meta, current_tick=100) is None


def test_forward_pf_above_threshold_passes():
    gate, meta = _build_walk([0.6] * 30 + [-0.4] * 20)  # PF = 18/8 = 2.25
    meta["killed_at_tick"] = 0
    result = gate.check_reactivation("dualma", meta, current_tick=100)
    assert result is not None
    assert "G3 pass" in result


def test_degenerate_estimator_blocked_no_losses():
    """distil109 I1: PF=inf from 0 losses must NOT pass reactivation."""
    gate, meta = _build_walk([0.1] * 50)  # all wins, no losses
    meta["killed_at_tick"] = 0
    assert gate.check_reactivation("dualma", meta, current_tick=100) is None


def test_manual_override_passes_immediately():
    gate = ReactivationGate()
    meta = gate.kill_metadata("dualma", "PF 0.70", tick=0,
                              cum_pnl=0.0, pf_at_kill=0.70)
    meta["manually_overridden"] = True
    assert gate.check_reactivation("dualma", meta, current_tick=1) == "manual_override"


def test_forward_walk_window_is_rolling():
    """Only last forward_window ticks should count toward PF."""
    gate = ReactivationGate(cooling_ticks=5, forward_window=10)
    meta = gate.kill_metadata("dualma", "PF 0.70", tick=0,
                              cum_pnl=0.0, pf_at_kill=0.70)
    # Start with 10 bad ticks
    for _ in range(10):
        meta = gate.record_forward_walk(meta, -0.5)
    # Then 10 mixed-positive ticks (7 wins, 3 losses; PF = 4.2/1.2 = 3.5)
    for _ in range(7):
        meta = gate.record_forward_walk(meta, 0.6)
    for _ in range(3):
        meta = gate.record_forward_walk(meta, -0.4)
    assert len(meta["forward_walk_ticks"]) == 10
    result = gate.check_reactivation("dualma", meta, current_tick=100)
    assert result is not None


def test_kill_metadata_shape():
    gate = ReactivationGate()
    meta = gate.kill_metadata("dualma", "PF 0.70 < 0.8", tick=64,
                              cum_pnl=-0.039, pf_at_kill=0.70)
    assert meta["killed_at_tick"] == 64
    assert meta["pf_at_kill"] == 0.70
    assert meta["cum_pnl_at_kill"] == -0.039
    assert meta["reentry_size_scale"] == 0.5
    assert meta["manually_overridden"] is False
    assert meta["forward_walk_ticks"] == []


if __name__ == "__main__":
    test_cooling_period_blocks_early_reactivation()
    test_cooling_elapsed_but_insufficient_forward_window()
    test_forward_pf_below_threshold_blocks()
    test_forward_pf_above_threshold_passes()
    test_degenerate_estimator_blocked_no_losses()
    test_manual_override_passes_immediately()
    test_forward_walk_window_is_rolling()
    test_kill_metadata_shape()
    print("All ReactivationGate tests passed")
