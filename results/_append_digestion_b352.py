"""Append batch 352 (TXAD_1_003_FlipLS01) — first non-TXDL strategy family.

B2 pipeline. 2026-04-14. TXAD = TX All-Day (day+night session) family.
This is the first TXAD entry, opening a new sub-category beyond the TXDL (day-only) zoo.
"""
from __future__ import annotations

import json
from pathlib import Path

BASE = Path("C:/Users/admin/workspace/digital-immortality/results")
TS = "2026-04-14T12:05"

entries: list[dict] = [
    {
        "path": "E:/@交易/@AVAVA/Keep/!_TXAD_1_003_FlipLS01/!_TXAD_1_003_FlipLS01.txt",
        "summary": (
            "TXAD_003_FlipLS01 (Andy_FlipLS) — TX 3-min ALL-DAY session strategy, "
            "breaks TXDL-family constraints: no entries-today cap, no mp=0 lockout, no "
            "directional lock. Entry long: day-session only + k>in + (lowd+opend)/2>closed(1) "
            "+ 'price-position-high' test (c sits in upper 1/3 of day H-L band) -> stop-buy "
            "at Highest(H,3) + amEntry*2*three-day-avg-range/100 (entry difficulty scales "
            "with amEntry re-entry counter). Exit: (A) near-close fade — if |c-entry| < "
            "avg-K-range * barssinceentry/2, declare 'insufficient progress' exit; (B) "
            ">=04:30 session-end exit (low-volume tail avoidance); (C) loss > stopLoss/2^N "
            "compounded SL tightening + c<L confirmation. Flip: in-bar (H-C) > "
            "max(stopLoss/2, threeDaysRange/10) — night-session variant uses 3-bar-high "
            "instead because night-bar volatility too small for single-bar flip. Stop-loss "
            "tightens geometrically per flip count (damping oscillation). Novel patterns: "
            "(1) 'entry-difficulty ramp' — parameter amEntry scales entry threshold with "
            "re-entry count (prevents over-trading same setup); (2) 'insufficient progress' "
            "exit as alternative to trailing stop; (3) day vs night asymmetric flip rules "
            "(bar-internal vs 3-bar-window) acknowledging session liquidity regime. "
            "Represents 'TXAD family charter': full-day coverage with counter-based "
            "difficulty dampening instead of hard entry caps."
        ),
    },
]

assert len(entries) == 1, f"expected 1, got {len(entries)}"

for i, e in enumerate(entries):
    e["timestamp"] = f"{TS}:{i:02d}+08:00"
    e["tier"] = 1
    e["readable"] = True
    e["summary_length"] = len(e["summary"])

log_path = BASE / "digestion_log.jsonl"
with log_path.open("a", encoding="utf-8") as f:
    for e in entries:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")
print(f"Appended {len(entries)} entries to {log_path.name}")

state_path = BASE / "digestion_state.json"
with state_path.open("r", encoding="utf-8") as f:
    state = json.load(f)

new_paths = [e["path"] for e in entries]
state["digested_paths"].extend(new_paths)
state["files_digested"] = len(state["digested_paths"])
state["total_digested"] = state.get("total_digested", state["files_digested"]) + len(entries)
state["last_digested_at"] = f"{TS}:59+08:00"
state["last_updated"] = f"{TS}:59+08:00"

with state_path.open("w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)
print(f"State updated: files_digested={state['files_digested']} total_digested={state['total_digested']}")

set_path = BASE / "digested_set.txt"
if set_path.exists():
    with set_path.open("a", encoding="utf-8") as f:
        for p in new_paths:
            f.write(p + "\n")
    print(f"Appended {len(new_paths)} paths to {set_path.name}")
