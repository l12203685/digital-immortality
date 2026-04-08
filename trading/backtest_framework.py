"""
Backtesting framework for BTC strategy validation.

Supports 4 strategy types x 3 timeframes with walk-forward validation.
Filter rules from DNA: walk-forward >= 3/5 windows, Sharpe > 1.0, MDD < 20%.

Zero external dependencies (numpy optional).
"""

import math
import random
from typing import List, Dict, Callable, Tuple, Optional

# ---------------------------------------------------------------------------
# Optional numpy — graceful fallback to stdlib math
# ---------------------------------------------------------------------------
try:
    import numpy as _np

    def _mean(xs):
        a = _np.array(xs, dtype=float)
        return float(_np.mean(a))

    def _std(xs, ddof=1):
        a = _np.array(xs, dtype=float)
        return float(_np.std(a, ddof=ddof)) if len(a) > 1 else 0.0

except ImportError:
    _np = None

    def _mean(xs):
        return sum(xs) / len(xs) if xs else 0.0

    def _std(xs, ddof=1):
        if len(xs) < 2:
            return 0.0
        m = _mean(xs)
        return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - ddof))


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------
TIMEFRAMES = ("1h", "4h", "1d")

# A bar is just a dict: {"open": f, "high": f, "low": f, "close": f, "volume": f}
Bar = Dict[str, float]

# A signal is +1 (long), -1 (short), or 0 (flat)
Signal = int

# Strategy function signature: (bars_so_far) -> Signal
StrategyFn = Callable[[List[Bar]], Signal]


# ---------------------------------------------------------------------------
# Strategy interfaces — four canonical types
# ---------------------------------------------------------------------------

def mean_reversion(bars: List[Bar], lookback: int = 20, z_entry: float = 1.5) -> Signal:
    """Go long when price is z_entry stdevs below mean, short when above."""
    if len(bars) < lookback:
        return 0
    closes = [b["close"] for b in bars[-lookback:]]
    mu = _mean(closes)
    sigma = _std(closes)
    if sigma == 0:
        return 0
    z = (bars[-1]["close"] - mu) / sigma
    if z < -z_entry:
        return 1
    if z > z_entry:
        return -1
    return 0


def momentum(bars: List[Bar], fast: int = 10, slow: int = 30) -> Signal:
    """Long when fast MA > slow MA, short otherwise."""
    if len(bars) < slow:
        return 0
    fast_ma = _mean([b["close"] for b in bars[-fast:]])
    slow_ma = _mean([b["close"] for b in bars[-slow:]])
    if fast_ma > slow_ma:
        return 1
    if fast_ma < slow_ma:
        return -1
    return 0


def breakout(bars: List[Bar], lookback: int = 20) -> Signal:
    """Long on new high, short on new low over lookback period."""
    if len(bars) < lookback + 1:
        return 0
    window = bars[-(lookback + 1):-1]
    highs = [b["high"] for b in window]
    lows = [b["low"] for b in window]
    cur = bars[-1]["close"]
    if cur > max(highs):
        return 1
    if cur < min(lows):
        return -1
    return 0


def volatility_regime(bars: List[Bar], lookback: int = 20, vol_threshold: float = 1.5) -> Signal:
    """Trade mean-reversion in low-vol regimes, momentum in high-vol."""
    n = len(bars)
    if n < lookback * 2 + 1:
        return 0
    recent_returns = [
        (bars[n - lookback + i]["close"] - bars[n - lookback + i - 1]["close"])
        / bars[n - lookback + i - 1]["close"]
        for i in range(lookback)
    ]
    older_returns = [
        (bars[n - 2 * lookback + i]["close"] - bars[n - 2 * lookback + i - 1]["close"])
        / bars[n - 2 * lookback + i - 1]["close"]
        for i in range(lookback)
    ]
    vol_recent = _std(recent_returns)
    vol_older = _std(older_returns)
    if vol_older == 0:
        return 0
    vol_ratio = vol_recent / vol_older
    if vol_ratio < vol_threshold:
        return mean_reversion(bars, lookback)
    else:
        return momentum(bars)


STRATEGIES: Dict[str, StrategyFn] = {
    "mean_reversion": mean_reversion,
    "momentum": momentum,
    "breakout": breakout,
    "volatility_regime": volatility_regime,
}

# ---------------------------------------------------------------------------
# Register external strategies from strategies/ directory
# ---------------------------------------------------------------------------
try:
    from strategies.momentum import momentum_crossover
    STRATEGIES["momentum_crossover"] = momentum_crossover
except ImportError:
    pass

try:
    from strategies.mean_reversion import bollinger_mean_reversion
    STRATEGIES["bollinger_mr"] = bollinger_mean_reversion
except ImportError:
    pass

try:
    from trading.strategies import (
        donchian_confirmed_btc_daily,
        dual_ma_rsi_btc_daily,
        dual_ma_rsi_filtered,
    )
    _EXTRA_STRATEGIES = {
        "DonchianConfirmed": donchian_confirmed_btc_daily,
        "DualMA_RSI": dual_ma_rsi_btc_daily,
        "DualMA_RSI_filtered": dual_ma_rsi_filtered,
    }
except ImportError:
    _EXTRA_STRATEGIES = {}


# ---------------------------------------------------------------------------
# Backtest engine
# ---------------------------------------------------------------------------

def run_backtest(bars: List[Bar], strategy_fn: StrategyFn) -> List[float]:
    """
    Run strategy over bars, return list of per-bar PnL (as fraction of price).
    Assumes: enter/exit at close, no slippage, no fees (add later).
    """
    pnl: List[float] = []
    position = 0  # current position: +1, -1, or 0
    entry_price = 0.0

    for i in range(1, len(bars)):
        # Realised PnL from holding
        if position != 0:
            ret = (bars[i]["close"] - bars[i - 1]["close"]) / bars[i - 1]["close"]
            pnl.append(position * ret)
        else:
            pnl.append(0.0)

        # Generate new signal
        signal = strategy_fn(bars[: i + 1])

        if signal != position:
            position = signal
            entry_price = bars[i]["close"]

    return pnl


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def compute_metrics(pnl: List[float], periods_per_year: int = 365) -> Dict[str, float]:
    """Compute Sharpe, MDD, win rate, profit factor from per-period returns."""
    if not pnl:
        return {"sharpe": 0.0, "mdd": 0.0, "win_rate": 0.0, "profit_factor": 0.0}

    # Sharpe ratio (annualised)
    mu = _mean(pnl)
    sigma = _std(pnl)
    sharpe = (mu / sigma) * math.sqrt(periods_per_year) if sigma > 0 else 0.0

    # Max drawdown on cumulative equity
    cumulative = 0.0
    peak = 0.0
    max_dd = 0.0
    for r in pnl:
        cumulative += r
        if cumulative > peak:
            peak = cumulative
        dd = peak - cumulative
        if dd > max_dd:
            max_dd = dd

    # Win rate
    wins = sum(1 for r in pnl if r > 0)
    trades = sum(1 for r in pnl if r != 0)
    win_rate = wins / trades if trades > 0 else 0.0

    # Profit factor = gross profit / gross loss
    gross_profit = sum(r for r in pnl if r > 0)
    gross_loss = abs(sum(r for r in pnl if r < 0))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

    return {
        "sharpe": round(sharpe, 4),
        "mdd": round(max_dd * 100, 2),  # as percentage
        "win_rate": round(win_rate * 100, 2),
        "profit_factor": round(profit_factor, 4),
    }


# ---------------------------------------------------------------------------
# Walk-forward validation
# ---------------------------------------------------------------------------

def walk_forward(
    bars: List[Bar],
    strategy_fn: StrategyFn,
    n_windows: int = 5,
    train_ratio: float = 0.6,
    periods_per_year: int = 365,
) -> List[Dict[str, float]]:
    """
    Split data into n_windows overlapping walk-forward segments.
    Each window: train on first train_ratio, test on remainder.
    Returns list of metric dicts (one per window, from the TEST portion).
    """
    total = len(bars)
    window_size = total // n_windows
    if window_size < 40:
        raise ValueError(f"Not enough data: {total} bars for {n_windows} windows")

    results = []
    for w in range(n_windows):
        start = w * (total - window_size) // max(n_windows - 1, 1)
        end = start + window_size
        window_bars = bars[start:end]

        train_end = int(len(window_bars) * train_ratio)
        test_bars = window_bars  # strategy sees all bars up to current point
        # but we only measure PnL on the test portion
        full_pnl = run_backtest(window_bars, strategy_fn)
        test_pnl = full_pnl[train_end:]

        metrics = compute_metrics(test_pnl, periods_per_year)
        results.append(metrics)

    return results


# ---------------------------------------------------------------------------
# Strategy filter — the DNA rules
# ---------------------------------------------------------------------------

def strategy_passes_filter(
    bars: List[Bar],
    strategy_fn: StrategyFn,
    n_windows: int = 5,
    min_passing_windows: int = 3,
    min_sharpe: float = 1.0,
    max_mdd: float = 20.0,
    periods_per_year: int = 365,
) -> Tuple[bool, List[Dict[str, float]]]:
    """
    Apply DNA filter rules:
      - Walk-forward must pass >= min_passing_windows / n_windows
      - Each window passes if: Sharpe > min_sharpe AND MDD < max_mdd
    Returns (passed: bool, window_results: list).
    """
    window_results = walk_forward(
        bars, strategy_fn, n_windows=n_windows, periods_per_year=periods_per_year
    )

    passing = 0
    for m in window_results:
        if m["sharpe"] > min_sharpe and m["mdd"] < max_mdd:
            passing += 1

    return passing >= min_passing_windows, window_results


# ---------------------------------------------------------------------------
# MAE/MFE analysis — MD-13, MD-157, MD-175
# ---------------------------------------------------------------------------

def _atr(bars: List[Bar], period: int = 14) -> float:
    """Average True Range over the last `period` bars."""
    if len(bars) < period + 1:
        return bars[-1]["high"] - bars[-1]["low"] if bars else 1.0
    trs = []
    for i in range(-period, 0):
        bar = bars[i]
        prev_close = bars[i - 1]["close"]
        tr = max(
            bar["high"] - bar["low"],
            abs(bar["high"] - prev_close),
            abs(bar["low"] - prev_close),
        )
        trs.append(tr)
    return _mean(trs) if trs else 1.0


def compute_mae_mfe(
    bars: List[Bar],
    strategy_fn: StrategyFn,
    atr_period: int = 14,
) -> Dict[str, float]:
    """
    Per-trade MAE/MFE analysis normalized by ATR at entry.

    MD-13:  edge_ratio = avg(MFE/ATR) / avg(MAE/ATR) × sqrt(N)
    MD-157: true edge = minimum MAE while capturing maximum MFE.
    MD-175: MAE/MFE distributions diagnose strategy-to-market fit.

    Returns:
        n_trades       — total closed trades analyzed
        avg_mae_atr    — avg Max Adverse Excursion / ATR
        avg_mfe_atr    — avg Max Favorable Excursion / ATR
        mae_mfe_ratio  — avg_mfe_atr / avg_mae_atr  (>1 = edge)
        edge_ratio     — mae_mfe_ratio × sqrt(N)    (MD-13 quality score)
    """
    trades = []
    position = 0
    entry_idx = 0
    entry_price = 0.0

    for i in range(1, len(bars)):
        signal = strategy_fn(bars[: i + 1])

        # Close existing trade when signal flips or goes flat
        if position != 0 and signal != position:
            trade_bars = bars[entry_idx : i + 1]
            atr_at_entry = _atr(bars[: entry_idx + 1], atr_period)
            if atr_at_entry <= 0:
                atr_at_entry = 1.0

            if position == 1:  # long: adverse = price below entry, favorable = above
                mfe = max((b["high"] - entry_price for b in trade_bars[1:]), default=0.0)
                mae = max((entry_price - b["low"] for b in trade_bars[1:]), default=0.0)
            else:  # short: adverse = price above entry, favorable = below
                mfe = max((entry_price - b["low"] for b in trade_bars[1:]), default=0.0)
                mae = max((b["high"] - entry_price for b in trade_bars[1:]), default=0.0)

            trades.append(
                {
                    "mfe_atr": max(mfe, 0.0) / atr_at_entry,
                    "mae_atr": max(mae, 0.0) / atr_at_entry,
                    "pnl": (bars[i]["close"] - entry_price) * position / entry_price,
                }
            )

        # Open new position
        if signal != position:
            position = signal
            entry_idx = i
            entry_price = bars[i]["close"]

    if not trades:
        return {
            "n_trades": 0,
            "avg_mae_atr": 0.0,
            "avg_mfe_atr": 0.0,
            "mae_mfe_ratio": 0.0,
            "edge_ratio": 0.0,
        }

    n = len(trades)
    avg_mae = _mean([t["mae_atr"] for t in trades])
    avg_mfe = _mean([t["mfe_atr"] for t in trades])
    mae_mfe_ratio = avg_mfe / avg_mae if avg_mae > 0 else float("inf")
    edge_ratio = mae_mfe_ratio * math.sqrt(n)

    return {
        "n_trades": n,
        "avg_mae_atr": round(avg_mae, 4),
        "avg_mfe_atr": round(avg_mfe, 4),
        "mae_mfe_ratio": round(mae_mfe_ratio, 4),
        "edge_ratio": round(edge_ratio, 4),
    }


# ---------------------------------------------------------------------------
# Synthetic data generation
# ---------------------------------------------------------------------------

def generate_synthetic_bars(
    n: int = 1000,
    start_price: float = 30000.0,
    drift: float = 0.0,
    volatility: float = 0.02,
    seed: Optional[int] = None,
) -> List[Bar]:
    """Generate synthetic OHLCV bars via geometric random walk."""
    if seed is not None:
        random.seed(seed)

    bars = []
    price = start_price
    for _ in range(n):
        ret = drift + volatility * random.gauss(0, 1)
        new_price = price * (1 + ret)
        high = max(price, new_price) * (1 + abs(random.gauss(0, 0.005)))
        low = min(price, new_price) * (1 - abs(random.gauss(0, 0.005)))
        bars.append({
            "open": round(price, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "close": round(new_price, 2),
            "volume": round(random.uniform(100, 10000), 2),
        })
        price = new_price
    return bars


def _timeframe_label(tf: str) -> int:
    """Periods per year for each timeframe."""
    return {"1h": 8760, "4h": 2190, "1d": 365}[tf]


# ---------------------------------------------------------------------------
# Main — demonstrate walk-forward filter rejecting a bad strategy
# ---------------------------------------------------------------------------

def main():
    print("=" * 64)
    print("BACKTEST FRAMEWORK — Walk-Forward Validation Demo")
    print("=" * 64)
    print(f"Strategies: {list(STRATEGIES.keys())}")
    print(f"Timeframes: {list(TIMEFRAMES)}")
    print(f"Filter: >= 3/5 windows, Sharpe > 1.0, MDD < 20%")
    print()

    total_pass = 0
    total_tests = 0

    for tf in TIMEFRAMES:
        n_bars = {"1h": 2000, "4h": 1000, "1d": 500}[tf]
        ppy = _timeframe_label(tf)

        print(f"--- Timeframe: {tf} ({n_bars} bars, {ppy} periods/year) ---")

        # Pure noise: no drift = no real edge. Most strategies should fail.
        bars = generate_synthetic_bars(n=n_bars, drift=0.0, volatility=0.02, seed=42)

        for name, fn in STRATEGIES.items():
            passed, results = strategy_passes_filter(
                bars, fn, n_windows=5, periods_per_year=ppy
            )

            windows_passed = sum(
                1 for m in results if m["sharpe"] > 1.0 and m["mdd"] < 20.0
            )
            avg_sharpe = _mean([m["sharpe"] for m in results])
            avg_mdd = _mean([m["mdd"] for m in results])

            verdict = "PASS" if passed else "REJECT"
            if passed:
                total_pass += 1
            total_tests += 1
            print(
                f"  {name:20s} | {verdict:6s} | "
                f"windows={windows_passed}/5 | "
                f"avg_sharpe={avg_sharpe:+.2f} | "
                f"avg_mdd={avg_mdd:.1f}%"
            )

        print()

    reject_rate = (total_tests - total_pass) / total_tests * 100
    print("=" * 64)
    print(f"Filter rejected {total_tests - total_pass}/{total_tests} "
          f"({reject_rate:.0f}%) strategy-timeframe combinations on noise.")
    print("Some may pass by chance — that is expected with random data.")
    print("Real deployment requires consistent edge, not lucky windows.")
    print("Bias toward inaction: no clear edge = no trade.")
    print("=" * 64)

    # MAE/MFE diagnostic (MD-13, MD-157, MD-175)
    print()
    print("=" * 64)
    print("MAE/MFE DIAGNOSTIC — MD-13 Edge Ratio (1d, trending data)")
    print("=" * 64)
    trending_bars = generate_synthetic_bars(n=500, drift=0.001, volatility=0.02, seed=7)
    all_mae_mfe = {**STRATEGIES, **_EXTRA_STRATEGIES}
    for name, fn in all_mae_mfe.items():
        stats = compute_mae_mfe(trending_bars, fn)
        print(
            f"  {name:22s} | trades={stats['n_trades']:3d} | "
            f"MAE/ATR={stats['avg_mae_atr']:.3f} | "
            f"MFE/ATR={stats['avg_mfe_atr']:.3f} | "
            f"ratio={stats['mae_mfe_ratio']:.3f} | "
            f"edge_ratio={stats['edge_ratio']:.2f}"
        )
    print()
    print("edge_ratio = (avg MFE/ATR)/(avg MAE/ATR) × √N  (MD-13)")
    print("Higher = better fit to market structure at entry.")
    print("DonchianConfirmed / RSI-filtered expected to show higher edge_ratio vs base.")
    print("=" * 64)


if __name__ == "__main__":
    main()
