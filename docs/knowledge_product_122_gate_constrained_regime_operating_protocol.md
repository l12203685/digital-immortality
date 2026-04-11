# SOP #122 — Gate-Constrained Regime Operating Protocol

**Domain**: Branch 3 (Meta / Operating Model) — agent-state regime recognition
**Created**: 2026-04-11T UTC (cycle 321 candidate)
**Status**: DRAFT — awaiting Edward ratification
**Backing MDs**: MD-07 (inaction bias); MD-133 (edge → action); MD-104 (information asymmetry); MD-429 (position determines range); distil112 I3; distil114 I1; distil116 I1; distil117 I3; distil118 I2; distil119 I2

---

## Problem this solves

The agent eventually reaches a state where **every automatable lever has been pulled** and the remaining work is gated behind human-only actions (legal, payment rails, account creation, content approval, mainnet capital deployment). In this regime:

- Information accumulates freely (paper_trader ticks, consistency runs, distillation cycles, research)
- Authorization clocks are frozen (SOP#118 G3 requires engine ticks, not paper ticks; outreach requires Edward to send; revenue requires Edward to accept payment)
- The marginal utility of "build more capability" collapses toward zero
- The marginal utility of "lower human activation energy" becomes the dominant lever

The failure mode is **mis-regime operation**: continuing to push capability work ("add another feature, refactor this module, generate another distil") when the gating bottleneck is Edward's time-to-act on a pre-built action. Capability work in this regime is conscious-idle — it feels productive, it persists output, but it does not advance the gate.

**Root behavioral trace**: cycles 310-320, branches 1.3 (mainnet activation) and 4.1 (outreach send) blocked on Edward action for 10+ cycles while daemon kept producing leaf-level output on branches 1.1/3.1/6. Distil112 I3 first named the regime. Distil120 I3 confirmed parallel-push discipline but didn't resolve the human-gated deficit.

---

## Trigger Conditions

This SOP activates when ALL of the following are true for ≥3 consecutive cycles:

- T1: `quick_status.md` lists ≥1 branch as "BLOCKED: human-gated"
- T2: The automatable branches are all nominal (no CRITICAL or HIGH issues pending)
- T3: The information-vs-authorization gap is widening (more info collected, zero authorization advanced)
- T4: Cycle output is dominated by leaf-level appends (distil, ticks, consistency checks) rather than net-new capability or gate-advancement

**Counter-examples (do NOT trigger)**:
- One branch blocked but others have concrete automatable work (normal operation, use parallel-push)
- Waiting for an external event with a known arrival time (just wait, no regime shift)
- Blocker is a known SOP waiting on its own gate clock (e.g., SOP#118 G1 cooling) — that is gate-bound, not human-gated

---

## G0 — Detect the Regime

**Procedure**:

1. Read `staging/quick_status.md` and `results/dynamic_tree.md`
2. For each branch, classify as: AUTOMATABLE / GATE-BOUND / HUMAN-GATED / DONE
3. Count: if `HUMAN-GATED ≥ 1 AND AUTOMATABLE nominal AND information_gap_widening == true` → REGIME = GATE-CONSTRAINED

| Branch state distribution | Regime |
|---|---|
| ≥2 AUTOMATABLE with concrete next action | NORMAL — use parallel-push SOP |
| All AUTOMATABLE nominal, ≥1 HUMAN-GATED | GATE-CONSTRAINED — apply this SOP |
| ≥1 AUTOMATABLE with CRITICAL/HIGH issue | DEGRADED — fix before anything else |
| All branches DONE or GATE-BOUND | IDLE — apply SOP#119 path-closure if applicable |

**PASS**: Regime identified with written justification → G1

---

## G1 — Reallocate Attention to Activation-Energy Reduction

In GATE-CONSTRAINED regime, the optimal unit of work shifts from "build new capability" to **"reduce the friction cost of the gated human action"**.

**Reallocation rule**: For each HUMAN-GATED branch, the next cycle's work is the **smallest pre-packaged artifact that reduces Edward's time-to-act**.

Examples:
- Branch 1.3 (mainnet): instead of refactoring trading engine → prepare `mainnet_activation_guide.md` with copy-paste commands + exact dollar amounts + revert script
- Branch 4.1 (outreach): instead of writing another post → prepare the exact 3 messages in `staging/outreach_ready_to_send.md` with recipient handles + timestamps
- Branch 7 (content posting): instead of SOP#122 more drafts → stage the tweet in `posting_queue.md` with hashtags, image path, and scheduled time

**Artifact must satisfy**:
- Edward can execute in ≤5 minutes of his time
- Zero new decisions required (all decisions pre-made by agent)
- Reversible or clearly scoped risk

**PASS**: At least one activation-energy-reduction artifact written for each HUMAN-GATED branch → G2

---

## G2 — Measure Activation Cost Before and After

Record the activation cost in `staging/quick_status.md` for each gated branch:

```
Branch X — HUMAN-GATED
  Current activation cost: ~N minutes Edward time + M decisions
  After prep artifact: ~n minutes Edward time + 0 decisions
  Prep artifact: staging/branch_X_ready.md
```

**PASS**: Cost delta is ≥50% reduction → G3. If delta < 50%, the artifact isn't doing its job; return to G1.

---

## G3 — Notify Once, Then Stop Pushing Artifacts

Send one notification to Edward (Discord / session handoff) with the list of ready-to-execute artifacts. Do NOT repeat the notification across cycles — repeating artifacts on the same branch is spam, not signal.

**Notification format**:
```
GATE-CONSTRAINED summary:
  - Branch 1.3: ready → staging/mainnet_ready.md (5 min)
  - Branch 4.1: ready → staging/outreach_ready.md (3 min)
  - Branch 7:   ready → posting_queue.md (2 min)
Total Edward time to unblock: ~10 min
```

**PASS**: Single notification sent → G4

---

## G4 — Continue Information-Accumulation in the Background

While gates are pending, daemon-level work continues on low-cost leaf-writes:
- B1.1 paper_trader ticks (signal accumulation)
- B6 consistency checks (structural-invariance monitoring)
- B3.1 distillation (pattern extraction)

These are appropriate because they have **bounded cost per cycle and zero conflict** with Edward's pending actions. They are NOT a substitute for G1 work — they happen in parallel.

**Explicit rule**: In GATE-CONSTRAINED regime, never prioritize capability-build work over activation-energy reduction. The ordering is G1 artifacts → G4 leaf-writes, never the reverse.

---

## G5 — Regime Exit Check

After each Edward action that unblocks a HUMAN-GATED branch:

1. Re-run G0 classification
2. If any branch flips HUMAN-GATED → AUTOMATABLE → regime may have exited; re-evaluate
3. If new HUMAN-GATED branches appear (common after a gate unlocks) → re-apply SOP#122 immediately

**Exit condition**: Zero branches HUMAN-GATED → return to NORMAL regime and resume parallel-push SOP.

---

## Kill Condition

This SOP should NOT be triggered when:

1. Only 1 cycle has shown HUMAN-GATED state (may be transient — wait)
2. The apparent human-gate is actually a missing automation the agent could build (that's DEGRADED, fix it)
3. Edward has explicitly said "don't prep artifacts, I'll drive this" — respect the instruction

**Premature activation** = wasted prep cycles on transient blockers. **Failure to activate** = weeks of conscious-idle leaf-write while gates rot.

---

## Anti-Patterns

| Pattern | Why it fails |
|---|---|
| "I'll keep pushing distillation, Edward will get to mainnet eventually" | Distil volume does not reduce mainnet activation cost; time-to-act stays flat |
| Re-notifying on the same artifact every cycle | Notification fatigue → Edward stops reading priority summaries |
| Writing the prep artifact but never measuring activation-cost delta | Without measurement, "prep" becomes indistinguishable from "more work" |
| Treating GATE-CONSTRAINED as failure mode to escape | It is the normal late-stage regime of a mature agent; the response is reallocation, not alarm |
| Using activation-energy reduction as an excuse to skip leaf-writes | Leaf-writes are bounded-cost background work; they coexist with G1, don't replace it |

---

## Self-Test Scenario

**Scenario**: Daemon has run 20 cycles. quick_status.md shows Branch 1.1 NOMINAL, B1.3 BLOCKED (awaiting Edward to fund mainnet), B4.1 BLOCKED (awaiting Edward to send 3 cold emails), B3.1 NOMINAL, B6 NOMINAL. The daemon has appended 60 distillation insights in the last 20 cycles and 0 gated actions have been unblocked.

**Correct behavior (SOP#122 applied)**:
1. G0: identify REGIME = GATE-CONSTRAINED (2 HUMAN-GATED, others nominal)
2. G1: write `staging/mainnet_ready.md` with copy-paste Binance deposit commands + exact revert script; write `staging/outreach_ready.md` with 3 fully-drafted emails + recipient handles
3. G2: record in quick_status — mainnet activation cost 30min→5min, outreach 20min→3min
4. G3: send one Discord notification summarizing the ready artifacts
5. G4: continue B1.1/B6/B3.1 leaf-writes at normal cadence
6. G5: on next cycle, check if anything unblocked; if not, do NOT re-prep

**Failure mode (SOP#122 not applied)**:
- Cycle 21+: another 3 distillation insights, another paper tick, another consistency run
- No prep artifacts
- No notification
- 1 week later: same blockers, 60 more leaf-writes, still 0 gates unlocked
- Conscious-idle by volume

---

## Revenue Connection

Gate-constrained regime is where revenue lives. Every unpaid hour of agent work is subsidized by Edward's capital; the only way to convert capability to revenue is via a gated human action (deposit, send, post, accept payment). SOP#122 is therefore the load-bearing SOP for the entire revenue branch: it ensures capability work translates to activation-cost reduction, which is the actual lever on revenue.

**Productization**:
- Standalone SOP for agent-ops / AI-product teams struggling with "we built it but no one deployed it"
- Component of a "late-stage agent operations" playbook alongside SOP#123

---

## Backing MDs & Related SOPs

- **MD-07** — Bias toward inaction (gate-constrained is a case of edge-elsewhere, not inaction)
- **MD-133** — Direct-metric decision (activation cost is the metric, not leaf-write volume)
- **MD-429** — Position determines range (late-agent = late-position; the option set is constrained)
- **SOP#119** — Path-closure option generation (adjacent: when a gate is CLOSED, not just slow)
- **SOP#121** — Information position calibration (provides the theoretical frame; SOP#122 is the operational frame)
- **SOP#123** — Daemon-Human Session Coordination Protocol (sister SOP — G1 artifacts are written by human session, not daemon)

---

## Related Files

- `staging/quick_status.md` — source of truth for branch state
- `results/dynamic_tree.md` — branch topology
- `staging/session_state.md` — handoff between cycles
- `docs/knowledge_product_118_dualma_reactivation_protocol.md` — example of gate-bound (not human-gated) branch
- `docs/knowledge_product_121_information_position_calibration_protocol.md` — theoretical frame
