# RLVR Book

## Conventions

- One Markdown file per chapter and per appendix.
- Keep all manuscript source inside `book/`.
- Keep all diagrams in `book/diagrams/` with chapter-prefixed filenames like `01-verifier-lens-overview.svg`.
- Keep executable examples in `code/` and datasets in `data/`, not mixed into the manuscript tree.
- Treat `build/` as generated output only.

## Commands

- `scripts/build-book`: render the Quarto book to HTML and PDF.
- `scripts/lint-book`: validate the scaffold shape and required chapter files.
- `scripts/check-diagrams`: enforce diagram filename conventions.
- `scripts/check-citations`: flag citekeys used in Markdown but missing from `book/bibliography.bib`.

## Writing Plan

1. Draft chapter 1 until the verifier-first framing is stable enough to constrain the rest of the book.
2. Write chapters 2-4 next so the verifier taxonomy and design space are fixed early.
3. Fill chapters 5-8 once the book has a settled vocabulary for signal design and failure modes.
4. Write chapters 9-11 after the core conceptual spine is stable.
5. Polish citations, diagrams, and cross-references only after the chapter drafts exist.
