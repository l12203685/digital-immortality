# Content Seeds — B7 Knowledge Output

Generated: 2026-04-14 | Source: 283 insights from recursive_distillation.md

SOP graph hubs: #001 Trading Strategy Development, #082 Revenue Activation Milestone Tracker, #083 Daily Posting Execution Ritual, #070 Revenue Conversion Protocol, #004 Strategy Failure & Kill Decision Tree

---

## 1. Crypto Prop Desk Risk Controls Are A Transferable Four Layer Framework
**Score**: 11.0 | **Cycle**: 172 | **Format**: post
**Categories**: trading

> @Crypto's 当日刷单率胜率公司利润合伙人风控报告完整版.sql implements a four-layer risk control framework for a crypto prop desk: (1) wash-trade detection — daily volume × win-rate × profit factor query identifies accounts whose statistical profile matches manipulated trading; (2) partner profit-share calculation — automated daily P&L split between company and limited partners with configurable ratio; (3) anomaly compensation registry — 异常赔付登记表 tracks periods of abnormal price movement where the desk compensates traders for exchange-caused losses (slippage, feed failures, circuit breakers); (4) big-user trade record monitoring — big_user_trade_record.csv enables identification of account clusters with correlated trading behavior that may indicate wash trades or coordinated manipulation.
The key insight is the asymmetry of the framework: it simultaneously protects the desk from being gamed by traders (wash-trade detection, correlated behavior monitoring) and protects traders from being harmed by the desk's infrastructure failures (anomaly compensation).

**Source insight**: `crypto-prop-desk-risk-controls-are-a-transferable-four-layer-framework` (cycle 172)

---

## 2. Strategy Exchange As Structured Learning Protocol Formal Accountability Not Informal Sharing
**Score**: 10.0 | **Cycle**: 173 | **Format**: article
**Categories**: trading, systems

> The 202007 and 202010 exchange batches, read together with 歸檔/作業交換細則.txt and the monthly 交換區_建議 review files, reveal that the strategy exchange program is a formal learning protocol with accountability infrastructure, not a casual sharing arrangement.
For ZP: this exchange SOP is a transferable framework for any community with shared epistemic standards — the three components (submission gate, named accountability, reciprocal access) are the minimum viable accountability infrastructure.

**Source insight**: `strategy-exchange-as-structured-learning-protocol-formal-accountability-not-informal-sharing` (cycle 173)

---

## 3. Taiwan Futures Community Conventions Form A Distinctive Local Toolkit Cdp Settlement Intraday Focus
**Score**: 10.0 | **Cycle**: 173 | **Format**: post
**Categories**: trading

> The 202007+202010 batches, read alongside the broader @StrategyManagement and @AK archives, reveal a coherent set of Taiwan-futures-specific conventions that constitute a distinctive local toolkit not found in Western quantitative trading literature.
The significance of this local toolkit is epistemological: these four conventions encode community-accumulated knowledge about Taiwan futures market structure that is not derivable from first principles or from backtesting alone.

**Source insight**: `taiwan-futures-community-conventions-form-a-distinctive-local-toolkit-CDP-settlement-intraday-focus` (cycle 173)

---

## 4. Strategy Exchange Program Is A Community Driven Edge Amplifier Not Just A Sharing Mechanism
**Score**: 10.0 | **Cycle**: 172 | **Format**: post
**Categories**: trading

> The @StrategyManagement 歸檔 directory reveals that the strategy exchange is a structured institution: 作業交換細則.txt defines the exchange rules; monthly 交換區_建議 files (202010 through 202202) record individual approval decisions with specific improvement feedback; the 202007 batch shows 20+ contributors each submitting a strategy with formal description file, parameter ranges, and WF results.
For B3.1 distillation and ZP: the strategy exchange SOP is a transferable framework for any community with shared epistemic standards.

**Source insight**: `strategy-exchange-program-is-a-community-driven-edge-amplifier-not-just-a-sharing-mechanism` (cycle 172)

---

## 5. Sop117 Dna Core Audit As Milestone Protocol Design
**Score**: 9.27 | **Cycle**: 100 | **Format**: thread
**Categories**: systems, philosophy

> SOP #117 (DNA Core Audit Protocol) encodes a principle about protocol design: audits that run on milestone triggers (every ~90 cycles) are structurally different from audits that run on drift triggers.
Milestone-triggered audits find drift before it becomes visible symptomatically.

**Source insight**: `sop117-dna-core-audit-as-milestone-protocol-design` (cycle 100)

---

## 6. Dashboard Redesign Audit Plain Zh Design System Edward Mental Model
**Score**: 9.21 | **Cycle**: 156 | **Format**: post
**Categories**: systems

> Dashboard redesign audit completed (staging/dashboard_redesign_audit.md + platform/pretty_translate.py).
Core diagnosis: dashboard built for engineer self-monitoring, not Edward's mental model.

**Source insight**: `dashboard-redesign-audit-plain-zh-design-system-edward-mental-model` (cycle 156)

---

## 7. Var And Greeks Are The Minimum Shared Vocabulary For Portfolio Level Risk Communication
**Score**: 9.0 | **Cycle**: 172 | **Format**: post
**Categories**: trading

> Files 69-99 include both Jorion's VaR (3rd ed.) and a Greek Letters.docx at the 財務相關知識/期貨與選擇權 layer.
The significance is not the formulas — it is the standardization: when every participant in a risk system uses the same VaR model and the same Greek definitions, risk can be aggregated, allocated, and communicated without ambiguity.

**Source insight**: `VaR-and-Greeks-are-the-minimum-shared-vocabulary-for-portfolio-level-risk-communication` (cycle 172)

---

## 8. 202007 Exchange Batch Reveals Entry Topology Diversity Is Bounded Exit Topology Is Convergent
**Score**: 9.0 | **Cycle**: 172 | **Format**: post
**Categories**: trading

> The 2020-07 strategy exchange batch (10+ readable submission files) shows a striking asymmetry: entry conditions are highly diverse across contributors — ATR-based breakout (Bohun), correlation trend (ChienShen), range comparison (JohnsonLo), Keltner channel (TimChen), gap-reversal (WenZiGi), Parabolic SAR (Kuang), CCI breakout (YenShen), pivot points (shuenhua), ORB (WGN), custom RSI (Morton) — but exit conditions converge to the same 3-4 patterns across almost all submissions: (1) trailing stop at N-bar low/high, (2) fixed stop at entry minus N points, (3) time-based forced exit (session close or N bars), (4) no-new-high/low pattern detection.
The implication: alpha generation is in the entry condition differentiation; risk management is in the exit condition standardization.

**Source insight**: `202007-exchange-batch-reveals-entry-topology-diversity-is-bounded-exit-topology-is-convergent` (cycle 172)

---

## 9. Engine Stopped Frozen G3 Clock Second Order Human Gate
**Score**: 8.41 | **Cycle**: 113 | **Format**: post
**Categories**: trading, systems

> Trading engine status: STOPPED (tick_count=91 from prior run, DRY_RUN restart ticks=2).
Design principle: second-order gates (automated kills + human restart) are intentionally asymmetric.

**Source insight**: `engine-stopped-frozen-g3-clock-second-order-human-gate` (cycle 113)

---

## 10. Walk Forward Date Overrides Are Poor Mans Regime Detection Hardcoded But Universal
**Score**: 8.0 | **Cycle**: 173 | **Format**: post
**Categories**: trading

> Across all 20 contributors in the 202007 and 202010 batches, a near-universal implementation pattern appears: hardcoded date breakpoints in strategy code where parameter sets switch based on when the trade occurs.
Example patterns observed: `if Date > 1090101 then FastLength=12 else FastLength=8`, `if CurrentDate >= 20201001 then ATRMult=1.8 else ATRMult=2.2`, pivot calculations with separate parameter tables for pre-2020 and post-2020 periods.

**Source insight**: `walk-forward-date-overrides-are-poor-mans-regime-detection-hardcoded-but-universal` (cycle 173)

---
