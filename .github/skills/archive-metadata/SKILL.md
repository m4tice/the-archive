---
name: archive-metadata
description: "Read and validate metadata on an archive document. Use when checking, fixing, or reporting on metadata fields."
---

# Archive Metadata

## Purpose
Read and validate metadata on an existing archive document.

## Procedure
1. Open the target document in `/archive`.
2. Parse the top-of-file metadata lines in fixed order as bold inline fields: `**ID:**`, `**Title:**`, `**Author:**`, `**Date:**`, `**Tags:**`.
3. Report any missing or malformed fields.
4. Offer corrections if needed — only modify these metadata lines, never the document body.

## Constraints
- Never modify the document body when fixing metadata.
- Metadata lines must appear in fixed order at the top of the file, using bold inline labels (not YAML frontmatter).
