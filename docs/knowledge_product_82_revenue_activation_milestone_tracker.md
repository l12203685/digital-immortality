# SOP #82: Revenue Activation Milestone Tracker
> Timestamp: 2026-04-09T UTC | Cycle 247 | Domain: 1 (經濟自給)

## Purpose

Maps the critical path from first post → revenue, with milestone gates and deadline tracking. Closes the "I know what to do but can't see if I'm on track" gap.

**Failure mode this prevents**: working on agent-side tasks while the human-gated critical path drifts past the ⚡ 2026-07-07 deadline unnoticed.

**Critical path**: Edward posts SOP #01 → audience accumulates → G2 (≥10 DMs in 30 days) → SOP #70 G0 activates → Gumroad live → first sale → revenue > API cost.

**Trigger**: Run weekly from the moment SOP #01 is posted. Updated by daemon each cycle.

**DNA Anchors**: MD-13 (edge_ratio = forward opportunity), derivative thinking (look at rate, not level), MD-012 (information asymmetry = edge), zero-revenue = parasitic not immortal.

---

## G0 — Milestone Map (set once at SOP #01 post date)

Record in `results/revenue_activation_tracker.json`:

```json
{
  "sop_01_posted": null,
  "deadline": "2026-07-07",
  "days_remaining": null,
  "milestones": {
    "M1_first_post": {"target": "day 0", "actual": null, "status": "PENDING"},
    "M2_week1_3posts": {"target": "day 7", "actual": null, "status": "PENDING"},
    "M3_first_dm": {"target": "day 14", "actual": null, "status": "PENDING"},
    "M4_g2_trigger": {"target": "day 30", "actual": null, "status": "PENDING"},
    "M5_gumroad_live": {"target": "day 32", "actual": null, "status": "PENDING"},
    "M6_first_sale": {"target": "day 45", "actual": null, "status": "PENDING"},
    "M7_revenue_gt_api_cost": {"target": "day 60", "actual": null, "status": "PENDING"}
  },
  "current_dms": 0,
  "current_posts": 0,
  "current_followers": 0,
  "gumroad_live": false,
  "revenue_usd": 0.0,
  "api_cost_usd_monthly": 20.0,
  "notes": []
}
```

**Day targets are relative to M1 (SOP #01 post date).** If M1 slips, all downstream targets adjust +1 day per slip day.

---

## G1 — Weekly Pulse Check

Run every 7 days from M1. Update `revenue_activation_tracker.json`.

For each milestone:
- **PENDING**: not started
- **ON_TRACK**: within target window
- **AT_RISK**: >3 days past target, no completion
- **DONE**: completed (record actual date)

Checklist:
```
[ ] posts this week ≥ SOP #81 cadence (3 posts/week)
[ ] DM count updated (current_dms)
[ ] follower delta recorded
[ ] gumroad_live status confirmed
[ ] revenue_usd updated
[ ] milestone statuses updated
```

---

## G2 — Deadline Math (run weekly)

```
days_remaining = (2026-07-07) - today
days_since_m1 = today - sop_01_posted (if posted)

if days_remaining < 30 and M5_gumroad_live == PENDING:
    → CRITICAL: Gumroad not live with <30 days to deadline
    → escalate: Edward must post SOP #01 immediately

if M4_g2_trigger == PENDING and days_since_m1 > 30:
    → BLOCKED: G2 not triggered; check DM conversion (SOP #81 G4)
    → check: are posts going out? (SOP #78 G1)
    → check: are DMs being handled? (SOP #69)

deadline_buffer = days_remaining - (days to M7 from current milestone)
if deadline_buffer < 14:
    → WARNING: buffer < 2 weeks; compress timeline or reduce price floor
```

---

## G3 — Blocker Escalation

If any milestone is AT_RISK or BLOCKED:

| Milestone | Blocker | Escalation Action |
|-----------|---------|-------------------|
| M1 first post | Edward hasn't posted | Re-read `docs/x_launch_sequence.md`; zero friction — only human action needed |
| M2 3 posts/week | Velocity not established | Run SOP #81 G1 (velocity baseline) |
| M3 first DM | No DM received | Check hook quality (SOP #12 hook formula); check post frequency |
| M4 G2 trigger | DMs < 10 by day 30 | Increase post frequency; engage replies; check SOP #81 G4 DM conversion |
| M5 Gumroad live | SOP #70 G0 not triggered | Confirm G2 met; run SOP #70 G0 manually if stuck |
| M6 first sale | Gumroad live but no sales | Check pricing; check CTA clarity; run SOP #69 (DM → sale conversion) |
| M7 revenue > cost | Sales < API cost | Check volume; lower price floor or add bundle; check SOP #81 compounding |

---

## G4 — Rate Analysis (monthly)

Compute trajectory:
```
dms_per_week = current_dms / weeks_since_m1
posts_per_week = current_posts / weeks_since_m1
projected_g2_date = today + (10 - current_dms) / dms_per_week * 7

if projected_g2_date > 2026-06-01:
    → CRITICAL: G2 projection misses revenue window before deadline
    → action: compress cadence (SOP #81 G2 weekly → daily)
```

---

## G5 — Persist + Daemon Integration

After each weekly pulse:
1. Save updated `results/revenue_activation_tracker.json`
2. Append one-line summary to `results/daily_log.md`:
   ```
   [SOP-82] Week N: posts=X DMs=Y milestone=Z status=STATUS days_remaining=D
   ```
3. Update `staging/session_state.md` blocker section with current milestone status
4. If M7 DONE: log `revenue_activation_date` and compute `days_ahead_of_deadline`

---

## Self-Test Walkthrough

Scenario: today = 2026-04-15 (6 days after SOP #01 posted on 2026-04-09).

- M1: DONE (2026-04-09)
- M2 target: day 7 (2026-04-16); current posts=3 → ON_TRACK
- M3 target: day 14 (2026-04-23); current DMs=0 → PENDING (within window)
- G2 math: days_remaining = 83; deadline_buffer = 83 - (60-6) = 29 → OK
- Weekly pulse: posts=3 ✓, DMs=0 (within M3 window), milestones ON_TRACK
- Next check: 2026-04-22

Output: revenue_activation_tracker.json updated, daily_log entry appended, session_state blocker section updated.

---

## SOP Cross-References

| SOP | Link |
|-----|------|
| SOP #78 | Posting mechanics (first post, batch write) |
| SOP #81 | Distribution velocity flywheel |
| SOP #69 | DM → value exchange protocol |
| SOP #70 | Gumroad activation (G2 → live) |
| SOP #12 | Hook formula (post quality) |
