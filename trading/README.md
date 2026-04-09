# trading/

Backtesting framework for the self-sustainability phase (SKILL.md Section 5).

Implements: 4 strategy interfaces x 3 timeframes with walk-forward validation.

**Filter rules** (from DNA): walk-forward >= 3/5 windows, Sharpe > 1.0, MDD < 20%.

Run: `python trading/backtest_framework.py`

No external dependencies required (numpy optional for faster math).
