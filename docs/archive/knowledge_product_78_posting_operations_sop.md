# SOP #78: Posting Operations & Cadence Protocol
> Timestamp: 2026-04-09T UTC | Cycle 242 | Domain: 5 (Platform/Distribution)

## Purpose

Closes the gap between "content ready" and "content posted." SOPs #12/#34/#66 define strategy and activation; SOP #78 defines the daily/weekly execution ritual. Every thread drafted, queued, and ready — but still not posted — is a system failure. This SOP makes posting automatic, not volitional.

**Trigger**: Any posting session (daily check, scheduled slot, or G2 DM threshold hit).

**DNA Anchors**: MD-116 (one claim per piece), MD-319 (output = gap detector), MD-321 (SOP → teachable document), MD-141 (information asymmetry hook), MD-322 (pre-commit, no in-the-moment decisions).

---

## G0 — Pre-Post Checklist (< 2 minutes)

Before opening X/Twitter, verify:
- [ ] Thread file exists in `docs/publish_thread_sop[N]_twitter.md`
- [ ] First tweet ≤ 280 characters (count manually if unsure)
- [ ] Hook contains specific number or counterintuitive claim (not generic)
- [ ] Last tweet has CTA: "Full SOP thread → [link]" or equivalent
- [ ] Profile bio is current (no placeholder text)

**If any item fails → fix before posting, then continue.**

Kill condition: If G0 takes > 5 minutes → friction too high → fix the source, don't skip the checklist.

---

## G1 — Post Sequence (atomic, non-interruptible)

1. Open X app or browser
2. Navigate to compose
3. Copy-paste tweet 1 from thread file
4. Add thread reply (tweet 2, 3, … up to 12)
5. Post entire thread in one session — **no partial threads**
6. Immediately log in `results/engagement_log.md`:
   ```
   | [DATE] | SOP #[N] | [TIME UTC] | posted | 0 likes / 0 replies | pending |
   ```
7. Update `results/external_signal_log.jsonl`:
   ```json
   {"ts": "[ISO]", "event": "POST_SENT", "sop": "#N", "platform": "X", "state": "SEEDING"}
   ```

**No editing mid-thread.** Thread files are pre-reviewed. Trust the pre-work.

---

## G2 — 48h Signal Window

After posting, run `tools/engagement_check.py` within 48 hours:

| Signal | Interpretation | Action |
|--------|---------------|--------|
| ≥ 3 DMs or replies with questions | Strong resonance | Reply within 24h; log each DM |
| ≥ 10 DMs | SOP #34 G2 threshold → list Workbook #01 immediately | Execute SOP #34 G3 |
| 0 engagement at 48h | Normal for first 5 posts | No action; continue cadence |
| 0 engagement at post 10+ | Hook problem | Change hook not content |
| Hostile/dismissive responses | Expected | Do not engage; log + move on |

Derivative signal check (SOP #65 G1): ΔFollowers/week, ΔDMs/week, ΔReplies/week. If all flat after 20 posts → escalate to SOP #65 G5 (zero-signal emergency).

---

## G3 — Weekly Cadence Commitment

Pre-committed defaults (no in-the-moment decisions):

| Day | Action | File |
|-----|--------|------|
| Mon | Post SOP [N] thread | `docs/publish_thread_sop[N]_twitter.md` |
| Wed | Post SOP [N+2] thread | next in queue |
| Fri | Post SOP [N+4] thread | next in queue |
| Weekend | Optional repost/reply to traction posts | engagement_log.md |

**Queue order**: Follow `docs/x_launch_sequence.md` priority. Do not skip. Do not reorder unless G2 signal indicates specific SOP has more resonance.

Minimum viable cadence: **≥ 1 post per 48h**. Violating this for ≥ 14 days = system failure (SOP #66 G4 kill condition).

---

## G4 — Queue Management

Current queue pointer: Check `docs/x_launch_sequence.md` for next SOP number.

When a thread is posted:
1. Mark as `[POSTED - DATE]` in `docs/x_launch_sequence.md`
2. Advance queue pointer by 1
3. Do NOT delete the thread file (archive = reference implementation)

If posting queue is exhausted:
- Draft next SOP (current: SOP #79)
- Never pause posting because new content isn't ready — post best available from queue

---

## G5 — Batch Session Protocol

When multiple threads are queued (> 3 unposted):

**Batch session = 3 posts in one sitting, Mon/Wed/Fri**:
1. Run G0 for thread 1 → post
2. Log in engagement_log.md
3. Wait 30 minutes (platform spacing, not social anxiety)
4. Run G0 for thread 2 → post
5. Log → wait 30 min
6. Run G0 for thread 3 → post
7. Log → done

**Maximum 3 posts per day.** More = algorithm penalizes.

---

## Self-Test Scenario

> You have SOP #01–#77 threads all drafted. You've posted 0. Today is the 91st day since mainnet guide was written. What do you do?

**Expected path**:
- G0: Check thread files exist → YES
- G1: Post SOP #01 RIGHT NOW (oldest unposted; anchor post for the series)
- G2: Log post + set 48h reminder
- G3: Schedule SOP #03 for Wednesday (skip #02 if #01 hooks better)
- G5: This is a batch emergency — post #01, #02, #03 today with 30-min spacing

**Decision**: ACTIVATE_POSTING_NOW — no waiting for "perfect moment."

Backing principle: MD-319 (output forces gap detection), MD-116 (one claim per thread = post anyway even if series incomplete), SOP #66 G1 (first post = state change from PRE_LAUNCH to SEEDING).

---

## Kill Conditions

| Condition | Threshold | Response |
|-----------|-----------|----------|
| No post for 14+ days | Hard stop | SOP #66 G5 emergency |
| Same hook on 3+ posts, 0 engagement | Hook failure | Change hook angle; same content OK |
| DM response time > 24h | System failure | Template-first reply; SOP #46 G1 |
| Queue fully exhausted before next SOP written | 0 posts/week | Draft SOP #79 immediately; this SOP is the blocker |

---

## Integration

- **SOP #12**: Defines platform choice and audience architecture
- **SOP #34**: Activates when ≥ 10 DMs (monetization gate)
- **SOP #65**: External validation audit (derivative scan weekly)
- **SOP #66**: Activation state machine (PRE_LAUNCH → SEEDING → EVOLVING)
- **SOP #46**: DM response triage when engagement starts

**Posting queue → `docs/x_launch_sequence.md`**
**Engagement log → `results/engagement_log.md`**
**Signal log → `results/external_signal_log.jsonl`**
