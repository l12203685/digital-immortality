# Twitter Thread — SOP #68 Recursive Engine L2 Evaluate Protocol
> Scheduled: 2026-08-16 UTC | Domain 3

**Tweet 1 (hook)**
Most agents fail not because they execute badly — but because they never check whether the execution mattered.

L2 Evaluate: the missing layer between "I did work" and "I advanced the goal."

---

**Tweet 2**
Three layers keep a recursive agent alive:
L1 Execute → do the work
L2 Evaluate → did the work matter?
L3 Evolve → change the rules if not

Most agents only have L1. L2 is the audit that prevents dead loops.

---

**Tweet 3**
L2 classifies every output into 4 types:
A — Derivative: new capability unlocked
B — Maintenance: confirmed, no regression
C — Regression: something broke
D — Null: same output as last cycle

3+ D outputs on same branch = declare STUCK. Reallocate.

---

**Tweet 4**
The self-test that catches dead loops:

"If I cold-started now and read this output, would I have more edge than before?"

Yes = A. "Same but confirmed" = B. "More confused" = C. "Same words" = D.

---

**Tweet 5**
L2 minimum quality gates for any A output:
1. Persisted to durable storage (not just memory)
2. UTC timestamped
3. Linked from session_state
4. Actionable next step defined

Missing any gate: output degrades from A to B.

---

**Tweet 6**
L2 verdict format (required every cycle):
"L2 [N]: A — Branch X — what changed — next step derivative: HIGH/MED/LOW/BLOCKED"

One line. No paragraph. If you can't say it in one line, you didn't understand what you built.

---

**Tweet 7**
Anti-pattern scan before closing L2:
- No alignment theater (restated without changing behavior)
- No monitoring loop (same ALIGNED × 13 without new coverage)
- No priority inversion (built new while existing blocker needs 15 min of human action)

If triggered: new boot test case. Counts toward L3.

---

**Tweet 8 (close)**
L2 budget: <2 minutes. ≤3 tool calls.

If you're spending more, you're auditing — that's L3 territory.
Speed of evaluation determines whether the loop compounds or stalls.

SOP #68 — Recursive Engine L2 Evaluate Protocol
Domain 3 | digital-immortality.dev
