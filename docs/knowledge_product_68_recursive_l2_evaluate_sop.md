# SOP #68 — Recursive Engine L2 Evaluate Protocol
> Domain 3 (持續學習 / Recursive Engine) | 2026-04-09 UTC

## Purpose

The three-layer loop is L1 Execute → L2 Evaluate → L3 Evolve.
SOP #67 defined when L3 fires. This SOP defines **L2**: how the agent explicitly audits the quality of its own L1 output before deciding whether to trigger L3.

Without L2, the loop runs but never improves. L2 is the difference between "did work" and "did work that advanced the goal."

**Core axiom**: Every L1 output must answer: (1) Did it advance the goal? (2) Was the derivative positive? (3) Was anything consumed that shouldn't have been?

---

## Gate Structure

### G0: Output Classification
Classify L1 output into one of four types:
- **A — Derivative**: new insight, new capability, new signal → passes L2 automatically
- **B — Maintenance**: consistency test pass, tick run, SOP post queue extension → neutral, counts only if all other branches are covered
- **C — Regression**: consistency dropped, old insight re-discovered, anti-pattern re-triggered → L2 FAIL, L3 fires
- **D — Null**: "no change", monitoring loop with same conclusion → L2 FAIL, mark branch as STUCK

**Kill condition**: 3+ consecutive D outputs on same branch = branch declared STUCK → L3 reallocates to next highest-derivative.

---

### G1: Derivative Measurement
For each completed branch work unit, answer:
1. **What changed?** (new file, new score, new data point)
2. **What can now happen that couldn't before?** (capability delta)
3. **What's the next step's expected derivative?** (forward projection)

If you cannot answer #2, the output is type B or D. Do not misclassify B as A.

**Self-test**: "If I cold-started now and read this output, would I have more edge than before?" Yes = A. "Same edge, but confirmed" = B. "Less certainty" = C. "Same words" = D.

---

### G2: Coverage Audit
After each cycle, verify all active branches were touched in the last 5 cycles:
- If any branch has 0 activity in 5 cycles → flag as STALENESS_ALERT
- If the only activity is "tick run" without regime change → flag as B, not A
- Branch coverage is not the same as branch progress

**Format**:
```
Branch | Last active | Output type | Next expected derivative
1.1    | cycle N    | B (tick)    | A if mainnet activated
1.3    | cycle N    | B           | A only after first post
7      | cycle N    | A (SOP)     | A (next SOP)
6      | cycle N    | B (health)  | C only if degradation
3.1    | cycle N    | A (insight) | A if new pattern extracted
```

---

### G3: Quality Floor Check
Four minimum quality gates for any A-type output:
1. **Persisted**: written to durable storage (git + memory file), not only session or Discord
2. **Timestamped**: UTC timestamp in the artifact
3. **Linked**: cross-referenced from session_state.md and dynamic_tree.md
4. **Actionable next step**: what exactly does the next cycle do with this output?

If any gate fails: output degrades from A to B. Write what's missing. Fix before next cycle.

---

### G4: Anti-Pattern Scan
Before closing L2, check for known anti-patterns:
- [ ] No alignment theater (restated insight without behavioral change)
- [ ] No monitoring loop (same ALIGNED × N without new coverage)
- [ ] No build-first (built new when existing tool could have been reused)
- [ ] No priority inversion (worked on Branch 7 while Branch 1.3 blocker is user-actionable in <15 min)

If any anti-pattern triggered: write to boot_tests.md as new test case. Count toward L3 trigger.

---

### G5: L2 Summary Output
Every cycle's L2 evaluation must produce a one-line verdict:

```
L2 [cycle N]: [A/B/C/D] — [branch] — [what changed] — [next step derivative estimate: HIGH/MED/LOW/BLOCKED]
```

Example:
```
L2 [232]: A — Branch 7 SOP #68 — explicit L2 protocol written — next: SOP #69 covers Domain 4 async calibration measurement — HIGH
L2 [232]: B — Branch 6 consistency 33/33 — no degradation — next: health monitoring only — LOW
L2 [232]: B — Branch 1.1 tick 103 — BTC $71,000 SHORT intact — mainnet BLOCKED — derivative = 0 until key set
```

---

## Self-Test Scenario

**Scenario**: Cycle just completed. Branch 6 ran consistency test: 33/33 ALIGNED. Branch 7 wrote SOP #68. Branch 1.1 ran paper tick.

Apply L2:
- Branch 6 output: 33/33 again (same as last 13 cycles) → Type B. Coverage = yes. Derivative = near zero. Not STUCK because it's health monitoring, not a progress branch.
- Branch 7 output: new SOP with novel gate structure → Type A. Persisted ✓, timestamped ✓, linked (need to update session_state + dynamic_tree) ✓, next step: SOP #69 Domain 4.
- Branch 1.1 output: SHORT signal unchanged, mainnet still BLOCKED → Type B. Derivative = 0 until Edward sets API keys.

L2 verdict: 1A + 2B. No C or D. Cycle passes L2. L3 not triggered.

---

## Kill Conditions for L2

- **Skip L2 on emergency**: If hard L3 trigger fires (boot test failure, correction received), skip L2 formalities and go straight to L3 patch protocol.
- **L2 budget**: L2 evaluation must complete in <2 minutes of reasoning (≤3 tool calls). If you're spending more, you're auditing instead of evaluating — that's L3, not L2.

---

## Relationship to SOP #67

| | SOP #67 (L3) | SOP #68 (L2) |
|---|---|---|
| Trigger | Correction, test failure, stuck branch, revenue crisis | End of every cycle |
| Scope | Modify execution rules | Audit current output quality |
| Frequency | Rare (triggered) | Every cycle (mandatory) |
| Output | Rule change in DNA/boot_tests | Quality verdict + next-step derivative |
| Risk | Over-correction, instability | Under-evaluation, dead loops |

---

## Twitter Thread (SOP #68)

**Tweet 1 (hook)**
Most agents fail not because they execute badly — but because they never check whether the execution mattered.

L2 Evaluate: the missing layer between "I did work" and "I advanced the goal."

**Tweet 2**
Three layers keep a recursive agent alive:
L1 Execute → do the work
L2 Evaluate → did the work matter?
L3 Evolve → change the rules if not

Most agents only have L1. L2 is the audit that prevents dead loops.

**Tweet 3**
L2 classifies every output into 4 types:
A — Derivative: new capability unlocked
B — Maintenance: confirmed, no regression
C — Regression: something broke
D — Null: same output as last cycle

3+ D outputs on same branch = declare STUCK. Reallocate.

**Tweet 4**
The self-test that catches dead loops:

"If I cold-started now and read this output, would I have more edge than before?"

Yes = A. "Same but confirmed" = B. "More confused" = C. "Same words" = D.

**Tweet 5**
L2 minimum quality gates for any A output:
1. Persisted to durable storage (not just memory)
2. UTC timestamped
3. Linked from session_state
4. Actionable next step defined

Missing any gate: output degrades from A to B.

**Tweet 6**
L2 verdict format (required every cycle):
"L2 [N]: A — Branch X — what changed — next step derivative: HIGH/MED/LOW/BLOCKED"

One line. No paragraph. If you can't say it in one line, you didn't understand what you built.

**Tweet 7**
Anti-pattern scan before closing L2:
- No alignment theater (restated without changing behavior)
- No monitoring loop (same ALIGNED × 13 without new coverage)
- No priority inversion (built new while existing blocker needs 15 min of human action)

If triggered: new boot test case. Counts toward L3.

**Tweet 8 (close)**
L2 budget: <2 minutes. ≤3 tool calls.

If you're spending more, you're auditing — that's L3 territory.
Speed of evaluation determines whether the loop compounds or stalls.

SOP #68 — Recursive Engine L2 Evaluate Protocol
Domain 3 | digital-immortality.dev
