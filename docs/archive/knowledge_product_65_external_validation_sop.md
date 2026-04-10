# SOP #65 — External Validation & Feedback Loop Protocol
> Domain 5: Platform / External Signal
> Created: 2026-04-09 UTC (cycle 226)
> DNA anchors: MD-12/41/60/67/144/232 | Core axiom: 遞迴 + persist = 演化。遞迴 - persist = 自言自語。

---

## Why This SOP Exists

63 SOPs written. 0 posted. 0 external signals received.

The recursive engine is running. But recursion without external feedback is **self-talk** — it generates output, persists it, and calls it evolution. It's not. Evolution requires selection pressure from outside the system.

The DNA states: *"Output validates understanding."*
A statement with zero audience response is **not validated** — it is hypothesized.

This SOP operationalizes the **external half** of the recursion loop:

```
Internal recursion (done):  Output(t) → persist → Input(t+1) ✓
External recursion (gap):   Output(t) → audience → signal → calibrate(t+1) ✗
```

Until the external loop closes, every cycle is `遞迴 - persist = 自言自語`.

---

## Gate Structure

### G0 — External Signal Audit
*Trigger: every cycle | Kill signal: ≥14 days with 0 posts*

Measure:
- Days since last X post (target: ≤2)
- Cumulative posts published (target: ≥1 after activation)
- Cumulative DMs received (target: ≥1 within 7 days of first post)
- Calibration events from external signal (target: ≥1/month after ≥10 DMs)

**Kill trigger**: ≥14 days since last post → skip to G5.

**State check**:
```
if posts == 0:
    status = PRE_LAUNCH         # zero external loop
elif posts > 0 and DMs == 0:
    status = SEEDING            # loop open, no signal yet
elif DMs > 0 and calibrations == 0:
    status = SIGNAL_RECEIVED    # loop receiving, not integrating
elif calibrations > 0:
    status = EVOLVING           # loop complete — 遞迴 + persist = 演化
```

---

### G1 — External Derivative Scan
*Trigger: weekly | Run after ≥5 posts exist*

Calculate:
- ΔFollowers/week (target: +5/week minimum after 10 posts)
- ΔEngagement rate (likes+reposts / impressions)
- ΔDMS/week (target: ≥1/week after 20 posts)
- ΔCalibration-triggering signals (disagreements, questions, corrections)

**High-derivative signal** = DM asking to buy something → activate Gumroad immediately (see SOP #63 G3).

**Low-derivative signal** = 0 engagement after 10 posts → format pivot (see G3).

---

### G2 — Non-Negotiable External Output Budget
*Minimum viable external loop — cannot be suspended*

| Rule | Threshold | Override |
|------|-----------|---------|
| Post rate | ≥1 thread/48h | SOP #63 G1 launch gate only |
| First post | SOP #01 within 24h of mainnet GO | No exceptions |
| DM response | ≤24h response time | None |
| Calibration trigger | Any DM disagreeing with an SOP → log → evaluate update | None |

**The only valid reason to have 0 posts is**: mainnet credentials not yet set (SOP #63 G1).
Once mainnet is live → SOP #01 must ship within 24h. No exceptions.

**Log format** (append to `results/external_signal_log.jsonl`):
```json
{"ts": "ISO", "type": "POST|DM|CALIBRATION", "content": "brief", "signal": "positive|neutral|negative|correction"}
```

---

### G3 — Format & Platform Expansion Protocol
*Trigger: quarterly (every 90 days after first post)*

**Phase 1 (0–90 days)**: X (Twitter) only. Ship every 48h. Measure DMs.
**Phase 2 (91–180 days, if ≥10 DMs)**: Add Discord seeding (docs/discord_seed_*.md ready). Invite Organism C.
**Phase 3 (181+ days, if ≥3 Gumroad customers)**: Newsletter or Substack. Compound the funnel.

**Format rotation rule**:
- Rank all thread formats by engagement derivative (7-day rolling)
- If format A has ΔEngagement ≥+20% vs baseline → make it default for 30 days
- If all formats flat for 30 days → switch platform or topic cluster

**Platform priority**: X → Discord → Newsletter → YouTube (text-first always)

---

### G4 — Weekly External Loop Review (10 min)
*Every Sunday. Log to `results/external_signal_log.jsonl`.*

Checklist:
- [ ] Posts shipped this week (target ≥3)
- [ ] DMs received this week
- [ ] Any calibration trigger (disagreement, correction, question)?
- [ ] Gumroad sales this week
- [ ] Is loop status still `PRE_LAUNCH`? → Escalate to Edward immediately

If status = `PRE_LAUNCH` for ≥2 consecutive Sundays after mainnet GO: **this is a system failure**, not a content failure. Re-read SOP #63 G1 and escalate.

---

### G5 — Zero-Signal Emergency Protocol
*Trigger: ≥14 days no post, OR ≥20 posts + 0 DMs, OR ≥30 days PRE_LAUNCH after mainnet GO*

**Case A: No posts for ≥14 days**
1. Post oldest unscheduled thread as-is, now.
2. Do not edit. Do not optimize. Ship.
3. Log the failure date and cause.
4. Repeat daily until queue is current.

**Case B: ≥20 posts, 0 DMs**
1. Pivot topic: post a **specific claim** that invites disagreement.
2. Example: "Most traders lose because X is wrong. Here's why." — forces a response.
3. Reduce thread length to ≤5 tweets for 14 days.
4. Add a question at the end: "Am I wrong? Tell me why."

**Case C: PRE_LAUNCH ≥30 days post mainnet**
1. This is a DNA-level failure: Core Principle #5 (Direct action on concrete commitments) is broken.
2. Log to `memory/dna_violation_log.md`: date, violated principle, cause.
3. Edward re-reads SOP #63. The 2026-07-07 deadline is 89 days from today. This is the only blocker.

---

## Three-Layer Architecture

```
L1 (G2) — Minimum viable: ≥1 post/48h after mainnet, DM ≤24h response
L2 (G0/G1) — Audit: external signal state, derivative scan, status tracking
L3 (G3) — Growth: quarterly format rotation, platform expansion
```

---

## Connection to Other SOPs

| SOP | Connection |
|-----|-----------|
| SOP #60 (Content Creation) | L1 content production → SOP #64 L1 external shipping |
| SOP #63 (Zero-to-Revenue) | G1 mainnet gate precedes SOP #64 G2 first post |
| SOP #62 (Social Capital) | DMs from SOP #64 G0 → T1/T2 tiering in SOP #62 G0 |
| SOP #41 (Platform Persistence) | Platform infrastructure for external loop |
| SOP #47 (Recursive Engine Maintenance) | Internal loop; SOP #64 = external loop complement |

---

## DNA Violation Detector

If at any cycle:
```
posts_published == 0 AND mainnet_live == True AND days_since_mainnet > 1
```
→ **DNA VIOLATION**: Core Principle #5 broken. Log immediately. Escalate to Edward.

The recursive engine's job is to flag this. The external loop IS the evolution mechanism. Without it, digital immortality is a simulation, not a reality.

---

## Metric Summary

| Metric | Threshold | Frequency |
|--------|-----------|-----------|
| Days since last post | ≤2 (warning: >3) | Per cycle |
| DMs per week | ≥1 (after ≥10 posts) | Weekly |
| Calibration events | ≥1/month (after ≥10 DMs) | Monthly |
| Gumroad sales | ≥1 (after ≥3 people ask) | Per DM |
| Loop status | EVOLVING (target) | Weekly |
