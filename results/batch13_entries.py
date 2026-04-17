import json

entries = [
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5) 139_TX7M_C-bar_DO_v1.1_2106-Alan.md",
        "strategy_id": "e3139_TX7M_C_bar_DO_v1.1_2106",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "intraday",
        "market": "TX",
        "entry_logic": {
            "long": "mp=0 AND condition1 -> market order",
            "short": "z<=0 AND highest(C_bar,3)<0 AND (OO*2+OC)/3 < closed(1) AND C<Closed(1) AND countif(C_bar<0,k)>(k/2+bar_condition) -> market order"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "1345/1330 time exits for both directions"
        },
        "indicators": ["Highest", "Lowest", "Daily_Close", "CountIf", "C_bar_custom"],
        "time_filter": ["calctime(sess1starttime)", "calctime(sess1endtime,-30)", "date<=1150408"],
        "key_insight": "C_bar directional momentum counting strategy - enters when more than half of recent bars show directional alignment (countif>k/2). Custom C_bar metric tracks bar-by-bar direction. Day trade session-end exit.",
        "tags": ["breakout", "day-trade", "intraday", "momentum", "bar-counting"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5) yita 007_TX_10m_open6_LT.md",
        "strategy_id": "yitab20007_TX_10m_open6_LT",
        "classification": "Swing",
        "direction": "both",
        "timeframe": "10m",
        "market": "TX",
        "entry_logic": {
            "long": "condition30 AND condition31 -> stop at maxlist(Amhighd_TX(1),Amhighd_TX(0)); add-on B_02 if initial trade profitable and maxpt>avgdis",
            "short": "condition30 AND condition31 -> stop at minlist(Amlowd_TX(1),Amlowd_TX(0))"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose; t>1300",
            "signal_exit": "condition11/12 market exit; win_pts>sl*multiplier; d-entrydate>2 and maxpt>avgdis and adverse move"
        },
        "indicators": ["Daily_High", "Daily_Low", "AmhighD_TX", "AmlowD_TX"],
        "time_filter": ["calctime(sess1starttime,barinterval*3)", "calctime(sess1endtime,-10*barinterval)", "t>1300"],
        "key_insight": "Open-range breakout using 2-day H/L as entry stops. Add-on B_02 only when initial trade is profitable (maxpt>avgdis). Multi-day hold allowed - exit multiplier scales by days held. Manages stagnant vs winning trades differently.",
        "tags": ["open-range", "swing", "10m", "multi-day", "add-on-entry", "profit-conditional"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5) 策略腳本 Ren01_TX_60m_20211020Triangle_FLT.md",
        "strategy_id": "Ren01_TX_60m_20211020Triangle_FLT",
        "classification": "Trend Following / Breakout",
        "direction": "both",
        "timeframe": "60m",
        "market": "TX",
        "entry_logic": {
            "long": "condition99 (Avg(H,Len*2)>Avg(H,Len) AND Avg(L,Len*2)<Avg(L,Len)) AND MP=0 AND EntriesToday<=1 AND not last trade day -> stop at highest(H,LenK)",
            "short": "same condition99 -> stop at lowest(L,LenK)"
        },
        "exit_logic": {
            "stop_loss": "entryprice +/- STP",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose; last trade day market exit",
            "signal_exit": "last trade day market exit"
        },
        "indicators": ["SMA_Avg(H,Len*2)", "SMA_Avg(L,Len*2)", "Highest(H,LenK)", "Lowest(L,LenK)"],
        "time_filter": [],
        "key_insight": "Triangle pattern via dual-MA convergence on separate H and L channels. Long MA(H)>Short MA(H) AND Long MA(L)<Short MA(L) = narrowing = breakout pending. Breakout entry at N-bar high/low. Fixed STP stop. One trade per day limit.",
        "tags": ["60m", "MA", "breakout", "trend", "triangle", "channel", "one-trade-per-day"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5) 策略腳本 Ren01_TX_60m_20211113Triangle_FLT_V2.md",
        "strategy_id": "Ren01_TX_60m_20211113Triangle_FLT_V2",
        "classification": "Trend Following / Breakout",
        "direction": "both",
        "timeframe": "60m",
        "market": "TX",
        "entry_logic": {
            "long": "MA alignment with independent LenL/LenS params AND MP=0 AND EntriesToday<=1 -> stop at highest(H,LenK)",
            "short": "same -> stop at lowest(L,LenK)"
        },
        "exit_logic": {
            "stop_loss": "entryprice +/- STP",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "LastDayBuyExit/LastDaySellExit"
        },
        "indicators": ["SMA_Avg(H,LenL)", "SMA_Avg(H,LenS)", "SMA_Avg(L,LenL)", "SMA_Avg(L,LenS)", "Highest", "Lowest"],
        "time_filter": [],
        "key_insight": "V2 upgrade: decouples LenL from LenS (was fixed Len*2 vs Len in V1). Same triangle detection logic but allows independent optimization. More degrees of freedom for tuning trend detection period vs breakout lookback.",
        "tags": ["60m", "MA", "breakout", "trend", "triangle", "v2", "decoupled-params"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5) 策略腳本.md",
        "strategy_id": "d21d40_TXAL_1_013_BoxInflectionBreakout_202107",
        "classification": "Trend Following / Breakout",
        "direction": "both",
        "timeframe": "unknown",
        "market": "TX",
        "entry_logic": {
            "long": "condition10 -> stop at highest(_price_buy, _box_len/2)",
            "short": "condition10 -> stop at lowest(_price_sell, _box_len/2)"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "sell/buytocover next bar market"
        },
        "indicators": ["SMA_average(absvalue(c-_price_buy),_box_len/2)", "Highest(_price_buy,_box_len/2)", "Lowest(_price_sell,_box_len/2)", "CountIf(_is_settle_day)"],
        "time_filter": [],
        "key_insight": "Box breakout at inflection points using _box_len/2 for both entry stop level and stop-loss distance. Excludes settlement days from box calculation. Custom _price_buy/sell inflection reference points. Stop = average true distance from reference.",
        "tags": ["MA", "breakout", "trend", "box", "inflection", "settlement-filter"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5) 策略腳本_Ed001_TX_GapMA_6K_LT.md",
        "strategy_id": "Ed001_TX_GapMA_6K_LT",
        "classification": "Swing / Gap Fade",
        "direction": "both",
        "timeframe": "intraday",
        "market": "TX",
        "entry_logic": {
            "long": "Gap up (open>highD(1)) AND pullback into gap zone (c < open*(1-_opend_ratio)+_opend_ratio*lowD(1)) AND below 300-bar MA AND fastMA > slowMA -> market buy",
            "short": "Gap down AND bounce into gap zone AND above 300-bar MA AND fastMA < slowMA -> market sell"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": None
        },
        "indicators": ["SMA(c,300/barinterval)", "SMA(c,_ma_len)", "SMA(c,_ma_len*(1+_slow_m))", "Daily_Open", "Daily_High", "Daily_Low"],
        "time_filter": [],
        "key_insight": "Gap fade within MA trend context. Waits for price to retrace into the gap zone (interpolated by _opend_ratio between open and prior day extremes). 300-bar MA as medium-term trend filter. Fast/slow MA for local trend. Three-layer filter for gap mean reversion.",
        "tags": ["MA", "gap", "swing", "mean-reversion", "fade", "intraday", "multi-layer-filter"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5) 策略腳本_ED001_TX_JumpGapMA6K_LT.md",
        "strategy_id": "b21b40Ed001_TX_JumpGapMA_6K_LT",
        "classification": "Swing / Gap Fade",
        "direction": "both",
        "timeframe": "intraday",
        "market": "TX",
        "entry_logic": {
            "long": "JumpGap condition + pullback in zone + below 300MA + MA trend up -> market buy",
            "short": "JumpGap down + bounce in zone + above 300MA + MA trend down -> market sell"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": None
        },
        "indicators": ["SMA(c,300/barinterval)", "SMA(c,_ma_len)", "SMA(c,_ma_len*(1+_slow_m))", "Daily_Open", "Daily_High", "Daily_Low"],
        "time_filter": [],
        "key_insight": "JumpGap variant of Ed001 GapMA. Jump implies larger/sharper gap threshold. Same three-layer logic. Strategy pair design pattern - test same framework with different gap size requirements for robustness across gap regimes.",
        "tags": ["MA", "gap", "swing", "mean-reversion", "fade", "intraday", "jump-gap", "strategy-pair"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5) 策略腳本_TXAL_1_007_VCP+RangeBreakout.md",
        "strategy_id": "d21d40_TXAL_1_007_VCPRangeBreakout",
        "classification": "Trend Following / Breakout",
        "direction": "both",
        "timeframe": "intraday",
        "market": "TX",
        "entry_logic": {
            "long": "c > _box_high -> market buy",
            "short": "c > _box_high -> market sell (symmetric level)"
        },
        "exit_logic": {
            "stop_loss": "entryprice +/- _stoploss_point",
            "profit_target": "scaled target via sqrt(barssinceentry)",
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "long time no profit -> market exit"
        },
        "indicators": ["Highest(c,_box_len)", "Lowest(c,_box_len)", "CountIf(_is_settle_day)", "Summation(c,_box_len)", "Variance_custom"],
        "time_filter": [],
        "key_insight": "VCP + Range Breakout. Variance over _box_len detects contraction phase. Profit target scales with sqrt(barssinceentry) modeling diffusion from breakout point. Settlement day excluded. Time-based exit for stagnant trades prevents capital lock-up.",
        "tags": ["MA", "breakout", "trend", "VCP", "volatility-contraction", "sqrt-diffusion-target", "settlement-filter"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5) 策略腳本Shuen036_TX_ASI23K_V3_LT.md",
        "strategy_id": "Shuen036_TX_ASI23K_V3_LT",
        "classification": "Swing",
        "direction": "both",
        "timeframe": "intraday",
        "market": "TX",
        "entry_logic": {
            "long": "ASI crossover Avg(ASI,len) AND mp=0 AND EntriesToday<2 AND condition30 AND not last trade day -> market or limit",
            "short": "ASI crossunder or condition30 -> market or limit"
        },
        "exit_logic": {
            "stop_loss": "high/low +/- 2*ATR(13)",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose; exits at 1100 and 1330",
            "signal_exit": "Time-L/Time-S at current close"
        },
        "indicators": ["ASI", "SMA(ASI,len)", "ATR(13)", "Daily_Open", "Daily_High", "Daily_Low", "Daily_Close", "AvgGap(20)", "AvgDRange"],
        "time_filter": ["calctime(sess1starttime,barinterval)", "calctime(sess1endtime,-4*barinterval)", "t>1100", "t>=1330"],
        "key_insight": "ASI (Accumulation Swing Index) crossover MA. ASI integrates gap, daily range, OHLC into cumulative trend metric. ATR(13)*2 volatility-adaptive stop. AvgGap(20) for gap context. Time filter manages AM/PM session transitions - avoids opening noise.",
        "tags": ["ATR", "MA", "ASI", "swing", "intraday", "gap-aware", "volatility-adaptive-stop"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5) 策略腳本Shuen037_TX_CamarillaPivot6k.md",
        "strategy_id": "Shuen037_TX_CamarillaPivot6k_DT",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "6m",
        "market": "TX",
        "entry_logic": {
            "long": "B1: open of session market; B2: stop at SP2; B3: stop at entryprice+stl after 1230",
            "short": "S1: condition30 market; S2: stop at RT2; S3: stop at entryprice-stl"
        },
        "exit_logic": {
            "stop_loss": "entryprice +/- stl",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": None,
            "signal_exit": "win_pts > RT4-SP4 range; c > RT4 for B2 exit; time exit after 1230+highestbar_offset"
        },
        "indicators": ["Camarilla_RT2", "Camarilla_RT3", "Camarilla_RT4", "Camarilla_SP2", "Camarilla_SP3", "Camarilla_SP4", "Daily_OHLC"],
        "time_filter": ["t>=0900", "t>=1230"],
        "key_insight": "Camarilla Pivot on 6m TX. Levels = 0.5*(Close(1)+Open(0)) +/- HL_range multiples. Multi-entry: initial session open, pivot level bounces, PM reversal. Exit when profit exceeds full RT4-SP4 range width. PM timing via highestbar(c,5) for optimal re-entry timing.",
        "tags": ["6m", "pivot", "Camarilla", "day-trade", "level-based", "structured-multi-entry"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5) 策略腳本Shuen038_TX_EarlyORB5K_DT.md",
        "strategy_id": "Shuen038_TX_EarlyORB5K_DT",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "intraday",
        "market": "TX",
        "entry_logic": {
            "long": "B1/B2: condition30 market; B3: stop at opend(0)+5; reversal entries REB1/REB2/REB3 for existing short",
            "short": "S1/S2: condition30 market; S3: stop at opend(0)-5; reversal entries RES1/RES2/RES3 for existing long"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": None,
            "signal_exit": "c < entryprice - iff(highd(0)=highw(0) AND dow>1, 50, 100) -> exit long; barssinceentry>5*in AND countif(c<entryprice,in)=in -> exit stagnant"
        },
        "indicators": ["Highest(h,3)", "Lowest(l,3)", "Daily_Open", "Daily_High", "Daily_Low", "Daily_Close", "CountIf"],
        "time_filter": ["t<1200", "t>1320", "DayOfWeek_filter"],
        "key_insight": "Early ORB with adaptive weekly high/low awareness. Exit threshold adapts by context: if daily high=weekly high AND not Monday, tighter exit (50 pts vs 100). Reversal entries after initial stop-out (REBx/RESx). Stop countdown: barssinceentry>5*in AND all bars against = forced exit.",
        "tags": ["breakout", "day-trade", "ORB", "weekly-level", "adaptive-exit", "reversal-entry"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5) 策略腳本Shuen040_TX_WeekCostLine_FLT.md",
        "strategy_id": "Shuen040_TX_WeekCostLineV1_FLT",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "unknown",
        "market": "TX",
        "entry_logic": {
            "long": "condition70 -> B1/B2 market order",
            "short": "condition70 -> S1/S2 market order"
        },
        "exit_logic": {
            "stop_loss": "entryprice +/- STL",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose; t>=1500",
            "signal_exit": "BE02: market exit; Lout-L/SE02: various exits"
        },
        "indicators": [],
        "time_filter": ["t>0900", "t>=1500", "t<=0500", "t>2100", "t<0400"],
        "key_insight": "Weekly cost line strategy - uses weekly cost/average price as key support/resistance. Fixed STL stop. Multiple time filters suggest overnight/foreign session awareness. No indicators detected in summary - likely uses custom weekly VWAP or cost calculations.",
        "tags": ["day-trade", "weekly-level", "cost-line", "VWAP-like", "overnight-aware"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5)@Ivan2109_TX_MACP19k_LT.md",
        "strategy_id": "b40Ivan2109_TX_MACP19k_LT",
        "classification": "Swing",
        "direction": "both",
        "timeframe": "intraday",
        "market": "TX",
        "entry_logic": {
            "long": "T_L: stop at maxlist(OpenD(0)+stl*0.5, highD(0)-1); CT_L: stop at (HighD(0)+H)/2; PL: reversal from short when H<dn AND C>(OpenD+highd)/2",
            "short": "T_S: stop at minlist(OpenD(0)-stl*0.5, LowD(0)+1); CT_S: DIF-DIF[1]>0 -> stop at (LowD+L)/2; PS: reversal from long"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": None,
            "signal_exit": "L9%: limit at entryprice*1.09; LTO: market; S9%: limit at entryprice*0.91"
        },
        "indicators": ["SMA(avgprice,Len)", "XAverage(h,k)", "XAverage(l,k)", "Average_Price(OHLC/4)", "Daily_Open", "Daily_High", "Daily_Low", "Daily_Close"],
        "time_filter": ["t>1200", "t>=1330"],
        "key_insight": "MA Channel Pivot strategy. Uses EMA(H,k) and EMA(L,k) as channel boundaries. Entry levels derived from daily OHLC midpoints. DIF = C - Avg(avgprice,Len) as momentum. Fixed 9% profit target (large for futures). Reversal entries PS/PL when trapped. up/dn bands from Close(1)+/-stl*r.",
        "tags": ["MA", "EMA", "swing", "intraday", "channel", "reversal-entry", "fixed-pct-target"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5)@LV@_08Week_of_DTstyle_7k_LO.md",
        "strategy_id": "a24a40LVa40_08Week_of_DTstyle_7K_LO",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "intraday",
        "market": "TX",
        "entry_logic": {
            "long": "mp=0 AND dayin>=3 AND not last trade day AND K>=kin AND t<=calctime(sess1endtime,-5*barinterval) -> stop at Highd(0)",
            "short": "condition19 AND C>Openw(0) AND (loww(0)+openw(0))/2 + C > closew(1)*2 -> stop at Lowd(0)"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": "maxlist(H,opend(0))",
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "Last L/S next bar market"
        },
        "indicators": ["Daily_Open", "Daily_High", "Daily_Low", "Weekly_Open", "Weekly_Low", "Weekly_Close"],
        "time_filter": ["calctime(sess1endtime,-5*barinterval)", "t>=1330"],
        "key_insight": "Week-context DT strategy. Uses weekly OHLC (openw, loww, highw, closew) for bias. Short condition requires price above weekly open AND midpoint of week low+open + current > 2x prior week close - weekly relative strength filter. Profit target at max of H vs daily open.",
        "tags": ["day-trade", "intraday", "weekly-context", "DT-style", "weekly-OHLC", "relative-strength"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5)@LV@_TX_Week_3GPSBL_17K_LT.md",
        "strategy_id": "a24a40LVa40_TX_Week_3GPSBL_17K_LT",
        "classification": "Swing",
        "direction": "both",
        "timeframe": "intraday",
        "market": "TX",
        "entry_logic": {
            "long": "dayin>=TD AND mp=0 AND k>=1 AND t<calctime(sess1endtime,-2*barinterval) -> stop (level unspecified); L2 with dayin>=1",
            "short": "same conditions -> stop (level unspecified); S2 secondary entry"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": "L, h, lowd(0), highd(0) - multiple targets",
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "LAST L/S market"
        },
        "indicators": ["Daily_Open", "Daily_High", "Daily_Low", "mid=(HighD(1)+LowD(1)+CloseD(1)*2)/4"],
        "time_filter": ["calctime(sess1endtime,-2*barinterval)"],
        "key_insight": "3G PSB Level swing strategy. 17K contract. Uses pivot mid = (H+L+C*2)/4 weighted formula. BullBear state machine. Multiple profit targets at H, L, daily extremes. dayin counter controls entry timing. Complex state (wait, z, k counters) for position management.",
        "tags": ["swing", "intraday", "17K", "pivot", "weighted-midpoint", "state-machine", "multi-target"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5)_@LV@_tx_TimeGuardian_13K_LT.md",
        "strategy_id": "b24b40LVb40b24_tx_TimeGuardian_13K_LT",
        "classification": "Swing",
        "direction": "both",
        "timeframe": "intraday",
        "market": "TX",
        "entry_logic": {
            "long": "dayin>=TD AND wait=0 AND mp=0 AND K>1 AND t<=calctime(sess1endtime,-2*barinterval) -> stop (L); L2 reversal from short; TL last-trade-day market",
            "short": "same conditions -> stop (S); S2 with wait=1 and ExitsToday=0 and K>(1+4); TS last-trade-day market"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": "maxlist(H,opend(0))",
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": None
        },
        "indicators": ["Daily_Open(midy)", "Daily_High(mid)", "Daily_Low", "Daily_Close", "midy=(HighD(2)+LowD(2)+CloseD(2)*2)/4", "upy/dny bands"],
        "time_filter": ["calctime(sess1endtime,-2*barinterval)"],
        "key_insight": "TimeGuardian 13K: uses 2-day-back pivot (midy formula) as range reference. upy/dny = midy +/- range bands. wait flag controls re-entry after exit. Last-trade-day special entries TL/TS. Profit at max(H,opend(0)) = recent session high or daily open. 13K contract size.",
        "tags": ["swing", "intraday", "13K", "2-day-lookback", "wait-flag", "time-guardian", "settlement-aware"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5)_@LV@_tx_TransFormer_17K_(DT)LT.md",
        "strategy_id": "b24b40LVb40b24_tx_TransFormer_17K_LT",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "intraday",
        "market": "TX",
        "entry_logic": {
            "long": "dayin>=TD AND k>=3 AND not sessionlastbar AND mp=0 AND ExitsToday=0 -> stop (L); RL In reversal stop; L In condition10 stop; DT_L2 for k<=ky/2",
            "short": "same structure -> S/RS/S In/DT_S2"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": "entryprice+/-iff(barssinceentry>ky, stp/(ED*0.5), stp); minlist(entryprice,lowd(0)); maxlist(entryprice,highd(0))",
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "DT L/S end: exit if c crosses (up-dn)/2 range midpoint"
        },
        "indicators": ["Daily_Open", "Daily_High(mid)", "Daily_Low", "Daily_Close", "midy=(HighD(2)+LowD(2)+CloseD(2)*2)/4", "up/dn bands"],
        "time_filter": ["calctime(sess1endtime,-1*barinterval)"],
        "key_insight": "TransFormer 17K: profit target adapts by barssinceentry vs ky threshold - later in trade gets tighter target (stp/(ED*0.5) vs stp). Exit also triggered if price crosses (up-dn)/2 midpoint or prior week midpoint. DT_L2/DT_S2 secondary entries in first half of session.",
        "tags": ["day-trade", "intraday", "17K", "adaptive-target", "time-adaptive", "multi-entry", "transformer"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5)_011_TX_4Day (OHLC)_FDT.md",
        "strategy_id": "_011_TX_5K_4DayOHLC_FDT",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "intraday",
        "market": "TX",
        "entry_logic": {
            "long": "normal buy: mp=0 AND dentry=0 AND condition1 -> stop at h; reverse buy: mp<>0 AND dentry<=1 -> stop at (mid+up)/2; countS reversal",
            "short": "normal: mp=0 AND dentry=0 -> stop at l; reverse: stop at (mid+dn)/2; position-loss reversal at 1505"
        },
        "exit_logic": {
            "stop_loss": "entryprice +/- Max_WinPoint*0.8",
            "profit_target": "entryprice target at various levels; Max_WinPoint*0.8",
            "trailing_stop": None,
            "time_exit": "SetExitOnClose; 1505 time exit for reversal",
            "signal_exit": "TM-L/TM-LL/BX10 exits"
        },
        "indicators": [],
        "time_filter": ["calctime(sess1starttime,barinterval)", "calctime(sess1starttime,2*barinterval)", "t=1505", "t>=0430", "t<=0500"],
        "key_insight": "4-Day OHLC framework FDT (Fully Dynamic Trading). Uses 4-day OHLC reference for up/mid/dn levels. Stop and target both = Max_WinPoint*0.8 - symmetric risk/reward. 1505 forced reversal entry if in loss. dentry counter limits re-entries. Overnight session filter (0430-0500).",
        "tags": ["day-trade", "intraday", "4-day-OHLC", "symmetric-risk-reward", "forced-reversal", "dentry-limit"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5)BN_003_TX_Sar_FDO_10k.md",
        "strategy_id": "c40BN_005_TX_SAR_FDT_10k_v2",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "intraday",
        "market": "TX",
        "entry_logic": {
            "long": "k 3-10 (or 20 if in position) AND dentry<=1 -> stop at h; reversal from stopped-out long: stop at lastentryprice",
            "short": "same k range -> stop at l; reversal: stop at 2*lossprice-lastentryprice (mirror); Loser-sell-again: re-short at last entry after exit"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose; AM/PM day-over exits",
            "signal_exit": "Loser sell/cover market; day over AM/PM session exits"
        },
        "indicators": ["ATR(AvgTrueRange)", "Average_Price(AvgPrice)", "CountIf(C>ST,3)", "AmOpend_TX", "AmClosed_TX"],
        "time_filter": ["t>0845", "t<1345", "t>1500", "t<0500", "calctime(sess1endtime,-1*barinterval)"],
        "key_insight": "SAR (Stop and Reverse) system with Loser re-entry logic. Reversal entry = 2*lossprice - lastentryprice (mirror of loss). Loser-sell-again: if exited at loss then condition met -> re-enter same direction. k window 3-20 bars. ATR for countif channel checks. AM/PM session separation.",
        "tags": ["ATR", "day-trade", "intraday", "SAR", "stop-and-reverse", "loser-re-entry", "mirror-entry"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5)BN_TX_2109_IslandReverse PLE.md",
        "strategy_id": "c40BN_TX_IslandReverseAndDoubleGap_LO_100k_v2",
        "classification": "Trend Following / Breakout",
        "direction": "both",
        "timeframe": "unknown",
        "market": "TX",
        "entry_logic": {
            "long": "gapbar distance<pp AND |gap[1]+gap[2]|<Avg(TrueRange,3)*pp2/100 -> market or stop at h; double gap buy -> stop at highest(h,kday); special buy on kday<45",
            "short": "condition10 AND gap[2]<0 -> market; positionprofit>0 AND openprofit<0 -> stop at l; double gap sell -> stop at lowest(l,kday)"
        },
        "exit_logic": {
            "stop_loss": "stopB/stopS custom levels",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "double gap sell over when gap[1]>0 -> buytocover"
        },
        "indicators": ["SMA_average(TrueRange,3)", "Highest(h,kday)", "Lowest(l,kday)", "True_Range", "gap_array"],
        "time_filter": [],
        "key_insight": "Island Reversal + Double Gap system. Detects island reversal (two opposite gaps close to each other). Gap size normalized by ATR*pp2/100. Double gap entry extends if initial holds. Add-on at multi-day breakout. 100K contract (large lot). Gap symmetry check via abs(gap[1]+gap[2]).",
        "tags": ["MA", "breakout", "trend", "island-reversal", "double-gap", "gap-symmetry", "ATR-normalized"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5)BN_TX_2109_orbplus_DO_4k_v2.md",
        "strategy_id": "a40BN_TX_ORB_DO_4k_v2",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "intraday",
        "market": "TX",
        "entry_logic": {
            "long": "EntriesToday=0 AND k>in AND t<=1200 AND mp=0 -> stop at highd(0)-Avg(TrueRange,k); Reverse Buy if below MA average -> stop at highest(h,barssinceentry)",
            "short": "EntriesToday=0 AND k>in AND t<=1200 AND mp=0 -> stop at lowd(0)+Avg(TrueRange,k); Reverse Short -> stop at lowest(l,barssinceentry)"
        },
        "exit_logic": {
            "stop_loss": "entryprice +/- diff*gg",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose; t>1320",
            "signal_exit": "Day Exit Sell/Cover"
        },
        "indicators": ["SMA_average(l,k)", "SMA_average(h,k)", "Highest(h,barssinceentry)", "Lowest(l,barssinceentry)", "TrueRange", "DTrueRange_BN", "Daily_High", "Daily_Low", "Daily_Close"],
        "time_filter": ["t<=1200", "t<=1100", "CalcTime(sess1endtime,-2*barinterval)", "t>1320"],
        "key_insight": "ORB Plus - entry inside daily range offset by ATR from extreme (highd-ATR / lowd+ATR) rather than at exact extreme. Condition10/20: average(l/h,k) vs 2*close(1)+1*high/lowD(1) trend check. Reversal entry tracks barssinceentry high/low. Morning-only entries (t<=1200).",
        "tags": ["MA", "breakout", "day-trade", "ORB", "ATR-offset", "intrabar-reversal", "morning-only"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5)NV002_TX30M_SR_FLT.md",
        "strategy_id": "NV002_TX30M_SR_FLT",
        "classification": "Trend Following / Breakout",
        "direction": "both",
        "timeframe": "30m",
        "market": "TX",
        "entry_logic": {
            "long": "C cross over AvgL -> RL stop order; Resistance>Resistance[1] -> TL stop order",
            "short": "C cross under AvgH -> RS stop order; Support<Support[1] -> TS stop order"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "RL-Profit: limit at Resistance; RS-Profit: limit at Support"
        },
        "indicators": ["SMA_Average(Low,Length)", "SMA_Average(High,Length)", "Highest(C,Length)", "Lowest(C,Length)"],
        "time_filter": [],
        "key_insight": "Support/Resistance channel with MA bands. AvgL=MA(Low), AvgH=MA(High) create adaptive channel. Resistance = Highest(C,Length) updated on crossunder AvgH. Support = Lowest(C,Length) updated on crossover AvgL. Profit target at the opposite channel level - range capture strategy.",
        "tags": ["MA", "breakout", "trend", "30m", "support-resistance", "channel", "range-capture"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5)NV2107003_TX3M_Amy_FDT.md",
        "strategy_id": "NV2107003_TX3M_Amy_FDT",
        "classification": "Trend Following",
        "direction": "both",
        "timeframe": "3m",
        "market": "TX",
        "entry_logic": {
            "long": "condition23 (Avg(weight,Len)>0) AND (condition21 OR condition22) AND AvgPrice>(highada(1)*2+closeada(1))/3 -> stop",
            "short": "same conditions -> stop"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose; T>=1345; T<0300",
            "signal_exit": "Lclose/Sclose market"
        },
        "indicators": ["SMA_Average(weight,Len)", "AvgPrice(OHLC/4)", "CountIf_NetGreenRed", "CountIf_NetUpDn"],
        "time_filter": ["T>=1345", "T<=0500", "T<1300", "T<0300"],
        "key_insight": "3m Amy: weight = Net green/red bar count + Net up/dn count combined. Avg(weight,Len)>0 = trend condition. AvgPrice vs (highada*2+closeada)/3 pivot reference. Ada = American day-ahead reference (prior session). Time cutoff at 1345 and overnight filter.",
        "tags": ["MA", "trend", "3m", "bar-weight", "net-directional", "pivot-reference", "AM-session"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5)NV2108004_TX15M_Bonny_LT.md",
        "strategy_id": "NV2108004_TX15M_Bonny_DT",
        "classification": "Swing",
        "direction": "both",
        "timeframe": "15m",
        "market": "TX",
        "entry_logic": {
            "long": "d=LastTradeDay(D) AND sessionlastbar -> market (settlement play)",
            "short": "d=LastTradeDay(D) AND sessionlastbar -> market (settlement play)"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": None
        },
        "indicators": ["SMA_average(H-L,300/barinterval)", "Highest(h,60/barinterval)", "Highest_a(HH,Len)", "Lowest(L,60/barinterval)", "Lowest_a(LL,Len)", "Daily_High", "Daily_Low", "Daily_Close"],
        "time_filter": [],
        "key_insight": "Settlement day play on 15m. Main entry logic at session last bar on last trade day (settlement). Uses vHH/vLL arrays and DS counter for directional state. Highest/Lowest over 60min (hour) vs daily levels as reference. vmp (virtual market position) tracks signal separately from actual mp.",
        "tags": ["MA", "breakout", "swing", "15m", "settlement-play", "virtual-position", "last-trade-day"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5)NV2109005_TX6M_Cindy_LT -original.md",
        "strategy_id": "NV2109005_TX6M_Cindy_LT_original",
        "classification": "Swing",
        "direction": "both",
        "timeframe": "6m",
        "market": "TX",
        "entry_logic": {
            "long": "B1: d=exitdate(1) AND vmp=0 AND vmp[1]<0 -> stop; B2: DS=0 AND C<minlist(closed(1),dn) AND not ShortExit -> stop; B3: lowd(0)>up AND c<o -> stop",
            "short": "S1: EntriesToday<=1 AND condition40 -> stop; S2: k>in AND not sessionlastbar -> stop; S3: S1 entry follow-up"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "CalcTime(sess1endtime,-barinterval)",
            "signal_exit": "RL-Run/RS-Run market when condition31/32 false"
        },
        "indicators": ["Highest(H,2)", "Lowest(L,2)", "Daily_High", "Daily_Low", "Daily_Close", "mid=(HLD(1)+LowD(1)+CloseD(1))/3", "up=mid*2-LowD(1)", "dn=mid*2-HighD(1)", "CountIf"],
        "time_filter": ["CalcTime(sess1endtime,-barinterval)"],
        "key_insight": "Cindy original: pivot (mid/up/dn) from prior day H,L,C. up=2*mid-Low (R2-type), dn=2*mid-High (S2-type). vmp virtual position tracks signal. DS state machine. B2/B3 anti-trend entries when price below dn or above up with bar direction contradiction. Original version has B3 that was removed in LT version.",
        "tags": ["breakout", "swing", "6m", "pivot", "DS-state", "virtual-position", "anti-trend-entry", "original"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5)NV2109005_TX6M_Cindy_LT.md",
        "strategy_id": "NV2109005_TX6M_Cindy_LT",
        "classification": "Swing",
        "direction": "both",
        "timeframe": "6m",
        "market": "TX",
        "entry_logic": {
            "long": "B1: d=exitdate(1) AND vmp=0 AND vmp[1]<0 -> stop; B2: DS=0 AND C<minlist(closed(1),dn) AND not ShortExit -> stop",
            "short": "S1: EntriesToday<=1 AND condition40 -> stop; S2: k>in AND not sessionlastbar AND vmp=0 -> stop"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "CalcTime(sess1endtime,-barinterval)",
            "signal_exit": "RL-Run/RS-Run market when condition31/32 false"
        },
        "indicators": ["Highest(H,2)", "Lowest(L,2)", "Daily_High", "Daily_Low", "Daily_Close", "mid=(HLD(1)+LowD(1)+CloseD(1))/3", "up=mid*2-LowD(1)", "dn=mid*2-HighD(1)", "CountIf"],
        "time_filter": ["CalcTime(sess1endtime,-barinterval)"],
        "key_insight": "Cindy LT production version: removes B3 anti-trend entry vs original. Cleaner entry set. Pivot levels mid/up/dn from prior day. vmp virtual position. DS=0 required (no directional state lock). EntriesToday<=1 for shorts. Runs condition31/32 as exit triggers.",
        "tags": ["breakout", "swing", "6m", "pivot", "DS-state", "virtual-position", "production-version"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5)NV2110006_TX3M_FLT.md",
        "strategy_id": "NV2110006_TX3M_FLT",
        "classification": "Breakout",
        "direction": "both",
        "timeframe": "3m",
        "market": "TX",
        "entry_logic": {
            "long": "(d=LastTradeDay AND T>=1330) OR (LastTradeDay changed AND T<=0500) -> stop at highest(H,15/barinterval)",
            "short": "(d=LastTradeDay AND T>=1330) OR settlement transition AND T<=0500 -> stop at lowest(L,15/barinterval)"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": None,
            "signal_exit": "LC/SC market"
        },
        "indicators": ["Highest(H,15/barinterval)", "Lowest(L,15/barinterval)"],
        "time_filter": ["T>=1330", "T<=0500", "T<0430", "T>=0845", "T<1345"],
        "key_insight": "Settlement and overnight breakout on 3m. Entry only at settlement time (1330+) or overnight near settlement transition (T<=0500). 15-min high/low breakout (15/barinterval bars = 5 bars on 3m). Exit when AvgHL*2 profit for short. Narrow entry window strategy.",
        "tags": ["breakout", "3m", "settlement-timing", "overnight", "narrow-window"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5)TimChen009_TX_30mBBI_LOS-策略腳本.md",
        "strategy_id": "a3009_BBI_30m",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "30m",
        "market": "TX",
        "entry_logic": {
            "long": "condition11 (BBI alignment) -> LE-1 market order",
            "short": "condition11 -> SS-1 market order"
        },
        "exit_logic": {
            "stop_loss": "(AmOpend_TX(0)+Amlowd_TX(1))/2 for long; (AmOpend_TX(0)+Amhighd_TX(1))/2 for short",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "L-EXIT-1/S-EXIT-1 on condition12/22; BX3 if h>=AmClosed_TX(1)*1.09"
        },
        "indicators": ["BBI_S_MA1", "BBI_S_MA2", "BBI_S_MA3", "BBI_S_MA4", "Highest(Close,iPeriod)", "Lowest(Close,iPeriod)", "Summation_AbsValue"],
        "time_filter": ["calctime(sess1starttime,barinterval)", "calctime(sess1endtime,barinterval)"],
        "key_insight": "BBI (Bull and Bear Index) on 30m TX. BBI = average of multiple MAs (S, S*2, S*3, S*4). Condition11 = BBI alignment for entry. Stop = midpoint of (AmOpen(0) + prior session low/high). Exit at 9% profit (BX3: h>=AmClosed*1.09). American session reference for stops via AmOpen/AmClose.",
        "tags": ["MA", "BBI", "breakout", "day-trade", "30m", "American-session-reference", "multi-MA-average"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5)TungWen002_TX_EMA50K_LT.md",
        "strategy_id": "TungWen002_TX_EMA50K_LT",
        "classification": "Swing",
        "direction": "both",
        "timeframe": "unknown",
        "market": "TX",
        "entry_logic": {
            "long": "mp=0 AND t between 0900-1330 AND EntriesToday<1 -> B_MA market; condition21 AND condition22 AND condition32 -> B_MA2 market",
            "short": "mp=0 AND t between 0900-1330 AND EntriesToday<1 -> S_MA / S_MA2 market"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": None
        },
        "indicators": ["XAverage(c,len)", "XAverage(c,len*2)", "MAdiffvalue=c-fastMA", "CountIf(c>slowMA,6)", "CountIf-based conditions"],
        "time_filter": ["t>0900", "t<1330"],
        "key_insight": "EMA 50K strategy. fastMA=EMA(c,len), slowMA=EMA(c,len*2). MAdiffvalue = c - fastMA for deviation. condition13: countif(c>slowMA,6)=6 AND c<slowMA*1.001 (just crossed back from above). Uses 6-bar lookback for sustained position above/below MA. One trade per day in trading hours only.",
        "tags": ["MA", "EMA", "swing", "crossover", "countif-sustained", "one-trade-per-day"]
    },
    {
        "batch": 13,
        "file": "E:/投資交易/pla_md/logic/(5)策略及指標程式碼-004_TXF_3G(1.382)_4mK_LO-202101-彥勝.md",
        "strategy_id": "a3004_TXF_3G_1e382_4mK_LO",
        "classification": "Day Trading",
        "direction": "both",
        "timeframe": "4m",
        "market": "TXF",
        "entry_logic": {
            "long": "M_P=0 AND condition1 AND condition2=false -> LE1 stop at Amhighd_TX(0)",
            "short": "M_P=0 AND condition1 AND condition2=false -> SE1 stop at Amlowd_TX(0)"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": None,
            "signal_exit": "LD_LX/LD_SX this bar at C (immediate exit)"
        },
        "indicators": [],
        "time_filter": ["time>=0845", "time<=1345", "calctime(sess1endtime,-barinterval)", "t>=1330", "date>=1170515"],
        "key_insight": "3G 1.382 pattern on 4m TXF. 1.382 likely refers to Fibonacci extension level (1 + 0.382). Entry at American session high/low breakout (Amhighd_TX). condition2=false as exclusion filter. Exit immediately at current bar close when exit condition met. Effective from date 1170515 (2028/05/15 in ROC dating = 2017/05/15).",
        "tags": ["day-trade", "4m", "TXF", "Fibonacci", "3G-pattern", "American-session", "date-filter"]
    }
]

with open("C:/Users/admin/workspace/digital-immortality/results/digestion_log.jsonl", "a", encoding="utf-8") as f:
    for e in entries:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")

print(f"Appended {len(entries)} entries successfully")
