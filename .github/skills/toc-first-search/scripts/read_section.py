"""
read_section.py  —  Stage 3: Extract a page range (or full-text search) from a PDF.

Usage — Path A (section extraction, preferred):
    python read_section.py <pdf_path> <start_page> <end_page>

Usage — Path B (full-text keyword search fallback):
    python read_section.py <pdf_path> --search <query> [--context 2]

Examples:
    python read_section.py archive/AR_standards/R24-11/CP/AUTOSAR_CP_SWS_COM.pdf 1 5
    python read_section.py archive/AR_standards/R24-11/CP/AUTOSAR_CP_SWS_COM.pdf --search "signal filter"

Output includes provenance header:
    Source: <filename>  ·  Pages: <start>–<end>  ·  Section: <title if known>
"""

import argparse
import re
import sys
from pathlib import Path

import pdfplumber


# ---------------------------------------------------------------------------
# Path A — Section/page-range extraction
# ---------------------------------------------------------------------------

def extract_pages(pdf_path: Path, start: int, end: int, section_title: str = "") -> str:
    """
    Extract text from pages start..end (1-based, inclusive).
    Returns a provenance header + extracted text.
    """
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        start = max(1, min(start, total))
        end   = max(start, min(end, total))

        provenance = (
            f"Source: {pdf_path.name}"
            + (f"  ·  Section: {section_title}" if section_title else "")
            + f"  ·  Pages: {start}–{end}"
        )
        separator = "─" * len(provenance)

        parts = [provenance, separator]
        for page_idx in range(start - 1, end):       # pdfplumber is 0-indexed
            page_text = pdf.pages[page_idx].extract_text() or ""
            parts.append(f"\n--- Page {page_idx + 1} ---\n{page_text}")

        return "\n".join(parts)


# ---------------------------------------------------------------------------
# Path B — Full-text keyword search
# ---------------------------------------------------------------------------

def _sentences_around(text: str, match_start: int, match_end: int, context: int) -> str:
    """Return ±context sentences around the match position."""
    # Split text into sentences (rough split on . / ! / ?)
    sentence_re = re.compile(r"(?<=[.!?])\s+")
    sentences = sentence_re.split(text)

    # Find which sentence contains the match offset
    offset = 0
    hit_idx = 0
    for i, sent in enumerate(sentences):
        if offset + len(sent) >= match_start:
            hit_idx = i
            break
        offset += len(sent) + 1  # +1 for the space consumed by the split

    lo = max(0, hit_idx - context)
    hi = min(len(sentences), hit_idx + context + 1)
    return " ".join(sentences[lo:hi])


def search_pdf(pdf_path: Path, query: str, context_sentences: int = 2, max_results: int = 10) -> str:
    """
    Full-text BM25-style keyword search across all pages.
    Returns passages with provenance.
    """
    keywords = [kw.lower() for kw in re.findall(r"[a-z0-9_]+", query.lower())]
    if not keywords:
        return "No valid keywords in query."

    pattern = re.compile("|".join(re.escape(kw) for kw in keywords), re.IGNORECASE)

    matches: list[dict] = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            for m in pattern.finditer(text):
                snippet = _sentences_around(text, m.start(), m.end(), context_sentences)
                # Score = number of distinct keywords found in snippet
                score = len({kw for kw in keywords if kw in snippet.lower()})
                matches.append({
                    "page":    page_idx + 1,
                    "score":   score,
                    "keyword": m.group(0),
                    "snippet": snippet.strip(),
                })

    if not matches:
        return f"No matches found for '{query}' in {pdf_path.name}"

    # Deduplicate: keep highest-score match per page, then sort
    by_page: dict[int, dict] = {}
    for hit in matches:
        if hit["page"] not in by_page or hit["score"] > by_page[hit["page"]]["score"]:
            by_page[hit["page"]] = hit

    top = sorted(by_page.values(), key=lambda x: (-x["score"], x["page"]))[:max_results]

    lines = [
        f"Source: {pdf_path.name}  ·  Full-text search: '{query}'",
        f"Found {len(by_page)} matching page(s); showing top {len(top)}",
        "─" * 60,
    ]
    for hit in top:
        lines.append(f"\n[Page {hit['page']}]  (matched: '{hit['keyword']}')  score={hit['score']}")
        lines.append(hit["snippet"])

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Extract a section or search a PDF (Stage 3)."
    )
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("start_page", nargs="?", type=int,
                        help="Start page (1-based, inclusive) — for section extraction")
    parser.add_argument("end_page", nargs="?", type=int,
                        help="End page (1-based, inclusive) — for section extraction")
    parser.add_argument("--section", default="",
                        help="Optional section title for provenance header")
    parser.add_argument("--search", default=None,
                        help="Full-text search query (Path B fallback)")
    parser.add_argument("--context", type=int, default=2,
                        help="Sentences of context around each match (default: 2)")
    args = parser.parse_args()

    pdf_path = Path(args.pdf_path).resolve()
    if not pdf_path.exists():
        sys.exit(f"Error: file not found: {pdf_path}")

    if args.search:
        # Path B — full-text search
        print(search_pdf(pdf_path, args.search, context_sentences=args.context))
    elif args.start_page is not None:
        # Path A — section extraction
        end_page = args.end_page if args.end_page is not None else args.start_page
        print(extract_pages(pdf_path, args.start_page, end_page, section_title=args.section))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
