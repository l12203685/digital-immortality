# SOP #88 — Discovery Call Protocol

> Domain: Consulting / Revenue
> Created: 2026-04-09T11:00Z
> Status: OPERATIONAL
> Trigger: G0 — SOP #86 fires (≥3 DMs/30d) AND inbound lead has responded to rate structure

---

## Why This Exists

SOP #86 (Consulting Rate Card) defines when to enter consulting mode and what to charge.
SOP #70 (DM Conversion) defines how to move a follower to a DM conversation.
Neither closes the gap between a DM that has self-qualified and an actual engagement.

**Gap identified:**
A lead says "I'm interested in a call." You have no script. You either over-explain (lose frame),
under-qualify (waste time), or fail to close (leave revenue on the table). All three are recoverable
with a pre-committed intake protocol.

**This SOP answers:** given an inbound lead who responded to your rate structure, run a
20-minute discovery call that either closes the engagement or produces a clean pass decision.

**Decision principles:**
- MD-148: Do not build demand-generation infrastructure without a capture protocol.
- MD-190: Pre-commit the qualification gate before hearing the pitch — prevents post-hoc rationalization.
- SOP #86 Kernel: $200/hr anchor. If lead can't evaluate that, pass in G2, not G5.

---

## Gate Sequence: G0 → G5

### G0 — Trigger Condition

Fire when ALL of:
- T1: SOP #86 is active (≥3 consulting DMs in last 30 days)
- T2: Inbound lead has responded to rate mention (not just liked/followed)
- T3: Lead has self-identified a problem domain (trading, career, productivity, or organism/digital twin)

If T3 not met → send: "What's the main thing you're trying to figure out right now?"
Wait for response before scheduling.

### G1 — Pre-Call Intake (async, 5 min before scheduling)

Send 3-question async qualifier before booking:
```
1. What's the core decision you're stuck on?
2. What have you already tried?
3. What does a good outcome look like in 90 days?
```

Qualify response:
- PROCEED: concrete problem + prior attempts + specific outcome target
- HOLD: vague (e.g., "just want to talk") → ask clarifying follow-up once
- PASS: no response after 48h → close thread politely

### G2 — Schedule + Frame (2-3 min)

Booking message:
```
[20-min discovery call — no pitch, no commitment]
I'll ask what you're working on, you ask me what I've done in that area.
If there's a fit, I'll tell you exactly what that looks like.
If not, I'll tell you who might help more.
[calendar link or time slot options]
```

If lead asks "what do you charge before we talk" → reference SOP #86 rate card.
Do not negotiate before G4.

### G3 — Call Execution (20 min max)

**Frame (first 2 min):**
> "I have 20 minutes. I'll spend 10 learning your situation, and if it's relevant, 10 showing you exactly how I'd approach it. At the end, one of us will say 'there's a fit here' or 'not yet.' Either is fine."

**Intake questions (minutes 2–10):**
1. "Walk me through the problem — what's actually happening?"
2. "What have you tried? What broke?"
3. "If this was fully solved, what changes in 90 days?"
4. [Listen. Do not interrupt with solutions yet.]

**Response decision (minute 10):**
- MATCH: problem overlaps with SOP #01-#87 domains (trading system, career architecture, decision OS, organism/digital twin) → go to G4
- PARTIAL: adjacent domain, unclear scope → offer 1-hour scoped diagnostic ($200 flat) → go to G4 with modified scope
- NO MATCH: outside expertise (operations, HR, product design, etc.) → pass with referral at minute 12, close gracefully

**Value demonstration (minutes 10–18, only if MATCH):**
Share 1 concrete framework from Edward's domain that directly applies.
Do not explain the full system. Show the diagnostic layer only.
Close with: "Based on what you described, here's what a 4-week engagement looks like."

**Close (minutes 18–20):**
> "Does that feel like the right scope to you?"
- YES → G4
- NOT SURE → "What would need to be true for it to feel right?" → address once, then G4 or close
- NO → clean pass, ask if there's a better framing, do not re-pitch

### G4 — Proposal (within 24h after call)

Send via same channel as DM:
```
[Proposal — [Lead Name] — [Domain]]

Problem: [1 sentence from their G1 intake]
Outcome target: [their 90-day answer]
Scope: [2–3 bullet deliverables, max]
Rate: $[X] (from SOP #86 rate card)
Duration: [2–4 weeks]
Start: [specific date]

To proceed: reply YES + I'll send the payment link.
To adjust scope: reply with what changes.
Pass deadline: [date + 5 days].
```

Proposal rules:
- One page max
- No discovery call notes in the doc — those are yours
- If lead ghosts 5 days → one nudge, then close thread

### G5 — Kill Conditions

Kill the engagement (not just this call) when:
- No response after proposal + 1 nudge
- Scope creep request before first invoice is paid
- Mismatch between stated problem (G1) and actual request (G3) that can't be resolved in 1 clarification
- Lead tries to negotiate below SOP #86 floor ($150/hr) — politely decline, hold frame

**Kill message:**
> "Sounds like the scope and structure aren't quite right for now. If that changes, same offer stands."

Never re-open a killed engagement within 30 days.

---

## Metrics

| Metric | Target |
|--------|--------|
| G1 response rate | ≥60% of T3-qualified leads |
| G3 → G4 conversion | ≥50% of calls |
| G4 → close rate | ≥40% of proposals sent |
| Call duration | ≤20 min (hard cap) |
| Time to proposal | ≤24h after G3 close |

---

## Anti-Patterns

| Pattern | Why it fails |
|---------|-------------|
| Skipping G1 async intake | Wastes call time on basic qualification |
| Over-explaining in G3 | Teaches instead of selling — client extracts value without paying |
| Negotiating before G4 | Destroys rate anchor before framing scope |
| Re-opening killed threads | Signals desperation, invites lowball re-entries |
| Proposing without 90-day target | No success criteria = no close |

---

## Integration

- SOP #86 (Consulting Rate Card) — defines rate structure and trigger condition
- SOP #70 (DM Conversion) — upstream: DM to consulting call pipeline  
- SOP #83 (Daily Posting Ritual) — generates inbound DMs
- SOP #85 (Gumroad Product) — lower-ticket alternative when G2 rate check fails

---

## Self-Test

Cycle 253 self-test: no discovery calls have occurred yet (0 DMs, M1 not started).
This SOP closes the gap: infrastructure exists (rate card, DM pipeline) but no intake protocol existed.
Trigger fires when SOP #86 activates (≥3 DMs/30d), which fires after SOP #83 daily ritual runs,
which fires after SOP #01 first post (human-gated).

Critical path remains: Edward posts SOP #01 → M1 → SOP #83 → SOP #86 → SOP #88.
