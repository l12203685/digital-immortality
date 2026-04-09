# SOP #62 — Social Capital & Relationship Investment Protocol

> UTC: 2026-04-09 | Domain: 4 (社交圈 / Social Capital)
> Backing MDs: MD-328/329/330/134/232/265/270

---

## The Core Problem

Relationships compound — or decay. Most people treat social capital as a byproduct of activity, not an asset to be actively managed. This SOP makes relationship investment auditable, derivative-driven, and compounding.

A digital twin without social coverage is a ghost: behaviorally accurate but socially absent. Organism interaction reveals decision divergence no self-reflection can surface.

---

## Gates

### G0 — Relationship Inventory Audit

Map current relationship graph:
- List active relationships (last contact ≤ 90 days)
- Classify by tier: T1 (highest compounding — close collaborators, calibration partners), T2 (periodic reinforcement), T3 (weak ties with option value)
- Calculate: days since last meaningful contact per T1 relationship
- Kill condition: any T1 relationship >30 days → G5

Signals:
1. T1 contact rate (target: ≥1 per 14 days per relationship)
2. Organism calibration sessions completed this quarter
3. Collaborative output shipped (joint projects, referrals, introductions)

### G1 — Derivative Scan

Track change rate, not level:
- ΔT1 contact frequency (rising/falling)
- ΔCollaborative output rate
- ΔOrganism collision sessions (scheduled vs completed)

If all three are falling: root cause = attention budget leak → redirect from low-EV social activity.

### G2 — Non-Negotiable Investment Budget

Commitments that cannot be skipped:
- Proactive reach-out: ≥1 T1 message per 14 days per relationship (not reactive — scheduled)
- Organism calibration: ≥1 session per month (Samuel, or any calibration partner)
- Result-reporting: after any introduction or referral, close the loop within 7 days
- No ghosting after high-context conversations — follow-up within 48h

Apply: MD-328 (MAINTAIN_PROACTIVE_CADENCE) — relationship investment is a scheduled output, not a reactive response.

### G3 — Quarterly Organism Leverage Scan

Identify the highest-derivative social move each quarter:
- Which relationship has highest compounding potential (EV × time horizon)?
- Which organism collision would surface maximum decision divergence?
- Identify one new organism to model (organism_c or beyond)

Select one 90-day trial: deepen one T1 or calibrate one new organism. Measure ΔDecision quality from collision, ΔOpportunities surfaced from referrals.

If ΔOutput ≥ +20% from pre-trial baseline → make permanent.

### G4 — Weekly Review (10 min Sunday)

Audit:
- T1 contacts made this week (count / scheduled)
- Organism calibration: sessions this month (on track?)
- Follow-ups outstanding (>48h) → resolve immediately
- Queue: next highest-derivative relationship action

### G5 — Emergency: Social Debt Protocol

Trigger: any T1 >30 days, OR organism calibration gap >45 days, OR ≥3 pending follow-ups.

Recovery:
1. Send one proactive message to highest-priority T1 today (no context required, short is fine)
2. Schedule organism calibration within 7 days
3. Resolve all pending follow-ups before any new social outreach
4. No G3 experiments until G0 is green ×2 weeks

---

## Three-Layer Integration

| Layer | Gate | What it does |
|-------|------|--------------|
| L1 Execute | G2 investment budget | Non-negotiable proactive cadence |
| L2 Evaluate | G0/G1 audit | Detect decay before it compounds |
| L3 Evolve | G3 leverage scan | Identify which relationship has highest EV this quarter |

---

## DNA Connections

| MD | Principle | Gate |
|----|-----------|------|
| MD-328 | Maintain proactive cadence — relationship investment is scheduled, not reactive | G2 |
| MD-329 | Build skeleton first — new social structure before populating contacts | G3 |
| MD-330 | Verify by behavior pattern — social signal reading is behavior, not words | G0 |
| MD-134 | Organism collision > self-reflection for uncovering blind spots | G3 |
| MD-232 | Partner financial design = two-layer system; relationship structures need architecture | G0 |
| MD-265 | Range thinking > single hand — read relationships as population distributions | G1 |
| MD-270 | Optimal decision ≠ correct decision — social EV ≠ social comfort | G3 |

---

## Organism Interaction Protocol

This SOP governs the human layer of what `organism_interact.py` operationalizes:

```
python organism_interact.py dna_a.md dna_b.md --all
```

- Run ≥ 1 collision session per month with a calibration partner
- Document divergences in memory/calibration.json
- Every divergence = new boot test candidate + new MD candidate
- Organism collision reveals what solo recursion cannot: edge cases in value structure

Current organisms:
- **Edward** (self): templates/example_dna.md
- **Samuel**: templates/samuel_dna.md (19/20 ALIGNED; async calibration DM ready)
- **Organism C**: templates/organism_c_draft.md (§0+§7 pending Edward input)

---

## Branch 4 Blockers (human-gated)

1. **Samuel async DM**: paste `docs/samuel_async_calibration_dm.md` via WhatsApp/LINE
2. **Discord seeding**: paste 4 seed posts (docs/discord_seed_*.md) → invite C
3. **Organism C**: fill §0 + §7 in `templates/organism_c_draft.md`

These are the highest-derivative social moves. Nothing in G3 has higher EV until these three are cleared.
