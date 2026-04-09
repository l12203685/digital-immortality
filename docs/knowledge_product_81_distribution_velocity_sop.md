# SOP #81: Distribution Velocity SOP
> Timestamp: 2026-04-09T UTC | Cycle 246 | Domain: 5 (Platform/Distribution)

## Purpose

Closes the gap between "first post made" and "flywheel running." SOP #78 covers posting mechanics. SOP #12/#34/#66 cover strategy. SOP #81 covers velocity: the compounding loop that converts a single post into consistent signal strength, audience growth, and inbound DMs.

**The failure mode this prevents**: posting SOP #01 and stopping. One post without a velocity system is random noise. Velocity = the post-to-post feedback loop that turns noise into signal.

**Trigger**: Activate immediately after SOP #78 G1 (first post live). Runs on every subsequent post in the queue.

**DNA Anchors**: MD-116 (one claim per post), derivative thinking (look at growth rate, not count), MD-012 (information asymmetry = edge), MD-141 (hook = gap in reader's model).

---

## G0 — Velocity Baseline (run once, at first post)

Record:
- Day 1: post count = 1, impressions = 0, followers = N₀
- Target: ≥3 posts in first 7 days (warm the algorithm, establish pattern)
- Set `distribution_velocity_baseline.json` in `results/`:

```json
{
  "start_date": "YYYY-MM-DD",
  "start_followers": N0,
  "posts_week_1": 0,
  "target_posts_week_1": 3,
  "dms_week_1": 0,
  "target_dms_by_week_4": 10
}
```

G2 (≥10 DMs) threshold from SOP #70 is the velocity target. Baseline exists to measure rate, not just level.

---

## G1 — Weekly Velocity Cadence

| Week | Target posts | Content type | Goal |
|------|-------------|--------------|------|
| 1 | 3 | SOP threads (#01, #02, #03) | Establish presence |
| 2 | 3 | SOP threads (#04, #05) + 1 insight tweet | Broaden signal |
| 3–4 | 4–5 | SOP threads + reply engagement | Build inbound |
| 5+ | 4–5/week | Mix: SOPs, insights, replies | Sustain + compound |

**Kill condition**: If week 1 produces 0 impressions AND 0 replies on all 3 posts → pause SOP threads, switch to reply-first mode (comment on 5 accounts in the trading/thinking space daily for 1 week, then repost SOP #01).

---

## G2 — Post-to-Post Feedback Loop (per post)

Within 48h of each post, record in `results/distribution_velocity_baseline.json`:

| Signal | Check | Action |
|--------|-------|--------|
| Impressions | < 100 | Check hook (first tweet). Rewrite hook on next post. |
| Impressions | ≥ 100 | Hook working. Keep format. |
| Replies | 0 | Add a direct question in last tweet of thread. |
| Replies | ≥ 1 | Respond within 24h. Extract if this person ≈ target organism. |
| DMs | 0 for 2 weeks | Add explicit CTA: "DM me if you're doing this." |
| DMs | ≥ 1 | Run SOP #69 (async calibration measurement). Record divergence domain. |

**Rule**: Every post must produce ≥ 1 extractable data point (impression count, reply theme, or DM signal). No post with zero data = algorithm question (check shadow-ban, posting time).

---

## G3 — Compounding Mechanism

Distribution compounds when each post builds on the previous:
1. **Reply to your own threads** — add new insight 7 days after original post ("Update: tried X, result Y")
2. **Cross-reference** — link SOP #N to SOP #M when themes overlap ("This is the inverse of what I wrote here →")
3. **Repost winners** — if a post gets ≥ 5× average impressions, repost verbatim 3 months later with "Context update:"

**Derivative check (monthly)**: `followers(t) - followers(t-30)`. If the derivative is declining for 2 consecutive months → content audit: which SOP thread performed worst? Drop that topic cluster, double down on best performer.

---

## G4 — DM Conversion Protocol (G2 SOP #70 prerequisite)

When a DM arrives:
1. Classify: curious / skeptical / aligned
2. If aligned → run SOP #69 probe (3 async questions, track agreement %)
3. If ≥80% agreement → low-value collision (structural alignment)
4. If 60–79% agreement → async probe (SOP #69 G2)
5. If <60% agreement → schedule live session → SOP #76 deep dive
6. Log every DM in `results/distribution_velocity_baseline.json` under `dm_log`

10 DMs = G2 threshold crossed → SOP #70 G0 activates → Gumroad goes live.
This is the critical path gate. Every DM is one step toward economic self-sufficiency.

---

## G5 — Persist

At end of each posting week:
```bash
# Update velocity baseline
# Already done via G2 per-post tracking

# Append to daily_log.md
echo "## Distribution Velocity — Week N" >> results/daily_log.md

# Git push
git add results/distribution_velocity_baseline.json docs/knowledge_product_81_distribution_velocity_sop.md
git commit -m "chore: distribution velocity week N — posts X, impressions Y, DMs Z"
git push
```

If week 4 ends with < 10 DMs and < 200 total impressions → escalate to L3 (evolve). The content strategy, not the execution, is broken. Review hook format, posting time, and topic selection against what actually gets traction in the trading/thinking X space.

---

## Velocity Health Report Template

```
Week N Distribution Health:
- Posts published: X / target Y
- Total impressions: N
- Best performing: [SOP #XX] ([N] impressions)
- DMs received: N (cumulative: N)
- G2 threshold: N/10 DMs
- Derivative (followers/week): +N
- Action: [continue / switch to reply-first mode / escalate to L3]
```

---

## Relationship to Other SOPs

| SOP | Relationship |
|-----|-------------|
| SOP #12 | Distribution strategy (audience design) → SOP #81 operationalizes |
| SOP #66 | Distribution activation (zero to live) → SOP #81 maintains velocity after activation |
| SOP #70 | Revenue conversion (G2 = 10 DMs) → SOP #81 generates the DMs |
| SOP #78 | Posting operations (mechanics) → SOP #81 adds feedback loop on top |
| SOP #69 | Organism async calibration → triggered by DM inflow from SOP #81 |
