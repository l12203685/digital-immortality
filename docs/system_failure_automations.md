# System Failure Automations — Branch 8.5
> MD-322: >3 decisions of the same type = system design failure. Fix: pre-commit defaults.
> Implemented: 2026-04-09 UTC (cycle 127)

Top 3 SYSTEM_FAILURE decisions from decision_audit.py (×6, ×5, ×5 occurrences):

---

## #1 — Exercise (×6 occurrences)
**Pre-committed default:** YES, always. No decision needed.

Decision tree:
- Mon/Wed/Fri: strength (30 min, bodyweight or gym)
- Tue/Thu/Sat: cardio (20 min walk/run minimum)
- Sun: rest (active recovery if energy permits)

**Rule**: If you're asking "should I exercise today?" — you already know the answer. Do it.
**Exception trigger**: fever, injury, or <5h sleep → reduce to 10-min walk only.

---

## #2 — Lunch (×5 occurrences)
**Pre-committed default:** Check morning_defaults.md for day-of-week rotation.

If not at home: default = highest-protein option available, skip menu analysis.
**Budget cap**: 200 TWD / 7 USD max. If over cap → home food.

---

## #3 — When to start deep-work block (×5 occurrences)
**Pre-committed default:** 09:00 sharp. No negotiation.

- Pre-work ritual ends at 08:55 (coffee made, desk clear, phone silent)
- 09:00: first task starts. Not email. Not Slack. Task.
- Block length: 90 min (08:55 env setup → 09:00 start → 10:30 break)
- Second block: 13:00 (post-lunch, 90 min)
- Off-peak (admin/email/review): 11:00–12:30 and 16:00+

**If you are asking when to start:** it's already 09:00 or later — you're late. Start now.

---

## #4 — Coffee vs tea (×4 occurrences)
**Pre-committed default:** Coffee before 13:00. Tea after 13:00.

- Morning (before 09:00): coffee (black, no decision)
- Mid-morning (09:00–13:00): coffee if <2 cups today; tea if already at 2 cups
- Afternoon (13:00+): tea only (avoid caffeine crash interference with sleep)

**If you are asking coffee or tea:** check the clock. Rule applies. No deliberation.

---

## #5 — Portfolio check timing (×4 occurrences)
**Pre-committed default:** Once per day, 16:00 local time. Not before.

- 16:00: open dashboard, check positions, check P&L — 5 min max
- No checks during deep-work blocks (09:00–10:30, 13:00–14:30)
- No checks during meals
- Exception: kill condition breach alert (MDD>10%) → check immediately

**If you are asking whether to check portfolio:** it is not 16:00 yet. Close the tab.
