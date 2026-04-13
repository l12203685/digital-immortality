# Replay Last Kill — SOP#118 Gate Validation

**Generated**: 2026-04-13 20:03 UTC
**Verdict**: BLOCKED by 4 gate(s)

## Kill Event

| Field | Value |
|-------|-------|
| Strategy | DualMA_RSI |
| Reason | PF 0.78 < 0.8 |
| Tick | 1268 |
| Timestamp | 2026-04-13T18:00:22.047781+00:00 |
| Cum PnL | 0.0791% |
| Price | $72,094.27 |
| Regime | mixed |

## Gate Results (simulating immediate restart)

| Gate | Result | Detail |
|------|--------|--------|
| G0 Kill Metadata | PASS | strategy=DualMA_RSI, reason=PF 0.78 < 0.8 |
| G1 Cooling Period | BLOCK | elapsed=0 ticks, required>=50 -> BLOCKED |
| G2 Regime Flip | BLOCK | kill_regime=mixed, current_regime=mixed -> same regime, no confirmation |
| G3 Forward-Walk PF | PASS | 81 ticks available, PF=2.74 (threshold=1.2) |
| G4 Orthogonality | BLOCK | strategy still in disabled dict, active_strategies=12 |
| G5 Post-Reactivation Monitor | BLOCK | requires 20-tick observation window after reactivation — not yet started |

## Conclusion

ReactivationGate correctly prevents immediate restart. 4 gate(s) block: G1 Cooling Period, G2 Regime Flip, G4 Orthogonality, G5 Post-Reactivation Monitor.
The restart loop that plagued DualMA_10_30 (killed 4x in 48h) would NOT recur under SOP#118.
