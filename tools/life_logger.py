#!/usr/bin/env python3
"""
life_logger.py -- Log life events for precommit compliance tracking.

CLI:
  python life_logger.py <event> [--note "..."]
  python life_logger.py --status

Events: exercise, lunch, deep-work, morning-drink, portfolio-check
Logs to results/life_events.jsonl. Stdlib only, <80 lines.
"""
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

TZ = timezone(timedelta(hours=8))
ROOT = Path(__file__).resolve().parent.parent
LOG_FILE = ROOT / "results" / "life_events.jsonl"
VALID_EVENTS = ["exercise", "lunch", "deep-work", "morning-drink", "portfolio-check"]

RULE_MAP = {
    1: {"name": "Exercise", "events": ["exercise"]},
    2: {"name": "Lunch", "events": ["lunch"]},
    3: {"name": "Deep Work Block", "events": ["deep-work"]},
    4: {"name": "Morning Drink", "events": ["morning-drink"]},
    5: {"name": "Portfolio Check", "events": ["portfolio-check"]},
}


def log_event(event: str, note: str = "") -> None:
    now = datetime.now(TZ).isoformat(timespec="seconds")
    entry = {"event": event, "timestamp": now, "note": note}
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"Logged: {event} at {now}")


def today_events() -> list[dict]:
    if not LOG_FILE.exists():
        return []
    today_str = datetime.now(TZ).strftime("%Y-%m-%d")
    entries = []
    for line in LOG_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        entry = json.loads(line)
        if entry["timestamp"].startswith(today_str):
            entries.append(entry)
    return entries


def show_status() -> None:
    entries = today_events()
    logged = {e["event"] for e in entries}
    today = datetime.now(TZ).strftime("%Y-%m-%d")
    print(f"Life Event Status for {today}\n")
    for rid, rule in RULE_MAP.items():
        matched = [ev for ev in rule["events"] if ev in logged]
        status = "DONE" if matched else "PENDING"
        print(f"  [{status:7s}] {rid}. {rule['name']}")
    done = sum(1 for r in RULE_MAP.values() if any(e in logged for e in r["events"]))
    print(f"\n  {done}/{len(RULE_MAP)} completed today")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(f"Usage: python life_logger.py <event> [--note '...']\n"
              f"       python life_logger.py --status\n"
              f"Events: {', '.join(VALID_EVENTS)}")
        sys.exit(1)
    if args[0] == "--status":
        show_status()
        return
    event = args[0]
    if event not in VALID_EVENTS:
        print(f"Unknown event: {event}. Valid: {', '.join(VALID_EVENTS)}")
        sys.exit(1)
    note = args[args.index("--note") + 1] if "--note" in args else ""
    log_event(event, note)


if __name__ == "__main__":
    main()
