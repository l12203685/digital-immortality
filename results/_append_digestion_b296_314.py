"""Append batch 296-314 (TXDL continuation) to digestion log. B2 pipeline. 2026-04-14."""
from __future__ import annotations

import json
from pathlib import Path

BASE = Path("C:/Users/admin/workspace/digital-immortality/results")
TS = "2026-04-14T10:45"

# 19 TXDL primary strategies not yet digested (batch 296-314)
entries: list[dict] = [
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_017_Transformer01/!_TXDL_1_017_Transformer01.txt",
        "summary": "$@LV@$__tx_TransFormer_17K_(DT)LT — TAIEX 17-min day-session hybrid day-trade + swing ('Transformer/Swingman'). Main logic: weekly midpoint ((highw(1)+loww(1))/2) defines medium-term bias; swing entry 3+ days after settlement, day-trade counter-weekly on mild pullback, auto-convert day-trade to swing if EOD profit reached. Post-settlement 2-day window reserved for counter-trend swing (institutions often close at settlement). Uses 三關價 (three-pivot) + weekly midpoint for stops that walk forward; no profit target — rides to settlement. WF TD param 3:11:1. Core essence: protect entry capital, let trend run till settlement.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_020_DCC01/!_TXDL_1_020_DCC01.txt",
        "summary": "GavinLu008_TX_DonChianChannel-D2106-K20m_LT — TAIEX 20-min day-session swing. Donchian Channel length 46 + EMA(320) trend filter. Entry: 2 consecutive breaks of DonChian upper/lower AND close on correct side of EMA(320). Four exits: (1) break-even stop after profit, (2) take-profit at maxRatio(5.8)x channel width, (3) stop-loss if losing + close reverts to DonAvg/EMA midline (best of two), (4) settlement close. Classic channel-breakout filtered by long EMA trend; only high-conviction moves trigger entry.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_020_WeekTrade01/!_TXDL_1_020_WeekTrade01.txt",
        "summary": "2106_Ivan_TX_WeekTrade20k_LT — TAIEX 20-min weekly-swing (Mon-Fri close-out) to avoid weekend holding risk. Filters: Thu/Fri only, non-settlement, skip first 30 min and last bar, max 2 entries/week. Entry: close > weekly open + today's weak price > yesterday's strong price + 60-min high breakout. Trailing stops use entry-day low then prev-two-day low. Moving exit triggered after profit > STP(285) or 5-day avg HL * golden ratio. Profit target 2x STP. Weekly sweep at Fri close; Mon-resume with gap-down stop. Friday/settlement entries use tighter day-trade-like thresholds.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_022_VHF01/!_TXDL_1_022_VHF01.txt",
        "summary": "2007TX_VHF_LinR_22K — TAIEX 22-min day-session. Two entry modes: (1) VHF (Vertical Horizontal Filter) directional + Linear Regression confirmation + session-time filter, (2) overnight-gap-in entry. Four exits: (1) PB2/2 pivot point reversal, (2) pb2 zone + VHF > average(VHF,10), (3) ATR-expansion widens stop loss, (4) settlement close. WF params PB2 245:320:15 and stpinput 17000:29000:2000. Demonstrates VHF as regime filter (trending vs choppy) combined with price-based Linear Regression trigger.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_023_ASI01/!_TXDL_1_023_ASI01.txt",
        "summary": "Shuen036_TX_ASI23K_V1_LT — TAIEX 23-min day-session swing using ASI (Accumulated Swing Index, Wilder). Two entries: (1) ASI crosses over its MA(Len=105) long / cross under short, (2) 'Guava' contrarian limit at 7% from midpoint for extreme-move reversal. Time filter 09:00 to 13:00-4bars. Two stops: long stops at low-2*ATR(13), short stops at high+2*ATR(13); long takes partial profit target at 11:00+ pullback 3/4 position, short takes 6/4 position pullback. Settlement exit 13:30. WF Len annual optimization. V1 = annualized WF version.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_023_ASI02/!_TXDL_1_023_ASI02.txt",
        "summary": "Shuen036_TX_ASI23K_V2_LT — parameter-free ASI variant on TAIEX 23-min. Fixed Len=100 (no WF) after author found param too sensitive. Adjusted exit asymmetry: short profit-taking at 11:00+ low pulled 3/4 up, long profit-taking at 11:00+ high pulled 6/4 down (more generous for longs, author bias). Same Guava 7% contrarian entry. Example of deliberately removing WF to prove strategy edge from structural logic, not optimization.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_023_ASI03/!_TXDL_1_023_ASI03.txt",
        "summary": "Shuen036_TX_ASI23K_V3_LT — ASI 23-min V3 personal-preference variant. Differs from V1: short profit-taking point pulled 2x from average dropping range (more aggressive short exit). Maintains V1's WF Len schedule + short 3/4 / long 6/4 asymmetric pullback exits. Adds AvgDRange 20-day array for dynamic stop-distance computation. Illustrates how one indicator (ASI) spawns 3 variants: WF-tuned, param-free, personal-pref — useful diversification over a single signal source.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_024_3DHL/!_TXDL_1_024_3DHL.txt",
        "summary": "3DHL_TX_24M LO — TAIEX 24-min day-session long-only based on 3-day high/low pivot structure. Params stp(575) profit target, stpl(45) stop-loss. Author notes netProfit maxed at stp=710 but refused due to retracement tolerance — example of discretionary override on optimization output. Uses 3-day rolling HL range to define entry pivots. Fixed stop + fixed target architecture. Cost $500 min + 1.5%. Max 1 contract. Demonstrates discipline: not every optimal WF param is accepted; equity-curve psychology overrides raw P/L optimum.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_025_3GP01/!_TXDL_1_025_3GP01.txt",
        "summary": "202106_TX25min_3gp_LO — TAIEX 25-min day-session long-only. 3-pivot 關價 breakout with 2-day body filter. Long entry: prev bar red or small-black body, lowd(1)>lowd(2), close breaks upper pivot. Short mirror with highd-descending filter. Exit: after half-day passed, prev-bar counter-color + HL sequence reversed, break today's low (long) / high (short). Settlement close. Params len(7), ratioin(0.35), r(1.1). Simple but effective: combines momentum (breakout) with pattern context (prev 2-day body structure) to avoid false breakouts.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_029_MA+ATR01/!_TXDL_1_029_MA+ATR01.txt",
        "summary": "boTX_202007_MAATR_LO — TAIEX 29-min day-session swing. Essence: 'MA+ATR breathing' — when ATR is stable, breakout along trend; when ATR suddenly expands, fade into mean. Entry 1: ATR < multi-day ATR, today high > yesterday/prior high, close crosses high-MA = breakout long. Entry 2: ATR > multi-day ATR, today low > prior lows = counter-trend dip long at low-MA. Exits: (1) large gap profit-take, (2) near-low or entry-ATR stop, (3) counter-trend entry stops at day-low. WF Len 8:32:6, ATRGAP 5:12:1. Demonstrates volatility-regime-dependent entry style switching.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_030_CT01/!_TXDL_1_030_CT001.txt",
        "summary": "腳麻 (Numb-Leg) strategy on TAIEX 30-min — 'brain-dead' entry designed to survive the May 2021 AV-reversal streak. Rule: skip 2 days before + settlement + 1 day after; otherwise, gap-up = long, gap-down = short, no condition. Two exits: (1) over-heat — intraday count of bars breaking day's high/low exceeds threshold BTOH(8) = close at bar, (2) extreme-drawdown exit. Core lesson: during slow-drift markets, simple directional gap entry + over-heat filter can survive volatility-cluster losses. WF BTOH 6:10:1. Minimalism as edge.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_030_MA+CT01/!_TXDL_1_030_MA+CT01.txt",
        "summary": "H053_TX_SM_LO_30M — TAIEX 30-min day-session long-only using KC-based pullback re-entry. MA: short-term high-MA of high-prices. After KC (high-MA minus low-MA) expands and current close > high-MA, wait for pullback, re-enter long at rebound pivot (pyramid-style). Exit after nBar(40) bars: if max profit < pft(200), exit at nBar window low/close. Settlement close. Params len 3:6:1, nK 3:5:1. Illustrates entering on 'clean pullback' after trend confirmation, not first breakout.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_030_MTM01/!_TXDL_1_030_MTM01.txt",
        "summary": "2106TX_MTM_LinR_30K — TAIEX 30-min day-session. Two entries: (1) MTM (Momentum) top/bottom expansion + 5-day HL extreme + time filter + storm-wind setting, (2) relative-strength gap-in entry. Five exits: (1) gap-in entry time-exit if no immediate pop, (2) PB2/2 pivot reversal (moving exit), (3) post-entry N-bar time exit, (4) price reversal to 9-day centroid (flip-exit), (5) fixed stop + settlement. WF PB2 225:400:25. Dense multi-exit stack targeting diverse failure modes.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_030_RSI01/!_TXDL_1_030_RSI01.txt",
        "summary": "TAIEX 30-min RSI swing strategy. Entry: RSI crosses BuyLine from below = long; crosses SellLine from above = short. Boost: RSI climbs through 72 from below AND breaks prior day-high + 5pt = stronger long. Floor: once RSI falls back below 15, cheap-long on break of prior day-low - 5pt. Fixed stop SLPoint(60:135:15). Two flip-style exits using the mirror RSI threshold cross. Params RSILength 5:8:1, BuyLine 57:72:5, SellLine 5:20:5. Classic RSI cross with threshold-boost + threshold-floor asymmetric entries.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_032_KC01/!_TXDL_1_032_KC01.txt",
        "summary": "TAIEX 32-min Keltner Channel swing. KC upper = MA + KCATRNu*ATR, lower symmetric. Entry: price crosses down through KC upper AND closes small red, break prior day-high = short; mirror for long. Time filter 08:45-13:00. Two stops: (1) fixed SLPoint, (2) channel-based: price crosses back through 2x-width channel + break entry-bar level = exit. Take-profit: after final 100pt reached + gap-up >= prev day, exit at prior day low break (long) or prior day high break (short). 100pt breakeven then 10pt trail. WF KCLen 13:16:1, KCATRNu 1.3:1.9:0.2.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_050_Gap01/!_TXDL_1_050_Gap01.txt",
        "summary": "yita_TX_50k_20210515_LO_003 — TAIEX 50-min day-session long-only. Single param in(3) for pivot-math. Setup: today's open is between closeD(1) and closeD(2) (gap-between) = pivot context. Entry: max(highD(0),highD(1)) stop-buy long; mirror short. Skip settlement, only when mp=0. Three exits: (1) half-day pass-through stop, (2) entry lasts >3 days AND floating losing AND entry-price gets breached = stop, (3) non-settlement day + break of entry-week's open = stop. 7-year stable PF > MDD with pf/mdd>1 for past 3 yrs. Example of minimal-param gap-inside-yesterday setup.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_060_BB01/!_TXDL_1_060_BB01.txt",
        "summary": "$2106K06_TX_BBand_LO — TAIEX 60-min day-session with Bollinger Band breakout. Entry: close > BB upper (BBLen=19, BBDev=1.5) + break of first-bar high + today's high < day-low + 1.5*ATR (avoid stretched bars) + exception: near quarterly MA (<20pt distance) with 2 prior losses, skip. Reverse: 3 bars after entry, RSI crosses over 80 then falls = flip short. Exits: (1) fixed stop, (2) fixed target STPratio(2.4)*stop, (3) after RSI flip, close falls into bottom 20% of BB width, (4) settlement. WF ATRLen, BBLen, BBDev, STPratio annually.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_060_LR01/!_TXDL_1_060_LR01.txt",
        "summary": "No32_TX_LinearRegCurve_60K_LO_S — TAIEX 60-min day-session using MC-default LinearRegCurve. Entry: LR curve crosses upward to rising trend AND 3-day high-expansion range reached = break-high entry long; short mirrored. Exits: (1) 3-day high range stop-loss — large expansion = larger stop, small expansion = tight stop, (2) take-profit at 2x stop-value, (3) settlement close. WF Len 26:38:6, Vol 500:1000:100, NRatio 7:19:4. Param-tight; LR as trend substrate, 3-day range as volatility-adjusted risk unit.",
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_075_DR01/!_TXDL_1_075_DR01.txt",
        "summary": "khsu_CFExTest_202106_HLChanDelayed_002 — TAIEX 75-min day-session swing. Core idea: distinguish 緩步盤升/戰 (slow drift) from 急噴 (burst). Entry: 3-day HL defines range; within range, wait for 'strong' day (rmp1=0.75 of range) = trend-continuation entry. Triggering uses N-shaped candle position detection — short-stop moves as N-pattern develops. Two exits: (1) start-stop = smaller of entry point or K-line mid-point, (2) pattern exit: once crossed through 5-day low, yellow-alert enters and exits on first pullback burst. Settlement close. Range-expansion gate vs burst-alarm separation.",
    },
]

assert len(entries) == 19, f"expected 19 entries, got {len(entries)}"

# attach tier/readable/summary_length/timestamp
for i, e in enumerate(entries):
    e["timestamp"] = f"{TS}:{i:02d}+08:00"
    e["tier"] = 1
    e["readable"] = True
    e["summary_length"] = len(e["summary"])

# Append to digestion log
log_path = BASE / "digestion_log.jsonl"
with log_path.open("a", encoding="utf-8") as f:
    for e in entries:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")
print(f"Appended {len(entries)} entries to {log_path.name}")

# Update state
state_path = BASE / "digestion_state.json"
with state_path.open("r", encoding="utf-8") as f:
    state = json.load(f)

new_paths = [e["path"] for e in entries]
state["digested_paths"].extend(new_paths)
state["files_digested"] = len(state["digested_paths"])
state["total_digested"] = state.get("total_digested", 295) + len(entries)
state["last_digested_at"] = f"{TS}:59+08:00"
state["last_updated"] = f"{TS}:59+08:00"

with state_path.open("w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)
print(f"State updated: files_digested={state['files_digested']} total_digested={state['total_digested']}")

# Append to digested_set.txt
set_path = BASE / "digested_set.txt"
with set_path.open("a", encoding="utf-8") as f:
    for p in new_paths:
        f.write(p + "\n")
print(f"Appended {len(new_paths)} paths to {set_path.name}")
