"""
archive-tools MCP server
Exposes three archive search tools to GitHub Copilot agents via the
Model Context Protocol (FastMCP / stdio transport).

Tools:
  preprocess    — Stage 0: build index.json from a PDF folder
  search        — Stage 1+2: BM25 ranking + TOC section highlighting
  read_section  — Stage 3: extract a page range or run full-text search
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

# Resolve paths relative to the workspace root (three parent levels up from this file:
#  server.py → archive-tools/ → mcp/ → .github/ → workspace root)
_HERE = Path(__file__).resolve().parent
_WORKSPACE = _HERE.parents[2]
_SCRIPTS = _WORKSPACE / ".github" / "skills" / "toc-first-search" / "scripts"

# Add scripts dir to path so we can import them as modules directly
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

# ---------------------------------------------------------------------------
# Direct imports from the skill scripts (no subprocess overhead)
# ---------------------------------------------------------------------------

import preprocess as _preprocess_mod
import search as _search_mod
import read_section as _read_section_mod

# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="archive-tools",
    instructions=(
        "Tools for searching and extracting content from archived document "
        "collections (PDFs, markdown, specs). Use these tools in sequence: "
        "preprocess once per collection, then search to rank and reveal TOC, "
        "then read_section to extract the relevant content."
    ),
)

# ---------------------------------------------------------------------------
# Tool 1 — preprocess
# ---------------------------------------------------------------------------

@mcp.tool
def preprocess(pdf_dir: str, force: bool = False) -> str:
    """Build (or update) the BM25 search index for a PDF collection.

    Scans pdf_dir recursively for PDFs, extracts metadata + first-page text +
    table of contents for each file, and writes index.json next to the PDFs.
    Re-running is safe and incremental — only changed files are re-processed.

    Args:
        pdf_dir: Path to the folder containing the PDFs (relative to workspace root).
        force:   Re-index all files even if unchanged. Default: False.
    """
    pdf_path = (_WORKSPACE / pdf_dir).resolve()
    output_path = pdf_path / "index.json"

    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        _preprocess_mod.build_index(pdf_path, output_path, force)
    return buf.getvalue().strip()


# ---------------------------------------------------------------------------
# Tool 2 — search
# ---------------------------------------------------------------------------

@mcp.tool
def search(
    query: str,
    index_path: str = "archive/AR_standards/R24-11/CP/index.json",
    top_k: int = 5,
) -> str:
    """Search the archive and return ranked documents with TOC section highlights.

    Implements Stage 1 (BM25 relevance scoring) and Stage 2 (TOC extraction +
    section highlighting) of the Three-Stage TOC-First strategy.

    Returns structured JSON with:
    - Ranked document list with relevance percentages
    - Table of contents for each match, with likely-relevant sections flagged

    Args:
        query:      Search query — keywords or a natural-language question.
        index_path: Path to index.json (relative to workspace root).
                    Default: archive/AR_standards/R24-11/CP/index.json
        top_k:      Number of top documents to return. Default: 5.
    """
    idx_path = (_WORKSPACE / index_path).resolve()
    docs   = _search_mod.load_index(idx_path)
    ranked = _search_mod.rank_documents(query, docs, top_k=top_k)
    normed = _search_mod.normalise_scores(ranked)
    return json.dumps(
        _search_mod.build_json_output(query, normed),
        indent=2,
        ensure_ascii=False,
    )


# ---------------------------------------------------------------------------
# Tool 3 — read_section
# ---------------------------------------------------------------------------

@mcp.tool
def read_section(
    pdf_path: str,
    start_page: int | None = None,
    end_page: int | None = None,
    section_title: str = "",
    search_query: str = "",
    context_sentences: int = 2,
) -> str:
    """Extract a section from a PDF or run a full-text keyword search.

    Implements Stage 3 of the Three-Stage TOC-First strategy.

    **Path A — section extraction (preferred):**
    Provide start_page (and optionally end_page) to extract an exact page range.
    Returns the text with a provenance header:
      Source: <filename>  ·  Section: <title>  ·  Pages: <start>-<end>

    **Path B — full-text search fallback:**
    Provide search_query to search across the entire PDF when no TOC was found.
    Returns the top 10 matching passages with surrounding context.

    Args:
        pdf_path:          Path to the PDF file (relative to workspace root).
        start_page:        First page to extract, 1-based (Path A).
        end_page:          Last page to extract, 1-based (Path A). Defaults to start_page.
        section_title:     Section name for the provenance header (Path A, optional).
        search_query:      Keyword/phrase to search across the full PDF (Path B).
        context_sentences: Sentences of context around each match (Path B). Default: 2.
    """
    resolved = (_WORKSPACE / pdf_path).resolve()

    if start_page is not None:
        return _read_section_mod.extract_pages(
            resolved, start_page,
            end_page if end_page is not None else start_page,
            section_title=section_title,
        )
    elif search_query:
        return _read_section_mod.search_pdf(
            resolved, search_query,
            context_sentences=context_sentences,
        )
    else:
        raise ValueError(
            "Provide either start_page (section extraction) or "
            "search_query (full-text search)."
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()  # stdio transport — VS Code spawns this process and communicates via stdin/stdout
