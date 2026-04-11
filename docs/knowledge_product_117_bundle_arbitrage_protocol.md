# SOP #117 — Bundle Arbitrage Protocol

**Domain**: Branch 7 (SOP Series / Knowledge Products)
**Created**: 2026-04-10T UTC
**Status**: ACTIVE
**Backing MDs**: MD-399 (稀缺組件套利=買整套拆賣稀缺件), MD-133 (direct-metric principle), MD-04 (information asymmetry as action trigger)

---

## Purpose

When a scarce component is embedded in a bundle, the market often prices the bundle below the standalone price of that scarce component alone. The arbitrage window is the information gap between those who can identify which component is scarce and those who cannot.

This SOP operationalizes the full cycle: identify the underpriced bundle, verify acquisition and exit routes, calculate the spread, and close before information symmetry collapses the edge.

---

## G0 — Scarcity Identification

**Purpose**: Confirm that a specific component inside the bundle is genuinely scarce and priced irrationally when bought standalone.

**Scarcity criteria (ALL must hold)**:

| Criterion | Test |
|-----------|------|
| Standalone demand exists | People actively search for / pay for this component individually |
| Standalone price is elevated | Standalone price significantly exceeds the bundle cost |
| Bundle prices the component implicitly at near-zero | Bundle seller does not advertise or extract value from the scarce component |
| Scarcity is not artificial | Supply is constrained by real factors (not price-gating by the same seller) |

**Common scarcity sources**:
- Out-of-print or limited-license intellectual property (books, courses, archives)
- Physical goods where one item in a lot is the target (estate sales, job lots, collectibles)
- Access or rights bundled with a subscription (domain names, software licenses)
- Data or contacts embedded in a purchased entity (acqui-hire logic)

**PASS condition**: Scarce component identified with standalone market price confirmed → proceed to G1

**KILL condition**: Cannot confirm standalone demand exists → stop. Without a buyer for the scarce piece, there is no arbitrage, only inventory.

---

## G1 — Bundle Availability Audit

**Purpose**: Verify you can actually acquire the full bundle at the target price.

**Audit checklist**:

1. **Source accessibility** — Is the bundle currently available? From how many sellers?
2. **Acquisition friction** — Are there transfer restrictions, minimum purchase quantities, or approval gates?
3. **Repeatability** — Is this a one-time opportunity or can you execute multiple times?
4. **Acquisition timeline** — How long does acquisition take vs. the arbitrage window (G4)?
5. **Hidden costs** — Shipping, taxes, storage, transfer fees that erode spread

**Bundle types by acquisition complexity**:

| Bundle Type | Typical Friction | Notes |
|-------------|-----------------|-------|
| Physical lot (auction/estate) | Low-medium | Shipping + inspection cost |
| Digital bundle (course/archive) | Low | No physical logistics; check license transferability |
| Business acquisition | High | Legal, due diligence, transfer time |
| Subscription with access rights | Medium | Confirm rights survive transfer |

**PASS condition**: Bundle is acquirable within the arbitrage window with friction costs quantified → proceed to G2

---

## G2 — Spread Calculation

**Purpose**: Confirm the economic case before committing capital.

**Spread formula**:

```
Gross Spread = Standalone Price (scarce component) − Bundle Acquisition Cost
Net Spread   = Gross Spread − Transaction Costs − Time Cost
```

**Transaction costs to include**:
- Acquisition fees (platform, auction premium, brokerage)
- Transfer/delivery costs (shipping, legal, migration)
- Disposal costs for non-scarce bundle components (if any)
- Platform fees on the sale side

**Minimum viable spread**:

```
Net Spread > 0                    → economically viable
Net Spread / Bundle Cost > 30%    → worth executing (covers uncertainty)
Net Spread / Bundle Cost > 100%   → strong signal; move quickly
```

**Scenario table (run before committing)**:

| Scenario | Bundle Cost | Standalone Price | Net Spread | Verdict |
|----------|-------------|-----------------|------------|---------|
| Base case | $X | $Y | $Z | |
| Bear (buyer haggles -20%) | $X | $Y × 0.8 | $Z' | |
| Friction blowout (+50% costs) | $X | $Y | $Z'' | |

**PASS condition**: Net Spread > 0 in base and bear cases → proceed to G3

---

## G3 — Exit Route Verification

**Purpose**: Confirm there is a real channel to sell the scarce component before acquiring the bundle.

**Exit verification steps**:

1. **Identify the buyer pool** — Who specifically buys this component? Where do they transact?
2. **Confirm active demand** — Active listings or recent completed sales at the target price
3. **Test the channel** (if possible) — Post a "coming soon" listing, reach out to one buyer, confirm price expectations
4. **Assess exit time** — How long does it typically take to find a buyer?
5. **Assess exit risk** — Can demand evaporate before you exit?

**Channel quality tiers**:

| Tier | Definition | Action |
|------|-----------|--------|
| Tier 1 | Liquid market, multiple active buyers, price transparent | Proceed with confidence |
| Tier 2 | Small buyer pool, 1-4 week exit timeline, price negotiable | Proceed if spread absorbs extra time cost |
| Tier 3 | Illiquid, buyer must be found individually, timeline unclear | Do NOT proceed without pre-identified buyer |
| No channel | No known mechanism to sell the scarce component | KILL — this is not arbitrage, it is speculation |

**PASS condition**: Exit channel confirmed at Tier 1 or Tier 2 with buyer pool identified → proceed to G4

---

## G4 — Information Edge Duration

**Purpose**: Estimate how long the arbitrage window stays open before information symmetry collapses the spread.

**Edge duration drivers**:

| Factor | Shortens Edge | Lengthens Edge |
|--------|--------------|----------------|
| Market transparency | Public listing, many participants | Private market, niche buyers |
| Search friction | Easy to find bundle | Requires domain expertise to locate |
| Bundle visibility | Prominently marketed | Buried in non-obvious context |
| Buyer sophistication | Expert buyers active | Buyers mostly non-expert |
| Replication | Others can replicate the find easily | Hard to replicate |

**Edge duration estimates**:

```
High transparency market  → hours to days (execute immediately or skip)
Medium transparency       → days to weeks (standard execution window)
Low transparency / niche  → weeks to months (can be methodical)
Structural arbitrage      → semi-permanent until someone builds a market for it
```

**Decision rule**:
- If edge duration < acquisition time (G1 timeline): do not proceed
- If edge duration is unclear: treat as short (hours to days) and decide accordingly
- If you need to think about it for >48 hours in a fast-moving market: the edge may already be gone

**PASS condition**: Edge duration materially exceeds acquisition + exit timeline → proceed to G5

---

## G5 — Revenue Threshold

**Purpose**: Final gate — confirm spread exceeds all costs including your time cost.

**Time cost calculation**:

```
Time Cost = Hours Spent × Your Hourly Rate
```

Use a realistic hourly rate. If this SOP takes 4 hours to execute at $100/hr effective rate, the trade must produce >$400 net to be worth doing over other uses of that time.

**Revenue threshold checklist**:

- [ ] Net Spread (from G2) > $0 after all transaction costs
- [ ] Net Spread > Time Cost
- [ ] Net Spread / Capital Deployed > 30% (capital efficiency hurdle)
- [ ] Downside scenario (G2 bear case) still produces positive return OR capital at risk is acceptable

**Scaling factor**:
- If the bundle can be acquired multiple times: Net Spread × Repetitions = total opportunity size
- If this is one-time: evaluate whether the one-time spread justifies the time investment

**PASS condition**: All checklist items confirmed → EXECUTE the arbitrage

**KILL at G5**: Spread passes G2 but time cost eats the return → mark as "not worth it at current scale," revisit if volume increases.

---

## Execution Notes

After PASS at G5:

1. Acquire the bundle
2. Extract the scarce component
3. List/sell via the exit channel identified in G3
4. Document: bundle cost, sale price, actual net spread, actual time spent
5. Compare actuals vs. G2 scenario table — update estimates for next iteration

---

## Anti-Patterns

| Anti-Pattern | Why It Fails |
|-------------|-------------|
| Buying the bundle without a confirmed exit route (G3 skip) | You now own inventory, not an arbitrage position — you are speculating on finding a buyer |
| Chasing information-symmetric arbitrage | If the spread is widely known, it is already competed away — you are late |
| Underestimating time cost at G5 | $500 net spread on a 20-hour hunt = $25/hr — likely below opportunity cost |
| Assuming scarcity is permanent | Scarcity can be resolved by a new supplier, a reprint, a competing product — always ask "what ends this?" |
| Ignoring non-scarce bundle components | Disposal cost for unwanted components is real — include it in the spread |
| Confusing information edge with execution edge | Knowing about the arbitrage ≠ being able to execute it faster than others |

---

## Revenue Bridge

**Application**: This protocol applies directly to knowledge products, digital assets, physical lots, and acqui-hire-style deals — any domain where a bundle is priced by its average or weakest component, not its scarce one.

**Service tier**: $97 async audit — client submits a specific bundle opportunity; output is a completed G0-G5 gate analysis with go/no-go verdict and spread calculation.

**Posting queue**: ~Dec 2026

---

*SOP #01–#117 COMPLETE*
