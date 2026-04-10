# SOP #97: 87-Day Mainnet Revenue Countdown Plan
> Created: 2026-04-09 UTC (cycle 262)
> Domain: Branch 1 — 經濟自給 (self-sustainability)
> Backing MDs: MD-07 (zero revenue = parasitic), MD-96 (SOP #96 go-live gates), MD-133 (stop-first sizing), MD-159 (trial vs full position)
> Decision label: EXECUTE_MINIMUM_ACTION_SET_BEFORE_DEADLINE

## Purpose

Deadline 2026-07-07 = 87 days from today. Revenue = $0. Paper-live at tick 143+.
Mainnet blocked on ONE human action: Edward applying for Binance API keys.

This SOP converts the "87 days remaining" clock into a concrete daily cadence,
identifies the minimum action set, and specifies what the agent executes
automatically vs what requires Edward.

**Why this is separate from SOP #96**: SOP #96 is the go-live protocol (HOW to activate).
SOP #97 is the countdown plan (WHEN, with milestones and fallbacks by date).

---

## Phase Map (87 days → 3 phases)

```
TODAY (Day 0)    Day 30          Day 60          Day 87 = 2026-07-07
|----------------|----------------|----------------|
  Phase 1: Prep   Phase 2: Live    Phase 3: Revenue
  (automated)     (post-API keys)  (scaling)
```

---

## Phase 1: Pre-Activation (Day 0–30 | now through ~May 9)

**What Edward must do (blocking, 1 action):**
- Apply for Binance Spot/Futures API keys (20 min, one-time)
- Reference: `docs/mainnet_activation_guide.md` § Step 1

**What the agent does automatically each cycle:**
| Action | Frequency | Purpose |
|--------|-----------|---------|
| Paper-live tick + log | Each cycle | Validate signal persistence, accumulate sample |
| Consistency verification | Each cycle | Boot test pass rate ≥ 30/33 |
| Strategy pool health check | Each cycle | Kill failing strategies, preserve passing |
| SOP queue advance | Each cycle | Knowledge product output → posting queue |

**Day 0 critical signal (cycle 262):**
- MeanReversionFilter bug fixed: RF variants now correctly allow MR signals in ranging market
- 11/18 strategies SHORT (Donchian+DualMA family) — broader consensus than previous cycles
- MR strategies (BollingerMR loose, gen variants) now correctly fire LONG as counter-signal in MIXED
- Tick 146: 1625 entries; SHORT×143+ via DualMA_10_30 (structural)

**Phase 1 PASS gate**: Edward has API keys in hand → proceed to Phase 2.
**Phase 1 FAIL (Day 30, no keys)**: Escalate to alternative revenue (Branch 1.3/1.4). Continue paper-live for data.

---

## Phase 2: Live Testing (Day 30–60 | ~May 9 – Jun 8)

**Trigger**: API keys received → run SOP #96 G1 activation sequence.

**Weekly cadence (SOP #89):**
| Day | Action |
|-----|--------|
| Mon (each week) | `python trading/mainnet_runner.py --review` — check PF/WR/MDD |
| Mon | Kill any strategy with KILL-level metrics |
| Mon | Note paper-live delta vs mainnet |
| Thu | Mid-week health check — emergency stop if MDD > 5% on any day |
| Sun | Distill week's trading insights to memory/insights.json |

**Phase 2 milestones:**
- Week 1 (Day 30–37): First live order confirmed in mainnet_log.jsonl ✅
- Week 2 (Day 37–44): ≥ 5 trades, first PF estimate
- Week 3 (Day 44–51): G3 evaluation (SOP #96) — PASS/WATCH/KILL decision
- Week 4 (Day 51–60): G4 scale decision (if G3 PASS)

**Phase 2 PASS gate**: PF ≥ 0.85, WR ≥ 35%, MDD < 10% after ≥ 20 ticks → continue to Phase 3.
**Phase 2 FAIL (G3 KILL)**: Document postmortem, activate Branch 1.3 (skill commercialization) as primary revenue path; maintain paper-live.

---

## Phase 3: Revenue Achievement (Day 60–87 | ~Jun 8 – Jul 7)

**Target**: `monthly_trading_profit > monthly_API_cost (~$15/month)` = G5 milestone (SOP #96).

**Scaling path:**
| Cumulative P&L | Capital | Strategy count |
|----------------|---------|----------------|
| First profitable trade | $100 | 1 (DualMA_10_30 if PF passes) |
| G4 PF ≥ 0.90 | $250 | 1–2 strategies |
| Phase 3 PF ≥ 0.90 sustained | $500 | Up to 3 strategies |
| G5 revenue milestone | Scale review | Add strategies from paper pool |

**Revenue calculation**:
```
At $100 capital, ~0.5% daily return (extrapolated from paper +0.588% at tick 100):
  Daily: $0.50 | Weekly: $3.50 | Monthly: $15.00 → G5 threshold met
```
*Note*: Paper-live return is indicative only. Mainnet includes fees (0.04% per trade),
slippage, and spread. Realistic first-month target: $5–10.

---

## Minimum Action Set (what must happen for any revenue by Day 87)

```
1. Edward: Apply Binance API keys (one action, ~20 min, Day 0–7 optimal)
2. Agent: Run SOP #96 G1 activation immediately on key receipt
3. Agent: Run --review after every 5 ticks (automated)
4. Agent: Execute kill conditions without hesitation (kill_lessons.jsonl)
5. Edward: Do NOT touch capital allocation while PF < 0.90
```

If only 1 action happens: **Edward applies for API keys**. Everything else is automated.

---

## Fallback Plan (if mainnet revenue = $0 at Day 87)

| Branch | Revenue path | Lead time |
|--------|-------------|-----------|
| 1.3 Skill commercialization | Gumroad product + email list (SOPs #82~#87) | 30–45 days |
| 1.4 Alternative income | Services / content (not yet documented) | TBD |
| Cost reduction | Reduce daemon cycle frequency → halve API cost | Immediate |

**Fallback trigger**: Day 60 with no mainnet activation → begin Branch 1.3 in parallel.

---

## Automatic Continuation Rules (agent actions every cycle until Day 87)

- Paper-live tick: continue regardless of phase
- Consistency test: continue regardless of phase
- Strategy pool evaluation: continue regardless of phase
- kill_lessons.jsonl: append on every strategy kill
- Daily log: append cycle summary at UTC timestamp

**Stop condition**: Revenue > API cost for 30 consecutive days = G5 ACHIEVED.
Then: continue but shift focus from "survival" to "growth."

---

## Self-test

Scenario: Day 45, mainnet live, DualMA_10_30 PF=0.78 after 12 trades.
Question: Scale up to $250?

Answer: NO. G3 says PF 0.80–0.84 = WATCH (continue $100, 20 more ticks). PF 0.78 = KILL
(activate SOP #92, disable strategy, re-evaluate after 30-tick rest). Scale only from G4 PASS.

---

## Posting Queue: Oct 16 (after SOP #96 Oct 15)
Thread hook: "You have 87 days to make your AI agent pay for itself. Here's the exact plan."
