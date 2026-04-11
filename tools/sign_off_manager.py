"""
Auto Sign-Off Batch System — sign_off_manager
=============================================

Edward (chairman) should not run operational decisions. The agent batches
decisions into a daily sign-off file with its recommendation pre-filled.
If Edward does not reject within N hours, the recommendation is auto-applied.

Default action = proceed. Stop pattern = Edward says no.

Schema of each decision block (Markdown section):

    ## Decision <n>: <title>
    - uid: <uuid>
    - Status: PENDING | APPROVED | REJECTED | AUTO_APPLIED | IN_PROGRESS | EXPIRED
    - Category: AUTO | ESCALATE
    - Posted: <iso ts>
    - Auto-approve at: <iso ts>
    - Recommendation: <agent pick>
    - Why: <reasoning>
    - Alternatives considered: <pipe-separated>
    - Impact if approved: <pipe-separated>
    - Reversibility: high | medium | low
    - One-line dismiss: <git revert ... or n/a>

CLI:
    python -m tools.sign_off_manager --add --title "X" --recommendation "Y" \
        --why "Z" --reversibility high [--category AUTO|ESCALATE] \
        [--alternatives "a1|a2"] [--impact "i1|i2"] [--default-hours 24]
    python -m tools.sign_off_manager --list [--json]
    python -m tools.sign_off_manager --apply-expired
    python -m tools.sign_off_manager --reject <uid> [--reason "..."]
    python -m tools.sign_off_manager --mark <uid> <status> [--who edward|agent]
    python -m tools.sign_off_manager --cleanup [--days 14]

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
PENDING_PATH = REPO_ROOT / "staging" / "pending_sign_off.md"
ARCHIVE_PATH = REPO_ROOT / "staging" / "sign_off_archive.md"

TAIPEI = timezone(timedelta(hours=8))

VALID_STATUS = {"PENDING", "APPROVED", "REJECTED", "AUTO_APPLIED",
                "IN_PROGRESS", "EXPIRED"}
VALID_CATEGORY = {"AUTO", "ESCALATE"}
VALID_REVERSIBILITY = {"high", "medium", "low"}


# --------------------------------------------------------------------------- #
# Model                                                                       #
# --------------------------------------------------------------------------- #

@dataclass
class Decision:
    uid: str
    title: str
    status: str
    category: str
    posted: str
    auto_approve_at: str
    recommendation: str
    why: str
    alternatives: List[str] = field(default_factory=list)
    impact: List[str] = field(default_factory=list)
    reversibility: str = "medium"
    dismiss: str = "n/a"
    reject_reason: str = ""
    resolved_by: str = ""

    def to_markdown(self, index: int) -> str:
        alt = " | ".join(self.alternatives) if self.alternatives else "(none)"
        imp = " | ".join(self.impact) if self.impact else "(none)"
        lines = [
            f"## Decision {index}: {self.title}",
            f"- uid: {self.uid}",
            f"- Status: {self.status}",
            f"- Category: {self.category}",
            f"- Posted: {self.posted}",
            f"- Auto-approve at: {self.auto_approve_at}",
            f"- Recommendation: {self.recommendation}",
            f"- Why: {self.why}",
            f"- Alternatives considered: {alt}",
            f"- Impact if approved: {imp}",
            f"- Reversibility: {self.reversibility}",
            f"- One-line dismiss: {self.dismiss}",
        ]
        if self.reject_reason:
            lines.append(f"- Reject reason: {self.reject_reason}")
        if self.resolved_by:
            lines.append(f"- Resolved by: {self.resolved_by}")
        return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- #
# Parse / serialize                                                           #
# --------------------------------------------------------------------------- #

_DECISION_RE = re.compile(r"^## Decision \d+: (?P<title>.+)$")


def _now_taipei() -> datetime:
    return datetime.now(TAIPEI)


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M Taipei")


def _parse_iso(s: str) -> Optional[datetime]:
    s = s.strip()
    if not s or s == "(none)":
        return None
    m = re.match(r"(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2})", s)
    if not m:
        return None
    dt = datetime.strptime(f"{m.group(1)} {m.group(2)}", "%Y-%m-%d %H:%M")
    return dt.replace(tzinfo=TAIPEI)


def _parse_file(path: Path) -> List[Decision]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    blocks: List[List[str]] = []
    current: List[str] = []
    for line in text.splitlines():
        if _DECISION_RE.match(line):
            if current:
                blocks.append(current)
            current = [line]
        elif current:
            current.append(line)
    if current:
        blocks.append(current)

    decisions: List[Decision] = []
    for block in blocks:
        title_match = _DECISION_RE.match(block[0])
        if not title_match:
            continue
        title = title_match.group("title").strip()
        fields = {}
        for line in block[1:]:
            m = re.match(r"^- ([A-Za-z][A-Za-z \-]*): (.*)$", line)
            if m:
                fields[m.group(1).strip().lower()] = m.group(2).strip()
        uid = fields.get("uid", "")
        if not uid:
            continue
        alt_raw = fields.get("alternatives considered", "")
        alternatives = (
            [a.strip() for a in alt_raw.split("|") if a.strip() and alt_raw != "(none)"]
        )
        imp_raw = fields.get("impact if approved", "")
        impact = (
            [a.strip() for a in imp_raw.split("|") if a.strip() and imp_raw != "(none)"]
        )
        decisions.append(Decision(
            uid=uid,
            title=title,
            status=fields.get("status", "PENDING"),
            category=fields.get("category", "AUTO"),
            posted=fields.get("posted", ""),
            auto_approve_at=fields.get("auto-approve at", ""),
            recommendation=fields.get("recommendation", ""),
            why=fields.get("why", ""),
            alternatives=alternatives,
            impact=impact,
            reversibility=fields.get("reversibility", "medium"),
            dismiss=fields.get("one-line dismiss", "n/a"),
            reject_reason=fields.get("reject reason", ""),
            resolved_by=fields.get("resolved by", ""),
        ))
    return decisions


def _write_file(path: Path, decisions: List[Decision], header_note: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    now = _iso(_now_taipei())
    header = [
        "# Pending Sign-Off Batch",
        "",
        f"> Auto-managed by tools/sign_off_manager.py — last updated {now}",
        "> Default action = proceed. Stop pattern = Edward rejects.",
        "> AUTO decisions auto-apply after their timer. ESCALATE decisions never auto-apply.",
        "",
    ]
    if header_note:
        header.append(header_note)
        header.append("")
    body_parts = [d.to_markdown(i + 1) for i, d in enumerate(decisions)]
    path.write_text("\n".join(header) + "\n" + "\n".join(body_parts), encoding="utf-8")


def _append_archive(decisions: List[Decision]) -> None:
    if not decisions:
        return
    ARCHIVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing = _parse_file(ARCHIVE_PATH)
    existing.extend(decisions)
    _write_file(ARCHIVE_PATH, existing, header_note="> Archive — historical decisions")


# --------------------------------------------------------------------------- #
# Public API                                                                  #
# --------------------------------------------------------------------------- #

def list_pending(path: Optional[Path] = None) -> List[Decision]:
    """Return all active decisions from the pending file."""
    return _parse_file(path if path is not None else PENDING_PATH)


def add_decision(
    title: str,
    recommendation: str,
    why: str,
    alternatives: Optional[List[str]] = None,
    impact: Optional[List[str]] = None,
    reversibility: str = "medium",
    category: str = "AUTO",
    default_hours: int = 24,
    dismiss: str = "n/a",
    status: str = "PENDING",
    path: Optional[Path] = None,
) -> Decision:
    """Append a decision to the pending sign-off file."""
    if path is None:
        path = PENDING_PATH
    if category not in VALID_CATEGORY:
        raise ValueError(f"category must be one of {VALID_CATEGORY}")
    if reversibility not in VALID_REVERSIBILITY:
        raise ValueError(f"reversibility must be one of {VALID_REVERSIBILITY}")
    if status not in VALID_STATUS:
        raise ValueError(f"status must be one of {VALID_STATUS}")
    now = _now_taipei()
    # ESCALATE items never auto-approve — push timer far into the future.
    if category == "ESCALATE":
        approve_at = now + timedelta(days=3650)
    else:
        approve_at = now + timedelta(hours=default_hours)
    decision = Decision(
        uid=str(uuid.uuid4())[:8],
        title=title,
        status=status,
        category=category,
        posted=_iso(now),
        auto_approve_at=_iso(approve_at),
        recommendation=recommendation,
        why=why,
        alternatives=list(alternatives or []),
        impact=list(impact or []),
        reversibility=reversibility,
        dismiss=dismiss,
    )
    decisions = _parse_file(path)
    decisions.append(decision)
    _write_file(path, decisions)
    return decision


def mark_decision(
    uid: str,
    status: str,
    who: str = "agent",
    reason: str = "",
    path: Optional[Path] = None,
) -> Optional[Decision]:
    """Update status for a decision. Returns the updated decision, or None."""
    if path is None:
        path = PENDING_PATH
    if status.upper() not in VALID_STATUS:
        raise ValueError(f"status must be one of {VALID_STATUS}")
    decisions = _parse_file(path)
    updated: Optional[Decision] = None
    for d in decisions:
        if d.uid == uid:
            d.status = status.upper()
            d.resolved_by = who
            if reason:
                d.reject_reason = reason
            updated = d
            break
    if updated is not None:
        _write_file(path, decisions)
    return updated


def auto_apply_expired(path: Optional[Path] = None) -> List[Decision]:
    """Mark expired PENDING AUTO decisions as AUTO_APPLIED.

    The caller (daemon or main session) is responsible for the actual
    real-world application of the recommendation. This function only
    tracks state.
    """
    if path is None:
        path = PENDING_PATH
    now = _now_taipei()
    decisions = _parse_file(path)
    applied: List[Decision] = []
    for d in decisions:
        if d.status != "PENDING" or d.category != "AUTO":
            continue
        approve_at = _parse_iso(d.auto_approve_at)
        if approve_at is not None and approve_at <= now:
            d.status = "AUTO_APPLIED"
            d.resolved_by = "agent:auto"
            applied.append(d)
    if applied:
        _write_file(path, decisions)
    return applied


def cleanup_old(days: int = 14, path: Optional[Path] = None) -> List[Decision]:
    """Archive decisions older than N days to sign_off_archive.md."""
    if path is None:
        path = PENDING_PATH
    cutoff = _now_taipei() - timedelta(days=days)
    decisions = _parse_file(path)
    to_archive: List[Decision] = []
    remaining: List[Decision] = []
    for d in decisions:
        posted = _parse_iso(d.posted)
        terminal = d.status in {"APPROVED", "REJECTED", "AUTO_APPLIED", "EXPIRED"}
        if terminal and posted is not None and posted <= cutoff:
            to_archive.append(d)
        else:
            remaining.append(d)
    if to_archive:
        _append_archive(to_archive)
        _write_file(path, remaining)
    return to_archive


# --------------------------------------------------------------------------- #
# CLI                                                                         #
# --------------------------------------------------------------------------- #

def _decision_to_dict(d: Decision) -> dict:
    return asdict(d)


def _cmd_add(args: argparse.Namespace) -> int:
    alts = [a for a in (args.alternatives or "").split("|") if a.strip()]
    imps = [a for a in (args.impact or "").split("|") if a.strip()]
    decision = add_decision(
        title=args.title,
        recommendation=args.recommendation,
        why=args.why,
        alternatives=alts,
        impact=imps,
        reversibility=args.reversibility,
        category=args.category,
        default_hours=args.default_hours,
        dismiss=args.dismiss,
        status=args.status,
    )
    print(json.dumps(_decision_to_dict(decision), ensure_ascii=False))
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    decisions = list_pending()
    if args.json:
        print(json.dumps([_decision_to_dict(d) for d in decisions], ensure_ascii=False, indent=2))
    else:
        if not decisions:
            print("(no pending decisions)")
            return 0
        for i, d in enumerate(decisions, 1):
            print(f"{i}. [{d.status}/{d.category}] {d.uid} — {d.title}")
            print(f"   → {d.recommendation}")
            print(f"   auto-approve at: {d.auto_approve_at}")
    return 0


def _cmd_apply_expired(args: argparse.Namespace) -> int:
    applied = auto_apply_expired()
    out = {
        "applied_count": len(applied),
        "applied": [_decision_to_dict(d) for d in applied],
        "ts": _iso(_now_taipei()),
    }
    print(json.dumps(out, ensure_ascii=False))
    return 0


def _cmd_reject(args: argparse.Namespace) -> int:
    updated = mark_decision(args.uid, "REJECTED", who="edward", reason=args.reason or "")
    if updated is None:
        print(f"uid not found: {args.uid}", file=sys.stderr)
        return 1
    print(json.dumps(_decision_to_dict(updated), ensure_ascii=False))
    return 0


def _cmd_mark(args: argparse.Namespace) -> int:
    updated = mark_decision(args.uid, args.status, who=args.who, reason=args.reason or "")
    if updated is None:
        print(f"uid not found: {args.uid}", file=sys.stderr)
        return 1
    print(json.dumps(_decision_to_dict(updated), ensure_ascii=False))
    return 0


def _cmd_cleanup(args: argparse.Namespace) -> int:
    archived = cleanup_old(days=args.days)
    print(json.dumps({"archived_count": len(archived)}, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="sign_off_manager",
                                description="Auto sign-off batch system")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--add", action="store_true", help="Add a new decision")
    g.add_argument("--list", action="store_true", help="List pending decisions")
    g.add_argument("--apply-expired", action="store_true",
                   help="Mark expired AUTO decisions as AUTO_APPLIED")
    g.add_argument("--reject", metavar="UID", help="Reject decision by uid")
    g.add_argument("--mark", metavar="UID", help="Set status for decision by uid")
    g.add_argument("--cleanup", action="store_true",
                   help="Archive decisions older than N days")

    # Shared
    p.add_argument("--title", default="")
    p.add_argument("--recommendation", default="")
    p.add_argument("--why", default="")
    p.add_argument("--alternatives", default="", help="Pipe-separated")
    p.add_argument("--impact", default="", help="Pipe-separated")
    p.add_argument("--reversibility", default="medium",
                   choices=sorted(VALID_REVERSIBILITY))
    p.add_argument("--category", default="AUTO", choices=sorted(VALID_CATEGORY))
    p.add_argument("--default-hours", type=int, default=24)
    p.add_argument("--dismiss", default="n/a")
    p.add_argument("--status", default="PENDING", choices=sorted(VALID_STATUS))
    p.add_argument("--reason", default="")
    p.add_argument("--who", default="agent", choices=["agent", "edward", "agent:auto"])
    p.add_argument("--days", type=int, default=14)
    p.add_argument("--json", action="store_true", help="JSON output for --list")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.add:
        if not args.title or not args.recommendation:
            print("--add requires --title and --recommendation", file=sys.stderr)
            return 2
        return _cmd_add(args)
    if args.list:
        return _cmd_list(args)
    if args.apply_expired:
        return _cmd_apply_expired(args)
    if args.reject:
        args.uid = args.reject
        return _cmd_reject(args)
    if args.mark:
        args.uid = args.mark
        if args.status == "PENDING":
            print("--mark requires --status != PENDING", file=sys.stderr)
            return 2
        return _cmd_mark(args)
    if args.cleanup:
        return _cmd_cleanup(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
