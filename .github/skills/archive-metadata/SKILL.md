---
name: archive-metadata
description: "Read and validate metadata on an archive document. Use when checking, fixing, or reporting on metadata fields."
---

# Archive Metadata

## Purpose
Read, validate, and correct metadata on an existing archive document. Ensure ID format matches the document's category directory.

## ID System (5-digit format: XNNNN)

| Prefix | Category | Directory |
|--------|----------|-----------|
| 1 | Policy | `/archive/design` |
| 2 | Projects | `/archive/projects` |
| 3 | Academic | `/archive/academic` |
| 4 | Technical | `/archive/technical` |
| 5 | Personal Interests | `/archive/personal-interests` |

## Procedure
1. **Open the target document** in `/archive/<category>/slug.md`.
2. **Parse metadata fields** in fixed order as bold inline fields: `**ID:**`, `**Title:**`, `**Author:**`, `**Date:**`, `**Tags:**`.
3. **Validate ID format**:
   - Must be 5 digits (XNNNN, e.g., 10001, 20001, 40001).
   - ID prefix (first digit) must match the document's category:
     - 1xxxx → must be in `/archive/design`
     - 2xxxx → must be in `/archive/projects`
     - 3xxxx → must be in `/archive/academic`
     - 4xxxx → must be in `/archive/technical`
     - 5xxxx → must be in `/archive/personal-interests`
4. **Report any missing or malformed fields**:
   - Missing metadata fields
   - ID format violations (not 5 digits or prefix mismatch)
   - Invalid date format (should be YYYY-MM-DD)
5. **Offer corrections** if needed — only modify these metadata lines, never the document body.

## Constraints
- Never modify the document body when fixing metadata.
- Metadata lines must appear in fixed order at the top of the file, using bold inline labels (not YAML frontmatter).
- ID corrections should reassign based on category if the prefix doesn't match the current directory.
