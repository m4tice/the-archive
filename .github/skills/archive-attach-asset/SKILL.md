---
name: archive-attach-asset
description: "Attach a binary asset to an archive document. Use when adding images, PDFs, or other files to an archive entry."
---

# Archive Attach Asset

## Purpose
Attach a binary asset to an archive document.

## Procedure
1. Receive the asset file and the target document slug.
2. Check `/archive/assets` for a duplicate filename — if found, reuse it.
3. Copy the asset to `/archive/assets/<filename>`.
4. Add a relative asset reference link in the target document:
   `![description](../assets/<filename>)` or `[filename](../assets/<filename>)`

## Constraints
- Assets must be placed in `/archive/assets` only.
- Never embed binary data directly in documents.
- Asset reference must use a relative path.
- Deduplicate by filename — reuse existing files and update references.
