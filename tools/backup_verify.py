#!/usr/bin/env python3
"""
backup_verify.py - B6 (存活冗餘/Anti-fragile) backup audit tool.

Checks that all critical files exist in 3+ locations (3-copy rule).
Exit 0 = all files have 3+ copies. Exit 1 = any file has <3 copies.

Usage:
    python backup_verify.py
    python backup_verify.py --fix    # show commands to create missing backups
    python backup_verify.py --json   # JSON-only output (no pretty print)
"""

import argparse
import glob
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── constants ────────────────────────────────────────────────────────────────

TAIPEI = timezone(timedelta(hours=8))
BASE_MEMORY = r"C:\Users\admin\.claude\projects\C--Users-admin\memory"
LYH_MEMORY  = r"C:\Users\admin\LYH\agent\claude_memory"
LYH_AGENT   = r"C:\Users\admin\LYH\agent"
GDRIVE_ROOT = r"C:\Users\admin\GoogleDrive"
GDRIVE_STAGING = r"C:\Users\admin\GoogleDrive\staging"
STAGING     = r"C:\Users\admin\staging"
DI_RESULTS  = r"C:\Users\admin\workspace\digital-immortality\results"
REPORT_PATH = os.path.join(DI_RESULTS, "backup_verify_report.json")

# ── manifest definition ───────────────────────────────────────────────────────
#
# Each entry: {
#   "label":     human-readable name
#   "path_a":    canonical/original path (Location A)
#   "path_b":    LYH git mirror path     (Location B)
#   "path_c":    GoogleDrive path        (Location C)
#   "git_repo":  repo root for git check (Location D, optional)
# }
#
# Special entry type "glob" expands into multiple entries at runtime.

STATIC_MANIFEST = [
    {
        "label": "dna_core.md",
        "path_a": r"C:\Users\admin\LYH\agent\dna_core.md",
        "path_b": r"C:\Users\admin\LYH\agent\claude_memory\dna_core.md",
        "path_c": None,  # no known GDrive copy - will be detected
        "git_repo": r"C:\Users\admin\LYH",
    },
    {
        "label": "boot_tests.md",
        "path_a": r"C:\Users\admin\LYH\agent\boot_tests.md",
        "path_b": r"C:\Users\admin\LYH\agent\claude_memory\boot_tests.md",
        "path_c": None,
        "git_repo": r"C:\Users\admin\LYH",
    },
    {
        "label": "MEMORY.md",
        "path_a": os.path.join(BASE_MEMORY, "MEMORY.md"),
        "path_b": os.path.join(LYH_MEMORY, "MEMORY.md"),
        "path_c": None,
        "git_repo": r"C:\Users\admin\LYH",
    },
    {
        "label": "CLAUDE.md",
        "path_a": r"C:\Users\admin\CLAUDE.md",
        "path_b": None,  # not in LYH claude_memory
        "path_c": os.path.join(GDRIVE_ROOT, "CLAUDE.md"),
        "git_repo": None,
    },
    {
        "label": "session_state.md",
        "path_a": os.path.join(STAGING, "session_state.md"),
        "path_b": None,
        "path_c": os.path.join(GDRIVE_STAGING, "session_state.md"),
        "git_repo": None,
    },
    {
        "label": "dynamic_tree.md",
        "path_a": os.path.join(DI_RESULTS, "dynamic_tree.md"),
        "path_b": None,
        "path_c": None,
        "git_repo": r"C:\Users\admin\workspace\digital-immortality",
    },
    {
        "label": "trading_engine_status.json",
        "path_a": os.path.join(DI_RESULTS, "trading_engine_status.json"),
        "path_b": None,
        "path_c": None,
        "git_repo": r"C:\Users\admin\workspace\digital-immortality",
    },
]

# ── helpers ───────────────────────────────────────────────────────────────────

def sha256_file(path: str) -> str | None:
    """Return hex SHA-256 of file contents, or None if not readable."""
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def file_meta(path: str) -> dict:
    """Return exists/size_kb/mtime for a path."""
    if not path or not os.path.exists(path):
        return {"exists": False, "size_kb": None, "mtime": None, "hash": None}
    stat = os.stat(path)
    mtime = datetime.fromtimestamp(stat.st_mtime, tz=TAIPEI).strftime("%Y-%m-%d %H:%M +08")
    return {
        "exists": True,
        "size_kb": round(stat.st_size / 1024, 1),
        "mtime": mtime,
        "hash": sha256_file(path),
    }


def git_check(file_path: str, repo_root: str) -> dict:
    """
    Check if file is tracked + pushed in git repo.
    Returns {tracked: bool, commit_hash: str|None, pushed: bool|None}.
    """
    result = {"tracked": False, "commit_hash": None, "pushed": None}
    if not repo_root or not os.path.exists(repo_root):
        return result

    # Normalise to forward slashes for git on Windows
    rel = os.path.relpath(file_path, repo_root).replace("\\", "/")

    try:
        out = subprocess.check_output(
            ["git", "-C", repo_root, "log", "-1", "--format=%H", "--", rel],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if out:
            result["tracked"] = True
            result["commit_hash"] = out[:12]

            # Check if HEAD is pushed to any remote
            try:
                remote_out = subprocess.check_output(
                    ["git", "-C", repo_root, "branch", "-r", "--contains", "HEAD"],
                    stderr=subprocess.DEVNULL,
                    text=True,
                ).strip()
                result["pushed"] = bool(remote_out)
            except subprocess.CalledProcessError:
                result["pushed"] = False
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return result


def detect_gdrive_copy(label: str) -> str | None:
    """
    Best-effort search for a file with a matching name somewhere under GDrive.
    Returns the first path found, or None.
    """
    filename = os.path.basename(label)
    pattern = os.path.join(GDRIVE_ROOT, "**", filename)
    matches = glob.glob(pattern, recursive=True)
    return matches[0] if matches else None


def expand_glob_memory_files() -> list[dict]:
    """Expand all *.md in BASE_MEMORY into individual manifest entries."""
    entries = []
    pattern = os.path.join(BASE_MEMORY, "*.md")
    for path_a in sorted(glob.glob(pattern)):
        filename = os.path.basename(path_a)
        if filename == "MEMORY.md":
            continue  # already in static manifest
        entries.append({
            "label": f"memory/{filename}",
            "path_a": path_a,
            "path_b": os.path.join(LYH_MEMORY, filename),
            "path_c": None,
            "git_repo": r"C:\Users\admin\LYH",
        })
    return entries


# ── core audit ────────────────────────────────────────────────────────────────

def audit_entry(entry: dict) -> dict:
    """Run full backup check for one manifest entry. Returns structured result."""
    label    = entry["label"]
    path_a   = entry.get("path_a")
    path_b   = entry.get("path_b")
    path_c   = entry.get("path_c")
    git_repo = entry.get("git_repo")

    loc_a = file_meta(path_a)
    loc_b = file_meta(path_b)

    # Location C: use explicit path first, then auto-detect from GDrive
    if path_c:
        loc_c = file_meta(path_c)
    else:
        detected = detect_gdrive_copy(os.path.basename(path_a) if path_a else label)
        path_c = detected
        loc_c = file_meta(detected) if detected else {"exists": False, "size_kb": None, "mtime": None, "hash": None}

    # Location D: git remote
    loc_d = git_check(path_a, git_repo) if path_a and git_repo else {"tracked": False, "commit_hash": None, "pushed": None}

    # Count valid copies
    copies = sum([
        loc_a["exists"],
        loc_b["exists"],
        loc_c["exists"],
        bool(loc_d.get("tracked") and loc_d.get("pushed")),
    ])

    # Divergence detection (A vs B)
    match_ab = None
    if loc_a["hash"] and loc_b["hash"]:
        match_ab = loc_a["hash"] == loc_b["hash"]

    return {
        "label": label,
        "copies": copies,
        "status": "OK" if copies >= 3 else ("WARNING" if copies == 2 else "CRITICAL"),
        "locations": {
            "A": {"path": path_a, **loc_a},
            "B": {"path": path_b, **loc_b},
            "C": {"path": path_c, **loc_c},
            "D_git": {
                "repo": git_repo,
                **loc_d,
            },
        },
        "match_AB": match_ab,
    }


# ── pretty printer ────────────────────────────────────────────────────────────

TICK  = "[OK]"
CROSS = "[!!]"

def _loc_str(meta: dict, label: str, path: str | None) -> str:
    if meta["exists"]:
        return f"  {TICK} {label}: {meta['size_kb']}KB, {meta['mtime']}"
    else:
        return f"  {CROSS} {label}: NOT FOUND" + (f" ({path})" if path else "")


def _git_str(loc_d: dict) -> str:
    if not loc_d.get("repo"):
        return f"  - Location D (git): N/A"
    if loc_d["tracked"] and loc_d["pushed"]:
        return f"  {TICK} Location D (git): pushed, commit {loc_d['commit_hash']}"
    elif loc_d["tracked"]:
        return f"  ! Location D (git): tracked but NOT pushed (commit {loc_d['commit_hash']})"
    else:
        return f"  {CROSS} Location D (git): not tracked"


def pretty_print(results: list[dict], ts: str) -> None:
    print(f"\n=== Backup Verification - {ts} ===\n")
    ok = warn = crit = 0
    for r in results:
        locs = r["locations"]
        s = r["status"]
        if   s == "OK":       ok   += 1
        elif s == "WARNING":  warn += 1
        else:                 crit += 1

        copies_str = f"{r['copies']}/4"
        status_tag = {"OK": "OK", "WARNING": "WARNING", "CRITICAL": "CRITICAL"}[s]
        print(f"{r['label']}:")
        print(_loc_str(locs["A"], "Location A (primary)", locs["A"]["path"]))
        print(_loc_str(locs["B"], "Location B (LYH mirror)", locs["B"]["path"]))
        print(_loc_str(locs["C"], "Location C (GoogleDrive)", locs["C"]["path"]))
        print(_git_str(locs["D_git"]))
        match_note = ""
        if r["match_AB"] is True:
            match_note = " (A=B MATCH)"
        elif r["match_AB"] is False:
            match_note = " (A≠B DIVERGED!)"
        print(f"  Copies: {copies_str} - {status_tag}{match_note}")
        print()

    total = len(results)
    print(f"Summary: {ok}/{total} files OK (3+ copies), {warn} WARNING (2 copies), {crit} CRITICAL (<=1 copy)")
    if warn or crit:
        print("  Action required - run with --fix for remediation commands.\n")
    else:
        print("  All files have adequate backup coverage.\n")


# ── fix suggestions ───────────────────────────────────────────────────────────

def suggest_fixes(results: list[dict]) -> None:
    print("\n=== Suggested Fix Commands ===\n")
    has_fixes = False
    for r in results:
        if r["status"] == "OK":
            continue
        locs  = r["locations"]
        label = r["label"]
        path_a = locs["A"]["path"]

        if not locs["A"]["exists"]:
            print(f"# {label}: PRIMARY MISSING - restore from another copy")
            if locs["B"]["exists"]:
                print(f'  copy "{locs["B"]["path"]}" "{path_a}"')
            elif locs["C"]["exists"]:
                print(f'  copy "{locs["C"]["path"]}" "{path_a}"')
            print()
            has_fixes = True
            continue

        if not locs["B"]["exists"] and locs["B"]["path"]:
            b_dir = os.path.dirname(locs["B"]["path"])
            print(f"# {label}: create LYH mirror copy")
            print(f'  mkdir -p "{b_dir}" && cp "{path_a}" "{locs["B"]["path"]}"')
            print(f'  cd "C:\\Users\\admin\\LYH" && git add -A && git commit -m "backup: sync {label}" && git push')
            print()
            has_fixes = True

        if not locs["C"]["exists"]:
            gdrive_target = os.path.join(GDRIVE_ROOT, "staging", os.path.basename(path_a))
            print(f"# {label}: create GoogleDrive copy")
            print(f'  cp "{path_a}" "{gdrive_target}"')
            print()
            has_fixes = True

        if locs["D_git"]["repo"] and not locs["D_git"]["pushed"]:
            print(f"# {label}: push to git remote")
            print(f'  cd "{locs["D_git"]["repo"]}" && git push')
            print()
            has_fixes = True

    if not has_fixes:
        print("  No fixes needed.\n")


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Backup verification for digital-immortality B6 branch")
    parser.add_argument("--fix",  action="store_true", help="Show commands to fix missing backups")
    parser.add_argument("--json", action="store_true", help="Output JSON only (skip pretty print)")
    args = parser.parse_args()

    now = datetime.now(tz=TAIPEI)
    ts  = now.strftime("%Y-%m-%d %H:%M +08")

    # Build full manifest (static + dynamic memory/*.md glob)
    manifest = STATIC_MANIFEST + expand_glob_memory_files()

    results = [audit_entry(e) for e in manifest]

    # ── save JSON report ──
    os.makedirs(DI_RESULTS, exist_ok=True)
    report = {
        "generated_at": ts,
        "total": len(results),
        "ok":       sum(1 for r in results if r["status"] == "OK"),
        "warning":  sum(1 for r in results if r["status"] == "WARNING"),
        "critical": sum(1 for r in results if r["status"] == "CRITICAL"),
        "files": results,
    }
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        pretty_print(results, ts)
        if args.fix:
            suggest_fixes(results)
        print(f"[Report saved to {REPORT_PATH}]")

    # Exit 1 if any file has fewer than 3 copies
    any_at_risk = any(r["status"] != "OK" for r in results)
    return 1 if any_at_risk else 0


if __name__ == "__main__":
    sys.exit(main())
