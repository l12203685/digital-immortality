#!/usr/bin/env python3
"""
Register the stale memory detector scheduled task.
Reads the XML and registers it with Windows Task Scheduler.
"""
import os
import sys
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
XML_PATH = REPO_ROOT / "tools" / "stale_detector_scheduler.xml"
TASK_NAME = "Edward_StaleMemory_Check"

def main() -> int:
    if not XML_PATH.exists():
        print(f"Error: XML file not found at {XML_PATH}", file=sys.stderr)
        return 1

    # Register task using schtasks
    cmd = [
        "schtasks.exe",
        "/Create",
        "/TN", TASK_NAME,
        "/XML", str(XML_PATH),
        "/F"
    ]

    print(f"Registering task '{TASK_NAME}'...")
    print(f"  XML: {XML_PATH}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0 or "successfully" in result.stdout.lower():
            print(f"✓ Task registered successfully")
        else:
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            print(f"Return code: {result.returncode}")
    except Exception as e:
        print(f"Error registering task: {e}", file=sys.stderr)
        return 1

    # Verify registration
    print("\nVerifying task registration...")
    verify_cmd = ["schtasks.exe", "/Query", "/TN", TASK_NAME]
    try:
        result = subprocess.run(verify_cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print(f"✓ Task is registered")
            # Extract key info
            for line in result.stdout.split("\n"):
                if "Task To Run" in line or "Schedule Type" in line or "Start Time" in line:
                    print(f"  {line.strip()}")
            return 0
        else:
            print(f"Task not found or query failed", file=sys.stderr)
            return 1
    except Exception as e:
        print(f"Error verifying task: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
