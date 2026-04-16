import json, os
from datetime import datetime, timezone, timedelta

tz = timezone(timedelta(hours=8))
now = datetime.now(tz).isoformat()

log_path = "C:/Users/admin/workspace/digital-immortality/results/digestion_log.jsonl"
set_path = "C:/Users/admin/workspace/digital-immortality/results/digested_set.txt"
state_path = "C:/Users/admin/workspace/digital-immortality/results/digestion_state.json"

# Read current state
with open(state_path, 'r', encoding='utf-8') as f:
    state = json.load(f)

with open(set_path, 'r', encoding='utf-8') as f:
    digested = set(line.strip() for line in f if line.strip())

base = "E:/投資交易/pla_md/signal/"

strategies = [
    {
        "path": base + "@@@173_TX_DVNormal_D0.md",
        "strategy_name": "173_TX_DVNormal_D0",
        "family": "Custom (DayVolatility)",
        "timeframe": "Intraday D0 (day-only)",
        "direction": "Both",
        "category": "Volatility breakout with custom DayVolatility function",
        "summary": "DVNormal -- TX intraday volatility breakout using custom DayVolatility function. Calculates cumulative open-close gaps over N days, splits into bullish (HCO) and bearish (LCO) components. Entry: when DayVolatility/len exceeds filter(1.9x) of avg bar range (75*len bars), price above/below AM open. Exit: trailing stop at midpoint of AM open + yesterday low/high when highest/lowest bar is in first half of trade. EOD exit at 13:35. Key insight: directional volatility decomposition -- separates gap energy into up/down components for directional bias."
    },
    {
        "path": base + "@@202106T90_Normal_CDP_K_D0.md",
        "strategy_name": "T90_Normal_CDP_K_D0",
        "family": "T90 (AZ series)",
        "timeframe": "4K D0 (day-only)",
        "direction": "Both",
        "category": "CDP-based with MA filter and KD regime detection",
        "summary": "T90_Normal_CDP -- TX 4K intraday CDP strategy with MA overlay. Computes CDP pivot (cdp/ah/nh/nl/al). Entry: MA>nh = bullish regime (buy at max(close,open)); MA<nl = bearish (sell at min(close,open)). Reversal entries when price extends 2x daily range beyond CDP. Mean-reversion entries when MA between levels but price dips below nl or spikes above nh with CountIf confirmation. Stop loss at STP(2%), trailing profit target, and 7-bar regime change exit using avg CDP. Walk-forward params shift STP/len/in across periods. Key insight: CDP levels + MA creates regime filter; reversal entries at 2x extensions are contrarian mean-reversion within trend context."
    },
    {
        "path": base + "@@202106T90_STRONG.md",
        "strategy_name": "T90_CDP_Strong_D0",
        "family": "T90 (AZ series)",
        "timeframe": "4K D0 (day-only)",
        "direction": "Both",
        "category": "CDP strong-trend variant with turbo mode and multi-entry",
        "summary": "T90_STRONG -- Aggressive CDP variant with TURBO mode. Same CDP framework as Normal but adds mid-range entries when MA is between CDP and nh/nl (TURBO ON -- entries at MA level with gap confirmation). Extra mean-reversion entries (SH/BL) when price stays between nh-ah or nl-al for 3 bars, with reversal triggers after 5 bars. Hold-exit: if >50% of bars since entry are losing and bars>10, tighten stop to 50% of STP(4.2%). MAMid = 125-bar avg CDP for regime exit. Key insight: turbo mode exploits mid-range opportunities the Normal version skips; wider STP(4.2% vs 2%) enables longer holds in strong trends."
    },
    {
        "path": base + "@@202107T89_CriticalOpenXDP_3K_D0.md",
        "strategy_name": "T89_CriticalOpenXDP_3K_D0",
        "family": "T89 (AZ series)",
        "timeframe": "3K D0 (day-only)",
        "direction": "Both",
        "category": "CDP with delayed open integration and Fibonacci exits",
        "summary": "T89_CriticalOpenXDP -- TX 3K CDP strategy using delayed open price (calctime in-bars after session start) blended into CDP calculation. CDP uses (H1+L1+C1+OPENIN)*0.25 -- incorporating intraday open after in bars for more informed pivot. Entry: OPENIN>cdp = bullish bias; breakout/reversal entries with ratio(1.6x) daily range threshold. Fibonacci exit: C crosses below ah+(ah-nh)*(1-0.618). NOLOSE exit: if >ratio/2 bars are profitable, lock profit at entry+avggap*ratio. Midpoint exit at (high+low)*0.5 after half session. Key insight: delayed open integration makes CDP more adaptive; Fibonacci-based trailing is unique among CDP variants."
    },
    {
        "path": base + "@LV@_TX_BayesLaw_7K_LT.md",
        "strategy_name": "LV_TX_BayesLaw_7K_LT",
        "family": "LoveVan (@LV@)",
        "timeframe": "7K LT (long-term, multi-day hold)",
        "direction": "Both",
        "category": "Bayesian conditional probability with wait/confidence states",
        "summary": "BayesLaw_7K_LT -- Concept from Bayes Law. Multi-day hold strategy with state machine. States: wait(0/1) based on 3 consecutive losing position bars; winL/winS tracks if last same-direction trade won. Skips first 2 days and settlement day. Entry conditions: higher lows + close above (prev_close+2*prev_high)/3 for long; CountIf on consecutive HH/HL bars. 3-tier difficulty: standard (2/4 bars confirming), hard (previous winner, 2/3 confirming), very hard (wait=1, 3/3 confirming + gap). Stop: 0.618 * max(daily_range, CDP_range), widening by ED (entry-days) factor. Protect profit when win_pts > stp*1.618 or ed>3. Key insight: Bayesian updating -- prior trade outcome (win/loss) + market state (wait) determines entry strictness. Truly adaptive conditional probability framework."
    },
    {
        "path": base + "@LV@_TX_Kings_men_11K_LT.md",
        "strategy_name": "LV_TX_Kings_men_11K_LT",
        "family": "LoveVan (@LV@)",
        "timeframe": "11K LT (long-term, multi-day hold)",
        "direction": "Both",
        "category": "Resilience-based trend following with weekly confirmation",
        "summary": "Kings_men_11K_LT -- Fighting with resilience (from Kings Men movie). Multi-day hold with weekly confirmation. Entry conditions: standard = C+open > prev_high+prev_close AND daily low > prev_low; hard (wait=1) adds weekly confirmation (prev week close+open > 2*two-days-ago close AND weekly low > prev weekly low). Stop: asymmetric STP_L/STP_S calculated from (entry - midpoint of prev close+low/high). Widens by ED factor for multi-day holds. Reversal exit: if price reverses to entry level and opposite condition fires. Protecting position: after ed>=2, when price retreats to (entry*2+EntryH)/3, exit at lowd-min(ED, avgHL). Gap filter at session end. Key insight: weekly+daily dual-timeframe confirmation for resilience; asymmetric stops based on distance-to-support/resistance."
    },
    {
        "path": base + "@LV@TX_AAA_13K_LT.md",
        "strategy_name": "LV_TX_AAA_13K_LT",
        "family": "LoveVan (@LV@)",
        "timeframe": "13K LT (long-term, multi-day hold)",
        "direction": "Both",
        "category": "Post-big-move continuation (Acting Again After)",
        "summary": "AAA_13K_LT -- After big trend, Acting Again. Requires prior large move: highest-lowest over 4*ky bars > R(3.4)*0.005*open. Then checks momentum: close moved > R*0.005*open*0.5 over 2*ky bars in trend direction. Plus daily bias: open+close > prev_close+prev_high for long. Stop: half of 4*ky-bar range, widens by ED factor. Protect position after ed>=2 when price in profit but retreating. Key insight: continuation-after-volatility-expansion -- waits for big move to establish, then rides the follow-through. R parameter controls required prior volatility magnitude."
    },
    {
        "path": base + "@M@S@Avg_MA.md",
        "strategy_name": "MS_Avg_MA_LT",
        "family": "M@S (Master/Student series)",
        "timeframe": "10-min LT (long-term, swing)",
        "direction": "Both",
        "category": "MA slope trend following with LinearRegAngle filter",
        "summary": "MS_Avg_MA -- TX 10-min MA trend follower using avgp=(O+H+L+C)/4 with 105-bar average. Entry: 3 consecutive rising/falling MA bars + LinearRegAngle of avgp since entry confirms direction. Entry at max(highD(0), highD(1)) for breakout. Exit: trailing profit at EntryH - win_pts*0.1; stop at entry +/- slp(0.1*open) loosening by bars-since-entry; regime exit when k>klen(90) and angle reverses. Avoids settlement Thursday and last trade day. Key insight: avgp smoothing reduces noise; LinearRegAngle since entry validates trade trajectory; stop loosens over time (barssinceentry adjustment) -- time = friend for winners."
    },
    {
        "path": base + "@M@S@DT_ORB.md",
        "strategy_name": "MS_DT_ORB",
        "family": "M@S (Master/Student series)",
        "timeframe": "8-min DT (day-trade, session close)",
        "direction": "Both",
        "category": "Opening range breakout with K-power momentum and candle pattern exit",
        "summary": "MS_DT_ORB -- TX 8-min day-trade ORB with cumulative K-power (sum of close-open per bar). Entry L1: kpwr>0 + daily low/open avg above prev close = breakout at highD. Entry L3: gap-up (close1-open0 > daily range) = breakout at HighD. Candle pattern exit: 3 consecutive bars where upper shadow > be(3.4x) lower shadow AND range>10pts = exhaustion signal. Stop at entry +/- rstl(1.1%)*open. EOD exit 13:42. Key insight: K-power as cumulative intraday momentum indicator; candle body-shadow ratio for exhaustion detection is sophisticated pattern recognition."
    },
    {
        "path": base + "@M@S@EMA.md",
        "strategy_name": "MS_EMA_FDT",
        "family": "M@S (Master/Student series)",
        "timeframe": "6-min FDT (flip, day+night sessions)",
        "direction": "Both",
        "category": "EMA trend following with K-power momentum across day/night sessions",
        "summary": "MS_EMA -- TX 6-min XAverage(205) trend follower spanning day+night sessions. Entry: NN(3) consecutive rising/falling EMA + 3 consecutive higher/lower closes + cumulative kpwr exceeds gap(65) threshold. After 2017/05: market orders (more aggressive). Exit: EMA slope reverses AND kpwr crosses zero with barssinceentry loosening; rate-based stop at 1.2%*open; short-term kpwr10 (6-bar) exceeds gap = momentum reversal. Key insight: dual kpwr (full-session + short-term) provides multi-timeframe momentum; night session trading post-2017 reform."
    },
    {
        "path": base + "@M@S@FDT_CDP.md",
        "strategy_name": "MS_FDT_CDP",
        "family": "M@S (Master/Student series)",
        "timeframe": "9-min FDT (flip, day+night sessions)",
        "direction": "Both",
        "category": "CDP pivot with ada (all-day-adjusted) OHLC for night session support",
        "summary": "MS_FDT_CDP -- TX 9-min CDP using ada (all-day-adjusted) OHLC functions for accurate day+night session pivots. CDP calculated from Highada/Lowada/Closeada(1). Entry B1: close > (ah+nh)/2 above openada (first entry); B2: close > ah (re-entry at Highada breakout). Candle exhaustion exit: 3 bars with shadow ratio > be(2.2) and range >10pts. Profit limit at entry*(1+/-slr(0.2%)). Time exit adjusted for pre/post 2017 night session reform. Key insight: ada functions solve the TAIFEX night-session OHLC problem -- standard HighD/LowD break across sessions, ada provides continuous daily aggregation."
    },
    {
        "path": base + "@M@S@LT_Mother_Son.md",
        "strategy_name": "MS_LT_Mother_Son",
        "family": "M@S (Master/Student series)",
        "timeframe": "LT (long-term, swing)",
        "direction": "Both",
        "category": "Inside bar (mother-son candle) breakout",
        "summary": "MS_LT_Mother_Son -- Inside bar breakout. Identifies mother-son pattern: highD(2)>=highD(1) AND lowD(2)<=lowD(1) (day2 engulfs day1 = day1 is inside bar). Sets uband/dband at inside bars high/low. Tracks hh/ll since pattern formation. Entry: close > uband AND bullish candle = buy at hh (highest since pattern). Exit: next day makes lower high AND lower low = trend reversal; rate stop at rSLP(1.7%)*open. Avoids settlement Thursday and last trade day. Key insight: clean inside-bar implementation; cnt counter tracks time since pattern -- longer consolidation = stronger breakout."
    },
    {
        "path": base + "@M@S@LT_WD4_WD3.md",
        "strategy_name": "MS_LT_WD4_WD3",
        "family": "M@S (Master/Student series)",
        "timeframe": "LT (long-term, weekly cycle)",
        "direction": "Both",
        "category": "Weekly range breakout (Thursday-to-Wednesday cycle)",
        "summary": "MS_LT_WD4_WD3 -- Weekly range breakout on Thursday-to-Wednesday cycle. Resets weekly high/low on Thursday open; accumulates through Wednesday. Entry: 2 consecutive closes >= prior weekly high = breakout buy at max(dhh, highD) stop. Stop: fixed slp(85) pts; weekly reversal exit on Wednesday if new week fails to exceed old weeks range. Profit take: win_pts > (whh-wll)*be(0.8) with trailing at EntryH - win_pts/4. Key insight: non-standard weekly cycle (Thu-Wed instead of Mon-Fri) aligns with TAIFEX settlement calendar; dhh/dll track intra-cycle developing highs/lows for precision entry."
    },
    {
        "path": base + "@M@S@WD1_WD5.md",
        "strategy_name": "MS_WD1_WD5",
        "family": "M@S (Master/Student series)",
        "timeframe": "LT (long-term, weekly cycle)",
        "direction": "Both",
        "category": "Weekly range breakout (Friday-to-Monday cycle)",
        "summary": "MS_WD1_WD5 -- Weekly range breakout on Friday-to-Monday cycle. Resets on Friday close or Monday open. Entry: 2 closes > prior weekly high AND close > prev close AND close-whh < (whh-wll)*be(0.71) -- breakout not too extended. Stop: rslp(7%)*open (wide for weekly holds); Friday reversal check; no-trend exit if >50% of bars since entry are below whh. Profit trailing at EntryH - win_pts/4; stop at min(entry-slp, whh-slp). Key insight: 7% stop is extremely wide for weekly system -- true swing trading; be(0.71) filter ensures entry near breakout, not at extended levels."
    },
    {
        "path": base + "@S_010_3G_D.md",
        "strategy_name": "S_010_3G_D",
        "family": "@S (Standard series)",
        "timeframe": "D0 (day-only)",
        "direction": "Both",
        "category": "Fibonacci 1.382 extension breakout with 5 entry scenarios",
        "summary": "S_010_3G -- TX intraday Fibonacci 1.382 extension. Calculates up=HL*1.382+Low, dn=High-HL*1.382, mid=(H+L)*0.5 from prior day. 5 entry scenarios: L1=open>up+bullish bar; L2=open between mid-up, high>up; L3=open<=mid but high>up (stretch breakout); L4=open<dn but first bar bullish, high>dn (reversal); L5=consolidation between dn-mid with low>mid (support hold). First half of day only (midK). EOD time exit. Key insight: systematic coverage of all open-relative-to-Fibonacci scenarios -- each entry type captures different market open behavior relative to 1.382 extensions."
    },
    {
        "path": base + "@S_047_TX_Trender_D.md",
        "strategy_name": "S_047_TX_Trender_D",
        "family": "@S (Standard series)",
        "timeframe": "7-min D0 (day-only)",
        "direction": "Both",
        "category": "PercentRank extremes with avg point movement breakout",
        "summary": "S_047_Trender -- 7-min intraday trend follower. Uses PercentRank: if low from len-1 bars ago is in bottom 10th percentile of last len(8) lows AND today high breaks above that low + perKPnt*num(9) average bar moves = trend confirmed. Entry at today high (highada). Stop level set at the extreme bar price. Fixed stl(185) point stop loss. EOD exit. Key insight: PercentRank identifies extreme lows/highs as launchpads; num*perKPnt threshold ensures sufficient escape velocity from the extreme -- combines statistical extreme detection with momentum confirmation."
    },
    {
        "path": base + "@S_072_TX_OpenerV3_L.md",
        "strategy_name": "S_072_TX_OpenerV3_L",
        "family": "@S (Standard series)",
        "timeframe": "15-min LT (long-term, swing)",
        "direction": "Both",
        "category": "Gap opening with average daily range stop",
        "summary": "S_072_OpenerV3 -- 15-min gap-open swing strategy. Entry: open > prev day high (gap-up) = buy at today high stop; open < prev day low (gap-down) = sell at today low. Uses array of last 20 days daily ranges with rolling average (dist.avg) for adaptive stop: stl=dist.avg*ratio(1.5). Bad-K exit: if close breaks below min(prev_low, open-dist.avg). Overbought exit: if win_pts > 2*stl and daily range exceeds dist.avg. Stop loosens by dist.avg/3 per holding day (k.day). Avoids settlement days +/-1 day. Key insight: array-based rolling daily range is more robust than simple ATR; stop loosening per day held acknowledges trend persistence."
    },
    {
        "path": base + "@SpyGrid(蛛網，網格交易).md",
        "strategy_name": "SpyGrid_GridTrading",
        "family": "Utility/Special",
        "timeframe": "Multi (grid)",
        "direction": "Long-biased grid",
        "category": "Grid trading system for stocks/ETFs with position scaling",
        "summary": "SpyGrid -- Grid trading system for TAISE stocks. Sets grid levels at +pSPersen(5.1%)/-pBPersen(5%) from reference price. Initial buy of pGrid(10) contracts, then buys at lower grid / sells at upper grid. Tracks net PnL, MDD, minimum capital required. Position cap at 2x grid size. UpMove mode: ratchets grid upward when price exceeds upper band. Uses TAISE tick-size functions for proper price rounding. Displays real-time stats: price/MP/amt/netprofit/MDD/return%. Key insight: proper implementation of grid trading with TAISE-specific tick sizes; capital efficiency metrics (Net/Amt/Cnt) enable comparison across instruments."
    },
    {
        "path": base + "@TX_20210219_LO.md",
        "strategy_name": "TX_20210219_LO",
        "family": "Custom",
        "timeframe": "LO (long-only swing)",
        "direction": "Both",
        "category": "3-day average high/low breakout",
        "summary": "TX_20210219_LO -- Swing strategy using 3-day average highs/lows. hh=avg(highD(1-3)), ll=avg(lowD(1-3)). Entry: high > hh AND open > prev low = buy at (highD+open)/2 stop; low < ll AND open < prev high = sell at (lowD+open)/2 stop. After in(54-69) bars delay. Trailing stop at EntryH/L +/- (hh-ll). Gap reversal exit: if open gaps against position. Walk-forward shifts in parameter. Key insight: 3-day averaged levels smooth out single-day noise; entry at midpoint of today extreme + open is compromise between aggressive and conservative entry."
    },
    {
        "path": base + "000_TX_CDPKD_D0.md",
        "strategy_name": "000_TX_CDPKD_D0",
        "family": "Numbered series (000)",
        "timeframe": "5K D0 (day-only)",
        "direction": "Both",
        "category": "CDP + SlowK stochastic with dynamic box range",
        "summary": "CDPKD_D0 -- TX 5K intraday CDP + KD oscillator. Builds dynamic hbox/lbox from first in-3 bars nh/nl levels. Entry: bar counter > in AND close breaks out of hbox/lbox AND close vs midpoint AND SlowDCustom(9) > kd_val(74-78) for long / < (100-kd_val) for short AND open gap confirmation. Stop: stp(60) pts, reduces to 50% when bar > 30 AND highest losing bar exceeds 50% of barssinceentry -- dynamic stop tightening when trade goes nowhere. EOD exit 13:25. Walk-forward shifts in/kd_val. Key insight: CDP range as initial box + KD overbought/oversold filter; stop halving when position is stuck is practical money management."
    },
    {
        "path": base + "001_TX_3Red_LO-1.md",
        "strategy_name": "001_TX_3Red_LO",
        "family": "Numbered series (001)",
        "timeframe": "45-min ALL (all sessions, 100K fee)",
        "direction": "Both",
        "category": "Three consecutive same-direction candle momentum with MA filter",
        "summary": "3Red_LO -- 45-min 3-candle momentum strategy. Entry: 3 ascending opens (o>o[1]>o[2]) + 2 higher closes + close>MA(n2=59-71) + net candle body power between n1(11-19) and 10*n1 (not too strong/weak) + no single bar > n2 pts (avoid spike bars). Volatility filter: 3-bar max body span < stp(130-170). Bad-entry detection: if bar after entry strongly reverses (body > prev body, breaks prev close, and crosses MA) = set bad_entry flag for immediate exit. Multi-exit: 3*n1 bar timeout if losing; lowest(len) trailing; 4*n1 adverse move; 3*stp profit take; 3 consecutive counter-candles. Key insight: bad-entry pattern recognition is sophisticated -- detects when entry bar was a false signal immediately, cutting losses before stop hit."
    },
    {
        "path": base + "001_TX_KPOWER_DO.md",
        "strategy_name": "001_TX_KPOWER_DO",
        "family": "Numbered series (001)",
        "timeframe": "10K D0 (day-only)",
        "direction": "Both",
        "category": "Candle body ratio (K-Power) momentum with trailing stop",
        "summary": "KPOWER_DO -- TX 10K intraday K-power (candle body ratio). Entry: CountIf (c-l)/(h-l) > 0.5 over len(8) bars >= 5 (majority of bars close in upper half) + daily bias (avg of low+open > prev close) + current bar bullish. Entry at highest(h, len3=5) stop. Trailing stop at movingstl(200) pts from position high/low. Profit target at entry+300 limit. EOD settlement exit. Key insight: (c-l)/(h-l) ratio as K-power -- measures closing position within bar range; statistical counting (5/8 bars) provides robust momentum detection vs single-bar patterns."
    },
    {
        "path": base + "001_TX_MACD_LO.md",
        "strategy_name": "001_TX_MACD_LO",
        "family": "Numbered series (001)",
        "timeframe": "1H (hourly, swing)",
        "direction": "Both",
        "category": "MACD histogram momentum with monthly loss limit and wrong-position exit",
        "summary": "MACD_LO -- TX hourly MACD histogram momentum with risk management. MACD(12,26,9). Counts consecutive bars of rising/falling histogram (buycount/sellcount). Entry: count >= EnterCount(9) + 3 higher lows/lower highs. Exit: count > OutCount(9) in opposite direction + close/open reversal. Monthly loss limiter: tracks cumulative monthly PnL, stops trading when monthly loss or MDD exceeds monthlevel(100K). Wrong-position exit: after BarX(8) bars, if >50% of bars have close against entry. N-bar lowest/highest trailing stop at BarN(30). Short profit limit at -7%. Key insight: monthly loss circuit breaker is professional risk management; wrong-position detector uses statistical evidence rather than fixed stop."
    },
    {
        "path": base + "001_TX_PT_D0.md",
        "strategy_name": "001_TX_PT_D0",
        "family": "Numbered series (001)",
        "timeframe": "D0 (day-only)",
        "direction": "Both",
        "category": "Pivot Trend with up/down volume accumulation",
        "summary": "PT_D0 -- TX intraday Pivot Trend strategy. Tracks cumulative up-volume (when high > prev close, adds h-l[1]) and down-volume (when prev close > low, adds h[1]-l). Entry: abs(up-dn) > previous session swing (sw) AND CountIf(consecutive higher lows or lower highs) >= G(60%) of bars. Entry at highest(h,3) stop. Exit: trailing stop at weighted avg of AM high/low minus max of current/previous daily range. Session 09:00-11:00 only. EOD exit. Key insight: up/dn accumulation is simplified volume-spread analysis -- measures directional pressure without volume data; G parameter sets consistency threshold."
    },
    {
        "path": base + "001_TX_Range R_LO.md",
        "strategy_name": "001_TX_Range_R_LO",
        "family": "Numbered series (001)",
        "timeframe": "19-min LO (swing, AM+PM)",
        "direction": "Both",
        "category": "Volatility expansion with Williams %R and adaptive trade limiting",
        "summary": "Range_R_LO -- TX 19-min volatility expansion strategy. Detects range expansion: near-term avg range > far-term avg range (R_near > R_far). Combines with Williams %R: > 80 for longs, < 20 for shorts. Adaptive trade limiting: if last 3 trades lost, limits to 1 trade/day; otherwise allows 3. Exit on contraction: R_near < R_far + opposite %R signal. Trailing pullback: EntryH/L minus recent close range when R_near > aa(60). Walk-forward stable: len(17-21), aa(45-60). Key insight: volatility cycle (compression->expansion->contraction) as regime framework; adaptive trade frequency based on recent PnL is practical money management."
    },
    {
        "path": base + "002_Sw_D_5min_Linear.md",
        "strategy_name": "002_Sw_D_5min_Linear",
        "family": "Numbered series (002)",
        "timeframe": "5-min D (swing, day+settlement aware)",
        "direction": "Both",
        "category": "Linear regression crossover with closing price zone filter",
        "summary": "Sw_D_5min_Linear -- TX 5-min linear regression strategy. LinearRegValue(16) vs XAverage(LR1, 32) crossover. Entry: N-1/N(12/13) bars of LR1 momentum in one direction + close vs prior day avg+/-range zone filter. Session 08:45-10:00 only, first entry of day. Exit: fixed sl(55-85) pts stop; 250pt profit trailing at lowest(l,2)/highest(h,2); moving profit: when maxprofit > 200 and position retraces > 50%, exit at market. Settlement day awareness with tag variable. Walk-forward: len(12-16), N(11-13), sl(55-85). Key insight: LinearReg vs its own EMA creates a smooth momentum oscillator; 50% retracement of max profit is an effective trailing method."
    },
    {
        "path": base + "002_TX_Keltner_LO_2010.md",
        "strategy_name": "002_TX_Keltner_LO_2010",
        "family": "Numbered series (002)",
        "timeframe": "13-min AM LT (long-term, swing)",
        "direction": "Both",
        "category": "Keltner Channel breakout with flag-based entry tracking",
        "summary": "Keltner_LO_2010 -- TX 13-min Keltner Channel (avg + ATR*KAtr(3.8) envelope, KLen=18). Entry: close crosses above upper band = sets Bflag, records HH; buys at HH+1 stop on next bar. Similar for shorts. Stop: fixed STL(90) pts; trailing Gap(180) pts from EntryH/L; band reversal exit (price fully below opposite band). 09:00-13:30 entry window. Key insight: Bflag mechanism decouples signal detection from entry execution -- close crossing band signals intent, but actual entry waits for HH+1 breakout confirmation. 3.8x ATR is very wide = catches only strong breakouts."
    },
    {
        "path": base + "002K_TX_PBO_LO(HW4).md",
        "strategy_name": "002K_TX_PBO_LO_HW4",
        "family": "Numbered series (002K)",
        "timeframe": "Multi-bar LO (swing)",
        "direction": "Both",
        "category": "Multi-scenario breakout with weekly midpoint, gap reversal, and NDayH/L",
        "summary": "PBO_LO (HW4) -- Complex multi-scenario breakout. 1) Gap reversal: open gaps above NDayH(3-day high) but closes below it with >80pt retracement = sellshort. 2) Weekly midpoint: close crosses through last week (H+L)/2 = enter with NDayL protection. 3) Standard breakout: 3 bars > NDayH with K-power majority + not gapped + LastWeekMiddleBiasLimit(500). 4) Reverse-on-reversal: if position retraces >RevStopVal(140) or gap-opens against = reverse position with bRevFlag. Middle-entry separate exit regime (stop at max(lastWeekMiddle, NDayL)). Walk-forward: notin(4-12), jump(50-130), RevStopVal(80-140). Key insight: systematic coverage of 4 distinct market scenarios with separate exit regimes per entry type -- each scenario has its own risk profile."
    },
    {
        "path": base + "006_LLH_6mK_FDO.md",
        "strategy_name": "006_LLH_6mK_FDO",
        "family": "Numbered series (006)",
        "timeframe": "6-min FDO (flip, day+night, day-only exits)",
        "direction": "Both",
        "category": "Consecutive higher low / lower high with ada OHLC",
        "summary": "LLH_6mK_FDO -- TX 6-min consecutive bar pattern using ada functions. Entry: h>h[1] AND l>l[1] AND l>closeada(1) for longs (higher high + higher low + above prev session close). First entry only per day, after in(10) bars. Stop: max(lowada(0), entry-sn(100)). Profit target: entry + (entry-lowada) + sn when H-entry > 2*sn AND lowada distance > sn. PM/night session exit if losing and below close. Time exit before night session end. Key insight: simple but effective -- consecutive HH+HL is strong momentum signal; ada functions handle night session OHLC correctly for TAIFEX."
    },
    {
        "path": base + "006_TXA_13mLineReg_LOS_V2.md",
        "strategy_name": "006_TXA_13mLineReg_LOS_V2",
        "family": "Numbered series (006)",
        "timeframe": "13-min LOS (long/short swing)",
        "direction": "Both",
        "category": "Linear regression angle with dual-timeframe trend detection and circuit breaker",
        "summary": "TXA_13mLineReg_LOS_V2 -- TX 13-min linear regression angle strategy. LinearRegValue(45) vs AverageFC(45) for trend; LinearRegAngleFC(6) > p2(58) for entry timing; LinearRegAngleFC(15) for exit timing. BullTrend = LR > LR[1] AND LR > MA AND angle > 58. Exit when angle < threshold and LR < MA. 9% daily limit circuit breaker: if high/low exceeds prev close * 1.09 = force exit (market crash/rally protection). Fixed 150pt stop. Skips first day after settlement. Walk-forward: Len(45), p1(-87), p2(58). Key insight: 3-speed angle system -- fast(6) for entry, medium(15) for exit, slow(45) for trend. 9% circuit breaker is unique risk management for tail events."
    }
]

# Write to JSONL
with open(log_path, 'a', encoding='utf-8') as f:
    for s in strategies:
        entry = {
            "path": s["path"],
            "strategy_name": s["strategy_name"],
            "family": s["family"],
            "timeframe": s["timeframe"],
            "direction": s["direction"],
            "category": s["category"],
            "summary": s["summary"],
            "timestamp": now,
            "tier": 1,
            "readable": True,
            "summary_length": len(s["summary"])
        }
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# Update digested set
new_paths = []
for s in strategies:
    if s["path"] not in digested:
        new_paths.append(s["path"])
        digested.add(s["path"])

# Also add variant/duplicate files as digested
variant_files = [
    base + "@M@S@EMA (5).md",
    base + "@M@S@EMA (6).md",
    base + "@CF 20220112.1.md",
    base + "@CF v20210125.1.md",
    base + "@MC2_All.md",
    base + "@MR_Total v20210125.1.md",
]
for v in variant_files:
    if v not in digested:
        new_paths.append(v)
        digested.add(v)

with open(set_path, 'a', encoding='utf-8') as f:
    for p in new_paths:
        f.write(p + "\n")

# Update state
new_count = len(digested)
state["files_digested"] = new_count
for s in strategies:
    if s["path"] not in state.get("digested_paths", []):
        state.setdefault("digested_paths", []).append(s["path"])

with open(state_path, 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

print(f"Digested {len(strategies)} strategies")
print(f"Total digested files: {new_count}")
print(f"Previous: 486, New strategies: {len(strategies)}, Variants skipped: {len(variant_files)}")
