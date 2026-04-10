# Paper Trader Review — 4/14 Go/No-Go
> Generated: 2026-04-08T00:55 UTC

## Decision: NO_GO
5/8 kills in primary regimes (62%). Extend paper trading 14 more days, recalibrate parameters.

---

## Kill Conditions
| Condition | Threshold |
|-----------|-----------|
| Min Sharpe (kill) | 0.5 |
| Max MDD (kill) | 20.0% |
| Min Profit Factor | 1.0 |
| Min Win Rate | 40.0% |

---

## Results by Strategy × Regime

### DualMA(fast=10,slow=30)
| Regime | Sharpe | MDD% | Win Rate | PF | Windows Passed | Kill |
|--------|--------|------|----------|----|----------------|------|
| trending | 1.7057 | 8.43 | 51.5% | 1.3353 | 4/5 | no |
| mean_reverting | -2.7556 | 23.75 | 43.4% | 0.7108 | 0/5 | YES |
| mixed | -0.0905 | 9.61 | 47.7% | 1.1515 | 1/5 | YES |

### Donchian(period=20)
| Regime | Sharpe | MDD% | Win Rate | PF | Windows Passed | Kill |
|--------|--------|------|----------|----|----------------|------|
| trending | -0.4846 | 2.07 | 40.5% | 0.9381 | 1/5 | YES |
| mean_reverting | -2.6858 | 7.53 | 30.7% | 0.3747 | 0/5 | YES |
| mixed | -1.8740 | 3.74 | 23.6% | 0.6439 | 1/5 | YES |

### DualMA+RegimeFilter
| Regime | Sharpe | MDD% | Win Rate | PF | Windows Passed | Kill |
|--------|--------|------|----------|----|----------------|------|
| trending | 2.1296 | 6.69 | 52.4% | 1.3695 | 4/5 | no |
| mean_reverting | -4.1455 | 14.99 | 32.6% | 0.3510 | 0/5 | YES |
| mixed | 0.3358 | 4.53 | 44.8% | 1.1117 | 1/5 | YES |

### Donchian+RegimeFilter
| Regime | Sharpe | MDD% | Win Rate | PF | Windows Passed | Kill |
|--------|--------|------|----------|----|----------------|------|
| trending | 0.9070 | 0.91 | 50.5% | 1.4133 | 2/5 | no |
| mean_reverting | -1.5491 | 2.46 | 18.0% | 0.1752 | 0/5 | YES |
| mixed | -0.7247 | 1.11 | 18.6% | 0.8407 | 1/5 | YES |

---

## Interpretation
- **Trending regime** (primary for trend-following): must pass
- **Mean-reverting regime** (non-primary for DualMA/Donchian): expected failure, not counted
- **Mixed regime** (primary): real-world proxy — must not catastrophically lose
- Kill conditions are only checked against each strategy's primary regimes

## Next Steps
- GO: → Testnet (Binance testnet USDT-M, same size as paper)
- CONDITIONAL_GO: → Testnet with position size floor (0.5% capital)
- NO_GO: → Extend paper trading 14 days, recalibrate strategy parameters