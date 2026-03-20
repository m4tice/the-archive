---
name: archive-capture
description: "Create a new archive document. Use when archiving a note, saving content to the archive, or capturing new information."
---

# Archive Capture

## Purpose
Create a new archive document in the appropriate category directory within `/archive`.

## ID System (5-digit format: XNNNN)

| Prefix | Category | Directory | Range |
|--------|----------|-----------|-------|
| 1 | Policy | `/archive/policy` | 10001–10999 |
| 2 | Projects | `/archive/projects` | 20001–20999 |
| 3 | Academic | `/archive/academic` | 30001–30999 |
| 4 | Technical | `/archive/technical` | 40001–40999 |
| 5 | Personal Interests | `/archive/personal-interests` | 50001–50999 |
| 6–9 | Reserved | N/A | future use |

## Procedure
1. **Determine category** — policy, projects, academic, technical, or personal-interests.
2. **Generate document title** from the content.
3. **Generate URL-safe slug** from the title.
4. **Assign ID** based on category prefix and next available sequential number within that category (e.g., 10001, 20001, 40001, 50001).
5. **Create filename** using pattern `slug.md` (no date prefix; preserve original slug when archiving).
6. **Insert metadata header** in fixed order at the top of the document using bold inline fields:
   ```
   **ID:** <XNNNN>  
   **Title:** <title>  
   **Author:** <author>  
   **Date:** <YYYY-MM-DD>  
   **Tags:** <tag1>, <tag2>  

   ---
   ```
7. **Save to category directory**: `/archive/<category>/slug.md`

## Constraints
- ID must match the 5-digit format (XNNNN) corresponding to the category.
- Document must be saved in the correct category directory.
- Metadata header is mandatory and must appear first in fixed order.
- Preserve original filenames (slug) when archiving; do not prepend date.
- Document must be valid Markdown.
- Directory `/archive/assets` is reserved for binary assets only.
