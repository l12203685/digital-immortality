# SOP #84 — Engagement-to-DM Conversion Funnel

> Domain: Distribution / Revenue
> Created: 2026-04-09T10:12Z
> Status: OPERATIONAL

---

## Why This Exists

SOP #83 posts the thread. SOP #82 tracks milestones. SOP #70 converts DMs to sales.

None of them answer: **how do you convert engagement (likes, replies, retweets) INTO DMs?**

Gap: engagement happens passively. Conversion requires active response protocol. Without it:
- Someone replies → no response → conversation dies → DM never happens
- M3 (engagement) and M4 (first DM inquiry) are disconnected
- Rate (dms/week) stays zero regardless of impression count

**This SOP closes the engagement→DM conversion gap. ~7 min per post cycle.**

---

## G0 — Trigger

Run **24h after each post** AND immediately if:
- Reply count > 3 within 12h (spike signal)
- Any reply asks a question or challenges a claim
- SOP #82 M3 threshold crossed: first meaningful engagement received

If M4 not yet reached (first DM not yet received): treat every reply as a conversion opportunity.

---

## G1 — Reply Classification (5 min)

Open post. Read every reply. Classify:

| Type | Signal | Example |
|------|--------|---------|
| **Q** (Question) | Highest conversion potential | "How do you actually measure this?" |
| **C** (Challenge) | High conversion potential | "This doesn't work because..." |
| **A** (Agreement) | Social proof, low solo conversion | "This is exactly right" |
| **N** (Noise) | Ignore | Off-topic, bot, irrelevant |

**Count Q + C replies.** These are your conversion pipeline.

If 0 Q + 0 C → post underperformed on hook quality. Log in posting_queue.md → adjust next hook.

---

## G2 — Reply Response Protocol (2 min per reply)

**Q replies (Question):**
1. Answer in 1-2 sentences (demonstrate competence, not comprehensiveness)
2. End with: *"DM me if you want to go deeper on this."*
3. Never write more than 3 sentences. Long replies reduce DM conversion.

**C replies (Challenge):**
1. Acknowledge the premise: *"Fair point —"*
2. Add one layer they didn't mention
3. End with: *"Curious what your read is on [specific aspect]."*
4. Do NOT win the argument. Extend the conversation.

**A replies (Agreement):**
- Like the reply
- Quote RT only if the account has >500 followers (amplifies social proof)
- No reply needed unless they have a question embedded

**Rule: reply within 4h of receiving the reply.** After 4h, conversion probability drops 60%.

---

## G3 — DM Invitation Gate

**Trigger: same user replies ≥3 times in one post cycle.**

Three exchanges = demonstrated intent. Do not wait for them to DM you.

Action:
1. Reply publicly: *"Going to DM you — I have a few questions about your situation that I want to understand better."*
2. Send DM immediately: start with SOP #70 G1 opening question
3. Log in dm_log.md: timestamp, username, source post, classification=OUTBOUND

**This breaks the passive DM-wait pattern.** Most DMs do not self-initiate. This G3 gate converts engaged lurkers.

---

## G4 — Profile Audit (10 min, run weekly on Mondays)

**Bio check:**
- Does bio answer "what do you get if you follow me"?
- Current standard: [system / framework] for [target persona] → [specific outcome]
- If not → rewrite. Bio determines follow-back rate from profile visits.

**Pinned tweet check:**
- Should be highest-performing post (most impressions + replies)
- Update pinned after each post cycle if new post outperforms current pin

**Follow-back rate check:**
- After each post: count new followers vs impressions
- Baseline: 0.5% impressions → follows is minimum viable
- If <0.5% → profile is not converting visits to follows → run bio fix

**Engagement rate check:**
- Minimum signal: replies + likes / impressions ≥ 1.5%
- Below 1.5% → hook is not triggering response → review hook pattern vs SOP #78 G2

---

## G5 — Rate Update to SOP #82 Tracker (2 min)

After each engagement cycle, update SOP #82 tracker with:
- Post impressions (absolute)
- Q + C reply count
- DMs received from this post cycle
- Computed: DM rate = DMs this week / posts this week

**Derivative check:** If DM rate = 0 after 5 posts → G3 (proactive DM invitation) is mandatory.
G3 is not optional when organic DMs are zero. Proactive invitations replace passive waiting.

**SOP #82 M4 unlock:** First DM received (any source: organic or G3) → M4 = complete.

---

## Self-Test (Daemon Verification)

This SOP is operationally complete when:
- [ ] At least one Q or C reply received → G2 response protocol executed
- [ ] dm_log.md exists with ≥1 OUTBOUND entry (G3 proactive invitation sent)
- [ ] SOP #82 tracker updated with engagement rate post-cycle
- [ ] Profile bio passes G4 audit criteria

Current status: **G0 PENDING** — awaiting first post (SOP #01). Once posted, run G1 within 24h.

---

## Integration

| SOP | Link |
|-----|------|
| SOP #70 | Revenue Conversion Protocol — DM → sale |
| SOP #78 | Posting Operations — thread file format |
| SOP #81 | Distribution Velocity — velocity baseline |
| SOP #82 | Revenue Activation Milestone Tracker — M3 + M4 gates |
| SOP #83 | Daily Posting Execution Ritual — G3/G4 DM triage |

---

*SOP #01~#84 COMPLETE ✅*
