---
applyTo: "archive/**"
---

# Archive Map — Complete Reference

This document defines the **structure, ID system, and rules** for the archive.

---

## 1. Root Directory Structure

```
/archive
  ├── design/              ← ID 1xxxx: Archive policies and governance
  ├── projects/            ← ID 2xxxx: Software project ideas
  ├── academic/            ← ID 3xxxx: Research, courses, learning
  ├── technical/           ← ID 4xxxx: Technical deep-dives
  ├── personal-interests/  ← ID 5xxxx: Personal topics (hobbies, interests)
  └── assets/              ← Binary files (images, PDFs, etc.)
```

---

## 2. ID System (5-digit format: XNNNN)

Every document must have a unique ID conforming to the format **XNNNN** where:
- **X** = category prefix (1–5, 6–9 reserved)
- **NNNN** = zero-padded sequential number within that category (0001–9999)

### Category Breakdown

| ID Prefix | Category | Directory | Example IDs |
|-----------|----------|-----------|-------------|
| **1** | Policy | `/archive/design` | 10001, 10002, 10003 |
| **2** | Projects | `/archive/projects` | 20001, 20002, 20003 |
| **3** | Academic | `/archive/academic` | 30001, 30002, 30003 |
| **4** | Technical | `/archive/technical` | 40001, 40002, 40003 |
| **5** | Personal Interests | `/archive/personal-interests` | 50001, 50002, 50003 |
| **6–9** | Reserved | N/A | future expansion |

---

## 3. Filename Convention

All documents follow this pattern:
```
<slug>.md
```

Where `<slug>` is a URL-safe, lowercase identifier derived from the document title.

**Do NOT include:**
- Date prefixes (use `**Date:**` metadata field instead)
- ID in filename (metadata `**ID:**` field only)

---

## 4. Metadata Fields (Fixed Order)

Every document must begin with metadata in this exact order:

```markdown
**ID:** XNNNN  
**Title:** Document Title  
**Author:** Author Name  
**Date:** YYYY-MM-DD  
**Tags:** tag1, tag2, tag3  

---
```

**Validation Rules:**
- **ID** must be 5 digits (XNNNN)
- **ID prefix** must match the document's directory category
- **Date** must be ISO 8601 format (YYYY-MM-DD)
- **Tags** must be comma-separated, lowercase

---

## 5. Directory Placement Rule

**Critical Rule:** ID prefix must match directory.

- **If ID is 1xxxx** → File MUST be in `/archive/design/`
- **If ID is 2xxxx** → File MUST be in `/archive/projects/`
- **If ID is 3xxxx** → File MUST be in `/archive/academic/`
- **If ID is 4xxxx** → File MUST be in `/archive/technical/`
- **If ID is 5xxxx** → File MUST be in `/archive/personal-interests/`

---

## 6. Asset Rules

Binary files only. Storage location: `/archive/assets/`

### Naming
```
<document-id>_<asset-name>.<ext>
```

### Reference (relative paths required)
```markdown
![Description](../assets/20001_diagram.png)
```

---

## 7. Rules

- Never add new top-level directories outside the 5 category folders.
- All binary assets go in `/archive/assets` only.
- Asset references must use relative paths.
- ID conflicts are not allowed; use archive-metadata skill to detect and resolve.
- All documents must remain valid Markdown.
- Metadata header is mandatory on all documents.

---

## 8. Document Validation Checklist

Before archiving, verify:
- [ ] Filename matches `<slug>.md` pattern
- [ ] ID is 5-digit format (XNNNN)
- [ ] ID prefix matches document's category directory
- [ ] Metadata fields are in fixed order
- [ ] Document is in correct category directory
- [ ] Metadata has no duplicate entries
- [ ] Tags are lowercase and comma-separated
- [ ] Date is YYYY-MM-DD format
- [ ] Document is valid Markdown
- [ ] All asset references use relative paths
