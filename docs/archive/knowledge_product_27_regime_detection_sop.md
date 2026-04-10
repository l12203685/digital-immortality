# SOP #27 — Regime Detection & Strategy Rotation

> "There is no permanently valid indicator. Determine the regime first, then select the tool." — MD-78

---

## Why This Matters

Every other SOP in this series assumes you know what regime you're in.
Position sizing (SOP #25) uses regime-conditional leverage.
Portfolio construction (SOP #24) routes allocation by regime.
Walk-forward validation (SOP #26) tests regime-by-regime OOS stability.
Strategy kill decisions (SOP #04) check regime-match before pulling the plug.

If regime detection fails, every downstream SOP runs on a corrupted input.
This is the root gate.

---

## The 3-State Framework (MD-105)

Markets exist in three states — no strategy dominates all three:

| State | Structure | Who wins |
|-------|-----------|----------|
| **Trend** (剪刀) | Directional, momentum | Trend-following |
| **Ranging-Divergent** (石頭) | Wide swings, oscillating | Breakout + mean-reversion boundaries |
| **Ranging-Convergent** (布) | Tight, compressing | Mean-reversion, volatility selling |

Strategic goal: hold ≥1 strategy per state. Any 2-state overlap = concentration risk.
Audit question: "On which day would all my strategies lose money simultaneously?"

---

## Gate 0 — Label the Current Regime Before Any Decision

**Tool: ATR percentile (MD-25)**

```
ATR_now = 20-day ATR on primary instrument
ATR_pct = percentile rank of ATR_now vs trailing 252 days

ATR_pct > 70%  → HIGH volatility regime  → trend-following window
ATR_pct 30–70% → NORMAL regime           → mixed, balanced sizing
ATR_pct < 30%  → LOW volatility regime   → mean-reversion / compression plays
```

**Validation:** Annual storm ratio (yearly P&L / max-drawdown) — if this year's ratio drops >30% below historical mean, the regime has structurally shifted. Recalibrate all leverage thresholds. "Feels hard" is NOT a trigger. The number is. (MD-107)

---

## Gate 1 — Strategy–Regime Match Check

Before entering any trade, confirm the active strategy matches the current regime:

```
IF regime = HIGH volatility AND strategy_type = mean_reversion:
    → HOLD. Wrong regime. Accept small P&L. Do not force. (MD-14)

IF regime = LOW volatility AND strategy_type = trend_following:
    → HOLD. Tail-risk: trend strategies bleed in compression. Minimize size. (MD-33)

IF regime = NORMAL:
    → Run mixed pool at standard sizing
```

Rationale: Adding leverage without a regime signal amplifies noise, not alpha (MD-31).

---

## Gate 2 — Leverage = f(Regime) (MD-32)

Optimal leverage is not fixed — it is a regime function:

| Regime | Leverage multiplier |
|--------|---------------------|
| HIGH (trend confirmed) | 1.0× → 1.5× baseline |
| NORMAL | 1.0× baseline |
| LOW (compression) | 0.5× → 0.8× baseline |

**Equity curve override (MD-75):** If equity curve drops below 1.5σ Bollinger band regardless of ATR regime → force to equal-weight leverage. Resume full sizing only after equity curve re-crosses above band. The equity curve knows something ATR doesn't.

---

## Gate 3 — Strategy Rotation Trigger

Rotation is triggered by regime change, not by strategy P&L alone:

```
Rotation condition:
  ATR_pct crosses regime boundary (HIGH→NORMAL, NORMAL→LOW, etc.)
  AND equity curve is not in Warning/Stop state

Rotation action:
  1. Reduce size on regime-mismatched strategies to 50%
  2. Increase size on regime-matched strategies (up to leverage cap)
  3. Log rotation in trade journal: "Regime: X → Y, rotated [strategy A] down, [strategy B] up"

Do NOT rotate based on:
  - "This strategy has been losing lately" (without regime check)
  - Calendar dates
  - Headlines or news sentiment
```

---

## Gate 4 — Rolling OOS Recalibration Cadence (MD-26)

Rolling OOS optimization naturally over-weights recent data (near-recent-regime bias).

Mitigation SOP:
1. Run WFA with ≥3 different window lengths (e.g., 60/90/120 days)
2. If all three converge to same parameters → regime-robust, proceed
3. If results diverge → regime is in transition, reduce sizing 30% until convergence

**Warning sign:** Parameter set that looked optimal 6 months ago now underperforms but regime hasn't changed → strategy-specific drift, not regime issue. Escalate to kill-decision SOP (#04).

---

## Self-Test

Given: BTC, current ATR_pct = 82%, equity curve at +1.2σ, trend-following strategy active.

- G0: HIGH volatility regime ✓
- G1: Trend-following matches HIGH regime ✓
- G2: Leverage = 1.3× baseline ✓
- G3: No rotation trigger (regime stable) ✓
- G4: WFA windows converging (assume) ✓

Result: **GO at 1.3× leverage.** All gates pass.

---

## Anti-Patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| Running trend strategy in compression | MD-33: bleeds on tail | Gate 1 check before entry |
| Rotating strategy because "it's been losing" | No regime evidence | Require ATR regime change first |
| Same leverage in all regimes | MD-32 violation | Use f(regime) table |
| Annual results "feel different" | Missing structural shift | Annual storm ratio check (MD-107) |
| Multiple correlated trend strategies | MD-118: false diversification | Require different regime dependencies |

---

## DNA Anchors

MD-14 · MD-25 · MD-26 · MD-31 · MD-32 · MD-33 · MD-75 · MD-78 · MD-105 · MD-107 · MD-118 · MD-143 · MD-173 · MD-181
