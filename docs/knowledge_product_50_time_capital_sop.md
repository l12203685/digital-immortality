# SOP #50: Time Capital & Priority Triage Protocol
> 2026-04-09 UTC cycle 211 — How to treat time as the only non-renewable capital asset, and protect it through pre-committed allocation, structured triage, and weekly review loops.

**DNA Anchors:** MD-322 (>3× same decision = system failure; pre-commit) / MD-323 (peak window = high-cognition tasks only) / MD-324 (environment design > willpower) / MD-1 (read derivative not level) / MD-142 (bandwidth cap = hard system limit) / MD-108 (meta-strategy when object-level stuck ≥3 cycles) / MD-112 (write kill condition before entry)

---

## Why This Matters

Every financial model discounts for time value of money. Almost no one discounts for the time value of attention. The result: high-performers consistently over-invest in low-EV activities because the cost is invisible until it compounds into opportunity cost.

Unlike money, time cannot be earned back, borrowed forward, or leveraged. It is the one resource where the Kelly criterion has no useful application — you can only allocate what you have, you cannot raise the bankroll.

This SOP replaces reactive scheduling with pre-committed capital allocation.

---

## The 5-Gate Protocol

### G0 — Time Reclassification

*"Every unrecorded hour is capital leakage, not lost time." — MD-322 extension*

Before any priority decision, reclassify the vocabulary:

| Common Label | Correct Label |
|--------------|---------------|
| "Free afternoon" | Unallocated capital — assign or defend |
| "Quick favor" | Unpriced commitment with unknown cost |
| "Just a meeting" | Peak-window extraction if scheduled 09:00–13:00 |
| "I'll deal with it later" | Time debt — must be tracked like financial debt |
| "Staying busy" | Capital deployed at unknown yield — audit required |

**Time debt** = total hours committed this week minus total hours available for committed work.  
Formula: `time_debt = Σ(commitments) − (weekly_capacity − maintenance_floor)`  
Maintenance floor = sleep + meals + transit + minimum hygiene ≈ 70 hrs/week.  
If `time_debt > 8 hrs/week` → OVERCOMMITTED state → invoke G4 immediately.

Kill condition: Any week with `time_debt > 16 hrs` = structural overcommit. System redesign required, not personal effort.

---

### G1 — Peak Window Lock

*"High-cognition tasks belong only in the biological peak window." — MD-323*

Allocate the day in three tiers before any scheduling request arrives:

| Tier | Window | Permitted work |
|------|--------|----------------|
| Peak | First 3–4 hrs after full alertness (typically 09:00–13:00) | Strategy, writing, analysis, complex decisions, creative output |
| Off-peak | 13:00–17:00 | Execution, email, scheduling, calls, routine review |
| Recovery | 17:00+ | Input consumption, low-stakes social, physical maintenance |

**Contamination rule**: Any deep-work task moved to off-peak produces ≈40% the output in ≈150% the time. This is not a feeling — it is a throughput cost.

Gate check: Is this scheduling request targeting a peak-window slot?  
- YES → reject by default unless it generates ≥3× the EV of displaced deep work  
- NO → proceed normally

Pre-commit: Peak window is **not negotiable in-the-moment**. The commitment exists before anyone asks.

---

### G2 — Priority Triage Matrix

*"Name the edge or default to inaction." — MD-96, applied to time allocation*

Before accepting any commitment, run the 2×2 triage:

|  | High effort | Low effort |
|--|-------------|------------|
| **High EV** | Schedule explicitly (block time, no interrupt) | Do immediately |
| **Low EV** | **DROP or delegate** | Batch or ignore |

EV assessment questions:
1. Will this compound positively on a 1-year horizon? (YES = keep)
2. Is this the only path to this outcome? (NO = defer until best path identified)
3. Am I the only person who can do this? (NO = delegate or drop)
4. Does this create options or foreclose them? (foreclose = elevated scrutiny)

**Top-3 pre-commitment rule (from MD-322)**: Identify the 3 highest-EV activities the night before. Any request that would displace a Top-3 item requires named EV justification before acceptance. No in-the-moment negotiation.

---

### G3 — Time Debt Audit

*"Bandwidth cap is a hard limit. Pretending otherwise doesn't raise the limit." — MD-142*

Weekly audit trigger: any week where actual output < planned output for 2+ consecutive days.

Audit steps:
1. List all active commitments (recurring + one-time)
2. Calculate total committed hours vs available non-maintenance hours
3. Identify all implicit commitments (things you'll feel obligated to do)
4. Compute `time_debt_ratio = committed ÷ available`

| Ratio | State | Response |
|-------|-------|----------|
| <0.7 | Healthy slack | Normal operations |
| 0.7–0.9 | Tight | Freeze new commitments for 2 weeks |
| 0.9–1.1 | OVERCOMMITTED | Cancel/defer 20% of lowest-EV commitments immediately |
| >1.1 | SYSTEM FAILURE | G4 mandatory; no new commitments until ratio <0.8 |

Implicit commitment trap: social obligations, weak-tie maintenance requests, and low-signal meetings are the main hidden sources of time debt. They don't feel like commitments until they demand time at the worst moment.

---

### G4 — Reclaim Protocol

*"Meta-strategy: when object-level is stuck ≥3 cycles, escalate." — MD-108*

When G3 signals OVERCOMMITTED or SYSTEM FAILURE:

**Step 1 — Cancel/defer first** (not compress):
- Identify the 3 lowest-EV commitments in current week
- Cancel or defer with minimum friction (one-sentence message)
- Default framing: "Rescheduling to [specific date]" — not "I'm busy"

**Step 2 — Compress what remains** (explicit quality tradeoff):
- For each remaining commitment: name the minimum viable output
- Do not compress peak-window deep work — compress off-peak admin tasks only
- "Good enough" is a valid output spec when time debt is being resolved

**Step 3 — Raise the no-default**:
- After reclaim event: install a 2-week "no new commitments" circuit breaker
- Any incoming request during circuit breaker period → "I'll respond in 2 weeks"
- This is not rudeness; it is system maintenance

Priority order for reclaim:
1. Revenue-generating activities → protect first
2. Skill-building (compounding, not immediately monetized) → protect second
3. Maintenance obligations → compress
4. Social obligations without named EV → cancel/defer first

---

### G5 — Weekly Review Trigger

*"Output forcing function: if you can't report it, you didn't do it." — MD-319 extension*

Every Sunday (or last working day of week), 20-minute structured review:

**Review questions (in order):**
1. What % of my time went to Top-3 priority items? (Target: ≥60%)
2. What was done that I wouldn't agree to again? → pre-commit the reverse
3. What implicit commitment consumed time without being planned? → name it + decide
4. What is the 3-item top-priority list for next week? → write before closing

**Rolling 4-week tracking:**

| Week | % High-EV | Time debt (hrs) | Peak contamination events |
|------|-----------|-----------------|--------------------------|
| W-4  | — | — | — |
| W-3  | — | — | — |
| W-2  | — | — | — |
| W-1  | — | — | — |

Kill conditions:
- ≥3 consecutive weeks below 40% high-EV → L3 evolution event: fundamental life-design review, not a scheduling fix
- Peak window contaminated >2×/day consistently → environment redesign required (SOP #32 G3)
- Time debt never resolves below 0.8 ratio → commitments exceed sustainable capacity; structural reduction needed

---

## Self-Test

**Scenario**: Week with 3 deep-work sessions, 12 social requests (3 coffee, 5 messages requiring real thought, 4 "quick call"), 2 major deliverables due.

**Run the protocol:**
- G0: Map all social requests as uncommitted capital asks
- G1: All coffees → off-peak only; deep-work sessions → peak window locked
- G2: Triage all 12 social requests → 2 high-EV (keep), 4 medium (batch to 1 session), 6 low-EV (defer/drop)
- G3: `time_debt = 22h committed ÷ 28h available = 0.79` → TIGHT → freeze new requests 2 weeks
- G4: Cancel 4 of the 6 low-EV social items immediately, defer 2 to next month
- G5: End of week: %High-EV = 64% ✓; 2 implicit commitments identified → pre-committed reverse for next week

**Result**: 2 major deliverables completed at full quality; peak window intact; social relationships not damaged (deferrals with specific reschedule dates).

---

## Complements

- **SOP #13** (Personal OS): G0 decision audit, G3 environment design → this SOP is the time-allocation layer SOP #13 doesn't fully cover
- **SOP #32** (Cognitive Capital): G1 peak window, G3 environment → complements but doesn't allocate across the week
- **SOP #22** (Universal Exit Protocol): pre-commit kill conditions before entry → apply same logic to time commitments
- **SOP #46** (Async Communication): message triage → reduces implicit time debt from communications
