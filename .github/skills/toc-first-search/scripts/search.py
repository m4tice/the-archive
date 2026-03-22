"""
search.py  —  Stage 1 + Stage 2: BM25 search + TOC presentation.

Usage:
    python search.py <query> [--index index.json] [--top 5]

Outputs:
  1. Ranked document list with relevance % (Stage 1)
  2. TOC structure for each match with likely-relevant sections highlighted (Stage 2)
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path

from rank_bm25 import BM25Okapi


# ---------------------------------------------------------------------------
# Tokeniser  (simple, punctuation-aware)
# ---------------------------------------------------------------------------

def tokenize(text: str) -> list[str]:
    text = text.lower()
    # Keep alphanumeric, digits, underscores; split on everything else
    tokens = re.findall(r"[a-z0-9_]+", text)
    return tokens


# ---------------------------------------------------------------------------
# Index loading
# ---------------------------------------------------------------------------

def load_index(index_path: Path) -> list[dict]:
    if not index_path.exists():
        raise FileNotFoundError(
            f"Index not found: {index_path}\n"
            "Run preprocess first to build the index."
        )
    with open(index_path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# BM25 ranking (Stage 1)
# ---------------------------------------------------------------------------

def rank_documents(query: str, docs: list[dict], top_k: int = 5) -> list[tuple[dict, float]]:
    """
    Score each document using BM25 on a corpus of:
      filename + title + head_text (first 2 pages)
    Returns a sorted list of (doc, score) pairs, top_k long.
    """
    corpus_texts = []
    for doc in docs:
        combined = " ".join([
            doc.get("filename", ""),
            doc.get("title", ""),
            doc.get("meta", {}).get("title", ""),
            doc.get("meta", {}).get("keywords", ""),
            doc.get("meta", {}).get("subject", ""),
            doc.get("head_text", ""),
        ])
        corpus_texts.append(combined)

    tokenized_corpus = [tokenize(t) for t in corpus_texts]
    tokenized_query  = tokenize(query)

    bm25  = BM25Okapi(tokenized_corpus)
    scores = bm25.get_scores(tokenized_query)

    # Build (doc, score) pairs; filter zero-score docs
    ranked = [(docs[i], float(scores[i])) for i in range(len(docs)) if scores[i] > 0]
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked[:top_k]


def normalise_scores(ranked: list[tuple[dict, float]]) -> list[tuple[dict, int]]:
    """Convert raw BM25 scores to 0–100 relevance percentages."""
    if not ranked:
        return []
    max_score = ranked[0][1]
    if max_score == 0:
        return [(doc, 0) for doc, _ in ranked]
    return [(doc, round(score / max_score * 100)) for doc, score in ranked]


# ---------------------------------------------------------------------------
# TOC highlighting (Stage 2)
# ---------------------------------------------------------------------------

def highlight_toc(toc: list[dict], query_tokens: set[str]) -> list[dict]:
    """
    Mark each TOC entry as likely_relevant if any query token appears in the
    entry's title (case-insensitive).
    """
    highlighted = []
    for entry in toc:
        title_tokens = set(tokenize(entry.get("title", "")))
        entry = dict(entry)  # shallow copy — don't mutate original
        entry["likely_relevant"] = bool(title_tokens & query_tokens)
        highlighted.append(entry)
    return highlighted


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_results(query: str, results: list[tuple[dict, int]]) -> str:
    if not results:
        return "No matching documents found."

    query_tokens = set(tokenize(query))
    lines = [f"Query: {query!r}\n"]

    # --- Stage 1: Ranked list ---
    lines.append("=== Stage 1 — Ranked Sources ===\n")
    for rank, (doc, pct) in enumerate(results, 1):
        lines.append(f"  {rank}. {doc['title']} ({pct}%)  —  {doc['path']}")

    # --- Stage 2: TOC per doc ---
    lines.append("\n=== Stage 2 — Document Structure ===\n")
    for doc, pct in results:
        toc = doc.get("toc", [])
        meta = doc.get("meta", {})
        lines.append(f"{'─'*60}")
        lines.append(f"{doc['title']} ({pct}%)  [{meta.get('pages', '?')} pages]")
        lines.append(f"Path: {doc['path']}")

        if toc:
            highlighted = highlight_toc(toc, query_tokens)
            lines.append("")
            for entry in highlighted:
                num   = entry.get("num", "")
                title = entry.get("title", "")
                sp    = entry.get("start_page", "?")
                ep    = entry.get("end_page", "?")
                marker = "  ← likely relevant" if entry.get("likely_relevant") else ""
                lines.append(f"  {num}{title}  (pp. {sp}–{ep}){marker}")
        else:
            lines.append("  [no TOC detected — use read_section.py with full-text search]")
        lines.append("")

    lines.append(
        "→ Next: run read_section.py <pdf_path> <start_page> <end_page>  "
        "to extract a section."
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# JSON output  (for agent consumption)
# ---------------------------------------------------------------------------

def build_json_output(query: str, results: list[tuple[dict, int]]) -> dict:
    query_tokens = set(tokenize(query))
    output = {"query": query, "results": []}
    for doc, pct in results:
        toc = highlight_toc(doc.get("toc", []), query_tokens)
        output["results"].append({
            "title":      doc["title"],
            "path":       doc["path"],
            "relevance":  pct,
            "pages":      doc.get("meta", {}).get("pages"),
            "has_toc":    bool(doc.get("toc")),
            "toc":        toc,
        })
    return output


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="BM25 search over PDF index.")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--index", default=None,
                        help="Path to index.json (default: auto-detect from cwd)")
    parser.add_argument("--top", type=int, default=5, help="Number of results (default: 5)")
    parser.add_argument("--json", action="store_true", help="Output as JSON (for agent use)")
    args = parser.parse_args()

    # Auto-detect index
    if args.index:
        index_path = Path(args.index)
    else:
        candidates = list(Path(".").rglob("index.json"))
        if not candidates:
            sys.exit("No index.json found. Run preprocess.py first.")
        index_path = candidates[0]

    docs   = load_index(index_path)
    ranked = rank_documents(args.query, docs, top_k=args.top)
    normed = normalise_scores(ranked)

    if args.json:
        print(json.dumps(build_json_output(args.query, normed), indent=2, ensure_ascii=False))
    else:
        print(format_results(args.query, normed))


if __name__ == "__main__":
    main()
