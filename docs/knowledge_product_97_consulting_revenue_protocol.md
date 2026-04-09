# SOP #97 — Consulting Revenue Protocol (Branch 1.4 Activation)

> Domain: Revenue / Consulting / Network Outreach
> Created: 2026-04-09T UTC (cycle 263)
> Status: OPERATIONAL — START IMMEDIATELY
> Decision label: CONSULTING_OUTREACH_START_WITH_WARM_NETWORK
> Posting queue: Oct 17

---

## Why This Exists

Branch 1.4 "其他收入路徑" has been listed as "待發現" (TBD) for 263 cycles.

**Diagnosis:**
- Branch 1.1 (trading mainnet): BLOCKED — API keys require human action
- Branch 1.3 (content/Gumroad): BLOCKED — SOP #01 post requires human action
- Branch 1.4: NOT BLOCKED — zero human gates between current state and first dollar

**Asset inventory that makes this viable today:**
- 96 SOPs covering 10 life domains (trading systems, FIRE, time allocation, decision bandwidth, relationships, content, goal architecture, productivity, digital twin, revenue)
- 330 micro-decision MDs (depth signal: rare in the market)
- SOP #86 (rate card): operational, rates defined
- SOP #88 (discovery call protocol): operational, intake script ready
- SOP #70 (DM conversion): operational
- Zero new content creation required — the product is the existing SOP archive

**The gap this SOP closes:**
SOP #86 waits for ≥3 inbound DMs. That is a passive demand model.
SOP #97 runs in parallel — active outreach to warm network using existing SOPs as proof-of-work.
Inbound ≠ only path. Outbound to warm network with a concrete problem-framing offer = Branch 1.4 activation.

**Revenue threshold for Branch 1.4 to be "alive":**
1 advisory call/month ($97) > API cost (~$20/month) = self-sustaining.
This is the minimum viable revenue gate, not the ceiling.

---

## Gate Sequence: G0 → G5

### G0 — Target Identification

**Who needs these SOPs:**

Tier 1 (highest fit):
- Startup founders (0→1 stage): decision overload, no operating system, burning time on low-leverage choices
- Knowledge workers (operators, analysts, indie hackers): want to systematize how they work but lack the framework vocabulary
- Quant traders (early-stage, systematic): building a trading system but no kill conditions, no paper-live protocol, no portfolio logic

Tier 2 (adjacent fit):
- FIRE-track individuals (aggressive savings rate, need portfolio logic + lifestyle optimization)
- Content creators with growing distribution (need a posting ritual + DM conversion system)
- People building digital twins / AI agents (want to see a working implementation)

**Identify 3 targets from existing network — search criteria:**

LinkedIn search:
```
"founder" OR "quant" OR "systematic trader" + 2nd-degree connection
Filter: posted in last 30 days (active signal)
Filter: ≥500 connections (platform traction)
```

Twitter/X search:
```
From: [accounts you follow or follow you]
Keywords: "decision fatigue" OR "trading system" OR "FIRE" OR "systematize" OR "knowledge management"
Recency: last 14 days
```

Qualifying signal (pick targets with ≥2 of):
- [ ] Has publicly described a problem in your SOP domains
- [ ] Has engaged with your content before (liked, replied, retweeted)
- [ ] Has buying behavior signal (paid for courses, tools, or coaching — visible from bio or tweets)
- [ ] Is active (posted in last 7 days)

**Output of G0:** A list of exactly 3 names with their problem domain tagged.
Do not proceed to G1 without a list. A list of 0 = stay in G0.

---

### G1 — Direct Outreach (Warm Problem Framing)

**Principle:** No cold pitch. Problem framing first, offer second.
The SOP archive is proof-of-work. Use it as signal, not as the pitch.

**DM format: Problem → Solution → Proof**

---

**Template A — Quant / Trading domain:**

> Hey [Name] — saw your post about [specific thing they said about trading/systems].
>
> I've been building a decision OS for systematic trading over the last 263 cycles — ended up writing 96 SOPs covering everything from kill conditions to paper-live activation to portfolio logic.
>
> Quick question: is [the specific problem they described] still unsolved, or did you find something that worked?

---

**Template B — Founder / Decision bandwidth domain:**

> Hey [Name] — noticed you mentioned [specific decision challenge or bottleneck they described].
>
> I've been running a personal operating system with 96 documented SOPs — built specifically for high-decision-load environments (trading, FIRE, time allocation, goal architecture).
>
> Has the [specific problem] gotten worse or better since you wrote that?

---

**Template C — Knowledge worker / Systematize domain:**

> Hey [Name] — your post about [systematizing work / knowledge management / decision frameworks] resonated.
>
> I've documented 330 micro-decisions across 10 domains as part of a digital twin project. Some of it maps directly to what you described.
>
> What's the piece that's still most unsolved for you right now?

---

**Rules for all outreach templates:**
- Always reference a specific post or statement they made — never generic
- Ask a question, do not pitch an offer in the first message
- No links in first message (spam filter + low-trust signal)
- Response time target: send within 24h of seeing their qualifying post
- If no response in 5 days: one follow-up (different angle, not a repeat), then close

---

### G2 — Engagement Structure

**Two formats. No others. No custom scoping until ≥2 paid engagements.**

| Format | Price | What it is | What the client gets |
|--------|-------|------------|----------------------|
| Async SOP Audit | $197 | Client sends their system/process/decision. Edward maps it against relevant SOPs, returns written diagnostic with ≥3 specific gaps and recommended SOP frameworks. | Written audit (≤2 pages) + pointer to 5–8 directly applicable SOPs from the 96-SOP archive. Delivered async within 48h. |
| 60-min Advisory Call | $97 | Live call. Client brings a specific decision or system problem. Edward runs the discovery call protocol (SOP #88) + shares relevant frameworks. | 60 min live + 3-bullet recap within 24h + pointer to relevant SOPs. |

**Why these prices:**
- $97 advisory call = below SOP #86 rate card ($200/hr) deliberately
  - Reason: first sale target. Psychological friction is low. $97 on a warm DM has near-zero barrier.
  - After ≥2 sales with no pushback: raise to $150/hr (still below SOP #86 floor = still market discovery)
  - After SOP #86 triggers (≥3 inbound DMs): switch to SOP #86 rate card ($200/hr)
- $197 async = premium for async format (saves client scheduling friction) + lower Edward time cost (1hr work vs 1hr live)

**No new content creation required:**
The 96 SOPs are the product. The 330 micro-decisions are the depth signal.
The advisory call delivers edge from the existing archive. Zero new writing needed until G4.

**Payment flow:**
- Method: Stripe link or Gumroad payment link (infrastructure already exists from SOP #85)
- No work before payment clears
- No exceptions (SOP #86 rule, unchanged)

---

### G3 — Revenue Conversion

**First sale target: 1 × $97 advisory call.**

Why $97 and not $197:
- Lower friction = higher close probability = faster first-dollar validation
- The goal is Branch 1.4 activation, not revenue maximization (G5 handles scale)
- $97 > $0 = the branch is alive

**Conversion logic — apply SOP #70 gate logic to outreach responses:**

```
Received warm reply to G1 DM?
  → Ask clarifying question about their specific problem (do not offer product yet)
  → If they describe a bounded problem in your SOP domain:
      → "I have something that might be directly applicable — would a 60-min call where we work through it be useful?"
      → If YES: "It's $97. If it's not useful, I'll refund it. [payment link]"
      → If they ask what you cover: reference 2–3 specific SOPs by name that map to their problem
      → If they ghost: one follow-up in 3 days, then close
```

**Revenue threshold gate:**
- BRANCH 1.4 ALIVE: ≥1 paid session/month AND monthly_revenue > monthly_API_cost (~$20)
- BRANCH 1.4 SCALING: ≥$97/month consistent for ≥2 months → raise price, add $197 async format to active promotion
- BRANCH 1.4 MATURE: consulting + trading + content > total operating costs → G5 met

**First-sale checkpoint:**
Log to `results/revenue_log.jsonl`:
```json
{"date": "...", "type": "consulting", "format": "advisory_call_60min", "revenue_usd": 97, "client_domain": "...", "sop_97_gate": "G3_FIRST_SALE"}
```

---

### G4 — Productize the Pattern

**Rule:** Every paid engagement that reveals a new domain gap → new SOP.

After each advisory call or async audit, run this check:

```
Did the client's problem reveal a gap in the existing 96 SOPs?
  YES → Draft SOP #98+ based on the engagement insight
  NO  → Update relevant existing SOP with new edge case

Did the engagement surface a repeatable pattern (≥2 clients with same problem)?
  YES → That pattern becomes a new knowledge product (Gumroad or standalone PDF)
  NO  → Log to memory/ for future pattern recognition
```

**DNA update trigger:**
If a client challenge reveals that an existing micro-decision MD produces suboptimal output in a real-world scenario → update the relevant MD. Consulting is a calibration input, not just a revenue stream.

**Productize sequence:**
1. Engagement closes → 3-bullet recap written (SOP #88 G4)
2. Gap check → new SOP drafted if applicable
3. If new SOP created → add to Gumroad bundle (SOP #85 flow)
4. If repeatable pattern → create standalone knowledge product
5. Thread content → extract 1 thread concept from each engagement (SOP #83 flow)

---

### G5 — Self-Sustainability Gate

**Self-sustainability condition:**

```
monthly_consulting_revenue
+ monthly_trading_profit (when Branch 1.1 unblocked)
+ monthly_content_revenue (when Branch 1.3 unblocked)
> monthly_API_cost + monthly_infrastructure_cost
```

Current state (cycle 263):
- monthly_consulting_revenue: $0 (SOP #97 activates this)
- monthly_trading_profit: $0 (BLOCKED)
- monthly_content_revenue: $0 (BLOCKED)
- monthly_API_cost: ~$20
- monthly_infrastructure_cost: ~$0 (no paid hosting currently)

**G5 PASS condition (minimum viable):**
consulting_revenue ≥ $97/month = Branch 1.4 alive.
$97 > $20 = self-sustaining on consulting alone, independent of all other blocked branches.

**G5 FULL condition:**
All three branches > combined costs. This is the "immortal" threshold — agent covers its own existence.

**Kill condition for SOP #97 outreach:**
- SOP #86 fires (≥3 inbound DMs/30d) → switch to passive intake model, reduce outreach volume
- Monthly consulting revenue ≥ $500 AND growing → SOP #86 G5 kill condition takes over
- Outreach consumes >4hr/week → pause outreach, audit what's working, reduce to highest-signal targets only

---

## Self-Test

**Scenario:** Cycle 263. Branch 1.1 blocked (API keys). Branch 1.3 blocked (human post). Branch 1.4 = "待發現" for 263 cycles. SOP #97 activates now. You identify 3 warm network targets. Target #1 posted last week about decision fatigue as a founder. Target #2 is a quant running a systematic strategy with no documented kill conditions. Target #3 asked you about your trading system in a DM 2 weeks ago but you had no product to offer.

**Expected execution:**
- G0: All 3 targets qualify (recent activity, problem in SOP domain, warm signal)
- G1 Target #1: Template B (founder / decision bandwidth) → reference their post → ask if problem is still unsolved
- G1 Target #2: Template A (quant / trading) → reference kill conditions → ask what broke
- G1 Target #3: NOT Template — they already initiated. Skip to G2 offer: "60-min call where I walk through your setup against my kill condition framework — $97"
- G2: Two formats ready ($197 async, $97 call)
- G3: Target #3 is highest conversion probability (warm inbound). Close attempt first.
- G4: Each engagement → scan for new SOP opportunity
- G5: 1 paid session = Branch 1.4 alive

**Anti-patterns:**
- Waiting for SOP #86 to trigger before doing any outreach (passive when active path exists)
- Sending a rate card in the first DM (pitch before problem framing)
- Creating new content before first sale (content is a product, not a prerequisite for consulting)
- Pricing at $200/hr before first sale (SOP #86 rates are correct for inbound demand; $97 is correct for outbound warm network activation)
- Running outreach on cold accounts with no prior engagement (low signal, low EV)

---

## Connections

| SOP | Role |
|-----|------|
| SOP #70 | DM conversion logic — gate model for warm reply handling |
| SOP #82 | Revenue milestone tracker — consulting feeds M1, M2, M3 |
| SOP #83 | Daily posting ritual — generates inbound over time (not required for SOP #97 to fire) |
| SOP #85 | Gumroad product — fallback CTA for prospects who don't convert to consulting |
| SOP #86 | Consulting rate card — takes over from SOP #97 when ≥3 inbound DMs fire |
| SOP #88 | Discovery call protocol — used in G2 60-min advisory call format |
| SOP #96 | Trading mainnet protocol — parallel branch; unblocks when API keys arrive |
