#!/usr/bin/env python3
"""balance_sheet_builder.py

Successor to the hand-maintained AssetManagement Google Sheet tab.

Reads:
  - results/holdings.yaml (Edward's single source of truth — cash, positions,
    liabilities) with a JSON fallback at results/holdings.json.
  - results/finance_marketcap.json (fresh prices from market_updater every
    30 min).
  - yfinance as a fallback for any tickers / FX pairs not present in the
    marketcap cache.

Writes:
  - results/finance_networth.json (schema matches what /api/finance and
    finance.html expect; adds a `computed_from_holdings: true` marker and
    a `positions_detail` section.)
  - results/balance_sheet_builder.log

Runs every 30 min via Windows Task Scheduler (mc_balance_sheet).

Timezone: Asia/Taipei on every user-facing timestamp.
Edward axiom: 看導數不看水平 — we report 7d/30d/ytd deltas, not just levels.
"""
from __future__ import annotations

import json
import logging
import sys
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

TPE = ZoneInfo("Asia/Taipei")

REPO = Path("C:/Users/admin/workspace/digital-immortality")
RESULTS = REPO / "results"
HOLDINGS_YAML = RESULTS / "holdings.yaml"
HOLDINGS_JSON = RESULTS / "holdings.json"
MARKETCAP = RESULTS / "finance_marketcap.json"
NETWORTH_OUT = RESULTS / "finance_networth.json"
LOG_FILE = RESULTS / "balance_sheet_builder.log"

FIRE_TARGET_TWD = 21_000_000

# FX in-process cache: ccy -> (rate_to_base, fetched_at_epoch)
_FX_CACHE: dict[str, tuple[float, float]] = {}
FX_TTL_SEC = 60 * 60


def _configure_logging() -> logging.Logger:
    RESULTS.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("balance_sheet_builder")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    return logger


log = _configure_logging()


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------


def now_tpe() -> datetime:
    return datetime.now(TPE)


def now_iso_tpe() -> str:
    return now_tpe().isoformat()


def now_label_tpe() -> str:
    return now_tpe().strftime("%Y-%m-%d %H:%M (Taipei, UTC+8)")


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class CashEntry:
    account: str
    currency: str
    balance: float


@dataclass
class Position:
    ticker: str
    qty: float
    cost_basis: float
    currency: str
    category: str
    account: str = ""
    note: str = ""
    # --- extensions for non-vanilla positions ---
    name: str = ""
    subtype: str = ""                       # "" | "gross_with_held_for_others"
    qty_gross: float = 0.0
    qty_held_for_others: float = 0.0
    held_for: list[dict] = field(default_factory=list)
    manual_price: dict | None = None        # {value, currency, as_of, source}
    has_cost_basis: bool = True
    # Cost-history extensions (used by gross_with_held_for_others positions
    # that track investment tranches rather than a per-share cost_basis).
    total_cost_native: float = 0.0
    avg_cost_per_share_native: float = 0.0
    cost_history: list[dict] = field(default_factory=list)
    accounting_basis: str = ""
    # --- computed fields ---
    price_native: float | None = None
    price_source: str = ""
    market_value_native: float = 0.0
    market_value_base: float = 0.0
    unrealized_pnl_native: float = 0.0
    unrealized_pnl_base: float = 0.0
    unrealized_pnl_pct: float | None = None


@dataclass
class Liability:
    name: str
    balance: float
    currency: str = "TWD"
    type: str = "static"                    # static | monthly_accrual | amortization
    note: str = ""
    # monthly_accrual fields
    start_date: str = ""
    monthly_amount: float = 0.0
    total_months: int = 0
    rate: float | None = None
    interest_only_months: int = 0
    # amortization fields
    principal: float = 0.0
    monthly_payment: float = 0.0
    # meta
    source: str = ""                        # e.g. "held_for_others"
    breakdown: list[dict] = field(default_factory=list)


@dataclass
class Holdings:
    as_of: str
    base_currency: str
    cash: list[CashEntry] = field(default_factory=list)
    positions: list[Position] = field(default_factory=list)
    liabilities: list[Liability] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------


def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        if v is None or v == "":
            return default
        return float(v)
    except (TypeError, ValueError):
        return default


def _safe_str(v: Any, default: str = "") -> str:
    if v is None:
        return default
    return str(v).strip()


def load_holdings() -> Holdings:
    raw: dict | None = None
    if HOLDINGS_YAML.exists():
        try:
            import yaml  # type: ignore
            raw = yaml.safe_load(HOLDINGS_YAML.read_text(encoding="utf-8"))
            log.info("loaded holdings.yaml")
        except ImportError:
            log.warning("PyYAML not installed — falling back to holdings.json")
            raw = None
        except Exception as exc:
            log.error("failed to parse holdings.yaml: %s", exc)
            raw = None
    if raw is None and HOLDINGS_JSON.exists():
        try:
            raw = json.loads(HOLDINGS_JSON.read_text(encoding="utf-8"))
            log.info("loaded holdings.json")
        except Exception as exc:
            log.error("failed to parse holdings.json: %s", exc)
            raw = None
    if raw is None:
        log.warning("no holdings file found — using empty skeleton")
        raw = {}

    if not isinstance(raw, dict):
        raw = {}

    base = _safe_str(raw.get("base_currency"), "TWD").upper() or "TWD"
    as_of = _safe_str(raw.get("as_of"), now_tpe().strftime("%Y-%m-%d"))

    cash: list[CashEntry] = []
    for entry in raw.get("cash") or []:
        if not isinstance(entry, dict):
            continue
        cash.append(
            CashEntry(
                account=_safe_str(entry.get("account"), "cash"),
                currency=_safe_str(entry.get("currency"), base).upper() or base,
                balance=_safe_float(entry.get("balance")),
            )
        )

    positions: list[Position] = []
    for entry in raw.get("positions") or []:
        if not isinstance(entry, dict):
            continue
        subtype = _safe_str(entry.get("subtype"))
        ticker = _safe_str(entry.get("ticker"))
        name = _safe_str(entry.get("name"))
        # Vanilla positions must have a ticker; special subtypes may omit it.
        if not ticker and subtype != "gross_with_held_for_others":
            continue
        manual_price_raw = entry.get("manual_price")
        manual_price: dict | None = None
        if isinstance(manual_price_raw, dict):
            manual_price = {
                "value": _safe_float(manual_price_raw.get("value")),
                "currency": _safe_str(
                    manual_price_raw.get("currency"), base
                ).upper() or base,
                "as_of": _safe_str(manual_price_raw.get("as_of")),
                "source": _safe_str(manual_price_raw.get("source")),
            }
        held_for_raw = entry.get("held_for") or []
        held_for: list[dict] = []
        if isinstance(held_for_raw, list):
            for h in held_for_raw:
                if isinstance(h, dict):
                    held_for.append(
                        {
                            "name": _safe_str(h.get("name")),
                            "qty": _safe_float(h.get("qty")),
                        }
                    )
        has_cost_basis = "cost_basis" in entry and entry.get("cost_basis") not in (
            None,
            "",
        )
        cost_history_raw = entry.get("cost_history") or []
        cost_history: list[dict] = []
        if isinstance(cost_history_raw, list):
            for c in cost_history_raw:
                if isinstance(c, dict):
                    cost_history.append(
                        {
                            "date": _safe_str(c.get("date")),
                            "amount_twd": _safe_float(c.get("amount_twd")),
                            "shares_added": _safe_float(c.get("shares_added")),
                            "note": _safe_str(c.get("note")),
                            "dividend_reinvest_twd": _safe_float(
                                c.get("dividend_reinvest_twd")
                            ),
                        }
                    )
        positions.append(
            Position(
                ticker=ticker,
                qty=_safe_float(entry.get("qty")),
                cost_basis=_safe_float(entry.get("cost_basis")),
                currency=_safe_str(entry.get("currency"), base).upper() or base,
                category=_safe_str(entry.get("category"), "其他"),
                account=_safe_str(entry.get("account")),
                note=_safe_str(entry.get("note")),
                name=name,
                subtype=subtype,
                qty_gross=_safe_float(entry.get("qty_gross")),
                qty_held_for_others=_safe_float(entry.get("qty_held_for_others")),
                held_for=held_for,
                manual_price=manual_price,
                has_cost_basis=has_cost_basis,
                total_cost_native=_safe_float(entry.get("total_cost_twd")),
                avg_cost_per_share_native=_safe_float(
                    entry.get("avg_cost_per_share_twd")
                ),
                cost_history=cost_history,
                accounting_basis=_safe_str(entry.get("accounting_basis")),
            )
        )

    liabilities: list[Liability] = []
    for entry in raw.get("liabilities") or []:
        if not isinstance(entry, dict):
            continue
        li_type = _safe_str(entry.get("type"), "static") or "static"
        rate_raw = entry.get("rate")
        rate_val: float | None
        if rate_raw in (None, ""):
            rate_val = None
        else:
            rate_val = _safe_float(rate_raw)
        liabilities.append(
            Liability(
                name=_safe_str(entry.get("name"), "liability"),
                balance=_safe_float(entry.get("balance")),
                currency=_safe_str(entry.get("currency"), base).upper() or base,
                type=li_type,
                note=_safe_str(entry.get("note")),
                start_date=_safe_str(entry.get("start_date")),
                monthly_amount=_safe_float(entry.get("monthly_amount")),
                total_months=int(_safe_float(entry.get("total_months"))),
                rate=rate_val,
                interest_only_months=int(
                    _safe_float(entry.get("interest_only_months"))
                ),
                principal=_safe_float(entry.get("principal")),
                monthly_payment=_safe_float(entry.get("monthly_payment")),
            )
        )

    return Holdings(
        as_of=as_of,
        base_currency=base,
        cash=cash,
        positions=positions,
        liabilities=liabilities,
    )


def load_marketcap() -> dict:
    if not MARKETCAP.exists():
        return {}
    try:
        return json.loads(MARKETCAP.read_text(encoding="utf-8"))
    except Exception as exc:
        log.warning("failed to read marketcap json: %s", exc)
        return {}


# ---------------------------------------------------------------------------
# Price + FX resolution
# ---------------------------------------------------------------------------


def _index_marketcap_by_symbol(mc: dict) -> dict[str, dict]:
    idx: dict[str, dict] = {}
    for bucket_key in ("top10", "top200", "weekly_gainers", "weekly_losers", "owned_in_top200"):
        bucket = mc.get(bucket_key)
        if not isinstance(bucket, list):
            continue
        for e in bucket:
            if isinstance(e, dict):
                sym = _safe_str(e.get("symbol")).upper()
                if sym and sym not in idx:
                    idx[sym] = e
    return idx


def _yf_price(ticker: str) -> tuple[float | None, str]:
    try:
        import yfinance as yf  # type: ignore
    except ImportError:
        log.warning("yfinance not installed; cannot fetch %s", ticker)
        return None, ""
    try:
        t = yf.Ticker(ticker)
        fi = getattr(t, "fast_info", None)
        price: float | None = None
        if fi is not None:
            for key in ("last_price", "lastPrice", "regular_market_price"):
                try:
                    val = fi[key] if hasattr(fi, "__getitem__") else getattr(fi, key, None)
                except Exception:
                    val = None
                if val:
                    try:
                        price = float(val)
                        break
                    except (TypeError, ValueError):
                        continue
        if price is None:
            hist = t.history(period="5d", interval="1d", auto_adjust=False)
            if hist is not None and not hist.empty:
                price = float(hist["Close"].dropna().iloc[-1])
        if price:
            return price, "yfinance"
    except Exception as exc:
        log.warning("yfinance lookup failed for %s: %s", ticker, exc)
    return None, ""


def resolve_price(
    pos: Position, mc_index: dict[str, dict]
) -> tuple[float | None, str]:
    sym = pos.ticker.upper()
    entry = mc_index.get(sym)
    if entry:
        for key in ("price_native", "price_usd", "price"):
            val = entry.get(key)
            if val:
                try:
                    return float(val), f"marketcap:{key}"
                except (TypeError, ValueError):
                    continue
    return _yf_price(pos.ticker)


def get_fx_rate(currency: str, base: str) -> float:
    """Return the multiplier to convert 1 unit of `currency` into `base`."""
    currency = (currency or base).upper()
    base = (base or "TWD").upper()
    if currency == base:
        return 1.0
    # USDT pegged ~= USD for simplicity
    lookup = "USD" if currency == "USDT" else currency
    cache_key = f"{lookup}->{base}"
    now = time.time()
    cached = _FX_CACHE.get(cache_key)
    if cached and (now - cached[1]) < FX_TTL_SEC:
        return cached[0]
    rate: float | None = None
    try:
        import yfinance as yf  # type: ignore
        # Try direct pair: <from><to>=X
        pair = f"{lookup}{base}=X"
        t = yf.Ticker(pair)
        hist = t.history(period="5d", interval="1d", auto_adjust=False)
        if hist is not None and not hist.empty:
            rate = float(hist["Close"].dropna().iloc[-1])
        else:
            # Try inverse pair
            inv = f"{base}{lookup}=X"
            t2 = yf.Ticker(inv)
            hist2 = t2.history(period="5d", interval="1d", auto_adjust=False)
            if hist2 is not None and not hist2.empty:
                inv_rate = float(hist2["Close"].dropna().iloc[-1])
                if inv_rate:
                    rate = 1.0 / inv_rate
    except Exception as exc:
        log.warning("fx lookup failed %s -> %s: %s", lookup, base, exc)
    if rate is None:
        # Fallback static estimates (better than 0)
        fallback = {("USD", "TWD"): 32.0, ("USDT", "TWD"): 32.0}
        rate = fallback.get((lookup, base), 1.0)
        log.warning(
            "FX %s->%s unresolved, using fallback %.4f", lookup, base, rate
        )
    _FX_CACHE[cache_key] = (rate, now)
    return rate


# ---------------------------------------------------------------------------
# Liability evaluators (dynamic outstanding computation)
# ---------------------------------------------------------------------------


def _parse_iso_date(s: str) -> date | None:
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def _months_between(start: date, end: date) -> int:
    """Whole months elapsed from start to end (end >= start)."""
    if end < start:
        return 0
    months = (end.year - start.year) * 12 + (end.month - start.month)
    if end.day < start.day:
        months -= 1
    return max(months, 0)


def _eval_static_liability(li: Liability, today: date) -> float:
    """Static snapshot — returns the declared balance as-is."""
    return max(li.balance, 0.0)


def _eval_monthly_accrual(li: Liability, today: date) -> float:
    """Cumulative disbursements, capped at total_months * monthly_amount.

    Used e.g. for 爸爸借款: drawn 180k/month starting 2024-06-05 for 60 months.
    """
    start = _parse_iso_date(li.start_date)
    if start is None or li.monthly_amount <= 0:
        return max(li.balance, 0.0)
    # Calendar months elapsed (no +1). Edward confirmed 2024-06-05 -> 2026-04-11
    # should yield 22 disbursements (22 * 180k = 3,960,000).
    elapsed = _months_between(start, today)
    elapsed = max(elapsed, 0)
    cap_months = li.total_months if li.total_months > 0 else elapsed
    effective_months = min(elapsed, cap_months)
    return float(effective_months) * float(li.monthly_amount)


def _solve_amortization_rate(
    principal: float, payment: float, n_months: int
) -> float | None:
    """Solve for monthly rate r from PV = P * (1 - (1+r)^-n) / r.

    Uses bisection on [1e-8, 1.0] monthly. Returns None if no solution.
    """
    if principal <= 0 or payment <= 0 or n_months <= 0:
        return None
    # Degenerate: payment * n ≈ principal means r ≈ 0.
    if abs(payment * n_months - principal) / principal < 1e-6:
        return 0.0

    def pv_at(rate: float) -> float:
        if rate <= 0:
            return payment * n_months
        return payment * (1.0 - (1.0 + rate) ** (-n_months)) / rate

    lo, hi = 1e-9, 1.0
    pv_lo = pv_at(lo)
    pv_hi = pv_at(hi)
    # pv is monotonically decreasing in rate. We need pv = principal.
    if principal > pv_lo or principal < pv_hi:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2.0
        pv_mid = pv_at(mid)
        if abs(pv_mid - principal) < 1e-4:
            return mid
        if pv_mid > principal:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def _eval_amortization(li: Liability, today: date) -> float:
    """Remaining principal on a level-payment loan.

    Before start_date → full principal.
    After start_date  → P * (1+r)^k - M * ((1+r)^k - 1)/r, for k payments made.
    If rate missing, solved numerically from (principal, payment, term).
    """
    if li.principal <= 0:
        return max(li.balance, 0.0)
    start = _parse_iso_date(li.start_date)
    if start is None or today < start:
        return float(li.principal)
    # Monthly rate
    monthly_rate: float | None = None
    if li.rate is not None and li.rate > 0:
        monthly_rate = float(li.rate) / 12.0
    else:
        monthly_rate = _solve_amortization_rate(
            li.principal, li.monthly_payment, li.total_months
        )
    if monthly_rate is None:
        return float(li.principal)
    # Payments made (including today's if on/after start_date)
    k = _months_between(start, today) + 1
    k = max(0, min(k, li.total_months))
    if k == 0:
        return float(li.principal)
    if monthly_rate <= 1e-12:
        return max(li.principal - li.monthly_payment * k, 0.0)
    growth = (1.0 + monthly_rate) ** k
    remaining = (
        li.principal * growth
        - li.monthly_payment * (growth - 1.0) / monthly_rate
    )
    return max(remaining, 0.0)


def evaluate_liability(li: Liability, today: date) -> float:
    """Dispatch to the correct evaluator based on liability type."""
    t = (li.type or "static").lower()
    if t == "monthly_accrual":
        return _eval_monthly_accrual(li, today)
    if t == "amortization":
        return _eval_amortization(li, today)
    return _eval_static_liability(li, today)


# ---------------------------------------------------------------------------
# Core computation
# ---------------------------------------------------------------------------


def compute(holdings: Holdings) -> dict:
    base = holdings.base_currency.upper() or "TWD"
    mc_raw = load_marketcap()
    mc_index = _index_marketcap_by_symbol(mc_raw)

    # Cash
    cash_detail: list[dict] = []
    total_cash_base = 0.0
    for c in holdings.cash:
        rate = get_fx_rate(c.currency, base)
        base_val = c.balance * rate
        total_cash_base += base_val
        cash_detail.append(
            {
                "account": c.account,
                "currency": c.currency,
                "balance": c.balance,
                "balance_base": round(base_val, 2),
                "fx_rate": rate,
            }
        )

    # Positions
    positions_detail: list[dict] = []
    total_positions_base = 0.0
    total_cost_base = 0.0
    # Implicit liabilities generated from positions (e.g. 代持 shares).
    implicit_liabilities: list[Liability] = []

    for p in holdings.positions:
        rate = get_fx_rate(p.currency, base)

        # ---- Special subtype: gross holding with shares held for others ----
        if p.subtype == "gross_with_held_for_others":
            mp = p.manual_price or {}
            mp_value = float(mp.get("value") or 0.0)
            price = mp_value if mp_value > 0 else None
            source = f"manual:{mp.get('source', '')}" if mp_value > 0 else ""
            p.price_native = price
            p.price_source = source
            qty_gross = float(p.qty_gross)
            qty_held = float(p.qty_held_for_others)
            net_qty = qty_gross - qty_held
            # Asset side = GROSS (liability side picks up 代持 separately).
            mv_native_gross = qty_gross * mp_value
            mv_base_gross = mv_native_gross * rate
            # Cost basis from tranche history (or avg_cost_per_share).
            avg_cost = float(p.avg_cost_per_share_native or 0.0)
            if avg_cost <= 0 and qty_gross > 0 and p.total_cost_native > 0:
                avg_cost = p.total_cost_native / qty_gross
            cost_native = (
                float(p.total_cost_native)
                if p.total_cost_native > 0
                else avg_cost * qty_gross
            )
            cost_base = cost_native * rate
            pnl_native_gross = mv_native_gross - cost_native
            pnl_base_gross = pnl_native_gross * rate
            pnl_pct_gross: float | None = None
            if cost_native > 0:
                pnl_pct_gross = (pnl_native_gross / cost_native) * 100.0
            # Edward-net unrealized (after 代持): uses net_qty.
            net_cost_native = avg_cost * net_qty if avg_cost > 0 else 0.0
            net_mv_native = net_qty * mp_value
            pnl_native_net = (
                net_mv_native - net_cost_native if avg_cost > 0 else 0.0
            )
            pnl_base_net = pnl_native_net * rate

            p.market_value_native = mv_native_gross
            p.market_value_base = mv_base_gross
            p.unrealized_pnl_native = pnl_native_gross
            p.unrealized_pnl_base = pnl_base_gross
            p.unrealized_pnl_pct = pnl_pct_gross

            total_positions_base += mv_base_gross
            if cost_native > 0:
                total_cost_base += cost_base

            display_name = p.name or p.ticker or p.account or "private_position"
            positions_detail.append(
                {
                    "ticker": p.ticker or display_name,
                    "name": display_name,
                    "subtype": p.subtype,
                    "accounting_basis": p.accounting_basis,
                    "qty_gross": qty_gross,
                    "qty_held_for_others": qty_held,
                    "qty_net": net_qty,
                    "held_for": p.held_for,
                    "currency": p.currency,
                    "category": p.category,
                    "account": p.account,
                    "note": p.note,
                    "price_native": price,
                    "price_source": source,
                    "manual_price_as_of": mp.get("as_of", ""),
                    "fx_rate": rate,
                    # Asset-side value = GROSS (correction per 2026-04-11)
                    "market_value_native": round(mv_native_gross, 2),
                    "market_value_base": round(mv_base_gross, 2),
                    "gross_market_value_base": round(mv_base_gross, 2),
                    "net_market_value_base": round(net_qty * mp_value * rate, 2),
                    "held_for_others_base": round(qty_held * mp_value * rate, 2),
                    # Cost-history unrealized P&L
                    "total_cost_native": round(cost_native, 2),
                    "total_cost_base": round(cost_base, 2),
                    "avg_cost_per_share_native": round(avg_cost, 2),
                    "cost_history": p.cost_history,
                    "unrealized_pnl_native": round(pnl_native_gross, 2),
                    "unrealized_pnl_base": round(pnl_base_gross, 2),
                    "unrealized_pnl_pct": (
                        round(pnl_pct_gross, 2)
                        if pnl_pct_gross is not None
                        else None
                    ),
                    "unrealized_pnl_net_native": round(pnl_native_net, 2),
                    "unrealized_pnl_net_base": round(pnl_base_net, 2),
                }
            )

            # Generate an implicit liability for the held-for-others portion.
            if p.qty_held_for_others > 0 and mp_value > 0:
                held_native = p.qty_held_for_others * mp_value
                implicit_liabilities.append(
                    Liability(
                        name=f"代持 {display_name}",
                        balance=held_native,
                        currency=p.currency,
                        type="static",
                        source="held_for_others",
                        note=(
                            f"代持 {p.qty_held_for_others} 股 × "
                            f"{mp_value:.0f} {p.currency}"
                        ),
                        breakdown=[
                            {
                                "name": h.get("name", ""),
                                "qty": h.get("qty", 0),
                                "amount_native": round(
                                    float(h.get("qty") or 0) * mp_value, 2
                                ),
                            }
                            for h in p.held_for
                        ],
                    )
                )
            continue

        # ---- Vanilla position path ----
        price, source = resolve_price(p, mc_index)
        p.price_native = price
        p.price_source = source
        if price is None:
            # Unknown price -> value at cost, flag in notes
            price_for_mv = p.cost_basis
            note_suffix = "價格未取得,以成本估算"
        else:
            price_for_mv = price
            note_suffix = ""
        mv_native = p.qty * price_for_mv
        mv_base = mv_native * rate
        cost_native = p.qty * p.cost_basis if p.has_cost_basis else 0.0
        cost_base = cost_native * rate
        pnl_native = mv_native - cost_native
        pnl_base = mv_base - cost_base
        pnl_pct: float | None = None
        if cost_native > 0:
            pnl_pct = (pnl_native / cost_native) * 100.0

        p.market_value_native = mv_native
        p.market_value_base = mv_base
        p.unrealized_pnl_native = pnl_native
        p.unrealized_pnl_base = pnl_base
        p.unrealized_pnl_pct = pnl_pct

        total_positions_base += mv_base
        total_cost_base += cost_base

        positions_detail.append(
            {
                "ticker": p.ticker,
                "qty": p.qty,
                "cost_basis": p.cost_basis,
                "currency": p.currency,
                "category": p.category,
                "account": p.account,
                "note": (p.note + (" " + note_suffix if note_suffix else "")).strip(),
                "price_native": price,
                "price_source": source,
                "fx_rate": rate,
                "market_value_native": round(mv_native, 2),
                "market_value_base": round(mv_base, 2),
                "unrealized_pnl_native": round(pnl_native, 2),
                "unrealized_pnl_base": round(pnl_base, 2),
                "unrealized_pnl_pct": (
                    round(pnl_pct, 2) if pnl_pct is not None else None
                ),
            }
        )

    # Liabilities (explicit + implicit from positions)
    today_tpe = now_tpe().date()
    liabilities_detail: list[dict] = []
    total_liabilities_base = 0.0
    all_liabilities: list[Liability] = list(holdings.liabilities) + implicit_liabilities
    for li in all_liabilities:
        current_native = evaluate_liability(li, today_tpe)
        rate = get_fx_rate(li.currency, base)
        base_val = current_native * rate
        total_liabilities_base += base_val
        detail = {
            "name": li.name,
            "amount": round(base_val, 2),
            "currency": li.currency,
            "native_balance": round(current_native, 2),
            "type": li.type,
            "note": li.note,
        }
        if li.source:
            detail["source"] = li.source
        if li.breakdown:
            detail["breakdown"] = li.breakdown
        if li.type == "monthly_accrual":
            detail["start_date"] = li.start_date
            detail["monthly_amount"] = li.monthly_amount
            detail["total_months"] = li.total_months
        elif li.type == "amortization":
            detail["start_date"] = li.start_date
            detail["principal"] = li.principal
            detail["monthly_payment"] = li.monthly_payment
            detail["total_months"] = li.total_months
        liabilities_detail.append(detail)

    total_assets_base = total_cash_base + total_positions_base
    net_worth = total_assets_base - total_liabilities_base
    leverage = (
        (total_assets_base / net_worth) if net_worth > 0 else None
    )
    debt_to_asset_pct = (
        (total_liabilities_base / total_assets_base * 100.0)
        if total_assets_base > 0
        else None
    )

    # Asset allocation by category
    alloc_cat: dict[str, float] = {}
    for p in holdings.positions:
        alloc_cat[p.category] = alloc_cat.get(p.category, 0.0) + p.market_value_base
    if total_cash_base > 0:
        alloc_cat["現金"] = alloc_cat.get("現金", 0.0) + total_cash_base
    asset_breakdown = sorted(
        [
            {"name": k, "amount": round(v, 2)}
            for k, v in alloc_cat.items()
            if v > 0
        ],
        key=lambda e: e["amount"],
        reverse=True,
    )

    # Asset allocation by currency
    alloc_ccy: dict[str, float] = {}
    for c in holdings.cash:
        rate = get_fx_rate(c.currency, base)
        alloc_ccy[c.currency] = alloc_ccy.get(c.currency, 0.0) + c.balance * rate
    for p in holdings.positions:
        alloc_ccy[p.currency] = alloc_ccy.get(p.currency, 0.0) + p.market_value_base
    alloc_by_currency = sorted(
        [
            {"currency": k, "amount": round(v, 2)}
            for k, v in alloc_ccy.items()
            if v > 0
        ],
        key=lambda e: e["amount"],
        reverse=True,
    )

    # Top holdings (positions only, sorted by base market value)
    top_holdings = []
    port_for_pct = total_assets_base if total_assets_base > 0 else 1.0
    sorted_positions = sorted(
        holdings.positions, key=lambda p: p.market_value_base, reverse=True
    )
    for p in sorted_positions:
        if p.market_value_base <= 0:
            continue
        top_holdings.append(
            {
                "ticker": p.ticker,
                "amount": round(p.market_value_base, 2),
                "pct_of_portfolio": round(
                    p.market_value_base / port_for_pct * 100.0, 2
                ),
            }
        )
    top_holdings = top_holdings[:10]

    # Preserve prior sparkline + deltas if the existing networth file has them.
    prior = {}
    if NETWORTH_OUT.exists():
        try:
            prior = json.loads(NETWORTH_OUT.read_text(encoding="utf-8"))
        except Exception:
            prior = {}
    sparkline = prior.get("sparkline") or []
    today_label = now_tpe().strftime("%Y/%m/%d")
    if isinstance(sparkline, list):
        # Replace today's entry if exists, else append. Keep last 13 entries.
        new_entry = {"date": today_label, "equity": round(net_worth, 2)}
        filtered = [s for s in sparkline if s.get("date") != today_label]
        filtered.append(new_entry)
        sparkline = filtered[-13:]
    else:
        sparkline = [{"date": today_label, "equity": round(net_worth, 2)}]

    def _delta_from(sparks: list[dict], days_back: int) -> dict:
        if not sparks:
            return {"abs": 0, "pct": 0.0, "from": "", "from_equity": 0}
        target = now_tpe() - timedelta(days=days_back)
        best = sparks[0]
        for s in sparks:
            try:
                dt = datetime.strptime(s.get("date", ""), "%Y/%m/%d").replace(
                    tzinfo=TPE
                )
            except ValueError:
                continue
            if dt <= target:
                best = s
        prev_eq = _safe_float(best.get("equity"))
        abs_d = net_worth - prev_eq
        pct = (abs_d / prev_eq * 100.0) if prev_eq else 0.0
        return {
            "abs": round(abs_d, 2),
            "pct": round(pct, 4),
            "from": best.get("date", ""),
            "from_equity": prev_eq,
        }

    payload = {
        "generated_at": now_label_tpe(),
        "computed_from_holdings": True,
        "as_of": now_iso_tpe(),
        "holdings_as_of": holdings.as_of,
        "currency": base,
        "equity": round(net_worth, 2),
        "assets": round(total_assets_base, 2),
        "liabilities": round(total_liabilities_base, 2),
        "leverage": round(leverage, 2) if leverage else None,
        "debt_to_asset_pct": (
            round(debt_to_asset_pct, 4) if debt_to_asset_pct is not None else None
        ),
        "delta_7d": _delta_from(sparkline, 7),
        "delta_30d": _delta_from(sparkline, 30),
        "delta_ytd": _delta_from(sparkline, (now_tpe() - datetime(now_tpe().year, 1, 1, tzinfo=TPE)).days or 1),
        "sparkline": sparkline,
        "asset_breakdown": asset_breakdown,
        "asset_allocation_by_currency": alloc_by_currency,
        "liability_breakdown": [
            {"name": li["name"], "amount": li["amount"]}
            for li in liabilities_detail
        ],
        "top_holdings": top_holdings,
        "fire_target_ntd": FIRE_TARGET_TWD,
        "fire_pct": round(
            (net_worth / FIRE_TARGET_TWD * 100.0) if FIRE_TARGET_TWD else 0.0, 4
        ),
        "totals": {
            "cash_base": round(total_cash_base, 2),
            "positions_base": round(total_positions_base, 2),
            "cost_base": round(total_cost_base, 2),
            "unrealized_pnl_base": round(total_positions_base - total_cost_base, 2),
            "unrealized_pnl_pct": (
                round((total_positions_base - total_cost_base) / total_cost_base * 100.0, 4)
                if total_cost_base > 0
                else None
            ),
        },
        "cash_detail": cash_detail,
        "positions_detail": positions_detail,
        "liabilities_detail": liabilities_detail,
    }
    return payload


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    log.info("balance_sheet_builder start")
    try:
        holdings = load_holdings()
    except Exception as exc:
        log.exception("failed to load holdings: %s", exc)
        return 2

    log.info(
        "holdings loaded: cash=%d positions=%d liabilities=%d base=%s as_of=%s",
        len(holdings.cash),
        len(holdings.positions),
        len(holdings.liabilities),
        holdings.base_currency,
        holdings.as_of,
    )

    try:
        payload = compute(holdings)
    except Exception as exc:
        log.exception("compute failed: %s", exc)
        return 3

    try:
        NETWORTH_OUT.parent.mkdir(parents=True, exist_ok=True)
        NETWORTH_OUT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as exc:
        log.exception("failed to write %s: %s", NETWORTH_OUT, exc)
        return 4

    log.info(
        "wrote %s | equity=%s assets=%s liabilities=%s positions=%d",
        NETWORTH_OUT.name,
        payload.get("equity"),
        payload.get("assets"),
        payload.get("liabilities"),
        len(payload.get("positions_detail") or []),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
