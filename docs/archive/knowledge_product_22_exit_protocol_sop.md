# SOP #22 — Universal Exit Protocol

> "You didn't have an exit. You had a hope."

**Claim:** Most bad outcomes aren't caused by a bad entry. They're caused by not writing the exit conditions before the entry.

**Backing MDs:** MD-96 / MD-112 / MD-133 / MD-75 / MD-159 / MD-322

---

## The Problem

Most decisions fail at the exit, not the entry:
- You enter a trade with a thesis. You exit on emotion.
- You start a job expecting growth. You leave after 4 years of hoping.
- You launch a project with a goal. You kill it when you run out of patience.

The pattern: the exit was never specified. It was always going to be improvised.

**An unwritten exit is not an exit. It's a gamble on your future self's clarity.**

---

## The 5-Gate Protocol

### G0 — Name the domain
Before writing anything else, label the decision type:
- **Trade** → time horizon + instrument
- **Career** → role + company + comp band
- **Project** → scope + timeline + output
- **Relationship** → collaboration type + dependency level

This prevents mixing frameworks across domains.

---

### G1 — Write the exit before the entry

Format: *"I will exit when [objective condition], regardless of emotional state."*

Examples by domain:

| Domain | Example exit condition |
|--------|----------------------|
| Trade | MDD > 10% from entry, or signal reversal on weekly close |
| Job | 12 months below MD-163 input quality threshold + no trajectory |
| Project | 3 consecutive cycles with no derivative improvement (MD-322) |
| Relationship | 3× commitment miss + behavior inconsistency > 50% (MD-327) |

**Rule:** If you can't write the exit condition in one sentence, you don't understand the position well enough to enter it.

---

### G2 — Separate kill conditions from performance conditions

Two distinct lists:

**Kill conditions** (immediate exit, no debate):
- Hard floor violations (MD-75): equity curve drops below stop level
- Structural failure: the *why* for entering no longer exists
- Kill conditions pre-defined in G1 are triggered

**Review conditions** (pause and reassess):
- Performance degrades but hasn't crossed kill threshold
- Environment changed but thesis still holds
- MD-112: "define what failure looks like before you start"

**Why separate?** Kill conditions must be mechanical. Review conditions are analytical. Mixing them causes you to rationalize through kill-worthy events.

---

### G3 — Size the trial position independently (MD-159)

Before committing full size:
- Trial position: 25–50% of intended full size
- Exit criteria for trial same as full position (same G1 conditions)
- Trial is complete when: kill condition NOT triggered AND evidence supports full commitment

**The trial position has independent positive EV. It is not a "test" that you expect to fail.**

If the trial hits kill conditions → exit entirely, do not add to full size.

---

### G4 — Equity curve trigger for scaling (MD-75)

Regardless of domain, use a 3-state leverage model:

| State | Condition | Response |
|-------|-----------|----------|
| Normal | Performance on track | Full allocation |
| Warning | 1st threshold breach (e.g., 5–8% DD or 2 consecutive miss months) | Reduce to 50% |
| Stop | 2nd threshold breach (e.g., 12% DD or 3 consecutive miss months) | Exit, paper-mode only |

**Recovery path:** Close → observe 5 units of time (sessions/weeks/months depending on domain) → restart at 25% size.

---

### G5 — Post-exit review (close the loop)

After every exit, within 48h:
1. Was the exit triggered by G1 kill condition or by emotion?
2. Did the position reach G3 full-size or stay at trial?
3. What would have happened with no exit written?
4. One sentence: what changes in the next position's G1?

**MD-322 check:** If you've reviewed the same exit failure 3+ times → this is a system design failure. Automate the trigger.

---

## Self-Test

**Scenario:** You've been at a job for 18 months. Compensation is at the 40th percentile for your level (MD-163). Your manager is supportive but organizational structure limits growth. You haven't written an exit condition.

Apply the protocol:

- **G0:** Career domain. Role: quant analyst. Comp band: current $X, market $X×1.6.
- **G1:** Exit condition: "If comp remains below market 60th percentile after one formal negotiation cycle, AND no trajectory to role change within 6 months → begin active search."
- **G2:** Kill condition: comp offer rejected AND no counter-structure offered → immediate search. Review condition: comp below target but explicit promotion timeline confirmed in writing.
- **G3:** Trial = one negotiation conversation. If kill condition triggered → exit (begin search). If review → set 90-day clock.
- **G4:** 90-day clock hits → re-evaluate. No movement → move to Stop state (active applications).
- **G5:** After exit: was the exit driven by G1 or frustration? Record.

**Verdict:** CONDITIONAL GO — with G1 written, the position is now manageable. Without G1, this is an open-ended commitment with no exit.

---

## Kill Conditions (for this protocol itself)

- You write the exit condition AFTER the event (MD-96 violated) → invalidate that decision from the record
- Exit was triggered by emotion, not G1 condition → mark as SYSTEM_FAILURE in G5 review
- G3 trial position was skipped → require explicit justification before next full-size entry

---

## Backing MD Summary

| MD | Principle |
|----|-----------|
| MD-96 | Write kill condition before entry |
| MD-112 | Define failure before starting |
| MD-133 | Stop-first sizing: stop → position size |
| MD-75 | Equity curve 3-state leverage trigger |
| MD-159 | Trial vs full position — independent EV |
| MD-322 | 3× same decision = system design failure |

---

*Part of the Edward Decision System — SOP #22 of 22*
