# SOP #03 — Execution & Sizing Real-Time Checklist

> Derived from: MD-13, MD-28, MD-29, MD-30, MD-133, MD-157, MD-159
> Purpose: Convert strategy signal into correctly-sized live order, every time.
> Format: Sequential gates. Fail any gate = no trade.

---

## Pre-Signal Gate (run once per session open)

**G0 — Strategy pool L/S balance audit (MD-29)**
- Count long-biased vs short-biased strategies in active pool
- Flag if long > short × 2 (rolling optimisation naturally over-selects longs)
- Imbalance = systematic regime blindspot, not edge
- Do NOT proceed if pool is structurally one-sided without conscious acknowledgement

**G1 — Leverage coefficient (MD-30)**
- Pull *historical* Calmar / Sharpe for each active strategy (from backtest, not recent 30d)
- Use historical R/R ratio to SET leverage cap for this session
- Recent performance = used only to detect failure, never to increase leverage
- Mixing these two numbers = using the wrong input for the lever

---

## Signal Validation Gate (run on each signal)

**G2 — Strategy quality check (MD-13)**
- Compute `edge_ratio = avg(MFE/ATR) / avg(MAE/ATR) × √N`
- Threshold: edge_ratio ≥ 1.5 for trend strategies, ≥ 1.2 for MR strategies
- Low edge_ratio with small N = small-sample overfit, not edge
- Below threshold: do not execute, log as SKIPPED_QUALITY

**G3 — First-principles coherence (MD-157)**
- Ask: "What is this strategy extracting from the market? Who is on the other side?"
- If you cannot articulate the mechanism in one sentence, the edge is borrowed, not owned
- Borrowed edges disappear when regime changes; owned edges can be regime-conditioned

---

## Sizing Gate (run after signal validated)

**G4 — Stop-loss first, size second (MD-133)**

Step 1: Define max risk = account equity × 1%  
Step 2: Identify stop-loss price level (structural: support/resistance/ATR multiple)  
Step 3: Compute stop distance in points = |entry_price − stop_price|  
Step 4: Back-calculate max entry from stop: `max_entry = stop + (1% equity / lot_size / contract_mult)`  
Step 5: If current price > max_entry → **no trade** (stop is too far, not that stop should move)

Never: "Enter, then find a stop." Always: "Find stop, then check if entry is within range."

**G5 — Position size formula (MD-28)**

```
lots = (account_equity × risk_pct) / (ATR × contract_multiplier)
```

Where:
- `risk_pct` = 0.01 (1% default; never override by feel)
- `ATR` = 14-period ATR in price units on signal timeframe
- `contract_multiplier` = instrument-specific (e.g. BTC perp = 1 USDT/contract)

Any deviation from this formula requires a written reason in the trade log before execution.  
"The signal feels strong" is not a valid reason.

**G6 — Trial vs full position (MD-159)**
- If edge_ratio 1.2–2.0 or market conditions uncertain: enter 50% size (trial)
- Trial position must have positive EV on its own, not as placeholder for future full entry
- Full position add: only if (a) price action confirms signal AND (b) stop can be moved to entry
- If trial position stopped out: log result, do NOT average down

---

## Execution Gate (final check before order submission)

**G7 — Order parameters checklist**
- [ ] Entry price: market/limit within G4 range
- [ ] Stop-loss: pre-set, not mental
- [ ] Size: from G5 formula, not rounded for convenience
- [ ] Target: from MAE/MFE distribution (p75 MFE as initial target)
- [ ] Leverage: within cap set in G1

**G8 — Conflict check**
- Is this trade correlated > 0.7 with an existing open position?
- If yes: new position reduces to 50% or existing is trimmed to make room
- Portfolio-level risk = sum of correlated exposures, not sum of individual stops

---

## Post-Trade Logging (run immediately after fill)

Required fields in trade log:
```
timestamp | strategy_id | signal | edge_ratio | stop_distance | lots | entry | stop | target | regime | notes
```

Minimum viable review trigger: 5 closed trades in same strategy  
Review question: "Is the edge_ratio stable, or was early performance lucky?"

---

## Kill Conditions (inherited from SOP #02, execution layer)

Per-trade:
- MFE never exceeds entry risk (edge_ratio < 0.8 over 10 trades) → pause strategy
- Stop hit 3× in same session on same strategy → halt for session

Session:
- Account drawdown > 3% intraday → close all positions, no new entries
- G0 or G1 fail at session open → trade in reduced size only (50% all positions)

---

## Failure Mode Reference

| Failure | Symptom | Root Cause | Fix |
|---------|---------|------------|-----|
| Oversizing | "Signal was so clear" | Skipped G5 formula | Hard-code formula in execution script |
| Stop set by price level, not risk | Stop > 2% away | Skipped G4 step 4 | Always compute back-calculated max entry |
| Averaging down | "It'll come back" | Skipped G6 trial rule | Trial loss = closed, not added |
| Leverage drift | Good recent run → bigger size | Mixed G1 metrics | Historical R/R is read-only, not updated by recent trades |

---

## Self-Test Scenario

**Scenario**: BTC dual_ma signals SHORT. Account = 10,000 USDT. ATR14 = 420 USDT. Contract mult = 1.  
Historical Calmar = 1.2. Recent 30d Calmar = 2.8. Edge ratio (last 20 trades) = 1.7.  
Nearest structural stop = 2.1% above entry.

**Apply SOP:**
- G1: Leverage cap from historical Calmar 1.2, NOT 2.8 (recent)
- G4: 1% equity = 100 USDT. Stop = 2.1% above entry ≈ 630 USDT distance. Lots = 100/420 = 0.238 lots
- G5: lots = (10000 × 0.01) / (420 × 1) = 0.238 → **0.24 lots**
- G6: edge_ratio = 1.7 (between 1.2–2.0) → enter trial 50% = 0.12 lots
- G7: stop pre-set, target = p75 MFE from historical distribution

**Result**: 0.12 lot SHORT, stop pre-set, leverage within historical cap. Not 1 lot because signal felt strong.
