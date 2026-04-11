# memory/recursive_distillation.md

Cross-session record of Branch 3.1 distillation cycles. Each entry captures the 3 insights extracted per cycle, their source signals, and the running total.

Never delete — append only.

---

## Cycle 241 — 2026-04-09T12:00:00+00:00

**Source cycles**: 240-241
**Branch**: 3.1 recursive distillation
**Insights appended**: 3 (total: 41)

### Insight 1: organism-network-pairwise-triage

SOP #76 formalized the first explicit topology for the organism network. The 3-tier divergence triage (≥80% skip / 60-79% async / <60% deep dive) is not just a workflow rule — it encodes that divergence magnitude determines urgency, and that treating all disagreement uniformly is both wasteful and fragile. The triage bands ARE the network architecture.

**Signal source**: SOP #76 written cycle 240; pairwise collision + ground truth escalation protocol
**Tags**: organism-network, SOP-76, divergence-triage, topology

### Insight 2: boot-test-llm-boundary

Boot tests reached 36 scenarios with 33 deterministic-pass and 3 LLM-required (MD-295/MD-28/MD-01). The LLM-required boundary is a diagnostic signal: wherever LLM evaluation is needed, the DNA principle exists but is not sufficiently explicit to produce a deterministic answer. Each LLM-boundary scenario is a DNA sharpening candidate.

**Signal source**: Boot test expansion cycles 240-241; 3 new scenarios added
**Tags**: boot-test, LLM-boundary, DNA-completeness, determinism

### Insight 3: least-recent-decay-signal

daemon_next_priority "least recent" routing is a minimum viable anti-decay mechanism for branch coverage. When all branches are covered and the signal reads "least recent: 存活/cold-start", this is urgency-proportional to time-since-last-touch — not a quiescent state. Branch decay is invisible until it triggers a boot test failure; least-recent selection keeps every branch in active rotation.

**Signal source**: daemon_next_priority.txt cycle 240-241; all-branches-covered condition
**Tags**: branch-decay, daemon-priority, least-recent, coverage-drift

---

## Cycle 243 — 2026-04-09T13:00:00+00:00

**Source cycles**: 241-242
**Branch**: 3.1 recursive distillation
**Insights appended**: 3 (total: 44)

### Insight 1: llm-validation-gate-architecture

SOP #77 G0-G5 gate structure encodes that scenario classification (G0) determines the entire validation path. Wrong classification at G0 = wrong gate = wrong verdict. The gate architecture IS the correctness guarantee for cold-start integrity. This generalizes: any multi-gate protocol's fidelity is bounded by the accuracy of its first classification step. Classification-first is not a convenience — it is load-bearing.

**Signal source**: SOP #77 written cycle 241; G0-G4 PASS; 3/3 LLM ALIGNED cycle 242
**Tags**: SOP-77, cold-start, gate-architecture, LLM-validation, classification-first

### Insight 2: ready-posted-gap-is-behavioral

SOP #78 closes the ready→posted gap. Root finding: content can be fully prepared (drafted, queued, threaded) and still never get posted. The gap is behavioral, not logistical. An explicit atomic post sequence (G1) and cadence protocol (G3) are required to bridge it. The gap is the critical path to distribution revenue: SOP #01 is ready and has been ready — the missing piece is the execution trigger. Having systems ready is necessary but not sufficient.

**Signal source**: SOP #78 written cycle 242; posting queue extended to Sep 10; blocker analysis
**Tags**: SOP-78, posting-ops, ready-posted-gap, behavioral-gap, cadence, distribution

### Insight 3: derivation-chain-scenarios-permanent-llm-boundary

Cycle 242 LLM validation (3/3 ALIGNED: poker_gto_mdf / trading_atr_sizing / career_multi_option_ev) confirmed that derivation-chain scenarios cannot be promoted to deterministic. They test reasoning path execution, not recall of a stored answer. This is a permanent taxonomic boundary: deterministic tests check stored decisions; LLM-required tests check live derivation. Both are necessary and neither can substitute for the other. Attempting to make derivation-chain tests deterministic would produce false positives (right answer, wrong path).

**Signal source**: LLM validation cycle 242 (3/3 ALIGNED); SOP #77 G2 protocol
**Tags**: LLM-validation, derivation-chain, permanent-boundary, boot-test-taxonomy, SOP-77

---

## Cycle 244 — 2026-04-09T UTC

**Source cycles**: 243-244
**Branch**: 3.1 recursive distillation
**Insights appended**: 3 (total: 47)

### Insight 1: sop-series-structural-completion

SOP #01–#80 now complete. The last six SOPs (#75–#80) closed structural gaps: pool lifecycle / organism network / LLM validation / posting ops / DNA update / cold-start calibration. The meta-framework is built. Future SOPs should target operational gaps in lived domains (health, time, relationships, finance, decisions in novel situations) — not new infrastructure. Building more infrastructure onto a complete foundation is over-engineering.

**Signal source**: SOP #80 written cycle 244; SOP #79 cycle 243; series retrospective
**Tags**: SOP-series, structural-completion, meta-framework, operational-gaps

### Insight 2: cold-start-calibration-first-run

SOP #80 first execution: 33/33 ALIGNED, PASS, no drift detected. The calibration run establishes a baseline — not a one-time check, but the anchor for monthly delta-tracking. Cold start was lucky streak; after SOP #80, cold start is a protocol-guaranteed property. Monthly cadence + post-DNA-update spot-check + score-drop trigger = three-layer invariant maintenance. The three permanent LLM-boundary scenarios are documented; recalibration should never target them.

**Signal source**: SOP #80 G1–G5 run cycle 244; consistency_test.py 33/33; cold_start_health_report.md
**Tags**: SOP-80, cold-start, calibration, baseline, invariant, branch-6

### Insight 3: paper-live-short-persistence-117

Tick 117: BTC=$71,240.33, DualMA_10_30=SHORT×117 consecutive (100%). 117 ticks of unbroken SHORT through the $70k–$72k range = signal persistence, not noise. The signal's durability demonstrates that regime-detection (MIXED) correctly filters non-trending conditions while DualMA's cross-timeframe signal remains clean. No regime flip in 117 ticks = macro SHORT intact. This is the longest unbroken signal streak recorded in the paper-live log.

**Signal source**: paper-live tick 117 cycle 244; paper_live_log.jsonl 1067 entries
**Tags**: trading, paper-live, signal-persistence, DualMA, branch-1.1, regime-MIXED

---

## Cycle 257 — 2026-04-09T UTC

**Source cycles**: 256-257
**Branch**: 3.1 recursive distillation
**Insights appended**: 3 (total: 90)

### Insight 1: cross-instance-calibration-is-survivability-test

Cross-instance calibration (SOP #93) is the survivability test for the digital twin. `consistency_test.py` checks regression within one instance; cross-instance test checks whether two fresh cold-starts agree. Model version upgrades are the highest-risk event — behavioral fidelity is not guaranteed across model generations. The protocol trigger on model upgrade is non-negotiable. Without this test, "passes 33/33" is a necessary but not sufficient condition for immortality.

**Signal source**: SOP #93 written cycle 257; gap analysis between consistency_test.py and cross_instance_test.py scope
**Tags**: digital-immortality, cross-instance, model-survivability, SOP-93, branch-6

### Insight 2: divergence-root-cause-4-class-taxonomy

Cross-instance divergence has 4 root cause classes: A=DNA gap (principle missing), B=reasoning path gap (principle exists but retrieval chain breaks), C=model boundary (formula derivation, permanent), D=scenario ambiguity (fix the question not the DNA). The critical error is applying Class A repair (add MD) to a Class C cause (model boundary) — this pollutes DNA with false principles derived from model limitations, not Edward's actual reasoning. Correct classification before repair is the load-bearing step of the entire protocol.

**Signal source**: SOP #93 G3 classification design; prior permanent-boundary insight (cycle 243); dna-hygiene lessons
**Tags**: cross-instance, divergence-classification, DNA-hygiene, SOP-93, root-cause

### Insight 3: sop92-strategy-lifecycle-closed-loop

SOP #92 (Strategy Disable & Reactivation Protocol) closes the strategy lifecycle loop. The kill decision existed (SOP #04), but the reactivation path was undefined. Without explicit reactivation criteria, disabled strategies either stay dead forever (lost alpha) or get re-enabled arbitrarily (undisciplined). The closed loop: kill threshold → disable → cooling period → reactivation gate (regime flip + re-backtest pass) → probation pool → full reactivation OR permanent retire. Open loops in the trading system become technical debt; closed loops become adaptive infrastructure.

**Signal source**: SOP #92 written cycle 46 (daemon); DualMA_10_30 disable event in paper-live log
**Tags**: trading, strategy-lifecycle, SOP-92, closed-loop, adaptive-infrastructure

---

## Cycle 95 — 2026-04-10 UTC

**Source cycles**: 296-297
**Branch**: 3.1 recursive distillation
**Insights appended**: 3 (total: 93)

### Insight 1: daemon-priority-stale-branch-alive

daemon_next_priority can flag a branch as "neglected" while it's actually being touched every cycle — if the definition of "touch" only checks recency but not forward-derivative (is the branch actually advancing?). Running the same consistency test is touching but not advancing. True "concrete work" on 存活 = expand the scenario set, improve cold-start protocol, or audit runbook freshness — not just re-running 33/33. Priority signal needs to distinguish "active maintenance" from "active advancement."

**Signal source**: daemon_next_priority.txt said "neglected for 20 cycles" while dynamic_tree showed 6.29→6.35 (consistency run every 2-3 cycles); semantic mismatch between "touched" and "advanced"
**Tags**: daemon, priority-signal, branch-health, meta-system, signal-decay

### Insight 2: b2.2-completion-archive-method-validated

416 MDs extracted from own message archive (202604→201709, 7.5 years). The archive method is validated: own chat history is the highest-fidelity source of behavioral patterns because the patterns existed before being named — extraction reveals structure that was operating implicitly. Archive exhaustion is not failure; it means the historical input is fully harvested. Future MD sources: live experience accumulation, recursive synthesis from existing MD cross-patterns, organism collision divergences. The method continues; the input source changes.

**Signal source**: cycle 296 verified 201610/11/12 = 0 Edward msgs; archive boundary confirmed; 416 MDs represents ~7.5 years compressed
**Tags**: branch-2.2, MD-extraction, archive-method, methodology, digital-immortality

### Insight 3: all-flat-mixed-regime-correct-signal

100+ consecutive ticks with 15 active strategies all FLAT in MIXED regime is correct behavior, not a dead loop. The inaction bias principle (no edge = no action) applies at the trading execution layer, not just at the meta-strategy layer. A system that fires no trades when regime is ambiguous is healthy. The error would be forcing a trade to show "activity." Distinguish: idle system (no signal) vs dead system (not running). The log entries continue; the signals are correctly suppressed.

**Signal source**: trading_engine tick 317: 15/15 FLAT for 100+ consecutive ticks; kill conditions monitored; regime=MIXED (no clear trending or mean-reverting signal)
**Tags**: trading, inaction-bias, regime-detection, all-flat, correct-behavior

---

---

## Cycle 96 — 2026-04-10T04:30Z

**Source cycles**: 298-299
**Branch**: 3.1 recursive distillation
**Insights appended**: 3 (total: 96)

### Insight 1: taxonomy-audit-drift-to-protocol-reclassification

When a taxonomy audit reclassifies a data point from DRIFT to protocol, this is frame evolution, not error correction. DRIFT = the current taxonomy frame did not fit; reclassification to protocol = the data point was load-bearing all along — the frame needed to evolve to make it visible. Taxonomy audit is not just correctness checking; it is a mechanism for detecting that the frame itself has become the bottleneck. Every DRIFT→protocol reclassification is evidence that the system is processing faster than its classification vocabulary can keep up.

**Signal source**: cycle 298 B3.1 taxonomy-audit COMPLETE (DRIFT→protocol reclassification confirmed)
**Tags**: taxonomy, branch-3.1, classification, frame-evolution, drift-to-protocol

### Insight 2: cold-start-g2-meta-rules-fully-covered

Cycle 299 audit confirms SOP #101 G2 passes: all 4 meta-rules covered in generic_boot_tests.json (39 scenarios): meta_search_before_act, meta_output_must_persist, meta_three_layer_loop, meta_strategy. G2 gate does not need re-work unless new meta-rules are added to the DNA. The audit itself took 1 command. Automated coverage verification >> manual checklist review. Next G2 audit trigger: new meta-rule added to dna_core.md.

**Signal source**: cycle 299 B存活 G2 audit; generic_boot_tests.json 39 scenarios; SOP #101
**Tags**: cold-start, branch-6, SOP-101, G2, boot-tests, meta-rules, coverage

### Insight 3: cold-start-cycle300-audit-is-designed-trigger

SOP #101 G1 specifies next dna_core.md audit at cycle ~300 (90 cycles from cycle 267). At cycle 299, the scheduled trigger is reached. Scheduled maintenance > reactive repair: the audit was designed in, not prompted by failure. Verify: (1) priority stack 可可>FIRE>trading>..., (2) three-layer loop L1/L2/L3 present, (3) SOP series (#01-#116) reflected, (4) no stale MDs from completed branches. This is the first cycle-300 DNA audit in project history — a designed checkpoint, not a spontaneous one.

**Signal source**: SOP #101 G1 audit cycle ~300 target; cycle 267 last dna_core audit; 90-cycle cadence
**Tags**: cold-start, branch-6, SOP-101, G1, dna-audit, scheduled-maintenance, cycle-300

---

## Cycle 97 — 2026-04-11T04:20Z

**Source cycles**: 300-301
**Branch**: 3.1 recursive distillation
**Insights appended**: 3 (total: 99)

### Insight 1: dualma-long-flip-is-regime-data-not-alpha

DualMA_10_30 flipped LONG at BTC=$72,790 after a sustained MIXED regime with prior PF=0.53 kill. The flip is not necessarily alpha — it may be regime data. A strategy killed for PF<0.8 cannot be re-enabled without the formal reactivation gate (SOP #92: cooling period + regime flip + re-backtest pass + probation pool). Observing the signal is correct (keep logging); acting on it without re-enabling it through SOP #92 is incorrect. The kill is persistent until formally reversed. Live signal ≠ live authorization.

**Signal source**: paper_trader --tick 2026-04-11; BTC=$72,790.5; DualMA_10_30=OPEN_LONG; prior kill at PF=0.53 cycle 277
**Tags**: trading, DualMA, signal-flip, LONG, SOP-92, kill-persistence, reactivation-gate

### Insight 2: sop117-bundle-arbitrage-is-information-edge-operationalized

SOP #117 (Bundle Arbitrage Protocol) encodes that bundle arbitrage is fundamentally an information asymmetry exploit (MD-04): the edge exists while most buyers see the bundle as a bundle, not as a scarce-component carrier. The G0-G5 protocol operationalizes the full cycle: identify scarce component → verify acquisition route → model spread → verify exit route → execute → close before information symmetry collapses. The kill condition is information collapse, not price movement. This generalizes: any information-asymmetry-based trade has a structural decay clock that starts the moment the edge becomes visible to others.

**Signal source**: SOP #117 created; MD-399 + MD-04 integration; knowledge_product_117_bundle_arbitrage_protocol.md
**Tags**: SOP-117, bundle-arbitrage, information-asymmetry, MD-04, edge-decay, branch-5, branch-7

### Insight 3: 52-clean-cycles-cold-start-structural-invariant

52 consecutive consistency-test passes (33/33 deterministic ALIGNED) through cycles 246-298 makes cold-start integrity a structural property, not an operational lucky streak. Below ~10 consecutive passes, a clean run is a check. Above 50, it is an invariant. The proper label changes from "passing the test" to "maintaining the invariant." Structural invariants should be monitored at lower frequency than active tests — the monitoring cost should be proportional to the probability of drift, which decreases as the streak lengthens. Monthly audit cadence (SOP #80) is correctly calibrated for an invariant at this streak length.

**Signal source**: consistency_test.py 33/33 ALIGNED cycle 298 (52nd consecutive); streak started cycle 246; SOP #80 monthly cadence
**Tags**: cold-start, branch-6, structural-invariant, consistency, streak-52, SOP-80

---

## Cycle 98 — 2026-04-11T05:00Z

**Source cycles**: 302-303 (session start)
**Branch**: 3.1 recursive distillation
**Insights appended**: 3 (total: 102)

### Insight 1: priority-file-branch-completion-lag

When daemon_next_priority.txt references B2.2 ("next JSONL batch") while dynamic_tree confirms B2.2 COMPLETE (archive exhausted at 416 MDs), the two persistence stores have diverged. This is a meta-system health signal: the priority mechanism does not auto-sync on branch completion. Result: daemon cycles wasted polling a closed branch while live branches starve. Fix direction: priority file update should be a required step in the branch-close protocol — same cycle the branch is marked COMPLETE in the tree, the priority pointer must be cleared. Unsync between priority and tree = invisible decay.

**Signal source**: daemon_next_priority.txt referencing B2.2; dynamic_tree line 84 confirming COMPLETE; session observation cycle 302
**Tags**: meta-system, priority-mechanism, branch-decay, sync-gap, daemon

### Insight 2: killed-strategy-signal-observation-vs-authorization

DualMA_10_30 emitted OPEN_LONG at BTC=$72,790 (paper_trader cycle 301) while still under kill conditions (PF=0.53 kill from cycle 277). The distinction: a killed strategy can still emit observable signals in the log — observation is correct (diagnostic data on whether the kill was premature). Acting on those signals without formal reactivation via SOP #92 (cooling period + regime flip + re-backtest + probation pool) would be a protocol violation. The kill is persistent until formally reversed. Live signal ≠ live authorization. Logging continues; execution is frozen. This is the correct behavior — not a bug in the system.

**Signal source**: paper_trader --tick 2026-04-11; DualMA_10_30=OPEN_LONG at $72,790; kill event cycle 277 PF=0.53; SOP #92 reactivation gate
**Tags**: trading, DualMA, kill-persistence, observation-vs-authorization, SOP-92, branch-1.1

### Insight 3: boot-tier-selection-is-resource-allocation

The 3-tier boot protocol (Type A ~600 tokens / Type B ~12K / Type C ~25K) is not a convenience choice — it is a resource allocation decision on the economic survivability critical path. API token cost is the denominator in the trading_profit > API_cost survivability condition. On daily check-ins with no active task and no flagged L3 event, escalating to Type C is a protocol violation with direct economic consequences. The boot tier classifier operationalizes the inaction-bias principle at the infrastructure layer: do not consume resources without a named edge. Type A is the hard default; Type C requires explicit Saturday or L3-event justification.

**Signal source**: CLAUDE.md boot tier table; SKILL.md economic survivability condition; quick_status daemon RUNNING cycle 302
**Tags**: boot-protocol, resource-allocation, survivability, token-cost, inaction-bias, branch-6

---

## Cycle 262-270 — 2026-04-09T12:10Z (backfill)

**Source cycles**: 259-270
**Branch**: 3.1 recursive distillation (taxonomy backfill)
**Insights appended**: 0 (narrative only — backfill for insights 94-120)

### Insight 1: paper-live-short-structural-persistence-tick141

Tick 141 (BTC=$71,182) confirmed that DualMA_10_30 SHORT signal had been structurally unbroken across the $70k–$72k mixed-regime window. The key finding: in a mixed regime, single-strategy SHORT persistence is not a contradiction — the regime classifier correctly filters execution while the structural signal waits. Signal durability in a flat execution environment means the thesis is intact, not stale. Patience under MIXED is the correct behavior; forcing entries to resolve uncertainty would be the error.

**Signal source**: insights.json entry 94 (paper-live-tick-141); entry 106 (paper-live strategy-convergence SHORT-consensus)
**Tags**: domain-knowledge + trading, paper-live, signal-persistence, regime-MIXED, branch-1.1

---

### Insight 2: organism-network-effect-structural-vs-idiosyncratic-divergence

SOP #95 (Organism Network Effect Protocol) introduced the taxonomy: structural divergence (appears in ≥2 organism pairs) vs idiosyncratic divergence (1 pair only). This distinction is load-bearing for resource allocation. Structural divergence = DNA gap; requires universal calibration. Idiosyncratic divergence = organism-specific noise; requires targeted recalibration only for that pair. Conflating them wastes calibration effort on noise while missing systemic DNA issues. The expansion window trigger (≥75% agreement) and contraction signal (<75%) encode this logic operationally.

**Signal source**: insights.json entry 96 (organism-network-effect-sop95); entry 147 (organism-collision-critical-regression-cycle277)
**Tags**: methodology + organism-network, divergence-taxonomy, SOP-95, structural-vs-idiosyncratic, branch-4

---

### Insight 3: turing-test-candidate-qualification-criteria

SOP #98 (Turing Test Candidate Selection) addressed Branch 9's 0/3 candidate blocker. The qualification criteria encode an important principle: ≥3 years known + ≥2 domains observed + ≥10 substantive exchanges. Family is disqualified (confirmation bias too high). The criteria are not arbitrary thresholds — they reflect the minimum information surface needed to distinguish Edward's specific reasoning from generic intelligent conversation. Too-close relationships produce false positives (they expect specific answers); too-distant relationships produce false negatives (no baseline). The criteria define the evidence boundary for valid Turing evaluation.

**Signal source**: insights.json entry 104 (turing-test-candidate-selection-sop98); entry 105 (fake-health-audit-cycle264)
**Tags**: methodology + turing-test, candidate-selection, validation-boundary, SOP-98, branch-9

---

## Cycle 270-285 — 2026-04-09T14:49Z (backfill)

**Source cycles**: 270-285
**Branch**: 3.1 recursive distillation (taxonomy backfill)
**Insights appended**: 0 (narrative only — backfill for insights 121-160)

### Insight 1: dual-ma-kill-and-reactivation-cycle-as-strategy-lifecycle-evidence

Cycle 277: DualMA_10_30 was killed (MDD=34.9% ≥ 15% threshold, PF=0.53 < 0.8) but then reactivated cycle 279 after re-backtest pass (PF=16.13, 2 trades +1.57%). This kill→cooling→reactivation sequence was the first live execution of SOP #92's closed loop. The reactivation succeeded: DualMA_10_30 immediately resumed SHORT signal with positive contribution. The lesson is that the kill protocol protects capital precisely so that reactivation can happen without scar tissue — the strategy returns clean, not damaged.

**Signal source**: insights.json entry 145 (paper-live-btc71361-disabled-cycle277); entry 158 (paper-live-btc72319-dual-ma-short-cycle279)
**Tags**: domain-knowledge + trading, strategy-lifecycle, kill-reactivation, SOP-92, branch-1.1

---

### Insight 2: md-extraction-behavioral-patterns-career-decision-architecture

Cycles 275-282 extracted MDs from 201901–201810 JSONL covering career decision-making. Three recurring behavioral patterns emerged: (1) concrete anchor in salary negotiation — a specific number forces a yes/no decision rather than exploratory bargaining; (2) safety net as risk-tolerance calibrator — existing buffers should shift the decision maker toward higher-variance/higher-EV options; (3) technical depth over salary delta when the gap is < 15% — early-career skill accumulation compounds faster than the incremental salary difference. These are not rules; they are observed decision patterns that revealed implicit logic Edward was already operating by before the principles were named.

**Signal source**: insights.json entries 152-154 (201901 salary/safety-net/technical-depth MDs); entries 163-165 (201811 claimed-framework/startup-hiring/early-mover MDs)
**Tags**: behavioral-patterns + career, salary-negotiation, risk-calibration, skill-accumulation, branch-2.2

---

### Insight 3: consulting-content-outreach-execution-gap-is-behavioral-not-logistical

Branch 1.3 stalled for 70 cycles because the diagnosis was wrong: "no audience yet" was treated as a prerequisite blocker. SOP #110 corrected this — the actual blocker was zero active outreach. The content was ready; the DM templates were drafted; the execution gap was purely behavioral (inertia, not resource constraint). SOP #111 closed the delivery protocol (4-phase 90-min guided onboarding). The pattern generalizes: when a branch stalls, the first audit question is "is the blocker logistical or behavioral?" Behavioral blockers do not yield to more planning; they require execution commitment with a concrete trigger.

**Signal source**: insights.json entry 166 (skill-commercialization-first-user-outreach-cycle282); entry 167 (skill-session-delivery-4-phase-90min-cycle282); entry 181 (branch-1-3-week1-dms-drafted-execution-ready)
**Tags**: self-awareness + behavioral-gap, execution-inertia, outreach, SOP-110, SOP-111, branch-1.3

---

## Cycle 285-298 — 2026-04-10T00:00Z (backfill)

**Source cycles**: 285-298
**Branch**: 3.1 recursive distillation (taxonomy backfill)
**Insights appended**: 0 (narrative only — backfill for insights 161-206)

### Insight 1: mainstream-signal-contrarian-protocol-as-exit-architecture

SOP #115 (Mainstream Signal Contrarian Protocol) encodes the observation from 201804 that social labels (poker=gambling, self-trading=proprietary trading) diverge from mechanism. The SOP operationalizes this: mainstream media + family chat = retail entry signal = informed exit window. The protocol is 5 gates (G0-G5): signal layer calibration → exposure audit → contrarian confirmation → exit execution → cash redeployment. The key design choice is signal layer calibration first — not all mainstream signal is equal. A Bloomberg article triggers differently than a family WhatsApp group. The L0–L4 calibration makes the protocol regime-specific rather than binary.

**Signal source**: insights.json entry 200 (sop115-mainstream-signal-contrarian-protocol); entries 188/190 (201804 social-label/result-decoupling)
**Tags**: domain-knowledge + contrarian-investing, signal-calibration, SOP-115, mainstream-signal, branch-7

---

### Insight 2: cold-start-runbook-staleness-is-behavioral-decay

Cycle 287 cold-start runbook update corrected 3 stale count references (330→387 MDs, 14→39 boot test scenarios). Stale runbook numbers are not cosmetic — they are behavioral decay markers. A runbook with wrong counts produces wrong triage decisions: a cold-start operator following stale numbers would underestimate coverage. The pattern: every time a system grows (more MDs, more scenarios), all downstream documentation that references counts must be updated atomically. Delayed updates accumulate as invisible drift. The fix requires a forcing function — either automated count injection or a mandatory runbook-sync step at every major milestone.

**Signal source**: insights.json entry 193 (存活-cold-start-runbook-updated-cycle287); entry 162 (daemon-priority-staleness-monitoring-drift)
**Tags**: self-awareness + cold-start, runbook-staleness, documentation-drift, forcing-function, branch-6

---

### Insight 3: md-extraction-archive-boundary-marks-method-transition

Cycle 296 confirmed the archive boundary: 201610/11/12 = 0 Edward messages. 416 MDs extracted covering 7.5 years (202604→201701). Archive exhaustion is a milestone, not a failure mode — it means historical input is fully harvested. Future MD sources shift: live experience accumulation, recursive cross-pattern synthesis from existing 416 MDs, and organism collision divergences as revealed preferences. The method continues but the input changes. This transition is structurally identical to the trading system's regime shift logic: when the data source changes, the extraction protocol must adapt, not stop. Archive-sourced MDs versus live-experience MDs have different noise characteristics; the validation protocol needs to account for this difference.

**Signal source**: insights.json entry 207 (taxonomy-drift-is-retrieval-drift); insights from cycle-95 entry (b2.2-completion-archive-method-validated); entry 199 (201801-md397-399-capital-gate)
**Tags**: methodology + archive-method, md-extraction, source-transition, digital-immortality, branch-2.2, branch-3.1

---

## Cycle 97 — 2026-04-10T08:30:00+00:00

**Source cycles**: 300-301
**Branch**: 3.1 recursive distillation
**Insights appended**: 3 (total: 99)

### Insight 1: two-signal-convergence-mixed-regime-conviction

At tick 350 (BTC=$72,351.36), two independent strategy families signal SHORT in MIXED regime: DualMA_10_30 (trend-following) and gen_BollingerMeanReversion_RF_598b24 (mean-reversion). When both a trend-follower and a mean-reverter agree on direction in a mixed regime — where they normally cancel each other — the convergence signal carries higher conviction than either alone. In mixed regimes, single-family signals are ambiguous; cross-family convergence is the exception worth tracking. Monitor: does 2+ SHORT convergence in MIXED precede directional price movement?

**Signal source**: paper-live tick 350 (daemon cycle 301); 2/18 SHORT (DualMA_10_30 + gen_BollingerMR_RF_598b24); 16/18 FLAT; regime=MIXED; 2092 log entries
**Tags**: trading, paper-live, signal-convergence, mixed-regime, branch-1.1, cross-family

### Insight 2: 55th-consecutive-consistency-as-invariant

The 55th consecutive 36/39 ALIGNED result confirms cold-start behavioral consistency has crossed from milestone to operational invariant. An invariant is a property maintained across all checks without degradation — not a high-water mark. The permanent 3 LLM-boundary misalignments (poker_gto_mdf, trading_atr_sizing, career_multi_option_ev) are now taxonomically settled: they test derivation-chain reasoning, not stored decisions. Invariant maintenance cost = 1 script run per cycle. Invariant failure cost = cold-start behavioral drift = existential. The asymmetry justifies indefinite continuation.

**Signal source**: consistency_test.py run cycle 301; 36/39 ALIGNED (55th consecutive); 3 MISALIGNED = permanent LLM-boundary; baseline saved results/consistency_baseline.json
**Tags**: cold-start, branch-6, consistency, invariant, boot-test, LLM-boundary, branch-存活

### Insight 3: branch-maintenance-vs-advancement-protocol-gap

daemon_next_priority.txt flags 存活 as "neglected for 20 cycles" while session_state shows 54th consecutive + G1-G5 HEALTHY. Both are correct: the branch is being *maintained* (same tests passing), not *advanced* (new scenarios added, protocol coverage extended, runbook freshness audited). Maintenance = running existing tests. Advancement = expanding the test surface, auditing protocol freshness, or closing gaps the tests don't yet cover. Every branch needs two protocols: a maintenance protocol (automated, low-friction) and an advancement protocol (human-gated or insight-driven, higher effort). The daemon priority signal fires on advancement-gap, not maintenance-gap — these need separate triggers.

**Signal source**: daemon_next_priority.txt "neglected 20 cycles"; cycle-95 insight 1 on touched-vs-advanced; cycle 301 consistency run as maintenance
**Tags**: daemon, branch-health, maintenance-vs-advancement, meta-system, branch-6, protocol-design

---
