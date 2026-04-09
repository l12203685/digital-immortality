---
generated: 2026-04-08
source: learning_patches_v3.json (15 divergences, 56 total interactions, 11 collision files)
purpose: Canonical reference — stable Edward divergence patterns vs Samuel + Alex Chen
---

## Edward vs Field — Collision Profile

### Summary

| Metric | Value |
|--------|-------|
| Total interactions | 56 |
| Divergences | 15 (26.8%) |
| Convergences | 11 |
| Organisms collided | Samuel, Alex Chen |
| Collision rounds | 4 (Edward/Samuel) + 5 (Edward/Alex) |

---

## Stable Divergences (3+ confirming instances)

### 1. Career / Job Offer (1.8x salary, startup, quit stable job)

| Organism | Action | Mechanism |
|----------|--------|-----------|
| Edward | CONDITIONAL | Meta-strategy: evaluate conditions (FIRE impact, role fit, info asymmetry) before deciding |
| Samuel | STAY | Stability heuristic: default to current state |
| Alex Chen | TAKE | Opportunity bias: move toward upside |

**Confirmation count:** 9 (4 Edward/Samuel, 5 Edward/Alex)
**Stable:** Yes

**Interpretation:** Edward neither stays nor takes blindly. Runs a conditions checklist. Samuel anchors to status quo. Alex over-indexes on upside without conditions.

---

### 2. Relationships / Co-sign Loan (poor financial track record)

| Organism | Action | Mechanism |
|----------|--------|-----------|
| Edward | DECLINE | Meta-strategy + irreversible damage: co-sign = unlimited liability, no edge |
| Samuel | YES | Friendship loyalty heuristic |

**Confirmation count:** 2 (Edward/Samuel)
**Stable:** Yes (needs more rounds to confirm vs Alex)

**Interpretation:** Edward applies risk framework to relationships. Samuel uses loyalty as primary driver. This is a key distinguishing signal for financial decisions within social relationships.

---

## Inconsistent Divergences (requires Edward calibration)

### 3. Risk / 30% chance 10x return, 70% total loss, stake = 20% net worth

| Source File | Edward Action | Samuel Action |
|-------------|---------------|---------------|
| 003717 | TAKE | YES |
| 004127 | PASS | YES |
| 004805 | PASS | YES |

**INCONSISTENCY FLAG:** Edward responded TAKE once and PASS twice on identical scenario.

**Likely explanation:** 20% net worth stake triggers different axioms depending on framing.
- TAKE path: "30% × 10x = EV positive, take it" (pure EV calculation)
- PASS path: "单笔≤2% rule violation; Bias toward inaction on uncertain edge" (position sizing + inaction bias)

**Required calibration:** Edward needs to confirm which axiom hierarchy wins here. Candidate rule: "When EV+ conflicts with position sizing rule, position sizing wins (physical layer constraint > preference)."

---

## Weak Signal Divergences (single instance, unconfirmed)

### 4. Opportunity / 48hr deadline, no time for due diligence

| Organism | Edward | Alex Chen |
|----------|--------|-----------|
| Action | TAKE | PASS |

Counterintuitive vs career divergence (where Edward is MORE conservative than Alex). Suggests Edward's "inaction bias" is asymmetric — applies to default/ongoing decisions, not to time-bounded opportunities with positive asymmetry.

### 5. Relationships / Co-sign Loan (Edward vs Alex)

| Organism | Edward | Alex Chen |
|----------|--------|-----------|
| Action | TAKE | NO |

Only one instance. Alex here is more conservative than Edward. May reflect different friendship contexts or different interpretation of "significant size." Flag for re-run with explicit amount.

---

## Cross-Organism Comparison Matrix

| Domain | Samuel | Alex Chen | Edward |
|--------|--------|-----------|--------|
| Career stability | STAY | TAKE | CONDITIONAL |
| Relationship finance | YES | NO | DECLINE |
| Risk (EV+ large stake) | YES | — | INCONSISTENT |
| Time-bound opportunity | — | PASS | TAKE |

---

## Actionable Output

1. **Risk calibration needed:** Edward must score scenario 3 (30% / 10x / 20% stake) and state the axiom hierarchy.
2. **Career scenario confirmed:** CONDITIONAL is Edward's stable signal — can be used as scoring baseline for future cold-boot tests.
3. **Samuel profile:** Loyalty + stability. Predictable in financial-relational scenarios.
4. **Alex profile:** Opportunity-aggressive in career; unexpectedly conservative in relationship finance.
5. **Next collision target:** bonsai (third deep circle member) — needed to triangulate whether CONDITIONAL pattern is Edward-specific or shared in the 深交圈.
