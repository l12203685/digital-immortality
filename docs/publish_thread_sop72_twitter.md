# Twitter Thread — SOP #72: Concentration Log Infrastructure
> Slot: Aug 26 | Domain 1 (經濟自給) | Status: pending

---

**Tweet 1 (hook)**
You built a multi-strategy trading system.
One strategy is signaling. Nine are FLAT.

How long has this been true?

You don't know. You have no log.

That's the problem SOP #72 solves.

---

**Tweet 2**
First: this is not a bug.

In a MIXED regime, most trend/MR strategies should be FLAT.
DualMA_10_30 catching the trend is correct.

But "correct" and "untracked" are different problems.

---

**Tweet 3**
A concentration event = 1 strategy = 100% of signals for 100+ consecutive ticks.

It's not a kill condition.
It's a diagnostic trigger.

The question is: have you been here before?
How long does this typically last?

Without a log, you can't answer either question.

---

**Tweet 4**
The schema (append-only JSONL):

```json
{
  "ts": "2026-04-09T08:12:15Z",
  "event_type": "CONCENTRATION_START",
  "strategy": "DualMA_10_30",
  "consecutive_ticks": 107,
  "regime": "mixed",
  "g1_audit": "PENDING"
}
```

One line per event. Never overwrite. Historical record is sacred.

---

**Tweet 5**
Four event types:

CONCENTRATION_START — threshold crossed
CONCENTRATION_EXPECTED — G1 audit passes (FLAT is correct)
CONCENTRATION_ESCALATED — G1 fails (something broken)
CONCENTRATION_RESOLVED — second strategy activates

Most events will be START → EXPECTED.
ESCALATED means something needs fixing.

---

**Tweet 6**
The G1 audit (from SOP #71):

Is FLAT the correct regime response?
Or is the strategy broken?

If regime = MIXED and trend score = 0.01:
FLAT is correct. Log CONCENTRATION_EXPECTED. Continue.

If regime = TRENDING and DualMA_RSI_filtered is still FLAT:
Something's wrong. Investigate.

---

**Tweet 7**
The quarterly kill condition:

If 1 strategy = sole signal for 3+ months
→ This is a portfolio design flaw, not a regime event.

3 months ≈ 1,314 ticks at daily cadence.
Current: 107 ticks = 8.1% of threshold.

Not a flaw. But now I'll know when it becomes one.

---

**Tweet 8**
Cold-start protocol:

On boot, check: any CONCENTRATION_START with no subsequent CONCENTRATION_RESOLVED?

If yes → open concentration event.
consecutive_ticks tells you how long it's been running.

Without this, every boot starts blind.

---

**Tweet 9**
The real insight:

Logging ≠ monitoring.

A log records what happened so you can reason about it later.
A monitor alerts when thresholds are crossed.

Build the log first.
Alerting comes from reading it.

Don't skip the log because you don't have the alert yet.

---

**Tweet 10**
This is SOP #72 in one sentence:

"The infrastructure that makes SOP #71 actionable."

SOP #71 defined the protocol.
SOP #72 built the storage.

Without both, G3 is a procedure you can't execute.

---

**Tweet 11**
Self-test result (cycle 236):

- concentration_log.jsonl created ✅
- Bootstrap entries written (START + EXPECTED) ✅
- DualMA_10_30 at tick 107: 8.1% of quarterly threshold ✅
- Cold-start query: 0 unresolved escalations ✅

Infrastructure complete.

---

**Tweet 12 (close)**
Every system has emergent gaps.

SOP #71 assumed a log existed.
The log didn't exist.
SOP #72 fills the gap.

This is how a knowledge machine evolves:
not by planning everything upfront
but by closing gaps as they surface.

SOP #01~#72 complete.
