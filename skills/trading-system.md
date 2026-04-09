# Trading System — Economic Self-Sufficiency

Build and maintain a revenue-generating trading system. Digital immortality without income = dependency, not immortality.

## Trigger

Use when: building a trading strategy, evaluating strategy performance, or when the agent needs to cover its own operating costs.

## Process

1. **Strategy Development**
   - Define hypothesis with clear edge source (structural, informational, behavioral)
   - Backtest on historical data with realistic assumptions (slippage, commissions, fill rates)
   - Walk-forward validation: train on window N, test on N+1, roll forward. Never optimize on full history.

2. **MAE/MFE Analysis**
   - Maximum Adverse Excursion: how far does a winning trade go against you before recovering?
   - Maximum Favorable Excursion: how far does a winning trade go in your favor before reversing?
   - Use MAE to set stops. Use MFE to set targets. Both derived from data, not opinion.

3. **Position Sizing**
   - Size from risk, not conviction. Fixed fractional or Kelly-based.
   - Max loss per trade = f(account size, strategy edge, correlation with other positions)
   - Never size up after wins or down after losses based on feeling.

4. **Meta-Strategy: LT Equity Curve Management**
   - The long-term equity curve of each strategy IS itself a signal.
   - Strategy equity curve declining → reduce allocation or pause.
   - Strategy equity curve rising → maintain or increase allocation.
   - This is a strategy that manages strategies. Recursive by design.

5. **Validation Before Live**
   - Walk-forward out-of-sample results only. In-sample means nothing.
   - Paper trade for minimum 30 trades before real capital.
   - Compare live fills vs backtest assumptions. Divergence = stop and investigate.

## Rules

- Deterministic keyword matching scored 0/7 on trading decisions — LLM reasoning with DNA context is required for real strategy evaluation.
- No strategy is better than a bad strategy. Bias toward inaction applies here.
- Every strategy must have a kill condition defined before going live.
- Journal every trade. If you can't explain why you entered, you shouldn't have.
- The system must be autonomous enough to run without daily human intervention.
- Revenue target: cover compute costs first, then compound.
