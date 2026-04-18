"""finance_engine.py — Dashin Capital per-share NAV engine.

Single source of truth for the formula Edward confirmed on 2026-04-15:

    new_per_share = prev_per_share * (
        ((base + prior_cum + this_week_pnl) / (base + prior_cum) - 1)
        * smoothing
        + 1
    )

Where:
  - base                 : ops_base_post_zhengzi_twd (fixed after 增資, 2026-03-21)
  - prior_cum            : cumulative pnl since 增資, up to the week BEFORE this one
  - this_week_pnl        : net pnl of the week being ingested
  - smoothing            : damping factor applied to the weekly return (0.9)

After each ingest, cumulative_pnl_since_zhengzi_twd is incremented by
this_week_pnl so the denominator grows week by week — this was the missing
variable in the earlier (incorrect) implementation that used a fixed
operation_total.

Usage:
    from finance_engine import compute_per_share, ingest_weekly_pnl

    new_ps = compute_per_share(
        prev_per_share=222347,
        this_week_pnl=53_454_000,
        base=306_780_000,
        prior_cumulative_pnl=68_326_000,
        smoothing=0.9,
    )
    # -> 250864.xx

    ingest_weekly_pnl(
        week_ending="2026-04-15",
        this_week_pnl=53_454_000,
        config_path="config/finance_capital_structure.json",
    )

All functions are pure except ingest_weekly_pnl, which writes back to the
config JSON and appends a history row.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# --------------------------------------------------------------------------- #
# Pure formula                                                                 #
# --------------------------------------------------------------------------- #


def compute_per_share(
    prev_per_share: float,
    this_week_pnl: float,
    base: float,
    prior_cumulative_pnl: float,
    smoothing: float = 0.9,
) -> float:
    """Return the new per-share NAV given the week's pnl and prior state.

    Raises ValueError if the denominator would be zero or negative.
    """
    prior_denom = base + prior_cumulative_pnl
    if prior_denom <= 0:
        raise ValueError(
            f"Invalid prior denominator {prior_denom} "
            f"(base={base}, prior_cum={prior_cumulative_pnl})"
        )
    new_denom = prior_denom + this_week_pnl
    weekly_return = new_denom / prior_denom - 1.0
    factor = weekly_return * smoothing + 1.0
    return prev_per_share * factor


# --------------------------------------------------------------------------- #
# Config I/O                                                                   #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class CapitalStructure:
    base: float
    cumulative_pnl: float
    cumulative_as_of_week_ending: str
    smoothing: float
    latest_per_share: float
    latest_per_share_as_of: str

    @classmethod
    def from_config(cls, config_path: str | Path) -> "CapitalStructure":
        data = json.loads(Path(config_path).read_text(encoding="utf-8"))
        return cls(
            base=float(data["ops_base_post_zhengzi_twd"]),
            cumulative_pnl=float(data["cumulative_pnl_since_zhengzi_twd"]),
            cumulative_as_of_week_ending=str(data["cumulative_pnl_as_of_week_ending"]),
            smoothing=float(data.get("smoothing_factor", 0.9)),
            latest_per_share=float(data["latest_per_share_twd"]),
            latest_per_share_as_of=str(data["latest_per_share_as_of"]),
        )


def ingest_weekly_pnl(
    week_ending: str,
    this_week_pnl: float,
    config_path: str | Path = "config/finance_capital_structure.json",
    smoothing: Optional[float] = None,
) -> dict:
    """Apply one week of pnl to the capital structure config.

    Returns the updated config dict and writes it back to disk atomically.
    Appends a history row for audit. Does NOT touch holdings.yaml — that is
    the balance-sheet builder's job (it reads latest_per_share_twd from this
    config or from holdings manual_price).
    """
    path = Path(config_path)
    data = json.loads(path.read_text(encoding="utf-8"))

    base = float(data["ops_base_post_zhengzi_twd"])
    prior_cum = float(data["cumulative_pnl_since_zhengzi_twd"])
    prev_per_share = float(data["latest_per_share_twd"])
    smooth = smoothing if smoothing is not None else float(data.get("smoothing_factor", 0.9))

    new_per_share = compute_per_share(
        prev_per_share=prev_per_share,
        this_week_pnl=this_week_pnl,
        base=base,
        prior_cumulative_pnl=prior_cum,
        smoothing=smooth,
    )
    new_cum = prior_cum + this_week_pnl

    data["prev_per_share_twd"] = prev_per_share
    data["prev_per_share_as_of"] = data.get("latest_per_share_as_of")
    data["latest_per_share_twd"] = round(new_per_share, 2)
    data["latest_per_share_as_of"] = week_ending
    data["cumulative_pnl_since_zhengzi_twd"] = new_cum
    data["cumulative_pnl_as_of_week_ending"] = week_ending

    history = data.setdefault("history", [])
    history.append(
        {
            "week_ending": week_ending,
            "prior_cum_before_week": prior_cum,
            "this_week_pnl": this_week_pnl,
            "prev_per_share": prev_per_share,
            "new_per_share": round(new_per_share, 2),
        }
    )

    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)
    return data


# --------------------------------------------------------------------------- #
# Audit / backfill                                                             #
# --------------------------------------------------------------------------- #


def replay_history(
    base: float,
    seed_per_share: float,
    seed_prior_cum: float,
    weekly_pnls: list[tuple[str, float]],
    smoothing: float = 0.9,
) -> list[dict]:
    """Replay a sequence of (week_ending, this_week_pnl) to reconstruct NAV.

    Useful for auditing against dashin_monthly_nav.jsonl or Edward's sheet.
    Returns a list of dicts [{week_ending, prior_cum, pnl, per_share}, ...].
    """
    out: list[dict] = []
    cum = seed_prior_cum
    per_share = seed_per_share
    for week_ending, pnl in weekly_pnls:
        per_share = compute_per_share(per_share, pnl, base, cum, smoothing)
        cum += pnl
        out.append(
            {
                "week_ending": week_ending,
                "prior_cum": cum - pnl,
                "pnl": pnl,
                "per_share": round(per_share, 2),
                "cumulative_after": cum,
            }
        )
    return out


# --------------------------------------------------------------------------- #
# Self-verify                                                                  #
# --------------------------------------------------------------------------- #


def _selftest() -> None:
    """Edward canonical example — must equal 250864 within 1 TWD."""
    got = compute_per_share(
        prev_per_share=222347,
        this_week_pnl=53_454_000,
        base=306_780_000,
        prior_cumulative_pnl=68_326_000,
        smoothing=0.9,
    )
    expected = 250864
    assert abs(got - expected) < 1.0, f"formula broken: got {got}, expected {expected}"
    print(f"[finance_engine] selftest OK: {got:.2f} ~= {expected}")


if __name__ == "__main__":
    _selftest()
