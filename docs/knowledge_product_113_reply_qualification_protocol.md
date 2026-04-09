# SOP #113 — Reply Qualification Protocol

> Domain: Revenue / Skill Commercialization / Inbound Conversion
> Created: 2026-04-10T UTC (cycle 285)
> Status: OPERATIONAL — run on every reply received from SOP #112 outreach
> Decision label: REPLY_QUALIFICATION_BUYER_VS_CURIOUS
> Revenue target: convert REPLIED → PAID at ≥30% rate
> Upstream: SOP #112 (cold outreach — generates the replies this SOP processes)
> Downstream: SOP #111 (guided onboarding delivery — fires after PAID)
> Posting queue: after first paid session confirmed (same gate as SOP #112 thread)

---

## Why This Exists

SOP #112 gets replies. This SOP decides what to do with them.

Without a qualification protocol, every reply triggers one of two failure modes:
1. **Over-invest** — you spend 5+ exchanges on someone who was never going to buy, treating curiosity as intent
2. **Under-invest** — you move too fast to the session offer and break rapport before the buyer is ready

SOP #113 eliminates both. It gives you a pass/fail decision on every reply within 2 exchanges, and a precise script for each case.

**The core question this SOP answers:**
Is this person a **buyer** (has a live problem, will pay to solve it) or **curious** (interested in the concept, not the solution)?

These two groups require completely different responses. Treating them the same wastes time on the curious and misses the window on the buyer.

**Revenue connection:**
REPLIED → PAID is the highest-leverage conversion in the funnel. This is where $97 either happens or doesn't. SOP #113 is what closes that gap.

---

## G0 — Trigger Condition

**Fire this SOP when:** A contact in `results/skill_outreach_tracker.jsonl` transitions from CONTACTED to REPLIED.

**Inputs required before running:**
- The full text of their reply
- Their original qualifying signal (from the tracker entry)
- Their archetype (agent_dev / founder_os / pkm_builder / digital_legacy / llm_researcher)
- Their score (from SOP #112 Section 1.3)
- How many days since first contact

**Do not run this SOP if:**
- The "reply" is a like, reaction, or emoji-only response (not a reply — no text, no signal)
- The reply is from a contact you did not initiate (spam, unrelated DM — mark CLOSED immediately)
- You have already sent the session offer in a previous exchange (jump to G5 instead)

**Update tracker immediately on reply:**
```json
{
  "date": "[today]",
  "contact_id": "[ID]",
  "stage": "REPLIED",
  "stage_history": [..., {"stage": "REPLIED", "date": "[today]"}],
  "reply_text": "[exact text of their reply]",
  "notes": "Running SOP #113 qualification",
  "next_action": "Qualify within 24h — buyer or curious?"
}
```

---

## G1 — Scope and Inputs

**What this SOP covers:**
- First reply analysis (buyer vs. curious classification)
- Second exchange qualification (if first reply is ambiguous)
- Session offer trigger (when to make the offer and how)
- Graceful close (when to stop and why)

**What this SOP does NOT cover:**
- How to find contacts (SOP #112 Section 1)
- What to send as a first DM (SOP #112 Section 2)
- How to deliver the session after booking (SOP #111)
- Objection handling after the price is stated (covered in G4 below)

**Time budget per contact:**
- Classification: 5 minutes (read the reply, score it, decide the path)
- Response drafting: 10 minutes (use the templates in G2, personalize the [specific] fields)
- Total per exchange: 15 minutes max
- Maximum exchanges before close or offer: 3

**Input files:**
- `results/skill_outreach_tracker.jsonl` — pipeline state
- SOP #112 Section 3 — decision tree (this SOP supersedes and expands it)

---

## G2 — Step-by-Step Protocol

### Step 1 — Read the reply. Do not respond yet.

Read the full reply text. Then answer these four questions:

```
Q1: Did they answer my question?
  YES → their answer reveals their level of problem urgency
  NO  → they pivoted (this is a signal — see G4 Edge Case 1)

Q2: Did they use any of these words or phrases?
  "I've been struggling with..."
  "I can't get X to work"
  "I keep running into..."
  "The problem is..."
  "I tried [X] but it doesn't..."
  "This breaks when..."
  "I need to solve..."
  → If YES to any: high buyer signal. Continue to Step 2 — Buyer Path.
  → If NO: continue to Step 2 — Curious Path.

Q3: Is the problem they described one that this skill directly solves?
  Direct match: cold-start identity drift, behavioral spec, decision capture, persona consistency
  Partial match: related but not exact — may need one clarifying question
  No match: they're interested in the domain but have a different problem → Curious Path

Q4: What is their urgency signal?
  HIGH urgency: "right now", "blocking my project", "deadline", "this week", "I need to fix this"
  MEDIUM urgency: "I'm working on this", "part of my roadmap", "been thinking about it"
  LOW urgency: "I'm curious", "just exploring", "someday", "interesting concept"
  → HIGH or MEDIUM: proceed with buyer path
  → LOW only: curious path
```

---

### Step 2A — Buyer Path (concrete problem confirmed)

**Criteria for Buyer Path:**
- Answered Q2 with ≥1 phrase indicating a live problem
- Problem maps to what the skill solves (Q3 = direct or partial match)
- Urgency is HIGH or MEDIUM (Q4)

**Response template — Buyer Path, Exchange 2:**

```
[Acknowledge their specific problem in their exact words — 1 sentence]

[Bridge to the outcome: what they'd walk out with from the session — 1-2 sentences]

The 90-minute guided session covers exactly this — you walk out with a working DNA core, your first boot test passing, and the recursive engine configured. It's $97. If it's not useful, I'll refund it. [payment link]
```

**Rules for this template:**
- First sentence MUST echo their exact words (not your paraphrase)
- Do not add qualifications ("I think this might help you" — delete)
- Do not describe the product architecture — describe the output they get
- Payment link goes at the end, not in the middle
- Do not ask another question if the problem is confirmed — make the offer

**Example (Agent Dev archetype):**

Their reply: "Yeah cold-start drift is brutal. Every new session I have to re-explain who the agent is. It's eating 20% of my context window and the persona still slips."

Your response:
```
Re-explaining the agent's identity every session and watching the persona slip anyway — that's the exact failure mode the DNA architecture was built to fix.

The session outputs a behavioral spec document that boots clean every time — no re-priming, consistent decisions from token 1. The boot test runs at session start and tells you immediately if alignment is off.

The 90-minute guided session covers exactly this — you walk out with a working DNA core, your first boot test passing, and the recursive engine configured. It's $97. If it's not useful, I'll refund it. [payment link]
```

---

### Step 2B — Curious Path (no concrete problem confirmed)

**Criteria for Curious Path:**
- Answered Q2 with NO live problem phrases
- Or urgency is LOW only
- Or the problem described is in the domain but doesn't map to the skill

**Response template — Curious Path, Exchange 2:**

One clarifying question. No offer. No pitch.

```
[Acknowledge what they said — 1 sentence]

[One specific question that surfaces whether there's a live problem beneath the curiosity]
```

**The clarifying question (pick the most relevant):**

For AI agent devs:
```
Is the persona consistency problem one you're actively trying to solve, or is it a known limitation you're working around?
```

For founders with personal OS:
```
What's the piece of your decision-making that lives most in your head right now — the part you couldn't brief someone else on in under 10 minutes?
```

For PKM builders:
```
Have you tried to capture the behavioral layer — how you decide — or has it mostly been knowledge and reference capture so far?
```

For digital legacy archetype:
```
What's the gap you've hit: is it capturing who the person is, or making that capture usable and persistent?
```

For LLM researchers:
```
Are you approaching persona consistency as a research problem or are you trying to build something that actually works in production?
```

**After Exchange 2 (Curious Path):**

If their Exchange 2 reply shows a concrete problem → pivot to Buyer Path (Step 2A).
If their Exchange 2 reply is still exploratory → one final exchange (Exchange 3), then close.

**Exchange 3 — Curious Path (final attempt):**
```
[Brief summary of what the skill does in 2 sentences]

If the [specific problem they described or adjacent problem] becomes live for you — the repo is open source and the session offer stands. github.com/l12203685/digital-immortality

[First name], good luck with [specific thing they mentioned].
```

This is a graceful exit that leaves the door open. Do not follow up after this unless they message again.

---

### Step 3 — Classify and update the tracker

After every exchange, update `results/skill_outreach_tracker.jsonl`:

```json
{
  "date": "[today]",
  "contact_id": "[ID]",
  "stage": "REPLIED|QUALIFIED|OFFERED|CLOSED",
  "qualification_path": "buyer|curious|ambiguous",
  "problem_confirmed": true|false,
  "problem_statement": "[their exact words describing the problem, if stated]",
  "urgency_signal": "high|medium|low",
  "exchange_count": 1|2|3,
  "offer_sent": true|false,
  "notes": "[anything that affects next action]",
  "next_action": "[specific next step + when]"
}
```

**Stage transitions:**
- REPLIED → QUALIFIED: concrete problem confirmed (buyer path criteria met)
- REPLIED → CLOSED: Exchange 3 sent with no problem confirmation
- QUALIFIED → OFFERED: session offer sent
- OFFERED → BOOKED: payment link clicked
- OFFERED → CLOSED: no response after 3 days + one check-in

---

## G3 — Qualification Criteria (Buyer vs. Curious)

### Buyer signals (green — proceed with offer)

Score each reply. ≥3 points = buyer path.

| Signal | Points | How to identify |
|--------|--------|-----------------|
| States a concrete problem in their own words | +2 | They say what breaks, what fails, what they can't get to work |
| Problem maps directly to what the skill solves | +2 | Cold-start drift, behavioral spec, decision capture, persona consistency |
| Uses urgency language | +1 | "right now", "blocking", "I need to", "this week", "keeps happening" |
| Describes a failed attempt at solving it | +1 | "I tried X but it doesn't work because Y" |
| Mentions a consequence of not solving it | +1 | "It's eating my context window", "clients notice", "slows down my builds" |
| Has a buying behavior signal | +1 | Mentions paid tools, courses, API costs — consistent with SOP #112 scoring |

Score ≥3: Buyer path. Make the offer in this exchange or the next.
Score 1-2: Curious path. One more qualifying exchange.
Score 0: No live problem. Graceful close.

### Curious signals (yellow — qualify further or close)

These patterns indicate engagement without commitment:

- "That's interesting" (no follow-up question or personal application)
- "I've been thinking about something like this" (no concrete context)
- "What exactly is this?" (pure information-seeking, no problem anchoring)
- "Cool project" (social acknowledgment, not problem engagement)
- "How does this compare to [other tool]?" (competitive framing, not problem framing)
- "I'm not building anything like that right now" (explicit no-problem signal)

One curious signal does not close the thread. Two consecutive curious signals = close after Exchange 3.

### Red flags (close immediately — do not offer)

These patterns indicate the contact is not a buyer and will not become one in this thread:

- Asks for free advice about their specific implementation (they want consulting, not the product)
- Reply is a counter-pitch (they're selling something to you)
- Describes a fundamentally different problem that this skill doesn't solve
- Expresses frustration with AI in general (not a specific solvable problem)
- Has replied 3+ times across multiple days with no problem statement emerging

**On red flag:** Close the thread cleanly.
```
Thanks for the conversation, [Name]. The repo is open source if you want to explore it on your own terms: github.com/l12203685/digital-immortality — good luck with [what they're building].
```
Do not offer the session. Do not follow up. Mark CLOSED.

---

## G4 — Edge Cases and Failure Modes

### Edge Case 1 — They pivoted to a different topic

**Symptom:** You asked about cold-start drift. They replied about something else entirely (their company, a different project, general AI commentary).

**What this means:** Low urgency or high social awareness — they replied to be polite, not because the problem is live.

**Response:** Acknowledge what they said in one sentence, then redirect with a focused question:
```
[Acknowledge their comment — 1 sentence]

Going back to the original question: [re-ask the question from your first DM, reworded slightly]. Is that something you're actively dealing with?
```

If they pivot again: close. Do not pursue a third redirect.

---

### Edge Case 2 — They ask about the open source repo before you've qualified them

**Symptom:** "Is this on GitHub? Can I see it?"

**What this means:** High curiosity, low urgency. They want to evaluate before committing. This is not a buyer signal — but it's not a close signal either.

**Response:** Give the link without hesitation, then pivot to qualification:
```
Yep — github.com/l12203685/digital-immortality. README has the setup path and the architecture overview.

While you're looking: is the [specific problem from your first DM] something you're hitting right now, or more of a future concern?
```

**Why this works:** Withholding the GitHub link kills trust. Giving it without a follow-up question abandons qualification. Give + ask.

---

### Edge Case 3 — They ask about price before you've confirmed a problem

**Symptom:** "How much does it cost?" (before you've established why they want it)

**What this means:** They're comparison-shopping or budget-checking. Not necessarily a buyer yet.

**Response:** Answer the price question directly, then immediately anchor it to the outcome:
```
The skill suite is fully open source — free to install. If you want me to walk you through building your DNA core live, that's a 90-minute session at $97.

What's the specific problem you're trying to solve? The output from the session depends on that.
```

**Why this works:** Hiding the price creates suspicion. Answering without context means they evaluate the price without knowing the value. Answer + anchor.

---

### Edge Case 4 — They're clearly a buyer but express price friction

**Symptom:** After you've confirmed their problem and made the offer: "That seems expensive" / "I'm not sure it's worth $97."

**This is not a close.** Price friction after a confirmed problem is a value articulation failure — they haven't connected $97 to their specific outcome.

**Response:**
```
The open source version is free — you can self-install from the repo and build your DNA core without paying anything.

The $97 is for the guided session: I walk you through the calibration live, we run the boot tests together, and you leave with something operational — not a draft you have to figure out later.

If the problem you described ([restate their exact problem in their words]) is live enough to be worth 90 minutes, the session is probably the faster path. If it's not that urgent, the repo is the right starting point.
```

Do not discount. Do not offer a free sample session. Reframe the offer as a choice between two legitimate paths.

---

### Edge Case 5 — They express interest but go quiet (ghost after warm reply)

**Symptom:** Exchange 1 was warm (buyer signals), but they haven't replied in 3+ days.

**Response (one message only):**
```
Hey [Name] — following up on our conversation about [specific problem they described].

Did you get a chance to look at the repo? Or did something change on your end?
```

If no reply after 3 more days: mark CLOSED. Do not send a third message. Ghosts after warm replies are usually: (a) genuinely busy, (b) got a competing solution, or (c) urgency dropped. None of these convert with more follow-up.

---

### Edge Case 6 — They ask for a free "sample" session or "just 15 minutes"

**Symptom:** "Can we just hop on a quick call first?" / "Can you give me a quick demo?" / "15 minutes to see if it's worth it?"

**What this means:** High interest, low urgency, unclear value perception. Not a hard no — but not a buyer yet.

**Response:**
```
The architecture is fully visible in the repo — github.com/l12203685/digital-immortality — so you can evaluate the methodology before committing to a session.

The 90-minute format isn't arbitrary: the first 20 minutes are identity anchor work that can't be rushed. A 15-minute preview would get you the architecture overview but not a working artifact.

If the [problem they described] is live: the $97 session gives you a working DNA core by the end. If you'd rather evaluate first, the repo is the demo.
```

Do not agree to a free 15-minute call. It sets the wrong anchor and creates a precedent that price is negotiable.

---

### Failure Mode 1 — Offering too early

**Pattern:** You made the session offer in Exchange 1 (before confirming a concrete problem).

**Why this fails:** You've converted yourself from a peer who's solving a similar problem into a salesperson. The rapport from your first DM — which got the reply — was built on peer positioning. Offering immediately breaks that.

**Recovery:** If they didn't respond to the premature offer, send one more message:
```
Ignore the offer in my last message — I jumped ahead.

What I actually wanted to know: [re-ask the qualifying question from your original DM]. That problem is what I'm most curious about.
```

---

### Failure Mode 2 — Spending 5+ exchanges on a curious contact

**Pattern:** You've had 4-5 back-and-forth exchanges. They're engaging but never describe a concrete problem. You keep probing.

**Why this fails:** This is a conversation that feels productive but converts at near-zero. The curious contact is getting value from talking to you without needing to buy anything. You're providing free consulting.

**Recovery:** Exchange 5 is the hard close:
```
[Name] — I've enjoyed this conversation. I'm going to be direct: I can't tell from our exchanges whether you have a live problem this solves or whether it's more of a conceptual interest.

If it's the latter, the repo is the right place to explore: github.com/l12203685/digital-immortality. I'm happy to answer questions in GitHub Issues.

If there's a specific thing you're trying to build or fix and you want to work through it properly: the $97 session is the right format. Happy to book if that's the case.
```

After this message: no further follow-up regardless of their response.

---

### Failure Mode 3 — Misclassifying curious as buyer (false positive)

**Pattern:** You ran Buyer Path because they used one buyer-signal phrase. They went through the session but their DNA work was shallow — no real commitment to the problem.

**How to detect retrospectively:**
- During the session, they struggled to answer the Identity Anchor questions (no concrete values come to mind)
- They said "I'm not sure this is what I need" mid-session
- They asked for a refund within 48h

**Prevention:**
- Score ≥3 buyer signals before making the offer — not ≥1
- Partial-match problems (Q3) require confirming the problem is live, not just adjacent
- "I've been thinking about this" without a concrete context = curious, not buyer

---

## G5 — Revenue Bridge

### The $97 booking — what converts it

The session offer converts when three things are true simultaneously:
1. **Problem confirmed** — they've stated it in their own words (not your paraphrase)
2. **Outcome clear** — they know exactly what they walk out with (working DNA core, passing boot test, recursive engine configured)
3. **Risk removed** — the refund guarantee is in the offer ("If it's not useful, I'll refund it")

If any of these three is missing when you send the offer, conversion rate drops significantly.

**The offer script that closes (mandatory format — do not vary):**

```
The 90-minute guided session covers exactly this — you walk out with a working DNA core, your first boot test passing, and the recursive engine configured. It's $97. If it's not useful, I'll refund it. [payment link]
```

Do not add qualifications. Do not change the order. Problem confirmation (from Exchange 1-2) does the setup work; this script closes.

---

### Conversion math — what SOP #113 produces

| Entry point | SOP #112 estimate | SOP #113 target |
|-------------|-------------------|-----------------|
| CONTACTED → REPLIED | 20-30% | (not affected — SOP #112 drives this) |
| REPLIED → QUALIFIED | 50% | 60% (better qualification = fewer false positives) |
| QUALIFIED → OFFERED | 100% | 100% (always offer after confirmed problem) |
| OFFERED → BOOKED | 30-40% | 35-45% (clear outcome + refund guarantee) |
| BOOKED → PAID | 95%+ | 95%+ (unchanged) |

**Expected output from 5 replies (week 1-2 baseline):**
- 3 qualified (60% of replies)
- 3 session offers sent (100% of qualified)
- 1-2 bookings (35-45% of offered)
- 1-2 paid sessions ($97-$194)

**If REPLIED → QUALIFIED is below 40% after 5 replies:**
- The contacts from SOP #112 were below-threshold (curiosity-seekers, not problem-havers)
- Raise the SOP #112 qualifying score to ≥4 (currently ≥3 is the floor)
- Return to SOP #112 Section 7 Diagnostic Step 2

**If QUALIFIED → BOOKED is below 20% after 3 offers:**
- The session outcome is not being described specifically enough
- Add more detail on what they walk out with (DNA core length, what the boot test measures, what the recursive engine does for them specifically given their archetype)
- Test the refund guarantee visibility — is it in every offer?

---

### Revenue pipeline state integration

After every exchange, run a 2-minute pipeline check:

```
Open results/skill_outreach_tracker.jsonl.

REPLIED contacts:
  → Replied < 24h ago? → You have 24h to respond (SLA: same-day)
  → Replied > 48h ago and no response from you? → Respond immediately

QUALIFIED contacts:
  → Offer not yet sent? → Send within next 24h
  → Offer sent > 3 days ago with no reply? → Send Edge Case 5 follow-up (once only)

OFFERED contacts with no booking:
  → < 3 days since offer: wait
  → 3 days: send check-in message (Edge Case 5 template)
  → 6 days: mark CLOSED

Branch 1.3 alive gate check:
  → Any PAID entry? → Gate met. Log to results/revenue_log.jsonl. Proceed to SOP #111.
  → No PAID by Day 14? → Return to SOP #112 Section 7. Do not wait.
```

---

### Post-conversion — what fires after PAID

When a contact transitions to PAID:

1. Log the revenue event:
```json
{
  "date": "[today]",
  "contact_id": "[ID]",
  "stage": "PAID",
  "revenue_usd": 97,
  "session_format": "guided_onboarding_90min",
  "payment_method": "stripe|gumroad",
  "archetype": "[their archetype]",
  "platform": "[platform of original contact]",
  "qualification_path": "buyer",
  "exchanges_to_close": 1|2|3,
  "sop_113_milestone": "FIRST_SALE|SECOND_SALE|..."
}
```

2. Activate SOP #111 (Guided Onboarding Delivery Protocol) immediately:
   - Send pre-session prep email within 2 hours of payment confirmation
   - Schedule session within 3 business days
   - Session must be delivered within 7 days of booking

3. After session delivery:
   - Send recap within 24h
   - Log DELIVERED status in tracker
   - If DNA was thin during session (< 40 lines): offer a follow-up session at $97 to deepen it

---

## Connections

| SOP | Role |
|-----|------|
| SOP #110 | Strategy and archetype definitions — defines who qualifies before SOP #112 contacts them |
| SOP #112 | Cold outreach — generates the REPLIED contacts that SOP #113 processes |
| SOP #111 | Session delivery — fires when SOP #113 produces a PAID contact |
| SOP #82 | Revenue milestone tracker — logs the $97 events that advance M1, M2, M3 |
| SOP #97 | Consulting revenue — parallel qualification logic; same buyer-signal taxonomy |
| SOP #85 | Gumroad product — fallback CTA for curious contacts who don't book a session |
| SOP #83 | Daily posting — generates inbound replies; SOP #113 processes those too |

---

## Self-Test

**Scenario:** C003 (Discord, agent_dev, score 5) replies to your DM:

> "Yeah I've actually been fighting this for a while. My agent sounds completely different between sessions — I have to add like 500 tokens of persona context at the start of every conversation just to keep it in character. It's eating my budget and it's still inconsistent."

**Expected execution:**
- Q1: Yes, answered your question
- Q2: Yes — "fighting this for a while", "eating my budget", "still inconsistent" — all concrete problem phrases
- Q3: Direct match — persona consistency across sessions = exactly what the DNA architecture solves
- Q4: HIGH urgency — "have to add 500 tokens", "eating my budget" = live, active cost
- Buyer score: stated problem (+2) + direct match (+2) + urgency (+1) + consequence described (+1) = 6 → Buyer Path
- Path: Step 2A — Buyer Path response immediately (Exchange 2 = offer)
- Offer: echo their exact words ("500 tokens of persona context... still inconsistent") → bridge to session output → $97 offer with refund
- Tracker update: stage → QUALIFIED → OFFERED in same exchange

**Anti-patterns (SOP #113 violations):**
- Asking another qualifying question when the problem is already confirmed (delays the offer unnecessarily)
- Paraphrasing their problem instead of echoing their exact words (breaks the rapport signal)
- Describing the architecture ("DNA documents are structured as...") instead of the output ("you walk out with...")
- Sending the offer without the refund guarantee ("if it's not useful, I'll refund it" removes the last friction point)
- Not updating the tracker after the exchange (tracker is the ground truth; memory is not)
- Spending Exchange 3 still qualifying when buyer signals are clear after Exchange 1
