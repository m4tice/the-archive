---
name: archive-capture
description: "Create a new archive document. Use when archiving a note, saving content to the archive, or capturing new information."
---

# Archive Capture

## Purpose
Create a new archive document in `/archive`.

## Procedure
1. Generate a document title from the content.
2. Generate a URL-safe slug from the title.
3. Create filename using pattern `slug.md` (preserve original slug when archiving existing documents; do NOT prepend the date).
4. Insert metadata header at the top of the document in fixed order using bold inline fields (match source format):
   ```
   **ID:** <uuid or sequential>  
   **Title:** <title>  
   **Author:** <author>  
   **Date:** <YYYY-MM-DD>  
   **Tags:** <tag1>, <tag2>  

   ---
   ```
5. Save to `/archive/slug.md`.

## Constraints
- Prefer preserving the original filename (`slug.md`) when archiving or appending to an existing document.
- When creating a new document without an original filename, use `slug.md` (no date prefix).
- Metadata header is mandatory and must appear first.
- Document must be valid Markdown.
- Metadata header is mandatory and must appear first.
- Document must be valid Markdown.
