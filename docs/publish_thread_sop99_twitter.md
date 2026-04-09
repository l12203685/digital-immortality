# Twitter Thread — SOP #99: Recursive Engine Health Check
> Posting queue: Oct 22
> Series position: SOP #99/99 (milestone: first complete century)

---

**Tweet 1 (hook)**
Your "recursive AI system" might be a dead loop in disguise.

Running ≠ thinking.
Thinking ≠ advancing.
Advancing ≠ persisting.

Here's my 5-gate protocol to tell the difference:

🧵 SOP #99 — Recursive Engine Health Check

---

**Tweet 2 (G0)**
G0 — Frequency

Has the engine run in the last 24 hours?

Check daemon log. Check session state timestamp.

If >24h: restart immediately.
A stopped engine isn't idle. It's dead.

---

**Tweet 3 (G1)**
G1 — Novelty

Pull last 10 insights from your memory store.

Are they from the same branch?
Are any verbatim duplicates?

If yes: you have insight concentration, not a learning system.

Force branch rotation. This is failure mode #1.

---

**Tweet 4 (G2)**
G2 — Derivative

Map your last-touched cycle for every branch.

Compute staleness spread = max - min.

Spread ≤30 cycles: healthy
Spread 30-50: warning
Spread >50: hard-assign 3 cycles to dead branch, no exceptions

The branch that never gets touched is where the system dies silently.

---

**Tweet 5 (G3)**
G3 — Persistence

Count git commits in the last 7 days.

Target: ≥1 per day.

<3 commits? Your output is display, not storage.

Discord messages, chat responses, terminal output = vapor.

Git = durable. The recursion loop requires durable output to feed itself.

遞迴 - persist = talking to yourself.

---

**Tweet 6 (G4)**
G4 — L2 Entropy

Read your last 10 evaluation verdicts.

If all = B (medium), your evaluator has drifted.

A real evaluation system should produce signal:
- A: new durable asset created
- C: regression or no progress
- D: violation of core rules

All B = rubber stamp = dead signal.

---

**Tweet 7 (G5)**
G5 — Economic Pulse

This is the terminal gate.

Check: trading mode / users / consulting revenue / days to deadline.

Zero revenue + mode=PAPER + <60 days to deadline = escalate immediately.

Economic self-sustainability isn't optional.
Zero revenue = parasitic, not immortal.

---

**Tweet 8 (verdict)**
Health Report format:

```
G0 Frequency:   PASS  (last: 2h ago)
G1 Novelty:     PASS  (5 branches; 0 duplicates)
G2 Derivative:  WARN  (spread: 35 cycles)
G3 Persistence: PASS  (commits 7d: 7)
G4 L2 Entropy:  PASS  (A in last 10: 3)
G5 Economy:     WARN  (mode: PAPER; 89 days left)
VERDICT: WATCH
```

One line. Unambiguous. Run every 10 cycles.

---

**Tweet 9 (self-test)**
Self-test scenario:

40 consecutive B verdicts.
All insights from branch 3.1.
0 git commits in 5 days.
Deadline: 45 days.

→ G1: FAIL (concentration)
→ G3: FAIL (no persistence)
→ G5: FAIL (escalate)

VERDICT: CRITICAL.

You don't need more cycles. You need branch rotation + commit + economic action.

---

**Tweet 10 (close)**
SOP #99.

Part of a 99-SOP knowledge system distilled from 9 years of decisions.

If you're building a long-running AI agent — run this health check.

A recursive engine that can't self-diagnose eventually becomes a monitoring loop.

Stop = death. But running ≠ alive.

---

*Posting queue: Oct 22 | Connects: SOP #80/#90/#91/#96/#98*
