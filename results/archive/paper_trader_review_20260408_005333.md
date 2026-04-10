# Paper Trader Review — 4/14 Go/No-Go
> Generated: 2026-04-08T00:53 UTC

## Decision: NO_GO
5/6 kill conditions triggered (83%). Extend paper trading 14 more days, re-review before live.

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

---

## Interpretation
- **Trending regime**: where DualMA/Donchian should shine
- **Mean-reverting regime**: expected underperformance for trend-following
- **Mixed regime**: real-world proxy — must not catastrophically lose

## Next Steps
- GO: → Testnet (Binance testnet USDT-M, same size as paper)
- CONDITIONAL_GO: → Testnet with position size floor (0.5% capital)
- NO_GO: → Extend paper trading 14 days, recalibrate strategy parameters