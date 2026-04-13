# -*- coding: utf-8 -*-
import json

timestamp = "2026-04-14T14:00:00+08:00"

entries = [
    {
        "path": "E:/@交易/@StrategyManagement/歸檔/202007/202007Bohun/boTX_202007_MAATR_LO說明檔.txt",
        "timestamp": timestamp,
        "tier": 1,
        "summary": "Bohun 2020-07 exchange: MA+ATR dual-mode entry on 29m TXF — ATR-stable breakout entry when volatility low, counter-trend entry when ATR spikes; stop at recent low or entry minus ATR."
    },
    {
        "path": "E:/@交易/@StrategyManagement/歸檔/202007/202007ChienShen/047說明.txt",
        "timestamp": timestamp,
        "tier": 1,
        "summary": "ChienShen 047: Correlation Trend on 13K FITXI — momentum indicator gates entry when threshold exceeded and rising vs prior bar; four exits: dynamic low, no-new-high, session-end loss exit, monthly stop; WF via ROA."
    },
    {
        "path": "E:/@交易/@StrategyManagement/歸檔/202007/202007JohnsonLo/011_TX_Range R_LO說明檔.txt",
        "timestamp": timestamp,
        "tier": 1,
        "summary": "JohnsonLo 011: Range-comparison trend on 19m FITXI — compares amplitude of prior vs next len-bar windows, uses Williams %R for trend direction, pullback entry at dynamic range high/low."
    },
    {
        "path": "E:/@交易/@StrategyManagement/歸檔/202007/202007TimChen/2-003_TXA_30mKeltner_LOS策略說明.txt",
        "timestamp": timestamp,
        "tier": 1,
        "summary": "TimChen 003: Keltner Channel breakout on 30m TXF full session — enters long when midline trends up and price breaks upper band; exits include stop, profit target, and 9% daily circuit breaker at 9% range."
    },
    {
        "path": "E:/@交易/@StrategyManagement/歸檔/202007/202007WenZiGi/策略說明檔 topbot 1-6.txt",
        "timestamp": timestamp,
        "tier": 1,
        "summary": "WenZiGi TopBot 1-6: Gap-and-reversal on 6m TXF day session — classifies 4 open-gap scenarios (gap x trend direction), reversal confirmation entry before 11:00, single trade per day, exit near prior close after N bars."
    },
    {
        "path": "E:/@交易/@StrategyManagement/歸檔/202007/202007Kuang/202007 QTC_TX_SAR_Kuang_DO_6K 策略說明.txt",
        "timestamp": timestamp,
        "tier": 1,
        "summary": "Kuang SAR: Parabolic SAR + gap-up pre-condition on 6m TXF 09:15-10:30 entry window; buy stop at Length-bar high; exits on fixed point stop or dynamic trailing low; hard flat at 13:39 and settlement day."
    },
    {
        "path": "E:/@交易/@StrategyManagement/歸檔/202007/202007YenShen/202007作業策略說明.txt",
        "timestamp": timestamp,
        "tier": 1,
        "summary": "YenShen 001: CCI breakout trend on 28m FITXI — stop-buy at N-bar high when CCI exceeds overbought zone; trailing stop at N-bar low or no-new-high detection; settlement hard exit; two exit speed modes."
    },
    {
        "path": "E:/@交易/@StrategyManagement/歸檔/202007/202007shuenhua/TX_Pivot_DO策略說明檔.txt",
        "timestamp": timestamp,
        "tier": 1,
        "summary": "shuenhua TX_Pivot_DO: Classic pivot-point intraday on 9m TXF — H1/H2/H3/L1/L2/L3 from prior-day HLC, 3-tier entry with 3-contract scaling; capital constraint filter 1.5M; partially garbled encoding."
    },
    {
        "path": "E:/@交易/@StrategyManagement/歸檔/202007/202007WGN/123_TX_HLORB_FDO說明檔.txt",
        "timestamp": timestamp,
        "tier": 1,
        "summary": "WGN 123: High-low opening range breakout on 3m TXF — entry after price exceeds prior session high/low by in*0.5 bar threshold; today's high/low as boundary exit; re-entry filter prevents same-side repeat."
    },
    {
        "path": "E:/@交易/@StrategyManagement/歸檔/202007/202007Morton/No22_TX_RSI_7K_DO_策略說明.txt",
        "timestamp": timestamp,
        "tier": 1,
        "summary": "Morton No22: Cumulative price-change RSI on 7m TXF intraday — bar-level changes accumulated into custom RSI, long entry on oversold break with ATR-based stop; partially garbled but entry/exit logic confirmed readable."
    }
]

log_path = r"C:\Users\admin\workspace\digital-immortality\results\digestion_log.jsonl"
with open(log_path, "a", encoding="utf-8") as f:
    for e in entries:
        e["summary_length"] = len(e["summary"])
        f.write(json.dumps(e, ensure_ascii=False) + "\n")

print(f"Appended {len(entries)} entries to digestion_log.jsonl")

# Update state
import datetime
state_path = r"C:\Users\admin\workspace\digital-immortality\results\digestion_state.json"
with open(state_path, "r", encoding="utf-8") as f:
    state = json.load(f)

state["files_digested"] = 110
state["last_digested_at"] = timestamp
for e in entries:
    state["digested_paths"].append(e["path"])

with open(state_path, "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

print(f"Updated digestion_state.json: files_digested={state['files_digested']}")
