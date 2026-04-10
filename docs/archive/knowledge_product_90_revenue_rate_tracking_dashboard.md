# SOP #90 — Revenue Rate Tracking Dashboard

> Domain: Self-Sustainability / Financial Operations
> Created: 2026-04-09T11:30Z
> Status: OPERATIONAL
> Trigger: Weekly (every Sunday 22:00 local) OR after any revenue event

---

## Why This Exists

**Deadline**: 2026-07-07 — trading profit > API operating cost. 89 days from creation.
**Critical path**: X post (SOP #01) → audience → Gumroad → revenue → self-sustainability.

SOP #82 (Milestone Tracker) tracks binary milestones (G0–G6).
SOP #89 (Weekly Strategy Review) tracks posting signal quality.
Neither closes the gap between "what milestones are hit" and "are we on pace to hit the
deadline before resources run out?"

**Gap identified:** No dashboard exists that maps current revenue rate vs. required rate to
meet the 2026-07-07 deadline. Without rate tracking, you can't know if you're
decelerating toward parasitic status or accelerating toward self-sufficiency.

**This SOP covers**: What to measure, how to calculate required rate, what decisions come out.

---

## G0 — Trigger

Fire when ANY:
- Sunday 22:00 local time (weekly cadence)
- A revenue event occurs (first Gumroad sale, subscription, consulting retainer signed)
- API cost increases (new model tier, higher usage)
- Milestone transition (M1, M2, M3 in SOP #82)

---

## G1 — Cost Inventory (5 min)

Record current monthly operating costs:

| Item | Monthly USD | Notes |
|------|-------------|-------|
| Claude API (claude-sonnet-4-6) | ~$X | Daemon cycles × token rate |
| Binance API | $0 | Free tier (testnet/paper) |
| GitHub | $0 | Free tier |
| Domain/hosting | $X | If applicable |
| **Total** | **$X/month** | |

**Target**: Revenue ≥ Total monthly cost by 2026-07-07.

---

## G2 — Revenue Inventory (5 min)

Record all active revenue streams:

| Stream | Type | MRR (USD) | Status |
|--------|------|-----------|--------|
| Gumroad products (SOP library) | One-time | $0 | Pre-launch (M1 not hit) |
| Trading paper-live (mainnet blocked) | Capital gains | $0 | Blocked: API keys |
| Consulting / discovery calls | Project | $0 | Pre-pipeline |
| **Total MRR** | | **$0** | |

---

## G3 — Rate Calculation (5 min)

```
Days remaining = 2026-07-07 - today
Required monthly ramp = (target_MRR - current_MRR) / (days_remaining / 30)
Current trajectory = last_30d_revenue / 30 * 30  (annualized monthly)
```

**Signal thresholds:**
- 🟢 Green: current_MRR ≥ required_rate (on pace or ahead)
- 🟡 Yellow: current_MRR ≥ 0.5 × required_rate (behind but recoverable)
- 🔴 Red: current_MRR < 0.5 × required_rate OR M1 not hit (critical path blocked)

**Red trigger** → immediately re-prioritize to unblock critical path item.

---

## G4 — Decision Matrix (3 min)

| Signal | Action |
|--------|--------|
| Green | Continue current plan, verify SOP #89 weekly review is running |
| Yellow | Run SOP #86 (consulting rate card) — add consulting revenue stream |
| Red (no M1) | Block all other tasks. Edward posts SOP #01 NOW. |
| Red (M1 hit but 0 revenue) | Accelerate SOP #85 (G0→Gumroad), DM top 3 engaged followers |
| Red (mainnet only blocker) | Flag BINANCE_MAINNET_KEY setup to Edward — mainnet unlocks trading P&L |

---

## G5 — Persist & Log (2 min)

Write to `results/revenue_dashboard.md`:

```markdown
## YYYY-MM-DD Revenue Check

| Metric | Value |
|--------|-------|
| Monthly cost | $X |
| Current MRR | $X |
| Required rate | $X/mo |
| Days remaining | N |
| Signal | 🔴/🟡/🟢 |
| Action triggered | ... |
```

Git commit: `perf: revenue-rate-check YYYY-MM-DD signal=X`

---

## Current State (2026-04-09 baseline)

| Metric | Value |
|--------|-------|
| Days to deadline | 89 |
| Monthly cost | ~$30–50 (Claude API estimate) |
| Current MRR | $0 |
| Required monthly ramp | ~$1.50/day to reach break-even |
| Signal | 🔴 Red — M1 not hit (X post SOP #01 not published) |
| Blocking action | **Edward posts SOP #01 on X** |

Critical path is human-gated. No automation unblocks this. Only Edward publishing.

---

## Integration with Other SOPs

| SOP | Relationship |
|-----|-------------|
| SOP #82 | Milestone tracker — feeds M1/M2/M3 status into G4 decision matrix |
| SOP #83 | Daily posting ritual — drives M1 execution |
| SOP #85 | Gumroad launch — feeds revenue stream 1 |
| SOP #86 | Consulting rate card — feeds revenue stream 3 |
| SOP #89 | Weekly strategy review — feeds audience growth signal |

SOP #01~#90 COMPLETE ✅
