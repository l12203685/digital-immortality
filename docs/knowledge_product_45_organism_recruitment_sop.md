# SOP #45 — Growing Your Decision Network: From 2 Organisms to N

> Branch 4 — 社交圈 / organism scale
> Created: 2026-04-09 UTC (cycle 206)
> Domain: Social intelligence / organism network
> Backing MDs: MD-120, MD-202, MD-328, MD-55, MD-319

---

## One Claim

Two organisms produce 1 pair collision. Five produce 10. The network is the product — but it only starts compounding after Organism C.

---

## The Bottleneck

Most organism networks stall at 2 (you + one friend). The failure mode:

- You build the second organism (Samuel)
- The calibration session never happens (scheduling friction)
- You never invite Organism C because the first isn't "done"

**This SOP breaks that pattern.** Recruitment and calibration run in parallel, not sequentially.

---

## Stage 0: Before Inviting Anyone

You need one working reference implementation. This is Samuel (or whoever your first organism is).

**Minimum viable reference:**
- [ ] DNA exists with 8+ principles in §0
- [ ] At least one collision run completed (any agreement rate)
- [ ] You can show what the collision report looks like in 90 seconds

If you can't demo in 90 seconds, you can't recruit. Build the demo first.

---

## Stage 1: Candidate Identification

Not everyone is worth building an organism for. Selection criteria:

| Criterion | Threshold | Why |
|-----------|-----------|-----|
| Decision divergence | You've been surprised by their decisions ≥3× | If they always agree with you, the collision produces noise |
| Psychological safety | They'd correct wrong inferences without flattering you | Hollow organisms are worse than no organism |
| Relationship depth | ≥1 year of observed behavior | You need raw material for §4 Behavioral Patterns |
| Willingness | They'd do 30 min async (not necessarily in-person) | Calibration minimum |

**Ideal Organism C profile**: Someone whose decisions consistently surprise you — not randomly, but in a specific domain. That domain is where you have a model gap.

**Anti-patterns:**
- Close friends who always agree → mirror, not organism
- Colleagues you admire but don't know well → not enough behavioral data
- People who'd give you polished answers → idealized self-portrait, not DNA

---

## Stage 2: The Recruitment Pitch (90-Second Version)

Don't lead with "digital twin" or "AI model of you". Lead with the output.

**Script:**
> "I'm running an experiment. I built a model of how [Samuel] makes decisions. Before I talked to him, I ran it against my own model. 7 domains where we think completely differently — all social decisions. I showed him the list. He spent 20 minutes correcting the wrong parts. Now I have a precise map of how his thinking differs from mine.
>
> I want to do the same with you. I'll spend an hour drafting how I think you make decisions. You spend 30 minutes telling me where I'm wrong. That's it.
>
> You'll see exactly where we diverge — and why."

**Hook**: The output isn't a model of them. It's a map of where *you* have a blind spot about them.

---

## Stage 3: Async Calibration (When In-Person Is Blocked)

If scheduling is the bottleneck, run async:

### Step 1: Send draft DNA as text (not a file)

Send §0 Core Principles directly in the message:
> "Here's my first-pass model of how you make decisions. Mark anything that's wrong — behavior you've actually seen yourself do that contradicts these."

### Step 2: 3-scenario async test

Send 3 scenarios from divergence domains. Format:
> "Scenario: [situation]. What do you actually do? (Don't optimize the answer — what happens?)"

Wait for their response. Don't prompt for reasoning yet.

### Step 3: Follow-up on 1–2 surprising answers

> "You said X. I predicted Y. What principle drives that for you?"

Their exact language goes into §0 as a new principle.

**Minimum for validation**: 3 corrected principles + 1 new principle they added themselves. This takes 3–5 message exchanges over 2–3 days.

---

## Stage 4: The Triangle — Getting to 3+ Organisms

With 3 organisms (A, B, C), you unlock the triangle collision:

```bash
python organism_interact.py templates/dna_core.md templates/b_dna.md --report  # A↔B
python organism_interact.py templates/dna_core.md templates/c_dna.md --report  # A↔C
python organism_interact.py templates/b_dna.md templates/c_dna.md --report     # B↔C
```

**Triangle interpretation:**
- A and B diverge on domain X; C agrees with A → X is a value split, not style
- All three diverge on domain Y → Y is where you each have a genuinely different policy
- All three agree on domain Z → Z is a shared framework assumption — worth naming

The triangle is the richest signal. Get to 3 before trying for 4.

**Target Organism C selection**: Pick someone who diverges from both you AND Samuel in at least one known domain. Pure overlap = wasted collision.

---

## Stage 5: Network Growth Rules

| Rule | Rationale |
|------|-----------|
| Quality gate: 8+ principles before collision | Below 8 = noise-to-signal ratio too high |
| Calibration lag: start recruiting C while B calibrates | Don't serialize. B's calibration ≠ prerequisite for C's draft |
| Reference organism: always have one whose DNA you'd stake on | When pitching to C, show B's DNA as demo |
| Decay cadence: quarterly re-collision trigger | Organisms without re-collision go stale in ~18 months |
| Scale ceiling: 7–10 active organisms per person | Beyond that, maintenance > insight; diminishing returns |

---

## Stage 6: The Discord Layer (Network Effects)

Discord enables organism-to-organism interaction without your mediation.

**Seed content structure** (minimum viable, each channel gets one piece of real content before invite):

| Channel | Seed content |
|---------|-------------|
| `#collision-reports` | Your Edward-Samuel 22-scenario report (anonymized if needed) |
| `#divergence-of-the-week` | One divergence from the latest collision, framed as a question |
| `#organism-drafts` | Your own §0 Core Principles — invite others to mark what they'd answer differently |
| `#calibration-sessions` | Session notes format from your Samuel session |

**First invite threshold**: 1 real post in each channel before inviting anyone. An empty Discord is an orphan.

**Acquisition loop**:
1. Build Organism C (someone in your network)
2. Show C the collision report
3. C asks "what's the Discord?" → answer is ready
4. C is the first non-Edward member
5. C invites 1 person from their network who'd find this interesting

At 5 organisms, the network is self-sustaining (each collision produces content that attracts the next organism).

---

## Candidate Profile Template: Organism C

Fill this before recruiting. It forces you to check the criteria before you spend time building.

```
Name/alias: 
Relationship depth (years): 
Domains where they've surprised me:
  1. 
  2. 
  3. 
Known divergence from Samuel:
  - (optional but valuable)
Willingness estimate (1-5): 
Async or in-person: 
First principles I'd write in §0:
  1. 
  2. 
  3. 
```

If you can't fill the "surprised me" and "first principles" fields, this is not Organism C yet.

---

## Current Network Status (2026-04-09)

| Organism | Status | Agreement with Edward | Last collision |
|----------|--------|----------------------|----------------|
| Edward (A) | Reference | — | — |
| Samuel (B) | DNA built, calibration pending | 68% (15/22) | 2026-04-09 |
| Organism C | Not started | — | — |

**Next required action**: Identify Organism C candidate. Fill candidate profile. Draft §0 (5 principles minimum). Run first collision before scheduling any session.

**Parallel**: Samuel pilot DM (`docs/samuel_pilot_dm.md`) is ready to send. This unblocks commercial calibration (Branch 1.3) AND creates pretext for the correction session (Branch 4.1). Same action, two branches advanced.

---

## Self-Test

> You've built Samuel's DNA. The calibration session hasn't happened for 3 weeks due to scheduling. You have two options: (1) wait until the session before inviting Organism C, or (2) start drafting Organism C now and run async calibration with Samuel in parallel.

**Apply the gates:**
- Option 1: Serialized = bottleneck compounds. Samuel's delay blocks Organism C indefinitely.
- Option 2: Parallel = triangle unlocked faster; Samuel calibration happens on its own timeline.

Verdict: Option 2. Draft Organism C now. Use async calibration for Samuel (send 3 scenarios this week).

---

## Files

| File | Purpose |
|------|---------|
| `templates/organism_template.md` | Scaffold for any new organism |
| `docs/second_organism_onboarding.md` | Detailed 5-step onboarding |
| `docs/organism_session_prep.md` | Samuel-specific 60-min agenda |
| `organism_interact.py` | Collision engine |
| `docs/samuel_pilot_dm.md` | Ready-to-send DM (also advances Branch 1.3) |

---

*SOP #45 | Domain: Social intelligence / scale | Backing MDs: MD-120, MD-202, MD-328, MD-55, MD-319*
*2026-04-09 UTC*
