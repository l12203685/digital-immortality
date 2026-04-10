# SOP #16 — Information Edge Classification: Know What You Know Before You Trade

> Source MDs: MD-141 (一致性缺失=隱性濾網未明言), MD-140 (思維層級=比對手多一層才有EV), MD-108 (年度風暴比=跨年Regime偵測器), MD-326 (技術合作=角色邊界先書面確認), MD-135 (實操知識=skin-in-the-game才外流)
> One-claim: "You don't have an edge. You have a belief. These are not the same thing."

---

## Why This SOP Exists

Most traders enter positions believing they have an information edge. Very few have classified what type of edge they actually hold — or verified that the edge still exists.

MD-141: Inconsistency in your own trading behavior signals an implicit filter you haven't articulated. If you sometimes take a signal and sometimes don't, you have a hidden rule you haven't named. Name it or remove it.

MD-140: Edge is relative to the opponent's thinking level. L1 = price movement. L2 = what others think about price. L3 = what others think others think. You need to be at L+1 relative to your competition. If everyone is at L2, L3 is edge. If L3 is widely known, it's no longer edge.

MD-135: Real operational knowledge only flows from practitioners with skin in the game. A public indicator is edge approaching zero (MD-107). Proprietary process + real risk capital = the only sustainable moat.

---

## Gate Sequence (4 gates)

### G0 — Classify Your Edge Type

Before entry, state which of three edge types you hold:

| Type | Definition | Example |
|------|-----------|---------|
| **Structural** | You have access others don't (data, speed, venue) | Tick data, co-location, dark pool flow |
| **Temporal** | You act faster or earlier in a known sequence | Pre-open gap fade, earnings drift window |
| **Interpretive** | You process the same data differently (higher L-level) | Regime classification, cross-asset correlation read |

**Rule**: You must name one type before entry. If you cannot classify, the position is belief not edge. Abort.

### G1 — Verify Edge Is Not Already Priced

Apply the MD-107 public-signal decay test:

1. Is this signal described in any public research, strategy guide, or social feed?
2. If yes: when was it first published? What is the estimated adoption rate?
3. Apply decay function: edge_remaining = original_edge × (1 - adoption_fraction)

**Kill condition**: adoption_fraction ≥ 0.5 → edge_remaining < 50% → require confirmation from G2 before proceeding.

### G2 — Confirm Thinking-Level Advantage

State explicitly what level your thesis operates at and what level your counterparty is at:

- **Your L-level**: _______
- **Market consensus L-level**: _______
- **Delta**: Your L - Market L = _______

**Rule**: Delta ≥ +1 required to proceed. Delta = 0 means you are the average participant. Delta = -1 means you are the fish.

Example: if the market is reacting to CPI headline (L1), and you are trading the regime-shift implied by the CPI trend over 6 months (L3), delta = +2. Proceed.

### G3 — Articulate the Hidden Filter

Per MD-141: if you have ever passed on a signal from your own system, you have an implicit filter. Before this trade:

1. List any reason you might skip this signal despite it meeting system rules.
2. If any reason exists → name it as a formal rule → add it to the system → apply it consistently.
3. If you cannot name it as a rule → it is behavioral noise → execute the system signal without override.

**Rule**: Overrides without named rules are system corruption. Either codify the filter or suppress the override.

---

## Self-Test Scenario

**Situation**: BTC showing SHORT signal from DualMA. Public sentiment is bearish. Three traders on CT posted the same short setup this morning.

- G0: Edge type = **Interpretive** (regime classification) → name it explicitly
- G1: Public adoption of "BTC bear trend" → high. Apply decay. Is your thesis the same as the crowd's or different? If same → edge ≈ 0 → abort or reduce size
- G2: If crowd is at L1 (price falling), and you have L2 (regime = TRENDING, not reversal) → delta = +1 → proceed with reduced confidence
- G3: Any reason to skip? "Feels risky today" = unnamed filter = suppress override → execute system signal

**Verdict**: CONDITIONAL GO — reduced size (50% of normal) due to G1 public-signal overlap.

---

## When to Use This SOP

- Before any discretionary override of a system signal
- Before entering a new strategy into live trading
- Quarterly: audit recent trades for edge-type distribution (are you drifting toward belief-based entries?)

---

## Connection to Other SOPs

- SOP #01 (Strategy Development): G0 of this SOP = G0 of strategy development — structure before parameters
- SOP #10 (Decision Under Uncertainty): This SOP operationalizes Kernel 2 (information asymmetry mapping)
- SOP #15 (Backtest Deception): G1 of this SOP extends the OOS proof — if your backtest is built on a public signal, the OOS period may already show decay
