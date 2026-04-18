"""Progressive knowledge digestion engine for the 永生樹 system.

Each daemon cycle, if no higher-priority task exists, digest one file from E:.
Track progress in results/digestion_state.json.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TPE = ZoneInfo("Asia/Taipei")
RESULTS = Path("C:/Users/admin/workspace/digital-immortality/results")
STATE_FILE = RESULTS / "digestion_state.json"
LOG_FILE = RESULTS / "digestion_log.jsonl"

# Priority tiers for E: drive content
PRIORITY_TIERS = {
    1: [  # Highest: direct trading system value
        "E:/@交易/@程式交易",
        "E:/投資交易/交易系統",
        "E:/@交易/MAEMFE",
        "E:/@交易/HiSKIO",
    ],
    2: [  # High: trading + DNA
        "E:/投資交易/量化金融文獻",
        "E:/@交易/@主觀交易",
        "E:/@交易/@選擇權",
        "E:/poker/GTO",
        "E:/poker/e-books",
    ],
    3: [  # Medium: foundational knowledge
        "E:/書籍",
        "E:/課程資料/證照考試資料",
        "E:/課程資料/財務工程_隨機財務理論",
    ],
    4: [  # Low: non-trading
        "E:/阿瓦隆百科",
        "E:/google takeout",
    ],
}

# File types we can digest
DIGESTIBLE_EXTENSIONS = {".md", ".txt", ".py", ".csv", ".json", ".pdf"}


class KnowledgeDigester:
    def __init__(self) -> None:
        self.state = self._load_state()

    def _load_state(self) -> dict:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return {
            "total_files_known": 0,
            "files_digested": 0,
            "digested_paths": [],
            "current_tier": 1,
            "last_digested_at": None,
        }

    def _save_state(self) -> None:
        RESULTS.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(
            json.dumps(self.state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def initialize(self) -> int:
        """Scan all priority directories and count digestible files."""
        total = 0
        for _tier, dirs in PRIORITY_TIERS.items():
            for d in dirs:
                p = Path(d)
                if p.exists():
                    for f in p.rglob("*"):
                        if f.is_file() and f.suffix.lower() in DIGESTIBLE_EXTENSIONS:
                            total += 1
        self.state["total_files_known"] = total
        self._save_state()
        return total

    def next_file(self) -> Path | None:
        """Return the next file to digest based on current tier."""
        digested = set(self.state.get("digested_paths", []))
        tier = self.state.get("current_tier", 1)

        for t in range(tier, max(PRIORITY_TIERS.keys()) + 1):
            for d in PRIORITY_TIERS.get(t, []):
                p = Path(d)
                if not p.exists():
                    continue
                for f in sorted(p.rglob("*")):
                    if f.is_file() and f.suffix.lower() in DIGESTIBLE_EXTENSIONS:
                        if str(f) not in digested:
                            return f
            # All files in current tier digested, move to next
            self.state["current_tier"] = t + 1

        return None  # All done

    def mark_complete(self, file_path: Path, summary: str) -> None:
        """Mark a file as digested and log the result."""
        self.state["files_digested"] += 1
        self.state["digested_paths"].append(str(file_path))
        self.state["last_digested_at"] = datetime.now(TPE).isoformat(
            timespec="seconds"
        )
        self._save_state()

        # Append to log
        entry = {
            "path": str(file_path),
            "timestamp": self.state["last_digested_at"],
            "tier": self.state["current_tier"],
            "summary_length": len(summary),
        }
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def status(self) -> str:
        """Return current digestion status."""
        return (
            f"Knowledge Digestion: {self.state['files_digested']}/{self.state['total_files_known']} files, "
            f"Tier {self.state.get('current_tier', 1)}, "
            f"Last: {self.state.get('last_digested_at', 'never')}"
        )


if __name__ == "__main__":
    d = KnowledgeDigester()
    total = d.initialize()
    print(f"Initialized: {total} digestible files found")
    print(d.status())
    nxt = d.next_file()
    if nxt:
        print(f"Next file to digest: {nxt}")
