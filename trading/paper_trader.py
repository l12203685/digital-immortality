"""
Paper-trading engine for live-simulation of strategies on real market data.

Fetches BTC/USDT candles from a public REST API (Binance), feeds them to a
StrategyFn, tracks positions / PnL, and logs every decision.

Designed to run as a long-lived process or be ticked manually in tests.

Dependencies: only `requests` (stdlib-fallback: urllib).
"""

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional, Callable

from trading.backtest_framework import Bar, Signal, compute_metrics

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Market data fetcher (Binance public API, no auth needed)
# ---------------------------------------------------------------------------

def _fetch_klines_requests(symbol: str, interval: str, limit: int) -> List[Bar]:
    """Fetch klines via the `requests` library."""
    import requests

    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return _parse_klines(resp.json())


def _fetch_klines_urllib(symbol: str, interval: str, limit: int) -> List[Bar]:
    """Fallback: fetch klines via stdlib urllib."""
    from urllib.request import urlopen, Request
    from urllib.parse import urlencode

    base = "https://api.binance.com/api/v3/klines"
    qs = urlencode({"symbol": symbol, "interval": interval, "limit": str(limit)})
    req = Request(f"{base}?{qs}", headers={"User-Agent": "paper-trader/0.1"})
    with urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
    return _parse_klines(data)


def _parse_klines(raw: list) -> List[Bar]:
    """Convert Binance kline arrays to Bar dicts."""
    bars: List[Bar] = []
    for k in raw:
        bars.append({
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5]),
            "open_time": int(k[0]),
            "close_time": int(k[6]),
        })
    return bars


def fetch_klines(symbol: str = "BTCUSDT", interval: str = "1d", limit: int = 100) -> List[Bar]:
    """Fetch klines, trying `requests` first, then falling back to urllib."""
    try:
        return _fetch_klines_requests(symbol, interval, limit)
    except ImportError:
        return _fetch_klines_urllib(symbol, interval, limit)


# ---------------------------------------------------------------------------
# Trade log
# ---------------------------------------------------------------------------

class TradeLog:
    """Append-only trade journal persisted to a JSON-lines file."""

    def __init__(self, path: Optional[str] = None):
        self.path = Path(path) if path else None
        self.entries: List[Dict] = []

    def record(self, entry: Dict) -> None:
        entry["timestamp"] = datetime.now(timezone.utc).isoformat()
        self.entries.append(entry)
        logger.info("TRADE: %s", json.dumps(entry))
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "a") as f:
                f.write(json.dumps(entry) + "\n")

    def summary(self) -> Dict:
        """Return quick summary stats from logged PnL entries."""
        pnl_list = [e.get("pnl", 0.0) for e in self.entries if "pnl" in e]
        return compute_metrics(pnl_list) if pnl_list else {}


# ---------------------------------------------------------------------------
# Paper Trader
# ---------------------------------------------------------------------------

class PaperTrader:
    """
    Simulates trading on live data without risking real capital.

    Usage:
        from trading.strategies import dual_ma_btc_daily
        pt = PaperTrader(strategy=dual_ma_btc_daily, name="DualMA")
        pt.run_once()          # fetch latest bars, generate signal, log
        pt.run_loop(interval=86400)  # run every 24h (for daily)
    """

    def __init__(
        self,
        strategy: Callable[[List[Bar]], Signal],
        name: str = "unnamed",
        symbol: str = "BTCUSDT",
        interval: str = "1d",
        lookback: int = 100,
        initial_capital: float = 10_000.0,
        log_path: Optional[str] = None,
    ):
        self.strategy = strategy
        self.name = name
        self.symbol = symbol
        self.interval = interval
        self.lookback = lookback
        self.capital = initial_capital
        self.position: Signal = 0
        self.entry_price: float = 0.0
        self.trade_log = TradeLog(log_path)
        self._bars: List[Bar] = []
        self._prev_price: float = 0.0

    def _update_bars(self) -> None:
        """Fetch fresh bars from the exchange."""
        self._bars = fetch_klines(self.symbol, self.interval, self.lookback)
        logger.debug("Fetched %d bars for %s %s", len(self._bars), self.symbol, self.interval)

    def run_once(self) -> Dict:
        """
        Single tick: fetch data, compute signal, update position, log.
        Returns the trade-log entry for this tick.
        """
        self._update_bars()
        if not self._bars:
            logger.warning("No bars fetched — skipping tick")
            return {}

        signal = self.strategy(self._bars)
        current_price = self._bars[-1]["close"]
        entry: Dict = {
            "strategy": self.name,
            "symbol": self.symbol,
            "interval": self.interval,
            "price": current_price,
            "signal": signal,
            "prev_position": self.position,
        }

        # Calculate per-bar PnL if we had a position
        # Use _prev_price (last tick's price) to get the single-bar return,
        # avoiding double-counting when holding across multiple ticks.
        if self.position != 0 and self._prev_price > 0:
            bar_return = (current_price - self._prev_price) / self._prev_price
            pnl_pct = self.position * bar_return
            entry["pnl"] = round(pnl_pct * 100, 4)
            self.capital *= (1 + pnl_pct)
            entry["capital"] = round(self.capital, 2)

        # Update position
        if signal != self.position:
            entry["action"] = (
                "OPEN_LONG" if signal == 1 else
                "OPEN_SHORT" if signal == -1 else
                "CLOSE"
            )
            self.position = signal
            self.entry_price = current_price if signal != 0 else 0.0
        else:
            entry["action"] = "HOLD"

        self.trade_log.record(entry)
        self._prev_price = current_price
        return entry

    def run_loop(self, interval_seconds: int = 86400, max_ticks: Optional[int] = None) -> None:
        """
        Run the paper trader in a loop, ticking every `interval_seconds`.
        For daily candles, 86400 (24h) is appropriate.
        Pass max_ticks to limit iterations (useful for testing).
        """
        tick = 0
        logger.info(
            "Starting paper trader: %s on %s %s (every %ds)",
            self.name, self.symbol, self.interval, interval_seconds,
        )
        try:
            while max_ticks is None or tick < max_ticks:
                self.run_once()
                tick += 1
                if max_ticks is not None and tick >= max_ticks:
                    break
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("Paper trader %s stopped by user after %d ticks", self.name, tick)

        logger.info("Paper trader %s summary: %s", self.name, self.trade_log.summary())


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    """Run both DualMA and Donchian paper traders for a single tick (demo)."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    from trading.strategies import dual_ma_btc_daily, donchian_btc_daily

    traders = [
        PaperTrader(
            strategy=dual_ma_btc_daily,
            name="DualMA_10_30",
            interval="1d",
            log_path="results/paper_dual_ma.jsonl",
        ),
        PaperTrader(
            strategy=donchian_btc_daily,
            name="Donchian_20",
            interval="1d",
            log_path="results/paper_donchian.jsonl",
        ),
    ]

    for pt in traders:
        print(f"\n--- {pt.name} ---")
        try:
            result = pt.run_once()
            for k, v in result.items():
                print(f"  {k}: {v}")
        except Exception as e:
            print(f"  [offline mode] Could not fetch live data: {e}")
            print("  Paper trader is structurally ready; needs network access to run.")


if __name__ == "__main__":
    main()
