# SOP #58 — Mental Capital & Psychological Resilience Protocol

**Domain 6: Mental Capital / Psychological Resilience**
**Status:** Active
**Version:** 1.0
**Dependencies:** SOP #52 (Sleep & Recovery), SOP #53 (Cognitive Bandwidth), SOP #47 (Engine Health), SOP #56 (FIRE Protocol)

---

## Why This SOP Exists

SOP #52 monitors sleep. SOP #53 manages cognitive bandwidth. Neither addresses the upstream variable that determines whether both matter: the baseline psychological state from which all decisions are made.

The gap: you can sleep 8 hours, protect your decision units, and still make systematically poor calls — because the degradation is psychological, not physiological. Emotional reactivity distorts signal reading. Sustained low mood narrows the solution space. Decision quality drops without a visible cause.

Mental capital is the asset beneath all other assets. A degraded trader with a working strategy loses money. A sharp mind with an imperfect strategy survives and improves. The hierarchy is not ambiguous.

This SOP formalizes measurement and maintenance of the psychological substrate:

```
State Audit → Derivative Scan → Non-Negotiable Budget → Quarterly Intervention → Weekly Review → Emergency Protocol
```

Completion signal: decision quality rate improves over 90 days. Not "I feel better." Not "I meditated this week."

---

## Three-Layer Architecture

| Layer | Gate | Function |
|-------|------|----------|
| L1 | G2 | Psychological budget enforcement — minimum viable state maintenance |
| L2 | G0/G1 | Continuous audit — is the mental substrate healthy? |
| L3 | G3 | Quarterly intervention scan — highest-EV psychological leverage |

L1 runs every session. L2 runs every week (G0) and derivative-tracks trend (G1). L3 runs every quarter.

---

## DNA Anchors

| MD | Principle | How it applies here |
|----|-----------|---------------------|
| MD-12 | Default gravity | Without L1 enforcement, mental state drifts to degraded baseline |
| MD-48 | Pattern extraction | Emotional reactivity events are signals, not noise — extract the pattern |
| MD-89 | Recursion | Each cycle's mental state is input to next cycle's decision quality |
| MD-67 | System | Psychological resilience is a system; it requires gates not mood management |
| MD-144 | Sensor management | State audit accuracy ≥ state audit frequency |

---

## Branch Connections

- **Branch 1.1** — Trading decision quality: every bad call in degraded state is a direct capital loss traceable to mental capital deficit.
- **Branch 3.1** — Recursive engine clarity: engine output quality is bounded by the clarity of the substrate running it. Degraded state = degraded recursion.
- **Branch 6** — Cold-start mental state: boot test pass rate is partially a function of the mental state at session start. G0 must be checked at cold-start.

---

## G0: Mental State Audit

**Purpose:** Measure whether the psychological substrate is operational.

**Run:** Weekly (Sunday, 10-min review — see G4)

**Three signals:**

| Signal | Measure | Green | Yellow | Red |
|--------|---------|-------|--------|-----|
| Decision quality rate | Bad calls / total decisions this week (bad = later judged clearly wrong) | ≤1/week | 2 | ≥3/week |
| Emotional reactivity events | Unplanned reactive responses (anger, panic, avoidance) per week | 0–1 | 2 | ≥3/week |
| Baseline mood score | Self-rated 1–10, 7-day average (morning assessment before any input) | ≥7 | 5–6 | ≤4 |

**Kill condition:** Decision quality rate ≥3 bad calls/week sustained for 2 consecutive weeks → skip to G5 immediately.

**Output:** One of: Green / Yellow / Red per signal. Log in `memory/mental_capital_audit.md`.

---

## G1: Derivative Scan

**Purpose:** Detect trend direction before it becomes a kill condition.

**Run:** Weekly alongside G0.

**Three derivatives:**

| Derivative | Calculation | Healthy signal |
|------------|-------------|----------------|
| ΔDecision quality | Bad call rate this week vs. 4-week average | Stable or improving |
| ΔEmotional reactivity | Events this week vs. 4-week average | Stable or declining |
| ΔCreative output rate | Generative sessions (non-reactive, exploratory thinking) this week vs. 4-week average | Stable or increasing |

**Interpretation:**
- All three trending positive → substrate healthy, continue L1
- Any derivative negative for 2+ consecutive weeks → investigate G2 compliance or trigger cause
- ΔCreative output rate = 0 for 4 weeks → L3 trigger (intervention scan)

**Output:** Log derivative trend in `memory/mental_capital_audit.md` alongside G0 signals.

---

## G2: Non-Negotiable Psychological Budget (L1)

**Purpose:** Minimum viable state maintenance. Non-negotiable. These are not aspirations — they are floor constraints on decision-making capacity.

**Frequency:** Per session / per week

**Constraints:**

1. **No major decisions in degraded state**
   - Degraded = any G0 signal in Red
   - "Major decision" = capital allocation, relationship commitments, strategy changes, L3 edits
   - If degraded and decision is time-sensitive: delay 24h or route to pre-written protocol (no live judgment)
   - If delay is impossible: flag the decision as degraded-state call, review within 48h

2. **Minimum decompression time after stress events**
   - Stress event = any experience with sustained cortisol response (conflict, loss, high-stakes outcome, sustained uncertainty)
   - Mandatory: ≥2h non-productive time before re-engaging analytical work
   - "Non-productive" = no screens, no content consumption, no problem-solving. Movement, sleep, or unstructured silence count.
   - Skipping decompression after a stress event is a G2 violation — log it

3. **Mood maintenance protocol (weekly minimums)**
   - Sleep: ≥7h average (tracked — see SOP #52 for protocol)
   - Movement: ≥4 sessions/week of any duration ≥20 min
   - Solitude quota: ≥2h/week of unstructured, unconnected time (no input, no agenda)
   - These three are the maintenance floor. Below any one → Yellow signal regardless of G0 mood score

4. **Every reactive event gets logged, not suppressed**
   - Log: [date | trigger | response | was it regrettable?]
   - Do not analyze in the moment — log only
   - Analysis happens in G4 weekly review, not at the time of the event
   - Suppression without logging is a G2 violation

**Enforcement:** If any G2 constraint is missed → log miss in `memory/mental_capital_audit.md` → treat as Yellow signal in G0 next review.

---

## G3: Quarterly Leverage Scan (L3)

**Purpose:** Find the highest-EV psychological intervention for the current life phase. Most interventions have diminishing returns after 90 days. New interventions compound early.

**Frequency:** Once per quarter (January, April, July, October)

**Protocol:**

1. List all active psychological maintenance practices with 90-day stats:
   - Practice name / type (meditation, therapy, journaling, environment change, social structure change)
   - Sessions per week
   - Estimated ΔDecision quality contribution (subjective, 1–5)
   - Estimated ΔEmotional reactivity reduction (subjective, 1–5)

2. Rank by decision quality impact per time invested, not subjective comfort

3. Identify candidate intervention:
   - Must have structural reason to produce ΔDecision quality ≥+10% over 90 days
   - Examples: structured journaling (pattern extraction from reactive events), therapy (trained external calibration), meditation protocol (sustained attention training), environment restructure (remove high-reactivity triggers)
   - "Interesting" or "feels good" are not structural reasons

4. **Isolated 90-day trial:**
   - Run candidate as addition to (not replacement of) existing G2 floor
   - Track: ΔDecision quality rate = (bad calls/week before) vs. (bad calls/week at day 90)
   - Threshold: ΔDecision quality ≥+10% improvement → write intervention to permanent protocol in `memory/mental_capital_audit.md`
   - Below threshold: archive — do not extend trial based on subjective improvement

5. **Practice retirement:**
   - Any practice with <1 subjective impact rating for 90 days → archive
   - Log retirement reason: plateaued / consumed fully / superseded / wrong phase

**Output:** Quarterly intervention log entry in `memory/mental_capital_audit.md`.

---

## G4: Weekly Review (10 min, Sunday)

**Purpose:** Lightweight weekly audit. Catches degradation before kill condition.

**Time budget:** 10 minutes hard cap.

**Checklist:**

```
[ ] G0: Count bad decisions this week (later-judged clearly wrong)
[ ] G0: Count emotional reactivity events (unplanned reactive responses)
[ ] G0: 7-day average mood score (morning, pre-input)
[ ] G1: Decision quality trending vs. last 4 weeks?
[ ] G1: Reactivity trending vs. last 4 weeks?
[ ] G1: Creative output sessions this week vs. last 4 weeks?
[ ] G2: Sleep compliance (≥7h average)?
[ ] G2: Movement compliance (≥4 sessions)?
[ ] G2: Solitude quota met (≥2h unstructured)?
[ ] Log: 3 signals + 3 derivatives → memory/mental_capital_audit.md
[ ] Action: If any Red signal → set G5 watch for next session
[ ] Action: If any Yellow signal → identify root cause (sleep deficit? stress event unprocessed? G2 violation?)
```

**Output format for log:**
```
[YYYY-MM-DD] G4 Review
G0: bad_calls=[X]/week | reactivity_events=[X]/week | mood_avg=[X]/10
G1: decision_trend=[+/-/=] | reactivity_trend=[+/-/=] | creative_trend=[+/-/=]
G2: sleep=[compliant/miss] | movement=[compliant/miss] | solitude=[compliant/miss]
Status: [Green/Yellow/Red]
Action: [none / investigation / G5 watch / G5 trigger]
```

---

## G5: Emergency — Degraded Decision Quality

**Trigger:** Decision quality rate ≥3 bad calls/week for 2 consecutive weeks (G0 kill condition met).

**This is a system failure state, not a rough patch.**

**Response protocol (in order, no skipping):**

1. **Halt trading immediately**
   - No new positions. No strategy changes. Existing positions: manage by pre-written rules only, no live judgment.
   - Duration: until G0 returns to Green ×2 consecutive sessions.
   - Rationale: degraded mental capital in a trading context produces compounding losses. Preservation is the only objective.

2. **Income-first recovery mode**
   - Redirect all cognitive capacity to income stability (employment, existing clients, baseline obligations)
   - No new ventures, no new commitments, no resource allocation decisions during G5
   - The goal is to eliminate external pressure that is compounding the degradation

3. **No L3 edits until G0 Green ×2 sessions**
   - No quarterly intervention trials
   - No protocol changes
   - No DNA edits
   - Degraded-state system edits produce degraded systems. Lock the architecture.

4. **Force-run G2 floor for 14 days**
   - Sleep: enforce ≥7h regardless of workload
   - Movement: enforce ≥4 sessions/week regardless of schedule
   - Solitude: enforce ≥2h/week regardless of social pressure
   - Decompression: enforce after every stress event without exception
   - Do not add anything. Do not optimize. Run the floor.

5. **Log one diagnostic entry explaining root cause:**
   - Was it sustained sleep deficit?
   - Was it unprocessed stress accumulation (skipped decompression)?
   - Was it G2 violations compounding (missed floor maintenance)?
   - Was it an external life event overloading the system?
   - Root cause drives the post-G5 structural fix

6. **G0 returns to Green** when: ≥2 consecutive weekly reviews with decision quality rate ≤1 bad call/week AND mood average ≥7

**Post-G5:** After 2 Green G0 sessions, resume L1/L2 normal operations. Log G5 event as correction → write 1 boot test case so cold-start catches same failure pattern. Treat as high-priority G3 input for next quarterly scan.

---

## Integration with Other SOPs

| SOP | Connection |
|-----|-----------|
| SOP #52 (Sleep & Recovery) | G2 sleep constraint delegates measurement to SOP #52's tracking protocol |
| SOP #53 (Cognitive Bandwidth) | G0 decision quality and G2 no-decisions-while-degraded gate interact with SOP #53's decision unit budget |
| SOP #47 (Engine Health) | G5 halt condition mirrors SOP #47's engine restart protocol — both freeze changes until baseline is restored |
| SOP #56 (FIRE Protocol) | G5 halts trading; FIRE trajectory holds during G5 — capital is preserved, not deployed |
| SOP #57 (Knowledge Integration) | Degraded mental state (G0 Red) invalidates new DNA edits — L3 locked per G5 constraint #3 |

---

## Metrics Dashboard

Track in `memory/mental_capital_audit.md`:

| Metric | Target | Actual (update weekly) |
|--------|--------|----------------------|
| Bad decisions per week | ≤1 | — |
| Emotional reactivity events/week | 0–1 | — |
| Baseline mood score (7-day avg) | ≥7/10 | — |
| Sleep compliance rate | ≥7h/night average | — |
| Movement compliance | ≥4 sessions/week | — |
| Solitude quota compliance | ≥2h/week | — |
| G5 events (lifetime) | 0 | — |
| Current intervention (G3) | — | — |
| Intervention ΔDecision quality | ≥+10% | — |

---

## Failure Modes

| Failure | Symptom | Gate that catches it |
|---------|---------|---------------------|
| Degraded-state decisions | Bad calls increasing, unrecognized | G0 red: decision quality rate |
| Reactive event suppression | Tension accumulating without log entry | G2 constraint #4 |
| Decompression skipped | Stress layering without discharge | G2 constraint #2 |
| G2 floor abandonment | Sleep/movement/solitude below floor | G0 yellow: mood score drops |
| Intervention plateau | Practice continues past useful life | G3: low impact rating |
| Degradation misread as normal | 2-week Red seems like "life is hard" | G0 kill condition → G5 |
| L3 edits in degraded state | Protocol changes made while impaired | G5 constraint #3 |

---

## Quick Reference Card

```
G0 (weekly): Is the substrate operational? 3 signals.
G1 (weekly): Is it improving? 3 derivatives.
G2 (every session): Am I above floor? No degraded-state decisions. Decompress after stress. Sleep + movement + solitude quota.
G3 (quarterly): What's the highest-EV intervention? 90-day isolated trial. ΔDecision quality ≥+10% → write to protocol.
G4 (Sunday 10 min): 9-item checklist + log entry.
G5 (emergency): Degraded ≥2 weeks. Halt trading. Income-first. No L3 edits. Run G2 floor 14 days. 2× Green before resuming.
```
