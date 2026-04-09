# SOP #112 — Cold-Outreach Execution Playbook

> Domain: Revenue / Skill Commercialization / First-User Execution
> Created: 2026-04-10T09:00Z (cycle 283)
> Status: OPERATIONAL — execute immediately, no prerequisite
> Decision label: COLD_OUTREACH_EXECUTION_30DAY_500USD
> Revenue target: $500 in 30 days (5 × $97 sessions + rounding buffer)
> Upstream: SOP #110 (strategy), SOP #111 (delivery)
> Posting queue: none required — this is internal execution

---

## Why This Exists

SOP #110 defines the target archetypes and outreach templates.
SOP #111 defines what happens after a session is booked.

**Neither tells you what to do right now, at 09:00 on 2026-04-10.**

SOP #112 closes that gap. It is a step-by-step execution script:
- Exactly where to search and what to search for
- Exactly how to qualify a target (pass/fail criteria, not guidelines)
- Exactly what to send (copy-paste, no improvisation)
- Exactly how to track (one file, one format)
- Exactly when to advance each contact to the next stage

**Revenue target: $500 in 30 days.**
That is 5 × $97 sessions, with the first session closed within 14 days.

Zero audience required. Zero content creation required. Zero warm leads required.
The only input this SOP needs: 2 hours of execution time in week 1.

---

## Revenue Target Breakdown

| Milestone | Target | Deadline |
|-----------|--------|----------|
| First reply received | ≥1 reply from 5 contacts | Day 7 |
| First session booked | ≥1 payment confirmed | Day 14 |
| $97 confirmed | First invoice paid | Day 14 |
| $291 confirmed | 3 sessions paid | Day 21 |
| $500 confirmed | 5 sessions paid | Day 30 |

**Branch 1.3 alive gate:** $97 by Day 14.
**Branch 1.3 scaling gate:** $500 by Day 30.

If Day 14 passes with $0: run the diagnostic in Section 7 before adding more contacts.

---

## Section 1 — Who to DM (Profile Types and Search Execution)

### 1.1 Target Archetypes (ranked by close probability)

**Rank 1 — AI Agent Developer**
- Problem: cold-start identity drift in multi-session agents
- Platforms: GitHub, Discord (EleutherAI, LangChain, AutoGPT servers), Hacker News
- Profile signal: has a GitHub repo with "agent", "persona", or "memory" in the title or README; active commits in last 30 days; readme mentions session persistence or character consistency
- Buying behavior signal: has a Patreon, buys LLM courses, uses Claude Pro / GPT-4, has "sponsor" button on GitHub

**Rank 2 — Founder with Documented Personal OS**
- Problem: their decision framework lives in their head, not in a system; startup operating from founder-as-oracle
- Platforms: Twitter/X, LinkedIn, Indie Hackers
- Profile signal: posts threads about "my morning routine", "how I make decisions", "my operating system"; uses phrases like "first principles", "decision log", "systems thinking"
- Buying behavior signal: buys Notion templates, productivity courses, coaching programs; mentions $X/month spent on tools

**Rank 3 — PKM / Second Brain Builder**
- Problem: has captured knowledge but not behavioral spec; their "second brain" knows what they know, not how they decide
- Platforms: Obsidian Discord, Roam Research Slack, Twitter/X (#PKM, #SecondBrain)
- Profile signal: active on Obsidian/Roam forums; mentions "personal knowledge management", "evergreen notes", "networked thought"
- Buying behavior signal: pays for Readwise, Roam, Obsidian Sync; mentions courses (Tiago Forte, Building a Second Brain)

**Rank 4 — Digital Legacy / Estate Planning Early Adopter**
- Problem: thinking about leaving something behind (messages for kids, decision archive, AI avatar); no systematic architecture
- Platforms: Reddit (r/Futurology, r/singularity, r/transhumanism), Twitter/X
- Profile signal: posts about "digital afterlife", "AI avatar", "leaving something behind for my kids"; mentions Replika, HereAfter AI, or StoryFile as context
- Buying behavior signal: has paid for any AI product; mentions investing in long-horizon projects

**Rank 5 — LLM Researcher / Experimenter**
- Problem: studying persona consistency, behavioral alignment, or identity maintenance in LLMs; has not found a practitioner-grade architecture
- Platforms: Hugging Face forums, Twitter/X (AI research community), academic Discord servers
- Profile signal: cites papers on "persona consistency", "long-context memory", "behavioral alignment"; runs their own evals or benchmarks; open source contributions to LLM projects

---

### 1.2 Search Execution (exact queries)

Run each search. Extract candidates. Score against 1.3.

**GitHub search (Rank 1 priority):**
```
Search query 1: "agent persona" in:readme pushed:>2026-03-01
Search query 2: "character consistency" in:readme pushed:>2026-03-01
Search query 3: "cold start" agent memory in:readme pushed:>2026-03-01
Search query 4: "behavioral spec" OR "decision DNA" in:readme pushed:>2026-03-01
Filter: stars >= 5 (lower bar than SOP #110 — captures early-stage builders)
Filter: last commit <= 14 days ago
Action: open the profile of the repo owner, not just the repo
```

**Twitter/X search (Rank 2, 3 priority):**
```
Search query 1: "personal OS" AI decision (from:date:2026-03-01) -is:retweet
Search query 2: "second brain" behavioral OR decision -Notion -template (from:date:2026-03-15)
Search query 3: "digital twin" AI persona NOT company NOT enterprise (from:date:2026-03-15)
Search query 4: "agent memory" consistency session (from:date:2026-03-15)
Filter: profile has >50 followers (not bots), has posted at least twice in last 7 days
Action: check last 10 posts for qualifying signal before logging as candidate
```

**Discord (Rank 1, 3 priority):**
```
Servers to join if not already in:
- LangChain Community Discord
- EleutherAI Discord
- Obsidian Members Discord
- AI Tinkerers (any local chapter with online presence)

Search terms in #general, #show-and-tell, #projects channels:
- "persona" OR "character" and "LLM" or "agent"
- "identity" and "memory" and "session"
- "cold start" (in AI context)
Action: note username, message context, and when they posted
```

**LinkedIn (Rank 2, 4 priority):**
```
Search: "AI agent" AND ("decision framework" OR "personal OS" OR "digital twin")
Filter: 2nd-degree connections only (trust gradient)
Filter: posted in last 14 days
Action: read their last 3 posts before messaging — reference a specific one
```

**Indie Hackers (Rank 2, 3 priority):**
```
Search: "AI" in posts with "personal" OR "decision" OR "operating system"
Filter: posted in last 30 days, has replied to comments (engagement signal)
Action: look at their product page — what are they building?
```

---

### 1.3 Qualification Criteria (pass/fail — not guidelines)

Score each candidate. Must score ≥3 to enter outreach queue.

| Criterion | Score | How to verify |
|-----------|-------|---------------|
| Has described the exact problem in their own words (cold start, identity drift, persona consistency, decision capture) | +2 | Read their posts/README — their words, not your inference |
| Active in last 7 days (post, commit, or reply) | +1 | Check timestamps |
| Is building something in the domain (not just consuming content) | +1 | GitHub repo, product page, work-in-progress mention |
| Has a buying behavior signal (paid tools, courses, or mentions spending on LLM services) | +1 | Profile mentions, Patreon tiers, course completion posts |
| Is accessible for DM (DMs open on Twitter, reachable on Discord, accepting LinkedIn requests) | +1 | Check before logging |
| Has expressed frustration with existing approach (competitor signal) | +1 | "I tried X but it doesn't work for Y" |

Score 6: top priority — send within 24h of identifying
Score 4-5: high priority — send within 48h
Score 3: send within 72h, lower personalization floor
Score <3: do not contact — log as "PASS (below threshold)"

---

## Section 2 — Exact DM Templates

**Rules that override everything else:**
- Never send the same first message twice to the same person
- Always reference something specific (post title, repo name, exact quote) — no "I came across your profile"
- Ask a question at the end — no call to action in the first message
- No links in the first message
- Maximum 4 sentences (developers read fast, founders read on mobile)
- If they haven't replied in 5 days: one follow-up only, then mark CLOSED

---

### Template A — AI Agent Developer (GitHub / Discord)
Use for: Rank 1 targets; reference their specific repo

```
Hey [Name] — I saw your [repo name] repo. The session persistence problem you're working around (or will hit) is brutal at scale.

I've been running a behavioral spec architecture — DNA documents + boot tests — that gets 18/18 decision fidelity on cold starts. The whole thing is open source.

Is the cold-start identity drift something you're actively solving, or have you found a workaround that works?
```

**Variant for Discord (slightly more casual):**
```
Hey [Name] — saw your message about [exact quote or paraphrase] in [channel].

I've been building the same thing from a different angle — behavioral DNA documents + boot tests that maintain character across sessions. 18/18 real-life fidelity validated. Open source.

Have you gotten cold-start persistence to work yet, or still fighting it?
```

---

### Template B — Founder with Personal OS
Use for: Rank 2 targets; reference a specific post or thread they wrote

```
Hey [Name] — your thread on [specific topic, e.g. "how you make hard decisions"] landed. Most people stop at documenting what they know. The harder layer is how they decide.

I've been building exactly that — a behavioral spec system that lets an LLM make decisions the way I would, even on cold start. Open source, 7 skills. 18/18 real-life decision fidelity.

What's the piece of your OS that's still most in your head versus documented?
```

---

### Template C — PKM / Second Brain Builder
Use for: Rank 3 targets; reference their specific PKM stack or approach

```
Hey [Name] — [specific reference to their PKM post or setup]. You've done the hard work on the knowledge layer.

The behavioral layer is different — it's not what you know but how you decide. I built a DNA document architecture that captures exactly that, bootstraps a digital twin from it. Open source.

Is the decision-layer something you've tried to capture, or mostly knowledge/notes so far?
```

---

### Template D — Digital Legacy / Estate Planning
Use for: Rank 4 targets; reference their specific post about legacy or AI avatars

```
Hey [Name] — your post about [specific reference] resonated. Most AI avatar projects capture what a person said — not how they'd decide on something new.

I've built a system for the second part: behavioral DNA documents that let an LLM make decisions the way you would. Open source, validated on 18 real-life scenarios.

What's the gap you haven't solved — capturing the person, or making it persistent and usable?
```

---

### Template E — LLM Researcher / Experimenter
Use for: Rank 5 targets; reference specific paper, benchmark, or experiment they mentioned

```
Hey [Name] — saw your work on [specific reference to paper, post, or repo]. I've been tackling the persona consistency problem from a practitioner angle rather than research.

Built a recursive self-feed architecture — behavioral DNA + boot tests — that maintains identity across sessions. 18/18 fidelity on real-life decision scenarios. Open source.

Are you approaching this from a research angle, or are you building something practical? (The architecture differs between the two.)
```

---

### Follow-Up Template (Day 5 — use if no reply)
Use only once. Never send a second follow-up.

```
Hey [Name] — following up on my message [X days] ago.

Different angle: the [specific thing they're building or working on] — have you considered documenting the behavioral layer of it, not just the knowledge or capability layer?

Happy to share the architecture if useful. Either way, keep shipping.
```

---

### Objection Response Templates

**Objection: "What is this exactly?"**
```
It's a skill suite for building a behavioral digital twin — an LLM that makes decisions the way you would, even starting from a cold session. The core is a DNA document (your values, micro-decisions, constraints) + boot tests that verify alignment.

There's a 90-min guided session where I walk you through building yours, and it's all open source so you can self-install if you prefer.

What part of the problem is most live for you right now?
```

**Objection: "How much does it cost?"**
```
The skill suite is fully open source — free to install. If you want me to walk you through building your DNA core live, that's a 90-minute session at $97.

If you'd rather self-install and figure it out: https://github.com/l12203685/digital-immortality — README has the setup path. I'm around if you hit friction.
```

**Objection: "I don't have time right now"**
```
No rush. The open source repo isn't going anywhere.

One question before you go: what's the trigger that would make this feel urgent? Is it when a project breaks down because you couldn't brief someone fast enough? Or something else?

(Asking because that's usually when people actually book the session.)
```

**Objection: "I can build this myself"**
```
You probably can — the repo is open source and the architecture is documented. Most people who say that either do build it themselves (and that's the right answer) or hit the calibration step and realize the guided session saves 3-4 hours.

Either path is fine. If you self-build and hit a wall, the session offer stands.
```

**Objection: "Is this just another AI wrapper?"**
```
No — the insight is that behavioral alignment is a data problem, not a model problem. The DNA document is the data layer. The LLM is just the runtime.

The validation is 18/18 real-life decision fidelity on cold start — meaning the LLM makes the same call the person would on scenarios it has never seen, starting from scratch.

Happy to walk through the architecture for 10 minutes if you want to evaluate it properly.
```

---

## Section 3 — Qualification During Reply Thread

After receiving a reply, run this decision tree before responding.

```
Did they answer the question I asked?
  YES → Continue conversation (their answer reveals the problem)
  NO (pivoted to a different topic) → Acknowledge, then redirect to the problem question

Do they describe a concrete problem that this skill solves?
  YES → Move toward session offer (see below)
  NO (just curious, no clear problem) → Ask one more clarifying question: "What's the specific thing that would need to be solved for this to be useful to you?"

Concrete problem identified (cold start, identity drift, behavioral spec, decision capture)?
  YES → Offer the session:
    "The 90-min guided session covers exactly that — [describe their specific problem and what they'd walk out with].
     It's $97. If it's not useful, I'll refund it. [payment link]"
  NO → Continue qualifying (max 2 more exchanges); if still no concrete problem, close politely

Price friction after session offer?
  "The repo is fully open source — self-install is free. The session is for if you want to skip the setup friction and walk out with a working DNA core."
  → If they still push back: share the GitHub link, mark as SELF_SERVE lead, follow up in 14 days

Ghosted after session offer?
  → Day 3: "Did you get a chance to look at the repo?" (one message only)
  → If no reply: mark CLOSED. Do not follow up again.
```

**Who to spend time on (green light):**
- Describes a specific problem in their own words
- Is building something where the problem is live (not hypothetical)
- Has at least one buying signal
- Responds within 48h of each message

**Who to pass (red flag — cut the thread):**
- Asks for free advice about their specific implementation (not a buyer, is using you as a free consultant)
- Has responded 3+ times with no movement toward session offer (low urgency)
- Pivots every message to a different topic (unfocused buyer = long sales cycle, low close rate)
- Mentions they "already have something like this" without expressing a problem with it

---

## Section 4 — Conversion Funnel

### Stage map

```
IDENTIFIED → QUEUED → CONTACTED → REPLIED → QUALIFIED → OFFERED → BOOKED → PAID → DELIVERED
```

| Stage | Definition | SLA |
|-------|------------|-----|
| IDENTIFIED | Found via search, scored ≥3 | — |
| QUEUED | Added to tracking file with template assigned | within 24h of IDENTIFIED |
| CONTACTED | First DM sent | within 72h of QUEUED |
| REPLIED | They responded to any message | — |
| QUALIFIED | Concrete problem confirmed in reply thread | within 2 exchanges |
| OFFERED | Session offer sent with payment link | within 1 exchange of QUALIFIED |
| BOOKED | Payment link clicked | — |
| PAID | Payment confirmed | — |
| DELIVERED | Session completed, recap sent | within 24h of session |

### Conversion expectations (realistic baseline)

| Conversion point | Expected rate | 30-day implication |
|-----------------|---------------|--------------------|
| CONTACTED → REPLIED | 20-30% | 5 contacts → 1-2 replies |
| REPLIED → QUALIFIED | 50% | 1-2 replies → 1 qualified |
| QUALIFIED → OFFERED | 100% | always offer after qualification |
| OFFERED → BOOKED | 30-40% | 1 qualified → ~0.3-0.4 booked |
| BOOKED → PAID | 95%+ | near-certain if link clicked |

**Week 1 arithmetic:**
- Search: 2 hours → 10-15 candidates
- Qualify: 5 pass the threshold
- Contact: 5 DMs sent
- Expected replies: 1-2
- Expected sessions by Day 14: 0.5-1.0
- This is why 5 contacts in week 1 is not enough. See week 2 escalation.

**Week 2 (if Day 14 passes with 0 sessions booked):**
- Search again: 2 hours → 10-15 new candidates
- Contact 5 more, follow up on existing thread (if within 5-day window)
- If still 0 replies after 10 contacts: see Section 7 Diagnostic

---

## Section 5 — Tracking System

### File: results/skill_outreach_tracker.jsonl

One entry per contact. Append-only. Never edit existing entries — add a new entry for each state change.

**Entry format:**
```json
{
  "date": "2026-04-10",
  "contact_id": "C001",
  "platform": "github|twitter|discord|linkedin|indiehackers",
  "handle": "@handle or github.com/username",
  "archetype": "agent_dev|founder_os|pkm_builder|digital_legacy|llm_researcher",
  "score": 4,
  "score_breakdown": {
    "stated_problem": 2,
    "active_7d": 1,
    "building_in_domain": 1,
    "buying_signal": 0,
    "dm_accessible": 1,
    "frustration_signal": 0
  },
  "qualifying_signal": "exact quote or description of what triggered qualification",
  "template_used": "A|B|C|D|E",
  "specific_reference": "what you referenced in the DM (repo name, post title, quote)",
  "stage": "IDENTIFIED|QUEUED|CONTACTED|REPLIED|QUALIFIED|OFFERED|BOOKED|PAID|DELIVERED|CLOSED",
  "stage_history": [
    {"stage": "IDENTIFIED", "date": "2026-04-10"},
    {"stage": "CONTACTED", "date": "2026-04-10"}
  ],
  "notes": "free text — anything that affects next action",
  "next_action": "description of what to do next and when",
  "revenue_usd": 0
}
```

**Revenue confirmation entry (add when PAID):**
```json
{
  "date": "2026-04-14",
  "contact_id": "C001",
  "stage": "PAID",
  "revenue_usd": 97,
  "session_format": "guided_onboarding_90min",
  "payment_method": "stripe|gumroad",
  "sop_112_milestone": "FIRST_SALE_14D"
}
```

### Daily review (takes 5 minutes)

Each day, open `results/skill_outreach_tracker.jsonl` and run this check:

```
For each contact in CONTACTED stage:
  - Days since first DM > 5? → Send follow-up (if not already sent) or mark CLOSED
  - Days since follow-up > 3? → Mark CLOSED

For each contact in REPLIED stage:
  - Have you responded? → Respond within 24h of their message
  - Is the thread going nowhere after 3 exchanges? → Offer the session or close

For each contact in OFFERED stage:
  - Days since offer > 3? → Send one check-in ("did you get a chance to look at the repo?")
  - Days since check-in > 3? → Mark CLOSED

For each contact in BOOKED stage:
  - Payment confirmed? → Proceed to SOP #111 delivery protocol
  - No payment after 48h? → Resend payment link once, then mark CLOSED
```

### Weekly pipeline review

Every 7 days, run this aggregate check:

```
Total contacts this week:
  CONTACTED: N
  REPLIED: N (reply rate = REPLIED/CONTACTED)
  QUALIFIED: N
  OFFERED: N
  BOOKED: N
  PAID: N ($X total)

If reply rate < 10%:
  → Templates are too generic — add more personalization (specific reference is missing or weak)
  
If REPLIED → QUALIFIED < 30%:
  → Targeting is off — qualifying score threshold too low; raise to ≥4
  
If QUALIFIED → BOOKED < 20%:
  → Session offer is wrong — test a different framing or price anchor
  
If pipeline has < 3 contacts in CONTACTED stage:
  → Run another search session (Section 1.2) immediately
```

---

## Section 6 — Week-by-Week Execution Plan

### Week 1 (Day 1-7): Seed the pipeline

**Day 1 (today, 2026-04-10):**
- [ ] Run GitHub search queries (1.2) — extract 10 candidates
- [ ] Run Twitter/X search queries (1.2) — extract 5 candidates
- [ ] Score all candidates against 1.3 criteria
- [ ] Select top 5 (score ≥3), assign templates
- [ ] Send 5 DMs — before end of day
- [ ] Log all 5 in `results/skill_outreach_tracker.jsonl`

**Day 2-5:**
- [ ] Check for replies daily (morning)
- [ ] Respond within 24h to any reply
- [ ] Run reply thread qualification (Section 3)
- [ ] If qualified: send session offer with payment link

**Day 6-7:**
- [ ] Send follow-up to any CONTACTED contacts with no reply (if ≥5 days since DM)
- [ ] Join 1 Discord server (LangChain or Obsidian) — introduce or engage in ≥1 relevant thread
- [ ] Run weekly pipeline review (Section 5)

**Week 1 target:** 5 contacts in pipeline, ≥1 reply, ≥1 session offer sent.

---

### Week 2 (Day 8-14): Scale and close

**Day 8:**
- [ ] Run Discord search (1.2) — extract 5 candidates from server(s) joined Week 1
- [ ] Run LinkedIn search (1.2) — extract 5 candidates
- [ ] Score and select top 5
- [ ] Send 5 more DMs (total: 10 contacts in pipeline)
- [ ] Log in tracker

**Day 8-13:**
- [ ] Daily reply check and response (24h SLA)
- [ ] Follow up on any OFFERED contacts from Week 1 (3 days since offer)
- [ ] Close any contacts that have passed 5-day window with no reply and no follow-up sent

**Day 14 — First-sale checkpoint:**
- [ ] Check tracker: any PAID entries?
  - YES → Branch 1.3 alive gate met. Log to `results/revenue_log.jsonl`. Begin SOP #111 delivery.
  - NO → Run Section 7 Diagnostic immediately.

**Week 2 target:** ≥1 PAID ($97 confirmed). Branch 1.3 alive.

---

### Week 3 (Day 15-21): Expand channels and hit $291

**Day 15-16:**
- [ ] Run Indie Hackers search (1.2) — extract 5 candidates
- [ ] Run Hugging Face forums search — extract 3 candidates (Rank 5 archetype)
- [ ] Send 5 more DMs (total: 15 contacts in pipeline)

**Day 17-21:**
- [ ] Continue daily pipeline management
- [ ] Deliver any booked sessions (SOP #111)
- [ ] Send session recaps within 24h
- [ ] After each delivered session: offer second session if DNA is thin (SOP #111 G3)

**Week 3 target:** $291 total (3 sessions paid).

---

### Week 4 (Day 22-30): Close to $500

**Day 22-24:**
- [ ] Review all DELIVERED contacts — any willing to refer?
  Script: "If you know anyone working on [similar problem], I'd appreciate you passing along the repo link or my handle."
- [ ] Re-engage any contacts that were QUALIFIED but went cold (>7 days silent) with one message:
  "Quick check-in — did you end up solving the [specific problem they described]? Curious what path you took."
- [ ] Send 3-5 more DMs to new contacts from any channel

**Day 25-30:**
- [ ] Close pipeline — deliver all booked sessions
- [ ] Tally revenue: is it ≥$500?
  - YES: log SOP_112_30D_TARGET_MET in `results/revenue_log.jsonl`; proceed to Section 8 (scaling trigger)
  - NO: log shortfall, run Section 7 Diagnostic, set 30-day reset

**Week 4 target:** $500 total (5 sessions paid). SOP #112 30-day target met.

---

## Section 7 — Diagnostic (run if stuck)

### If Day 14 passes with $0 (0 sessions booked):

**Step 1 — Check template quality**
```
Open the 5 DMs you sent. For each one:
- Did you reference something specific (repo name, post title, quote)?
  NO → This is the failure. Generic outreach = no reply. Fix before sending more.
- Did you ask a question at the end?
  NO → DM is a pitch, not a conversation. Rewrite with a question.
- Was it more than 4 sentences?
  YES → Too long. Trim.
```

**Step 2 — Check target quality**
```
Open the 5 targets. For each one:
- Did they score ≥3 on the qualification criteria?
  NO → You contacted below-threshold targets. Raise the bar.
- Did their qualifying signal actually state the problem in their own words?
  NO → You inferred the problem. Targets must state it themselves.
- Were they active in the last 7 days?
  NO → Contacting inactive users. Fix the search filter.
```

**Step 3 — Check channel**
```
Which platform had the highest reply rate?
  → Double down on that platform in Week 2-3.
Which platform had 0 replies?
  → Drop it for now. Platforms have different DM cultures.
  
GitHub note: GitHub profiles rarely check DMs. Try Issues tab ("I noticed your repo does X — curious if you've run into Y") or their Twitter link from their GitHub profile.
Discord note: DMs in Discord have high spam probability. Engage in a public channel first, then DM after they've seen your name.
```

**Step 4 — Check the offer framing**
```
If you received replies but nothing converted to OFFERED:
- Did you move too fast to the offer? (Did you offer before confirming they have a concrete problem?)
  YES → Slow down. Add one more qualifying exchange before the offer.
- Did you describe the session output clearly? (What they walk out with: working DNA core, boot test passing, recursive engine configured)
  NO → Add the output contract to your session offer message.
- Did you anchor price before or after describing value?
  BEFORE → Reverse the order: value first, price second.
```

**Step 5 — If all templates are clean but still 0 replies after 10 contacts:**
```
The problem is platform choice, not template quality.
→ Switch primary channel to Discord (join LangChain server, engage publicly in #show-and-tell, then DM)
→ Discord has the highest density of Rank 1 targets (AI agent developers) and a culture of peer outreach
→ Spend 30 minutes engaging publicly (answer a question or share an observation) before sending any DM
```

---

## Section 8 — Scaling Trigger (post-$500)

After $500 in 30 days is confirmed, do not increase outreach volume. Instead:

**Trigger 1 — Group session format ($197 × 4-6 people)**
- Activate when: ≥2 booked contacts have similar problems (same archetype)
- Format: 90-min group onboarding, same structure as SOP #111 but with peer calibration benefit
- Price: $197/person (higher than individual because of social proof and peer learning)
- Benefit: 6x revenue per session-hour ($32/hr → $197+/hr)

**Trigger 2 — Inbound pipeline (content-driven)**
- Activate when: ≥3 inbound contacts in 30 days from GitHub or Discord (without outreach)
- Action: shift primary channel from DM outreach to SOP #83 (daily posting ritual) + SOP #01 (audience building)
- Note: this unblocks the original Branch 1.3 path (the audience gate is no longer the blocker once inbound is proven)

**Trigger 3 — Async audit product ($197, no session)**
- Activate when: ≥2 contacts express interest but cannot commit to 90-min live session (timezone, schedule)
- Format: client sends their DNA draft → you review async → deliver written feedback within 48h
- Price: $197 (higher than session because async = no scheduling friction for them, more flexibility for you)

**Do NOT activate scaling until $500 in 30 days is confirmed.**
Premature scaling = diffused effort = nothing gets done.

---

## Section 9 — Revenue Log Protocol

**File:** `results/revenue_log.jsonl`

Log every financial event here, append-only.

```json
{"date": "2026-04-14", "type": "skill_onboarding", "format": "guided_session_90min", "revenue_usd": 97, "contact_id": "C001", "archetype": "agent_dev", "platform": "github", "sop_112_milestone": "FIRST_SALE_14D", "cumulative_30d": 97}
{"date": "2026-04-18", "type": "skill_onboarding", "format": "guided_session_90min", "revenue_usd": 97, "contact_id": "C003", "archetype": "founder_os", "platform": "twitter", "sop_112_milestone": "SECOND_SALE", "cumulative_30d": 194}
{"date": "2026-04-21", "type": "skill_onboarding", "format": "guided_session_90min", "revenue_usd": 97, "contact_id": "C007", "archetype": "pkm_builder", "platform": "discord", "sop_112_milestone": "291_MILESTONE_21D", "cumulative_30d": 291}
```

**Monthly summary format (append at end of 30-day window):**
```json
{"date": "2026-05-10", "type": "monthly_summary", "period": "2026-04-10_to_2026-05-09", "sessions_delivered": 5, "revenue_usd": 500, "contacts_reached": 20, "reply_rate": 0.25, "conversion_rate_to_paid": 0.25, "top_archetype": "agent_dev", "top_platform": "discord", "sop_112_status": "30D_TARGET_MET|BELOW_TARGET", "next_action": "..."}
```

---

## Connections

| SOP | Role |
|-----|------|
| SOP #110 | Strategy and archetype definitions — SOP #112 operationalizes it |
| SOP #111 | Delivery protocol — fires after BOOKED stage in this SOP |
| SOP #97 | Consulting revenue — parallel outreach infrastructure, same tracking format |
| SOP #83 | Daily posting — generates inbound over time, reduces outreach dependency |
| SOP #82 | Revenue milestone tracker — skill revenue feeds M1, M2, M3 |
| SOP #85 | Gumroad product — fallback CTA for contacts who won't book a session |
| SOP #99 | Recursive Engine Health Check — referenced in session delivery |

---

## Self-Test

**Scenario:** It is Day 1. You have found a GitHub profile: @ai_tinkerer, repo "agent-persona" (32 stars, last commit 3 days ago). Their README says "I'm still fighting cold-start character drift between sessions — any approaches welcome." They have a Twitter linked from their GitHub profile with 180 followers and a post from 2 days ago asking if anyone has solved "LLM persona persistence."

**Expected execution:**
- Score: stated_problem (+2), active_7d (+1), building_in_domain (+1), dm_accessible (+1) = 5 → HIGH PRIORITY
- Template: A (AI Agent Developer)
- Reference: "agent-persona repo" + "your post about LLM persona persistence from 2 days ago"
- Platform: Twitter (more responsive than GitHub DMs)
- Send within 24h
- Log as C001, stage CONTACTED
- If reply → run Section 3 qualification thread → offer $97 session if problem is confirmed

**Anti-patterns (SOP #112 violations):**
- Sending to a profile with no clear problem statement (score < 3)
- Sending the template without a specific reference ("I came across your work" → delete)
- Offering the session in the first message (pitching before qualifying)
- Not logging the contact (tracker is the ground truth; memory is not)
- Sending follow-up before Day 5 (premature follow-up signals desperation)
- Sending more than one follow-up (hard limit: one follow-up, then close)
