# Orthogonality Report

Generated: 2026-04-13T20:35:35.048342+00:00 | Lookback: 999999 ticks | Threshold: 0.7

## Strategies Analyzed

| Strategy | Status | Non-zero signals |
|----------|--------|-----------------|
| BollingerMR_20 | active | 0 |
| BollingerMR_loose | active | 0 |
| DonchianConfirmed_20 | active | 0 |
| DonchianConfirmed_filtered | active | 0 |
| Donchian_20 | disabled | 22 |
| Donchian_filtered | disabled | 22 |
| DualMA_10_30 | active | 731 |
| DualMA_RSI | disabled | 594 |
| DualMA_RSI_filtered | disabled | 53 |
| DualMA_filtered | disabled | 53 |
| gen_BollingerMeanReversion_RF_598b24 | disabled | 23 |
| gen_BollingerMeanReversion_RF_7abfe4 | disabled | 23 |
| gen_BollingerMeanReversion_f91248 | active | 0 |
| gen_DonchianConfirmed_RSI_9b2bf4 | active | 0 |
| gen_DonchianConfirmed_a7186a | active | 0 |
| gen_Donchian_RF_5e649e | active | 0 |
| gen_Donchian_RSI_d3d59e | active | 0 |
| gen_DualMA_RF_602541 | active | 0 |
| gen_DualMA_RF_eda1cb | active | 0 |

## Top Correlated Pairs

| Rank | Strategy A | Strategy B | Correlation | Flag |
|------|-----------|-----------|-------------|------|
| 1 | Donchian_20 | Donchian_filtered | +1.0000 | NON-ORTHOGONAL |
| 2 | gen_BollingerMeanReversion_RF_598b24 | gen_BollingerMeanReversion_RF_7abfe4 | +1.0000 | NON-ORTHOGONAL |
| 3 | DualMA_RSI_filtered | DualMA_filtered | +1.0000 | NON-ORTHOGONAL |
| 4 | DualMA_RSI_filtered | gen_BollingerMeanReversion_RF_598b24 | -0.6562 |  |
| 5 | DualMA_RSI_filtered | gen_BollingerMeanReversion_RF_7abfe4 | -0.6562 |  |
| 6 | DualMA_filtered | gen_BollingerMeanReversion_RF_598b24 | -0.6562 |  |
| 7 | DualMA_filtered | gen_BollingerMeanReversion_RF_7abfe4 | -0.6562 |  |
| 8 | DualMA_10_30 | DualMA_RSI | +0.4497 |  |
| 9 | DualMA_RSI | DualMA_RSI_filtered | +0.2766 |  |
| 10 | DualMA_RSI | DualMA_filtered | +0.2766 |  |
| 11 | DualMA_10_30 | DualMA_RSI_filtered | +0.2441 |  |
| 12 | DualMA_10_30 | DualMA_filtered | +0.2441 |  |
| 13 | DualMA_RSI | gen_BollingerMeanReversion_RF_598b24 | -0.1815 |  |
| 14 | DualMA_RSI | gen_BollingerMeanReversion_RF_7abfe4 | -0.1815 |  |
| 15 | Donchian_20 | DualMA_RSI | +0.1775 |  |
| 16 | Donchian_filtered | DualMA_RSI | +0.1775 |  |
| 17 | DualMA_10_30 | gen_BollingerMeanReversion_RF_598b24 | -0.1602 |  |
| 18 | DualMA_10_30 | gen_BollingerMeanReversion_RF_7abfe4 | -0.1602 |  |
| 19 | Donchian_20 | DualMA_10_30 | -0.0367 |  |
| 20 | Donchian_filtered | DualMA_10_30 | -0.0367 |  |

## Risk Concentration

- **Flagged pairs**: 3/171 (1.8%)
- **Strategies in flagged pairs**: 6/19 (31.6%)
- **Risk level**: MEDIUM

## Recommendations

- **Donchian_20** <-> **Donchian_filtered** (corr=+1.000): Consider disabling **Donchian_20** (fewer active signals) or diversifying its logic.
- **gen_BollingerMeanReversion_RF_598b24** <-> **gen_BollingerMeanReversion_RF_7abfe4** (corr=+1.000): Consider disabling **gen_BollingerMeanReversion_RF_598b24** (fewer active signals) or diversifying its logic.
- **DualMA_RSI_filtered** <-> **DualMA_filtered** (corr=+1.000): Consider disabling **DualMA_RSI_filtered** (fewer active signals) or diversifying its logic.
