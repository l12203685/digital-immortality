# SOP #98 — Turing Test Candidate Selection Protocol

> Domain: Branch 9 — Behavioral Equivalence Certification (External Tier)
> Created: 2026-04-09T14:00Z
> Status: ACTIVE — unblocks Branch 9; 0/3 candidates current
> Decision label: SELECT_3_QUALIFIED_EVALUATORS_BEFORE_SCHEDULING_TEST
> Trigger: Run once to identify and secure 3 qualified evaluators

---

## Why This Exists

**Gap (identified cycle 263):**

The Turing Test Protocol (docs/turing_test_protocol.md, 470 lines) is fully designed. It defines G0–G5 evaluation stages, scoring rubrics, blind session mechanics, and DNA patch loops. The protocol is complete. The project is not blocked on methodology.

It is blocked on **zero candidates**.

Without qualified human evaluators, the highest validation tier in the SKILL.md hierarchy remains permanently unreachable. Machine validation (33/33 ALIGNED, 100% cross-instance) is proven. The ceiling is: *a person who knows Edward well, in a blind evaluation, cannot reliably distinguish the agent from Edward.*

This SOP converts a blocked branch into a runnable process.

**DNA anchors:**
- Behavioral equivalence is the project core axiom
- Validation hierarchy: Turing test by close friends/family = highest tier
- Bias toward inaction on no-edge decisions. This is a high-edge decision: closing the validation gap.

---

## G0 — Candidate Qualification Criteria

A qualified evaluator must meet ALL of the following:

| Criterion | Requirement | Why |
|-----------|-------------|-----|
| Relationship depth | Knows Edward ≥ 3 years | Short-term contacts can't detect behavioral drift |
| Domain coverage | Observed Edward in ≥ 2 of: trading / career / relationships / finance | Single-domain observers miss cross-domain patterns |
| Conversation history | ≥ 10 substantive exchanges with Edward | Evaluator needs internalized baseline for Edward's voice and framing |
| Availability | Can commit 2 sessions × 45 min within a 2-week window | Evaluation must complete before DNA drift accumulates |
| Blind commitment | Agrees to attempt identification, not meta-reason about format | Contamination invalidates results |

**Minimum pool size:** 3 confirmed. If only 2 can be secured, defer; the 3-evaluator minimum exists to get majority-vote scoring (2/3 fail rate threshold).

---

## G1 — Candidate Identification (The Shortlist)

### Selection Framework

Run this scan against Edward's actual network. The shortlist should contain 5–8 candidates, from which 3 will be confirmed.

**Tier A — Highest qualification probability:**
- Friends from pre-2023 with regular contact maintained
- Former colleagues who worked closely with Edward (not just same team)
- People Edward has had multi-domain conversations with (work + life + money)

**Tier B — Likely qualified but verify:**
- University classmates with regular contact
- Friends who know Edward's trading or career moves in detail
- Anyone who has given Edward direct feedback on decisions (not just social contact)

**Disqualify immediately:**
- Family members (too close; emotional contamination)
- Colleagues who know Edward only professionally (single-domain)
- Contacts with < 1 conversation per month in last 12 months (baseline decay)

### Shortlist Output Format

```
Candidate: [Name]
Tier: A / B
Years known: [N]
Domains observed: [trading / career / relationships / finance]
Contact frequency: [daily / weekly / monthly]
Known Edward's major decisions: [yes / no — specify]
Disqualifying factor: [if any]
Verdict: SHORTLIST / DISQUALIFY
```

Target: 5–8 on shortlist. Rank by qualification score.

---

## G2 — Approach Script

### First Message (WhatsApp / LINE / Signal preferred)

```
Hey [Name],

做一個個人專案 — 在研究 AI 數位分身的行為對齊。想邀你參與一個小實驗：
兩段對話，你來判斷哪一段是我本人、哪一段是我的 AI。

不需要 AI 背景。就是需要「認識我夠久、夠熟」的人。
一次大概 45 分鐘，兩週內找一個時間。完全保密。

有興趣的話我再傳詳細說明給你。
```

**If English preferred:**
```
Hey [Name], 

Working on a personal project — researching behavioral alignment in AI systems. 
Inviting you to a small experiment: two conversations, you judge which is me and which is AI.

No technical background needed. Just need someone who knows me well.
~45 min, within a 2-week window. Fully confidential.

If you're interested, I'll send the details.
```

### What NOT to say in the approach:
- Don't mention "Turing test" by name (primes the wrong frame)
- Don't describe what you're testing for (anchors their evaluation)
- Don't send the full protocol upfront (cognitive overload → declining)

---

## G3 — Consent and Baseline Calibration

Once candidate confirms interest:

### Consent Checklist (verify before scheduling)

- [ ] Candidate understands: 2 sessions, 45 min each, 2-week window
- [ ] Candidate agrees: will attempt honest identification, not second-guess the format
- [ ] Candidate agrees: results stay between Edward and them (no third-party sharing)
- [ ] Candidate understands: their feedback will be used to improve the AI system

### Pre-Evaluation Baseline Conversation

Before the formal sessions, have ONE casual conversation with the candidate (5–10 min) on a normal topic. This:
1. Refreshes the candidate's baseline sense of Edward's voice
2. Confirms the candidate's memory of Edward's recent context is current
3. Establishes a control sample for the evaluator

Log this conversation date in `results/turing_test_candidates.md`.

---

## G4 — Scheduling and Pipeline Management

### Candidate Tracker

Update `results/turing_test_candidates.md` after each G1–G3 step.

### Pipeline States

```
SHORTLISTED → APPROACHED → CONFIRMED → BASELINE_DONE → READY
```

Move candidates through states as each step completes. Block G0 of the Turing Test Protocol until 3 candidates reach READY state.

### Timing

- Approach: within 7 days of shortlist finalization
- Confirm: within 14 days of approach
- Baseline conversation: within 7 days of confirmation
- Evaluation window: 2 weeks after baseline

If any candidate falls out after confirmation, go to the next shortlist candidate immediately (maintain a backup list of 2).

---

## G5 — Success Criteria

| Gate | Criterion |
|------|-----------|
| G1 complete | 5–8 candidates on shortlist with qualification scores |
| G2 complete | ≥5 approached |
| G3 complete | 3 confirmed with signed consent understanding |
| G4 complete | 3 baselines done; 3 candidates at READY state |
| SOP complete | Trigger G0 of `docs/turing_test_protocol.md` |

### What changes when this SOP completes

- Branch 9 unblocks from BLOCKED → ACTIVE
- Turing Test Protocol becomes schedulable
- Validation hierarchy ceiling becomes reachable

---

## Self-Test (verify SOP is internalized)

**Scenario:** You have 5 friends on your shortlist. Two of them are family members. One is a colleague you only talk to about work. How many candidates are actually on your active shortlist?

**Answer:** 2. Family members (emotional contamination) and single-domain colleagues (domain coverage < 2) are disqualified by G0 criteria. You need 3 more candidates before you can proceed.

---

## Connections to Other SOPs

| SOP | Link |
|-----|------|
| Turing Test Protocol | docs/turing_test_protocol.md — G0 triggers after this SOP completes |
| Samuel Organism Calibration | docs/samuel_async_calibration_dm.md — Samuel is a candidate (Tier A); send DM first |
| Cross-Instance Calibration | SOP #94 — machine-tier ceiling; this SOP opens human-tier ceiling |
| Monthly DNA Calibration Audit | SOP #91 — gaps found in Turing test → new calibration cycles |

---

*SOP #98 | Created 2026-04-09T14:00Z | digital-immortality project*
