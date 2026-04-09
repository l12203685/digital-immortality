# SOP #86 — Consulting Rate Card

> Domain: Revenue / Client Acquisition
> Created: 2026-04-09T10:30Z
> Status: OPERATIONAL
> Trigger: G0 (≥3 DMs: "do you consult?" / "can I hire you?" / rate inquiry)

---

## Why This Exists

SOP #85 validated the first product (Gumroad bundle, $19). SOP #70 handles DM conversion.
But neither covers the scenario where someone skips the product and asks to hire Edward directly.

**Gap identified:**
When consulting DMs arrive without a rate card, the default response is either fumbled (no price = no deal)
or over-committed (takes a bad client out of social pressure). Both failure modes cost time with zero EV.

**Decision principles in play:**
- MD-148: Infrastructure must have ROI threshold. A rate card is a filter, not just a price list.
- MD-102: Time is the scarcest resource in the pre-revenue phase. Consulting must pay enough to justify diverting from product velocity.
- MD-103: Consulting is a market signal. ≥3 DMs = demand exists. Ignore it = information waste.
- Bias toward inaction (Kernel Rule 5): no edge = no action. But ≥3 DMs = edge exists. Now act.

---

## Gate Sequence: G0 → G5

### G0 — Trigger Check

Fire when ALL of:
- T1: ≥3 DMs received in any 30-day window asking "do you consult?", "can I hire you?", or rate inquiry
- T2: Current phase is pre-revenue OR product revenue < $500/mo (consulting fills gap, not cannibalizes)
- T3: At least 1 DM sender has visible credibility signal (funded startup, real company, verified profile, or ≥500 followers with content activity)

If T1 not met: **STOP. Do not create rate card preemptively. Wait for demand.**

If T1 met but T2 not met (product revenue ≥ $500/mo and scaling): **Pause consulting. Protect product velocity. See G5 kill condition.**

If T3 not met (3 DMs but all low-signal senders): **Do not skip G0. Filter is the point.**

> Anti-pattern: Publishing a rate card on your website before anyone asks.
> Same failure mode as building product before demand validated. Wait for pull.

---

### G1 — Rate Structure Decision

**Phase: Pre-revenue ($0–$500/mo product revenue)**

Consulting is a YES. Rates are a discovery instrument — price anchors what you learn about demand.

| Format | Rate | When to Use |
|--------|------|-------------|
| Discovery call (30 min) | Free (one-time) | Qualification only. No advice on free call. |
| Hourly advisory | $200/hr | Single session, tactical question, no ongoing |
| Project-based | $1,500–$5,000 | Defined scope + deliverable (e.g. trading system audit, strategy review) |
| Monthly retainer | $2,000/mo | Ongoing access, 4×30-min calls/month + async Slack/DM |

**Pricing logic:**
- Anchor at $200/hr. Do NOT start below this. Below $200 signals commodity, not edge.
- Retainer = $2,000/mo because 4 calls × $200 = $800 in calls + async = $1,200 premium for availability. Fair.
- Project floor = $1,500. Below $1,500 the overhead (scoping, proposal, payment) costs more than the work.
- Raise prices after ≥2 paid engagements with zero pushback. Pushback = right price. Immediate yes = underpriced.

**Do NOT offer equity-only or revenue share unless:**
- Company is funded (≥Seed)
- Your equity stake is ≥2%
- Vesting cliff ≤12 months

---

### G2 — DM Response Template

When T1 fires (≥3rd DM asking about consulting), use this template. Adapt per sender.

---

**Template A — First response (warm, no price yet):**

> Hey — yeah I do take on a small number of advisory clients when the fit is right.
>
> Quick question before I share rates: what's the specific problem you're trying to solve? (Trading system? Business decision? Something else?)
>
> I want to make sure I'm the right person before we talk numbers.

---

**Template B — After they reply with problem (price reveal):**

> Got it. That's in my wheelhouse.
>
> My current structure:
> - 30-min discovery call: free (we figure out if there's a real fit)
> - Hourly advisory: $200/hr
> - Project-based (scoped deliverable): $1,500–$5,000 depending on scope
> - Monthly retainer (ongoing access): $2,000/mo
>
> If you want to move forward, let's do the free discovery call first.
> [Link to calendar / "I'll send a Calendly link"]

---

**Template C — Decline (wrong fit):**

> Thanks for reaching out. After thinking about it, I don't think I'm the right fit for this one —
> [too early stage / outside my edge / timing is off].
>
> If you haven't already, the SOP bundle at [Gumroad link] covers a lot of the frameworks I'd walk you through in a session. Might be the faster path.

---

**Rules for all templates:**
- Never apologize for your rates
- Never volunteer a discount before they ask
- If they ask for a discount: offer a scoped-down version at the lower price, not a discount on the same scope
- Response time: reply within 24h. Beyond 48h = signal you're not serious about consulting

---

### G3 — Qualification Filter

**Take the client if ALL of:**
- [ ] Has a specific, bounded problem (not "help me think about my whole life")
- [ ] Has budget signal (doesn't flinch at rate reveal, or already mentioned paying others)
- [ ] Domain is in Edward's edge zone: trading systems, decision frameworks, product strategy, systematic thinking
- [ ] Engagement is ≤3 months (no open-ended dependency)
- [ ] They did work before the call (read the SOPs, watched threads — not starting from zero)

**Decline immediately if ANY of:**
- [ ] They want "partner" framing without equity conversation (unpaid leverage attempt)
- [ ] Problem is purely emotional / life coaching (not edge, not leverage)
- [ ] They've emailed 5+ times before first call (high-maintenance signal)
- [ ] They want guaranteed outcomes (trading returns, revenue targets, etc.)
- [ ] "I can't afford your rates but..." (T3 failed — low-signal sender)
- [ ] They're a direct competitor to a current client (conflict of interest)

**Red flag phrases:**
- "Can we do a quick call to see if it's worth paying?"  → Discovery call IS the answer. If they want free advice before paying for discovery, they won't pay for the session.
- "I just want your opinion on..." → Opinion is $200/hr. It is not free because it sounds casual.
- "Can we work something out?" → Equity or scope reduction only. Not rate reduction.

---

### G4 — Intake Process

**Step 1: Discovery call (free, 30 min)**

Agenda (non-negotiable — don't let it drift):
1. (5 min) What is the specific problem?
2. (10 min) What have they already tried?
3. (10 min) What does success look like in 90 days?
4. (5 min) Decision: fit or no-fit. Say it on the call. Do not ghost.

Decision criteria: Can I solve this AND does it fit my edge? If both yes → proceed.

**Step 2: Proposal (within 48h of discovery call)**

Send a written proposal with:
- Problem statement (their words, not yours)
- Scope: what is included, what is NOT included
- Format: hourly / project / retainer
- Price (specific number, not range)
- Payment terms: 50% upfront, 50% on delivery (project) OR monthly prepay (retainer)
- Expiry: proposal valid for 7 days

Template file: `templates/consulting_proposal_template.md` (create on first use, reuse after)

**Step 3: Payment**

- Method: Stripe invoice (use Gumroad payment link or Stripe directly)
- No work starts before first payment clears
- No exceptions. Non-payment risk = project scope creep risk. Same root cause.

**Step 4: Engagement**

- Start with written summary of agreed scope (1 page max)
- Each call: send 3-bullet recap within 24h (what was decided, what Edward will do, what client will do)
- No scope creep: new requests = new engagement or scope change order (in writing)

**Step 5: Close**

- Retainer: 30-day notice to cancel (both sides)
- Project: final deliverable + "did this solve the problem?" check
- Referral ask: if they're happy, ask within 48h of close ("Do you know anyone else who'd benefit from this?")
- Log to `results/revenue_log.jsonl`: `{"date": "...", "type": "consulting", "format": "hourly|project|retainer", "revenue_usd": X, "client_domain": "trading|product|other"}`

---

### G5 — Kill Condition

**Pause consulting when ANY of:**
- Product revenue ≥ $500/mo AND growing (consulting hours now cannibalize product compounding)
- Consulting takes >8 hrs/week (above this threshold, product velocity drops below recovery rate)
- Client is extracting edge without improving Edward's own system (zero-sum time trade)
- 2+ consecutive clients require scope creep management (pattern = wrong client filter, not one-off)

**Kill sequence:**
1. Do not take new clients
2. Honor existing commitments to completion
3. Raise rates 2× on next inquiry (price as filter, not income target)
4. Redirect DMs to product: "I'm paused on consulting for now — the SOPs cover most of what people hire me for: [Gumroad link]"
5. Log kill decision to `staging/session_state.md`

**Resume condition:** Product revenue stalls for ≥30 days AND consulting pipeline has ≥2 qualified inbound DMs.

---

## Self-Test

**Scenario:** You receive 4 DMs in 2 weeks. DM #1: "can I hire you to review my trading system?" DM #2: "what are your rates?" DM #3: "I run a $500k fund, looking for a systematic edge advisor." DM #4: "can we hop on a call for free, then I'll decide if I want to pay?" Product revenue is $0.

**Expected:**
- G0 fires: T1 (4 DMs ≥ 3) ✓, T2 (pre-revenue) ✓, T3 (DM #3 has credibility signal: $500k fund) ✓
- DM #1 + #2: Template A (ask for problem statement first)
- DM #3: Template A → likely Template B fast-track (high-signal sender)
- DM #4: Template A, but if they repeat "free first then decide" → Template C decline (T3 filter: extractive pattern)
- Rate: $200/hr or $2,000/mo retainer revealed in Template B
- If DM #3 says yes: discovery call → proposal within 48h → 50% upfront before call #1

**Anti-patterns:**
- Offering a free "trial session" to close DM #4 (breaks the filter; sets wrong precedent)
- Publishing rates publicly before ≥3 DMs (supply before demand = zero price discovery)
- Taking a retainer without written scope (scope creep probability = 100%)
- Discounting rates because DM #2 said "that's expensive" (pushback is signal you're at the right price)

---

## Connections

| SOP | Role |
|-----|------|
| SOP #70 | DM conversion → consulting is a conversion path alongside product |
| SOP #82 | Revenue milestone tracker → consulting contributes to M3 |
| SOP #83 | Daily posting ritual → consulting credibility builds from thread authority |
| SOP #85 | Gumroad product → fallback CTA when declining consulting DMs |
