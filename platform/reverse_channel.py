#!/usr/bin/env python3
"""Reverse channel sender — agent → web_outbox.jsonl.

Appends a reply entry to C:/Users/admin/staging/web_outbox.jsonl
so the mission control /api/outbox endpoint can stream it to the voice.html UI.

Entry schema (same as what /api/outbox serves):
    {"ts": ISO8601, "channel": str, "text": str, "status": "posted"}

Usage:
    python reverse_channel.py "reply text here"
    python reverse_channel.py --text "reply text here" [--channel mission_control]

In-process usage:
    from platform.reverse_channel import send
    send("cycle 367 complete — B4 ACK received")
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

OUTBOX = Path(r"C:\Users\admin\staging\web_outbox.jsonl")
TAIPEI = timezone(timedelta(hours=8))


def send(text: str, channel: str = "mission_control") -> dict:
    """Append one reply to web_outbox.jsonl.  Returns the written entry."""
    entry = {
        "ts": datetime.now(TAIPEI).isoformat(timespec="microseconds"),
        "channel": channel,
        "text": text,
        "status": "posted",
    }
    OUTBOX.parent.mkdir(parents=True, exist_ok=True)
    with OUTBOX.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write a reply to web_outbox.jsonl (reverse channel)"
    )
    parser.add_argument("text", nargs="?", help="reply text (positional)")
    parser.add_argument("--text", dest="text_kw", help="reply text (keyword)")
    parser.add_argument(
        "--channel", default="mission_control", help="channel label (default: mission_control)"
    )
    args = parser.parse_args()

    text = args.text or args.text_kw
    if not text:
        parser.error("provide reply text as positional arg or --text")

    entry = send(text.strip(), channel=args.channel)
    print(json.dumps(entry, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
