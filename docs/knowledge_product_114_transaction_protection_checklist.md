# Knowledge Product #114 — Transaction Protection Checklist
> SOP for any commitment-based transaction where delivery is expected
> Extracted from MD-394 (201802 pattern: no written penalty = payer treated as fool)
> Created: 2026-04-10 UTC (cycle 290)

## Problem

Any transaction where you pay upfront and counterparty delivers later has a structural asymmetry: you've already transferred value, they control delivery timing. Without written terms, "delivery delay" has no cost to them. You become the fool who trusted a handshake.

**Pattern source**: 2018-02-05 — 「這樣感覺當初應該要簽個 沒有在該日交貨 要付違約金之類的合約，不然付錢的都被當傻子」(mining hardware pre-order; hardware withheld while price rose)

---

## When to Use

Any transaction where:
- You pay before receiving
- Delivery has a timeline commitment
- Counterparty has incentive to delay (rising market, better offers)
- No formal contract exists by default

---

## G0 — Pre-Transaction Check

Before paying:

| Gate | Question | Required |
|------|----------|----------|
| G0-A | Is there a delivery date? | If yes → G1 |
| G0-B | Does counterparty benefit from delay? | If yes → written terms required |
| G0-C | Can you recover payment without a contract? | If no → written terms required |

If all three flags are YES: do not pay without written terms.

---

## G1 — Minimum Written Terms

Required before payment:

```
1. Delivery date: [DATE]
2. What is delivered: [SPEC]
3. Penalty if missed: [AMOUNT or %/day]
4. Refund condition: if delivery >X days late → full refund
5. Counterparty signature / acknowledgment
```

Minimum viable format: a LINE/WhatsApp message where counterparty explicitly acknowledges delivery date and penalty. Screenshot = evidence.

---

## G2 — Penalty Calibration

Penalty must hurt them more than the benefit of delaying:

```
If market price rose X% while they held your order:
  Minimum penalty = X% of order value (makes delay EV-neutral for them)
  Better penalty = 2X% (makes delay EV-negative → they won't delay)
```

If you can't negotiate a real penalty: raise the question explicitly. Their resistance to written terms is itself a signal.

---

## G3 — Red Flags During Execution

If counterparty shows these: escalate immediately, don't wait.

- Vague delivery date → ask for specific date, write it down
- "Almost ready" for more than 2 days → trigger penalty conversation
- "Market price went up" as explanation for delay → that's the mechanism you protected against
- Refuses to put delivery date in writing → do not pay

---

## G4 — Post-Delivery Verification

- Confirm delivery matches spec before releasing final payment (if staged)
- If partial delivery: document what was received, what remains
- Keep all written records for 12 months

---

## Self-Test Scenario

> You pre-order 10 units of a product at current price. Delivery promised in 30 days. Market price rises 40% in 2 weeks.

**G0**: Yes delivery date, yes counterparty benefits from delay, yes no formal contract → written terms required.

**G1**: Write: "Delivery by [DATE]. If late, penalty = 2%/day up to 20% of order value. If >15 days late, full refund."

**Result**: Counterparty now has zero incentive to delay — delay costs them more than early delivery.

---

## Key Principle

**合約保護原則**: 任何承諾性交易，付款方主動要求書面違約條款。不依賴對方誠信，依賴結構性激勵對齊。

Parallel principle: MD-133 (stop-first sizing), MD-392 (dependent exposure), MD-157 (first-principles coherence). All three share the same architecture: define failure cost before committing.
