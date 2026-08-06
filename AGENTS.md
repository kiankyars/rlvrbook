# Repository Guidelines

## Project Layout

- The Quarto manuscript is under `book/`: `index.md` is the landing page, numbered chapters live in `chapters/`, and lettered appendices live in `appendices/`.
- Keep shared references in `book/bibliography.bib` and chapter-prefixed visual assets in the flat `book/diagrams/` directory.
- Generated output belongs in `build/`; experiments and supporting artifacts belong in `code/` or `data`, not the manuscript tree.

## Build and Checks

- `quarto render book` renders the book.
- `scripts/check-citations` verifies that Markdown citekeys exist in the bibliography.
- `scripts/check-diagrams` verifies diagram naming.

## Editorial Guidance

This is a reference work about RLVR, not a general RL/RLHF textbook, an optimizer survey, or a paper timeline.

- Do not replace human-written prose with LLM-generated text unless explicitly instructed.
- Lead with intuitive, concrete examples before abstraction and carry useful examples across chapters.
- Preserve the main-chapter house style: an Escher image, a short two-bullet chapter map, then flexible chapter-specific structure. Put reusable terminology in an appendix rather than repeating it in every chapter.
- Write plain Markdown with short paragraphs and explicit headings. Use sentence case for prose headings, kebab-case for filenames, and ASCII unless a source requires otherwise.
- Avoid positional references such as "above" or "the figure below". Use explicit cross-references such as `@fig-...` and `@tbl-...`, or stable wording.

## Citations and Figures

- Cite sources with Pandoc/Quarto citekeys such as `[@deepseekai2025r1]`; references come from `book/bibliography.bib`.
- Use interactive HTML figures only when they materially improve comprehension. Follow the existing `content-visible` HTML/PDF pattern and provide a static PDF fallback.
- For dual-mode images, preserve web light/dark switching and use only the light-mode variant in PDF output.

## Contributions

Use concise imperative commit messages and keep unrelated edits separate. PRs should summarize the change, identify affected chapters or files and new bibliography entries, and include screenshots or PDFs for layout, diagram, or styling changes.
