import json

entries = [
    {
        "file": "E:/\u6295\u8cc7\u4ea4\u6613/pla_md/signal/(4)NV2108004_TX15M_Bonny_LT.md",
        "name": "NV2108004_TX15M_Bonny_LT",
        "type": "swing",
        "timeframe": "15min",
        "direction": "both",
        "logic": "Dynamic channel breakout using rolling Len-day HH/HC/LL/LC to set up/dn levels. Shake-filter suppresses entry when mid direction is unstable (pos() of oscillation < Len/4). Multi-layer exit: channel stop, fixed stop, jump-gap trailing.",
        "indicators": ["Highest(H/C Len-day rolling)", "Lowest(L/C Len-day rolling)", "Shake oscillator (mid direction count over Len/2 periods)"],
        "entry": "C breaks up/dn computed from prior Len days max(HH-LC, HC-LL)*Lratio/Sratio; extra breakout filter when shake < Len/4 adds ATR(5h) to threshold",
        "exit": "Stop at opposite channel (dn for long); fixed stop at min(pt, daily ATR); jump-gap trailing after 2-day gap with profit; nobreak counter exit after 3 days without hitting target",
        "notable": "Shake-filter unique: counts oscillation of mid-direction over half-period to reduce choppy entries. Jump-gap regime tightens stop when asset gaps through prior 2 highs and is profitable."
    },
    {
        "file": "E:/\u6295\u8cc7\u4ea4\u6613/pla_md/signal/(4)NV2109005_TX6M_Cindy_LT.md",
        "name": "NV2109005_TX6M_Cindy_LT",
        "type": "daytrade",
        "timeframe": "6min",
        "direction": "both",
        "logic": "CDP pivot system on 6-min bars. Computes mid/up/dn from prior day HLC. Enters trend or anti-trend based on gap expansion. Adaptive profit target uses running average of daily gap size (AvgGap). BackHand reversal logic when price extends and then re-enters.",
        "indicators": ["CDP pivot: mid=(H+L+C)/3 up=2*mid-L dn=2*mid-H", "gap=up-dn daily range", "countif(c<c[1] k) momentum check"],
        "entry": "Trend: C breaks max(close[1] up) long between bar in-notin range; Anti-trend: price trapped outside CDP band with reversal candle; BackHand: reverse when price re-enters after extended move",
        "exit": "Trend exit at min(lowd[1] dn) for long; ratio*AvgGap profit target with trailing using running daily gap avg; reversal positions exit at mid or entry price next day; force exit session end for B2/S2",
        "notable": "AvgGap running average as adaptive profit target scales with recent daily volatility. BackHand reversal logic allows full strategy reversal embedded within same framework."
    },
    {
        "file": "E:/\u6295\u8cc7\u4ea4\u6613/pla_md/signal/(4)NV2110006_TX3M_FLT.md",
        "name": "NV2110006_TX3M_FLT",
        "type": "daytrade",
        "timeframe": "3min",
        "direction": "both",
        "logic": "AM vs PM session bias with counter-trend filter. Uses AmCloseD_TX (AM close tracking array) vs prior day to determine directional bias. Enters AGAINST the bias if price extends away from open by AvgHL (contrarian setup in PM session).",
        "indicators": ["AmCloseD_TX intraday AM close tracker", "AvgHL = avg(daily HL range Len days)/2", "OHLCPeriodsAgoADA/ADP multi-timeframe functions"],
        "entry": "After first 140 bars (pm session): if AM close stronger than prior day AND price rises above open+AvgHL buy at day high stop. If AM weaker AND falls below open-AvgHL short at day low.",
        "exit": "Stop at day low/high; profit trailing starts at 2*AvgHL gain: trail = win_pts*(0.2 + 0.01*bars_since_entry); AM session exits use prior day open/close levels",
        "notable": "Trailing formula with time-decay component (0.01 per bar) is novel - trail tightens as position ages forcing earlier exit. Contrarian AM-bias entry after drift beyond expected range."
    },
    {
        "file": "E:/\u6295\u8cc7\u4ea4\u6613/pla_md/signal/(4)NV2112008_TX60M_FLT.md",
        "name": "NV2112008_TX60M_FLT",
        "type": "swing",
        "timeframe": "60min",
        "direction": "both",
        "logic": "Linear regression trend + midprice momentum dual confirmation. Long when LinReg < 0 AND falling consistently (>half of Len2 bars) AND avg(midprice) rising. Entry stop uses HighestBar adaptive multiplier: doubles lookback when prior trade was loss AND sequence confirmed.",
        "indicators": ["LinearReg(close Len1=25) slope and direction", "avg=(C+O)/2 midprice trend", "countif trend consistency check", "HighestBar/LowestBar adaptive entry multiplier"],
        "entry": "Long: LinReg<0 all Len2 values<0 >half rising + midprice rising: buy at Highest(H Len2*multiplier) where multiplier=2 if prior bars bullish+prior loss, else 1",
        "exit": "Trailing when win_pts>=pt: exit = entryprice + 0.1*count*win_pts (accelerates with each profitable bar since entry); initial stop = Lowest(L Len2) for long",
        "notable": "Adaptive entry doubles lookback when coming off a loss to force stronger confirmation. Profit multiplier builds with each favorable bar since entry - self-reinforcing trailing mechanism."
    },
    {
        "file": "E:/\u6295\u8cc7\u4ea4\u6613/pla_md/signal/(4)NV2202009_TX300M_LT.md",
        "name": "NV2202009_TX300M_LT",
        "type": "swing",
        "timeframe": "300min",
        "direction": "both",
        "logic": "Asymmetric channel breakout: uses different lookback for long (Buyday=13) vs short (Shortday=17). Monthly DD circuit breaker with net profit tracking. Trend filter: exits if N/2 consecutive lower highs/lows detected after profitable move.",
        "indicators": ["Asymmetric HLCC range Buyday=13 for buy Shortday=17 for short", "Monthly net profit DD monitor level=200k", "checkday function for settlement-day detection"],
        "entry": "Buy = C + Kbuy*BuyRange (from Buyday lookback); Short = C - Kshort*SellRange (from Shortday lookback)",
        "exit": "Long: exit if countif(lower daily lows Shortday/2) >= Shortday/4 AND LowestBar>0; monthly DD: flagM if month loss > 200k or drawdown from month peak > 200k forces flat",
        "notable": "Asymmetric lookback for bull vs bear: different trend memory periods. Monthly circuit breaker forces flat for rest of month. Streak-based exit not fixed price level."
    },
    {
        "file": "E:/\u6295\u8cc7\u4ea4\u6613/pla_md/signal/(4)TimChen009_TX_30mBBI_LOS-\u7b56\u7565\u8173\u672c.md",
        "name": "TimChen009_TX_30mBBI_LOS",
        "type": "swing",
        "timeframe": "30min",
        "direction": "both",
        "logic": "BBI (Bull and Bear Index = avg of 4 MAs) dual-speed filter: BBI_S (fast 1,2,4,8x base) vs BBI_L (slow 54,108,216,432x base). VHF oscillator gates entries (VHF > 0.58). Extreme price exit guard (>9% vs prior AM close).",
        "indicators": ["BBI_S = avg(MA_1 MA_2 MA_4 MA_8)", "BBI_L = avg(MA_54 MA_108 MA_216 MA_432)", "VHF(17) = (Highest-Lowest)/SumAbsChange"],
        "entry": "BBI_S rising + C > BBI_S + VHF>0.58 + BBI_S > BBI_L: buy at market. Short: BBI_S falling + C < BBI_S + VHF>0.58 + BBI_S < BBI_L.",
        "exit": "BBI_S falls below BBI_L for long exit; stoploss-2: if HighestBar >= 40% of bars since entry sell at avg(open today + yesterday low); extreme-3: if price moves >9% from prior AM close exit",
        "notable": "BBI uses geometric scaling (1/2/4/8x). Extreme price guard prevents holding through limit moves. VHF as genuine trend/chop filter. 9% circuit handles Taiwan market circuit breaker."
    },
    {
        "file": "E:/\u6295\u8cc7\u4ea4\u6613/pla_md/signal/(4)TX_HLdistance15K.md",
        "name": "TX_HLdistance15K",
        "type": "swing",
        "timeframe": "15min",
        "direction": "both",
        "logic": "Gap open continuation: enters if open today > yesterday high AND majority of bars closed bullish over 96-bar window. Entry uses partial lookback breakout (excludes bars since highest bar was made).",
        "indicators": ["AmOpend_TX vs Amhighd/Amlowd_TX gap open", "CountIf(C>O Length) majority test", "Highest(H len-HighestBar(H len)) partial breakout level"],
        "entry": "Long: open > prev high + >50% of 96 bars close up -> buy at Highest(H len-HighestBar) stop. Short: open < prev low + majority down.",
        "exit": "Stoploss = entry - (Highest(C Len)-Lowest(C Len))/2 half close range; 7% circuit breaker if today high > open*1.07",
        "notable": "Partial-lookback breakout excludes bars since last high to avoid stale resistance levels. 7% circuit breaker handles Taiwan limit-up. Half close-range as volatility-adjusted stop."
    },
    {
        "file": "E:/\u6295\u8cc7\u4ea4\u6613/pla_md/signal/(4)\u7b56\u7565\u7a0b\u5f0f\u78bc 001_TX_20210204d_LO.md",
        "name": "a3001_TX_20210204_LOd",
        "type": "swing",
        "timeframe": "5min",
        "direction": "both",
        "logic": "ATR-filtered dual-MA crossover with low-volatility regime switch. Uses 1.5-day and 2.5-day moving averages. Enters only when HL gap exceeds ATR confirming meaningful move. StdDev < threshold triggers switch from trend-following to breakout-fading.",
        "indicators": ["Average(C 1.5-day bars)", "Average(C 2.5-day bars)", "avg price = (2C+L+H)/4", "AvgTrueRange(2.5-day)", "StdDev(C 1.5-day) volatility threshold"],
        "entry": "Early session (k < half-day): if today high > yesterday high + ATR AND midprice crosses below short MA: buy at L+5. Reversal after 100 bars: if position wrong and gap against position short.",
        "exit": "Low-volatility: when StdDev < threshold flip at N-day extremes (Highest/Lowest over somedays). Always exit at lastTradeDay.",
        "notable": "Low-volatility detection triggers regime switch from trend to mean-reversion. StdDev threshold as regime classifier. Variable N-day period based on x parameter WF-optimized."
    },
    {
        "file": "E:/\u6295\u8cc7\u4ea4\u6613/pla_md/signal/(4)\u7b56\u7565\u7a0b\u5f0f\u78bc TX_MAHL_FDT_1.md",
        "name": "TXF_MAHL_FDT_1",
        "type": "daytrade",
        "timeframe": "9min",
        "direction": "both",
        "logic": "Morning open comparison with adaptive MA slope filter. Requires new open > prior day close AND prior day open AND MA rising. Adaptive MA: doubles period (N to 2N) after losing trade to force stronger next-signal confirmation.",
        "indicators": ["Moving Average(C N or 2N based on prior trade profit)", "AmClosed_TX AmOpend_TX comparison array", "6-bar window for early open capture"],
        "entry": "Condition: newopen (captured at 6-bar mark) > prior AmClose AND > prior AmOpen AND MA rising. Buy at HH(6) stop if C>MA. Short: inverse.",
        "exit": "Fixed stop 40pts; profit trailer at 200pts gain with 40pt trail; day exit at 13:30 AM session",
        "notable": "Adaptive MA length: doubles period after losing trade forces stronger confirmation next time. Dual-open comparison ensures overnight conviction before entry."
    },
    {
        "file": "E:/\u6295\u8cc7\u4ea4\u6613/pla_md/signal/(4)\u7b56\u7565\u7a0b\u5f0f\u786201M60ML.md",
        "name": "a32201TC60ML",
        "type": "swing",
        "timeframe": "60min",
        "direction": "both",
        "logic": "RSI extreme mean reversion on 60min bars. Enters when smoothed RSI (3-bar average) > 85 or < 15. Exits when RSI reverses through 10/90 threshold. Momentum exit: if majority of bars since entry close against position, reverse to day extreme stop.",
        "indicators": ["RSI(C 6)", "3-bar RSI average smoothing", "countif(c<c[1] barssinceentry) >0.5*barssinceentry momentum check"],
        "entry": "Buy when RSI_avg < 15 (oversold); Short when RSI_avg > 85 (overbought). Must wait 3 bars into session.",
        "exit": "Exit when RSI < 10 for long (extreme exit); momentum exit: if more than half bars since entry closing against position reverse to day high/low stop",
        "notable": "Triple RSI smoothing reduces false extremes. Momentum-based reversal exit switches from exit to reverse-position entry when position clearly failing."
    },
    {
        "file": "E:/\u6295\u8cc7\u4ea4\u6613/pla_md/signal/(4)\u7b56\u7565\u7a0b\u5f0f\u786206M03MD0.md",
        "name": "a306M03MD0",
        "type": "daytrade",
        "timeframe": "6min",
        "direction": "both",
        "logic": "Linear regression angle + consecutive close momentum with 10% pullback trailing. Enters only before 11:00 if LRAngle > threshold for 5 bars AND 3 consecutive closes in same direction. Entry at opening 3-bar high/low.",
        "indicators": ["LinearRegAngle(C 40) trend quality", "3-bar close momentum count", "Opening 3-bar High/Low TH/TL from session start"],
        "entry": "After 3 session bars: 3+ consecutive higher closes + LRAngle>36 for 5 bars -> buy at TH(3-bar-high) stop. Short: inverse. Only before 11:00.",
        "exit": "When win_pts > max(TH-TL 40): trail to entryprice + (maxH-entryprice)*0.1 (10% pullback from intraday high); momentum-reverse exit: 3 consecutive closes against + outside entry-str; force exit at 13:35",
        "notable": "10% pullback trailing from intraday high protects gains while riding trends. LRAngle threshold filters direction quality. Morning-only entry window concentrates on strong momentum."
    },
    {
        "file": "E:/\u6295\u8cc7\u4ea4\u6613/pla_md/signal/(4)\u7b56\u7565\u8173\u672c - Wesley002_TX_2107SQX0001_DT.md",
        "name": "Wesley002_TX_2107SQX001_DT",
        "type": "daytrade",
        "timeframe": "5min",
        "direction": "both",
        "logic": "Heiken Ashi trend filter with dynamic stop adjustment based on position quality. All-same-direction HA bars for N periods signals trend. Adaptive SL: halved if >50% bars closed against position since entry.",
        "indicators": ["W_HeikenAshi(HA Low/High)", "CountIf(HA_Low > HA_Low[1] Period) = Period", "Dynamic stoploss halved if majority bars against"],
        "entry": "Long: HA Lows all rising for Period=8 bars -> buy at current High stop. Short: HA Highs all falling -> short at Low stop. Lunch session (12:15-12:45) with extra close direction filter.",
        "exit": "Adaptive SL: if >50% bars since entry closed against halve stop distance. Profit target at prior day low. 7% daily circuit breaker (Taiwan limit-up guard). EOD exit 4 bars before close.",
        "notable": "Halved stoploss key innovation: dynamically adjusts risk based on position quality since entry. Flash crash protection at 7% daily limit. Lunch session extension with extra confirmation."
    },
    {
        "file": "E:/\u6295\u8cc7\u4ea4\u6613/pla_md/signal/(4)\u7b56\u7565\u8173\u672c - Wesley003_TX_2110KPower_LO.md",
        "name": "Wesley003_TX_2110KPower_LO",
        "type": "swing",
        "timeframe": "15min",
        "direction": "both",
        "logic": "KPower = abs(LPower-SPower) > StdDev for trend strength measurement. LPower=sum(C-L 4bars) captures buying pressure; SPower=sum(H-C 4bars) captures selling pressure. Three-day consecutive high/low constraint confirms multi-day trend. Monthly loss circuit breaker.",
        "indicators": ["LPower = sum(C-L 4bars) buying pressure", "SPower = sum(H-C 4bars) selling pressure", "KPower = abs(LPower-SPower) net pressure", "StdDev(Close STD_Len=20) volatility benchmark", "3-day consecutive day-HL trend"],
        "entry": "Long: LowD(0)>=LowD(1)>=LowD(2) (3-day higher lows) AND LPower>SPower AND KPower>StdDev -> buy at TypicalPrice stop.",
        "exit": "SL at entryprice - SLC*StdDev. Jump-gap protection on open. Fast PT at 3.5%*price. Extended PT: PTC*StdDev with PercentRank>=90% AND new high condition.",
        "notable": "KPower as directional momentum combining bull and bear pressure magnitudes. PercentRank exit gate: only take profit when price at 90th percentile of recent range. Monthly DD circuit breaker."
    },
    {
        "file": "E:/\u6295\u8cc7\u4ea4\u6613/pla_md/signal/(4)\u7b56\u7565\u8173\u672c - Wesley004_TX_2112SQX003_LT.md",
        "name": "Wesley004_TX_2112SQX003_LT",
        "type": "swing",
        "timeframe": "20min",
        "direction": "both",
        "logic": "Three-bar reversal pattern with Heiken Ashi entry trigger and STD-based trailing stop. Pattern: Close[3]<Low[2] AND Close[2]>Low[1] AND TypicalPrice rising (bullish recovery from false breakdown). HA entry at HA_High of 1 bar ago.",
        "indicators": ["W_HeikenAshi(1/2 1) HA High/Low 1 bar ago", "StdDev(Close STDLen=30) volatility", "TypicalPrice = (H+L+C)/3"],
        "entry": "Long: 3-bar recovery (prior close pierced low then reversed) -> buy at HA_High[1] stop. Short: 3-bar distribution -> short at HA_Low[1] stop.",
        "exit": "Fixed SL at entryprice - StopLoss(145pts). Trailing stop only moves when in profit AND improvement better than current trail: TSC=2.1*StdDev as trail distance.",
        "notable": "Captures false breakdown recoveries (bear traps). Trailing only moves in profit direction and only if improvement - prevents widening. StdDev trail auto-adapts to volatility."
    },
    {
        "file": "E:/\u6295\u8cc7\u4ea4\u6613/pla_md/signal/(4)\u7b56\u7565\u8173\u672c PTstartup105_TX_PivotReversal04_DT.md",
        "name": "PTstartup105_TX_PivotReversal04_DT",
        "type": "daytrade",
        "timeframe": "5min",
        "direction": "both",
        "logic": "Swing point reversal after gap open. Detects prior swing extremes using SwingHigh/SwingLow functions with Strength parameter. Enters when gap direction matches swing and price approaches swing extreme. Filters extreme gap sizes.",
        "indicators": ["SwingHigh(1 High Strength Strength+1)", "SwingLow(1 Low Strength Strength+1)", "OpenD(0) vs CloseD(1) gap direction"],
        "entry": "If gap up AND prior swing high detected -> limit buy at swing high - 1 tick. Only in first 30 bars of session. Filters abs(C-CloseD(1)) < STP to avoid runaway gaps.",
        "exit": "No trailing stop - exits only at 2 bars before session close (market order). Full-day ride or close.",
        "notable": "Post-gap reversal entry near prior pivot. No profit target - full day ride. Very simple exit relative to complex entry. SwingHigh/Low detection with configurable Strength period."
    },
    {
        "file": "E:/\u6295\u8cc7\u4ea4\u6613/pla_md/signal/(4)\u7b56\u7565\u8173\u672c_LanDi001_TX_BIAS_50mK_20220217_LT.md",
        "name": "LanDi001_TX_BIAS_50mK_LT",
        "type": "swing",
        "timeframe": "50min",
        "direction": "both",
        "logic": "BIAS indicator trend-following with bounded zone entry. BIAS = 10000*(C-MA)/MA. Enters when BIAS in bounded range (bias to ratio*bias) AND has been at local low for 5+ bars (momentum turning). Avoids settlement days.",
        "indicators": ["BIAS = 10000*(C-MA50)/MA50 percentage deviation from MA", "lowestBar(BIAS 10) > 5 local minimum detection"],
        "entry": "Long: BIAS > 105 AND BIAS < 4.75*105 AND BIAS at local low 5+ bars ago -> buy market. Short: BIAS < -105 AND BIAS > -4.75*105 AND BIAS at local high.",
        "exit": "Long exit: BIAS turns negative (mean reversion); BIAS > ratio*bias (extended) -> sell at 2-bar low. Settlement day exit at 11:00.",
        "notable": "Bounded BIAS zone 1x-4.75x threshold avoids both timid and extreme readings. lowestBar filter ensures BIAS recently bottomed out (momentum turning point). Avoids settlement and prior settlement day."
    },
    {
        "file": "E:/\u6295\u8cc7\u4ea4\u6613/pla_md/signal/(4)\u7b56\u7565\u8173\u672c004_TX_PriceInterval5K_LO.md",
        "name": "b3004_TX_PriceInterval5K_LO",
        "type": "swing",
        "timeframe": "5min",
        "direction": "both",
        "logic": "Adaptive regime-switching strategy: large-interval (trending) vs small-interval (compression). Uses 6-day and 12-day avg HL distance to classify regime. Four progressive long entry levels based on position and context. Adaptive exit with 2% circuit breaker.",
        "indicators": ["avgHLDist = avg(daily HL range 6 days)", "avgHLDist2 = avg(daily HL range 12 days)", "avgCDDist = avg(max distance close to H or L 6 days)", "weekly H/L as multi-day reference"],
        "entry": "Large-interval (avgHL >= avgHL2): multiple signals from close avg comparison midpoint vs yesterday TPx candle vs open. Small-interval (avgHL < avgHL2): 3-day pattern with internal structure confirmation.",
        "exit": "Trailing: if win_pts > 2*STP trail at 50% retracement of gain. Initial stop entryH - STP. 2% circuit breaker from entry price.",
        "notable": "Regime detection by comparing 6-day vs 12-day range averages: larger recent range = trending. Up to 4 entry signals per side. Progressive confidence scoring with position awareness."
    },
    {
        "file": "E:/\u6295\u8cc7\u4ea4\u6613/pla_md/signal/(4)\u7b56\u7565\u8173\u672c005_TX_wCDP20K_FLO.md",
        "name": "a3005_TX_wCDP20K_FLO",
        "type": "swing",
        "timeframe": "20min",
        "direction": "both",
        "logic": "Daily CDP + Weekly CDP combined framework. dCDP from daily HLC, wCDP computed on Wednesday from 5-day weighted average. Two regime modes: wide (avgRange>avgRange2) for trending and narrow for compression with different entry logic.",
        "indicators": ["Daily CDP = (H+L+3C)/5", "Weekly CDP computed each Wednesday from 5-day OHLC averages", "R1=2*dCDP-L S1=2*dCDP-H range pivots", "avgRange = avg(R2-S2 Len days) volatility regime"],
        "entry": "Wide regime: enter if dCDP trending + wCDP bullish + C >= R1. Narrow regime: multiple conditions comparing dCDP to wCDP trend AND weekly trend AND position in range.",
        "exit": "If win_pts < range*ratio trail from EntryH by range+avgRange/4; if win_pts >= range*ratio trail at 80% of gains; 2% circuit breaker",
        "notable": "Weekly CDP as multi-day S/R anchor combined with daily CDP. Range-based profit target adapts to recent daily volatility. Two regime modes with entirely different entry logic."
    },
    {
        "file": "E:/\u6295\u8cc7\u4ea4\u6613/pla_md/signal/(4)\u7b56\u7565\u8173\u672cDrschnabel_TX_trend&oscillation20k_LT.md",
        "name": "Drschnabel_TX_trend_oscillation20k_LT",
        "type": "swing",
        "timeframe": "20min",
        "direction": "both",
        "logic": "Dual MA trend filter with golden-ratio (phi=1.618) period relationship + KD oscillator crossover entry. AvgDif = MA(56) - MA(91). Two entry modes: trend (when MA56>MA91) and counter-trend (when MA56<MA91 but FastD extreme).",
        "indicators": ["Average(C 56) vs Average(C 91) golden-ratio pair", "FastK(11) oscillator", "FastD(11) for counter-trend"],
        "entry": "Trend: C>MA56 + AvgDif>0 + FastK crosses above (50-KDif=34) -> buy at H stop. Counter: C>MA56 + AvgDif<0 + FastD>84 -> buy at rolling high breakout.",
        "exit": "Long exit: C < (AvgSlow + entryprice)/2 midpoint between MA91 and entry -> exit market. Extended profit: C > AvgSlow + 590 -> exit.",
        "notable": "Golden ratio (phi=1.618) for MA period relationship. Counter-trend entry when short MA diverges from long. Conditional no-trade filter: skip if traded within last 12 bars."
    },
    {
        "file": "E:/\u6295\u8cc7\u4ea4\u6613/pla_md/signal/(4)\u7b56\u7565\u8173\u672cGavinLu008_TX_DonChianChannel-D2106-K20m_LT.md",
        "name": "GavinLu008_TX_DonChianChannel_20m_LT",
        "type": "swing",
        "timeframe": "20min",
        "direction": "both",
        "logic": "Donchian Channel breakout with EMA(320) very-long-term trend filter. DonHigh/DonLow of 46-bar Donchian. Entry when channel expanding (DonHigh rising 2 consecutive bars) AND price on correct side of long-term EMA.",
        "indicators": ["DonChian: Highest(C 46) Lowest(C 46)", "EMA = XAverage(C 320) long-term filter", "maxWinPoint tracker", "maxRatio = 5.8x profit multiple"],
        "entry": "Long: DonHigh rising 2 consecutive bars + C > EMA -> buy market. Short: DonLow falling 2 bars + C < EMA. Only 1 trade per day allowed.",
        "exit": "If win_pts > maxWinPoint*maxRatio: full exit. DonLow as trailing reference for long.",
        "notable": "EMA(320) on 20min bars = ~26 days long-term trend filter. maxRatio=5.8x ensures capturing full trend legs before exiting. Channel expansion as momentum confirmation."
    },
    {
        "file": "E:/\u6295\u8cc7\u4ea4\u6613/pla_md/signal/(4)\u7b56\u7565\u8173\u672cJack106_TX_Neckline10K_L0.md",
        "name": "Jack106_TX_Neckline10K_L0",
        "type": "swing",
        "timeframe": "10min",
        "direction": "both",
        "logic": "Neckline breakout based on 2-day candle pattern (morning star / evening star type). Detects bearish-then-bullish or bullish-then-bearish daily candle sequence. Enters at average of the two prior day highs as neckline level.",
        "indicators": ["closed/opend comparison daily candle direction", "2-day high/low average as neckline S/R", "OpenD vs CloseD gap filter"],
        "entry": "Long: Close[2]<Open[2] (bearish day) AND Close[1]>Open[1] (bullish reversal) AND Close[1]>Close[2] AND today C>Open -> buy at avg(High[1] High[2]) stop.",
        "exit": "Reversal exit: 3 consecutive bars H below yesterday low + bearish bar -> reverse to short if profitable. Wrong-direction exit within 1 bar at market. Last trade day close.",
        "notable": "Neckline = midpoint of two-day swing as natural S/R. Pattern reversal double-duty: when 3 bars fail and momentum reverses flip position. Simple but robust entry combining candle and gap."
    },
    {
        "file": "E:/\u6295\u8cc7\u4ea4\u6613/pla_md/signal/(4)\u7b56\u7565\u8173\u672cJack112_TX_HLR13K_LT_Jack \u8ecd\u9091\u8ecd\u5b87.md",
        "name": "Jack112_TX_HLR13K_LT",
        "type": "swing",
        "timeframe": "13min",
        "direction": "both",
        "logic": "3-layer rolling high/low lookback at different day offsets (t, t-1day, t-2day) for convergent trend confirmation. Detects descending low structure at three timeframes simultaneously. Entry at 1-day-ago highest close during 9:30-13:30.",
        "indicators": ["Highest(C[1] TLen) Highest(C[TLen] TLen) Highest(C[TLen] TLen*2) three-layer lookback", "Lowest variants at same three offsets"],
        "entry": "Long: value4<value5<value6 (3-layer descending lows = holding support) AND NOT value2>value1 (not yet breaking high resistance) -> buy at value1 stop.",
        "exit": "Same-day candle reversal exit. WrongBuy/WrongSell: immediate failure within 1 bar exits at market. Profit target: 1.4% of price. Settlement: exit at 13:00.",
        "notable": "3-layer lookback structure at t/t-1day/t-2day provides layered trend confirmation. Immediate failure exit (WrongBuy) within 1 bar prevents large losses. 1.4% fixed profit target."
    },
    {
        "file": "E:/\u6295\u8cc7\u4ea4\u6613/pla_md/signal/(4)\u7b56\u7565\u7a0b\u5f0f\u786c%%AVgirl_202106_5K.md",
        "name": "b25b25AVgirl_202106",
        "type": "daytrade",
        "timeframe": "5min",
        "direction": "both",
        "logic": "Bar-timing analysis: tracks when each session H and L are made (Hbar Lbar variables). Enters when LowestBar > Lbar (new lows forming later than the established low bar) signaling continuation. Candle direction count provides momentum adjustment to entry threshold.",
        "indicators": ["Hbar = bar number when daily H was made (updated each bar)", "Lbar = bar number when daily L was made", "LowestBar(L fmk) HighestBar(H fmk) position tests", "CountIf(C>O) candle direction count"],
        "entry": "Condition1 (breakout): new low forms after expected low bar AND closed down from open with direction count adjustment. Condition11 (gap): LowestBar > max(Lbar Hbar) AND open gap up -> long at highest H since key bar.",
        "exit": "Long: sell if prior day close < today low (trend fails) -> stop at midpoint. Short: inverse. Day exit at 13:30.",
        "notable": "Bar-timing analysis of when H/L form within session is novel - later-than-expected low suggests later-session continuation. Momentum adjustment to entry filter based on directional candle count."
    }
]

output_path = r'C:\Users\admin\workspace\digital-immortality\results\digestion_log.jsonl'
with open(output_path, 'a', encoding='utf-8') as f:
    for entry in entries:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

print(f'Written {len(entries)} entries to digestion_log.jsonl')
