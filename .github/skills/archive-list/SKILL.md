---
name: archive-list
description: "List documents in the archive with optional filters. Use when browsing the archive or filtering by date, tag, author, or keyword."
---

# Archive List

## Purpose
List documents in the archive with optional filters.

## Procedure
1. Receive optional filters: `date`, `tag`, `author`, `keyword`.
2. Scan `/archive` for `.md` files.
3. Return a concise listing of matching documents: filename, title, date, tags.

## Constraints
- Listing is read-only.
