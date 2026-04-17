import json

entries = [
    {
        "source": "E:/投資交易/pla_md/logic/047_TXI_Correlation Trend_DO.md",
        "strategy_name": "b3047_TXI_Correlation_Trend_DO",
        "classification": "Day Trading",
        "direction": "Both",
        "timeframe": "unknown",
        "entry_logic": {
            "long": "dentry<1 AND k>1 AND k<23 AND mp=0 AND flagM=0 -> stop order at Highada(0)",
            "short": "dentry<1 AND k>1 AND k<23 AND mp=0 AND flagM=0 -> stop order at Lowada(0)"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "sell('maxEL') next bar market; if mp>0 and barssinceentry>=k/3 and Highest(h,barssinceentry)<Highest(h,barssinceentry+1) then sell('LX2'); if mp>0 and c<entryprice then sell('PM_LX')"
        },
        "indicators": ["Highest", "Lowest"],
        "time_filters": ["t>=1344", "t<1500", "t>0426", "t<0500"],
        "tags": ["breakout", "day-trade", "correlation"],
        "notes": "Correlation trend: dentry<1 and k in [1,23]; adaptive high/low (Highada/Lowada) for entry stops; exit on peak fade (highest<previous highest); covers both day and pre-market windows"
    },
    {
        "source": "E:/投資交易/pla_md/logic/0528.md",
        "strategy_name": "nob20may_1_1h",
        "classification": "Breakout",
        "direction": "Both",
        "timeframe": "unknown",
        "entry_logic": {
            "long": "mp=0 AND close>var2 -> buy stop at highest(h,3)",
            "short": "mp=0 AND close<var3 -> sellshort stop at lowest(l,3)"
        },
        "exit_logic": {
            "stop_loss": "SetStopLoss(x1*200)",
            "profit_target": "SetProfitTarget(y1*200)",
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": None
        },
        "indicators": ["Highest(h,3)", "Lowest(l,3)", "ATR(5)", "Daily Open", "Daily Close"],
        "time_filters": [],
        "tags": ["ATR", "breakout"],
        "notes": "var2/var3 = ATR(5)*0.02*var1 offset bands; condition1 uses opend>closed[1] and spread and weekly midpoint filter; SL/PT from dynamic ATR bands scaled by x1/y1"
    },
    {
        "source": "E:/投資交易/pla_md/logic/053_TX_NBY_DO.md",
        "strategy_name": "a3053_NBY_DO",
        "classification": "Day Trading",
        "direction": "Both",
        "timeframe": "5m",
        "entry_logic": {
            "long": "[B-1] based on AvgPrice range condition (highest-lowest > DayAvg*Avgratio)",
            "short": "[S-1] based on AvgPrice range condition"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "if mp>0 then sell('Nature B-SL') next bar; sell('LEnd1') all contracts next bar market; if mp<0 then buytocover('Nature S-SL') next bar"
        },
        "indicators": ["Highest", "Lowest", "AvgPrice(OHLC/4)", "CountIf"],
        "time_filters": ["calctime(sess1firstbartime,barinterval)", "calctime(sess1endtime,-1*barinterval)"],
        "tags": ["5m", "breakout", "day-trade", "nature-SL"],
        "notes": "NBY=nature-based Y; tracks AvgHigh/AvgLow from AvgPrice; entry when range expands past DayAvg*Avgratio; nature stop: exit when avg price reverts; countif condition3 for secondary exit"
    },
    {
        "source": "E:/投資交易/pla_md/logic/053_TX_NBY_DO (2).md",
        "strategy_name": "a3053_NBY_DO",
        "classification": "Day Trading",
        "direction": "Both",
        "timeframe": "5m",
        "entry_logic": {"long": "same as 053_TX_NBY_DO.md", "short": "same as 053_TX_NBY_DO.md"},
        "exit_logic": {"stop_loss": None, "profit_target": None, "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": "nature stop signals"},
        "indicators": ["Highest", "Lowest", "AvgPrice", "CountIf"],
        "time_filters": [],
        "tags": ["5m", "day-trade", "duplicate"],
        "notes": "Duplicate of 053_TX_NBY_DO.md"
    },
    {
        "source": "E:/投資交易/pla_md/logic/0530.md",
        "strategy_name": "no2",
        "classification": "Trend Following",
        "direction": "Both",
        "timeframe": "unknown",
        "entry_logic": {
            "long": "value8>bv AND value1>value1[1] -> stop order at upband",
            "short": "value8>bv AND value1>value1[1] -> stop order at dnband"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": None,
            "signal_exit": "sell THIS BAR on close; buytocover THIS BAR on close"
        },
        "indicators": ["MA(SMA of (h+l+c)/3)", "ATR"],
        "time_filters": ["time>1319", "DayOfWeek filter", "holiday dates 1040127/1070226/1100617"],
        "tags": ["ATR", "MA", "trend", "channel-breakout"],
        "notes": "ATR channel: upband=SMA((h+l+c)/3,len)+w*ATR; dnband=SMA-w*ATR; value8 as volatility threshold; close-on-bar exit only; holiday exclusions encoded"
    },
    {
        "source": "E:/投資交易/pla_md/logic/059_TXI_CLOSED_LO.md",
        "strategy_name": "a3059_TXI_CLOSED_LO",
        "classification": "Trend Following",
        "direction": "Both",
        "timeframe": "unknown",
        "entry_logic": {
            "long": "mp=0 AND Daytradetime=0 AND (t>=0845 OR t<=0300) AND dcount>IFF(positionprofit(1)<0,in*2,in) -> stop at IFF(profit>0, Highada(0)+Avg(|c-o|,k), Highada(0)-Avg(|c-o|,k))",
            "short": "same structure -> stop at Lowada variant"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "sell('LX') next bar market; sell('maxLX') next bar market; buytocover('SX') next bar market"
        },
        "indicators": ["MA(SMA)", "Range(H-L)"],
        "time_filters": ["t>=0845", "t<=0300"],
        "tags": ["MA", "trend", "overnight", "adaptive-entry", "conditional-re-entry"],
        "notes": "CLOSED_LO=closed overnight long; dcount threshold doubles to in*2 after losing trade; entry level: winning extends farther (Highada+Avg(|c-o|,k)), losing pulls back; covers overnight t<=0300 and morning t>=0845; 4 duplicate files total"
    },
    {
        "source": "E:/投資交易/pla_md/logic/059_TXI_CLOSED_LO (2).md",
        "strategy_name": "a3059_TXI_CLOSED_LO",
        "classification": "Trend Following",
        "direction": "Both",
        "timeframe": "unknown",
        "entry_logic": {"long": "same as 059 canonical", "short": "same as 059 canonical"},
        "exit_logic": {"stop_loss": None, "profit_target": None, "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": "market exits"},
        "indicators": ["MA(SMA)", "Range(H-L)"],
        "time_filters": ["t>=0845", "t<=0300"],
        "tags": ["MA", "trend", "overnight", "duplicate"],
        "notes": "Duplicate of 059_TXI_CLOSED_LO.md"
    },
    {
        "source": "E:/投資交易/pla_md/logic/059_TXI_CLOSED_LO (3).md",
        "strategy_name": "a3059_TXI_CLOSED_LO",
        "classification": "Trend Following",
        "direction": "Both",
        "timeframe": "unknown",
        "entry_logic": {"long": "same as 059 canonical", "short": "same as 059 canonical"},
        "exit_logic": {"stop_loss": None, "profit_target": None, "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": "market exits"},
        "indicators": ["MA(SMA)", "Range(H-L)"],
        "time_filters": ["t>=0845", "t<=0300"],
        "tags": ["MA", "trend", "overnight", "duplicate"],
        "notes": "Duplicate of 059_TXI_CLOSED_LO.md"
    },
    {
        "source": "E:/投資交易/pla_md/logic/059_TXI_CLOSED_LO (4).md",
        "strategy_name": "a3059_TXI_CLOSED_LO",
        "classification": "Trend Following",
        "direction": "Both",
        "timeframe": "unknown",
        "entry_logic": {"long": "same as 059 canonical", "short": "same as 059 canonical"},
        "exit_logic": {"stop_loss": None, "profit_target": None, "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": "market exits"},
        "indicators": ["MA(SMA)", "Range(H-L)"],
        "time_filters": ["t>=0845", "t<=0300"],
        "tags": ["MA", "trend", "overnight", "duplicate"],
        "notes": "Duplicate of 059_TXI_CLOSED_LO.md"
    },
    {
        "source": "E:/投資交易/pla_md/logic/060_Hsiang_TXA_Q5_R_10min_FLT.md",
        "strategy_name": "b3060_Hsiang_TXA_Q5_R_10min_FLT",
        "classification": "Breakout",
        "direction": "Both",
        "timeframe": "10m",
        "entry_logic": {
            "long": "mp=0 AND dentry<=0 -> buy stop at Amhighd_TX(0)",
            "short": "L<maxlist(amclosed_TX(0),amclosed_TX(1))-ratio*avggap AND consecutive lower-low acceleration AND HIGHEST(H,N1)<HIGHEST(H,N1)[N1] -> sellshort stop at Amlowd_TX(0)"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": None,
            "signal_exit": "if AmOpend_TX(0)<Amlowd_TX(1) and t>=0930 and c<AmOpend_TX(0) then sell('SO1W'); if c<entryprice-200 then sell('SO2W'); if countif(C<entryprice-1,LENGTH)>=0.8*LENGTH then sell('SO3'); sell('TimeOut-L') all shares this bar at close"
        },
        "indicators": ["Highest(H,N1)", "Lowest(L,N1)", "CountIf"],
        "time_filters": ["t>=0930", "time>=1320"],
        "tags": ["10m", "breakout", "Hsiang", "AM-session", "persistence-exit"],
        "notes": "Hsiang series; AM adapted high/low (Amhighd/Amlowd); short requires consecutive lower-low acceleration + HIGHEST fade; SO3 exit: if 80% of LENGTH bars below entry-1 (persistent weakness); 2 duplicate files"
    },
    {
        "source": "E:/投資交易/pla_md/logic/060_Hsiang_TXA_Q5_R_10min_FLT (2).md",
        "strategy_name": "b3060_Hsiang_TXA_Q5_R_10min_FLT",
        "classification": "Breakout",
        "direction": "Both",
        "timeframe": "10m",
        "entry_logic": {"long": "same as 060 canonical", "short": "same as 060 canonical"},
        "exit_logic": {"stop_loss": None, "profit_target": None, "trailing_stop": None, "time_exit": None, "signal_exit": "same as 060 canonical"},
        "indicators": ["Highest", "Lowest", "CountIf"],
        "time_filters": ["t>=0930", "time>=1320"],
        "tags": ["10m", "breakout", "Hsiang", "duplicate"],
        "notes": "Duplicate of 060_Hsiang_TXA_Q5_R_10min_FLT.md"
    },
    {
        "source": "E:/投資交易/pla_md/logic/0629.md",
        "strategy_name": "AA02",
        "classification": "Trend Following",
        "direction": "Both",
        "timeframe": "unknown",
        "entry_logic": {
            "long": "value1[0]>value1[1] AND value1[1]>value1[2] AND value1[2]>value1[3] -> buy market",
            "short": "value1[0]<value1[1] AND value1[1]<value1[2] AND value1[2]<value1[3] -> sellshort market"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": None,
            "signal_exit": "sell('Exitbuy1') THIS BAR on close; buytocover('Exitshort1') THIS BAR on close"
        },
        "indicators": [],
        "time_filters": ["time>1314", "DayOfWeek filter", "holiday exclusions"],
        "tags": ["momentum", "trend", "consecutive-bars"],
        "notes": "Simple 3-bar consecutive momentum: 4-bar monotone increasing/decreasing value1; exit on close same bar (very short hold); holiday exclusion list"
    },
    {
        "source": "E:/投資交易/pla_md/logic/064_TXA_HLGAPBC_LO_20min.md",
        "strategy_name": "d3064_TXA_HLGAPBC_LO_20min",
        "classification": "Breakout",
        "direction": "Both",
        "timeframe": "unknown",
        "entry_logic": {
            "long": "dentry<=0 -> stop order at h",
            "short": "HIGHADA(1)<MAXLIST(HIGHADA(1),HIGHADA(2))-ratio*avggap AND HIGHEST(H,N1)<LOWEST(L,N1)[1.5*N1] AND lowest acceleration AND range contraction -> stop order at l"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "if c<entryprice-maxlist(opend(0)*0.02) then SELL next bar; if c>entryprice+maxlist(opend(0)*0.02) then buytocover; sell/buytocover('End_sell') next bar"
        },
        "indicators": ["Highest", "Lowest", "Daily Open"],
        "time_filters": ["t>=1310"],
        "tags": ["breakout", "gap", "HL-gap", "range-contraction", "compression"],
        "notes": "HLGAPBC=HL gap bar count; short requires: ada-high gap below prior AND full range below prior low AND lower-low acceleration AND range contraction (classic squeeze); loss exit at 2% of opend (dynamic SL); compression-then-extension concept"
    },
    {
        "source": "E:/投資交易/pla_md/logic/064_TXI_ORB_LO.md",
        "strategy_name": "a3064_TXI_ORB_LO",
        "classification": "Breakout",
        "direction": "Both",
        "timeframe": "intraday (bar-interval dependent)",
        "entry_logic": {
            "long": "mp=0 AND (time>calctime(0845,in*barinterval) OR time<0300) -> stop at Amhighd_TX(0)",
            "short": "mp=0 AND (time>calctime(0845,in*barinterval) OR time<0300) -> stop at Amlowd_TX(0)"
        },
        "exit_logic": {
            "stop_loss": "entryprice-opend(0)/10000*stp (long); entryprice+opend(0)/10000*stp (short)",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "sell('Exit 4 L') / buytocover('Exit 4 S') next bar market; exit2: avgprice breaks highest/lowest(avgprice,2)"
        },
        "indicators": ["Highest", "Lowest", "AvgPrice"],
        "time_filters": ["time<0300 (overnight)", "calctime(0845,in*barinterval)"],
        "tags": ["breakout", "ORB", "open-range-breakout", "overnight", "percentage-SL"],
        "notes": "ORB=Open Range Breakout; AM adapted extremes as entry; SL=entryprice*(stp/10000) pct of open; avgprice pivot exit (Exit 2); covers overnight t<0300 and morning after n bars; stf trailing parameter"
    },
    {
        "source": "E:/投資交易/pla_md/logic/0704.md",
        "strategy_name": "no110a2d2",
        "classification": "Breakout",
        "direction": "Both",
        "timeframe": "unknown",
        "entry_logic": {
            "long": "BeginTime<Time AND Time<EndTime -> stop at highest(high,3)",
            "short": "BeginTime<Time AND Time<EndTime -> stop at lowest(low,3)"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": "sell('BSL1') next bar at entryprice*(1+sp) limit",
            "trailing_stop": None,
            "time_exit": None,
            "signal_exit": "if high-entryprice>pr and value3<0 then sell this bar on close; sell THIS BAR on close"
        },
        "indicators": ["Highest(high,3)", "Lowest(low,3)"],
        "time_filters": ["time>1314", "DayOfWeek filter", "holiday dates"],
        "tags": ["breakout", "3-bar-high-low", "limit-profit"],
        "notes": "Simple 3-bar high/low stop entry in time window; limit profit at entry*(1+sp); signal exit: if gain>pr AND momentum indicator value3<0; holiday exclusion list"
    },
    {
        "source": "E:/投資交易/pla_md/logic/09042.md",
        "strategy_name": "J_Qindicator3_13min_LT",
        "classification": "Trend Following / Breakout",
        "direction": "Both",
        "timeframe": "13m",
        "entry_logic": {
            "long": "d<>LastTradeDay AND NOT _afterSettThurs AND mp=0 -> stop at highest(h,3); re-entry [RE L]: mp>0 AND barssinceentry<=60 AND Qindicator<0 AND not already RE -> market",
            "short": "d<>LastTradeDay AND NOT _afterSettThurs AND mp=0 -> stop at lowest(l,3); re-entry [RE S] market"
        },
        "exit_logic": {
            "stop_loss": "Stop at minlist(Lowd(0),lowd(1)) for long; maxlist(highd(0),highd(1)) for short",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "if mp>0 and maxlist(highd(0),highd(1))<highd(3) and entd>3 then sell('L11'); if mp<0 and minlist(lowd(0),lowd(1))<lowd(3) and entd>3 then buytocover('S22')"
        },
        "indicators": ["MA(SMA)", "Highest(h,3)", "Lowest(l,3)", "Daily High/Low", "Summation(C-C[1],3)", "Deviation from mean"],
        "time_filters": ["t<1330"],
        "tags": ["13m", "MA", "breakout", "trend", "Qindicator", "re-entry", "averaging-down"],
        "notes": "Qindicator=summation(C-C[1],3)/deviation from average; excludes settlement Thursday; stop at running daily extremes; re-entry when Qindicator<0 within 60 bars; exit when daily range narrows vs 3 days ago (momentum waning); 2 duplicate files"
    },
    {
        "source": "E:/投資交易/pla_md/logic/09042 (2).md",
        "strategy_name": "J_Qindicator3_13min_LT",
        "classification": "Trend Following / Breakout",
        "direction": "Both",
        "timeframe": "13m",
        "entry_logic": {"long": "same as 09042.md", "short": "same as 09042.md"},
        "exit_logic": {"stop_loss": "Daily extremes", "profit_target": None, "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": "same as 09042.md"},
        "indicators": ["MA(SMA)", "Highest", "Lowest", "Daily High/Low", "Summation"],
        "time_filters": ["t<1330"],
        "tags": ["13m", "MA", "breakout", "trend", "duplicate"],
        "notes": "Duplicate of 09042.md"
    },
    {
        "source": "E:/投資交易/pla_md/logic/092_vwap_3k_DT.md",
        "strategy_name": "b3092_VWAP_3k_DT_v2",
        "classification": "Day Trading",
        "direction": "Both",
        "timeframe": "intraday (bar-interval dependent)",
        "entry_logic": {
            "long": "condition99 AND EntriesToday<1 AND t<=1100 -> stop at highest(H,5); [L burst in]: Trendbull AND countif(avgprice>midline,3)>=2 AND condition1 -> market; [reverse B]: mp>0 AND barssinceentry>=10 AND DentryL+dentrys<=1 AND t<1200 -> market",
            "short": "condition99 AND EntriesToday<1 AND t<=1100 -> stop at lowest(L,5); [S burst in] / [reverse S] similar"
        },
        "exit_logic": {
            "stop_loss": "entryprice+win_pts*0.8+barssinceentry (time-expanding); Sstop+Avg(H-L,k)-0.3*barssinceentry",
            "profit_target": "entryprice+win_pts*0.8+barssinceentry (symmetric)",
            "trailing_stop": None,
            "time_exit": "SetExitOnClose; sell('Time out L') at session end time",
            "signal_exit": "sell this bar at close on early exit"
        },
        "indicators": ["MA(SMA)", "Highest(H,5)", "Lowest(L,5)", "AvgPrice", "Daily OHLC", "CountIf"],
        "time_filters": ["t<=1100", "t<1200", "t>=1200", "time=1330"],
        "tags": ["VWAP", "MA", "breakout", "day-trade", "midline", "burst-entry", "time-adaptive-SL"],
        "notes": "VWAP midline: Trendbull=countif(c>=midline,k)>=ratio*k; SL/PT both expand with barssinceentry (time-adaptive risk); condition1=openD>avgD; burst entry on VWAP reclaim; reverse entry after 10 bars if only 1 entry; 3k=capital unit reference"
    },
    {
        "source": "E:/投資交易/pla_md/logic/1_策略_@SW_008_2021_06_TXF_open gate trend_DT.md",
        "strategy_name": "b40SW_008_open_gate_trend_DT",
        "classification": "Day Trading",
        "direction": "Both",
        "timeframe": "intraday (bar-interval dependent)",
        "entry_logic": {
            "long": "t>=0845 AND t<1200 AND EntriesToday<1 -> stop at h[k-1]+0.25*|lowd(1)-closed(1)|; [B3]: condition31 AND (cond11 OR cond12) -> market",
            "short": "t>=0845 AND t<1200 AND EntriesToday<1 -> stop at l[k-1]-0.25*|highd(1)-closed(1)|; [B4]: condition30 AND (cond21 OR cond22) -> market"
        },
        "exit_logic": {
            "stop_loss": "Fixed at entryprice-stl / entryprice+stl",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "if barssinceentry>8 and countif(c<entryprice,barssinceentry)>=0.5*barssinceentry then sell('S3'); sell next bar market"
        },
        "indicators": ["Daily Open/High/Low/Close", "CountIf"],
        "time_filters": ["t>=0845", "t<1200"],
        "tags": ["TX", "day-trade", "open-range", "gate", "SW-series", "gap-condition"],
        "notes": "SW_008 open gate trend; condition30=opend>highd(1)-0.25*(highd(1)-closed(1)) (gap into upper 25% of prev day); condition31=opend<lowd(1)+0.25*(closed(1)-lowd(1)) (gap into lower 25%); persistence exit: 50% of elapsed bars below entry; k-bar offset stop; 4 duplicate files"
    },
    {
        "source": "E:/投資交易/pla_md/logic/1_策略_@SW_008_2021_06_TXF_open gate trend_DT (2).md",
        "strategy_name": "b40SW_008_open_gate_trend_DT",
        "classification": "Day Trading",
        "direction": "Both",
        "timeframe": "intraday",
        "entry_logic": {"long": "same as SW_008 canonical", "short": "same as SW_008 canonical"},
        "exit_logic": {"stop_loss": "Fixed stl", "profit_target": None, "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": "persistence exit"},
        "indicators": ["Daily OHLC", "CountIf"],
        "time_filters": ["t>=0845", "t<1200"],
        "tags": ["TX", "day-trade", "SW-series", "duplicate"],
        "notes": "Duplicate of SW_008 canonical"
    },
    {
        "source": "E:/投資交易/pla_md/logic/1_策略_@SW_008_2021_06_TXF_open gate trend_DT (3).md",
        "strategy_name": "b40SW_008_open_gate_trend_DT",
        "classification": "Day Trading",
        "direction": "Both",
        "timeframe": "intraday",
        "entry_logic": {"long": "same as SW_008 canonical", "short": "same as SW_008 canonical"},
        "exit_logic": {"stop_loss": "Fixed stl", "profit_target": None, "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": "persistence exit"},
        "indicators": ["Daily OHLC", "CountIf"],
        "time_filters": ["t>=0845", "t<1200"],
        "tags": ["TX", "day-trade", "SW-series", "duplicate"],
        "notes": "Duplicate of SW_008 canonical"
    },
    {
        "source": "E:/投資交易/pla_md/logic/1_策略_@SW_008_2021_06_TXF_open gate trend_DT (4).md",
        "strategy_name": "b40SW_008_open_gate_trend_DT",
        "classification": "Day Trading",
        "direction": "Both",
        "timeframe": "intraday",
        "entry_logic": {"long": "same as SW_008 canonical", "short": "same as SW_008 canonical"},
        "exit_logic": {"stop_loss": "Fixed stl", "profit_target": None, "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": "persistence exit"},
        "indicators": ["Daily OHLC", "CountIf"],
        "time_filters": ["t>=0845", "t<1200"],
        "tags": ["TX", "day-trade", "SW-series", "duplicate"],
        "notes": "Duplicate of SW_008 canonical"
    },
    {
        "source": "E:/投資交易/pla_md/logic/1_策略_@SW_009_2021_08_TXF_CO propotion of HL_FLT.md",
        "strategy_name": "a40SW_009_CO_proportion_HL_FLT",
        "classification": "Breakout",
        "direction": "Both",
        "timeframe": "intraday (bar-interval dependent)",
        "entry_logic": {
            "long": "LastTradeDay(d)<>d AND EntriesToday=0 -> stop at highest(h,2)",
            "short": "LastTradeDay(d)<>d AND EntriesToday=0 -> stop at lowest(l,2)"
        },
        "exit_logic": {
            "stop_loss": "entryprice-(stl/value1) long; _EntryH-0.5*stp alternate",
            "profit_target": "_EntryH-0.5*stp / _EntryL+0.5*stp",
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "early_out_S1: if H<L[barssinceentry*2] and C<C[barssinceentry] then sell; if value1>n and c<entryprice then sell('S5')"
        },
        "indicators": ["Highest(h,2)", "Lowest(l,2)"],
        "time_filters": [],
        "tags": ["TX", "breakout", "CO-proportion", "HL-filter", "SW-series"],
        "notes": "SW_009; value1=CO proportion of HL range (close-open/high-low); SL normalized by value1; early_out: current H below L[2x bars ago] AND close deteriorated = early reversal; value1>n filter for adequate bar range"
    },
    {
        "source": "E:/投資交易/pla_md/logic/1_策略_@SW_010_2021_09_TXF_kbar ratio_DT.md",
        "strategy_name": "c40SW_010_kbar_ratio_DT",
        "classification": "Day Trading",
        "direction": "Both",
        "timeframe": "intraday (bar-interval dependent)",
        "entry_logic": {
            "long": "k>5 AND k<=85 AND EntriesToday=0 -> stop at average(h,k); [B3]: condition20 AND condition21 -> market",
            "short": "k>5 AND k<=85 AND EntriesToday=0 -> stop at average(l,k); [B4] market"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose; sell('timeout_B'/'timeout_S') next bar market",
            "signal_exit": "sell('S3') on condition31 (avgprice breaks)"
        },
        "indicators": ["MA(average h/l,k)", "Highest(c,k)", "Lowest(c,k)", "AvgPrice"],
        "time_filters": ["calctime(sess1endtime,-barinterval)"],
        "tags": ["MA", "TX", "breakout", "day-trade", "kbar-ratio", "SW-series"],
        "notes": "SW_010; entry at average(h,k) stop (MA of highs); HighT=bar position where c=highest(c,k); LowT=bar where c=lowest(c,k); cond11=HighT>LowT (high came after low=uptrend in K bars); cond21=LowT>HighT (downtrend); avgprice pivot S3 exit; 2 duplicate files"
    },
    {
        "source": "E:/投資交易/pla_md/logic/1_策略_@SW_010_2021_09_TXF_kbar ratio_DT (2).md",
        "strategy_name": "c40SW_010_kbar_ratio_DT",
        "classification": "Day Trading",
        "direction": "Both",
        "timeframe": "intraday",
        "entry_logic": {"long": "same as SW_010 canonical", "short": "same as SW_010 canonical"},
        "exit_logic": {"stop_loss": None, "profit_target": None, "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": "timeout"},
        "indicators": ["MA", "Highest", "Lowest", "AvgPrice"],
        "time_filters": [],
        "tags": ["MA", "TX", "day-trade", "kbar-ratio", "SW-series", "duplicate"],
        "notes": "Duplicate of SW_010 canonical"
    },
    {
        "source": "E:/投資交易/pla_md/logic/1_策略_@SW_011_202109_MA Trend_30m_LT.md",
        "strategy_name": "b40SW_011_MA_Trend_30m_LT",
        "classification": "Swing / Long-Term",
        "direction": "Both",
        "timeframe": "intraday (bar-interval dependent)",
        "entry_logic": {
            "long": "mp=0 AND d<>LastTradeDay AND EntriesToday=0 AND ExitsToday=0 -> stop at highest(h,len/4)",
            "short": "mp=0 AND d<>LastTradeDay AND EntriesToday=0 AND ExitsToday=0 -> stop at lowest(l,len/4)"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "sell('S5') next bar at entryprice*1.1 limit; buytocover('S6') at entryprice*0.9 limit"
        },
        "indicators": ["Highest(h,len/4)", "Lowest(l,len/4)"],
        "time_filters": [],
        "tags": ["breakout", "swing", "MA-trend", "30m", "SW-series", "range-compression"],
        "notes": "SW_011; cond11=highest(h,len/4)==highest(h,len/2) AND lowest(l,len/4)>lowest(l,len/2) = consolidation at top (range compressed in shorter window); cond20=c<mal; exit at +/-10% of entry (wide swing target); 2 duplicate files"
    },
    {
        "source": "E:/投資交易/pla_md/logic/1_策略_@SW_011_202109_MA Trend_30m_LT (2).md",
        "strategy_name": "b40SW_011_MA_Trend_30m_LT",
        "classification": "Swing / Long-Term",
        "direction": "Both",
        "timeframe": "intraday",
        "entry_logic": {"long": "same as SW_011 canonical", "short": "same as SW_011 canonical"},
        "exit_logic": {"stop_loss": None, "profit_target": None, "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": "+/-10% limit exit"},
        "indicators": ["Highest", "Lowest"],
        "time_filters": [],
        "tags": ["breakout", "swing", "SW-series", "duplicate"],
        "notes": "Duplicate of SW_011 canonical"
    },
    {
        "source": "E:/投資交易/pla_md/logic/1_策略_@SW_013_2022_02_TXF_higher_30m_LT.md",
        "strategy_name": "a40SW_013_higher_30m_LT",
        "classification": "Swing / Long-Term",
        "direction": "Both",
        "timeframe": "intraday (bar-interval dependent)",
        "entry_logic": {
            "long": "mp=0 AND LastTradeDay(d)<>d -> market order",
            "short": "mp=0 AND LastTradeDay(d)<>d -> market order"
        },
        "exit_logic": {
            "stop_loss": "entryprice-maxlist(stl*10000, entryprice*stl) = max(fixed, percentage) SL",
            "profit_target": "_EntryH-0.4*win_pts / _EntryL+0.4*win_pts",
            "trailing_stop": None,
            "time_exit": None,
            "signal_exit": "if barssinceentry>30 and c<entryprice then sell('S3'); sell('lastD1') next bar; if barssinceentry>30 and c>entryprice then buytocover('S4')"
        },
        "indicators": ["Highest", "Lowest", "CountIf"],
        "time_filters": [],
        "tags": ["TX", "breakout", "swing", "higher-timeframe", "SW-series", "dual-SL"],
        "notes": "SW_013; market entry on non-settlement day; SL=max(fixed_ticks, pct_of_price) = dual floor SL; cond10=h>highest(h[1],len) and c>o (new high with bullish close); win_pts target at 0.4 multiplier; adverse exit after 30 bars"
    },
    {
        "source": "E:/投資交易/pla_md/logic/1_策略_QTC_TX_WeekTrading_LT.md",
        "strategy_name": "QTC_TX_WeekTrading",
        "classification": "Swing / Long-Term",
        "direction": "Both",
        "timeframe": "unknown",
        "entry_logic": {
            "long": "MP=0 AND _TXinDay AND d<>LastTradeDay AND t<1345 -> market; [entrydat_out2]: condition20 -> stop at entryprice+stl1",
            "short": "MP=0 AND _TXinDay AND d<>LastTradeDay AND t<1345 -> market; [entrydat_out1]: condition10 -> stop at entryprice-stl1"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "if mp>0 and c<entryprice and entryname='entrydat_out2' then sell('double_fault_1'); sell next bar market; buytocover('double_fault_2')"
        },
        "indicators": ["Daily Open", "Daily High", "Daily Low", "Daily Close"],
        "time_filters": ["t<1345", "t>=1344"],
        "tags": ["swing", "week-trading", "QTC", "gap-condition", "midpoint-filter"],
        "notes": "QTC week trading; cond10=opend>(highd(1)+closed(1))*0.5 (open above midpoint prev high+close=strong gap up); cond20=opend<(lowd(1)+closed(1))*0.5 (gap down into lower half); double-fault exit: re-entry stop that if also fails triggers full exit; TX weekly bias"
    },
    {
        "source": "E:/投資交易/pla_md/logic/1-003_TXA_30mKeltner_LOS.md",
        "strategy_name": "b3003_TXA_30mKeltner_LOS",
        "classification": "Day Trading",
        "direction": "Both",
        "timeframe": "intraday (bar-interval dependent)",
        "entry_logic": {
            "long": "flagM=0 AND mp=0 AND kday<>1 (not settlement) -> stop at UBand=EMA(C,KCLen)+NumATRs*ATR(KCLen)",
            "short": "flagM=0 AND mp=0 AND kday<>1 -> stop at LBand=EMA(C,KCLen)-NumATRs*ATR(KCLen)"
        },
        "exit_logic": {
            "stop_loss": "entryprice+Max_WinPoint*0.8 for short; entryprice-Max_WinPoint*0.8 for long",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "sell('maxEL') next bar market; sell('BX1') if l<=entryprice-150+barssinceentry/2 (time-decaying SL); sell('BX3') if h>=AmClosed_TX(1)*1.09 (9% circuit breaker)"
        },
        "indicators": ["EMA(XAverage,KCLen)", "ATR(KCLen)", "Daily High"],
        "time_filters": ["calctime(sess2endtime,-barinterval)", "calctime(sess1starttime,barinterval)", "t>150"],
        "tags": ["ATR", "MA", "day-trade", "Keltner", "circuit-breaker", "time-decaying-SL"],
        "notes": "Keltner Channel: EMA+/-NumATRs*ATR; excludes settlement day (kday<>1); SL=Max_WinPoint*0.8; BX1 time-decaying SL: entryprice-150+barssinceentry/2 (gets looser each bar = dynamic risk); BX3 circuit at 9% from prev AM close; 4 duplicate files"
    },
]

output_path = "C:/Users/admin/workspace/digital-immortality/results/digestion_log.jsonl"
with open(output_path, "a", encoding="utf-8") as f:
    for entry in entries:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print("Appended {} entries. Total new entries written.".format(len(entries)))
