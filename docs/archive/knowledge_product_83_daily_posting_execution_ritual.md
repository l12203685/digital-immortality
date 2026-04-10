# SOP #83 — Daily Posting Execution Ritual

> Domain: Distribution / Execution
> Created: 2026-04-09T10:00Z
> Status: OPERATIONAL

---

## Why This Exists

SOP #81 built the velocity flywheel. SOP #82 built the milestone tracker.
Neither answers: **what does Edward actually do, in what order, every single day?**

Gap: Infrastructure-ready ≠ posts going out. The missing layer is the daily micro-ritual.
Without it: infrastructure decays, the flywheel never spins, M1 never happens.

**This SOP closes that gap. ~20 min/day total.**

---

## G0 — Trigger

Run daily. Best time: first cognitive window (morning, before context-switching).
Minimum: once every 48h (posting cadence SOP #81 G2 = 1 thread per 48h).

If >48h since last post: **PRIORITY OVERRIDE** — run G1→G5 before any other work.

---

## G1 — Identify Today's Post (5 min)

1. Open `docs/posting_queue.md`
2. Find first row with `Status = pending`
3. Confirm the thread file exists: `docs/publish_thread_sop<NN>_twitter.md`
4. Read thread file: first tweet (hook) + last tweet (CTA)
5. Note the **One-Claim Hook** column — this is the only thing that matters for click-through

**If thread file missing**: skip to next pending row. Do not write a new thread on posting day.

---

## G2 — Post Execution (5 min)

1. Open X (Twitter) on desktop
2. Copy tweet 1 (hook) from thread file → paste → do NOT post yet
3. Read hook out loud. Does it make one strong claim? If yes: post.
4. Add remaining tweets as replies in thread (copy-paste sequentially)
5. Final tweet in thread = CTA ("Follow for next one. DM me if you want to go deeper.")
6. Post the thread
7. Log to `docs/posting_queue.md`: update `Status` → `posted YYYY-MM-DD`

**Anti-pattern**: editing tweets during posting. If you edit, you won't post. Trust the thread file.

---

## G3 — 48h Signal Capture (5 min, runs after 48h)

After 48h, check:
- Impressions (absolute, not relative)
- Reply count
- DM count (direct signal from SOP #82 M2)

Record in `docs/posting_queue.md` as `signal: NN impressions / N replies / N DMs`.

Verdict (per SOP #81 G3):
- `HIGH`: >500 impressions OR any DM → amplify (reshare, reply to replies)
- `LOW`: <500 impressions AND 0 DMs → analyze hook, note in queue, continue cadence

**Do not pause cadence based on LOW signal.** First 10 posts = baseline calibration (SOP #82 G2).

---

## G4 — DM Triage (2 min per DM, runs when DMs arrive)

When DM arrives (M2 milestone in SOP #82):
1. Read DM. Classify: curious / ready / spam
2. `ready`: share Gumroad product link → M4 potential
3. `curious`: ask one question ("What's the main thing you're trying to solve?") → qualify
4. `spam`: ignore
5. Log in `docs/dm_log.md` (create if missing): timestamp, classification, response sent

Target: reply within 24h. Delay kills conversion.

---

## G5 — Persist + Advance (2 min)

After each posting session:
1. Update `docs/posting_queue.md` (status + signal logged)
2. Update `staging/session_state.md` → Branch 1.3 last touched = today
3. Check SOP #82 milestone tracker: which milestone just advanced?
4. If M1 just happened (first post): update session_state Branch 1.3 status → "M1 ✅"
5. `git add docs/posting_queue.md staging/session_state.md && git commit -m "Branch 1.3: SOP#83 post cycle [date]"`

---

## Self-Test (Daemon Verification)

This SOP is operationally complete when:
- [ ] `docs/posting_queue.md` has ≥1 row with `Status = posted YYYY-MM-DD`
- [ ] G3 signal captured for that row after 48h
- [ ] Session state Branch 1.3 updated

Current status: **G0 PENDING** — Edward has not yet posted SOP #01 (first row in posting_queue.md).
Critical path: SOP #01 post → M1 milestone → velocity flywheel starts → SOP #82 tracker activates.

---

## Integration

| SOP | Link |
|-----|------|
| SOP #78 | Posting Operations — thread file format |
| SOP #81 | Distribution Velocity — flywheel mechanism |
| SOP #82 | Revenue Activation Milestone Tracker — M1→M7 milestones |

---

*SOP #01~#83 COMPLETE ✅*
