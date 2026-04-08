# Publish Thread — SOP #32: Edge Decay & Signal Crowding Protocol

**Hook tweet:**
> Your strategy stopped working. You didn't change anything.
>
> The market changed it for you.
>
> Here's how to detect edge decay before it drains your account. 🧵

---

**Tweet 2 — The problem:**
> Most traders catch edge decay at the drawdown stage.
>
> By then you've already paid for it.
>
> The goal: detect the decay signal *before* it becomes a drawdown signal.

---

**Tweet 3 — Edge type classification (MD-108):**
> First question before any deployment: what *kind* of edge do you have?
>
> Type A: Structural (market mechanism) — slowest to decay
> Type B: Behavioral (human bias) — moderate decay
> Type C: Statistical (optimization artifact) — fast decay
> Type D: Public indicator — fastest decay
>
> Public indicators: marginal edge approaches zero as adoption scales.

---

**Tweet 4 — The baseline fingerprint:**
> Day 1 of deployment: lock in your fingerprint.
>
> Historical OOS Sharpe. Win rate. Avg R/R. Crowding level.
>
> Without a baseline, you can't detect drift. You'll just feel confused when it changes.

---

**Tweet 5 — Survival rate (MD-98):**
> Every 30 live trades:
>
> survival_rate = rolling_30d_Sharpe ÷ historical_OOS_Sharpe
>
> < 0.80 → monitor weekly
> < 0.60 → pause. run diagnosis.
>
> This metric fires *before* drawdown becomes severe.

---

**Tweet 6 — Bayesian posterior update (MD-109):**
> When survival_rate < 0.60, don't panic. Update your belief systematically:
>
> 1. Is the regime correct for this strategy?
> 2. Are similar strategies also underperforming? (market-wide vs specific)
> 3. Are entry signals still clustering near inflection points?
> 4. Does the strategy survive at 2× transaction costs?
>
> Each answer shifts P(edge_decayed).

---

**Tweet 7 — The cohort test:**
> Underrated diagnostic: check your strategy's cohort.
>
> If ALL trend-following strategies are down this month → market-wide stress, not your edge decaying.
>
> If only yours is down → specific signal. Investigate front-running and cost sensitivity.

---

**Tweet 8 — Response protocol:**
> P(edge_decayed) > 0.65 → reduce to 25% size. Diagnose. Give it 30 trades.
> P(edge_decayed) 0.50–0.65 → hold at 50%. Paper-track killed version for 60 days.
> P(edge_decayed) < 0.50 → likely regime problem. See SOP #27.
>
> Precision matters. Don't kill good strategies during bad regimes.

---

**Tweet 9 — The kill condition:**
> If P > 0.65 AND survival_rate stays below 0.80 after 30 reduced-size trades:
>
> Kill. No exceptions.
>
> Capital freed. Bandwidth freed (MD-143). Open new research thread immediately.

---

**Tweet 10 — Depth × breadth replenishment (MD-110):**
> Every kill event → mandatory: open one new strategy research thread.
>
> Requirements:
> - Different edge_type from what you killed
> - Paper-test candidate within 30 days
>
> Bandwidth is finite (MD-143). Killing frees it. Reinvest it.

---

**Tweet 11 — What not to do:**
> The most expensive mistake: "It'll come back."
>
> It might. But:
> - Your capital is paying for the wait
> - Your bandwidth is blocked (MD-143)
> - You're not developing the next edge
>
> Sunk cost is not a trading thesis.

---

**Tweet 12 — Close:**
> Edge decay is a law, not an exception.
>
> Every edge gets found, copied, crowded, and arbitraged.
>
> The only durable edge: detecting decay faster than other participants.
>
> SOP #32: Edge Decay & Crowding Protocol
> Full framework: [link to repo]
>
> — SOP series #01–#32 now complete
