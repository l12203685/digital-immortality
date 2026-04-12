#!/usr/bin/env python3
"""History indexer — builds an SQLite FTS5 index over Edward's chat JSONL archive.

Archive layout (observed 2026-04):
    C:\\Users\\admin\\GoogleDrive\\聊天記錄\\jsonl\\
        2016NN.jsonl .. 2026NN.jsonl        (~118 files, one per month)
        mapping.json                         (group & sender id -> display name)

Each JSONL line is a flat JSON object. The common shape in the archive is:
    {"ts": "2016-10-14T19:25:00", "g": "g18", "s": "E", "t": "..."}

To stay forgiving for other shapes we also try: text / content / message / body /
parts[*].text for the message text, and a handful of common field aliases for
timestamp / source / author.

The index lives at:
    C:\\Users\\admin\\workspace\\digital-immortality\\results\\history_index.db

Re-runs are idempotent — we track (file, mtime, size, lines) in a `sources`
table. Only files whose mtime changed since the last run are re-indexed; on
re-index the messages rows for that file are deleted first.

Usage:
    python history_indexer.py                # full / incremental auto-detect
    python history_indexer.py --incremental  # explicit incremental
    python history_indexer.py --rebuild      # drop and rebuild everything
"""
from __future__ import annotations

import argparse
import json
import logging
import sqlite3
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

ARCHIVE_DIR = Path("C:/Users/admin/GoogleDrive/聊天記錄/jsonl")
MAPPING_FILE = ARCHIVE_DIR / "mapping.json"
RESULTS_DIR = Path("C:/Users/admin/workspace/digital-immortality/results")
DB_PATH = RESULTS_DIR / "history_index.db"
LOG_PATH = RESULTS_DIR / "history_indexer.log"

TEXT_FIELDS: tuple[str, ...] = ("t", "text", "content", "message", "body", "msg")
TS_FIELDS: tuple[str, ...] = ("ts", "timestamp", "date", "time", "created_at")
SOURCE_FIELDS: tuple[str, ...] = ("g", "source", "channel", "chat", "room")
AUTHOR_FIELDS: tuple[str, ...] = ("s", "author", "user", "sender", "from", "name")

BATCH_SIZE = 5000


@dataclass(frozen=True)
class Mapping:
    groups: dict[str, str]
    senders: dict[str, str]

    def group_name(self, gid: str) -> str:
        return self.groups.get(gid, gid)

    def sender_name(self, sid: str) -> str:
        return self.senders.get(sid, sid)


def setup_logging() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def load_mapping() -> Mapping:
    if not MAPPING_FILE.exists():
        logging.warning("mapping.json not found at %s", MAPPING_FILE)
        return Mapping(groups={}, senders={})
    try:
        data = json.loads(MAPPING_FILE.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        logging.warning("failed to parse mapping.json: %s", exc)
        return Mapping(groups={}, senders={})
    groups = data.get("groups") or {}
    senders = data.get("senders") or {}
    if not isinstance(groups, dict):
        groups = {}
    if not isinstance(senders, dict):
        senders = {}
    return Mapping(groups=groups, senders=senders)


def detect_fts5(con: sqlite3.Connection) -> bool:
    try:
        con.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS __fts_probe USING fts5(x, "
            "tokenize='unicode61 remove_diacritics 2')"
        )
        con.execute("DROP TABLE __fts_probe")
        return True
    except sqlite3.OperationalError as exc:
        logging.warning("FTS5 unavailable, falling back to LIKE: %s", exc)
        return False


def ensure_schema(con: sqlite3.Connection, *, fts5: bool) -> None:
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS sources (
            file TEXT PRIMARY KEY,
            mtime REAL NOT NULL,
            size INTEGER NOT NULL,
            line_count INTEGER NOT NULL,
            indexed_at TEXT NOT NULL
        )
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    if fts5:
        con.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS messages USING fts5(
                ts UNINDEXED,
                source UNINDEXED,
                author UNINDEXED,
                text,
                file UNINDEXED,
                line UNINDEXED,
                tokenize = 'unicode61 remove_diacritics 2'
            )
            """
        )
        con.execute(
            """
            INSERT OR REPLACE INTO meta(key, value) VALUES('engine', 'fts5')
            """
        )
    else:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                rowid INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT,
                source TEXT,
                author TEXT,
                text TEXT,
                file TEXT,
                line INTEGER
            )
            """
        )
        con.execute("CREATE INDEX IF NOT EXISTS idx_messages_file ON messages(file)")
        con.execute(
            "INSERT OR REPLACE INTO meta(key, value) VALUES('engine', 'like')"
        )


def extract_text(obj: dict[str, Any]) -> str:
    for key in TEXT_FIELDS:
        val = obj.get(key)
        if isinstance(val, str) and val.strip():
            return val
    parts = obj.get("parts")
    if isinstance(parts, list):
        acc: list[str] = []
        for p in parts:
            if isinstance(p, str):
                acc.append(p)
            elif isinstance(p, dict):
                txt = p.get("text") or p.get("content")
                if isinstance(txt, str):
                    acc.append(txt)
        joined = " ".join(a for a in acc if a)
        if joined:
            return joined
    # last resort: collapse any string-ish fields
    for v in obj.values():
        if isinstance(v, str) and len(v) > 2 and not v.startswith(("g", "s")):
            return v
    return ""


def extract_first(obj: dict[str, Any], keys: Iterable[str]) -> str:
    for key in keys:
        val = obj.get(key)
        if isinstance(val, (str, int, float)) and str(val).strip():
            return str(val)
    return ""


def iter_file_rows(
    path: Path, mapping: Mapping
) -> Iterable[tuple[str, str, str, str, str, int]]:
    """Yield (ts, source, author, text, file, line) tuples for each JSONL line."""
    file_name = path.name
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for lineno, raw in enumerate(f, start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except Exception:
                continue
            if not isinstance(obj, dict):
                continue
            text = extract_text(obj)
            if not text:
                continue
            ts = extract_first(obj, TS_FIELDS)
            src_raw = extract_first(obj, SOURCE_FIELDS)
            author_raw = extract_first(obj, AUTHOR_FIELDS)
            source = mapping.group_name(src_raw) if src_raw else ""
            author = mapping.sender_name(author_raw) if author_raw else ""
            yield (ts, source, author, text, file_name, lineno)


def index_file(
    con: sqlite3.Connection, path: Path, mapping: Mapping
) -> tuple[int, int]:
    """Index a single file, deleting any existing rows for it first.

    Returns (inserted_rows, raw_lines).
    """
    cur = con.cursor()
    cur.execute("DELETE FROM messages WHERE file = ?", (path.name,))
    batch: list[tuple] = []
    inserted = 0
    raw_lines = 0
    for row in iter_file_rows(path, mapping):
        raw_lines += 1
        batch.append(row)
        if len(batch) >= BATCH_SIZE:
            cur.executemany(
                "INSERT INTO messages(ts, source, author, text, file, line)"
                " VALUES(?, ?, ?, ?, ?, ?)",
                batch,
            )
            inserted += len(batch)
            batch.clear()
    if batch:
        cur.executemany(
            "INSERT INTO messages(ts, source, author, text, file, line)"
            " VALUES(?, ?, ?, ?, ?, ?)",
            batch,
        )
        inserted += len(batch)
    stat = path.stat()
    cur.execute(
        "INSERT OR REPLACE INTO sources(file, mtime, size, line_count, indexed_at)"
        " VALUES(?, ?, ?, ?, datetime('now'))",
        (path.name, stat.st_mtime, stat.st_size, inserted),
    )
    con.commit()
    return inserted, raw_lines


def scan_archive() -> list[Path]:
    if not ARCHIVE_DIR.exists():
        logging.error("archive dir missing: %s", ARCHIVE_DIR)
        return []
    files = sorted(ARCHIVE_DIR.glob("*.jsonl"))
    return files


def needs_reindex(con: sqlite3.Connection, path: Path) -> bool:
    stat = path.stat()
    row = con.execute(
        "SELECT mtime, size FROM sources WHERE file = ?", (path.name,)
    ).fetchone()
    if row is None:
        return True
    return abs(row[0] - stat.st_mtime) > 1e-6 or row[1] != stat.st_size


def run(rebuild: bool = False) -> int:
    setup_logging()
    logging.info("history indexer start (rebuild=%s)", rebuild)
    started = time.time()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if rebuild and DB_PATH.exists():
        DB_PATH.unlink()
        logging.info("removed existing DB for rebuild")

    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    fts5 = detect_fts5(con)
    ensure_schema(con, fts5=fts5)

    mapping = load_mapping()
    logging.info(
        "loaded mapping: %d groups, %d senders",
        len(mapping.groups),
        len(mapping.senders),
    )

    files = scan_archive()
    logging.info("found %d jsonl files", len(files))

    total_inserted = 0
    total_raw = 0
    files_indexed = 0
    files_skipped = 0
    errors: list[tuple[str, str]] = []

    for path in files:
        try:
            if not rebuild and not needs_reindex(con, path):
                files_skipped += 1
                continue
            inserted, raw_lines = index_file(con, path, mapping)
            total_inserted += inserted
            total_raw += raw_lines
            files_indexed += 1
            logging.info(
                "indexed %s -> %d rows (%d raw lines)",
                path.name,
                inserted,
                raw_lines,
            )
        except Exception as exc:  # noqa: BLE001
            errors.append((path.name, str(exc)))
            logging.exception("failed to index %s", path.name)

    total_rows = con.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    con.execute(
        "INSERT OR REPLACE INTO meta(key, value) VALUES('last_run', datetime('now'))"
    )
    con.commit()
    con.close()

    elapsed = time.time() - started
    logging.info(
        "done: files_indexed=%d skipped=%d total_rows=%d raw_lines=%d errors=%d elapsed=%.1fs",
        files_indexed,
        files_skipped,
        total_rows,
        total_raw,
        len(errors),
        elapsed,
    )
    if errors:
        for name, msg in errors:
            logging.error("error in %s: %s", name, msg)
    return 0


def query_history(query: str, limit: int = 20) -> list[dict]:
    """Search the FTS5 index for behavioral evidence."""
    if not DB_PATH.exists():
        return []
    conn = sqlite3.connect(str(DB_PATH))
    try:
        rows = conn.execute(
            "SELECT * FROM messages WHERE messages MATCH ? ORDER BY rank LIMIT ?",
            (query, limit),
        ).fetchall()
        return [{"text": r[0]} for r in rows] if rows else []
    except Exception:
        return []
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Index chat history JSONL archive")
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="drop existing DB and rebuild from scratch",
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="only re-index files whose mtime/size changed (default behaviour)",
    )
    args = parser.parse_args()
    return run(rebuild=args.rebuild)


if __name__ == "__main__":
    sys.exit(main())
