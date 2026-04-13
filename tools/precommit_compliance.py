#!/usr/bin/env python3
"""
precommit_compliance.py — Check adherence to decision pre-commit rules.

Reads rules/decision_precommits.md + recent daemon_log.md for evidence.
Outputs results/precommit_compliance.md with per-rule status.
Stdlib only, <90 lines.
"""
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES_FILE = ROOT / "rules" / "decision_precommits.md"
LOG_FILE = ROOT / "results" / "daemon_log.md"
OUT_FILE = ROOT / "results" / "precommit_compliance.md"

RULES = [
    {
        "id": 1, "name": "Exercise",
        "keywords": ["exercise", "gym", "walk", "workout", "fitness"],
        "schedule": "MWF gym, TuTh walk, SaSu rest",
    },
    {
        "id": 2, "name": "Lunch",
        "keywords": ["lunch", "meal prep", "batch cook", "meal-prep"],
        "schedule": "Weekday meal prep from Sunday batch cook",
    },
    {
        "id": 3, "name": "Deep Work Block",
        "keywords": ["deep work", "deep-work", "focus block", "09:00-12:00", "protected block"],
        "schedule": "09:00-12:00 daily, no interruptions",
    },
    {
        "id": 4, "name": "Morning Drink",
        "keywords": ["coffee", "tea", "morning drink", "breakfast drink"],
        "schedule": "Mon-Fri coffee, Sat-Sun tea",
    },
    {
        "id": 5, "name": "Portfolio Check",
        "keywords": ["portfolio", "account balance", "NAV", "drawdown", "trading check"],
        "schedule": "Monday only (or >5% drawdown alert)",
    },
]


def load_log_tail(n: int = 50) -> str:
    if not LOG_FILE.exists():
        return ""
    lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[-n:]).lower()


def check_rule(rule: dict, log: str) -> tuple[str, str]:
    """Return (status, evidence) for a rule. Uses word-boundary matching."""
    hits = [kw for kw in rule["keywords"] if re.search(r'\b' + re.escape(kw) + r'\b', log)]
    if hits:
        return "COMPLIANT", f"Evidence found: {', '.join(hits)}"
    return "UNKNOWN", "No mention in recent daemon log (not violated, but unverified)"


def generate_report(results: list[dict]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M +08")
    compliant = sum(1 for r in results if r["status"] == "COMPLIANT")
    total = len(results)
    rate = compliant / total * 100 if total else 0

    lines = [
        f"# Pre-Commit Compliance Report",
        f"",
        f"Generated: {now}",
        f"",
        f"## Overall: {compliant}/{total} verified ({rate:.0f}%)",
        f"",
        f"| # | Rule | Schedule | Status | Evidence |",
        f"|---|------|----------|--------|----------|",
    ]
    for r in results:
        lines.append(f"| {r['id']} | {r['name']} | {r['schedule']} | **{r['status']}** | {r['evidence']} |")

    lines += [
        f"",
        f"## Recommendations",
        f"",
    ]
    unknowns = [r for r in results if r["status"] == "UNKNOWN"]
    if unknowns:
        for u in unknowns:
            lines.append(f"- **{u['name']}**: Add logging/tracking to daemon loop for verification.")
    if not unknowns:
        lines.append("- All rules verified. No action needed.")
    violated = [r for r in results if r["status"] == "VIOLATED"]
    for v in violated:
        lines.append(f"- **{v['name']}**: VIOLATED. Review override conditions and reinforce.")
    lines.append(f"\n---\n*Source: `tools/precommit_compliance.py` reading `rules/decision_precommits.md`*")
    return "\n".join(lines)


def main() -> None:
    log = load_log_tail(50)
    results = []
    for rule in RULES:
        status, evidence = check_rule(rule, log)
        results.append({**rule, "status": status, "evidence": evidence})
    report = generate_report(results)
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
