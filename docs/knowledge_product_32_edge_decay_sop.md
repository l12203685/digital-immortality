# SOP #32 — Edge Decay & Signal Crowding Protocol

> **Core principle:** A strategy that worked yesterday may not work tomorrow — not because you changed it, but because the market did. This SOP tells you how to detect edge decay before it kills your account.

---

## The Problem

You backtested a strategy. OOS looks good. You deploy it. Slowly, returns flatten. Then drawdown. Then you question everything.

What happened: **your edge was arbitraged away.** Other participants found the same signal, exploited it, and erased the inefficiency you were harvesting.

Most traders catch this too late. This SOP catches it early.

**DNA anchors:** MD-108 (public indicators→marginal edge→zero), MD-109 (probability posterior update), MD-98 (survival rate = rolling÷historical), MD-143 (bandwidth cap), MD-96 (failure contract), MD-110 (depth×breadth parallel)

---

## When to Use This SOP

- Before deploying any strategy that uses publicly documented indicators (RSI, MACD, Bollinger, moving averages, etc.)
- When live performance diverges from backtest expectations
- Quarterly review of each running strategy
- When a strategy's survival_rate drops below 0.60

---

## G0 — Crowding Pre-Check (before first deployment)

**Question:** Is this signal's source public or proprietary?

Classify your edge source:
- **Type A — Structural:** exploits market mechanism (e.g. overnight gap, liquidity provision, options expiry). *Slower to decay.*
- **Type B — Behavioral:** exploits predictable human bias (e.g. momentum, anchoring). *Moderate decay risk.*
- **Type C — Statistical:** exploits historical pattern detected by optimization. *Fast decay risk.*
- **Type D — Public indicator-based:** uses indicators from any free charting platform. *Very fast decay. MD-108: marginal edge → zero.*

**If Type D:** require OOS Sharpe ≥1.2 (not 0.8) before deployment. The burden of proof is higher because crowding is already occurring.

**Output:** edge_type ∈ {A, B, C, D}, adjusted_OOS_threshold

---

## G1 — Baseline Fingerprint (deployment day)

Before going live, lock in your strategy's fingerprint:

```
baseline_fingerprint = {
  "date": deployment_date,
  "edge_type": A|B|C|D,
  "historical_OOS_sharpe": float,       # from backtest OOS period
  "historical_OOS_win_rate": float,
  "historical_OOS_avg_RR": float,
  "crowding_indicator": "N/A|low|medium|high",  # your subjective assessment
  "notes": "..."
}
```

Save to: `results/edge_fingerprints/{strategy_name}.json`

**Why:** This is your baseline for posterior updates (MD-109). Without a fingerprint, you have no reference to update from.

---

## G2 — Rolling Survival Rate Monitor

Every 30 live trades, compute:

```
survival_rate = rolling_30d_sharpe / historical_OOS_sharpe
```

| survival_rate | Status | Action |
|---|---|---|
| ≥ 1.0 | Thriving | No change |
| 0.80–0.99 | Stable | Monitor weekly |
| 0.60–0.79 | Stressed | Reduce size 50%, investigate |
| < 0.60 | Critical | Pause immediately, run G3 |

**This is MD-98 applied to edge monitoring, not just drawdown monitoring.**

Log each rolling check to `results/edge_monitor_log.jsonl`:
```json
{"date": "...", "strategy": "...", "survival_rate": 0.74, "status": "stressed", "action": "size_50pct"}
```

---

## G3 — Posterior Update (Bayesian diagnosis)

When survival_rate < 0.60, update your belief about whether the edge still exists:

**Prior:** P(edge_exists) = 0.8 (you deployed because you believed in it)

**Evidence to collect:**

1. **Regime test:** Is current regime consistent with strategy's design regime?
   - If NO → P(regime_mismatch) = 0.7 → this is regime problem, not edge decay. See SOP #27.
   - If YES → edge decay is more likely. Continue.

2. **Cohort check:** How are similar strategies (same logic family) performing?
   - If they're all down → market-wide effect, not your strategy's decay
   - If only yours is down → specific decay signal

3. **Signal timing drift:** Are entry signals still clustering around price inflection points, or are they now randomly distributed?
   - Plot entry_signal vs next_bar_move distribution
   - If distribution has flattened → signal is being front-run (crowded)

4. **Transaction cost sensitivity:** Recalculate OOS with costs ×2. Still profitable?
   - If no → marginal edge was thin, now gone (MD-108)

**Update posterior:**
```
P(edge_decayed | evidence) = update_bayesian(prior, regime_ok, cohort_down, timing_drift, cost_sensitive)
```

If P(edge_decayed) > 0.65 → proceed to G4.
If P(edge_decayed) ≤ 0.65 → likely regime problem → see SOP #27.

---

## G4 — Response Protocol

Based on P(edge_decayed):

**P(edge_decayed) > 0.65:**
1. Reduce position size to 25% (preserve capital while diagnosing)
2. Run depth investigation: is there a variant of this logic that's less crowded?
   - Type D → can you make it proprietary? (add filter only you can compute)
   - Can you shift to Type A/B (structural or behavioral anchor)?
3. Set 30-trade window at 25% size
4. If survival_rate recovers to ≥0.80 in 30 trades → restore to 50%, then 100% over next 30 trades
5. If not → kill. **Bandwidth freed for new strategy (MD-143)**

**P(edge_decayed) 0.50–0.65 (uncertain):**
1. Hold at 50% size
2. Paper-track the killed-off version for 60 days
3. If paper version also underperforms → confirm kill
4. If paper version recovers → execution issue, not edge issue → investigate slippage (SOP #28)

---

## G5 — Depth × Breadth Replenishment

When a strategy is killed or quarantined, the portfolio has a gap. **Do not let it stay empty.**

MD-110 principle: strategy development should always run depth (improving existing) AND breadth (exploring new) in parallel.

**Trigger:** any kill or quarantine event → immediately open one new strategy research thread
- Document the gap: what regime/type is now underrepresented?
- Required: new strategy must be different edge_type from the killed one
- Timeline: have a candidate in paper-test within 30 days

**Why this matters:** MD-143 says bandwidth is the hard cap on portfolio size. A killed strategy frees bandwidth. Immediately reinvesting that bandwidth in research maintains your portfolio's adaptive capacity.

---

## Self-Test Scenario

**Situation:** DualMA_10_30 has been live for 3 months. survival_rate = 0.52. Regime check confirms trending market (matches strategy design). Cohort check: all trend-following strategies down 15% this month. Cost sensitivity: OOS at 2× costs = +0.3% (marginal).

**Apply SOP:**
- G2: survival_rate 0.52 < 0.60 → Critical → pause, run G3
- G3 posterior:
  - Regime: YES (trending, correct regime) → not regime issue
  - Cohort: ALL trend-followers down → market-wide effect, not specific decay
  - Signal timing: not front-run (cohort confirms)
  - Cost sensitivity: marginal at 2× → Type C/D hybrid
  - P(edge_decayed) = 0.45 — uncertain, cohort evidence lowers decay probability
- G4: P=0.45, hold at 50%, paper-track for 60 days
- G5: open research on mean-reversion strategy (underrepresented given trending strategies all stressed)

**Verdict: HOLD 50% + RESEARCH MR.** Not a kill — cohort evidence suggests market-wide stress, not strategy-specific decay.

---

## Output Checklist

Before marking this SOP complete:
- [ ] edge_type classified (A/B/C/D)
- [ ] baseline_fingerprint saved to results/edge_fingerprints/
- [ ] survival_rate monitoring scheduled (every 30 trades)
- [ ] G3 posterior template understood
- [ ] G5 replenishment reflex active: every kill → new research thread

---

## Series Context

| SOP | Topic | Key MDs |
|-----|-------|---------|
| #29 | Strategy Monitoring | MD-96/98/42/142 |
| #30 | Drawdown Recovery | MD-42/55/98/32 |
| #31 | Parsimony & Complexity | MD-97/113/114/116/98 |
| **#32** | **Edge Decay & Crowding** | **MD-108/109/98/143/110/96** |

**Full series:** `docs/posting_queue.md`
