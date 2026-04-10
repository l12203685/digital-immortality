# SOP #89 — Weekly Strategy Review Ritual

> Domain: Distribution / Content Strategy
> Created: 2026-04-09T11:15Z
> Status: OPERATIONAL
> Trigger: G0 — First post published (M1 milestone hit) AND 7 days elapsed since previous review

---

## Why This Exists

SOP #83 (Daily Posting Execution Ritual) defines the daily 20-min posting cadence.
SOP #81 (Distribution Velocity SOP) defines velocity baselines and weekly compounding targets.
Neither closes the gap between executing daily and knowing whether execution is working.

**Gap identified:**
Daily posting generates signal (replies, likes, DMs, profile clicks). Without a structured
weekly review, that signal is invisible. You post in the dark for weeks, then wonder why
the flywheel hasn't started. The weekly review turns daily signal into directional decisions:
hook quality, topic selection, posting time, and pipeline adjustment.

**This SOP covers**: When to trigger, what to review, what decisions come out, where to persist.

---

## G0 — Trigger

Fire when ALL:
- M1 hit (first post published)
- 7 days elapsed since last review (or Day 7 after M1 for first review)
- SOP #83 daily ritual operational

Cadence: Every Monday 09:00 local time (or closest weekday if Monday blocked).

Skip condition: 0 posts published in the last 7 days → skip review, trigger SOP #87 G0
cold-start override instead.

---

## G1 — Signal Capture (10 min)

Open last 7 days posts. For each post, record:

| Post | Date | Format | Topic | Replies | Likes | DMs triggered | Profile clicks |
|------|------|--------|-------|---------|-------|---------------|----------------|
| SOP #01 | ... | thread | strategy dev | ... | ... | ... | ... |

Threshold definitions (from SOP #81 velocity baseline):
- **Green**: replies ≥ 2 OR DMs ≥ 1 per post
- **Yellow**: replies = 1, DMs = 0 (signal but weak hook)
- **Red**: replies = 0, DMs = 0 (hook failed or wrong audience)

If all 7 posts are Red → G3 hook revision required.
If ≥ 3 posts are Green → velocity baseline met, continue current cadence.

---

## G2 — Performance Assessment (5 min)

Compare against SOP #82 milestone tracker:

| Metric | Target | Actual | Delta |
|--------|--------|--------|-------|
| Posts this week | 7 | ? | ? |
| Green posts | ≥ 2 | ? | ? |
| DMs received | ≥ 1 | ? | ? |
| Follower delta | ≥ +5 | ? | ? |
| Revenue | $0 until M2 (10 DMs total) | — | — |

Verdict:
- **ON TRACK**: ≥ 2 Green, ≥ 1 DM → continue
- **LAGGING**: 0-1 Green, 0 DMs → trigger G3 hook revision
- **STALLED**: 0 posts published → SOP #87 cold-start override NOW

---

## G3 — Hook Revision (15 min, if triggered)

Fired when: All 7 posts Red, OR performance verdict = LAGGING.

Process:
1. Pick the post with highest likes (even if 0 replies) — it had the right topic, wrong hook
2. Rewrite the opening line: lead with the conclusion, not the setup
3. Check posting time: was it posted Mon-Thu 09:00-12:00? If not, reschedule
4. Compare against SOP #01 thread format (numbered list + concrete mechanism)
5. Write revised hook to `staging/hook_revision_log.md` with original + revision + reason

Anti-patterns:
- Changing topic (topic is not the problem, hook is)
- Posting at irregular times (algorithm penalizes inconsistency)
- Writing longer posts to "add value" (brevity = conviction signal)

---

## G4 — Queue Confirmation (5 min)

Confirm next 7 days queue:

1. Pull from `staging/next_input.md` or SOP #83 daily prep
2. Confirm 7 posts are pre-written and ready to execute (no writing on posting day)
3. If queue < 7 posts → repurpose using SOP #87 (Content Repurposing SOP)
4. Mark each post with: topic / format (thread|single|quote) / posting day

Persist queue to `staging/weekly_queue.md` (overwrite weekly).

---

## G5 — Kill Conditions

Stop weekly review if:
- M7 reached (trading profit > API cost) AND revenue > $500/mo → shift to monthly review cadence
- Audience > 1,000 followers → switch to SOP #81 Phase 3 compounding playbook
- DM volume > 20/week → hand off to SOP #70 + SOP #88 pipeline exclusively

---

## Connections

| SOP | Connection |
|-----|-----------|
| SOP #83 | Supplies daily execution data for G1 signal capture |
| SOP #81 | Provides velocity baseline thresholds for G2 assessment |
| SOP #87 | Triggered by G3 (hook revision) or G4 (queue replenishment) |
| SOP #82 | Milestone tracker: weekly review reports into milestone progress |
| SOP #70 | DM conversion: G2 DM count feeds G0 trigger for SOP #70 |
| SOP #88 | Discovery call: weekly DM volume feeds G0 trigger for SOP #88 |

---

## Anti-Patterns

| Pattern | Why it fails |
|---------|-------------|
| Reviewing mid-week | Incomplete signal; makes decisions on noise not trend |
| Skipping Red weeks | Red = signal; skipping = not learning |
| Changing topic instead of hook | Topic selection is not the bottleneck; hook clarity is |
| No persistent queue | Winging it daily = friction = stalls |
| Review without decision | Observation without action is just journaling |

---

## Self-Test

Given: 7 posts published, 0 replies, 0 DMs, 3 likes.
Answer: All Red → G3 hook revision triggered → pick highest-like post → rewrite opening line → log to hook_revision_log.md → no topic change.

Given: 5 posts published, 1 Green (2 replies + 1 DM), 4 Yellow.
Answer: G2 = ON TRACK (≥2 Green threshold not met but ≥1 DM = velocity signal). Rewrite the 4 Yellow hooks but don't change topics.

---

## Critical Path

SOP #01 post → M1 → SOP #83 daily ritual → **SOP #89 weekly review (Day 7)** → G3 hook revision (if needed) → SOP #82 milestone update → M2 clock ticks.

**SOP #01~#89 COMPLETE ✅**
