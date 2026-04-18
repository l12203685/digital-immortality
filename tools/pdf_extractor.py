#!/usr/bin/env python3
"""
PDF Text Extraction Pipeline for Edward's Knowledge Base
=========================================================
Extracts text from PDFs and outputs Markdown files for AI digestion.

Usage:
    # Extract a single PDF:
    python pdf_extractor.py extract "E:/書籍/book.pdf" --output-dir C:/Users/admin/staging/pdf_extracted

    # Batch extract a directory:
    python pdf_extractor.py batch "E:/書籍" --output-dir C:/Users/admin/staging/pdf_extracted

    # Extract $$$ priority books only:
    python pdf_extractor.py priority --output-dir C:/Users/admin/staging/pdf_extracted

Dependencies: pymupdf (pip install pymupdf)
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

try:
    import fitz  # pymupdf
except ImportError:
    print("ERROR: pymupdf not installed. Run: pip install pymupdf")
    sys.exit(1)


# ── Constants ──────────────────────────────────────────────────────────────────

PRIORITY_PREFIX = "$$$"
MIN_TEXT_CHARS_PER_PAGE = 50  # below this → page is image/scanned
PROGRESS_EVERY = 10           # pages between progress prints


# ── Data types ─────────────────────────────────────────────────────────────────

@dataclass
class ExtractionResult:
    source_path: str
    output_path: str
    pages_total: int
    pages_extracted: int
    pages_skipped_ocr: int
    chars_extracted: int
    is_priority: bool
    scanned_ratio: float       # fraction of pages that were image-only
    duration_sec: float
    success: bool
    error: Optional[str] = None


# ── Core extraction ────────────────────────────────────────────────────────────

def _clean_text(raw: str) -> str:
    """Normalize whitespace, remove garbage control chars."""
    # Replace form-feed and other control chars
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', raw)
    # Collapse 3+ blank lines to 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Strip trailing whitespace per line
    lines = [l.rstrip() for l in text.splitlines()]
    return '\n'.join(lines).strip()


def _page_is_scanned(text: str) -> bool:
    """True if a page has almost no machine-readable text (likely image/scan)."""
    return len(text.strip()) < MIN_TEXT_CHARS_PER_PAGE


def _make_output_stem(pdf_path: Path) -> str:
    """Convert PDF filename to a safe output stem."""
    stem = pdf_path.stem
    # Remove $$$prefix for cleaner filenames
    stem = stem.replace("$$$ ", "").replace("$$$", "")
    # Collapse special chars
    stem = re.sub(r'[<>:"/\\|?*]', '_', stem)
    return stem.strip("_- ")


def _build_markdown_header(pdf_path: Path, doc: fitz.Document) -> str:
    """Build YAML-ish frontmatter + title block."""
    meta = doc.metadata or {}
    title = meta.get("title", "").strip() or pdf_path.stem
    author = meta.get("author", "").strip() or "Unknown"
    pages = doc.page_count
    source = str(pdf_path)
    is_priority = pdf_path.name.startswith(PRIORITY_PREFIX)

    header = f"""---
title: "{title}"
author: "{author}"
source: "{source}"
pages: {pages}
priority: {"true" if is_priority else "false"}
extracted: "{time.strftime('%Y-%m-%d %H:%M +08')}"
---

# {title}

**Author:** {author}
**Source:** `{source}`
**Pages:** {pages}
**Priority:** {"YES ($$$ marked)" if is_priority else "No"}

---

"""
    return header


def extract_pdf(
    path: str | Path,
    output_dir: str | Path,
    ocr_fallback: bool = False,
    force: bool = False,
) -> ExtractionResult:
    """
    Extract text from a single PDF → Markdown file.

    Args:
        path:        Path to source PDF.
        output_dir:  Directory to write .md output.
        ocr_fallback: If True, attempt OCR on image pages (requires tesseract).
        force:       Re-extract even if output already exists.

    Returns:
        ExtractionResult with stats.
    """
    pdf_path = Path(path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = _make_output_stem(pdf_path)
    out_path = out_dir / f"{stem}.md"

    # Skip if already extracted
    if out_path.exists() and not force:
        # Read existing to return stats
        existing_chars = out_path.stat().st_size
        return ExtractionResult(
            source_path=str(pdf_path),
            output_path=str(out_path),
            pages_total=0,
            pages_extracted=0,
            pages_skipped_ocr=0,
            chars_extracted=existing_chars,
            is_priority=pdf_path.name.startswith(PRIORITY_PREFIX),
            scanned_ratio=0.0,
            duration_sec=0.0,
            success=True,
            error="SKIPPED (already extracted)",
        )

    t0 = time.time()
    is_priority = pdf_path.name.startswith(PRIORITY_PREFIX)

    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        return ExtractionResult(
            source_path=str(pdf_path),
            output_path=str(out_path),
            pages_total=0,
            pages_extracted=0,
            pages_skipped_ocr=0,
            chars_extracted=0,
            is_priority=is_priority,
            scanned_ratio=1.0,
            duration_sec=time.time() - t0,
            success=False,
            error=f"Cannot open PDF: {e}",
        )

    n_pages = doc.page_count
    pages_extracted = 0
    pages_skipped = 0
    all_parts = [_build_markdown_header(pdf_path, doc)]

    for i, page in enumerate(doc):
        raw = page.get_text("text", sort=True)

        if _page_is_scanned(raw):
            pages_skipped += 1
            if ocr_fallback:
                # OCR via pymupdf built-in (requires tesseract in PATH)
                try:
                    tp = page.get_textpage_ocr(language="eng", full=False)
                    raw = page.get_text(textpage=tp)
                except Exception:
                    pass  # OCR failed, skip page silently

            if _page_is_scanned(raw):
                all_parts.append(f"\n\n<!-- Page {i+1}: image/scanned, no text -->\n\n")
                continue

        cleaned = _clean_text(raw)
        all_parts.append(f"\n\n<!-- Page {i+1} -->\n\n{cleaned}")
        pages_extracted += 1

        if (i + 1) % PROGRESS_EVERY == 0:
            pct = (i + 1) / n_pages * 100
            print(f"  [{pdf_path.name[:50]}] {i+1}/{n_pages} pages ({pct:.0f}%)", flush=True)

    doc.close()

    full_text = "\n".join(all_parts)
    out_path.write_text(full_text, encoding="utf-8")

    duration = time.time() - t0
    scanned_ratio = pages_skipped / n_pages if n_pages > 0 else 0.0

    return ExtractionResult(
        source_path=str(pdf_path),
        output_path=str(out_path),
        pages_total=n_pages,
        pages_extracted=pages_extracted,
        pages_skipped_ocr=pages_skipped,
        chars_extracted=len(full_text),
        is_priority=is_priority,
        scanned_ratio=scanned_ratio,
        duration_sec=duration,
        success=True,
    )


# ── Batch extraction ───────────────────────────────────────────────────────────

def batch_extract(
    directory: str | Path,
    output_dir: str | Path,
    recursive: bool = True,
    ocr_fallback: bool = False,
    priority_first: bool = True,
    force: bool = False,
    limit: Optional[int] = None,
) -> list[ExtractionResult]:
    """
    Batch-extract all PDFs in a directory.

    Args:
        directory:     Root directory to scan.
        output_dir:    Where to write .md files (mirrors subdirs).
        recursive:     Walk subdirectories.
        ocr_fallback:  Try OCR on scanned pages.
        priority_first: Extract $$$ books before others.
        force:         Re-extract even if output exists.
        limit:         Max number of PDFs to process (None = all).

    Returns:
        List of ExtractionResult, one per PDF.
    """
    src_dir = Path(directory)
    out_dir = Path(output_dir)

    pattern = "**/*.pdf" if recursive else "*.pdf"
    all_pdfs = sorted(src_dir.glob(pattern))

    if priority_first:
        priority = [p for p in all_pdfs if p.name.startswith(PRIORITY_PREFIX)]
        rest = [p for p in all_pdfs if not p.name.startswith(PRIORITY_PREFIX)]
        all_pdfs = priority + rest

    if limit:
        all_pdfs = all_pdfs[:limit]

    total = len(all_pdfs)
    print(f"Found {total} PDFs in {src_dir}")
    print(f"Output directory: {out_dir}")
    print(f"Priority books first: {priority_first}\n")

    results = []
    for idx, pdf in enumerate(all_pdfs, 1):
        label = "[PRIORITY] " if pdf.name.startswith(PRIORITY_PREFIX) else ""
        print(f"[{idx}/{total}] {label}{pdf.name[:70]}")

        # Mirror subdirectory structure in output
        rel = pdf.parent.relative_to(src_dir)
        sub_out = out_dir / rel

        result = extract_pdf(pdf, sub_out, ocr_fallback=ocr_fallback, force=force)

        if result.error:
            print(f"  -> {result.error}")
        else:
            print(
                f"  -> {result.pages_extracted}/{result.pages_total} pages, "
                f"{result.chars_extracted:,} chars, "
                f"{result.duration_sec:.1f}s"
                + (f", scanned: {result.scanned_ratio:.0%}" if result.scanned_ratio > 0 else "")
            )

        results.append(result)

    return results


def extract_priority_books(
    search_dirs: list[str | Path],
    output_dir: str | Path,
    ocr_fallback: bool = False,
    force: bool = False,
) -> list[ExtractionResult]:
    """
    Find and extract all $$$ priority books across multiple directories.
    """
    results = []
    for directory in search_dirs:
        src = Path(directory)
        if not src.exists():
            print(f"Skipping (not found): {src}")
            continue
        pdfs = list(src.rglob("$$$*.pdf"))
        print(f"Found {len(pdfs)} priority PDFs in {src}")
        for pdf in pdfs:
            print(f"  Extracting: {pdf.name}")
            result = extract_pdf(pdf, output_dir, ocr_fallback=ocr_fallback, force=force)
            if result.error:
                print(f"    -> {result.error}")
            else:
                print(
                    f"    -> {result.pages_extracted}/{result.pages_total} pages, "
                    f"{result.chars_extracted:,} chars, {result.duration_sec:.1f}s"
                )
            results.append(result)
    return results


# ── Report ─────────────────────────────────────────────────────────────────────

def print_summary(results: list[ExtractionResult]) -> None:
    """Print a compact extraction summary."""
    total = len(results)
    ok = [r for r in results if r.success and not (r.error and "SKIPPED" in str(r.error))]
    skipped = [r for r in results if r.error and "SKIPPED" in str(r.error)]
    failed = [r for r in results if not r.success]

    total_chars = sum(r.chars_extracted for r in ok)
    total_pages = sum(r.pages_total for r in ok)
    total_time = sum(r.duration_sec for r in ok)

    print("\n" + "=" * 60)
    print("EXTRACTION SUMMARY")
    print("=" * 60)
    print(f"Total PDFs:      {total}")
    print(f"Extracted:       {len(ok)}")
    print(f"Skipped (cache): {len(skipped)}")
    print(f"Failed:          {len(failed)}")
    print(f"Total pages:     {total_pages:,}")
    print(f"Total chars:     {total_chars:,}")
    print(f"Total time:      {total_time:.1f}s")

    if failed:
        print("\nFailed files:")
        for r in failed:
            print(f"  {Path(r.source_path).name}: {r.error}")


def save_manifest(results: list[ExtractionResult], output_dir: str | Path) -> Path:
    """Save extraction manifest as JSON for later reference."""
    manifest_path = Path(output_dir) / "_extraction_manifest.json"
    data = [asdict(r) for r in results]
    manifest_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest_path


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="PDF text extraction pipeline for Edward's knowledge base",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # extract single file
    p_extract = sub.add_parser("extract", help="Extract a single PDF")
    p_extract.add_argument("pdf", help="Path to PDF file")
    p_extract.add_argument("--output-dir", default="C:/Users/admin/staging/pdf_extracted")
    p_extract.add_argument("--ocr", action="store_true", help="Enable OCR fallback for scanned pages")
    p_extract.add_argument("--force", action="store_true", help="Re-extract even if output exists")

    # batch extract directory
    p_batch = sub.add_parser("batch", help="Batch-extract all PDFs in a directory")
    p_batch.add_argument("directory", help="Source directory")
    p_batch.add_argument("--output-dir", default="C:/Users/admin/staging/pdf_extracted")
    p_batch.add_argument("--no-recursive", action="store_true", help="Don't recurse into subdirs")
    p_batch.add_argument("--ocr", action="store_true")
    p_batch.add_argument("--force", action="store_true")
    p_batch.add_argument("--limit", type=int, help="Max PDFs to process")

    # extract priority books only
    p_priority = sub.add_parser("priority", help="Extract $$$ priority books from all known dirs")
    p_priority.add_argument("--output-dir", default="C:/Users/admin/staging/pdf_extracted/priority")
    p_priority.add_argument("--ocr", action="store_true")
    p_priority.add_argument("--force", action="store_true")
    p_priority.add_argument(
        "--dirs",
        nargs="+",
        default=["E:/書籍", "E:/投資交易/金融書籍", "E:/投資交易/交易學習資料"],
        help="Directories to search for $$$ books",
    )

    args = parser.parse_args()

    if args.cmd == "extract":
        result = extract_pdf(args.pdf, args.output_dir, ocr_fallback=args.ocr, force=args.force)
        print_summary([result])

    elif args.cmd == "batch":
        results = batch_extract(
            args.directory,
            args.output_dir,
            recursive=not args.no_recursive,
            ocr_fallback=args.ocr,
            priority_first=True,
            force=args.force,
            limit=args.limit,
        )
        print_summary(results)
        manifest = save_manifest(results, args.output_dir)
        print(f"\nManifest saved: {manifest}")

    elif args.cmd == "priority":
        results = extract_priority_books(
            args.dirs,
            args.output_dir,
            ocr_fallback=args.ocr,
            force=args.force,
        )
        print_summary(results)
        manifest = save_manifest(results, args.output_dir)
        print(f"\nManifest saved: {manifest}")


if __name__ == "__main__":
    main()
