import json

entries = [
    {
        'file': 'E:/投資交易/pla_md/logic/OSCAR034_TXALL_CHAIKIN_FDL.md',
        'strategy_name': 'OSCAR034_TXALL_CHAIKIN_FDL',
        'classification': 'Trend Following',
        'direction': 'both',
        'timeframe': 'intraday',
        'entry_logic': {
            'long': ['Value1[Shift]<>0 stop at (AmHighD_TX(0)+AmCloseD_TX(1))/2 - pivot midpoint entry'],
            'short': ['MP=0 AND flagM=0 AND Condition1 stop at (AmLowD_TX(0)+AmCloseD_TX(1))/2']
        },
        'exit_logic': {
            'stop_loss': 'SetStopLoss(AvgPrice*STL*Bigpointvalue)',
            'profit_target': 'none',
            'trailing_stop': 'Setpercenttrailing(AvgPrice*STL*Bigpointvalue, 30-BarsSinceEntry/20) - time-decaying trailing',
            'time_exit': 'SetExitOnClose',
            'signal_exit': 'sell/buytocover maxEL/maxES next bar market'
        },
        'indicators': ['EMA/XAverage on TRValue', 'Chaikin oscillator', 'AmHighD/AmLowD/AmCloseD (daily OHLC)'],
        'time_filters': [],
        'key_concepts': ['Chaikin momentum filter', 'pivot midpoint entry: (day_high + prev_close)/2', 'time-decaying trailing stop: tighter as trade ages', 'EMA smoothed true range as trend signal'],
        'tags': ['chaikin', 'trend', 'pivot-entry', 'trailing-stop', 'EMA'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/OSCAR035_TXALL_RSIMOM_FDL.md',
        'strategy_name': 'OSCAR035_TXALL_RSIMOM_FDL',
        'classification': 'Day Trading',
        'direction': 'both',
        'timeframe': 'intraday',
        'entry_logic': {
            'long': ['MP=0 AND flagM=0 AND Condition1 stop at minlist(AmHighD_TX(0), AmHighD_TX(1)) - 2-day high breakout'],
            'short': ['MP=0 AND flagM=0 AND Condition1 stop at maxlist(AmLowD_TX(0), AmLowD_TX(1)) - 2-day low breakdown']
        },
        'exit_logic': {
            'stop_loss': 'SetStopLoss(AvgPrice*STL*Bigpointvalue)',
            'profit_target': 'none',
            'trailing_stop': 'Setpercenttrailing(AvgPrice*STL*2*Bigpointvalue, 30-BarsSinceEntry/20) - 2x wider trailing',
            'time_exit': 'SetExitOnClose',
            'signal_exit': 'sell/buytocover maxEL/maxES next bar market'
        },
        'indicators': ['RSI(High, Len) = MomL', 'RSI(Low, Len) = MomS', 'AmHighD_TX / AmLowD_TX'],
        'time_filters': [],
        'key_concepts': ['RSI momentum on High/Low series separately for L/S', '2-day high/low for entry stop', 'wider trailing 2x vs OSCAR034 Chaikin version', 'separate RSI thresholds for long vs short'],
        'tags': ['RSI', 'momentum', 'day-trade', 'trailing-stop', '2-day-HL'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/OpenD0105_6K_DT.md',
        'strategy_name': 'Work_TX_OpenD0105_6K_DO',
        'classification': 'Day Trading',
        'direction': 'both',
        'timeframe': '6m',
        'entry_logic': {
            'long': ['k>=kin AND t<=1200 AND mp=0: L and L2 entries', 'condition21: open RL entry', 'k>=kin AND t<=1200 AND EntriesToday=1: L_again re-entry'],
            'short': ['k>=kin AND t<=1200 AND mp=0: RS entry', 'y=0 AND lowd(0)<dn AND L>max(dn,opend(0)) AND lowd(0)<lowd(1): S entry', 'z=0 AND (c+opend(0)<closed(1)+closed(2)): bearish open structure entry']
        },
        'exit_logic': {
            'stop_loss': 'none',
            'profit_target': 'none',
            'trailing_stop': 'none',
            'time_exit': 'SetExitOnClose',
            'signal_exit': 'none'
        },
        'indicators': ['OpenD(0)', 'HighD/LowD daily levels', 'dn (Donchian lower)', 'session K-bar count (k>=kin)'],
        'time_filters': ['t<=1200'],
        'key_concepts': ['open gap structure: compare open vs prior closes for trend bias', 'K-count gate: only enter after k>=kin bars elapsed', 're-entry after first trade in same direction', 'day low breakdown: lowd(0)<lowd(1) bearish confirmation'],
        'tags': ['6m', 'day-trade', 'open-gap', 'donchian', 'k-count'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/PLA (2).md',
        'strategy_name': 'a28Sa29Gift',
        'classification': 'Day Trading',
        'direction': 'both',
        'timeframe': 'intraday',
        'entry_logic': {
            'long': ['condition3 stop at maxlist(highada(0), dhigh[1]) - current high or yesterday high'],
            'short': ['condition3 stop at minlist(lowada(0), dlow[1]) - current low or yesterday low']
        },
        'exit_logic': {
            'stop_loss': 'none',
            'profit_target': 'none',
            'trailing_stop': 'none',
            'time_exit': 'SetExitOnClose',
            'signal_exit': 'none'
        },
        'indicators': ['highada(0) / lowada(0) - adjusted daily high/low', 'dhigh[1] / dlow[1] - previous day HL'],
        'time_filters': ['t>0900', 't<1330'],
        'key_concepts': ['adaptive HL vs prior day HL for entry stop selection', 'no stop or target - relies on EOD exit only'],
        'tags': ['day-trade', 'adaptive-HL', 'prior-day-HL', 'EOD-exit'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/PLA.md',
        'strategy_name': '_b24b2eCF_TX_Z00_MAArea_FD1',
        'classification': 'Trend Following / Breakout',
        'direction': 'both',
        'timeframe': 'intraday',
        'entry_logic': {
            'long': ['absvalue(Area)>valveArea AND T in cTime1 or cTime2 AND mp=0 -> B entry'],
            'short': ['Area>valveArea -> S entry (bearish area dominance)']
        },
        'exit_logic': {
            'stop_loss': 'none',
            'profit_target': 'none',
            'trailing_stop': 'none',
            'time_exit': 'SetExitOnClose',
            'signal_exit': 'sell Bx Bad / Bx TO M / Bx TO AM next bar market'
        },
        'indicators': ['MA Area - cumulative gap between price and MA', 'SMA implied'],
        'time_filters': ['cTime1Begin <= T < cTime1Inter', 'T >= cTime2Begin OR T < cTime2Inter'],
        'key_concepts': ['Area = cumulative signed distance price-vs-MA = trend strength proxy', 'valveArea = minimum conviction threshold before entry', 'dual time window logic', 'marked COMPLEX - manual review needed'],
        'tags': ['MA-area', 'trend', 'time-window', 'complex', 'area-threshold'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/P_CDP_TXF_1_DT.md',
        'strategy_name': 'P_CDP_TXF_1_DT_V2',
        'classification': 'Day Trading',
        'direction': 'both',
        'timeframe': 'intraday',
        'entry_logic': {
            'long': ['time>=0930 AND opend(0)>closed(1) AND c>cdp -> buy stop at dh (gap up + above CDP)'],
            'short': ['time>=0930 -> sell stop at dl']
        },
        'exit_logic': {
            'stop_loss': 'none',
            'profit_target': 'none',
            'trailing_stop': 'highest(high,barsSinceEntry)-ReturnB long; lowest(low,barsSinceEntry)+ReturnS short',
            'time_exit': 'time>=1344',
            'signal_exit': 'sell/buytocover next bar at market'
        },
        'indicators': ['CDP = (H+L+2C)/4', 'dh/dl = daily high/low', 'opend/closed = daily open/close', 'Highest/Lowest since entry'],
        'time_filters': ['time>=0930 entry', 'time>=1344 exit'],
        'key_concepts': ['CDP central pivot: (H+L+2C)/4', 'gap up = open>prev_close = bullish session bias', 'close>CDP = price above central pivot = long confirmation', 'trailing tracks full trade range minus return buffer'],
        'tags': ['CDP', 'pivot', 'day-trade', 'gap', 'trailing-stop', 'daily-HL'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/QTC01.md',
        'strategy_name': 'T_QTC501_TX_CDP_D0',
        'classification': 'Day Trading',
        'direction': 'both',
        'timeframe': 'intraday',
        'entry_logic': {
            'long': ['DB=0 AND c<=NL AND C>AL AND countif(O<C, bars_ac) >= half: NL-L market order', 'condition2: AH-L market', 'mp<0 AND barssinceentry>2 AND condition2: RB stop at max(h[n+1],h[n])'],
            'short': ['condition1: NH-S market', 'DS<=2 AND c<AL AND countif(O>C) >= half: AL-S market', 'mp<0 AND AB=0: RS stop at min(l[n+1],l[n])']
        },
        'exit_logic': {
            'stop_loss': 'none',
            'profit_target': 'none',
            'trailing_stop': 'none',
            'time_exit': 'SetExitOnClose',
            'signal_exit': 'none'
        },
        'indicators': ['CDP levels: NH/NL/AH/AL zones', 'countif(O<C) bullish bar ratio', 'daily session bar count (ac)'],
        'time_filters': [],
        'key_concepts': ['CDP multi-level: NH (neutral high), NL (neutral low), AH, AL', 'bar-majority: >50% bullish bars confirms trend direction', 'reversal entry after 2+ bars in position (RB/RS)', 'price-zone market orders vs stop orders'],
        'tags': ['CDP', 'pivot-levels', 'bar-majority', 'reversal', 'day-trade'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/QTCXXX.md',
        'strategy_name': 'QTCXXX_TX_GapeaterV2_FL0',
        'classification': 'Day Trading',
        'direction': 'both',
        'timeframe': 'intraday',
        'entry_logic': {
            'long': ['condition70 AND condition30 AND Daytradetime=0 -> stop at h'],
            'short': ['condition70 AND condition30 AND Daytradetime=0 -> stop at l']
        },
        'exit_logic': {
            'stop_loss': 'none',
            'profit_target': 'none',
            'trailing_stop': 'none',
            'time_exit': 'SetExitOnClose',
            'signal_exit': 'sell/buytocover next bar market'
        },
        'indicators': ['Gap detection (Gapeater)', 'High/Low breakout'],
        'time_filters': ['t>1500', 't<0500 overnight', 't>0845', 't<1345', 't>=1335 exit'],
        'key_concepts': ['Gapeater: trade gap fill or continuation', 'condition70/30 = dual thresholds (gap size + momentum)', 'Daytradetime=0 = first entry of day only', 'multi-session: overnight + day windows'],
        'tags': ['gap', 'day-trade', 'breakout', 'first-entry-only', 'multi-session'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/QX523T13.md',
        'strategy_name': '_QX523T13',
        'classification': 'Trend Following / Breakout',
        'direction': 'both',
        'timeframe': 'intraday',
        'entry_logic': {
            'long': ['TrueRange < AvgTrueRange(BarsBack)*Fb -> stop at highest(High,len)-2*MinMove'],
            'short': ['TrueRange < AvgTrueRange(BarsBack)*Fb -> stop at lowest(Low,len-2)+2*MinMove']
        },
        'exit_logic': {
            'stop_loss': 'SetStopLoss(PL*BigPointValue)',
            'profit_target': 'SetProfitTarget(PF*BigPointValue)',
            'trailing_stop': 'none',
            'time_exit': 'none',
            'signal_exit': 'Sell TrendS / LX_Bal / SX_Bal next bar market'
        },
        'indicators': ['TrueRange vs AvgTrueRange(BarsBack)*Fb - volatility contraction', 'Highest(High,len) / Lowest(Low,len)', 'SMA Average(close,21)'],
        'time_filters': [],
        'key_concepts': ['TR < ATR*Fb = volatility squeeze entry trigger', 'Fb = fraction (e.g. 0.7 = TR must be <70% of ATR)', 'inside bar / low-vol contraction before breakout', 'fixed PL/PF stop+target in points'],
        'tags': ['volatility-contraction', 'ATR', 'breakout', 'inside-bar', 'fixed-stop'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/QX532T25.md',
        'strategy_name': '_QX532T25',
        'classification': 'Trend Following / Breakout',
        'direction': 'both',
        'timeframe': 'intraday',
        'entry_logic': {
            'long': ['MP<>1 AND MagicLuckyNet(FTR_LE)>0 AND RSIGapL<buylevel AND RSI(Close,12)>50 -> stop at Highest(High,NBarS)'],
            'short': ['same conditions -> stop at Lowest(Low,NBarL)']
        },
        'exit_logic': {
            'stop_loss': 'SetStopLoss(PL*BigPointValue)',
            'profit_target': 'SetProfitTarget(PF*BigPointValue)',
            'trailing_stop': 'none',
            'time_exit': 'none',
            'signal_exit': 'Sell TrendS / LX_Bal / SX_Bal next bar market'
        },
        'indicators': ['MagicLuckyNet(FTR_LE) proprietary trend filter', 'RSI(Close,12) > 50 trend confirmation', 'RSIGapL = RSI gap indicator', 'Highest/Lowest channel'],
        'time_filters': [],
        'key_concepts': ['MagicLuckyNet>0 = net long signal from proprietary system', 'RSI>50 = momentum above midline = trend confirm', 'RSIGapL<buylevel = pullback in RSI gap', 'triple filter: trend + momentum + pullback'],
        'tags': ['MagicLuckyNet', 'RSI', 'trend', 'triple-filter', 'proprietary'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/QX533T28.md',
        'strategy_name': '_QX533T28',
        'classification': 'Trend Following / Breakout',
        'direction': 'both',
        'timeframe': 'intraday',
        'entry_logic': {
            'long': ['MP<>-1 AND MagicLuckyNet(FTR_LE)<0 AND Close<LOrder[LenA] -> stop at Highest(High,Highbar) - counter-trend pullback'],
            'short': ['Low<=Supp -> stop at Lowest(Low,LowBar) - support breakdown']
        },
        'exit_logic': {
            'stop_loss': 'SetStopLoss(PL*BigPointValue)',
            'profit_target': 'SetProfitTarget(PF*BigPointValue)',
            'trailing_stop': 'none',
            'time_exit': 'none',
            'signal_exit': 'Sell TrendS / LX_Bal / SX_Bal next bar market'
        },
        'indicators': ['MagicLuckyNet(FTR_LE)', 'Average(AvgPrice,LenA) = LOrder - MA of avg price', 'Support level (Supp)', 'Highest/Lowest channel'],
        'time_filters': [],
        'key_concepts': ['counter-trend long: net short signal but price below MA = oversold reversal', 'support breakdown short: direct breakdown entry', 'LOrder = MA of AvgPrice vs Close = more stable mean', 'two different philosophies in one strategy'],
        'tags': ['counter-trend', 'MagicLuckyNet', 'support-breakdown', 'MA-avgprice'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/QX534T21.md',
        'strategy_name': '_QX534T21',
        'classification': 'Trend Following / Breakout',
        'direction': 'both',
        'timeframe': 'intraday',
        'entry_logic': {
            'long': ['MP<>1 AND MagicLuckyNet(FTR_LE)>0 AND OBVL>AvgL1 -> B1 stop at Highest(High,NBarL)', 'MP<>-1 AND MagicLuckyNet(FTR_SE)<0 AND OBVS<AvgS1 -> 3DL stop at RangeH+Avg(Range,BarLen)'],
            'short': ['MP<>1 AND MagicLuckyNet(FTR_LE)>0 AND OBVL>AvgL1 -> S1 stop at Lowest(Low,NBarS)', 'EntriesToday=0 AND MagicLuckyNet(FTR_AE)>0 AND Close<RangeH -> 3DS stop at RangeL-Avg(Range,BarLen)']
        },
        'exit_logic': {
            'stop_loss': 'SetStopLoss(PL*BigPointValue)',
            'profit_target': 'SetProfitTarget(PF*BigPointValue)',
            'trailing_stop': 'none',
            'time_exit': 'none',
            'signal_exit': 'Sell TrendS / LX_Bal / SX_Bal next bar market'
        },
        'indicators': ['OBV(L)/OBV(S) vs their averages', 'MagicLuckyNet 3 modes: FTR_LE/SE/AE', 'RangeH/RangeL + Average(Range,BarLen)'],
        'time_filters': ['EntriesToday=0 for 3DS'],
        'key_concepts': ['OBV>AvgOBV = volume confirms trend direction', 'MagicLuckyNet 3 modes: LE/SE/AE', '3D range-extended entry: stop at range boundary + avg bar range', 'first-entry-only gate for 3DS variant'],
        'tags': ['OBV', 'MagicLuckyNet', 'range-extension', 'volume-confirm', 'multi-entry'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/QX543T23.md',
        'strategy_name': '_QX543T23',
        'classification': 'Trend Following / Breakout',
        'direction': 'both',
        'timeframe': 'intraday',
        'entry_logic': {
            'long': ['Cond_LE AND MagicLuckyNet(FTR_LE)>0 AND Curve1>Curve2 -> stop at Avg(High,HighBar)+Avg(Range,BarLen)'],
            'short': ['Cond_LE AND Curve1>Curve2 -> stop at Avg(Low,LowBar)-Avg(Range,BarLen)', 'Cond_SE AND MagicLuckyNet(FTR_SE)<0 AND Curve1<Curve2 -> market order']
        },
        'exit_logic': {
            'stop_loss': 'SetStopLoss(PL*BigPointValue)',
            'profit_target': 'SetProfitTarget(PF*BigPointValue)',
            'trailing_stop': 'none',
            'time_exit': 'none',
            'signal_exit': 'Sell TrendS / LX_Bal / SX_Bal next bar market'
        },
        'indicators': ['MagicLuckyNet(FTR_LE/SE)', 'Curve1 vs Curve2 - dual curve momentum', 'Average(High/Low, HighBar/LowBar)', 'Average(Range, BarLen)'],
        'time_filters': [],
        'key_concepts': ['Curve1>Curve2 = momentum curve crossover for direction', 'range-extended stop: avg_high + avg_range = volatility buffer', 'short has market-order fast variant on curve cross', 'asymmetric Cond_LE/Cond_SE for L vs S'],
        'tags': ['curve-crossover', 'MagicLuckyNet', 'range-extension', 'momentum', 'asymmetric'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/Q_CT00_000M_PT.md',
        'strategy_name': 'Q_CT00_000M_PT_KD_base',
        'classification': 'Breakout',
        'direction': 'both',
        'timeframe': 'intraday',
        'entry_logic': {
            'long': ['MKP=0 AND Q_TX_EntryTime(0900,1100,2130,0130) AND Q_TX_EntryContract<1 -> stop'],
            'short': ['same conditions -> stop']
        },
        'exit_logic': {
            'stop_loss': 'none',
            'profit_target': 'none',
            'trailing_stop': 'Highest(High,barsSinceEntry)-ReturnB / Lowest(Low,barsSinceEntry)+ReturnS',
            'time_exit': 'SetExitOnClose',
            'signal_exit': 'none'
        },
        'indicators': ['Stochastic KD', 'Highest/Lowest since entry for trailing', 'Q_TX_EntryTime / Q_TX_EntryContract'],
        'time_filters': ['Q_TX_EntryTime(0900,1100,2130,0130) 4 entry windows'],
        'key_concepts': ['Q_TX framework: modular entry time + contract count gating', 'trailing stop via barsSinceEntry high/low with ReturnB/S offset', 'Q_CT series: systematic testing same framework across different indicators'],
        'tags': ['Q_CT-series', 'KD', 'trailing-stop', 'entry-time-filter', 'modular'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/Q_CT00_Free (2).md',
        'strategy_name': 'Q_CT00_Free_A_v2',
        'classification': 'Breakout',
        'direction': 'both',
        'timeframe': 'unknown',
        'entry_logic': {
            'long': ['marketposition=0 -> stop at Highest(High,Len)'],
            'short': ['marketposition=0 -> stop at BB lower']
        },
        'exit_logic': {
            'stop_loss': 'none',
            'profit_target': 'none',
            'trailing_stop': 'none',
            'time_exit': 'SetExitOnClose',
            'signal_exit': 'sell 1 total next bar entryprice*(1+Profit) limit; buytocover entryprice*(1-Profit) limit'
        },
        'indicators': ['Bollinger Bands: BollingerBand(Close,Len,NumDevs)', 'Highest(High,Len)'],
        'time_filters': [],
        'key_concepts': ['BB + highest channel free template', 'exit at fixed % profit from entry (limit order)', 'duplicate of Q_CT00_Free series v2'],
        'tags': ['BB', 'channel-breakout', 'fixed-profit-exit', 'template', 'duplicate'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/Q_CT00_Free (3).md',
        'strategy_name': 'Q_CT00_Free_A_v3',
        'classification': 'Breakout',
        'direction': 'both',
        'timeframe': 'unknown',
        'entry_logic': {
            'long': ['marketposition=0 -> stop at Highest(High,Len)'],
            'short': ['marketposition=0 -> stop at BB lower']
        },
        'exit_logic': {
            'stop_loss': 'none',
            'profit_target': 'none',
            'trailing_stop': 'none',
            'time_exit': 'SetExitOnClose',
            'signal_exit': 'profit limit exit at entry*(1+/-Profit)'
        },
        'indicators': ['Bollinger Bands', 'Highest channel'],
        'time_filters': [],
        'key_concepts': ['duplicate of Q_CT00_Free base v3'],
        'tags': ['BB', 'channel-breakout', 'duplicate'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/Q_CT00_Free.md',
        'strategy_name': 'Q_CT00_Free_A_base',
        'classification': 'Breakout',
        'direction': 'both',
        'timeframe': 'unknown',
        'entry_logic': {
            'long': ['marketposition=0 -> stop at Highest(High,Len)'],
            'short': ['marketposition=0 -> stop at BB lower (BollingerBand negative devs)']
        },
        'exit_logic': {
            'stop_loss': 'none',
            'profit_target': 'none',
            'trailing_stop': 'none',
            'time_exit': 'SetExitOnClose',
            'signal_exit': 'sell 1 total next bar entryprice*(1+Profit) limit; buytocover entryprice*(1-Profit) limit'
        },
        'indicators': ['BollingerBand(Close,Len,+/-NumDevs)', 'Highest(High,Len)'],
        'time_filters': [],
        'key_concepts': ['free template base: BB lower for short, highest channel for long', 'exit at fixed % profit via limit order', 'no stop loss - pure profit-target or EOD exit only'],
        'tags': ['BB', 'channel-breakout', 'profit-target-limit', 'no-stop', 'template'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/Q_CT01_060M_KD.md',
        'strategy_name': 'Q_CT01_060M_KD',
        'classification': 'Breakout',
        'direction': 'both',
        'timeframe': '60m',
        'entry_logic': {
            'long': ['MKP=0 AND Q_TX_EntryTime(0900,1100,2130,0130) AND Q_TX_EntryContract<1 -> stop (KD crossover)'],
            'short': ['same conditions -> stop (KD crossover)']
        },
        'exit_logic': {
            'stop_loss': 'none',
            'profit_target': 'none',
            'trailing_stop': 'Highest(High,barsSinceEntry)-ReturnB / Lowest(Low,barsSinceEntry)+ReturnS',
            'time_exit': 'SetExitOnClose',
            'signal_exit': 'none'
        },
        'indicators': ['Stochastic KD', 'Highest/Lowest since entry', 'Q_TX_EntryTime / Q_TX_EntryContract'],
        'time_filters': ['0900', '1100', '2130', '0130 entry windows'],
        'key_concepts': ['60m KD stochastic as trend filter for breakout', 'barsSinceEntry trailing - tighten as trade progresses', 'Q_CT modular: same framework swapping indicator'],
        'tags': ['60m', 'KD', 'stochastic', 'trailing-stop', 'Q_CT-series'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/Q_CT02_060M_RSI.md',
        'strategy_name': 'Q_CT02_060M_RSI',
        'classification': 'Breakout',
        'direction': 'both',
        'timeframe': '60m',
        'entry_logic': {
            'long': ['MKP=0 AND Q_TX_EntryTime AND Q_TX_EntryContract<1 -> stop (RSI on High)'],
            'short': ['same -> stop (RSI on Low)']
        },
        'exit_logic': {
            'stop_loss': 'none',
            'profit_target': 'none',
            'trailing_stop': 'Highest/Lowest since entry',
            'time_exit': 'SetExitOnClose',
            'signal_exit': 'none'
        },
        'indicators': ['RSI(High,LengthB) = RSB', 'RSI(Low,LengthS) = RSS', 'Q_TX_SessionOpenD (JUP)', 'Highest/Lowest since entry'],
        'time_filters': ['Q_TX_EntryTime 4 windows'],
        'key_concepts': ['RSI applied to High series for long, Low series for short = directional RSI', 'JUP = session open reference for intraday direction', 'Q_CT02 = RSI variant of modular framework on 60m'],
        'tags': ['60m', 'RSI', 'High-Low-series', 'Q_CT-series', 'trailing-stop'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/Q_CT03_060M_CCI.md',
        'strategy_name': 'Q_CT03_060M_CCI',
        'classification': 'Breakout',
        'direction': 'both',
        'timeframe': '60m',
        'entry_logic': {
            'long': ['MKP=0 AND Q_TX_EntryTime AND Q_TX_EntryContract<1 -> stop (CCI filter)'],
            'short': ['same -> stop']
        },
        'exit_logic': {
            'stop_loss': 'none',
            'profit_target': 'none',
            'trailing_stop': 'Highest/Lowest since entry',
            'time_exit': 'SetExitOnClose',
            'signal_exit': 'none'
        },
        'indicators': ['CCI', 'Highest/Lowest since entry'],
        'time_filters': ['Q_TX_EntryTime 4 windows'],
        'key_concepts': ['CCI variant of Q_CT modular (Q_CT03)', 'same exit as Q_CT01/02, only filter indicator changes'],
        'tags': ['60m', 'CCI', 'Q_CT-series', 'trailing-stop'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/Q_CT04_060M_MTM.md',
        'strategy_name': 'Q_CT04_060M_MTM',
        'classification': 'Breakout',
        'direction': 'both',
        'timeframe': '60m',
        'entry_logic': {
            'long': ['MKP=0 AND Q_TX_EntryTime AND Q_TX_EntryContract<1 -> stop (Momentum)'],
            'short': ['same -> stop']
        },
        'exit_logic': {
            'stop_loss': 'none',
            'profit_target': 'none',
            'trailing_stop': 'Highest/Lowest since entry',
            'time_exit': 'SetExitOnClose',
            'signal_exit': 'none'
        },
        'indicators': ['Momentum (price change over N bars)', 'Highest/Lowest since entry'],
        'time_filters': ['Q_TX_EntryTime 4 windows'],
        'key_concepts': ['Momentum as trend filter', 'Q_CT04 = MTM variant', 'systematic indicator comparison: KD vs RSI vs CCI vs MTM'],
        'tags': ['60m', 'momentum', 'MTM', 'Q_CT-series'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/Q_CT05_060M_OBV.md',
        'strategy_name': 'Q_CT05_060M_OBV',
        'classification': 'Breakout',
        'direction': 'both',
        'timeframe': '60m',
        'entry_logic': {
            'long': ['MKP=0 AND Q_TX_EntryTime AND Q_TX_EntryContract<1 -> stop (OBV filter)'],
            'short': ['same -> stop']
        },
        'exit_logic': {
            'stop_loss': 'none',
            'profit_target': 'none',
            'trailing_stop': 'Highest/Lowest since entry',
            'time_exit': 'SetExitOnClose',
            'signal_exit': 'none'
        },
        'indicators': ['OBV (On-Balance Volume)', 'Highest/Lowest since entry'],
        'time_filters': ['Q_TX_EntryTime 4 windows'],
        'key_concepts': ['OBV confirms volume supports directional move before entry', 'Q_CT05 = volume-based variant', 'volume on futures = indirect commitment proxy'],
        'tags': ['60m', 'OBV', 'volume', 'Q_CT-series'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/Q_CT06_060M_MACD.md',
        'strategy_name': 'Q_CT06_060M_MACD',
        'classification': 'Trend Following / Breakout',
        'direction': 'both',
        'timeframe': '60m',
        'entry_logic': {
            'long': ['MKP=0 AND Q_TX_EntryTime AND Q_TX_EntryContract<1 -> stop (MACD on High)'],
            'short': ['same -> stop (MACD on Low)']
        },
        'exit_logic': {
            'stop_loss': 'none',
            'profit_target': 'none',
            'trailing_stop': 'Highest/Lowest since entry',
            'time_exit': 'SetExitOnClose',
            'signal_exit': 'none'
        },
        'indicators': ['MACD(High, FastB, SlowB) = DIB', 'XAverage(DIB, MACDLengthB) = DEB signal line', 'MACD(Low, FastS, SlowS) for short'],
        'time_filters': ['Q_TX_EntryTime 4 windows'],
        'key_concepts': ['MACD on High for long signal, Low for short = H/L asymmetric MACD', 'DIB/DEB crossover = long trigger', 'Q_CT06 = MACD H/L variant'],
        'tags': ['60m', 'MACD', 'High-Low-series', 'Q_CT-series', 'trend'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/Q_CT07_060M_DMI.md',
        'strategy_name': 'Q_CT07_060M_DMI',
        'classification': 'Breakout',
        'direction': 'both',
        'timeframe': '60m',
        'entry_logic': {
            'long': ['MKP=0 AND Q_TX_EntryTime AND Q_TX_EntryContract<1 -> stop (DMI/ADX filter)'],
            'short': ['same -> stop']
        },
        'exit_logic': {
            'stop_loss': 'none',
            'profit_target': 'none',
            'trailing_stop': 'Highest/Lowest since entry',
            'time_exit': 'SetExitOnClose',
            'signal_exit': 'none'
        },
        'indicators': ['DMI +DI/-DI crossover', 'ADX threshold', 'Highest/Lowest since entry'],
        'time_filters': ['Q_TX_EntryTime 4 windows'],
        'key_concepts': ['+DI>-DI = bullish DMI; ADX>threshold = trend strength confirm', 'Q_CT07 = directional movement variant', 'DMI filters: direction + strength before breakout entry'],
        'tags': ['60m', 'DMI', 'ADX', 'directional-movement', 'Q_CT-series'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/Q_CT08_060M_BB.md',
        'strategy_name': 'Q_CT08_060M_BB',
        'classification': 'Trend Following / Breakout',
        'direction': 'both',
        'timeframe': '60m',
        'entry_logic': {
            'long': ['MKP=0 AND Q_TX_EntryTime AND Q_TX_EntryContract<1 -> stop (BB on High filter)'],
            'short': ['same -> stop (BB on Low)']
        },
        'exit_logic': {
            'stop_loss': 'none',
            'profit_target': 'none',
            'trailing_stop': 'Highest/Lowest since entry',
            'time_exit': 'SetExitOnClose',
            'signal_exit': 'none'
        },
        'indicators': ['UPB = Avg(High,LengthB) + NumDevsB*StdDev(High)', 'DLS = Avg(Low,LengthS) - NumDevsS*StdDev(Low)', 'Highest since entry'],
        'time_filters': ['Q_TX_EntryTime 4 windows'],
        'key_concepts': ['BB on High for upper band, BB on Low for lower band = asymmetric Bollinger', 'UPB/DLS reduce whipsaw vs standard BB on Close', 'Q_CT08 = Bollinger Band H/L variant'],
        'tags': ['60m', 'BB', 'Bollinger', 'High-Low-asymmetric', 'Q_CT-series'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/Q_CT09_060M_KC.md',
        'strategy_name': 'Q_CT09_060M_KC',
        'classification': 'Trend Following / Breakout',
        'direction': 'both',
        'timeframe': '60m',
        'entry_logic': {
            'long': ['MKP=0 AND Q_TX_EntryTime AND Q_TX_EntryContract<1 -> stop (Keltner on High)'],
            'short': ['same -> stop (Keltner on Low)']
        },
        'exit_logic': {
            'stop_loss': 'none',
            'profit_target': 'none',
            'trailing_stop': 'Highest/Lowest since entry',
            'time_exit': 'SetExitOnClose',
            'signal_exit': 'none'
        },
        'indicators': ['UPB = Avg(High,LengthB) + NumATRsB*ATR(LengthB)', 'DLS = Avg(Low,LengthS) - NumATRsS*ATR', 'Keltner Channel on H/L'],
        'time_filters': ['Q_TX_EntryTime 4 windows'],
        'key_concepts': ['KC uses ATR vs BB uses StdDev - volatility regime adaptive', 'ATR-based channel expands in volatile markets', 'Q_CT09 = Keltner variant (compare: Q_CT08 BB vs Q_CT09 KC)'],
        'tags': ['60m', 'Keltner', 'ATR', 'channel', 'volatility-adaptive', 'Q_CT-series'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/Q_CT10_060M_EL.md',
        'strategy_name': 'Q_CT10_060M_EL',
        'classification': 'Trend Following / Breakout',
        'direction': 'both',
        'timeframe': '60m',
        'entry_logic': {
            'long': ['MKP=0 AND Q_TX_EntryTime AND Q_TX_EntryContract<1 -> stop (MA Envelope on High)'],
            'short': ['same -> stop (MA Envelope on Low)']
        },
        'exit_logic': {
            'stop_loss': 'none',
            'profit_target': 'none',
            'trailing_stop': 'Highest/Lowest since entry',
            'time_exit': 'SetExitOnClose',
            'signal_exit': 'none'
        },
        'indicators': ['UPB = Avg(High,LengthB)*(1+PctB) - pct-based envelope', 'DLS = Avg(Low,LengthS)*(1-PctS)', 'MA Envelope on H/L'],
        'time_filters': ['Q_TX_EntryTime 4 windows'],
        'key_concepts': ['Envelope = MA +/- fixed % (simplest band method)', 'UPB/DLS on H/L = price envelope around H/L means', 'Q_CT10 = EL variant (simplest): BB(StdDev) vs KC(ATR) vs EL(pct) comparison'],
        'tags': ['60m', 'envelope', 'MA-pct', 'Q_CT-series', 'band-method'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/Q_CT11_030M_KD.md',
        'strategy_name': 'Q_CT11_030M_KD',
        'classification': 'Breakout',
        'direction': 'both',
        'timeframe': '30m',
        'entry_logic': {
            'long': ['Q_TX_EntryTime AND Q_TX_EntryContract<2 -> stop at Highest(High,StochLenB)'],
            'short': ['JUP<0 AND SKS<SDS -> stop at Lowest(Low,StochLenS)']
        },
        'exit_logic': {
            'stop_loss': 'none',
            'profit_target': 'none',
            'trailing_stop': 'Highest/Lowest since entry',
            'time_exit': 'SetExitOnClose',
            'signal_exit': 'none'
        },
        'indicators': ['Stochastic KD: SKS/SDS crossover', 'Highest(High,StochLenB) / Lowest(Low,StochLenS)', 'Q_TX_EntryTime / Q_TX_EntryContract'],
        'time_filters': ['Q_TX_EntryTime 4 windows'],
        'key_concepts': ['30m timeframe (vs 60m in Q_CT01-10)', 'Q_TX_EntryContract<2 = up to 2 contracts (vs <1 in 60m)', 'SKS<SDS = K below D = stochastic short signal', 'JUP<0 = session open bearish reference'],
        'tags': ['30m', 'KD', 'stochastic', 'Q_CT-series', 'trailing-stop'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/Q_CT12_030M_RSI.md',
        'strategy_name': 'Q_CT12_030M_RSI',
        'classification': 'Breakout',
        'direction': 'both',
        'timeframe': '30m',
        'entry_logic': {
            'long': ['Q_TX_EntryTime AND Q_TX_EntryContract<2 -> stop (RSI on High 30m)'],
            'short': ['JUP<0 AND RSS<OverSold -> stop at Lowest(Low,LengthS)']
        },
        'exit_logic': {
            'stop_loss': 'none',
            'profit_target': 'none',
            'trailing_stop': 'Highest/Lowest since entry',
            'time_exit': 'SetExitOnClose',
            'signal_exit': 'none'
        },
        'indicators': ['RSI(High,LengthB) = RSB', 'RSI(Low,LengthS) = RSS', 'Q_TX_SessionOpenD (JUP)'],
        'time_filters': ['Q_TX_EntryTime 4 windows'],
        'key_concepts': ['30m RSI variant', 'RSS<OverSold = RSI on Low in oversold = bearish for short', 'Q_CT12 = 30m RSI (parallel to Q_CT02 60m)'],
        'tags': ['30m', 'RSI', 'Q_CT-series', 'trailing-stop'],
        'batch': 41
    },
    {
        'file': 'E:/投資交易/pla_md/logic/Q_CT13_030M_CCI.md',
        'strategy_name': 'Q_CT13_030M_CCI',
        'classification': 'Breakout',
        'direction': 'both',
        'timeframe': '30m',
        'entry_logic': {
            'long': ['Q_TX_EntryTime AND Q_TX_EntryContract<2 -> stop at Highest(High,LengthB) (CCI filter)'],
            'short': ['JUP<0 AND CCS<OverSold -> stop at Lowest(Low,LengthS)']
        },
        'exit_logic': {
            'stop_loss': 'none',
            'profit_target': 'none',
            'trailing_stop': 'Highest/Lowest since entry',
            'time_exit': 'SetExitOnClose',
            'signal_exit': 'none'
        },
        'indicators': ['CCI', 'Highest(High,LengthB) / Lowest(Low,LengthS)', 'Q_TX_EntryTime'],
        'time_filters': ['Q_TX_EntryTime 4 windows'],
        'key_concepts': ['CCS<OverSold = CCI in oversold = bearish signal', '30m CCI (parallel to Q_CT03 60m)', 'Q_CT matrix: timeframe(30m/60m) x indicator(KD/RSI/CCI/MTM/OBV/MACD/DMI/BB/KC/EL)'],
        'tags': ['30m', 'CCI', 'Q_CT-series', 'trailing-stop'],
        'batch': 41
    },
]

# Append to JSONL
output_path = 'C:/Users/admin/workspace/digital-immortality/results/digestion_log.jsonl'
with open(output_path, 'a', encoding='utf-8') as f:
    for entry in entries:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

# Update digested_set.txt
tracking_path = 'C:/Users/admin/workspace/digital-immortality/results/digested_set.txt'
with open(tracking_path, 'a', encoding='utf-8') as f:
    for entry in entries:
        f.write(entry['file'] + '\n')

print(f'Done: appended {len(entries)} entries to JSONL and tracking')
