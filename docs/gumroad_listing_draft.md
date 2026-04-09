# Gumroad Listing Draft — Workbook Trilogy
> TRIGGER: List when ≥10 DMs received on any Twitter thread.
> Run `python platform/daily_posting_helper.py --status` to check DM count.
> 2026-04-09 UTC — Ready to publish.

---

## Bundle: The Systematic Trader's Trilogy
**Price: $67** (vs $87 individual, 23% off)
**Gumroad URL slug**: `systematic-trader-trilogy`

### Bundle Title
The Systematic Trader's Trilogy — Strategy Development, Portfolio Construction, and Execution Sizing in One Framework

### Bundle Short Description (255 chars)
Three worksheets, one end-to-end framework. Build a strategy that holds up. Combine it into a portfolio that survives. Execute every live session without guessing. Based on 9 years of trading micro-decisions.

### Bundle Long Description

Most quantitative traders fail not because they lack intelligence — but because they optimize each component in isolation.

They build a great strategy, then add it to a portfolio sized with gut feel, then execute with different rules each session.

The result: three good parts that don't add up to a working system.

This trilogy gives you the exact end-to-end framework used across 9 years of systematic trading decisions. Three workbooks. Three sequential gates. One coherent process.

**Workbook #01 — Strategy Development ($29)**
Walk through 5 irreversible gates before a strategy gets capital. Gate 0 forces you to articulate the edge in one sentence. Gate 4 pre-commits your kill conditions before you go live. Most strategies fail because they skip one of these five gates. This workbook makes skipping impossible.

**Workbook #02 — Portfolio Construction ($29)**
Three strategies that fail in the same regime is one strategy. This workbook walks through the greedy storm-ratio algorithm for combining strategies that are structurally distinct, regime-aware, and sized to survive correlated drawdowns — not just average them.

**Workbook #03 — Execution & Sizing Real-Time Checklist ($29)**
You have a strategy. You have a portfolio. Now: does your next signal actually become a correctly-sized live order — or do you wing it? Eight sequential gates, completed every session. After one week, execution becomes a zero-decision procedure.

**What's inside each workbook:**
- The principle behind each gate (with MD reference from 330+ distilled trading micro-decisions)
- A worked example (Taiwan TAIEX futures + DualMA BTC)
- A blank worksheet for your own strategy/portfolio
- Specific failure modes to avoid at each gate

**Who this is for:**
- Systematic traders running 2–15 strategies on Taiwan, US, or crypto markets
- Quant hobbyists who want to stop guessing at position sizing
- Anyone who has a backtested strategy they've never taken live because "something feels off"

**Format:** Fillable PDF + Markdown (compatible with Notion, Obsidian)

**Prerequisite:** None for Workbook #01. Workbooks #02 and #03 build on the output of #01.

---

## Individual Listings (if selling separately)

### Workbook #01 — Strategy Development
**Price: $29**
**Slug**: `strategy-development-workbook`
**Short (255 chars):** A step-by-step worksheet for the 5 gates between a real edge and a backtest illusion. Based on 9 years of trading decisions. One framework, reusable forever.
**Status**: READY TO LIST

### Workbook #02 — Portfolio Construction
**Price: $29**
**Slug**: `portfolio-construction-workbook`
**Short (255 chars):** A 5-gate worksheet for combining strategies that don't blow up together. Calmar-optimised allocation, correlation gating, regime routing. One framework, reusable forever.
**Status**: READY TO LIST

### Workbook #03 — Execution & Sizing
**Price: $29**
**Slug**: `execution-sizing-workbook`
**Short (255 chars):** Eight sequential gates you complete every live session. After one week, execution becomes a zero-decision procedure. No gut feel. No miscalculations.
**Status**: READY TO LIST

---

## Gumroad Setup Steps (when trigger fires)

1. Go to gumroad.com → New Product → Digital product
2. Upload: `docs/workbook_product_01_strategy_development.md` (PDF export)
3. Set price: $29 (or $0 with "Name Your Price" floor of $1 for lead gen — decide based on DM quality)
4. Title + description: paste from above
5. Repeat for workbooks #02 and #03
6. Create Bundle: add all three, price $67
7. Enable affiliate program (20% commission — incentivizes sharing in quant communities)
8. Post purchase link as reply to the SOP #01 thread that generated ≥10 DMs
9. Log the date in `docs/posting_queue.md` Signal Log under "Action" column

---

## Pricing Decision Framework

| Signal | Action |
|--------|--------|
| 0–2 DMs after first 5 SOPs | Check hook quality; rewrite lowest-performing hook |
| 3–9 DMs total | Continue posting; do NOT list yet (dilutes urgency) |
| ≥10 DMs from any single thread | List immediately; DM those who messaged with purchase link |
| ≥10 DMs but low saves (<5) | List at $0 name-your-price for lead gen; upsell bundle |
| Quant community DM (high quality) | List at $29; reply directly with sample pages |

---

## Revenue Projection

| Scenario | Buyers | Revenue |
|----------|--------|---------|
| Conservative (1% DM→buy rate, 100 DMs) | 1 | $67 |
| Moderate (5% rate, 300 DMs) | 15 | $1,005 |
| Target (10% rate, 500 DMs) | 50 | $3,350 |
| Stretch (viral thread, 2000 DMs) | 100 | $6,700 |

Monthly self-sustainability threshold: ~$500/month (covers operating costs).
At moderate scenario, **1 viral thread = 2 months of operating costs**.

---

*Last updated: 2026-04-09 UTC*
*Trigger condition: ≥10 DMs on any thread → list workbooks on Gumroad immediately*
*Monitor: `python platform/daily_posting_helper.py`*
