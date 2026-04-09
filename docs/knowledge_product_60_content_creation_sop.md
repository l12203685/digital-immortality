# SOP #60 — Content Creation & Shipping Protocol

**Domain 10: Content Pipeline / Economic Self-Sufficiency**
**Status:** Active
**Version:** 1.0
**Dependencies:** SOP #12 (Distribution), SOP #51 (Time Allocation), SOP #13 (Personal OS), SOP #59 (Life Default Design)

---

## Why This SOP Exists

The recursive engine can produce insights indefinitely. SOP #12 defines distribution architecture. Neither operationalizes the daily act of converting insights into shipped content.

The gap: Branch 1.3 revenue is zero not because content doesn't exist — 59 SOPs are written — but because zero posts have shipped. The bottleneck is not creation, it is the habitual execution of the final step: publish.

This is the last 5% problem. The SOP exists to eliminate it.

```
Insight → Format → Draft → Review → Publish → Log Signal → Iterate
```

Without this loop running, all upstream work is display, not storage. A published post exists in the world even after context is cleared. An unpublished draft doesn't.

Completion signal: SOP #01 posted on X. Every subsequent SOP posted within 48h of its queue date.

---

## Three-Layer Architecture

| Layer | Gate | Function |
|-------|------|----------|
| L1 Execute | G0–G2 | Daily: check queue → format → post → log |
| L2 Evaluate | G0–G1 | Weekly: audit posting rate + engagement signals |
| L3 Evolve | G3 | Quarterly: rotate formats based on ΔEngagement |

---

## Gates

### G0: Queue Audit (Daily, 5 min)

**Signals:**
1. `posting_queue.md` — today's post scheduled?
2. Thread file exists in `docs/publish_thread_sop*.md`?
3. Last post date vs. today's date → days since last post

**Kill switch**: ≥14 days since last post → G5

**Healthy state**: queue date matches today → proceed to G1

---

### G1: Derivative Scan

Track weekly:
- ΔPosting rate (posts/week vs. prior week)
- ΔEngagement rate (signals logged in `posting_queue.md`)
- ΔGumroad DMs (proxy for revenue proximity)

Decision rule: if ΔPosting rate = 0 for 7 days → escalate to G5 before checking anything else.

---

### G2: Non-Negotiable Shipping Budget

Minimum viable execution, every week:
- ≥1 SOP thread posted per 48h (queue date compliance)
- Every post logged in `posting_queue.md` with status=posted + date
- Every 10 DMs → Gumroad activation check (see `docs/gumroad_listing_draft.md`)
- `platform/daily_posting_helper.py --confirm` after each post
- No new SOPs written while ≥3 posts are overdue on queue

G2 is non-negotiable. Content creation continues only when shipping is current.

---

### G3: Quarterly Format Rotation (Leverage Scan)

Every 90 days:
- Export engagement data from `posting_queue.md` signals column
- Rank SOP threads by engagement rate
- Identify highest-performing hook format
- Run 30-day trial of new format for next 10 SOPs
- If ΔEngagement ≥+20% → write as default format to this SOP

---

### G4: Weekly Review (10 min, Sunday)

| Metric | Target | Current |
|--------|--------|---------|
| Posts shipped this week | ≥3 | log in queue |
| Queue compliance rate | 100% | (posted on date / scheduled) |
| Engagement signals logged | 100% of posted | |
| DM count vs. G2 threshold | count/10 | |

---

### G5: Emergency — Shipping Freeze

**Trigger**: ≥14 days since last post OR queue ≥3 posts overdue

**Protocol:**
1. HALT all new SOP drafting
2. Post oldest overdue SOP thread immediately (no editing — ship as-is)
3. Post next day, next day
4. Do not resume drafting until queue is current (0 overdue posts)
5. Log freeze start/end dates in `posting_queue.md`

No L3 format experiments during G5. Ship first, optimize later.

---

## DNA Anchors

- MD-12: distribution is the 12th gate, not a bonus step
- MD-41: platform persistence — consistent posting > burst posting
- MD-48: Bayesian update — engagement signals update content strategy
- MD-67: economic self-sufficiency as survival condition
- MD-144: recursive output must persist to durable storage, not just display

## Three-Layer Integration

- **L1 (G2)**: daily shipping budget — 1 post per 48h, no exceptions
- **L2 (G0/G1)**: weekly audit of posting rate + engagement derivative
- **L3 (G3)**: quarterly format evolution based on what actually works

## Connection to Other Branches

- **Branch 1.3**: direct dependency — zero posts → zero audience → zero revenue
- **Branch 3.1**: recursive engine produces insights; this SOP ships them
- **Branch 7**: each SOP is a content unit; this SOP ensures they're published

---

*Last updated: 2026-04-09T UTC*
