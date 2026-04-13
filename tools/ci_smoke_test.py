"""
CI Smoke Test — digital-immortality project
Usage: python ci_smoke_test.py [--verbose]
Exit 0 if all checks pass, exit 1 if any fail.
"""

import sys
import os
import json
import importlib.util
import argparse
import pathlib

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"
RESULTS_DIR = PROJECT_ROOT / "results"

checks_run = 0
checks_passed = 0
verbose = False


def log(msg: str) -> None:
    if verbose:
        print(msg)


def check(name: str, ok: bool, detail: str = "") -> None:
    global checks_run, checks_passed
    checks_run += 1
    if ok:
        checks_passed += 1
        log(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}" + (f": {detail}" if detail else ""))


def check_tool_imports() -> None:
    """Verify every .py in tools/ can be imported without syntax errors."""
    for py_file in sorted(TOOLS_DIR.glob("*.py")):
        if py_file.name == "ci_smoke_test.py":
            continue
        name = py_file.stem
        spec = importlib.util.spec_from_file_location(name, py_file)
        try:
            mod = importlib.util.module_from_spec(spec)
            # Only compile, do not execute module-level side effects
            with open(py_file, "r", encoding="utf-8", errors="replace") as fh:
                source = fh.read()
            compile(source, str(py_file), "exec")
            check(f"tools/{py_file.name} compiles", True)
        except SyntaxError as exc:
            check(f"tools/{py_file.name} compiles", False, str(exc))
        except Exception as exc:
            check(f"tools/{py_file.name} compiles", False, str(exc))


def load_json(path: pathlib.Path) -> tuple:
    """Return (ok, data, error)."""
    if not path.exists():
        return False, None, "file not found"
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return True, json.load(fh), ""
    except json.JSONDecodeError as exc:
        return False, None, str(exc)


def load_jsonl(path: pathlib.Path) -> tuple:
    """Return (ok, line_count, error). Validates every line is valid JSON."""
    if not path.exists():
        return False, 0, "file not found"
    try:
        count = 0
        with open(path, "r", encoding="utf-8") as fh:
            for i, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue
                json.loads(line)
                count += 1
        return True, count, ""
    except json.JSONDecodeError as exc:
        return False, 0, f"line {i}: {exc}"


def check_result_files() -> None:
    """Verify key result files exist and are valid JSON/JSONL."""
    json_files = [
        "digestion_state.json",
        "trading_engine_status.json",
        "cycle_counter.json",
        "consistency_scorecard.json",
        "dashboard_state.json",
    ]
    for fname in json_files:
        ok, _, err = load_json(RESULTS_DIR / fname)
        check(f"results/{fname} valid JSON", ok, err)

    jsonl_files = [
        "digestion_log.jsonl",
        "agent_progress.jsonl",
    ]
    for fname in jsonl_files:
        path = RESULTS_DIR / fname
        ok, count, err = load_jsonl(path)
        check(f"results/{fname} valid JSONL", ok, err)
        if ok:
            log(f"          ({count} lines)")


def check_digestion_state() -> None:
    """Verify digestion_state.json has required fields and sane values."""
    ok, data, err = load_json(RESULTS_DIR / "digestion_state.json")
    if not ok:
        check("digestion_state structure", False, err)
        return
    required = ["total_files_known", "files_digested", "digested_paths",
                "current_tier", "last_digested_at"]
    missing = [k for k in required if k not in data]
    check("digestion_state has required keys", not missing,
          f"missing: {missing}" if missing else "")
    if missing:
        return
    ok2 = (
        isinstance(data["total_files_known"], int) and data["total_files_known"] > 0
        and isinstance(data["files_digested"], int) and data["files_digested"] >= 0
        and isinstance(data["digested_paths"], list)
        and len(data["digested_paths"]) == data["files_digested"]
    )
    check("digestion_state values are sane", ok2,
          "path count mismatch or non-positive total" if not ok2 else "")


def check_trading_engine_status() -> None:
    """Verify trading_engine_status.json loads and has minimal structure."""
    ok, data, err = load_json(RESULTS_DIR / "trading_engine_status.json")
    if not ok:
        check("trading_engine_status loads", False, err)
        return
    check("trading_engine_status loads", True)
    is_dict = isinstance(data, dict)
    check("trading_engine_status is a dict", is_dict,
          f"got {type(data).__name__}" if not is_dict else "")


def check_memory_files() -> None:
    """Verify key memory files exist and are non-empty."""
    memory_dir = PROJECT_ROOT / "memory"
    key_files = [
        "recursive_distillation.md",
    ]
    for fname in key_files:
        path = memory_dir / fname
        exists = path.exists()
        check(f"memory/{fname} exists", exists, "not found" if not exists else "")
        if exists:
            size = path.stat().st_size
            check(f"memory/{fname} non-empty", size > 0, "empty file")


def main() -> None:
    global verbose
    parser = argparse.ArgumentParser(description="CI smoke test for digital-immortality")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print passing checks as well as failures")
    args = parser.parse_args()
    verbose = args.verbose

    print("CI Smoke Test — digital-immortality")
    print(f"Project root: {PROJECT_ROOT}")
    print()

    print("[1] Tool import checks")
    check_tool_imports()

    print("[2] Result file validation")
    check_result_files()

    print("[3] digestion_state.json structure")
    check_digestion_state()

    print("[4] trading_engine_status.json structure")
    check_trading_engine_status()

    print("[5] Memory file presence")
    check_memory_files()

    print()
    status = "PASSED" if checks_passed == checks_run else "FAILED"
    print(f"Summary: {checks_passed}/{checks_run} checks passed  [{status}]")
    sys.exit(0 if checks_passed == checks_run else 1)


if __name__ == "__main__":
    main()
