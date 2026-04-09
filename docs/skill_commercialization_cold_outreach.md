# Branch 1.3 Skill 商業化 — Cold Outreach Action Pack
> Created: 2026-04-09 UTC (Cycle 283)
> Agent-executable portions of Branch 1.3 launch
> Human-gated: posting requires Edward to copy-paste

---

## Minimum Viable Audience Metric (MVAM)

Branch 1.3 is ALIVE when ANY of these thresholds are hit:

| Signal | Threshold | Meaning |
|--------|-----------|---------|
| Twitter DMs received | ≥ 3 DMs on any thread | G0 proof-of-trust → eligible to offer |
| Email subscribers | ≥ 1 signup | Any signal beats zero |
| Consulting inquiry | ≥ 1 reply to cold outreach | Branch 1.4 activated |
| Paid transaction | ≥ $1 revenue | Branch 1.3 alive, clock to $197 starts |

**Kill condition:** 10 threads posted + 0 engagement (0 replies, 0 DMs) → run SOP #12 platform-audience fit audit.

**Current status:** 0/4 thresholds met. 0 threads posted. Action required: Edward posts SOP #01 thread.

---

## Cold Outreach DM Template (0-Follower Path)

> Use when: Edward has 0 audience and wants the first consulting inquiry.
> Channel: Twitter/X DM, LinkedIn message, or Discord server DM.
> Target: Quantitative traders, systematic traders, crypto traders who post publicly about strategy problems.

### Template A — Strategy Problem Response

*Use when: target has posted about a specific trading problem (losing streak, strategy not working, etc.)*

```
Hey [name] — saw your thread about [specific problem they mentioned].

I've built a 5-gate strategy development protocol from real backtest data that addresses exactly this. Works for crypto/futures/equity systematic.

Would you want me to walk through how it applies to your setup? Async, no pitch, just the framework.

— Edward
```

**Send criteria:** Target has ≥ 100 followers + posts about systematic trading/quant problems publicly. Personalise [specific problem] with exact quote.

---

### Template B — Career/Salary Problem Response

*Use when: target has posted about career transition, salary negotiation, career decision.*

```
Hey [name] — quick thought on your [career/salary] situation.

I've documented a decision framework from 5 years of career negotiations that reduces this to 3 questions. Cuts through the noise fast.

Happy to share the framework if useful — async, 5 minutes to read.

— Edward
```

**Send criteria:** Target is in tech/finance field, ≥ 50 followers, public post about career decision in last 7 days.

---

### Template C — Cold to Warm (no specific problem)

*Use when: target is a respected quant/systematic trader. No specific problem to reference.*

```
[Name] — I follow your work on [specific thing they do well].

I build trading systems systematically. Recently documented [X protocol/result]. 

Curious if you'd be open to a quick exchange — I share my framework, you poke holes in it. 20 min async.

— Edward
```

**Send criteria:** Target is visible practitioner (not academic), posts trading content regularly. Mention something specific from their last 3 posts.

---

## Outreach SOP (G0 → G1)

### G0 — Target Identification (5 min/day)

**Search queries (Twitter/X Advanced Search):**
- `(systematic OR quant OR algo) trading strategy (problem OR struggling OR not working)` — last 7 days
- `(career decision OR job offer OR salary) AND (trading OR finance OR tech)` — last 7 days
- `(futures OR crypto) strategy (backtest OR drawdown OR kill)` — last 7 days

**Filter:** ≥ 50 followers, ≥ 1 relevant post in last 7 days, English or Traditional Chinese.

**Volume:** 3 DMs/day max (Twitter rate limit + quality > quantity).

### G1 — Send (2 min/DM)

1. Read last 3 posts by target — find specific hook
2. Choose Template A/B/C based on context
3. Fill [name] and [specific problem/thing]
4. Send. Do not follow up more than once.

### G2 — Response Protocol

| Response type | Action |
|--------------|--------|
| Positive (wants framework) | Send PDF link (docs/workbook_product_01_strategy_development.md) + offer $97 advisory call |
| Neutral (polite decline) | Thank, no follow-up |
| Question about framework | Answer concisely, then offer $197 async audit |
| No response after 7 days | No follow-up — move to next target |

### G3 — First Revenue Gate ($97 advisory call)

**Trigger:** Target asks to "learn more" or "see the framework in action"

**Offer (copy-paste):**
```
Happy to. Two options:

1. Async: I review your current strategy setup and send a written analysis with the 5-gate framework applied. $197, 48h turnaround.

2. Sync: 45-min call, we work through your strategy together. $97.

Both include the full SOP deck (108 protocols).

Which fits better?
```

---

## Posting Queue — Next 3 Required Actions (Human)

| Priority | Action | File | Est. time |
|----------|--------|------|-----------|
| 1 (TODAY) | Post SOP #01 thread on X | `docs/publish_thread_sop01_twitter.md` | 5 min |
| 2 | 3 cold DMs (Template A targets from search) | This file | 15 min |
| 3 | Post SOP #02 thread on X | `docs/publish_thread_sop02_twitter.md` | 5 min |

**Friction to first post = 5 minutes.** File is open → copy Tweet 1 → paste → post → reply chain.

---

## Branch 1.3 State Tracker

| Metric | Current | Target |
|--------|---------|--------|
| Threads posted | 0 | 1 (unlock G0) |
| Cold DMs sent | 0 | 3 this week |
| Replies received | 0 | 1 (proof of pulse) |
| DMs received | 0 | 3 (G0 threshold) |
| Revenue | $0 | $97 first transaction |
| Users (Skill v2.1.0) | 0 | 1 paying |

**Branch 1.3 status: PRE-LAUNCH. Blocked on Edward's first post.**

---

## Self-Correct Note (Cycle 283)

Branch 1.3 neglected 69 cycles. Root cause: agent produces content → human action required → agent treats human block as "done." **This is wrong.** The correct model:

- Agent-executable: content creation ✓, outreach templates ✓, target search queries ✓
- Human-gated: actual posting (requires Edward)
- Next cycle self-check: has Edward posted SOP #01? Check posting_queue.md Status field.
- If Status still "pending" after 3 cycles: escalate in daily_log + daemon_next_priority

**daemon_next_priority** → Branch 1.3: Edward must post SOP #01 (5 min, file ready). First revenue gate blocked until first post.
