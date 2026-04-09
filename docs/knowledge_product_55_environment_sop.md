# SOP #55 — Environment & Physical Space Protocol

> Domain: 9 (環境設計 Environment Design)
> Created: 2026-04-09T UTC (cycle 216)
> DNA anchors: MD-89 (單日時限) / MD-12 (看導數不看水平) / MD-48 (知識=時間密度乘積) / MD-144 (監控帶寬是上限) / MD-67 (現金流=買時間)

---

## One-Claim Insight

**Your environment is making decisions for you.** Every object in your field of view, every notification that reaches your screen, every friction point between you and a tool — these are pre-committed choices that run before you think. Most people optimize their thinking. Almost no one audits their environment. The correct model: environment design → reduced decision overhead → more bandwidth available for L3 decisions → compounding on everything else.

---

## 5-Gate Framework

### G0: Environment Audit

**Question**: Is my current environment aligned with my highest-priority work?

Three signals, weekly check (5 min):

1. **Visual noise index**: Objects/apps/notifications in default view that are not relevant to current priority — count them
2. **Friction score**: How many steps between me and my most important daily tool? (target: ≤1 click/gesture)
3. **Interrupt rate**: Average number of unplanned context switches per peak cognitive hour

**Kill condition**: Visual noise > 10 irrelevant objects in workspace OR interrupt rate > 3/hour during cognitive peak → G5.

---

### G1: Environment Derivative Scan

**Question**: Is my environment trending toward or away from cognitive clarity?

Track 3 derivatives (not snapshots):

- **ΔFriction/week**: Are common tools getting faster to access, or slower?
- **ΔInterrupt rate/week**: More or fewer unplanned context switches in peak window?
- **ΔDefault gravity**: Are defaults (browser homepage, phone apps, physical desk) pulling toward priority work, or away?

**Rule (MD-12)**: Single messy day is noise. Three consecutive days of high friction = structural signal, not willpower problem.

**Threshold**: If friction or interrupt rate worsens for 2 consecutive weeks → G4 structural review, not "try harder to focus."

---

### G2: Non-Negotiable Environment Budget

**Minimum viable environment investment (recurring, not one-time):**

| Category | Minimum | Rationale |
|----------|---------|-----------|
| Workspace reset | 2 min end-of-day clear | Prevents visual noise accumulation; next day starts clean |
| Notification audit | Monthly review of all notification sources | Defaults are always pro-interrupt, never pro-focus |
| Digital default alignment | Quarterly: does browser/phone/desktop default serve current priority? | Default gravity is the most persistent form of decision pre-commitment |
| Tool friction scan | Monthly: top 3 most-used tools — is access still ≤1 step? | Friction compounds invisibly |

**Rule**: These are infrastructure costs. They prevent environment degradation from silently draining bandwidth.

**Edge case**: During high-output sprints, workspace reset may slip. Maximum: 3 consecutive days before mandatory reset.

---

### G3: Environment Leverage Scan

**Question**: Which single environment change would most reduce cognitive overhead?

Run quarterly. Environment leverage is slow-changing:

1. List current environment friction points (digital, physical, notification, workflow)
2. Identify which single point causes the most unplanned context switches or L3 interruptions
3. Implement one change (not a stack)
4. Measure G0 signals before and after over 2 weeks
5. If ΔInterrupt rate ≥ −1/hour OR ΔFriction score ≥ −20% → write to protocol; set new default

**Anti-pattern**: Wholesale "productivity overhaul." Running 10 environment changes simultaneously produces unattributable results and reversion. Isolate, measure, keep.

---

### G4: Weekly Environment Review

**Sunday, 10 min. Three questions:**

1. **Coverage**: Did environment support or undermine priority work this week? (Y/N)
2. **Cause classification**: If N → behavioral (habit failure) / structural (bad default) / external (external interrupt source)?
3. **L3 edit decision**: Is this pattern persistent enough (2+ consecutive weeks) to change a default or protocol?

**Tracking format** (minimal):

| Week | Workspace reset Y/N | Interrupt rate | Friction score | Classification |
|------|---------------------|----------------|----------------|----------------|
| W1   |                     |                |                |                |

---

### G5: Environment Emergency

**Trigger**: 3 consecutive days of interrupt rate > 5/hour during cognitive peak OR visual noise has completely disrupted work output.

**Protocol**:

1. **Emergency reset**: 15-min full workspace and digital notification clear (non-negotiable before any work)
2. **Interrupt source audit**: List all interrupt sources that fired in last 3 days; classify each as essential/non-essential
3. **Kill non-essentials**: Turn off all non-essential notification sources (not "mute" — disable)
4. **Friction repair**: Restore top 3 tools to ≤1-step access
5. **No L3 edits until G0 signals return to baseline** (visual noise <5, interrupt rate <2/hour × 2 days)

**Rule**: During environment emergency, environment repair IS the highest-derivative activity. Not catching up on work. The debt compounds.

---

## Three-Layer Integration

| Layer | Environment Role |
|-------|-----------------|
| L1 (Execute) | G2 daily/weekly maintenance budget runs automatically; workspace reset, notification check |
| L2 (Evaluate) | G0/G1 audit detects drift; G4 weekly review classifies cause |
| L3 (Evolve) | G3 quarterly leverage scan modifies defaults; G4 triggers protocol edits when pattern confirmed |

**Rule**: L1 without L2+L3 = slow environment decay. Reviews detect the decay. Quarterly scans restructure it.

---

## DNA Anchors

| MD | Principle | Application |
|----|-----------|-------------|
| MD-89 | 單日時限 (single-day horizon) | Environment review cycles are daily/weekly, not quarterly only |
| MD-12 | 看導數不看水平 | Manage by interrupt rate trend, not snapshot |
| MD-48 | 知識=時間密度乘積 | Environment quality multiplies time density — good environment = same hours, higher output |
| MD-144 | 監控帶寬是上限 | Environment audit itself must cost <5 min/week — overhead cannot exceed savings |
| MD-67 | 現金流=買時間 | Low-friction environment = buying cognitive time without spending real time |

---

## Anti-Patterns

| Pattern | Why it fails |
|---------|-------------|
| One-time environment redesign | Defaults revert. Without maintenance budget, gains decay in 2–4 weeks |
| Willpower-based focus | Friction and interrupts run before willpower engages. Fix the source, not the symptom |
| Stack of environment changes | Unattributable. Impossible to know which change produced which result |
| Audit paralysis | Reviewing environment instead of working. G0 = 5 min. Not a project |
| Notification "mute" vs disable | Mute still allows badge accumulation and occasional firing. Disable is the only zero-friction option |
