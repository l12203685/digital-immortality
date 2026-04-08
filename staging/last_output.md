# Cycle 20 — Output

## What was done

- **CRITICAL FIX — dna_core.md learn=write gap**: Cycles 16-19 claimed "15 micro-decisions in dna_core.md" but never wrote to the file. Fixed: added `## Micro-Decisions (12 calibrated patterns)` section with MD-01 through MD-12. File is now 88 lines. The pattern names are: 多方案並列, 自推到底再確認, 不動作是最難, AI=語言外包, 帳戶×券商分層, 不確定→清倉等訊號, 清單式確認, 資金閉鎖期認知, 賣出有掛單紀律, 先做後說, 截止前確認, 系統性歸檔.

- **testnet_runner.py --portfolio-gated**: Added portfolio regime-gated tick mode. `--portfolio-gated` flag gates which strategy runs per tick based on `PortfolioSelector` regime detection. Non-matching strategies log `SKIPPED_REGIME`. Adds `regime` + `regime_selected_strategy` fields to live tick entries. This was Cycle 8's #1 deferred priority — now done.

- **daily_log.md restored**: Cycles 9-19 were missing from the log. Written a compact summary covering: testnet GO review, mainnet_runner.py build, paper-live ticks, and JSONL micro-decision extraction cycles.

- **dynamic_tree.md updated**: Corrected 2.2 branch status to reflect actual file state. Added cycle 20 evolution record.

## Repo state

- dna_core.md: 88 lines — 71 core + 12 micro-decisions (MD-01~MD-12) ✓
- testnet_runner.py: `--portfolio-gated` flag live ✓
- Trading path: paper_review GO → testnet GO → mainnet built → paper-live active (SHORT ×3) → mainnet awaits credentials
- Boot test: 8/8 aligned (maintained)
- Daily log: cycle 20 — restored continuity after 12-cycle gap
- Memory: 20+ distilled entries
- Branch 2.2: 12 micro-decisions extracted and PERSISTED (202601-202604 done); 202512+ next

## Key insight from this cycle

遞迴 + persist = 演化. Cycles 16-19 were 遞迴 - persist = 自言自語. The recursive loop must write to durable storage — not just claim it did. Lesson: every "distilled X patterns" step must include an explicit file edit as verification.

## Next cycle priorities (ranked by derivative)

1. **Add**: Makefile targets `make portfolio-tick` and `make dashboard`
2. **Improve**: Read 202512 JSONL → extract 3 micro-decisions → MD-13~MD-15
3. **Add**: Portfolio-gated mode to mainnet_runner.py `--paper-live` (mirrors testnet fix)
4. **Improve**: Cross-instance test — boot from dna_core.md micro-decisions, verify decision consistency
5. **Fix**: Investigate why staging/last_output.md wasn't updated during cycles 9-19 (daemon loop issue?)
