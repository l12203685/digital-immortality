"""
Testnet Runner — Binance USDT-M Futures Testnet

Runs validated strategies on Binance testnet with structured logging.
Serves as the GO/NO-GO gate before mainnet at small size.

Usage:
    python testnet_runner.py --tick                 # single tick, all strategies
    python testnet_runner.py --tick --strategy dual_ma  # single tick, named strategy
    python testnet_runner.py --status              # show current state from log
    python testnet_runner.py --review              # print GO/NO-GO vs kill conditions
    python testnet_runner.py --loop 3600           # loop every 3600s (1h)
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from trading.backtest_framework import Bar, compute_mae_mfe
from trading.live_binance import BinanceConfig, LiveExecutor
from trading.strategies import (
    dual_ma_btc_daily,
    donchian_btc_daily,
    dual_ma_filtered,
    donchian_filtered,
)

try:
    from trading.portfolio import PortfolioSelector
    _PORTFOLIO_SELECTOR = PortfolioSelector()
    _HAS_PORTFOLIO = True
except ImportError:
    _HAS_PORTFOLIO = False

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RESULTS_DIR = Path(__file__).parent.parent / "results"
TESTNET_LOG = RESULTS_DIR / "testnet_log.jsonl"
BACKTEST_RESULTS = RESULTS_DIR / "backtest_results.json"

STRATEGIES = {
    "dual_ma": dual_ma_btc_daily,
    "donchian": donchian_btc_daily,
    "dual_ma_filtered": dual_ma_filtered,
    "donchian_filtered": donchian_filtered,
}

STRATEGY_MIN_LOOKBACK = {
    "dual_ma": 31,           # slow=30 + 1 buffer
    "donchian": 22,          # period=20 + 2 buffer
    "dual_ma_filtered": 56,  # RegimeFilter(trend_period=50, slope_bars=5) + 1
    "donchian_filtered": 56,
}

# Maps STRATEGIES keys → portfolio strategy names returned by PortfolioSelector.select()
STRATEGY_PORTFOLIO_NAME = {
    "dual_ma": "DualMA_10_30",
    "donchian": "DonchianConfirmed_20",
    "dual_ma_filtered": "DualMA_filtered",
    "donchian_filtered": None,   # no direct portfolio equivalent
}

# Kill conditions (mirror paper_trader_review thresholds)
KILL_MAX_DRAWDOWN_PCT = 15.0   # stricter on testnet (paper was 20%)
KILL_MIN_WIN_RATE = 0.35
KILL_MIN_PROFIT_FACTOR = 0.85
REVIEW_MIN_TICKS = 7           # minimum ticks before issuing GO/NO-GO


# ---------------------------------------------------------------------------
# State persistence (append-only JSONL)
# ---------------------------------------------------------------------------

def _log_tick(entry: Dict) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(TESTNET_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def _load_log() -> List[Dict]:
    if not TESTNET_LOG.exists():
        return []
    entries = []
    with open(TESTNET_LOG, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries


# ---------------------------------------------------------------------------
# Portfolio regime helpers
# ---------------------------------------------------------------------------

def _detect_regime_strategy(bars: List[Bar]):
    """
    Detect the current market regime and return the recommended strategy.

    Returns (regime_str, strategy_name) using the module-level
    _PORTFOLIO_SELECTOR.  Falls back to ("unknown", None) if the portfolio
    module is unavailable.
    """
    if not _HAS_PORTFOLIO:
        return "unknown", None
    regime, strategy_name, _strategy_fn = _PORTFOLIO_SELECTOR.select(bars)
    return regime, strategy_name


# ---------------------------------------------------------------------------
# Performance tracking
# ---------------------------------------------------------------------------

def _compute_stats(entries: List[Dict], strategy: str) -> Dict:
    """Compute running PnL, drawdown, win rate, and profit factor from log."""
    ticks = [e for e in entries if e.get("strategy") == strategy]
    if not ticks:
        return {"tick_count": 0}

    pnl_series = []
    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    wins = 0
    losses = 0
    gross_profit = 0.0
    gross_loss = 0.0

    for e in ticks:
        pnl = e.get("pnl_usdt", 0.0)
        equity += pnl
        if equity > peak:
            peak = equity
        dd = (peak - equity) / max(peak, 1.0) * 100 if peak > 0 else 0.0
        max_dd = max(max_dd, dd)
        if pnl > 0:
            wins += 1
            gross_profit += pnl
        elif pnl < 0:
            losses += 1
            gross_loss += abs(pnl)
        pnl_series.append(equity)

    total_trades = wins + losses
    win_rate = wins / total_trades if total_trades > 0 else 0.0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

    return {
        "strategy": strategy,
        "tick_count": len(ticks),
        "total_pnl_usdt": round(equity, 4),
        "max_drawdown_pct": round(max_dd, 2),
        "win_rate": round(win_rate, 4),
        "profit_factor": round(profit_factor, 4),
        "wins": wins,
        "losses": losses,
    }


def _check_kills(stats: Dict) -> List[str]:
    kills = []
    if stats.get("max_drawdown_pct", 0) >= KILL_MAX_DRAWDOWN_PCT:
        kills.append(f"MDD {stats['max_drawdown_pct']:.1f}% >= {KILL_MAX_DRAWDOWN_PCT}%")
    if stats.get("win_rate", 1.0) < KILL_MIN_WIN_RATE and stats.get("wins", 0) + stats.get("losses", 0) >= 5:
        kills.append(f"WinRate {stats['win_rate']:.1%} < {KILL_MIN_WIN_RATE:.0%}")
    if stats.get("profit_factor", 999) < KILL_MIN_PROFIT_FACTOR and stats.get("losses", 0) >= 3:
        kills.append(f"PF {stats['profit_factor']:.3f} < {KILL_MIN_PROFIT_FACTOR}")
    return kills


# ---------------------------------------------------------------------------
# Single tick execution
# ---------------------------------------------------------------------------

def _compute_sim_pnl(entries: List[Dict], strategy: str, current_price: float, position_usdt: float) -> float:
    """
    Simulate PnL for dry-run ticks.

    Logic: the position held during [prev_tick → this_tick] was signaled by prev_tick.
    PnL = prev_signal × (current_price − prev_price) / prev_price × position_usdt
    Returns 0.0 if no prior tick or prior price is missing.
    """
    prev = next(
        (e for e in reversed(entries)
         if e.get("strategy") == strategy and e.get("price") and "signal" in e),
        None,
    )
    if prev is None:
        return 0.0
    prev_signal = prev["signal"]      # int: 1=LONG, -1=SHORT, 0=FLAT
    prev_price = float(prev["price"])
    if prev_price <= 0 or prev_signal == 0:
        return 0.0
    pct = (current_price - prev_price) / prev_price
    return round(prev_signal * pct * position_usdt, 4)


def run_tick(strategy_name: str, dry_run: bool = False, portfolio_gated: bool = False) -> Dict:
    """Execute one tick for a strategy. Returns the tick result dict."""
    strategy_fn = STRATEGIES[strategy_name]
    position_usdt = 100.0
    config = BinanceConfig(
        testnet=True,
        max_position_usdt=position_usdt,
        max_drawdown_pct=KILL_MAX_DRAWDOWN_PCT,
        leverage=1,
    )

    executor = LiveExecutor(config, strategy_fn, name=strategy_name)

    if dry_run or not config.has_credentials:
        # Dry run: fetch data, compute signal, no orders
        try:
            bars: List[Bar] = executor.client.fetch_ohlcv("1d", 100)

            # Portfolio regime gate: skip if this strategy is not the regime pick
            if portfolio_gated:
                regime, regime_strategy = _detect_regime_strategy(bars)
                expected_portfolio_name = STRATEGY_PORTFOLIO_NAME.get(strategy_name)
                if regime_strategy is not None and expected_portfolio_name != regime_strategy:
                    result = {
                        "ts": datetime.now(timezone.utc).isoformat(),
                        "strategy": strategy_name,
                        "action": "SKIPPED_REGIME",
                        "regime": regime,
                        "regime_selected_strategy": regime_strategy,
                        "pnl_usdt": 0.0,
                        "dry_run": True,
                    }
                    _log_tick(result)
                    return result

            signal = executor.strategy(bars)
            current_price = bars[-1]["close"] if bars else None
            prior_entries = _load_log()
            sim_pnl = _compute_sim_pnl(prior_entries, strategy_name, current_price, position_usdt) if current_price else 0.0
            result = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "strategy": strategy_name,
                "action": "DRY_RUN",
                "signal": signal,
                "price": current_price,
                "bars_fetched": len(bars),
                "pnl_usdt": sim_pnl,
                "dry_run": True,
            }
            if portfolio_gated:
                result["regime"] = regime
                result["regime_selected_strategy"] = regime_strategy
        except Exception as e:
            result = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "strategy": strategy_name,
                "action": "ERROR",
                "error": str(e),
                "pnl_usdt": 0.0,
                "dry_run": True,
            }
    else:
        # Live execution path
        if portfolio_gated:
            # Fetch bars early to run regime detection before executing
            try:
                bars_for_regime: List[Bar] = executor.client.fetch_ohlcv("1d", 100)
                regime, regime_strategy = _detect_regime_strategy(bars_for_regime)
                expected_portfolio_name = STRATEGY_PORTFOLIO_NAME.get(strategy_name)
                if regime_strategy is not None and expected_portfolio_name != regime_strategy:
                    result = {
                        "ts": datetime.now(timezone.utc).isoformat(),
                        "strategy": strategy_name,
                        "action": "SKIPPED_REGIME",
                        "regime": regime,
                        "regime_selected_strategy": regime_strategy,
                        "pnl_usdt": 0.0,
                    }
                    _log_tick(result)
                    return result
            except Exception as e:
                logger.warning("portfolio_gated regime detection failed for %s: %s", strategy_name, e)
                regime = "unknown"
                regime_strategy = None

        result = executor.tick()
        result["ts"] = datetime.now(timezone.utc).isoformat()
        result.setdefault("pnl_usdt", 0.0)
        if portfolio_gated:
            result["regime"] = regime
            result["regime_selected_strategy"] = regime_strategy

    _log_tick(result)
    return result


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------

def cmd_tick(strategy_name: Optional[str], dry_run: bool, portfolio_gated: bool = False) -> None:
    targets = [strategy_name] if strategy_name else list(STRATEGIES.keys())
    for s in targets:
        result = run_tick(s, dry_run=dry_run, portfolio_gated=portfolio_gated)
        ts = result.get("ts", "")[:19]
        signal_map = {1: "LONG", -1: "SHORT", 0: "FLAT"}
        sig = signal_map.get(result.get("signal", 0), "?")
        action = result.get("action", "?")
        price = result.get("price")
        price_str = f"${price:,.0f}" if price else "N/A"
        regime_str = ""
        if portfolio_gated:
            regime = result.get("regime", "")
            regime_strat = result.get("regime_selected_strategy", "")
            regime_str = f" regime={regime}({regime_strat})"
        print(f"[{ts}] {s:25s} signal={sig:5s} action={action:20s} price={price_str}{regime_str}")


def cmd_status(strategy_name: Optional[str]) -> None:
    entries = _load_log()
    if not entries:
        print("No testnet log entries found.")
        return

    targets = [strategy_name] if strategy_name else list(STRATEGIES.keys())
    for s in targets:
        stats = _compute_stats(entries, s)
        if stats["tick_count"] == 0:
            print(f"{s}: no data")
            continue
        kills = _check_kills(stats)
        kill_str = "KILL" if kills else "OK"
        print(
            f"{s:25s} ticks={stats['tick_count']:3d} "
            f"pnl={stats['total_pnl_usdt']:+8.2f} USDT "
            f"mdd={stats['max_drawdown_pct']:5.1f}% "
            f"wr={stats['win_rate']:5.1%} "
            f"pf={stats['profit_factor']:6.3f} "
            f"[{kill_str}]"
        )
        if kills:
            for k in kills:
                print(f"  KILL: {k}")


def _load_backtest_results() -> Optional[Dict]:
    """Load persisted backtest results if available."""
    if not BACKTEST_RESULTS.exists():
        return None
    try:
        with open(BACKTEST_RESULTS, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def cmd_review(strategy_name: Optional[str]) -> None:
    entries = _load_log()
    targets = [strategy_name] if strategy_name else list(STRATEGIES.keys())

    print(f"\n{'='*60}")
    print("Testnet GO/NO-GO Review")
    print(f"{'='*60}")
    print(f"Kill conditions: MDD>{KILL_MAX_DRAWDOWN_PCT}%, WR<{KILL_MIN_WIN_RATE:.0%}, PF<{KILL_MIN_PROFIT_FACTOR}")
    print(f"Min ticks for review: {REVIEW_MIN_TICKS}")
    print()

    go_count = 0
    insufficient = []
    for s in targets:
        stats = _compute_stats(entries, s)
        tc = stats.get("tick_count", 0)
        if tc < REVIEW_MIN_TICKS:
            insufficient.append((s, tc))
            continue
        kills = _check_kills(stats)
        verdict = "GO" if not kills else "NO_GO"
        if verdict == "GO":
            go_count += 1
        pf = stats.get("profit_factor", 0)
        pf_str = f"{pf:.3f}" if pf != float("inf") else "inf"
        print(
            f"{s:25s} {verdict:6s} "
            f"pnl={stats['total_pnl_usdt']:+.2f} USDT "
            f"mdd={stats['max_drawdown_pct']:.1f}% "
            f"wr={stats['win_rate']:.1%} "
            f"pf={pf_str}"
        )
        for k in kills:
            print(f"  -> KILL: {k}")

    if insufficient:
        bt = _load_backtest_results()
        print(f"\n-- Live ticks insufficient for: {[s for s, _ in insufficient]} --")
        if bt:
            print(f"   Backtest fallback (run: {bt['ts'][:19]}, bars={bt['bars_used']})")
            bt_by_name = {r["strategy"]: r for r in bt["strategies"]}
            for s, tc in insufficient:
                r = bt_by_name.get(s)
                if r:
                    pf_val = r["profit_factor"]
                    pf_str = f"{pf_val:.3f}" if pf_val is not None else "inf"
                    print(
                        f"   {s:25s} {r['verdict']:6s} [BACKTEST] "
                        f"pnl={r['total_pnl_usdt']:+.2f} USDT "
                        f"mdd={r['max_drawdown_pct']:.1f}% "
                        f"wr={r['win_rate']:.1%} "
                        f"pf={pf_str} "
                        f"trades={r['total_trades']}"
                    )
                    if r["verdict"] == "GO":
                        go_count += 1
                    for k in r["kills"]:
                        print(f"     -> KILL: {k}")
                else:
                    print(f"   {s:25s} INSUFFICIENT_DATA ({tc}/{REVIEW_MIN_TICKS} live ticks, no backtest)")
        else:
            for s, tc in insufficient:
                print(f"   {s:25s} INSUFFICIENT_DATA ({tc}/{REVIEW_MIN_TICKS} ticks) — run --backtest --save")

    print(f"\n{'='*60}")
    if go_count == len(targets):
        print("OVERALL: GO -> Proceed to mainnet small size")
    elif go_count > 0:
        print(f"OVERALL: CONDITIONAL_GO -> {go_count}/{len(targets)} strategies pass")
    else:
        print("OVERALL: NO_GO -> Extend testnet, recalibrate")
    print(f"{'='*60}\n")


def _run_backtest_strategy(strategy_name: str, bars: List[Dict]) -> Dict:
    """Run walk-forward backtest for one strategy. Returns stats dict."""
    strategy_fn = STRATEGIES[strategy_name]
    min_lookback = STRATEGY_MIN_LOOKBACK.get(strategy_name, 56)
    position_usdt = 100.0
    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    wins = 0
    losses = 0
    gross_profit = 0.0
    gross_loss = 0.0
    prev_signal: int = 0

    for i in range(min_lookback, len(bars)):
        window = bars[:i]
        signal = strategy_fn(window)
        cur_price = bars[i]["close"]
        prev_price = bars[i - 1]["close"]

        if prev_signal != 0 and prev_price > 0:
            pct = (cur_price - prev_price) / prev_price
            pnl = prev_signal * pct * position_usdt
            equity += pnl
            if equity > peak:
                peak = equity
            dd = max(peak - equity, 0.0) / position_usdt * 100
            max_dd = max(max_dd, dd)
            if pnl > 0:
                wins += 1
                gross_profit += pnl
            elif pnl < 0:
                losses += 1
                gross_loss += abs(pnl)

        prev_signal = signal

    total_trades = wins + losses
    win_rate = wins / total_trades if total_trades > 0 else 0.0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

    kills = []
    if max_dd >= KILL_MAX_DRAWDOWN_PCT:
        kills.append(f"MDD {max_dd:.1f}%>={KILL_MAX_DRAWDOWN_PCT}%")
    if win_rate < KILL_MIN_WIN_RATE and total_trades >= 5:
        kills.append(f"WR {win_rate:.1%}<{KILL_MIN_WIN_RATE:.0%}")
    if profit_factor < KILL_MIN_PROFIT_FACTOR and losses >= 3:
        kills.append(f"PF {profit_factor:.3f}<{KILL_MIN_PROFIT_FACTOR}")

    return {
        "strategy": strategy_name,
        "verdict": "GO" if not kills else "NO_GO",
        "total_pnl_usdt": round(equity, 4),
        "max_drawdown_pct": round(max_dd, 2),
        "win_rate": round(win_rate, 4),
        "profit_factor": round(profit_factor, 4) if profit_factor != float("inf") else None,
        "wins": wins,
        "losses": losses,
        "total_trades": total_trades,
        "kills": kills,
    }


def cmd_backtest(strategy_name: Optional[str], bars_limit: int = 100, save: bool = False) -> None:
    """
    Walk-forward backtest using live OHLCV bars from Binance testnet.

    For each bar i: signal = strategy(bars[:i]), hold during i→i+1.
    PnL[i] = prev_signal × (close[i] - close[i-1]) / close[i-1] × position_usdt
    Uses same kill conditions as --review. Produces immediate GO/NO-GO.
    With --save, persists results to results/backtest_results.json.
    """
    config = BinanceConfig(
        testnet=True,
        max_position_usdt=100.0,
        max_drawdown_pct=KILL_MAX_DRAWDOWN_PCT,
        leverage=1,
    )
    executor = LiveExecutor(config, dual_ma_btc_daily, name="backtest_fetch")

    print(f"\nFetching {bars_limit} daily bars from Binance testnet...")
    try:
        bars = executor.client.fetch_ohlcv("1d", bars_limit)
    except Exception as e:
        print(f"ERROR fetching bars: {e}")
        return

    if len(bars) < 55:
        print(f"Insufficient data: {len(bars)} bars (need 55+)")
        return

    price_lo = min(b["close"] for b in bars)
    price_hi = max(b["close"] for b in bars)
    print(f"Got {len(bars)} bars. BTC range: ${price_lo:,.0f}–${price_hi:,.0f}\n")

    targets = [strategy_name] if strategy_name else list(STRATEGIES.keys())

    print(f"{'='*70}")
    print(f"Walk-Forward Backtest — {len(bars)} daily bars, position=100.0 USDT")
    print(f"Kill: MDD>{KILL_MAX_DRAWDOWN_PCT}%, WR<{KILL_MIN_WIN_RATE:.0%}(≥5), PF<{KILL_MIN_PROFIT_FACTOR}(≥3 losses)")
    print(f"{'='*70}")
    print()

    results = []
    go_count = 0
    for s in targets:
        stats = _run_backtest_strategy(s, bars)
        results.append(stats)
        if stats["verdict"] == "GO":
            go_count += 1

        pf_val = stats["profit_factor"]
        pf_str = f"{pf_val:.3f}" if pf_val is not None else "  inf"
        print(
            f"{s:25s} {stats['verdict']:6s}  "
            f"pnl={stats['total_pnl_usdt']:+8.2f} USDT  "
            f"mdd={stats['max_drawdown_pct']:5.1f}%  "
            f"wr={stats['win_rate']:5.1%}  "
            f"pf={pf_str}  "
            f"trades={stats['total_trades']}"
        )
        for k in stats["kills"]:
            print(f"  -> KILL: {k}")

    overall = (
        "GO" if go_count == len(targets)
        else f"CONDITIONAL_GO ({go_count}/{len(targets)})"
        if go_count > 0
        else "NO_GO"
    )

    print(f"\n{'='*70}")
    if go_count == len(targets):
        print(f"BACKTEST: GO ({go_count}/{len(targets)}) -> Proceed to mainnet small size")
    elif go_count > 0:
        print(f"BACKTEST: CONDITIONAL_GO ({go_count}/{len(targets)} pass) -> Use passing strategies only")
    else:
        print(f"BACKTEST: NO_GO (0/{len(targets)}) -> Recalibrate before mainnet")
    print(f"{'='*70}\n")

    # MAE/MFE diagnostic (MD-13 edge ratio)
    print()
    print(f"{'='*70}")
    print("MAE/MFE Edge Ratio Diagnostic (MD-13, MD-157, MD-175)")
    print(f"{'='*70}")
    for s in targets:
        strategy_fn = STRATEGIES[s]
        mae_stats = compute_mae_mfe(bars, strategy_fn)
        if mae_stats["n_trades"] == 0:
            print(f"  {s:25s} no trades")
        else:
            print(
                f"  {s:25s} trades={mae_stats['n_trades']:3d} | "
                f"MAE/ATR={mae_stats['avg_mae_atr']:.3f} | "
                f"MFE/ATR={mae_stats['avg_mfe_atr']:.3f} | "
                f"edge_ratio={mae_stats['edge_ratio']:.2f}"
            )
    print(f"  edge_ratio>3 = strategy fits market structure (MD-13)")
    print(f"{'='*70}\n")

    if save:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "bars_used": len(bars),
            "overall": overall,
            "strategies": results,
        }
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        with open(BACKTEST_RESULTS, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        print(f"Backtest results saved -> {BACKTEST_RESULTS}")


def cmd_loop(strategy_name: Optional[str], interval: int, dry_run: bool) -> None:
    print(f"Starting testnet loop: interval={interval}s, strategies={strategy_name or 'all'}")
    targets = [strategy_name] if strategy_name else list(STRATEGIES.keys())
    tick_count = 0
    try:
        while True:
            for s in targets:
                result = run_tick(s, dry_run=dry_run)
                ts = result.get("ts", "")[:19]
                sig = {1: "LONG", -1: "SHORT", 0: "FLAT"}.get(result.get("signal", 0), "?")
                logger.info("[%s] %s signal=%s action=%s", ts, s, sig, result.get("action"))
            tick_count += 1
            logger.info("Sleeping %ds (tick %d)...", interval, tick_count)
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\nLoop stopped after {tick_count} ticks.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    parser = argparse.ArgumentParser(
        description="Testnet runner for Binance USDT-M Futures"
    )
    parser.add_argument("--strategy", choices=list(STRATEGIES.keys()), help="Strategy to run (default: all)")
    parser.add_argument("--tick", action="store_true", help="Execute one tick")
    parser.add_argument("--status", action="store_true", help="Show status from log")
    parser.add_argument("--review", action="store_true", help="GO/NO-GO review")
    parser.add_argument("--loop", type=int, metavar="SECONDS", help="Run in loop with given interval")
    parser.add_argument("--backtest", action="store_true", help="Walk-forward backtest using live testnet bars")
    parser.add_argument("--bars", type=int, default=100, help="Historical bars for --backtest (default: 100)")
    parser.add_argument("--save", action="store_true", default=False,
                        help="Persist --backtest results to results/backtest_results.json")
    parser.add_argument("--dry-run", action="store_true", default=False,
                        help="Compute signals without placing orders (default when no API keys)")
    parser.add_argument("--portfolio-gated", action="store_true", default=False,
                        help="Only run the regime-selected strategy per tick")

    args = parser.parse_args()

    if args.tick:
        cmd_tick(args.strategy, dry_run=args.dry_run, portfolio_gated=args.portfolio_gated)
    elif args.status:
        cmd_status(args.strategy)
    elif args.review:
        cmd_review(args.strategy)
    elif args.backtest:
        cmd_backtest(args.strategy, bars_limit=args.bars, save=args.save)
    elif args.loop is not None:
        cmd_loop(args.strategy, args.loop, dry_run=args.dry_run)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
