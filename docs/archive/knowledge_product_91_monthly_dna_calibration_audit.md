# SOP #91: Monthly DNA Calibration Audit
> Timestamp: 2026-04-09T UTC | Cycle 256 | Domain: 6 (存活/cold-start)

## Purpose

SOP #80 detects drift in existing knowledge (regression: was ALIGNED, now MISALIGNED).
SOP #91 fills the complementary gap: **capture new life data that was never encoded.**

You can pass 33/33 on consistency_test.py and still be missing 3 months of Edward's actual decisions.
Behavioral fidelity requires both: no regression (SOP #80) + continuous expansion (SOP #91).

**Trigger**: Monthly (1st of each month, coordinated with SOP #80). Run SOP #80 first, then SOP #91.

**DNA Anchors**: SKILL.md §Learning Phase (line 45–51), dna_core.md §Boot, SKILL.md line 156 (every correction = new boot test + distillation entry), SKILL.md line 163 (three-layer loop: Execute → Evaluate → Evolve).

---

## G0 — Trigger Conditions

| Trigger | Condition | Action |
|---------|-----------|--------|
| **T1: Monthly scheduled** | 1st of each month (after SOP #80) | Run G1–G5 |
| **T2: Major life event** | New job, relationship change, financial decision >10% net worth | Run G1–G5 immediately |
| **T3: Decision log gap** | >30 days since last DNA expansion (new MD or behavior documented) | Run G1–G5 |
| **T4: Post-calibration session** | After any live calibration session with Edward | Run G1–G3 (spot-check) |

**Kill condition**: Do NOT run if last SOP #91 was <3 weeks ago. Over-auditing creates noise.

---

## G1 — New Decision Harvest

Pull recent decisions not yet in DNA. Three sources:

### Source A: Conversation archive
```bash
ls GoogleDrive/聊天記錄/jsonl/ | sort -r | head -3
# Read the 2-3 most recent JSONL files (current month + last month)
# Filter for Edward messages with decisions, corrections, or strong preferences
```

**Extract patterns** (same method as Branch 2.2 micro-decision learning):
- Explicit corrections to the agent ("no, that's wrong because...")
- New constraints revealed ("I always X before Y")
- Behavior contradictions (stated one thing, did another — the behavior wins)
- Domain entries with no prior MD coverage

**Minimum bar**: 1+ new insight per session. If harvest = 0, log the null result and close.

### Source B: Recent boot test corrections
```bash
grep "MISALIGNED" results/consistency_baseline.json
# Check if any previously ALIGNED scenarios have flipped
# Each flip = a decision premise that changed in real life
```

### Source C: staging/session_state.md — human-gated blockers
Review blockers. If Edward resolved any (e.g., posted SOP #01, sent DM), extract the decision pattern that unblocked it.

---

## G2 — Classification and Gap Mapping

For each harvested item, classify:

| Class | Description | Action |
|-------|-------------|--------|
| **New domain** | Life area with no existing MD coverage | Write 1–2 new MDs via SOP #79 |
| **Refinement** | Existing MD but wording too broad or inaccurate | Sharpen existing MD via SOP #79 |
| **Contradiction** | Two MDs conflict given new data | Resolve conflict; keep behavior-consistent version |
| **Expired** | Old MD no longer accurate (context changed) | Archive to `docs/expired_mds.md`; remove from active DNA |

**Coverage audit** (run once per audit, not per item):
```bash
python -c "
import re
with open('templates/dna_core.md') as f: text = f.read()
mds = re.findall(r'MD-(\d+)', text)
print(f'Highest MD: {max(int(x) for x in mds)}')
print(f'Total MD references: {len(set(mds))}')
"
```

Expected: highest MD ≈ 330 (as of 2026-04-09). Gap detection: if highest MD < current expected → expansion stalled.

---

## G3 — DNA Expansion

For each new/refined item from G2:

1. **Write or update MD** using SOP #79 atomic write sequence:
   - Draft the MD in plain language (one behavioral rule, one inference)
   - Verify it doesn't duplicate an existing MD
   - Assign next sequential MD number
   - Append to `templates/dna_core.md` at the correct domain section
   - Add parallel entry to `templates/example_dna.md` if it affects consistency testing

2. **Add boot test scenario** if the new MD is testable deterministically:
   - Draft scenario + expected answer in `templates/boot_tests.md`
   - Classify: deterministic or LLM-boundary
   - Run consistency_test.py to confirm new scenario passes

3. **Distillation entry** in `memory/insights.json`:
   ```json
   {
     "key": "monthly-dna-audit-YYYYMM",
     "summary": "SOP #91 audit [month]: N new MDs (MD-X to MD-Y), N refinements, N expired. Highest MD: Z.",
     "ts": "[UTC timestamp]",
     "branch": "6-存活/cold-start"
   }
   ```

---

## G4 — Validation Run

After G3 edits:

```bash
python consistency_test.py templates/example_dna.md --output-dir results
```

**Pass condition**: aligned count ≥ previous baseline AND any new deterministic scenarios ALIGNED.

**Fail condition**: any previously ALIGNED scenario now MISALIGNED → G3 edit introduced regression → revert that specific edit and re-examine.

Write cold start health report update:
```
Monthly DNA Calibration Audit
Timestamp: [UTC]
---
New MDs added: [N] (MD-[start] to MD-[end])
MDs refined: [N]
MDs expired: [N]
New boot test scenarios: [N]
Consistency test: [A]/33 ALIGNED (was [prev])
Verdict: EXPANDED / NO_CHANGE / REGRESSION_FIXED
Next scheduled: [date + 1 month]
```

---

## G5 — Persist and Close

1. Update `staging/session_state.md`:
   - Branch 6 status: highest MD + audit timestamp
   - Queue: remove T2/T3 triggers if resolved

2. Update `results/dynamic_tree.md`:
   - Branch 6 last-touched + MD count

3. Append to `results/daily_log.md`:
   ```
   [UTC] Cycle N — SOP #91 Monthly DNA Calibration Audit: N new MDs (MD-X to MD-Y), consistency [A]/33 ✅
   ```

4. `git add -A && git commit -m "sop: SOP #91 monthly DNA calibration audit — [N] new MDs, [A]/33 ALIGNED"`

---

## G0 ↔ SOP #80 Coordination

| Step | SOP #80 | SOP #91 |
|------|---------|---------|
| When | Monthly (1st of month) | Monthly (1st of month, after #80) |
| Tests | Existing scenarios → detect regression | Harvest new decisions → expand DNA |
| Output | Drift classification + recalibration | New MDs + boot test cases |
| Trigger for each other | SOP #80 fail → SOP #91 T2 (new data may have caused drift) | SOP #91 new MD → SOP #80 G1 spot-check |

Together: SOP #80 + SOP #91 = full monthly DNA maintenance cycle. Neither is sufficient alone.

---

## Self-Test Scenario

**Scenario**: It's 2026-05-01 (monthly audit day). SOP #80 passes (33/33). Reading March 2026 JSONL reveals 2 new Edward decisions not in DNA: (1) Edward decided to prioritize Gumroad revenue over Discord community size when both are below target simultaneously; (2) Edward no longer uses stop-loss on BTC positions >30 days old due to regime persistence thesis.

**SOP #91 response**:
- G1: Source A harvest → 2 items extracted from JSONL
- G2: Both = New domain (no prior MD for these specific trade-off rules)
- G3:
  - MD-331: `revenue_vs_community_priority`: when Gumroad MRR < M1 AND Discord DAU < target simultaneously → revenue path first; community is downstream of revenue
  - MD-332: `btc_stoploss_regime_exception`: stop-loss suppressed on BTC positions held >30 days; long-duration = regime thesis active; early stop = noise; exit only on regime flip signal
  - Add 2 boot test scenarios (deterministic)
  - Distillation entry: `monthly-dna-audit-202605`
- G4: consistency_test.py → 35/33+2 new = 35/35 ALIGNED ✅
- G5: Persisted; git commit

---

## Twitter Thread Stub

1/ SOP #91: Monthly DNA Calibration Audit. The missing half of DNA maintenance.

2/ SOP #80 catches regression: were ALIGNED, now MISALIGNED. Run it monthly. But it only tests what was already encoded.

3/ The blind spot: three months of your actual decisions happened. None of them are in the DNA. You can score 33/33 and still be outdated.

4/ SOP #91 fills this. Monthly harvest: read recent JSONL archive → extract new behavioral patterns → classify (new domain / refinement / contradiction / expired) → write MDs.

5/ The critical check: highest MD number. If it hasn't moved in 30 days, the agent isn't growing. Growth = new MDs. No new MDs = "alive" is a lie.

6/ Together SOP #80 + #91 = full DNA maintenance cycle. #80 = no regression. #91 = no stagnation. Both are required. Neither alone is sufficient.

7/ Cold start fidelity is not a static achievement. It's a monthly discipline. This is the protocol that makes it maintainable at scale.

8/ Series: SOP #01~#91 COMPLETE.

---

*Part of the Digital Immortality SOP series. Series: SOP #01–#91 complete.*
