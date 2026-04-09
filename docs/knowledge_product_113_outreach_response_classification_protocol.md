# SOP #113 — Outreach Response Classification Protocol
> Digital Immortality Knowledge Product Series
> Created: 2026-04-10T UTC (cycle 288)

## Purpose

When Branch 1.3 (Skill 商業化) DMs land, the agent needs a deterministic protocol to classify responses and route to the correct next action. Without this, responses sit unprocessed, pipeline stalls, and the 14-day first-sale target slips.

This SOP covers: response classification → routing → follow-up cadence → pipeline state tracking.

## Gate Structure (G0–G5)

### G0: Response arrives
- Trigger: Any reply to a Week 1 DM (Archetype A–E in `outreach_week1_execution.md`)
- Action: Log to `results/outreach_pipeline.jsonl` with timestamp + contact ID + raw response
- Never let >24h pass before classifying a response

### G1: Classify response
Map every reply to exactly one of 5 labels:

| Label | Pattern | Example |
|-------|---------|---------|
| **COLD** | Polite decline or no-fit signal | "Not for me right now" / "Not interested" |
| **WARM** | Curiosity or request for more info | "How does this work?" / "Tell me more" |
| **HOT** | Clear buying signal or time/price ask | "What's the price?" / "Can we schedule?" |
| **REJECT** | Hard no or rude reply | "Don't DM me" / "Spam" |
| **BOUNCE** | No reply after 7 days | [silence] |

Tie-breaking rule: When in doubt between WARM and HOT, default to WARM (prevents premature pitch).

### G2: Route by label

| Label | Next action | Timing |
|-------|-------------|--------|
| COLD | Thank + leave door open ("understood, feel free to reach out later") | Within 24h |
| WARM | Send 3-line response: confirm problem → describe session → offer time slot | Within 4h |
| HOT | Send calendar link + price ($97 advisory call / $197 async audit) | Within 1h |
| REJECT | Log + blacklist contact + no further outreach | Immediate |
| BOUNCE | Send one follow-up on day 7: "quick check-in — does this problem still apply?" | Day 7 |

WARM → HOT conversion: After WARM reply, if they ask pricing or scheduling = re-classify to HOT.

### G3: Track pipeline state

Maintain `results/outreach_pipeline.jsonl` schema:
```json
{
  "contact_id": "arch_a_001",
  "archetype": "AI Agent Dev",
  "platform": "X",
  "dm_sent_date": "2026-04-10",
  "response_date": null,
  "label": "BOUNCE",
  "follow_up_sent": false,
  "converted": false,
  "revenue": 0,
  "notes": ""
}
```

Weekly pipeline audit (every Monday):
- Count by label: WARM+HOT = pipeline health
- Conversion rate: HOT → paid session
- If BOUNCE > 60% of total: revise DM template (message not landing)
- If WARM → no HOT conversion after 3 follow-ups: revise offer framing

### G4: Cadence rules

- Week 1: 5 sends (Archetype A — AI Agent Dev)
- Week 2: 5 sends (Archetype B — Digital Legacy Builder), pending Week 1 signal
- Week 2 cadence decision: If Week 1 has ≥1 HOT → continue with same template. If Week 1 is all COLD/BOUNCE → revise template before Week 2 send.
- Max outreach per week: 10 (maintain signal clarity per cohort)
- Pause rule: If REJECT ≥ 3 in one week → pause, diagnose message fit before continuing

### G5: Revenue trigger

- First paid session = Branch 1.3 alive
- $97/month from advisory calls = covers API cost → self-sustaining
- Track: `results/outreach_pipeline.jsonl` → `converted: true` + `revenue: 97` or `197`

## Pipeline State Summary

```
Current (2026-04-10):
- Week 1 DMs: 5 templates drafted (outreach_week1_execution.md), 0 sent
- Contacts identified: results/skill_outreach_targets.md (5 archetypes, PENDING)
- First send: blocked on Edward (human gate)
- Pipeline health: 0 HOT / 0 WARM / 0 BOUNCE (no sends yet)
```

## Kill Condition

If after 30 days and ≥20 DMs sent: 0 WARM + 0 HOT → DM strategy is not the right acquisition channel. Escalate to: content-first (post SOP#01 on X to build inbound) or warm-network referral path.

## Backing Principles

- MD-393: 多路徑平行申請=信號生成策略 (parallel outreach = market signal)
- MD-133: 策略池高淘汰率=過濾訊號 (high reject rate = message mismatch signal)
- MD-04: 不對稱資訊先行動 (asymmetric info = act on limited info, update from response)
- SOP #112: Cold-Outreach Execution Playbook (upstream: defines who to contact and message)
- SOP #110: Skill First-User Acquisition Protocol (upstream: defines archetype targets)

## Related Files

- `results/outreach_pipeline.jsonl` — response tracking log
- `staging/outreach_week1_execution.md` — Week 1 DM templates
- `results/skill_outreach_targets.md` — contact list by archetype
- `docs/knowledge_product_110_skill_first_user_acquisition.md` — archetype definitions
- `docs/knowledge_product_112_cold_outreach_execution_playbook.md` — execution playbook
