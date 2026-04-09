# Morning Defaults — Branch 8.4 Automation #1
> MD-322: >3 decisions of the same type = system design failure. Fix: pre-commit defaults.
> Implemented: 2026-04-09 UTC (cycle 126)

## Why this exists

Audit showed 8 meal decisions/week × 9 min avg = **69 min/week** on zero-EV cognitive load.
Same for work block start (4× / week, 37 min) and exercise routing (4× / week, 65 min).
Total recoverable: **171 min/week = 148 hrs/year**.

---

## Pre-committed defaults (no decision required)

### Meal rotation (Mon–Sun)
| Day | Breakfast | Lunch | Dinner |
|-----|-----------|-------|--------|
| Mon | Eggs + coffee | Batch-cooked rice + protein | Whatever's in fridge |
| Tue | Oatmeal + coffee | Same batch | Same |
| Wed | Eggs + coffee | Eat out (fixed budget) | Same |
| Thu | Oatmeal + coffee | Batch-cooked rice + protein | Same |
| Fri | Eggs + coffee | Same batch | Eat out |
| Sat | Anything (low-decision day) | Delivery allowed (15-min cap) | Anything |
| Sun | Batch-prep day (cook for Mon–Fri) | Leftovers | Leftovers |

**Rule**: If default is unavailable → next item on list, no deliberation.

---

### Work block start: 09:00 UTC fixed
- Default: desk at 09:00, no re-deciding.
- Exception: scheduled meeting overrides. That's not a decision — it's a calendar event.

---

### Exercise routing decision tree
```
Today is: [check calendar]
  Has 30+ min free before 12:00 UTC? → Home workout (20 min minimum)
  No?                                 → Walk during lunch (15 min minimum)
  Travel / sick?                      → Skip (no guilt, log reason)
```
- Rule: the decision is made at 08:55 UTC by checking calendar. Not at 09:30 when willpower is lower.

---

### Learning resource (MD-322 violation: 4×/week, 52 min wasted)
**Pre-committed sequence** (rotate in order, no choice):
1. Anki deck (trading MDs) — 20 min
2. Active JSONL batch (if pending) — until done
3. Book/paper — remainder of session

Reset on Monday. If blocked on item N, skip to N+1. Log reason, move on.

---

## Self-test

If you find yourself deliberating on any of the above → **flag it**. That is a system signal, not a personal failure. The system needs an update, not willpower.

Update frequency: quarterly or after 3 logged exceptions to the same default.
