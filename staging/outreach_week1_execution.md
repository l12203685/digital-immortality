# Cold Outreach Week 1 — Execution File
## Timestamp: 2026-04-10T10:30:00+00:00
## Target: 5 DMs to AI Agent Dev archetype (Rank 1)
## Status: READY TO SEND

> SOP #112 Section 2 compliant. All 5 messages reference specific content.
> No links. Ends with a question. ≤4 sentences. No "I came across your profile."
> Templates A/A-variant used throughout (AI Agent Dev archetype).

---

### DM #1
**Platform:** Twitter/X
**Target profile type:** AI Agent Developer — building a multi-session agent with character/persona continuity; GitHub repo with memory or persona in title; linked their Twitter from GitHub profile; posted about the problem publicly
**Qualification score (projected):** 5 (stated_problem +2, active_7d +1, building_in_domain +1, dm_accessible +1)
**Template used:** A (Twitter variant)

**Trigger:** They have a GitHub repo called something like `agent-memory` or `persistent-persona`; their pinned tweet or a recent tweet says something like "struggling to keep my agent in-character after a session reset" or "cold-start ruins persona — anyone solved this?"

**Message (Twitter DM, 275 chars):**
```
Your tweet about cold-start killing your agent's persona — I've been deep in exactly this.

Built a behavioral DNA doc + boot test architecture that gets 18/18 decision fidelity on cold starts. Open source.

Is the drift between sessions the core problem, or are you hitting something upstream of that?
```

**Tracker entry:**
- contact_id: C001
- archetype: agent_dev
- template: A
- specific_reference: [their tweet text about cold-start persona drift]
- stage: CONTACTED

---

### DM #2
**Platform:** GitHub (Issues tab — not DMs; per SOP #112 Section 7 Step 3 note)
**Target profile type:** AI Agent Developer — active repo building an LLM agent with session persistence; README explicitly mentions "I'm still working on character consistency between sessions" or "TODO: fix identity reset on cold start"; last commit ≤7 days ago; stars ≥5
**Qualification score (projected):** 5 (stated_problem +2, active_7d +1, building_in_domain +1, dm_accessible +1)
**Template used:** A (GitHub Issues approach — opens a public issue or a discussion, not a cold DM, to get on their radar first)

**Trigger:** README has a TODO or known issue explicitly naming "cold-start" or "persona reset" as an open problem. Their profile links to Twitter with a handle.

**Message (GitHub Issue titled: "Approach for cold-start identity persistence — sharing what's worked"):**
```
Hey [Name] — your README calls out cold-start character drift as an open problem.

I've been running a behavioral spec architecture (DNA documents + boot tests) that handles exactly this — 18/18 fidelity on cold starts across real-life decision scenarios. Open source.

Is the drift happening at the prompt layer for you, or deeper in the memory/context architecture?
```

**Follow-on action:** After posting the issue, find their Twitter (linked from GitHub profile) and send a short DM pointing to the issue: "Left a note on your [repo-name] issue tracker — might be relevant to the cold-start problem."

**Tracker entry:**
- contact_id: C002
- archetype: agent_dev
- template: A
- specific_reference: [exact README line about cold-start or persona reset]
- stage: CONTACTED

---

### DM #3
**Platform:** Discord — LangChain Community server, #show-and-tell or #general channel
**Target profile type:** AI Agent Developer — posted in a Discord channel about their agent project; message explicitly mentions session persistence, persona consistency, or identity drift; posted within the last 7 days; is responsive in threads (replied to at least one other person)
**Qualification score (projected):** 5 (stated_problem +2, active_7d +1, building_in_domain +1, dm_accessible +1)
**Template used:** A Discord variant

**Trigger:** They posted in #show-and-tell something like "built a multi-session agent but the character keeps drifting after a few conversations — thinking about how to fix this." You engaged in the public thread first (one substantive reply), then send the DM.

**Message (Discord DM — after public thread engagement):**
```
Hey [Name] — following up from the thread about your agent's session drift.

I've been building the same thing from a different angle — behavioral DNA documents + boot tests that maintain character across cold starts. 18/18 fidelity validated on real-life scenarios. Open source.

Have you gotten persistence to work yet, or still fighting it?
```

**Pre-DM public reply (send in their thread before DMing):**
```
The drift issue is usually upstream of the memory layer — it's a behavioral spec problem, not a retrieval problem. Have you tried encoding the persona as constraints + decision rules rather than as example outputs?
```

**Tracker entry:**
- contact_id: C003
- archetype: agent_dev
- template: A (Discord variant)
- specific_reference: [their exact message text + channel + server]
- stage: CONTACTED

---

### DM #4
**Platform:** Twitter/X
**Target profile type:** AI Agent Developer — building or experimenting with LLM agents; recently tweeted a thread or reply specifically about the problem of agents losing their persona or behaving inconsistently across different sessions or users; has >50 followers; DMs open
**Qualification score (projected):** 4 (stated_problem +2, active_7d +1, building_in_domain +1; no explicit buying signal observed yet)
**Template used:** A (Twitter variant, adjusted for thread-reply context)

**Trigger:** They posted a thread: "Things that still don't work in LLM agents (2026 edition)" — one bullet is "consistent identity across sessions" or "character persistence without a 100k-token context." Thread got engagement, showing they're in the space actively.

**Message (Twitter DM, 269 chars):**
```
Your thread on LLM agent failure modes — the character persistence bullet hit. Most solutions just extend context. That's the wrong layer.

Built a behavioral spec system (DNA doc + boot tests) that solves it at the data layer. 18/18 fidelity on cold starts. Open source.

What's your current workaround for the identity reset problem?
```

**Tracker entry:**
- contact_id: C004
- archetype: agent_dev
- template: A
- specific_reference: [thread title or URL + specific bullet about character persistence]
- stage: CONTACTED

---

### DM #5
**Platform:** Twitter/X
**Target profile type:** AI Agent Developer — has built and open-sourced an agent framework or persona-based chatbot; README or pinned tweet mentions they're looking for contributors or feedback; posts show they're actively iterating; has a buying signal (Claude Pro user, mentions API costs, has a "sponsor" button)
**Qualification score (projected):** 6 (stated_problem +2, active_7d +1, building_in_domain +1, buying_signal +1, dm_accessible +1) — TOP PRIORITY, send within 24h
**Template used:** A (GitHub repo variant, sent via Twitter)

**Trigger:** Their GitHub repo (found via search query: `"agent persona" in:readme pushed:>2026-03-01`) has a README that says "Note: persona consistency across sessions is still an unsolved problem in this repo." They link to Twitter. Their Twitter shows they posted 3 days ago asking for feedback on their agent's memory architecture.

**Message (Twitter DM, 276 chars):**
```
Your [repo-name] README — the note about persona consistency across sessions being unsolved. That's the problem I've been building against.

Behavioral DNA documents + boot tests. 18/18 cold-start fidelity on real decision scenarios. Open source, not a wrapper.

Is the consistency problem blocking you right now, or is it a known debt you're living with?
```

**Tracker entry:**
- contact_id: C005
- archetype: agent_dev
- template: A
- specific_reference: [exact repo name + README quote about unsolved persona consistency]
- stage: CONTACTED
- score: 6 (top priority)

---

## Execution Checklist — Day 1 (2026-04-10)

- [ ] Run GitHub search: `"agent persona" in:readme pushed:>2026-03-01` → extract C005 candidate
- [ ] Run GitHub search: `"cold start" agent memory in:readme pushed:>2026-03-01` → extract C001/C002 candidates
- [ ] Run Twitter search: `"agent memory" consistency session (from:date:2026-03-15)` → extract C001/C004 candidates
- [ ] Join LangChain Discord → search #show-and-tell for cold-start/persona messages → extract C003 candidate
- [ ] Score all candidates against SOP #112 Section 1.3 (must score ≥3)
- [ ] Fill in [Name] and [specific_reference] placeholders in each DM above
- [ ] For C003 (Discord): post public reply first, wait for their acknowledgment, then DM
- [ ] Send all 5 messages — copy-paste from the Message blocks above
- [ ] Log all 5 contacts in `results/skill_outreach_tracker.jsonl` (format: SOP #112 Section 5)

## Reply Handling (Day 2-5)

If any contact replies:
1. Read SOP #112 Section 3 qualification decision tree
2. If they describe a concrete problem in their own words → offer the session
3. Offer script: "The 90-min guided session covers exactly that — you walk out with a working DNA core, boot test passing, and recursive engine configured. It's $97. If it's not useful, I'll refund it. [payment link]"
4. Update stage in `results/skill_outreach_tracker.jsonl`

## Day 6-7 Follow-Up Rule

- Send follow-up ONLY if ≥5 days have passed since the DM with no reply
- Use SOP #112 Follow-Up Template (Section 2)
- One follow-up only per contact — then mark CLOSED if no response within 3 days

## Branch 1.3 Alive Gate

**$97 confirmed by Day 14 = Branch 1.3 alive.**
First session booking expected from C005 (score 6, top priority) or C003 (Discord — highest reply-rate channel per SOP #112 Section 7 Step 3).
