# SOP #53: Cognitive Performance & Decision Bandwidth Protocol
> UTC: 2026-04-09 | Domain: 8 (生活維護) + 2 (行為等價) | Status: COMPLETE ✅

## Purpose

Protect peak cognitive state as a scarce resource. Decision quality is a function of cognitive bandwidth, not just knowledge. The same decision made tired = a different (worse) decision. This SOP operationalizes MD-111 (穩定收入=認知資源先決) and MD-53 (認知資源有限,排程有限).

## Backing MDs

| MD | Principle |
|----|-----------|
| MD-111 | 穩定收入=認知資源先決 — cognitive resource is the prerequisite for everything |
| MD-53 | 認知有限,高優先任務排認知峰值時段 |
| MD-89 | 策略監控=人均帶寬是投組規模硬上限 — bandwidth caps portfolio size |
| MD-48 | 時間配置先定義高槓桿任務再排其他 |
| MD-12 | 決策架構=先定變數集再求解 |
| MD-67 | 教學=給起手式,不是完整框架 |
| MD-136 | 職涯=程式交易時間優先薪資 |

## Decision Label

`PROTECT_COGNITIVE_PEAK` — when any task competes for peak-hour slots, protect the highest-leverage task.

## Gates

### G0: Bandwidth Audit (Weekly, Sunday)
Map cognitive load into 4 tiers:
- **L0 (Autopilot)**: habit loops, physical maintenance — zero bandwidth cost
- **L1 (Routine)**: email triage, scheduled reviews, template execution — 1–2 units
- **L2 (Focused)**: strategy development, code, DNA calibration, writing — 4–6 units
- **L3 (Deep)**: novel problem solving, cross-domain transfer, organism calibration — 8–10 units

Total daily budget: 20 units. Peak window (first 4h post-wake): 12 units available.

**Gate pass**: ≥1 L3 task scheduled in peak window. Fail = reschedule L1/L2 until L3 fits.

### G1: Cognitive Load Classification Before Scheduling
Before adding any task to calendar:
1. Classify L0/L1/L2/L3
2. Check current peak window load: if L2+L3 total > 12 → defer L2, never defer L3
3. Never schedule L3 in post-14:00 slot unless peak window was wasted (see G5)

**Kill condition**: if peak window has ≥3 L1 tasks = system failure. Remove all L1 from peak window.

### G2: Decision Debt Detection
Decision debt = backlog of unmade decisions draining background bandwidth.

Audit weekly: list all open decisions (should I X? when to Y?). For each:
- Is there enough information to decide now? → **decide immediately** (MD-12: define variable set first)
- Not enough information? → set explicit trigger date, park it
- No decision possible ever? → delete from list

**Rule**: >5 open decisions in working memory = cognitive debt emergency → G5 protocol.

### G3: Environment Redesign Trigger
When the same category of low-value decision appears ≥3× per week:
1. Pre-commit the default (morning_defaults.md pattern — MD-322)
2. Eliminate the decision entirely via system design
3. Record eliminated decision types in `docs/cognitive_defaults.md`

Examples already applied: meal routing (morning_defaults), SOP template-first composition (SOP #46).

**Rule**: any recurring L1 decision that appeared ≥3× this week = G3 trigger. Pre-commit or automate.

### G4: Cognitive State Gate Before High-Stakes Decisions
Before any irreversible decision (strategy kill, career move, relationship downgrade, capital reallocation):
1. Check: >4h since wake? → post-peak, high-stakes decision deferred to tomorrow's peak
2. Check: >3 L2/L3 tasks completed today? → cognitive fatigue, defer
3. Check: sleep <6h last night? → defer, execute recovery SOP #52 first

**Rule**: if any gate above triggers → no irreversible decision. Schedule it in next peak window. Not optional.

### G5: Emergency Protocol (Cognitive Debt > 5 or Peak Window Lost)
1. Stop all L2/L3 work
2. List every open decision (5 min max)
3. Decide or park with trigger date (10 min max)
4. Block next morning peak window as recovery (no meetings, no L1)
5. Execute G3 for any recurring pattern found in the list

## Domain Application

| Domain | Application |
|--------|-------------|
| Trading | Strategy development = L3. Only in peak window. Signal monitoring = L1 (automated). |
| DNA calibration | L3. Schedule explicitly. Not during email triage hours. |
| Career decisions | L3. Salary negotiation prep = peak. Offer comparison = peak. Never rushed. |
| Writing / SOP creation | L2-L3. Peak window only. Templates reduce to L2. |
| Communication triage | L1. Off-peak only (SOP #46 defines windows). |
| Physical health | L0. Habits, not decisions (SOP #52 defines defaults). |

## Self-Test

Scenario: It's 15:00. You have 2h available. There's an open strategy kill decision (DualMA MDD approaching threshold) and 23 unread messages.

Apply gates:
- G0: Budget check — peak window (morning) used. Remaining budget = ~8 units.
- G1: Strategy kill = L3. 15:00 = post-peak. → **Defer to tomorrow's peak window.**
- G2: Is the kill decision urgent? → check kill conditions (MDD > 10%?). If no threshold crossed → park with trigger date (MDD crossing). If threshold crossed → override G1 (kill conditions are pre-committed, execution is L1).
- G3: 23 messages = L1. Post-peak = correct slot. Apply SOP #46.

**Output**: defer strategy review to tomorrow 09:00. Triage messages now via SOP #46.

## Kill Conditions

- Scheduling L3 task post-14:00 without peak-window evidence it was exhausted = **protocol violation**
- Making an irreversible decision after G4 gate triggers = **protocol violation**
- Decision debt >5 open items for >3 days = **system failure → G5 immediately**

## Integration

- SOP #51 (Time Allocation): G0 bandwidth audit informs weekly time budget
- SOP #52 (Sleep & Recovery): G4 sleep gate requires SOP #52 compliance
- SOP #46 (Async Communication): G3 pre-commits message triage to off-peak
- morning_defaults.md: G3 output accumulates here (recurring decision eliminations)
