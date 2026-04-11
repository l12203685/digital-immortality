# SOP #121+ Proposal — Post-Closure Regime-Shift SOPs

> Note: SOP#121 is already taken (`knowledge_product_121_information_position_calibration_protocol.md`, cycle 319). New proposals are numbered #122 / #123 / #124.

**Status**: DRAFT — awaiting Edward ratification
**Created**: 2026-04-11T UTC (cycle 321 candidate)
**Rationale**: SOP#01~#121 closed-world milestone achieved (distil110 I2). New SOPs should mark regime-shifts or newly-emerged failure modes, not gap-fill the existing taxonomy. Three genuine gaps identified after reviewing distil100-121 and today's audit.

---

## Proposed New SOPs

### SOP #122 — Gate-Constrained Regime Operating Protocol
**Essence**: When every automatable lever is pulled and only human-gated actions remain, the agent must reallocate from "build capability" to "lower human activation energy".
**File**: `docs/knowledge_product_122_gate_constrained_regime_operating_protocol.md`
**Readiness**: DRAFT-READY — no Edward input required to ratify
**Gaps it closes**: Item 4 (distil112 I3, distil114 I1, distil116 I1, distil117 I3, distil118 I2, distil119 I2 — all observed this regime but no SOP codified it)
**Relationship to existing SOPs**:
- Related to SOP#121 (Information Position Calibration) — SOP#121 is the theoretical frame (position determines range), SOP#122 is the operational frame (what to DO from late position)
- Related to SOP#119 (Path Closure) — SOP#119 handles CLOSED paths, SOP#122 handles SLOW/GATED paths
- Not a duplicate: SOP#121 says "act from position"; SOP#122 says "when all positions are worst-position and only Edward can act, prep his action to be cheap"

---

### SOP #123 — Daemon / Human-Session Coordination Protocol
**Essence**: Division of labor: daemon = leaf-append writes; human session = structural/source/commit writes. Pre-flight via git diff, classify writes before executing, route daemon structural needs through a request channel.
**File**: `docs/knowledge_product_123_daemon_human_session_coordination_protocol.md`
**Readiness**: DRAFT-READY — no Edward input required to ratify
**Gaps it closes**: Item 5 (cold-start agent + daemon collision). Four distils (114 I3, 116 I3, 118 I3, 119 I3) + distil121 I1 all observed pieces but no SOP integrated them.
**Relationship to existing SOPs**:
- Related to SOP#108 (Cold-start drift detection) — SOP#108 DETECTS drift, SOP#123 PREVENTS drift via a coordination protocol
- Related to SOP#117 (DNA Core Audit) — audit protocol for DNA; SOP#123 is audit protocol for code/structural writes
- Not a duplicate: No existing SOP codifies the write taxonomy or daemon-request channel. Creates a new `staging/daemon_requests.md` primitive.

---

### SOP #124 — Kill-Window State Persistence Protocol
**Essence**: All strategy state that feeds kill/reactivation decisions MUST be durable + reloaded on process start. In-memory state is a cache, never source of truth. `kill_window_floor` must be > 0 to avoid absorbing state.
**File**: `docs/knowledge_product_124_kill_window_state_persistence_protocol.md`
**Readiness**: DRAFT-READY — codifies the fix from today's audit (commit `c29865a`, ReactivationGate). Edward may want to adjust specific thresholds but structure is correct.
**Gaps it closes**: Item 1 (Restart-loop bug). SOP#118 is about the gate logic ABOVE the state layer; SOP#109 is about gate criteria; NEITHER covers the in-memory-dict-wiped-on-restart failure mode that caused DualMA to be killed 4x in 48h.
**Relationship to existing SOPs**:
- Related to SOP#118 (DualMA Reactivation) — SOP#118 operates ABOVE the state layer, SOP#124 makes that state layer durable. SOP#118 gates can't work if state doesn't persist.
- Related to SOP#109 (Strategy Re-Activation Gate) — gate criteria vs state durability; different layers
- Related to SOP#96 (Mainnet Revenue Go-Live) — SOP#124 is a mainnet gate prerequisite
- Not a duplicate: SOP#118 explicitly assumes `disabled` dict is persistent (line 130: "remove it from the disabled dict") — the assumption was wrong and unverified until today. SOP#124 enforces the assumption.

---

## Items Evaluated & NOT Proposed

| Item | Reason |
|---|---|
| Two-tracker divergence (item 2) | SOP#120 does NOT cover this (SOP#120 is about negotiation root-variable confirmation). But distil116-118 "information-vs-authorization" pattern is now captured in proposed SOP#122 G0 (regime classification distinguishes info-tracker from authorization-tracker). Creating a separate SOP would duplicate SOP#122. |
| Concentration / orthogonality (item 3) | Parallel sub-agent is currently implementing the orthogonality filter; let that work finish first. If the filter fails to close the gap, revisit as SOP#125 candidate. Not ready to codify. |
| Subagent permission collision (item 6) | User explicitly marked skip (not permanent SOP-worthy) |
| Discord communication streaming (item 7) | User explicitly marked behavioral feedback, not SOP-worthy; already in memory |

---

## Edward Ratification Step

If approved, single command to commit all three + this proposal:

```bash
cd C:/Users/admin/workspace/digital-immortality && \
  git add docs/knowledge_product_122_gate_constrained_regime_operating_protocol.md \
          docs/knowledge_product_123_daemon_human_session_coordination_protocol.md \
          docs/knowledge_product_124_kill_window_state_persistence_protocol.md \
          staging/sop_121_plus_proposal.md && \
  git commit -m "feat: ratify SOP#122-#124 (gate-constrained regime, daemon-human coord, kill-window persistence)" && \
  git push
```

After ratification, update `memory/recursive_distillation.md` to mark `SOP#01~#124 series extended` and adjust `distil110 I2` closure reference.

---

## Changes Required if Any SOP is Rejected

- **Reject SOP#122**: revisit item 4 as a pure memory note (not SOP); update proposal
- **Reject SOP#123**: delete file; revert to ad-hoc session discipline; revisit when next collision happens
- **Reject SOP#124**: **DO NOT** — this one is already fixed in code (commit `c29865a`); rejecting the SOP means the fix has no documentation layer, leaving a regression risk. If anything is wrong with SOP#124, edit the thresholds, don't reject.

---

## Files Touched (not yet committed)

- `docs/knowledge_product_122_gate_constrained_regime_operating_protocol.md` (new, ~210 lines)
- `docs/knowledge_product_123_daemon_human_session_coordination_protocol.md` (new, ~215 lines)
- `docs/knowledge_product_124_kill_window_state_persistence_protocol.md` (new, ~235 lines)
- `staging/sop_121_plus_proposal.md` (this file)
