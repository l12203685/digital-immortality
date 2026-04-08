# Recursive Cycle 47 — 2026-04-08T18:00Z

## What was done

### Branch 2.2: DNA distillation — 9 MDs written (backfill + new)
- Backfilled MD-193~MD-198 to dna_core.md (these were marked ✓ in tree but missing from file — persistence failure fixed)
- Added MD-199~MD-201 for 202002 (Feb 2020 COVID panic onset)
- dna_core.md: 192 → 201 MDs, 273 → 282 lines

### Branch 1.2: Trading MAE/MFE integration
- `testnet_runner.py`: `compute_mae_mfe` imported; `cmd_backtest` now shows per-strategy edge_ratio diagnostic after main results table
- `backtest_framework.py`: `_EXTRA_STRATEGIES` block added (DonchianConfirmed + DualMA_RSI + DualMA_RSI_filtered); all 7 strategies now appear in MAE/MFE demo

## What changed
- `templates/dna_core.md`: +9 rows (MD-193~MD-201)
- `trading/testnet_runner.py`: compute_mae_mfe import + diagnostic block in cmd_backtest
- `trading/backtest_framework.py`: _EXTRA_STRATEGIES import + extended MAE/MFE demo
- `results/dynamic_tree.md`: cycle 47 update, MD count 195→201, 202002 marked ✓
- `results/daily_log.md`: cycle 47 appended

## Next cycle should focus on
1. **202001 JSONL** → MD-202~MD-204 (January 2020 — pre-COVID, BTC ~$8-9k)
2. **testnet_runner RSI strategies** — add `dual_ma_rsi_btc_daily` and `dual_ma_rsi_filtered` to STRATEGIES dict so they get tracked in testnet log
3. Consider: `--review` output could show edge_ratio from saved backtest_results.json without needing live bar fetch
