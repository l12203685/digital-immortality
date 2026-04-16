"""Append PLA batch 001: First 30 unique PLA signal strategies from E:/投資交易/pla_md/signal/.

B2 pipeline. 2026-04-16. Opening PLA strategy family digestion.
These are MultiCharts EasyLanguage strategies for TXF (Taiwan Futures Exchange).
"""
from __future__ import annotations

import json
from pathlib import Path

BASE = Path("C:/Users/admin/workspace/digital-immortality/results")
TS = "2026-04-16T16:30"

entries: list[dict] = [
    {
        "path": "E:/投資交易/pla_md/signal/!_TXDD_1_003_TXEX2104.md",
        "strategy_name": "a39130_TX_20210406_DO",
        "family": "TXDD",
        "timeframe": "3-min intraday",
        "direction": "Both (Long+Short)",
        "category": "N-shape breakout day-trade",
        "summary": (
            "TXDD_003 — TX 3-min day-trade (day+night session). N-shape breakout: tracks "
            "bar-count since session open (k), records highestbar/lowestbar of close. At 10:00, "
            "if high came before low (N-shape) -> bullish bias, reverse -> bearish. Entry requires "
            "price above/below 2/3-weighted channel (Highest*2+Lowest)/3 and avgprice confirmation. "
            "Stop-loss = min(100pt, day-range*0.618). Dynamic trailing: once profit > 2*stp, trail "
            "at max(entryH-stp, lowest(L,15min)). Session-end flat. Key patterns: (1) N-shape "
            "morning structure as directional signal; (2) Fibonacci 0.618 stop-loss scaling; "
            "(3) one-entry-per-direction-per-day cap (y/z counters). Indicators: Highest/Lowest of "
            "close, daily OHLC, 3-day average close/range."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/!_TXDD_1_006_TXEX2106.md",
        "strategy_name": "_TXex_DT_6mk_202106",
        "family": "TXDD",
        "timeframe": "6-min intraday",
        "direction": "Both + inversion",
        "category": "Gap + momentum reversal day-trade",
        "summary": (
            "TXDD_006 — TX 6-min day-trade. Two entry modes: (1) Gap entry — OpenD(0) gaps "
            "above/below prev close by ratio(1.5%), enter on stop at dynamic level using IFF "
            "prev-close trend; (2) Deep pullback — OpenD below close-2/3*(close-low)-DATR/2, "
            "mean-reversion entry. Novel: INV 2 flip — if in position >3 bars, place stop-reverse "
            "at entryprice+/-stp (inversion when wrong). Save-exit: once profit>2*stp, trail at "
            "entryprice+2*stp or lowest(h,5)+stp. Max 3 entries/day. Session-end flat. "
            "Indicators: _Datr (N-day average true range function), win_pts (max position profit). "
            "Key insight: combines gap-fade with momentum continuation via the INV flip mechanism."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/!_TXDL_1_060_TXEX2107.md",
        "strategy_name": "a3997",
        "family": "TXDL",
        "timeframe": "60-min intraday",
        "direction": "Both",
        "category": "Volatility breakout (StdDev vs amplitude)",
        "summary": (
            "TXDL_060 — TX 60-min day-only. Entry condition: stddev(C,35) > average(|O-C|,35), "
            "i.e., realized volatility exceeds average bar body size — signals trending regime. "
            "Direction: avgprice vs average of last two closes -> buy at highest(H, stdLen*0.5) stop "
            "or short at lowest(L, stdLen*0.5) stop. Settlement day awareness via LastTradeDay "
            "tag system (tag=1 on settlement, flips to 0 at session end). Exit: setstoploss, "
            "setexitonclose. Profit target: PFT=200 points. Key insight: stddev>amplitude filter "
            "selects trending-regime bars, avoiding choppy sideways markets. Parameters: "
            "stdLen(35), PFT(200)."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/$@LV_lowebar_jump_11K_LT.md",
        "strategy_name": "LV_TX_lowBar_jump_11K_LT",
        "family": "LV (LoveVan)",
        "timeframe": "11K (11-min) intraday",
        "direction": "Both",
        "category": "Open-jump + lowestbar position trade",
        "summary": (
            "LV_lowebar_jump — TX 11-min long-term hold. Uses 3GP (Three-Point Grid): mid = "
            "(H1+L1+2*C1)/4, up = 2*mid-L1, dn = 2*mid-H1. Entry combines open-gap detection "
            "(gap = |C1-O0|) with lowestbar/highestbar position. Walk-forward optimized "
            "(WF:2:18:2, kin parameter). Data: 2014.09-2021.09. Key concept: open-jump magnitude "
            "relative to 3GP levels determines entry, with bar-position (lowestbar) confirming "
            "exhaustion point. Stop via daily range levels. Parameters: len(3) fixed, kin(4) "
            "walk-forward optimized. Author: LoveVan."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/$2106K06_TX_BBand_LO_60K.md",
        "strategy_name": "2106K06_TX_BBand_LO",
        "family": "K06",
        "timeframe": "60K (60-min)",
        "direction": "Long Only (LO)",
        "category": "Bollinger Band + RSI + ATR filter",
        "summary": (
            "BBand_LO_60K — TX 60-min long-only Bollinger strategy. Calculates Bval = "
            "(close-LB)/(HB-LB) — normalized position within Bollinger band (0=lower, 1=upper). "
            "Entry when Bval < BvalLimit(0.8) and RSI conditions met, with ATR filter for "
            "volatility regime. Walk-forward parameters across 7 periods (2015-2021) show stable "
            "BBLen=19, BBDev=1.5-1.7, STPratio=2.2-2.4. Stop-loss = STPratio * ATR. "
            "Key insight: long-only bias exploits upward drift in TAIEX futures; Bval normalization "
            "creates regime-aware entry zones. Parameters: ATRLen(54), BBLen(19), BBDev(1.5), "
            "STPratio(2.4). Commission: 600 NTD round-trip."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/$ShaoWei001_TX_Gap202107_LT03.md",
        "strategy_name": "ShaoWei001_TX_Gap202107_LT03",
        "family": "ShaoWei",
        "timeframe": "15-min (500 bars back)",
        "direction": "Both",
        "category": "Gap + swing level breakout",
        "summary": (
            "ShaoWei001_Gap — TX 15-min long-term hold. Entry: gap-up (Open > (Close1+High1*2)/3) "
            "-> buy at HighD stop; gap-down (Open < (Close1+Low1*2)/3) -> short at LowD stop. "
            "Secondary: prev-close vs 2-day midpoint confirmation. Exit layers: (1) entry-date "
            "end-of-day stop at previous day levels; (2) 'big loss' exit at (HH+entry)/2 — "
            "midpoint between historical extreme and entry; (3) 'wrong position' exit if >50% "
            "of bars since entry show price below entry (barssinceentry persistence test). "
            "Uses Highest(H,len=190) and Lowest(L,len=190) for long-term channel. Key insight: "
            "persistence test — position closed when price spends majority of holding period "
            "on wrong side. Cost: 1000 NTD."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/(10) 策略腳本Shuen036_TX_ASI23K_V3_LT.md",
        "strategy_name": "Shuen036_TX_ASI23K_V1_LT",
        "family": "Shuen",
        "timeframe": "23-min (23K)",
        "direction": "Both + Guava limit entries",
        "category": "Accumulation Swing Index trend-follow",
        "summary": (
            "Shuen036_ASI — TX 23-min ASI (AccumSwingIndex) crossover. Entry: ASI crosses above/"
            "below Average(ASI, Len=105). Secondary 'Guava' entries: limit orders at "
            "0.5*(Open+prevClose)*(1+/-0.07) — mean-reversion fade at 7% deviation from midpoint. "
            "Stop-loss: 2*ATR(13) from entry bar L/H. Multi-day hold with daily gap analysis "
            "(AvgGap array over 20 sessions). Walk-forward: Len stable at 95-110 across 7 periods. "
            "Key insight: ASI captures cumulative swing momentum, slower signal than pure price "
            "crossover. Guava entries add counter-trend layer for reversal capture. "
            "Indicators: AccumSwingIndex, AvgTrueRange(13), 20-session gap/range arrays."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/(10)@@202106TAZ_CDP_4K_D0.md",
        "strategy_name": "202106T90_Normal_CDP_4K_D0",
        "family": "TAZ (T90)",
        "timeframe": "4K (4-min) day-trade",
        "direction": "Both",
        "category": "CDP (Central Dynamic Point) reversal",
        "summary": (
            "TAZ_CDP — TX 4-min CDP day-trade. CDP = (H1+L1+2*C1)/4; derives AH (above-high), "
            "NH (near-high), NL (near-low), AL (above-low) levels. Entry: after gap assessment "
            "(Open vs prev Close), enter at CDP-derived levels with MA(C,len=27) trend filter. "
            "Max 2 entries/day, time window from bar 4*in to 10:00+4*in. Walk-forward: STP stable "
            "at 0.014-0.026, len at 21-27 across 7 periods. Key insight: CDP is a pivot-point "
            "derivative that creates 4 support/resistance zones from a single day's OHLC. "
            "Classical Japanese pivot methodology adapted for TXF intraday. "
            "Parameters: STP(0.02), len(27), in(4). Commission: 600 NTD."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/(10)策略PLA (S)003_TX_Score_2k_DT_20210618.md",
        "strategy_name": "003_TX_Score_2k_DT",
        "family": "Score",
        "timeframe": "2K (2-min) day-trade",
        "direction": "Both",
        "category": "Bar-scoring momentum system",
        "summary": (
            "Score_2k_DT — TX 2-min scoring day-trade. Counts upk (H>H[1]) and downk (L<L[1]) "
            "since session start, score = upk + downk. Entry: score crosses over/under +/-N(9). "
            "Price filter: C must be in upper/lower 1/3 of day range. Exit: when score retreats "
            "to 50% of peak (highest/lowest score). Profit target: max of last 3 days' ranges. "
            "Key insight: pure momentum counting — no indicator lag. Score is an internal "
            "breadth measure of bar-by-bar directional persistence. Walk-forward: N stable at "
            "7-9 across 6 periods. Indicators: none (raw price comparison). "
            "Max 0 entries/day filter, 150 bars back. Commission: max(300, 0.015%)."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/(3) PLA腳本 Ren04_TX_20m_20211230Engulfing_LT.md",
        "strategy_name": "Ren04_TX_20m_Engulfing_LT",
        "family": "Ren",
        "timeframe": "20-min (150K bars back)",
        "direction": "Both",
        "category": "Engulfing pattern swing trade",
        "summary": (
            "Ren04_Engulfing — TX 20-min engulfing candlestick pattern swing trade. No input "
            "parameters (fully rule-based). Bullish engulfing: L[2]>=L[1] AND C>O AND C[1]<O[1] "
            "AND C>O[1] AND O<C[1]; enter at H stop. Bearish mirror image. Multi-day hold. "
            "Exit layers: (1) Reverse-exit if opposing engulfing appears within 3 days and "
            "position underwater; (2) Gap-loss: OpenD jumps beyond prev-day extreme with "
            "confirming bar; (3) No-progress: if HighD[1]<HighD[2] after 4+ days, exit at "
            "LowD[1]; (4) 7% happy exit: trail at _EntryH*0.97 once profit > 7%; (5) 200-point "
            "hard stop. Key insight: no-input strategy relies purely on price structure recognition "
            "with 5-layer exit framework. Commission: min(500, 0.015%)."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/(4 )策略程式碼 D027_6KAM_20201018_MID_TREND_DO.md",
        "strategy_name": "D027_6KAM_MID_TREND_DO",
        "family": "D027",
        "timeframe": "6K (6-min) day-trade",
        "direction": "Both",
        "category": "Midpoint trend day-trade",
        "summary": (
            "D027_MID_TREND — TX 6-min midpoint trend day-trade. Uses AM (morning session) "
            "midpoint as directional reference. Entry requires bar-count filter (in*barinterval "
            "from open) and time window before session end. Walk-forward: 'in' parameter ranges "
            "3-9 across 7 periods (2015-2021). Key concept: midpoint of daily range as "
            "trend-defining level; price above mid = bullish regime, below = bearish. "
            "Day-trade only (DO) with session-end flatten."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/(4 )策略程式碼 TXF_B022_056_50KAM_20201210_BB_BO.md",
        "strategy_name": "TXF_B022_056_50KAM_BB_BO",
        "family": "B022",
        "timeframe": "50K (50-min) AM session",
        "direction": "Both",
        "category": "Bollinger breakout AM session",
        "summary": (
            "B022_BB_BO — TX 50-min Bollinger breakout, AM session only. Likely uses BB upper/"
            "lower band breakout for entry with AM-session (morning-only) constraint. "
            "Walk-forward optimized with 3 parameters across 7 periods. The 50K timeframe "
            "targets medium-term intraday moves. BB_BO = Bollinger Band Break Out. "
            "Key concept: Bollinger band breakout filtered by morning session liquidity."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/(4)  yita 010_TX_20m_3GP_FLT.md",
        "strategy_name": "yita_010_TX_20m_3GP_FLT",
        "family": "yita",
        "timeframe": "20-min",
        "direction": "Both (FLT = flip long-term)",
        "category": "Three-grid-point (3GP) swing",
        "summary": (
            "yita_010_3GP_FLT — TX 20-min Three-Grid-Point swing trade. 3GP derives mid/up/dn "
            "pivot levels from previous day's OHLC. FLT = Flip Long-Term, allowing position "
            "reversal and multi-day holds. Walk-forward optimized across 7 periods (2014-2021). "
            "Key concept: 3GP is a pivot system similar to CDP but with different weighting; "
            "FLT strategies can flip from long to short on signal change, maintaining always-in "
            "market exposure."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/(4) @S_070_TX_Reverser_D.md",
        "strategy_name": "S_070_TX_Reverser_D",
        "family": "S-series",
        "timeframe": "Daily (1D)",
        "direction": "Both + reversal",
        "category": "Multi-bar reversal with shadow analysis",
        "summary": (
            "S_070_Reverser — TX daily reversal strategy. Tracks per-day trade counters "
            "(trades.long, trades.short). Builds 20-element arrays of daily metrics: cl (close-low), "
            "hc (high-close), maxshadow (upper wick), minshadow (lower wick). Averages these "
            "over len(13) periods. Entry based on shadow/body ratios and wick exhaustion signals. "
            "Deadline parameter (17) caps maximum holding bars. Key insight: uses shadow (wick) "
            "analysis as reversal signal — long upper shadows signal selling pressure exhaustion, "
            "long lower shadows signal buying exhaustion. Array-based historical shadow tracking "
            "creates adaptive thresholds."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/(4) @S_110_TX_SnP_L.md",
        "strategy_name": "S_110_TX_SnP_L",
        "family": "S-series",
        "timeframe": "Multi-day (box-breakout)",
        "direction": "Both (despite name)",
        "category": "Box breakout with adaptive lookback",
        "summary": (
            "S_110_SnP — TX box breakout. Adaptive lookback: boxLen doubles (len*2) after a losing "
            "trade (positionprofit(1)<0), preventing re-entry too quickly after loss. Tracks "
            "highestbar/lowestbar of box period. Entry: price breaks box high when lowestbar is "
            "in second half of box (exhaustion of prior low) and LBar rising (l[boxLBar]>l[boxLBarOld]). "
            "Multi-day condition: avoids settlement day and day before/after. Stop: slPnt = "
            "box-range * stlMult(0.9). Walk-forward: len(16-20), stlMult(0.7-1.3). Key insight: "
            "adaptive box length penalizes after losses, reducing trade frequency in adverse regimes. "
            "boxHBar/boxLBar position within box adds structure-quality filter."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/(4) @S_HW2111_TX_1D_VolaRush_L.md",
        "strategy_name": "S_HW2111_TX_1D_VolaRush_L",
        "family": "S-series (HW2111)",
        "timeframe": "1D (daily bars, weekly reference)",
        "direction": "Both",
        "category": "Volatility rush breakout on weekly pivot",
        "summary": (
            "S_HW2111_VolaRush — TX daily volatility rush. Entry: price position relative to "
            "weekly pivot pLine = (highW1+lowW1+2*closeW1)/4. If (2*L+C)/3 > pLine -> bullish bias, "
            "buy at H + stddev(C,len)*mul stop (volatility breakout). If (2*H+C)/3 < pLine -> "
            "bearish, short at L - vola stop. Quick exit: if bias condition invalidated within "
            "len2 bars, exit immediately (momentum failure). Stop: 2*vola from entry. "
            "Settlement day flat. Walk-forward: len(4-6), mul(0.55-0.83), len2(2-5). "
            "Key insight: weekly pivot as regime filter, daily stddev as breakout threshold. "
            "Rapid exit on bias invalidation prevents holding losing positions."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/(4) _004_TX_4K_5D (H-C L-C O-C)-average_DT.md",
        "strategy_name": "_004_TX_4K_5D_HC_LC_OC_average_DT",
        "family": "004",
        "timeframe": "4K (4-min) day-trade",
        "direction": "Both",
        "category": "Multi-day OHLC deviation grid",
        "summary": (
            "004_5D_average — TX 4-min day-trade using 5-day arrays of daily deviations: "
            "H-C, L-C, O-C. Builds maxdis/mindis arrays via _ArrayShift, averages over len(5) days. "
            "Constructs up/dn/mid levels from historical average daily deviations. Entry when "
            "price exceeds these adaptive grid levels. Per-direction entry counters (y/z). "
            "Walk-forward: len(4-5), ratio(0.46-0.50), a2(3-5). Key insight: instead of fixed "
            "point levels, uses rolling average of daily bar statistics (H-C, L-C, O-C) to create "
            "adaptive support/resistance grid that adjusts to recent market character."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/(4) 139_TX7M_C-bar_DO_v1.1_2106-Alan.md",
        "strategy_name": "139_TX7M_C_bar_DO",
        "family": "139 (Alan exchange)",
        "timeframe": "7-min day-trade",
        "direction": "Both",
        "category": "Close-bar (C-bar) momentum",
        "summary": (
            "139_C_bar — TX 7-min C-bar day-trade (2021.06 exchange version by Alan). C_bar = "
            "C - C[1] (close-to-close change). Entry within time window (in*barinterval from "
            "session start to -30min before end). Walk-forward: 'in' ranges 3-9 across 7 periods. "
            "OO/OC capture opening bar O/C for reference. Key concept: C-bar measures per-bar "
            "momentum as raw close difference, simplest possible momentum indicator. "
            "Day-only with session flatten. Uses daily y/z counters for entry limits."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/(4) CB_HW_2111_Bignose_TX_3BarSoilder_FDO_6k_PLE.md",
        "strategy_name": "CB_HW_2111_Bignose_TX_3BarSoilder_FDO_6k",
        "family": "CB_HW (Bignose)",
        "timeframe": "6K (6-min) FDO (flip day-only)",
        "direction": "Both (flip capable)",
        "category": "Three-bar soldier/crow pattern",
        "summary": (
            "CB_3BarSoldier — TX 6-min three-bar-soldier pattern with flip. Uses custom functions: "
            "AmClosed_TX (AM session close), DTrueRange_BN (daily true range). Entry condition: "
            "C vs 2-day AM-close average +/- DTR*ratio. AM/PM bar counters (amk/pmk) for session "
            "awareness. Walk-forward: ratio(0.1-0.4), ratio2(0.1-0.2), ratio3(0.7-1.2) across "
            "7 periods. PLE = Position Limit Enabled. Key insight: three-bar-soldier is a "
            "classic candlestick continuation pattern; this version adds AM-session close "
            "as trend reference and daily true range as volatility-adaptive filter."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/(4) H066_TX_BT_LO_13M_(202107HW).md",
        "strategy_name": "H066_TX_BT_LO_13M",
        "family": "H066 (HW2107)",
        "timeframe": "13-min long-only",
        "direction": "Both (despite LO name)",
        "category": "ATR-filtered channel breakout with loss-adaptive entry",
        "summary": (
            "H066_BT_LO — TX 13-min breakout (BT = breakout). Dual ATR: short ATR(8) and long "
            "ATR(39). Entry at Highest(H,len=39)+value31 / Lowest(L,39)-value32 stop. Loss-adaptive: "
            "value31/value32 initially 0; after 2+ consecutive losses, set to short-ATR (widens "
            "entry threshold). If profitable, reset to 0 (tightens). Caps at PP(100) points. "
            "Secondary entry: after exit with loss, if L touches session low and H > prev close. "
            "Settlement day avoidance. Walk-forward: len(35-43), ATRLen(5-8), PP(100-130). "
            "Key insight: loss-adaptive entry widening — after losses, require larger moves before "
            "re-entry, preventing whipsaw in choppy markets. Self-adjusting difficulty."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/(4) yita 007_TX_10m_open6_LT.md",
        "strategy_name": "yita_007_TX_10m_open6_LT",
        "family": "yita",
        "timeframe": "10-min (15-min variant) long-term",
        "direction": "Both",
        "category": "Opening gap magnitude with AM-session functions",
        "summary": (
            "yita_007_open6 — TX 10-min open-based long-term hold. Uses custom AM-session "
            "functions: AmClosed_TX, AmOpend_TX, AmHighd_TX, AmLowd_TX. Tracks maximum "
            "abs(AmClose-AmOpen) over 'jump' prior sessions as volatility benchmark (maxpt). "
            "Builds distance arrays (dis) for historical true-range tracking. Walk-forward: "
            "sl(160-220), jump(1-8) across 7 periods. Key concept: opening-bar behavior relative "
            "to AM-session historical patterns determines entry, with multi-session volatility "
            "calibration. Data: 2014.08-2021.08."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/(4) yita 008_TX_6m_3GP_DT.md",
        "strategy_name": "yita_008_TX_6m_3GP_DT",
        "family": "yita",
        "timeframe": "6-min day-trade",
        "direction": "Both",
        "category": "Three-grid-point (3GP) day-trade",
        "summary": (
            "yita_008_3GP_DT — TX 6-min 3GP day-trade. 3GP: mid/up/dn from prev day OHLC. "
            "Daily HLD (high-low-distance) tracked in 60-element array, averaged over 10 sessions "
            "(avgdis). Maximum |AmClose-AmOpen| over 3 sessions as volatility reference (maxpt). "
            "Walk-forward: in(13-17), in2(4-8) across 6 periods, remarkably stable. "
            "Key concept: 3GP pivot levels + AM-session volatility calibration for day-trade "
            "entry/exit. Day-only flatten. Data: 2014.09-2021.10. Reference: MoneyDJ forum "
            "thread by yita (posterid=53371)."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/(4) yita 009_TX_50m_3GP_LT.md",
        "strategy_name": "yita_TX_50m_Bollinger_FLT",
        "family": "yita",
        "timeframe": "50-min long-term",
        "direction": "Both (FLT = flip long-term)",
        "category": "Bollinger band position + ORB filter",
        "summary": (
            "yita_009_50m — TX 50-min Bollinger + ORB flip long-term. Calculates Bollinger "
            "position: RL = (C-avg)/(upBB-avg), RS = (C-avg)/(downBB-avg) — normalized position "
            "relative to upper/lower bands. Uses difference between xAverage and BB bands as "
            "squeeze indicator. Filter parameter (25) and ratio (0.19) for entry threshold. "
            "Walk-forward: filter=25 stable, ratio(0.13-0.19) across 8 periods. Key insight: "
            "dual normalization (RL/RS) creates a Bollinger oscillator; combined with BB squeeze "
            "(value3) for regime detection. FLT allows position flipping and multi-day holds."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/(4) @S_070_TX_Reverser_D.md",
        "strategy_name": "S_070_TX_Reverser_D",
        "family": "S-series",
        "timeframe": "Daily",
        "direction": "Both",
        "category": "Daily reversal with shadow arrays",
        "summary": (
            "S_070_Reverser — [Already digested above, same file]. Daily reversal strategy using "
            "20-session arrays of close-low, high-close, and shadow metrics. Len=13 averaging "
            "period. Deadline=17 bars max hold. Shadow-analysis based reversal signals."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/(4)@Ivan2109_TX_MACP19k_LT.md",
        "strategy_name": "Ivan2109_TX_MACP19k_LT",
        "family": "Ivan",
        "timeframe": "19K (19-min) long-term",
        "direction": "Both + counter-trend + protection",
        "category": "MA-Close-Price differential with counter-trend flip",
        "summary": (
            "Ivan_MACP — TX 19-min MA-Close-Price differential long-term. DIF = C - Average("
            "avgprice, Len=45). Entry: DIF-DIF[1] > 0 -> buy at max(Open+stl*0.5, HighD-1) stop. "
            "Counter-trend flip (CT_L/CT_S): if short and H below dn-level and C > (Open+High)/2, "
            "flip long. Protection: bad flip detection — if CT entry's LowD rising while position "
            "losing, exit (PL/PS). 'Run fast' (LRF/SRF): if XAverage on wrong side of 2-day "
            "midpoint after 12:00, cut immediately. 9% profit target. ATR-based trailing stop "
            "scaled by Len/10. Walk-forward: Len(39-51), r(0.75-0.95). Key insight: layered "
            "strategy — main trend + counter-trend flip + flip-protection + urgency exit + "
            "target. 5 exit mechanisms. Commission: 0.015% min 500."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/(4)@R006_TX_Bollien_Backout_FLT.md",
        "strategy_name": "R006_TX_Bollinger_Backout_FLT",
        "family": "R006",
        "timeframe": "60-min all-day (day+night)",
        "direction": "Both",
        "category": "Bollinger backout (mean-reversion re-entry)",
        "summary": (
            "R006_Bollinger_Backout — TX 60-min all-day Bollinger mean-reversion. Entry: L[1] < "
            "lower BB and C[1] < O[1] and C > O (reversal bar after BB touch) -> buy at market. "
            "Mirror for shorts. 'Backout' = re-entry after price exits and re-enters Bollinger "
            "envelope. Exit: if bars > avgn(22) and maxprofit > winPoint/2 and price retreats to "
            "entry+winPoint/2 -> exit (profit protection). Else hard stop at 200 points. "
            "Key insight: mean-reversion signal confirmed by reversal candlestick (bearish bar "
            "followed by bullish bar at BB lower band). Profit-aware exit: only triggers after "
            "minimum profit threshold reached. Parameters: avgn(22), NumDevs(0.6), "
            "backPercent(72)."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/(4)_@LV@_tx_TransFormer_17K_(DT)LT.md",
        "strategy_name": "LV_tx_TransFormer_17K_LT",
        "family": "LV (LoveVan)",
        "timeframe": "17K (17-min) LT with DT support",
        "direction": "Both (Transformer = flip + hybrid)",
        "category": "3GP dual-style Transformer (trend + reversal)",
        "summary": (
            "LV_TransFormer — TX 17-min dual-style 'Transformer' strategy. 3GP: mid=(H1+L1+2*C1)/4, "
            "up=2*mid-L1, dn=2*mid-H1. Also tracks yesterday's 3GP (midy/upy/dny) and gap. "
            "Two trading styles combined: trending (breakout from 3GP levels) + reverse "
            "(mean-reversion to 3GP). Accomplishes 'one mission' via style transformation. "
            "LT with DT support: long-term holds but uses day-trade exits for risk management. "
            "Per-direction entry limits (y/z). Walk-forward: TD(6), WF:3:11:1. "
            "Key insight: 'Transformer' concept — strategy adapts between trend-following and "
            "mean-reversion modes based on price position relative to two days of 3GP levels. "
            "Author: LoveVan. Data: 2014.05-2021.05. Commission: 0.015% ($1000)."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/(4)BN_002_TX_BarTunnel_LO_8k.md",
        "strategy_name": "BN_002_TX_BarTunnel_LO_8k",
        "family": "BN (Bignose)",
        "timeframe": "8K (8-min) long-only",
        "direction": "Long Only",
        "category": "Bar-tunnel (bull/bear bar array channels)",
        "summary": (
            "BN_BarTunnel — TX 8-min bar-tunnel long-only. Separates bars into bullish (C>O) "
            "and bearish (C<O), building separate arrays of their H/L values (ArrayLongL, "
            "ArrayLongH, ArrayShortL, ArrayShortH). Creates a 'tunnel' from NBar(8) recent "
            "bull/bear bar extremes. Entry when price breaks tunnel boundary. HL_ratio(2) and "
            "dayago(1) filter parameters. kperiod(5) for multi-bar confirmation. "
            "Walk-forward: NBar(4-10), HL_ratio(1.5-2.5), dayago(1-5), kperiod(1-5). "
            "Key insight: bar-tunnel separates market microstructure into bull-bar and bear-bar "
            "channels, creating asymmetric support/resistance from bar-type-specific extremes. "
            "Novel concept not found in standard TA."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/(4)BN_003_TX_Sar_FDO_10k.md",
        "strategy_name": "BN_005_TX_SAR_FDT_10k_v2",
        "family": "BN (Bignose)",
        "timeframe": "10K (10-min) FDO (flip day-only)",
        "direction": "Both (flip capable)",
        "category": "Parabolic SAR with tunnel + loss memory",
        "summary": (
            "BN_SAR_FDO — TX 10-min Parabolic SAR with tunnel overlay. SAR with AFStep(0.01-0.03), "
            "trratio(0.1-0.5) for trend-following. Tunnel from prior-bar high/low with "
            "tunnelratio(1.8-2.0). Stop at stp(100-160) points. Tracks profit history: "
            "PFCounter, profitcount, totalprofit, lastentryprice — accumulates P&L memory. "
            "Walk-forward: 7 periods with notable AFStep shift (0.01->0.03 after 2016). "
            "Key insight: SAR provides trend direction, tunnel provides entry levels, and "
            "profit-history tracking enables regime-aware position sizing. FDO = flip + day-only."
        ),
    },
    {
        "path": "E:/投資交易/pla_md/signal/(4)BN_004_TX_Pivot_FLO_10k.md",
        "strategy_name": "BN_006_TX_Swing_v4",
        "family": "BN (Bignose)",
        "timeframe": "10K (10-min) FLO (flip long-only)",
        "direction": "Both (with long bias)",
        "category": "Swing-point pivot breakout with slope filter",
        "summary": (
            "BN_Swing_v4 — TX 10-min swing-point pivot breakout. Identifies swing highs/lows "
            "using SwingHighBar/SwingLowBar with StrengthL=17 (strength = bars on each side). "
            "Stores 5 most recent swing points in arrays (SW_High/Low/HighBar/LowBar). Entry "
            "when price breaks above/below swing points with slope filter: entryslope parameter "
            "and sloperatio(2.2-2.4) for trend quality. Walk-forward: StrengthL(15-17), "
            "sloperatio(2.2-2.4) — remarkably stable. Key insight: multi-swing-point system — "
            "tracks last 5 swing points, not just the most recent, creating layered support/ "
            "resistance with slope-based quality filter. badentrycount tracks consecutive "
            "losing entries for adaptation."
        ),
    },
]

# Remove the duplicate S_070 entry (index 24 is a repeat)
entries = [e for i, e in enumerate(entries) if i != 24]

assert len(entries) == 29, f"expected 29, got {len(entries)}"

for i, e in enumerate(entries):
    e["timestamp"] = f"{TS}:{i:02d}+08:00"
    e["tier"] = 1
    e["readable"] = True
    e["summary_length"] = len(e["summary"])

log_path = BASE / "digestion_log.jsonl"
with log_path.open("a", encoding="utf-8") as f:
    for e in entries:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")
print(f"Appended {len(entries)} entries to {log_path.name}")

state_path = BASE / "digestion_state.json"
with state_path.open("r", encoding="utf-8") as f:
    state = json.load(f)

new_paths = [e["path"] for e in entries]
state["digested_paths"].extend(new_paths)
state["files_digested"] = len(state["digested_paths"])
state["total_digested"] = state.get("total_digested", state["files_digested"])
state["last_digested_at"] = f"{TS}:59+08:00"
state["last_updated"] = f"{TS}:59+08:00"

with state_path.open("w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)
print(f"State updated: files_digested={state['files_digested']}")

set_path = BASE / "digested_set.txt"
if set_path.exists():
    with set_path.open("a", encoding="utf-8") as f:
        for p in new_paths:
            f.write(p + "\n")
    print(f"Appended {len(new_paths)} paths to {set_path.name}")
