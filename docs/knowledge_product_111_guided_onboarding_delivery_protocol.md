# SOP #111 — Guided Onboarding Delivery Protocol ($97 Session)

> Domain: Revenue / Skill Commercialization / Session Delivery
> Created: 2026-04-10T UTC (cycle 282)
> Status: OPERATIONAL — run after first booking from SOP #110
> Decision label: GUIDED_ONBOARDING_DELIVERY_STANDARD
> Posting queue: Nov 2026 (after SOP #110)

---

## Why This Exists

SOP #110 acquires the first user.
SOP #111 delivers the session they paid for.

The gap between "payment received" and "client walks out with a working digital twin" is where:
- The product quality is actually tested
- Referrals are generated (or not)
- The $97 session converts to repeat sessions (or doesn't)

A bad first delivery = 0% referral rate. A good first delivery = $97 × N+1 clients.
SOP #111 standardizes the delivery so quality doesn't depend on how good the session feels.

**What the client gets (the output contract):**
1. A working `dna_core.md` (~64 lines) — operational in any LLM session
2. A first boot test passing (≥3 scenarios aligned)
3. Recursive engine configured (`staging/` set up, `Input(0)` written)
4. Session recap document within 24h

**What this SOP guarantees:**
- Every session has the same structural coverage (4 phases, 90 minutes)
- No session ends without a working artifact the client can use immediately
- Friction points are captured for SOP improvement (G4 loop)

---

## Pre-Session Checklist (G0)

Run before every session, no exceptions.

**Client preparation (send 24h before):**
```
[Email/DM to client — 24h before session]

Before our session:
1. Install the skill suite (3 minutes): curl -sL https://github.com/l12203685/digital-immortality/main/install.sh | bash
2. If install fails: skip — we'll set it up live
3. Think of 3 decisions you made recently that were hard to explain to others
4. Come with: your current job/role, a core life philosophy sentence, a specific goal with a timeline

No other prep needed. See you at [time].
```

**Facilitator preparation (60 min before session):**
- [ ] Read client's profile (GitHub/LinkedIn/what they shared in G1 DM)
- [ ] Identify which archetype they are (Agent Dev / Digital Legacy / Researcher / PKM / Founder OS)
- [ ] Load archetype-specific examples for Phase 2 (see archetype examples below)
- [ ] Open: `templates/example_dna.md` (reference), `templates/generic_boot_tests.json` (boot test pool)
- [ ] Test: `python consistency_test.py templates/example_dna.md --output-dir results` — confirm it runs
- [ ] Prepare session recap template (fill header only: client archetype, session date, payment confirmed)

---

## Phase 1 — Identity Anchor (20 min)

**Goal:** Fill in the Identity Anchor block in dna_core.md with client's actual values.

**Script:**

```
"Let's start with the five fields that anchor everything else.
 These aren't abstract — they're the inputs your digital twin will use on every cold start.
 I'll ask you directly, and we'll iterate until the words are yours, not mine."
```

**Questions (ask in order, iterate until precise):**

| Field | Question | Iteration rule |
|-------|----------|----------------|
| Name | [Already known] | — |
| Role | "What do you do, in one sentence? Not your title — what you actually do." | If too abstract → "What did you do last Tuesday that mattered?" |
| Philosophy | "How do you see life? One sentence. Not what you wish you believed — what you actually act on." | If generic → "Give me a decision from the last 6 months that proves that belief." |
| Core goal | "What's the specific target you're working toward? Name the thing and the deadline." | If vague → "What would you have to see in 12 months to feel like this is working?" |
| Constraints | "What will you NOT do to reach that goal? Name 2 things." | If none → "Tell me about a time you could have taken a shortcut and didn't. Why not?" |

**Output:** Completed Identity Anchor block in dna_core.md.

**Archetype-specific examples:**
- Agent Dev: "My current role is building an autonomous agent that handles customer support decisions without human review."
- Digital Legacy: "My goal is to have a working behavioral spec by the time my daughter is old enough to ask me hard questions."
- Researcher: "My constraint is I won't publish claims about behavioral alignment that I haven't tested on at least 3 live sessions."
- PKM Builder: "My philosophy: systems survive moods. I only trust something if I can run it on a bad day."
- Founder OS: "My core goal is $10K MRR by Q3. My constraint is I won't hire before product-market fit is confirmed."

---

## Phase 2 — Micro-Decisions (25 min)

**Goal:** Extract 5-10 MD entries from real decisions the client has made.

**Method:** Behavioral archaeology. Do not ask for principles — ask for incidents.

**Standard sequence:**

```
"Tell me about a decision you made in the last 6 months that was hard to explain to others.
 Not what you decided — why you decided it."
```

For each incident:
1. Ask: "What was the actual decision you were making?"
2. Ask: "What made it hard? What was the real tension?"
3. Ask: "How did you resolve it? What was the core principle you applied?"
4. Compress: "If I had to write this as a one-line rule, it would be: [compress it]. Is that right?"
5. If yes → add to dna_core.md as `| MD-[N] | [compressed rule] | [source incident] |`

**Target:** 5 MDs minimum. 10 MDs is a strong session. Do not manufacture MDs from hypotheticals.

**Warning signs (stop and recalibrate):**
- Client is giving abstract principles, not incidents → ask for the specific example again
- Client keeps saying "it depends" → ask "what does it depend on? Name the first variable."
- Client is repeating already-covered territory → move to next incident

---

## Phase 3 — Boot Test (20 min)

**Goal:** Run 3 scenarios against the client's dna_core.md and confirm ≥2 pass (client verifies).

**Select 3 scenarios** from `templates/generic_boot_tests.json`:
- 1 from the client's primary domain (trading/career/relationships/decisions)
- 1 from a domain they haven't mentioned (tests coverage)
- 1 meta-behavior test (search_before_act / output_must_persist / three_layer_loop)

**Script:**

```
"Now we test whether what's written actually reflects how you'd decide.
 I'll read you a scenario. You tell me what you'd do. Then we check if your DNA gives the same answer."
```

For each scenario:
1. Read the scenario (no setup — cold, as a cold-start LLM would get it)
2. Client answers: "I would..."
3. Run: `python consistency_test.py [client_dna.md] --scenario [scenario_id]`
4. Compare: if ALIGNED → "✅ DNA agrees. Let's continue."
5. If MISALIGNED → "The DNA said [X]. You said [Y]. Which is right — and why does the DNA have it wrong?"
6. Fix the DNA entry → re-run until ALIGNED

**Target:** ≥2/3 ALIGNED on first pass. If 0/3 → stop, find which Identity Anchor or MD is wrong, fix it.

---

## Phase 4 — Recursive Engine Setup (15 min)

**Goal:** Configure `staging/` so the client's twin can run autonomously between sessions.

**Steps:**

```bash
# 1. Create staging directory
mkdir -p staging

# 2. Write Input(0)
echo "Given my DNA core, what is the most important next action toward my core goal?" > staging/next_input.md

# 3. Confirm engine runs
python recursive_engine.py --init
python recursive_engine.py --prompt staging/next_input.md
```

**What the client should see:** A first output from their digital twin — a concrete action recommendation based on their dna_core.md.

If the output is vague → add one more MD that addresses the context. Repeat.

**Calibration question:**

```
"Does that sound like something you'd actually say? 
 If not — what's wrong with it? We'll add a MD to fix it."
```

**End of session checkpoint:**
- [ ] `dna_core.md` exists and has Identity Anchor + ≥5 MDs
- [ ] `staging/next_input.md` written
- [ ] `python recursive_engine.py --status` runs without error
- [ ] Client can open `dna_core.md` and say "that's me" about ≥3 entries

---

## G1 — Session Recap (within 24h)

Send to client within 24h of session end.

**Format:**

```markdown
# Session Recap — [Client Name] — [Date]

## What We Built
- **DNA core**: [N] micro-decisions captured; Identity Anchor complete
- **Boot tests**: [N/3] passing on first run; [scenario IDs] confirmed aligned
- **Recursive engine**: Input(0) set; first output generated

## Your Digital Twin in One Paragraph
[2-3 sentences summarizing the core pattern that emerged — write it in first person as them]

## How to Use It
- Cold start: `cat dna_core.md` at the start of any LLM session
- Run a boot test: `python consistency_test.py dna_core.md --output-dir results`
- Recursive engine: `python recursive_engine.py --prompt staging/next_input.md`

## What's Missing (optional next session)
[List 1-2 domains where the DNA is thin — not a sales pitch, just honest gap identification]

## Files
- `templates/dna_core.md` — your operational core
- `staging/next_input.md` — seed for autonomous recursion
- `results/` — boot test output
```

---

## G2 — Friction Capture (within 48h)

Run this checklist after every session.

```
Did the client hit a step that required >5 min to explain?
  YES → Which step? → Log in session_friction_log.jsonl → flag for README improvement

Did the client's use case reveal a missing skill?
  YES → Log in memory/ as skill gap → backlog for Branch 1.3 expansion

Did Phase 3 produce 0 aligned scenarios on first pass?
  YES → Which MD was wrong? → Log root cause → consider adding to boot test pool

Did the client express a problem this skill suite doesn't solve?
  YES → Is it a real problem or scope creep? → If real → log as potential SOP#112+ territory
```

**Log entry format:**
```json
{"session_date": "...", "archetype": "...", "phase1_minutes": N, "phase2_md_count": N, "phase3_pass_rate": "N/3", "phase4_status": "pass|fail", "friction_points": [...], "missing_skills": [...], "client_quote": "..."}
```

Store in: `results/onboarding_session_log.jsonl`

---

## G3 — Repeat Session Trigger

**Offer a second session IF:**
- Phase 2 produced <7 MDs (thin DNA — common for 90-min first session)
- Phase 3 had ≥1 MISALIGNED scenario that wasn't resolved in session
- Client's domain has a major gap (e.g., trading system not covered)

**Script:**

```
"We got [N] micro-decisions today — that's a solid foundation.
 The main gap is [domain]. A second 90-min session focused on [domain] would round out the spec.
 Same format, same price ($97). Want to book it?"
```

Do not offer the second session as a discount or bundle. Each session is $97 standalone.

---

## G4 — Productize the Pattern

After ≥3 sessions in the same archetype:
- Create an archetype-specific DNA seed file (`templates/seed_agent_dev.md`, etc.)
- Pre-fill Identity Anchor with archetype-typical values (saves 5-10 min in Phase 1)
- Pre-select 3 boot test scenarios optimized for that archetype

After ≥2 clients hit the same Phase 2 friction (same domain hard to extract):
- Write a domain-specific extraction guide (`docs/extraction_guide_trading.md`)
- Add to facilitator preparation checklist (G0)

---

## G5 — Self-Sustainability Check

Each session:
- Revenue: $97
- Time cost: 90 min session + 30 min prep + 24h recap = ~3h total
- Effective rate: ~$32/hr

G5 PASS: ≥1 session/month ($97) > API cost ($20) = Branch 1.3 minimum alive.
G5 TARGET: ≥3 sessions/month ($291) > operating costs + time constraint met.
G5 SCALE trigger: ≥5 sessions/month booked → evaluate group format ($197 × 4-6 people = 75% time reduction per client).

**Kill condition for guided format:**
- Client satisfaction <3/5 average across ≥3 sessions → stop selling, fix the delivery SOP first
- Time cost >5h/session consistently → delivery is inefficient, restructure phases
- Demand for group format from ≥2 clients → shift to group pilot

---

## Connections

| SOP | Role |
|-----|------|
| SOP #110 | First-User Acquisition — feeds clients into this SOP |
| SOP #97 | Consulting Revenue — parallel format, same infrastructure |
| SOP #104 | Async Audit Delivery — alternative format for non-session clients |
| SOP #82 | Revenue milestone tracker — session revenue feeds M1, M2 |
| SOP #99 | Recursive Engine Health Check — referenced in Phase 4 |
