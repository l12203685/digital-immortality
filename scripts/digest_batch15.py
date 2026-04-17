import json

records = [
    {
        "source_file": "E:/投資交易/pla_md/logic/(7) 策略腳本Shuen036_TX_ASI23K_V3_LT.md",
        "strategy_name": "Shuen036_TX_ASI23K_V3_LT (ver 7)",
        "classification": "Swing/Long-Term",
        "direction": "Both",
        "entry_logic": {
            "long": ["ASI cross over Average(ASI,len) = L-Guava limit; mp=0 AND EntriesToday<2 AND condition30 = L market"],
            "short": ["Symmetric S/S-Guava"]
        },
        "exit_logic": {"stop_loss": "None", "profit_target": "None", "trailing_stop": "None", "time_exit": "SetExitOnClose", "signal_exit": "Time-L/Time-S this bar at close"},
        "indicators": ["ASI (Accumulation Swing Index)", "SMA", "ATR", "Daily OHLC"],
        "time_filters": ["t>1100", "t>=1330"],
        "key_insight": "ASI crossover above its own MA as trend entry; daily gap/range arrays (AvgGap,DRange) for market context; ATR for stop placement; swing strategy up to 2 entries/day",
        "tags": ["ASI", "ATR", "MA", "swing", "intraday"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/(7)@@202102T98_LATETREND_4M_D0.md",
        "strategy_name": "202102T98_LATETREND_4M_D0 (ver 7)",
        "classification": "Day Trading",
        "direction": "Both",
        "entry_logic": {
            "long": ["condition1 = L in stop at MAXlist(C,openD(0))", "condition2 = L in2 adaptive with EntriesToday"],
            "short": ["condition1 = S in stop at MINlist(C,openD(0))", "condition2 = S in2 adaptive"]
        },
        "exit_logic": {"stop_loss": "Fixed entryprice +/- stp", "profit_target": "None", "trailing_stop": "None", "time_exit": "SetExitOnClose", "signal_exit": "TOB/TOS market"},
        "indicators": ["Daily OHLC", "CountIf(H>H[1],3>=3 consecutive)"],
        "time_filters": ["t<1000", "t>1000", "t<1300"],
        "key_insight": "Late-trend: c-o vs c[1]-o[1] momentum comparison; COUNTIF 3+ consecutive H>H[1]; entry MAXlist(C,openD(0)) = always >= open capturing gap-up; 2nd entry uses HIGHD(0) if already traded",
        "tags": ["day-trade", "late-trend", "consecutive-candle", "intraday"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/(7)@@202106TAZ_CDP_4K_D0.md",
        "strategy_name": "202106T90_Normal_CDP_4K_D0 (ver 7)",
        "classification": "Trend Following / Breakout",
        "direction": "Both",
        "entry_logic": {
            "long": ["mp=0 AND T<1325 AND condition2 = Bnhnl-1 stop at maxlist(close,opend(0))", "MA<nl = BMA or Bnhnl-3 stop"],
            "short": ["Symmetric Snhnl/SMA conditions"]
        },
        "exit_logic": {"stop_loss": "entryprice*(1-STP) / *(1+STP)", "profit_target": "maxlist(entryprice+Closed(1)*STP, h, entryprice+(ah-cdp))", "trailing_stop": "None", "time_exit": "SetExitOnClose; SETTLEOut at 1325", "signal_exit": "TOB/TOS market"},
        "indicators": ["SMA", "CDP pivot (H+L+2C)/4 deriving ah/al/nh/nl zones", "Highest/Lowest", "CountIf"],
        "time_filters": ["T<1325", "time>=1325"],
        "key_insight": "CDP pivot (H+L+2C)/4 creates dynamic price zones; profit target maxlist(percentage STP, structural ah-cdp extension) = always takes wider target; MA vs CDP zones determines directional bias",
        "tags": ["CDP", "MA", "breakout", "pivot", "intraday", "trend"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/(7)@@202108T87_BouncyBall_6K_D0.md",
        "strategy_name": "202107T87_AZ_6K_BouncyBall_D0 (ver 7)",
        "classification": "Trend Following / Breakout",
        "direction": "Both",
        "entry_logic": {
            "long": ["condition91 AND EntriesToday<1 = L in stop at IFF(opend(0)>closed(1),openD(0),H)", "mp<>0 AND EntriesToday<=1 = S_I_PUNCH stop at highest(L,3)"],
            "short": ["condition91 AND EntriesToday<1 = S in stop at IFF(opend(0)<closed(1),openD(0),L)", "mp<>0 AND barssinceentry=0 = L_I_PUNCH stop at lowest(H,3)"]
        },
        "exit_logic": {"stop_loss": "None", "profit_target": "None", "trailing_stop": "None", "time_exit": "SetExitOnClose", "signal_exit": "TOB/TOS market"},
        "indicators": ["EMA/XAverage(TrueRange,3)", "Highest/Lowest", "CountIf", "Daily Open/Close"],
        "time_filters": ["time>=1325"],
        "key_insight": "BouncyBall: gap-adaptive entry = if gap up use open else use H; I_PUNCH counter-trend at 3-bar highest L (short reverse) or lowest H (long reverse); COUNTIF consecutive candles as momentum check",
        "tags": ["bouncy-ball", "gap-adaptive-entry", "counter-trend", "EMA", "intraday"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/(7)@@202109T86_AZ_4K_D0.md",
        "strategy_name": "202109T86_AZ_Vol_4K_D0 (ver 7)",
        "classification": "Trend Following",
        "direction": "Both",
        "entry_logic": {
            "long": ["condition91 AND (cond11 OR cond21) AND EntriesToday<2 = L stop at maxlist(opend,closed(1))", "condition24 = CT_L stop at (Opend+highd)*0.5"],
            "short": ["Symmetric; CT_S at (Opend+lowd)*0.5"]
        },
        "exit_logic": {"stop_loss": "None", "profit_target": "None", "trailing_stop": "None", "time_exit": "SetExitOnClose", "signal_exit": "L_I_PUNCH COUNTIF; B8% limit closed(1)*(1+0.08); TOB/TOS"},
        "indicators": ["SMA Average H-L", "EMA XAverage TrueRange", "CountIf", "Daily OHLC"],
        "time_filters": ["time>=1325"],
        "key_insight": "Volatility trend: DayVolatility vs AvgHL range as filter; CT_L/CT_S counter-trend entries at midpoint open+high/low; 8% limit exit from prior close = profit capture at pre-defined structural level",
        "tags": ["trend", "volatility-filter", "counter-trend", "EMA", "intraday"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/(7)_@LV@_tx_TransFormer_17K_(DT)LT.md",
        "strategy_name": "LV_tx_TransFormer_17K_DT_LT (ver 7)",
        "classification": "Day Trading",
        "direction": "Both",
        "entry_logic": {
            "long": ["dayin>=TD AND k>=3 AND mp=0 AND ExitsToday=0 = L stop", "condition21 = RL In; condition10 = L In", "dayin>=3 AND k>=2 AND k<=ky/2 = DT_L2 stop"],
            "short": ["Symmetric S/RS/S In/DT_S2"]
        },
        "exit_logic": {"stop_loss": "None", "profit_target": "entryprice+iff(barssinceentry>ky,stp/(ED*0.5),stp); also minlist(entryprice,lowd)/maxlist(entryprice,highd)", "trailing_stop": "None", "time_exit": "SetExitOnClose", "signal_exit": "DT end: c<entryprice+(up-dn)/2 OR c<(highw(1)+loww(1)*2)/3"},
        "indicators": ["Daily OHLC", "Weekly High/Low (highw/loww)", "mid=(H+L+C*2)/4 pivot"],
        "time_filters": ["calctime(sess1endtime,-1*barinterval)"],
        "key_insight": "TransFormer: adaptive target compresses when held>ky bars = stp/(ED*0.5) smaller; exit uses weekly pivots as mid-reference; dayin session bar counter; multiple re-entry modes (DT_L2 for second-half session)",
        "tags": ["day-trade", "adaptive-target", "weekly-pivot", "complex", "intraday"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/(7)NV002_TX30M_SR_FLT.md",
        "strategy_name": "NV002_TX30M_SR_FLT (ver 7)",
        "classification": "Trend Following / Breakout",
        "direction": "Both",
        "entry_logic": {
            "long": ["C Cross over AvgL = RL stop", "Resistance>Resistance[1] = TL stop (expanding resistance breakout)"],
            "short": ["C cross under AvgH = RS stop", "Support<Support[1] = TS stop (contracting support breakdown)"]
        },
        "exit_logic": {"stop_loss": "None", "profit_target": "None", "trailing_stop": "None", "time_exit": "SetExitOnClose", "signal_exit": "RL-Profit limit at Resistance; RS-Profit limit at Support"},
        "indicators": ["SMA AvgL=Average(Low,Length) AvgH=Average(High,Length)", "Highest dynamic Resistance", "Lowest dynamic Support"],
        "time_filters": ["None"],
        "key_insight": "Dynamic SR: Resistance updates to Highest(C,Length) when C crosses AvgH; Support updates to Lowest(C,Length) when C crosses AvgL; profit targets taken AT SR levels after breakout = fades back to key levels",
        "tags": ["support-resistance", "dynamic-SR", "breakout", "MA"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/(7)策略PLA (S)003_TX_Score_2k_DT_20210618.md",
        "strategy_name": "003_TX_Score_2k_DT (ver 7 20210618)",
        "classification": "Day Trading",
        "direction": "Both",
        "entry_logic": {"long": ["condition3 = L-in market"], "short": ["condition3 = S-in market"]},
        "exit_logic": {"stop_loss": "None", "profit_target": "None", "trailing_stop": "None", "time_exit": "SetExitOnClose", "signal_exit": "score<highest(score,k)/2 = sell; win_pts>target AND c<(highd*2+lowd)/3 = sell"},
        "indicators": ["Score composite", "Highest/Lowest score", "Daily High/Low"],
        "time_filters": ["t<1300"],
        "key_insight": "Score-based exit: sells when score fades below half its recent max; secondary exit at (highd*2+lowd)/3 price level when profitable = combines momentum scoring with structural price reference",
        "tags": ["scoring", "day-trade", "momentum-exit", "intraday"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/(7)策略PLA(S) 005_TX_RSI_60k_LT_20210811.md",
        "strategy_name": "005_TX_RSI_60k_LT (ver 7 20210811)",
        "classification": "Swing/Long-Term",
        "direction": "Both",
        "entry_logic": {"long": ["mp=0 AND t<1100 = stop at h (RSI<20 oversold)"], "short": ["mp=0 AND t<1100 = stop at l (RSI>80 overbought)"]},
        "exit_logic": {"stop_loss": "None", "profit_target": "entryprice*(1+BP*0.01) / *(1-SP*0.01) limit", "trailing_stop": "None", "time_exit": "SetExitOnClose", "signal_exit": "Percentage limit orders"},
        "indicators": ["RSI(c,N)"],
        "time_filters": ["t<1100"],
        "key_insight": "RSI extremes as direction filter (>80 short, <20 long); morning H/L breakout entry; percentage profit targets (BP%/SP%) from entry = simple overbought/oversold reversal",
        "tags": ["RSI", "swing", "percentage-target", "overbought-oversold"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/(7)策略程式碼 sungwen.007_Tx_202106_FLT.md",
        "strategy_name": "sungwen007_Tx_202106_FLT (ver 7)",
        "classification": "Breakout",
        "direction": "Both",
        "entry_logic": {"long": ["mp=0 AND condition3 = stop at UpperEntryChannel Highest(High,EntryChannelLength)"], "short": ["mp=0 AND condition3 = stop at LowerEntryChannel Lowest(Low,EntryChannelLength)"]},
        "exit_logic": {"stop_loss": "UpperExitChannel-StopATR / LowerExitChannel+StopATR", "profit_target": "None", "trailing_stop": "None", "time_exit": "SetExitOnClose", "signal_exit": "_EntryH-entryprice>profit.get*entryprice = sell market"},
        "indicators": ["Highest/Lowest dual Donchian channels", "ATR AvgTrueRange"],
        "time_filters": ["None"],
        "key_insight": "Dual Donchian (separate entry vs exit channel lengths); ATR stop from exit channel; entry filter AvgTrueRange(1)<StopATR[1]*ATR = low volatility regime entry only; percentage profit exit",
        "tags": ["breakout", "Donchian", "ATR", "channel", "volatility-filter"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/(7)策略腳本004_TX_PriceInterval5K_LO.md",
        "strategy_name": "004_TX_PriceInterval5K_LO (ver 7)",
        "classification": "Trend Following",
        "direction": "Both",
        "entry_logic": {
            "long": ["mp=0 AND cond1 AND cond10 = L1/L2 stop at H", "mp<0 AND barssinceentry>=3session AND tight range = L3 reversal stop at H", "mp<0 AND tight AND c>(highw+loww)/2 AND fastMA>slowMA = L4 stop at H", "mp=0 AND cond11 AND H>lowd+avgCDDist = L5 stop at highd(0)"],
            "short": ["Symmetric S1-S5"]
        },
        "exit_logic": {"stop_loss": "Fixed entryprice +/- win_pts*0.5", "profit_target": "None", "trailing_stop": "None", "time_exit": "SetExitOnClose", "signal_exit": "LE/SE end Contract market"},
        "indicators": ["SMA avg C/H/L", "CountIf", "Daily OHLC", "Weekly H/L", "avgCDDist average candle distance"],
        "time_filters": ["t>=1300", "t<1345"],
        "key_insight": "PriceInterval: avgCDDist as dynamic zone measure; L3/L4 reversal re-entries when price tight while counter-positioned; L4 adds weekly mid-filter and dual MA cross; stop=0.5*win_pts implies 2:1 R:R",
        "tags": ["trend", "price-interval", "reversal-reentry", "MA", "weekly-filter", "intraday"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/(7)策略腳本GavinLu008_TX_DonChianChannel-D2106-K20m_LT.md",
        "strategy_name": "GavinLu008_TX_DonchianChannel_D2106_K20m (ver 7)",
        "classification": "Day Trading",
        "direction": "Both",
        "entry_logic": {
            "long": ["d<>d[1] new day market IF countif(DonHigh>DonHigh[1],2)=2 AND Close>EMA"],
            "short": ["d<>d[1] market IF DonLow descending AND Close<EMA"]
        },
        "exit_logic": {"stop_loss": "maxlist(EMA,DonAvg) / minlist(EMA,DonAvg)", "profit_target": "(lowd(0)+lowd(1))/2 for long; (highd(0)+highD(1))/2 for short", "trailing_stop": "None", "time_exit": "t>=1235; SetExitOnClose", "signal_exit": "BX/SX Max Profit market"},
        "indicators": ["EMA XAverage", "Highest/Lowest Donchian (DonHigh DonLow DonAvg)", "CountIf", "Daily High/Low"],
        "time_filters": ["t>=1235"],
        "key_insight": "Donchian expansion filter (DonHigh>DonHigh[1] for 2 bars = widening = momentum confirmed); entry AT new day open; profit target = 2-day average H/L = mean reversion; EMA+DonAvg combo as dynamic stop",
        "tags": ["Donchian", "day-trade", "channel-expansion", "EMA", "mean-reversion-exit"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/(7)策略腳本Jack106_TX_Neckline10K_L0.md",
        "strategy_name": "Jack106_TX_Neckline10K (ver 7)",
        "classification": "Breakout",
        "direction": "Both",
        "entry_logic": {
            "long": ["EntriesToday<2 AND k>in AND d>NoTradeday = B1 stop at (highd(1)+highd(2))*0.5", "barssinceentry<session AND positionprofit>0 = BH2 market add-on"],
            "short": ["EntriesToday<2 = S1 stop at (lowd(1)+lowd(2))*0.5", "condition20 AND c<o = BH1 market"]
        },
        "exit_logic": {"stop_loss": "None", "profit_target": "None", "trailing_stop": "None", "time_exit": "SetExitOnClose", "signal_exit": "WrongBuy if c<Lowest(L[1],2); WrongSS if c>Highest(H[1],2) = false breakout detection"},
        "indicators": ["Highest/Lowest", "CountIf", "Daily OHLC"],
        "time_filters": ["None"],
        "key_insight": "Neckline: entry at avg of last 2 days H/L = classic SR neckline; NoTradeday calendar filter; BH2 adds to winner within time window; WrongBuy/WrongSS = 2-bar H/L violation after entry = false breakout exit",
        "tags": ["breakout", "neckline", "add-on-winner", "false-breakout-filter", "intraday"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/(7)策略腳本katsu005_TXAM_LENGATE_3mK_DT-彥勝.md",
        "strategy_name": "katsu005_TXAM_LENGATE_3mK_DT (ver 7)",
        "classification": "Day Trading",
        "direction": "Both",
        "entry_logic": {"long": ["condition31 = LE1/LE2 stop at Average(H,k) MA-of-highs gate"], "short": ["condition31 = SE1/SE2 stop at Average(L,k)"]},
        "exit_logic": {"stop_loss": "None", "profit_target": "entryprice+AvgTrueRange(k)*ATR limit", "trailing_stop": "Highest(H,barssinceentry)/Lowest(L,barssinceentry) expanding trail", "time_exit": "calctime(sess1endtime,-2*barinterval)", "signal_exit": "L_T_out1 market; LD_LX at C"},
        "indicators": ["SMA Average H/L as dynamic gate", "Highest/Lowest trailing", "ATR", "CountIf"],
        "time_filters": ["t>=1330", "calctime(sess1endtime,-15*barinterval)"],
        "key_insight": "LENGATE: MA of highs/lows as dynamic entry gate; trailing stop = entire holding window (barssinceentry) = widens proportionally to time; ATR profit target; time gate opens near session end only",
        "tags": ["day-trade", "MA-gate", "ATR-target", "trailing-stop", "intraday"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/(7)策略腳本Ray101_TX_3 gate 6k_DO.md",
        "strategy_name": "Ray101_TX_3gate_6k_DO (ver 7)",
        "classification": "Day Trading",
        "direction": "Both",
        "entry_logic": {"long": ["condition1 = B1 stop at (HighD(0)+Highest(H,2))/2"], "short": ["DB=0 AND C>up AND condition10 = S1 stop at (LowD(0)+Lowest(L,2))/2"]},
        "exit_logic": {"stop_loss": "_EntryH-STL / _EntryL+STL fixed dollar from entry bar H/L", "profit_target": "None", "trailing_stop": "None", "time_exit": "calctime(sess1endtime,-1*barinterval)", "signal_exit": "Timeout market; CountIf(C<O,barssinceentry)>0.5*barssinceentry = majority bearish bars = exit"},
        "indicators": ["Highest/Lowest", "CountIf", "Daily OHLC", "CDP pivot mid=(H+L+C)/3; up/down zones"],
        "time_filters": ["calctime(sess1endtime,-1*barinterval)"],
        "key_insight": "3-gate: entry at midpoint of dayH and 2-bar highest H; CDP pivot bias filter; candle quality exit: CountIf(C<O,barssinceentry)>50% = majority bearish bars = market not following through = exit",
        "tags": ["day-trade", "CDP", "3-gate", "candle-quality-exit", "intraday"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/(7)策略腳本TimChen008_TX_15mKD202106_LT.md",
        "strategy_name": "TimChen008_TX_15mKD202106_LT (ver 7)",
        "classification": "Swing/Long-Term",
        "direction": "Both",
        "entry_logic": {"long": ["vMP=0 AND flagM=0 AND vTrendBull = stop at Highest(H,1)"], "short": ["vTrendBear = stop at Lowest(L,1)"]},
        "exit_logic": {"stop_loss": "None", "profit_target": "entryprice+iPFT*minmove*iff(positionprofit>0,1.5,1) = scales 1.5x if profitable", "trailing_stop": "Trl_LX: time-decaying trail = sell if vEH>=entryprice+iPFT-barssinceentry*decay", "time_exit": "T 0900-1330", "signal_exit": "maxEL market; PFT_LX limit"},
        "indicators": ["Stochastic(H,L,C,iLenKD)", "Highest(H,1)", "vEH entry-high tracking"],
        "time_filters": ["T>=0900", "T<1330"],
        "key_insight": "Stochastic vTrendBull/Bear direction filter; profit target scales 1.5x when already profitable; time-decay trailing: target-barssinceentry*decay = stop tightens as time passes forcing exit on stalling moves",
        "tags": ["swing", "stochastic", "time-decay-trailing", "scaled-profit-target", "intraday"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/(8) 策略腳本Shuen036_TX_ASI23K_V3_LT.md",
        "strategy_name": "Shuen036_TX_ASI23K_V3_LT (ver 8)",
        "classification": "Swing/Long-Term",
        "direction": "Both",
        "entry_logic": {"long": ["ASI cross MA = L market; condition30 = L-Guava limit"], "short": ["Symmetric"]},
        "exit_logic": {"stop_loss": "None", "profit_target": "None", "trailing_stop": "None", "time_exit": "SetExitOnClose", "signal_exit": "Time-L/Time-S at close"},
        "indicators": ["ASI", "SMA", "ATR", "Daily OHLC"],
        "time_filters": ["t>1100", "t>=1330"],
        "key_insight": "Ver 8 Shuen036 ASI -- same ASI+MA crossover core. Multi-version consistency confirms ASI cross MA as stable paradigm; condition30 and gap/range params likely tuned between versions.",
        "tags": ["ASI", "ATR", "MA", "swing", "versioned"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/(8)@@202102T98_LATETREND_4M_D0.md",
        "strategy_name": "202102T98_LATETREND_4M_D0 (ver 8)",
        "classification": "Day Trading",
        "direction": "Both",
        "entry_logic": {"long": ["condition1 = L in stop MAXlist(C,openD(0))", "condition2 = adaptive 2nd entry"], "short": ["Symmetric"]},
        "exit_logic": {"stop_loss": "Fixed +/- stp", "profit_target": "None", "trailing_stop": "None", "time_exit": "SetExitOnClose", "signal_exit": "TOB/TOS market"},
        "indicators": ["Daily OHLC", "CountIf consecutive candles"],
        "time_filters": ["t<1000", "t>1000", "t<1300"],
        "key_insight": "Ver 8 LATETREND -- same adaptive max(C,openD) entry confirmed. MAXlist(C,openD) captures both gap and intraday breakout in single stop order.",
        "tags": ["day-trade", "late-trend", "versioned", "intraday"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/(8)@@202106TAZ_CDP_4K_D0.md",
        "strategy_name": "202106T90_Normal_CDP_4K_D0 (ver 8)",
        "classification": "Trend Following / Breakout",
        "direction": "Both",
        "entry_logic": {"long": ["mp=0 AND T<1325 AND condition2 = stop at maxlist(close,opend(0))", "MA<nl = BMA/Bnhnl-3"], "short": ["Symmetric"]},
        "exit_logic": {"stop_loss": "entryprice*(1+-STP)", "profit_target": "CDP extension maxlist", "trailing_stop": "None", "time_exit": "1325 settlement", "signal_exit": "TOB/TOS market"},
        "indicators": ["SMA", "CDP (H+L+2C)/4 pivot zones", "CountIf"],
        "time_filters": ["T<1325", "time>=1325"],
        "key_insight": "Ver 8 CDP Normal -- CDP formula unchanged across versions. Confirms (H+L+2C)/4 as canonical pivot with only STP% and MA len varying between iterations.",
        "tags": ["CDP", "MA", "breakout", "versioned", "pivot"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/(8)@@202109T86_AZ_4K_D0.md",
        "strategy_name": "202109T86_AZ_Vol_4K_D0 (ver 8)",
        "classification": "Trend Following",
        "direction": "Both",
        "entry_logic": {"long": ["condition91 AND (cond11 OR cond21) AND EntriesToday<2 = stop at maxlist(opend,closed(1))", "cond24 = CT_L midpoint stop"], "short": ["Symmetric"]},
        "exit_logic": {"stop_loss": "None", "profit_target": "None", "trailing_stop": "None", "time_exit": "SetExitOnClose", "signal_exit": "L_I_PUNCH COUNTIF; B8% limit; TOB/TOS"},
        "indicators": ["SMA", "EMA TrueRange", "CountIf", "Daily OHLC"],
        "time_filters": ["time>=1325"],
        "key_insight": "Ver 8 AZ Vol -- DayVolatility filter and CT_L/CT_S midpoint counter-trends stable. 8% limit exit from prior close persistent.",
        "tags": ["trend", "volatility-filter", "versioned", "intraday"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/(8)Code_026_Sw_D_18min_KeltnerChange_YingCC3.md",
        "strategy_name": "Code026_Sw_D_18min_KeltnerChange_YingCC3 (ver 8)",
        "classification": "Day Trading",
        "direction": "Both",
        "entry_logic": {
            "long": ["mp<=0 AND Bflag=1 = B+ stop at HH+iff(var1<0,3,0)", "mp>=0 AND Sflag=1 = Rev+ stop at LL+stl*2 (flip from short)"],
            "short": ["mp<=0 AND Bflag=1 = Rev- stop at HH-stl*2", "mp>=0 AND Sflag=1 = SS- stop at LL-iff(var1<0,3,0)"]
        },
        "exit_logic": {"stop_loss": "None", "profit_target": "None", "trailing_stop": "None", "time_exit": "CalcTime(sess1endtime,-in*barinterval)", "signal_exit": "noP+: barssinceentry>2session AND c<entryprice AND 3-of-4 bars down = sell; S+: condition23"},
        "indicators": ["EMA XAverage Keltner base", "ATR KBW*AvgTrueRange bands", "Highest/Lowest HH/LL", "CountIf"],
        "time_filters": ["CalcTime(sess1firstbartime,in*barinterval)", "CalcTime(sess1endtime,-in*barinterval)"],
        "key_insight": "Keltner reversal: Rev+/Rev- flip position at 2*stl from channel boundary; var1<0 adds 3 ticks for microstructure; noP+ exit requires BOTH time threshold AND consecutive down bars = avoids premature exit on consolidation",
        "tags": ["Keltner", "reversal", "channel", "ATR", "day-trade", "position-flip"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/(8)策略PLA (S)003_TX_Score_2k_DT_20210618.md",
        "strategy_name": "003_TX_Score_2k_DT (ver 8 20210618)",
        "classification": "Day Trading",
        "direction": "Both",
        "entry_logic": {"long": ["condition3 = L-in market"], "short": ["condition3 = S-in market"]},
        "exit_logic": {"stop_loss": "None", "profit_target": "None", "trailing_stop": "None", "time_exit": "SetExitOnClose", "signal_exit": "score fade; day-range structural; unconditional"},
        "indicators": ["Score composite", "Highest/Lowest score", "Daily H/L"],
        "time_filters": ["t<1300"],
        "key_insight": "Ver 8 Score 2k -- score<highest(score,k)/2 momentum fade exit confirmed across versions as robust exit for composite scoring systems.",
        "tags": ["scoring", "day-trade", "versioned", "momentum-exit"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/(8)策略PLA(S) 005_TX_RSI_60k_LT_20210811.md",
        "strategy_name": "005_TX_RSI_60k_LT (ver 8 20210811)",
        "classification": "Swing/Long-Term",
        "direction": "Both",
        "entry_logic": {"long": ["mp=0 AND t<1100 = stop at h (RSI<20)"], "short": ["mp=0 AND t<1100 = stop at l (RSI>80)"]},
        "exit_logic": {"stop_loss": "None", "profit_target": "entryprice*(1+BP*0.01) / *(1-SP*0.01) limit", "trailing_stop": "None", "time_exit": "SetExitOnClose", "signal_exit": "Percentage limit"},
        "indicators": ["RSI(c,N)"],
        "time_filters": ["t<1100"],
        "key_insight": "Ver 8 RSI swing -- same RSI extreme + morning entry + percentage profit target. BP/SP% parameter optimization confirmed.",
        "tags": ["RSI", "swing", "percentage-target", "versioned"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/(9) 策略腳本Shuen036_TX_ASI23K_V3_LT.md",
        "strategy_name": "Shuen036_TX_ASI23K_V3_LT (ver 9)",
        "classification": "Swing/Long-Term",
        "direction": "Both",
        "entry_logic": {"long": ["ASI cross MA = L market; condition30 = L-Guava limit"], "short": ["Symmetric"]},
        "exit_logic": {"stop_loss": "None", "profit_target": "None", "trailing_stop": "None", "time_exit": "SetExitOnClose", "signal_exit": "Time-L/Time-S at close"},
        "indicators": ["ASI", "SMA", "ATR", "Daily OHLC"],
        "time_filters": ["t>1100", "t>=1330"],
        "key_insight": "Ver 9 Shuen036 ASI -- 9 iterations confirms ASI+MA combination stable. Extensive walk-forward optimization of condition30/len/gap averaging parameters.",
        "tags": ["ASI", "ATR", "MA", "swing", "versioned"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/(9)@@202106TAZ_CDP_4K_D0.md",
        "strategy_name": "202106T90_Normal_CDP_4K_D0 (ver 9)",
        "classification": "Trend Following / Breakout",
        "direction": "Both",
        "entry_logic": {"long": ["mp=0 AND T<1325 AND condition2 = stop at maxlist(close,opend(0))"], "short": ["Symmetric"]},
        "exit_logic": {"stop_loss": "entryprice*(1+-STP)", "profit_target": "CDP extension", "trailing_stop": "None", "time_exit": "1325", "signal_exit": "TOB/TOS market"},
        "indicators": ["SMA", "CDP (H+L+2C)/4", "CountIf"],
        "time_filters": ["T<1325", "time>=1325"],
        "key_insight": "Ver 9 CDP Normal -- CDP formula (H+L+2C)/4 canonical across all 9 versions. Structural zone system locked; only STP% and MA len vary. Represents a heavily tested pivot framework.",
        "tags": ["CDP", "MA", "breakout", "versioned", "pivot"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/(9)策略PLA (S)003_TX_Score_2k_DT_20210618.md",
        "strategy_name": "003_TX_Score_2k_DT (ver 9 20210618)",
        "classification": "Day Trading",
        "direction": "Both",
        "entry_logic": {"long": ["condition3 = L-in market"], "short": ["condition3 = S-in market"]},
        "exit_logic": {"stop_loss": "None", "profit_target": "None", "trailing_stop": "None", "time_exit": "SetExitOnClose", "signal_exit": "score fade; day-range structural; unconditional"},
        "indicators": ["Score composite", "Highest/Lowest score"],
        "time_filters": ["t<1300"],
        "key_insight": "Ver 9 Score 2k -- 9 versions confirms score momentum exit as proven robust paradigm. Score-based composite entry AND exit = self-consistent signal system.",
        "tags": ["scoring", "day-trade", "versioned", "momentum-exit"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/@@@173_TX_DVNormal_D0.md",
        "strategy_name": "173_TX_DVNormal_D0",
        "classification": "Trend Following",
        "direction": "Both",
        "entry_logic": {
            "long": ["DayVolatility(len,30)/len > Average(H-L,75*len)*filter AND k>in AND c>AmOpend_TX(0) = BE01 market"],
            "short": ["DayVolatility(len,30)/len < -Average(H-L,75*len)*filter AND k>in AND c<AmOpend_TX(0) = SE01 market"]
        },
        "exit_logic": {"stop_loss": "None", "profit_target": "None", "trailing_stop": "None", "time_exit": "t>=1335", "signal_exit": "sell/buytocover market"},
        "indicators": ["DayVolatility(len,30) custom", "SMA Average H-L", "AmOpend_TX(0) custom AM session open"],
        "time_filters": ["t>=1335"],
        "key_insight": "DayVolatility normalized: DayVol/len vs AvgHL*75*len compares current volatility rate to long-term range average; direction from AM session open (AmOpend_TX); 1 entry/day at late session >=1335; simplest volatility-trend combo",
        "tags": ["trend", "DayVolatility", "AM-open-bias", "late-session"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/@@202106T90_Normal_CDP_K_D0 (2).md",
        "strategy_name": "202106T90_Normal_CDP_K_D0 (copy-2)",
        "classification": "Trend Following / Breakout",
        "direction": "Both",
        "entry_logic": {"long": ["mp=0 AND T<1325 AND condition2 = Bnhnl-1 stop at maxlist(close,opend(0))", "MA<nl = BMA/Bnhnl-3"], "short": ["Symmetric"]},
        "exit_logic": {"stop_loss": "entryprice*(1+-STP)", "profit_target": "maxlist(entryprice+Closed(1)*STP, h, entryprice+(ah-cdp))", "trailing_stop": "None", "time_exit": "1325 settlement", "signal_exit": "TOB/TOS market"},
        "indicators": ["SMA", "CDP (H+L+2C)/4", "CountIf", "Daily OHLC"],
        "time_filters": ["T<1325", "time>=1325"],
        "key_insight": "Duplicate of CDP Normal -- confirms maxlist() profit formula: takes wider of percentage STP vs structural CDP extension (ah-cdp); guarantees minimum acceptable profit while capturing structural targets when market extends",
        "tags": ["CDP", "MA", "breakout", "maxlist-target", "copy"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/@@202106T90_Normal_CDP_K_D0.md",
        "strategy_name": "202106T90_Normal_CDP_K_D0 (original)",
        "classification": "Trend Following / Breakout",
        "direction": "Both",
        "entry_logic": {"long": ["mp=0 AND T<1325 AND condition2 = Bnhnl-1 stop at maxlist(close,opend(0))", "MA<nl = BMA or Bnhnl-3"], "short": ["Symmetric"]},
        "exit_logic": {"stop_loss": "entryprice*(1+-STP)", "profit_target": "maxlist(entryprice+Closed(1)*STP, h, entryprice+(ah-cdp))", "trailing_stop": "None", "time_exit": "SetExitOnClose; 1325", "signal_exit": "TOB/TOS market"},
        "indicators": ["SMA", "CDP (H+L+2C)/4 with ah/al/nh/nl zone derivation", "CountIf", "Daily OHLC"],
        "time_filters": ["T<1325", "time>=1325"],
        "key_insight": "Original CDP Normal canonical file. CDP zones: ah=cdp+(H-L) above high; nh=cdp*2-LowD(1) near high resistance; nl=2*LowD(1)-cdp near low support; al=cdp-(H-L) below low. Maxlist profit target ensures structural or percentage min whichever wider.",
        "tags": ["CDP", "MA", "breakout", "pivot-zones", "canonical", "intraday"]
    },
    {
        "source_file": "E:/投資交易/pla_md/logic/@@202106T90_STRONG.md",
        "strategy_name": "202106T90_CDP_STRONG",
        "classification": "Trend Following / Breakout",
        "direction": "Both",
        "entry_logic": {
            "long": ["mp=0 AND T<1325 AND EntriesToday<=2 = Bnhnl-1 stop at maxlist(close,opend(0))", "Lowd(0)>al AND Lowd(0)<cdp = buy (day low in al-cdp zone)", "Highd(0)<ah AND Highd(0)>cdp = Bcdp-1 (day high in cdp-ah zone)", "MA<cdp AND MA>nl = BMA stop", "MA>nl AND Lowd<nl AND CountIf(C<nl,K)<K/4 AND c>nh[K+1] = BL strong breakout (<25% bars below nl)", "opend(0)<ah AND MA<nh AND CountIf(C>nh AND c<ah,3)=3 = RB reversal (3 failed nh bars = fakeout)"],
            "short": ["Symmetric 6 short conditions"]
        },
        "exit_logic": {"stop_loss": "entryprice*(1+-STP)", "profit_target": "None", "trailing_stop": "None", "time_exit": "SetExitOnClose; SETTLEOut", "signal_exit": "SETTLEOut-L/S at close"},
        "indicators": ["SMA (MA + MAMid=Average(cdp,125) slow CDP MA)", "CDP (H+L+2C)/4 with 4 zones", "Highest/Lowest", "CountIf"],
        "time_filters": ["T>0900", "T<1000", "T>1000", "T<1300", "T<1325"],
        "key_insight": "STRONG CDP: 6 entry conditions vs 3 in Normal; adds zone entries (al-cdp, cdp-ah), strict breakout qualifier (CountIf<K/4 = <25% bars = true breakout), and RB reversal (3 failed nh bars = fakeout fade); MAMid=Average(cdp,125) as slow CDP MA trend filter; most complex CDP variant",
        "tags": ["CDP", "MA", "breakout", "multi-zone", "reversal", "STRONG", "fakeout-fade", "intraday"]
    }
]

output_path = 'C:/Users/admin/workspace/digital-immortality/results/digestion_log.jsonl'
with open(output_path, 'a', encoding='utf-8') as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

print(f'Appended {len(records)} records to {output_path}')
