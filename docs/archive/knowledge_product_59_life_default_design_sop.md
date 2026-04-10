# SOP #59 — Life Default Design Protocol

**Domain 7: System Architecture / Behavioral Infrastructure**
**Status:** Active
**Version:** 1.0
**Dependencies:** SOP #53 (Cognitive Bandwidth), SOP #55 (Environment), SOP #58 (Mental Capital), SOP #13 (Personal OS)

---

## Why This SOP Exists

SOP #53 budgets your 20 decision units per day. SOP #58 monitors the psychological substrate. Neither addresses the upstream design flaw that drains both: recurring decisions that were never converted into defaults.

The gap: most life systems are operated by willpower rather than architecture. Every repeated decision — what to eat, when to exercise, which task to start, how to handle a routine trigger — consumes a decision unit it was never meant to consume. The unit was spent not because the situation was new, but because no default was ever written.

This is not a discipline failure. It is a system design failure.

The fix is structural: convert every repeated decision into a pre-written default. Schedule high-cognitive work in peak windows. Build environments where the optimal behavior is the lowest-friction path. The result is not more self-control — it is less need for self-control.

```
Repeated Decision Audit → Default Conversion → Peak Window Protection → Environment Redesign → Weekly Friction Scan → Default Maintenance
```

Completion signal: decision unit burn rate drops ≥30% within 60 days with no reduction in output quality.

---

## Three-Layer Architecture

| Layer | Gate | Function |
|-------|------|----------|
| L1 | G0/G1 | Audit — identify where decision units are being consumed by non-novel problems |
| L2 | G2/G3 | Build — convert repeated decisions into defaults; protect peak windows |
| L3 | G4/G5 | Maintain — weekly friction scan; emergency protocol when system degrades |

L1 runs once (initial audit) then quarterly. L2 produces the architecture. L3 runs every week.

---

## DNA Anchors

| MD | Principle | How it applies here |
|----|-----------|---------------------|
| MD-322 | Life system = minimum decision frequency design | Every repeated decision is a system design failure — convert to default |
| MD-323 | Physiological peak window = high-cognitive task's only valid slot | Protect peak window; administrative tasks fill low-cognitive slots |
| MD-324 | Environment design > willpower execution | Optimal behavior must be the lowest-friction path; friction blocks non-optimal |
| MD-13 | Default gravity | Without designed defaults, behavior drifts to minimum energy state |
| MD-67 | System | Willpower is finite; architecture is constant — route through architecture |

---

## Branch Connections

- **Branch 5 (Cognitive Bandwidth / SOP #53):** Every default written frees decision units for novel problems. G0 audit output feeds directly into SOP #53's decision unit accounting.
- **Branch 6 (Mental Capital / SOP #58):** Decision unit depletion from repeated decisions is a hidden drain on mental capital. Defaults reduce the depletion rate without requiring G2 floor adjustments.
- **Branch 1 (Trading / SOP #01-#09):** Peak window protection is a prerequisite for trading work. Non-default noise bleeding into peak window is a direct capital risk.

---

## G0: Repeated Decision Audit

**Purpose:** Identify every decision that has occurred more than 3 times in the past 30 days. Each is a default candidate.

**Run:** Initial setup (Day 1). Repeat quarterly.

**Protocol:**

Track for 7 days (or reconstruct from memory if auditing cold):

| Decision | Frequency in last 30 days | Domain | Outcome variance |
|----------|--------------------------|--------|-----------------|
| What to eat (meals) | daily | nutrition | low |
| When to exercise | multiple/week | physical | low |
| Which task to start first | daily | work | low |
| How to respond to routine messages | multiple/week | communication | low |
| When to check notifications | multiple/day | attention | low |

**Classification rule:**
- Frequency ≥ 3×/month AND outcome variance is low (no new information each time) → **Default candidate**
- Frequency ≥ 3×/month AND outcome variance is high (situationally dependent) → **Decision heuristic candidate** (not a hard default, but a trigger-condition rule)
- Novel or genuinely situational → **Keep as live decision**

**Output:** Default candidate list in `memory/life_defaults.md`.

---

## G1: Decision Unit Cost Mapping

**Purpose:** Rank default candidates by decision unit drain — highest cost first.

**Run:** Immediately after G0 audit.

**Scoring per candidate:**

| Factor | Score |
|--------|-------|
| Frequency (×/week) | 1 pt per occurrence |
| Timing (peak window = ×3 multiplier, off-peak = ×1) | multiply base score |
| Friction at decision point (how much deliberation?) | +0 to +3 pts |

**Priority rule:** Any repeated decision consuming peak window time is Priority 1 regardless of total score.

**Output:** Ranked default candidate list. Top 5 become the first conversion targets.

---

## G2: Default Conversion

**Purpose:** Write the defaults. Convert the top 5 candidates from live decisions to pre-written rules.

**Format for each default:**

```
[DEFAULT-ID] [Domain]
Trigger: [what situation fires this default]
Default action: [exact action to take — specific enough to execute without thinking]
Override condition: [the only situations where live judgment replaces the default]
Review date: [quarterly — defaults can become stale]
```

**Examples:**

```
[D-001] Nutrition
Trigger: Meal time (breakfast, lunch, dinner)
Default action: Rotation from fixed menu (Week A / Week B); menu in memory/defaults_nutrition.md
Override condition: Social meal with others; travel outside home base
Review date: quarterly

[D-002] Work start
Trigger: First sit-down of the day
Default action: Open single priority task (pre-selected the evening before); no email/notifications for first 90 min
Override condition: Pre-scheduled external obligation starts within 30 min
Review date: monthly

[D-003] Communication response
Trigger: Non-urgent message arrives
Default action: Batch response at 12:00 and 18:00; no individual-message-prompted responses outside windows
Override condition: Pre-designated urgent-flag senders (list in default file)
Review date: monthly
```

**Write output to:** `memory/life_defaults.md`

**Validation test:** Can you execute the default without making any decision? If yes — it is a working default. If you find yourself deliberating — the trigger condition or action is underspecified. Rewrite.

---

## G3: Peak Window Protection

**Purpose:** Map the physiological peak cognitive window and ensure only high-cognitive work occupies it.

**Run:** Once during initial setup. Re-verify quarterly.

**Peak window identification:**

Step 1: Track subjective cognitive clarity (1–10) at 2-hour intervals for 7 days.

Step 2: Identify the 3–4 hour window that consistently scores highest. This is the peak window. For most people it is 1–3 hours post-waking; verify empirically, do not assume.

Step 3: Classify all recurring task types:

| Task type | Cognitive demand | Slot assignment |
|-----------|-----------------|-----------------|
| Strategy development | High | Peak window only |
| Trade analysis and execution decisions | High | Peak window only |
| Deep reading / learning | High | Peak window only |
| Writing (generative) | High | Peak window only |
| Email / messages | Low | Off-peak only |
| Administrative / logistics | Low | Off-peak only |
| Routine review (checklists) | Low | Off-peak only |
| Social media | Low | Designated slot, not peak |

**Enforcement mechanism (G3 defaults to write):**

```
[D-004] Peak window scheduling
Trigger: Peak window begins (personal time — see identification above)
Default action: Single pre-selected high-cognitive task; no notifications active; no context switches
Override condition: Pre-scheduled external deadline with no rescheduling option
Review date: quarterly — re-verify peak window hasn't shifted

[D-005] Low-cognitive task containment
Trigger: Off-peak window
Default action: Process from low-cognitive task list only; no strategy work, no important decisions
Override condition: None — if decision appears urgent, log it and schedule for peak window next day
Review date: quarterly
```

**Write to:** `memory/life_defaults.md`

**Kill condition:** Any high-cognitive task routinely occurring outside peak window is a G3 breach. Log it. Identify which default failed to block the leak.

---

## G4: Weekly Friction Scan (10 min, Sunday)

**Purpose:** Detect where defaults are being bypassed and where new repeated decisions have appeared.

**Time budget:** 10 minutes hard cap.

**Checklist:**

```
[ ] How many times did I make a decision that has an active default?
    → Log count as "default bypass rate"
    → For each bypass: was the override condition met, or was it friction/forgetting?
[ ] Did any decision appear ≥3 times this week that has no default?
    → Add to default candidate list for next G0 cycle
[ ] Was peak window breached by low-cognitive tasks on any day?
    → Log breach days; identify cause (external interrupt / scheduled conflict / drift)
[ ] Were all batch communication windows honored?
    → If not: what caused the deviation?
[ ] Any default that felt wrong this week?
    → Flag for review — may need override condition update or retirement
[ ] Check decision unit burn rate (subjective): did you feel depleted by logistics before noon?
    → If yes: new default candidate probably emerged this week
```

**Output format for log:**

```
[YYYY-MM-DD] G4 Friction Scan
Default bypass rate: [X] times
New default candidates: [list or none]
Peak window breaches: [X days; cause]
Communication window compliance: [Y/N; cause if N]
Defaults flagged for review: [list or none]
Decision unit burn rate: [low/medium/high]
Status: [Nominal / Degrading / Breach]
```

**Write to:** `memory/life_defaults.md`

---

## G5: Emergency — System Degradation

**Trigger:** Default bypass rate ≥5×/week for 2 consecutive weeks OR decision unit burn rate = High for 5+ consecutive days.

**This is system drift, not a rough week.**

**Response protocol (in order):**

1. **Stop adding new defaults.**
   Running new conversions on a degraded system embeds bad architecture. Freeze the default library until root cause is resolved.

2. **Identify bypass root causes.**
   For each bypassed default this week:
   - Was the trigger condition underspecified? (Rewrite trigger)
   - Was the override condition too broad? (Narrow it)
   - Was the default action ambiguous? (Rewrite to single unambiguous action)
   - Was the default simply forgotten? (Environment cue missing)

3. **Environment audit.**
   For each bypass caused by "forgotten" or "too much friction":
   - Is the default visible at the point of decision? (Written somewhere you see it?)
   - Is the default action more effortful than the non-default action?
   - If the non-default action has less friction than the default → environment redesign required (see MD-324)

4. **Reduce default count.**
   If bypass rate is high, the system may have too many defaults competing for attention. Cut to the 3 highest-value defaults. Run with minimal set for 2 weeks before expanding.

5. **Log G5 event:**
   - Root cause (underspecified / too many defaults / environment friction / external disruption)
   - Structural fix made
   - Next G4 date

**Resume normal operations after:** 2 consecutive weeks with default bypass rate ≤2 and peak window compliance ≥4/5 days.

---

## Integration with Other SOPs

| SOP | Connection |
|-----|-----------|
| SOP #53 (Cognitive Bandwidth) | G0 audit identifies where decision units are being consumed; freed units return to SOP #53's budget |
| SOP #55 (Environment) | G5 environment audit delegates physical environment changes to SOP #55's protocol |
| SOP #58 (Mental Capital) | Decision unit depletion from repeated decisions feeds Mental Capital degradation; defaults reduce drain at source |
| SOP #13 (Personal OS) | This SOP operationalizes the OS concept — defaults ARE the OS; SOP #13 is the architecture intent, SOP #59 is the mechanism |
| SOP #52 (Sleep & Recovery) | Peak window timing is downstream of sleep schedule; SOP #52 controls the input that determines when peak window begins |

---

## Metrics Dashboard

Track in `memory/life_defaults.md`:

| Metric | Target | Actual (update weekly) |
|--------|--------|----------------------|
| Active defaults (written and tested) | ≥5 | — |
| Default bypass rate | ≤2×/week | — |
| Peak window compliance | ≥4/5 days | — |
| Communication window compliance | ≥4/5 days | — |
| Decision unit burn rate by noon | Low | — |
| New default candidates this week | Track | — |
| G5 events (lifetime) | 0 | — |

---

## Failure Modes

| Failure | Symptom | Gate that catches it |
|---------|---------|---------------------|
| Default bypass without override condition | Deliberating on a solved problem | G4: bypass rate |
| Peak window invaded by low-cognitive tasks | Strategic work compressed into off-peak | G3 breach / G4 scan |
| Too many defaults (system overload) | High bypass rate despite compliant environment | G5: cut to minimal set |
| Default trigger underspecified | Same decision appearing multiple times despite active default | G4 + G5 rewrite |
| Environment not reinforcing defaults | Friction for optimal behavior higher than non-optimal | G5 environment audit |
| No defaults updated as life phase changes | Old defaults firing in wrong contexts | Quarterly G0 re-audit |

---

## Quick Reference Card

```
G0 (quarterly): Audit all repeated decisions. Classify by frequency + outcome variance.
G1 (quarterly): Rank default candidates by decision unit cost. Top 5 first.
G2 (setup + as needed): Write the defaults. Trigger + Action + Override + Review date.
G3 (setup + quarterly): Map peak window. Classify all task types. Protect peak window with defaults.
G4 (Sunday 10 min): Bypass rate? New candidates? Peak window compliance? Communication windows? Any defaults feeling wrong?
G5 (emergency): Bypass rate ≥5/week for 2 weeks. Freeze new defaults. Find root cause. Environment audit. Cut to minimal set.
```
