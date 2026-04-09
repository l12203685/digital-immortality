# SOP #104 — Async Audit Delivery Protocol

> Domain: Revenue / Consulting / Delivery
> Created: 2026-04-09T UTC (cycle 270)
> Status: OPERATIONAL
> Decision label: ASYNC_AUDIT_DELIVER_ON_PAYMENT
> Posting queue: Oct 27

---

## Why This Exists

SOP #97 created the consulting revenue protocol. It defines two products:
- $197 Async SOP Audit
- $97 Advisory Call

SOP #88 covers the discovery call protocol for the $97 advisory call.

**The gap this SOP closes:**
No protocol exists for what happens after someone pays $197 for an async audit.

The revenue protocol says "return written diagnostic with ≥3 specific gaps." It does not specify:
- What intake questions to ask the client
- How to analyze their situation against Edward's decision frameworks
- What the deliverable document looks like
- How to deliver and follow up
- When and how to collect a testimonial
- When to ask for a referral

Without this SOP, a paid engagement becomes a blank canvas problem — high variance output, inconsistent quality, no feedback loop.

**The chain this SOP completes:**

```
G0 (SOP #97): Outreach → warm reply → offer made
G1 (SOP #97): Client expresses interest
G2 (SOP #97): Payment link sent — $197 async audit
G3 (SOP #97): Payment clears
→ [GAP — SOP #104 starts here]
```

---

## Gate Sequence: G0 → G5

### G0 — Payment Receipt + Intake

**Trigger:** Payment of $197 clears (Stripe or Gumroad notification received).

**Immediate action (within 2 hours of payment):**

Send intake form to client. Do not start any analysis before intake is complete.

**Intake message template:**

> Payment received — thank you.
>
> Before I start, I need your answers to 5 questions. Async format means I work from what you give me — the more specific you are, the more actionable the audit will be.
>
> Please reply with:
>
> 1. **What system or decision are you asking me to audit?** (e.g., "my trading entry/exit rules", "my daily time allocation", "how I'm structuring my productized service")
>
> 2. **What outcome are you trying to achieve?** (e.g., "be profitable by Q3", "work 6hr/day max", "close 3 consulting clients/month")
>
> 3. **What's the specific friction or failure you're experiencing right now?** (e.g., "I keep overriding my own rules", "I'm spending 4 hours/day on email", "I close discovery calls but clients don't pay")
>
> 4. **What have you already tried?** List anything you've attempted to fix the problem — even if it partially worked.
>
> 5. **What does "this audit was worth $197" look like to you?** (What would change after reading it?)
>
> No minimum length required. Short and specific beats long and vague.

**Wait for intake.** Do not start analysis on assumptions.

**Intake timeout:** If no response within 48 hours, send one follow-up:

> Just checking — did my intake questions reach you? I want to make sure I'm working on the right problem before I start.

If no response in 72 hours total: flag in `results/revenue_log.jsonl` as `INTAKE_STALLED`. Do not refund until client explicitly requests it. Hold the engagement open for 7 days.

**Output of G0:** 5 intake answers received. No analysis started until all 5 are answered.

---

### G1 — Analysis Phase

**Input:** The 5 intake answers from G0.

**Time budget:** 60–90 minutes of analysis. Not more. Scope creep here = unprofitable audit.

**Analysis framework — run in this order:**

**Step 1: Map the client's system to the SOP archive**

For each of Edward's 10 SOP domains, ask: does the client's problem touch this domain?

| Domain | SOP Range | Signal Keywords |
|--------|-----------|----------------|
| Trading systems | SOP #01–#30 | entry/exit rules, kill conditions, position sizing, paper-live |
| FIRE / financial | SOP #31–#40 | savings rate, portfolio logic, withdrawal strategy |
| Time allocation | SOP #41–#50 | deep work, calendar, daily ritual, time blocking |
| Decision bandwidth | SOP #51–#60 | decision fatigue, meta-strategy, bias toward inaction |
| Relationships | SOP #61–#65 | network, DM conversion, trust signals |
| Content / distribution | SOP #66–#75 | posting ritual, thread structure, conversion |
| Goal architecture | SOP #76–#82 | milestone tracking, branch logic, priority ranking |
| Productivity | SOP #83–#90 | daily ritual, weekly review, cold start |
| Digital twin / AI | SOP #91–#97 | recursive engine, DNA calibration, consistency testing |
| Revenue | SOP #97–#104 | consulting protocol, product creation, rate card |

Select 5–8 SOPs that are directly applicable to the client's stated problem.

**Step 2: Apply the 5 decision principles**

Run the client's situation through Edward's decision kernel:

1. **Derivative over level** — Is the client's problem that their current state is bad, or that the trajectory is wrong? Which is it?
2. **Information asymmetry** — Does the client have an edge in their domain, or are they competing in a symmetric-information market?
3. **Meta-strategy vs. strategy** — Is the client solving the wrong problem at the wrong level? (e.g., optimizing execution when strategy is broken)
4. **Population exploit** — Is the client doing what everyone else does? If so, what's the contrarian move?
5. **Bias toward inaction** — Are they acting without edge, or failing to act when edge is clear?

For each principle: one sentence on how it applies to the client's specific situation. If a principle is not applicable, skip it — do not force it.

**Step 3: Identify gaps**

Minimum 3 gaps required. Maximum 6. More than 6 = scope bloat.

Gap format:
```
Gap [N]: [Gap name]
Observed: [What the client is currently doing or not doing]
Expected: [What a well-functioning system would have at this point]
Impact: [What breaks because this gap exists]
Applicable SOP: [SOP #XX — name]
```

**Step 4: Draft the recommendation priority**

Of the identified gaps, which is the highest-leverage fix?

Apply: "If the client could only fix ONE thing in the next 14 days, what would create the most change in trajectory?"

That is the primary recommendation. The others are secondary.

---

### G2 — Deliverable Format

**Structure of the written audit document:**

The audit is a plain text or markdown document. No slides. No charts. No embellishment.
Target length: 800–1200 words. Not more. Longer = diluted. Shorter = underpowered.

---

**[CLIENT NAME] Async Audit — [DATE]**

**Situation Summary** (2–3 sentences)
Restate what the client said in their own words. This confirms you understood the problem before diagnosing it.

**Decision Kernel Analysis** (3–5 sentences)
Apply the relevant principles from Step 2. Write this as a direct diagnosis, not as a framework explanation. The client does not need to know what the framework is called — they need to know what it reveals about their situation.

**Gap Analysis**

For each gap (3–6 total), use the format from Step 3.

> Gap 1: [Name]
> Observed: [What they're doing]
> Expected: [What should exist]
> Impact: [What's broken because of this]
> Applicable SOP: [SOP #XX — name]

**Primary Recommendation** (1 short paragraph)
The single highest-leverage fix. Be direct. Do not hedge. Do not offer 3 equal options — pick the one.

**Secondary Recommendations** (bulleted list)
The remaining gaps, each with a 1-sentence action recommendation.

**Applicable SOPs** (list)
5–8 SOPs from the archive that are most directly relevant. Format:
- SOP #XX — [name] — [1-line relevance note]

**Caveats** (optional, max 2 sentences)
Only include if there is a genuine assumption risk in the analysis — something that would materially change the diagnosis if the client's situation turns out to be different than stated. Do not include caveats to hedge. Include them only to surface real blind spots.

---

**Formatting rules:**
- No markdown headers with `#` symbols in the delivered document (plain text delivery is default)
- No em dashes in the final document
- No bullet lists longer than 6 items (split into separate sections if needed)
- Avoid "I think" and "you should consider" — use "The gap is" and "The fix is"
- Write as if the client has read nothing about frameworks — explain by example, not by concept name

---

### G3 — Delivery and Follow-Up

**Delivery method:** Email or the same channel used for intake (DM, etc.)

**Delivery message template:**

> Audit complete. Full document below.
>
> [PASTE AUDIT DOCUMENT]
>
> Three things to note:
>
> 1. The primary recommendation is the one thing worth acting on in the next 14 days. The secondary recommendations are real but lower urgency.
>
> 2. If any part of the diagnosis feels off — meaning I interpreted your situation incorrectly — reply and tell me. I will re-examine that section.
>
> 3. If you want to work through the primary recommendation on a call (60 min, $97, see SOP #88 format), I can schedule one within 7 days of delivery.
>
> Delivered within 48h of intake receipt, as promised.

**Follow-up (Day 7 after delivery):**

If no reply received by Day 7, send one follow-up:

> Checking in — did the audit land as useful? No action required on your end. Curious whether the primary recommendation resonated or whether I missed something.

Purpose: testimonial trigger and engagement recovery. If they respond, proceed to G4.

---

### G4 — Revenue Tracking + Testimonial Collection

**Revenue log entry (write immediately after delivery):**

```json
{"date": "...", "type": "consulting", "format": "async_audit_197", "revenue_usd": 197, "client_domain": "...", "delivery_time_hours": "...", "sop_104_gate": "G4_DELIVERED"}
```

Log to `results/revenue_log.jsonl`.

**Gap check (run within 24 hours of delivery):**

```
Did the client's problem reveal a gap in the existing SOP archive?
  YES → Draft SOP #105+ based on the engagement insight
  NO  → Update relevant existing SOP with the new edge case observed

Did the audit surface a repeatable pattern?
  YES → Log to memory/ as "pattern candidate" — after ≥2 clients with same problem, create standalone product
  NO  → Log to memory/ for future recognition
```

**Testimonial collection (trigger: client replies positively to Day 7 follow-up OR to delivery message):**

When a client signals the audit was useful (positive reply, specific thank you, "this helped me see X"), send:

> Glad it was useful. One ask: if you had 2 sentences about what the audit clarified for you, I'd use that as a reference for future clients. No obligation — only if it felt worth it to you.

Format of testimonial request: always 2 sentences max, always framed as "what it clarified" (not "how great it was"). Clarity testimonials are more credible than praise testimonials.

Store received testimonials in `memory/testimonials.md` (create if not exists).

---

### G5 — Referral Trigger

**When to ask for a referral:**

Ask only after both conditions are met:
- Testimonial received (G4 complete)
- At least 14 days have passed since delivery

Do not ask for a referral in the same message as the testimonial ask.

**Referral trigger message:**

> One more thing — do you know anyone who's building a systematic approach to [client's domain — e.g., trading, time allocation, revenue] and running into the same kind of friction you described? I'm taking on 2–3 audits per month. Happy to offer them the same format. No commission structure — just a straight referral if you think it's a fit.

**Referral qualification criteria (same as SOP #97 G0):**
- Problem in Edward's SOP domains
- Recent activity signal (posted or active in last 7 days)
- Warm introduction available (the existing client knows them)

**Log referred prospects in G0 of the next SOP #97 cycle.**

---

## Delivery Timing Commitments

| Phase | Time Budget | Commitment to Client |
|-------|-------------|---------------------|
| Intake acknowledgment | ≤ 2 hours after payment | "Starting now, intake questions sent" |
| Analysis start | ≤ 2 hours after intake received | — |
| Audit delivered | ≤ 48 hours after intake received | Stated in delivery message |
| Follow-up check | Day 7 after delivery | — |
| Testimonial ask | Within 24h of positive signal | — |
| Referral ask | Day 14+ after delivery, only if testimonial received | — |

**No exceptions on the 48-hour delivery commitment.** If intake arrives at an inconvenient time, the 48-hour clock still runs. Deliver on time or notify proactively with a revised ETA before the window closes.

---

## Self-Test

**Scenario:** Client pays $197 at 09:00 on a Monday. Intake form sent by 11:00. Client replies at 15:00 with all 5 answers. Their problem: "I have a systematic trading strategy but I keep overriding my exit rules when trades go against me."

**Expected execution:**
- G0: Payment received → intake sent within 2 hours → intake answers received at 15:00 → G0 complete
- G1: Map to trading domain (SOP #01–#30). Apply derivative principle (problem is behavioral override, not rule design). Identify gaps: no documented kill condition for override behavior, no cooling-off period rule, no post-override log protocol.
- G2: 900-word audit document. Situation summary restates the override problem. Decision kernel: bias toward inaction applies — overriding exits is acting without edge. Gap 1: no rule for what to do when the urge to override appears. Primary recommendation: add a 15-minute cooling-off rule before any manual override, with a required log entry.
- G3: Delivered within 48 hours of intake. Follow-up on Day 7.
- G4: Revenue logged. Gap check: "override behavior management" not covered in current trading SOPs → flag for SOP #105.
- G5: Testimonial received → referral ask on Day 14.

**Anti-patterns:**
- Starting analysis before all 5 intake answers received (working on assumptions)
- Delivering more than 6 gaps (scope bloat, dilutes primary recommendation)
- Asking for referral in the same message as testimonial request (too much ask, wrong sequence)
- Writing the audit longer than 1200 words (longer = less actionable)
- Using hedged language ("you might want to consider") instead of direct recommendations
- Delivering late without proactive notification

---

## Connections

| SOP | Role |
|-----|------|
| SOP #86 | Rate card — price escalation triggers |
| SOP #88 | Discovery call protocol — used for $97 advisory call (the upsell from G3) |
| SOP #97 | Consulting revenue protocol — defines the $197 async audit product and outreach |
| SOP #82 | Revenue milestone tracker — audit revenue feeds M1, M2, M3 |
| SOP #70 | DM conversion logic — warm reply handling before payment |

---

*SOP #104 closes the gap between revenue protocol and delivery. The product existed. The delivery protocol did not. Now it does.*
