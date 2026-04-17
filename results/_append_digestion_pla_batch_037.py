import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
from datetime import datetime, timezone, timedelta

tz = timezone(timedelta(hours=8))
now = datetime.now(tz).isoformat()

log_path = "C:/Users/admin/workspace/digital-immortality/results/digestion_log.jsonl"
set_path = "C:/Users/admin/workspace/digital-immortality/results/digested_set.txt"
state_path = "C:/Users/admin/workspace/digital-immortality/results/digestion_state.json"

with open(state_path, 'r', encoding='utf-8') as f:
    state = json.load(f)

with open(set_path, 'r', encoding='utf-8') as f:
    digested = set(l.strip() for l in f if l.strip())

base = "E:/投資交易/pla_md/logic/"

strategies = [
    {
        "path": base + "NV2109005_TX6M_Cindy_LT-original (2).md",
        "strategy_name": "NV2109005_TX6M_Cindy_LT_original",
        "family": "NV series (Cindy)",
        "timeframe": "Intraday (bar-interval dependent)",
        "direction": "Both",
        "category": "Multi-entry complex swing with pivot + anti-trend layers",
        "summary": "NV2109005_TX6M_Cindy_LT-original -- TX6M (TXF mini) complex swing strategy. Long entries: B1=(vmp=0 AND vmp[1]<0 same as exitdate) -> stop at (HighD(0)+Highest(H,2))/2; B2=(DS=0 AND C<minlist(CloseD(1),dn) AND not ShortExit) -> stop; B3=(DS=0 AND LowD(0)>up AND c<o) -> stop. Short entries: S1=(EntriesToday<=1 AND condition40) -> stop; S2/S3=(k>in AND not sessionlastbar) anti-trend entries with pyramid. Pivot levels: mid=(HighD(1)+LowD(1)+CloseD(1))/3; up=mid*2-LowD(1); dn=mid*2-HighD(1) (R1/S1 classic pivot). gap=up-dn. k=CountIf(c<c[1],k) bearish bar count. Exit: RL-Run/RS-Run signals; SetExitOnClose. Key insight: 'anti-trend' entries S2/S3 when k>in = counter-trend when too many consecutive down bars; B3 = inside-bar below pivot resistance with bearish candle = reversal setup at pivot."
    },
    {
        "path": base + "NV2109005_TX6M_Cindy_LT-original.md",
        "strategy_name": "NV2109005_TX6M_Cindy_LT_original_base",
        "family": "NV series (Cindy)",
        "timeframe": "Intraday (bar-interval dependent)",
        "direction": "Both",
        "category": "Multi-entry complex swing with pivot + anti-trend layers (base copy)",
        "summary": "NV2109005_TX6M_Cindy_LT-original (base) -- Identical to (2) copy. TX6M complex pivot-based swing. Same B1/B2/B3 long and S1/S2/S3 short logic. DS=0 flag controls entry permission. Pivot: mid=(H1+L1+C1)/3; R1=mid*2-L1; S1=mid*2-H1. Anti-trend entries when consecutive down-bar count k>in threshold. Note: deduped original copy."
    },
    {
        "path": base + "No22_TX_RSI_7K_DO (2).md",
        "strategy_name": "No22_TX_RSI_7K_DO",
        "family": "No series",
        "timeframe": "Intraday (bar-interval dependent)",
        "direction": "Both",
        "category": "RSI-based composite score breakout with ATR extension",
        "summary": "No22_TX_RSI_7K_DO (7K capital, Day-Only) -- TX RSI composite score breakout. SumScore=Summation(Score,Len); Condition11=RSI(SumScore,Len)>50+Bias; Condition21=RSI(SumScore,Len)<50-Bias. Primary long: Condition31 AND EntriesToday<=1 -> stop at HighD(0)+AvgTrueRange(Len); primary short: -> LowD(0)-ATR(Len). Reversal long (Rev-LE): mp=0 AND Condition11 -> stop at HighD(0). Reversal short (Rev-SE): Condition21 -> LowD(0). Exit: TimeOut at t<1300 and t>=1325; maxpositionprofit trailing; Highest(H,2)/Lowest(L,2) trailing. Date cutoff: date<=1140312 (2014-03-12). Key insight: RSI of a composite Score variable (not raw price) = second-order momentum; ATR extension of daily high/low creates momentum-adjusted breakout levels; date cutoff shows walk-forward boundary."
    },
    {
        "path": base + "No22_TX_RSI_7K_DO (3).md",
        "strategy_name": "No22_TX_RSI_7K_DO_copy3",
        "family": "No series",
        "timeframe": "Intraday (bar-interval dependent)",
        "direction": "Both",
        "category": "RSI composite score breakout (deduped copy 3)",
        "summary": "No22_TX_RSI_7K_DO (3) -- Identical to base copy. Deduped."
    },
    {
        "path": base + "No22_TX_RSI_7K_DO (4).md",
        "strategy_name": "No22_TX_RSI_7K_DO_copy4",
        "family": "No series",
        "timeframe": "Intraday (bar-interval dependent)",
        "direction": "Both",
        "category": "RSI composite score breakout (deduped copy 4)",
        "summary": "No22_TX_RSI_7K_DO (4) -- Identical to base copy. Deduped."
    },
    {
        "path": base + "No22_TX_RSI_7K_DO.md",
        "strategy_name": "No22_TX_RSI_7K_DO_base",
        "family": "No series",
        "timeframe": "Intraday (bar-interval dependent)",
        "direction": "Both",
        "category": "RSI composite score breakout (base)",
        "summary": "No22_TX_RSI_7K_DO (base) -- Same as (2)(3)(4) copies. RSI of Summation(Score,Len) as momentum measure; HighD(0)+ATR and LowD(0)-ATR as breakout levels; Reversal entries at raw daily H/L. Deduped."
    },
    {
        "path": base + "No25_TXA_CandleShadow_60K_LO (2).md",
        "strategy_name": "No25_TXA_CandleShadow_60K_LO",
        "family": "No series",
        "timeframe": "Intraday (60K capital)",
        "direction": "Both",
        "category": "Candle shadow pattern breakout",
        "summary": "No25_TXA_CandleShadow_60K_LO -- TXA (mini) candle shadow pattern. LowerShadow=Condition11 AND Condition12: Condition11=(MinList(Open,Close)-Low)>0.5*Range (lower shadow > 50% of range); Condition22=(High-MaxList(Open,Close))>... for upper shadow. UpperHigh=Highest(High,UpperLen); LowerLow=Lowest(Low,LowerLen). Entry: SellCondition AND High>UpperHigh[0] -> market order (both long and short -- note: same condition for both suggests error or complex logic). Date cutoff: date<=1140314. Key insight: candle shadow size vs body = pin bar detection; shadow > 50% of range = strong rejection candle; N-bar high/low for breakout confirmation after shadow."
    },
    {
        "path": base + "No25_TXA_CandleShadow_60K_LO.md",
        "strategy_name": "No25_TXA_CandleShadow_60K_LO_base",
        "family": "No series",
        "timeframe": "Intraday (60K capital)",
        "direction": "Both",
        "category": "Candle shadow pattern breakout (base copy)",
        "summary": "No25_TXA_CandleShadow_60K_LO (base) -- Identical to (2) copy. Shadow detection: lower = (low end - low) > 50% range; upper = (high - high end) > 50% range. Deduped."
    },
    {
        "path": base + "No28_TX_MA_60K_LO (2).md",
        "strategy_name": "No28_TX_MA_60K_LO",
        "family": "No series",
        "timeframe": "Intraday (60K capital)",
        "direction": "Both",
        "category": "Dual EMA with gap-open trend confirmation and CountIf exit",
        "summary": "No28_TX_MA_60K_LO -- TX dual EMA with gap filter. Condition10=XAverage(Close,FastLen)>XAverage(Close,SlowLen) AND Close>Maxlist(CloseD(1),...). Entry: mp=0 AND gap-up (OpenD(0)>CloseD(1)) AND Condition10 -> stop at Highest(High,(FastLen+SlowLen)/2); gap-down -> stop at Lowest(Low,(FastLen+SlowLen)/2). NShares position sizing. Exit: CountIf(c<o,barssinceentry) = count bearish bars since entry -> trailing stop level STPL+countif(...)*factor. Date cutoff: date<=1140414. Key insight: N=(FastLen+SlowLen)/2 for breakout lookback = average of two MA periods; CountIf bearish bars since entry = progressive stop tightening as bars close bearish."
    },
    {
        "path": base + "No28_TX_MA_60K_LO.md",
        "strategy_name": "No28_TX_MA_60K_LO_base",
        "family": "No series",
        "timeframe": "Intraday (60K capital)",
        "direction": "Both",
        "category": "Dual EMA gap-open trend (base copy)",
        "summary": "No28_TX_MA_60K_LO (base) -- Identical to (2). Deduped."
    },
    {
        "path": base + "No32_TX_LinearRegCurve_60K_LO_S (2).md",
        "strategy_name": "No32_TX_LinearRegCurve_60K_LO_S",
        "family": "No series",
        "timeframe": "Intraday (60K capital)",
        "direction": "Both",
        "category": "Linear regression + 3-day volatility filter with 2*Vol limit exit",
        "summary": "No32_TX_LinearRegCurve_60K_LO_S -- TX linear regression curve strategy. r0=LinearRegValue(C,Len,0). ThreeDayVolatility=MaxList(HighD(1..3))-MinList(LowD(1..3)) (3-day range). Condition30=AbsValue(CloseD(0)-OpenD(0))>ThreeDayVolatility*0.618 (today intraday range > 61.8% of 3-day range). Entry: mp=0 AND C>O AND Condition10 -> market or stop at Highest/Lowest(N). Exit: sell LX-2 at entryPrice+2*Vol limit / BuyToCover at entryPrice-2*Vol limit (symmetric 2-volatility target). Date cutoff: date<=1150204. Key insight: 0.618 Fibonacci ratio as threshold for 'significant' intraday move vs 3-day range; LinearRegValue as trend filter; 2*Vol exit = Fibonacci 2x extension target."
    },
    {
        "path": base + "No32_TX_LinearRegCurve_60K_LO_S (3).md",
        "strategy_name": "No32_TX_LinearRegCurve_60K_LO_S_copy3",
        "family": "No series",
        "timeframe": "Intraday (60K capital)",
        "direction": "Both",
        "category": "Linear regression 3-day vol filter (deduped copy 3)",
        "summary": "No32_TX_LinearRegCurve_60K_LO_S (3) -- Identical to base. Deduped."
    },
    {
        "path": base + "No32_TX_LinearRegCurve_60K_LO_S (4).md",
        "strategy_name": "No32_TX_LinearRegCurve_60K_LO_S_copy4",
        "family": "No series",
        "timeframe": "Intraday (60K capital)",
        "direction": "Both",
        "category": "Linear regression 3-day vol filter (deduped copy 4)",
        "summary": "No32_TX_LinearRegCurve_60K_LO_S (4) -- Identical to base. Deduped."
    },
    {
        "path": base + "No32_TX_LinearRegCurve_60K_LO_S.md",
        "strategy_name": "No32_TX_LinearRegCurve_60K_LO_S_base",
        "family": "No series",
        "timeframe": "Intraday (60K capital)",
        "direction": "Both",
        "category": "Linear regression 3-day vol filter (base copy)",
        "summary": "No32_TX_LinearRegCurve_60K_LO_S (base) -- Same as (2)(3)(4). LinearRegValue trend filter; ThreeDayVolatility*0.618 entry condition; 2*Vol symmetric limit exits. Deduped."
    },
    {
        "path": base + "No33_TX_RSIInv_30K_LO (2).md",
        "strategy_name": "No33_TX_RSIInv_30K_LO",
        "family": "No series",
        "timeframe": "Intraday (bar-interval dependent)",
        "direction": "Both",
        "category": "Fisher-inverse RSI breakout with 300-minute N-bar lookback",
        "summary": "No33_TX_RSIInv_30K_LO -- TX RSI+Fisher inverse breakout. value1=(RSI(C,Len1)-50)/10 = normalized RSI centered at 0. value2=WAverage(value1,Len2) = weighted smoothing. FisherInv(value2) = inverse Fisher transform of smoothed RSI. CountIf(FisherInv(value2)>0.5,2)=2 = two consecutive bars above 0.5 threshold. Entry: -> stop at Highest(H,300/barinterval) / Lowest(L,300/barinterval). N=300/barinterval = dynamic lookback (300 minutes regardless of bar size). STP=MaxList(HighD(1)-LowD(1),FP) as SL. Date cutoff: date<=1150605. Key insight: inverse Fisher transform compresses RSI to (-1,+1) range and sharpens signals at extremes; 300/barinterval = 5-hour lookback in any timeframe; CountIf=2 requires persistence, not single-bar signal."
    },
    {
        "path": base + "No33_TX_RSIInv_30K_LO.md",
        "strategy_name": "No33_TX_RSIInv_30K_LO_base",
        "family": "No series",
        "timeframe": "Intraday (bar-interval dependent)",
        "direction": "Both",
        "category": "Fisher-inverse RSI breakout (base copy)",
        "summary": "No33_TX_RSIInv_30K_LO (base) -- Identical to (2). Fisher(WAverage(normalized RSI)); 300-min dynamic N-bar; 2-bar CountIf confirmation. Deduped."
    },
    {
        "path": base + "No34_TX_TL_17K_LO (2).md",
        "strategy_name": "No34_TX_TL_17K_LO",
        "family": "No series",
        "timeframe": "Intraday",
        "direction": "Both",
        "category": "HighestBar recency filter trend entry",
        "summary": "No34_TX_TL_17K_LO (TL=Trend Line?, 17K capital) -- TX recency-filtered trend entry. Entry: Condition10 AND HighestBar(High,Len)<=NBar -> market order (both long and short same condition). HighestBar returns how many bars ago the Len-bar high occurred; <=NBar means recent high = recent momentum. SetExitOnClose. Date cutoff: date<=1150114. Key insight: HighestBar(High,Len)<=NBar = 'the N-bar high is recent' = current uptrend has made a new high within last NBar bars; combines trend check (Condition10) with momentum recency."
    },
    {
        "path": base + "No34_TX_TL_17K_LO.md",
        "strategy_name": "No34_TX_TL_17K_LO_base",
        "family": "No series",
        "timeframe": "Intraday",
        "direction": "Both",
        "category": "HighestBar recency filter trend entry (base copy)",
        "summary": "No34_TX_TL_17K_LO (base) -- Identical to (2). Deduped."
    },
    {
        "path": base + "No35_TXA_Efficiency_29K_LO (2).md",
        "strategy_name": "No35_TXA_Efficiency_29K_LO",
        "family": "No series",
        "timeframe": "Intraday (bar-interval dependent)",
        "direction": "Both",
        "category": "Efficiency ratio entry with reversal at Efficiency extreme",
        "summary": "No35_TXA_Efficiency_29K_LO (Efficiency Ratio, 29K capital, TXA mini) -- Entry using Efficiency ratio. Efficiency=Difference/PathValue where Difference=AvgPrice-AvgPrice[Len] (net move); PathValue=Summation(AbsValue(AvgPrice-AvgPrice[1]),Len) (total path). Primary: d>=01170515 -> stop at H-Efficiency*10 long / L+Efficiency*10 short. Reversal (LE_REV): AbsValue(Efficiency-Highest(Efficiency,3))<=(1-NRatio) -> market long when efficiency dropped from recent high; (SE_REV): mp>0 -> market short. Time exit: Calctime(sess1endtime,-2*barinterval). Key insight: Efficiency ratio = directional efficiency of price path (1=straight line, 0=random walk); entry price at H-Efficiency*10 = the higher the efficiency the closer to current price (tighter entry); reversal when Efficiency drops from 3-bar high = momentum decay."
    },
    {
        "path": base + "No35_TXA_Efficiency_29K_LO.md",
        "strategy_name": "No35_TXA_Efficiency_29K_LO_base",
        "family": "No series",
        "timeframe": "Intraday (bar-interval dependent)",
        "direction": "Both",
        "category": "Efficiency ratio entry (base copy)",
        "summary": "No35_TXA_Efficiency_29K_LO (base) -- Identical to (2). Efficiency=NetMove/TotalPath; stop entry adjusted by efficiency magnitude; reversal at efficiency decay. Deduped."
    },
    {
        "path": base + "No36_TX_STD_60K_LO (2).md",
        "strategy_name": "No36_TX_STD_60K_LO",
        "family": "No series",
        "timeframe": "Intraday (bar-interval dependent)",
        "direction": "Both",
        "category": "TypicalPrice STD breakout with 2-bar CountIf confirmation",
        "summary": "No36_TX_STD_60K_LO (STD=Standard Deviation?, 60K capital) -- TX TypicalPrice breakout with var2/var3 bands. var2/var3 likely derived from StdDev of TypicalPrice. Entry: Countif(TypicalPrice>var2,2)=2 AND C>O -> stop at Highest(H,300/barinterval); Countif(TypicalPrice<var3,2)=2 AND C<O -> Lowest(L,300/barinterval). N=300/barinterval dynamic lookback. STP=MaxList(HighD(1)-LowD(1),500*TickSize). Date cutoff: date<=1150204. Key insight: 2-bar CountIf of TypicalPrice above band = requires persistence beyond band for 2 consecutive bars; C>O (bullish close) as additional confirmation; dynamic 300-min N-bar for any timeframe."
    },
    {
        "path": base + "No36_TX_STD_60K_LO.md",
        "strategy_name": "No36_TX_STD_60K_LO_base",
        "family": "No series",
        "timeframe": "Intraday (bar-interval dependent)",
        "direction": "Both",
        "category": "TypicalPrice STD breakout (base copy)",
        "summary": "No36_TX_STD_60K_LO (base) -- Identical to (2). TypicalPrice 2-bar CountIf above/below var bands; 300/barinterval dynamic breakout. Deduped."
    },
    {
        "path": base + "OI.md",
        "strategy_name": "a21a21_TXFSF_060_OI01",
        "family": "a21 series",
        "timeframe": "Intraday (60-min)",
        "direction": "Both",
        "category": "Open Interest + gap-open swing filter breakout",
        "summary": "a21a21_TXFSF_060_OI01 -- TX 60-min OI-based breakout. OFD = absolute open gap: OpenD(0)-CloseD(1). Condition21: OFD>=nH AND LowD(0)>CloseD(1)-AbsValue(gap) -> up gap, buy at MaxList(HighD(0),HighD(1)) stop. Condition22: OFD>=nL AND HighD(0)<CloseD(1)+AbsValue(gap) -> down gap, buy near low. Condition23: alternate gap condition. Short: swing=1 -> stop at Lowest(l,lenL). Uses FIELD_VOLUME for OI data. Time filter: t>=1330 AND t<=1345. HH=Highest(h,lenH); LL=Lowest(l,lenL) for breakout levels. Key insight: OI + gap direction = institutional positioning; gap opening above prior close with LowD staying positive = confirmed gap-up regime; OI field distinguishes volume (flow) vs open interest (position accumulation)."
    },
    {
        "path": base + "OSCAR028_TXALL_CCICHANNEL_LO.md",
        "strategy_name": "OSCAR028_TXALL_CCICHANNEL_LO",
        "family": "OSCAR series",
        "timeframe": "Intraday",
        "direction": "Both",
        "category": "CCI channel breakout with reversal entries at +/-100",
        "summary": "OSCAR028_TXALL_CCICHANNEL_LO -- TX CCI channel breakout. VarUp=CCI(CCI_Len); CondL=VarUp>100; CondS=VarDn<-100. Primary: flagM=0 -> stop at Highest(H,NN) long / Lowest(L,NN) short. Reversal: VarUp cross under 100 AND C<O -> Sell short (fade CCI exit from overbought with bearish close). VarDn cross over -100 AND C>O -> Buy (fade CCI exit from oversold with bullish close). Stop: avgEntryPrice +/- win_pts*(1-30/100) = 70% of win_pts as SL. Exit: maxEL/maxES limits; t>1330 AND t<1500 session gate. Key insight: CCI >100 = overbought; CCI crossing back below 100 WITH bearish close = confirmed reversal signal; 70% of win_pts as SL means stop placed at 30% pullback of expected profit."
    },
    {
        "path": base + "OSCAR029_TXALL_ADAPTIVEATR_FLT (2).md",
        "strategy_name": "OSCAR029_TXALL_ADAPTIVEATR_FLT",
        "family": "OSCAR series",
        "timeframe": "Intraday",
        "direction": "Both",
        "category": "Adaptive ATR with Bollinger band framework and monthly MDD control",
        "summary": "OSCAR029_TXALL_ADAPTIVEATR_FLT -- TX adaptive ATR breakout. currentV=AvgTrueRange(ATRn); preV=ATR[1]; deltaV=(currentV-preV)/preV = ATR change rate. buyPoint=Highest(High,BackBars); sellPoint=Lowest(Low,BackBars). BollingerBand(Close,BackBars,iff(MP<>1,BBandL,BBandS)) = dynamic band width by position. SL: entryPrice-(buyPoint-sellPoint)/5 = 20% of channel width. Trailing: Setpercenttrailing(AvgPrice*STL*Bigpointvalue,30). Monthly MDD control var for drawdown limiting. AMOpenD_TX/AMLowD_TX AM session functions. BadJump exit: AMOpenD<AMLowD[1] = AM open below yesterday's AM low. Reversal entries: revS/revB market orders. Key insight: deltaV = ATR acceleration; SL at 1/5 of channel = tight stops inside the channel; BadJump exit uses AM session data to detect unfavorable gap-down opens."
    },
    {
        "path": base + "OSCAR029_TXALL_ADAPTIVEATR_FLT.md",
        "strategy_name": "OSCAR029_TXALL_ADAPTIVEATR_FLT_base",
        "family": "OSCAR series",
        "timeframe": "Intraday",
        "direction": "Both",
        "category": "Adaptive ATR Bollinger breakout (base copy)",
        "summary": "OSCAR029_TXALL_ADAPTIVEATR_FLT (base) -- Identical to (2). ATR acceleration as adaptive filter; channel/5 SL; monthly MDD control; AM session BadJump exit. Deduped."
    },
    {
        "path": base + "OSCAR030_TX_3MA_LO.md",
        "strategy_name": "OSCAR030_TX_3MA_LO",
        "family": "OSCAR series",
        "timeframe": "30-minute",
        "direction": "Both",
        "category": "Triple EMA trend with weekly-open breakout and counter-trend reversal",
        "summary": "OSCAR030_TX_3MA_LO (30-min TX) -- Triple EMA trend system. FastL/MidL/SlowL = EMA(AvgPrice,MALen) trend flags with cross-over checks. HPoint/LPoint = entry levels. Primary: flagM=0 -> stop at HPoint/LPoint. Reversal long (Rev_L): mp>0 AND EntriesToday=1 AND barssinceentry>(5*60/BarInterval)/2 AND win_pts<0 -> market (scale-in when losing after half-session). Reversal short (Rev_S): (FastS OR SlowS OR MidS) AND MRO(Close>=Open,3,1)>-1 AND C<OpenW(0). OpenW(0) = weekly open reference. SL: SetStopLoss(AvgPrice*STL); PT: PD (fixed points); trailing: 30% of 3*STL. Key insight: C<OpenW(0) = price below weekly open = weekly downtrend; Rev_L when losing after half-session = scale-in at adversity; barssinceentry>(5*60/BarInterval)/2 = position held for half session."
    },
    {
        "path": base + "OSCAR032_TXALL_2MA_FDL (2).md",
        "strategy_name": "OSCAR032_TXALL_2MA_FDL",
        "family": "OSCAR series",
        "timeframe": "30-minute (FDL=Full Day + Late)",
        "direction": "Both",
        "category": "Dual MA with AM session midpoint entry and CountIf confirmation",
        "summary": "OSCAR032_TXALL_2MA_FDL (30-min, Full Day + Late session) -- Dual SMA with AM session reference. MAL1=Average(High,FastLen); MAL2=Average(High,SlowLen); MAS1/MAS2 on Low. Condition6 = dual MA alignment. Entry: flagM=0 AND mp=0 AND Condition6 AND CountIf(C>O,CI)>CI*0.5 -> stop at (AmHighD_TX(0)+AmCloseD_TX(1))/2 long; (AmLowD_TX(0)+AmCloseD_TX(1))/2 short. AmHighD_TX/AmLowD_TX = AM session functions. CountIf(C>O,CI)>50% = majority of last CI bars are bullish. Trailing: Setpercenttrailing(AvgPrice*STL*2,30). Time filter: T>0900 AND T<1200 OR T>1800 AND T<0500 (includes night session). Key insight: AM session H+prior close / 2 = equilibrium entry between yesterday's sentiment and today's AM range; CountIf majority confirmation prevents premature trend entry; night session inclusion."
    },
    {
        "path": base + "OSCAR032_TXALL_2MA_FDL.md",
        "strategy_name": "OSCAR032_TXALL_2MA_FDL_base",
        "family": "OSCAR series",
        "timeframe": "30-minute (FDL)",
        "direction": "Both",
        "category": "Dual MA AM session midpoint entry (base copy)",
        "summary": "OSCAR032_TXALL_2MA_FDL (base) -- Identical to (2). AM session equilibrium entry; CountIf majority; night session. Deduped."
    },
    {
        "path": base + "OSCAR033_TXALL_2MA_FDL.md",
        "strategy_name": "OSCAR033_TXALL_2MA_FDL",
        "family": "OSCAR series",
        "timeframe": "Intraday (T>0915 AND T<1300 OR night)",
        "direction": "Both",
        "category": "Dual MA with adaptive trailing and multi-layer SL",
        "summary": "OSCAR033_TXALL_2MA_FDL -- TX dual MA with adaptive trailing. MAL1=Average(High,FastLen); MAL2=Average(High,FastLen*2) = 1x/2x ratio. Entry: MP=0 AND flagM=0 AND Condition5 -> stop at Minlist(AmHighD_TX(0),AmHighD_TX(1)) long (lower of today's vs yesterday's AM high = conservative entry). Short: Maxlist(AmLowD_TX(0),AmLowD_TX(1)). Multi-layer SL: SetStopLoss(AvgPrice*STL); fixed at entryPrice-PD*6; additional levels at PD and 5-point tight stop. Adaptive trailing: Setpercenttrailing(AvgPrice*STL*2, 30-BarsSinceEntry/10) = trail percentage TIGHTENS as bars progress. Time filter: T>0915 AND T<1300 OR T>1500 AND T<0500. Key insight: Minlist(AmH(0),AmH(1)) = conservative entry, only entering if today's AM high is below yesterday's; trailing % = 30-BSE/10 means after 100 bars trailing is only 20% = automatic tightening over time."
    },
]

new_entries = []
new_paths = []

for s in strategies:
    path = s["path"]
    if path in digested:
        print(f"SKIP: {os.path.basename(path)}")
        continue

    entry = {
        "timestamp": now,
        "batch": "pla_batch_037",
        "source_file": path,
        "strategy_name": s["strategy_name"],
        "family": s["family"],
        "timeframe": s["timeframe"],
        "direction": s["direction"],
        "category": s["category"],
        "summary": s["summary"],
    }
    new_entries.append(entry)
    new_paths.append(path)
    print(f"NEW: {os.path.basename(path)}")

if new_entries:
    with open(log_path, 'a', encoding='utf-8') as f:
        for e in new_entries:
            f.write(json.dumps(e, ensure_ascii=False) + '\n')

    with open(set_path, 'a', encoding='utf-8') as f:
        for p in new_paths:
            f.write(p + '\n')

    state["last_batch"] = "pla_batch_037"
    state["last_updated"] = now
    state["total_digested"] = state.get("total_digested", 0) + len(new_entries)
    with open(state_path, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    print(f"\nAppended {len(new_entries)} new entries.")
    print(f"Total in digested_set: {len(digested) + len(new_entries)}")
else:
    print("No new entries.")
