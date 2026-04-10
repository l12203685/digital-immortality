# SOP #87 — Email List Bootstrap

> Domain: Revenue / Audience Ownership
> Created: 2026-04-09T10:35Z
> Status: OPERATIONAL
> Trigger: G3 (Gumroad product live, SOP #85 G5 complete). Run once to build owned channel.

---

## Why This Exists

X (Twitter) = rented audience. Gumroad = transactional. Email = owned.

If X bans the account or algorithm changes → audience disappears.  
Email list = the only asset that survives platform collapse.

**Decision principle in play:**
- MD-003: Own the channel, not just the content. Platform dependency = single point of failure.
- Once Gumroad is live (SOP #85 G5), every buyer should be captured into an email list.
- Every product → email list → warm audience for next product. Compounding.

---

## Gate Sequence: G0 → G5

### G0 — Trigger Check

Run when ALL of:
- [ ] SOP #85 G5 complete (Gumroad product live, at least one sale possible)
- [ ] Committed to posting ≥3×/week on X (SOP #83 habit established)

If neither: STOP. Email list without content = list decay.

---

### G1 — Platform Selection (5 min)

Default: **Beehiiv** (free up to 2500 subs, built-in monetization, referral program)

| Platform | Free tier | Built-in monetization | When |
|----------|-----------|----------------------|------|
| Beehiiv | ≤2500 subs | Yes (ads + paid subs) | Default |
| ConvertKit | ≤1000 subs | Limited | If already on ConvertKit |
| Substack | Unlimited | Yes (paid subs) | If long-form editorial is primary content |

Pick ONE. Do not run two lists simultaneously.

---

### G2 — Setup (20 min)

1. Create account at beehiiv.com
2. **Newsletter name:** Use personal brand name (e.g., "Edward Lin's Trading Edge") — not a concept name
3. **Welcome email:** Write in 10 min using template:

```
Subject: You're in. Here's what happens next.

Hey [first name],

Welcome. You're now on the list for [newsletter name].

What you'll get:
• [Frequency: e.g., 1x/week] on [topic: trading/building/thinking]
• The frameworks I use, not the theory I don't

First thing I'm sending you: [promise of first valuable email]

Reply with one word: what's your biggest problem with [topic right now]?
(I read every reply.)

— Edward
```

4. **Opt-in page URL:** Use your newsletter name as slug (e.g., beehiiv.com/subscribe/edwardlin)
5. **Unsubscribe footer:** Keep Beehiiv default — do NOT strip it (legal requirement + trust signal)

---

### G3 — Connect to Gumroad (10 min)

**Goal:** Every buyer auto-added to email list.

Option A (Beehiiv + Gumroad native):
- Gumroad → Product settings → "Thank you page" → add: "Also join my newsletter: [beehiiv link]"
- Not automated — captures ≥60% who see the page

Option B (Zapier automation — recommended):
- Zap: Gumroad "New Sale" → Beehiiv "Add Subscriber"
- Cost: Free tier sufficient for first 100 sales
- Captures 100% of buyers automatically

Minimum: Option A. Target: Option B within first 10 sales.

---

### G4 — X → List Bridge (5 min)

1. Add newsletter link to X bio (below Gumroad link if both exist)
2. Tweet once per week: "If you want the longer version of [top thread], it's in the newsletter: [link]"
3. Pin the newsletter link tweet when no product is pinned

Anti-pattern: Tweeting about the newsletter every day = annoying. Once/week = good.

---

### G5 — Sign-Off

- [ ] Beehiiv account live
- [ ] Welcome email written and set as automation
- [ ] Gumroad connected (at minimum Option A)
- [ ] Newsletter link in X bio
- [ ] First issue scheduled or sent

**Next SOP: #88 — First Newsletter Issue**  
Trigger: List has ≥1 subscriber OR 7 days after G5 complete (whichever first)

---

## Metrics

| Metric | Threshold | Action |
|--------|-----------|--------|
| Open rate | <30% | Fix subject line formula |
| Click rate | <5% | Fix CTA placement |
| Unsubscribe rate | >2% per issue | Fix content relevance |
| List growth | <10 subs/week after X is active | Fix X→list bridge tweet frequency |

---

## Anti-Patterns

| Pattern | Problem |
|---------|---------|
| Building list before Gumroad | No product to sell = list decays |
| Posting daily newsletter | Unsustainable; subscriber fatigue |
| Using platform name as newsletter name | Brand lock-in; hard to migrate |
| Skipping welcome email | First impression sets open rate baseline |
| Not replying to replies | "Reply with one word" CTA = engagement signal; ignoring it = broken promise |

---

## Connections

| SOP | Role |
|-----|------|
| SOP #83 | Daily posting → content engine feeding list |
| SOP #85 | Gumroad product → list capture via G3 above |
| SOP #86 | Consulting → high-value DMs become list subscribers too |
| SOP #70 | DM conversion → offer newsletter as fallback when DM doesn't convert |

*Timestamp: 2026-04-09T10:36Z | SOP #87 of Edward's Knowledge Product Series*
