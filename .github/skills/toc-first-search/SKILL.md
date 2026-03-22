---
name: toc-first-search
description: "Use when: searching or retrieving knowledge from any document collection — PDFs, markdown files, text documents, technical specs, wikis, code docs, AUTOSAR specs, design docs, or standards archives. Trigger phrases: search documents, find information, look up in archive, extract from PDF, scan specs, retrieve knowledge, what does X say about Y, summarize docs, search archive. Implements the Three-Stage TOC-First strategy: fast relevance scoring → structure extraction → targeted section reading."
argument-hint: "Describe what you are looking for. Example: 'How is signal mapping configured in AUTOSAR?' or 'Summarize the architecture section of the design doc.'"
---

# Three-Stage TOC-First Search

A knowledge retrieval workflow that combines relevance scoring, table-of-contents extraction, and targeted section reading — reducing search time by 2–10x versus brute-force full-text scanning.

Full technical specification: [references/consume_pdf.md](./references/consume_pdf.md)

## Scripts

| Script | Stage | Purpose |
|--------|-------|---------|
| [scripts/preprocess.py](./scripts/preprocess.py) | 0 — Setup | Index a PDF folder; extracts metadata, first-page text, and TOC for every PDF |
| [scripts/search.py](./scripts/search.py) | 1 + 2 | BM25 search → ranked list + TOC with highlighted sections |
| [scripts/read_section.py](./scripts/read_section.py) | 3 | Extract a page range (Path A) or run full-text keyword search (Path B) |

**Python environment:** `.venv` at workspace root. Dependencies: `pdfplumber`, `rank_bm25`.

---

## When to Use

- Searching for specific information across a large document collection (10–1,000s of files)
- Extracting content from PDFs, markdown, plaintext, HTML exports, or code docs
- When precise answers with source provenance (document, section, page/line range) are required

---

## Stage 0 — Index (one-time setup per collection)

Build the search index before running any query.

```
python .github/skills/toc-first-search/scripts/preprocess.py <pdf_dir>
# produces: <pdf_dir>/index.json  (incremental — skips unchanged PDFs)
```

---

## Stage 1 — Fast Relevance Scoring

**Goal:** Identify the top 3–5 most relevant sources without reading them in full.

```
python .github/skills/toc-first-search/scripts/search.py "<query>" --index <pdf_dir>/index.json
# add --json for structured output  |  --top N to change result count
```

1. Parse the query into keywords and intent.
2. BM25 search across filename + title + first-page text of all indexed docs.
3. Rank by relevance — exact keyword matches first, then partial.
4. Output a ranked list with estimated relevance (%):
   ```
   1. <Title> (92%) — <relative path>
   2. <Title> (78%) — <relative path>
   3. <Title> (64%) — <relative path>
   ```
5. Proceed with the top 3–5 documents.

**Time target:** < 2s for up to 1,000 docs (index is pre-built).

---

## Stage 2 — Structure Extraction & Section Selection

**Goal:** Use document structure to guide reading — never scan blindly.

For each top-ranked source:

1. Read the opening section to detect structure:
   - PDFs → Table of Contents (chapter names + page ranges)
   - Markdown / HTML → heading hierarchy (heading anchors or line ranges)
2. Parse section/chapter names and their locations.
3. Present the structure alongside the relevance score, with likely-relevant sections highlighted:
   ```
   ComScl_ModelMngr (92%):
     1. Overview (pp. 1–5)
     2. Architecture (pp. 6–15)
     3. Signal Mapping (pp. 16–35)  ← likely relevant
     4. API Reference (pp. 36–50)
   ```
4. Select sections based on query intent (or ask the user to confirm).

**Fallback — no structure detected:** Flag the source and proceed to Stage 3, Path B.

**Time target:** < 2s per document.

---

## Stage 3 — Contextual Extraction

### Path A — Section-based extraction (preferred)

Use when Stage 2 produced a valid structure.

```
python .github/skills/toc-first-search/scripts/read_section.py <pdf_path> <start_page> <end_page> [--section "<title>"]
```

1. Extract only the selected sections (page ranges for PDFs).
2. Parse content into paragraphs, tables, and code blocks.
3. Return results with full provenance:
   > **Source:** `<filename>`  ·  Section: `<name>`  ·  Pages: `<start>–<end>`

**Time target:** 1–3s per chapter.

### Path B — Full-text search fallback

Use when no structure was detected in Stage 2.

```
python .github/skills/toc-first-search/scripts/read_section.py <pdf_path> --search "<query>" [--context 2]
```

1. Run a targeted keyword search across the full source text.
2. Extract matching passages with ±N sentences of surrounding context.
3. Return results with page number and a relevance score.

**Time target:** 5–10s per 100-page PDF.

---

## Output Format

Always structure results in three parts:

1. **Ranked source list** from Stage 1.
2. **Structure summaries** with highlighted sections from Stage 2.
3. **Extracted content** with provenance from Stage 3:
   > **Source:** `<file path>` · Section: `<name>` · Location: `<pages or lines>`

Use headers and code blocks to preserve document structure. Separate multiple section results clearly.

---

## Constraints

- Do NOT scan all sources in full — relevance scoring filters first.
- Do NOT return decontextualized snippets without provenance.
- Do NOT skip Stage 2 unless the source has no detectable structure and the user explicitly requests full-text results only.
- Only read sections selected in Stage 2; expand scope only if explicitly asked.
- Handle all source types equally: PDFs, markdown, plaintext, HTML exports, code documentation.

---

## Error Handling

| Condition | Action |
|-----------|--------|
| Source corrupted / unreadable | Log, skip, report to user, continue with remaining sources |
| Structure extraction fails | Flag "no structure detected", proceed with Path B |
| Embeddings unavailable | Fall back to keyword search silently |
| Query is vague | Ask one clarifying question before Stage 1, or proceed with best-effort extraction and note the assumption |
