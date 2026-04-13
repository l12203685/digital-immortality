"""collision_diff.py — Compare two collision JSON reports from organism_interact.py.

Usage:
    python collision_diff.py report1.json report2.json [--output diff.md]
"""
import argparse
import json
import sys
from pathlib import Path


def load_report(path: Path) -> dict:
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON in {path}: {exc}", file=sys.stderr)
        sys.exit(1)


def extract_scenarios(report: dict) -> dict[str, str]:
    """Return {domain: classification} map from a report."""
    scenarios = report.get("scenarios", [])
    if not isinstance(scenarios, list):
        print("Error: 'scenarios' must be a list", file=sys.stderr)
        sys.exit(1)
    result: dict[str, str] = {}
    for s in scenarios:
        domain = s.get("domain", "unknown")
        classification = s.get("classification", "UNKNOWN")
        result[domain] = classification
    return result


def diff_reports(
    map1: dict[str, str], map2: dict[str, str]
) -> dict:
    """Identify flips and unchanged entries between two scenario maps."""
    all_domains = set(map1) | set(map2)
    agree_to_diverge: list[str] = []
    diverge_to_agree: list[str] = []
    unchanged_agree: list[str] = []
    unchanged_diverge: list[str] = []
    only_in_r1: list[str] = []
    only_in_r2: list[str] = []

    for domain in sorted(all_domains):
        c1 = map1.get(domain)
        c2 = map2.get(domain)
        if c1 is None:
            only_in_r2.append(domain)
        elif c2 is None:
            only_in_r1.append(domain)
        elif c1 == c2:
            if c1 == "AGREEMENT":
                unchanged_agree.append(domain)
            else:
                unchanged_diverge.append(domain)
        else:
            if c1 == "AGREEMENT" and c2 == "DIVERGENCE":
                agree_to_diverge.append(domain)
            elif c1 == "DIVERGENCE" and c2 == "AGREEMENT":
                diverge_to_agree.append(domain)
            # other transitions recorded as diverge_to_agree fallback
            else:
                agree_to_diverge.append(domain)

    return {
        "agree_to_diverge": agree_to_diverge,
        "diverge_to_agree": diverge_to_agree,
        "unchanged_agree": unchanged_agree,
        "unchanged_diverge": unchanged_diverge,
        "only_in_r1": only_in_r1,
        "only_in_r2": only_in_r2,
    }


def format_report(
    path1: Path,
    path2: Path,
    report1: dict,
    report2: dict,
    diff: dict,
) -> str:
    rate1 = report1.get("summary", {}).get("agreement_rate", "N/A")
    rate2 = report2.get("summary", {}).get("agreement_rate", "N/A")
    try:
        delta = f"{float(rate2) - float(rate1):+.1f}%"
    except (TypeError, ValueError):
        delta = "N/A"

    lines = [
        "# Collision Report Diff",
        "",
        f"| | Report 1 | Report 2 |",
        f"|---|---|---|",
        f"| File | `{path1.name}` | `{path2.name}` |",
        f"| Agreement Rate | {rate1}% | {rate2}% |",
        f"| Delta | | **{delta}** |",
        "",
    ]

    def section(title: str, domains: list[str], empty_msg: str = "_none_") -> list[str]:
        out = [f"## {title} ({len(domains)})", ""]
        if domains:
            out += [f"- `{d}`" for d in domains]
        else:
            out.append(empty_msg)
        out.append("")
        return out

    lines += section("AGREEMENT → DIVERGENCE (regressions)", diff["agree_to_diverge"])
    lines += section("DIVERGENCE → AGREEMENT (improvements)", diff["diverge_to_agree"])
    lines += section("Unchanged AGREEMENT", diff["unchanged_agree"])
    lines += section("Unchanged DIVERGENCE", diff["unchanged_diverge"])

    if diff["only_in_r1"] or diff["only_in_r2"]:
        lines += section(f"Only in {path1.name}", diff["only_in_r1"])
        lines += section(f"Only in {path2.name}", diff["only_in_r2"])

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Diff two collision JSON reports from organism_interact.py"
    )
    parser.add_argument("report1", type=Path, help="First collision JSON report")
    parser.add_argument("report2", type=Path, help="Second collision JSON report")
    parser.add_argument("--output", type=Path, default=None, help="Write markdown to file")
    args = parser.parse_args()

    r1 = load_report(args.report1)
    r2 = load_report(args.report2)
    map1 = extract_scenarios(r1)
    map2 = extract_scenarios(r2)
    diff = diff_reports(map1, map2)
    md = format_report(args.report1, args.report2, r1, r2, diff)

    if args.output:
        args.output.write_text(md, encoding="utf-8")
        print(f"Diff written to {args.output}")
    else:
        print(md)


if __name__ == "__main__":
    main()
