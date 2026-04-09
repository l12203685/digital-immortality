# SOP #57 — Knowledge Integration Pipeline

**Domain 3: 持續學習 (Continuous Learning)**
**Status:** Active
**Version:** 1.0
**Dependencies:** SOP #47 (Engine Health), SOP #48 (Bayesian Update), SOP #50 (L3 System Evolution)

---

## Why This SOP Exists

SOP #47 monitors recursive engine health. SOP #48 formalizes how to update beliefs. Neither closes the loop from raw input to behavioral change.

The gap: you can read, absorb, and even update a belief — and still make the same decisions next month. Learning without behavioral output is consumption, not integration.

This SOP formalizes the full pipeline:

```
Raw Input → Extract Essence → Cross-Validate → Write to DNA → Distillation → Behavioral Verification
```

Completion signal: boot test pass rate improves. Not "I read something." Not "I wrote a note."

---

## Three-Layer Architecture

| Layer | Gate | Function |
|-------|------|----------|
| L1 | G2 | Learning budget enforcement — minimum viable input |
| L2 | G0/G1 | Continuous audit — is the pipeline flowing? |
| L3 | G3 | Quarterly source rotation — highest-EV input discovery |

L1 runs every session. L2 runs every week (G0) and derivative-tracks trend (G1). L3 runs every quarter.

---

## DNA Anchors

| MD | Principle | How it applies here |
|----|-----------|---------------------|
| MD-89 | 遞迴 (Recursion) | Every learning session feeds next session's input |
| MD-48 | Pattern extraction | Essence extraction discipline — structure over volume |
| MD-12 | Default gravity | Without L1 enforcement, the system drifts to zero input |
| MD-144 | Sensor management | Input source quality ≥ input source quantity |
| MD-67 | System | Integration pipeline is a system; it requires gates not willpower |

---

## Branch Connections

- **Branch 2.2** — Micro-decision learning: 330 MDs complete. Each new MD must pass G2 before commit.
- **Branch 3.1** — Recursive engine: Output(t) is valid input for this pipeline. Engine output counts as raw input.
- **Branch 3.2** — Correction pipeline: every correction event must generate ≥1 boot test case before closing.

---

## G0: Input Audit

**Purpose:** Measure whether the learning pipeline is alive.

**Run:** Weekly (Sunday, 10-min review — see G4)

**Three signals:**

| Signal | Measure | Green | Yellow | Red |
|--------|---------|-------|--------|-----|
| Input freshness | Days since last new source consumed | ≤7 | 8–14 | >14 |
| Extraction rate | Insights extracted per session (MDs or distillation entries) | ≥3 | 1–2 | 0 |
| Behavioral change rate | DNA (MD) updates per month | ≥2 | 1 | 0 |

**Kill condition:** Behavioral change rate = 0 for 30 consecutive days → skip to G5 immediately.

**Output:** One of: Green / Yellow / Red per signal. Log in `memory/knowledge_audit.md`.

---

## G1: Derivative Scan

**Purpose:** Detect trend direction before it becomes a kill condition.

**Run:** Weekly alongside G0.

**Three derivatives:**

| Derivative | Calculation | Healthy signal |
|------------|-------------|----------------|
| ΔInput quality/week | Avg insight density this week vs. last 4 weeks | Stable or increasing |
| ΔExtraction efficiency | Insights per hour of input time | Stable or increasing |
| ΔBehavioral alignment | Are new MDs changing actual decisions? (track: last 5 decisions against relevant MDs) | ≥1 decision influenced per month |

**Interpretation:**
- All three trending positive → pipeline healthy, continue L1
- Any derivative negative for 2+ consecutive weeks → investigate source quality or extraction discipline
- ΔBehavioral alignment = 0 for 4 weeks → L3 trigger (source rotation)

**Output:** Log derivative trend in `memory/knowledge_audit.md` alongside G0 signals.

---

## G2: Non-Negotiable Learning Budget (L1)

**Purpose:** Minimum viable pipeline activity. Non-negotiable. These are not targets — they are floor constraints.

**Frequency:** Per session / per month

**Constraints:**

1. **≥1 JSONL session per month** (or equivalent raw input: book, paper, conversation log, podcast transcript)
   - "Equivalent" = structured source with extractable content, not passive consumption
   - JSONL = own conversation archive; highest-density input available

2. **≥1 DNA update (MD) per learning session**
   - A session with zero MD output is consumption, not integration
   - If no MD emerges naturally: force extraction — find 1 principle from the session worth encoding

3. **Every correction event → boot test case + distillation entry**
   - Correction = any moment Edward's decision differed from what he would later judge correct
   - Boot test case: add to `templates/` so cold-start catches same failure mode
   - Distillation entry: write to `memory/distillation.md` with: [date | context | old pattern | new pattern | MD reference]

4. **Every session ends with persist, not display**
   - No session ends with "here's what I learned" without a git push
   - Output that isn't pushed is lost on cold-start → dead learning
   - Minimum persist: `git add -A && git commit -m "learn: [summary]" && git push`

**Enforcement:** If any G2 constraint is missed → log miss in `memory/knowledge_audit.md` → treat as Yellow signal in G0 next review.

---

## G3: Quarterly Leverage Scan (L3)

**Purpose:** Find highest-EV input sources. Most sources decay. New sources compound early.

**Frequency:** Once per quarter (January, April, July, October)

**Protocol:**

1. List all active input sources with 90-day extraction stats:
   - Source name / type
   - Sessions consumed
   - MDs generated
   - Decisions influenced (behavioral alignment count)

2. Rank by MDs-per-session (extraction density), not volume consumed

3. Identify candidate new source:
   - Must have structural reason to be high-density (not just "interesting")
   - Examples: conversation archive with high-disagreement organism, adversarial paper in domain with active belief, JSONL batch from high-stakes period

4. **Isolated 30-day trial:**
   - Run candidate source alongside (not replacing) current sources
   - Track: ΔAlignment = boot test pass rate delta after 30 days
   - Threshold: ΔAlignment ≥+5% → write source to permanent input queue

5. **Source retirement:**
   - Any source with 0 MDs in 90 days → archive, remove from active queue
   - Log retirement reason: decayed / consumed fully / superseded

**Output:** Quarterly source rotation log entry in `memory/knowledge_audit.md`.

---

## G4: Weekly Review (10 min, Sunday)

**Purpose:** Lightweight weekly audit. Catches decay before kill condition.

**Time budget:** 10 minutes hard cap.

**Checklist:**

```
[ ] G0: Count inputs read this week (sessions / sources)
[ ] G0: Count insights extracted (MDs written or updated)
[ ] G0: Count DNA updates this month (running total)
[ ] G1: Is extraction rate stable vs. last 4 weeks?
[ ] G1: Did any new MD influence a decision this week?
[ ] Log: 3 signals + 2 derivatives → memory/knowledge_audit.md
[ ] Action: If any Red signal → set G5 trigger for next session
[ ] Action: If any Yellow signal → identify root cause (source quality? extraction discipline? time?)
```

**Output format for log:**
```
[YYYY-MM-DD] G4 Review
G0: freshness=[X]d | extraction=[X]/session | MDs this month=[X]
G1: quality_trend=[+/-/=] | efficiency_trend=[+/-/=] | alignment_count=[X]
Status: [Green/Yellow/Red]
Action: [none / investigation / G5 trigger]
```

---

## G5: Emergency — Learning Engine Stalled

**Trigger:** 0 new DNA entries (MDs) in 30 days.

**This is a system failure state, not a bad week.**

**Response protocol (in order, no skipping):**

1. **Stop all L3 edits** — no source rotation, no new input experiments until G0 returns to Green ×2 consecutive sessions

2. **Force-read 1 JSONL batch** (minimum: 50 conversation turns from own archive)
   - Priority: most recent high-stakes period
   - If no JSONL available: read last 30 days of `results/daily_log.md` as input

3. **Extract ≥3 MDs** from the batch
   - Do not filter for "good" insights — extract first, evaluate later
   - Each MD: one principle, one sentence, one reference to the context that generated it

4. **Run consistency test:**
   ```bash
   python consistency_test.py templates/example_dna.md --output-dir results
   ```
   - If pass rate < 80%: recalibrate DNA before continuing
   - Log pass rate in `memory/knowledge_audit.md`

5. **Write 1 distillation entry** explaining why the engine stalled:
   - Was it input starvation (no sources)?
   - Was it extraction failure (consumed but didn't encode)?
   - Was it persist failure (encoded but didn't push)?
   - Root cause drives the fix

6. **G0 returns to Green** when: ≥2 consecutive weekly reviews with Behavioral change rate ≥1 and Extraction rate ≥3

**Post-G5:** After 2 Green G0 sessions, resume normal L1/L2 operations. Log stall event as correction → boot test case.

---

## Integration with Other SOPs

| SOP | Connection |
|-----|-----------|
| SOP #47 (Engine Health) | G5 uses same consistency test as SOP #47's restart protocol |
| SOP #48 (Bayesian Update) | G2 constraint #3 (correction → MD) feeds SOP #48's belief update pipeline |
| SOP #50 (L3 Evolution) | G3 quarterly scan is the source-layer equivalent of SOP #50's strategy-layer rotation |
| SOP #49 (Cold-Start) | Every G2 correction event generates boot test cases → improves cold-start fidelity |

---

## Metrics Dashboard

Track in `memory/knowledge_audit.md`:

| Metric | Target | Actual (update weekly) |
|--------|--------|----------------------|
| Input freshness | ≤7 days | — |
| MDs per session | ≥3 | — |
| MDs per month | ≥2 | — |
| Boot test pass rate | ≥80% | — |
| G5 events (lifetime) | 0 | — |
| Active input sources | 2–5 | — |
| Source retirement rate | ≤1/quarter | — |

---

## Failure Modes

| Failure | Symptom | Gate that catches it |
|---------|---------|---------------------|
| Input starvation | 0 new sources in 14+ days | G0 red: input freshness |
| Passive consumption | Reading without extracting | G0 red: extraction rate |
| Belief update without behavioral change | MDs written, decisions unchanged | G1: ΔBehavioral alignment = 0 |
| Source decay | Same sources, diminishing returns | G3: low MD-per-session score |
| Session output not persisted | Learning lost on cold-start | G2 constraint #4 |
| Stall misread as normal | 30-day silence seems fine | G0 kill condition → G5 |

---

## Quick Reference Card

```
G0 (weekly): Is the pipeline flowing? 3 signals.
G1 (weekly): Is it improving? 3 derivatives.
G2 (every session): Did I extract + persist + update DNA?
G3 (quarterly): Is this the highest-EV source available?
G4 (Sunday 10 min): 5-item checklist + log entry.
G5 (emergency): Stalled. Force-read → extract 3 MDs → consistency test → no L3 until 2× Green.
```
