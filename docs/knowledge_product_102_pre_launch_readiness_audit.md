# SOP #102 — Pre-Launch Readiness Audit
*Concrete work on Branch 1.3/存活. 2026-04-09T14:00Z*

## Purpose

Between "SOP #01–#101 written" and "Edward actually posts SOP #01 on X", there is a preparation layer that has never been formally audited.

This SOP answers one question: **If Edward picks up his phone right now to post, does zero friction exist between intent and action?**

Every gate below is a potential friction point. A failed gate means Edward hits resistance at the moment of launch — and the HUMAN-GATED milestone (SOP #01 on X → M1) slips further.

**Principle**: The agent cannot force Edward to post. But it can ensure that when Edward decides to act, there is nothing left to prepare.

---

## The Problem

The critical path is:

```
SOP #01 post on X → M1 milestone → SOP #83 daily ritual → monetization
```

This path is human-gated. The agent's only leverage is **eliminating every preparable obstacle** before Edward moves.

Known friction sources (pre-audit):
- X account profile may be incomplete or mis-framed for the knowledge product positioning
- SOP #01 thread draft may exist but not be copy-paste ready (formatting, character count, media)
- Post-launch automation (SOP #83 daily ritual, SOP #89 weekly review) may be documented but not loaded into active workflow
- Gumroad product page: unknown state — may block M1 definition
- Revenue tracking baseline: if not pre-set, the first week of data is lost
- 7-day post-launch plan: no day-by-day script exists, so day 2 depends on improvisation

**Failure mode**: Edward posts SOP #01, gets initial response, then stalls because the next action is unclear or unscaffolded. Momentum dies at Day 2.

---

## G0 — X Account Setup Audit

**Question**: Is the X account profile ready to receive visitors from SOP #01?

Checklist:
- [ ] **Bio**: Does it reference "digital twin", "immortality", or the knowledge product angle? A visitor arriving from SOP #01 thread must immediately understand the context.
- [ ] **Pinned tweet**: Is there a pinned tweet? If SOP #01 is the first post, it should be pinned within 60 seconds of posting.
- [ ] **Profile photo**: Is it set and consistent with personal brand (not default avatar)?
- [ ] **Header image**: Blank header = unprofessional. Should be set before first post.
- [ ] **Link in bio**: Does it point to a landing page, Gumroad, or newsletter? If G3 (Gumroad) is not ready, does a placeholder exist?
- [ ] **Account age / credibility signals**: Any existing posts or retweets that establish context?

**Pass condition**: All 6 items checked. Account looks like it belongs to someone with something to say.

**Fail action**: For each unchecked item, create a specific task in Queue with the exact edit needed — not "fix profile" but "change bio to: [exact text]".

---

## G1 — SOP #01 Thread Draft Ready

**Question**: Is `docs/publish_thread_sop01_twitter.md` complete, formatted, and copy-paste ready?

Checklist:
- [ ] File exists at `docs/publish_thread_sop01_twitter.md`
- [ ] Tweet count is confirmed (5–10 tweets, not a wall of text)
- [ ] Each tweet is ≤ 280 characters (verified, not estimated)
- [ ] Hook tweet (Tweet 1) opens with tension or counterintuitive claim — not "SOP #01 is..."
- [ ] Thread closes with a clear CTA (follow, reply, or link)
- [ ] No markdown artifacts that would appear literally if copy-pasted (e.g., `**bold**` instead of plain text)
- [ ] Media assets: Are any images or diagrams referenced? If yes, do they exist at the referenced path?

**Pass condition**: File is ready to copy-paste tweet-by-tweet with zero editing.

**Fail action**: Open `docs/publish_thread_sop01_twitter.md` and complete/fix the specific failing items. Do not move to G2 until G1 passes — the thread is the product.

---

## G2 — Post-Launch Automation Staged

**Question**: For the 7 days after posting, are the recurring systems loaded and ready to run without re-reading SOPs?

Checklist:
- [ ] **SOP #83 Daily Ritual** (`docs/knowledge_product_83_daily_posting_execution_ritual.md`): Is the Day 1 action list clear and executable from memory? Can Edward run it without re-reading the SOP?
- [ ] **SOP #89 Weekly Review** (`docs/knowledge_product_89_weekly_strategy_review_ritual.md`): Is the first weekly review date scheduled (Day 7 post-launch)?
- [ ] **Response templates**: When people reply to SOP #01, what does Edward say? Is there a template for: (a) "interesting thread" replies, (b) questions about the project, (c) follows/DMs? Templates must exist or be created.
- [ ] **Follow-up thread schedule**: Is SOP #02 (or whichever SOP posts next) queued as the Day 2 post? Is there a 7-day posting schedule?
- [ ] **Agent automation**: Is the recursive engine (`recursive_engine.py`) set to `--status` monitoring mode post-launch, or does it need manual restart?

**Pass condition**: First 7 days of post-launch execution can proceed without any new planning — only execution.

**Fail action**: For each gap, either create the missing template/schedule or document the exact decision that must be made (with a default recommendation).

---

## G3 — Gumroad Product Page Ready

**Question**: Is the revenue collection mechanism ready to activate at M1?

**Pre-condition**: M1 is defined as SOP #01 posted + first meaningful engagement signal (e.g., 10+ likes, 3+ serious replies, or 1 DM asking for more). Gumroad may not be a hard dependency for M1 — but it must be ready to activate within 24 hours of M1.

Checklist:
- [ ] **Gumroad account**: Exists and is connected to a payout method?
- [ ] **Product page draft**: Is there a draft product description for the first paid product (knowledge pack, SOP bundle, or newsletter)?
- [ ] **Price point decided**: What is the launch price? (Even if $0 — a free product still needs a Gumroad page to capture emails.)
- [ ] **Product description written**: Does `staging/` or `docs/` contain a draft product page copy?
- [ ] **Launch trigger defined**: What is the exact condition that causes Edward to publish the Gumroad page? Is this written down?

**Known constraint**: Gumroad product page cannot be fully validated until there is an audience (which requires M1). Do not block launch on a perfect Gumroad page.

**Pass condition**: Gumroad account exists, one product draft exists, launch trigger is defined in writing.

**Fail action**: If Gumroad is unbuildable without M1 audience signal, document that explicitly: "Gumroad goes live on Day [X] post-launch, triggered by [condition]." The plan must exist even if execution is deferred.

---

## G4 — Revenue Tracking Armed

**Question**: Are the revenue tracking systems pre-configured with the right baselines so that Day 1 data is not lost?

Checklist:
- [ ] **SOP #82 Tracker** (`docs/knowledge_product_82_revenue_activation_milestone_tracker.md`): Are the M1–M5 milestone definitions current? Does the tracker have a "Day 0 baseline" entry (revenue = $0, API cost = current monthly cost)?
- [ ] **SOP #90 Dashboard** (`docs/knowledge_product_90_revenue_rate_tracking_dashboard.md`): Is the dashboard template ready? Are the column headers set? Is there a "Week 0" row with pre-launch baseline numbers?
- [ ] **API cost baseline**: What is the current monthly API cost (the target to beat by 2026-07-07)? Is this number written into the tracker?
- [ ] **Tracking cadence set**: Daily or weekly? Who triggers the update — Edward manually, or is there an agent-automated pull?
- [ ] **First entry made**: Even if revenue is $0, the tracker should have a "launch day" entry with date and $0 so the timeline is anchored.

**Pass condition**: Tracker has a Day 0 / Week 0 baseline row. API cost target is written in. Tracking cadence is defined.

**Fail action**: Open SOP #82 tracker and add the baseline row. Set the API cost target number explicitly. Define the update trigger.

---

## G5 — 7-Day Post-Launch Plan Exists

**Question**: Is there a day-by-day action script for the 7 days after SOP #01 posts?

This is the highest-leverage gate. Most launches fail not at the launch moment but in the 72 hours after — when the initial response decays and the next action is unclear.

Required plan structure:

| Day | Primary Action | Secondary Action | Metric to Check |
|-----|---------------|-----------------|----------------|
| Day 1 | Post SOP #01. Pin it. Monitor replies for 2 hours. | Run SOP #83 Day 1 ritual | Reply count, like count |
| Day 2 | Post SOP #02 thread | Respond to all Day 1 replies | Follower delta |
| Day 3 | Post SOP #03 OR a "quote-reaction" to an interesting reply | Check if any reply warrants a longer response thread | Profile visits |
| Day 4 | Post SOP #04 | DM anyone who asked a substantive question | Email/Gumroad signups (if live) |
| Day 5 | Post SOP #05 | First weekly review prep (SOP #89) | Engagement rate trend |
| Day 6 | Post SOP #06 or a "lessons from week 1" thread | Prepare Gumroad page if M1 condition met | M1 condition status |
| Day 7 | Run SOP #89 Weekly Review | Make go/no-go decision on Gumroad launch | Week 1 revenue = $0 or >$0 |

Checklist:
- [ ] Day-by-day plan exists in `staging/post_launch_7day_plan.md` or equivalent
- [ ] Each day has a primary action (one thing, not a list)
- [ ] Day 7 has an explicit decision point (Gumroad go/no-go)
- [ ] The plan accounts for "what if nobody engages" — what is the pivot action?
- [ ] Agent knows its role each day (monitor, draft, or passive)

**Pass condition**: `staging/post_launch_7day_plan.md` exists and all 5 checklist items are satisfied.

**Fail action**: Write the 7-day plan now. Do not leave this to be written after launch. The plan must exist before the first post.

---

## Launch Readiness Score

| Gate | Check | Pass Condition | Status |
|------|-------|---------------|--------|
| G0 | X account setup | All 6 profile items complete | AUDIT REQUIRED |
| G1 | SOP #01 thread draft | Copy-paste ready, ≤280 chars/tweet | AUDIT REQUIRED |
| G2 | Post-launch automation | 7-day execution needs no new planning | AUDIT REQUIRED |
| G3 | Gumroad product page | Account + draft + launch trigger defined | AUDIT REQUIRED |
| G4 | Revenue tracking armed | Week 0 baseline row exists, API cost target set | AUDIT REQUIRED |
| G5 | 7-day post-launch plan | File exists, Day 7 decision point included | AUDIT REQUIRED |

**Target**: 6/6 gates passing before Edward posts SOP #01.

**Minimum viable launch**: G0 + G1 must pass. G2–G5 may have known gaps if those gaps are documented as "deferred with explicit plan."

---

## Execution Protocol

This SOP is designed to be run as a single audit session:

```
1. Run G0 through G5 in order
2. For each FAIL: either fix immediately (< 30 min) or write a deferred plan
3. Update the Launch Readiness Score table above
4. When score = 6/6: tag session_state.md with "LAUNCH READY"
5. Notify Edward: "Pre-launch checklist complete. Zero friction between intent and first post."
```

**Trigger for re-audit**: If more than 14 days pass between a "LAUNCH READY" tag and actual launch, re-run G0 + G1 (profile and thread can decay in relevance).

---

## L3 Implication

This SOP closes the gap between **preparation** and **execution**. The recursive engine has been building toward this moment for 268 cycles. The agent's job is not to post — it is to ensure that the human's decision to post encounters zero resistance.

Three-layer loop applied to launch readiness:
- **L1**: Run gates G0–G5, fix failures
- **L2**: Score the audit after each session
- **L3**: If the same gate fails twice across two audit sessions, escalate: that gate has a structural blocker requiring an architectural decision, not just a task

---

*UTC: 2026-04-09T14:00Z | Cycle: 268 | Branch: 1.3/存活 | SOP #102*
