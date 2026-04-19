"""Token budget audit -- checks key files against size targets."""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TPE = ZoneInfo("Asia/Taipei")

# WSL-safe path translation: Windows C:/ paths resolve to /mnt/c/ under WSL.
IS_WSL = (sys.platform == "linux" and os.path.exists("/mnt/c"))


def _win_to_posix(p: str) -> str:
    """Translate Windows drive paths to /mnt/<drive>/ under WSL."""
    if not IS_WSL or not p:
        return p
    q = p.replace("\\", "/")
    if len(q) >= 2 and q[1] == ":" and q[0].isalpha():
        return f"/mnt/{q[0].lower()}{q[2:]}"
    return q


# Target definitions: (path, metric, limit, description)
# metric: "tokens" (chars/4), "entries" (lines starting with "- ["), "lines"
TARGETS: list[dict[str, str | int | Path]] = [
    {
        "path": Path(_win_to_posix(r"C:\Users\admin\CLAUDE.md")),
        "metric": "tokens",
        "limit": 800,
        "label": "CLAUDE.md",
    },
    {
        "path": Path(_win_to_posix(r"C:\Users\admin\LYH\agent\dna_core.md")),
        "metric": "tokens",
        "limit": 2000,
        "label": "dna_core.md",
    },
    {
        "path": Path(_win_to_posix(r"C:\Users\admin\.claude\projects\C--Users-admin\memory\MEMORY.md")),
        "metric": "entries",
        "limit": 50,
        "label": "MEMORY.md",
    },
    {
        "path": Path(_win_to_posix(r"C:\Users\admin\staging\session_state.md")),
        "metric": "lines",
        "limit": 40,
        "label": "session_state.md",
    },
]


def _count_tokens(text: str) -> int:
    """Rough token estimate: chars / 4."""
    return len(text) // 4


def _count_entries(text: str) -> int:
    """Count MEMORY.md-style entries (lines starting with '- [')."""
    return sum(1 for line in text.splitlines() if line.strip().startswith("- ["))


def _count_lines(text: str) -> int:
    """Count non-empty lines."""
    return sum(1 for line in text.splitlines() if line.strip())


def audit_file(target: dict[str, str | int | Path]) -> dict[str, str | int | bool]:
    """Audit a single file against its target. Returns result dict."""
    path = Path(target["path"])
    metric = str(target["metric"])
    limit = int(target["limit"])
    label = str(target["label"])

    if not path.exists():
        return {
            "label": label,
            "path": str(path),
            "metric": metric,
            "current": "N/A",
            "limit": limit,
            "status": "MISSING",
            "chars": 0,
        }

    text = path.read_text(encoding="utf-8")
    chars = len(text)

    if metric == "tokens":
        current = _count_tokens(text)
        unit = "tok"
    elif metric == "entries":
        current = _count_entries(text)
        unit = "entries"
    elif metric == "lines":
        current = _count_lines(text)
        unit = "lines"
    else:
        raise ValueError(f"Unknown metric: {metric}")

    status = "OK" if current <= limit else "OVER"

    return {
        "label": label,
        "path": str(path),
        "metric": metric,
        "unit": unit,
        "current": current,
        "limit": limit,
        "status": status,
        "chars": chars,
    }


def audit_all(targets: list[dict[str, str | int | Path]] | None = None) -> list[dict]:
    """Audit all target files. Returns list of result dicts."""
    if targets is None:
        targets = TARGETS
    return [audit_file(t) for t in targets]


def _print_table(results: list[dict]) -> None:
    """Print a human-readable audit table."""
    now_str = datetime.now(tz=TPE).strftime("%Y-%m-%d %H:%M +08")
    print(f"Token Budget Audit  |  {now_str}")
    print()

    label_w = max(len(str(r["label"])) for r in results)
    label_w = max(label_w, 4)

    header = f"{'File':<{label_w}}  {'Current':>10}  {'Limit':>10}  {'Chars':>8}  Status"
    print(header)
    print("-" * len(header))

    for r in results:
        if r["status"] == "MISSING":
            current_str = "N/A"
        else:
            current_str = f"{r['current']} {r['unit']}"

        limit_str = f"{r['limit']} {r.get('unit', r['metric'])}"

        print(
            f"{r['label']:<{label_w}}  "
            f"{current_str:>10}  "
            f"{limit_str:>10}  "
            f"{r['chars']:>8}  "
            f"{r['status']}"
        )

    over_count = sum(1 for r in results if r["status"] == "OVER")
    missing_count = sum(1 for r in results if r["status"] == "MISSING")

    print()
    if over_count:
        print(f"[!] {over_count} file(s) over budget.")
    if missing_count:
        print(f"[?] {missing_count} file(s) not found.")
    if not over_count and not missing_count:
        print("All files within budget.")


def main() -> None:
    results = audit_all()
    _print_table(results)

    # Exit with non-zero if any file is over budget
    if any(r["status"] == "OVER" for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
