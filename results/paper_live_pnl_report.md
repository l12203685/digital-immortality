# Paper-Live SHORT P&L Simulation
> Generated 2026-04-09 UTC | 21 ticks | Entry: $71,509.90

## Setup
- Entry tick 1: BTC=$71,509.90 → SHORT
- Notional: $100 → size=0.001398 BTC
- Signal: dual_ma (close > MA10/MA30 → SHORT in current regime)

## Tick-by-Tick P&L
| Tick | BTC Price | Unrealized P&L |
|------|-----------|----------------|
|  1   | $71,509.90 | +$0.000 |
|  2   | $71,484.80 | +$0.035 |
|  3   | $71,443.20 | +$0.093 |
|  4   | $71,881.30 | $-0.519 |
|  5   | $72,043.10 | $-0.746 |
|  6   | $72,116.10 | $-0.848 |
|  7   | $72,202.70 | $-0.969 |
|  8   | $72,459.40 | $-1.328 |
|  9   | $72,332.10 | $-1.150 |
| 10   | $71,679.00 | $-0.236 |
| 11   | $71,279.46 | +$0.322 |
| 12   | $71,409.55 | +$0.140 |
| 13   | $71,500.76 | +$0.013 |
| 14   | $71,551.96 | $-0.059 |
| 15   | $71,437.38 | +$0.101 |
| 16   | $71,355.00 | +$0.217 |
| 17   | $71,241.11 | +$0.376 |
| 18   | $71,097.79 | +$0.576 |
| 19   | $71,114.18 | +$0.553 |
| 20   | $71,176.00 | +$0.467 |
| 21   | $71,247.59 | +$0.367 |

## Summary
- **Final unrealized P&L: +$0.3668 (+0.37% on $100)**
- Best case (MFE): +$0.5763
- Worst case (MAE): $-1.3278
- Signal consistency: SHORT x 21 ticks (100%)
- MFE/MAE ratio: 0.43x

## Verdict
SHORT signal persistent for 21 consecutive ticks.
Price range: $71,097.79 - $72,459.40
Position currently profitable vs entry.

**Next action**: Set BINANCE_MAINNET_KEY/SECRET → run `python -m trading.mainnet_runner --tick`
See docs/mainnet_activation_guide.md for exact steps.