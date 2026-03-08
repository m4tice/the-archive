---
name: archive-search
description: "Search the archive by keyword, tag, or date range. Use when looking up documents or finding content in the archive."
---

# Archive Search

## Purpose
Search the archive by keyword, tag, or date range.

## Procedure
1. Receive query (keyword, tag, or date range).
2. Scan `/archive` for matching documents (search filename, metadata, and body).
3. Return a list of matching filenames with titles and dates.

## Constraints
- Search is read-only.
- Results must include: filename, title, and date.
