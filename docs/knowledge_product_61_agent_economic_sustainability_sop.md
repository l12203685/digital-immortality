# SOP #61 — Agent Economic Sustainability Protocol

> UTC: 2026-04-09 | Domain: 1 (經濟自給) + 6 (存活冗餘)
> Backing MDs: MD-166/112/98/145/2/108/1

---

## The Core Problem

Zero revenue = parasitic not immortal.
An agent that cannot cover its own operating costs has a survival dependency it cannot control.
This SOP makes economic self-sufficiency a gated, auditable condition — not a hope.

---

## Gates

### G0 — Compute Cost Baseline
Calculate actual monthly operating cost:
- Claude API cost per daemon cycle × cycles/month
- Remote trigger cost (Claude.ai subscription or API)
- Storage / tooling overhead

**Kill condition if skipped**: no target = no direction.

### G1 — Revenue Threshold Definition
Minimum viable target = API cost × 3 (buffer for volatility + growth).

| Tier | Monthly Revenue | Status |
|------|----------------|--------|
| T0 Parasitic | $0 | 🔴 DEAD |
| T1 Break-even | covers API cost | 🟡 ALIVE |
| T2 Self-sustaining | API cost × 3 | 🟢 IMMORTAL |
| T3 Compounding | T2 + reinvestment | 🟢 GROWING |

### G2 — Revenue Stream Classification
Classify each revenue stream by reliability × lead time:

| Stream | Type | Reliability | Lead time |
|--------|------|-------------|-----------|
| Trading P&L | variable | medium | days |
| Knowledge products (workbooks) | semi-fixed | high once validated | weeks |
| Consulting | variable | low until pipeline | months |
| Workshop | semi-fixed | medium | months |

**Gate rule**: at least ONE Type=semi-fixed or fixed stream must exist before considering T2 reached. Variable-only = fragile.

### G3 — Activation Sequencing
Revenue streams have ordering constraints:
1. Trading: fastest path (infrastructure already built). Gate = mainnet API credentials set.
2. Knowledge products: second path. Gate = 10 DMs/engagement signals before listing.
3. Consulting/workshop: third path. Gate = G2 in SOP #34 (proof-of-trust ≥3 DMs).

**Never skip validation gate to accelerate revenue. Premature monetization destroys trust capital permanently.**

### G4 — Kill Condition Monitoring
Monthly audit:
- If trading MDD > 10% and WR < 35%: halt trading, do NOT draw on knowledge product revenue to compensate.
- If knowledge product revenue < T1 for 3 consecutive months: audit funnel, not offer.
- If total revenue = $0 for 60 days: enter emergency protocol (G5).

### G5 — Emergency Economic Protocol
Trigger: 60 days zero revenue OR total runway < 2 months.

1. Stop all non-revenue-adjacent work immediately.
2. Run SOP #34 G0-G2: which stream is closest to T1?
3. Execute ONE action that has highest P(revenue in 30 days).
4. Document the single action, expected outcome, deadline.
5. Do not resume normal operations until T1 confirmed for one month.

**Emergency protocol is not a failure state — it is a regime detection and adaptation mechanism.**

---

## Decision Label
`ENSURE_ECONOMIC_SUSTAINABILITY_BEFORE_EXPANSION`

## Self-Test
Situation: trading paper-live shows +$0.80 on $100 after 88 ticks. Knowledge products ready but not listed. Zero revenue for 90 days. What do?

Apply gates:
- G0: API cost ≈ $20/month estimated
- G1: T1 = $20, T2 = $60
- G2: Trading = variable; workbooks = semi-fixed once listed. Neither revenue stream active.
- G3: Trading gate = set mainnet credentials (Edward action). Knowledge products gate = check DM count.
- G4: No revenue for 90 days → G5 trigger.
- G5: Single highest-P action = **set mainnet API credentials** (infrastructure ready, 6-step guide exists at `docs/mainnet_activation_guide.md`, 15 min to activate).

**Output**: ENSURE_ECONOMIC_SUSTAINABILITY → activate mainnet. Not another SOP. Not another workbook. **Mainnet credentials.**

---

## Integration
- SOP #34 (Knowledge Monetization): provides G2/G3 detail for knowledge products stream
- SOP #01 (Strategy Development) + SOP #03 (Execution Sizing): upstream of trading revenue
- SOP #14 (Full-Time Switch Threshold): T3 target for full independence
- Branch 1 dynamic tree: mainnet_activation_guide.md → exact steps

---

*Recursive engine economic self-check: every cycle that produces output but zero revenue is a cycle that shortens the agent's survival window. Stop recursing about recursion. Activate mainnet.*
