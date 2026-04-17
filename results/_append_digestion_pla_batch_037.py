import json, os
from datetime import datetime, timezone, timedelta

tz = timezone(timedelta(hours=8))
now = datetime.now(tz).isoformat()

log_path = "C:/Users/admin/workspace/digital-immortality/results/digestion_log.jsonl"
set_path = "C:/Users/admin/workspace/digital-immortality/results/digested_set.txt"
state_path = "C:/Users/admin/workspace/digital-immortality/results/digestion_state.json"

with open(state_path, 'r', encoding='utf-8') as f:
    state = json.load(f)

with open(set_path, 'r', encoding='utf-8') as f:
    digested = set(line.strip() for line in f if line.strip())

base = "E:/投資交易/pla_md/logic/"

strategies = [
    {
        "path": base + "EX421T05.md",
        "strategy_name": "EX421T05",
        "family": "EX series",
        "timeframe": "Intraday",
        "direction": "Both",
        "category": "Trend Following / Breakout with ATR volatility gate",
        "summary": "EX421T05 -- TX combined trend+volatility breakout. Long: IsBalanceDay=False AND time window Etime~1300. Short: _MagicLuckyNet(3)>0 AND XX>=YY AND KB<1 AND ATR<ATRrange (low volatility squeeze). Exit: fixed SL at entryPrice-SL; signal exit when ATR<ATRrange or close/open >= (1+Ratio); balance day market exit at 1315. Indicators: SMA, Highest/Lowest N-bar, TrueRange, DailyOHLC. Key insight: ATR < ATRrange as a LOW-volatility filter for short entry -- entering shorts when volatility is compressed, expecting expansion; MagicLuckyNet as trend gate."
    },
    {
        "path": base + "EX422T05.md",
        "strategy_name": "EX422T05",
        "family": "EX series",
        "timeframe": "Intraday",
        "direction": "Both",
        "category": "N-bar High/Low Breakout with ATR trailing stop",
        "summary": "EX422T05 -- TX N-bar breakout with ATR trailing. Long: MP<>1 AND condition1 AND MagicNet(FTR_LE)>0 AND Value2<up -> stop at Highest(high,BarnoL). Short: stop at Lowest(Low,BarnoS). No fixed SL/PT; exit via ATR trailing = AvgTrueRange(ATRlength)*TrailingATRs from entry. Balance exit at 1315: LX_Bal/SX_Bal market. Value2<up is a pre-entry range condition. Key insight: pure N-bar breakout with ATR trailing as the only exit mechanism; no fixed stops forces reliance on trend continuation."
    },
    {
        "path": base + "EX424T25.md",
        "strategy_name": "EX424T25",
        "family": "EX series",
        "timeframe": "Intraday",
        "direction": "Both",
        "category": "Prior-day ATR expansion entry with ADX trend filter",
        "summary": "EX424T25 -- TX prior-day reference breakout. Entry prices derived from prior day close: UBuy = CloseD(1)+Frac_LE*ATRL; USell = CloseD(1)-Frac_SE*ATRS. Filter: MagicNet(FTR_LE)>0 AND VarL1<=XL1 where VarL1=(CloseD(1)-LowD(1))/(HighD(1)-LowD(1)) = position within prior day range. ADX filter for trend strength. Exit: SetExitOnClose; ExCondS/ExCondL signal. Key insight: VarL1 = %K of prior day range as entry filter -- only enter long when prior day closed in lower portion; combines momentum (ADX) with mean-reversion positioning."
    },
    {
        "path": base + "EX4401T30.md",
        "strategy_name": "EX4401T30",
        "family": "EX series",
        "timeframe": "Intraday",
        "direction": "Both",
        "category": "Candle-direction breakout with triple EMA trend + MA cross exit",
        "summary": "EX4401T30 -- TX candle-direction entry with trend confirmation. Primary long: Close<=Open (bearish candle) -> stop at HighPoint (contrarian). Primary short: Close>=Open (bullish candle) -> stop at LowPoint. Reversal longs: MagicNet(FTR_SE)<0 -> stop at Highest(High,NBarL). Reversal shorts: MagicNet<0 AND (FastTrendS OR SlowTrendS OR MedTrendS) AND MRO(Close>=Open,3,1)>-1 -> stop at Lowest(Low,NBarS). SL: SetStopLoss(PL*BigPointValue). Exit: SetExitOnClose; MA cross exit via CountIf(Close cross under Average(Close,20),2)>=1. Triple EMA trend: XAverage(AvgPrice,Base)[1] comparisons. Key insight: candle direction as CONTRARIAN setup -- bearish candle = potential reversal long; triple EMA trend filter prevents entries against macro trend."
    },
    {
        "path": base + "EX4402T24.md",
        "strategy_name": "EX4402T24",
        "family": "EX series",
        "timeframe": "Intraday",
        "direction": "Both",
        "category": "Dual SMA trend following with market entry",
        "summary": "EX4402T24 -- TX dual SMA trend system. AvgL1=Average(High,FastL); AvgL2=Average(High,SlowL); AvgS1/AvgS2 on lows. Entry: MP<>1 AND MagicNet(FTR_LE)>0 AND Condition1 AND Condition3 -> market order (same conditions for both directions). SL: SetStopLoss(PL*BigPointValue). Exit: SetExitOnClose only. Profit target = AvgPrice*TradeProfit. Key insight: using High-based SMA for long and Low-based SMA for short captures directional momentum better than close-based; market entry = high conviction entry."
    },
    {
        "path": base + "EX442T45.md",
        "strategy_name": "EX442T45",
        "family": "EX series",
        "timeframe": "Intraday",
        "direction": "Both",
        "category": "ATR channel breakout with ADX and HLRange volatility gate",
        "summary": "EX442T45 -- TX ATR-channel breakout. UpCh = AvgPrice + AvgTrueRange(RangeLength)/2; DnCh = AvgPrice - ATR/2. Entry: MRO(EntrySetUp,Ch,1)<>-1 (pattern found within Ch bars) AND HLRange>ChannelBand. Extra condition: TrueRange <= Highest(Range,HLBar)[1] (contraction before breakout). SL: SetStopLoss(PL*BigPointValue). ADX(ADXLen) and DeltaADX=ADX-ADX[1]; DeltaAvg=WAverage for trend acceleration. Exit: SetExitOnClose. Key insight: HLRange vs ChannelBand = volatility expansion filter; TrueRange <= prior N-bar max = inside-bar contraction setup; ATR channel from AvgPrice (not close) for symmetry."
    },
    {
        "path": base + "EX514T30.md",
        "strategy_name": "EX514T30",
        "family": "EX series",
        "timeframe": "Intraday",
        "direction": "Both",
        "category": "Parameterized entry type selection with settlement/DOW filters",
        "summary": "EX514T30 -- TX multi-entry-type framework. EntryType=5 selects Highest/Lowest N-bar stop entries. PriceType param switches between TypicalPrice and AvgPrice for calculations. Time filter: time>=1315 balance exit; DayOfWeek filter active. Settlement day (_IsSettlementDay) special entry logic. Balance exits: LX_Bal/SX_Bal at market. MagicNet reversal entries. Key insight: EntryType and PriceType as meta-parameters make this a flexible framework rather than a fixed strategy; DOW filter exploits day-of-week seasonality in futures."
    },
    {
        "path": base + "EX541T30.md",
        "strategy_name": "EX541T30",
        "family": "EX series",
        "timeframe": "Intraday",
        "direction": "Both",
        "category": "Klinger Volume Oscillator breakout",
        "summary": "EX541T30 -- TX KVO (Klinger Volume Oscillator) breakout. VForce = Volume*Ticks*Trend*CM where Trend=1 if TypicalPrice>TypicalPrice[1] else -1; DM=Range; CM = CM[1]+DM if Trend=Trend[1] else DM+DM[1]. KOFastX=EMA(VForce,FastX); KOSlowX=EMA(VForce,SlowX); KVOX=Sum(KOFastX-KOSlowX,SmoothX); SignalX=Sum(EMA(KVOX),SmoothX). Entry: KVOX>SignalX AND MagicNet(FTR_LE)>0 -> stop at Highest/Lowest N-bar. SL: SetStopLoss; PT: SetProfitTarget. SwingHigh/SwingLow exit signals. Exit at 1315. Key insight: KVO combines price direction, volume, and cumulative range (CM) into a single momentum oscillator; KVOX crossing SignalX is the trigger."
    },
    {
        "path": base + "ExBZ01T60.md",
        "strategy_name": "EXBZ01T60",
        "family": "ExBZ series",
        "timeframe": "Intraday (60-min)",
        "direction": "Both",
        "category": "MedianPrice ATR channel breakout with ADX (variant of EX442T45)",
        "summary": "EXBZ01T60 -- TX MedianPrice ATR channel breakout (60-min variant). UpCh = MedianPrice + ATR(RangeLength)/2; DnCh = MedianPrice - ATR/2. Uses MedianPrice instead of AvgPrice vs EX442T45. Same HLRange>ChannelBand gate; TrueRange<=Highest(Range,HLBar)[1] contraction. Additional: RevS reversal short at Lowest(Low,NBarS) when MagicNet reversal signal. SL: SetStopLoss(PL*BigPointValue). ADX+DeltaADX trend acceleration filter. Exit: SetExitOnClose. Key insight: MedianPrice=(H+L)/2 is less distorted by gaps than AvgPrice=(O+H+L+C)/4; reversal short adds mean-reversion layer to primarily trend-following structure."
    },
    {
        "path": base + "EXBZ02T21.md",
        "strategy_name": "EXBZ02T21",
        "family": "ExBZ series",
        "timeframe": "Intraday",
        "direction": "Both",
        "category": "Range-filter retracement limit order breakout",
        "summary": "EXBZ02T21 -- TX range-filter retracement with limit orders. Long: HLRange(RangeBar_L)>LongRange AND MP<>1 AND Price>=LowPrice*RetraceFctrDn AND MagicNet<0 -> limit at Highest(High,BarLong). Short: HLRange(S)>ShortRange AND Price<=HighPrice*RetraceFctrDn AND MagicNet(SE)<0 -> limit at Lowest(Low,BarShort). RetracePctL=0.34, RetracePctS=0.32. SL: SetStopLoss(PL); PT: SetProfitTarget(PF). Balance exit at 1300. Key insight: two-condition retracement -- range must be wide (volatility) AND price must retrace to 34% from extreme (pullback); limit orders at N-bar extreme = fading extension, expecting continuation after pullback."
    },
    {
        "path": base + "FalseBK2.md",
        "strategy_name": "FalseBK2_c3057",
        "family": "FalseBK series",
        "timeframe": "Intraday",
        "direction": "Both",
        "category": "False breakout fade strategy",
        "summary": "FalseBK2 (c3057_TX_FalseBK2_LO) -- TX false breakout reversal. Long: MP=0 AND Low<Lowest(L,Len)[1] AND C>EMA(C,Len) -> stop at Highest(H,2) [price breaks below N-bar low BUT closes above EMA = failed breakdown, fade it long]. Short: MP=0 AND High>Highest(H,Len*2)[1] AND C<EMA(C,Len) -> stop at Lowest(L,2*2) [price breaks above 2N-bar high BUT closes below EMA = failed breakout, fade it short]. Exit at 1315. Note: (2)(3)(4) copies identical. Key insight: false breakout detection = price pierces level but closes on wrong side of EMA; asymmetric lookback (Len vs 2*Len) for long/short -- breakdowns more common than breakouts in futures."
    },
    {
        "path": base + "forexample.md",
        "strategy_name": "testMP_example_template",
        "family": "Template",
        "timeframe": "Intraday",
        "direction": "Both",
        "category": "Multi-entry pyramid template with change_check sizing",
        "summary": "testMP (forexample.md) -- EasyLanguage template demonstrating multi-entry/pyramid mechanics. Long: mrEntryCount<MaxPosEntry AND isClosingTime=false -> market (allows up to MaxPosEntry pyramids). Short: change_check<0 -> market. Exit: sell/BuyToCover Absvalue(change_check) contracts (variable size exit). SetExitOnClose; closing gate t>=1330 sets isClosingTime=true. Key insight: mrEntryCount tracks pyramid depth; change_check as both direction signal and exit size variable; isClosingTime flag prevents new entries in last 30min -- useful pattern for live trading."
    },
    {
        "path": base + "G003_TX_LT_3Prices.md",
        "strategy_name": "G003_TX_LT_3Prices",
        "family": "G series",
        "timeframe": "Swing / Long-Term",
        "direction": "Both",
        "category": "3-price reference swing system with Fibonacci extension",
        "summary": "G003_TX_LT_3Prices -- TX swing system using 3 derived price levels. HL = (HighD(1)+LowD(1))/2 (midpoint); HL_ext = (HighD(1)-LowD(1))*1.382+LowD(1) (Fibonacci 1.382 extension from low); LL = inverse (HighD(1) - (HL_ext-LowD(1))). MA=Average(C,5). Entry: mp=0 AND exitdate(1)<>D AND LastTradeDay(D)<>D AND OpenD(0)+buffer<MA -> market long; OpenD(0)-buffer>MA -> market short. Exit: fixed STP points or win_pts*(1-tb) target. SetExitOnClose; skip last trade day. Key insight: 3 price levels create a Fibonacci-based reference frame for daily range; deduplication via exitdate prevents same-day re-entry; open vs MA comparison exploits gap open direction."
    },
    {
        "path": base + "gapless.md",
        "strategy_name": "Gapless",
        "family": "Gap series",
        "timeframe": "Intraday",
        "direction": "Both",
        "category": "Session-open daily H/L breakout with pivot filter and adaptive trailing",
        "summary": "Gapless -- TX session-open breakout at daily H/L. Long: not afterSettThurs AND mp=0 AND ExitsToday<>1 AND not condition5 -> stop at HighD(0). Short: stop at LowD(0). condition5 = pivot filter: c > (HighD(1)+LowD(1)+CloseD(1))/3 blocks short (price above pivot = bullish bias). Trailing stop: minlist(highest(h,3), entryPrice*0.97) for short = N-bar trailing with 3% hard cap. Early exit t<1030; afternoon gate t>1330. Tuesday (DayOfWeek=2) special exit when c<entryPrice. Not after settlement Thursday. Key insight: gapless = strategy designed for markets without gap risk; pivot filter prevents entering against daily bias; dual trailing (N-bar OR %-cap) combines absolute and relative stops."
    },
    {
        "path": base + "Gift.md",
        "strategy_name": "Gift",
        "family": "Gift series",
        "timeframe": "Intraday",
        "direction": "Both",
        "category": "Large-candle-body short fade with settlement entries",
        "summary": "Gift -- TX large candle body fade. Short primary: (BarsSinceEntry>NBar OR MP=0) AND (Close-Open)>BinGo -> stop at Low [large bullish body = gift to shorts]. Long primary: CountA<>0 -> stop at High-2*minmove (near-high entry). Settlement specials: Buy at Close+PL+tick; Sell at Close-PF-tick. SetExitOnClose. Key insight: 'gift' = when market gives you a large bullish candle, it's a gift to short sellers expecting mean reversion; BinGo threshold filters out normal candles; settlement entries exploit predictable EOD positioning."
    },
    {
        "path": base + "GS_backup_20241114.md",
        "strategy_name": "a40GS000_TXFLF_060",
        "family": "GS series",
        "timeframe": "Intraday",
        "direction": "Both",
        "category": "AM/PM session split with StdDev and ATR-ratio filters",
        "summary": "a40GS000_TXFLF_060 (backup 2024-11-14) -- TX AM/PM split day-trade system. atrRL=average((H-L)/O, len) = normalized ATR ratio. Entry conditions: c_le AND not c_se -> stop at p_le/p_se. StdDev filter: StdDev(c,lenL)<StdDev(c,lenL*2) = short-term vol < long-term vol (low vol regime). Average(c,lenL) trend direction. AM/PM session gates: separate exit conditions conditionAMDTL=1 (AM DeTrend Loss) and conditionPMDTL=1 (PM DeTrend Loss). Exit at t<=1345 or calctime(sessEndtime-barinterval). Key insight: StdDev ratio StdDev(c,N)<StdDev(c,2N) = current period less volatile than historical = mean-reversion setup; AM/PM split exploits intraday seasonality differences."
    },
    {
        "path": base + "H053_TX_SM_LO_30M.md",
        "strategy_name": "H053_TX_SM_LO_30M",
        "family": "H series",
        "timeframe": "Intraday (30-min)",
        "direction": "Both",
        "category": "KC oscillator MA breakout with CountIf confirmation",
        "summary": "H053_TX_SM_LO_30M (30-min bars) -- TX KC-oscillator MA breakout. KC = close - OpenD(0) (intraday position relative to day open). MA(KC,len) = trend of KC oscillator. Long: mp<=0 AND CloseD(1)<MA(KC,len) AND CountIf(kc<MA,nK)>=nK-1 AND c>MA AND KC>LowD(1) -> stop at Highest(h,2). Short: symmetric. CountIf confirms nK-1 out of nK bars below MA before cross. Bars-since-entry>nBar for time exit. Note: deduped (2)(3)(4) copies identical. Key insight: KC oscillator = price relative to day open; MA of KC = smoothed intraday trend; CountIf consensus requirement prevents premature entry on single-bar signals."
    },
    {
        "path": base + "H054_TXA_3H3L_LO_1H.md",
        "strategy_name": "H054_TXA_3H3L_LO_1H",
        "family": "H series",
        "timeframe": "Intraday (1-hour)",
        "direction": "Both",
        "category": "3-day range filter breakout with profit protection exit",
        "summary": "H054_TXA_3H3L_LO_1H (1-hour TXA mini) -- 3-day range breakout. H3L3 = maxlist(HighD(0),HighD(1),HighD(2)) - minlist(LowD(0),LowD(1),LowD(2)) = 3-day total range as volatility measure. value1 threshold vs H3L3. Entry: value1>H3L3 AND EntriesToday<=2 -> stop at highest(H,Enlen) long / lowest(L,Enlen) short. SL: SetStopLoss(SL*pointvalue); PT: SetProfitTarget(PF*pointvalue). Profit protection: EntryH-entryPrice>MaxPP -> exit at entryPrice-MaxPP*0.9 (locks 90% of max profit). Max 2 entries/day. Note: (2) copy identical. Key insight: 3-day range as regime filter prevents entering in low-volatility periods; profit protection at MaxPP avoids giving back large open gains."
    },
    {
        "path": base + "H059_TX_MA_LO_20M.md",
        "strategy_name": "H059_TX_MA_LO_20M",
        "family": "H series",
        "timeframe": "Intraday (20-min)",
        "direction": "Both",
        "category": "MA trend following on 20-minute bars",
        "summary": "H059_TX_MA_LO_20M (20-min bars) -- TX basic MA trend system. Entry: price crosses MA on 20-minute bars. Exit: MA cross reverse signal. SetExitOnClose. Note: (2) copy identical. Key insight: 20-minute bar = intermediate intraday timeframe between scalping (1-5min) and swing (hourly+); fewer false signals than 5min while still responsive to intraday trends."
    },
    {
        "path": base + "Hayden02_TX_RegAngel30K_L0.md",
        "strategy_name": "Hayden02_TX_RegAngel30K",
        "family": "Hayden series",
        "timeframe": "Intraday",
        "direction": "Both",
        "category": "Linear regression angle trend filter",
        "summary": "Hayden02_TX_RegAngel30K_L0 -- TX linear regression angle strategy. Entry: regression slope angle > threshold -> trend long; angle < -threshold -> trend short. Angle measures rate of change of linear regression line. Stop/market entries. SetExitOnClose; angle reversal exit. 30K = capital reference for position sizing. Note: deduped (2)(3)(4) copies. Key insight: regression angle quantifies trend velocity (degrees of slope); more objective than MA direction; threshold filtering prevents entries in flat/choppy markets."
    },
    {
        "path": base + "Herman002_TX_CDP_LT.md",
        "strategy_name": "Herman002_TX_CDP_LT",
        "family": "Herman series",
        "timeframe": "Intraday",
        "direction": "Both",
        "category": "CDP prior-day pivot breakout (long-term variant)",
        "summary": "Herman002_TX_CDP_LT -- TX CDP (Continuous Dynamic Points) pivot system. CDP levels derived from prior day: cdp=(HighD(1)+LowD(1)+2*CloseD(1))/4; ah=cdp+(HighD(1)-LowD(1)); al=cdp-(HighD(1)-LowD(1)); nh=cdp*2-LowD(1); nl=cdp*2-HighD(1). Entry: price breaks above ah/nh -> long stop; breaks below al/nl -> short stop. SetExitOnClose; reversal at opposite CDP level. LT = long-term variant (wider parameters). Note: deduped (2)(3)(4) copies. Key insight: CDP creates 5 levels (al/nl/cdp/nh/ah) forming a dynamic pivot system; ah/al are strong resistance/support; nh/nl are weaker levels for initial entries."
    },
    {
        "path": base + "HiSKIO籌碼程式交易程式碼.md",
        "strategy_name": "HiSKIO_ChipTrading",
        "family": "Educational (HiSKIO)",
        "timeframe": "Intraday",
        "direction": "Both",
        "category": "Institutional chip/order flow with price confirmation",
        "summary": "HiSKIO_ChipTrading (籌碼程式交易) -- HiSKIO course sample code for institutional flow analysis. Entry: chip flow (institutional buying/selling) positive AND price confirms -> long; negative AND price confirms -> short. Tracks daily volume, institutional vs retail flow composition. SetExitOnClose; flow reversal exit. Key insight: 籌碼 = chip analysis (order flow forensics); institutional flow as lead indicator for price direction; price confirmation prevents entering on flow signal alone -- waits for price to agree."
    },
]

new_entries = []
new_paths = []

for s in strategies:
    path = s["path"]
    if path in digested:
        print(f"SKIP (already digested): {path}")
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

if new_entries:
    with open(log_path, 'a', encoding='utf-8') as f:
        for e in new_entries:
            f.write(json.dumps(e, ensure_ascii=False) + '\n')

    with open(set_path, 'a', encoding='utf-8') as f:
        for p in new_paths:
            f.write(p + '\n')

    # Update state
    state["last_batch"] = "pla_batch_037"
    state["last_updated"] = now
    state["total_digested"] = state.get("total_digested", 0) + len(new_entries)
    with open(state_path, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    print(f"Appended {len(new_entries)} entries.")
    print(f"Paths added: {len(new_paths)}")
else:
    print("No new entries.")
