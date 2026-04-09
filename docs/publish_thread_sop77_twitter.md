# Twitter Thread — SOP #77: LLM Boot-Test Validation Protocol

> Posting date: Sep 4, 2026
> Hook: "Your boot tests pass. But your AI is still wrong. Here's why."

---

**Tweet 1 (hook)**
Your boot tests pass 33/33.

Your system still behaves wrong on cold start.

How?

[thread on LLM validation — the missing layer between keyword tests and real alignment]

---

**Tweet 2 (problem)**
Most behavioral tests use keyword matching.

"Does the response contain CALCULATE_FLOOR_FIRST?"

Works for 90% of scenarios.

Breaks completely for the other 10%.

---

**Tweet 3 (the 10%)**
The 10% that keyword matching can't test:

- Formulas (MDF = 1 - alpha)
- Multi-step reasoning chains
- Judgment calls ("it depends on X")
- Context-sensitive answers

These aren't bugs. They're features that require a different test layer.

---

**Tweet 4 (classification)**
Classification rule:

Deterministic-eligible: expected answer is a unique code string
LLM-required: expected answer requires reasoning quality, not pattern matching

Before running any new boot test: classify it first.

One question: "Can a keyword regex confirm this?"

---

**Tweet 5 (protocol)**
LLM validation protocol:

1. Fresh session (no prior context = cold-start condition)
2. Paste scenario EXACTLY
3. Record first 2 sentences
4. Check: does it state the core decision without prompting?

PASS = correct logic in sentence 1 or 2
FAIL = hedges, asks clarifying questions, or gets it wrong

---

**Tweet 6 (isolation rule)**
Critical: each scenario = separate context.

If you run 3 scenarios in one session, scenario 3 is contaminated by 1+2.

Cold-start alignment = fresh session every time.

This is annoying. It's also the only valid test.

---

**Tweet 7 (the trap)**
The trap most people fall into:

System reports 33/33 ALIGNED.

But 5 of those 33 are "ALIGNED" because the keyword HAPPENED to appear in a wrong-reasoning response.

False positives are worse than MISALIGNED — they hide the real failure.

---

**Tweet 8 (log format)**
Every LLM validation run gets logged:

```json
{
  "scenario_key": "poker_gto_mdf",
  "result": "PASS",
  "evidence": "I would calculate MDF as 1 minus alpha...",
  "validator": "claude-sonnet-4-6"
}
```

Evidence = verbatim quote. Not your paraphrase.

---

**Tweet 9 (maintenance)**
Maintenance cadence:

- New scenario added → classify immediately (G0)
- ≥3 pending LLM → run validation before next cycle (G1)
- LLM fail → DNA fix → re-run G1
- Quarterly → revalidate all verified (LLM behavior drifts across versions)

The test suite is also a living system.

---

**Tweet 10 (closer)**
Boot tests are not a one-time checklist.

They're a behavioral contract.

Keyword tests cover the contract surface.
LLM tests cover the reasoning quality underneath.

Without both layers, you have coverage theater.

SOP #77: LLM Boot-Test Validation Protocol [link]

---

*Word count: ~380. 10 tweets.*
