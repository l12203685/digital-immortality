# Paper Trader Review — 4/14 Go/No-Go
> Generated: 2026-04-08T00:58 UTC

## Decision: CONDITIONAL_GO
6/12 kills in primary regimes. Proceed at 0.5% position size max, daily loss limit 1%.

---

## Kill Conditions
| Condition | Threshold |
|-----------|-----------|
| Min Sharpe (kill) | 0.0 |
| Max MDD (kill) | 20.0% |
| Min Profit Factor | 0.85 |
| Min Win Rate | 35.0% |

---

## Results by Strategy × Regime

### DualMA(fast=10,slow=30)
| Regime | Sharpe | MDD% | Win Rate | PF | Windows Passed | Kill |
|--------|--------|------|----------|----|----------------|------|
| trending | 5.3001 | 4.85 | 59.0% | 2.0325 | 5/5 | no |
| mean_reverting | -4.2912 | 25.59 | 42.6% | 0.5861 | 0/5 | YES |
| mixed | 0.9062 | 8.90 | 51.8% | 1.2437 | 3/5 | no |

### Donchian(period=20)
| Regime | Sharpe | MDD% | Win Rate | PF | Windows Passed | Kill |
|--------|--------|------|----------|----|----------------|------|
| trending | 1.5400 | 1.52 | 49.8% | 1.7932 | 4/5 | no |
| mean_reverting | -3.2894 | 7.35 | 26.7% | 0.2901 | 0/5 | YES |
| mixed | 0.0056 | 1.28 | 28.1% | 1.0887 | 1/5 | YES |

### DonchianConfirmed(period=20)
| Regime | Sharpe | MDD% | Win Rate | PF | Windows Passed | Kill |
|--------|--------|------|----------|----|----------------|------|
| trending | -1.2585 | 1.42 | 26.7% | 0.6929 | 1/5 | YES |
| mean_reverting | -1.9344 | 3.46 | 10.0% | 0.2837 | 0/5 | YES |
| mixed | 0.4130 | 0.24 | 25.0% | 20.3506 | 1/5 | YES |

### DualMA+RegimeFilter
| Regime | Sharpe | MDD% | Win Rate | PF | Windows Passed | Kill |
|--------|--------|------|----------|----|----------------|------|
| trending | 5.3001 | 4.85 | 59.0% | 2.0325 | 5/5 | no |
| mean_reverting | -3.0193 | 9.14 | 31.9% | 0.4464 | 0/5 | YES |
| mixed | 2.3903 | 6.26 | 63.7% | 1.5512 | 3/5 | no |

### Donchian+RegimeFilter
| Regime | Sharpe | MDD% | Win Rate | PF | Windows Passed | Kill |
|--------|--------|------|----------|----|----------------|------|
| trending | 1.5400 | 1.52 | 49.8% | 1.7932 | 4/5 | no |
| mean_reverting | -0.5846 | 0.76 | 30.0% | 0.0213 | 1/5 | YES |
| mixed | 0.2029 | 0.83 | 20.0% | 1.7342 | 1/5 | YES |

### DonchianConfirmed+RegimeFilter
| Regime | Sharpe | MDD% | Win Rate | PF | Windows Passed | Kill |
|--------|--------|------|----------|----|----------------|------|
| trending | -1.2585 | 1.42 | 26.7% | 0.6929 | 1/5 | YES |
| mean_reverting | 0.0000 | 0.00 | 0.0% | inf | 0/5 | YES |
| mixed | 0.4344 | 0.10 | 15.0% | 30.0504 | 1/5 | YES |

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