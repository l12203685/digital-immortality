# DNA Write — Writing and Updating DNA Files

Best practices for creating and maintaining high-quality DNA documents. Bad DNA = bad twin. The DNA file is the single most important artifact in the system.

## Trigger

Use when: creating a new DNA file, updating existing DNA sections, after calibration sessions, or after correction events.

## Process

1. **Read ALL source material** — not sampling, not skimming. Full read. (Learning Phase from SKILL.md)
2. **Find essence** — distill to cross-domain patterns, not summaries
3. **Cross-domain validation** — same principle must explain behavior in multiple life areas. If it only applies to one domain, it is a fact, not a principle.
4. **Write in DNA format** — follow the template in `templates/example_dna.md`
5. **Verify with boot tests** — run existing tests against updated DNA. If tests break, the edit was wrong.
6. **Version and date** — every DNA update gets a version bump and timestamp

## Quality Principles

### Specificity > Generality
- Write: "Reject any trade with MAE > 2% of account"
- Not: "Manage risk carefully"

### Actions > Beliefs
- Write: "When partner is upset, listen first, then ask one clarifying question before responding"
- Not: "Values empathy in relationships"

### Patterns > Instances
- Write: "Bias toward inaction: no clear edge = no action. Applies to trading, career moves, social commitments."
- Not: "Didn't take the job at Company X in 2024"
- Instances are evidence for patterns. Include them as examples, not as standalone entries.

## DNA Section Priority

Fill sections in this order (most critical first):
1. **BOOT_CRITICAL** — the 3 behavioral rules for the agent
2. **Core Principles** — 3-8 rules that never change, explain all domains
3. **Decision Framework** — how decisions actually get made, with real examples
4. **Communication Style** — tone per context, with actual phrases
5. **Everything else** — relationships, career, daily patterns, values

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Aspirational content ("I value health") | Write actual behavior ("Skip exercise 4/5 weekdays") |
| Abstract principles without examples | Every principle needs 2+ concrete decisions as evidence |
| Duplicate information across sections | Single source of truth per fact, reference from elsewhere |
| Stale entries after life changes | Date all entries, review quarterly, update or mark obsolete |

## Rules

- The person's correction always wins. When corrected, update DNA immediately, don't argue.
- Never delete boot tests when updating DNA. Tests are monotonically increasing.
- If a principle can't explain at least 2 real decisions, it's not a principle yet — it's a hypothesis.
- DNA is never "done." It evolves as the person does.
- Write for a cold-start reader: someone with zero context should understand the person from DNA alone.
