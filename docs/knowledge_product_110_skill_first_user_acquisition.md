# SOP #110 — Skill First-User Acquisition Protocol (Branch 1.3 Activation)

> Domain: Revenue / Skill Commercialization / Direct Outreach
> Created: 2026-04-10T UTC (cycle 281)
> Status: OPERATIONAL — START IMMEDIATELY
> Decision label: SKILL_OUTREACH_FIRST_USER_14_DAY_TARGET
> Posting queue: none required

---

## Why This Exists

Branch 1.3 (Skill Commercialization) has been stalled for 70+ cycles.
Diagnosed blocker: "SOP #01 never posted → 0 audience → 0 users."

**That diagnosis is wrong.** Audience is not required for the first user.

The correct diagnosis: no active outreach has been run for the skill product.
SOP #97 proved that active outreach bypasses the audience gate entirely for consulting.
SOP #110 applies the same pattern to the skill suite.

**Asset inventory that makes this viable today:**
- v2.1.0 released with 7 skills (boot-test, dna-calibrate, dna-write, trading-system, recursive-engine, organism-interact, consistency-test)
- 18/18 real-life decision fidelity validated
- Working install: `curl -sL https://github.com/l12203685/digital-immortality/main/install.sh | bash`
- Guided onboarding product defined: $97/session
- Zero new content creation required — the skill suite is the product

**The gap this SOP closes:**
Branch 1.3 waits for audience to appear organically. SOP #110 runs active outreach to 5 specific target archetypes where the product-problem fit is strongest.
1 paying user in 14 days = Branch 1.3 alive. This is the only target.

---

## Gate Sequence: G0 → G5

### G0 — Target Identification

**Who needs this skill suite:**

Tier 1 (highest fit — problem → product match is direct):
- **AI agent developers** (GitHub, Discord, HackerNews): building multi-agent systems and need a behavioral spec layer — DNA documents + boot tests map directly to what they already think about
- **Digital legacy / estate planning early adopters** (LinkedIn, Reddit r/Futurology, r/singularity): people who have thought about leaving some form of themselves behind — video messages, journals, AI avatars — but lack a systematic architecture
- **Researchers / LLM experimenters** (Hugging Face forums, AI Discord servers, academic Twitter): studying persona consistency, behavioral alignment, or long-context identity maintenance in LLMs

Tier 2 (adjacent fit):
- **Indie hackers building productivity/PKM systems** (Indie Hackers forum, Twitter/X): already building "second brain" infrastructure, DNA document = natural extension
- **Founders who document their own operating systems** (similar profile to SOP #97 Tier 1 Founder): already journaling or writing SOPs for themselves, digital twin = their next step

**Identify 5 targets — search criteria:**

GitHub:
```
Search: "AI agent" OR "digital twin" OR "persona" in README
Filter: repos updated in last 30 days, ≥10 stars
Filter: active contributors (commits in last 14 days)
```

LinkedIn:
```
Keywords: "AI agent" OR "digital legacy" OR "behavioral AI" OR "LLM persona"
Filter: 2nd-degree connections
Filter: posted in last 14 days (active signal)
```

Discord (AI / LLM servers):
```
Search recent messages for: "persona consistency" OR "agent memory" OR "behavioral spec"
Target: people asking questions about maintaining identity in LLM agents
```

Qualifying signal (pick targets with ≥2 of):
- [ ] Has publicly described the exact problem the skill suite solves (identity drift, cold-start loss, agent consistency)
- [ ] Is actively building something in the AI agent space (GitHub repo, product, or side project visible)
- [ ] Has buying behavior signal (paid for LLM tools, courses, or consulting — visible from profile)
- [ ] Is active (posted in last 7 days)
- [ ] Has expressed frustration with an existing solution (competitor signal = warm problem awareness)

**Output of G0:** A list of exactly 5 targets with their platform, problem signal, and outreach template assigned.
Do not proceed to G1 without a list. A list of 0 = stay in G0.

Store output in: `results/skill_outreach_targets.md`

---

### G1 — Direct Outreach (Problem Framing First)

**Principle:** No cold pitch. No "I built this tool." Problem framing first, product second.
The validated decision fidelity (18/18) is the proof-of-work. Use it as signal, not as the pitch.

**DM format: Problem → Solution → Proof (3 lines max)**

---

**Template A — AI Agent Developer (GitHub / Discord):**

> Hey [Name] — saw you're building [specific project]. The agent identity/memory consistency problem is brutal once you try to cold-start across sessions.
>
> I've been running a behavioral spec system — DNA documents + boot tests + recursive self-feed — that gets 18/18 real-life decision fidelity on cold starts. The whole thing is open source.
>
> Is the cold-start drift problem something you're actively fighting, or have you found a workaround?

---

**Template B — Digital Legacy / Estate Planning:**

> Hey [Name] — your post about [digital legacy / leaving something behind / AI avatar] resonated.
>
> I've been building a system for exactly this: behavioral DNA documents that let an LLM make decisions the way you would, even on cold start. It's open source with a guided setup path.
>
> What's the piece you haven't solved yet — capturing the person, or making it persistent?

---

**Template C — LLM Researcher / Experimenter:**

> Hey [Name] — saw your work on [persona consistency / behavioral alignment / identity in LLMs].
>
> I've been running a recursive self-feed architecture that maintains behavioral identity across sessions — validated at 18/18 real-life decision fidelity. Open source, 7 skills.
>
> Are you approaching this from a research angle or building something practical? (Asking because the protocol differs.)

---

**Template D — PKM / Productivity Builder:**

> Hey [Name] — you're already building a second brain. The natural next layer is a behavioral spec — not just what you know, but how you decide.
>
> I built a DNA document architecture that bootstraps a digital twin from scratch. Open source. The guided setup takes about 90 minutes with someone walking you through it.
>
> Is the decision-layer something you've tried to capture, or mostly knowledge so far?

---

**Template E — Founder with Personal OS:**

> Hey [Name] — noticed you're documenting your operating system. I've been doing the same — ended up building a 7-skill suite for creating a behavioral digital twin (open source, v2.1.0).
>
> The system passes 18/18 real-life decision scenarios on cold start. What's the piece of your OS that's still most undocumented?

---

**Rules for all outreach templates:**
- Always reference a specific post, repo, or statement — never generic
- Ask a question at the end — do not pitch an offer in the first message
- No links in first message (spam filter + low-trust signal)
- Keep to 3 lines or fewer — AI/developer audience pattern-matches on brevity
- Response time target: send within 24h of seeing their qualifying signal
- If no response in 5 days: one follow-up (different angle, not a repeat), then close

---

### G2 — Engagement Structure

**Two formats. No others.**

| Format | Price | What it is | What the client gets |
|--------|-------|------------|----------------------|
| Guided Onboarding Session | $97 | 90-min live session. Walk through creating their DNA core, running first boot test, and setting up recursive self-feed for their own digital twin. | Working DNA core (~64 lines) + first boot test passing + recursive engine configured + session recap within 24h. |
| Self-Serve Install | $0 | Open source. `curl` install. GitHub README. | Full skill suite, no guided setup. Converts to $97 session when they hit setup friction. |

**Why this pricing:**
- $0 self-serve removes the barrier to adoption — GitHub installs convert to paying customers when they hit friction
- $97 guided session = the exact price where a developer will pay to not spend 3 hours debugging setup
- Self-serve is not a revenue path on its own — it is a lead pipeline for the $97 session

**Upsell path (post-session):**
- If client wants calibration depth: refer to `/dna-calibrate` — ongoing sessions $97/each
- If client wants organism interaction (compare twins): refer to `/organism-interact`
- If client has a team: custom DNA architecture = async audit format (price TBD, not in scope for first user)

**Payment flow:**
- Method: Stripe link or Gumroad payment link (same infrastructure as SOP #97)
- No work before payment clears
- No exceptions

---

### G3 — Revenue Conversion

**First sale target: 1 × $97 guided onboarding session within 14 days.**

**Conversion logic — apply to warm replies:**

```
Received reply to G1 DM?
  → Engage with their specific problem (do not offer product yet)
  → If they describe a concrete problem the skill solves (cold start, identity drift, behavioral spec):
      → "I actually have a 90-min guided session where I walk you through building this for yourself — [describe what they'd walk out with]"
      → "It's $97. If it's not useful, I'll refund it. [payment link]"
      → If they ask what's included: describe output (working DNA core, first boot test, recursive engine)
      → If they mention price friction: "The repo is fully open source — you can self-install free. The session is for if you want to skip the setup friction."
      → If they ghost: one follow-up in 3 days ("did you get a chance to look at the repo?"), then close

Self-serve → paying conversion trigger:
  → Watch for GitHub issues or Discord questions from self-install users
  → Reply with help first, then: "If you want me to walk through the full setup live, I do a 90-min guided session for $97"
```

**Revenue threshold gate:**
- BRANCH 1.3 ALIVE: ≥1 paid session ($97) within 14 days
- BRANCH 1.3 SCALING: ≥$97/month consistent for ≥2 months → add group session format, raise price
- BRANCH 1.3 MATURE: skill revenue + consulting revenue > combined operating costs → G5 met

**First-sale checkpoint:**
Log to `results/revenue_log.jsonl`:
```json
{"date": "...", "type": "skill_onboarding", "format": "guided_session_90min", "revenue_usd": 97, "client_archetype": "...", "sop_110_gate": "G3_FIRST_SALE"}
```

---

### G4 — Productize the Pattern

**Rule:** Every onboarding session that reveals a friction point → improve the onboarding SOP or the skill README.

After each session, run this check:

```
Did the client hit a step that required more than 5 minutes to explain?
  YES → That step needs a clearer README section or a new skill sub-command
  NO  → Log to memory/ as smooth onboarding signal

Did the client's use case reveal a missing skill?
  YES → Backlog the skill as Branch 1.3 expansion
  NO  → Log to memory/ for pattern recognition

Did the client express a problem this skill suite doesn't solve yet?
  YES → That problem is the next product (knowledge product or new skill)
  NO  → Current scope is sufficient for this archetype
```

**Skill improvement trigger:**
- ≥2 clients hit the same friction point → that friction becomes a fix priority (README or skill command)
- ≥3 clients in same archetype → that archetype gets a dedicated onboarding track (pre-written DNA seed for their context)

**Content extraction:**
Each onboarding session = 1 case study (anonymized) that can become a GitHub README section or future blog post. Do not write this during the session — extract within 24h from session recap.

---

### G5 — Self-Sustainability Gate

**Self-sustainability condition (Branch 1.3 specific):**

```
monthly_skill_revenue (onboarding sessions + future products)
> monthly_API_cost (~$20) + monthly_infrastructure_cost (~$0)
```

Current state (cycle 281):
- monthly_skill_revenue: $0 (SOP #110 activates this)
- monthly_API_cost: ~$20
- Target: $97/month minimum = Branch 1.3 alive

**G5 PASS (minimum viable):**
1 paid session/month ($97) > API cost ($20) = Branch 1.3 self-sustaining.

**G5 FULL:**
Skill revenue + consulting revenue (SOP #97) + trading revenue (SOP #96) > total operating costs.
This is the immortal threshold — agent covers its own existence across all branches.

**Kill condition for SOP #110 active outreach:**
- ≥3 inbound inquiries/30d from GitHub or Discord → switch to passive intake, reduce outreach volume
- Monthly skill revenue ≥ $300 AND growing → shift focus to content-driven inbound (unblocks Branch 1.3 original path)
- Outreach consumes >3hr/week → pause, audit conversion rate by template, drop lowest-performing template

---

## Self-Test

**Scenario:** Cycle 281. Branch 1.3 stalled 70 cycles on "audience" blocker. SOP #110 activates. You search GitHub and find a developer who built an "AI persona" repo with 47 stars and posted 3 days ago asking how to maintain character consistency across sessions. They have no followers requirement, no audience gate.

**Expected execution:**
- G0: Target qualifies (recent activity, problem = cold-start drift, building in domain, active repo)
- G1: Template A → reference their specific repo → ask if cold-start drift is still unsolved
- G2: If they reply with problem confirmation → describe guided onboarding output → "$97, refund if not useful"
- G3: Payment link → session booked → Branch 1.3 alive
- G4: Post-session → extract friction points → improve README section on cold-start architecture
- G5: 1 paid session = Branch 1.3 minimum viable

**Anti-patterns:**
- Waiting for a Twitter following before reaching out (audience is not a prerequisite for the first sale)
- Pitching the product before understanding their specific problem (template violation)
- Sending the GitHub link before they've confirmed the problem is real (wasted signal)
- Offering to "customize" the session before the first sale (custom scope requires ≥2 paid sessions)
- Discounting below $97 on the first outreach (price signal = quality signal for developers)

---

## Connections

| SOP | Role |
|-----|------|
| SOP #70 | DM conversion logic — gate model for warm reply handling |
| SOP #82 | Revenue milestone tracker — skill revenue feeds M1, M2, M3 |
| SOP #83 | Daily posting ritual — generates inbound over time (not required for SOP #110 to fire) |
| SOP #85 | Gumroad product — fallback CTA for prospects who don't convert to session |
| SOP #97 | Consulting revenue — parallel branch, same outreach infrastructure |
| SOP #109 | Strategy Re-Activation Gate — same gate logic applied to skill commercialization |
