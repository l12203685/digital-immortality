# SOP #23 — Regime Detection & Strategy Rotation

**Tagline:** *Most traders lose not because their strategy is wrong — but because they're running the right strategy in the wrong regime.*

**Backing MDs:** MD-25 (ATR-driven rotation), MD-26 (Rolling OOS recency bias), MD-27 (reduce leverage 50% before events), MD-75 (equity curve 3-state trigger), MD-35 (strategy pool long/short audit)

---

## The Core Problem

A trend-following strategy has a positive expectancy in trending markets. The same strategy has negative expectancy in ranging markets. Most people optimize the strategy. Edward optimizes the regime classification.

**Regime first. Strategy second.**

---

## Gate 0 — Define Your Regime Taxonomy

Before any strategy runs, define 3 regimes:

| Regime | ATR Condition | Market Character | Strategy Set |
|--------|--------------|-----------------|--------------|
| **Trending** | ATR > 30-day MA | Directional, momentum | Trend-following, breakout |
| **Ranging** | ATR < 30-day MA | Oscillating, mean-reverting | Mean-reversion, range fade |
| **Event** | VIX spike or scheduled catalyst | Elevated uncertainty | Reduce size 50%, options hedge |

*Rule (MD-27): Before any scheduled event (FOMC, earnings, macro release) → reduce leverage 50% regardless of regime.*

---

## Gate 1 — ATR-Driven Rotation Signal

```
Daily ATR(14) vs 30-day rolling average of ATR(14)

If ATR_today > ATR_30d_MA:
    Regime = TRENDING
    Active strategies: trend + breakout pool
    
If ATR_today <= ATR_30d_MA:
    Regime = RANGING
    Active strategies: mean-reversion pool
```

**Why ATR, not price?** Price tells you direction. ATR tells you whether the market is *moving at all*. A strategy that needs movement to work requires ATR above baseline. (MD-25)

---

## Gate 2 — Rolling OOS Reality Check

**Problem:** Recent OOS data receives implicit higher weight in your mental model. You think the strategy "works now" because it worked last week. This is recency bias masquerading as regime adaptation. (MD-26)

**Fix:** Minimum 90-trade OOS window before declaring regime stability.

```
Regime confirmation requires:
- ATR signal consistent for ≥5 trading days
- Rolling OOS window ≥90 trades
- Sharpe stability: last 30 trades vs prior 30 trades within 20%
```

*Do NOT rotate strategy based on 1–2 days of ATR signal.*

---

## Gate 3 — Strategy Pool Long/Short Audit

Every quarter, audit your strategy pool for directional bias. (MD-35)

```
Long-only strategies in pool: N_long
Short-capable strategies in pool: N_short

Target ratio: N_short / N_total ≥ 0.3

If ratio < 0.3:
    You are structurally net-long and will lose in bear regimes
    Action: add short or hedged strategy before next regime shift
```

A portfolio that can only make money in up markets is not a trading system — it's levered beta.

---

## Gate 4 — Equity Curve 3-State Trigger

The equity curve IS your regime detector at the portfolio level. (MD-75)

| State | Condition | Action |
|-------|-----------|--------|
| **Normal** | Equity within 5% of all-time high | Full leverage, all strategies live |
| **Warning** | 5–15% drawdown from ATH | Reduce leverage 50%, pause lowest-Sharpe strategy |
| **Stop** | >15% drawdown from ATH | All strategies off, paper trade only, diagnose |

*Warning → Stop transition: requires 24h hold before executing. Prevents panic capitulation.*

---

## Gate 5 — Rotation Execution Protocol

When regime shifts (ATR crosses MA + confirmation):

1. **Do NOT close all positions immediately.** Let existing trades finish their natural exit.
2. **Stop opening new trades** in the deactivated strategy set.
3. **Activate** new strategy set for the next entry signal only.
4. **Log the rotation** with timestamp, ATR values, and current equity curve state.

Rotation is a slow process, not a switch. Regime can oscillate at boundaries. One crossover ≠ confirmed shift.

---

## Self-Test

Given:
- ATR(14) today: 28.4
- ATR 30-day MA: 31.2
- Portfolio drawdown: 8%
- Next FOMC: 3 days away

**Which state are you in?**

- Regime: **RANGING** (ATR below MA)
- Portfolio: **WARNING** state (8% drawdown)
- Event: **Reduce leverage 50%** in 3 days regardless

**Correct action:** Deactivate trend strategies now. Mean-reversion strategies only at 50% size. Prepare leverage reduction plan for FOMC day. No new trend entries until regime confirms trending.

---

## The Meta-Principle

Regime detection is not prediction. You are not forecasting the future regime — you are *measuring the current one* and running the appropriate strategy for the current environment.

**The signal is not "what will happen." The signal is "what kind of game am I currently playing."**
