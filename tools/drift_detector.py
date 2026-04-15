"""
drift_detector.py — B4 Organism Ecosystem drift monitor

Scans collision reports for registered organisms and flags any whose
current AGREE rate has drifted >20 percentage points from baseline.

Supported file patterns (results/ and systems/organisms/):
  collision_*.json  — has summary.agreements / summary.total_scenarios
  dna_core_vs_*.json, organism_*.json, samuel_*.json
      — has interactions[].synthesis (CONVERGE = agree, DIVERGE = disagree)

Usage:
  python tools/drift_detector.py            # print report
  python tools/drift_detector.py --check    # exit 1 if any drift detected
  python tools/drift_detector.py --reset    # re-calculate baselines from scratch
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

RESULTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "results",
)
ORGANISMS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "systems", "organisms",
)
BASELINES_FILE = os.path.join(RESULTS_DIR, "drift_baselines.json")
DRIFT_REPORT_FILE = os.path.join(RESULTS_DIR, "drift_report.json")
DRIFT_JSONL_FILE = os.path.join(RESULTS_DIR, "organism_drift.jsonl")
DRIFT_FLAG_FILE = os.path.join(RESULTS_DIR, "organism_drift_flag.json")

DRIFT_THRESHOLD_PP = 20.0   # percentage points
CONSECUTIVE_DRIFT_WARN = 3  # warn after N consecutive drifted checks

# Documented baselines (override when no file exists yet)
KNOWN_BASELINES = {
    "Samuel": {"agree_count": 16, "total": 40, "agree_rate": 40.0},
}

TZ_TAIPEI = timezone(timedelta(hours=8))


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

def _scan_dir(directory: str) -> list[str]:
    """Return absolute paths of all JSON files in directory (non-recursive)."""
    if not os.path.isdir(directory):
        return []
    return [
        os.path.join(directory, f)
        for f in sorted(os.listdir(directory))
        if f.endswith(".json")
    ]


def _extract_organism_name(filename: str) -> str | None:
    """
    Derive organism name from filename.

    Handles patterns:
      collision_dna_core_vs_Samuel_20260413_035318.json  -> Samuel
      dna_core_vs_Samuel_20260413_005106.json            -> Samuel
      samuel_run_20260413.json                           -> Samuel
      organism_Alice_20260413.json                       -> Alice
    """
    base = os.path.splitext(os.path.basename(filename))[0]

    # collision_*_vs_<Name>_<ts>
    m = re.match(r"collision_.*_vs_([A-Za-z][A-Za-z0-9_]+)_\d{8}_\d{6}$", base)
    if m:
        return m.group(1)

    # *_vs_<Name>_<ts>  (dna_core_vs_Samuel_... style)
    m = re.match(r".*_vs_([A-Za-z][A-Za-z0-9_]+)_\d{8}_\d{6}$", base)
    if m:
        return m.group(1)

    # organism_<Name>_<ts>
    m = re.match(r"organism_([A-Za-z][A-Za-z0-9_]+)_\d{8}_\d{6}$", base)
    if m:
        return m.group(1)

    # <name>_<ts>  (samuel_20260413_035318)
    m = re.match(r"([A-Za-z][A-Za-z0-9_]+)_\d{8}_\d{6}$", base)
    if m:
        return m.group(1).capitalize()

    return None


def _parse_timestamp(ts_str: str) -> datetime | None:
    """Parse ISO timestamp, return tz-aware datetime or None."""
    if not ts_str:
        return None
    try:
        # Python 3.7+ fromisoformat doesn't handle trailing Z
        ts_str = ts_str.replace("Z", "+00:00")
        return datetime.fromisoformat(ts_str)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Agreement extraction
# ---------------------------------------------------------------------------

def _extract_from_summary(data: dict) -> tuple[int, int] | None:
    """
    Extract (agree_count, total) from collision report summary block.
    Returns None if fields are missing.
    """
    summary = data.get("summary", {})

    # Primary: explicit fields
    if "agreements" in summary and "total_scenarios" in summary:
        return int(summary["agreements"]), int(summary["total_scenarios"])

    # Aliases
    for agree_key in ("agree_count", "agree_pct", "agree_rate"):
        if agree_key in summary:
            total = summary.get("total_scenarios") or summary.get("total") or 0
            if total:
                val = summary[agree_key]
                if agree_key in ("agree_pct", "agree_rate"):
                    # stored as percentage float
                    agree_count = round(val / 100.0 * total)
                else:
                    agree_count = int(val)
                return agree_count, int(total)

    return None


def _extract_from_results_array(data: dict) -> tuple[int, int] | None:
    """
    Extract (agree_count, total) from a 'results' array with
    AGREE/DISAGREE string entries.
    """
    results = data.get("results", [])
    if not results:
        return None
    agree = sum(1 for r in results if isinstance(r, str) and r.upper() == "AGREE")
    return agree, len(results)


def _extract_from_interactions(data: dict) -> tuple[int, int] | None:
    """
    Extract (agree_count, total) from interactions[].synthesis.
    CONVERGE in synthesis string = agreement.
    """
    interactions = data.get("interactions", [])
    if not interactions:
        return None
    agree = sum(
        1 for i in interactions
        if isinstance(i.get("synthesis"), str)
        and i["synthesis"].upper().startswith("CONVERGE")
    )
    return agree, len(interactions)


def _extract_agreement(data: dict) -> tuple[int, int] | None:
    """
    Try all extraction strategies in priority order.
    Returns (agree_count, total) or None.
    """
    result = _extract_from_summary(data)
    if result:
        return result

    result = _extract_from_results_array(data)
    if result:
        return result

    result = _extract_from_interactions(data)
    if result:
        return result

    return None


# ---------------------------------------------------------------------------
# Report data structures
# ---------------------------------------------------------------------------

class CollisionRecord:
    """One parsed collision file."""

    def __init__(
        self,
        filepath: str,
        organism: str,
        timestamp: datetime | None,
        agree_count: int,
        total: int,
    ):
        self.filepath = filepath
        self.organism = organism
        self.timestamp = timestamp
        self.agree_count = agree_count
        self.total = total
        self.agree_rate = round(agree_count / total * 100, 2) if total else 0.0

    def __repr__(self) -> str:
        ts = self.timestamp.isoformat() if self.timestamp else "unknown"
        return (
            f"<CollisionRecord organism={self.organism} "
            f"rate={self.agree_rate:.1f}% ({self.agree_count}/{self.total}) ts={ts}>"
        )


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

def load_collision_records(warnings: list[str]) -> dict[str, list[CollisionRecord]]:
    """
    Scan results/ and systems/organisms/ for collision files.
    Returns {organism_name: [CollisionRecord, ...]} sorted by timestamp asc.
    """
    candidates: list[str] = []
    for directory in [RESULTS_DIR, ORGANISMS_DIR]:
        candidates.extend(_scan_dir(directory))

    # Keep only files that match known collision patterns
    def _is_collision_file(path: str) -> bool:
        base = os.path.basename(path)
        return (
            base.startswith("collision_")
            or re.match(r"dna_core_vs_\w+_\d{8}_\d{6}\.json", base) is not None
            or re.match(r"organism_\w+_\d{8}_\d{6}\.json", base) is not None
            or re.match(r"samuel_\w+_\d{8}_\d{6}\.json", base) is not None
        )

    records: dict[str, list[CollisionRecord]] = {}

    for path in candidates:
        if not _is_collision_file(path):
            continue

        organism = _extract_organism_name(path)
        if not organism:
            warnings.append(f"Could not determine organism name: {os.path.basename(path)}")
            continue

        try:
            with open(path, encoding="utf-8") as fh:
                content = fh.read().strip()
            if not content:
                warnings.append(f"Empty file skipped: {os.path.basename(path)}")
                continue
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            warnings.append(f"JSON parse error in {os.path.basename(path)}: {exc}")
            continue
        except OSError as exc:
            warnings.append(f"Cannot read {os.path.basename(path)}: {exc}")
            continue

        extraction = _extract_agreement(data)
        if extraction is None:
            warnings.append(
                f"No agreement data found in {os.path.basename(path)} "
                f"(keys: {list(data.keys())})"
            )
            continue

        agree_count, total = extraction
        ts_str = (data.get("meta") or {}).get("generated_at", "")
        timestamp = _parse_timestamp(ts_str)

        rec = CollisionRecord(
            filepath=path,
            organism=organism,
            timestamp=timestamp,
            agree_count=agree_count,
            total=total,
        )
        records.setdefault(organism, []).append(rec)

    # Sort each organism's records by timestamp ascending (None timestamps go last)
    for name in records:
        records[name].sort(
            key=lambda r: (r.timestamp is None, r.timestamp or datetime.min)
        )

    return records


# ---------------------------------------------------------------------------
# Baseline management
# ---------------------------------------------------------------------------

def load_baselines() -> dict:
    if os.path.isfile(BASELINES_FILE):
        try:
            with open(BASELINES_FILE, encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_baselines(baselines: dict) -> None:
    with open(BASELINES_FILE, "w", encoding="utf-8") as fh:
        json.dump(baselines, fh, indent=2, ensure_ascii=False)


def get_baseline(
    organism: str,
    records: list[CollisionRecord],
    stored: dict,
    reset: bool = False,
) -> dict:
    """
    Return baseline dict: {agree_count, total, agree_rate, source}.
    Priority: stored file > KNOWN_BASELINES > earliest record.
    """
    if not reset and organism in stored:
        return stored[organism]

    if organism in KNOWN_BASELINES:
        return {**KNOWN_BASELINES[organism], "source": "hardcoded"}

    # Fall back to earliest record
    if records:
        earliest = records[0]
        return {
            "agree_count": earliest.agree_count,
            "total": earliest.total,
            "agree_rate": earliest.agree_rate,
            "source": f"earliest_record:{os.path.basename(earliest.filepath)}",
        }

    return {"agree_count": 0, "total": 0, "agree_rate": 0.0, "source": "none"}


# ---------------------------------------------------------------------------
# Drift analysis
# ---------------------------------------------------------------------------

class OrganismDriftResult:
    def __init__(
        self,
        organism: str,
        baseline: dict,
        current: CollisionRecord | None,
        all_records: list[CollisionRecord],
    ):
        self.organism = organism
        self.baseline = baseline
        self.current = current
        self.all_records = all_records

        if current is None:
            self.drift_pp = 0.0
            self.drifted = False
            self.trend = "unknown"
            self.consecutive_drift = 0
        else:
            self.drift_pp = round(current.agree_rate - baseline["agree_rate"], 2)
            self.drifted = abs(self.drift_pp) > DRIFT_THRESHOLD_PP

            # Trend: compare last 3 agree_rates
            rates = [r.agree_rate for r in all_records]
            if len(rates) >= 3:
                recent = rates[-3:]
                if recent[-1] > recent[0]:
                    self.trend = "increasing"
                elif recent[-1] < recent[0]:
                    self.trend = "decreasing"
                else:
                    self.trend = "stable"
            elif len(rates) == 2:
                self.trend = "increasing" if rates[1] > rates[0] else (
                    "decreasing" if rates[1] < rates[0] else "stable"
                )
            else:
                self.trend = "single_sample"

            # Consecutive drift count from most recent backward
            self.consecutive_drift = 0
            for rec in reversed(all_records):
                pp = abs(rec.agree_rate - baseline["agree_rate"])
                if pp > DRIFT_THRESHOLD_PP:
                    self.consecutive_drift += 1
                else:
                    break


def analyze_drift(
    records: dict[str, list[CollisionRecord]],
    stored_baselines: dict,
    reset: bool = False,
) -> list[OrganismDriftResult]:
    results = []
    updated_baselines = dict(stored_baselines)

    for organism, recs in sorted(records.items()):
        baseline = get_baseline(organism, recs, stored_baselines, reset=reset)

        # Persist baseline if not already stored
        if organism not in updated_baselines or reset:
            updated_baselines[organism] = {
                k: v for k, v in baseline.items() if k != "source"
            }

        current = recs[-1] if recs else None
        result = OrganismDriftResult(organism, baseline, current, recs)
        results.append(result)

    save_baselines(updated_baselines)
    return results


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def _sign(val: float) -> str:
    return f"+{val:.1f}" if val >= 0 else f"{val:.1f}"


def print_report(drift_results: list[OrganismDriftResult], warnings: list[str]) -> None:
    now = datetime.now(TZ_TAIPEI)
    print(f"\n=== Drift Detector Report  [{now.strftime('%Y-%m-%d %H:%M %z')}] ===\n")

    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  ! {w}")
        print()

    any_drift = False

    for dr in drift_results:
        base = dr.baseline
        print(f"Organism: {dr.organism}")
        print(
            f"  Baseline: {base['agree_rate']:.1f}% AGREE "
            f"({base['agree_count']}/{base['total']})"
            f"  [source: {base.get('source', 'unknown')}]"
        )

        if dr.current is None:
            print("  Current:  NO DATA")
            print("  Drift:    N/A")
        else:
            cur = dr.current
            ts_str = (
                cur.timestamp.astimezone(TZ_TAIPEI).strftime("%Y-%m-%d %H:%M")
                if cur.timestamp else "unknown time"
            )
            print(
                f"  Current:  {cur.agree_rate:.1f}% AGREE "
                f"({cur.agree_count}/{cur.total})  [{ts_str}]"
            )

            status = "DRIFT DETECTED" if dr.drifted else "WITHIN TOLERANCE"
            print(f"  Drift:    {_sign(dr.drift_pp)}pp — {status}")
            print(f"  Trend:    {dr.trend}  (over {len(dr.all_records)} records)")

            if dr.consecutive_drift >= CONSECUTIVE_DRIFT_WARN:
                print(
                    f"  WARNING:  Drifted for {dr.consecutive_drift} consecutive checks"
                )

            if dr.drifted:
                any_drift = True

        print()

    summary = "DRIFT DETECTED in one or more organisms." if any_drift else "All organisms WITHIN TOLERANCE."
    print(f"Summary: {summary}")
    print(f"Threshold: {DRIFT_THRESHOLD_PP:.0f}pp absolute\n")


def save_report(
    drift_results: list[OrganismDriftResult],
    warnings: list[str],
) -> None:
    now = datetime.now(TZ_TAIPEI)
    report = {
        "generated_at": now.isoformat(),
        "threshold_pp": DRIFT_THRESHOLD_PP,
        "warnings": warnings,
        "organisms": [],
    }

    any_drift = False
    for dr in drift_results:
        base = dr.baseline
        cur = dr.current

        entry: dict = {
            "name": dr.organism,
            "baseline": {
                "agree_count": base["agree_count"],
                "total": base["total"],
                "agree_rate": base["agree_rate"],
                "source": base.get("source", "unknown"),
            },
            "record_count": len(dr.all_records),
            "trend": dr.trend,
        }

        if cur is not None:
            entry["current"] = {
                "agree_count": cur.agree_count,
                "total": cur.total,
                "agree_rate": cur.agree_rate,
                "timestamp": cur.timestamp.isoformat() if cur.timestamp else None,
                "file": os.path.basename(cur.filepath),
            }
            entry["drift_pp"] = dr.drift_pp
            entry["drifted"] = dr.drifted
            entry["consecutive_drift_checks"] = dr.consecutive_drift
            if dr.drifted:
                any_drift = True
        else:
            entry["current"] = None
            entry["drift_pp"] = None
            entry["drifted"] = False
            entry["consecutive_drift_checks"] = 0

        report["organisms"].append(entry)

    report["any_drift"] = any_drift

    with open(DRIFT_REPORT_FILE, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)

    print(f"Report saved: {DRIFT_REPORT_FILE}")

    _append_jsonl(report)
    _write_flag(report)


def _append_jsonl(report: dict) -> None:
    """Append one compact JSONL line per drift_detector run for time-series.

    Each line captures: generated_at, any_drift, and per-organism summary.
    """
    line = {
        "generated_at": report["generated_at"],
        "threshold_pp": report["threshold_pp"],
        "any_drift": report.get("any_drift", False),
        "organisms": [
            {
                "name": o["name"],
                "baseline_rate": o["baseline"]["agree_rate"],
                "current_rate": (o.get("current") or {}).get("agree_rate"),
                "drift_pp": o.get("drift_pp"),
                "drifted": o.get("drifted", False),
                "trend": o.get("trend"),
                "record_count": o.get("record_count", 0),
                "consecutive_drift_checks": o.get("consecutive_drift_checks", 0),
            }
            for o in report["organisms"]
        ],
    }
    try:
        with open(DRIFT_JSONL_FILE, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(line, ensure_ascii=False) + "\n")
        print(f"JSONL appended: {DRIFT_JSONL_FILE}")
    except OSError as exc:
        print(f"  ! Failed to append JSONL: {exc}")


def _write_flag(report: dict) -> None:
    """Write a small flag file consumed by the dashboard /api/statusline.

    Presence alone is not enough — the dashboard reads ``red_flag`` to decide
    whether to raise an alert. We always rewrite so the flag reflects the
    latest run (avoids stale red after drift resolves).
    """
    drifted = [
        o for o in report["organisms"]
        if o.get("drifted") or o.get("consecutive_drift_checks", 0) >= CONSECUTIVE_DRIFT_WARN
    ]
    flag = {
        "generated_at": report["generated_at"],
        "red_flag": bool(drifted),
        "threshold_pp": report["threshold_pp"],
        "drifted_organisms": [
            {
                "name": o["name"],
                "drift_pp": o.get("drift_pp"),
                "consecutive_drift_checks": o.get("consecutive_drift_checks", 0),
            }
            for o in drifted
        ],
        "total_organisms": len(report["organisms"]),
    }
    try:
        with open(DRIFT_FLAG_FILE, "w", encoding="utf-8") as fh:
            json.dump(flag, fh, indent=2, ensure_ascii=False)
        print(f"Flag written: {DRIFT_FLAG_FILE} (red_flag={flag['red_flag']})")
    except OSError as exc:
        print(f"  ! Failed to write flag: {exc}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect agreement-rate drift in organism collision reports."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if any organism has drifted beyond threshold (for CI/cron).",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Recalculate baselines from scratch, ignoring stored baselines.",
    )
    args = parser.parse_args()

    warnings: list[str] = []

    # Load data
    records = load_collision_records(warnings)

    if not records:
        print("No collision records found.")
        print(f"  Searched: {RESULTS_DIR}")
        if os.path.isdir(ORGANISMS_DIR):
            print(f"            {ORGANISMS_DIR}")
        print("  Expected patterns: collision_*.json, dna_core_vs_*.json, organism_*.json")
        return 0

    stored_baselines = {} if args.reset else load_baselines()
    drift_results = analyze_drift(records, stored_baselines, reset=args.reset)

    print_report(drift_results, warnings)
    save_report(drift_results, warnings)

    any_drift = any(dr.drifted for dr in drift_results)

    if args.check:
        return 1 if any_drift else 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
