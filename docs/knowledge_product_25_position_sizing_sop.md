# SOP #25 — Position Sizing: The Only Variable You Fully Control

> "Your strategy tells you when to trade. Position sizing tells you whether you survive long enough to trade again."
> — MD-160: build confidence intervals before performance metrics

**Backing MDs:** MD-33 (tail cap), MD-87 (anti-martingale), MD-99 (constant leverage), MD-160 (sizing from full range), MD-183 (capital transmission chain), MD-219 (Kelly insurance)

---

## The Problem

Most traders obsess over entry signals. Entry determines direction. Position sizing determines survival.

You can have a 55% win rate and blow up. You can have a 45% win rate and compound. The difference is sizing.

---

## The 5-Gate Framework

### G0 — Define Maximum Acceptable Loss First
Before sizing anything, answer: "What is the maximum dollar amount I can lose on this trade without needing to change my behavior?"

That number is your **loss budget per trade**. Sizing is derived from it — not the other way around.

```
Max position size = Loss Budget ÷ Distance to Stop
```

If your stop is 2% away and your loss budget is $100 → max position = $5,000.

**MD-160: size from the full range of outcomes, not the expected case.**

---

### G1 — Constant Leverage Baseline
Start with constant leverage, not constant dollar risk.

```
Daily rebalance: position_size = account_equity × target_leverage
```

Why: drawdowns self-reduce your size automatically. Recovery doesn't require extra leverage.

**MD-99: constant leverage = daily rebalance to fixed notional/equity ratio.**

Anti-pattern: fixed lot size. When equity falls 20%, a fixed lot is now 25% of account — you're adding leverage into a hole.

---

### G2 — Anti-Martingale Rule
Never increase position size after a loss.

```
IF current_equity < equity_at_last_trade: size ≤ previous_size
IF consecutive_losses ≥ 3: size = max(previous_size × 0.5, minimum_size)
```

Martingale logic (double after loss to recover) assumes infinite capital and no kill conditions. You have neither.

**MD-87: martingale = self-negating premise. The "recoup" trade is always the kill trade.**

---

### G3 — Tail Position Cap
Cap any single position at 2× your average position size.

```
Max single position = mean(last_20_positions) × 2.0
```

Why: outlier conviction can be wrong. Concentration kills faster than dilution. The cap isn't about doubt — it's about asymmetric ruin.

**MD-33: tail position cap prevents single-trade ruin regardless of conviction level.**

---

### G4 — Kelly Ceiling (Volatility-Adjusted)
When win rate is high, Kelly can suggest aggressive sizing. Apply a Kelly ceiling:

```
Kelly fraction = (win_rate × avg_win - loss_rate × avg_loss) / avg_win
Safe sizing = Kelly × 0.25  (quarter-Kelly)
```

Quarter-Kelly captures ~75% of Kelly growth rate while reducing drawdown by ~50%.

Exception: when Kelly < 0.10 (weak edge) → size at minimum, not Kelly.

**MD-219: Kelly insurance — near-full-Kelly sizing increases volatility with minimal extra EV. Haircut is free risk reduction.**

---

### G5 — Equity Curve Trigger Integration
Position sizing connects to equity curve states (see SOP #23 Regime Detection):

| Equity Curve State | Sizing Rule |
|--------------------|-------------|
| Normal (< 5% DD) | Full target leverage |
| Warning (5–10% DD) | 50% of target leverage |
| Stop (> 10% DD) | Halt. Paper trade. Diagnose. |

**MD-75: equity curve is the leverage trigger, not a performance dashboard.**

---

## Self-Test

Scenario: $10,000 account. Target leverage 3×. Strategy has 55% WR, avg win = $300, avg loss = $200. Current equity = $9,100 (9% drawdown).

1. G0: loss budget = $200 → stop 2% away → max position = $10,000 ✓
2. G1: equity × 3 = $27,300 notional. But...
3. G4: Kelly = (0.55×300 - 0.45×200)/300 = (165-90)/300 = 0.25 → quarter-Kelly = 0.0625 → $9,100 × 0.0625 = $569 max risk per trade
4. G3: check if above 2× average — first trade, no history → use G4 output
5. G5: 9% drawdown → **WARNING STATE → 50% leverage** → $27,300 × 0.5 = $13,650 notional

**Result: CONDITIONAL GO at 50% leverage. Size down, stay in the game.**

---

## The Takeaway

Position sizing is not risk management as an afterthought. It's the mechanism that converts a positive-EV strategy into compounding equity.

Entry signal = direction. Position size = whether you survive to take the next one.

Four rules to remember:
1. Size from max loss, not expected gain
2. Constant leverage, not constant lots
3. Never double after a loss
4. Equity curve state gates your leverage — automatically

---

*Part of the Edward Trading System SOP Series — #01~#25*
