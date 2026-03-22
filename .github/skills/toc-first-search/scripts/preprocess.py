"""
preprocess.py  —  Stage 0: Build the search index for a PDF collection.

Usage:
    python preprocess.py <pdf_dir> [--output index.json] [--force]

For each PDF it extracts:
  - Metadata (title, author, creation date from PDF properties)
  - First 2 pages of text  (used for BM25 ranking in Stage 1)
  - Table of Contents       (used for section selection in Stage 2)

Output: a single JSON file (default: index.json next to the PDFs).
Re-run is incremental — only re-processes PDFs whose MD5 hash changed.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import pdfplumber


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_metadata(pdf) -> dict:
    """Return a cleaned metadata dict from pdf.metadata."""
    meta = pdf.metadata or {}
    return {
        "title":   (meta.get("Title")  or "").strip(),
        "author":  (meta.get("Author") or "").strip(),
        "subject": (meta.get("Subject") or "").strip(),
        "keywords":(meta.get("Keywords") or "").strip(),
        "creator": (meta.get("Creator") or "").strip(),
        "date":    (meta.get("CreationDate") or "").strip(),
        "pages":   len(pdf.pages),
    }


# ---------------------------------------------------------------------------
# TOC extraction
# ---------------------------------------------------------------------------

# Matches lines like:
#   1  Overview  .......  3
#   2.1  Architecture  ....  15
#   Appendix A  Reference  .  120
_TOC_LINE_RE = re.compile(
    r'^(?P<num>[\dA-Z][\d\.A-Z]*\.?\s+)?'   # optional section number
    r'(?P<title>[A-Za-z].{3,80}?)'           # section title (3–80 chars)
    r'[\s\.…\-]{2,}'                          # separator (dots/dashes/spaces)
    r'(?P<page>\d{1,4})\s*$',               # page number at end of line
    re.UNICODE,
)

# Heading lines with page on same line: "1.2 Signal Mapping 16"
_TOC_COMPACT_RE = re.compile(
    r'^(?P<num>[\dA-Z][\d\.A-Z]*\.?\s+)'
    r'(?P<title>[A-Za-z].{3,60}?)\s+'
    r'(?P<page>\d{1,4})\s*$',
    re.UNICODE,
)


def _parse_toc_lines(lines: list[str]) -> list[dict]:
    entries = []
    for line in lines:
        line = line.strip()
        for pattern in (_TOC_LINE_RE, _TOC_COMPACT_RE):
            m = pattern.match(line)
            if m:
                num   = (m.group("num") or "").strip()
                title = m.group("title").strip()
                page  = int(m.group("page"))
                entries.append({"num": num, "title": title, "start_page": page})
                break
    return entries


def _assign_end_pages(entries: list[dict], total_pages: int) -> list[dict]:
    for i, entry in enumerate(entries):
        if i + 1 < len(entries):
            entry["end_page"] = entries[i + 1]["start_page"] - 1
        else:
            entry["end_page"] = total_pages
    return entries


def extract_toc(pdf) -> list[dict]:
    """
    Scan the first 15 pages for a Table of Contents section.
    Returns a list of {num, title, start_page, end_page} dicts.
    Falls back to empty list if none found.
    """
    toc_start = -1
    all_lines: list[str] = []

    scan_pages = min(15, len(pdf.pages))
    for page_idx in range(scan_pages):
        text = pdf.pages[page_idx].extract_text() or ""
        lines = text.splitlines()

        # Detect the TOC page
        for i, line in enumerate(lines):
            lower = line.lower()
            if toc_start < 0 and any(
                kw in lower for kw in ("table of contents", "contents", "inhaltsverzeichnis")
            ):
                toc_start = page_idx
                all_lines.extend(lines[i + 1 :])
                break
        else:
            if toc_start >= 0:
                all_lines.extend(lines)

        # Stop after we've collected 3 pages past the TOC start
        if toc_start >= 0 and page_idx >= toc_start + 3:
            break

    if not all_lines:
        return []

    entries = _parse_toc_lines(all_lines)
    if len(entries) < 2:
        return []

    return _assign_end_pages(entries, len(pdf.pages))


# ---------------------------------------------------------------------------
# First-page text  (used for BM25)
# ---------------------------------------------------------------------------

def extract_head_text(pdf, num_pages: int = 2) -> str:
    parts = []
    for i in range(min(num_pages, len(pdf.pages))):
        text = pdf.pages[i].extract_text() or ""
        parts.append(text)
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Per-file processing
# ---------------------------------------------------------------------------

def process_pdf(path: Path) -> dict | None:
    try:
        with pdfplumber.open(path) as pdf:
            meta = extract_metadata(pdf)
            # Prefer the PDF Title property; fall back to the filename stem
            title = meta["title"] or path.stem
            # Make the title human-readable when it's just a filename
            display_title = title.replace("_", " ").replace("-", " ")

            return {
                "path":       str(path),
                "filename":   path.name,
                "title":      display_title,
                "raw_title":  title,
                "md5":        md5(path),
                "meta":       meta,
                "head_text":  extract_head_text(pdf, num_pages=2),
                "toc":        extract_toc(pdf),
            }
    except Exception as exc:
        print(f"  [WARN] Could not process {path.name}: {exc}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_index(pdf_dir: Path, output: Path, force: bool) -> None:
    # Load existing index if present
    existing: dict[str, dict] = {}
    if output.exists() and not force:
        with open(output, encoding="utf-8") as f:
            existing = {entry["path"]: entry for entry in json.load(f)}

    pdfs = sorted(pdf_dir.glob("**/*.pdf"))
    print(f"Found {len(pdfs)} PDF(s) in {pdf_dir}")

    results = []
    for pdf_path in pdfs:
        key = str(pdf_path)
        current_md5 = md5(pdf_path)

        if key in existing and existing[key].get("md5") == current_md5:
            print(f"  [SKIP]  {pdf_path.name}  (unchanged)")
            results.append(existing[key])
            continue

        print(f"  [INDEX] {pdf_path.name} …", end=" ", flush=True)
        entry = process_pdf(pdf_path)
        if entry:
            results.append(entry)
            print(f"{entry['meta']['pages']}p, {len(entry['toc'])} TOC entries")
        else:
            print("FAILED")

    with open(output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nIndex written to {output}  ({len(results)} documents)")


def main():
    parser = argparse.ArgumentParser(description="Build PDF search index.")
    parser.add_argument("pdf_dir", help="Directory containing PDFs (searched recursively)")
    parser.add_argument("--output", default=None, help="Output JSON path (default: <pdf_dir>/index.json)")
    parser.add_argument("--force", action="store_true", help="Re-index all files even if unchanged")
    args = parser.parse_args()

    pdf_dir = Path(args.pdf_dir).resolve()
    if not pdf_dir.is_dir():
        sys.exit(f"Error: {pdf_dir} is not a directory.")

    output = Path(args.output) if args.output else pdf_dir / "index.json"
    build_index(pdf_dir, output, args.force)


if __name__ == "__main__":
    main()
