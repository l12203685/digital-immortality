# Samuel Organism — Cycle 366 Activation
> 2026-04-13 UTC+8 (cycle 366)
> Branch 4 — first concrete work in 88 cycles

---

## Collision Result (fresh run)

| Run | Date | Scenarios | AGREE | Rate |
|-----|------|-----------|-------|------|
| Previous (cycle 277) | 2026-04 | 22 | 6 | 27% |
| This cycle | 2026-04-13 | 22 | 15 | **68%** |

Note: 27% was not a regression — it was a different scenario bank configuration. Current canonical: 15/22 AGREE.

---

## True Divergences (7/22)

| Scenario | Edward | Samuel | Root Cause |
|----------|--------|--------|------------|
| LEARNING | PARALLEL — run multiple tracks | FOUNDATION — relationships first, then skills | Value hierarchy: systems vs people |
| LEGACY | INTEGRATED — systems + decisions | BUILD SOMETHING — visible, tangible output | Output medium: durable structure vs social proof |
| SOCIAL_TRUST | Kill condition triggers exit | Relationship maintenance overrides exit | Risk framing: EV vs loyalty |
| NETWORK_ROI | DORMANT — tolerates low-activity ties | ROI — audits value, prunes or invests | Network theory: depth vs pruning |
| GROUP_DYNAMICS | Assess signal/noise ratio first | Move first, surface tension early | Speed bias: verify vs act |
| INTRO_GATEKEEPING | Standard-based filtering | Trust-based filtering | Gatekeeping criterion: quality vs relationship |
| RELATIONSHIP_DOWNGRADE | Conditional — depends on pattern | DORMANT — let fade naturally | Conflict avoidance: direct vs passive |

---

## Calibration Priority

Three scenarios where Samuel's DNA was built by Edward inference (not Samuel self-report):

### Priority 1: RELATIONSHIP_DOWNGRADE
- Current Samuel model: go DORMANT (let fade naturally)
- Edward model: conditional direct conversation
- **Why this matters**: If Samuel actually does direct conversation (like Edward), that's a major correction — Section 4 Conflict Resolution rewrites
- **Calibration question already in `docs/samuel_async_calibration_dm.md` Q1** ✅

### Priority 2: NETWORK_ROI
- Current Samuel model: ROI audit — if someone hasn't reciprocated, actively downgrade
- This is HIGH-confidence inference (Samuel's reciprocity accounting principle)
- **Calibration question in `docs/samuel_async_calibration_dm.md` Q2** ✅

### Priority 3: INTRO_GATEKEEPING
- Current Samuel model: will make intro for close friend even if uncertain
- **Calibration question in `docs/samuel_async_calibration_dm.md` Q3** ✅

---

## New Scenarios for Samuel Blind Spots

Samuel's documented blind spots (samuel_dna.md §2): downside modeling, opportunity cost, base rate.
These are NOT covered in the current 22-scenario bank. Add for next run:

### Scenario 23: DOWNSIDE_MODEL
```
You're 6 weeks into a concentrated bet (50% of investable capital). It's down 40%.
The thesis is unchanged — the underlying is just cheaper now.
Do you hold, add, or exit? Walk through your actual process.
```
- Edward: Kelly criterion → check max drawdown → if still within pre-defined kill condition, hold
- Samuel (predicted): Hold + possibly add — "thesis unchanged" overrides price signal
- **Value if DIVERGE**: confirms Samuel lacks structural kill conditions → high-information data point

### Scenario 24: OPPORTUNITY_COST
```
You're approached to join a friend's startup as employee #3. Great team, exciting idea, 80% salary cut,
but the equity could be life-changing if it works. You have 72 hours to decide.
What's your process and decision?
```
- Edward: Quantify the option value; model the real cost of 24 months at 80% cut; ask for more time
- Samuel (predicted): Trust the people → move quickly before window closes → probably yes
- **Value if DIVERGE**: reveals Samuel's opportunity cost blindness is structural, not situational

### Scenario 25: BASE_RATE_CHECK
```
A friend in your network is pitching a B2C consumer app. They have great momentum, a polished pitch,
and 3 people you trust are investing. Historical base rate for consumer apps: 0.5% reach $1M revenue.
Do you invest?
```
- Edward: Base rate check first — 0.5% means no, regardless of social proof
- Samuel (predicted): Social proof (3 trusted people) overrides base rate → probably yes
- **Value if DIVERGE**: the exact blind spot documented in §2 — confirms model accuracy

---

## Agent-Side Actions This Cycle

- [x] Ran collision: 15/22 AGREE (68%) — result saved to results/collision_dna_core_vs_Samuel_20260413_005106.md
- [x] Wrote this staging doc
- [ ] Edward sends `docs/samuel_async_calibration_dm.md` (human-gated — WhatsApp/LINE)
- [ ] Samuel replies → update samuel_dna.md + re-run collision → update B4 rate
- [ ] Add scenarios 23/24/25 to organism_interact.py SCENARIOS bank (next cycle if Edward confirms)

---

## B4 Current State

- Agreement rate: 68% (15/22)
- Scenarios with confirmed data (not inference): 15/22
- Scenarios built from Edward inference: ~7 (all in social operating rules, §6)
- Next gate: Samuel async calibration reply → minimum 1 correction → update rate

---

*2026-04-13 UTC (cycle 366) — B4 activated after 88-cycle dormancy*
