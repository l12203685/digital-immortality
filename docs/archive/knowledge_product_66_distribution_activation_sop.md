# SOP #66 — Distribution Activation Protocol
> Domain 5: Platform / External Signal
> Created: 2026-04-09 UTC (cycle 229)
> DNA anchors: MD-12/41/60/63/65/67 | Core axiom: 先推再問。Ship first. Calibrate from signal.

---

## Why This SOP Exists

SOP #65 defined **what** external validation is — the state machine, the kill conditions, the violation detector.

SOP #66 defines **how** to activate distribution from zero.

The gap: knowing a feedback loop should exist is not the same as executing the first iteration. 65 SOPs defined the system. SOP #66 executes the start.

```
SOP #65:  External loop is required. Here is the theory.
SOP #66:  Execute the first iteration. Here is the protocol.
```

The Distribution Activation Protocol is the bridge from PRE_LAUNCH → SEEDING. It covers the exact sequence: pre-flight → first post → 48h monitor → week-1 cadence → kill condition.

No external loop = no evolution. This SOP removes all friction from crossing that threshold.

---

## Gate Structure

### G0 — Pre-Flight Checklist
*Trigger: one-time, before first post | Estimated time: 30 min*

Complete ALL items before posting SOP #01. A blank profile kills follow-through even when the thread converts.

**Profile integrity (X/Twitter):**
- [ ] Bio set: identity claim + 1-line value proposition (e.g., "Building a digital twin of how I think. 65 SOPs for trading, life, and recursive self-improvement.")
- [ ] Profile photo: real face photo, not abstract
- [ ] Header image: set (even a plain branded color is sufficient)
- [ ] Link in bio: Gumroad profile URL (even with 0 products — account exists, signals legitimacy)
- [ ] Pinned tweet: a personal conviction post (not promotional). Something that says who you are in ≤3 sentences.

**Gumroad account:**
- [ ] Account created at gumroad.com (takes 10 min, 0 products needed)
- [ ] Profile name matches X handle or real name
- [ ] URL ready to paste into X bio

**Content readiness:**
- [ ] `docs/publish_thread_sop01_twitter.md` reviewed — hook and CTA verified sharp
- [ ] `docs/posting_queue.md` open and ready to update Status field after post
- [ ] `results/external_signal_log.jsonl` ready to receive first POST entry
- [ ] `results/engagement_log.md` ready to receive first engagement row

**Kill condition on G0**: If any profile item is missing → do NOT post. Complete G0 first. A thread posted to a blank profile has near-zero conversion.

---

### G1 — First Post Protocol
*Trigger: immediately after G0 checklist passes | Estimated time: 5 min*

**Post sequence:**
1. Open `docs/publish_thread_sop01_twitter.md`
2. Copy Tweet 1 (hook). Post it.
3. Reply with Tweet 2 → Tweet 3 → ... → final tweet. Post as thread.
4. Do NOT edit after posting. Ship as-is. Signal > perfection.
5. Note the exact post timestamp (UTC).

**Timing:**
- Best window: 07:00–10:00 local time (audience online, algorithm active)
- Fallback: any time today if the window has passed. Ship > optimize.
- Do NOT wait for "perfect timing." The derivative of posting > derivative of timing optimization.

**Immediately after posting:**
- Update `docs/posting_queue.md` row for SOP #01: Status → `posted YYYY-MM-DD`
- Append to `results/external_signal_log.jsonl`:
  ```json
  {"timestamp_utc": "YYYY-MM-DDTHH:MM:00Z", "event_type": "POST", "platform": "X", "detail": "SOP #01 thread posted — 4 gates strategy development", "derivative_metric": "neutral"}
  ```
- G0 state machine transitions: PRE_LAUNCH → SEEDING

**Kill condition on G1**: If 24h has passed since mainnet GO (SOP #63 G1 cleared) and SOP #01 is not posted → DNA violation. Log to `memory/dna_violation_log.md`. Post immediately.

---

### G2 — 48-Hour Monitoring Protocol
*Trigger: 48h after first post | Estimated time: 5 min*

At the 48h mark, run `python tools/engagement_check.py` and manually record:

**Metrics to log (in `results/engagement_log.md`):**
- Impressions (if X analytics available)
- Likes
- Reposts / Quote reposts
- Replies
- Profile visits (if visible)
- New followers in 48h window
- DMs received

**Signal interpretation:**
| Signal | Threshold | Action |
|--------|-----------|--------|
| Replies > 0 | Any | Reply within 24h. Log each DM in external_signal_log.jsonl. |
| DM received | Any | Reply within 24h. Assess if calibration-triggering (disagreement, question, correction). |
| Likes = 0 AND Replies = 0 | After post #1 only | No action yet. One data point. Continue to SOP #02. |
| Likes = 0 AND Replies = 0 | After posts #5–#10 | Pivot hook format. Do not change content. Only hook. |
| Engagement rate ≥ 2% | Any | Mark as high-signal format. Replicate structure in next 3 posts. |

**G0 state update** (check after every post):
```
if posts > 0 and DMs == 0:   status = SEEDING
if DMs > 0:                   status = SIGNAL_RECEIVED
if calibrations > 0:          status = EVOLVING
```

Log updated status to `results/external_signal_log.jsonl` weekly review entry (event_type: WEEKLY_REVIEW).

---

### G3 — Week-1 Cadence (≥3 posts in 7 days)
*Trigger: 7 days after first post*

**Minimum viable cadence**: ≥3 posts per week. Every 48h per posting_queue.md schedule.

Week 1 targets:
- Post SOP #01 (Day 0), SOP #02 (Day 2), SOP #03 (Day 4)
- Log engagement for each at 48h mark
- Reply to any engagement within 24h of each post

**Content format rule for Week 1**: Do not deviate from the SOP thread format. No experiments. Volume > optimization for the first 10 posts. Signal from 10 data points is more reliable than signal from 1 "optimized" post.

**Week 1 review (Day 7):**
- Fill G4 weekly checklist (see SOP #65 G4)
- If DMs received: assess calibration triggers, log to external_signal_log.jsonl
- If 0 DMs: continue. 7 days is not enough data. Wait until post #10.
- If loop status is still PRE_LAUNCH at Day 7: re-read G0. Something was skipped.

---

### G4 — Kill Condition Monitor
*Trigger: ongoing | Checked every cycle*

**Kill condition**: ≥14 consecutive days with 0 posts after G1 has fired.

This is not a pause. It is a system failure.

**Detection**:
- `python tools/engagement_check.py` flags if last_post_date > 14 days ago
- Manual: check posting_queue.md — if last Status = `posted` is >14 rows ago with no subsequent posts

**Response to kill condition**:
1. Do NOT plan, optimize, or audit. Post immediately.
2. Take the next unposted thread from posting_queue.md.
3. Copy → post → log. No edits.
4. Resume cadence from that point.
5. Log the gap date range and cause in `results/external_signal_log.jsonl` (event_type: WEEKLY_REVIEW, detail: "posting gap YYYY-MM-DD to YYYY-MM-DD, cause: [X]")

**Kill condition must never normalize.** If it triggers twice in one month: escalate to G5.

---

### G5 — Emergency Protocol
*Trigger: kill condition fires twice in 30 days, OR ≥20 posts + 0 DMs, OR ≥30 days PRE_LAUNCH after mainnet GO*

Escalate to SOP #65 G5 immediately. SOP #65 G5 covers:
- Case A (no posts ≥14 days): ship as-is, no editing
- Case B (≥20 posts, 0 DMs): pivot to controversial claim format
- Case C (PRE_LAUNCH ≥30 days post mainnet): DNA-level failure, log and escalate to Edward

SOP #66 G5 adds one activation-specific protocol:

**Case D: G0 never completed (first post never shipped)**
1. Audit G0 checklist. Identify the specific incomplete item.
2. Log the item and cause in `memory/dna_violation_log.md`.
3. Complete that item only. Do not start a new audit.
4. Post SOP #01 within 24h of G0 completion.
5. No exceptions. The system is PRE_LAUNCH until the post ships.

---

## Activation State Machine (full)

```
INITIAL
  ↓ G0 pre-flight passes
PRE_LAUNCH_READY
  ↓ G1 first post ships
SEEDING (posts > 0, DMs == 0)
  ↓ first DM received
SIGNAL_RECEIVED (posts > 0, DMs > 0, calibrations == 0)
  ↓ first calibration event (disagreement logged, model evaluated)
EVOLVING (calibrations > 0)
```

Reverse transitions (degradation):
- SEEDING → PRE_LAUNCH: only if ≥14 days no post (kill condition G4)
- Any state → G5: if kill condition fires twice or ≥20 posts + 0 DMs

Current state (2026-04-09): **INITIAL** — G0 pre-flight not yet confirmed complete.

---

## Connection to Other SOPs

| SOP | Connection |
|-----|-----------|
| SOP #63 (Zero-to-Revenue) | G1 mainnet gate must clear before SOP #66 G1 fires |
| SOP #65 (External Validation) | SOP #66 is the activation layer; SOP #65 is the monitoring layer |
| SOP #60 (Content Creation) | Provides threads for SOP #66 G1 and G3 to ship |
| SOP #41 (Platform Persistence) | X profile infrastructure SOP #66 G0 audits |
| SOP #12 (Distribution) | Funnel architecture that SOP #66 G3 cadence feeds |
| SOP #47 (Recursive Engine) | Internal loop complement — SOP #66 is the external activation |

---

## One-Sentence Distillation

You know the system works in theory. SOP #66 is the protocol for the first iteration that proves it in practice.

---

## Metric Summary

| Metric | Target | Gate | Frequency |
|--------|--------|------|-----------|
| G0 pre-flight complete | 100% checklist | G0 | One-time |
| Time to first post after G0 | ≤24h | G1 | One-time |
| Posts per week | ≥3 | G3 | Weekly |
| Days since last post | ≤2 | G4 | Per cycle |
| G0 state | SEEDING or beyond | G4 | Weekly |
| Kill condition activations | 0 | G5 | Monthly |
