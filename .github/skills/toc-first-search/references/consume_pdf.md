**ID:** 40002  
**Title:** PDF Reading Strategy & Technical Specification  
**Author:** m4tice  
**Date:** 2026-03-20  
**Tags:** PDF, search, strategy, information-retrieval, technical-documentation  

---

# PDF Reading Strategy & Technical Specification

## 1. Executive Summary

This document outlines a comprehensive strategy for searching and extracting information from large PDF document collections (10–1000s of files). It combines multiple retrieval techniques — from fast full-text indexing to semantic embeddings — with a **three-stage TOC-first approach** optimized for technical documentation (e.g., AUTOSAR specs, design docs, standards).

**Key Innovation:** Relevance scoring + table-of-contents (TOC) extraction before full-text reading, reducing search time by 2–10x compared to brute-force approaches while improving precision and document context preservation.

---

## 2. Problem Statement

### Challenges with Large PDF Collections

- **Scale:** Thousands of PDFs containing critical technical information
- **Variability:** Inconsistent structure (some with TOC, some without; some scanned/OCR, some native text)
- **Latency:** Brute-force full-text search on all documents is slow (30–60s for 1000 docs)
- **Context Loss:** Scattered passage retrieval loses document structure and chapter hierarchy
- **User Experience:** Non-deterministic results; users unsure which docs are relevant

### Current Approaches & Limitations

| Approach | Latency (1000 docs) | Precision | Cons |
|----------|-------------------|-----------|------|
| Full-text search (grep/ripgrep) | 30–60s | Medium | Slow, scattered passages, no structure |
| Semantic embeddings only | 5–15s (at scale) | High | Requires pre-computed embeddings, cold-start expensive |
| BM25 (TF-IDF) only | 10–20s | Medium | Fast but misses semantic relevance |
| Hybrid (BM25 + re-rank) | 15–30s | High | Better, but still scans all docs |

---

## 3. Proposed Solution: Three-Stage Relevance + TOC-First

### 3.1 Overview

A three-stage retrieval pipeline optimized for medium-scale technical document collections:

```
Query
  ↓
Stage 1: Fast Relevance Scoring (BM25 + metadata)
  ↓
Filter to Top-N Documents (e.g., top 3–5 of 20; top 10–20 of 1000)
  ↓
Stage 2: TOC Extraction & Selection
  ├─ Extract table of contents from each top-ranked doc
  ├─ Present user/agent with chapter names, page ranges, relevance scores
  ├─ User selects relevant chapters
  └─ If no TOC available → skip to Stage 3
  ↓
Stage 3: Contextual Extraction
  ├─ If chapters selected: extract those page ranges only
  └─ If no TOC: perform full-text search on full PDF, extract matching passages
  ↓
Results (with provenance: doc_id, chapter, page_range, offsets)
```

### 3.2 Stage 1: Fast Relevance Scoring

**Goal:** Identify top-N most relevant documents without full extraction.

**Inputs:**
- Query (keywords or question)
- Collection metadata (cached from preprocessing)

**Process:**
1. **BM25 Ranking** on first 1–2 pages + metadata (title, author, tags, date, category)
   - Fast: O(n) scan of inverted index
   - ~ 2–3s for 1000 docs
2. **Optional Semantic Boost** (if embeddings cached)
   - Embed query + compute cosine similarity to cached embeddings
   - Re-rank top-N by combined score
3. **Metadata Filters** (optional)
   - Boost by date (recent docs higher rank)
   - Boost by author/source trust (e.g., official specs)
   - Filter by tags or category

**Output:**
- Ranked list of documents with relevance scores (%)
  ```json
  [
    {"doc_id": "40001", "title": "ComScl_ModelMngr", "relevance": 92, "path": "archive/technical/..."},
    {"doc_id": "40003", "title": "Signal Configuration", "relevance": 78, "path": "archive/technical/..."},
    {"doc_id": "40004", "title": "Communication Protocol", "relevance": 64, "path": "archive/technical/..."}
  ]
  ```

**Time Cost:** ~2–5s for 1000 docs (depending on indexing backend)

### 3.3 Stage 2: TOC Extraction & Selection

**Goal:** Leverage document structure to guide reading; let user/agent visually scan chapters.

**Inputs:**
- Top-N ranked documents from Stage 1
- Raw PDF files

**Process:**
1. **TOC Detection & Extraction** (for each top-ranked doc)
   - Look for common TOC markers: "Table of Contents", "Contents", indentation levels, page numbers on right
   - Parse TOC structure: chapter name, section, page range
   - Store as structured JSON:
     ```json
     {
       "doc_id": "40001",
       "chapters": [
         {"name": "1. Overview", "start_page": 1, "end_page": 5},
         {"name": "2. Architecture", "start_page": 6, "end_page": 15},
         {"name": "3. Configuration", "start_page": 16, "end_page": 35}
       ]
     }
     ```
2. **Present to User/Agent**
   - Format: List with chapter names, page ranges, doc summary
   - Example: "**ComScl_ModelMngr** (relevance: 92%): 1. Overview (1–5), 2. Architecture (6–15), **3. Configuration (16–35) ← likely relevant**, 4. API Reference (36–50)"
3. **User/Agent Selects Chapters**
   - Choose chapter(s) to read next
   - Example selection: "Read Chapter 3: Configuration (pages 16–35)"

**Fallback (if TOC missing):**
- Flag document as "no TOC detected"
- User can opt to skip or perform full-text search on this doc
- Move to Stage 3 (brute-force) if user chooses to proceed

**Time Cost:** ~1–5s for top-N (1–20 docs), depending on PDF size

### 3.4 Stage 3: Contextual Extraction

**Goal:** Extract only the selected content; preserve document context.

**Inputs:**
- Selected chapters (page ranges from TOC) OR
- Full-text search query (if no TOC available)

**Process A: Chapter-based Extraction** (preferred)
1. Extract PDF text for selected page ranges
2. Parse into paragraphs, code blocks, tables
3. Return with metadata:
   ```json
   {
     "doc_id": "40001",
     "chapter": "3. Configuration",
     "pages": [16, 35],
     "content": "...",
     "extraction_metadata": {
       "method": "chapter_extract",
       "confidence": "high",
       "contains_code": true,
       "contains_tables": true
     }
   }
   ```

**Process B: Full-Text Search** (fallback if no TOC)
1. Perform BM25 full-text search on entire PDF
2. Extract matching passages with surrounding context (±2 sentences)
3. Return with offsets and confidence scores:
   ```json
   {
     "doc_id": "40001",
     "matches": [
       {"text": "Signal configuration is...", "page": 20, "char_offset": 4521, "confidence": 0.87},
       {"text": "Configuration parameters...", "page": 23, "char_offset": 1234, "confidence": 0.74}
     ],
     "extraction_metadata": {
       "method": "full_text_search",
       "confidence": "medium",
       "total_matches": 15,
       "returning_top_5": 5
     }
   }
   ```

**Time Cost:** 
- Chapter extraction: ~1–3s per chapter
- Full-text search: ~5–10s per 100-page PDF

---

## 4. Preprocessing Pipeline

### 4.1 PDF Extraction & Normalization

**Goal:** Convert raw PDFs into searchable, structured text.

**Steps:**

1. **Text Extraction**
   - **Native PDFs (text layer):** Use `pdfplumber` or `pdfminer.six` for fast extraction
   - **Scanned/OCR PDFs:** Detect using image content analysis; flag for OCR with pytesseract
   - Output: Plain text + page offsets

2. **Metadata Extraction**
   - PDF properties: title, author, creation date, subject, keywords
   - First-page content: often contains summary or document type markers
   - Extract and store in metadata JSON

3. **TOC Detection & Parsing**
   - Scan pages 1–10 for TOC patterns
   - Parse indentation, numbering schemes
   - Extract (chapter_name, start_page, end_page)
   - Store as JSON

4. **Deduplication**
   - Compute file-level hash (MD5 of raw PDF)
   - Compute first-page hash (to detect near-duplicates)
   - Use simhash for content-level fuzzy matching
   - Mark duplicates; index only once with aliases

5. **Chunking** (optional, for semantic embeddings)
   - Split text into fixed-size chunks (300–800 tokens) or page-level chunks
   - Preserve page/section metadata per chunk
   - Store chunk ID → (doc_id, page, offset)

### 4.2 Indexing

**Dual-Index Architecture:**

1. **Full-Text Index (BM25)**
   - Technology: SQLite FTS5 (for < 10k docs), Elasticsearch/Meilisearch (for > 10k)
   - Content: First 2 pages + metadata (title, author, tags)
   - Query: Fast prefix/phrase/boolean search
   - Latency: < 1s for 1000 docs

2. **Vector Index (Semantic)**
   - Technology: FAISS / Qdrant / Chroma
   - Content: Page-level or section-level embeddings
   - Model: `sentence-transformers/all-MiniLM-L6-v2` (fast, local) or OpenAI/Cohere (cloud)
   - Latency: 2–5s refresh; < 1s query

3. **Metadata Store**
   - JSON file or lightweight SQL DB
   - Fields: doc_id, title, author, date, tags, file_path, pages, has_toc, toc_json
   - Used for filtering and display

### 4.3 Incremental Updates

**Trigger:** New PDFs added to `/archive/assets/`, or existing PDFs modified

**Process:**
1. Compute file hash
2. Compare with cached hash; if changed, re-process
3. Extract & index new content
4. Update metadata store
5. Rebuild affected indexes (avoid full reindex)

---

## 5. AUTOSAR Case Study: Relevance + TOC-First Strategy

### 5.1 Context

- **Collection:** ~20 AUTOSAR technical specification PDFs
- **Typical doc size:** 100–300 pages
- **Query type:** Structured (e.g., "signal mapping", "configuration parameters", "communication protocol")
- **Success metric:** Time to find answer; precision of result

### 5.2 Observed Pattern

User's effective workflow for ~20 docs:

1. **Score all docs:** BM25 ranking on title + first page (2–3s for 20 docs)
2. **Filter to top 3–5:** Identify most relevant docs (e.g., "Signal Configuration", "Communication Protocol", "AUTOSAR Overview")
3. **Extract & scan TOC:** Each top doc's table of contents (1–2 minutes for human, 1–2s for automated)
4. **Read selected chapters:** User selects relevant sections (e.g., "Chapter 3: Signal Mapping", "Section 5.2: Parameter Definition")
5. **[Fallback only if needed] Brute-force search:** If TOC unavailable or insufficient, search full PDF text

### 5.3 Performance Comparison

| Metric | Brute-Force (Full-Text All) | TOC-First Strategy |
|--------|----------------------------|-------------------|
| **Time (query → filtered results, 20 docs)** | 5–10s | 3–4s (score + extract top-3 TOCs) |
| **User interaction time** | N/A | 1–2 min (select chapters) |
| **Total time (query → answer)** | 5–10s | 5–7 min (with human chapter selection) |
| **Information density** | Single passages, scattered | Full chapters, structured context |
| **Precision** | 60–70% | 80–90% (with human guidance) |
| **Docs examined** | All 20 | Top 3–5 |

### 5.4 Why This Works for Technical Docs

- **Consistent structure:** Technical specs follow standard TOC layout (chapters, sections, appendices)
- **Well-organized content:** Information follows logical hierarchy (overview → detail → reference)
- **User familiarity:** Engineers are trained to navigate technical docs via TOC
- **Predictable relevance:** Document title + first page strongly signal relevance (or lack thereof)

---

## 6. Implementation Architecture

### 6.1 Minimal Stack (Single Machine, < 10k PDFs)

```
Frontend (Chat Interface)
  ↓
Orchestrator (Python CLI or MCP server)
  ├─ Query parser
  ├─ Ranking (BM25)
  └─ Result formatter
  ↓
Full-Text Index (SQLite FTS5)
Vector Index (FAISS, in-memory or on-disk)
Metadata Store (JSON or SQLite)
  ↓
PDF Storage & Preprocessing Cache
  ├─ Raw PDFs: /archive/assets/
  ├─ Extracted text: /archive/assets/*_extracted.txt
  ├─ TOC JSON: /archive/assets/*_toc.json
  └─ Metadata: /archive/metadata.json
```

### 6.2 Scalable Stack (Multi-machine, > 10k PDFs)

```
Query Interface (Web UI / Chat)
  ↓
API Gateway (FastAPI / Flask)
  ↓
Cache Layer (Redis)
  ↓
Ranking Service (BM25)           Semantic Service (Embeddings)
  ├─ Elasticsearch/Meilisearch ← Qdrant/Milvus/Chroma
  └─ Top-N score retrieval       Vector similarity search
  ↓
Document Retrieval Service (TOC extraction, chapter reading)
  ├─ PDF cache
  ├─ OCR service (async, batch)
  └─ Chunk storage (PostgreSQL or vector DB)
  ↓
Logging & Evaluation (metrics, user feedback)
```

### 6.3 Core Components (Pseudocode)

**1. Fast Relevance Scoring**
```python
def score_documents(query: str, top_k: int = 5) -> List[Dict]:
    # BM25 search on metadata + first page
    bm25_results = fts_index.search(query, limit=50)  # ~1s for 1000 docs
    
    # Optional: semantic re-ranking
    if use_embeddings:
        query_vec = embed(query)
        for doc in bm25_results[:top_k]:
            doc['semantic_score'] = cosine_sim(query_vec, doc['embedding'])
        bm25_results = sorted(bm25_results, 
                            key=lambda x: 0.6*x['bm25'] + 0.4*x['semantic_score'],
                            reverse=True)
    
    return bm25_results[:top_k]
```

**2. TOC Extraction**
```python
def extract_toc(pdf_path: str) -> Optional[Dict]:
    doc = pdfplumber.open(pdf_path)
    pages = doc.pages[:10]  # scan first 10 pages
    
    toc_pattern = detect_toc(pages)  # regex/heuristic
    if not toc_pattern:
        return None
    
    chapters = parse_toc(toc_pattern)
    return {
        'chapters': chapters,  # [{'name': '1. Overview', 'start': 1, 'end': 5}]
        'extraction_method': 'regex' | 'ml' | 'manual',
        'confidence': 0.95
    }
```

**3. Chapter-Based Extraction**
```python
def extract_chapter(pdf_path: str, start_page: int, end_page: int) -> str:
    doc = pdfplumber.open(pdf_path)
    text = ""
    for page_num in range(start_page - 1, end_page):
        page = doc.pages[page_num]
        text += page.extract_text() + "\n---\n"
    return text
```

---

## 7. Recommended Strategy by Collection Size

| Collection Size | Recommended Approach | Tech Stack | Est. Query Latency |
|-----------------|----------------------|------------|-------------------|
| **< 50 PDFs** | TOC-first (Stage 1+2+3) | BM25 (SQLite FTS5) + manual TOC | 3–5s (+ human interaction) |
| **50–1000 PDFs** | TOC-first + BM25 ranking | SQLite FTS5 + FAISS (optional) | 5–10s (+ human interaction) |
| **1000–10k PDFs** | TOC-first + BM25 + semantic re-rank | Meilisearch + Qdrant | 10–20s |
| **> 10k PDFs** | Hybrid (BM25 + semantic) with optional TOC fallback | Elasticsearch + Milvus/Chroma + async OCR | 5–15s |

---

## 8. Performance Metrics & Evaluation

### 8.1 Key Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Query latency (stage 1)** | < 5s | Time from query → top-N docs |
| **TOC extraction** | < 2s per doc | Time to extract & parse TOC |
| **Full-text search** | < 30s | Time to scan + match all docs |
| **Precision@5** | > 80% | 5 results returned; 4+ relevant |
| **Recall@10** | > 85% | Top 10 results; 8+ relevant docs found |
| **User satisfaction** | > 4/5 | Feedback on relevance + usability |

### 8.2 Evaluation Framework

**Ground Truth:** Curated query-document pairs with relevance labels (0–3 scale)

**Test Queries:**
- Structured (e.g., "signal mapping", "parameter configuration")
- Vague (e.g., "tell me about communication")
- Boolean (e.g., "signal mapping AND CAN protocol")
- Cross-domain (e.g., "how does X relate to Y?")

**Baseline Comparison:**
- Full-text search (grep)
- BM25 only
- Semantic embeddings only
- Hybrid (BM25 + semantic)
- TOC-first (proposed)

---

## 9. Security & Privacy

### 9.1 Constraints

- **Local retrieval:** Process PDFs locally; no external network calls without explicit permission
- **Access control:** Index only PDFs in designated archive directories
- **Data retention:** Cache extracted text locally; purge on user request
- **Audit logging:** Log all queries, results returned, user feedback

### 9.2 Error Handling

**Graceful degradation:**
- If embeddings model unavailable → fall back to BM25
- If PDF corrupted → mark as unreadable; retry with OCR
- If TOC extraction fails → log; allow full-text search fallback
- If user cancels chapter selection → revert to BM25 top-5 results

---

## 10. Future Enhancements

### 10.1 Short-term (Next Release)

- [ ] Automated TOC generation using ML (if PDF lacks TOC)
- [ ] User feedback loop (thumbs up/down → improve ranking)
- [ ] Query expansion (synonyms, stemming, abbreviation expansion)
- [ ] Cross-document reference mapping (e.g., "see also: ComScl_ModelMngr, Section 3.2")

### 10.2 Medium-term (Q2–Q3 2026)

- [ ] Batch OCR processing for scanned PDFs (async pipeline)
- [ ] Semantic clustering (group related docs by topic)
- [ ] Citation graph (track which docs reference which)
- [ ] Multi-language support (translate queries, preserve original docs)

### 10.3 Long-term (Q4 2026+)

- [ ] Knowledge graph extraction (entity linking, relationship inference)
- [ ] Conversational interface (maintain context across queries)
- [ ] Real-time indexing (incremental updates, eventual consistency)
- [ ] Federated search (search across multiple document archives)

---

## 11. Testing & Validation Plan

### 11.1 Unit Tests
- TOC parsing with various PDF formats
- BM25 ranking edge cases (empty query, special characters)
- Embedding similarity edge cases (identical documents, outliers)

### 11.2 Integration Tests
- Full pipeline (query → score → TOC → extract → return)
- Fallback behavior (missing TOC, corrupted PDF, exhausted cache)
- Incremental indexing (add/remove/modify PDFs)

### 11.3 Performance Tests
- Latency benchmarks (query time, TOC extraction, full-text search)
- Scalability (1k, 10k, 100k PDFs)
- Memory usage (index size, cache size, peak memory)

### 11.4 User Acceptance Tests
- AUTOSAR spec queries (20–50 real queries, 20 docs)
- Relevance scoring (precision@5, recall@10)
- TOC utility (time saved vs. full-text search)

---

## 12. References & Further Reading

- **BM25 / TF-IDF:** Okapi BM25 — https://en.wikipedia.org/wiki/Okapi_BM25
- **Vector Embeddings:** Sentence Transformers — https://www.sbert.net/
- **PDF Extraction:** pdfplumber (https://github.com/jamesturk/pdfplumber), pdfminer.six (https://github.com/pdfminer/pdfminer.six)
- **Full-Text Indexing:** SQLite FTS5 (https://www.sqlite.org/fts5.html), Elasticsearch (https://www.elastic.co/), Meilisearch (https://www.meilisearch.com/)
- **Vector Indexes:** FAISS (https://github.com/facebookresearch/faiss), Qdrant (https://qdrant.tech/), Chroma (https://www.trychroma.com/)
- **ML/AI:** Hugging Face Transformers (https://huggingface.co/), PyTorch (https://pytorch.org/)

---

## 13. Appendix: Example Queries & Results

### Example 1: AUTOSAR Signal Mapping (TOC-First Success)

**Query:** "How do I configure signal mapping in AUTOSAR?"

**Stage 1 Results (Relevance Scoring):**
```
1. "ComScl_ModelMngr" (92%) — ~/archive/technical/comsclmodelmngr.md
2. "Signal Configuration Guide" (78%) — ~/archive/technical/signal_config.md
3. "Communication Protocol" (64%) — ~/archive/technical/comm_protocol.md
```

**Stage 2 Results (TOC Extraction, top-3 docs):**
```
ComScl_ModelMngr (92%):
  1. Overview (pages 1–5)
  2. AUTOSAR Architecture (pages 6–15)
  3. Signal Mapping (pages 16–35) ← SELECTED
  4. Parameter Configuration (pages 36–50)
  5. API Reference (pages 51–80)

Signal Configuration Guide (78%):
  1. Introduction (pages 1–3)
  2. Basic Signals (pages 4–10)
  3. Advanced Mapping (pages 11–25) ← SELECTED
  4. Troubleshooting (pages 26–30)

Communication Protocol (64%):
  [TOC omitted — lower relevance]
```

**Stage 3 Results (Chapter Extraction):**
- Extracted Chapter 3 from ComScl_ModelMngr (pages 16–35): 2,300 words, includes code examples
- Extracted Chapter 3 from Signal Configuration Guide (pages 11–25): 1,800 words
- Ready for user reading

**Total Time:** ~5s (ranking) + 1s (TOC extraction) + 2s (chapter extraction) = **~8s** (vs. 10–20s full-text search)

---

**End of Document**
