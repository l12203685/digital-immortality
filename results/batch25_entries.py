import json

entries = [
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/2101TX_KD_LinR_37K.md",
        "strategy_id": "a32101TX_KD_LinR_37K",
        "classification": "Mean Reversion",
        "direction": "both",
        "timeframe": "unknown",
        "instruments": ["TX"],
        "entry_logic": {
            "long": "Buyset=1 AND condition1 AND condition3 -> stop at highd(0)",
            "short": "Sellset=1 AND condition2 AND condition3 -> stop at lowd(0)"
        },
        "exit_logic": {
            "stop_loss": "entryprice +/- maxwin*0.05",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose"
        },
        "indicators": ["Stochastic(KD)", "Daily OHLC", "CountIf"],
        "time_filter": "t<1200",
        "key_concepts": [
            "KD stochastic overbought/oversold: countif(vSlowD>80,5)>2 -> Buyset",
            "5-period stochastic persistence for signal quality filter",
            "stop entry at daily high/low extremes",
            "tight stop at 5% of maxwin range"
        ],
        "tags": ["mean-reversion", "stochastic", "TX"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/2106_Ivan_TX_WeekTrade20k_LT.md",
        "strategy_id": "b32106_Ivan_TX_WeekTrade20k_LT",
        "classification": "Swing / Long-Term",
        "direction": "both",
        "timeframe": "intraday",
        "instruments": ["TX"],
        "entry_logic": {
            "long": "mp=0 AND k>=30/barinterval AND not LastTradeDay AND ExitsToday>=1+profit>0 filter AND ESweek<2 -> stop at Highest(H,60/barinterval)",
            "short": "C>Openw(0) AND (lowd(0)+opend(0)+c)/3 > (highd(1)+closed(1)*R)/(R+1) -> stop at Lowest(L,60/barinterval)"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "C < min(lowd(1),lowd(2)) or C<loww(0)[1]"
        },
        "indicators": ["Highest(H,60/barinterval)", "Lowest(L,60/barinterval)", "Weekly Open", "Daily OHLC"],
        "time_filter": "t>=1345 t<1500 t>=1330 DayOfWeek filter",
        "key_concepts": [
            "week-based breakout: entry on 60-bar highest high",
            "uses weekly open vs close directional bias",
            "profit filter: only re-enter if previous exit was profitable",
            "ESweek limit: max 2 entries per settlement week",
            "pivot filter: (lowd+opend+c)/3 vs (highd+closedR*R)/(R+1) for trend confirmation"
        ],
        "tags": ["swing", "breakout", "weekly", "TX"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/2106TX_MTM_LinR_30K.md",
        "strategy_id": "a32106TX_MTM_LinR_30K",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "intraday",
        "instruments": ["TX"],
        "entry_logic": {
            "long": "MP=0 AND EntriesToday<1 AND condition11 AND condition33 AND c>max5DayHigh -> stop at iff(opend>closed(1),h,highd(0))",
            "short": "MP=0 AND EntriesToday<1 AND condition11 AND condition34 AND c<min5DayLow -> stop at iff(opend<closed(1),l,lowd(0))"
        },
        "exit_logic": {
            "stop_loss": "SetStopLoss(count2*0.2*bigpointvalue); dynamic stop based on AM high/low penetration count",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "maxEL/S2 scaled exit; limit at entryprice"
        },
        "indicators": ["Momentum(C,barinterval)", "Daily OHLC", "CountIf", "AmhighD_TX", "AmlowD_TX"],
        "time_filter": "t>0915 t<1200",
        "key_concepts": [
            "momentum filter: CountIf(l_MTM1>l_MTM1[1],3)>1 for long trend confirmation",
            "multi-day breakout: c>max of last 5 daily highs",
            "gap-adjusted entry: if open>prev close use current high else use daily high as stop",
            "dynamic stop widens by counting how many bars pierced AM high/low",
            "re-entry allowed if barssinceexit<10 using daily high/low stops"
        ],
        "tags": ["day-trade", "momentum", "breakout", "TX"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/2106TX_MTM_LinR_30K (2).md",
        "strategy_id": "a32106TX_MTM_LinR_30K_v2",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "intraday",
        "instruments": ["TX"],
        "entry_logic": {"long": "same as 2106TX_MTM_LinR_30K", "short": "same as 2106TX_MTM_LinR_30K"},
        "exit_logic": {"stop_loss": "same", "time_exit": "SetExitOnClose"},
        "indicators": ["Momentum", "Daily OHLC", "CountIf", "AmhighD_TX"],
        "time_filter": "t>0915 t<1200",
        "key_concepts": ["duplicate variant of 2106TX_MTM_LinR_30K - same logic"],
        "tags": ["day-trade", "momentum", "duplicate", "TX"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/2106TX_MTM_LinR_30K (3).md",
        "strategy_id": "a32106TX_MTM_LinR_30K_v3",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "intraday",
        "instruments": ["TX"],
        "entry_logic": {"long": "same as 2106TX_MTM_LinR_30K", "short": "same"},
        "exit_logic": {"stop_loss": "same", "time_exit": "SetExitOnClose"},
        "indicators": ["Momentum", "Daily OHLC", "CountIf"],
        "time_filter": "t>0915 t<1200",
        "key_concepts": ["duplicate variant of 2106TX_MTM_LinR_30K - same logic"],
        "tags": ["day-trade", "momentum", "duplicate", "TX"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/2106TX_MTM_LinR_30K (4).md",
        "strategy_id": "a32106TX_MTM_LinR_30K_v4",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "intraday",
        "instruments": ["TX"],
        "entry_logic": {"long": "same as 2106TX_MTM_LinR_30K", "short": "same"},
        "exit_logic": {"stop_loss": "same", "time_exit": "SetExitOnClose"},
        "indicators": ["Momentum", "Daily OHLC", "CountIf"],
        "time_filter": "t>0915 t<1200",
        "key_concepts": ["duplicate variant of 2106TX_MTM_LinR_30K - same logic"],
        "tags": ["day-trade", "momentum", "duplicate", "TX"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/217_TX_MYTK_LT.md",
        "strategy_id": "a3217_TX_MYTK_LT",
        "classification": "Swing / Long-Term",
        "direction": "both",
        "timeframe": "intraday",
        "instruments": ["TX"],
        "entry_logic": {
            "long": "mp=0 AND k>3 AND not LastTradeDay AND EntriesToday=0 AND flagM=0 -> Bin1: stop at HighD(0); Bin2: stop at max(OpenD(0)+Highest_a(array_HighOffset,avgLength),HighD(0))",
            "short": "HighD(0) in (avgHigh, avgHigh+stdHigh) range AND OpenD-maxlist(avgLow-stdLow*2,0)>CloseD(1) -> Sin1: stop at LowD(0); Sin2: stop at min(OpenD-Highest_a(array_LowOffset,avgLength),LowD(0))"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "intraday entry loss: c<entryprice AND c<(HighD+LowD*2)/3"
        },
        "indicators": ["Daily OHLC rolling arrays", "avgHigh/avgLow/stdHigh/stdLow statistics"],
        "time_filter": "none",
        "key_concepts": [
            "statistical range model: uses avg and std of daily high/low offsets from open",
            "two-tier entry: Bin1 at current DayHigh; Bin2 extended by rolling average of high offsets",
            "short entry requires DayHigh to penetrate avgHigh band but not exceed avgHigh+stdHigh",
            "complex flagM controls re-entry suppression",
            "rolling array tracks daily H-O and O-L offsets for statistical bounds"
        ],
        "tags": ["swing", "statistical", "daily-range", "complex", "TX"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/217_TX_MYTK_LT (2).md",
        "strategy_id": "a3217_TX_MYTK_LT_v2",
        "classification": "Swing / Long-Term",
        "direction": "both",
        "timeframe": "intraday",
        "instruments": ["TX"],
        "entry_logic": {"long": "same as 217_TX_MYTK_LT", "short": "same"},
        "exit_logic": {"time_exit": "SetExitOnClose"},
        "indicators": ["Daily OHLC rolling arrays"],
        "time_filter": "none",
        "key_concepts": ["duplicate variant of 217_TX_MYTK_LT"],
        "tags": ["swing", "statistical", "duplicate", "TX"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/2201TXA_MA_LinR_10K.md",
        "strategy_id": "b32201TXA_MA_LinR_10K",
        "classification": "Trend Following",
        "direction": "both",
        "timeframe": "unknown",
        "instruments": ["TXA"],
        "entry_logic": {
            "long": "condition31 AND EntriesToday<3 AND CountIf(SMA rising,2)=2 AND l>highd(1) AND lowd(0)>min(lowd(1..10)) -> stop at Amhighd_TX(0)",
            "short": "condition31 AND EntriesToday<3 AND CountIf(SMA falling,2)=2 AND h<lowd(1) AND lowd(0)<min(lowd(1..10)) -> stop at Amlowd_TX(0)"
        },
        "exit_logic": {
            "stop_loss": "SetStopLoss(c)",
            "profit_target": "SetProfitTarget(c*profitinput)",
            "trailing_stop": None,
            "time_exit": "SetExitOnClose"
        },
        "indicators": ["SMA (Average of lows)", "CountIf for trend persistence", "Daily High/Low", "AmhighD_TX/AmlowD_TX"],
        "time_filter": "t>0915 t<1300",
        "key_concepts": [
            "MA trend confirmation: SMA of lows rising for 2 consecutive bars",
            "price location filter: current low > yesterday high (strong up-gap condition for long)",
            "10-day low support: intraday low above 10-day minimum for long entry",
            "AM session high/low as entry stop price",
            "symmetric fixed profit target as multiple of close price"
        ],
        "tags": ["trend", "MA", "TXA", "breakout"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/222_TX_MYTK_FLT.md",
        "strategy_id": "a3222_TX_MYTK_FLT",
        "classification": "Breakout",
        "direction": "both",
        "timeframe": "unknown",
        "instruments": ["TX"],
        "entry_logic": {
            "long": "condition1 AND flagM=0 -> b1: stop at highest(h,lenB/3)",
            "short": "condition1 AND flagM=0 -> S1: stop at lowest(l,lenS/3)"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "7% circuit breaker: sell if highd(0)>AmOpen*(1+0.07); cover if lowd(0)<AmOpen*(1-0.07)"
        },
        "indicators": ["Highest(H,lenB/3)", "Lowest(L,lenS/3)", "AmOpend_TX", "Daily High/Low"],
        "time_filter": "none",
        "key_concepts": [
            "fractional lookback breakout: uses lenB/3 and lenS/3 bars for high/low",
            "flagM prevents re-entry after exit signal",
            "7% circuit breaker from AM open as hard exit (Taiwan stock limit rule applied to futures)",
            "asymmetric lengths for long vs short breakout lookback"
        ],
        "tags": ["breakout", "TX", "circuit-breaker"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/2MaKD.md",
        "strategy_id": "khsu_2MaKDTest",
        "classification": "Breakout",
        "direction": "both",
        "timeframe": "unknown",
        "instruments": ["CF"],
        "entry_logic": {
            "long": "condition11=True AND EntriesToday<1 AND MP<=0 -> B1: market order",
            "short": "condition11=True AND EntriesToday<1 AND MP<=0 -> S1: market order"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "EOD close exit"
        },
        "indicators": ["Highest (from MA crossup bar)", "Lowest (from MA crossdown bar)", "Stochastic(11)", "SlowK", "SlowD"],
        "time_filter": "time>=1330",
        "key_concepts": [
            "dual MA crossover + stochastic confirmation for entry signal",
            "condition11 combines MA cross bar distance with stochastic KD state",
            "slowDXUp20Bar/slowDXDn80Bar track bar index where slow stochastic crossed 20/80",
            "entry only once per day (EntriesToday<1)",
            "EOD close exit (market on close)"
        ],
        "tags": ["breakout", "stochastic", "MA", "CF"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/2MaKD (2).md",
        "strategy_id": "khsu_2MaKDTest_v2",
        "classification": "Breakout",
        "direction": "both",
        "timeframe": "unknown",
        "instruments": ["CF"],
        "entry_logic": {"long": "same as 2MaKD", "short": "same"},
        "exit_logic": {"time_exit": "SetExitOnClose"},
        "indicators": ["Stochastic", "Highest", "Lowest"],
        "time_filter": "time>=1330",
        "key_concepts": ["duplicate of 2MaKD"],
        "tags": ["breakout", "stochastic", "duplicate", "CF"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/2MaKD_WF.md",
        "strategy_id": "khsu_2MaKDTest_WF",
        "classification": "Breakout",
        "direction": "both",
        "timeframe": "unknown",
        "instruments": ["CF"],
        "entry_logic": {
            "long": "same as 2MaKD but with separate stochastic length 11",
            "short": "same with stochastic length 11"
        },
        "exit_logic": {"time_exit": "SetExitOnClose"},
        "indicators": ["Stochastic(11)", "SlowD11", "SlowD13", "Highest", "Lowest"],
        "time_filter": "time>=1330",
        "key_concepts": [
            "WF = Walk-Forward variant of 2MaKD",
            "adds secondary stochastic with fixed length 11 for robustness test",
            "SlowD11/SlowD13 track multiple KD periods for walk-forward validation"
        ],
        "tags": ["breakout", "stochastic", "walk-forward", "CF"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/2MaKD_WF (2).md",
        "strategy_id": "khsu_2MaKDTest_WF_v2",
        "classification": "Breakout",
        "direction": "both",
        "timeframe": "unknown",
        "instruments": ["CF"],
        "entry_logic": {"long": "same as 2MaKD_WF", "short": "same"},
        "exit_logic": {"time_exit": "SetExitOnClose"},
        "indicators": ["Stochastic(11)", "Highest", "Lowest"],
        "time_filter": "time>=1330",
        "key_concepts": ["duplicate of 2MaKD_WF"],
        "tags": ["breakout", "stochastic", "walk-forward", "duplicate", "CF"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/3. 3DOHL.md",
        "strategy_id": "_2110_3DOHLa20TXa206Ma20DO",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "6m",
        "instruments": ["TX"],
        "entry_logic": {
            "long": "mp=0 AND condition1 AND t<1200 AND EntriesToday<1 -> L_in_1: stop at L_power-k*5; L_in_2: stop at L_power+k*5; L_in_3/4 re-entry",
            "short": "mp=0 AND condition1 AND t<1200 AND EntriesToday<1 -> S_in_1: stop at S_power+k*5; S_in_2: stop at S_power-k*5; S_in_3/4 re-entry"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "L_timeout/S_timeout market exit"
        },
        "indicators": ["Daily High/Low/Open/Close 3-day averages", "Highest/Lowest for range check"],
        "time_filter": "t<1200 sess1endtime-1*barinterval",
        "key_concepts": [
            "3-day power levels: L_power=(lowD(1)+lowD(2)+lowD(3)+opend(0))/4; S_power=(highD(1)+highD(2)+highD(3)+opend(0))/4",
            "N_power=(closeD avg): neutral level between bull/bear power",
            "entry bands: k*5 ticks offset from power level for two-tier entry",
            "4 entry signals per direction (L_in_1..4) for different market states",
            "re-entry on pullback: c<o (bearish bar) used as long re-entry condition",
            "power levels blend today open with 3-day average for dynamic S/R"
        ],
        "tags": ["day-trade", "6m", "breakout", "power-levels", "TX"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/3. 3DOHL (2).md",
        "strategy_id": "_2110_3DOHLa20TXa206Ma20DO_v2",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "6m",
        "instruments": ["TX"],
        "entry_logic": {"long": "same as 3. 3DOHL", "short": "same"},
        "exit_logic": {"time_exit": "SetExitOnClose"},
        "indicators": ["Daily OHLC 3-day averages"],
        "time_filter": "t<1200",
        "key_concepts": ["duplicate of 3. 3DOHL"],
        "tags": ["day-trade", "6m", "duplicate", "TX"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/3. Aline-2.md",
        "strategy_id": "_2107_Alineb2d2_TXFb207Mb20DF",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "7m",
        "instruments": ["TXF"],
        "entry_logic": {
            "long": "condition1 AND t>0845 -> L_in_1/2: stop at AmhighD_TX(0)-5; re-entry L_in_N: market if condition40",
            "short": "condition1 AND t>0845 -> S_in_1/2: stop at Amlowd_TX(0)+5; re-entry S_in_N: market if condition40"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "c <= max(BB_Line, AmlowD_tx(0)) after barssinceentry>5 -> L_out; also loss-exit if c<entryprice"
        },
        "indicators": ["AmhighD_TX", "Amlowd_TX", "BB_Line (Bollinger Band)", "Average(h,3)", "Average(l,3)"],
        "time_filter": "t>0845 calctime(sess1endtime,-4*barinterval) time>0330 t<0400",
        "key_concepts": [
            "AM session high/low as primary entry reference (offset -5 ticks for less aggressive fill)",
            "Bollinger Band line as dynamic trailing exit for longs",
            "condition40 triggers market-order re-entry when position held and signal refreshes",
            "overnight session filter (0330-0400) for pre-market signals",
            "barssinceentry>5 required before signal exit activates to avoid premature stop"
        ],
        "tags": ["day-trade", "7m", "AM-session", "TXF"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/3. Aline-2 (2).md",
        "strategy_id": "_2107_Alineb2d2_TXFb207Mb20DF_v2",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "7m",
        "instruments": ["TXF"],
        "entry_logic": {"long": "same as 3. Aline-2", "short": "same"},
        "exit_logic": {"time_exit": "SetExitOnClose"},
        "indicators": ["AmhighD_TX", "BB_Line", "Average"],
        "time_filter": "t>0845",
        "key_concepts": ["duplicate of 3. Aline-2"],
        "tags": ["day-trade", "7m", "duplicate", "TXF"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/3. BS ratio.md",
        "strategy_id": "_2109_BSc20Ratioc20TXc2030Mc20LF",
        "classification": "Trend Following / Breakout",
        "direction": "both",
        "timeframe": "30m",
        "instruments": ["TX"],
        "entry_logic": {
            "long": "long_line > Short_line AND condition99 AND condition1 -> L_in: stop at highest(h,len)",
            "short": "long_line > Short_line AND condition99 AND condition1 -> S_in: stop at lowest(l,len)"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose"
        },
        "indicators": [
            "BuySaleRatio = summation(BuyRatio,len)/summation(SaleRatio,len)",
            "long_line = summation(BuySaleRatio,len)",
            "Average(BuySaleRatio,len)",
            "Highest/Lowest(len)"
        ],
        "time_filter": "CalcTime(sess1starttime,barinterval)",
        "key_concepts": [
            "buy/sell ratio (order flow proxy): BuySaleRatio = rolling buy vol / sell vol",
            "long_line is cumulative sum of BuySaleRatio - measures sustained buying pressure",
            "entry requires long_line > Short_line (sustained buy dominance vs sell dominance)",
            "breakout entry using len-bar high/low stop orders",
            "exits when BuySaleRatio MA reverts to neutral (no-trend condition)"
        ],
        "tags": ["trend", "30m", "order-flow", "TX"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/3. BS ratio (2).md",
        "strategy_id": "_2109_BSc20Ratioc20TXc2030Mc20LF_v2",
        "classification": "Trend Following / Breakout",
        "direction": "both",
        "timeframe": "30m",
        "instruments": ["TX"],
        "entry_logic": {"long": "same as 3. BS ratio", "short": "same"},
        "exit_logic": {"time_exit": "SetExitOnClose"},
        "indicators": ["BuySaleRatio", "Summation", "Highest", "Lowest"],
        "time_filter": "CalcTime(sess1starttime,barinterval)",
        "key_concepts": ["duplicate of 3. BS ratio"],
        "tags": ["trend", "30m", "order-flow", "duplicate", "TX"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/3. LSlevel.md",
        "strategy_id": "_2112a20LSlevel_7Ma20LF",
        "classification": "Trend Following / Breakout",
        "direction": "both",
        "timeframe": "7m",
        "instruments": ["TX"],
        "entry_logic": {
            "long": "mp=0 AND condition1 -> L_in_1: stop order",
            "short": "mp=0 AND condition1 -> S_in_1: stop order"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "maxEL/maxES market exit"
        },
        "indicators": [
            "long_level = H - Lowest(L,len)",
            "short_level = Highest(H,len) - L",
            "avg_LL = Average(long_level,len)",
            "avg_SL = Average(short_level,len)",
            "trend = avg_LL - avg_SL"
        ],
        "time_filter": "t>0900 t<1200",
        "key_concepts": [
            "long_level measures distance from current high to lookback low (bull strength indicator)",
            "short_level measures distance from lookback high to current low (bear strength indicator)",
            "trend = avg_LL - avg_SL: positive means bulls stronger than bears over len bars",
            "entry when trend differential confirms direction",
            "morning session only (0900-1200)"
        ],
        "tags": ["trend", "7m", "range-analysis", "TX"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/3. reverse4.md",
        "strategy_id": "_2108_Reversea2d4_TXFa207M_DF",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "7m",
        "instruments": ["TXF"],
        "entry_logic": {
            "long": "mp=0 AND condition1 AND condition3 -> L-in-1: stop; condition10 -> L-Rin reversal stop; condition40 -> L_in_N market",
            "short": "mp=0 AND condition1 AND condition3 -> S-in-1: stop; condition10 -> S-Rin reversal; condition40 -> S_in_N market"
        },
        "exit_logic": {
            "stop_loss": "entryprice +/- stp (ATR-based)",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "c<entryprice intraday loss exit"
        },
        "indicators": [
            "AvgTrueRange(len)",
            "h1 = Highest(h,len) - ATR/2 (ATR-adjusted Donchian upper)",
            "l1 = Lowest(l,len) + ATR/2 (ATR-adjusted Donchian lower)",
            "Average(h,3)", "Average(l,3)", "AmHighD_TX", "CountIf"
        ],
        "time_filter": "t>0845 t<1200 time>0330 t<0400 calctime(sess1endtime,-2*barinterval)",
        "key_concepts": [
            "ATR-adjusted Donchian bands: subtract ATR/2 from highest, add ATR/2 to lowest for tighter channel",
            "reverse entry (L-Rin): enters long when price reverses from short zone",
            "condition40 for scaling into held position on new signal",
            "countif(h>=amHighD_TX,k) counts breakout bars to adjust stop price dynamically",
            "avgprice (OHLC/4) used for pre-2017 dates as alternative reference",
            "dual session coverage: main (0845-1200) + overnight (0330-0400)"
        ],
        "tags": ["day-trade", "7m", "ATR", "reversal", "TXF"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/3. reverse4 (2).md",
        "strategy_id": "_2108_Reversea2d4_TXFa207M_DF_v2",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "7m",
        "instruments": ["TXF"],
        "entry_logic": {"long": "same as 3. reverse4", "short": "same"},
        "exit_logic": {"stop_loss": "ATR-based", "time_exit": "SetExitOnClose"},
        "indicators": ["ATR", "Highest", "Lowest"],
        "time_filter": "t>0845 t<1200",
        "key_concepts": ["duplicate of 3. reverse4"],
        "tags": ["day-trade", "7m", "ATR", "reversal", "duplicate", "TXF"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/3. trend-1.md",
        "strategy_id": "_2111_Trenda2d1_TXF_150Ma20LF",
        "classification": "Breakout",
        "direction": "both",
        "timeframe": "unknown",
        "instruments": ["TXF"],
        "entry_logic": {
            "long": "condition1 AND flagM=0 -> L_in_1: stop at max(AmhighD_TX(0), highest(H,3))",
            "short": "condition1 AND flagM=0 -> S_in_1: stop at min(AmhighD_TX(0), lowest(L,3))"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "L_out_1 when high range condition triggers; weekly stop based on highW"
        },
        "indicators": ["Highest(H,len1)", "Lowest(L,len1)", "CountIf(condition21,len2)", "highW(1) weekly high"],
        "time_filter": "none",
        "key_concepts": [
            "entry at max of AM session high and 3-bar highest for confirmed breakout",
            "highestbar(H,len1)<len3: breakout must be recent (within len3 bars)",
            "weekly high as trailing exit: based on highW(1)*(1-stp_ratio/200)",
            "CountIf(condition21,len2)>1 filters for sustained trend condition",
            "flagM suppresses re-entry during unfavorable regimes"
        ],
        "tags": ["breakout", "trend", "weekly", "TXF"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/3. weeklevel.md",
        "strategy_id": "_2202a20weeklevela20TXFa2030Ma20LF",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "30m",
        "instruments": ["TXF"],
        "entry_logic": {
            "long": "mp=0 AND kday>1 -> L_in_1: market order",
            "short": "mp=0 AND kday>1 -> S_in_1: market order"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "L_out_1 range exit; settlement exit at close"
        },
        "indicators": [
            "Highest(h,barssinceentry)/Lowest(l,barssinceentry) for intrabar range",
            "CountIf(h-c>c-l,len) -> condition21 bearish candle structure count",
            "CountIf(h-c<c-l,len) -> condition22 bullish candle structure count",
            "Daily High tracking"
        ],
        "time_filter": "t>=1330",
        "key_concepts": [
            "kday>1 ensures at least 2 trading days since settlement for swing hold",
            "candle structure analysis: h-c vs c-l ratio classifies bullish/bearish bias over len bars",
            "market order entry - relies entirely on condition21/22 for direction filter",
            "range exit: if highest-lowest of position > entryprice*(stp_ratio/10) take profit",
            "settlement-day close exit",
            "afternoon entry window (t>=1330)"
        ],
        "tags": ["day-trade", "30m", "weekly", "candle-structure", "TXF"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/3.3DHL.md",
        "strategy_id": "_2106_3DHL_TX_24Ma20LO",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "unknown",
        "instruments": ["TX"],
        "entry_logic": {
            "long": "mp=0 AND condition1 -> L_in_1: stop at iff(condition99, max(highD(1),highD(0))-monthlost, highD(0)-monthlost); condition30+condition20 -> L_in_2",
            "short": "mp=0 AND condition1 -> S_in_1: stop at iff(condition99, min(LowD(1),LowD(0))+monthlost, LowD(0)+monthlost); condition31+condition11 -> S_in_2"
        },
        "exit_logic": {
            "stop_loss": "entryprice +/- stpl (fixed)",
            "profit_target": "entryprice +/- stpl (same value = 1:1 R/R)",
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "c < (lowD1+lowD2+lowD3)/3 -> L_out_2; c > (highD1+highD2+highD3)/3 -> S_out_2"
        },
        "indicators": [
            "value1 = (highD(1)+highD(2)+highD(3))/3 (3-day avg high resistance)",
            "value2 = (lowD(1)+lowD(2)+lowD(3))/3 (3-day avg low support)",
            "monthlost = running monthly loss counter for adaptive entry offset",
            "condition99 = monthly loss threshold breached flag"
        ],
        "time_filter": "none",
        "key_concepts": [
            "3-day average high/low as pivot entry price adjuster",
            "monthlost: entry price offset by cumulative monthly loss (adaptive risk sizing)",
            "condition99 monthly loss mode: switches to conservative entry using 2-day max high",
            "symmetric SL=PT (same stpl) creates fixed 1:1 risk-reward",
            "secondary exit on 3-day average high/low as mean-reversion pivot",
            "kday counter: 0 on settlement day, increments through week for cycle tracking"
        ],
        "tags": ["day-trade", "pivot-levels", "monthly-drawdown", "adaptive", "TX"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/3.3DHL (2).md",
        "strategy_id": "_2106_3DHL_TX_24Ma20LO_v2",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "unknown",
        "instruments": ["TX"],
        "entry_logic": {"long": "same as 3.3DHL", "short": "same"},
        "exit_logic": {"stop_loss": "entryprice +/- stpl", "profit_target": "entryprice +/- stpl"},
        "indicators": ["3-day avg H/L", "monthlost"],
        "time_filter": "none",
        "key_concepts": ["duplicate of 3.3DHL"],
        "tags": ["day-trade", "pivot-levels", "duplicate", "TX"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/3.3DHL (3).md",
        "strategy_id": "_2106_3DHL_TX_24Ma20LO_v3",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "unknown",
        "instruments": ["TX"],
        "entry_logic": {"long": "same as 3.3DHL", "short": "same"},
        "exit_logic": {"stop_loss": "entryprice +/- stpl", "profit_target": "entryprice +/- stpl"},
        "indicators": ["3-day avg H/L", "monthlost"],
        "time_filter": "none",
        "key_concepts": ["duplicate of 3.3DHL"],
        "tags": ["day-trade", "pivot-levels", "duplicate", "TX"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/3.3DHL (4).md",
        "strategy_id": "_2106_3DHL_TX_24Ma20LO_v4",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "unknown",
        "instruments": ["TX"],
        "entry_logic": {"long": "same as 3.3DHL", "short": "same"},
        "exit_logic": {"stop_loss": "entryprice +/- stpl", "profit_target": "entryprice +/- stpl"},
        "indicators": ["3-day avg H/L", "monthlost"],
        "time_filter": "none",
        "key_concepts": ["duplicate of 3.3DHL"],
        "tags": ["day-trade", "pivot-levels", "duplicate", "TX"]
    },
    {
        "batch": 25,
        "file": "E:/投資交易/pla_md/logic/4.策略程式碼.md",
        "strategy_id": "c3001_TX_Breakout_DO",
        "classification": "Breakout",
        "direction": "both",
        "timeframe": "7m",
        "instruments": ["TX"],
        "entry_logic": {
            "long": "t>0930 AND t<1000 AND opend(0)>closed(1) AND opend-closed<Jump AND C>highD(1) -> B: stop at highest(C,len)",
            "short": "t>0930 AND t<1000 AND opend(0)<closed(1) AND closed-opend<Jump AND C<lowD(1) -> S: stop at lowest(C,len)"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "if mp=1 AND c>opend(0)+X sell Bsp profit; if mp=-1 AND c<opend(0)-X cover Ssp; BE exit at t>=1339"
        },
        "indicators": ["Highest(C,len)", "Lowest(C,len)", "Daily Open/High/Low/Close"],
        "time_filter": "t>0930 t<1000 t>=1339",
        "key_concepts": [
            "opening 30-min breakout window (0930-1000) with gap direction confirmation",
            "gap-up long: open>prev close AND gap<Jump threshold (filters runaway gaps)",
            "direction confirmation: C>highD(1) for long (price above yesterday high)",
            "CC flag: +1 if first bar closes above prev close, -1 if below (daily sentiment tracker)",
            "profit target: opend(0)+X points from open for long, -X for short",
            "time stop: BE exit at 1339 to avoid settlement-period risk"
        ],
        "tags": ["breakout", "7m", "opening-range", "gap-filter", "TX"]
    }
]

output_path = "C:/Users/admin/workspace/digital-immortality/results/digestion_log.jsonl"
with open(output_path, "a", encoding="utf-8") as f:
    for entry in entries:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print(f"Written {len(entries)} entries to JSONL")
