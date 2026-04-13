#!/usr/bin/env python
"""
backup_manifest.py - B6 backup priority manifest generator.

Scans critical files, checks local existence + sizes, assigns tiers,
and outputs a human-actionable manifest at results/backup_manifest.md
with ready-to-run copy commands.

Usage:
    python backup_manifest.py
    python backup_manifest.py --dest "C:/Users/admin/GoogleDrive/backup"
"""

import argparse
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

TAIPEI = timezone(timedelta(hours=8))

BASE_MEMORY = r"C:\Users\admin\.claude\projects\C--Users-admin\memory"
LYH_AGENT   = r"C:\Users\admin\LYH\agent"
STAGING     = r"C:\Users\admin\staging"
DI_ROOT     = r"C:\Users\admin\workspace\digital-immortality"
DI_RESULTS  = os.path.join(DI_ROOT, "results")
DI_TOOLS    = os.path.join(DI_ROOT, "tools")
GDRIVE_ROOT = r"C:\Users\admin\GoogleDrive"


def _build_catalog() -> list[tuple[int, str, str]]:
    """Build the full critical-file catalog (static + dynamic memory files)."""
    catalog: list[tuple[int, str, str]] = [
        # Tier 1 — identity / DNA
        (1, "dna_core.md",        os.path.join(LYH_AGENT, "dna_core.md")),
        (1, "edward_dna_v18.md",  os.path.join(LYH_AGENT, "edward_dna_v18.md")),
        (1, "boot_tests.md",      os.path.join(LYH_AGENT, "boot_tests.md")),
        (1, "CLAUDE.md",          r"C:\Users\admin\CLAUDE.md"),
        (1, "domain_rules.md",    os.path.join(LYH_AGENT, "domain_rules.md")),
        (1, "recursive_distillation.md", os.path.join(LYH_AGENT, "recursive_distillation.md")),
        # Tier 2 — memory / session state
        (2, "MEMORY.md",          os.path.join(BASE_MEMORY, "MEMORY.md")),
        (2, "session_state.md",   os.path.join(STAGING, "session_state.md")),
        (2, "dynamic_tree.md",    os.path.join(DI_RESULTS, "dynamic_tree.md")),
        (2, "daemon_log.md",      os.path.join(DI_RESULTS, "daemon_log.md")),
        (2, "digestion_state.json", os.path.join(DI_RESULTS, "digestion_state.json")),
        (2, "digestion_log.jsonl",  os.path.join(DI_RESULTS, "digestion_log.jsonl")),
        (2, "continuous_go_state.json", os.path.join(STAGING, "continuous_go_state.json")),
        (2, "quick_status.md",    os.path.join(DI_ROOT, "staging", "quick_status.md")),
        # Tier 3 — tools / config
        (3, "backup_verify.py",   os.path.join(DI_TOOLS, "backup_verify.py")),
        (3, "backup_manifest.py", os.path.join(DI_TOOLS, "backup_manifest.py")),
        (3, "consistency_test.py", os.path.join(DI_ROOT, "consistency_test.py")),
        (3, "recursive_engine.py", os.path.join(DI_ROOT, "recursive_engine.py")),
        (3, "organism_interact.py", os.path.join(DI_ROOT, "organism_interact.py")),
        (3, "SKILL.md",           os.path.join(DI_ROOT, "SKILL.md")),
        (3, "index.md",           os.path.join(DI_ROOT, "index.md")),
    ]
    # Tier 2 — dynamic: all feedback_*.md / project_*.md in BASE_MEMORY
    if os.path.isdir(BASE_MEMORY):
        for fn in sorted(os.listdir(BASE_MEMORY)):
            if fn.endswith(".md") and fn != "MEMORY.md":
                catalog.append((2, f"memory/{fn}", os.path.join(BASE_MEMORY, fn)))
    return catalog


CRITICAL_FILES = _build_catalog()


def file_info(path: str) -> dict:
    if not path or not os.path.exists(path):
        return {"exists": False, "size_kb": None, "mtime": None}
    st = os.stat(path)
    mtime = datetime.fromtimestamp(st.st_mtime, tz=TAIPEI).strftime("%Y-%m-%d %H:%M")
    return {"exists": True, "size_kb": round(st.st_size / 1024, 1), "mtime": mtime}


def build_manifest(dest: str) -> list[dict]:
    rows = []
    seen = set()
    for tier, label, path in CRITICAL_FILES:
        if path in seen:
            continue
        seen.add(path)
        info = file_info(path)
        dest_path = os.path.join(dest, "tier" + str(tier), os.path.basename(path))
        rows.append({
            "tier": tier, "label": label, "path": path,
            "dest": dest_path, **info,
        })
    return sorted(rows, key=lambda r: (r["tier"], r["label"]))


def write_markdown(rows: list[dict], dest: str, out_path: str, ts: str) -> None:
    t1 = [r for r in rows if r["tier"] == 1]
    t2 = [r for r in rows if r["tier"] == 2]
    t3 = [r for r in rows if r["tier"] == 3]

    missing = [r for r in rows if not r["exists"]]
    present = [r for r in rows if r["exists"]]

    lines = [
        f"# Backup Priority Manifest",
        f"",
        f"Generated: {ts}  ",
        f"Destination: `{dest}`  ",
        f"Files: {len(present)}/{len(rows)} present locally  ",
        f"",
        f"## Summary",
        f"",
        f"| Tier | Description | Count | Missing |",
        f"|------|-------------|-------|---------|",
        f"| 1 | Identity / DNA | {len(t1)} | {sum(1 for r in t1 if not r['exists'])} |",
        f"| 2 | Memory / State | {len(t2)} | {sum(1 for r in t2 if not r['exists'])} |",
        f"| 3 | Tools / Config | {len(t3)} | {sum(1 for r in t3 if not r['exists'])} |",
        f"",
    ]

    for tier_rows, tier_name in [(t1, "Tier 1 — Identity / DNA"), (t2, "Tier 2 — Memory / State"), (t3, "Tier 3 — Tools / Config")]:
        lines += [f"## {tier_name}", f"", f"| File | Exists | Size (KB) | Modified |",
                  f"|------|--------|-----------|----------|"]
        for r in tier_rows:
            exists = "YES" if r["exists"] else "**MISSING**"
            size = str(r["size_kb"]) if r["size_kb"] is not None else "-"
            mtime = r["mtime"] or "-"
            lines.append(f"| `{r['label']}` | {exists} | {size} | {mtime} |")
        lines.append("")

    # Copy commands section
    lines += ["## Copy Commands", "", "Run these to back up all present files to destination:", ""]
    lines.append(f"```batch")
    lines.append(f'mkdir "{dest}\\tier1"')
    lines.append(f'mkdir "{dest}\\tier2"')
    lines.append(f'mkdir "{dest}\\tier3"')
    lines.append("")
    for r in present:
        src = r["path"].replace("/", "\\")
        dst = r["dest"].replace("/", "\\")
        lines.append(f'copy /Y "{src}" "{dst}"')
    lines.append("```")
    lines.append("")

    if missing:
        lines += ["## Missing Files (cannot back up)", ""]
        for r in missing:
            lines.append(f"- `{r['label']}`: `{r['path']}`")
        lines.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build backup priority manifest for digital-immortality B6")
    parser.add_argument("--dest", default=os.path.join(GDRIVE_ROOT, "backup"),
                        help="Backup destination root (default: GoogleDrive/backup)")
    args = parser.parse_args()

    now = datetime.now(tz=TAIPEI)
    ts = now.strftime("%Y-%m-%d %H:%M +08")

    dest = args.dest
    rows = build_manifest(dest)

    out_path = os.path.join(DI_RESULTS, "backup_manifest.md")
    os.makedirs(DI_RESULTS, exist_ok=True)
    write_markdown(rows, dest, out_path, ts)

    present = sum(1 for r in rows if r["exists"])
    missing = sum(1 for r in rows if not r["exists"])
    print(f"Manifest written to: {out_path}")
    print(f"Files: {present} present, {missing} missing, {len(rows)} total")
    print(f"Destination: {dest}")
    return 0 if missing == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
