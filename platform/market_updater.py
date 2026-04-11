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
LOG_FILE = RESULTS / "market_updater.log"

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

    # Detect the set of currencies we need FX rates for before converting.
    needed_currencies: set[str] = {detect_currency(s) for s in symbols}
    logger.info(
        "currencies needed: %s", ",".join(sorted(needed_currencies))
    )
    fx_rates = fetch_fx_rates(needed_currencies)
    logger.info(
        "fx rates resolved: %s",
        ", ".join(f"{k}={v:.6f}" for k, v in sorted(fx_rates.items())),
    )

    updated = apply_prices(doc, prices, fx_rates)
    doc["updated_at"] = taipei_now_iso()
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
