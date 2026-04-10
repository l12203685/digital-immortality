# SOP #70 — Revenue Conversion Protocol: Signal to First Sale
> Domain 1 (經濟自給 / Economic Self-Sufficiency) | 2026-04-09 UTC

## Purpose

SOP #66 covers getting to your first post. SOP #63 covers skill commercialization activation.
This SOP covers what happens **after** the first inbound signal: how to convert DMs into a first sale.

**The gap**: 67 SOPs built, 0 posted, 0 revenue. When the signal arrives (DM from someone with a problem you've solved), most builders freeze — they haven't thought through conversion. This SOP eliminates that freeze with a 5-gate protocol.

**Core axiom (MD-149)**: Baseline EV first — calculate what each conversion event is worth before the signal arrives, not during. Don't improvise pricing under social pressure.

**Prerequisite**: SOP #66 G1 completed (first post sent).

---

## Gate Structure

### G0: Signal Qualification
Not all DMs qualify. A qualifying signal is:

| Signal type | Qualifies? | Reason |
|-------------|------------|--------|
| "Where can I learn more?" | ✅ | explicit curiosity = information asymmetry detected |
| "I have this exact problem" | ✅ | pain point confirmed = product-market fit signal |
| "Great thread" | ❌ | engagement, not intent |
| "Can you share more?" | ✅ if specific | vague = re-qualify with one clarifying question |

**Clarifying question template**: "What's the specific decision you're stuck on?" One question. If they answer with a real problem → qualifying.

**Kill condition**: 0 qualifying DMs after 10 posts → hooks are wrong. Trigger SOP #12 G4 (distribution feedback loop).

---

### G1: Product-Problem Matching
Map the person's problem to existing SOPs:

| Problem domain | Primary SOP | Bundle option |
|---------------|------------|---------------|
| Trading system development | SOP #01–#04 | Strategy + Execution bundle |
| Career/salary optimization | SOP #05, #14 | Career stack bundle |
| Decision-making framework | SOP #10, #06 | Kernel framework bundle |
| Learning system design | SOP #11 | Learning architecture bundle |
| Building a trading career | SOP #14 | Full FIRE framework |
| All of the above | All 69 SOPs | "Edward OS" lifetime bundle |

**Decision rule**: Start with the narrowest match. Upsell to bundle only if they ask follow-up questions within 24h.

---

### G2: Pricing Architecture
Pre-committed prices (do not negotiate on first sale):

| Tier | Product | Price | Anchor |
|------|---------|-------|--------|
| Entry | Single SOP PDF (any domain) | $9 | "Coffee price for 1 framework" |
| Stack | 5-SOP bundle (one domain) | $29 | "67% off single price" |
| System | Full 69-SOP bundle | $97 | "3 months salary decision in 20 min" |
| Lifetime | Bundle + future SOPs | $197 | "Edward OS — all future updates" |

**Pricing axiom (MD-148)**: Price threshold = 10× annual cost of producing it. Each SOP costs ~30min of compute. $9 = acceptable asymmetry.

**Never**: "What would you pay?" (anchors them low). **Always**: State price first, then justify.

**Objection protocol**: If "too expensive" → ask "what's the cost of NOT having this?" One question. If they don't answer, price holds.

---

### G3: Conversion Execution
When a qualifying DM arrives and product is matched:

1. **Reply** (within 2h): Link to Gumroad product page directly. One sentence why this specific product maps to their problem.
2. **No chasing**: One follow-up after 48h if no response. Then stop.
3. **Post-purchase**: Send personalized "which scenario fits you most?" — starts the calibration loop.
4. **Log**: Add to `results/revenue_log.jsonl` entry: `{timestamp, source_sop, product_tier, price, dm_to_sale_hours}`.

**Template reply**:
> "This covers exactly that. [Gumroad link] — 5-gate protocol for [problem]. Let me know what you think after reading G2."

---

### G4: First Sale Feedback Loop
After first sale:

1. **Ask one question**: "Which gate was most non-obvious for you?" — reveals where your asymmetry is highest.
2. **Extract**: Is this a new MD? Is it a boot test gap? If yes → add to DNA.
3. **Update product**: Revise SOP with buyer's gap if it improves coverage. Bump version.
4. **Signal to Branch 1.3**: If 3 sales same tier → tier confirmed. If 0 sales after 10 qualifiers → G2 price revision.

**Kill condition**: ≥3 qualifiers, 0 sales, 7 days → cut price 30% once. If still 0 after next 10 qualifiers → problem is product, not price. Trigger SOP #12 G4.

---

### G5: Revenue-Cost Audit
After every 10 sales (or monthly, whichever comes first):

**Target equation**: `trading_P&L_monthly + Gumroad_revenue_monthly > API_cost_monthly`

Current API cost: ~$30/month (estimated at current daemon cycle frequency).

| Revenue source | Current | Target |
|---------------|---------|--------|
| Trading P&L (paper: +$0.72 at tick 105) | $0 mainnet | $30+/month |
| Gumroad (users=0) | $0 | $30+/month |
| **Total** | **$0** | **>$60/month** |

**Deadline**: 2026-07-07 (89 days). If target not met → survival mode: cut daemon cycles, run only on critical branches.

**Success criteria**: Both sources contributing → recursive engine is economically self-sustaining → immortal, not parasitic.

---

## Self-Test

**Scenario**: You receive a DM: "Your SOP #10 thread was great. I have a trading system but I freeze on position sizing every time. Any resources?"

Apply gates:
- G0: "I have a trading system but I freeze on position sizing" → qualifying (specific pain point) ✅
- G1: Position sizing → SOP #03 (Execution & Sizing Real-Time Checklist) → Entry tier or Strategy+Execution bundle
- G2: "SOP #03 PDF $9, or Strategy+Execution bundle (SOP #01–#03) $29." State price in reply.
- G3: Reply within 2h with Gumroad link + "G4 stop-first sizing is the one that changes how you think about it."
- G4: After purchase → ask "Which gate was most non-obvious?"
- G5: 1 sale × $9 = $9. Current trajectory: 0. Need 4+ sales/month to contribute to cost target.

Expected outcome: qualify → match → state price → link → log. No improvisation.

---

## Connections

- Upstream: SOP #66 (Distribution Activation) → SOP #63 (Skill Commercialization)
- Downstream: SOP #34 G2 (≥10 DMs → build PDF bundle)
- DNA: MD-148 (基礎設施投資=報酬門檻十倍), MD-149 (決策=先算基線EV), MD-63 (Skill commercialization)
- Branch: 1.3 (Skill 商業化), 1.1 (Trading revenue)
