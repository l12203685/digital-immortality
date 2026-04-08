# SOP #19 — Derivative Thinking & Inflection Point Detection

> Operationalizes Kernel 1: 看導數不看水平 (look at rate of change, not current level)
> Backing MDs: MD-1 (derivative > level), MD-122 (近期績效比=策略動能加速度), MD-13 (edge_ratio=MFE/MAE×√N), MD-108 (年度風暴比=跨年Regime偵測器), MD-2 (detect turning points before consensus)

---

## The Core Principle

**Level tells you where you are. Derivative tells you where you're going.**

Most decisions fail because the input data is a snapshot (current salary, current P&L, current follower count). The snapshot looks stable — but the rate of change already decided the outcome two quarters ago.

Derivative thinking = act on the slope, not the intercept.

---

## When to Apply

- Evaluating any trend: strategy performance, career trajectory, market regime, skill development
- Comparing two options that look similar at current level
- Deciding whether to accelerate, hold, or exit a position

---

## The 5-Gate Protocol

### G0 — Establish the Baseline Level

State the current value explicitly.

> "Strategy P&L is +$340. Portfolio is at ATH. Follower count is 820."

Purpose: Make the snapshot visible so you can consciously set it aside.

### G1 — Calculate First Derivative (Rate of Change)

Compute δ over a meaningful period (trailing 4–8 periods):

> Δ = (current − prior) / prior

| Context | Good period |
|---------|-------------|
| Trading strategy | 20–60 trades |
| Career/salary | 12–24 months |
| Content growth | 4–8 weeks |
| Market regime | 20–60 bars |

**Flag if δ is decelerating even while level is rising.**

### G2 — Calculate Second Derivative (Acceleration)

Is the rate of change itself increasing or decreasing?

> δ² = (δ_recent − δ_prior)

| δ² > 0 | Accelerating — trend strengthening |
|---------|-------------------------------------|
| δ² < 0 | Decelerating — trend weakening, watch for inflection |
| δ² ≈ 0 | Cruise — no signal |

**Critical rule:** A decelerating positive trend is closer to a reversal than a still-negative accelerating trend.

### G3 — Identify Inflection Point Conditions

An inflection point = δ crosses zero OR δ² crosses zero with confirmation.

Pre-conditions checklist:
- [ ] δ sign change in trailing 2 periods?
- [ ] δ² sign change with ≥2 consecutive confirmation bars?
- [ ] External regime signal aligned? (MD-108: regime detector before action)
- [ ] Volume/signal-weight corroborates direction?

If ≥3 of 4 checked → **INFLECTION CONFIRMED**. Act now, not after level confirms.

### G4 — Action at Inflection, Idle at Plateau

Default state = IDLE (consistent with Kernel 5).

| State | δ | δ² | Action |
|-------|---|----|--------|
| Rising plateau | + | ≈0 | HOLD — no new input needed |
| Decelerating rise | + | − | PREPARE EXIT — set kill condition |
| Inflection (turning down) | 0→− | − | EXIT or reduce |
| Decelerating fall | − | + | PREPARE ENTRY — set trigger |
| Inflection (turning up) | 0→+ | + | ENTER or add |
| Accelerating rise | + | + | HOLD/ADD — let compounding run |

**Never add at plateau. Never exit at trough. Act at inflection.**

---

## Self-Test Scenario

**Scenario:** Strategy dual_ma has P&L trajectory: +$12, +$14, +$15, +$15.2, +$15.1 over 5 windows.

- G0: Current level = +$15.1 (near ATH — looks fine)
- G1: δ_recent = ($15.1−$15.2)/$15.2 = −0.7% (first negative print)
- G2: δ² = negative (prior δ was +1.3%, now −0.7%) → **deceleration confirmed**
- G3: δ sign just turned negative, δ² confirmed negative — **INFLECTION SIGNAL**
- G4: → PREPARE EXIT. Set kill condition at MDD>10% from current peak.

**Decision:** Don't wait for the level to fall significantly. The derivative already told you.

---

## Anti-Patterns

| Anti-Pattern | Why it fails |
|--------------|--------------|
| "P&L is still positive, keep running" | Level bias — ignores deceleration signal |
| "It just started recovering, wait for confirmation" | Level bias — misses inflection entry |
| "Compare year-over-year not month-over-month" | Wrong period — obscures regime change |
| "The trend is strong, don't fight it" | Ignores δ² — strength without acceleration = stalled |

---

## Integration with Other SOPs

- **SOP #07 Regime Detection** — use regime δ to confirm trend direction
- **SOP #04 Strategy Kill** — trigger kill at inflection, not at level threshold breach
- **SOP #01 Strategy Development** — backtest momentum = near-term δ vs long-term baseline (MD-122)
- **SOP #18 Inaction Bias** — default IDLE is consistent; only break at confirmed inflection

---

*Series: SOP #01~#19. Operationalizes Edward Decision Kernel 1.*
