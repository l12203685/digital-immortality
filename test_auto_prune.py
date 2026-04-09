#!/usr/bin/env python3
"""
Test auto-prune logic in memory_manager.

Verifies:
1. Age-based pruning removes old entries
2. Cap-based pruning respects max_entries limit
3. High-confidence entries are protected from cap-based pruning
4. prune_old works standalone
5. Confidence field is stored and preserved
"""

import json
import shutil
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Patch MEMORY_DIR before importing memory_manager
import memory_manager

PASSED = 0
FAILED = 0


def setup_temp_memory():
    """Create a temp directory for isolated testing."""
    tmpdir = Path(tempfile.mkdtemp(prefix="mem_test_"))
    memory_manager.MEMORY_DIR = tmpdir
    tmpdir.mkdir(exist_ok=True)
    return tmpdir


def cleanup(tmpdir):
    shutil.rmtree(tmpdir, ignore_errors=True)


def check(name, condition):
    global PASSED, FAILED
    if condition:
        print(f"  PASS: {name}")
        PASSED += 1
    else:
        print(f"  FAIL: {name}")
        FAILED += 1


def test_confidence_stored():
    """Test that confidence field is stored on entries."""
    print("\n--- Test: confidence field stored ---")
    tmpdir = setup_temp_memory()
    try:
        entry = memory_manager.store("insights", "conf-test", "test content",
                                     confidence=0.85)
        check("confidence field present", "confidence" in entry)
        check("confidence value correct", entry.get("confidence") == 0.85)

        # Verify it persists on disk
        recalled = memory_manager.recall("insights", "conf-test")
        check("confidence persists on recall", recalled[0].get("confidence") == 0.85)

        # Test clamping
        entry2 = memory_manager.store("insights", "conf-clamp", "test", confidence=1.5)
        check("confidence clamped to 1.0", entry2.get("confidence") == 1.0)

        entry3 = memory_manager.store("insights", "conf-no", "test")
        check("no confidence when not provided", "confidence" not in entry3)
    finally:
        cleanup(tmpdir)


def test_prune_old():
    """Test that prune_old removes entries older than max_age_days."""
    print("\n--- Test: prune_old removes old entries ---")
    tmpdir = setup_temp_memory()
    try:
        # Manually insert entries with old timestamps
        old_ts = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
        recent_ts = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()

        data = {
            "category": "insights",
            "description": "",
            "entries": [
                {"id": "old-1", "key": "old", "content": "old entry",
                 "timestamp": old_ts, "source": "test", "tags": []},
                {"id": "recent-1", "key": "recent", "content": "recent entry",
                 "timestamp": recent_ts, "source": "test", "tags": []},
            ]
        }
        path = memory_manager._memory_path("insights")
        with open(path, "w") as f:
            json.dump(data, f)

        pruned = memory_manager.prune_old(max_age_days=30)
        check("pruned 1 old entry", pruned == 1)

        remaining = memory_manager.recall("insights")
        check("1 entry remains", len(remaining) == 1)
        check("recent entry kept", remaining[0]["key"] == "recent")
    finally:
        cleanup(tmpdir)


def test_auto_prune_cap():
    """Test that auto_prune enforces max_entries cap."""
    print("\n--- Test: auto_prune enforces cap ---")
    tmpdir = setup_temp_memory()
    try:
        # Insert 10 recent entries
        base_ts = datetime.now(timezone.utc) - timedelta(days=1)
        entries = []
        for i in range(10):
            ts = (base_ts + timedelta(minutes=i)).isoformat()
            entries.append({
                "id": f"entry-{i}", "key": f"k{i}", "content": f"content {i}",
                "timestamp": ts, "source": "test", "tags": [],
            })

        data = {"category": "insights", "description": "", "entries": entries}
        path = memory_manager._memory_path("insights")
        with open(path, "w") as f:
            json.dump(data, f)

        removed = memory_manager.auto_prune(max_entries=5, max_age_days=365)
        check("removed 5 entries from insights", removed["insights"] == 5)

        remaining = memory_manager.recall("insights")
        check("5 entries remain", len(remaining) == 5)

        # Should have kept the most recent (highest minute offset)
        keys = [e["key"] for e in remaining]
        check("kept most recent entries", "k9" in keys and "k8" in keys)
        check("removed oldest entries", "k0" not in keys and "k1" not in keys)
    finally:
        cleanup(tmpdir)


def test_auto_prune_protects_high_confidence():
    """Test that high-confidence entries survive cap-based pruning."""
    print("\n--- Test: auto_prune protects high-confidence entries ---")
    tmpdir = setup_temp_memory()
    try:
        base_ts = datetime.now(timezone.utc) - timedelta(days=1)
        entries = []

        # 3 old low-confidence entries
        for i in range(3):
            ts = (base_ts + timedelta(minutes=i)).isoformat()
            entries.append({
                "id": f"low-{i}", "key": f"low-{i}", "content": f"low conf {i}",
                "timestamp": ts, "source": "test", "tags": [], "confidence": 0.3,
            })

        # 2 old HIGH-confidence entries (oldest timestamps but should be kept)
        for i in range(2):
            ts = (base_ts + timedelta(minutes=i)).isoformat()
            entries.append({
                "id": f"high-{i}", "key": f"high-{i}", "content": f"high conf {i}",
                "timestamp": ts, "source": "test", "tags": [], "confidence": 0.9,
            })

        # 3 recent low-confidence entries
        for i in range(3):
            ts = (base_ts + timedelta(minutes=10 + i)).isoformat()
            entries.append({
                "id": f"recent-{i}", "key": f"recent-{i}", "content": f"recent {i}",
                "timestamp": ts, "source": "test", "tags": [], "confidence": 0.5,
            })

        data = {"category": "decisions", "description": "", "entries": entries}
        path = memory_manager._memory_path("decisions")
        with open(path, "w") as f:
            json.dump(data, f)

        # Cap at 5: should keep 2 high-conf + 3 most recent low-conf
        removed = memory_manager.auto_prune(max_entries=5, max_age_days=365)
        check("removed 3 entries", removed["decisions"] == 3)

        remaining = memory_manager.recall("decisions")
        check("5 entries remain", len(remaining) == 5)

        remaining_keys = {e["key"] for e in remaining}
        check("high-conf entries protected", "high-0" in remaining_keys and "high-1" in remaining_keys)
        check("recent entries kept", "recent-2" in remaining_keys)
        check("old low-conf entries pruned", "low-0" not in remaining_keys)
    finally:
        cleanup(tmpdir)


def test_auto_prune_no_op_within_bounds():
    """Test that auto_prune does nothing when within limits."""
    print("\n--- Test: auto_prune no-op within bounds ---")
    tmpdir = setup_temp_memory()
    try:
        memory_manager.store("corrections", "k1", "content 1")
        memory_manager.store("corrections", "k2", "content 2")

        removed = memory_manager.auto_prune(max_entries=100, max_age_days=365)
        check("0 removed from corrections", removed["corrections"] == 0)

        remaining = memory_manager.recall("corrections")
        check("both entries intact", len(remaining) == 2)
    finally:
        cleanup(tmpdir)


if __name__ == "__main__":
    test_confidence_stored()
    test_prune_old()
    test_auto_prune_cap()
    test_auto_prune_protects_high_confidence()
    test_auto_prune_no_op_within_bounds()

    print(f"\n{'='*40}")
    print(f"Results: {PASSED} passed, {FAILED} failed")
    if FAILED == 0:
        print("All tests passed.")
    else:
        print("SOME TESTS FAILED.")
        exit(1)
