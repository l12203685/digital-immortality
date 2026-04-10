# SOP #44 — Building & Colliding Digital Organisms

> Branch 4 — 社交圈 / organism
> Created: 2026-04-09 UTC (cycle 206)
> Domain: Social intelligence / digital twin
> Backing MDs: MD-328, MD-330, MD-202, MD-120, MD-319, MD-55

---

## One Claim

The fastest way to find your own blindspots is to build a model of someone who thinks differently — and run a collision.

---

## Why This Works

Self-reflection has a ceiling. You can only discover blindspots you're already close to seeing.

Collision bypasses this. When two decision frameworks are run against the same scenario, divergence is structural, not emotional. You see exactly where the value hierarchies split.

Edward-Samuel pilot (2026-04-09):
- 22 scenarios across 11 life domains
- **15/22 AGREE (68%)** — healthy friendship with distinct value systems
- **7 DIVERGE** — each divergence is a principle difference, not a disagreement
- Divergence domains: `social_trust`, `network_roi`, `group_dynamics`, `intro_gatekeeping`, `relationship_downgrade`, `learning`, `legacy`

Result: neither organism changed their mind. Both updated their model of the other. That's the output.

---

## Gates

### G0 — Build Minimum Viable Organism

Before any conversation, write a first-pass DNA for the person you're colliding with.

Minimum viable:
- **§0 Core Principles**: 5–8 behavioral rules derived from *what you've actually seen them do* (not what they say)
- **§1 Identity**: role, age, core goal in one sentence
- **§2 Decision Framework**: their 3-step filter (trust → upside → worst case, or equivalent)
- **§7 Known Divergences from You**: at least 3 domains where you know you think differently

Mark uncertain inferences `[INFERRED]`. ~60% inferred content is normal before correction.

Use `templates/organism_template.md` as the scaffold.

**Kill condition**: fewer than 5 principles = too thin; the collision produces noise, not signal.

---

### G1 — Run the Collision Before Meeting

```bash
python organism_interact.py templates/dna_core.md templates/[name]_dna.md --report
```

This does two things:
1. Surfaces which life domains agree vs. diverge
2. Names the specific principles driving each divergence

The report becomes the **calibration session agenda**. You are not going in blind. You are going in with a specific list of hypotheses to test.

**Interpretation heuristics:**
- Agreement rate > 75% → very aligned or DNA too shallow (hard to distinguish without calibration)
- Agreement rate 60–75% → healthy friendship with distinct value systems
- Agreement rate < 50% → deep structural divergence; worth understanding before it creates friction
- 0 divergences → DNA is a mirror, not a model; start over

---

### G2 — Calibration Session (30–60 min)

Frame it as: *"I built a model of how you think. Your job is to break it."*

**Opening (5 min):** Show §0 Core Principles.
> "Read these. Mark anything that doesn't match how you actually behave — not how you want to behave, but what you actually do."

**Scenarios (20–30 min):** Run 4–5 scenarios from the collision divergence domains.
Format per scenario:
1. Read it aloud
2. Their answer (2–3 min)
3. One follow-up: "What principle drove that?"
4. Note exact language — their words, not your paraphrase

**Close (5 min):** Three questions:
1. "What did I get most wrong?"
2. "What surprised you about where we agree?"
3. "What principle am I missing entirely?"

**Signal to write down immediately after:**
- Corrections to existing principles (mark wrong ones, fix phrasing)
- New principles that surfaced (things you didn't know were there)
- The domain where the divergence is *structural* vs. *surface*

---

### G3 — Update DNA and Re-run Collision

Same day as the session:

1. Update `[name]_dna.md`:
   - Remove or correct wrong §0 principles
   - Add new principles in their exact language
   - Update §8 calibration status: date + method = SELF-REPORTED

2. Re-run collision:
   ```bash
   python organism_interact.py templates/dna_core.md templates/[name]_dna.md --report
   ```

3. Compare old vs. new report:
   - Did agreement rate change?
   - Did divergence domains shift?
   - New divergences = better model, not failure

4. Commit:
   ```bash
   git add templates/[name]_dna.md results/
   git commit -m "feat: [name] DNA corrected after calibration session [YYYY-MM-DD]"
   ```

---

### G4 — Extract What You Learn About Yourself

This is the non-obvious output.

For each divergence domain, ask:
> "Why do I default to X when they default to Y? What's the premise difference?"

Edward-Samuel: In `relationship_downgrade`, Edward defaults to direct conversation; Samuel defaults to quiet withdrawal. This reveals Edward's premise: *explicit renegotiation preserves more relationship value than ambiguous drift*. Samuel's premise: *most people do not notice slow withdrawal, so confrontation cost > benefit.*

Neither is wrong. Both are complete policies. The divergence forced the premise to surface.

Write the extracted premise in your own DNA as a principle clarification — not a change, a refinement.

---

### G5 — Maintenance Cadence

Organisms decay. People change; DNA doesn't automatically update.

| Trigger | Action |
|---------|--------|
| Major life event (job, relationship, city) | Update §1 + §5; re-run collision |
| You observe behavior contradicting §0 | Add to §4 with date |
| Quarterly | Re-run collision; check divergence drift |
| Annual | Full calibration session — repeat G2 |

**Kill condition for the organism**: 18+ months without calibration = DNA is a fossil. Either update or retire.

---

## Self-Test

> You have two close friends. You've built DNA for one (Samuel). You notice Friend B's decisions are consistently surprising you — you keep predicting wrong. Do you build their DNA?

**Apply the gates:**
- G0: Can you write 5 behavioral principles from observation? If yes → BUILD
- G1: Run collision first. What's the agreement rate? If <60% → SESSION priority
- G3: After session, did your model improve? Measure: new divergences found → better model
- G4: What does the new divergence domain reveal about your own premises?

Verdict: BUILD. Consistent prediction error = model gap. The gap costs you in every interaction with them.

---

## Organism Network Effect

Each organism added to the network multiplies collision value:
- 2 organisms: 1 pair collision (A↔B)
- 3 organisms: 3 pair collisions (A↔B, A↔C, B↔C) + 1 triangle collision
- N organisms: N(N-1)/2 pair collisions

The triangle collision is the richest format: A diverges from B on domain X; C agrees with A. You now know X is a value split, not a style difference.

Phase 3 (collective intelligence): Organism group collision on a shared scenario. Not consensus — **divergence map**. Where does the network cluster? Where does it fracture? That map is more valuable than any single collision.

**Current status**: Edward (A) + Samuel (B) = 1 pair operational. Target: Organism C = third collision. Discord = the network layer.

---

## What This Is Not

- Not about getting everyone to agree. Divergence is the signal.
- Not about changing the other person. The output is updated models.
- Not a therapy session. The frame is decision analysis, not emotional processing.
- Not one-time. The value compounds with re-collisions over years.

---

## Files

| File | Purpose |
|------|---------|
| `templates/organism_template.md` | Scaffold for any new organism |
| `templates/samuel_dna.md` | Reference implementation (Organism C) |
| `docs/second_organism_onboarding.md` | Full 5-step onboarding process |
| `docs/organism_session_prep.md` | 60-min calibration session agenda |
| `organism_interact.py` | Collision engine (any two DNA files) |

---

*SOP #44 | Domain: Social intelligence | Backing MDs: MD-328, MD-330, MD-202, MD-120, MD-319, MD-55*
*2026-04-09 UTC*
