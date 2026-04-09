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
