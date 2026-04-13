"""Book scanner — extract TOC from PDF files for knowledge digestion prioritization.

Scans a directory for PDF files, extracts table of contents / bookmarks,
and outputs structured JSON for Tier 3+ knowledge digestion pipeline.

Usage:
    python book_scanner.py <directory>            # Full JSON output
    python book_scanner.py <directory> --summary   # One-line-per-file summary
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from zoneinfo import ZoneInfo

TPE = ZoneInfo("Asia/Taipei")

try:
    import fitz  # pymupdf

    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False


def _extract_toc_pymupdf(pdf_path: Path) -> dict[str, Any]:
    """Extract metadata and TOC using pymupdf (fitz)."""
    doc = fitz.open(str(pdf_path))
    metadata = doc.metadata or {}

    title = metadata.get("title", "").strip() or pdf_path.stem
    page_count = doc.page_count

    # Get bookmarks / TOC: list of [level, title, page_number]
    raw_toc = doc.get_toc(simple=True)
    toc_entries = [
        {"level": entry[0], "title": entry[1], "page": entry[2]}
        for entry in raw_toc
    ]

    doc.close()
    return {
        "title": title,
        "page_count": page_count,
        "toc_entries": toc_entries,
        "toc_source": "bookmarks" if toc_entries else "none",
    }


def _extract_toc_fallback(pdf_path: Path) -> dict[str, Any]:
    """Fallback: read first 2 pages as text to guess TOC content."""
    try:
        import fitz

        doc = fitz.open(str(pdf_path))
        metadata = doc.metadata or {}
        title = metadata.get("title", "").strip() or pdf_path.stem
        page_count = doc.page_count

        first_pages_text: list[str] = []
        for page_num in range(min(2, page_count)):
            page = doc.load_page(page_num)
            text = page.get_text("text").strip()
            if text:
                first_pages_text.append(text)

        doc.close()

        # Parse lines that look like TOC entries (lines with page numbers at the end)
        toc_entries: list[dict[str, Any]] = []
        for text in first_pages_text:
            for line in text.split("\n"):
                line = line.strip()
                if not line:
                    continue
                # Heuristic: lines ending with a number, possibly preceded by dots/spaces
                parts = line.rstrip(".… \t").rsplit(None, 1)
                if len(parts) == 2 and parts[1].isdigit():
                    toc_entries.append(
                        {"level": 1, "title": parts[0].rstrip(".… \t"), "page": int(parts[1])}
                    )

        return {
            "title": title,
            "page_count": page_count,
            "toc_entries": toc_entries,
            "toc_source": "first_pages_heuristic" if toc_entries else "none",
        }
    except Exception:
        # If even fitz text extraction fails, return minimal info
        return {
            "title": pdf_path.stem,
            "page_count": -1,
            "toc_entries": [],
            "toc_source": "error",
        }


def scan_pdf(pdf_path: Path) -> dict[str, Any]:
    """Scan a single PDF and return structured metadata + TOC."""
    if not HAS_PYMUPDF:
        return {
            "file": str(pdf_path),
            "title": pdf_path.stem,
            "page_count": -1,
            "toc_entries": [],
            "toc_source": "unavailable",
            "error": "pymupdf not installed",
        }

    try:
        result = _extract_toc_pymupdf(pdf_path)

        # If no bookmarks found, try fallback heuristic on first pages
        if not result["toc_entries"]:
            fallback = _extract_toc_fallback(pdf_path)
            result["toc_entries"] = fallback["toc_entries"]
            result["toc_source"] = fallback["toc_source"]

        result["file"] = str(pdf_path)
        result["error"] = None
        return result

    except Exception as e:
        return {
            "file": str(pdf_path),
            "title": pdf_path.stem,
            "page_count": -1,
            "toc_entries": [],
            "toc_source": "error",
            "error": str(e),
        }


def scan_directory(directory: Path) -> list[dict[str, Any]]:
    """Scan all PDF files in a directory (non-recursive) and extract TOC data."""
    if not directory.is_dir():
        print(f"Error: '{directory}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    pdf_files = sorted(directory.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in '{directory}'.", file=sys.stderr)
        return []

    results: list[dict[str, Any]] = []
    for pdf_path in pdf_files:
        results.append(scan_pdf(pdf_path))

    return results


def format_summary(results: list[dict[str, Any]]) -> str:
    """One-line-per-file summary."""
    lines: list[str] = []
    for r in results:
        toc_count = len(r.get("toc_entries", []))
        pages = r.get("page_count", -1)
        source = r.get("toc_source", "unknown")
        error_tag = f" [ERROR: {r['error']}]" if r.get("error") else ""
        lines.append(
            f"{r['title']}  |  {pages} pages  |  {toc_count} TOC entries ({source}){error_tag}"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan PDF files and extract table of contents for knowledge digestion."
    )
    parser.add_argument("directory", type=Path, help="Directory containing PDF files to scan")
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print one-line-per-file summary instead of full JSON",
    )
    args = parser.parse_args()

    if not HAS_PYMUPDF:
        print(
            "Warning: pymupdf not installed. Install it for full functionality:\n"
            "  pip install pymupdf\n",
            file=sys.stderr,
        )

    results = scan_directory(args.directory)

    # Add scan metadata
    scan_time = datetime.now(tz=TPE).isoformat()

    if args.summary:
        print(f"Scanned at {scan_time} (Asia/Taipei)")
        print(f"Found {len(results)} PDF files in {args.directory}\n")
        print(format_summary(results))
    else:
        output = {
            "scanned_at": scan_time,
            "directory": str(args.directory),
            "file_count": len(results),
            "files": results,
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
