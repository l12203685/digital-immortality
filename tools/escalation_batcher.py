"""
Escalation Batcher — batches ESCALATE-class sign-off items into a single
Discord message on a cadence. Default: 1 batch / 4 hours.

Goal: Edward never sees individual "please approve X" pings. He sees one
summary every N hours with a numbered list of strategic decisions that
require his human judgment. Everything else auto-approves.

Stdlib only (uses urllib.request for the Discord webhook).

CLI:
    python -m tools.escalation_batcher               # check + send if due
    python -m tools.escalation_batcher --force       # send regardless of cadence
    python -m tools.escalation_batcher --dry-run     # print message, don't post
    python -m tools.escalation_batcher --cadence 8   # override hours
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

from tools.sign_off_manager import (
    Decision,
    list_pending,
    _iso,
    _now_taipei,
    _parse_iso,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = REPO_ROOT / "results" / "escalation_state.json"

# Same #永生樹 webhook used by recursive_daemon + trading/engine.
# Read from env var. If unset, posting is skipped (tracked via _webhook_configured).
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK_TREE", "")

DEFAULT_CADENCE_HOURS = 4


def _load_state() -> dict:
    if not STATE_PATH.exists():
        return {"last_batch_ts": None, "last_message": "", "batches_sent": 0}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"last_batch_ts": None, "last_message": "", "batches_sent": 0}


def _save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2),
                          encoding="utf-8")


def filter_escalate_pending(decisions: List[Decision]) -> List[Decision]:
    return [d for d in decisions
            if d.category == "ESCALATE" and d.status == "PENDING"]


def build_message(items: List[Decision]) -> str:
    if not items:
        return ""
    header = f"你有 {len(items)} 件事要核章 (ESCALATE — 不會自動通過)："
    lines = [header, ""]
    for i, d in enumerate(items, 1):
        lines.append(f"{i}. [{d.uid}] {d.title}")
        lines.append(f"   推薦: {d.recommendation}")
        lines.append(f"   為什麼: {d.why[:180]}")
        lines.append(f"   可逆性: {d.reversibility}")
        lines.append("")
    lines.append("核章: `python -m tools.sign_off_manager --mark <uid> APPROVED --who edward`")
    lines.append("拒絕: `python -m tools.sign_off_manager --reject <uid> --reason \"...\"`")
    return "\n".join(lines)


def is_due(state: dict, cadence_hours: int) -> bool:
    last_ts = state.get("last_batch_ts")
    if not last_ts:
        return True
    last = _parse_iso(last_ts)
    if last is None:
        return True
    return _now_taipei() - last >= timedelta(hours=cadence_hours)


def post_discord(message: str) -> bool:
    if not DISCORD_WEBHOOK:
        print("[escalation_batcher] DISCORD_WEBHOOK_TREE unset; skipping post", file=sys.stderr)
        return False
    payload = json.dumps({"content": message[:1900], "username": "SignOffBatcher"}).encode("utf-8")
    req = urllib.request.Request(
        DISCORD_WEBHOOK,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        print(f"[escalation_batcher] Discord post failed: {e}", file=sys.stderr)
        return False


def run_once(cadence_hours: int = DEFAULT_CADENCE_HOURS,
             force: bool = False,
             dry_run: bool = False) -> dict:
    decisions = list_pending()
    items = filter_escalate_pending(decisions)
    state = _load_state()

    result = {
        "items": len(items),
        "sent": False,
        "dry_run": dry_run,
        "due": force or is_due(state, cadence_hours),
        "ts": _iso(_now_taipei()),
    }

    if not items:
        result["reason"] = "no-escalate-items"
        return result
    if not result["due"]:
        result["reason"] = "cadence-not-met"
        return result

    message = build_message(items)
    result["message"] = message

    if dry_run:
        result["reason"] = "dry-run"
        return result

    ok = post_discord(message)
    if ok:
        state["last_batch_ts"] = _iso(_now_taipei())
        state["last_message"] = message
        state["batches_sent"] = state.get("batches_sent", 0) + 1
        _save_state(state)
        result["sent"] = True
    else:
        result["reason"] = "post-failed"
    return result


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(prog="escalation_batcher",
                                description="Batched Discord escalation for sign-off items")
    p.add_argument("--cadence", type=int, default=DEFAULT_CADENCE_HOURS,
                   help="Hours between batches (default: 4)")
    p.add_argument("--force", action="store_true",
                   help="Send regardless of cadence")
    p.add_argument("--dry-run", action="store_true",
                   help="Print message without posting")
    args = p.parse_args(argv)

    result = run_once(cadence_hours=args.cadence,
                      force=args.force,
                      dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
