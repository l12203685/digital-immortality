#!/usr/bin/env python3
"""
Verify that the stale memory detector task is registered and run a test.
"""
import subprocess
import sys
from pathlib import Path

TASK_NAME = "Edward_StaleMemory_Check"
REPO_ROOT = Path(__file__).resolve().parent.parent

def verify_task():
    """Check if task is registered."""
    cmd = ["schtasks.exe", "/Query", "/TN", TASK_NAME, "/V", "/FO", "LIST"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and TASK_NAME in result.stdout:
        print(f"[OK] Task '{TASK_NAME}' is registered")
        # Print key details
        for line in result.stdout.split("\n"):
            if any(x in line for x in ["Task", "Status", "Next Run", "Schedule", "Launch"]):
                print(f"  {line.strip()}")
        return True
    else:
        print(f"[FAIL] Task '{TASK_NAME}' not found")
        if result.stderr:
            print(f"  Error: {result.stderr}")
        return False

def run_test():
    """Run the stale detector script directly for verification."""
    script = REPO_ROOT / "tools" / "stale_detector_run.py"
    print(f"\n=== Running test execution ===")
    result = subprocess.run(
        ["python", str(script)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print(f"stderr: {result.stderr}")
    return result.returncode == 0 or result.returncode == 1  # 1 = stale files found

def main():
    print("Edward Stale Memory Detector - Task Verification\n")
    print("=" * 50)

    # Verify task is registered
    task_ok = verify_task()

    # Run a test
    test_ok = run_test()

    print("\n" + "=" * 50)
    if task_ok and test_ok:
        print("Status: OK - Task is registered and functional")
        return 0
    else:
        print("Status: FAILED - See errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
