# SOP #52 — Sleep & Physical Recovery Protocol
> Domains: 8 (生活維護)
> Timestamp: 2026-04-09T06:00:00Z (cycle 213)
> Backing MDs: MD-89/48/144/12/53
> Status: COMPLETE ✅

---

## The Problem

Sleep and physical recovery are classified as Maintenance in SOP #51's time audit — not Compounding. This is a mistake that compounds in the wrong direction.

Cognitive degradation from insufficient sleep is nonlinear: the first 24h of mild deprivation produces a 25% drop in executive function. By 36h, decision quality resembles clinical impairment. The person experiencing this does not feel impaired — they feel merely tired. This asymmetry is the failure mode.

The structural problem: sleep is the first thing traded away under time pressure, and the last thing restored when capacity returns. Result: chronic partial deprivation masquerading as normal operation, while every downstream task (trading decisions, content quality, calibration accuracy) degrades invisibly.

This SOP applies MD-12 (look at derivatives, not levels) to sleep: the question is not "how tired do I feel?" but "what is my cognitive performance trajectory over the past 5 days?"

---

## Core Framework: Recovery as System Infrastructure

**MD-89**: First-pass quality of any prototype (article, strategy, decision) should be achievable in ≤1 day. If it routinely takes longer, the constraint is not time — it is cognitive bandwidth. Sleep debt is a hidden bandwidth tax.

**MD-48**: Knowledge requires time density. Dense observation requires full cognitive presence. Partial presence (from sleep debt) means observations are made but not integrated — information loss at the processing layer, not the input layer.

**MD-144**: Monitoring bandwidth has an absolute ceiling. Sleep deprivation compresses this ceiling. The number of signals you can track simultaneously drops by approximately 30% after two nights of 6h sleep.

**MD-53**: Career EV = output / hours. Sleep debt reduces the numerator (output quality) while the denominator (hours) stays constant. The result is negative-EV time — hours that feel productive but produce degraded work that must be redone.

**MD-12**: Look at the derivative. If decision quality, article coherence, or trading review depth has been declining for 5+ days, the cause is almost certainly recovery deficit, not knowledge deficit.

---

## 5-Gate Protocol

### G0 — Recovery Audit: Classify Sleep Quality (5 min, daily)

Self-measurement before work begins. Two signals:

| Signal | Green | Yellow | Red |
|--------|-------|--------|-----|
| Hours in bed | ≥7.5h | 6–7.5h | <6h |
| Morning cognitive clarity | Can reason abstractly within 20 min | Foggy for 30–60 min | Foggy >60 min or impaired judgment |

**Self-test**: Rate the last 3 nights. If 2+ nights are Yellow or Red → G5 emergency protocol.

**Kill condition**: Three consecutive nights with <6h or persistent Red clarity → declare recovery emergency. No major decisions, no trading parameter changes, no DNA edits until resolved.

---

### G1 — Performance Trajectory Scan (2 min, daily)

Not "how tired do I feel?" — that signal is corrupted by adaptation. Instead:

1. Compare yesterday's first-pass work quality to the 7-day average.
2. Did complex reasoning (trading strategy review, article structure, calibration decisions) take significantly longer or produce shallower output?
3. Did reactive/emotional responses increase? (Irritability, avoidance, binary thinking = executive function proxy)

**Rule**: Two consecutive days of trajectory decline without external cause → primary suspect is sleep/recovery.

**MD-12 applied**: The derivative of performance over days is more reliable than a single-day measurement.

---

### G2 — Recovery Budget Allocation (fixed daily commitment)

Two non-negotiable blocks:

| Block | Duration | Rule |
|-------|----------|------|
| **Core Sleep** | 7–8h | Fixed window, non-negotiable. Cannot be compressed for deadlines — compressing it is borrowing against tomorrow's performance at compound interest. |
| **Physical Reset** | 20–30 min | Movement, sunlight, or deliberate rest. Not optional during high-cognitive-load periods. |

**Scheduling rule**: Set sleep window in calendar as a hard constraint, not a target. If a deadline conflicts with sleep window → the deadline is wrong, not the sleep window. Reschedule the work, not the recovery.

---

### G3 — Context-Switching Cost Gate (applies to recovery, not just work)

Sleep quality degrades under two conditions:
1. Cognitive arousal within 60 min of sleep window (unresolved tasks, stimulating content, open loops)
2. Irregular sleep/wake timing (±90 min across the week = phase shift equivalent to mild jet lag)

**Protocol**:
- 60 min before sleep: open loops → written to session_state.md. Captured = closed cognitively.
- Irregular timing: accept ±30 min variance, flag ±60 min, intervene at ±90 min.
- Morning alarm: fixed time regardless of sleep debt. Compensate via earlier bedtime, not later alarm.

---

### G4 — Weekly Recovery Review (15 min, Sunday)

Alongside SOP #51's G4 (weekly time reallocation):

1. Count Red/Yellow nights in the past week.
2. If ≥3 Yellow or ≥1 Red: identify cause. Categories:
   - **Structural** (schedule has no room for 7.5h) → fix G2 allocation
   - **Behavioral** (late-night stimulation, irregular timing) → fix G3 protocol
   - **External** (travel, illness, acute stress) → accept, plan recovery week
3. If performance trajectory (G1) was declining this week: cross-reference with sleep log.

**Metric**: Target 6+ Green nights per week. Two consecutive weeks below 5 Green → structural problem requiring SOP #51 G5 cascade.

---

### G5 — Recovery Emergency Protocol

Triggered by: Compounding < 30% (from SOP #51) AND ≥3 Red nights in 7 days.

1. **Declare recovery priority**: Sleep window becomes the highest-derivative activity. All other branches deprioritized for 5 days.
2. **Debt payback**: Add 1h to sleep window for 5 days. Do not compress to "catch up in one night" — the debt is not linear.
3. **Stimulant audit**: Map last 7 days of caffeine, screen time, and sleep timing. Identify the proximate cause.
4. **Performance freeze**: No major decisions, no trading parameter changes, no DNA edits until 3 consecutive Green nights achieved.
5. **Re-entry**: Run G0 audit. If 3+ Green → resume normal queue. Log recovery event in daemon_log.md.

---

## Integration with Three-Layer Loop

| Layer | Recovery touchpoint |
|-------|---------------------|
| L1 Execute | Physical capacity to run the daemon (sleep = uptime) |
| L2 Evaluate | Review quality (degraded sleep → degraded evaluation → L2 misclassifies drift as progress) |
| L3 Evolve | DNA edits require full cognitive presence — no L3 changes during recovery emergency |

**Critical**: L2 evaluation under sleep debt produces false negatives (misses drift, accepts lower quality output). This means recovery debt propagates undetected into system quality before it's visible. Prevention > correction.

---

## Anti-Patterns

| Pattern | Why it fails |
|---------|-------------|
| "I'll sleep when the deadline is done" | The deadline requires the cognition the sleep deprivation is destroying |
| "I only need 6h" | True for ~3% of population. Likelihood you are in that group = unlikely. |
| Nap as compensation | Naps address acute sleepiness, not accumulated sleep debt. Not a substitute for G2. |
| "I feel fine" | Adaptation masks subjective impairment while objective impairment accumulates. Use trajectory (G1), not feeling. |
| Recovery = laziness | The system running on degraded hardware is the waste. Recovery is maintenance of the execution layer. |

---

## Key Metrics

| Metric | Target |
|--------|--------|
| Green nights / week | ≥6 |
| Morning clarity score | Green within 20 min ≥5 days/week |
| G5 triggers / month | 0 |
| Recovery debt duration | ≤3 days when it occurs |
