# SOP #105 — Testimonial Collection Protocol

> Domain: Revenue / Consulting / Social Proof
> Created: 2026-04-09T UTC (cycle 271)
> Status: OPERATIONAL
> Decision label: TESTIMONIAL_COLLECT_ON_POSITIVE_SIGNAL
> Posting queue: Oct 28

---

## Why This Exists

SOP #104 closes the delivery loop: intake → analysis → audit → follow-up.

**The gap this SOP closes:**
SOP #104 G4 includes a one-line testimonial ask: "2 sentences about what it clarified." It does not specify:
- The exact timing window before the ask
- How to frame the request to increase response rate
- What format the testimonial should take (tweet-quote vs. LinkedIn)
- Where testimonials are stored and how they are deployed
- Which downstream products and posts are unlocked by having testimonials

Without this SOP, testimonial collection is reactive and ad hoc. Consulting revenue hits a glass ceiling at warm network because no social proof exists for cold-to-warm conversion.

**The chain this SOP continues:**

```
SOP #97: Outreach → warm reply → offer made
SOP #104: Payment → intake → audit → delivery → positive signal
→ [SOP #105 starts here: testimonial collection]
→ SOP #70: Testimonial as G2 trigger in DM conversion
```

---

## Gate Sequence: G0 → G5

### G0 — Trigger

**Conditions (both required):**
1. SOP #104 G5 complete — audit delivered, Day 7 follow-up sent
2. Client response received — any reply that is positive or substantive

**Positive signal examples:**
- Explicit thanks ("this was really useful")
- Specific mention of what changed ("I realized I was solving the wrong problem")
- Question about the next step ("how do I work on gap 2?")
- Unprompted share or repost of the audit framing

**Not a trigger:**
- No reply (silence is not a positive signal)
- A question during delivery with no affirmation ("what does X mean?")
- A complaint or correction request

**Output of G0:** Positive signal confirmed. Clock starts.

---

### G1 — Wait Window

**Required:** 48–72 hours after positive signal before sending the testimonial ask.

Do not ask for a testimonial in the same message as the delivery. Do not ask in the Day 7 follow-up unless the client volunteers unsolicited praise in that follow-up.

**Rationale:** The value needs time to land. Asking immediately after delivery signals that the ask was the goal, not the value. Waiting 48–72h gives the client time to act on the recommendation and feel the difference.

**Exception:** If the client sends an unsolicited strong endorsement ("this was the best $197 I've spent") at any point, the wait window collapses. Respond within 24 hours.

**Output of G1:** Wait window elapsed. Proceed to G2.

---

### G2 — Testimonial Request

**Single DM only.** One ask. No follow-up on the testimonial request itself.

**Request template:**

> Glad the audit was useful. One ask — if you had 2 sentences describing what it clarified for you, I'd use that as a reference for future clients.
>
> Two formats work:
> — Short (tweet-length, 280 chars or under): I use these in threads and posts
> — Long (LinkedIn-style, 3–5 sentences): I use these on product pages
>
> Either one, or both if you're inclined. No obligation — only if it felt worth it.

**Framing rules:**
- Ask for "what it clarified" — not "how great it was"
- Clarity testimonials are more credible than praise testimonials
- Offer the two formats explicitly — clients default to long when not given a short option, and long testimonials are harder to deploy on social
- One ask only. If no response in 7 days, log as `TESTIMONIAL_NO_RESPONSE` and move on

**Output of G2:** Ask sent. Wait for response.

---

### G3 — Format Guidance

If the client replies but their testimonial needs shaping, use this guidance (send only if their draft is unclear or unusable):

**Tweet-quote format:**
- 280 characters or under
- First person, present tense ("I realized..." / "This helped me see...")
- Specific to their problem domain, not generic praise
- Ideally includes a concrete outcome or shift ("I stopped overriding my exits")

Example of weak tweet-quote (do not accept):
> "Edward's audit was really insightful and I learned a lot. Highly recommend."

Example of strong tweet-quote:
> "Sent Edward my trading system. Two days later I had a diagnosis I couldn't see myself — my exits were fine, my override behavior wasn't. One rule change fixed three months of friction."

**LinkedIn long-form format:**
- 3–5 sentences
- Describes the problem before the audit, the insight during, and the change after
- No need to name the price — the specificity does the credibility work
- Optional: mention a specific SOP domain (trading, time allocation, etc.)

Example of strong LinkedIn testimonial:
> "I hired Edward for an async audit of my trading system. I expected him to find problems with my entry rules. Instead, he diagnosed that my rules were fine — I was overriding them after entries, which is a different problem entirely. He gave me a single behavioral rule to test. Two weeks in, my execution improved more than any system tweak had in six months. The format is efficient. The diagnosis was accurate. Worth it."

**Output of G3:** Testimonial received in usable format.

---

### G4 — Usage: What Testimonials Unlock

**Tweet-quote testimonials unlock:**
- Social proof layer in content threads (embed in SOP thread posts, not as separate posts)
- G2 trigger in SOP #70 DM conversion: when a warm prospect sees a thread, a tweet-quote from a past client serves as the credibility signal that moves them from "interested" to "I want this"
- Rotate into pinned tweet or bio section when 3+ tweet-quotes are available

**LinkedIn long-form testimonials unlock:**
- Product page for the $197 async audit (add to Gumroad or standalone page)
- Outreach cold DMs: one testimonial embedded in the outreach sequence (SOP #97) when prospect pool expands beyond warm network
- Workbook social proof layer (SOP #88 and SOP #97 product pages)

**Threshold rules:**
- 1 testimonial: usable in content, not yet sufficient for cold outreach
- 2 testimonials: sufficient for product page
- 3+ testimonials: unlock cold outreach sequence expansion (SOP #97 cold tier)
- 5+ testimonials: sufficient to raise the $197 price to $247 (SOP #86 rate escalation trigger)

**Output of G4:** Testimonial categorized and deployment path noted.

---

### G5 — Storage

**Log all testimonials to `docs/testimonials_log.jsonl`.**

Schema:

```json
{
  "date": "YYYY-MM-DDTHH:MM:SSZ",
  "client_id": "anonymous_handle_or_initials",
  "sop_engagement": "104",
  "format": "tweet_quote | linkedin | both",
  "domain": "trading | time | revenue | productivity | other",
  "text_tweet": "...",
  "text_linkedin": "...",
  "deployed_in": [],
  "status": "received | formatted | deployed | archived"
}
```

**Field notes:**
- `client_id`: Use initials or anonymous handle — never full name without consent
- `deployed_in`: Array of posts, threads, or product pages where this testimonial has been used. Update on each deployment.
- `status`: Progress field — a received testimonial that has not been deployed is a wasted asset

**After logging:** Update `memory/testimonials.md` with a one-line entry:

```
[DATE] — [DOMAIN] — [FORMAT] — [ONE-LINE SUMMARY OF WHAT THEY SAID]
```

**Output of G5:** Testimonial logged and indexed.

---

## Anti-Patterns

**Asking too early (before G1 wait window):**
Asking for a testimonial in the delivery message collapses the value signal. The client has not yet acted on the recommendation. Their testimonial will be generic ("the audit was detailed") rather than outcome-specific ("I stopped doing X").

**Asking for both formats in a single mandatory ask:**
The G2 template offers both formats as optional. Do not require both. One strong tweet-quote is more deployable than two mediocre long testimonials.

**Generic ask ("what did you think?"):**
This produces generic answers ("it was great"). The ask must specify the format: "2 sentences about what it clarified." The framing determines the output quality.

**Following up on the testimonial ask:**
One ask. No follow-up. Following up on a testimonial ask signals desperation and damages the relationship. If they do not respond, the engagement was still complete — the revenue was logged, the client was served.

**Storing testimonials in memory/ only:**
`memory/testimonials.md` is a human-readable summary file. The canonical record is `docs/testimonials_log.jsonl`. Both must be updated.

**Deploying testimonials before logging:**
Always log first, deploy second. The `deployed_in` field is the audit trail.

---

## Self-Test

**Scenario:** Audit delivered Day 1. Day 7 follow-up sent. Client replies Day 8: "This was really useful — I didn't realize I was treating my time allocation like a trading system without any exit rules. Working on it now."

**Expected execution:**
- G0: Positive signal confirmed (specific, outcome-oriented reply). Clock starts.
- G1: Wait 48–72 hours. Do not ask immediately.
- G2: Day 10 or 11 — send single testimonial request. Offer tweet-quote and LinkedIn formats.
- G3: Client sends: "Edward audited how I was allocating deep work time. He identified that I had no rules for when to stop a session — I'd keep working past the point of usefulness. One rule change fixed my afternoon energy. The audit paid for itself the first week." → Strong LinkedIn format. Ask if they can also do a tweet-length version.
- G4: Tweet-quote extracted. Deployed in next content thread on time allocation. Logged as G2 trigger candidate for SOP #70.
- G5: Logged to `docs/testimonials_log.jsonl` with `status: received`. Updated `memory/testimonials.md`.

---

## Connections

| SOP | Role |
|-----|------|
| SOP #70 | DM conversion logic — tweet-quote testimonial is the G2 credibility trigger |
| SOP #86 | Rate card — 5+ testimonials trigger price escalation from $197 to $247 |
| SOP #97 | Consulting revenue protocol — 3+ testimonials unlock cold outreach tier |
| SOP #104 | Async audit delivery — G4 positive signal is the G0 trigger for this SOP |

---

*SOP #105 closes the loop between delivery and social proof. Without testimonials, consulting revenue is bounded by warm network. With them, the pipeline compounds.*
