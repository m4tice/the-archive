**ID:** 20002  
**Title:** Sudoku — Ad-free Mobile Game  
**Author:** m4tice  
**Date:** 2026-03-20  
**Tags:** game, project, idea, ios  

---

# Sudoku — Ad-free Mobile Game

Ad-free mobile Sudoku built primarily for iOS for the owner's parent. The focus is accessibility, simplicity, and offline play: large fonts, high-contrast UI, VoiceOver support, and a clean, uncluttered experience with no ads.

## Goals

- Create a simple, family-friendly, ad-free Sudoku app.
- Prioritize accessibility and ease of use for older players.
- Provide multiple difficulty levels and a reliable puzzle generator.
- Keep the app small, offline-capable, and private.

## Core Features (ideas)

- Puzzle generator and validator (seedable RNG or curated puzzles).
- Difficulty levels: easy, medium, hard, expert.
- Hints, undo, pencil marks, auto-check, and notes.
- Daily puzzles and local statistics (no remote tracking).
- Accessibility settings: large text, high-contrast palette, color-blind mode, VoiceOver support.

## Technical Notes

- Platform: primarily iOS (Swift + SwiftUI recommended).
- Storage: Core Data or SQLite for local puzzles and stats.
- Puzzle generation: implement a generator or ship a curated set.
- Testing: XCTest; distribute via TestFlight to the parent for feedback.
- Monetization: paid app or optional donation model (no ads).

## Next Steps

1. Draft wireframes and accessibility requirements.
2. Implement a puzzle generator and a minimal SwiftUI prototype.
3. Test with the parent and iterate on usability.

This is a project/idea note; expand into design docs or prototypes as needed.
