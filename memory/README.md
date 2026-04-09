# memory/ -- Cross-Session Persistence

Learnings that survive restarts.

Unlike `staging/` (which is consumed each cycle), files here accumulate over time. Store calibration insights, behavioral corrections, and discovered patterns that should persist across all future sessions.

Never delete from memory -- only append or update (except via explicit `--prune`).

## Categories

| File | Purpose |
|------|---------|
| `corrections.json` | Behavioral corrections from boot tests. When a test fails, record what went wrong and what fixed it so the twin never regresses. |
| `insights.json` | Cross-domain patterns discovered during recursive cycles. Connections between different life domains or new principles. |
| `decisions.json` | Decisions made and their outcomes. Audit trail for decision fidelity tracking. |
| `calibration.json` | DNA calibration notes. Adjustments from conversations or corrections that tune the behavioral model. |
| `schema.json` | Defines the memory structure and entry format. |

## Entry Structure

Every memory entry contains:

```json
{
  "id": "uuid4",
  "key": "human-readable-key",
  "content": "The actual insight, correction, or decision.",
  "timestamp": "2026-04-07T12:00:00+00:00",
  "source": "cycle-5",
  "tags": ["boot-test", "anti-pattern"]
}
```

- **id**: Auto-generated UUID for uniqueness.
- **key**: Short name for retrieval (`--recall corrections my-key`).
- **content**: The memory itself.
- **timestamp**: ISO-8601 UTC, set automatically on store.
- **source**: Where this came from -- `cycle-N`, `boot-test`, `manual`, `calibration-session`, etc.
- **tags**: List of strings for cross-category search.

## CLI Usage (memory_manager.py)

```bash
# Store a correction from a boot test failure
python memory_manager.py --store corrections alignment-theater \
  "Agent restated feedback beautifully but did not change behavior. Fix: check for behavioral change, not verbal acknowledgment." \
  --source boot-test --tags boot-test,anti-pattern,alignment-theater

# Recall all corrections
python memory_manager.py --recall corrections

# Recall a specific entry by key
python memory_manager.py --recall corrections alignment-theater

# Search across all categories by tag
python memory_manager.py --search --tags anti-pattern

# Search within a specific category
python memory_manager.py --search --tags boot-test --category corrections

# List all categories and entry counts
python memory_manager.py --list

# Prune entries older than 90 days
python memory_manager.py --prune --days 90

# Export all memory to JSON (for backup)
python memory_manager.py --export > memory_backup.json
```

## Integration with recursive_engine.py

The recursive engine should use memory at two points in each cycle:

1. **At cycle start (read)**: Load relevant memories to inform the current cycle.
   - `recall("corrections")` -- avoid known anti-patterns
   - `recall("insights")` -- build on discovered patterns
   - `search_by_tags(["current-focus-tag"])` -- context-relevant memories

2. **At cycle end (write)**: Store anything learned during the cycle.
   - Boot test failures -> `corrections`
   - New cross-domain patterns -> `insights`
   - Decisions made -> `decisions`
   - DNA adjustments -> `calibration`

### Programmatic usage from Python

```python
from memory_manager import store, recall, search_by_tags, list_categories

# Store
store("corrections", "asked-known-question",
      "Asked user about investment strategy when DNA already documents it.",
      source="cycle-7", tags=["boot-test", "anti-pattern"])

# Recall
entries = recall("corrections")
entry = recall("corrections", "asked-known-question")

# Search by tags across all categories
results = search_by_tags(["anti-pattern"])

# List
counts = list_categories()  # {"corrections": 3, "insights": 1, ...}
```

## Design Principles

- **Pure Python, no external deps** -- works anywhere Python 3.10+ runs.
- **JSON-based** -- human-readable, git-diffable, one file per category.
- **Atomic writes** -- uses temp file + `os.replace()` so a crash never corrupts data.
- **Append-biased** -- memory grows. Pruning is explicit and optional.
- **Tag-queryable** -- any entry can be found by tag across all categories.
