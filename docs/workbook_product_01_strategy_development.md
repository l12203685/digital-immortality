# Workbook #01 — Strategy Development Framework
> Price: $29 | Based on SOP #01 + MD-97/113/116/157/159
> Status: READY TO LIST — list on Gumroad when G2 triggers (≥10 DMs in 48h)

---

## Gumroad Listing Copy (paste-ready)

**Title:** The Strategy Development Workbook — Build Systems That Actually Hold Up

**Short description (255 chars):**
A step-by-step worksheet that walks you through the 5 gates separating a real edge from a backtest illusion. Based on 9 years of quantitative trading decisions. One framework, reusable forever.

**Long description:**
Most strategies fail not because the idea was bad — but because the development process skipped the hard questions.

This workbook gives you the exact 5-gate framework used to evaluate every strategy before it gets capital. Not theory. Executable worksheets with worked examples.

**What's inside:**
- Gate 0: Mechanism worksheet — articulate the edge in one sentence (no parameters allowed)
- Gate 1: Degrees of freedom audit — count P + B + I, set minimum OOS trade threshold
- Gate 2: OOS sample size calculator — walk-forward windows, regime coverage check
- Gate 3: Kill conditions pre-commitment worksheet — MDD, WR, PF thresholds before backtest
- Gate 4: Deployment contract — sign off before live capital

Each gate includes:
- The principle behind it (with MD reference)
- A worked example (DualMA BTC)
- A blank worksheet for your own strategy
- Failure modes to avoid

**Who this is for:** Traders who have backtested strategies before and want to know why they stopped working live.

**Format:** PDF, 28 pages, instant download.

---

## Workbook Content

### Introduction (1 page)

The gap between a backtest and a live system is not technical — it's process.

Every strategy that failed live had a moment when the developer could have caught it. They didn't, because they had no checklist. This workbook is the checklist.

Five gates. Each one designed to kill bad strategies before they kill your capital.

---

### Gate 0: Mechanism Articulation Worksheet

**Principle:** MD-97 — 策略=先抽象結構再固定參數 (abstract structure before fixing parameters)

**The test:** Can you explain why this strategy makes money without naming a single parameter?

**Worked example:**
- ❌ FAIL: "DualMA with 10/30 periods goes long when fast crosses slow"
- ✅ PASS: "Trend-following exploits momentum persistence: markets that have been moving tend to continue moving. The strategy extracts this by buying breakouts and holding until momentum reverses."

**Your worksheet:**

```
Strategy name: _______________________

Edge mechanism (no parameters):
_______________________________________________
_______________________________________________

Does this mechanism have a structural reason to persist?
[ ] YES — explain: _____________________
[ ] NO — stop here, redesign the hypothesis

Mechanism category:
[ ] Trend-following (momentum persistence)
[ ] Mean-reversion (overextension correction)  
[ ] Carry (rate differential)
[ ] Market-making (bid-ask spread capture)
[ ] Event-driven (information asymmetry)
[ ] Other: _____________________
```

---

### Gate 1: Degrees of Freedom Audit

**Principle:** MD-113 — 無參數≠免疫過度最佳化 (zero parameters ≠ immune to overfitting)
**Principle:** MD-114 — 參數數量=功能性指標非絕對最小化

**The formula:**
```
DoF = P (parameters optimized) + B (booleans/regime filters) + I (indicators used)
Minimum OOS trades required = DoF × 10
```

**Worked example:**
- DualMA BTC: P=2 (fast/slow periods), B=1 (long-only flag), I=2 (MA, ATR stop) → DoF=5
- Minimum OOS trades needed: 5 × 10 = 50 trades
- Actual OOS trades: 200 → 40× coverage → PASS

**Your worksheet:**

```
Parameters optimized (P): ___ 
List them: ___________________________

Boolean switches (B): ___
List them: ___________________________

Indicators used (I): ___
List them: ___________________________

Total DoF = P + B + I = ___

Minimum OOS trades required: DoF × 10 = ___

Actual OOS trades available: ___

Coverage ratio: actual ÷ minimum = ___ ×

[ ] ≥ 10× — PASS, proceed to Gate 2
[ ] < 10× — FAIL, extend OOS window or reduce DoF
```

---

### Gate 2: Walk-Forward Validation Setup

**Principle:** MD-98 — 策略存活=近期vs歷史60%門檻
**Principle:** MD-144 — WFA全樣本悖論=分段最佳化優於整體

**The test:** Does the strategy hold up across different market regimes, not just in aggregate?

**Walk-forward structure:**
```
Total data: split 70% IS / 30% OOS
OOS window: minimum 6 months, prefer 12+
Regime coverage: trending + mean-reverting + sideways (at least 2 of 3)
Survival rate test: rolling_30d_Sharpe ÷ historical_OOS_Sharpe ≥ 0.60
```

**Worked example:**
- DualMA BTC: IS=2019-2022, OOS=2023-2024
- Trending regime (2021 bull): Sharpe=1.8 — PASS
- Sideways regime (2022 bear): Sharpe=0.6 — marginal
- Mean-reverting regime (2024): Sharpe=0.4 — WEAK
- Verdict: CONDITIONAL GO — trending regime only, add regime filter

**Your worksheet:**

```
IS period: _____________ to _____________
OOS period: _____________ to _____________
OOS months: ___

Regimes present in OOS:
[ ] Trending (ADX > 25): Sharpe = ___
[ ] Mean-reverting (ADX < 20): Sharpe = ___
[ ] Sideways/high-vol: Sharpe = ___

Overall OOS Sharpe: ___
Minimum required (any strategy): 0.8

[ ] All regimes ≥ 0.8 — GO, no regime filter needed
[ ] Some regimes weak — CONDITIONAL GO, add regime filter
[ ] All regimes < 0.8 — STOP, redesign mechanism

Cross-asset validation (same mechanism, different instrument):
Instrument: _____ OOS Sharpe: ___
[ ] ≥ 0.6 — mechanism generalizes, PASS
[ ] < 0.6 — instrument-specific, flag risk
```

---

### Gate 3: Kill Conditions Pre-Commitment

**Principle:** MD-96 — 策略管理先定失效條件
**Principle:** MD-133 — 風控前置=停損反推進場點

**The rule:** Write kill conditions BEFORE you see live results. Post-hoc kill conditions are not kill conditions.

**Kill condition formula:**
```
MDD kill = historical_OOS_MDD × 1.5  (never exceed 1.5× historical drawdown)
WR kill = OOS_WR × 0.75  (minimum viable win rate after friction)
PF kill = OOS_PF × 0.8  (minimum viable profit factor)
Sample minimum: 10 completed trades before kill conditions are valid
```

**Worked example:**
- DualMA BTC OOS: MDD=8%, WR=55%, PF=1.6
- Kill conditions: MDD>12%, WR<41%, PF<1.28
- Sample minimum: 10 trades before any kill assessment

**Your worksheet:**

```
OOS MDD: ___% → Kill at: ___ × 1.5 = ___%
OOS WR: ___% → Kill at: ___ × 0.75 = ___%
OOS PF: ___ → Kill at: ___ × 0.8 = ___
Sample minimum: 10 trades

Kill condition file location: _____________________
(write this to a file before going live — not in your head)

Date written: _______________
Signed: _______________  (commitment device)
```

---

### Gate 4: Deployment Contract

**Principle:** MD-159 — 試單與加碼單各自獨立正EV
**Principle:** MD-1 — 看導數不看水平

**The contract:** Before any capital goes live, sign off on all six fields. If any field is blank, you're not ready.

```
DEPLOYMENT CONTRACT — Strategy: _____________________

Date: _______________

1. Mechanism (one sentence, no parameters):
   _______________________________________________

2. Kill conditions (MDD / WR / PF / sample):
   MDD > ___% | WR < ___% | PF < ___ | min trades: ___

3. Position sizing formula:
   lots = (equity × 1%) ÷ (ATR × multiplier)
   ATR period: ___ | Multiplier: ___

4. Trial position size: ___% of full size
   Condition to scale to full: ___________________
   (e.g., "10 trades, WR ≥ OOS baseline, no kill condition triggered")

5. Regime conditions for this strategy:
   [ ] Trending (ADX > 25)
   [ ] Mean-reverting (ADX < 20)  
   [ ] Any regime
   Note: ___________________________________

6. Review frequency: every ___ trades or ___ days (whichever first)
   Review checklist: survival_rate check + kill condition check + regime alignment

Signed: _____________________  Date: _______________
```

---

### Appendix: Common Failure Modes

**Failure 1: Mechanism described in terms of parameters**
> "Short when 14-period RSI > 70" is not a mechanism. "Exploit mean-reversion after overextension" is.

**Failure 2: In-sample OOS**
> Tuning parameters to maximize performance on the "OOS" set makes it in-sample. True OOS = data your optimizer never touched.

**Failure 3: Kill conditions set after seeing results**
> "I'll stop at 15% MDD" decided after a 12% drawdown is not a kill condition. It's hope with a number attached.

**Failure 4: No cross-regime validation**
> A strategy backtested only on 2020-2021 (trending, low-friction) will fail in a different regime. Regime coverage is not optional.

**Failure 5: Full size on deployment**
> Trial position (25-50% of full size) for the first 10 trades is not caution — it's protocol. Full size requires 10 trades of evidence.

---

### Quick Reference Card (print this)

```
Gate 0: One mechanism sentence, no parameters
Gate 1: DoF × 10 = minimum OOS trades needed
Gate 2: OOS Sharpe ≥ 0.8, survival_rate ≥ 0.60
Gate 3: Kill conditions written BEFORE live trading
Gate 4: Deployment contract signed, trial position first

Kill formula: MDD × 1.5 | WR × 0.75 | PF × 0.8
Size formula: lots = (equity × 1%) ÷ (ATR × mult)
Trial rule: 25-50% size for first 10 trades
```

---

## Gumroad Setup Steps (when G2 triggers)

1. Go to gumroad.com → New Product → Digital Product
2. Title: "The Strategy Development Workbook"
3. Price: $29
4. Upload: export this file as PDF (Markdown → PDF via Pandoc or browser print)
5. Cover image: plain dark background, white text, title + "5 Gates to a Live-Tradable System"
6. Description: paste the long description above
7. Publish → copy link → add to X bio / link-in-bio

**Time to list after G2 triggers: ~20 minutes**
