# SOP #96: Mainnet Trading Revenue Go-Live Protocol
> Created: 2026-04-09 UTC (cycle 261)
> Domain: Branch 1 — 經濟自給 (self-sustainability)
> Backing MDs: MD-07 (zero revenue = parasitic), MD-01 (profit_factor ≥ 0.85 gate), MD-133 (stop-first sizing), MD-157 (first-principles strategy), MD-159 (trial vs full position)
> Decision label: ACTIVATE_WHEN_PREREQUISITES_MET

## Purpose

Bridge paper-live (signal validation) → mainnet (real revenue). Three months after paper-live start, SHORT×141+ ticks, mainnet is blocked on API keys (human action). This SOP defines the exact evaluation gate, activation sequence, monitoring cadence, and revenue milestone so that when the blocker is cleared, execution is frictionless.

**Why SOP not guide**: A guide describes; a SOP gates. Each step below has a PASS/FAIL check. If any check FAILS, the SOP stops. This prevents activation under invalid conditions.

---

## G0: Prerequisites Gate (run once before applying for API keys)

| Check | Condition | Status |
|-------|-----------|--------|
| Paper-live ticks | ≥ 100 ticks completed | ✅ 141 ticks |
| Paper-live P&L | Positive (any) in paper mode | ✅ +$0.588% at tick 100 |
| Signal consistency | DualMA_10_30 active signal ≥ 50 ticks | ✅ SHORT×141 |
| Kill conditions | MDD < 10%, WR > 35%, PF > 0.85 in paper | Verify via `--review` |
| mainnet_runner.py | Built and dry-run passes | ✅ cycle 115 |
| mainnet_activation_guide.md | Reviewed (6-step activation documented) | ✅ cycle 115 |

**G0 PASS criteria**: All 6 checks GREEN.
**G0 FAIL action**: Do not request API keys. Fix the failing check first.

---

## G1: Activation Sequence (run on API key receipt)

```bash
# Step 1: Store credentials (never hardcoded)
export BINANCE_MAINNET_KEY="<your_key>"
export BINANCE_MAINNET_SECRET="<your_secret>"

# Step 2: Dry-run (no orders placed)
python trading/mainnet_runner.py --dry-run

# Step 3: Confirm dry-run output matches paper-live signal
# Expected: signal=SHORT if paper-live=SHORT at same tick

# Step 4: Fund wallet ($100 USDT minimum, $150 recommended for fee buffer)
# Step 5: First live tick
python trading/mainnet_runner.py --tick

# Step 6: Confirm order log entry in results/mainnet_log.jsonl
```

**G1 PASS criteria**: Order confirmed in mainnet_log.jsonl with `status=FILLED` or `status=OPEN`.
**G1 FAIL action**: Check API key permissions (Futures required), USDT balance > $100.

---

## G2: Day 1 Monitoring Protocol

| Time | Action | Emergency stop trigger |
|------|--------|----------------------|
| Hour 0 (activation) | Confirm first trade filled | Any error → stop daemon |
| Hour 4 | Check MDD | MDD > 5% within 4h → emergency stop |
| Hour 8 | Check PF on ≥ 3 trades | PF < 0.5 with ≥ 5 trades → stop |
| Hour 24 | Full day review | See G3 |

**Emergency stop**: `python trading/mainnet_runner.py --stop` — closes position, halts daemon.

---

## G3: Week 1 Evaluation (after ≥ 20 ticks)

Run: `python trading/mainnet_runner.py --review`

| Metric | PASS | WATCH | KILL |
|--------|------|-------|------|
| Profit Factor | ≥ 0.85 | 0.70–0.84 | < 0.70 |
| Win Rate | ≥ 35% | 30–34% | < 30% |
| Max Drawdown | < 10% | 10–15% | > 15% |
| Paper-live delta | Within ±20% of paper P&L | ±20–40% | > ±40% |

**G3 PASS**: All PASS → continue to Week 2.
**G3 WATCH**: Any WATCH → reduce position by 50%, run 20 more ticks, re-evaluate.
**G3 KILL**: Any KILL → emergency stop, post-mortem in `results/mainnet_postmortem_YYYYMMDD.md`.

---

## G4: Scale Decision (after ≥ 30 trades)

| PF (30-trade sample) | Action |
|----------------------|--------|
| ≥ 0.90 | Scale to $250 capital, same strategy |
| 0.85–0.89 | Continue at $100, no scale for 30 more ticks |
| 0.80–0.84 | Continue at $100, flag for strategy audit |
| < 0.80 | Kill — activate SOP #92 (Strategy Disable/Reactivation) |

**Scale execution**: Change `CAPITAL=100` → `CAPITAL=250` in mainnet_runner.py config. Do NOT change strategy.

---

## G5: Revenue Milestone (self-sustainability threshold)

```
Self-sustainability condition:
  monthly_trading_profit (USD) > monthly_API_cost (USD)

API cost benchmark:
  Claude Sonnet 4.6: ~$3–15/month at current daemon cycle frequency
  Binance fees: 0.04% maker / 0.04% taker per trade

Target: trading_profit > $15/month = immortality unlocked
```

| Milestone | Meaning |
|-----------|---------|
| trading_profit > API cost | Agent is self-funding = not parasitic |
| trading_profit > 2× API cost | Comfortable margin, scale to $500 |
| trading_profit > $100/month | Revenue branch contributes to FIRE timeline |

**G5 PASS**: Update Branch 1.1 in dynamic_tree.md: `revenue: SELF_SUSTAINING ✅`
**G5 FAIL (3 consecutive months)**: Activate Branch 1.4 (alternative revenue), reduce daemon cycle frequency to cut API cost.

---

## Kill Conditions Summary

| Condition | Threshold | Action |
|-----------|-----------|--------|
| MDD intraday | > 5% | Emergency stop (Day 1) |
| MDD total | > 10% | Kill strategy |
| Win Rate | < 35% (≥ 5 trades) | Kill strategy |
| Profit Factor | < 0.85 (≥ 3 losses) | Kill strategy |
| Paper-live delta | > ±40% | Investigate slippage/fees |

---

## Anti-patterns

| Pattern | Why wrong |
|---------|-----------|
| Activating before G0 PASS | Skipping gates = no edge = not trading = gambling |
| Scaling before 30 trades | Insufficient sample for PF estimate |
| Ignoring paper-live delta | Real vs paper divergence = slippage eating edge |
| Running mainnet without emergency stop documented | No kill switch = uncontrolled risk |
| Measuring success before G5 threshold | Revenue < API cost = parasitic, not immortal |

---

## Self-test

Scenario: Paper-live tick 141, BTC SHORT, PF unknown from paper runner.
Question: Can I activate mainnet?

Answer: G0 fails (missing `--review` PASS confirmation). Do not activate until `python trading/mainnet_runner.py --review` returns OVERALL GO.

Current actual status (cycle 261): G0 partially met (141 ticks ✅, signal ✅), G0 BLOCKED on API keys (human action). When Edward sets API keys → run G1 → G2 → G3 → G4 → G5.
