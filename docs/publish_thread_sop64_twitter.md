# Twitter Thread — SOP #64: Technology Stack & Agent Infrastructure Management

> UTC: 2026-04-09 | Slot: Aug 11 | Domain: 8 (Technology Systems)
> Hook: "Your system broke. You didn't notice for 3 weeks."

---

**Tweet 1 (Hook)**
Your system broke.

You didn't notice for 3 weeks.

Not because you're careless. Because you have no stack audit protocol.

SOP #64: Technology Stack & Agent Infrastructure Management

(most overlooked SOP in this series)

---

**Tweet 2**
Every automated system runs on a dependency stack.

Mine runs on: Binance API, Claude API, GitHub, cron jobs, JSONL logs.

Each one is a single point of failure.

Most people find out it broke when the output stops.

By then, 3 weeks of data is gone.

---

**Tweet 3**
The fix is 3 tiers:

T1 — Mission Critical: agent cannot function without it
(Claude API, Binance API, GitHub)

T2 — Operational: degrades function but not fatal
(cron jobs, logging)

T3 — Enhancement: improves but not required
(monitoring dashboards, UI)

You only need air-gap protection on T1.

---

**Tweet 4**
Gate 1: Stack Inventory Audit

Map every tool → assign tier → verify each has a fallback or documented failure mode.

Kill signals: T1 tool down >1h. Any T1 cost >$50/month without ROI review.

Most operators skip this. They "know" their stack. Until they don't.

---

**Tweet 5**
Gate 2: Derivative Scan

Track what's CHANGING about each tool — not just whether it's running.

ΔCost: API cost trending up?
ΔReliability: errors this week?
ΔUsage: idle or overloaded?
ΔAlternatives: better tool available?

A tool that was right 6 months ago may be wrong today.

---

**Tweet 6**
Gate 3: Non-Negotiable Maintenance Budget

Weekly minimum (takes 10 minutes):
→ Verify daily tick executed (check log count)
→ Run consistency test (≥30/33 pass rate)
→ Confirm git push synced

Monthly:
→ T1 cost audit vs last month
→ Cold-start test from minimal state

This is your stack health insurance premium.

---

**Tweet 7**
Gate 4: Quarterly Stack Evolution

Every 90 days: is the current stack still optimal?

Evolution only if: ΔCost >30% savings OR ΔReliability >20% AND migration risk <1 week.

Rule: Never migrate T1 tools during active production runs.

Rule: Rename/archive old configs. Never delete. History = reference implementation.

---

**Tweet 8**
Gate 5: Emergency Recovery Protocol

Trigger: T1 tool down | consistency <30/33 | git push failed >48h

Recovery sequence:
1. Isolate the failing tool
2. Use documented fallback (F1–F9 runbook)
3. Continue work on unaffected branches (don't halt everything)
4. Smallest intervention first: restart → reconfigure → replace
5. Log root cause. Update runbook.

---

**Tweet 9**
Three-layer implementation:

L1 Execute → daily/weekly maintenance (ticks, tests, pushes)
L2 Evaluate → derivative scan + weekly review (cost, reliability)
L3 Evolve → quarterly evolution (replace, simplify, upgrade)

Execute without Evaluate+Evolve = tool debt accumulates silently.

Most operators live in L1 forever.

---

**Tweet 10**
The ROI rule for infrastructure:

Any T1 tool must return >10× its annual cost.

Claude API costs ~$X/month. The agent must generate >10× that in either revenue or capability multiplier.

If it doesn't, you're not running a system. You're maintaining a hobby.

---

**Tweet 11**
The meta-insight:

SOP #64 is the meta-SOP.

Every other SOP in this series (trading, content, social capital, revenue) depends on the infrastructure in SOP #64 running.

Most builders obsess over the application layer. The infrastructure layer is what keeps it alive.

---

**Tweet 12 (CTA)**
SOP #64: Technology Stack & Agent Infrastructure Management

5 gates. Three-layer. Built for the operator who wants to still be running in 5 years.

Full protocol: [link to product]

This is SOP #64 of 64. The complete behavioral OS is now documented.

What's the T1 tool you'd lose the most if it went down tomorrow? Reply below.
