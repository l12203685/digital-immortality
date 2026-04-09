# Strategy Comparison Report
Generated: 2026-04-08 (cycle 35)

Walk-forward backtest: 5 windows, train/test 60/40 split, MDD<20% AND Sharpe>1.0 to pass.

| Strategy | Trending | MeanRev | Mixed | Notes |
|---|---|---|---|---|
| DualMA_10_30 | **GO** sh=+5.30 er=7.8 | NO sh=-4.29 er=2.4 | **GO** sh=+0.91 er=3.6 | Portfolio: trending regime |
| Donchian_20 | **GO** sh=+1.54 er=11.2 | NO sh=-3.29 er=3.0 | NO sh=+0.01 er=6.9 | Breakout-only |
| DonchianConfirmed_20 | NO sh=-1.26 er=5.5 | NO sh=-1.93 er=0.7 | NO sh=+0.41 er=8.4 | Fails all regimes — removed from portfolio |
| DualMA_filtered | **GO** sh=+5.30 er=9.8 | NO sh=-3.02 er=1.9 | **GO** sh=+2.39 er=4.3 | Superseded by DualMA_RSI_filtered |
| Donchian_filtered | **GO** sh=+1.54 er=8.8 | NO sh=-0.58 er=1.4 | NO sh=+0.20 er=6.9 | - |
| DonchianConfirmed_filtered | NO sh=-1.26 er=4.4 | NO sh=+0.00 er=0.1 | NO sh=+0.43 er=6.6 | - |
| DualMA_RSI | **GO** sh=+4.05 er=14.0 | NO sh=-5.67 er=4.0 | NO sh=+0.25 er=9.3 | Best edge on trending but lower Sharpe |
| DualMA_RSI_filtered | **GO** sh=+4.05 er=12.6 | NO sh=-2.69 er=1.7 | **GO** sh=+1.74 er=9.9 | Portfolio: mixed regime (er=9.9 best on mixed) |
| BollingerMR_20 | NO sh=+0.00 er=1.1 | NO sh=+0.92 er=4.8 | NO sh=-1.15 er=2.7 | Trend filter too tight |
| BollingerMR_loose | NO sh=+0.37 er=3.4 | **GO** sh=+3.40 er=16.5 | NO sh=-1.20 er=4.0 | Portfolio: mean_reverting regime (only passer, er=16.5) |

## Key Findings
- **BollingerMR_loose**: Only strategy that passes mean-reverting (er=16.5 highest of all)
- **DualMA_RSI_filtered**: Best on mixed regime (er=9.9, GO)
- **DonchianConfirmed**: Fails all 3 regimes — was previously used for mean_reverting (bug)
- **DualMA_10_30**: Strong on trending (sh=+5.30), crashes on mean-reverting (sh=-4.29)

## Portfolio Mapping (post cycle-35)
| Regime | Strategy | Sharpe | EdgeRatio |
|---|---|---|---|
| trending | DualMA_10_30 | +5.30 | 7.8 |
| mean_reverting | BollingerMR_loose | +3.40 | 16.5 |
| mixed | DualMA_RSI_filtered | +1.74 | 9.9 |