# The Archive — Workspace Instructions

## Purpose
This workspace is a knowledge archive for searching and extracting information from large document collections. The primary document types are AUTOSAR Classic Platform specification PDFs.

## Structure

```
archive/
  AR_standards/
    R24-11/
      CP/            ← AUTOSAR CP spec PDFs (35 docs, R24-11 release)
                        index.json  ← pre-built BM25 search index

.vscode/
  mcp.json           ← Registers the archive-tools MCP server with VS Code

.github/
  copilot-instructions.md
  agents/
    archivist.agent.md    ← Archivist agent (uses archive-tools MCP tools)
  mcp/
    archive-tools/
      server.py           ← FastMCP server: preprocess / search / read_section
  skills/
    toc-first-search/
      SKILL.md            ← Three-Stage TOC-First search skill
      scripts/
        preprocess.py     ← Stage 0: build index.json from a PDF folder
        search.py         ← Stage 1+2: BM25 search + TOC highlighting
        read_section.py   ← Stage 3: page-range extraction or full-text search
      references/
        consume_pdf.md    ← Full technical specification of the strategy
```

## Python Environment
- Virtual environment: `.venv/` at workspace root
- Run scripts with: `.venv/Scripts/python.exe <script>`
- Installed packages: `pdfplumber`, `rank_bm25`, `fastmcp`

## Search Index
Each PDF collection has a pre-built `index.json` at its root. The index is incremental — re-run `preprocess.py` after adding new PDFs to update it.

Current indexes:
- `archive/AR_standards/R24-11/CP/index.json` — 35 AUTOSAR CP R24-11 specs

## Key Conventions
- Always provide source provenance with extracted content: document title, section name, page range.
- Never return decontextualized snippets.
- Use the `toc-first-search` skill for all document retrieval tasks.
