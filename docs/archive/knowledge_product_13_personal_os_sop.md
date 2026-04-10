# SOP #13 — Personal Operating System: Recurring Decision Elimination

> Source MDs: MD-322, MD-323, MD-324 (Branch 8, life maintenance)
> One-claim: "Willpower is a finite resource. Your OS should never touch it."

---

## Why This SOP Exists

If you make the same decision more than 3 times, you don't have a decision — you have a system failure (MD-322).

Every recurring decision burns cognitive bandwidth that should go to strategy, learning, or execution. The goal is zero recurring overhead.

---

## Gate Sequence (5 gates)

### G0 — Audit: Identify Recurring Decisions
Run a 2-week decision log. Flag any decision that appears ≥3×.

Failure mode: skipping audit because "I already know my patterns." You don't. The data surprises you every time.

Output: list of SYSTEM_FAILURE decisions sorted by frequency.

Edward audit results (2026):
- Exercise: ×6 → SYSTEM_FAILURE
- Lunch: ×5 → SYSTEM_FAILURE
- Deep-work timing: ×5 → SYSTEM_FAILURE
- Coffee vs tea: ×4 → SYSTEM_FAILURE
- Portfolio check timing: ×4 → SYSTEM_FAILURE

### G1 — Peak Cognitive Protection
Identify your biological peak (most people: 09:00–13:00). Hard-assign only: strategy, analysis, creative work (MD-323).

Rule: if the task doesn't require peak cognition, it does not happen during peak hours.

Admin, email, routing decisions → off-peak only.

Failure mode: letting "urgent" admin invade peak hours. Urgency is a feeling, not a fact.

### G2 — Environment Design Before Willpower
Before invoking willpower on any behavior, redesign the environment first (MD-324).

Examples:
- Want to exercise? Lay out gear the night before.
- Want deep work? Phone out of reach, not just silenced.
- Want consistent meal choice? Pre-decide rotation, not in-the-moment.

Rule: if willpower is required, the environment is wrong.

### G3 — Pre-Commit the Top 5 System Failures
For each SYSTEM_FAILURE decision: write one permanent default. No re-evaluation allowed.

Format:
```
[Decision]: [Always/Never] + [Condition]
Exercise: always yes — Mon/Wed/Fri/Sat, 07:00
Lunch: rotation from morning_defaults.md, ≤200 TWD cap
Deep work: 09:00 hard start, no exceptions
Coffee/tea: coffee before 13:00, tea after 13:00
Portfolio check: 16:00 once daily, no earlier
```

Once pre-committed: remove the decision from your mental stack. It no longer exists.

### G4 — Morning Defaults Routing
First 3 routing decisions of the day (meal, work block, exercise) must be automated before bed the night before.

Output: `morning_defaults.md` — a pre-committed rotation that eliminates day-start friction.

Zero-EV decisions before 10:00 = context switching tax on the most valuable hours.

### G5 — Quarterly Re-Audit
Every 90 days: re-run the decision log. New SYSTEM_FAILURE decisions emerge as life changes.

Compounding check: score = (new decisions pre-committed) / (new SYSTEM_FAILURES found)
- Score ≥ 0.8: OS healthy, continue
- Score < 0.8: audit cycle too slow, tighten frequency

---

## Self-Test Scenario

Situation: you find yourself deciding at 09:30 whether to go to the gym today.

Apply SOP:
- G0: gym decision appearing at all = SYSTEM_FAILURE (already decided ×5 this month)
- G3: pre-committed default = always yes on scheduled days
- G4: gear already laid out (environment design)
- Correct action: execute default, do not re-evaluate

Wrong action: spend 3 minutes weighing energy levels, decide "maybe tomorrow." Tomorrow = same loop.

---

## Output File
- `docs/morning_defaults.md` ✓ (cycle 126)
- `docs/system_failure_automations.md` ✓ (cycle 127)
- `memory/decision_audit.json` ✓ (decision_audit.py persistent state)

---

## Series Position
SOP #13 of the Digital Immortality Knowledge Product Series.
Extends the series beyond trading/career into the operating layer that makes everything else possible.
