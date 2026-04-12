"""
Parse PLA logic index to catalog untapped indicator patterns.

Reads E:/pla_md/logic/LOGIC_INDEX.md and builds a frequency table of
indicator tags across all 950 extracted strategy logics. Identifies
indicator combinations not yet represented in the active strategy pool.

Usage:
    python trading/pla_pattern_catalog.py
    python trading/pla_pattern_catalog.py --show-combos
"""

import argparse
import re
from collections import Counter
from pathlib import Path
from typing import List


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
        "--top", type=int, default=20,
        help="Number of top results to show (default 20)",
    )
    args = parser.parse_args()

    index_path = Path(args.index)
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
