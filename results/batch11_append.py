import json

records = [
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4) 策略腳本.md",
        "strategy_id": "d21d40_TXAL_1_013_BoxInflectionBreakout_202107",
        "classification": "Trend Following / Breakout",
        "direction": "both",
        "timeframe": "unknown",
        "entry_logic": {
            "long": "condition10 -> stop order at highest(_price_buy, _box_len/2)",
            "short": "condition10 -> stop order at lowest(_price_sell, _box_len/2)"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "sell/buytocover next bar at market"
        },
        "indicators": ["SMA", "Highest", "Lowest", "CountIf"],
        "time_filter": None,
        "key_logic": "Box inflection breakout: enter on stop order at box high/low extremes defined by half-box length; exit on close or signal; filters out settlement days via countif",
        "tags": ["MA", "breakout", "trend"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4) 策略腳本_Ed001_TX_GapMA_6K_LT.md",
        "strategy_id": "Ed001_TX_GapMA_6K_LT",
        "classification": "Swing / Long-Term",
        "direction": "both",
        "timeframe": "intraday bar-interval dependent",
        "entry_logic": {
            "long": "opend(0)>highd(1) AND c<opend(0)*(1-ratio)+ratio*lowd(1) AND c<avg(c,300/barinterval) AND fast_MA>slow_MA -> market",
            "short": "opend(0)<lowd(1) AND c>opend(0)*(1-ratio)+ratio*highd(1) AND c>avg(c,300/barinterval) AND fast_MA<slow_MA -> market"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": None
        },
        "indicators": ["SMA", "Daily Open", "Daily High", "Daily Low"],
        "time_filter": None,
        "key_logic": "Gap MA 6k: today gaps above prior high (long) or below prior low (short); price must retrace into interpolated gap zone (ratio-weighted between open and prior extreme); dual MA confirms trend; pure EOD exit",
        "tags": ["MA", "gap", "swing"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4) 策略腳本_ED001_TX_JumpGapMA6K_LT.md",
        "strategy_id": "b21b40Ed001_TX_JumpGapMA_6K_LT",
        "classification": "Swing / Long-Term",
        "direction": "both",
        "timeframe": "intraday bar-interval dependent",
        "entry_logic": {
            "long": "opend(0)>highd(1) AND c<ratio-interpolated gap zone AND c<avg AND fast_MA>slow_MA -> market",
            "short": "opend(0)<lowd(1) AND c>ratio-interpolated gap zone AND c>avg AND fast_MA<slow_MA -> market"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": None
        },
        "indicators": ["SMA", "Daily Open", "Daily High", "Daily Low"],
        "time_filter": None,
        "key_logic": "JumpGap variant of Ed001: identical logic to GapMA - jump gap opens beyond prior day range, retrace into gap zone, dual MA filter; both variants are equivalent implementations with same conditions",
        "tags": ["MA", "gap", "swing"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4) 策略腳本_TXAL_1_007_VCP+RangeBreakout.md",
        "strategy_id": "d21d40_TXAL_1_007_VCP_RangeBreakout",
        "classification": "Trend Following / Breakout",
        "direction": "both",
        "timeframe": "intraday bar-interval dependent",
        "entry_logic": {
            "long": "c > _box_high -> market",
            "short": "c > _box_high -> market"
        },
        "exit_logic": {
            "stop_loss": "fixed at entryprice +/- _stoploss_point",
            "profit_target": "dynamic profit target",
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "long time no profit -> exit market at barssinceentry threshold"
        },
        "indicators": ["SMA", "Highest", "Lowest", "CountIf", "Summation"],
        "time_filter": None,
        "key_logic": "VCP + Range Breakout: variance compression pattern (VCP) uses summation/squareroot to compute variance contraction; enter on box-high breakout; stop at fixed points; time-based exit if no profit within barssinceentry window",
        "tags": ["MA", "breakout", "trend", "VCP", "variance-compression"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4) 策略腳本Shuen004_TX_LSS_LT.md",
        "strategy_id": "Shuen004_TX_LSS_LT",
        "classification": "Swing / Long-Term",
        "direction": "both",
        "timeframe": "unknown",
        "entry_logic": {
            "long": "condition30 -> stop at highest(h,3)",
            "short": "condition30 -> stop at lowest(l,3)"
        },
        "exit_logic": {
            "stop_loss": "entryprice - iff(gap_up, iff(wide_range>200,3,2),1)*stl for long; symmetric for short",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "slowk<30 AND slowd<30 -> sell; slowk>70 AND slowd>70 -> buytocover; LSS channel exit"
        },
        "indicators": ["SMA", "Highest", "Lowest", "Stochastic SlowK", "Stochastic SlowD", "Daily OHLC", "LSS High/Low"],
        "time_filter": ["0900", "1130", "1330"],
        "key_logic": "LSS (Low-Short-Short) system: 3-bar high/low breakout entry; stop sized dynamically by gap type (gap day = larger stop) and day range width (>200pt = 3x, else 2x, normal=1x); stochastic overbought/oversold forces exit; LSSHigh/Low from 3-day OHLC averages as channel",
        "tags": ["MA", "breakout", "stochastic", "swing", "LSS"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4) 策略腳本Shuen034_TX_StochRSI_LT.md",
        "strategy_id": "Shuen034_TX_StochRSI_LT",
        "classification": "Swing / Long-Term",
        "direction": "both",
        "timeframe": "30m",
        "entry_logic": {
            "long": "condition30 (StochRSI cross above SRMA) -> order",
            "short": "condition30 (StochRSI cross below SRMA) -> order"
        },
        "exit_logic": {
            "stop_loss": "c - 2*len / c + 2*len",
            "profit_target": "c - 2*len / c + 2*len (symmetric stop/target)",
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": None
        },
        "indicators": ["SMA (SRMA = avg of StochRSI)", "RSI", "Highest/Lowest of RSI for normalization"],
        "time_filter": ["0900", "1330"],
        "key_logic": "StochRSI: normalizes RSI into 0-100 oscillator using (RSI-RSImin)/(RSImax-RSImin)*100; SRMA = average(StochRSI,len); entry on crossover; symmetric fixed stop and target at 2*len points",
        "tags": ["30m", "MA", "RSI", "StochRSI", "swing"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4) 策略腳本Shuen036_TX_ASI23K_V3_LT.md",
        "strategy_id": "Shuen036_TX_ASI23K_V1_LT",
        "classification": "Swing / Long-Term",
        "direction": "both",
        "timeframe": "intraday bar-interval dependent",
        "entry_logic": {
            "long": "mp=0 AND EntriesToday<2 AND condition30 AND d<>LastTradeDay -> market; OR ASI cross avg(ASI,len) -> limit",
            "short": "symmetric conditions -> market or limit"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "Sell/Buytocover this bar at c on time filter"
        },
        "indicators": ["SMA", "ATR (AvgTrueRange 13)", "Daily OHLC", "ASI (Accumulation Swing Index)", "AvgGap/AvgDRange"],
        "time_filter": ["sess1starttime", "sess1endtime-4*barinterval", "1100", "1330"],
        "key_logic": "ASI 23k: ASI crossover average as primary signal; ATR(13)*2 as stop buffer; daily gap (opend-closeD[1]) and daily range normalized by 20-day average; max 2 entries per day; no last-trade-day entries",
        "tags": ["ATR", "MA", "ASI", "swing"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4) 策略腳本Shuen037_TX_CamarillaPivot6k.md",
        "strategy_id": "Shuen037_TX_CamarillaPivot6k_V1_DT",
        "classification": "Unclassified",
        "direction": "both",
        "timeframe": "6m",
        "entry_logic": {
            "long": "B1: first bar of session -> market; B2: condition30 -> stop at SP2; B3: t>=1230+barinterval*highestbar(c,5) -> stop at entryprice+stl",
            "short": "S1: condition30 -> market; S2: condition30 -> stop at RT2; S3: mp>0 -> stop at entryprice-stl"
        },
        "exit_logic": {
            "stop_loss": "fixed at entryprice +/- stl",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": None,
            "signal_exit": "win_pts>RT4-SP4; entryname=B2 and c>RT4; time t>=1230 exit"
        },
        "indicators": ["Camarilla Pivot Levels: RT4/RT3/RT2/SP2/SP4", "Daily Open/High/Low/Close", "HL = 0.5*(2-day avg range)"],
        "time_filter": ["0900", "1230"],
        "key_logic": "Camarilla Pivot 6m: RT/SP levels computed from 2-day average HL range; B1 first-bar market entry; B2 at SP2 support stop; exit when profit exceeds RT4-SP4 full range; B3 re-entry after highest bar in 5 after 1230; highestbar(c,5) finds best recent bar for timing",
        "tags": ["6m", "pivot", "Camarilla"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4) 策略腳本Shuen038_TX_EarlyORB5K_DT.md",
        "strategy_id": "Shuen038_TX_EarlyORB5K_DT",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "unknown",
        "entry_logic": {
            "long": "B1/B2: condition30 -> market; B3: stop at opend(0)+5; REB1: mp<0 -> stop at lowest(l,3)+st; REB2: mp<0 -> stop at entryprice+30; REB3: c>entryprice+iff(lowd=loww AND DoW>1,50,100) -> market",
            "short": "S1/S2: condition30 -> market; S3: stop at opend(0)-5; RES1/2/3: reversal stops symmetric"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": None,
            "signal_exit": "c<entryprice-100; barssinceentry>5*in AND countif(c<entryprice,in)=in; momentum decay exit"
        },
        "indicators": ["Highest", "Lowest", "Daily OHLC", "CountIf", "Weekly High/Low (highw/loww)"],
        "time_filter": ["<1200", ">1320", "DayOfWeek filter"],
        "key_logic": "Early ORB 5k: 3-level reversal entry system with weekly extreme awareness; take-profit target 50pts when today is weekly low day (not Monday), else 100pts; momentum decay exit via countif all bars below entryprice in window; opend(0)+/-5 as very tight ORB entry",
        "tags": ["breakout", "ORB", "day-trade", "weekly-filter"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4) 策略腳本Shuen040_TX_WeekCostLine_FLT.md",
        "strategy_id": "Shuen040_TX_WeekCostLineV1_FLT",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "unknown",
        "entry_logic": {
            "long": "condition70 -> B1/B2 market",
            "short": "condition70 -> S1/S2 market"
        },
        "exit_logic": {
            "stop_loss": "fixed at entryprice +/- STL",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "sell/buytocover market on signal"
        },
        "indicators": ["WeekCostLine (weekly average cost, implied)"],
        "time_filter": ["0900", "1500", "0500", "2100", "0400"],
        "key_logic": "WeekCostLine: weekly average cost as mean-reversion or trend anchor; multi-session time filters spanning overnight and daytime; fixed stop, signal-driven exit; dual long entries (B1/B2) allow scaling or re-entry",
        "tags": ["day-trade", "weekly-cost-line"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4) 策略腳本Shuen041_TX_WeekCDP_LT.md",
        "strategy_id": "Shuen041_TX_WeekCDP_LT",
        "classification": "Swing / Long-Term",
        "direction": "both",
        "timeframe": "unknown",
        "entry_logic": {
            "long": "condition30 -> B1 market",
            "short": "condition30 -> S1 market"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "win_pts > iff(same_entry_day, ah2-al2, ah-al) -> exit"
        },
        "indicators": ["CDP = (H+L+2*C)/4", "ah/nh/al/nl from CDP and daily range", "Daily High/Low/Close"],
        "time_filter": ["0845", "1300", "1330", "DayOfWeek filter"],
        "key_logic": "Week CDP: daily CDP (Central Dip Point) as base; ah2/al2 for same-day targets (tighter), ah/al for next-day wider targets; exit when profit exceeds daily CDP range; weekly day-of-week filter for weekly rhythm trading",
        "tags": ["CDP", "swing", "weekly-filter"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4)%%TX_KBAR_L0_15K.md",
        "strategy_id": "c25c25TX_kbar_L0_15K",
        "classification": "Breakout",
        "direction": "both",
        "timeframe": "unknown",
        "entry_logic": {
            "long": "mp=0 AND EntriesToday(D)=0 -> stop at Highest(h,highestbar(HL,length))+Highest(HL,length)",
            "short": "mp=0 AND EntriesToday(D)=0 -> stop at lowest(l,highestbar(HL,length))-Highest(HL,length)"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": None,
            "signal_exit": "Lout-B/Lout-S next bar market; countif(H<entryprice,barssinceentry)>0.6*barssinceentry -> exit"
        },
        "indicators": ["Highest", "Lowest", "CountIf", "HL range"],
        "time_filter": ["1315"],
        "key_logic": "KBAR L0: one trade per day; entry level = high at most-extreme HL bar + that bar's HL range as buffer; uniquely uses highestbar() to find the index of peak range bar, then places stop at that bar's high plus its own range; 60% countif momentum decay as exit",
        "tags": ["breakout", "kbar-pattern"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4)@Ivan2109_TX_MACP19k_LT.md",
        "strategy_id": "b40Ivan2109_TX_MACP19k_LT",
        "classification": "Swing / Long-Term",
        "direction": "both",
        "timeframe": "intraday bar-interval dependent",
        "entry_logic": {
            "long": "T_L: mp=0 AND not last-trade-day -> stop at maxlist(OpenD(0)+stl*0.5, highD(0)-1); CT_L: mp=0 -> stop at (HighD(0)+H)/2; PL: mp<0 AND H<dn AND C>(OpenD(0)+highd(0))/2 -> market reversal",
            "short": "T_S: stop at minlist(OpenD(0)-stl*0.5, LowD(0)+1); CT_S: DIF-DIF[1]>0 -> stop at (LowD(0)+L)/2; PS: mp>0 AND L>up AND C<(OpenD(0)+lowd(0))/2 -> market reversal"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": None,
            "signal_exit": "9% limit profit exit from entryprice; LTO market exit"
        },
        "indicators": ["SMA (avgprice)", "EMA/XAverage of H and L", "DIF = C - Average(avgprice,Len)", "Daily OHLC", "up/dn bands from closeD+stl*r"],
        "time_filter": ["1200", "1330"],
        "key_logic": "MACP 19k: DIF (price minus avgprice MA) as momentum indicator; XAverage of H/L vs daily mid determines trend zone; 3 entry modes: T (trend stop near open), CT (counter-trend at mid-price), P (position reversal when in losing trade); 9% profit limit target; k adapts via barssinceentry",
        "tags": ["MA", "EMA", "swing", "MACP", "position-reversal"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4)@Ivan2111_TX_shadow11k_LT.md",
        "strategy_id": "b40Ivan2111_TX_shadow11k_LT",
        "classification": "Swing / Long-Term",
        "direction": "both",
        "timeframe": "intraday bar-interval dependent",
        "entry_logic": {
            "long": "condition99 -> stop at maxlist(highd(0),highd(1),highd(2))",
            "short": "condition99 -> stop at minlist(lowd(0),lowd(1),lowd(2))"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": None,
            "signal_exit": "LTO/STO next bar market"
        },
        "indicators": ["upshadow = maxlist(highd(0..2)) - maxlist(opend(2),C)", "dnshadow = minlist(opend(2),C) - minlist(lowd(0..2))", "totl = max high - min low across 3 days"],
        "time_filter": ["1330"],
        "key_logic": "Shadow 11k: measures candlestick shadow dominance across 3 days; upshadow (wick above body) vs dnshadow (tail below body) over 3-day combined range; condition99 likely filters for dominant direction shadow; enters at 3-day range extremes via stop order",
        "tags": ["swing", "shadow-pattern", "3-day-range"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4)@Ivan2112_TX_CorrectionShort_20k_LT.md",
        "strategy_id": "b40Ivan2112_TX_CorrectionShort_20k_LT",
        "classification": "Swing / Long-Term",
        "direction": "both",
        "timeframe": "intraday bar-interval dependent",
        "entry_logic": {
            "long": "condition99 AND t>=0930 -> stop at (highd(0)+H)/2",
            "short": "condition99 AND t>=0930 -> stop at (lowd(0)+L)/2"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": None,
            "signal_exit": "mp>0 AND barssinceentry>len AND c<entryprice AND highestbar(C,len)>0.8*len -> exit (price peak was early in position life)"
        },
        "indicators": ["feature = Highest(L,len) - Lowest(H,len)", "ATR for condition1/condition2 comparison"],
        "time_filter": ["1330", "0930"],
        "key_logic": "CorrectionShort 20k: feature=Highest(L)-Lowest(H) measures inverted range (L range above H range = correction territory); condition1: feature>ATR*(1+r) for true correction; exit logic: highestbar(C,len)>0.8*len means price peak was in the first 20% of position age - momentum gone, cut",
        "tags": ["ATR", "breakout", "swing", "correction-pattern"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4)@R006_TX_Bollien_Backout_FLT.md",
        "strategy_id": "d40R006_TX_Bollien_Backout_FLT",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "60m",
        "entry_logic": {
            "long": "mp=0 -> L_in market (Bollinger band backout conditions implied)",
            "short": "mp=0 -> S_in market"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "long: c<entryprice+winPoint/2 -> exit (failed to reach half target); short: c>entryprice-winPoint/2 -> exit"
        },
        "indicators": ["Bollinger Band (implied)", "winPoint (expected move)"],
        "time_filter": None,
        "key_logic": "Bollinger Backout 60m: Bollinger band mean-reversion; exit logic is distinctive - exit if price fails to reach 50% of expected winPoint, cutting momentum-failed trades early rather than holding to stop",
        "tags": ["60m", "day-trade", "Bollinger", "mean-reversion"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4)_@LV@_tx_TransFormer_17K_(DT)LT.md",
        "strategy_id": "LV_tx_TransFormer_17K_DTLT",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "intraday bar-interval dependent",
        "entry_logic": {
            "long": "L: dayin>=TD AND k>=3 AND mp=0 AND ExitsToday=0 -> stop; RL: condition21 -> stop; L_In: condition10 -> stop; DT_L2: dayin>=3 AND k in [2,ky/2] AND mp=0 -> stop",
            "short": "S/RS/S_In/DT_S2: mirror long conditions with symmetric constraints"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": "entryprice + iff(barssinceentry>ky, stp/(ED*0.5), stp) for long",
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "c<entryprice+(up-dn)/2 OR c<(highw(1)+loww(1)*2)/3 -> exit long (weekly pivot test)"
        },
        "indicators": ["Daily OHLC mid=(H+L+2C)/4 and midy for prior day", "Weekly High/Low (highw/loww)", "dayin counter", "k counter", "ED parameter"],
        "time_filter": ["sess1endtime-1*barinterval"],
        "key_logic": "TransFormer: complex multi-mode system tracking consecutive days (dayin) and bar count (k); 4 entry modes per direction; profit target halves when barssinceentry>ky (half-cycle elapsed); weekly pivot (highw+2*loww)/3 as floor/ceiling for exit; DT_L2 sub-mode for late-trend entries",
        "tags": ["day-trade", "TransFormer", "weekly-pivot", "complex"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4)_011_TX_4Day (OHLC)_FDT.md",
        "strategy_id": "_011_TX_5K_4Day_OHLC_FDT",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "intraday bar-interval dependent",
        "entry_logic": {
            "long": "normal: mp=0 AND dentry=0 AND condition1 -> stop at h; adaptive: (c+c[1])/2<Smove AND c<mid -> market; reversal: mp<>0 AND dentry<=1 -> stop at (mid+up)/2; countS>0 -> market",
            "short": "normal: mp=0 AND dentry=0 -> stop at l; AmClosed-openadp>avgmin/2 -> market reversal; mp<>0 AND dentry<=1 -> stop at (mid+dn)/2"
        },
        "exit_logic": {
            "stop_loss": "Max_WinPoint*0.8 from entry",
            "profit_target": "entryprice or entryprice+Max_WinPoint*0.8",
            "trailing_stop": None,
            "time_exit": "t=1505 forced exit; SetExitOnClose",
            "signal_exit": "TM-L/TM-LL/BX10 exit signals"
        },
        "indicators": ["4-day OHLC levels (mid/up/dn)", "Smove as momentum threshold", "AmClosed_TX/AmOpend_TX", "avgmin"],
        "time_filter": ["sess1starttime+barinterval", "1505", "0430", "0500"],
        "key_logic": "4-Day OHLC FDT: derives mid/up/dn from 4-day OHLC reference; Max_WinPoint controls both stop (at 80%) and target; Smove momentum threshold for adaptive entry; dentry<=1 allows one reversal trade; AmClosed vs openadp for position profit threshold; t=1505 hard exit",
        "tags": ["day-trade", "OHLC", "complex", "4-day-pattern"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4)BN_002_TX_BarTunnel_LO_8k.md",
        "strategy_id": "c40BN_002_TX_BarTunnel_LO_8k_final",
        "classification": "Unclassified",
        "direction": "both",
        "timeframe": "unknown",
        "entry_logic": {
            "long": "right-side: 915<=t<=1245 AND mp=0 AND k>2 AND not last-trade-day -> market; left-side: c[1]>RangeHigh[1] AND MRO(c<RangeLow,k,1) in (0,k) AND c<o -> market; bh: openpositionprofit<0 -> market",
            "short": "right-side/left-side/bh symmetric; l>rangehigh -> directional market"
        },
        "exit_logic": {
            "stop_loss": "stop at rangelow (for long) / rangehigh (for short)",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": None,
            "signal_exit": "morning gap up AND close<open AND t>1300 -> sell; bh conditions"
        },
        "indicators": ["RangeHigh/RangeLow (tunnel)", "CountIf (k>=0.6*kperiod for left-side)", "MRO (most recent occurrence function)", "Daily Open/High/Low/Close"],
        "time_filter": ["915", "1245", "1300", "1315"],
        "key_logic": "BarTunnel: defines tunnel range using k-period highs/lows; right-side entry when k consecutive bars confirm tunnel and MRO shows recent touch; left-side entry after tunnel breach if price still trending; stop at tunnel boundary; morning gap up with afternoon weakness = exit signal",
        "tags": ["kbar-pattern", "tunnel", "range-breakout", "MRO"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4)BN_003_TX_Sar_FDO_10k.md",
        "strategy_id": "c40BN_005_TX_SAR_FDT_10k_v2",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "intraday bar-interval dependent",
        "entry_logic": {
            "long": "Basic Buy: k in (3,iff(mp=0,10,20)] AND Dentry<=1 -> stop at h; stprevse: openprofit<0 AND condition70 AND abs(c-entryprice)>stp -> market; Loser buy again: mp>0 -> stop at lastentryprice",
            "short": "Basic Sellshort: symmetric; stp Revers: mp<>-1 AND condition21/22 -> market; Loser change direction: stop at 2*lossprice-lastentryprice"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose (AM and PM session exits)",
            "signal_exit": "Loser sell market; day-over AM/PM exits"
        },
        "indicators": ["ATR (AvgTrueRange)", "Average Price (OHLC/4)", "CountIf"],
        "time_filter": ["0845", "1345", "1500", "0500", "sess1endtime-barinterval"],
        "key_logic": "SAR FDT 10k: parabolic-SAR-like with 3 entry modes; k window expands from 10 to 20 when in position (more flexible re-entry); Loser logic: re-enter at lastentryprice if losing, or reverse at 2*lossprice-lastentry (equidistant reversal); Dentry<=1 prevents over-trading",
        "tags": ["ATR", "day-trade", "SAR", "loss-reversal"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4)BN_004_TX_Pivot_FLO_10k.md",
        "strategy_id": "a40BN_006_TX_Swing_v4",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "intraday bar-interval dependent",
        "entry_logic": {
            "long": "LE1: mp=0 AND cond70/10/12 -> stop at h; LE2: mp=0 AND cond70/10/12 -> stop at highest(h, Barnumber-SW_LowBar[2])",
            "short": "SE1: mp=0 AND cond70/20/22 -> stop at l; SE2: mp=0 -> stop at lowest(l, Barnumber-SW_HighBar[2])"
        },
        "exit_logic": {
            "stop_loss": "stop at refvaluelow2/refvaluehigh2 (latest swing reference) or current l/h",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "shorterm bad slope -> exit market"
        },
        "indicators": ["PivotHighVS / PivotLowVS (swing detection)", "SW_LowBar / SW_HighBar (bar index of last swing)", "Highest/Lowest over dynamic range"],
        "time_filter": ["0845", "0500", "sess1endtime-barinterval"],
        "key_logic": "Pivot Swing: PivotHighVS/PivotLowVS detect structural swing points; LE2/SE2 extends entry stop to cover full range from last swing bar (Barnumber-SW_LowBar[2] lookback); stop trails to latest swing low/high reference; slope filter on short-term pivot sequence for exit",
        "tags": ["breakout", "day-trade", "pivot-swing", "PivotHighVS"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4)BN_TX_2109_IslandReverse PLE.md",
        "strategy_id": "c40BN_TX_IslandReverseAndDoubleGap_LO_100k_v2",
        "classification": "Trend Following / Breakout",
        "direction": "both",
        "timeframe": "unknown",
        "entry_logic": {
            "long": "basic: gapbar[1]-gapbar[2]<pp AND abs(gap[1]+gap[2])<avg(TR,3)*pp2/100 -> market or stop at h; re-entry: mp changed to positive AND gapbar[1]<>gapbar[2] -> stop at stopB; double gap: mp>0 AND barssinceentry>3 -> stop at highest(h,kday)",
            "short": "basic: condition10 AND gap[2]<0 -> market; win then lose: posprofit>0 AND openprofit<0 -> stop at l; double gap short: stop at lowest(l,kday)"
        },
        "exit_logic": {
            "stop_loss": "stop at stopB/stopS",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "double gap exit when gap[1] reverses sign"
        },
        "indicators": ["SMA (avg TrueRange)", "Highest/Lowest", "gapbar[] array (tracks gap occurrence bar)", "gap[] array (gap size)"],
        "time_filter": None,
        "key_logic": "Island Reversal + Double Gap: tracks two consecutive gaps in gapbar/gap arrays; island = two gaps close together (pp bars apart) with canceling sizes (abs sum < ATR threshold); enter on island confirmation; double-gap follow-through adds position at kday-high breakout; exit when gap series reverses polarity",
        "tags": ["MA", "breakout", "trend", "island-reversal", "gap-pattern"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4)BN_TX_2109_orbplus_DO_4k_v2.md",
        "strategy_id": "a40BN_TX_ORB_DO_4k_v2",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "intraday bar-interval dependent",
        "entry_logic": {
            "long": "Basic Buy: EntriesToday=0 AND k>in AND t<=1200 AND mp=0 -> stop at highd(0)-avg(TrueRange,k); Reverse Buy: h<avg(iff(maxDTR<diff,l,h),k) -> stop at highest(h,barssinceentry)",
            "short": "Basic Short: stop at lowd(0)+avg(TrueRange,k); Reverse Short: mp<>0 AND barssinceentry>3 -> stop at lowest(l,barssinceentry)"
        },
        "exit_logic": {
            "stop_loss": "fixed at entryprice - diff*gg",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "Day Exit Sell/Cover market"
        },
        "indicators": ["SMA", "Highest/Lowest", "TrueRange (ATR k-period)", "DTrueRange_BN (daily true range function)", "Daily High/Low/Close"],
        "time_filter": ["1200", "1100", "sess1endtime-2*barinterval", "1320"],
        "key_logic": "ORB Plus DO 4k: entry at highd-ATR(k) = slightly inside daily high, not at exact breakout (reduces false entry); condition10: avg(l,k)>(2*closed(1)+highd(1))/3 as trend filter using prior day weighted level; reverse entry after 3+ bars uses highestbar range; diff*gg as range-proportional stop",
        "tags": ["MA", "breakout", "day-trade", "ORB", "ATR-entry"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4)CB_HW_2201_Bignose_TX_3SameBar_DO_6k.md",
        "strategy_id": "f40CB_HW_2201_Bignose_TX_3SameBar_DO_6k",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "intraday bar-interval dependent",
        "entry_logic": {
            "long": "t>=sess1firstbartime+3*barinterval AND t<=iff(lastloss<0,1100,1300) AND EntriesToday<2 AND condition6 -> market; condition11 AND countif(cond12,3)=3 -> stop at (h*2+l)/3",
            "short": "same window -> stop at (h+l*2)/3; c-l[2]>DATR*OverRatio2 AND highd>=highw -> market (weekly extreme short)"
        },
        "exit_logic": {
            "stop_loss": "SetStopLoss(DATR(3))",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "Day over sell/cover; Lastday over sell"
        },
        "indicators": ["SMA (avg c)", "Daily High/Low/Close", "CountIf (3-bar momentum)", "DATR (daily ATR function)", "Weekly High (highw)"],
        "time_filter": ["sess1endtime-barinterval"],
        "key_logic": "3SameBar Bignose: entry window shrinks from 1300 to 1100 after a loss day (protective); 3-consecutive-bar pattern (countif(cond12,3)=3) for momentum confirmation; DATR(3) as dynamic stop; highd>=highw triggers aggressive short when today reaches weekly high; entry offset 3 bars from open avoids opening whipsaw",
        "tags": ["MA", "day-trade", "3-bar-pattern", "DATR", "weekly-filter"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4)coke777_TX_0921_LT策略腳本.md",
        "strategy_id": "a3777_coke777",
        "classification": "Swing / Long-Term",
        "direction": "both",
        "timeframe": "unknown",
        "entry_logic": {
            "long": "mp=0 AND EntriesToday=0 AND ExitsToday=0 -> market (fresh day only); last trade day AND t>=1330 -> market",
            "short": "arrRed[0] AND arrRed[1] AND opend(0)>opend(1) -> market (2 red bars + rising open); last trade day AND t>=1330 -> market"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "timeoutB/fullB/cutB exits"
        },
        "indicators": ["arrRed[] (red bar array tracker)", "Daily Open/High/Low/Close", "value1=(maxlist(opend,closeD)*2+highd)/3 pivot", "value2=(minlist(opend,closeD)*2+lowd)/3 pivot"],
        "time_filter": ["1330"],
        "key_logic": "coke777 swing: long only on completely fresh day (no prior entries or exits = no reversals); short triggered by 2 consecutive red bars with rising open (continuation bearish pressure); OHLC pivot values value1/value2 as open gap direction filter; expiry day forced exit at 1330",
        "tags": ["swing", "open-gap", "red-bar-pattern"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4)Ivan2109_TX_DV6k_DT.md",
        "strategy_id": "Ivan2109_TX_DV6k_DT",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "intraday bar-interval dependent",
        "entry_logic": {
            "long": "CT_L: t=sess1firstbartime -> stop at AmOpend; T_L: AmOpend+avg(h-l,300/barinterval*3)<AmClosed[1] -> stop at AmOpend; BH_B: DayVolatility(3,20)<-(2/3)*DayVol(3,31) AND retrace -> stop",
            "short": "CT_S: first bar -> stop at AmOpend; T_S: k>in AND t<1320 -> stop at AmOpend; BH_S: low vol regime -> stop"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "LTO/STO market; highest(C,k-barssinceentry+3)+2*k stop trail"
        },
        "indicators": ["SMA (avg h-l range)", "Highest/Lowest (trailing)", "DayVolatility(3,20) vs DayVolatility(3,31) ratio"],
        "time_filter": ["<0900", "<1320", "<1500"],
        "key_logger": "DV 6k: DayVolatility ratio 20-day vs 31-day as regime filter; negative ratio = vol contracting = BH entries trigger; AmOpend as anchor for all stop entries; 3-session average range (300/barinterval*3) as amplitude filter for T_L entry; trailing highest/lowest exit",
        "tags": ["MA", "breakout", "day-trade", "volatility-filter", "AmOpen-anchor"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4)NV002_TX30M_SR_FLT.md",
        "strategy_id": "NV002_TX30M_SR_FLT",
        "classification": "Trend Following / Breakout",
        "direction": "both",
        "timeframe": "unknown",
        "entry_logic": {
            "long": "RL: C cross over AvgL (avg of Low) -> stop; TL: Resistance>Resistance[1] (new resistance high) -> stop",
            "short": "RS: C cross under AvgH -> stop; TS: Support<Support[1] (new support low) -> stop"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "RL-Profit: from RL entry -> sell limit at Resistance; RS-Profit: from RS entry -> buytocover limit at Support"
        },
        "indicators": ["SMA (AvgL=avg(Low,Length), AvgH=avg(High,Length))", "Resistance = Highest(C,Length) updated on AvgH cross", "Support = Lowest(C,Length) updated on AvgL cross"],
        "time_filter": None,
        "key_logic": "S/R Trend FLT: dynamic S/R updated on MA cross events; RL entry when price crosses AvgLow (bullish); TL when resistance makes new high (trend continuation); profit exits at opposing dynamic level; two entry types per direction (cross-based vs level-extension)",
        "tags": ["MA", "breakout", "trend", "support-resistance"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4)NV2107003_TX3M_Amy_FDT.md",
        "strategy_id": "NV2107003_TX3M_Amy_FDT",
        "classification": "Trend Following",
        "direction": "both",
        "timeframe": "intraday bar-interval dependent",
        "entry_logic": {
            "long": "condition23 (AvgWeight>0) AND (condition21 OR condition22) AND AvgPrice>(highada(1)*2+closeada(1))/3 -> L1 stop",
            "short": "same conditions -> S1 stop"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "Lclose/Sclose next bar market"
        },
        "indicators": ["weight = countif(C>O,k)-countif(C<O,k) + countif(C>C[1],k)-countif(C<C[1],k)", "Average(weight,Len) as AvgWeight", "AvgPrice (OHLC/4)", "ADA high/close levels"],
        "time_filter": ["1345", "0500", "1300", "0300"],
        "key_logic": "Amy FDT: weight scoring system counting net green bars and net up closes over k bars; AvgWeight>0 = net bullish score (condition23); AvgPrice vs ADA weighted pivot as directional filter; dual session (AM<1300, night<0300) with different endpoints; 3m timeframe focus",
        "tags": ["MA", "trend", "bar-scoring", "weight-system"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4)NV2108004_TX15M_Bonny_LT.md",
        "strategy_id": "NV2108004_TX15M_Bonny_DT",
        "classification": "Swing / Long-Term",
        "direction": "both",
        "timeframe": "intraday bar-interval dependent",
        "entry_logic": {
            "long": "d=LastTradeDay(D) AND sessionlastbar -> market (expiry settlement only)",
            "short": "d=LastTradeDay(D) AND sessionlastbar -> market"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": None
        },
        "indicators": ["SMA (avg H-L range)", "Highest(h,60/barinterval) vs highd(0)", "Lowest(L,60/barinterval) vs lowd(0)", "HH[]/LL[]/CC[] arrays of daily extremes", "Highest_a/Lowest_a (array-based peak detection)"],
        "time_filter": None,
        "key_logic": "Bonny 15m: complex multi-day array tracking HH/LL/CC; 60-min rolling high/low vs daily extremes for intraday trend; vHH/vLL = Highest_a/Lowest_a over Len days for longer-term trend; entry ONLY at expiry day last bar = settlement-price play; likely a hedge or settlement arbitrage",
        "tags": ["MA", "breakout", "swing", "expiry-day", "array-tracking"]
    },
    {
        "batch": 11,
        "file": "E:/投資交易/pla_md/logic/(4)NV2109005_TX6M_Cindy_LT -original.md",
        "strategy_id": "NV2109005_TX6M_Cindy_LT_original",
        "classification": "Swing / Long-Term",
        "direction": "both",
        "timeframe": "intraday bar-interval dependent",
        "entry_logic": {
            "long": "B1: d=exitdate(1) AND vmp=0 AND vmp[1]<0 -> stop (re-entry day after short exit); B2: DS=0 AND c<minlist(closed(1),dn) AND not ShortExit -> stop; B3: DS=0 AND lowd(0)>up AND c<o -> stop (fake breakout above pivot, reversal)",
            "short": "S1: EntriesToday<=1 AND condition40 -> stop; S2: k>in AND not sessionlastbar -> stop; S3: k>in AND (prior S1) -> stop (second short confirmation)"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "condition31=false -> RL-Run sell; condition32=false -> RS-Run cover (trend momentum lost)"
        },
        "indicators": ["HLC/3 pivot: mid=HLC/3, up=mid*2-L, dn=mid*2-H", "gap=up-dn (daily pivot range)", "DS (direction state flag)", "countif(c<c[1],k) for trend counting", "vmp (virtual market position)"],
        "time_filter": ["sess1endtime-barinterval"],
        "key_logic": "Cindy original 6m: pivot-based (HLC/3) with DS state machine; B1 re-entry on day after short exit (mean-reversion); B2 pullback below dn level; B3 fake-breakout reversal (low opens above up band but close<open = rejection); S1-S3 progressive short confirmation; countif-weighted entry level adjustment",
        "tags": ["breakout", "swing", "CDP-pivot", "re-entry", "fake-breakout", "state-machine"]
    }
]

output_path = "C:/Users/admin/workspace/digital-immortality/results/digestion_log.jsonl"
with open(output_path, "a", encoding="utf-8") as f:
    for rec in records:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

print(f"Appended {len(records)} records to {output_path}")
