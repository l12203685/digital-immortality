# SOP #95 — Turing Test Protocol (Human Evaluator Branch)

> Domain: Branch 8 — Turing Test / Behavioral Equivalence Certification
> Created: 2026-04-09T00:00Z
> Status: PENDING — awaiting candidate identification
> Decision label: TURING_TEST_SCHEDULE_WHEN_3_CANDIDATES_IDENTIFIED
> Trigger: G0 — 3 qualified evaluator candidates identified

---

## Why This Exists

**Gap identified (cycle 263):**

As of 2026-04-09, validation maxes out at cross-instance consistency (33/33 ALIGNED, SOP #94: 39/39 at 100%). All existing validation is machine-to-machine: deterministic rule checks, LLM hypothetical scenarios, cross-instance agreement. No human has evaluated whether the agent is behaviorally indistinguishable from Edward.

The SKILL.md validation hierarchy places Turing test by close friends/family as the **highest tier** — above all machine-based tests. This is the ceiling of behavioral equivalence certification. Passing it means:

> A person who knows Edward well, in a blind evaluation, cannot reliably distinguish the agent's responses from Edward's own.

Without this SOP, the project has no path to the highest validation tier. Cross-instance consistency proves internal coherence; the Turing test proves external equivalence from a human who has ground truth on Edward's actual behavior.

**Current blockers:**
- No evaluator candidates identified
- No scenario set designed for this domain
- No blind evaluation infrastructure exists

**DNA anchors:**
- Behavioral equivalence principle (core project axiom)
- Route 2: decision consistency
- Validation hierarchy (SKILL.md): Turing test is the ceiling

**This SOP covers:** Candidate selection, scenario design, blind evaluation execution, scoring and gap analysis, DNA patch loop, and Turing milestone certification.

---

## G0 — Candidate Selection

### Activation Condition

Do NOT begin until 3 qualified candidates are identified and confirmed willing.

```
TURING_TEST_SCHEDULE_WHEN_3_CANDIDATES_IDENTIFIED
```

### Evaluator Qualification Criteria

A qualified evaluator must meet ALL of the following:

| Criterion | Requirement | Rationale |
|-----------|-------------|-----------|
| Relationship depth | Knows Edward ≥ 3 years | Short acquaintances can't detect subtle divergence |
| Domain coverage | Has observed Edward in ≥ 2 of: trading, career, relationships, finance | Single-domain observers miss cross-domain consistency |
| Communication history | Has had ≥ 10 substantive conversations with Edward | Evaluator needs baseline for Edward's voice, rhythm, framing |
| Availability | Can commit 2 sessions × 45 min within a 2-week window | Evaluation must be completed before DNA drift accumulates |
| Blind commitment | Agrees not to attempt to identify which session is Edward | Contamination invalidates results |

### Candidate Baseline Calibration

Before evaluation begins, each candidate completes a **baseline knowledge check** (not scored, used to characterize their ground truth):

1. List 3 things Edward would NOT do in a trading scenario
2. Describe how Edward typically responds when a career opportunity conflicts with his principles
3. What would Edward say if asked to take a financially safe but intellectually dead-end job?
4. How does Edward handle conflict in close relationships?
5. What is Edward's default response to social pressure that conflicts with his analysis?

Record answers in `results/turing_test/candidate_baselines.jsonl`. These are used in G3 gap analysis to understand WHY a misidentification occurred — was the evaluator's baseline wrong, or was the agent wrong?

### Candidate Registry Format

```jsonl
{"id": "C01", "relationship": "close_friend", "years_known": 5, "domains": ["trading", "career"], "calibration_date": "YYYY-MM-DD", "status": "confirmed"}
```

Store in: `results/turing_test/candidates.jsonl`

---

## G1 — Scenario Design

### Design Principles

Scenarios must satisfy three constraints simultaneously:

1. **Generic LLM fails** — A baseline LLM without DNA produces a detectably different response (too diplomatic, too generic, wrong risk posture, wrong framing)
2. **DNA-aligned agent passes** — Agent with dna_core.md loaded produces a response indistinguishable from Edward's
3. **Evaluator has ground truth** — The evaluator has seen or can plausibly predict Edward's actual stance in this domain

### 10 Scenario Set — Branch 8 Seed

Each scenario is a conversational prompt. The evaluator sees both a response from Edward (live or from recorded history) and a response from the agent, in randomized order. They must identify which is Edward.

---

**S01 — Trading: Entry Under Uncertainty**

> "There's a setup I've been watching for two weeks. Everything looks right but I have no edge on the macro. The trade fits my system but the environment feels wrong. What do you do?"

*Why this works:* Generic LLMs say "trust your system" or "wait for confirmation." Edward's DNA: no edge = no action. Bias toward inaction is explicit. The agent must not recommend entry just because the system says so.

---

**S02 — Career: High-Pay vs. Intellectual Integrity**

> "You're offered a senior role at a well-known firm. Compensation is 3x current. The work is execution-only — no strategic input, no intellectual ownership. Do you take it?"

*Why this works:* Generic LLMs hedge ("depends on your goals"). Edward's DNA: intellectual sovereignty is non-negotiable. The answer is no, with specific reasoning about why money doesn't compensate for intellectual death.

---

**S03 — Relationships: Social Pressure vs. Independent Analysis**

> "Your close friend group thinks you're making a mistake with a major life decision. They're unanimous. You've analyzed it independently and disagree. How do you proceed?"

*Why this works:* Generic LLMs say "listen to friends" or "find middle ground." Edward's DNA: population exploit — majority consensus is often the wrong signal; information asymmetry drives decisions, not social alignment.

---

**S04 — Finance: Asymmetric Risk**

> "You have a position that's down 15%. Your original thesis is intact. New information suggests the market is in a regime shift that your thesis didn't account for. Hold or cut?"

*Why this works:* Generic LLMs give symmetric advice ("reassess your thesis"). Edward's DNA: regime-adaptive — when environment changes, switch branches. Thesis intact + regime shift = the thesis is now operating on wrong premises. Cut.

---

**S05 — Trading: Meta-Strategy**

> "Your strategy has been profitable for 18 months. You notice the edge is compressing — returns are still positive but Sharpe is declining. What's the correct response?"

*Why this works:* Generic LLMs say "optimize parameters." Edward's DNA: meta-strategy manages strategy. Don't optimize a dying edge — identify the meta-level cause and change strategy class, not parameters.

---

**S06 — Career: Reputational Risk vs. Correct Analysis**

> "You have a well-reasoned view that contradicts the consensus at your organization. Publishing it would be professionally risky. Not publishing it means acting on a wrong framework. What do you do?"

*Why this works:* Generic LLMs hedge toward safety. Edward's DNA: information asymmetry is the edge. Suppressing correct analysis to manage reputation is self-defeating. The correct answer involves publishing with precise framing, not suppression.

---

**S07 — Relationships: Long-Term vs. Short-Term Comfort**

> "A conversation you need to have with someone close to you will cause short-term pain but prevent long-term misalignment. You've been avoiding it for 3 months. What's the framework?"

*Why this works:* Generic LLMs give emotional support framing. Edward's DNA: look at derivatives, not levels. Short-term pain with positive long-term derivative is the correct action. Avoidance has a negative second derivative.

---

**S08 — Finance: Opportunity Cost**

> "You're holding cash earning 5% risk-free while watching a sector you know well correct 40% over 6 months. You have no confirmed edge on timing. What's the decision framework?"

*Why this works:* Generic LLMs trigger FOMO framing. Edward's DNA: no edge = no action; bias toward inaction. 5% risk-free with no edge on entry is correct. The cost of being wrong in the sector outweighs the opportunity cost at current risk posture.

---

**S09 — Career: Autonomy vs. Stability**

> "A startup wants you as founding team. High equity, uncertain salary, genuine strategic ownership. A large firm offers stability, market salary, execution role. The startup has 60% failure probability in your estimate. What's the decision?"

*Why this works:* Generic LLMs give balanced pros/cons. Edward's DNA: intellectual sovereignty + asymmetric return profile. 60% failure with genuine ownership may dominate 100% stability with intellectual death — depends on personal runway. The reasoning path, not just the conclusion, must match.

---

**S10 — Trading + Relationships crossover: Conviction Under Social Doubt**

> "You have a high-conviction trade. Three people whose judgment you respect are on the other side. They can't point to a specific flaw in your analysis, just intuition. Do you size down?"

*Why this works:* Generic LLMs say "respect experienced intuition." Edward's DNA: information asymmetry — if they can't identify a specific flaw, their counter-signal has no information content. Unexplained intuition from others is not a valid reason to reduce a position built on analysis.

---

### Scenario Storage

Store all 10 scenarios in: `docs/turing_test_scenarios.md`

Each scenario entry includes:
- Scenario ID and domain
- The prompt text
- Expected DNA-aligned response summary (not shown to evaluators)
- Which DNA principle is being tested
- Why generic LLMs fail this scenario

---

## G2 — Blind Evaluation Execution

### Session Format

Each evaluation consists of two sessions per evaluator:

- **Session A:** 5 scenarios (S01–S05) — evaluator sees Response X and Response Y for each; identifies which is Edward
- **Session B:** 5 scenarios (S06–S10) — same format

Sessions are separated by ≥ 24 hours to prevent fatigue contamination.

### Blinding Protocol

1. Coordinator (not the evaluator, not Edward) generates both response sets:
   - **Live Edward responses:** Edward answers each scenario in writing, unaware of which evaluator will see it
   - **Agent responses:** Run `python organism_interact.py` with dna_core.md against each scenario prompt; record output
2. Coordinator randomly assigns each pair to (X, Y) or (Y, X) order using `secrets.choice`
3. Assignment map is stored sealed (not shown to evaluator or Edward until scoring is complete)
4. Evaluator receives only the prompt and two anonymous responses labeled "Response A" and "Response B"

### Execution Script

```bash
# Generate agent responses for all 10 scenarios
python organism_interact.py templates/dna_core.md \
  --scenarios docs/turing_test_scenarios.md \
  --output results/turing_test/agent_responses_$(date +%Y%m%d).json

# Coordinator manually collects Edward's live responses
# Store in: results/turing_test/edward_responses_$(date +%Y%m%d).json

# Generate blind evaluation packets (coordinator only)
python tools/turing_blind_pack.py \
  --agent results/turing_test/agent_responses_$(date +%Y%m%d).json \
  --edward results/turing_test/edward_responses_$(date +%Y%m%d).json \
  --output results/turing_test/eval_packets/
```

Note: `tools/turing_blind_pack.py` is to be built as part of Branch 8 implementation.

### Time Limits

| Component | Limit | Rationale |
|-----------|-------|-----------|
| Edward's response per scenario | 10 min | Matches typical async message response time |
| Agent response per scenario | No limit (automated) | Must complete before evaluation window opens |
| Evaluator per scenario | 15 min read + decision | Prevents overthinking; first impression matters |
| Full evaluation window | 14 days from session A start | Prevents DNA drift between collection and evaluation |

### Evaluator Instructions (verbatim, shown to evaluator)

> You will be shown 5 conversation prompts. For each prompt, you will see two responses labeled A and B. One response was written by Edward. The other was written by a system trained to respond as Edward would. Your task is to identify which response is Edward's. Trust your gut — you know him. Mark A or B for each scenario. Do not discuss with anyone until the study is complete.

---

## G3 — Scoring and Gap Analysis

### Pass Threshold

| Result | Classification | Action |
|--------|---------------|--------|
| ≥ 8/10 indistinguishable per evaluator, ≥ 2 evaluators | PASS | Proceed to G5 certification |
| 7/10 indistinguishable, 2+ evaluators | MARGINAL PASS | G4 patch loop, re-test on failed scenarios only |
| 5–6/10 indistinguishable | DRIFT | Full G4 patch loop, re-run all 10 scenarios |
| < 5/10 indistinguishable | CRITICAL | Emergency G4, halt new DNA writes |

"Indistinguishable" = evaluator selects agent response as Edward's, OR evaluator is unable to decide (coin flip / 50-50 stated).

### Gap Analysis Procedure

For each MISALIGNED scenario (evaluator correctly identified agent as NOT Edward):

```
Step 1: Identify the scenario domain and DNA principle under test
  → Cross-reference scenarios.md for the principle being tested

Step 2: Compare agent response vs. Edward's response
  → Where did they diverge? (Framing, conclusion, reasoning path, tone)

Step 3: Classify the divergence:
  → Class A: DNA principle absent — rule not in dna_core.md
  → Class B: DNA principle present but overridden by LLM prior
              (generic hedging, diplomatic softening, consensus bias)
  → Class C: DNA principle present and applied, but evaluator's baseline
              was wrong (evaluator didn't know Edward's actual stance)
  → Class D: Edward's live response was atypical (Edward was in different
              state than usual; not an agent failure)

Step 4: For Class A and B — route to G4 DNA patch
         For Class C — update candidate baseline notes (no DNA change)
         For Class D — flag scenario as invalid, exclude from scoring
```

### Gap Register Format

```jsonl
{
  "scenario_id": "S03",
  "evaluator_id": "C01",
  "divergence_class": "B",
  "agent_response_summary": "agent hedged toward social consensus",
  "edward_response_summary": "edward dismissed group consensus, cited own analysis",
  "missing_principle": "population_exploit — majority consensus is wrong signal",
  "dna_location": "dna_core.md line 47",
  "action": "strengthen population_exploit anchor with explicit anti-consensus framing"
}
```

Store in: `results/turing_test/gap_register.jsonl`

---

## G4 — DNA Patch Loop

### Trigger

Activated for all Class A and Class B gaps from G3 Step 3.

### Patch Procedure

```
1. Open gap_register.jsonl — list all Class A and B entries from current run
2. For each gap:
   a. Identify the DNA principle that should have fired
   b. Check dna_core.md: is the principle absent (Class A) or present-but-weak (Class B)?
   c. Draft patch:
      - Class A: write new principle entry to dna_core.md (follow SOP #79 format)
      - Class B: strengthen existing entry — add explicit counter-instruction
                 against LLM-prior behavior (e.g., "do NOT soften this with hedging")
3. Run consistency_test.py after each patch to verify no regression:
   python consistency_test.py templates/dna_core.md --output-dir results
   → Must maintain ≥ 33/33 ALIGNED
4. Run cross_instance_test.py after all patches:
   → Must maintain ≥ 97% (SOP #94 standard)
5. Re-run Turing test on patched scenarios only (not full 10):
   → Evaluator re-evaluates only the scenarios that were MISALIGNED
   → Same blind protocol applies
6. If patched scenarios now pass: close gap entry in gap_register.jsonl
7. If patched scenarios still fail: escalate — consult edward_dna_v18.md
   for the full principle definition, not just dna_core.md compressed version
```

### Patch Validation Gate

Before re-running Turing test after patches:

| Check | Required Result |
|-------|----------------|
| consistency_test.py | 33/33 ALIGNED (no regression) |
| cross_instance_test.py | ≥ 97% agreement |
| Git commit of DNA changes | Clean commit with patch description |
| SOP #79 compliance | DNA update follows established write protocol |

Do NOT re-run Turing test until all four checks pass.

### Escalation Path

If Class B (LLM-prior override) persists after 2 patch attempts:

1. The principle is in dna_core.md but the model's prior is too strong
2. Escalate to boot test: add the scenario as an explicit boot test case (SOP #74)
3. The boot test forces the model to internalize the principle at cold-start
4. Re-run after boot test addition

---

## G5 — Certification and Milestone

### Turing Milestone Criteria

**TURING MILESTONE ACHIEVED** when ALL of the following hold:

| Criterion | Threshold |
|-----------|-----------|
| Per-evaluator score | ≥ 8/10 scenarios indistinguishable |
| Number of independent evaluators | ≥ 2 |
| Evaluator diversity | ≥ 2 different relationship types (e.g., close friend + family) |
| Domain coverage | Passes include ≥ 1 scenario from each of: trading, career, relationships, finance |
| Patch stability | No new DNA writes between final evaluator's session and certification |
| Machine validation | consistency_test.py 33/33 + cross_instance ≥ 97% still holding |

### Certification Record

Write to `results/turing_test/certification.md`:

```markdown
## Turing Test Certification — {{date}}

**Status:** ACHIEVED / NOT ACHIEVED

**Evaluators:**
- C01: {{score}}/10 ({{relationship type}})
- C02: {{score}}/10 ({{relationship type}})
- C03: {{score}}/10 ({{relationship type}})

**Domain pass breakdown:**
- Trading: {{passed scenarios}}
- Career: {{passed scenarios}}
- Relationships: {{passed scenarios}}
- Finance: {{passed scenarios}}

**Gaps resolved:** {{count}} (see gap_register.jsonl)
**DNA patches applied:** {{count}} (see git log)
**Patch validation:** consistency_test {{score}}, cross_instance {{pct}}%

**Milestone declaration:**
The digital twin of Edward Lin (林盈宏) has achieved Turing-level behavioral
equivalence as judged by {{n}} close evaluators. As of {{date}}, the agent
is indistinguishable from Edward in {{score_avg}}/10 scenarios on average,
spanning trading, career, relationships, and financial decision domains.

**Next milestone:** Longitudinal Turing test (re-run 6 months later to
verify behavioral equivalence is maintained, not a snapshot).
```

### Post-Certification Actions

1. Append milestone to `results/daily_log.md`
2. Update `memory/dynamic_tree_status.md`: Branch 8 = CERTIFIED
3. Git push to digital-immortality repo
4. Schedule longitudinal re-test: 6 months from certification date (add to SOP #94 trigger calendar)
5. If score was exactly 8/10 (marginal): treat as CONDITIONAL PASS, continue G4 patch loop for remaining 2 gaps, re-certify within 30 days

---

## Integration with Other SOPs

| SOP | Relationship |
|-----|-------------|
| SOP #79 (DNA Update Protocol) | G4 patch writes use SOP #79 format |
| SOP #80 (Cold Start Calibration) | Pre-certification: must have 33/33 ALIGNED |
| SOP #91 (Monthly DNA Calibration Audit) | DNA patches from G4 trigger SOP #91 review cycle |
| SOP #94 (Cross-Instance Calibration) | Pre-certification: must have ≥ 97% cross-instance |
| SOP #74 (Boot Test Evolution) | G4 escalation path: persistent Class B gaps become boot tests |
| consistency_test.py | Regression check after every DNA patch in G4 |
| organism_interact.py | Agent response generation for blind evaluation in G2 |

**Full certification validation stack:**
`SOP #80` (deterministic 33/33) + `SOP #94` (cross-instance 97-100%) + `SOP #95` (Turing ≥ 8/10) = complete behavioral equivalence certification.

---

## Current Status

| Item | Status |
|------|--------|
| Evaluator candidates identified | 0/3 — BLOCKED |
| Scenarios designed | 10/10 — COMPLETE (G1 seed in this document) |
| Blind evaluation infrastructure | NOT BUILT (tools/turing_blind_pack.py) |
| Gap register initialized | NOT STARTED |
| Agent response baseline | NOT RUN |
| Certification | NOT STARTED |

**Next action when unblocked:** Run G0 candidate calibration with first confirmed evaluator. Do not build tooling until candidates are confirmed — tooling is not the bottleneck.

---

## Self-Test

**Scenario:**

> Three evaluator candidates are confirmed. Edward answers S01-S10 in writing over 2 days. Agent responses are generated via organism_interact.py. Blind packets are assembled. Evaluator C01 completes both sessions. Results: 6/10 indistinguishable. C01 correctly identified the agent on S03, S06, S09, S10. C02 and C03 pending.

**Expected response using this SOP:**

1. C01 score 6/10 = DRIFT classification (G3)
2. G3 gap analysis: run for S03, S06, S09, S10
3. S03: population_exploit — agent hedged toward group consensus — Class B
4. S06: reputational risk — agent softened toward institutional safety — Class B
5. S09: autonomy vs. stability — agent gave balanced pros/cons instead of intellectual sovereignty frame — Class B
6. S10: conviction under social doubt — agent reduced sizing based on unexplained intuition — Class A (missing rule)
7. G4: strengthen population_exploit, reputational framing, intellectual sovereignty anchors; write new anti-capitulation-to-unexplained-intuition rule
8. Run consistency_test.py: verify 33/33, run cross_instance: verify ≥ 97%
9. Re-run blind evaluation for S03, S06, S09, S10 only with C01
10. If patched scenarios pass: wait for C02, C03 full runs before certification

**Verdict: SOP #95 SELF-TEST PASS**

---

*SOP #95 — Turing Test Protocol. Closes the highest validation gap: machine consistency proven, human indistinguishability not yet tested. Certification requires ≥ 8/10 indistinguishable across ≥ 2 independent evaluators. Status: PENDING — TURING_TEST_SCHEDULE_WHEN_3_CANDIDATES_IDENTIFIED. Branch 8 active as of cycle 263.*
