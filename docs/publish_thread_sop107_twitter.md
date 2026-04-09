# Twitter Thread — SOP #107 Incremental Performance Evaluation

> Status: QUEUED | Scheduled: ~Nov 2026 | Cycle: 279

---

**Tweet 1 (hook)**
Most people evaluate performance wrong.

They look at total win rate.
They should look at the *last 30 data points*.

The aggregate lies. The marginal tells the truth.

🧵 SOP #107: Incremental Performance Evaluation Protocol

---

**Tweet 2 (the problem)**
Real example:

Player A: 70 games, 47% WR
Player B: 58 games, 50% WR

Naive pick: B (higher WR)

Now look at A's last 12 games: 4 wins.
That's 33%.

Player A is *declining*.
Player B is stable.

Total WR masked the decay.

---

**Tweet 3 (the rule)**
Rule: Aggregate metrics include the learning curve.

Marginal metrics show you what's happening NOW.

Early games = adaptation period.
Recent games = true current ability.

If recent WR < total WR by >5%: you're declining.

---

**Tweet 4 (minimum N)**
Don't fall for small sample noise.

N < 50: Statistical garbage. Wait.
N 50–100: Use cautiously.
N > 100: Marginal analysis is reliable.

Same applies to:
- Trading strategy evaluation
- Hiring decisions
- Your own skill tracking

---

**Tweet 5 (trading application)**
I apply this to every trading strategy I run.

Total PF = 1.4? Looks fine.
Last 40 ticks PF = 0.67? 

That strategy is degrading.

Kill it before the total PF catches up to the marginal truth.

---

**Tweet 6 (the insight)**
Most systems optimize for total metrics because they're easy to compute.

Marginal metrics require:
- Time segmentation
- Enough data
- Willingness to see the decline

That's the edge.

---

**Tweet 7 (CTA)**
SOP #107 of my Digital Immortality system.

Building decision frameworks that survive the person.

What metric are you tracking that might be masking a declining trajectory?
