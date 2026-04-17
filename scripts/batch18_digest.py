"""Batch 18 digestion append script - 35 files from E:/投資交易/pla_md/logic/"""
import json

entries = [
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/01.202109功課_Sing_010_TX_W_LT_改良版.md",
        "strategy_id": "Sing_010_TX_W_LT_improved",
        "strategy_name": "Sing_010_TX_W_LT 改良版",
        "classification": "swing",
        "direction": "both",
        "timeframe": "unknown",
        "instrument": "TX",
        "entry_logic": {
            "long": "condition10 AND condition30 → stop order at (H + iff(C[1]>O[1],C[1],H[1]))/2; midpoint of current high and prior close or high",
            "short": "condition10 AND condition30 → stop order (price unspecified)"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": None
        },
        "indicators": ["ATR: ATR(len) > ATR(len*2) as condition filter — entry only when short-term ATR exceeds long-term ATR (expanding volatility)"],
        "time_filter": None,
        "key_insight": "Entry price is the midpoint between current high and prior bar close (if bullish) or high — hybrid momentum/mean-reversion entry. ATR expansion filter ensures entries only in volatile regimes.",
        "tags": ["ATR", "swing", "volatility-filter"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/016_TX_KCForward_L0.md",
        "strategy_id": "CBrother_HW16_KCForward",
        "strategy_name": "016 TX KCForward L0 (Keltner Channel Forward)",
        "classification": "day-trade",
        "direction": "both",
        "timeframe": "intraday",
        "instrument": "TX",
        "entry_logic": {
            "long": "MP=0 AND 08:45<time<13:00 → stop at HighD(0); breakout of daily high",
            "short": "MP=0 AND 08:45<time<13:00 → stop at LowD(0); breakdown of daily low"
        },
        "exit_logic": {
            "stop_loss": "fixed: entryprice +/- SLPoint; also +/-10 pts hard stop",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "KC channel exit: sell when close crosses under KCDown with close<open; buytocover on symmetrical KCUp cross"
        },
        "indicators": ["ATR for Keltner Channel: KCMiddle +/- (KCATRNu * ATR(KCLen))", "KCTwoUp = KCMiddle + 2*KCATRNu*ATR(KCLen)", "Daily High/Low for entry stops"],
        "time_filter": ["08:45-13:00 entry window", "13:20 time exit"],
        "key_insight": "Keltner Channel used as exit signal rather than entry filter — price breaking KC boundary triggers exit not entry. Entry is pure daily high/low breakout within time window. Dual stops: ATR-based SLPoint and hard 10pt stop.",
        "tags": ["ATR", "Keltner-Channel", "breakout", "day-trade", "daily-HL"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/016_TX_KCForward_L0 (2).md",
        "strategy_id": "CBrother_HW16_KCForward_dup2",
        "strategy_name": "016 TX KCForward L0 (copy 2)",
        "classification": "day-trade",
        "direction": "both",
        "timeframe": "intraday",
        "instrument": "TX",
        "entry_logic": {"long": "same as CBrother_HW16_KCForward", "short": "same as CBrother_HW16_KCForward"},
        "exit_logic": {"stop_loss": "same", "profit_target": None, "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": "same"},
        "indicators": ["same"],
        "time_filter": ["08:45-13:00"],
        "key_insight": "Duplicate of CBrother_HW16_KCForward.",
        "tags": ["duplicate", "ATR", "Keltner-Channel", "breakout", "day-trade"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/016_TX_KCForward_L0 (3).md",
        "strategy_id": "CBrother_HW16_KCForward_dup3",
        "strategy_name": "016 TX KCForward L0 (copy 3)",
        "classification": "day-trade",
        "direction": "both",
        "timeframe": "intraday",
        "instrument": "TX",
        "entry_logic": {"long": "same as CBrother_HW16_KCForward", "short": "same"},
        "exit_logic": {"stop_loss": "same", "profit_target": None, "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": "same"},
        "indicators": ["same"],
        "time_filter": ["08:45-13:00"],
        "key_insight": "Duplicate of CBrother_HW16_KCForward.",
        "tags": ["duplicate", "ATR", "Keltner-Channel", "breakout", "day-trade"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/016_TX_KCForward_L0 (4).md",
        "strategy_id": "CBrother_HW16_KCForward_dup4",
        "strategy_name": "016 TX KCForward L0 (copy 4)",
        "classification": "day-trade",
        "direction": "both",
        "timeframe": "intraday",
        "instrument": "TX",
        "entry_logic": {"long": "same as CBrother_HW16_KCForward", "short": "same"},
        "exit_logic": {"stop_loss": "same", "profit_target": None, "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": "same"},
        "indicators": ["same"],
        "time_filter": ["08:45-13:00"],
        "key_insight": "Duplicate of CBrother_HW16_KCForward.",
        "tags": ["duplicate", "ATR", "Keltner-Channel", "breakout", "day-trade"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/017_TXA_CHANNEL_LO.md",
        "strategy_id": "b3017_TXA_CHANNEL_LO",
        "strategy_name": "017 TXA Channel LO (Multi-session Channel Breakout)",
        "classification": "day-trade",
        "direction": "both",
        "timeframe": "daily",
        "instrument": "TXA",
        "entry_logic": {
            "long": "Day (09:00-12:45): BuyCond AND open within HLRange → stop at vClose+HLRange-CountIf(C>O,12); gap-up with SellCond → stop at RefHigh+AvgRange(LenA)",
            "short": "Day: BuyCond AND open within range → stop at vClose-HLRange+CountIf(C<O,12); Night (after 16:00 or before 03:00): BuyCond AND LC → stop at RefLow-AvgRange(LenA)"
        },
        "exit_logic": {
            "stop_loss": "StpL (long) and StpS (short) dynamic stops",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "sell/buytocover at bar close on M.CloseL/M.CloseS signal"
        },
        "indicators": ["SMA: Average(Range,LenA) for range calculation", "Highest(High,3) and Lowest(Low,3) for 3-bar extremes", "CountIf(Close>=Open,3)>=3: 3 consecutive bullish bars condition", "TypicalPrice vs AmOpenD_TX/AmCloseD_TX session reference", "HLRange from H-L"],
        "time_filter": ["09:00-12:45 day session", "16:00 or before 03:00 night session", "05:00 reset"],
        "key_insight": "Dual-session strategy. Day session CountIf adjustment on entry stop level: more consecutive same-direction bars narrows entry threshold. Night session uses ATR-extended reference levels. TypicalPrice vs session open/close as directional filter.",
        "tags": ["channel", "breakout", "day-trade", "night-session", "CountIf", "daily", "multi-session"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/017_TXA_CHANNEL_LO (2).md",
        "strategy_id": "b3017_TXA_CHANNEL_LO_dup2",
        "strategy_name": "017 TXA Channel LO (copy 2)",
        "classification": "day-trade",
        "direction": "both",
        "timeframe": "daily",
        "instrument": "TXA",
        "entry_logic": {"long": "same as b3017_TXA_CHANNEL_LO", "short": "same"},
        "exit_logic": {"stop_loss": "same", "profit_target": None, "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": "same"},
        "indicators": ["same"],
        "time_filter": ["same"],
        "key_insight": "Duplicate of b3017_TXA_CHANNEL_LO.",
        "tags": ["duplicate", "channel", "breakout", "day-trade"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/017_TXA_CHANNEL_LO (3).md",
        "strategy_id": "b3017_TXA_CHANNEL_LO_dup3",
        "strategy_name": "017 TXA Channel LO (copy 3)",
        "classification": "day-trade",
        "direction": "both",
        "timeframe": "daily",
        "instrument": "TXA",
        "entry_logic": {"long": "same", "short": "same"},
        "exit_logic": {"stop_loss": "same", "profit_target": None, "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": "same"},
        "indicators": ["same"],
        "time_filter": ["same"],
        "key_insight": "Duplicate of b3017_TXA_CHANNEL_LO.",
        "tags": ["duplicate", "channel", "breakout", "day-trade"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/017_TXA_CHANNEL_LO (4).md",
        "strategy_id": "b3017_TXA_CHANNEL_LO_dup4",
        "strategy_name": "017 TXA Channel LO (copy 4)",
        "classification": "day-trade",
        "direction": "both",
        "timeframe": "daily",
        "instrument": "TXA",
        "entry_logic": {"long": "same", "short": "same"},
        "exit_logic": {"stop_loss": "same", "profit_target": None, "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": "same"},
        "indicators": ["same"],
        "time_filter": ["same"],
        "key_insight": "Duplicate of b3017_TXA_CHANNEL_LO.",
        "tags": ["duplicate", "channel", "breakout", "day-trade"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/017_TXA_CO4_DO_5min.md",
        "strategy_id": "b3017_TXA_CO4_DO_5min",
        "strategy_name": "017 TXA CO4 DO 5min (Consecutive 4-bar Daily Open Breakout 5min)",
        "classification": "day-trade",
        "direction": "both",
        "timeframe": "5m",
        "instrument": "TXA",
        "entry_logic": {
            "long": "Pre-2017/05/15: MP=0 AND entries<=4 AND 08:45<t<13:00 AND bars>3min → market. Post-2017/05/15: MP=0 AND entries<=3 AND t<23:59 → market (night enabled). Conditions: OpenD(0)>CloseD(1)+5 AND consecutive higher highs AND bullish candles",
            "short": "Pre-2017 daytime: market; post-2017: CountIf(C>O,4)>=4 AND CountIf(H-L>n3,4)>=3 AND H>H[1] → night short"
        },
        "exit_logic": {
            "stop_loss": "entryprice + win_pts*0.8 protective",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "highest(h,n2)=highadp(0) AND CountIf(L<L[1],3)>=3 AND CountIf(C<O,3)>=3 → sell; CountIf(L<lowest[1],4)>=4 AND CountIf(C<O,5)>=5 → sell; C<entry AND bearish → sell"
        },
        "indicators": ["Highest/Lowest for N-bar extremes", "OpenD CloseD HighD LowD for daily reference", "CountIf for consecutive bar conditions", "highadp(0)/lowadp(0) all-day H/L"],
        "time_filter": ["08:45-13:00 pre-2017", "all session post-2017", "13:33 and 04:30 night exits"],
        "key_insight": "Date-conditioned regime switch on 2017/05/15 when TXA night session opened. Entry uses gap-up open vs prior close (+5pts) plus consecutive higher highs as momentum confirmation. Exit uses multi-condition reversal detection via CountIf patterns.",
        "tags": ["5m", "breakout", "day-trade", "night-session", "CountIf", "date-regime-switch", "gap"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/017_TXA_CO4_DO_5min (2).md",
        "strategy_id": "b3017_TXA_CO4_DO_5min_dup2",
        "strategy_name": "017 TXA CO4 DO 5min (copy 2)",
        "classification": "day-trade",
        "direction": "both",
        "timeframe": "5m",
        "instrument": "TXA",
        "entry_logic": {"long": "same as b3017_TXA_CO4_DO_5min", "short": "same"},
        "exit_logic": {"stop_loss": "same", "profit_target": None, "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": "same"},
        "indicators": ["same"],
        "time_filter": ["same"],
        "key_insight": "Duplicate of b3017_TXA_CO4_DO_5min.",
        "tags": ["duplicate", "breakout", "day-trade"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/018_TXF_JumpRange3K_DT.md",
        "strategy_id": "b3018_TXF3K_JumpRange_DT",
        "strategy_name": "018 TXF JumpRange3K DT (Jump Range 3000pt Day Trade)",
        "classification": "day-trade",
        "direction": "both",
        "timeframe": "intraday (bar-interval dependent)",
        "instrument": "TXF",
        "entry_logic": {
            "long": "condition70 → stop at myH (session high reference)",
            "short": "condition70 → stop at myL (session low reference)"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose; CalcTime(sess1endtime,-1*barinterval) pre-close exit",
            "signal_exit": "sell/buytocover at market on reversal"
        },
        "indicators": ["CountIf(C>O or C>C[1], 5)>3: 4+ of 5 bars bullish by close direction OR close>prior close (permissive OR logic)"],
        "time_filter": ["08:45-15:00 main session", "15:00-05:00 night", "calctime relative session exits"],
        "key_insight": "CountIf uses OR logic (close>open OR close>prior close) more permissive than strict bullish-candle count — catches momentum even on small-body bars. Session-aware exits via calctime relative to boundaries. 3K in name = 3000-point jump range entry threshold.",
        "tags": ["jump-range", "breakout", "day-trade", "session-aware", "CountIf"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/019_TX_LongBandForwardTrade_L0.md",
        "strategy_id": "CBrother_HW19_LongBandForward",
        "strategy_name": "019 TX LongBandForwardTrade L0 (Wide Range Afternoon Forward Trade)",
        "classification": "day-trade",
        "direction": "both",
        "timeframe": "intraday",
        "instrument": "TX",
        "entry_logic": {
            "long": "MP=0 AND D>NoTradeday AND High>TwoDayHigh AND (H-TwoDayLow)>Close*Action → market",
            "short": "same conditions → market"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "FixSL-1/FixSL-2 at market"
        },
        "indicators": ["TwoDayHigh = max(HighD(1),HighD(2))", "TwoDayLow = min(LowD(1),LowD(2))", "Action: H-L > Close*Action volatility % filter"],
        "time_filter": ["time>13:00 afternoon only"],
        "key_insight": "Afternoon-only after 13:00 when day range established. Requires: new 2-day high (trend confirmation) AND range exceeds Action% of price (wide enough). NoTradeday avoids expiry. Both long/short on same conditions — system likely separates via separate condition flags.",
        "tags": ["wide-range", "breakout", "day-trade", "afternoon-entry", "two-day-reference"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/019_TX_LongBandForwardTrade_L0 (2).md",
        "strategy_id": "CBrother_HW19_LongBandForward_dup2",
        "strategy_name": "019 TX LongBandForwardTrade L0 (copy 2)",
        "classification": "day-trade",
        "direction": "both",
        "timeframe": "intraday",
        "instrument": "TX",
        "entry_logic": {"long": "same as CBrother_HW19_LongBandForward", "short": "same"},
        "exit_logic": {"stop_loss": None, "profit_target": None, "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": "same"},
        "indicators": ["same"],
        "time_filter": ["time>13:00"],
        "key_insight": "Duplicate of CBrother_HW19_LongBandForward.",
        "tags": ["duplicate", "wide-range", "breakout", "day-trade"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/020_TX_3DAYBRK_LO.md",
        "strategy_id": "c3020_TX_3DAYBRK_LO",
        "strategy_name": "020 TX 3DAYBRK LO (3-Day Breakout with ADX Filter)",
        "classification": "trend-following",
        "direction": "both",
        "timeframe": "daily",
        "instrument": "TX",
        "entry_logic": {
            "long": "MP=0 AND Condition41 (ADX>ADXN AND entries=0) AND Condition31 → stop at max(HighD(1),HighD(2),HighD(3)); REVBS re-entry: barssinceentry<=15 → stop at entryprice+HLRange/2",
            "short": "MP=0 AND Condition41 AND Condition31 → stop at min(LowD(1),LowD(2),LowD(3)); REVBS: stop at entryprice-HLRange/2"
        },
        "exit_logic": {
            "stop_loss": "fixed: entryprice+stp",
            "profit_target": None,
            "trailing_stop": "SetPercentTrailing(AvgPrice*0.02*BigPointValue, 30): 2% trailing 30% activation",
            "time_exit": "SetExitOnClose on last trading day",
            "signal_exit": None
        },
        "indicators": ["ADX(20) > ADXN: trend strength filter required at entry", "Pivot: middle=(H+L+C)/3 prior day; HH=middle*2-LowD(1); LL=middle*2-HighD(1)", "AvgPrice for trailing stop sizing"],
        "time_filter": ["T>09:30"],
        "key_insight": "Three-layer: ADX filter (trending) + 3-day breakout (entry) + REVBS re-entry within 15 bars at midpoint of prior range. 2% trailing with 30% activation. Pivot HH/LL for Condition31 reference levels.",
        "tags": ["ADX", "breakout", "trend-following", "3-day", "pivot", "trailing-stop", "REVBS"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/021_TXA_2N_DO_3min.md",
        "strategy_id": "b3021_TXA_2N_DO_3min",
        "strategy_name": "021 TXA 2N DO 3min (2-Entry Night Dual-Open 3min)",
        "classification": "day-trade",
        "direction": "both",
        "timeframe": "3m",
        "instrument": "TXA",
        "entry_logic": {
            "long": "MP=0 AND entries<=2 AND condition31 → market (max 2 entries per session)",
            "short": "MP=0 AND entries<=2 AND condition31 → market"
        },
        "exit_logic": {
            "stop_loss": "entryprice +/- win_pts*0.8",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "C<entryprice-50 → sell; H[3]=highadp(0) AND CountIf(L<=L[1] AND C<O,3)>=3 AND L<lowest(l,3)[1]-10 → sell (topping); HIGHEST(H,2*n5)>HIGHEST(H,n5) AND CountIf(L<L[1],4)>=4 AND mid<avg_close AND C<highadp-ratio*(H-L) → sell (exhaustion)"
        },
        "indicators": ["Highest/Lowest N-bar", "Daily Open/Close", "CountIf patterns", "highadp(0)/lowadp(0)", "REVBS: Highest(H,2*n5)>Highest(H,n5) = long lookback high exceeds short = momentum weakening"],
        "time_filter": ["08:45-15:00 day session", "15:00-03:00/05:00 night session"],
        "key_insight": "Three exit patterns: (1) simple price-below-entry, (2) topping candle at all-day high with 3 lower lows + bearish candles + new low, (3) exhaustion via long>short lookback high (momentum divergence) + 4 lower lows + price at extended zone by session range ratio.",
        "tags": ["3m", "breakout", "day-trade", "night-session", "exhaustion", "CountIf", "momentum-exit"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/021_TXA_2N_DO_3min (2).md",
        "strategy_id": "b3021_TXA_2N_DO_3min_dup2",
        "strategy_name": "021 TXA 2N DO 3min (copy 2)",
        "classification": "day-trade",
        "direction": "both",
        "timeframe": "3m",
        "instrument": "TXA",
        "entry_logic": {"long": "same as b3021_TXA_2N_DO_3min", "short": "same"},
        "exit_logic": {"stop_loss": "same", "profit_target": None, "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": "same"},
        "indicators": ["same"],
        "time_filter": ["same"],
        "key_insight": "Duplicate of b3021_TXA_2N_DO_3min.",
        "tags": ["duplicate", "3m", "breakout", "day-trade"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/022_TX_TwoDayHighLow_L0.md",
        "strategy_id": "CBrother_HW22_TwoDayHL",
        "strategy_name": "022 TX TwoDayHighLow L0 (2-Day H/L Gap-Aware Range Trade)",
        "classification": "day-trade",
        "direction": "both",
        "timeframe": "intraday",
        "instrument": "TX",
        "entry_logic": {
            "long": "K>=2 AND open in 2-day range → market (no gap, range continuation); K>=2 AND open above TwoDayHigh → stop at HighD(0) (gap-up breakout confirm)",
            "short": "K>=2 AND open in 2-day range → market; K>=2 AND open below TwoDayLow → stop at LowD(0) (gap-down confirm)"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": "(OpenD(0)+HighD(1))*0.5 long; (OpenD(0)+LowD(1))*0.5 short — midpoint of today open and prior day extreme",
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "DayOut-1/FixOut-1 at market"
        },
        "indicators": ["TwoDayHigh = max(HighD(1),HighD(2))", "TwoDayLow = min(LowD(1),LowD(2))", "K counter: K=1 on new day K++ per bar; K>=2 prevents first-bar entries", "LastTradeDay expiry guard"],
        "time_filter": ["time>13:20 afternoon close-out"],
        "key_insight": "Dual logic by gap status: no gap → market order (mean reversion within range); gap → stop order at daily extreme (momentum confirm). Profit target = midpoint of today open and prior day extreme — mean reversion target for in-range, momentum target for gap. K>=2 prevents first-bar execution.",
        "tags": ["two-day-reference", "day-trade", "gap", "mean-reversion", "breakout", "profit-target"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/022_TX_TwoDayHighLow_L0 (2).md",
        "strategy_id": "CBrother_HW22_TwoDayHL_dup2",
        "strategy_name": "022 TX TwoDayHighLow L0 (copy 2)",
        "classification": "day-trade",
        "direction": "both",
        "timeframe": "intraday",
        "instrument": "TX",
        "entry_logic": {"long": "same as CBrother_HW22_TwoDayHL", "short": "same"},
        "exit_logic": {"stop_loss": None, "profit_target": "same", "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": "same"},
        "indicators": ["same"],
        "time_filter": ["same"],
        "key_insight": "Duplicate of CBrother_HW22_TwoDayHL.",
        "tags": ["duplicate", "two-day-reference", "day-trade"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/023_TX_WEEKBRKOUT_LO.md",
        "strategy_id": "a3023_TX_WEEKBRKOUT_LO",
        "strategy_name": "023 TX WEEKBRKOUT LO (Weekly Range Breakout with Shrinking Stop)",
        "classification": "day-trade",
        "direction": "both",
        "timeframe": "weekly",
        "instrument": "TX",
        "entry_logic": {
            "long": "09:00<=time<12:00 AND entries<=1 → stop at HighD(0)",
            "short": "09:00<=time<12:00 AND entries<=1 → stop at LowD(0)"
        },
        "exit_logic": {
            "stop_loss": "SetStopLoss((AvgPrice*0.01 - BarsSinceEntry/3)*BigPointValue): shrinking stop from 1% decreasing 1/3pt per bar",
            "profit_target": None,
            "trailing_stop": "SetPercentTrailing(AvgPrice*0.027*BigPointValue, 30): 2.7% trailing 30% activation; exit on close crossing WeekAvg",
            "time_exit": "SetExitOnClose",
            "signal_exit": "close cross under/over WeekAvg (weekly MA)"
        },
        "indicators": ["WeekAvg: weekly moving average", "AvgPrice for stop sizing", "BigPointValue for contract conversion"],
        "time_filter": ["09:00-12:00 morning entry only"],
        "key_insight": "Shrinking stop formula (1% - BarsSinceEntry/3) tightens as trade ages — protects growing profit. 2.7% trailing (wider than 020 2%) suited for weekly breakouts expecting larger moves. Weekly MA cross as trend exit. Morning-only entries avoid afternoon chop.",
        "tags": ["weekly", "breakout", "day-trade", "trailing-stop", "shrinking-stop", "weekly-MA"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/023_TX_WEEKBRKOUT_LO (2).md",
        "strategy_id": "a3023_TX_WEEKBRKOUT_LO_dup2",
        "strategy_name": "023 TX WEEKBRKOUT LO (copy 2)",
        "classification": "day-trade",
        "direction": "both",
        "timeframe": "weekly",
        "instrument": "TX",
        "entry_logic": {"long": "same as a3023_TX_WEEKBRKOUT_LO", "short": "same"},
        "exit_logic": {"stop_loss": "same", "profit_target": None, "trailing_stop": "same", "time_exit": "SetExitOnClose", "signal_exit": "same"},
        "indicators": ["same"],
        "time_filter": ["09:00-12:00"],
        "key_insight": "Duplicate of a3023_TX_WEEKBRKOUT_LO.",
        "tags": ["duplicate", "weekly", "breakout", "day-trade"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/024_TXF_RSI_60m_FLT.md",
        "strategy_id": "a3024_TXF_RSI_60m_FLT",
        "strategy_name": "024 TXF RSI 60m FLT (RSI Afternoon 1-Hour Filter)",
        "classification": "mean-reversion",
        "direction": "both",
        "timeframe": "60m",
        "instrument": "TXF",
        "entry_logic": {
            "long": "vRSI crosses over x threshold → market buy",
            "short": "vRSI crosses over x (downward cross implied) → market sell"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": None
        },
        "indicators": ["RSI(Close, Len): standard configurable RSI", "x: crossover threshold level"],
        "time_filter": ["12:45<t<=13:45: 1-hour afternoon window"],
        "key_insight": "RSI crossover (fires only when RSI actively changes direction at threshold) within tight 1-hour afternoon window. Likely a filter component or signal trigger within a larger system. Very restricted trade frequency by design.",
        "tags": ["RSI", "60m", "mean-reversion", "afternoon-filter", "crossover"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/024_TXF_RSI_60m_FLT (2).md",
        "strategy_id": "a3024_TXF_RSI_60m_FLT_dup2",
        "strategy_name": "024 TXF RSI 60m FLT (copy 2)",
        "classification": "mean-reversion",
        "direction": "both",
        "timeframe": "60m",
        "instrument": "TXF",
        "entry_logic": {"long": "same as a3024_TXF_RSI_60m_FLT", "short": "same"},
        "exit_logic": {"stop_loss": None, "profit_target": None, "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": None},
        "indicators": ["same"],
        "time_filter": ["12:45-13:45"],
        "key_insight": "Duplicate of a3024_TXF_RSI_60m_FLT.",
        "tags": ["duplicate", "RSI", "mean-reversion"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/026_TX_RSIForwardTrade_L0 說明檔.md",
        "strategy_id": "CBrother_HW26_RSIForward",
        "strategy_name": "026 TX RSIForwardTrade L0 (RSI Overbought Momentum Entry)",
        "classification": "trend-following",
        "direction": "both",
        "timeframe": "intraday",
        "instrument": "TX",
        "entry_logic": {
            "long": "FirstTrade AND RSI(7) crosses over BuyLine=72 → stop at RSIDayHigh+5 (5pts above day high at RSI overbought moment)",
            "short": "FirstTrade AND RSIShort → stop at RSIDayLow-5; SecondTrade AND RSI<SellLine=15 → stop at TwoDayLow (extreme oversold second entry)"
        },
        "exit_logic": {
            "stop_loss": "fixed: entryprice +/- SLPoint=120 pts",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": None
        },
        "indicators": ["RSI(Close,7): short-period RSI for sensitivity", "BuyLine=72 (overbought momentum entry)", "SellLine=15 (extreme oversold continuation short)", "RSIDayHigh = HighD(0) snapshot at RSI signal", "TwoDayLow = min of 2-day lows"],
        "time_filter": ["02:00/01:45 night reset", "time>13:00 primary afternoon window"],
        "key_insight": "Counterintuitive RSI use: overbought RSI (72) triggers LONG not short — this is momentum forward trade not mean reversion. Entry +5pts above day high at overbought confirms breakout. Short at RSI<15 is momentum-continuation short (extreme oversold goes lower). SLPoint=120pts large for trending positions. SecondTrade allows pyramid into short at 2-day low.",
        "tags": ["RSI", "momentum", "forward-trade", "overbought-entry", "day-trade", "complex", "pyramid"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/026_TX_RSIForwardTrade_L0 說明檔 (2).md",
        "strategy_id": "CBrother_HW26_RSIForward_dup2",
        "strategy_name": "026 TX RSIForwardTrade L0 (copy 2)",
        "classification": "trend-following",
        "direction": "both",
        "timeframe": "intraday",
        "instrument": "TX",
        "entry_logic": {"long": "same as CBrother_HW26_RSIForward", "short": "same"},
        "exit_logic": {"stop_loss": "SLPoint=120", "profit_target": None, "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": None},
        "indicators": ["same"],
        "time_filter": ["same"],
        "key_insight": "Duplicate of CBrother_HW26_RSIForward.",
        "tags": ["duplicate", "RSI", "momentum"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/026_TX_RSIForwardTrade_L0 說明檔 (3).md",
        "strategy_id": "CBrother_HW26_RSIForward_dup3",
        "strategy_name": "026 TX RSIForwardTrade L0 (copy 3)",
        "classification": "trend-following",
        "direction": "both",
        "timeframe": "intraday",
        "instrument": "TX",
        "entry_logic": {"long": "same", "short": "same"},
        "exit_logic": {"stop_loss": "same", "profit_target": None, "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": None},
        "indicators": ["same"],
        "time_filter": ["same"],
        "key_insight": "Duplicate of CBrother_HW26_RSIForward.",
        "tags": ["duplicate", "RSI", "momentum"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/026_TX_RSIForwardTrade_L0 說明檔 (4).md",
        "strategy_id": "CBrother_HW26_RSIForward_dup4",
        "strategy_name": "026 TX RSIForwardTrade L0 (copy 4)",
        "classification": "trend-following",
        "direction": "both",
        "timeframe": "intraday",
        "instrument": "TX",
        "entry_logic": {"long": "same", "short": "same"},
        "exit_logic": {"stop_loss": "same", "profit_target": None, "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": None},
        "indicators": ["same"],
        "time_filter": ["same"],
        "key_insight": "Duplicate of CBrother_HW26_RSIForward.",
        "tags": ["duplicate", "RSI", "momentum"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/027_TX_DayContrarian_LO_300M.md",
        "strategy_id": "b3027_TX_DayContrarian_300M",
        "strategy_name": "027 TX DayContrarian LO 300M (5-Hour Bar Contrarian with Pyramid)",
        "classification": "day-trade",
        "direction": "both",
        "timeframe": "300m",
        "instrument": "TX",
        "entry_logic": {
            "long": "MP=0 AND dayk>1 AND D<>LastTradeday AND flagM=0 → LE1/LE2 market; MP>0 AND barssinceentry>=1 → BHLE1 add-on 1 bar after entry",
            "short": "MP=0 AND dayk>1 AND flagM=0 → SE1/SE2 market; condition21 → BHSE1 add-on"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "sell(maxEL) / buytocover(maxES) at market"
        },
        "indicators": ["dayk: day counter (dayk>1 = not first day)", "flagM: signal memory flag (=0 unused)", "barssinceentry for add-on timing"],
        "time_filter": None,
        "key_insight": "300-minute (5-hour) bars = 1-2 bars per session. Add-on (BHLE1/BHSE1) fires exactly 1 bar after initial entry — pyramids into winning direction. flagM=0 prevents duplicate signals. dayk>1 avoids first-day noise. No stop loss — pure signal-driven exits. Contrarian name = entry against prior bar direction.",
        "tags": ["300m", "day-trade", "contrarian", "pyramid", "intraday-trend"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/027_TX_DayContrarian_LO_300M (2).md",
        "strategy_id": "b3027_TX_DayContrarian_300M_dup2",
        "strategy_name": "027 TX DayContrarian LO 300M (copy 2)",
        "classification": "day-trade",
        "direction": "both",
        "timeframe": "300m",
        "instrument": "TX",
        "entry_logic": {"long": "same as b3027_TX_DayContrarian_300M", "short": "same"},
        "exit_logic": {"stop_loss": None, "profit_target": None, "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": "same"},
        "indicators": ["same"],
        "time_filter": None,
        "key_insight": "Duplicate of b3027_TX_DayContrarian_300M.",
        "tags": ["duplicate", "300m", "day-trade", "contrarian"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/027_TX_MACDADX_L0.md",
        "strategy_id": "CBrother_HW27_MACDADX",
        "strategy_name": "027 TX MACDADX L0 (MACD + Accelerating ADX Afternoon Trend)",
        "classification": "trend-following",
        "direction": "both",
        "timeframe": "intraday",
        "instrument": "TX",
        "entry_logic": {
            "long": "MP=0 AND D<>NoTradeday AND LongSignal AND ADX>max(ADX[1],ADX[2],ADX[3]) → stop at max(HighD(0),aa) OR HighD(0)",
            "short": "same with ShortSignal AND ADX accelerating → stop at min(LowD(0),bb) OR LowD(0)"
        },
        "exit_logic": {
            "stop_loss": "fixed: entryprice-SLPoint",
            "profit_target": None,
            "trailing_stop": None,
            "time_exit": "SetExitOnClose",
            "signal_exit": "LCOut-1 (MACD cross) / TwoDayOut-1 (2-day level) / SCOut-1 at market"
        },
        "indicators": ["MACD(Close, FastLen, SlowLen)", "XAverage(MACDVal, MACDLen): signal line", "MACDDiffVal = MACD - Signal (histogram)", "ADX(ADXLen): trend strength", "ADX accelerating: ADX > max(ADX[1],ADX[2],ADX[3]) — ADX at new 3-bar high = trend gaining strength", "aa = session-running max HighD(0); bb = session-running min LowD(0)"],
        "time_filter": ["time>13:00 afternoon entry only"],
        "key_insight": "ADX acceleration filter (ADX at new 3-bar high) more demanding than simple threshold — trend must be gaining strength not just present. Dual entry stops: current HighD(0) and session-running extreme aa/bb. Three exit types: MACD cross, 2-day reference breach, general signal. Afternoon-only for confirmed trend setups.",
        "tags": ["MACD", "ADX", "trend-following", "accelerating-ADX", "afternoon-entry", "dual-entry-stops"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/027_TX_MACDADX_L0 (2).md",
        "strategy_id": "CBrother_HW27_MACDADX_dup2",
        "strategy_name": "027 TX MACDADX L0 (copy 2)",
        "classification": "trend-following",
        "direction": "both",
        "timeframe": "intraday",
        "instrument": "TX",
        "entry_logic": {"long": "same as CBrother_HW27_MACDADX", "short": "same"},
        "exit_logic": {"stop_loss": "same", "profit_target": None, "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": "same"},
        "indicators": ["same"],
        "time_filter": ["time>13:00"],
        "key_insight": "Duplicate of CBrother_HW27_MACDADX.",
        "tags": ["duplicate", "MACD", "ADX", "trend-following"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/028_TX_17mFFG_LOS.md",
        "strategy_id": "a3028_TX_17mFFG_LOS",
        "strategy_name": "028 TX 17mFFG LOS (17-min FFG Adaptive Lookback Long/Short)",
        "classification": "day-trade",
        "direction": "both",
        "timeframe": "intraday (bar-interval dependent)",
        "instrument": "TX",
        "entry_logic": {
            "long": "condition1 AND CountIf(H>H[1],4)>=2 AND CountIf(L>L[1],n3)>=n3/2 (mixed momentum 50% threshold) → market; BE1: condition1 AND higher-high/low majority; BE2: positionprofit(1)>=0 AND ent>0 → stop at exitprice(1) (add-on at prior exit)",
            "short": "C<O → market (simple bearish bar); SE1: condition1 AND momentum conditions; SE2: condition2 AND le>0 AND L<exitprice(1) → stop at exitprice(1)"
        },
        "exit_logic": {
            "stop_loss": None,
            "profit_target": "H>=AmClosed_TX(1)*(1+0.09): 9% above prior session close (explosive move target)",
            "trailing_stop": None,
            "time_exit": "SetExitOnClose; session boundary calctime exits",
            "signal_exit": "sell(maxEL); BX2: condition21 AND (CountIf lower lows + range expansion OR wide bearish bar); 9% target → sell"
        },
        "indicators": ["Highest/Lowest with adaptive mul: mul=1+ratio if prior trade lost else 1 (adaptive lookback!)", "CountIf with 50% ratio thresholds (>=4*0.5, >=n3*0.5)", "AmClosed_TX(1): prior session all-day close", "positionprofit(1): first position unrealized profit for add-on", "countif(positionprofit(1)<0,3)>=1: trigger to expand lookback after losing streak"],
        "time_filter": ["Session-based: calctime(sess1/sess2 start/endtime, +/-barinterval) dual session"],
        "key_insight": "Most innovative feature: adaptive lookback mul — after a losing trade, multiplier expands lookback window (more conservative). This is anti-martingale in lookback space. Add-on BE2/SE2 at prior exit price when first position profitable. Short has two-speed entry: simple (C<O) and complex (condition1). 9% above prior session close = very wide target for explosive breakouts.",
        "tags": ["17m", "breakout", "day-trade", "adaptive-lookback", "add-on", "session-aware", "complex", "anti-martingale"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/028_TX_17mFFG_LOS (2).md",
        "strategy_id": "a3028_TX_17mFFG_LOS_dup2",
        "strategy_name": "028 TX 17mFFG LOS (copy 2)",
        "classification": "day-trade",
        "direction": "both",
        "timeframe": "intraday (bar-interval dependent)",
        "instrument": "TX",
        "entry_logic": {"long": "same as a3028_TX_17mFFG_LOS", "short": "same"},
        "exit_logic": {"stop_loss": None, "profit_target": "same", "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": "same"},
        "indicators": ["same"],
        "time_filter": ["same"],
        "key_insight": "Duplicate of a3028_TX_17mFFG_LOS.",
        "tags": ["duplicate", "17m", "breakout", "day-trade"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/028_TX_17mFFG_LOS (3).md",
        "strategy_id": "a3028_TX_17mFFG_LOS_dup3",
        "strategy_name": "028 TX 17mFFG LOS (copy 3)",
        "classification": "day-trade",
        "direction": "both",
        "timeframe": "intraday (bar-interval dependent)",
        "instrument": "TX",
        "entry_logic": {"long": "same", "short": "same"},
        "exit_logic": {"stop_loss": None, "profit_target": "same", "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": "same"},
        "indicators": ["same"],
        "time_filter": ["same"],
        "key_insight": "Duplicate of a3028_TX_17mFFG_LOS.",
        "tags": ["duplicate", "17m", "breakout", "day-trade"]
    },
    {
        "batch": 18,
        "file": "E:/投資交易/pla_md/logic/028_TX_17mFFG_LOS (4).md",
        "strategy_id": "a3028_TX_17mFFG_LOS_dup4",
        "strategy_name": "028 TX 17mFFG LOS (copy 4)",
        "classification": "day-trade",
        "direction": "both",
        "timeframe": "intraday (bar-interval dependent)",
        "instrument": "TX",
        "entry_logic": {"long": "same", "short": "same"},
        "exit_logic": {"stop_loss": None, "profit_target": "same", "trailing_stop": None, "time_exit": "SetExitOnClose", "signal_exit": "same"},
        "indicators": ["same"],
        "time_filter": ["same"],
        "key_insight": "Duplicate of a3028_TX_17mFFG_LOS.",
        "tags": ["duplicate", "17m", "breakout", "day-trade"]
    }
]

output_path = "C:/Users/admin/workspace/digital-immortality/results/digestion_log.jsonl"
with open(output_path, "a", encoding="utf-8") as f:
    for entry in entries:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print(f"Appended {len(entries)} entries to {output_path}")
