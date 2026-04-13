"""Market price updater for Edward's finance dashboard.

Refreshes `price_usd` for every ticker embedded in
`results/finance_marketcap.json` (top10 + weekly_gainers + weekly_losers +
owned_in_top200) using yfinance as the primary source and Stooq CSV as a
fallback. Also stamps `updated_at` (ISO Asia/Taipei) so the dashboard can
display data freshness.

Design constraints (see finance_data_audit.md):
  * No auth / no credit card — only free public feeds.
  * Resilient — one ticker failing must not break the run.
  * Preserves schema — existing keys are never renamed or dropped.
  * Append-only log in results/market_updater.log; no stdout prints.
  * Never mutates `finance_networth.json` (holdings in NTD, not market-priced
    equities in real time).

Run as:  python market_updater.py    (no args)

Scheduled via:  schtasks /Create /SC MINUTE /MO 30 /TN mc_market_updater ...
"""
from __future__ import annotations

import csv
import io
import json
import logging
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo

# --- Paths ---------------------------------------------------------------

REPO = Path("C:/Users/admin/workspace/digital-immortality")
RESULTS = REPO / "results"
MARKETCAP_JSON = RESULTS / "finance_marketcap.json"
WATCHLIST_YAML = RESULTS / "watchlist.yaml"
WATCHLIST_HISTORY_JSON = RESULTS / "watchlist_history.json"
ZERO_PORTFOLIO_JSON = RESULTS / "zero_portfolio_history.json"
LOG_FILE = RESULTS / "market_updater.log"

# How stale watchlist_history.json can get before we refetch. 20 h guards
# against daily Task Scheduler drift while keeping API calls low-volume.
WATCHLIST_HISTORY_MAX_AGE_S = 20 * 3600

# How many years of daily closes to cache for the slider (3M–60M).
WATCHLIST_HISTORY_PERIOD: str = "5y"

# Bonds are total-return (auto_adjust=True so dividends are reinvested
# into the close). Everything else defaults to auto-adjusted closes
# too — yfinance's auto_adjust already handles splits + divs cleanly.
BOND_SYMBOLS: frozenset[str] = frozenset({"ZROZ", "BIL", "IEF", "TLT"})

# Zero-portfolio composite formulas. Each entry is a list of
# (ticker, weight) pairs; a row-level formula evaluator handles the
# equity-bucket fractional weight on 2330.TW.
ZERO_PORTFOLIO_FORMULAS: dict[str, list[tuple[str, float]]] = {
    # 股 = IOO * 0.32 + TOPT * 0.32 + QTOP * 0.32 + 2330.TW * 0.04
    "股": [
        ("IOO", 0.32),
        ("TOPT", 0.32),
        ("QTOP", 0.32),
        ("2330.TW", 0.04),
    ],
    # 金 = GLDM * 0.90 + IBIT * 0.10
    "金": [
        ("GLDM", 0.90),
        ("IBIT", 0.10),
    ],
    # 避 = avg(DBMF, KMLM, CTA)
    "避": [
        ("DBMF", 1.0 / 3.0),
        ("KMLM", 1.0 / 3.0),
        ("CTA", 1.0 / 3.0),
    ],
    # 債 = SGOV 100% (fixed income)
    "債": [
        ("SGOV", 1.0),
    ],
}

ZERO_PORTFOLIO_FORMULA_LABELS: dict[str, str] = {
    "股": "(IOO + TOPT + QTOP) / 3 * 0.96 + 2330.TW * 0.04",
    "金": "GLDM * 0.90 + IBIT * 0.10",
    "避": "(DBMF + KMLM + CTA) / 3",
    "債": "(ZROZ + BIL + IEF + TLT) / 4",
}

# Crypto tickers we always pull (additive; never removed from the doc).
CRYPTO_TICKERS: tuple[str, ...] = ("BTC-USD", "ETH-USD")

FX_CACHE = Path.home() / ".claude" / "cache" / "fx_rates.json"
FX_CACHE_TTL_SECONDS = 3600  # 1 hour

TAIPEI = ZoneInfo("Asia/Taipei")

# Yahoo suffix → native currency for that exchange.
# Tickers without a suffix default to USD. `GBX` = London pence (1/100 GBP).
SUFFIX_CURRENCY: dict[str, str] = {
    "KS": "KRW",   # Korea (KOSPI)
    "KQ": "KRW",   # Korea (KOSDAQ)
    "SR": "SAR",   # Saudi Arabia (Tadawul)
    "HK": "HKD",   # Hong Kong
    "T": "JPY",    # Tokyo
    "TW": "TWD",   # Taiwan
    "TWO": "TWD",  # Taiwan OTC
    "L": "GBX",    # London (pence)
    "DE": "EUR",   # Xetra
    "F": "EUR",    # Frankfurt
    "PA": "EUR",   # Paris
    "AS": "EUR",   # Amsterdam
    "MI": "EUR",   # Milan
    "MC": "EUR",   # Madrid
    "BR": "EUR",   # Brussels
    "LS": "EUR",   # Lisbon
    "VI": "EUR",   # Vienna
    "HE": "EUR",   # Helsinki
    "IR": "EUR",   # Dublin
    "SW": "CHF",   # SIX Swiss
    "VX": "CHF",   # SIX (legacy)
    "TO": "CAD",   # Toronto
    "V": "CAD",    # TSX Venture
    "AX": "AUD",   # ASX
    "NZ": "NZD",   # New Zealand
    "SA": "BRL",   # B3 Brazil
    "MX": "MXN",   # Mexico
    "BK": "THB",   # Thailand
    "JK": "IDR",   # Indonesia
    "KL": "MYR",   # Malaysia
    "SI": "SGD",   # Singapore
    "BO": "INR",   # Bombay
    "NS": "INR",   # NSE India
    "ST": "SEK",   # Stockholm
    "CO": "DKK",   # Copenhagen
    "OL": "NOK",   # Oslo
    "WA": "PLN",   # Warsaw
    "PR": "CZK",   # Prague
    "JO": "ZAR",   # Johannesburg
    "IS": "TRY",   # Istanbul
    "TA": "ILS",   # Tel Aviv
    "SN": "CLP",   # Santiago
    "BA": "ARS",   # Buenos Aires
}

# Default big-cap tickers used only if the target file is completely empty.
DEFAULT_TICKERS: tuple[str, ...] = (
    "NVDA", "AAPL", "GOOG", "MSFT", "AMZN",
    "TSM", "AVGO", "META", "TSLA", "BRK-B",
)

# --- Logging -------------------------------------------------------------

logger = logging.getLogger("market_updater")
logger.setLevel(logging.INFO)
# Ensure parent dir exists before we attach the handler.
RESULTS.mkdir(parents=True, exist_ok=True)
_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
)
logger.addHandler(_handler)
logger.propagate = False


# --- Helpers -------------------------------------------------------------

def taipei_now_iso() -> str:
    """Taipei timestamp matching the format used by build_finance_dashboards."""
    return datetime.now(TAIPEI).strftime("%Y-%m-%d %H:%M:%S (Taipei, UTC+8)")


def read_marketcap() -> dict[str, Any]:
    if not MARKETCAP_JSON.exists():
        return {}
    try:
        return json.loads(MARKETCAP_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.error("Failed to read %s: %s", MARKETCAP_JSON, exc)
        return {}


def write_marketcap_atomic(payload: dict[str, Any]) -> None:
    """Write JSON atomically — temp file + os.replace — so a partial write can
    never corrupt the file that the MC server is polling."""
    MARKETCAP_JSON.parent.mkdir(parents=True, exist_ok=True)
    tmp = MARKETCAP_JSON.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    os.replace(tmp, MARKETCAP_JSON)


def ticker_buckets(doc: dict[str, Any]) -> list[list[dict[str, Any]]]:
    """Return every list-of-dict bucket inside the marketcap JSON that may
    carry a `symbol` + `price_usd` — so the updater can walk them uniformly."""
    buckets: list[list[dict[str, Any]]] = []
    for key in ("top10", "weekly_gainers", "weekly_losers", "owned_in_top200"):
        bucket = doc.get(key)
        if isinstance(bucket, list):
            buckets.append(bucket)
    return buckets


def collect_symbols(doc: dict[str, Any]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for bucket in ticker_buckets(doc):
        for entry in bucket:
            sym = (entry or {}).get("symbol")
            if isinstance(sym, str):
                s = sym.strip()
                if s and s not in seen:
                    seen.add(s)
                    ordered.append(s)
    return ordered


# --- Currency / FX -------------------------------------------------------

def detect_currency(symbol: str) -> str:
    """Return the native currency for a Yahoo-style ticker.

    Defaults to USD for unsuffixed symbols (NYSE / NASDAQ) and for suffixes
    we don't explicitly know.
    """
    s = symbol.strip().upper()
    if "." not in s:
        return "USD"
    suffix = s.rsplit(".", 1)[1]
    return SUFFIX_CURRENCY.get(suffix, "USD")


def _read_fx_cache() -> dict[str, Any]:
    if not FX_CACHE.exists():
        return {}
    try:
        return json.loads(FX_CACHE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.debug("fx cache read failed: %s", exc)
        return {}


def _write_fx_cache(cache: dict[str, Any]) -> None:
    try:
        FX_CACHE.parent.mkdir(parents=True, exist_ok=True)
        tmp = FX_CACHE.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(cache, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        os.replace(tmp, FX_CACHE)
    except OSError as exc:
        logger.debug("fx cache write failed: %s", exc)


def _yf_fx_rate(currency: str) -> float | None:
    """Fetch `<CCY>USD=X` via yfinance → float USD per 1 unit of `currency`."""
    try:
        import yfinance as yf  # type: ignore[import-untyped]
    except Exception as exc:  # pragma: no cover - missing dep
        logger.warning("yfinance import failed: %s", exc)
        return None
    pair = f"{currency}USD=X"
    try:
        ticker = yf.Ticker(pair)
        hist = ticker.history(period="5d", auto_adjust=False)
        if hist is None or len(hist) == 0:
            return None
        rate = float(hist["Close"].iloc[-1])
        if rate <= 0:
            return None
        return rate
    except Exception as exc:
        logger.debug("yfinance FX fetch failed for %s: %s", pair, exc)
        return None


def fetch_fx_rates(currencies: Iterable[str]) -> dict[str, float]:
    """Return dict[currency → USD_per_unit] using 1h file cache.

    USD → 1.0 always. GBX → 0.01 × GBP (pence). Unknown currencies map to
    None (caller must treat None as missing FX).
    """
    now = time.time()
    cache = _read_fx_cache()
    rates: dict[str, float] = {"USD": 1.0}
    touched = False

    unique = {c for c in currencies if c and c != "USD"}

    for ccy in sorted(unique):
        # GBX = pence sterling; derived from GBP.
        if ccy == "GBX":
            gbp = _rate_from_cache_or_fetch("GBP", cache, now)
            if gbp is not None:
                rates["GBX"] = gbp / 100.0
            continue
        rate = _rate_from_cache_or_fetch(ccy, cache, now)
        if rate is not None:
            rates[ccy] = rate
        touched = True

    if touched:
        _write_fx_cache(cache)
    return rates


def _rate_from_cache_or_fetch(
    ccy: str, cache: dict[str, Any], now: float
) -> float | None:
    """Helper: return cached rate if fresh, else fetch + update cache."""
    entry = cache.get(ccy)
    if (
        isinstance(entry, dict)
        and isinstance(entry.get("rate"), (int, float))
        and isinstance(entry.get("ts"), (int, float))
        and now - float(entry["ts"]) < FX_CACHE_TTL_SECONDS
    ):
        return float(entry["rate"])

    rate = _yf_fx_rate(ccy)
    if rate is not None:
        cache[ccy] = {"rate": rate, "ts": now}
        logger.info("fx %s→USD = %.6f (fresh)", ccy, rate)
        return rate

    # Fetch failed — fall back to stale cached value if we have one.
    if isinstance(entry, dict) and isinstance(entry.get("rate"), (int, float)):
        logger.warning("fx %s→USD fetch failed, using stale cache", ccy)
        return float(entry["rate"])
    logger.warning("fx %s→USD unavailable (no fresh fetch, no cache)", ccy)
    return None


# --- Price sources -------------------------------------------------------

def _yf_price(symbol: str) -> float | None:
    """Primary: yfinance.Ticker.history(period='1d') -> last close."""
    try:
        import yfinance as yf  # type: ignore[import-untyped]
    except Exception as exc:  # pragma: no cover - missing dep
        logger.warning("yfinance import failed: %s", exc)
        return None
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d", auto_adjust=False)
        if hist is None or len(hist) == 0:
            return None
        close = float(hist["Close"].iloc[-1])
        if close <= 0:
            return None
        return close
    except Exception as exc:
        logger.debug("yfinance failed for %s: %s", symbol, exc)
        return None


def _stooq_symbol(symbol: str) -> str | None:
    """Map a Yahoo-style symbol to a Stooq symbol.

    Stooq covers US tickers as `AAPL.US`; foreign suffixes (`.KS`, `.SR`,
    Hong Kong, etc.) are not reliably supported so we skip them and let
    yfinance be the only source for those.
    """
    s = symbol.strip().upper()
    if not s:
        return None
    if "." in s:
        return None  # non-US — skip stooq
    if "-" in s:  # e.g. BRK-B
        return None
    return f"{s.lower()}.us"


def _stooq_price(symbol: str) -> float | None:
    """Fallback: Stooq free CSV quote feed. No auth required."""
    stq = _stooq_symbol(symbol)
    if stq is None:
        return None
    url = f"https://stooq.com/q/l/?s={stq}&f=sd2t2ohlcv&h&e=csv"
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "mc-market-updater/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:  # noqa: S310
            raw = resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError) as exc:
        logger.debug("stooq fetch failed for %s: %s", symbol, exc)
        return None
    try:
        reader = csv.DictReader(io.StringIO(raw))
        row = next(reader, None)
        if not row:
            return None
        close_raw = row.get("Close")
        if not close_raw or close_raw in {"N/D", "-"}:
            return None
        close = float(close_raw)
        return close if close > 0 else None
    except (ValueError, csv.Error) as exc:
        logger.debug("stooq parse failed for %s: %s", symbol, exc)
        return None


def fetch_price(symbol: str) -> float | None:
    """Try yfinance first, then Stooq. Returns None on total failure."""
    price = _yf_price(symbol)
    if price is not None:
        return price
    return _stooq_price(symbol)


def fetch_prices(symbols: Iterable[str]) -> dict[str, float]:
    """Return dict[symbol → native-currency price]."""
    prices: dict[str, float] = {}
    for sym in symbols:
        price = fetch_price(sym)
        if price is not None:
            prices[sym] = round(price, 4)
    return prices


def _yf_weekly_history(symbol: str) -> tuple[float | None, float | None]:
    """Return (latest_close, seven_day_ago_close) via yfinance history.

    Used to compute a weekly % change for crypto and watchlist entries so
    the dashboard can color them green/red. Returns (None, None) on failure.
    """
    try:
        import yfinance as yf  # type: ignore[import-untyped]
    except Exception as exc:  # pragma: no cover - missing dep
        logger.warning("yfinance import failed: %s", exc)
        return (None, None)
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="7d", auto_adjust=False)
        if hist is None or len(hist) == 0:
            return (None, None)
        latest = float(hist["Close"].iloc[-1])
        earliest = float(hist["Close"].iloc[0])
        if latest <= 0 or earliest <= 0:
            return (None, None)
        return (latest, earliest)
    except Exception as exc:
        logger.debug("yfinance history failed for %s: %s", symbol, exc)
        return (None, None)


def _weekly_pct(latest: float | None, earliest: float | None) -> float | None:
    """Compute percent change from earliest → latest close. None on bad input."""
    if latest is None or earliest is None or earliest == 0:
        return None
    try:
        return round((latest - earliest) / earliest * 100.0, 4)
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def fetch_crypto_bucket(stamp: str) -> list[dict[str, Any]]:
    """Fetch BTC / ETH prices + weekly change, return crypto bucket entries.

    Each entry matches the watchlist shape for easy UI reuse:
      {symbol, label, price_usd, price_native, currency, weekly_pct,
       category, updated_at}
    """
    labels = {
        "BTC-USD": "Bitcoin",
        "ETH-USD": "Ethereum",
    }
    bucket: list[dict[str, Any]] = []
    for sym in CRYPTO_TICKERS:
        latest, earliest = _yf_weekly_history(sym)
        if latest is None:
            # Fall back to single-day close so we at least have a price.
            fallback = _yf_price(sym)
            if fallback is None:
                logger.warning("crypto fetch failed for %s", sym)
                continue
            latest = fallback
        pct = _weekly_pct(latest, earliest)
        entry: dict[str, Any] = {
            "symbol": sym,
            "label": labels.get(sym, sym),
            "price_usd": round(latest, 4),
            "price_native": round(latest, 4),
            "currency": "USD",
            "weekly_pct_recent": pct,
            "category": "crypto",
            "updated_at": stamp,
        }
        bucket.append(entry)
        logger.info(
            "crypto %s price=%.4f weekly_pct=%s",
            sym,
            latest,
            f"{pct:.2f}" if pct is not None else "n/a",
        )
    return bucket


def _yf_history_range(
    symbol: str, period: str = WATCHLIST_HISTORY_PERIOD
) -> list[dict[str, Any]]:
    """Return ``period`` of daily closes as [{date, close}, ...].

    Used by /api/watchlist/history so the 總覽 page can render 3M-60M
    charts without hitting yfinance on every request. Empty list on failure.

    All tickers (bonds and equities/commodities alike) use
    ``auto_adjust=True`` so the returned ``Close`` series reflects splits,
    dividends, and distributions. This is especially important for bonds
    (ZROZ/BIL/IEF/TLT) whose raw price would otherwise ignore coupon
    reinvestment and make the 避/債 composites look flat.
    """
    try:
        import yfinance as yf  # type: ignore[import-untyped]
    except Exception as exc:  # pragma: no cover - missing dep
        logger.warning("yfinance import failed for history %s: %s", symbol, exc)
        return []
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval="1d", auto_adjust=True)
        if hist is None or len(hist) == 0:
            return []
        out: list[dict[str, Any]] = []
        for idx, row in hist.iterrows():
            try:
                close = float(row["Close"])
            except (TypeError, ValueError, KeyError):
                continue
            if close <= 0:
                continue
            try:
                date_str = idx.strftime("%Y-%m-%d")
            except Exception:
                date_str = str(idx)[:10]
            out.append({"date": date_str, "close": round(close, 4)})
        return out
    except Exception as exc:
        logger.debug(
            "yfinance %s history failed for %s: %s", period, symbol, exc
        )
        return []


# Backward-compat alias — older call sites still reference _yf_history_1y.
def _yf_history_1y(symbol: str) -> list[dict[str, Any]]:
    return _yf_history_range(symbol, period="1y")


def _watchlist_history_fresh() -> bool:
    """Return True if watchlist_history.json is younger than MAX_AGE."""
    if not WATCHLIST_HISTORY_JSON.exists():
        return False
    try:
        age = time.time() - WATCHLIST_HISTORY_JSON.stat().st_mtime
    except OSError:
        return False
    return age < WATCHLIST_HISTORY_MAX_AGE_S


def update_watchlist_history(
    watchlist_entries: list[dict[str, Any]], force: bool = False
) -> int:
    """Refresh watchlist_history.json if stale. Returns number of symbols
    successfully fetched (0 on skip).
    """
    if not watchlist_entries:
        return 0
    if not force and _watchlist_history_fresh():
        logger.info(
            "watchlist history still fresh — skipping refetch (age < %ds)",
            WATCHLIST_HISTORY_MAX_AGE_S,
        )
        return 0
    payload: dict[str, Any] = {
        "generated_at": taipei_now_iso(),
        "period": WATCHLIST_HISTORY_PERIOD,
        "tickers": {},
    }
    ok_count = 0
    for entry in watchlist_entries:
        symbol = entry.get("symbol")
        if not symbol:
            continue
        series = _yf_history_range(str(symbol), period=WATCHLIST_HISTORY_PERIOD)
        if not series:
            # Don't fail the whole run — unresolved tickers (DBMF/CTA etc.
            # on some yfinance versions) get logged and skipped.
            logger.warning(
                "watchlist history empty for %s (skipping, run continues)",
                symbol,
            )
            continue
        payload["tickers"][str(symbol)] = {
            "label": entry.get("label", symbol),
            "currency": entry.get("currency", "USD"),
            "category": entry.get("category", ""),
            "series": series,
        }
        ok_count += 1
        logger.info(
            "watchlist history %s: %d daily closes", symbol, len(series)
        )
    try:
        tmp = WATCHLIST_HISTORY_JSON.with_suffix(".json.tmp")
        tmp.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        tmp.replace(WATCHLIST_HISTORY_JSON)
    except OSError as exc:
        logger.error("watchlist history write failed: %s", exc)
        return 0

    # Composite zero-portfolio indices derived from the same cache.
    try:
        composite_count = build_zero_portfolio_history(payload)
        if composite_count:
            logger.info(
                "zero_portfolio_history.json built: %d indices",
                composite_count,
            )
    except Exception as exc:  # noqa: BLE001
        logger.error("zero portfolio build failed: %s", exc)

    return ok_count


def _forward_fill_series(series: list[dict[str, Any]]) -> dict[str, float]:
    """Convert a [{date, close}] series into a dense date → close map
    suitable for aligning with other tickers. No forward-fill yet; done
    at alignment time when we know the full date index.
    """
    out: dict[str, float] = {}
    for row in series:
        try:
            date_str = str(row.get("date") or "")
            close = float(row.get("close") or 0.0)
        except (TypeError, ValueError):
            continue
        if not date_str or close <= 0:
            continue
        out[date_str] = close
    return out


def build_zero_portfolio_history(
    watchlist_payload: dict[str, Any],
) -> int:
    """Build results/zero_portfolio_history.json from the cached watchlist.

    For each composite (股/金/避/債):
      1. Look up component tickers in ``watchlist_payload['tickers']``.
      2. Forward-fill each ticker's closes onto the union date index.
      3. Drop any component entirely missing for this run (warning logged).
      4. Re-normalise the remaining weights to sum to 1.0.
      5. Compute weighted-sum series.
      6. Normalise the output to start at 100 on the earliest common date.
    Returns the number of composites successfully built.
    """
    tickers_payload = watchlist_payload.get("tickers") or {}
    if not isinstance(tickers_payload, dict):
        return 0

    # Gather per-ticker date → close maps for every ticker referenced by
    # any formula so we only materialise things once.
    referenced: set[str] = set()
    for spec in ZERO_PORTFOLIO_FORMULAS.values():
        for sym, _w in spec:
            referenced.add(sym)

    per_ticker: dict[str, dict[str, float]] = {}
    for sym in referenced:
        entry = tickers_payload.get(sym)
        if not isinstance(entry, dict):
            continue
        series = entry.get("series")
        if not isinstance(series, list):
            continue
        dense = _forward_fill_series(series)
        if dense:
            per_ticker[sym] = dense

    indices_out: dict[str, list[dict[str, Any]]] = {}
    latest_out: dict[str, dict[str, Any]] = {}

    for label, components in ZERO_PORTFOLIO_FORMULAS.items():
        # Filter out missing components
        present = [(sym, w) for sym, w in components if sym in per_ticker]
        if not present:
            logger.warning(
                "zero portfolio %s: no components available, skipping", label
            )
            continue
        missing = [sym for sym, _w in components if sym not in per_ticker]
        if missing:
            logger.warning(
                "zero portfolio %s: missing %s — re-normalising weights",
                label,
                ",".join(missing),
            )
        total_w = sum(w for _sym, w in present)
        if total_w <= 0:
            continue
        norm_components = [(sym, w / total_w) for sym, w in present]

        # Union of dates for present components.
        all_dates: set[str] = set()
        for sym, _w in norm_components:
            all_dates.update(per_ticker[sym].keys())
        sorted_dates = sorted(all_dates)

        # Forward-fill each component onto the sorted date index.
        ffilled: dict[str, list[float]] = {}
        for sym, _w in norm_components:
            dense = per_ticker[sym]
            last_val = 0.0
            col: list[float] = []
            for d in sorted_dates:
                v = dense.get(d)
                if v is not None and v > 0:
                    last_val = v
                col.append(last_val)
            ffilled[sym] = col

        # Trim leading zeros (dates before all components have any data).
        start_i = 0
        for i in range(len(sorted_dates)):
            if all(ffilled[sym][i] > 0 for sym, _w in norm_components):
                start_i = i
                break
        else:
            continue

        trimmed_dates = sorted_dates[start_i:]
        raw_values: list[float] = []
        for i, _d in enumerate(trimmed_dates):
            abs_i = i + start_i
            total = 0.0
            for sym, w in norm_components:
                total += ffilled[sym][abs_i] * w
            raw_values.append(total)

        if not raw_values or raw_values[0] <= 0:
            continue

        base = raw_values[0]
        series_out = [
            {"date": trimmed_dates[i], "value": round(raw_values[i] / base * 100.0, 4)}
            for i in range(len(trimmed_dates))
        ]
        indices_out[label] = series_out
        if series_out:
            latest_out[label] = {
                "date": series_out[-1]["date"],
                "value": series_out[-1]["value"],
                "components": [
                    {"symbol": sym, "weight": round(w, 6)}
                    for sym, w in norm_components
                ],
                "missing": missing,
            }

    if not indices_out:
        return 0

    payload = {
        "generated_at": taipei_now_iso(),
        "period": WATCHLIST_HISTORY_PERIOD,
        "formulas": ZERO_PORTFOLIO_FORMULA_LABELS,
        "latest": latest_out,
        "indices": indices_out,
    }
    try:
        tmp = ZERO_PORTFOLIO_JSON.with_suffix(".json.tmp")
        tmp.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        tmp.replace(ZERO_PORTFOLIO_JSON)
    except OSError as exc:
        logger.error("zero portfolio write failed: %s", exc)
        return 0
    return len(indices_out)


def load_watchlist() -> list[dict[str, Any]]:
    """Load watchlist.yaml. Returns [] if missing / unparseable."""
    if not WATCHLIST_YAML.exists():
        logger.info("watchlist.yaml not found at %s", WATCHLIST_YAML)
        return []
    try:
        import yaml  # type: ignore[import-untyped]
    except Exception as exc:  # pragma: no cover - missing dep
        logger.warning("PyYAML import failed: %s", exc)
        return []
    try:
        raw = yaml.safe_load(WATCHLIST_YAML.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        logger.error("watchlist parse failed: %s", exc)
        return []
    if not isinstance(raw, dict):
        return []
    tickers = raw.get("tickers")
    if not isinstance(tickers, list):
        return []
    cleaned: list[dict[str, Any]] = []
    for entry in tickers:
        if not isinstance(entry, dict):
            continue
        sym = str(entry.get("symbol") or "").strip()
        if not sym:
            continue
        cleaned.append(
            {
                "symbol": sym,
                "label": str(entry.get("label") or sym),
                "currency": str(entry.get("currency") or detect_currency(sym)),
                "category": str(entry.get("category") or "stock"),
            }
        )
    return cleaned


def fetch_watchlist_bucket(
    watchlist: list[dict[str, Any]],
    fx_rates: dict[str, float],
    stamp: str,
) -> list[dict[str, Any]]:
    """For every watchlist entry fetch native price + weekly % change and
    convert to USD via the shared FX cache."""
    bucket: list[dict[str, Any]] = []
    for wl in watchlist:
        sym = wl["symbol"]
        latest, earliest = _yf_weekly_history(sym)
        if latest is None:
            # Fall back to last-close so at least one price is available.
            latest = _yf_price(sym)
        if latest is None:
            logger.warning("watchlist fetch failed for %s", sym)
            bucket.append(
                {
                    "symbol": sym,
                    "label": wl["label"],
                    "price_native": None,
                    "price_usd": None,
                    "currency": wl["currency"],
                    "weekly_pct": None,
                    "category": wl["category"],
                    "updated_at": stamp,
                    "stale": True,
                }
            )
            continue
        currency = wl["currency"]
        fx = fx_rates.get(currency)
        price_usd: float | None
        if fx is None:
            price_usd = None
            logger.warning(
                "watchlist %s: FX %s→USD missing, price_usd=null",
                sym,
                currency,
            )
        else:
            price_usd = round(latest * fx, 4)
        pct = _weekly_pct(latest, earliest)
        bucket.append(
            {
                "symbol": sym,
                "label": wl["label"],
                "price_native": round(latest, 4),
                "price_usd": price_usd,
                "currency": currency,
                "weekly_pct": pct,
                "category": wl["category"],
                "updated_at": stamp,
            }
        )
        logger.info(
            "watchlist %s native=%.4f usd=%s weekly_pct=%s",
            sym,
            latest,
            f"{price_usd:.4f}" if price_usd is not None else "n/a",
            f"{pct:.2f}" if pct is not None else "n/a",
        )
    return bucket


# --- Apply ---------------------------------------------------------------

def apply_prices(
    doc: dict[str, Any],
    prices: dict[str, float],
    fx_rates: dict[str, float],
) -> int:
    """Mutate every bucket in-place, return count of updated entries.

    For each ticker we now store three fields additively:
      * `price_native` — raw exchange price
      * `currency`     — ISO code detected from suffix
      * `price_usd`    — converted to USD (None + `stale_fx=True` if FX missing)

    Original schema keys are preserved so the dashboard keeps working.
    """
    updated = 0
    for bucket in ticker_buckets(doc):
        for entry in bucket:
            sym = (entry or {}).get("symbol")
            if not isinstance(sym, str) or sym not in prices:
                continue
            native_price = prices[sym]
            currency = detect_currency(sym)
            entry["price_native"] = native_price
            entry["currency"] = currency

            fx = fx_rates.get(currency)
            if fx is None:
                # FX unavailable — do not corrupt price_usd with native value.
                entry["price_usd"] = None
                entry["stale_fx"] = True
                logger.warning(
                    "%s: FX %s→USD missing, price_usd=null", sym, currency
                )
            else:
                usd_price = round(native_price * fx, 4)
                entry["price_usd"] = usd_price
                # Clear any prior stale marker.
                if "stale_fx" in entry:
                    entry.pop("stale_fx", None)
            updated += 1
    return updated


def build_stub(symbols: Iterable[str]) -> dict[str, Any]:
    """If the target file is missing or empty, scaffold a minimal doc so the
    dashboard shows *something* instead of 404ing."""
    top10 = [
        {
            "rank": i + 1,
            "name": s,
            "symbol": s,
            "marketcap": None,
            "price_usd": None,
            "country": "",
            "sector": "",
            "industry": "",
            "weekly_pct_recent": None,
            "weekly_pct_prev": None,
        }
        for i, s in enumerate(symbols)
    ]
    return {
        "generated_at": taipei_now_iso(),
        "top10": top10,
        "top200_count": len(top10),
        "weekly_gainers": [],
        "weekly_losers": [],
        "sector_summary": [],
        "etf_summary": [],
        "owned_in_top200": [],
    }


# --- Main ----------------------------------------------------------------

def run() -> int:
    logger.info("=== market_updater run start ===")
    doc = read_marketcap()

    if not doc or not collect_symbols(doc):
        logger.warning(
            "%s missing or empty — building default stub from DEFAULT_TICKERS",
            MARKETCAP_JSON.name,
        )
        doc = build_stub(DEFAULT_TICKERS)

    symbols = collect_symbols(doc)
    logger.info("collected %d distinct symbols: %s", len(symbols), ",".join(symbols))

    try:
        prices = fetch_prices(symbols)
    except Exception as exc:  # pragma: no cover - total network failure
        logger.error("price fetch aborted: %s", exc)
        doc["updated_at"] = taipei_now_iso()
        doc["stale"] = True
        write_marketcap_atomic(doc)
        logger.info("=== market_updater run end (stale) ===")
        return 1

    if not prices:
        logger.warning(
            "no prices retrieved — leaving price_usd fields untouched, "
            "stamping updated_at with stale=true"
        )
        doc["updated_at"] = taipei_now_iso()
        doc["stale"] = True
        write_marketcap_atomic(doc)
        logger.info("=== market_updater run end (stale) ===")
        return 1

    # Load watchlist early so its currencies are included in the FX pass.
    watchlist_entries = load_watchlist()
    if watchlist_entries:
        logger.info(
            "watchlist loaded: %d entries (%s)",
            len(watchlist_entries),
            ",".join(e["symbol"] for e in watchlist_entries),
        )

    # Detect the set of currencies we need FX rates for before converting.
    needed_currencies: set[str] = {detect_currency(s) for s in symbols}
    needed_currencies.update(e["currency"] for e in watchlist_entries)
    logger.info(
        "currencies needed: %s", ",".join(sorted(needed_currencies))
    )
    fx_rates = fetch_fx_rates(needed_currencies)
    logger.info(
        "fx rates resolved: %s",
        ", ".join(f"{k}={v:.6f}" for k, v in sorted(fx_rates.items())),
    )

    updated = apply_prices(doc, prices, fx_rates)
    stamp = taipei_now_iso()

    # Additive: populate crypto + watchlist buckets.
    crypto_bucket = fetch_crypto_bucket(stamp)
    if crypto_bucket:
        doc["crypto"] = crypto_bucket
    watchlist_bucket = fetch_watchlist_bucket(
        watchlist_entries, fx_rates, stamp
    )
    if watchlist_bucket:
        doc["watchlist"] = watchlist_bucket

    # Refresh 1-year daily history cache for charts (cheap: runs ~once/day).
    try:
        refreshed = update_watchlist_history(watchlist_entries)
        if refreshed:
            logger.info("watchlist_history.json refreshed: %d tickers", refreshed)
    except Exception as exc:  # noqa: BLE001
        logger.error("watchlist history refresh failed: %s", exc)

    doc["updated_at"] = stamp
    doc["stale"] = False
    doc["price_source"] = "yfinance+stooq"
    doc["fx_rates"] = {k: round(v, 6) for k, v in fx_rates.items()}

    write_marketcap_atomic(doc)

    logger.info(
        "updated %d / %d symbols: %s",
        len(prices),
        len(symbols),
        ", ".join(f"{k}={v}" for k, v in prices.items()),
    )
    logger.info("updated_entries_in_buckets=%d", updated)
    logger.info("=== market_updater run end (ok) ===")
    return 0


if __name__ == "__main__":
    sys.exit(run())
