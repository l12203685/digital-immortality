# SOP #46 — Async Communication & Message Triage Protocol

> Branch 7 — 知識輸出 / life maintenance
> Created: 2026-04-09 UTC (cycle 207)
> Domain: 4 (社交圈) + 8 (生活維護)
> Backing MDs: MD-322, MD-116, MD-328, MD-141, MD-13

---

## One Claim

Every unread message is a decision deferred. You don't have a communication problem. You have a triage problem.

---

## The Real Cost

The cost of poor message triage is not missed messages.
It's decision fatigue:

- Each message without a system = another in-the-moment judgment call
- 40 messages/day × 30 seconds each = 20 min/day in micro-decisions
- None of those micro-decisions require your peak cognitive state
- But they erode it

**This SOP eliminates in-the-moment communication decisions.** Pre-commit everything: who gets a response, when, how long, what the CTA is.

---

## Gate 0: Classify Inbound

Before reading message content, classify the source:

| Tier | Who | Default action | SLA |
|------|-----|----------------|-----|
| T1 | Core relationships (daily-life, family, Tier 1 network) | Read + respond | 24h |
| T2 | Active network (colleagues, collaborators, regular contacts) | Read + respond | 48h |
| T3 | Weak ties, acquaintances, low-signal contacts | Skim → batch | 72h |
| T0 | Cold outreach, mass communications, FYI CC'd | Archive/ignore | N/A |

**Signal vs noise filter** (apply before reading):
- Does sender have history of sending actionable content? → Signal
- Is this the first direct message or clearly mass-sent? → Noise until proven otherwise
- Does the subject/preview contain a named question or request? → Signal
- Vague opener ("Hey, how are you?") with no apparent context → Wait for follow-up before responding

**Rule**: Classify source first, read content second. Tier determines response SLA before the message content does.

---

## Gate 1: Response Window Pre-Commitment

Never negotiate SLA in the moment. Pre-commit:

| Tier | Response window | Exception |
|------|-----------------|-----------|
| T1 | ≤24h | Time-sensitive (explicit deadline) → immediate |
| T2 | ≤48h | — |
| T3 | ≤72h, batch on one day/week | — |
| T0 | No response required | — |

**Rule**: If you receive a T1 message and can't respond within 24h, send a receipt acknowledgment: "Got this, will reply by [time]." One sentence. No content yet.

**Anti-pattern**: Responding immediately to T3/T0 because it's low-effort = rewarding noise + signal to sender that you're always available.

**MD-322 application**: If you find yourself making the same SLA judgment ≥3 times, the sender has been misclassified. Reclassify them.

---

## Gate 2: Template-First Composition

Never compose to a blank screen. For every recurring message type, a template exists:

| Message type | Template location | Modification allowed |
|-------------|------------------|---------------------|
| Positive/agreement reply | `docs/engagement_response_templates.md` §1 | Personalize last line |
| Question/challenge | §2 | No change to structure |
| DM from thread (trust ladder) | §3 | Substitute product/topic |
| Hiring inquiry | §5 | Add role-specific line |
| Async calibration request | `docs/samuel_async_dm.md` §Parts | Adapt scenarios for target |
| Organism recruitment pitch | `docs/knowledge_product_45_organism_recruitment_sop.md` §Stage 2 | Keep core script |

**If no template exists**: write one. The second time you compose a message type from scratch = system failure. First instance is acceptable. Second = create the template.

**Rule**: Open the template file first. Write from there. Never from blank.

---

## Gate 3: Length Calibration

Message length is inversely correlated with clarity of thinking:

```
Certainty → brevity
Uncertainty → length
```

| Scenario | Target length |
|----------|---------------|
| Simple answer to simple question | 1–3 sentences |
| Explanation of a position | 3–5 sentences + 1 example |
| Complex async calibration | 3 structured parts (see samuel_async_dm.md) |
| Disagreement | 2 sentences: "I'd frame it differently: [one sentence]" |
| Declining a request | 1 sentence. No over-explanation. |

**Diagnostic**: If a draft exceeds 200 words, ask: "Am I uncertain about my answer or uncertain that they'll accept it?" 
- Uncertain about answer → think more, write less
- Uncertain they'll accept → their acceptance is not in your message, it's in the relationship

**MD-116 application**: One claim per message. If you're making 3 points, send 3 messages or pick the one that matters.

---

## Gate 4: CTA Clarity

Every outbound message has exactly one of:
- One clear ask (requires action from them)
- One clear offer (requires decision from them)
- No ask (share/inform only — state this explicitly: "no reply needed")

**Anti-pattern**: Multi-ask messages.

```
WRONG: "Let me know what you think, and if you want to catch up, and also check out this thread I wrote."
RIGHT: "Read this [link] when you have 5 min. Let me know what stands out." (one ask)
```

**Samuel DM application**: Part 1 = one ask (mark what's wrong in §0). Part 2 = one ask per scenario (what do you actually do?). Never combine.

**MD-328 application**: Proactive maintenance messages (no ask, no agenda) should be explicitly no-ask: "No reply needed — just wanted to share this." Removes pressure, increases response rate paradoxically.

---

## Gate 5: Extract to Memory

Every conversation that contains ≥1 behavioral signal goes to durable storage within 24h:

| Signal type | Where to extract |
|------------|-----------------|
| Their decision in a real scenario | `templates/[person]_dna.md` §4 Behavioral Patterns |
| Correction of your model of them | `templates/[person]_dna.md` §0 (update principle) |
| Insight applicable to Edward's DNA | `LYH/agent/dna_core.md` as new MD candidate |
| Meta-observation about communication | This SOP (update gate) |

**Kill condition**: If a conversation yields ≥3 behavioral signals but nothing is extracted → system failure. The conversation didn't count.

**Distillation rule**: Don't summarize. Extract the sentence that could become a principle. "Samuel said he'd reach out even if there's nothing specific to discuss" → `§4: Initiates contact without agenda when relationship value is high`. One behavior, stated as a pattern.

---

## Self-Test

> It's Tuesday. You have 23 unread messages. Among them:
> - Samuel replied to your calibration DM (T1)
> - A recruiter cold-messaged about a "great opportunity" (T0)
> - A Twitter DM from someone who replied to SOP #01 thread, asking for the workbook link (T2)
> - A colleague asking for your take on a strategy they're developing (T2)
> - Your partner asking about dinner plans (T1)

Apply the gates:
- Samuel reply → T1, read immediately, respond ≤24h, extract behavioral signals to samuel_dna.md §4
- Recruiter → T0, archive without reading (or skim preview only; if genuinely interesting, reclassify to T3)
- Twitter DM → T2, respond ≤48h, use engagement_response_templates.md §3 trust ladder exchange 1
- Colleague strategy → T2, respond ≤48h, one-sentence frame: "What's the mechanism you're betting on?" (one ask, not review)
- Partner dinner → T1, respond immediately (1 sentence)

Total in-the-moment decision time: ~2 min. Without triage system: ~20 min.

---

## Kill Conditions

| Condition | Response |
|-----------|----------|
| Same SLA judgment ≥3× for same sender | Reclassify sender tier |
| Draft >200 words for simple exchange | Stop. State your answer in one sentence first. |
| Composing from blank screen for 2nd time | Create template now |
| Signal extracted to nowhere | Flag as system failure; extract retroactively |
| T3/T0 responded immediately | Audit: was this FOMO, guilt, or politeness? Pre-commit response for next occurrence |

---

## Files

| File | Purpose |
|------|---------|
| `docs/engagement_response_templates.md` | Twitter/DM response templates |
| `docs/samuel_async_dm.md` | Samuel calibration DM (3-part async protocol) |
| `docs/knowledge_product_45_organism_recruitment_sop.md` | Organism C recruitment pitch script |

---

*SOP #46 | Domain: 4 (社交圈) + 8 (生活維護) | Backing MDs: MD-322, MD-116, MD-328, MD-141, MD-13*
*2026-04-09 UTC | Cycle 207*
