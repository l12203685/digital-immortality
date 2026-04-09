#!/usr/bin/env python3
"""
Generate realistic synthetic market data with known statistical properties.

Produces OHLCV CSV files that match the format expected by trading_system.py:
    date,open,high,low,close,volume

Regimes:
  --regime trending       Strong directional moves with pullbacks.
                          Momentum / trend-following strategies should profit.
  --regime mean-reverting Oscillating price confined to a channel.
                          Bollinger-band / mean-reversion strategies should profit.
  --regime mixed          Alternating trending and mean-reverting phases,
                          closer to real markets.

Price dynamics use geometric Brownian motion with regime-dependent drift,
Ornstein-Uhlenbeck mean reversion, and optional regime switching.

Usage:
    python tools/generate_market_data.py --regime trending   --bars 500 --output data/trending_500.csv
    python tools/generate_market_data.py --regime mean-reverting --bars 500 --output data/mean_reverting_500.csv
    python tools/generate_market_data.py --regime mixed      --bars 500 --output data/mixed_500.csv
"""

import argparse
import csv
import math
import random
from datetime import datetime, timedelta
from pathlib import Path


def _ou_increment(x: float, mu: float, theta: float, sigma: float, dt: float = 1.0) -> float:
    """
    One step of the Ornstein-Uhlenbeck process:
        dx = theta * (mu - x) * dt + sigma * sqrt(dt) * N(0,1)
    Returns the new value of x.
    """
    noise = random.gauss(0, 1)
    return x + theta * (mu - x) * dt + sigma * math.sqrt(dt) * noise


def generate_trending(
    n: int,
    start_price: float = 40000.0,
    seed: int = 101,
) -> list:
    """
    Generate bars with clear trending behavior.

    Strategy: alternate between strong uptrend and strong downtrend legs,
    each lasting 40-120 bars, with gentle pullbacks in between.
    Drift is strong enough that a dual-MA crossover can capture it;
    volatility is moderate so signals are not whipsawed.
    """
    random.seed(seed)
    bars = []
    price = start_price

    # Plan trend legs
    legs = []
    remaining = n
    while remaining > 0:
        leg_len = random.randint(40, 120)
        leg_len = min(leg_len, remaining)
        # Alternate direction with some randomness
        if not legs:
            direction = random.choice([1, -1])
        else:
            direction = -legs[-1][1]
        legs.append((leg_len, direction))
        remaining -= leg_len

    bar_idx = 0
    for leg_len, direction in legs:
        # Drift per bar: strong enough for MA crossover to detect
        # ~0.2-0.5% per bar in the trend direction
        drift = direction * random.uniform(0.002, 0.005)
        # Volatility: moderate, less than drift magnitude to keep signal clear
        vol = random.uniform(0.008, 0.015)

        for j in range(leg_len):
            # Slight drift decay near end of leg (trend exhaustion)
            progress = j / max(leg_len - 1, 1)
            effective_drift = drift * (1.0 - 0.5 * progress ** 2)

            ret = effective_drift + vol * random.gauss(0, 1)
            new_price = price * (1 + ret)

            # Realistic OHLCV
            intra_vol = abs(ret) + random.uniform(0.001, 0.005)
            high = max(price, new_price) * (1 + random.uniform(0, intra_vol))
            low = min(price, new_price) * (1 - random.uniform(0, intra_vol))

            # Volume spikes at trend start and end
            base_volume = random.uniform(15000, 25000)
            if progress < 0.1 or progress > 0.85:
                base_volume *= random.uniform(1.5, 2.5)

            bars.append({
                "open": price,
                "high": high,
                "low": low,
                "close": new_price,
                "volume": base_volume,
            })
            price = new_price
            bar_idx += 1

    return bars


def generate_mean_reverting(
    n: int,
    start_price: float = 40000.0,
    seed: int = 202,
) -> list:
    """
    Generate bars with strong mean-reverting behavior.

    Uses Ornstein-Uhlenbeck process for log-prices, producing oscillations
    around a slowly drifting mean. Price repeatedly touches upper/lower
    bands and reverts, which Bollinger Band strategies can capture.
    """
    random.seed(seed)
    bars = []

    # OU parameters tuned so price oscillates with clear band-touching behavior.
    # Higher sigma drives price to Bollinger band extremes; higher theta
    # snaps it back, creating the classic mean-reversion pattern.
    log_price = math.log(start_price)
    log_mean = log_price
    theta = 0.15       # mean-reversion speed (higher = faster reversion)
    sigma = 0.022      # noise amplitude — large enough to push past 2-sigma bands
    mean_drift = 0.00005  # very slow drift of the mean itself

    for i in range(n):
        # Slowly drift the mean to avoid perfectly stationary data
        log_mean += mean_drift + 0.00005 * math.sin(2 * math.pi * i / 200)

        # OU step
        log_price = _ou_increment(log_price, log_mean, theta, sigma)
        close = math.exp(log_price)

        # Previous close (or start_price for first bar)
        if bars:
            open_price = bars[-1]["close"]
        else:
            open_price = start_price

        # Intraday range: add some noise but keep it bounded
        spread = close * random.uniform(0.003, 0.012)
        high = max(open_price, close) + random.uniform(0, spread)
        low = min(open_price, close) - random.uniform(0, spread)

        # Volume: higher when price is far from mean (at extremes)
        deviation = abs(log_price - log_mean) / sigma
        base_volume = random.uniform(12000, 20000)
        if deviation > 1.5:
            base_volume *= random.uniform(1.3, 2.0)

        bars.append({
            "open": open_price,
            "high": high,
            "low": low,
            "close": close,
            "volume": base_volume,
        })

    return bars


def generate_mixed(
    n: int,
    start_price: float = 40000.0,
    seed: int = 303,
) -> list:
    """
    Generate mixed-regime data: alternating trending and mean-reverting phases.

    Each phase lasts 50-150 bars. Transitions are smooth (not abrupt) to mimic
    real market regime changes. This tests whether strategies can handle both
    environments and, importantly, whether they avoid losses during the
    wrong regime.
    """
    random.seed(seed)
    bars = []
    price = start_price

    # Plan regime segments
    segments = []
    remaining = n
    regime = random.choice(["trend", "mr"])
    while remaining > 0:
        seg_len = random.randint(50, 150)
        seg_len = min(seg_len, remaining)
        segments.append((seg_len, regime))
        remaining -= seg_len
        regime = "mr" if regime == "trend" else "trend"

    log_price = math.log(price)
    log_mean = log_price  # for MR phases

    for seg_len, regime in segments:
        if regime == "trend":
            direction = random.choice([1, -1])
            drift = direction * random.uniform(0.0015, 0.004)
            vol = random.uniform(0.010, 0.018)

            for j in range(seg_len):
                progress = j / max(seg_len - 1, 1)
                effective_drift = drift * (1.0 - 0.3 * progress ** 2)
                ret = effective_drift + vol * random.gauss(0, 1)
                new_price = price * (1 + ret)

                intra_vol = abs(ret) + random.uniform(0.001, 0.004)
                high = max(price, new_price) * (1 + random.uniform(0, intra_vol))
                low = min(price, new_price) * (1 - random.uniform(0, intra_vol))

                base_volume = random.uniform(14000, 22000)
                if progress < 0.1:
                    base_volume *= random.uniform(1.3, 2.0)

                bars.append({
                    "open": price,
                    "high": high,
                    "low": low,
                    "close": new_price,
                    "volume": base_volume,
                })
                price = new_price
        else:
            # Mean-reverting phase
            log_price = math.log(price)
            log_mean = log_price
            theta = random.uniform(0.08, 0.15)
            sigma = random.uniform(0.012, 0.018)

            for j in range(seg_len):
                log_mean += 0.0001 * math.sin(2 * math.pi * j / 100)
                log_price = _ou_increment(log_price, log_mean, theta, sigma)
                close = math.exp(log_price)
                open_price = price

                spread = close * random.uniform(0.003, 0.010)
                high = max(open_price, close) + random.uniform(0, spread)
                low = min(open_price, close) - random.uniform(0, spread)

                base_volume = random.uniform(12000, 20000)
                deviation = abs(log_price - log_mean) / max(sigma, 0.001)
                if deviation > 1.5:
                    base_volume *= random.uniform(1.2, 1.8)

                bars.append({
                    "open": open_price,
                    "high": high,
                    "low": low,
                    "close": close,
                    "volume": base_volume,
                })
                price = close

    return bars


def bars_to_csv(bars: list, output_path: str, start_date: str = "2024-01-02"):
    """
    Write bars to a CSV file in the standard OHLCV format.

    Dates are sequential trading days starting from start_date.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    dt = datetime.strptime(start_date, "%Y-%m-%d")

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "open", "high", "low", "close", "volume"])

        for bar in bars:
            # Skip weekends for realism
            while dt.weekday() >= 5:
                dt += timedelta(days=1)

            writer.writerow([
                dt.strftime("%Y-%m-%d"),
                f"{bar['open']:.2f}",
                f"{bar['high']:.2f}",
                f"{bar['low']:.2f}",
                f"{bar['close']:.2f}",
                f"{bar['volume']:.2f}",
            ])
            dt += timedelta(days=1)

    print(f"Wrote {len(bars)} bars to {path}")


def print_stats(bars: list, label: str):
    """Print summary statistics for generated data."""
    closes = [b["close"] for b in bars]
    returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]

    mean_ret = sum(returns) / len(returns)
    var_ret = sum((r - mean_ret) ** 2 for r in returns) / (len(returns) - 1)
    std_ret = math.sqrt(var_ret)

    # Autocorrelation of returns (lag 1) — positive = trending, negative = mean-reverting
    mean_r = mean_ret
    numerator = sum((returns[i] - mean_r) * (returns[i-1] - mean_r) for i in range(1, len(returns)))
    denominator = sum((r - mean_r) ** 2 for r in returns)
    autocorr = numerator / denominator if denominator > 0 else 0.0

    # Price range
    min_price = min(closes)
    max_price = max(closes)

    # Total return
    total_ret = (closes[-1] - closes[0]) / closes[0] * 100

    print(f"\n  {label}:")
    print(f"    Bars: {len(bars)}")
    print(f"    Price range: {min_price:.2f} - {max_price:.2f}")
    print(f"    Total return: {total_ret:+.2f}%")
    print(f"    Mean daily return: {mean_ret*100:+.4f}%")
    print(f"    Std daily return: {std_ret*100:.4f}%")
    print(f"    Return autocorrelation (lag-1): {autocorr:+.4f}")
    print(f"      (positive = trending, negative = mean-reverting)")


def main():
    parser = argparse.ArgumentParser(
        description="Generate realistic synthetic market data with known regime properties."
    )
    parser.add_argument(
        "--regime",
        choices=["trending", "mean-reverting", "mixed"],
        required=True,
        help="Market regime: trending, mean-reverting, or mixed",
    )
    parser.add_argument(
        "--bars", type=int, default=500,
        help="Number of bars to generate (default: 500)",
    )
    parser.add_argument(
        "--output", type=str, required=True,
        help="Output CSV file path",
    )
    parser.add_argument(
        "--seed", type=int, default=None,
        help="Random seed for reproducibility (default: regime-specific)",
    )
    parser.add_argument(
        "--start-price", type=float, default=40000.0,
        help="Starting price (default: 40000.0)",
    )

    args = parser.parse_args()

    generators = {
        "trending": generate_trending,
        "mean-reverting": generate_mean_reverting,
        "mixed": generate_mixed,
    }

    gen_fn = generators[args.regime]
    kwargs = {"n": args.bars, "start_price": args.start_price}
    if args.seed is not None:
        kwargs["seed"] = args.seed

    bars = gen_fn(**kwargs)
    bars_to_csv(bars, args.output)
    print_stats(bars, f"{args.regime} regime")


if __name__ == "__main__":
    main()
