"""
Trading module — backtesting, paper trading, and live execution for BTC strategies.

Core components:
  - backtest_framework: Walk-forward backtesting engine with DNA filter rules
  - strategies: Named strategies (DualMA, Donchian) for BTC daily
  - paper_trader: Live-simulation on real market data (no capital at risk)
  - live_binance: Binance USDT-M Futures execution layer with safety rails
"""

from trading.backtest_framework import (
    Bar,
    Signal,
    StrategyFn,
    STRATEGIES,
    TIMEFRAMES,
    run_backtest,
    compute_metrics,
    walk_forward,
    strategy_passes_filter,
    generate_synthetic_bars,
)

from trading.strategies import (
    DualMA,
    Donchian,
    dual_ma_btc_daily,
    donchian_btc_daily,
    NAMED_STRATEGIES,
)

from trading.paper_trader import PaperTrader, TradeLog, fetch_klines

from trading.live_binance import (
    BinanceConfig,
    BinanceFuturesClient,
    SafetyRails,
    LiveExecutor,
)

__all__ = [
    # Types
    "Bar", "Signal", "StrategyFn",
    # Backtest
    "STRATEGIES", "TIMEFRAMES",
    "run_backtest", "compute_metrics", "walk_forward",
    "strategy_passes_filter", "generate_synthetic_bars",
    # Strategies
    "DualMA", "Donchian", "dual_ma_btc_daily", "donchian_btc_daily",
    "NAMED_STRATEGIES",
    # Paper trading
    "PaperTrader", "TradeLog", "fetch_klines",
    # Live trading
    "BinanceConfig", "BinanceFuturesClient", "SafetyRails", "LiveExecutor",
]
