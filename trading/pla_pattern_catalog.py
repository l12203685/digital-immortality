"""
PLA Pattern Catalog — extract indicator patterns from digestion_log.jsonl.

Parses the B2-digested strategy corpus (636+ entries) to build:
  1. Indicator frequency table
  2. Co-occurrence matrix (pairs & triples)
  3. Parameter ranges observed per indicator
  4. Structured catalog JSON + markdown summary

Also provides ``generate_strategy_configs_from_catalog()`` which maps
PLA indicators to concrete strategy class + parameter-space entries
that ``strategy_generator.py`` can consume.

Usage:
    python trading/pla_pattern_catalog.py
    python trading/pla_pattern_catalog.py --show-combos
    python trading/pla_pattern_catalog.py --generate-configs
    python trading/pla_pattern_catalog.py --export
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default paths
# ---------------------------------------------------------------------------

_DEFAULT_DIGESTION_LOG = Path(
    "C:/Users/admin/workspace/digital-immortality/results/digestion_log.jsonl"
)
_DEFAULT_CATALOG_JSON = Path(
    "C:/Users/admin/workspace/digital-immortality/results/pla_pattern_catalog.json"
)
_DEFAULT_CATALOG_MD = Path(
    "C:/Users/admin/workspace/digital-immortality/results/pla_pattern_catalog.md"
)

# Legacy path kept for backward compat in generate_strategy_configs_from_catalog
_LEGACY_INDEX_PATH = Path("E:/pla_md/logic/LOGIC_INDEX.md")

# ---------------------------------------------------------------------------
# Indicator detection patterns
# ---------------------------------------------------------------------------

INDICATOR_PATTERNS: Dict[str, str] = {
    "MA": r"\b(?:MA|moving[- ]?average|SMA|EMA|DMA|WMA|DEMA|TEMA|dual[- ]?ma)\b",
    "RSI": r"\bRSI\b",
    "MACD": r"\bMACD\b",
    "KD": r"\b(?:KD|stochastic|%K|%D)\b",
    "CCI": r"\bCCI\b",
    "DMI": r"\b(?:DMI|ADX|directional[- ]?movement)\b",
    "Bollinger": r"\b(?:BBand|Bollinger|BB|Bval)\b",
    "ATR": r"\b(?:ATR|average[- ]?true[- ]?range|true[- ]?range)\b",
    "CDP": r"\bCDP\b",
    "SAR": r"\b(?:SAR|Parabolic[- ]?SAR)\b",
    "Keltner": r"\b(?:Keltner|KC)\b",
    "Ichimoku": r"\b(?:Ichimoku|Kinko|Kumo)\b",
    "Volume": r"\b(?:volume[- ]?(?:indicator|filter|breakout)|VOL|OBV|MFI)\b",
    "StdDev": r"\b(?:stddev|standard[- ]?deviation|StdDev)\b",
    "Donchian": r"\b(?:Donchian|channel[- ]?breakout)\b",
    "Gap": r"\b(?:gap[- ]?(?:fade|entry|filter|trade|open)|open[- ]?gap|gap[- ]?up|gap[- ]?down)\b",
    "ORB": r"\b(?:ORB|opening[- ]?range[- ]?breakout|open[- ]?range)\b",
    "Pivot": r"\b(?:pivot[- ]?point|support[- ]?resistance|S/R)\b",
    "Slope": r"\b(?:slope|momentum[- ]?(?:indicator|filter|score))\b",
    "WilliamsR": r"\b(?:Williams[- ]?%?R|WilliamsR)\b",
    # New patterns from batches 4-6
    "ShakeFilter": r"\b(?:shake[- ]?filter|shake[- ]?oscillat|oscillation[- ]?count|mid[- ]?direction)\b",
    "SqrtTimeTrail": r"\b(?:sqrt[- ]?(?:time|barsince)|square[- ]?root[- ]?(?:time|trail)|sqrt\(bars)\b",
    "AdaptiveMultiplier": r"\b(?:adaptive[- ]?(?:entry|multiplier|lookback)|doubles?[- ]?(?:after|period|lookback)[- ]?loss|loss[- ]?doubl)\b",
    "GoldenRatioMA": r"\b(?:golden[- ]?ratio|phi[= ]?1\.618|fibonacci[- ]?MA|golden[- ]?ratio[- ]?MA)\b",
    "KPower": r"\b(?:KPower|LPower|SPower|buying[- ]?pressure[- ]?score|pressure[- ]?score)\b",
    "BarTiming": r"\b(?:bar[- ]?timing|Hbar|Lbar|when[- ]?(?:daily[- ]?)?[HL][- ]?(?:was[- ]?)?made|session[- ]?high[- ]?bar|session[- ]?low[- ]?bar)\b",
}

# Compiled patterns for performance
_COMPILED_PATTERNS: Dict[str, re.Pattern[str]] = {
    name: re.compile(pat, re.IGNORECASE)
    for name, pat in INDICATOR_PATTERNS.items()
}

# Parameter extraction patterns: indicator -> param_name -> regex
PARAM_PATTERNS: Dict[str, Dict[str, str]] = {
    "MA": {
        "period": r"(?:MA|SMA|EMA|moving.?average)\D{0,10}(\d{1,3})\b",
    },
    "RSI": {
        "period": r"RSI\D{0,10}(\d{1,3})\b",
    },
    "CCI": {
        "period": r"CCI\D{0,10}(\d{1,3})\b",
        "threshold": r"CCI\D{0,20}(?:threshold|level|limit)\D{0,5}(\d+)",
    },
    "MACD": {
        "fast": r"MACD\D{0,20}(?:fast|short)\D{0,5}(\d{1,3})\b",
        "slow": r"MACD\D{0,20}(?:slow|long)\D{0,5}(\d{1,3})\b",
        "signal": r"MACD\D{0,20}(?:signal)\D{0,5}(\d{1,3})\b",
    },
    "ATR": {
        "period": r"ATR\D{0,10}(\d{1,3})\b",
    },
    "Bollinger": {
        "period": r"(?:BB|Bollinger)\D{0,10}(?:Len|period|lookback)?\D{0,5}(\d{1,3})\b",
        "std_dev": r"(?:BB|Bollinger)\D{0,20}(?:Dev|std|sigma)\D{0,5}([\d.]+)",
    },
    "KD": {
        "period": r"KD\D{0,10}(\d{1,3})\b",
    },
    "Donchian": {
        "period": r"(?:Donchian|channel)\D{0,10}(\d{1,3})\b",
    },
}

# Tags corresponding to strategies already in the pool
EXISTING_STRATEGY_TAGS = [
    "MA",           # DualMA
    "Donchian",     # Donchian, DonchianConfirmed
    "Bollinger",    # BollingerMeanReversion
    "RSI",          # RSIFilter
    "CCI",          # CCIStrategy
    "DMI",          # DMIStrategy
    "MACD",         # MACDStrategy
    "ORB",          # ORBStrategy
    "ATR",          # KeltnerStrategy
    # Batch 3 additions (Stochastic/CDP/SAR/Gap)
    "KD",           # StochasticStrategy
    "CDP",          # CDPStrategy
    "SAR",          # ParabolicSARStrategy
    "Gap",          # GapFadeStrategy
    # Batch 4-6 additions (novel techniques from extended digestion)
    "ShakeFilter",      # ShakeFilterStrategy
    "SqrtTimeTrail",    # SqrtTimeTrailStrategy
    "AdaptiveMultiplier",  # AdaptiveMultiplierMAStrategy
    "GoldenRatioMA",    # GoldenRatioMAStrategy
    "KPower",           # KPowerStrategy
    "BarTiming",        # BarTimingStrategy
]


# ---------------------------------------------------------------------------
# Data extraction from digestion log
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DigestionEntry:
    """Immutable representation of a single digested PLA strategy."""

    path: str
    summary: str
    strategy_name: str
    category: str
    family: str
    direction: str
    timeframe: str
    tags: Tuple[str, ...]
    tier: Optional[int]


def load_digestion_log(log_path: Path) -> List[DigestionEntry]:
    """Load and parse digestion_log.jsonl into structured entries.

    Only returns entries with a non-empty summary (meaningful content).
    """
    if not log_path.exists():
        raise FileNotFoundError(f"Digestion log not found: {log_path}")

    entries: List[DigestionEntry] = []
    with open(log_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            raw = json.loads(line)
            summary = raw.get("summary", "") or ""
            if len(summary) < 20:
                continue
            entries.append(DigestionEntry(
                path=raw.get("path", ""),
                summary=summary,
                strategy_name=raw.get("strategy_name", "") or "",
                category=raw.get("category", "") or "",
                family=raw.get("family", "") or "",
                direction=raw.get("direction", "") or "",
                timeframe=raw.get("timeframe", "") or "",
                tags=tuple(raw.get("tags", []) or []),
                tier=raw.get("tier"),
            ))
    return entries


def _entry_text(entry: DigestionEntry) -> str:
    """Combine all text fields of an entry for indicator detection."""
    parts = [
        entry.summary,
        entry.category,
        " ".join(entry.tags),
        entry.strategy_name,
    ]
    return " ".join(p for p in parts if p)


def detect_indicators(text: str) -> List[str]:
    """Detect which indicators are mentioned in a text block.

    Returns sorted list of unique indicator names found.
    """
    found: List[str] = []
    for name, pattern in _COMPILED_PATTERNS.items():
        if pattern.search(text):
            found.append(name)
    return sorted(found)


def build_indicator_frequency(
    entries: List[DigestionEntry],
) -> Dict[str, int]:
    """Count how many entries mention each indicator.

    Returns dict mapping indicator name -> occurrence count.
    """
    freq: Counter[str] = Counter()
    for entry in entries:
        text = _entry_text(entry)
        for indicator in detect_indicators(text):
            freq[indicator] += 1
    return dict(freq)


def build_cooccurrence(
    entries: List[DigestionEntry],
) -> Tuple[Dict[Tuple[str, str], int], Dict[Tuple[str, str, str], int]]:
    """Build indicator co-occurrence counts.

    Returns (pair_counts, triple_counts) where keys are sorted tuples.
    """
    pair_freq: Counter[Tuple[str, str]] = Counter()
    triple_freq: Counter[Tuple[str, str, str]] = Counter()

    for entry in entries:
        text = _entry_text(entry)
        indicators = detect_indicators(text)
        if len(indicators) < 2:
            continue
        for pair in combinations(indicators, 2):
            pair_freq[pair] += 1  # type: ignore[arg-type]
        for triple in combinations(indicators, 3):
            triple_freq[triple] += 1  # type: ignore[arg-type]

    return dict(pair_freq), dict(triple_freq)


def extract_parameter_ranges(
    entries: List[DigestionEntry],
) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """Extract observed parameter ranges from strategy summaries.

    Returns nested dict: indicator -> param_name -> {min, max, values, count}.
    Only includes values in plausible ranges (1-500) to filter noise.
    """
    raw_params: Dict[str, Dict[str, List[float]]] = defaultdict(
        lambda: defaultdict(list)
    )

    for entry in entries:
        text = entry.summary
        if not text:
            continue
        for indicator, params in PARAM_PATTERNS.items():
            for param_name, pattern in params.items():
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    try:
                        val = float(match.group(1))
                        # Filter implausible values (strategy file names
                        # sometimes contain dates like 202106)
                        if 1 <= val <= 500:
                            raw_params[indicator][param_name].append(val)
                    except (ValueError, IndexError):
                        pass

    result: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for indicator, params in raw_params.items():
        result[indicator] = {}
        for param_name, values in params.items():
            sorted_vals = sorted(set(values))
            result[indicator][param_name] = {
                "min": min(sorted_vals),
                "max": max(sorted_vals),
                "median": sorted_vals[len(sorted_vals) // 2],
                "values": sorted_vals,
                "count": len(values),
            }
    return result


# ---------------------------------------------------------------------------
# Catalog building
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PatternCatalog:
    """Immutable catalog of PLA indicator patterns."""

    total_entries: int
    indicator_frequency: Dict[str, int]
    pair_cooccurrence: Dict[str, int]  # "A + B" -> count
    triple_cooccurrence: Dict[str, int]  # "A + B + C" -> count
    parameter_ranges: Dict[str, Dict[str, Dict[str, Any]]]
    covered_indicators: List[str]
    untapped_indicators: List[Tuple[str, int]]
    untapped_pairs: List[Tuple[str, int]]


def build_catalog(
    entries: List[DigestionEntry],
    existing_tags: Optional[List[str]] = None,
) -> PatternCatalog:
    """Build a complete pattern catalog from digestion entries."""
    if existing_tags is None:
        existing_tags = list(EXISTING_STRATEGY_TAGS)

    existing_set = set(existing_tags)
    ind_freq = build_indicator_frequency(entries)
    pairs, triples = build_cooccurrence(entries)
    param_ranges = extract_parameter_ranges(entries)

    # Format co-occurrence keys as strings for JSON serialization
    pair_strs = {
        f"{a} + {b}": count
        for (a, b), count in sorted(pairs.items(), key=lambda x: -x[1])
    }
    triple_strs = {
        f"{a} + {b} + {c}": count
        for (a, b, c), count in sorted(triples.items(), key=lambda x: -x[1])
    }

    # Untapped single indicators (not in existing pool, count >= 2)
    untapped = [
        (tag, count)
        for tag, count in sorted(ind_freq.items(), key=lambda x: -x[1])
        if tag not in existing_set and count >= 2
    ]

    # Untapped pairs (at least one indicator not covered, count >= 2)
    untapped_pairs = [
        (f"{a} + {b}", count)
        for (a, b), count in sorted(pairs.items(), key=lambda x: -x[1])
        if not all(t in existing_set for t in (a, b)) and count >= 2
    ]

    return PatternCatalog(
        total_entries=len(entries),
        indicator_frequency=dict(
            sorted(ind_freq.items(), key=lambda x: -x[1])
        ),
        pair_cooccurrence=pair_strs,
        triple_cooccurrence=triple_strs,
        parameter_ranges=param_ranges,
        covered_indicators=[t for t in existing_tags if t in ind_freq],
        untapped_indicators=untapped,
        untapped_pairs=untapped_pairs,
    )


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def export_catalog_json(catalog: PatternCatalog, out_path: Path) -> None:
    """Write catalog to a structured JSON file."""
    data = {
        "total_entries_analyzed": catalog.total_entries,
        "indicator_frequency": catalog.indicator_frequency,
        "covered_indicators": catalog.covered_indicators,
        "untapped_indicators": [
            {"indicator": tag, "count": count}
            for tag, count in catalog.untapped_indicators
        ],
        "pair_cooccurrence": catalog.pair_cooccurrence,
        "triple_cooccurrence": catalog.triple_cooccurrence,
        "untapped_pairs": [
            {"pair": pair, "count": count}
            for pair, count in catalog.untapped_pairs
        ],
        "parameter_ranges": catalog.parameter_ranges,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    logger.info("Wrote catalog JSON to %s", out_path)


def export_catalog_markdown(catalog: PatternCatalog, out_path: Path) -> None:
    """Write catalog summary as a markdown report."""
    lines: List[str] = []
    lines.append("# PLA Pattern Catalog")
    lines.append("")
    lines.append(
        f"Analyzed **{catalog.total_entries}** digested PLA strategies."
    )
    lines.append("")

    # Indicator frequency table
    lines.append("## Indicator Frequency")
    lines.append("")
    lines.append("| Indicator | Count | Status |")
    lines.append("|-----------|-------|--------|")
    covered_set = set(catalog.covered_indicators)
    for tag, count in catalog.indicator_frequency.items():
        status = "COVERED" if tag in covered_set else "untapped"
        lines.append(f"| {tag} | {count} | {status} |")
    lines.append("")

    # Untapped indicators
    if catalog.untapped_indicators:
        lines.append("## Untapped Indicators")
        lines.append("")
        lines.append(
            "Indicators found in PLA corpus but not in the active strategy pool:"
        )
        lines.append("")
        for tag, count in catalog.untapped_indicators:
            lines.append(f"- **{tag}**: {count} strategies")
        lines.append("")

    # Top co-occurring pairs
    lines.append("## Top Indicator Pairs")
    lines.append("")
    lines.append("| Pair | Count |")
    lines.append("|------|-------|")
    top_pairs = list(catalog.pair_cooccurrence.items())[:20]
    for pair, count in top_pairs:
        lines.append(f"| {pair} | {count} |")
    lines.append("")

    # Top triples
    top_triples = list(catalog.triple_cooccurrence.items())[:10]
    if top_triples:
        lines.append("## Top Indicator Triples")
        lines.append("")
        lines.append("| Triple | Count |")
        lines.append("|--------|-------|")
        for triple, count in top_triples:
            lines.append(f"| {triple} | {count} |")
        lines.append("")

    # Parameter ranges
    if catalog.parameter_ranges:
        lines.append("## Observed Parameter Ranges")
        lines.append("")
        for indicator, params in sorted(catalog.parameter_ranges.items()):
            lines.append(f"### {indicator}")
            lines.append("")
            lines.append("| Parameter | Min | Max | Median | Sample Values |")
            lines.append("|-----------|-----|-----|--------|---------------|")
            for param_name, info in sorted(params.items()):
                vals_str = ", ".join(str(int(v)) for v in info["values"][:8])
                lines.append(
                    f"| {param_name} | {info['min']:.0f} | {info['max']:.0f}"
                    f" | {info['median']:.0f} | {vals_str} |"
                )
            lines.append("")

    # Untapped pairs
    if catalog.untapped_pairs:
        lines.append("## Untapped Indicator Pairs")
        lines.append("")
        lines.append(
            "Pairs where at least one indicator is not in the active pool:"
        )
        lines.append("")
        for pair, count in catalog.untapped_pairs[:15]:
            lines.append(f"- **{pair}**: {count} strategies")
        lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote catalog markdown to %s", out_path)


# ---------------------------------------------------------------------------
# Tag -> Strategy class mapping for config generation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class StrategyConfig:
    """Immutable description of a strategy to instantiate."""

    strategy_class: str          # e.g. "CCIStrategy"
    module: str                  # e.g. "trading.strategies_extended"
    params: Dict[str, Any]       # constructor kwargs
    pla_tag: str                 # originating PLA tag
    priority: int = 0            # higher = more PLA corpus support


# Mapping from indicator names to (class_name, module, parameter_space).
TAG_TO_STRATEGY_SPACE: Dict[str, List[Dict[str, Any]]] = {
    "CCI": [
        {"class": "CCIStrategy", "module": "trading.strategies_extended",
         "params": {"period": p, "threshold": t}}
        for p in [14, 20, 25, 30]
        for t in [80.0, 100.0, 120.0, 150.0]
    ],
    "DMI": [
        {"class": "DMIStrategy", "module": "trading.strategies_extended",
         "params": {"period": p, "adx_threshold": a}}
        for p in [10, 14, 20, 25]
        for a in [20.0, 25.0, 30.0, 35.0]
    ],
    "MACD": [
        {"class": "MACDStrategy", "module": "trading.strategies_extended",
         "params": {"fast": f, "slow": s, "signal": sig}}
        for f in [8, 12, 16]
        for s in [21, 26, 34]
        for sig in [7, 9, 12]
        if f < s
    ],
    "ORB": [
        {"class": "ORBStrategy", "module": "trading.strategies_extended",
         "params": {"range_bars": rb, "atr_filter": af, "atr_period": ap}}
        for rb in [1, 2, 3, 5]
        for af in [0.0, 0.3, 0.5, 0.8]
        for ap in [10, 14, 20]
    ],
    "ATR": [
        {"class": "KeltnerStrategy", "module": "trading.strategies_extended",
         "params": {"ema_period": ep, "atr_period": ap, "multiplier": m, "mode": mode}}
        for ep in [15, 20, 25, 30]
        for ap in [10, 14, 20]
        for m in [1.5, 2.0, 2.5, 3.0]
        for mode in ["momentum", "reversion"]
    ],
    "MA": [
        {"class": "DualMA", "module": "trading.strategies",
         "params": {"fast": f, "slow": s}}
        for f in [5, 8, 10, 15, 20]
        for s in [20, 30, 40, 50, 60]
        if f < s
    ],
    "Bollinger": [
        {"class": "BollingerMeanReversion", "module": "trading.strategies",
         "params": {"lookback": lb, "num_std": ns, "trend_lookback": tl,
                    "trend_threshold": tt}}
        for lb in [15, 20, 25, 30]
        for ns in [1.5, 2.0, 2.5]
        for tl in [40, 50, 60]
        for tt in [0.001, 0.003, 0.005]
    ],
    "Donchian": [
        {"class": "Donchian", "module": "trading.strategies",
         "params": {"period": p}}
        for p in [10, 15, 20, 25, 30, 40, 55]
    ],
    "RSI": [
        {"class": "RSIFilter", "module": "trading.strategies",
         "params": {"period": p, "rsi_long_min": lm, "rsi_short_max": sm}}
        for p in [10, 14, 21]
        for lm in [45, 50, 55]
        for sm in [45, 50, 55]
    ],
    "KD": [
        {"class": "StochasticStrategy", "module": "trading.strategies_extended",
         "params": {"k_period": kp, "d_period": dp, "overbought": ob,
                    "oversold": os_}}
        for kp in [9, 14, 20]
        for dp in [3, 5]
        for ob in [75, 80, 85]
        for os_ in [15, 20, 25]
    ],
    "CDP": [
        {"class": "CDPStrategy", "module": "trading.strategies_extended",
         "params": {"mode": mode}}
        for mode in ["breakout", "reversion"]
    ],
    "SAR": [
        {"class": "ParabolicSARStrategy", "module": "trading.strategies_extended",
         "params": {"af_start": af, "af_step": af, "af_max": mx}}
        for af in [0.01, 0.02, 0.03]
        for mx in [0.10, 0.20, 0.30]
    ],
    "Gap": [
        {"class": "GapFadeStrategy", "module": "trading.strategies_extended",
         "params": {"gap_threshold": gt, "atr_period": ap, "mode": mode}}
        for gt in [0.005, 0.01, 0.015, 0.02]
        for ap in [10, 14, 20]
        for mode in ["fade", "follow"]
    ],
    # ---------------------------------------------------------------------------
    # Batch 4-6: Novel techniques from extended PLA digestion (636+ strategies)
    # ---------------------------------------------------------------------------
    # ShakeFilter: counts oscillation of mid-direction over half-period window.
    # Source: NV2108004_TX15M_Bonny_LT — suppresses entry when pos() < Len/4.
    "ShakeFilter": [
        {"class": "ShakeFilterStrategy", "module": "trading.strategies_extended",
         "params": {"period": p, "shake_threshold": st, "atr_period": ap}}
        for p in [10, 15, 20, 30]
        for st in [0.25, 0.33, 0.40]
        for ap in [10, 14, 20]
    ],
    # SqrtTimeTrail: trailing stop tightens as sqrt(bars_since_entry) grows.
    # Source: TXAL_1_007_VCP_RangeBreakout — trail = entry + mpp - ATR/sqrt(bars).
    "SqrtTimeTrail": [
        {"class": "SqrtTimeTrailStrategy", "module": "trading.strategies_extended",
         "params": {"breakout_period": bp, "atr_period": ap, "trail_atr_mult": m}}
        for bp in [7, 10, 14, 20]
        for ap in [10, 14, 20]
        for m in [1.0, 1.5, 2.0]
    ],
    # AdaptiveMultiplier: doubles MA lookback period after a losing trade.
    # Source: NV2112008_TX60M_FLT, TXF_MAHL_FDT_1 — forced stronger confirmation.
    "AdaptiveMultiplier": [
        {"class": "AdaptiveMultiplierMAStrategy",
         "module": "trading.strategies_extended",
         "params": {"base_period": bp, "loss_multiplier": lm}}
        for bp in [10, 14, 20, 25]
        for lm in [1.5, 2.0, 2.5]
    ],
    # GoldenRatioMA: MA period pair with phi=1.618 relationship (e.g. 56/91).
    # Source: Drschnabel_TX_trend_oscillation20k_LT — MA(56) vs MA(91).
    "GoldenRatioMA": [
        {"class": "GoldenRatioMAStrategy", "module": "trading.strategies_extended",
         "params": {"fast_period": fp, "slow_period": round(fp * 1.618)}}
        for fp in [21, 34, 55, 89]  # Fibonacci seeds; slow = fast * phi
    ],
    # KPower: directional pressure score abs(LPower - SPower) vs StdDev benchmark.
    # Source: Wesley003_TX_2110KPower_LO — LPower=sum(C-L), SPower=sum(H-C).
    "KPower": [
        {"class": "KPowerStrategy", "module": "trading.strategies_extended",
         "params": {"pressure_period": pp, "std_period": sp,
                    "consecutive_days": cd}}
        for pp in [3, 4, 5]
        for sp in [14, 20, 25]
        for cd in [2, 3]
    ],
    # BarTiming: enters based on when intraday H/L formed relative to session.
    # Source: AVgirl_202106_5K — LowestBar > Lbar signals late-session continuation.
    "BarTiming": [
        {"class": "BarTimingStrategy", "module": "trading.strategies_extended",
         "params": {"session_bars": sb, "lookback": lb}}
        for sb in [26, 48, 78]   # ~1hr / ~2hr / ~3hr sessions on 5-min bars
        for lb in [5, 10, 20]
    ],
}

# Legacy alias for backward compatibility
_LEGACY_TAG_MAP = {
    "ADX": "DMI",
    "BBand": "Bollinger",
    "breakout": "Donchian",
    "open-range": "ORB",
    # Batch 4-6 canonical names
    "shake": "ShakeFilter",
    "sqrt_time": "SqrtTimeTrail",
    "adaptive_ma": "AdaptiveMultiplier",
    "golden_ratio": "GoldenRatioMA",
    "kpower": "KPower",
    "bar_timing": "BarTiming",
}


def generate_strategy_configs_from_catalog(
    index_path: Optional[Path] = None,
    log_path: Optional[Path] = None,
    top_n: int = 30,
) -> List[StrategyConfig]:
    """Generate strategy configurations prioritized by PLA indicator frequency.

    Reads the digestion log, identifies which indicators are most common
    and which are underserved, and returns ``StrategyConfig`` objects
    sorted by corpus frequency (highest first).

    Parameters
    ----------
    index_path : Path, optional
        Legacy parameter (ignored). Kept for backward compatibility.
    log_path : Path, optional
        Path to digestion_log.jsonl.  Defaults to the standard results path.
    top_n : int
        Maximum number of configs to return (default 30).

    Returns
    -------
    list[StrategyConfig]
        Concrete strategy configs ready for instantiation, sorted by priority.
    """
    if log_path is None:
        log_path = _DEFAULT_DIGESTION_LOG

    configs: List[StrategyConfig] = []

    if log_path.exists():
        entries = load_digestion_log(log_path)
        ind_freq = build_indicator_frequency(entries)
        existing_set = set(EXISTING_STRATEGY_TAGS)

        # Untapped indicators first (not yet in strategy pool)
        untapped = [
            (tag, count)
            for tag, count in sorted(ind_freq.items(), key=lambda x: -x[1])
            if tag not in existing_set and count >= 2
        ]
        for tag, count in untapped:
            if tag in TAG_TO_STRATEGY_SPACE:
                for entry in TAG_TO_STRATEGY_SPACE[tag]:
                    configs.append(StrategyConfig(
                        strategy_class=entry["class"],
                        module=entry["module"],
                        params=dict(entry["params"]),
                        pla_tag=tag,
                        priority=count,
                    ))

        # Then covered indicators, ordered by frequency
        for tag in EXISTING_STRATEGY_TAGS:
            freq = ind_freq.get(tag, 0)
            if freq > 0 and tag in TAG_TO_STRATEGY_SPACE:
                for entry in TAG_TO_STRATEGY_SPACE[tag]:
                    configs.append(StrategyConfig(
                        strategy_class=entry["class"],
                        module=entry["module"],
                        params=dict(entry["params"]),
                        pla_tag=tag,
                        priority=freq,
                    ))
    else:
        # No log file -- generate from all known tag spaces equally
        for tag, space in TAG_TO_STRATEGY_SPACE.items():
            for entry in space:
                configs.append(StrategyConfig(
                    strategy_class=entry["class"],
                    module=entry["module"],
                    params=dict(entry["params"]),
                    pla_tag=tag,
                    priority=1,
                ))

    # Sort by priority descending, deduplicate by (class, params)
    configs.sort(key=lambda c: -c.priority)

    seen: set[Tuple[str, str]] = set()
    unique: List[StrategyConfig] = []
    for cfg in configs:
        key = (cfg.strategy_class, str(sorted(cfg.params.items())))
        if key not in seen:
            seen.add(key)
            unique.append(cfg)

    return unique[:top_n]


# ---------------------------------------------------------------------------
# Backward-compatible aliases
# ---------------------------------------------------------------------------

def build_tag_frequency(index_path: Path) -> Dict[str, int]:
    """Legacy wrapper: build frequency from digestion log instead of index."""
    entries = load_digestion_log(_DEFAULT_DIGESTION_LOG)
    return build_indicator_frequency(entries)


def build_combo_frequency(index_path: Path) -> Dict[Tuple[str, ...], int]:
    """Legacy wrapper: build combo frequency from digestion log."""
    entries = load_digestion_log(_DEFAULT_DIGESTION_LOG)
    pairs, _ = build_cooccurrence(entries)
    return {k: v for k, v in pairs.items()}  # type: ignore[misc]


def find_untapped_combinations(
    tag_freq: Dict[str, int],
    combo_freq: Dict[Tuple[str, ...], int],
    existing_tags: List[str],
) -> List[Tuple[str, int]]:
    """Find indicator tags not yet in the strategy pool."""
    existing_set = set(existing_tags)
    untapped = [
        (tag, count)
        for tag, count in tag_freq.items()
        if tag not in existing_set and count >= 2
    ]
    untapped.sort(key=lambda x: -x[1])
    return untapped


def find_untapped_combos(
    combo_freq: Dict[Tuple[str, ...], int],
    existing_tags: List[str],
) -> List[Tuple[Tuple[str, ...], int]]:
    """Find indicator combos where at least one tag is untapped."""
    existing_set = set(existing_tags)
    untapped: List[Tuple[Tuple[str, ...], int]] = []
    for combo, count in combo_freq.items():
        if not all(t in existing_set for t in combo) and count >= 2:
            untapped.append((combo, count))
    untapped.sort(key=lambda x: -x[1])
    return untapped


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser(
        description="PLA pattern catalog -- analyze indicator patterns from digested strategies.",
    )
    parser.add_argument(
        "--log", type=str, default=str(_DEFAULT_DIGESTION_LOG),
        help="Path to digestion_log.jsonl",
    )
    parser.add_argument(
        "--show-combos", action="store_true",
        help="Show indicator combination frequencies",
    )
    parser.add_argument(
        "--generate-configs", action="store_true",
        help="Generate strategy configs for strategy_generator consumption",
    )
    parser.add_argument(
        "--export", action="store_true",
        help="Export catalog to JSON + markdown files",
    )
    parser.add_argument(
        "--top", type=int, default=20,
        help="Number of top results to show (default 20)",
    )
    # Legacy compat
    parser.add_argument("--index", type=str, default=None, help=argparse.SUPPRESS)
    args = parser.parse_args()

    log_path = Path(args.log)

    if args.generate_configs:
        configs = generate_strategy_configs_from_catalog(
            log_path=log_path, top_n=args.top,
        )
        print(f"=== Generated {len(configs)} Strategy Configs (PLA-prioritized) ===\n")
        for i, cfg in enumerate(configs, 1):
            print(
                f"  {i:3d}. [{cfg.pla_tag}] {cfg.strategy_class}("
                f"{', '.join(f'{k}={v}' for k, v in cfg.params.items())}"
                f") priority={cfg.priority}"
            )
        return

    entries = load_digestion_log(log_path)
    catalog = build_catalog(entries)

    print(f"=== PLA Pattern Catalog ({catalog.total_entries} entries analyzed) ===\n")
    print(f"Top {args.top} indicators:")
    covered_set = set(catalog.covered_indicators)
    for tag, count in list(catalog.indicator_frequency.items())[:args.top]:
        status = " [COVERED]" if tag in covered_set else ""
        print(f"  {tag}: {count}{status}")

    if catalog.untapped_indicators:
        print(f"\n=== Untapped Indicators (not in current pool) ===\n")
        for tag, count in catalog.untapped_indicators[:args.top]:
            print(f"  {tag}: {count}")

    if args.show_combos:
        print(f"\n=== Top Indicator Pairs ({len(catalog.pair_cooccurrence)} unique) ===\n")
        for pair, count in list(catalog.pair_cooccurrence.items())[:args.top]:
            print(f"  {pair}: {count}")

        if catalog.untapped_pairs:
            print(f"\n=== Untapped Pairs (at least one indicator not covered) ===\n")
            for pair, count in catalog.untapped_pairs[:args.top]:
                print(f"  {pair}: {count}")

    if args.export:
        export_catalog_json(catalog, _DEFAULT_CATALOG_JSON)
        export_catalog_markdown(catalog, _DEFAULT_CATALOG_MD)
        print(f"\nExported to:")
        print(f"  JSON: {_DEFAULT_CATALOG_JSON}")
        print(f"  MD:   {_DEFAULT_CATALOG_MD}")


if __name__ == "__main__":
    main()
