"""
Parse PLA logic index to catalog untapped indicator patterns.

Reads E:/pla_md/logic/LOGIC_INDEX.md and builds a frequency table of
indicator tags across all 950 extracted strategy logics. Identifies
indicator combinations not yet represented in the active strategy pool.

Also provides ``generate_strategy_configs_from_catalog()`` which maps
untapped PLA tags to concrete strategy class + parameter-space entries
that ``strategy_generator.py`` can consume.

Usage:
    python trading/pla_pattern_catalog.py
    python trading/pla_pattern_catalog.py --show-combos
    python trading/pla_pattern_catalog.py --generate-configs
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# Tags corresponding to strategies already in the pool
EXISTING_STRATEGY_TAGS = [
    "MA",           # DualMA
    "breakout",     # Donchian, DonchianConfirmed
    "BBand",        # BollingerMeanReversion
    "RSI",          # RSIFilter
    # New extended strategies (strategies_extended.py)
    "CCI",
    "ADX",          # DMIStrategy
    "MACD",
    "open-range",   # ORBStrategy
    # Keltner is tagged as ATR+MA in PLA corpus
]


def build_tag_frequency(index_path: Path) -> dict[str, int]:
    """Count tag frequencies across all logic file entries in LOGIC_INDEX.md.

    Parses the markdown table rows and extracts the Tags column.
    Returns a Counter mapping tag -> count.
    """
    if not index_path.exists():
        raise FileNotFoundError(f"Index file not found: {index_path}")

    text = index_path.read_text(encoding="utf-8")
    freq: Counter[str] = Counter()

    # Match table rows: | # | Strategy | Direction | Timeframe | Complex | Tags |
    row_pattern = re.compile(
        r"^\|\s*\d+\s*\|"       # row number
        r"[^|]*\|"              # strategy name
        r"[^|]*\|"              # direction
        r"[^|]*\|"              # timeframe
        r"[^|]*\|"              # complex flag
        r"\s*([^|]*)\s*\|",     # tags (capture group)
        re.MULTILINE,
    )

    for match in row_pattern.finditer(text):
        tags_str = match.group(1).strip()
        if not tags_str:
            continue
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]
        for tag in tags:
            freq[tag] += 1

    return dict(freq)


def build_combo_frequency(index_path: Path) -> dict[tuple[str, ...], int]:
    """Count co-occurring tag combinations (pairs and triples).

    Returns a Counter of sorted tag tuples -> count.
    """
    if not index_path.exists():
        raise FileNotFoundError(f"Index file not found: {index_path}")

    text = index_path.read_text(encoding="utf-8")
    combo_freq: Counter[tuple[str, ...]] = Counter()

    row_pattern = re.compile(
        r"^\|\s*\d+\s*\|"
        r"[^|]*\|"
        r"[^|]*\|"
        r"[^|]*\|"
        r"[^|]*\|"
        r"\s*([^|]*)\s*\|",
        re.MULTILINE,
    )

    for match in row_pattern.finditer(text):
        tags_str = match.group(1).strip()
        if not tags_str:
            continue
        tags = sorted(set(t.strip() for t in tags_str.split(",") if t.strip()))
        if len(tags) < 2:
            continue
        # Record pairs
        for i in range(len(tags)):
            for j in range(i + 1, len(tags)):
                combo_freq[(tags[i], tags[j])] += 1

    return dict(combo_freq)


def find_untapped_combinations(
    tag_freq: dict[str, int],
    combo_freq: dict[tuple[str, ...], int],
    existing_tags: List[str],
) -> List[tuple[str, int]]:
    """Find indicator tags and combos in PLA files not yet in the strategy pool.

    Returns sorted list of (tag_or_combo, count) for tags NOT in existing_tags.
    """
    untapped: List[tuple[str, int]] = []

    # Single tags not covered
    for tag, count in tag_freq.items():
        if tag not in existing_tags and count >= 3:  # minimum threshold
            untapped.append((tag, count))

    untapped.sort(key=lambda x: -x[1])
    return untapped


def find_untapped_combos(
    combo_freq: dict[tuple[str, ...], int],
    existing_tags: List[str],
) -> List[tuple[tuple[str, ...], int]]:
    """Find indicator combos where at least one tag is untapped."""
    untapped: List[tuple[tuple[str, ...], int]] = []
    existing_set = set(existing_tags)

    for combo, count in combo_freq.items():
        # Include combos where not ALL tags are already covered
        if not all(t in existing_set for t in combo) and count >= 3:
            untapped.append((combo, count))

    untapped.sort(key=lambda x: -x[1])
    return untapped


# ---------------------------------------------------------------------------
# Tag → Strategy class mapping for config generation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class StrategyConfig:
    """Immutable description of a strategy to instantiate."""

    strategy_class: str          # e.g. "CCIStrategy"
    module: str                  # e.g. "trading.strategies_extended"
    params: Dict[str, Any]       # constructor kwargs
    pla_tag: str                 # originating PLA tag
    priority: int = 0            # higher = more PLA corpus support


# Mapping from PLA tag strings to (class_name, module, parameter_space).
# Each entry is a list of representative parameter sets for that indicator family.
TAG_TO_STRATEGY_SPACE: Dict[str, List[Dict[str, Any]]] = {
    "CCI": [
        {"class": "CCIStrategy", "module": "trading.strategies_extended",
         "params": {"period": p, "threshold": t}}
        for p in [14, 20, 25, 30]
        for t in [80.0, 100.0, 120.0, 150.0]
    ],
    "ADX": [
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
    "open-range": [
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
    "BBand": [
        {"class": "BollingerMeanReversion", "module": "trading.strategies",
         "params": {"lookback": lb, "num_std": ns, "trend_lookback": tl, "trend_threshold": tt}}
        for lb in [15, 20, 25, 30]
        for ns in [1.5, 2.0, 2.5]
        for tl in [40, 50, 60]
        for tt in [0.001, 0.003, 0.005]
    ],
    "breakout": [
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
}


def generate_strategy_configs_from_catalog(
    index_path: Optional[Path] = None,
    top_n: int = 30,
) -> List[StrategyConfig]:
    """Generate strategy configurations prioritized by untapped PLA patterns.

    Reads the PLA logic index, identifies which indicator tags are underserved
    in the current pool, and returns a list of ``StrategyConfig`` objects
    sorted by PLA corpus frequency (highest first).

    Parameters
    ----------
    index_path : Path, optional
        Path to LOGIC_INDEX.md.  Defaults to ``E:/pla_md/logic/LOGIC_INDEX.md``.
    top_n : int
        Maximum number of configs to return (default 30).

    Returns
    -------
    list[StrategyConfig]
        Concrete strategy configs ready for instantiation, sorted by priority.
    """
    if index_path is None:
        index_path = Path("E:/pla_md/logic/LOGIC_INDEX.md")

    configs: List[StrategyConfig] = []

    # If the index file is available, prioritize untapped tags
    if index_path.exists():
        tag_freq = build_tag_frequency(index_path)
        untapped = find_untapped_combinations(tag_freq, {}, EXISTING_STRATEGY_TAGS)

        # Untapped tags first (not yet in strategy pool)
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

        # Then covered tags, ordered by frequency (more PLA support = higher value)
        for tag in EXISTING_STRATEGY_TAGS:
            freq = tag_freq.get(tag, 0)
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
        # No index file available — generate from all known tag spaces equally
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PLA logic pattern catalog — identify untapped indicator patterns.",
    )
    parser.add_argument(
        "--index", type=str, default="E:/pla_md/logic/LOGIC_INDEX.md",
        help="Path to LOGIC_INDEX.md",
    )
    parser.add_argument(
        "--show-combos", action="store_true",
        help="Also show tag combination frequencies",
    )
    parser.add_argument(
        "--generate-configs", action="store_true",
        help="Generate strategy configs from catalog (for strategy_generator consumption)",
    )
    parser.add_argument(
        "--top", type=int, default=20,
        help="Number of top results to show (default 20)",
    )
    args = parser.parse_args()

    index_path = Path(args.index)

    if args.generate_configs:
        configs = generate_strategy_configs_from_catalog(
            index_path=index_path, top_n=args.top,
        )
        print(f"=== Generated {len(configs)} Strategy Configs (PLA-prioritized) ===\n")
        for i, cfg in enumerate(configs, 1):
            print(
                f"  {i:3d}. [{cfg.pla_tag}] {cfg.strategy_class}("
                f"{', '.join(f'{k}={v}' for k, v in cfg.params.items())}"
                f") priority={cfg.priority}"
            )
        return

    freq = build_tag_frequency(index_path)

    print(f"=== PLA Logic Index Tag Frequency ({sum(freq.values())} total tag occurrences) ===\n")
    print(f"Top {args.top} indicator tags:")
    for tag, count in sorted(freq.items(), key=lambda x: -x[1])[:args.top]:
        covered = " [COVERED]" if tag in EXISTING_STRATEGY_TAGS else ""
        print(f"  {tag}: {count}{covered}")

    print(f"\n=== Untapped Single Tags (not in current pool, count >= 3) ===\n")
    untapped = find_untapped_combinations(freq, {}, EXISTING_STRATEGY_TAGS)
    for tag, count in untapped[:args.top]:
        print(f"  {tag}: {count}")

    if args.show_combos:
        combo_freq = build_combo_frequency(index_path)
        print(f"\n=== Top Tag Combinations ({len(combo_freq)} unique pairs) ===\n")
        for combo, count in sorted(combo_freq.items(), key=lambda x: -x[1])[:args.top]:
            print(f"  {' + '.join(combo)}: {count}")

        print(f"\n=== Untapped Combos (at least one tag not covered) ===\n")
        untapped_combos = find_untapped_combos(combo_freq, EXISTING_STRATEGY_TAGS)
        for combo, count in untapped_combos[:args.top]:
            print(f"  {' + '.join(combo)}: {count}")


if __name__ == "__main__":
    main()
