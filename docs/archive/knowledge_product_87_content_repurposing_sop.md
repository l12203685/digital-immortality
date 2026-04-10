# SOP #87 — Content Repurposing: SOP → X Thread

> Domain: Distribution / Content Operations
> Created: 2026-04-09T11:00Z
> Status: OPERATIONAL
> Trigger: G0 (posting_queue has ≥1 row Status=pending AND no thread posted yet)

---

## Why This Exists

SOP #83 builds the daily posting ritual. SOP #78 defines thread file format.
Neither closes the gap between a written SOP doc and a ready-to-post X thread.

**Gap identified:**
SOP #01 is written. The thread file exists. Zero posts have gone out. The blocker is not content — it is the absence of a repeatable conversion protocol that takes a doc and produces a postable thread with a strong hook.

**Current state (cycle 252):**
- 86 SOPs written, 0 posted
- posting_queue.md has 84 rows, all Status=pending
- SOP #01 thread file exists at `docs/publish_thread_sop01_twitter.md`
- Branch 1.3 stalled: 0 audience, 0 M1

**This SOP answers:** given a written SOP doc, produce a thread ready to post in ≤30 min.
First use: SOP #01 → post TODAY.

**Decision principles:**
- MD-148: Distribution is the ROI gate. Content with no distribution is zero-value storage.
- Kernel Rule 1 (see derivative not level): 86 SOPs stored = flat. 1 SOP posted = non-zero. The derivative matters.
- Bias toward inaction is NOT applicable here — demand signal exists (posting_queue built), edge exists (content is already written), the only missing step is execution.

---

## Gate Sequence: G0 → G5

### G0 — Trigger Condition

Fire when ALL of:
- T1: `docs/posting_queue.md` has ≥1 row with `Status = pending`
- T2: The corresponding thread file exists at `docs/publish_thread_sop<NN>_twitter.md`
- T3: Last post was >48h ago OR no post has ever gone out (cold start = immediate fire)

**Cold start override (applies NOW):**
If 0 posts have ever been made AND posting_queue has pending rows: **SKIP all other conditions. Fire immediately on SOP #01.**

If thread file is missing for the next pending row: generate it using G1→G2 before proceeding to G3.

---

### G1 — Input Selection

**Standard path (thread file already exists):**
1. Open `docs/posting_queue.md`
2. Find first row with `Status = pending`
3. Confirm thread file exists: `docs/publish_thread_sop<NN>_twitter.md`
4. Read the thread file: verify hook tweet and CTA are present
5. If hook is weak (no clear single claim, no tension, >280 chars): go to G2 hook rewrite. Otherwise proceed to G3.

**Hook quality test (30-second check):**
- Does tweet 1 make ONE strong, falsifiable claim?
- Does it create a gap (reader wants to know the answer)?
- Is it ≤280 characters?
- Does it avoid "A thread:" without a claim before it?

If all four: hook is strong. Skip to G3.
If any fail: rewrite hook using G2 template.

---

### G2 — Thread Structure Template

Use this template when creating a new thread from a SOP doc, or rewriting a weak hook.

**Minimum viable thread: 5 tweets**

```
Tweet 1 — HOOK (the only tweet that determines if anyone reads the rest)
Format: [Pain/misconception statement] + [claim that contradicts it] + [thread signal]

Pattern options:
  A. "Most [people/traders] [wrong behavior]. The fix is [N gates/steps]."
  B. "You [did X]. [Bad outcome followed]. Here's why and what to do instead."
  C. "[Common belief]. Wrong. Here's what the data shows: 🧵"

Rules:
- One claim. Not two.
- Tension must be present (the reader's belief challenged or curiosity triggered)
- ≤280 characters including 🧵
- Never start with "I"
- Never use "A thread:" without a claim — the claim IS the thread signal

Tweet 2–4 — BODY (one gate/step per tweet)
Format: Gate N: [Label] + [mechanism in plain language] + [why it matters]

Rules:
- One idea per tweet
- Use concrete numbers when available (Edge Ratio > 1.5, not "pretty good")
- No jargon without definition
- Each tweet must stand alone (screenshot shareable)

Tweet 5 — CTA (call to action)
Format: [Summary of the framework] + [follow/DM prompt]

Standard CTA options:
  A. "Follow for [frequency]. DM me if you want to go deeper."
  B. "Save this. The [N]-gate sequence is [what it solves]."
  C. "Full SOP with worked examples at [link]. Follow for next one."

Rules:
- One action, not three
- Do not say "hope this helps" or "let me know what you think"
- Include a DM hook if the thread's topic is consulting-adjacent (trading systems, strategy, career)
```

**Extended thread (8–12 tweets) — use when:**
- The SOP has a worked example worth including (adds credibility)
- There are ≥3 failure modes worth naming (failure modes = shares)
- The topic is high-stakes (trading, money, career)

For SOP #01 (already written as 12 tweets): the thread file at `docs/publish_thread_sop01_twitter.md` is the extended format. Use it as-is.

---

### G3 — Scheduling and Posting Execution

**Immediate posting (cold start / first post ever):**

1. Open X (Twitter) on desktop — do NOT use mobile (harder to thread correctly)
2. Open `docs/publish_thread_sop01_twitter.md` (or the target thread file)
3. Copy Tweet 1 (hook) → paste into X compose box
4. Read hook aloud: does it make one strong claim? If yes, do NOT edit. Editing on posting day = not posting.
5. Post Tweet 1
6. Immediately reply to your own Tweet 1 with Tweet 2 → continue until all tweets posted as replies
7. Final tweet = CTA

**Post timing (when choosing post time):**
- Target: 07:00–09:00 local time OR 20:00–22:00 local time (highest engagement windows for trading/finance audience)
- Avoid: 12:00–14:00 (noise window) and Friday evening (low signal weekend)
- For cold start: time of day is secondary. Post NOW is better than perfect timing.

**After posting:**
1. Update `docs/posting_queue.md`: change `Status` → `posted YYYY-MM-DD`
2. Update `staging/session_state.md`: Branch 1.3 last post = today, M1 = ✅ (if first post)
3. Set a 48h reminder (or cron) to run G4 signal capture

---

### G4 — Signal Capture (48h engagement metrics)

Run 48h after posting. Check:

| Metric | Where | What to record |
|--------|-------|----------------|
| Impressions | X Analytics | absolute number |
| Profile clicks | X Analytics | signal of credibility interest |
| Replies | X thread | count + classify (curious / bot / substantive) |
| DMs | X DMs inbox | count + classify per SOP #83 G4 |
| Follows | X notifications | net new follows from this thread |

Record in `docs/posting_queue.md` signal column:
`signal: [impressions] imp / [replies] replies / [DMs] DMs / [follows] follows`

**Verdict:**
- `HIGH`: >500 impressions OR any organic DM OR ≥3 replies → amplify (reply to replies within 2h, reshare hook tweet standalone)
- `MED`: 100–500 impressions, 0 DMs → continue cadence, no change
- `LOW`: <100 impressions, 0 replies → analyze hook failure. Did the hook make a single strong claim? Rewrite before next post using G2.

**Hook failure analysis (for LOW verdict):**
Compare hook against G2 template. Common failures:
1. No tension — states a fact instead of challenging a belief
2. Multiple claims — reader doesn't know what the thread delivers
3. Too long — hook got cut, reader never saw the claim
4. Starts with "I" — self-referential, not audience-relevant
5. No specificity — "Here's what I learned" vs "5 gates that prevent a $40K sizing mistake"

Log the failure pattern in `memory/content_learnings.md` (create if missing).

---

### G5 — Kill Condition / Graduation

**Kill this repurposing workflow when:**
- K1: First 10 posts average <100 impressions AND hook rewrites show no improvement across 3 consecutive posts → content format wrong, not just hooks. Switch to video or carousel format. Log to `staging/session_state.md`.
- K2: Inbound DMs reach ≥10/week → graduate to a dedicated DM conversion workflow (SOP #88 target). Repurposing cadence continues but DM handling needs its own protocol.
- K3: Product revenue ≥ $500/mo → posting cadence de-prioritizes tutorial threads, shifts to authority-building threads (predictions, live trade logs, contrarian takes). Thread format changes, not the repurposing workflow.

**Graduation condition (Branch 1.3 unblocked):**
This SOP has done its job when:
- [ ] ≥1 post published (M1 milestone achieved)
- [ ] ≥10 posts published (baseline calibration per SOP #82 G2)
- [ ] At least one LOW-verdict hook has been rewritten and re-tested
- [ ] `memory/content_learnings.md` has ≥3 entries

After graduation: this SOP becomes maintenance-mode. Run G1→G3 on autopilot per SOP #83 daily ritual. Only revisit G2 (template) when hook quality degrades.

---

## Immediate Action Checklist (Cold Start — Use TODAY)

SOP #01 thread is already written. Execute in order:

- [ ] Open `docs/publish_thread_sop01_twitter.md`
- [ ] Read Tweet 1 aloud — does it make one strong claim? (Yes: "Most traders build strategies backwards. 5 irreversible gates: 🧵")
- [ ] Open X desktop, paste Tweet 1, do NOT edit
- [ ] Thread all 12 tweets as replies
- [ ] Update `docs/posting_queue.md`: SOP #01 → `posted 2026-04-09`
- [ ] Update `staging/session_state.md`: M1 ✅, Branch 1.3 = unblocked
- [ ] Set 48h reminder for G4 signal capture
- [ ] git commit: `feat: Branch 1.3 M1 — SOP #01 posted`

**Time required: 10 minutes.**
The content is ready. The queue is ready. The only remaining action is execution.

---

## Self-Test

**Scenario:** It is cycle 253. 0 posts have been made. posting_queue has 84 pending rows. Thread file for SOP #01 exists.

**Expected behavior:**
- G0 fires: T1 (pending rows exist) ✓, T2 (thread file exists) ✓, T3 (cold start = 0 posts ever) ✓ — cold start override fires
- G1: SOP #01 selected (first pending row), hook quality check passes (strong claim, tension present, ≤280 chars)
- G2: no rewrite needed (thread already written in extended format)
- G3: post SOP #01 thread NOW, update queue and session_state, M1 logged
- G4: 48h later — capture signal, log to posting_queue
- G5: not triggered (first post, no kill conditions met)

**Anti-patterns:**
- Waiting for a "better" time to post the first thread (timing is secondary to execution)
- Rewriting the hook on posting day (editing = not posting)
- Posting Tweet 1 standalone without threading replies (breaks the SOP format, loses context)
- Skipping G4 signal capture (no signal = no learning = no hook improvement)
- Building SOP #88 before SOP #01 is posted (infrastructure before demand = SOP #66 anti-pattern)

---

## Connections

| SOP | Role |
|-----|------|
| SOP #78 | Posting Operations — defines thread file format |
| SOP #81 | Distribution Velocity — flywheel this SOP activates |
| SOP #82 | Revenue Activation Milestone Tracker — M1 is first post |
| SOP #83 | Daily Posting Execution Ritual — runs after this SOP unblocks posting |
| SOP #84 | Engagement-to-DM Conversion Funnel — downstream of this SOP |
| SOP #86 | Consulting Rate Card — downstream of the DM flow this SOP initiates |
