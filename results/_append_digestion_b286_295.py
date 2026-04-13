"""Append batch 286-295 to digestion log. B2 pipeline. 2026-04-14."""
import json
from pathlib import Path

BASE = Path("C:/Users/admin/workspace/digital-immortality/results")
TS = "2026-04-14T07:00"

entries = [
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_005_ATR01/!_TXDL_1_005_ATR01.txt",
        "timestamp": f"{TS}:00+08:00",
        "tier": 1,
        "readable": True,
        "summary": "TAIEX 5-min day-long (當日做多/空) ATR-ratio strategy. Uses Len(6) MA and ratio(1.8) to classify short-term price zones into big/small zones via high-low amplitude. Entry: when current zone > previous zone AND price breaks recent high by ratio; short mirror. Exit: 2x ATR stop + EOD. Parameter Len 4:8:1, ratio 1.2:2.4:0.3. Cost $500 + commission 1.5%, data 2014/01/01-2021/05/31. Demonstrates ATR-range-ratio as entry filter on day-session.",
        "summary_length": 430,
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_005_CDP01/!_TXDL_1_005_CDP01.txt",
        "timestamp": f"{TS}:10+08:00",
        "tier": 1,
        "readable": True,
        "summary": "CDP reversal strategy herman002_TX_CDP20210615_LT on TAIEX 5-min day-session, parameter-free. Multiple entry modes: (1) no-trend long on pullback to AH after 9:00 when 4 prior bars close above AH, (2) gap-down reversal long at AL-(NL-AL)*0.5, (3) deep-gap long at AL-(NL-AL) for high-volatility days, (4) mean-reversion short at daily high during down trend, (5) trailing exit at daily low. Settlement close + 7% trailing stop. Classic CDP pivot multi-mode framework.",
        "summary_length": 455,
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_006_Gap+MA01/!_TXDL_1_006_Gap+MA01.txt",
        "timestamp": f"{TS}:20+08:00",
        "tier": 1,
        "readable": True,
        "summary": "Gap+MA breakout strategy ED001_TX_JumpGapMA6K_LT on TAIEX 6-min day-session long-term. Entry: open-gap-up (opend(1)>highd(1)) triggers daily bias, enters long after first bar breaks above 300/barinterval moving average with price > opend & prev close. MA-fast/slow stack (fast>slow) required. Exit: reverse signal at recent low, settlement close. Parameters hour_len(13) 7:17, slow_m(0.6), opend_ratio(0.44). Uses WF re-optimization annually. Example of combining gap context + MA-stack for momentum entry.",
        "summary_length": 490,
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_008_BarTunnel01/!_TXDL_1_008_BarTunnel01.TXT",
        "timestamp": f"{TS}:30+08:00",
        "tier": 1,
        "readable": True,
        "summary": "BN_002_TX_BarTunnel_LO_8k on TAIEX 8-min bars day-session long-only. Builds a price tunnel from rolling NBar(8) high/low with HL_ratio(2) wide channel. Entry 1: N consecutive bars close above upper tunnel (breakout continuation). Entry 2: reversal long after initial breakout fails and returns below channel for a bar. Exits: tunnel-based stop, reversal exit when candle lower shadow breaches lower tunnel, large gap-up open > tunnel width triggers profit exit, settlement close. Example of self-adaptive channel structure with dual entry modes.",
        "summary_length": 520,
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_010_PT01/!_TXDL_1_010_PT_NeckLine01.txt",
        "timestamp": f"{TS}:40+08:00",
        "tier": 1,
        "readable": True,
        "summary": "Jack106_TX_Neckline10K_L0 neckline pattern strategy on TAIEX 10-min day-session long-only. Entry: price breaks K-line-defined neckline (trendline), requires 2 prior down days with ≤2 entries/day, enters at 2 prior bars' high. Exit 1 (reversal stop): 3 K-bars after entry with lowest-close break = failed reversal, exit on break of prev-bar low if K count <=1. Exit 2 (target): new-high then pullback to 3rd bar's low = target exit. Settlement close. WF code updates param `in` annually. Large MDD but stable pattern.",
        "summary_length": 510,
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_013_Gap+RSI01/!_TXDL_1_013_Gap+RSI01.txt",
        "timestamp": f"{TS}:50+08:00",
        "tier": 1,
        "readable": True,
        "summary": "TX_RSI-13m-GapIn_LO on TAIEX 13-min day-session long. Entry: open in prior-day high zone (gap-in context) AND RSI(14) > 65 AND break of 3-bar low — counter-intuitive: buys after RSI overbought + gap-in after price pulls back. Max 2 entries/day before 13:00. Exits: trailing 60% retracement after 150pt profit, hard target 250pts (scales to 375pts = 1.5x if 3-day avg profit is positive), 30-pt stop that widens to 60pt after gap-in, settlement exit. Counter-trend gap-reversal logic wrapped in trend indicator.",
        "summary_length": 510,
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_015_Gap01/!_TXDL_1_015_Gap01.txt",
        "timestamp": f"{TS}:55+08:00",
        "tier": 1,
        "readable": True,
        "summary": "@S_072_TX_OpenerV3_L on TAIEX 15-min day-session short-only. Built around 特徵值 (characteristic value) – a proprietary indicator from gap-open behavior. Entry: 3-day consecutive high count filter, gap-up open above prior-day high, characteristic value match, trend confirmation on reversal. Exit: quarterly HL mean trailing, daily 1/3 HL uplift trail, large volatility prev-day low-close reversal, HL ratio 1:1 triggers +1 tick rebate exit, HL ratio 2:1 with short trend = expected large rebound exit, settlement close. WF len(8) 7:19, ratio(2.1) 0.9:2.1.",
        "summary_length": 545,
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_015_KD01/!_TXDL_1_015_KD01.txt",
        "timestamp": f"{TS}:58+08:00",
        "tier": 1,
        "readable": True,
        "summary": "TimChen008_TX_15mKD202106_LT on TAIEX 15-min day-session long-term. Simple KD stochastic crossover: long when SlowK crosses above SlowD and SlowD > iOverSold(79); short when inverse with threshold 100-iOverSold. Exit modes: (1) target profit 1.5x iPFT after prior bar new high (else 1x), (2) stop 0.9x iPFT tightened (else 1x), (3) floating profit protection — after profit > iPFT - K count*0.5, exit at 20% retrace from post-entry high, (4) TX index trailing 9%, (5) settlement exit. WF annual: iLenKD 9, iOverSold 74-76, iPFT 295.",
        "summary_length": 525,
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_015_MA01/!_TXDL_1_015_MA01.txt",
        "timestamp": f"{TS}:59+08:00",
        "tier": 1,
        "readable": True,
        "summary": "mai_LT_15K_60AVG on TAIEX 15-min day-session long-term. 60-bar MA trend filter + range breakout. Long: c > MA60 AND open > yesterday close AND break of today high or prev-bar high. Short mirror. Exits: (1) open < yesterday low (long) closes at market, (2) price < entryprice triggers trailing stop at min(today low, 48-bar-low), (3) 3% STP fixed stop-loss, (4) settlement close. Parameters aa(155) 115:195:20 highest-bar window, bb(48) 40:56:2 trailing window. Cost $500+500. Max bars 200. Classic MA + highest-window trend follow.",
        "summary_length": 530,
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDL_1_017_FFG01/!_TXDL_1_017_FFG01.txt",
        "timestamp": f"{TS}:59+08:00",
        "tier": 1,
        "readable": True,
        "summary": "FFG (First-bar-fail-gap? framework) strategy on TAIEX 17-min bars. Full EasyLanguage source — inputs ratio(0.66), amp(130); internal vars n1..n3, et, kk track bar counts from session start. Condition7 filters to overnight session boundaries. Includes built-in Strategy Management drawdown control: monthlevel=150000, maxDDlevel=200000, tracks NetP / maxDM arrays per month, resets at month start, suspends trading when monthly drawdown breach flag triggered (flagM). Countif(positionprofit<0,3) tightens size multiplier. Example of integrated strategy + drawdown-control meta-layer in same script.",
        "summary_length": 570,
    },
]

assert len(entries) == 10

# Append to log
log_path = BASE / "digestion_log.jsonl"
with log_path.open("a", encoding="utf-8") as f:
    for e in entries:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")
print(f"Appended {len(entries)} to {log_path.name}")

# Update state
state_path = BASE / "digestion_state.json"
with state_path.open("r", encoding="utf-8") as f:
    state = json.load(f)

new_paths = [e["path"] for e in entries]
state["digested_paths"].extend(new_paths)
state["files_digested"] = len(state["digested_paths"])
state["total_digested"] = state.get("total_digested", 285) + len(entries)
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
print(f"Appended {len(new_paths)} to {set_path.name}")
