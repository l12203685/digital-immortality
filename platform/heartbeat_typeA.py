#!/usr/bin/env python3
"""Type A daily heartbeat check. Silent if healthy; Discord alert if not.

Exit: 0=healthy, 1=alert. Usage: python platform/heartbeat_typeA.py
"""
from __future__ import annotations
import json, os, re, subprocess, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STAGING, RESULTS, MEMORY = REPO / "staging", REPO / "results", REPO / "memory"
STALE_DAEMON = 7200
STALE_ENGINE = 7200
STALE_DASHBOARD = 86400


def read_head(path: Path, n: int) -> str:
    if not path.exists():
        return ""
    with path.open("r", encoding="utf-8", errors="replace") as f:
        return "".join(next(f, "") for _ in range(n))


def read_tail(path: Path, n: int) -> str:
    if not path.exists():
        return ""
    with path.open("r", encoding="utf-8", errors="replace") as f:
        return "".join(f.readlines()[-n:])


def git_epoch(path: Path) -> int | None:
    try:
        out = subprocess.check_output(
            ["git", "log", "-1", "--format=%at", "--", str(path)],
            cwd=REPO, stderr=subprocess.DEVNULL, text=True).strip()
        return int(out) if out else None
    except Exception:
        return None


def parse_tick(status: dict) -> int | None:
    ts = status.get("last_tick")
    if not ts:
        return None
    try:
        return int(datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp())
    except Exception:
        return None


def parse_b6(text: str) -> int | None:
    m = re.findall(r"B6\s+(\d+)(?:st|nd|rd|th)\s+clean", text)
    return max(int(x) for x in m) if m else None


def resolve_webhook() -> str | None:
    val = os.environ.get("DISCORD_WEBHOOK")
    if val:
        return val.strip()
    engine = REPO / "trading" / "engine.py"
    if engine.exists():
        txt = engine.read_text(encoding="utf-8", errors="replace")
        m = re.search(r'DISCORD_WEBHOOK\s*=\s*\(?\s*"([^"]+)"\s*(?:"([^"]+)")?', txt)
        if m:
            return (m.group(1) + (m.group(2) or "")).strip()
    return None


def post_discord(webhook: str, msg: str) -> bool:
    try:
        data = json.dumps({"content": msg}).encode("utf-8")
        req = urllib.request.Request(webhook, data=data,
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            return 200 <= r.status < 300
    except Exception as e:
        print(f"[heartbeat] discord failed: {e}", file=sys.stderr)
        return False


def run_checks() -> dict:
    now = int(datetime.now(timezone.utc).timestamp())
    rep: dict = {"generated_at": datetime.now(timezone.utc).isoformat(),
                 "checks": {}, "warnings": [], "failures": []}
    qs = read_head(STAGING / "quick_status.md", 40)
    tree = read_head(RESULTS / "dynamic_tree.md", 60)
    dlog = read_tail(RESULTS / "daemon_log.md", 30)
    rep["inputs"] = {"qs": len(qs), "tree": len(tree), "dlog": len(dlog)}

    # 1: daemon recursive_distillation freshness
    le = git_epoch(MEMORY / "recursive_distillation.md")
    if le is None:
        rep["checks"]["daemon_push_fresh"] = "UNKNOWN"
        rep["warnings"].append("distillation: no git log")
    else:
        age = now - le
        rep["checks"]["daemon_push_fresh"] = {"age": age, "threshold": STALE_DAEMON, "ok": age <= STALE_DAEMON}
        if age > STALE_DAEMON:
            rep["failures"].append(f"daemon stale: distillation {age}s (>{STALE_DAEMON})")

    # 2: trading engine tick freshness (OR intentionally stopped)
    stopped = bool(re.search(r"trading_engine:\s*STOPPED", qs))
    sp = RESULTS / "trading_engine_status.json"
    if sp.exists():
        try:
            status = json.loads(sp.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            status = {}
        tick = parse_tick(status)
        if tick is None:
            rep["checks"]["engine_tick_fresh"] = "UNKNOWN"
            if not stopped:
                rep["warnings"].append("engine: last_tick unparseable")
        else:
            age = now - tick
            fresh = age <= STALE_ENGINE
            rep["checks"]["engine_tick_fresh"] = {"age": age, "ok": fresh, "stopped": stopped}
            if not fresh and not stopped:
                rep["failures"].append(f"engine stale: last_tick {age}s and not STOPPED")
    else:
        rep["checks"]["engine_tick_fresh"] = "MISSING"
        if not stopped:
            rep["warnings"].append("engine: status file missing")

    # 3: B6 streak unbroken
    b6q, b6d = parse_b6(qs), parse_b6(dlog)
    vals = [x for x in (b6q, b6d) if x is not None]
    streak = max(vals) if vals else None
    regress = bool(re.search(r"B6\s+(REGRESS|BROKE|FAIL)", qs + dlog))
    rep["checks"]["b6_streak"] = {"quick": b6q, "daemon": b6d, "streak": streak, "regression": regress}
    if regress:
        rep["failures"].append("B6 regression keyword detected")
    if streak is None:
        rep["warnings"].append("B6 streak: no 'NNth clean' marker parsed")

    # 4: no BLOCKER/CRITICAL in dynamic_tree head
    bad = re.findall(r"\b(BLOCKER|CRITICAL)\b", tree)
    rep["checks"]["tree_clean"] = {"flagged": bad, "ok": not bad}
    if bad:
        rep["failures"].append(f"dynamic_tree flagged: {bad}")

    # 5: dashboard freshness (warning only — builder wiring unconfirmed)
    dp = RESULTS / "dashboard_state.json"
    if dp.exists():
        age = now - int(dp.stat().st_mtime)
        ok = age <= STALE_DASHBOARD
        rep["checks"]["dashboard_fresh"] = {"age": age, "ok": ok}
        if not ok:
            rep["warnings"].append(f"dashboard_state.json stale: {age}s")
    else:
        rep["checks"]["dashboard_fresh"] = "MISSING"
        rep["warnings"].append("dashboard_state.json missing")

    rep["healthy"] = not rep["failures"]
    return rep


def main() -> int:
    rep = run_checks()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = RESULTS / f"heartbeat_{today}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(f"[heartbeat] report: {out}")
    print(json.dumps({"healthy": rep["healthy"], "failures": rep["failures"],
                      "warnings": rep["warnings"]}, indent=2))
    if rep["healthy"]:
        return 0
    webhook = resolve_webhook()
    if not webhook:
        print("[heartbeat] DISCORD_WEBHOOK unavailable", file=sys.stderr)
        return 1
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    reason = "; ".join(rep["failures"])[:1500]
    post_discord(webhook, f"\u26a0\ufe0f Heartbeat FAIL {ts}: {reason}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
