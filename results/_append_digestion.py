import json

entries = [
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDD_1_003_Gate01/KO003_TX_3Guan_DO_Code.txt",
        "timestamp": "2026-04-14T06:30:00+08:00",
        "tier": 1,
        "readable": True,
        "summary": "TradeStation EasyLanguage code for the 3-Gate (三關) day-only strategy on TAIEX futures using 3-minute bars. Entry uses previous day Fibonacci 1.382 extension levels to define Up_Bound/Middle/Down_Bound zones; two entry modes—trend-following and counter-trend reversal—with Walk-Forward parameter updates by date. Exit logic includes zone-based stop, 3-consecutive-close-below-middle stop, quarter-range trailing, and EOD market exit.",
        "summary_length": 420
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDD_1_003_Gate02/KO003_TX_3GuanVer2_DO_Code.txt",
        "timestamp": "2026-04-14T06:30:10+08:00",
        "tier": 1,
        "readable": True,
        "summary": "Version 2 of the 3-Gate strategy (KO003_TX_3GuanVer2_DO) adding a volatility-spike filter: when current day quarter-range is double last day and exceeds 150 points, exceed_flag tightens the loss stop. Entry condition uses determine_ratio to require more than 70% of intraday bars to close above/below prior close, making entries more trend-confirming than V1.",
        "summary_length": 410
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDD_1_006_QIndicatorLaddar01/!_TXDD_1_006_KH01_QIndicatorLaddar_202007.txt",
        "timestamp": "2026-04-14T06:30:20+08:00",
        "tier": 1,
        "readable": True,
        "summary": "Strategy description for QIndicatorLaddar on TAIEX 6-min bars with parameters Qlen (13:19:2), STL (19), in (3), notin (18), laddarStep (8), and Qvalue (2.5:5:0.5). The concept uses a Q-indicator ladder structure where entry triggers when the Q-value crosses a step threshold; exits include stop-loss and trailing logic. Illustrates how custom quantitative indicators can be layered to create step-wise entry and exit ladders.",
        "summary_length": 450
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDD_1_006_SAR01/!_TXDD_1_006_SAR01.txt",
        "timestamp": "2026-04-14T06:30:30+08:00",
        "tier": 1,
        "readable": True,
        "summary": "Parabolic SAR-based intraday strategy on TAIEX 6-min bars (日盤當沖) using time filter 0915-1030, entering only once per day when today open beats yesterday close. Long entries breakout the Length-bar high when SAR PS value is positive. Two exits: fixed-point stop-loss (N points) and a trend-quality filter exit after 60 minutes if fewer than 70% of bars sustain above entry price. Demonstrates SAR used as a regime filter rather than direct signal.",
        "summary_length": 455
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDD_1_007_CBar01/!_TXDD_1_007_CBar01.txt",
        "timestamp": "2026-04-14T06:30:40+08:00",
        "tier": 1,
        "readable": True,
        "summary": "7-min TAIEX day-trade strategy using cumulative C-bar (close-to-close change) as the primary signal. Entry: three consecutive C-bar values in same direction with open filter confirming larger-than-average price movement; stop set at 3x Ratio of C-bar amplitude. Exits include initial stop, profit target (1x Pft), trailing stop (2x Pft), and dynamic stop widening. Demonstrates how simple price-velocity measures construct robust trend entries on Taiwan futures.",
        "summary_length": 445
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDD_1_007_Gap01/!_TXDD_1_007_Gap01.txt",
        "timestamp": "2026-04-14T06:30:50+08:00",
        "tier": 1,
        "readable": True,
        "summary": "Gap-based intraday trend strategy on TAIEX 7-min bars with two entry modes: Entry 1 targets gap-down opens with strong first bar candle body position; Entry 2 targets gap-up opens above yesterday upper zone with continuation confirmed after n bars. Exits use fixed-point stop-loss and a 60-minute trend-quality filter. Notable distinction between gap-down-reversal and gap-up-continuation setups using candle body ratio to confirm directional strength.",
        "summary_length": 450
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDD_1_007_RSI01/!_TXDD_1_007_MT01_RSI_202007.txt",
        "timestamp": "2026-04-14T06:30:55+08:00",
        "tier": 1,
        "readable": True,
        "summary": "RSI-based 7-min TAIEX day-trade (No22_TX_RSI_7K_DO) with optimization ranges Len (13:21:2), Bias (4:8:1), NRatio (fixed 4.3), STP (fixed 95). Core logic accumulates bar data by volume weighting then feeds into RSI calculation; entry when RSI exits extreme zone offset by ATR from price. Three exits: stop-loss, trailing profit, and time-based close. Shows RSI used as entry timing filter layered on cumulative bar momentum.",
        "summary_length": 435
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDD_1_008_BSPower01/!_TXDD_1_008_BSPower01.txt",
        "timestamp": "2026-04-14T06:31:00+08:00",
        "tier": 1,
        "readable": True,
        "summary": "BSPower strategy (whw013) on TAIEX 8-min bars counting bars where close+high exceeds previous close+high as a buy-power metric. Entry when buy-power bar count exceeds (in) times the weak-bar count AND price filter is met versus yesterday close. Exit uses fixed stop, dynamic stop narrowing for bad entries (bearish entry candle), and trailing low-point exit after 3 bars. Walk-Forward parameters updated annually. Volume-neutral trend confirmation approach using high-close bar counting.",
        "summary_length": 475
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDD_1_009_PVG01/!_TXDD_1_009_PVG01.txt",
        "timestamp": "2026-04-14T06:31:10+08:00",
        "tier": 1,
        "readable": True,
        "summary": "Comprehensive pivot-based multi-level entry strategy (TX_Pivot_Do) on TAIEX 9-min bars defining 7 entry conditions (L1-L7) across Fibonacci-expanded pivot levels H1/H2/H3 and L1/L2/L3. Conditions include breakout confirmations, swing-high/low patterns, gap reversal traps, and Nike-curve recoveries. Dynamic stop-loss widens for high-volatility gap-open days. Highly relevant as a reference architecture for building multi-condition pivot trading systems with regime-dependent parameter selection.",
        "summary_length": 470
    },
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXDD_1_030_LR+SLP01/!_TXDD_1_030_LR+SLP01.txt",
        "timestamp": "2026-04-14T06:31:20+08:00",
        "tier": 1,
        "readable": True,
        "summary": "Linear regression angle strategy (Hayden02_TX_RegAngel30K_L0) on TAIEX 30-min bars. Entry requires three consecutive days without breaking prior low, then intraday n-bar MA regression angle must exceed 54 degrees and increase for 3 consecutive bars. Exits: profit-protection defending prior day low on gap-down (profit >250pts), volatility-based stop from entry-to-low amplitude ratio, overnight continuation stop, and settlement exit. Shows regression slope as signal filter to improve trend entry timing.",
        "summary_length": 475
    }
]

# Write to digestion log
with open("C:/Users/admin/workspace/digital-immortality/results/digestion_log.jsonl", "a", encoding="utf-8") as f:
    for entry in entries:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print(f"Appended {len(entries)} entries to digestion_log.jsonl")

# Update state
with open("C:/Users/admin/workspace/digital-immortality/results/digestion_state.json", "r", encoding="utf-8") as f:
    state = json.load(f)

new_paths = [e["path"] for e in entries]
state["digested_paths"].extend(new_paths)
state["files_digested"] = len(state["digested_paths"])
state["last_digested_at"] = "2026-04-14T06:31:20+08:00"
state["last_updated"] = "2026-04-14T06:31:20+08:00"

with open("C:/Users/admin/workspace/digital-immortality/results/digestion_state.json", "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

print(f"Updated state: {state['files_digested']} total digested")
