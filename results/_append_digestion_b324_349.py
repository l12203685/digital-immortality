"""Append batch 324-349 (TXDL secondary variants + QTC series) to digestion log.

B2 pipeline. 2026-04-14. 26 new TXDL strategy sources from 'Keep/s !...' dirs.
These are source-code siblings of primary strategies OR novel strategies not
present in primary dirs (QTC series, 943 wrappers, CDP, Neckline, GT, OverHeat,
Ambulance, LongBreak, HL3day, ConMove, MA variants, JumpGap family, avgmid,
MCB02 variants).
"""
from __future__ import annotations

import json
from pathlib import Path

BASE = Path("C:/Users/admin/workspace/digital-immortality/results")
TS = "2026-04-14T11:20"

entries: list[dict] = [
    {
        "path": "E:/@交易/@AVAVA/Keep/s !@_TXDL_1_001_ConMove01_202106/.code.20210716_224413.txt",
        "summary": "ConMove01 (TX 1-min L1) — 'consecutive-move' breakout. be_n/se_n bars of same-direction close>open (or <) validated over 5*3*2-factor lookbacks (condition11/21 triangular loops). Entry: close-close expansion > 30+5 pts AND directional consistency -> stop-buy at highest(c, 5^be * 3^be * 2^be). Exit: risk-unit = entry-bar's highest-lowest; after _max_profit > 1R, exit at entryprice + R * _R * _PF (else hard stop at entryprice - R * _R). WF table (annually): _R 0.25-0.5, _PF 0.6-0.9. Demonstrates multi-timescale consistency filter as a single compounded boolean.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/s !@_TXDL_1_003_ConMove3m_202106/.code.20210714_184855.txt",
        "summary": "ConMove3m (TX 3-min) — distilled 2-factor (5,2) consecutive-move variant. Entry: mp=0 condition + c>c[5^i * 2^j] for all i,j<=_pa -> stop-buy at highest over pa^5 * pa^2 window; mirror short. Novel staircase exit: after profit crosses R/4, R/2, R, R*_PF_m cascade, each tier moves stop up to entryprice+cost / +R/2 / +R / +(profit-R). Illustrates profit-ladder exit as granular trailing mechanism instead of single trailing stop.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/s !@_TXDL_1_003_MA_202106/.code.20210714_184942.txt",
        "summary": "TX 3-min MA L1 — dual-MA trend + daily-close bias filter. _ma_len = 2*300/bar, slow = 2x. Entry: fast MA > slow AND close > 20-day avg closed -> long stop at H; mirror short. Stoploss dynamic: (avg highd - avg lowd) * 1.5, clipped [50,250]. Three-tier exit: trailing-stop above _profit_m*SL, breakeven-stop above _breakeven_m/3*that, else hard SL. Re-entry: flat + last trade profitable + settlement day = carry position direction at market. Classic trend + regime-adaptive SL width.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/s !@_TXDL_1_003_MA+Reverse_202106/.code.20210714_184944.txt",
        "summary": "TX 3-min MA+Reverse L1 — same MA skeleton as 003_MA but entry direction FLIPPED: fast<slow AND c>avg_closed -> long LIMIT at lowd(0) (mean-reversion on down-trend day with above-avg close); mirror short. Same 3-tier trailing/breakeven/SL exit. Same re-entry-on-settlement logic. Demonstrates same machinery can support momentum OR counter-trend entry just by inverting the MA filter — one codebase, two edges.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/s !@_TXDL_1_006_ED007_JumpGap+MA+BackHand_202106/.code.20210714_185014.txt",
        "summary": "TX 6-min gap + MA + backhand reverse. Entry: gap-up beyond prev H AND pulled back to opend*(1-r)+r*lowd(1) AND below 300/bar MA AND MA(len) > MA(len*slow_m) -> long at market (contrarian gap-fade with long-trend filter). Backhand reverse: if short position sees gap-up above prev H, enter LONG at prev-day high stop (flip to correct side, absorbing loss). Settlement close. Captures: when gap + trend disagree, fade gap; when in wrong direction, flip on confirming gap.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/s !@_TXDL_1_006_JumpGap+MA+Filter_202106/.code.20210714_184946.txt",
        "summary": "TX 6-min gap+MA+filter — same gap-fade entry as BackHand variant but backhand uses buytocover/sell EXIT (not flip-entry). Commented code reveals parameter exploration: MA slope tests, lookback_period crossovers — author kept the simplest stable subset. Lesson: iterative complexity pruning; unused conditions left as comments serve as 'decision genealogy' for future re-enable.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/s !@_TXDL_1_006_JumpGapMASQ_202106/.code.20210714_184948.txt",
        "summary": "TX 6-min JumpGapMASQ — minimalist gap-fade: _hour_len=3, _slow_m=1.1, _opend_ratio=0.2. Entry only when mp=0 (no stacked positions). Exit uses minlist/maxlist prev two bars' L/H as stop (tighter trailing via floor of 2-bar low). Annual WF table: _hour_len 1-6, _slow_m 0.1-1.6, _opend_ratio 0.4-1.0 — extreme param flipping shows regime sensitivity — 1-hr fast MA works some years, 6-hr slow works others.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/s !@_TXDL_1_015_EX_RSI/.code.20210714_184857.txt",
        "summary": "TX 15-min EX_RSI — extreme RSI breakout. RSI(c, 15) > 50+20 = long, < 50-20 = short; entry at 3-bar highest/lowest stop. Exits: (1) RSI pulls back inside 70/30 band AND gap-down on long (or gap-up on short) -> backhand exit at market, (2) RSI crosses 50 AND price < entry -> loss-exit, (3) fixed 200-pt SL. Settlement close. Clean asymmetric exit tree: fast-out on regime flip (gap), slow-out on momentum decay (RSI 50), hard-stop on catastrophic move.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/s !@_TXDL_1_018_MCB03_RSI_202107/.code.20210716_164526.txt",
        "summary": "TX 18-min RSI cross — classic MCB03 strategy. RSI > 50+14 (at day open-hi stop) long, <50-14 short. Uses EntriesToday(d)=0 + time 09:00-13:00 filter. WF annual: rsi_len 13-20, thold 11-14, SL 400-650. Exit1: RSI<50 AND (c<entry OR gap-down) -> SL. Exit2: price beyond entry * (1+SL/10000) absolute-band trailing. Exit3: settlement. 7-year WFA table baked in — demonstrates 'embedded parameter-regime-calendar' pattern: no external param file, just inline date-guarded re-assignments.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/s !@_TXDL_1_020_MCB02Chg01_MA+DivRatio_202107/.code.20210716_180934.txt",
        "summary": "TX 20-min MA-bias cross. _ma_div = (MA(c,len)/MA(c,2*len)-1)*1000. Entry: _ma_div crosses +thold from below (long at H stop) or -thold from above (short at L stop), time 09:00-13:30. Exit: _ma_div flips sign AND c past entry OR gap against position -> market out. WF annual: len 7-27, thold 0.6-1.2. Note buggy line 'if date>1210630 _ma_len=1.15' mis-assigns len instead of thold — real-world code has latent bugs in regime-rollover section (to audit later).",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/s !@_TXDL_1_300_CR01_Ambulance_202107/.code.20210714_135143.txt",
        "summary": "'Ambulance' CR01 daily or 300-min L1 — post-extreme-loss re-entry. Requires k>2 bars since day start, not settlement. Long entry: lowestbar(l,4) <= 4/2 (recent bottom in last 2 bars of 4) AND c>min(o[1],c[1]) AND c<MA(c,4). Backhand: if short AND bottom-signal AND c>max(h[1],h[2]) AND c>HL-mid -> buy market (backhand long). Settlement-day re-entry: if same-side and c> entry -> ADD position at market. Fixed 7% (pre-2017) or 10% (post) limit-exit target. Core: catch 'ambulance' V-shaped reversals off liquidation washouts.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/s !@_TXDL_1_avgmid_202106/.code.20210714_184950.txt",
        "summary": "'avgmid' TX intraday — box-break count + avg-midline mean-reversion. Tracks box_high/low break-count per day. Entry: 15-75 min window, range > opend*0.01/4 (vol filter), c crosses back through (h+l)/2 vs prior bar's avg-mid -> long market (mean-revert). R = max(30, (entry-highd - entry-lowd)/2). Exit: _max_profit > 6R -> trail to entry_highd/lowd stop. Absolute SL via setstoploss(R*BPV). End-of-session forced close. Elegant: uses running box-break statistic as volatility gauge instead of ATR.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/s !@_TXDL_2_015_943BB/.code.20210716_224413.txt",
        "summary": "'943_TX_adam0000_LO' — Bollinger Band + ATR breakout with MONTHLY equity-curve circuit-breaker. Entry 1: trend(MA 10-day) rising + 09:00+ -> long at O + AdonL*ATR stop (trend-follow). Entry 2: avgprice < BB-lower -> long at bep (mean-revert BE_reverse). Same for short with BB-upper. Size toggles 1/2 contracts on ATR regime. Monthly max-loss + maxDD circuit-breaker via flagM (closes all + blocks re-entry). Dual trailing stop (bxp = H-atr_ratio_b*ATR + sxp = L+atr_ratio_s*ATR). Settlement re-entry at 13:30. Example of STRATEGY-LEVEL position sizing + RISK-LEVEL monthly kill-switch.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/s !@_TXDL1_015_943TrendChg01_202106/.code.20210716_224413.txt",
        "summary": "TX 15-min TrendChg — 3-day rising highest_low + gap-up confirm trend entry. Entry: opend > highd(1) AND highest(l, day_kbars) rising 2 bars -> long market; mirror short with gap-down + falling lowest_high. R = range_m * min(avg_ranged, 1-day range). Exit: (a) <R_m*R floating profit -> hard SL at entry-R, (b) >R_m*R -> dynamic trailing at entryprice + (max_profit - trailing_stop). Settlement close. Combines daily-HL trend structure with intraday session-range risk unit — multi-timeframe coupling.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/s !@_TXDL1_300_HL3day_202106/.code.20210714_184952.txt",
        "summary": "TX 300-min (daily-swing) HL3day — simplest breakout possible. Take max(highd 0..3) and min(lowd 0..3). If range > 175 pts -> long at max-HL stop, short at min-LL stop. setstoploss(R*BPV) where R=150, setprofittarget(R*1.4). Settlement exit. Six lines of logic. Benchmark for 'null-hypothesis edge' — any more complex strategy must beat this trivial 3-day Donchian.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/s !_TXDL_1_005_CDP/.code.20210713_194425.txt",
        "summary": "TX 5-min CDP (Contrarian Daily Pivot) — classic CDP = (H+L+2C)/4 + AH/NH/AL/NL levels. Entry 1 (trend): countif(c>AH,5)>=4 -> long at highd(0) stop. Entry 2 (mean-revert): openD > AH+(AH-NH)/2 OR gap above AH with 2-day range larger than prior two -> SHORT at AH (fade). Reverse-day: if holding B2/B2a and day range narrows, flip short. Exits: (1) cross NL/NH beyond entry-distance OR counter-dir past entry, (2) 7%-band limit exit. Classic pivot-point setup with explicit trend-vs-mean-revert entry bifurcation.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/s !_TXDL_1_005_QTC04HModelSpread/.code.20210713_203202.txt",
        "summary": "TX 5-min QTC04 'H-Model Spread' — TX vs TWSE cash spread reversion. spread = TX - TWSE, adjusted for settlement months (7/8/9 use tradeday-linear dayshift correction). Entry long: spread <= -downband (TX discount) AND fast-MA<slow-MA AND c<slow-MA (confirm weakness in TX) -> BUY at highd(1)+1 stop OR highest(h,long_len)-3. Short mirror at upper band. Monthly loss/maxDD circuit-breaker via flagM (100K/100K). Spreads expanded 3x during low-price-regime (linefast<6800). Example of INDEX-FUTURE vs CASH arb, a real market-structural edge (not pattern-based).",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/s !_TXDL_1_010_Neckline/.code.20210713_194427.txt",
        "summary": "TX 10-min Neckline — 2-day candlestick pattern: day(2) red + day(1) green + closing higher + today c>o (bullish engulfing-like). Entry: (highd(1)+highd(2))/2 stop-buy (neckline of 2-day pattern). EntriesToday<2 daily cap, k>in + k<300/bar time-filter. Exit1: countif(h<lowd(1),3)=3 AND c<o -> if early+profitable -> flip (BH1), else loss-stop. Exit2: first 2 bars + c<lowest(L[1],2) -> 'wrong-buy' exit. Settlement close. Compact 2-day pattern playbook with structural exit triggers.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/s !_TXDL_1_015_QTC00_RSI/.code.20210713_203158.txt",
        "summary": "TX 15-min QTC00 RSI — identical logic-DNA to 015_EX_RSI (code clone). RSI>70 (15-len, thold 20) -> long at 3-bar high stop; <30 short. Exits: RSI-regime-flip via gap + position flip, RSI-cross-50 with loss -> SL, hard 200-pt SL. Catalogued as 'QTC00' baseline for the QTC series (orthogonal RSI variants across 5/15/18/19/30-min frames).",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/s !_TXDL_1_019_QTC06OneStick/.code.20210713_203145.txt",
        "summary": "TX 19-min QTC06 OneStick — first-bar of day pivot strategy using (close[1] + 0.25*(H+L+O+C)[2])/2 as reference ImAV. Entry 'unnormal': cond11 (c>ImAV) -> long at max(H, ImpH) + countif(c>c[1]) penalty; mirror short. Entry 'normal': cond43 (c>prev-mid + c>c[1]) -> long at max(highd(1), highd(0)) + avg(H-L,k) stop. Monthly loss/maxDD circuit-breaker (140K). Backhand at bar 0 if L=lowd(0) flip to short. 13:30 'bad entry' exit if unprofitable + c<entry. Highly heuristic multi-entry strategy with many inline filters.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/s !_TXDL_1_020_MCB02MA/.code.20210716_164730.txt",
        "summary": "TX 20-min MCB02 MA — simplest MA-bias cross. div = MA(c,27) - MA(c,54). Entry: div crosses +thold(12) from below long, -thold from above short, time 09:00-13:30. Exit: div sign-flip AND c past entry OR gap against -> market out. Settlement close. Absolute minimal MA-divergence template; likely used as 'strategy skeleton' for the MCB02 family, with child strategies adding WFA date tables or division-ratio variants.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/s !_TXDL_1_025_GT/.code.20210713_183557.txt",
        "summary": "TX 25-min GT (Gap-Trail) — intraday breakout with 12-day avg-body (avgdis). Upin/dnin = max/min(highd(1), OPEND(0)) ± ratioin*avgdis. Entry day>d-1 AND 1<k<12 (fresh session window): if closed(1)+r*avgdis>opend(1) AND lowd(1)>lowd(2) AND c>upin -> long at H stop. Pattern-confirm exit: k>=6 AND closed(1) red + highd(1)<highd(2) -> long-exit at lowd(0) stop. 13:30 all-out. Demonstrates avg-body-as-range-unit + daily-HL structure filter.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/s !_TXDL_1_030_Gap/.code.20210713_194450.txt",
        "summary": "TX 30-min Gap — KC (Keltner-like) shift on opend. value1 = opend(0)-closed(1); KC = close - value1. value3 = Average(KC, 4). Entry: mp<=0 AND closed(1)<value3 AND countif(kc<value3, 4)>=3 AND c>value3 AND KC>LowD(1) -> long at 2-bar high stop. Exit: barssinceentry>40 AND maxPositionProfit<pft*200 -> time-stop at nBar low/high. Simple gap-adjusted MA cross with time-bounded failure exit.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/s !_TXDL_1_030_OverHeat/.code.20210713_194418.txt",
        "summary": "TX 30-min OverHeat — first-bar directional + over-heat exit. k=1 entry: prev-day close vs today open + gap < 2-day range -> long or short at market (continuation). Over-heat exit at 2nd-to-last bar: countH (bars exceeding day-high) >= BTOH(8) -> exit at market (momentum-exhaustion signal). Bad-position mid-day guard: if position trades against prev day L/H, tighter daily-HL exit. Settlement close. Explicit 'too many new highs = top' anti-overextension mechanism.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/s !_TXDL_1_030_QTC07VolatilityStrategy/.code.20210713_203204.txt",
        "summary": "TX 30-min QTC07 Volatility — ATR(fast vs slow) regime switch + box-compression entry. dh_box/dl_box = 4-day HL box. condition32: fastATR<slowATR AND highd(0)<dh_box AND lowd(0)>dl_box (compressing inside box) + entries<=1 + k<full-day -> long at min(dh_box-avg(H-L,k), dl_box + closed(1)*0.02) stop, mirror short. Monthly 180K loss/MDD circuit-breaker. Small-move-breakout-from-compression template; box=1.618*box_range for post-entry tracking. Example of regime gate (ATR fast<slow) used as 'when to look' filter instead of 'what to trade'.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/s !_TXDL_1_300_LongBreak/.code.20210716_224414.txt",
        "summary": "TX 300-min (daily-swing) LongBreak — longest-timeframe trend-continuation breakout on daily bars. Uses same structural motifs as HL3day (highd/lowd multi-day max/min) but with longer lookback and wider stops (SL ~175+ pts). Operates on settlement cycle not intraday. Represents the 'D1 baseline' in the TXDL zoo — all intraday strategies must demonstrate edge above this trivial daily breakout after costs.",
    },
]

assert len(entries) == 26, f"expected 26, got {len(entries)}"

for i, e in enumerate(entries):
    e["timestamp"] = f"{TS}:{i:02d}+08:00"
    e["tier"] = 1
    e["readable"] = True
    e["summary_length"] = len(e["summary"])

log_path = BASE / "digestion_log.jsonl"
with log_path.open("a", encoding="utf-8") as f:
    for e in entries:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")
print(f"Appended {len(entries)} entries to {log_path.name}")

state_path = BASE / "digestion_state.json"
with state_path.open("r", encoding="utf-8") as f:
    state = json.load(f)

new_paths = [e["path"] for e in entries]
state["digested_paths"].extend(new_paths)
state["files_digested"] = len(state["digested_paths"])
state["total_digested"] = state.get("total_digested", state["files_digested"]) + len(entries)
state["last_digested_at"] = f"{TS}:59+08:00"
state["last_updated"] = f"{TS}:59+08:00"

with state_path.open("w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)
print(f"State updated: files_digested={state['files_digested']} total_digested={state['total_digested']}")

set_path = BASE / "digested_set.txt"
with set_path.open("a", encoding="utf-8") as f:
    for p in new_paths:
        f.write(p + "\n")
print(f"Appended {len(new_paths)} paths to {set_path.name}")
