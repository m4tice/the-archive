**ID:** 20001  
**Title:** ARTIKA  
**Author:** m4tice  
**Date:** 2026-03-20  
**Tags:** software, project, idea, techincal  

---

# ARTIKA

ARTIKA is a small software project to help learners memorize gender (e.g., der, die, das for German) of nouns. It aims to support any language that uses noun articles. The motivation: the owner has difficulty memorizing articles, so ARTIKA provides focused practice, lookup, and spaced-repetition tools to learn noun genders and articles.

## Goals

- Provide quick lookup for nouns and their articles.
- Offer drills and spaced-repetition practice.
- Support multiple languages with article systems.
- Allow community contributions for noun lists.

## Core Features (ideas)

- Dictionary lookup: noun → article, plural, part of speech, example sentence.
- Practice modes: flashcards, multiple-choice, typing.
- Import/export word lists (CSV, JSON).
- API for integrations (mobile apps, web frontends).
- Admin UI for editing entries and adding example sentences.

## Technical Notes

- Backend: small REST API (Python/Flask or Node.js/Express).
- Storage: SQLite or a simple JSON DB for portability.
- Optional: spaced-repetition algorithm (SM-2).
- CLI tool for importing/exporting word lists.

## Next Steps

1. Create an initial schema and seed with German nouns.
2. Build a minimal REST API and simple web UI.
3. Add spaced-repetition and practice features.

This is a project/idea note; expand with specs or prototypes as needed.
