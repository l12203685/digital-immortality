# SOP #63 — Zero-to-Revenue 90-Day Activation Protocol

> UTC: 2026-04-09 | Domain: 1 (經濟自給) + 7 (知識輸出)
> Backing MDs: MD-111/166/319/321/1/141

---

## The Core Problem

Trading is live. 62 decision protocols are written. Workbooks are ready to sell. Revenue = $0.

Building is not activating. The gap between "infrastructure complete" and "revenue flowing" is not a content problem, not a product problem, and not a timing problem. It is a sequencing problem. This SOP defines the exact 90-day activation sequence — gated, auditable, with kill conditions at every step.

Deadline: 2026-07-07 (89 days from protocol date).

---

## Gates

### G0 — Revenue Gap Audit

Compute monthly API cost baseline vs current MRR. Classify current state:

| State | Definition | Condition |
|-------|-----------|-----------|
| PRE_LAUNCH | No revenue stream activated | MRR = $0, no mainnet key, no content posted |
| SEEDING | Content live, no conversions yet | MRR = $0, content posted, DMs < 10 |
| MONETIZING | First revenue received, not break-even | MRR > $0, MRR < API cost |
| SUSTAINABLE | Revenue covers API cost × 1.5+ | MRR ≥ API cost × 1.5 |

**Kill condition if skipped**: no baseline = no kill condition = no urgency = no activation. Run G0 before any other gate.

### G1 — Mainnet Activation Gate

Before any content work: infrastructure must be live.

Check all three:
- [ ] `BINANCE_MAINNET_KEY` set in environment
- [ ] Paper-to-live P&L delta > 0 (at least one forward-tested tick positive)
- [ ] Kill conditions documented (`docs/mainnet_activation_guide.md` §Kill Switches)

**If any box unchecked**: execute `docs/mainnet_activation_guide.md` now. Estimated: 30 min. Do not proceed to G2 until all three are checked.

Rationale: content seeding drives DMs. DMs convert to workbook sales. Workbook sales depend on credibility signal from live trading. Dead infrastructure = no credibility signal.

### G2 — Content Seeding Gate (Launch Day)

Three actions define "launch day." All three required, same day:

1. **X post**: publish SOP #01 thread (`docs/publish_thread_sop01_twitter.md`). Estimated: 15 min.
2. **Discord**: paste 4 seed posts (`docs/discord_seed_*.md`) → invite Organism C.
3. **Samuel async DM**: paste `docs/samuel_async_calibration_dm.md` via WhatsApp/LINE.

These three actions = the network seeding event. They are not independent — run as a batch or not at all. Partial seeding resets the DM clock without the compound.

**Gate rule**: do not list Gumroad workbooks before G2 complete. Premature listing with no audience = zero conversion + no signal.

### G3 — Signal Monitor (Weekly, Every Sunday)

Track three signals post-launch:

| Signal | Target | Trigger |
|--------|--------|---------|
| Followers delta (week-over-week) | +5 minimum | If flat ×2 weeks → change hook |
| DMs received (cumulative) | ≥10 by day 30 | If ≥10 → list Workbook #01 ($29) immediately |
| Gumroad page clicks | any | If clicks > 0 but zero purchases → audit price, not product |

**DM ≥10 trigger**: list Gumroad Workbook #01 at $29 within 24 hours of hitting threshold. No further validation needed. The 10 DMs ARE the validation.

**DM = 0 after 30 days**: content hypothesis wrong. Do not post more of the same content. Execute: repost SOP #10 (Decision-Making) with a different hook angle. Wait 14 days. Reassess. See SOP #12 G2 for gap detection protocol.

### G4 — Revenue Kill Conditions

Assess on Day 90:

**If total revenue < (API_cost × 1.5):**
Emergency protocol activated. In order:
1. Pause all SOP production immediately.
2. Identify one person in existing network who has paid for advice, consulting, or information in the past.
3. Send one direct pitch for a single paid engagement. Target: $50 minimum, paid in advance.
4. Do not resume SOP production until that payment clears.

**If total revenue ≥ (API_cost × 1.5):**
Proceed to G5 reinvestment rule.

### G5 — Reinvestment Rule

| Revenue Band | Reinvestment | Reserve |
|-------------|-------------|---------|
| First $100 | 100% → audience growth (ads or tools) | 0% |
| $101–$500 | 70% → audience growth | 30% reserve |
| >$500/month | 50% → audience growth | 50% reserve |

Audience growth = paid X promotion, email list tooling, or Discord growth. Not more content production. Content is already sufficient at SOP #62. Distribution is the constraint.

---

## Decision Label

`ACTIVATE_REVENUE_PATH_NOW`

---

## Self-Test

**Situation**: Day 45. 0 DMs. 12 followers. G3 weekly check.

Apply gates:

- G0: State = SEEDING (content posted, MRR = $0, DMs = 0)
- G1: Mainnet credentials confirmed (done at launch)
- G2: Launch day executed (SOP #01 posted, Discord seeded, Samuel DM sent)
- G3: DMs = 0 at day 45 → threshold was day 30 → content hypothesis wrong
- Action: do NOT post more SOPs with the same hook. Repost SOP #10 (Decision-Making framework) with new hook angle. Wait 14 days. Track DM delta.
- G4: Not yet triggered (day 45 of 90). Continue monitoring.

**Output**: `ACTIVATE_REVENUE_PATH_NOW` → change hook, repost SOP #10, set day 59 reassessment checkpoint. Not another new SOP. Not a price change. **Hook change.**

---

## DNA Connections

| MD | Principle | Gate |
|----|-----------|------|
| MD-111 | 穩定收入=認知資源先決 — stable income is a prerequisite for sustained cognitive output | G0 |
| MD-166 | 財務自由三層框架 — three-tier financial freedom: cover costs → 3× buffer → compound | G4/G5 |
| MD-319 | 輸出=缺口偵測器 — output is a gap detector; zero DMs = wrong hook, not wrong product | G3 |
| MD-321 | SOP→teachable document — formalized decisions become sellable knowledge products | G2 |
| MD-1 | 看導數不看水平 — track change rate (follower delta, DM velocity), not absolute level | G3 |
| MD-141 | 資訊不對稱決定方向 — act where edge exists; consulting pitch = edge play when content fails | G4 |

---

## Integration

- SOP #61 (Agent Economic Sustainability): upstream framework; G0 here maps to G1/T0 there
- SOP #34 (Knowledge Monetization): G3 DM threshold and Gumroad listing mechanics
- SOP #12 (Gap Detection): hook-change protocol when DM signal fails at day 30
- SOP #62 (Social Capital): G2 launch day actions (Samuel DM, Discord seeding, Organism C)
- `docs/mainnet_activation_guide.md`: G1 execution guide (30 min, 6 steps)
- `docs/x_launch_sequence.md`: G2 X posting protocol

---

## 90-Day Checkpoint Map

| Day | Gate | Required State | If Not Met |
|-----|------|---------------|-----------|
| 0 | G0 + G1 | Mainnet live, state classified | Stop. Do G1 first. |
| 1 | G2 | Launch day executed (X + Discord + Samuel) | Block G3 entirely. |
| 7 | G3 first check | Followers delta tracked, DM count recorded | Record zeros. Continue. |
| 30 | G3 critical check | DMs ≥10 OR hook change triggered | DMs=0 → change hook now. |
| 45 | G3 mid-check | New hook posted (if triggered), DM delta measured | If no change made → G4 risk. |
| 60 | G3/G4 pre-check | Any revenue received? | If $0: prepare consulting pitch. |
| 90 | G4 kill check | Revenue ≥ API cost × 1.5? | Emergency protocol: consulting pitch. |

*The 90-day window is not a planning horizon — it is a survival window. Every day without revenue is a day closer to G4 emergency protocol.*
