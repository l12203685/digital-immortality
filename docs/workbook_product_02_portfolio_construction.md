# Workbook #02 — Portfolio Construction Framework
> Price: $29 | Based on SOP #02 + MD-100/52/53/54/13/107/75
> Prerequisite: Workbook #01 (each strategy must pass individual gates before entering the portfolio)
> Status: READY TO LIST — list on Gumroad when G2 triggers (≥10 DMs in 48h)

---

## Gumroad Listing Copy (paste-ready)

**Title:** The Portfolio Construction Workbook — Combine Strategies That Survive Together

**Short description (255 chars):**
A 5-gate worksheet for building a quantitative portfolio that doesn't blow up when one strategy fails. Calmar-optimised allocation, correlation gating, regime routing. One framework, reusable forever.

**Long description:**
Most traders who build multiple strategies make the same mistake: they add them all to a portfolio and call it diversification.

It's not. Two trend-following strategies in the same instrument are one strategy with twice the drawdown.

This workbook gives you the exact 5-gate framework for combining strategies that are structurally distinct, regime-aware, and sized to survive correlated drawdowns — not just average them away.

**What's inside:**
- Gate 0: 2×2 strategy classification grid — Trend/MR × Long/Short. Redundancy check before anything else.
- Gate 1: Pairwise Calmar computation — find your best seed pair from OOS data, not IS
- Gate 2: Greedy addition worksheet — add one strategy at a time, only if portfolio Calmar improves
- Gate 3: Correlation gate — reject any pair with rolling 30-day correlation >0.70
- Gate 4: Portfolio kill conditions — pre-committed, written before capital is deployed

Each gate includes:
- The principle behind it (with MD reference)
- A worked example (DualMA + BollingerMR BTC portfolio)
- A blank worksheet for your own strategy set
- Failure modes to avoid

**Who this is for:** Traders who have ≥2 working strategies and want to combine them without creating hidden concentration risk.

**Format:** PDF, 26 pages, instant download.

---

## Workbook Content

### Introduction (1 page)

Portfolio construction is not diversification. Diversification is the goal. Portfolio construction is the process of achieving it structurally — not by adding strategies, but by adding non-redundant edges.

The most common failure mode: a trader runs two strategies, both go into drawdown simultaneously, and they conclude "the market changed." The market didn't change. The strategies were correlated from day one.

Five gates. Each one designed to surface hidden redundancy before it surfaces in your equity curve.

---

### Gate 0: Strategy Classification Worksheet

**Principle:** MD-53 — 策略分類=多空×類型的二維最細分 (classify strategies by direction × type before combining)

**The test:** Can you place every strategy in a unique cell of the 2×2 grid?

**The grid:**

| | **Trend-following** | **Mean-reverting** |
|---|---|---|
| **Long-biased** | Trend-Long | MR-Long |
| **Short-biased** | Trend-Short | MR-Short |

**Worked example:**
- DualMA BTC → exploits momentum persistence, long-biased → **Trend-Long**
- BollingerMR BTC → exploits mean reversion after deviation, long/short → **MR** (both cells)
- Donchian BTC → breakout trend, no directional bias → **Trend-Long + Trend-Short**

**Your worksheet:**

| Strategy Name | Instrument | Direction (L/S/Both) | Type (Trend/MR) | Cell Assigned |
|---|---|---|---|---|
| | | | | |
| | | | | |
| | | | | |
| | | | | |

**Gate 0 pass condition:** ≥2 cells covered. Strategies sharing a cell need explicit justification (different instrument OR different timeframe with documented evidence of low correlation).

**Gate 0 failure modes:**
- 3 trend-following BTC strategies = 1 amplified bet, not a portfolio
- "Diversification by asset" without checking strategy type still fails this gate

---

### Gate 1: Pairwise Calmar Worksheet

**Principle:** MD-100 — 投組最佳化=遞迴兩兩最高風暴比 (portfolio optimization = recursive pairwise max Calmar ratio)

**Why Calmar (not Sharpe)?** Calmar penalises peak-to-trough drawdown. That's the metric that terminates real accounts. Sharpe averages volatility, which can mask correlated drawdowns arriving in sequence.

**Formula:**
```
Combined_Calmar(A, B) = CAGR(A+B, equal weight) / MaxDrawdown(A+B, equal weight)
```

Run this on OOS data only. Equal weight is the starting hypothesis — you are testing structural fit, not optimising allocations yet.

**Worked example:**

Using OOS data:
- DualMA alone: CAGR=18%, MDD=12% → Calmar=1.50
- BollingerMR alone: CAGR=14%, MDD=11% → Calmar=1.27
- DualMA + BollingerMR equal weight: CAGR=16%, MDD=7% → Calmar=**2.29** ✅

Combined Calmar (2.29) > both individual Calmars → structural fit confirmed. This pair becomes the seed portfolio.

**Your worksheet:**

List every candidate pair. Compute Combined_Calmar for each on OOS data:

| Strategy A | Strategy B | Combined CAGR | Combined MDD | Combined Calmar | Rank |
|---|---|---|---|---|---|
| | | | | | |
| | | | | | |
| | | | | | |

**Gate 1 pass condition:** Seed pair = highest Combined_Calmar pair. Seed Calmar must exceed both individual Calmars.

**Gate 1 failure mode:** Running Gate 1 on IS data. The pair looks great because it was optimised on the same data. OOS only.

---

### Gate 2: Greedy Addition Worksheet

**Principle:** MD-52 — 投組最佳化=遞迴兩兩最高風暴比 (add greedily — each addition must improve portfolio Calmar)

**The rule:** Add one strategy at a time. Only include it if it raises portfolio Calmar. Stop when no candidate improves the score.

**Algorithm:**
```
current_portfolio = seed pair (Gate 1 winner)
current_calmar = Gate 1 result

For each remaining candidate C:
  temp_calmar = Calmar(current_portfolio + C, equal weight, OOS)
  IF temp_calmar > current_calmar:
    ADD C to portfolio
    current_calmar = temp_calmar
  ELSE:
    REJECT C (log reason)

Hard limits:
  - Max 6–8 strategies (monitoring bandwidth cap, MD-107)
  - Min 2 cells on 2×2 grid maintained throughout
```

**Worked example:**

Seed: DualMA + BollingerMR → Calmar=2.29

Candidate 3: Donchian BTC
- DualMA + BollingerMR + Donchian (equal weight): CAGR=15%, MDD=8% → Calmar=1.88
- 1.88 < 2.29 → **REJECT** (Donchian adds trend-following redundancy with DualMA)

Candidate 4: RSI_MeanRevert ETH
- DualMA + BollingerMR + RSI_MR_ETH: CAGR=17%, MDD=6.5% → Calmar=2.62
- 2.62 > 2.29 → **ADD** ✅ (different asset, MR type, improves Calmar)

Final portfolio: DualMA + BollingerMR + RSI_MR_ETH → Calmar=2.62

**Your worksheet:**

| Candidate | Portfolio Calmar Before | Portfolio Calmar After Adding | Decision | Reason |
|---|---|---|---|---|
| | | | ADD / REJECT | |
| | | | ADD / REJECT | |
| | | | ADD / REJECT | |

**Gate 2 pass condition:** Final portfolio Calmar > seed Calmar. Max 8 strategies. Min 2 cells covered.

---

### Gate 3: Correlation Gate Worksheet

**Principle:** MD-54 — 跨Session留倉=需獨立Edge (different strategies must exploit different edges, not the same move)

**The test:** Rolling 30-day return correlation between every strategy pair must be ≤0.70.

**Why 0.70?** Above this threshold, under regime stress (when correlations spike), two strategies will experience simultaneous drawdowns. The portfolio MDD becomes additive, not averaged.

**Formula:**
```
For each pair (A, B) in final portfolio:
  corr(A, B) = Pearson correlation of daily_returns_A and daily_returns_B
               computed on rolling 30-day window
  
  IF max(corr) > 0.70 → REJECT the lower-Calmar strategy from the pair
```

**Worked example:**

Pair 1: DualMA vs BollingerMR → rolling 30d corr range: -0.15 to +0.42 → **PASS** ✅
Pair 2: DualMA vs RSI_MR_ETH → rolling 30d corr range: -0.08 to +0.38 → **PASS** ✅
Pair 3: BollingerMR vs RSI_MR_ETH → rolling 30d corr range: +0.22 to +0.61 → **PASS** (max<0.70) ✅

**Your worksheet:**

| Strategy A | Strategy B | Corr Min | Corr Max | Corr Mean | Gate 3 Status |
|---|---|---|---|---|---|
| | | | | | PASS / FAIL |
| | | | | | PASS / FAIL |
| | | | | | PASS / FAIL |

**Gate 3 failure modes:**
- Only computing average correlation (misses regime-stress spikes)
- Using IS correlation (will be lower than OOS during stress)
- Adding strategies from the same exchange in the same market session — structural correlation floor is high

---

### Gate 4: Portfolio Kill Conditions Pre-Commitment

**Principle:** MD-96 — 策略管理先定失效條件 (define failure conditions before capital is deployed)

**These are written before go-live. Not updated after losses begin.**

Three kill levels:

**Level 1 — Reduce size 50% (WARNING):**
- Portfolio equity curve crosses below 20-day MA
- Any single strategy hits its individual kill condition (suspend that strategy, not the portfolio)

**Level 2 — Pause all trading (STOP):**
- Portfolio MDD exceeds: ___% (fill in: recommended 15–20% depending on risk tolerance)
- Two or more strategies hit individual kill conditions simultaneously

**Level 3 — Full liquidation and post-mortem (SHUTDOWN):**
- Portfolio MDD exceeds: ___% (fill in: 25–30% absolute floor)
- Correlation between any pair exceeds 0.85 for >10 consecutive trading days

**Post-mortem trigger:** Any Level 2 event requires a written post-mortem before resuming. Template:
- What was the drawdown magnitude and duration?
- Were kill conditions triggered by regime shift, execution failure, or noise?
- Which strategy(ies) caused the drawdown?
- What changes, if any, are made to the kill conditions? (changes require 5 new OOS examples to validate)

**Your worksheet:**

| Kill Level | Trigger Condition | My Threshold | Pre-Committed? (sign + date) |
|---|---|---|---|
| WARNING | Portfolio equity below 20d MA | — | |
| WARNING | Single strategy hits kill | automatic | |
| STOP | Portfolio MDD | ___% | |
| STOP | ≥2 strategies hit kill simultaneously | automatic | |
| SHUTDOWN | Portfolio MDD | ___% | |
| SHUTDOWN | Pair correlation >0.85 for 10d | automatic | |

**Signed:** _____________ **Date:** _____________

**Gate 4 pass condition:** All thresholds filled in and signed before any live capital is deployed. Unsigned = not deployed.

---

### Quick Reference Card (print and keep)

**Pre-deployment checklist (5 items):**
- [ ] Gate 0: ≥2 cells covered on 2×2 grid
- [ ] Gate 1: Seed pair Calmar > both individual Calmars (OOS)
- [ ] Gate 2: Each addition improved portfolio Calmar; ≤8 strategies total
- [ ] Gate 3: All pairs rolling corr ≤0.70
- [ ] Gate 4: Kill conditions written and signed

**Live monitoring (weekly):**
- Check rolling 30d correlation for all pairs → flag if any >0.60 (approaching threshold)
- Check equity curve vs 20d MA → resize if below
- Check individual strategy survival rate = rolling Sharpe ÷ historical OOS Sharpe → suspend if <0.60

**Kill condition reminder:**
Portfolio-level kill ≠ strategy-level kill. A strategy can be suspended (individual kill) while the portfolio continues running on remaining strategies. Only deploy portfolio-level kills for systemic failures.

---

### Gumroad Setup Steps (~20 min after G2 triggers)

1. Go to gumroad.com → New Product → Digital
2. Upload: paste this document as PDF (print → save as PDF)
3. Title: paste from Listing Copy above
4. Price: $29
5. Description: paste Long Description from Listing Copy
6. Thumbnail: screenshot of Gate 0 2×2 grid (visual hook)
7. Publish → copy URL → add to X bio link-in-bio (replace or add alongside Workbook #01)

**Upsell note:** In Gumroad confirmation email, add: "If you haven't done Workbook #01 (Strategy Development), complete that first — each strategy must pass individual gates before entering a portfolio." Links both products.
