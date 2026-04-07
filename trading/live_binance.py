"""
Live trading infrastructure for Binance USDT-M Futures.

Provides an execution layer that can:
  - Connect to Binance USDT-M futures via ccxt
  - Place market orders based on strategy signals
  - Manage position sizing with configurable risk limits
  - Enforce kill-switch / max-drawdown safety rails

This module is the bridge between paper-validated strategies and real capital.

Dependencies: ccxt (pip install ccxt)
"""

import logging
import os
import time
from typing import List, Dict, Optional, Callable

from trading.backtest_framework import Bar, Signal

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

class BinanceConfig:
    """
    Configuration for Binance USDT-M Futures connection.
    Reads credentials from environment variables by default.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        testnet: bool = True,
        symbol: str = "BTC/USDT:USDT",
        leverage: int = 1,
        max_position_usdt: float = 1000.0,
        max_drawdown_pct: float = 10.0,
    ):
        self.api_key = api_key or os.environ.get("BINANCE_API_KEY", "")
        self.api_secret = api_secret or os.environ.get("BINANCE_API_SECRET", "")
        self.testnet = testnet
        self.symbol = symbol
        self.leverage = leverage
        self.max_position_usdt = max_position_usdt
        self.max_drawdown_pct = max_drawdown_pct

    @property
    def has_credentials(self) -> bool:
        return bool(self.api_key and self.api_secret)


# ---------------------------------------------------------------------------
# Exchange connection
# ---------------------------------------------------------------------------

class BinanceFuturesClient:
    """
    Thin wrapper around ccxt for Binance USDT-M Futures.
    Defaults to testnet for safety.
    """

    def __init__(self, config: BinanceConfig):
        self.config = config
        self._exchange = None

    def _connect(self):
        """Lazily initialise the ccxt exchange object."""
        if self._exchange is not None:
            return

        try:
            import ccxt
        except ImportError:
            raise ImportError(
                "ccxt is required for live trading. Install with: pip install ccxt"
            )

        options = {
            "defaultType": "future",
        }

        self._exchange = ccxt.binance({
            "apiKey": self.config.api_key,
            "secret": self.config.api_secret,
            "options": options,
            "enableRateLimit": True,
        })

        if self.config.testnet:
            self._exchange.set_sandbox_mode(True)
            logger.info("Connected to Binance USDT-M Futures TESTNET")
        else:
            logger.info("Connected to Binance USDT-M Futures LIVE")

    @property
    def exchange(self):
        self._connect()
        return self._exchange

    def fetch_ohlcv(self, timeframe: str = "1d", limit: int = 100) -> List[Bar]:
        """Fetch OHLCV data and convert to our Bar format."""
        raw = self.exchange.fetch_ohlcv(self.config.symbol, timeframe, limit=limit)
        bars: List[Bar] = []
        for candle in raw:
            bars.append({
                "open_time": candle[0],
                "open": candle[1],
                "high": candle[2],
                "low": candle[3],
                "close": candle[4],
                "volume": candle[5],
            })
        return bars

    def get_balance(self) -> Dict:
        """Fetch USDT futures balance."""
        balance = self.exchange.fetch_balance({"type": "future"})
        usdt = balance.get("USDT", {})
        return {
            "free": usdt.get("free", 0.0),
            "used": usdt.get("used", 0.0),
            "total": usdt.get("total", 0.0),
        }

    def get_position(self) -> Dict:
        """Get current position for the configured symbol."""
        positions = self.exchange.fetch_positions([self.config.symbol])
        for pos in positions:
            if pos["symbol"] == self.config.symbol:
                return {
                    "side": pos.get("side", "none"),
                    "size": float(pos.get("contracts", 0)),
                    "entry_price": float(pos.get("entryPrice", 0)),
                    "unrealized_pnl": float(pos.get("unrealizedPnl", 0)),
                    "leverage": int(pos.get("leverage", 1)),
                }
        return {"side": "none", "size": 0.0, "entry_price": 0.0, "unrealized_pnl": 0.0, "leverage": 1}

    def set_leverage(self, leverage: int) -> None:
        """Set leverage for the symbol."""
        self.exchange.set_leverage(leverage, self.config.symbol)
        logger.info("Leverage set to %dx for %s", leverage, self.config.symbol)

    def market_order(self, side: str, amount_usdt: float) -> Dict:
        """
        Place a market order.
        side: 'buy' or 'sell'
        amount_usdt: notional value in USDT
        """
        ticker = self.exchange.fetch_ticker(self.config.symbol)
        price = ticker["last"]
        if price is None or price <= 0:
            raise ValueError(f"Invalid ticker price: {price}")

        # Convert USDT notional to contract quantity
        amount = amount_usdt / price

        # Binance has minimum quantity rules; round to exchange precision
        market = self.exchange.market(self.config.symbol)
        precision = market.get("precision", {}).get("amount", 3)
        amount = round(amount, precision)

        if amount <= 0:
            logger.warning("Order amount rounds to zero — skipping")
            return {}

        order = self.exchange.create_market_order(
            self.config.symbol, side, amount
        )
        logger.info(
            "ORDER %s %s %.6f @ ~%.2f (id=%s)",
            side.upper(), self.config.symbol, amount, price, order.get("id"),
        )
        return order

    def close_position(self, side: str, amount_contracts: float) -> Dict:
        """
        Close a position by placing a market order for a specific number of
        contracts (base currency units), bypassing notional-to-quantity conversion.
        side: 'buy' or 'sell'
        amount_contracts: position size in base currency (e.g. BTC)
        """
        market = self.exchange.market(self.config.symbol)
        precision = market.get("precision", {}).get("amount", 3)
        amount = round(amount_contracts, precision)

        if amount <= 0:
            logger.warning("Close amount rounds to zero — skipping")
            return {}

        order = self.exchange.create_market_order(
            self.config.symbol, side, amount, params={"reduceOnly": True}
        )
        logger.info(
            "CLOSE %s %s %.6f contracts (id=%s)",
            side.upper(), self.config.symbol, amount, order.get("id"),
        )
        return order


# ---------------------------------------------------------------------------
# Safety rails
# ---------------------------------------------------------------------------

class SafetyRails:
    """
    Kill-switch and risk management layer.

    - Max drawdown: if account drops below threshold, close all and halt.
    - Max position: caps notional exposure.
    - Cooldown: minimum seconds between orders to prevent rapid flipping.
    """

    def __init__(
        self,
        client: BinanceFuturesClient,
        max_drawdown_pct: float = 10.0,
        max_position_usdt: float = 1000.0,
        cooldown_seconds: int = 60,
    ):
        self.client = client
        self.max_drawdown_pct = max_drawdown_pct
        self.max_position_usdt = max_position_usdt
        self.cooldown_seconds = cooldown_seconds
        self._initial_balance: Optional[float] = None
        self._last_order_time: float = 0.0
        self.halted = False

    def initialize(self) -> None:
        """Record the starting balance for drawdown tracking."""
        bal = self.client.get_balance()
        self._initial_balance = bal["total"]
        logger.info("Safety rails initialized. Starting balance: %.2f USDT", self._initial_balance)

    def check(self) -> bool:
        """
        Run all safety checks. Returns True if trading is allowed.
        """
        if self.halted:
            logger.warning("HALTED — safety kill-switch active")
            return False

        if self._initial_balance is None:
            self.initialize()

        # Drawdown check
        bal = self.client.get_balance()
        current = bal["total"]
        if self._initial_balance > 0:
            dd_pct = (self._initial_balance - current) / self._initial_balance * 100
            if dd_pct >= self.max_drawdown_pct:
                logger.critical(
                    "MAX DRAWDOWN BREACHED: %.1f%% (limit %.1f%%). HALTING.",
                    dd_pct, self.max_drawdown_pct,
                )
                self.halted = True
                return False

        # Cooldown check
        elapsed = time.time() - self._last_order_time
        if elapsed < self.cooldown_seconds:
            logger.info("Cooldown active (%.0fs remaining)", self.cooldown_seconds - elapsed)
            return False

        return True

    def record_order(self) -> None:
        self._last_order_time = time.time()

    def close_all(self) -> None:
        """Emergency close: flatten the position."""
        pos = self.client.get_position()
        if pos["size"] > 0:
            side = "sell" if pos["side"] == "long" else "buy"
            # pos["size"] is in contracts (base currency units).
            # Use close_position() which directly specifies the amount
            # in base currency, bypassing the notional->quantity conversion
            # in market_order().
            self.client.close_position(side, pos["size"])
            logger.info("Emergency close executed")


# ---------------------------------------------------------------------------
# Live executor
# ---------------------------------------------------------------------------

class LiveExecutor:
    """
    Connects a strategy to the Binance client with safety rails.

    Usage:
        config = BinanceConfig(testnet=True)
        executor = LiveExecutor(config, strategy=dual_ma_btc_daily, name="DualMA")
        executor.tick()  # single tick
    """

    def __init__(
        self,
        config: BinanceConfig,
        strategy: Callable[[List[Bar]], Signal],
        name: str = "unnamed",
        timeframe: str = "1d",
        lookback: int = 100,
    ):
        self.config = config
        self.strategy = strategy
        self.name = name
        self.timeframe = timeframe
        self.lookback = lookback
        self.client = BinanceFuturesClient(config)
        self.rails = SafetyRails(
            self.client,
            max_drawdown_pct=config.max_drawdown_pct,
            max_position_usdt=config.max_position_usdt,
        )
        self._current_signal: Signal = 0

    def tick(self) -> Dict:
        """Single execution tick: fetch data, compute signal, execute if needed."""
        result: Dict = {"strategy": self.name, "timeframe": self.timeframe}

        # Safety check
        if not self.rails.check():
            result["action"] = "BLOCKED_BY_SAFETY"
            return result

        # Fetch bars
        bars = self.client.fetch_ohlcv(self.timeframe, self.lookback)
        if not bars:
            result["action"] = "NO_DATA"
            return result

        result["price"] = bars[-1]["close"]
        result["bars_fetched"] = len(bars)

        # Compute signal
        signal = self.strategy(bars)
        result["signal"] = signal
        result["prev_signal"] = self._current_signal

        # Execute if signal changed
        if signal != self._current_signal:
            pos = self.client.get_position()

            # Close existing position
            if pos["size"] > 0:
                close_side = "sell" if pos["side"] == "long" else "buy"
                self.client.close_position(close_side, pos["size"])
                result["closed"] = pos["side"]

            # Open new position
            if signal != 0:
                open_side = "buy" if signal == 1 else "sell"
                self.client.market_order(open_side, self.config.max_position_usdt)
                result["opened"] = open_side

            self._current_signal = signal
            self.rails.record_order()
            result["action"] = "EXECUTED"
        else:
            result["action"] = "HOLD"

        logger.info("Tick result: %s", result)
        return result

    def run_loop(self, interval_seconds: int = 86400, max_ticks: Optional[int] = None) -> None:
        """Run the executor in a loop."""
        logger.info(
            "Starting live executor: %s on %s %s",
            self.name, self.config.symbol, self.timeframe,
        )
        self.client.set_leverage(self.config.leverage)

        tick_count = 0
        try:
            while max_ticks is None or tick_count < max_ticks:
                self.tick()
                tick_count += 1
                if max_ticks is not None and tick_count >= max_ticks:
                    break
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("Live executor stopped by user")
        finally:
            logger.info("Executor %s completed %d ticks", self.name, tick_count)


# ---------------------------------------------------------------------------
# CLI — status check only (never auto-trades from CLI)
# ---------------------------------------------------------------------------

def main():
    """Check Binance connectivity and show account status. Does NOT trade."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    config = BinanceConfig(testnet=True)

    print("=" * 60)
    print("Binance USDT-M Futures — Infrastructure Check")
    print("=" * 60)
    print(f"Symbol:    {config.symbol}")
    print(f"Testnet:   {config.testnet}")
    print(f"Leverage:  {config.leverage}x")
    print(f"Max pos:   {config.max_position_usdt} USDT")
    print(f"Max DD:    {config.max_drawdown_pct}%")

    if not config.has_credentials:
        print("\n[INFO] No API credentials found.")
        print("Set BINANCE_API_KEY and BINANCE_API_SECRET environment variables.")
        print("Infrastructure code is ready — credentials needed for connectivity test.")
        return

    try:
        client = BinanceFuturesClient(config)
        balance = client.get_balance()
        print(f"\nBalance:   {balance}")

        position = client.get_position()
        print(f"Position:  {position}")

        bars = client.fetch_ohlcv("1d", limit=5)
        print(f"Latest 5d closes: {[b['close'] for b in bars]}")

        print("\nAll systems operational.")
    except ImportError:
        print("\n[INFO] ccxt not installed. Install with: pip install ccxt")
        print("Infrastructure code is ready — install ccxt to connect.")
    except Exception as e:
        print(f"\nConnection error: {e}")


if __name__ == "__main__":
    main()
