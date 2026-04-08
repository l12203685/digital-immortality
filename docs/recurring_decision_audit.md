# Recurring Decision Audit — Branch 8.4
> 生活維護 | Life Maintenance System
> Cycle: 2026-04-08 UTC
> Generated: 2026-04-08T00:00:00Z
> MD-322: >3次同一決策=系統設計失敗

---

## Purpose

Every recurring decision is a tax on cognitive resources. This audit surfaces which decisions are repeating, calculates their total drain, and converts them into pre-committed defaults or automated flows.

**Rule:** If a decision has appeared >3 times in the past week, it is not a decision problem — it is a system design failure (MD-322).

---

## Section 1 — Decision Log (One Week Sample)

Record every decision you made, however small. Date range: seven consecutive days.

| # | Date | Decision Made | Category | Time Spent (min) | Cognitive Load (1–5) | Outcome |
|---|------|---------------|----------|:-----------------:|:-------------------:|---------|
| 1 | Mon | What to eat for breakfast | Nutrition | 8 | 2 | Eggs + coffee |
| 2 | Mon | Whether to check trading dashboard before market open | Trading ops | 5 | 3 | Checked — no issues |
| 3 | Mon | Which learning resource to open (book vs Anki vs paper) | Learning | 12 | 3 | Started paper |
| 4 | Tue | What to eat for breakfast | Nutrition | 7 | 2 | Skipped, grabbed bar |
| 5 | Tue | When to start peak-hour work block | Schedule | 10 | 2 | 9:30 AM |
| 6 | Tue | Whether to reply to a low-priority message now or later | Communication | 4 | 1 | Replied immediately |
| 7 | Wed | What to eat for breakfast | Nutrition | 9 | 2 | Oatmeal |
| 8 | Wed | Which strategy to review first in morning SOP | Trading ops | 7 | 3 | Sorted by drawdown |
| 9 | Wed | Whether to exercise today (gym vs home vs skip) | Health | 15 | 3 | Skipped — rationalised |
| 10 | Wed | When to start peak-hour work block | Schedule | 8 | 2 | 9:15 AM |
| 11 | Thu | What to eat for breakfast | Nutrition | 6 | 2 | Eggs + coffee |
| 12 | Thu | Whether to reply to a low-priority message now or later | Communication | 5 | 1 | Deferred — then forgot |
| 13 | Thu | Which learning resource to open | Learning | 14 | 3 | Opened three tabs, decided nothing |
| 14 | Thu | Whether to check trading dashboard before market open | Trading ops | 4 | 3 | Checked |
| 15 | Fri | What to eat for breakfast | Nutrition | 7 | 2 | Skipped again |
| 16 | Fri | When to start peak-hour work block | Schedule | 11 | 2 | 10:00 AM (late) |
| 17 | Fri | Whether to exercise today | Health | 18 | 3 | Did 20 min home workout |
| 18 | Fri | Which strategy to review first in morning SOP | Trading ops | 8 | 3 | No consistent criteria |
| 19 | Sat | What to eat for lunch | Nutrition | 10 | 2 | Delivery app scroll 15 min |
| 20 | Sat | Whether to work on a weekend project or rest | Schedule | 20 | 4 | Worked but felt guilty |
| 21 | Sun | Which learning resource to open | Learning | 13 | 3 | Anki but stopped after 10 min |
| 22 | Sun | Whether to exercise today | Health | 16 | 3 | Skipped |
| 23 | Sun | What to prep / eat for the coming week | Nutrition | 22 | 3 | No prep, punted to Monday |

---

## Section 2 — Frequency Counter

Tally recurring decisions from the log above. Only decisions appearing **>3 times** qualify as system failures.

| Decision | Occurrences | Total Time Lost (min) | Avg Cognitive Load | Failure Flag |
|----------|-----------:|:---------------------:|:-----------------:|:------------:|
| What to eat (any meal) | 8 | 69 | 2.2 | YES (MD-322) |
| When to start peak work block | 4 | 37 | 2.0 | YES (MD-322) |
| Which learning resource to open | 4 | 52 | 3.0 | YES (MD-322) |
| Whether to check trading dashboard | 3 | 16 | 3.0 | Borderline |
| Whether to exercise / how | 4 | 65 | 3.0 | YES (MD-322) |
| Whether to reply to low-priority messages now | 3 | 14 | 1.0 | Borderline |
| Which strategy to review first | 3 | 22 | 3.0 | Borderline |
| Whether to work on weekend | 1 | 20 | 4.0 | Not yet |

**Total decision overhead this week: ~275 minutes (~4.6 hours)**

---

## Section 3 — Automation Candidates

Ranked by: **Frequency × Decision Cost (time × load) × Repeatability score (1–3)**

Repeatability: 1 = situational, 2 = mostly stable, 3 = fully repeatable week-over-week.

| Rank | Decision | Freq | Time×Load | Repeat | Score | Automation Type |
|------|----------|:----:|:---------:|:------:|------:|-----------------|
| 1 | What to eat (meals) | 8 | 69×2.2=152 | 3 | **3,648** | Pre-committed rotating menu |
| 2 | Whether / how to exercise | 4 | 65×3.0=195 | 3 | **2,340** | Calendar block + default format |
| 3 | Which learning resource to open | 4 | 52×3.0=156 | 2 | **1,248** | Sequenced queue (Anki→paper→book) |
| 4 | When to start peak work block | 4 | 37×2.0=74 | 3 | **888** | Fixed alarm, no override allowed |
| 5 | Which strategy to review first | 3 | 22×3.0=66 | 3 | **594** | Sort rule: highest current DD first |
| 6 | Whether to check trading dashboard | 3 | 16×3.0=48 | 3 | **432** | Scheduled in morning SOP checklist |
| 7 | Whether to reply to low-priority messages | 3 | 14×1.0=14 | 2 | **84** | Batch window: once at end of day |

---

## Section 4 — Pre-Commit Resolutions

For each ranked candidate, the decision is made **once, here, permanently**, unless a major life condition changes. This is MD-318 applied to life operations: separate "is this worth doing" from "what is the default execution".

---

### R-01: Meal Defaults (Score 3,648 — highest priority)

**Pre-committed answer:** Rotate a fixed 5-meal breakfast set on weekday mornings. No decision allowed before 10 AM.

```
Mon/Wed/Fri: Eggs (2) + black coffee
Tue/Thu:     Oatmeal + black coffee
Sat/Sun:     First thing available in fridge, 5-minute rule
Lunch:       Meal-prepped on Sunday for Mon–Thu; Friday is free choice (1 decision/week allowed)
```

**Trigger for override:** Fridge is empty (then: convenience store default, no delivery app scroll).

**MD link:** MD-322 (>3 repetitions = system failure), MD-324 (remove friction from desired path).

---

### R-02: Exercise Schedule (Score 2,340)

**Pre-committed answer:** Exercise is not a daily decision. It is a scheduled appointment.

```
Mon / Wed / Fri: 07:30–08:15 — home strength (bodyweight + dumbbells)
Sat:             09:00–10:00 — longer run or gym session
Tue / Thu / Sun: Rest (no guilt, no renegotiation)
```

**Default format if time-constrained:** 20-minute home circuit. Skip = only allowed for illness or travel; logged in journal.

**MD link:** MD-322, MD-324.

---

### R-03: Learning Queue (Score 1,248)

**Pre-committed answer:** Learning session order is determined by a fixed priority queue, not by morning mood.

```
Session type A (peak window, 45 min): Active paper / book chapter
Session type B (mid window, 20 min):  Anki review deck
Session type C (low window, 10 min):  Passive (podcast / listen-only)

Queue rule: Complete current unit before opening next. No "let me just check what else there is".
```

**MD link:** MD-322, MD-323 (peak window = type A only), MD-07 (checklist execution).

---

### R-04: Peak Work Block Start Time (Score 888)

**Pre-committed answer:** Peak cognitive window starts at **09:00 sharp**, no exceptions on weekdays.

```
08:45 — final prep (water, no phone, all tabs pre-loaded)
09:00 — block begins (1.5–2 hr, no meetings, no messages)
10:30 — first break allowed
```

**Rule:** If block did not start by 09:15, the morning is considered a half-day peak loss — log it, do not attempt to recover by pushing into mid-window.

**MD link:** MD-323 (peak = only for high-cognition), MD-322.

---

### R-05: Strategy Review Order (Score 594)

**Pre-committed answer:** Morning strategy review follows a fixed sort rule — no browsing.

```
Sort criteria (applied in order):
  1. Current drawdown as % of historical MDD (highest first)
  2. Days since last manual review (longest first)
  3. Alphabetical (tiebreak only)

Time box: 15 minutes maximum for morning review scan.
```

**MD link:** MD-07 (checklist confirmation), MD-95 (kill conditions defined in advance).

---

### R-06: Trading Dashboard Check (Score 432)

**Pre-committed answer:** Dashboard check is part of the morning SOP, not a separate decision.

```
Morning SOP item #3 (after boot, after email scan):
  - Open dashboard
  - Check: position sync, overnight fills, margin status
  - Total time: 5 min
  - Result: green (no action) / yellow (note) / red (alert protocol)
```

**MD link:** MD-84 (position sync is non-negotiable daily discipline), MD-07.

---

### R-07: Low-Priority Message Handling (Score 84)

**Pre-committed answer:** One batch window per day: **17:30–18:00**. Nothing answered outside that window unless sender is on Tier 1 (partner, defined close contacts).

**MD link:** MD-322, MD-324.

---

## Section 5 — Environment Redesign Checklist

Based on MD-324: redesign the environment so that each pre-committed resolution above has the minimum possible friction and the alternative path has maximum friction.

### Physical Environment

- [ ] Breakfast ingredients for the full rotating menu are prepped and visible on Sunday evening (not buried in fridge)
- [ ] Exercise gear is left out the night before scheduled workout days — no searching required
- [ ] Phone is physically in a different room from 08:45 to 10:30 (peak block protection)
- [ ] Laptop has a saved browser session with peak-work tabs pre-loaded — one click to start
- [ ] Kitchen has no delivery app shortcut visible on phone home screen (friction for scroll behaviour)

### Digital Environment

- [ ] Trading dashboard URL is pinned as first tab in morning SOP browser session
- [ ] Learning queue is a single flat text file — one file, no folders, top item is current task
- [ ] Anki deck is always the first app opened after 12:00 (shortcut on home screen, not buried)
- [ ] Low-priority messaging apps have notifications fully silenced (no badges until batch window)
- [ ] Calendar has a permanent recurring block: Mon/Wed/Fri 07:30 "Exercise" — deletion requires two steps

### Scheduling Environment

- [ ] Sunday 20:00: 15-minute weekly reset (meal prep, queue update, SOP check) — recurring calendar block
- [ ] Each work morning: phone alarm at 08:45 labelled "Peak block — phone away now"
- [ ] Strategy review: automated sort script runs at 08:50, outputs today's review order to a single text file

### Social / Friction Fences

- [ ] Communicate batch window hours to regular contacts ("I reply to non-urgent messages after 17:30")
- [ ] Meal delivery app deleted from phone home screen; bookmark only in desktop browser (increases friction by ~40 sec)
- [ ] Grocery standing order: recurring weekly auto-delivery covers breakfast staples — no manual shopping decision

---

## Section 6 — Audit Summary

| Metric | Before audit | After implementation |
|--------|:-----------:|:-------------------:|
| Recurring decisions requiring active thought per week | ~23 | ~4 (exceptions only) |
| Weekly decision overhead (est.) | ~275 min | ~30 min |
| Decisions hitting MD-322 failure threshold | 5 confirmed | 0 (converted to defaults) |
| Peak cognitive window protected days/week | ~2 (informal) | 5 (enforced by environment) |

**Next audit cycle:** 2026-04-15 UTC
**Trigger for earlier re-audit:** Any pre-commit resolution broken more than twice in a week = the resolution itself is poorly designed (MD-322 applies recursively to the system design).

---

## Appendix — Scoring Formula

```
Automation Priority Score = Frequency × (Time_per_instance × Cognitive_Load) × Repeatability

Where:
  Frequency       = occurrences in the log week
  Time_per_instance = minutes spent per occurrence
  Cognitive_Load  = self-rated 1–5 (1=trivial, 5=high-stakes)
  Repeatability   = 1 (situational) | 2 (usually repeats) | 3 (always repeats)

Higher score = address first.
```
