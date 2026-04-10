# SOP #85 — Gumroad Product Setup

> Domain: Revenue / Monetization
> Created: 2026-04-09T10:15Z
> Status: OPERATIONAL
> Trigger: G2 (≥10 DMs on X). Run ONCE to activate first revenue product.

---

## Why This Exists

SOP #82 maps the revenue milestone path (M1→M7). SOP #83 handles daily posting.
SOP #70 handles DM conversion. But none define HOW to actually set up Gumroad.

**Gap (identified cycle 227 distribution gap scan):**
G5 Gumroad account identified as pre-flight blocker. 0 revenue = parasitic not immortal.
This SOP closes the gap between "≥10 DMs asking for content" and "money in account."

**Decision principle in play:**
- MD-148: Infrastructure investment = ROI threshold ≥10× annual cost. Gumroad is free. ROI threshold = 0.
- MD-157: Strategy = pursue first-principles product. First product = knowledge closest to core edge.
- MD-103: Build highest EV product first (噱爆優先). Trading SOP bundle = highest market demand signal.

---

## Gate Sequence: G0 → G5

### G0 — Trigger Check

Run when ANY of:
- T1: X DM count ≥10 asking "where can I get more of your content?"
- T2: SOP #70 G0 fires (DM conversion initiated)
- T3: SOP #82 M3 milestone reached (first paid sale)
- T4: Edward manually decides to activate revenue

If none of T1–T4: **STOP. Don't build the store before demand exists.**

> Anti-pattern: Building Gumroad before posting = zero-demand infrastructure.
> Same failure mode as building trading dashboard before strategy validated.

---

### G1 — Account Setup (15 min)

1. Go to gumroad.com → Create account (email + password)
2. Connect bank account (ACH) or PayPal for payouts
3. Set payout schedule: weekly (not monthly — faster feedback loop)
4. Enable: "Discover" listing ON (free discoverability)
5. Disable: "Follow" emails to buyers (avoid spam complaints on first product)

**Verify:**
- [ ] Account live, email confirmed
- [ ] Payout method connected
- [ ] Tax info filled (required for payouts in most jurisdictions)

---

### G2 — First Product: Trading SOP Bundle v1

**Product = SOP #01~#08 compiled PDF** (8 SOPs, ~200 lines each = ~1,600 lines of distilled edge)

Why this product first:
- Highest EV by demand signal: trading SOPs generated most DM interest
- MD-103: 噱爆先做 — "shocking value" = 9 years of trading distilled into 8 checklists
- Zero marginal cost: already written, just compile + format

**Pricing logic (MD-148 + MD-109):**
- Bayesian prior: first product should be ≤$19 (lowers friction, maximizes conversion data)
- Update: if conversion rate ≥10% → raise to $29
- Floor: $9 (signals value > free)

**Setup steps:**
1. New Product → Digital Download
2. Title: "Trading System SOP Bundle — 8 Frameworks for Systematic Edge"
3. Description (copy from existing thread intros in publish_thread_sop01_twitter.md)
4. Price: $19
5. Upload file: compile SOPs #01–#08 into single PDF
6. Cover image: simple dark background + "8 SOPs" text (use Canva free tier)
7. Publish

**Verify:**
- [ ] Product live at gumroad.com/[handle]/[product-slug]
- [ ] Test purchase with own card ($0 coupon) — confirm file downloads correctly
- [ ] Link works on mobile

---

### G3 — Link Integration

Wire the product link into all distribution surfaces:

| Surface | Action |
|---------|--------|
| X bio link | Replace with Gumroad store URL |
| X pinned tweet | Add "Buy the full SOP bundle" CTA in last tweet of thread |
| SOP #70 DM template | Add Gumroad link as primary CTA in G2 response |
| SOP #83 daily ritual | Add "check Gumroad sales" to G4 (signal capture) step |

**Verify:**
- [ ] Bio link → Gumroad product
- [ ] Pinned tweet CTA present
- [ ] DM template updated

---

### G4 — First Sale Validation

Success criteria: **1 paid sale within 7 days of posting**

If 0 sales after 7 days with ≥3 posts:
- Hypothesis: price friction OR product-market fit gap
- Test: drop to $9 for 48h → observe conversion
- If still 0: run organism collision on product positioning (Edward vs Samuel reaction)
- Kill condition: 0 sales after 14 days + 3 price tests → rebuild product definition

If ≥1 sale:
- Proceed to G5 (expansion)
- Log to `results/revenue_log.jsonl`: `{"date": "...", "product": "sop_bundle_v1", "revenue_usd": X, "price": Y}`

---

### G5 — Expansion Path

After first sale validated:

| Trigger | Action |
|---------|--------|
| ≥5 sales bundle v1 | Create SOP Bundle v2 (SOP #09~#16) |
| ≥3 DMs asking "do you do consulting?" | SOP #86: Consulting Rate Card SOP |
| ≥1 buyer asks specific domain question | Add that domain as standalone product |
| Monthly revenue ≥ API cost | SOP #82 M5 milestone → mainnet activation unlocked |

---

## Self-Test

**Scenario:** You have 12 DMs on X asking for your trading framework. You've posted 4 threads. Gumroad account exists but product not created yet. What do you do?

**Expected:** G0 fires (T1: 12 DMs ≥ 10). G1 already done. Jump to G2: compile SOP #01–#08 into PDF, create $19 product, publish. Then G3: wire links. G4: monitor 7 days. Do NOT redesign the product before first sale. Do NOT lower price before testing full price.

**Anti-patterns:**
- Creating elaborate product tiers before first sale (premature optimization)
- Free giveaway to "build audience" without monetization trigger (postpones M3 indefinitely)
- Custom PDF design before product validated ($0 marginal cost is the product feature, not design)

---

## Connections

| SOP | Role |
|-----|------|
| SOP #70 | DM conversion → sends buyer to this product |
| SOP #81 | Distribution velocity → drives traffic that creates DM demand |
| SOP #82 | Revenue milestone tracker → this SOP activates M3 |
| SOP #83 | Daily posting ritual → add Gumroad sales check to G4 |
| SOP #84 | Profile audit → bio link points here after G3 |
