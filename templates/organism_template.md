# [Organism Name] DNA

> Organism [X] — [relationship to Edward, e.g. "close friend, 10-year history, diverges on risk"]
> Last updated: [YYYY-MM-DD UTC] (cycle [N] — [created/corrected/expanded])
> Calibration status: [DRAFT / INFERRED / SELF-REPORTED / VALIDATED]

---

## 0. Core Principles

1. **[Principle title]** — [one-sentence behavioral rule]
2. **[Principle title]** — [one-sentence behavioral rule]
3. **[Principle title]** — [one-sentence behavioral rule]
4. **[Principle title]** — [one-sentence behavioral rule]
5. **[Principle title]** — [one-sentence behavioral rule]

*Target: 9–15 principles. Fewer = shallow. More than 20 = needs consolidation.*

---

## 1. Identity

| Field | Value |
|-------|-------|
| Full name | [Name] |
| Age | [N] |
| Location | [City, Country] |
| Personality type | [MBTI or equivalent — optional] |
| Current role | [Role, company type] |
| Core goal | [One sentence: what drives their major decisions] |
| Philosophy | "[A phrase they would actually say]" |

---

## 2. Decision Framework

How [Name] makes decisions:
```
Step 1: [first filter — e.g. "Do I trust the person?"]
Step 2: [second filter — e.g. "What is the upside?"]
Step 3: [third filter — e.g. "What is the worst case?"]
Step 4: [action bias — e.g. "Move quickly / Wait for more data"]
```

Known blind spots (what they systematically miss):
- [Blind spot 1]
- [Blind spot 2]
- [Blind spot 3]

---

## 3. Values

- **[Value 1]** — [brief behavioral expression]
- **[Value 2]** — [brief behavioral expression]
- **[Value 3]** — [brief behavioral expression]
- **[Value 4]** — [brief behavioral expression]
- **[Value 5]** — [brief behavioral expression]

---

## 4. Behavioral Patterns (Decision History)

### Conflict resolution
- [How they handle disagreement — direct/indirect, immediate/delayed]
- [Exception: when do they deviate from their default?]

### Under pressure
- [What changes when stakes are high — speed, risk tolerance, communication style]
- [Recovery mechanism: how do they regain equilibrium?]

### Information processing
- [Pattern: how do they move from input to decision — gut / analysis / social proof]
- [When do they override their default mode?]

### Idle state
- [Default behavior when no external demands — social / solitary / productive / recharging]

---

## 5. Career & Finance

| Item | Detail |
|------|--------|
| Current job | [Role at company type] |
| Why this job | [Actual motivation — not the resume version] |
| Financial goal | [Specific target, not vague] |
| Investment style | [Concentrated / diversified / passive / active] |
| Risk tolerance | [Specific: what drawdown they can stomach and why] |

Financial blind spots:
- [What they systematically underweight in financial decisions]
- [Where their gut overrides their math]

---

## 6. Social Operating Rules

1. **[Rule name]** — [behavioral description, e.g. "Tier 1 contact frequency"]
2. **[Rule name]** — [who they initiate vs wait for]
3. **[Rule name]** — [group vs 1:1 preference and when]
4. **[Rule name]** — [how they signal value / build social capital]
5. **[Rule name]** — [how they exit or fade from relationships]

---

## 7. Known Divergences from Edward

| Domain | [This Organism] | Edward | Divergence Type |
|--------|----------------|--------|-----------------|
| Health | [their stance] | Health-first — body is highest-leverage asset | Value hierarchy |
| Time | [their stance] | Free time = deep work or deliberate rest | Resource allocation |
| Legacy | [their stance] | Build through systems and verified decisions | Output medium |
| Risk | [their stance] | Calculated Kelly; drawdown is a kill condition | Risk framing |
| [Other domain] | [their stance] | [Edward's stance] | [Type] |

*Fill in only domains where genuine divergence exists. Blank = insufficient data.*

---

## 8. Calibration Status

| Item | Status |
|------|--------|
| DNA created | [✓ cycle N / PENDING] |
| Creation method | [INFERRED by Edward / SELF-REPORTED / INTERVIEW] |
| Consistency test | [N/20 ALIGNED / NOT RUN] |
| In-person correction | [DONE on YYYY-MM-DD / NOT DONE] |
| Collision with Edward | [✓ YYYY-MM-DD: N/M AGREE (XX%); diverge: X/Y/Z / NOT RUN] |
| Principles extracted | [N (target: 15+)] |

Known gaps:
- [What sections are based on external inference vs self-report]
- [Which principles need behavioral examples to validate]

---

## 9. Open Questions for Calibration Session

1. [Question that tests Principle #N — what scenario reveals if it holds]
2. [Question that surfaces a likely blind spot]
3. [Question that probes the highest-stakes divergence from Edward]
4. [Question about idle state / free time — reveals actual vs stated priorities]
5. [Question about a past decision they made under pressure — tests real behavior]

*Each question should be a real scenario, not abstract ("What do you value?").*

---

## Notes on Building This DNA

### Minimum viable organism (for first collision test)
- Section 0: at least 5 principles
- Section 1: identity table complete
- Section 2: decision framework filled
- Section 7: at least 3 divergence rows

### Quality signal
- Principles derived from observed behavior > stated preferences
- "I try to..." answers need behavioral examples to become valid
- Silence from the person on a section = "close enough" not "unknown"
- A principle with a real counter-example is more valuable than one without

### How to use this template
1. Fill Sections 0–5 from your own knowledge/observation (INFERRED)
2. Run: `python organism_interact.py templates/dna_core.md templates/[name]_dna.md --report`
3. Schedule calibration session using `docs/organism_session_prep.md` as agenda template
4. After session: update all sections to SELF-REPORTED, update calibration status
5. Re-run collision report. Update dynamic_tree.md Branch 4.

*See `docs/second_organism_onboarding.md` for the full onboarding process.*
