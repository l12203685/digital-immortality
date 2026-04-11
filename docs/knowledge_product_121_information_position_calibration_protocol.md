# SOP #121 — Information Position Calibration Protocol

**Root insight**: MD-429 (POSITION_DETERMINES_RANGE, 2017-10-11)
**Backing MDs**: MD-429 / MD-104 (information asymmetry drives action) / MD-133 (edge → action, no edge → wait)
**Created**: 2026-04-11T22:30Z
**Series**: SOP #01~#121 COMPLETE ✅

---

## Core Principle

Before evaluating any option, determine your **information position** first.

In poker: position determines hand range, not hand strength alone.
Generalized: your information position (who acts before you, what you can observe before deciding) determines your safe action range.

```
Late position (info-rich)  → wider option set available
Early position (info-poor) → restrict to highest-confidence options only
Worst position (SB)        → default = no action, require overwhelming edge
```

---

## G0 — Detect Information-Asymmetric Decision

Trigger this protocol when:
- You're about to make a move where others have information you don't yet have
- You're choosing a strategy before observing how others respond
- You're entering a competitive situation (market, negotiation, job market, partnership)

**Skip if**: pure analysis with no other actors involved (e.g., solo technical work with full information).

---

## G1 — Map Your Information Position

Ask: **"Who acts before me, and what can I observe before I decide?"**

| Position Type | What It Means | Poker Equivalent |
|---|---|---|
| **Late** | Most relevant actors have already moved; their signals are observable | Button / CO |
| **Middle** | Some signals available, some not yet | HJ / MP |
| **Early** | Acting before most others; minimal observable signals | UTG / UTG+1 |
| **Forced** | Already committed; evaluate using sunk cost + pot odds | Big Blind |
| **Worst** | Acting first with zero observable signals; re-acting in worst position | Small Blind |

---

## G2 — Calibrate Action Range to Position

| Your Position | Default Action Range |
|---|---|
| Late | Consider full option set; use all available signals to refine |
| Middle | Consider primary options; skip high-variance secondary options |
| Early | Restrict to top-tier, highest-confidence options only |
| Forced | Calculate EV from current committed resources; not from ideal entry |
| Worst | **Default = no action.** Require overwhelming edge (≥2× normal threshold) before acting |

**Key rule**: If you find yourself wanting to act from worst position because "the opportunity looks good," treat this as a yellow flag. The opportunity may genuinely be good — but you're evaluating it without the signals that late-position actors will have.

---

## G3 — Check for Position Improvement Options

Before acting from an unfavorable position, ask:
1. **Can I wait for more information?** (Convert early position to late position by observing first)
2. **Can I create information?** (Low-cost probes, pilot tests, small trials that generate signal)
3. **Do I have private information that offsets my position disadvantage?** (Unique knowledge = synthetic late position)

If any of these apply → use the available lever before committing.

---

## G4 — Execute with Position-Appropriate Sizing

| Position | Action Size / Commitment |
|---|---|
| Late + strong signal | Full commitment available |
| Late + weak signal | Half commitment, re-evaluate after more info |
| Middle | Reduced commitment; no doubling down until position improves |
| Early | Minimal commitment / pilot only |
| Worst | Pass, or single minimal test if opportunity-cost of missing is very high |

---

## G5 — Document and Update

After the decision resolves:
1. Was your position assessment correct? (Did others have information you didn't?)
2. Did the outcome match what late-position actors saw? (Calibration check)
3. If you acted from early/worst position: what did you learn about whether that was correct?

Write findings to `kill_lessons.jsonl` or `memory/insights.json` as applicable.

---

## Anti-Patterns

| Anti-Pattern | Why It Fails |
|---|---|
| "This opportunity looks great" without position check | Absolute opportunity quality ≠ position-adjusted EV |
| Acting from SB because "the hand is too good to fold" | Even premium options lose EV from worst position |
| Treating all markets/negotiations as "late position" | You always have less info than you think before acting |
| Waiting indefinitely for "perfect information" | Late position ≠ full information; good-enough signal is sufficient |

---

## Application Examples

**Trading**: Entering a new strategy before regime is confirmed = early position. Wait for regime signal (let others act first = observe market direction) before committing full sizing.

**Career decision**: Evaluating a job offer before understanding the team dynamics / manager style = early position. Run discovery conversations first (convert to late position), then evaluate.

**Negotiation**: Making an offer before understanding counterparty's constraints = early position. Ask questions first; let them reveal their position before committing to a number.

**Partnership**: Investing in a collaboration before observing how the other party handles small stakes = worst position. Run a low-cost test project first (probe = position improvement mechanism).
