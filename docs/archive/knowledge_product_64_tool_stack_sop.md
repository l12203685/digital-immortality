# SOP #64 — Technology Stack & Agent Infrastructure Management Protocol

> UTC: 2026-04-09 | Domain: 8 (Technology Systems / Agent Infrastructure)
> Backing MDs: MD-106/141/148/314/324/319

---

## The Core Problem

The agent runs on a stack of external tools: Binance API, Claude API, GitHub, Windows Task Scheduler, JSONL logging, cron jobs. Each dependency is a single point of failure. Most operators manage their tool stack reactively — they notice broken tools when work stops. The fix: a 5-gate protocol that audits the stack before failure, tracks costs, and evolves the architecture proactively.

This is the operational backbone SOP. Every other SOP depends on this running.

---

## Gates

### G0 — Stack Inventory Audit

Map every tool in the current stack. Classify by dependency tier:

| Tier | Definition | Example |
|------|-----------|---------|
| T1 — Mission Critical | Agent cannot function without it | Claude API, Binance API, GitHub |
| T2 — Operational | Degrades function but not fatal | Task Scheduler cron, JSONL logging |
| T3 — Enhancement | Improves but not required | Trading UI, monitoring dashboard |

**Kill signals triggering G0:**
- Any T1 tool down for >1h
- Monthly cost for any T1 tool exceeds $50 without ROI review
- Cold-start failure rate >10% in consistency test
- New tool dependency introduced without tier classification

**G0 action:** List all tools → assign tier → verify each has fallback or documented failure mode → output: `results/stack_inventory.md`

---

### G1 — Derivative Scan

Track what's changing about each tool:

- ΔCost: Is API cost trending up or down?
- ΔReliability: Any errors in last 7 days?
- ΔUsage: Utilization increasing or idle?
- ΔAlternatives: Has a better tool appeared?

**Metrics to watch:**
- Binance API: rate limit errors / tick
- Claude API: token cost / cycle
- GitHub Actions (if used): CI failure rate
- cron jobs: missed ticks / week
- JSONL logs: entry count growth rate (proxy for system health)

**G1 action:** For each T1/T2 tool, compute 30-day derivative → flag any tool with ΔCost >+20% or ΔReliability <95% uptime → output: `results/stack_derivative.md`

---

### G2 — Non-Negotiable Maintenance Budget

Weekly minimum actions:

| Cadence | Action |
|---------|--------|
| Daily | Verify cron tick executed (check paper_live_log.jsonl count) |
| Weekly (Sunday) | Check GitHub push sync (both LYH + digital-immortality) |
| Weekly (Sunday) | Run consistency_test.py — verify 33/33 ALIGNED |
| Monthly | Audit all T1 tool costs vs last month |
| Monthly | Test cold-start from session_state.md + dna_core.md only |
| Quarterly | Full G0 inventory re-run |

**Non-negotiables (hard minimum):**
- ≥1 paper-live tick per 48h (proves stack is alive)
- ≥1 git push per session (proves memory persistence is working)
- consistency test ≥ 33/33 (proves behavioral layer is intact)
- No T1 tool introduced without: tier classification + documented fallback + cost estimate

**G2 violations:**
- Paper-live gap >7 days → system health unknown → run G0 immediately
- Consistency drop → re-read dna_core.md + boot_tests.md → rerun test
- git push failure → resolve before any other work (memory persistence > new output)

---

### G3 — Quarterly Stack Evolution

Every 90 days: evaluate whether the current stack is still the best available.

**Evolution triggers:**
- A T1 tool raises prices >30% → evaluate alternatives
- Cold-start failure rate rises → simplify architecture
- A new tool reduces operational friction by >50% → trial for 30 days

**Evaluation framework:**
1. What problem does the current tool solve?
2. Is there a simpler or cheaper tool that solves 80% of it?
3. What's the migration cost (time + data loss risk)?
4. Migration only if: ΔCost >30% savings OR ΔReliability >20% improvement AND migration risk <1 week work

**Stack evolution rules:**
- Never migrate T1 tools during active paper-live or mainnet runs
- Rename/archive old tool configs — never delete (history = reference implementation)
- Migration = create new → validate → decommission old (never hot-swap)
- All migrations logged in `results/stack_evolution_log.md`

---

### G4 — Weekly Review (10 min Sunday)

| Check | Metric |
|-------|--------|
| Tick count | ≥7 paper-live ticks this week? |
| Consistency | Test passing (33/33)? |
| Git sync | Both repos pushed this week? |
| Cost delta | Any T1 tool cost spike? |
| Cold-start | Any session required full DNA re-read (indicator of boot failure)? |

Output: 5-line status block appended to `results/stack_weekly_review.md`

---

### G5 — Emergency Infrastructure Recovery

**Trigger:** Any of: consistency <30/33 | paper-live gap >14 days | T1 tool unreachable | cold-start failure | git push failure >48h

**Recovery sequence:**
1. **Isolate**: Identify which T1 tool is failing
2. **Fallback**: Use documented fallback (see `docs/cold_start_recovery_runbook.md` F1–F9)
3. **Triage**: Can agent continue work on other branches while T1 is down? (Bias toward continuing on unaffected branches, not halting all work)
4. **Restore**: Smallest intervention first — restart before reconfigure, reconfigure before replace
5. **Root cause**: After restoration, append root cause to `results/stack_evolution_log.md`
6. **SOP update**: If this failure mode wasn't in F1–F9, add it

**Kill condition:** If T1 recovery >72h and no fallback path → escalate to Edward (human-gated unblock)

---

## Three-Layer Implementation

```
L1 Execute  → G2 daily/weekly maintenance cadence (ticks, tests, pushes)
L2 Evaluate → G1 derivative scan + G4 weekly review (cost, reliability, utilization)
L3 Evolve   → G3 quarterly evolution (replace, simplify, upgrade)
```

Execute without Evaluate+Evolve = tool debt accumulates silently.
L2 without L3 = identified problems never fixed.
L3 without L1 = evolved architecture never maintained.

---

## DNA Anchors

| MD | Principle | Application |
|----|-----------|-------------|
| MD-106 | 公開指標=邊際edge趨零 | Don't over-rely on external tools that competitors have equal access to |
| MD-141 | 基礎設施投資=報酬門檻十倍年成本 | T1 tool must return >10× its annual cost |
| MD-148 | 基礎設施投資=報酬門檻十倍年成本 | Same principle — verify ROI before adding any T1 dependency |
| MD-324 | Three-layer loop (L1+L2+L3) | Every automated system needs execute+evaluate+evolve |
| MD-319 | Recursive output must persist | Stack health = persistence pipeline health |

---

## Connection to Other Branches

| Branch | Dependency |
|--------|-----------|
| 1.1 Trading | Binance API (T1), cron jobs (T2), JSONL (T2) |
| 2.3 Validation | consistency_test.py depends on organism_interact.py (T2) |
| 3.1 Recursive Engine | Claude API (T1), git push (T1) |
| 6 存活/Cold-start | cold_start_recovery_runbook.md F1–F9 (G5 connection) |
| 7 SOP series | GitHub (T1) for all docs persistence |

**SOP #64 is the meta-SOP**: all other SOPs depend on this infrastructure running.
