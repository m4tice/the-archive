---
name: archive-search
description: "Search the archive by keyword, tag, date range, or category. Use when looking up documents or filtering by type."
---

# Archive Search

## Purpose
Search the archive by keyword, tag, date range, or category.

## Categories (Directory-based Organization)

| ID Prefix | Category | Directory |
|-----------|----------|-----------|
| 1 | Policy | `/archive/design` |
| 2 | Projects | `/archive/projects` |
| 3 | Academic | `/archive/academic` |
| 4 | Technical | `/archive/technical` |
| 5 | Personal Interests | `/archive/personal-interests` |

## Procedure
1. **Receive search query** with optional filters:
   - `keyword` — search filename, metadata, and body
   - `tag` — filter by document tags
   - `date` or `date-range` — filter by date (YYYY-MM-DD)
   - `category` — filter by ID prefix or directory (policy, projects, academic, technical, personal-interests)
   - `author` — filter by author name
2. **Scan `/archive/<category>` directories** matching the filters.
3. **Return results** as a list with: filename, title, date, ID, and tags.

## Example Queries
- "Search for 'sudoku'" → returns all documents matching "sudoku"
- "Search for tag:game in projects" → searches only `/archive/projects` for documents tagged 'game'
- "Search date:2026-03 in technical" → searches `/archive/technical` for documents dated March 2026
- "Search author:m4tice in personal-interests" → searches `/archive/personal-interests` by author

## Constraints
- Search is read-only.
- Results must include: filename, title, date, ID, and tags.
 - Search scan order: `/archive/design`, `/archive/projects`, `/archive/academic`, `/archive/technical`, `/archive/personal-interests`.
