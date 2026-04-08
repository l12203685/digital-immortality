# Paper-Live SHORT P&L Simulation
> Updated 2026-04-09 UTC | 33 ticks | Entry: $71,509.90

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
| 22   | $71,225.83 | +$0.397 |
| 23   | $71,190.69 | +$0.446 |
| 24   | $71,186.58 | +$0.452 |
| 25   | $71,300.00 | +$0.293 |
| 26   | $71,238.01 | +$0.380 |
| 27   | $71,332.14 | +$0.249 |
| 28   | $71,359.94 | +$0.210 |
| 29   | $70,966.00 | +$0.760 |
| 30   | $71,007.77 | +$0.702 |
| 31   | $70,961.36 | +$0.767 |
| 32   | $71,114.01 | +$0.554 |
| 33   | $71,083.18 | +$0.596 |

## Summary
- **Current unrealized P&L: +$0.5957 (+0.60% on $100)**
- Best case (MFE): +$0.7669 (tick 31, BTC=$70,961)
- Worst case (MAE): $-1.3274
- Signal consistency: SHORT x 33 ticks (100%)
- MFE/MAE ratio: 0.58x

## Verdict
SHORT signal persistent for 33 consecutive ticks. BTC recovered from tick 32 ($71,114) to $71,083 — slight improvement. Signal still profitable. MFE remains tick 31.

**Next action**: Set BINANCE_MAINNET_KEY/SECRET → run `python -m trading.mainnet_runner --tick`
See docs/mainnet_activation_guide.md for exact steps.