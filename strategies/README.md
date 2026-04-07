# strategies/ — Strategy Registry

Custom strategies go here. Each strategy must conform to `StrategyFn`:

```python
from typing import List, Dict

Bar = Dict[str, float]  # {"open", "high", "low", "close", "volume"}
Signal = int  # +1 (long), -1 (short), 0 (flat)

def my_strategy(bars: List[Bar]) -> Signal:
    """Return a signal given price history up to the current bar."""
    ...
```

## Built-in strategies (in `trading/backtest_framework.py`)

| Name | Type | Description |
|------|------|-------------|
| `mean_reversion` | Mean reversion | Z-score entry against rolling mean |
| `momentum` | Trend following | Fast/slow SMA crossover |
| `breakout` | Breakout | New high/low over lookback window |
| `volatility_regime` | Adaptive | Switches between MR and momentum by vol ratio |

## Named strategies (in `trading/strategies.py`)

| Class | Type | Description |
|-------|------|-------------|
| `DualMA` | Trend following | Configurable dual moving average crossover |
| `Donchian` | Breakout | Donchian channel breakout with explicit channel |

## Adding a new strategy

1. Create a file here (e.g., `my_strat.py`)
2. Implement the `StrategyFn` interface
3. Register in `trading/backtest_framework.py` STRATEGIES dict or pass directly to `run_backtest()`
4. Validate: `python trading_system.py --backtest --strategy <name>`
5. Kill conditions: define max drawdown and loss thresholds before going live

## Rules

- Every strategy must have a kill condition defined before deployment
- Walk-forward validation required: >= 3/5 windows passing
- No strategy is better than a bad strategy (bias toward inaction)
- Journal every trade decision
