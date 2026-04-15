# Repository Guidelines

## Project Structure & Module Organization

The manuscript lives in [`book/`](/Users/kian/Developer/rlvrbook/book). Use [`book/index.md`](/Users/kian/Developer/rlvrbook/book/index.md) for the landing page, [`book/chapters/`](/Users/kian/Developer/rlvrbook/book/chapters) for numbered chapter files (`01-...md` through `11-...md`), and [`book/appendices/`](/Users/kian/Developer/rlvrbook/book/appendices) for appendices (`a-...md` through `d-...md`). Put shared references in [`book/bibliography.bib`](/Users/kian/Developer/rlvrbook/book/bibliography.bib). Store visual assets in the flat [`book/diagrams/`](/Users/kian/Developer/rlvrbook/book/diagrams) directory with chapter-prefixed names such as `01-verifier-stack.png`. Generated output belongs in [`build/html/`](/Users/kian/Developer/rlvrbook/build/html) and [`build/pdf/`](/Users/kian/Developer/rlvrbook/build/pdf). Keep experiments or supporting artifacts in [`code/`](/Users/kian/Developer/rlvrbook/code) and [`data/`](/Users/kian/Developer/rlvrbook/data), not inside the manuscript tree.

## Build, Test, and Development Commands

- `scripts/build-book` runs the repo’s build wrapper.
- `scripts/check-citations` ensures all citekeys used in Markdown exist in `bibliography.bib`.
- `scripts/check-diagrams` enforces diagram naming conventions.

## Editorial Guardrails

This book is not:

- a RL or RLHF textbook
- a survey organized around optimizer variants
- a pure paper timeline

## Writing Style & Naming Conventions

Do not replace any human-written prose with LLM text unless explicitly instructed to. Write in plain Markdown with short paragraphs and explicit headings. Each chapter may use a different structure. Every main chapter should preserve the current house style: Escher image at the top, then a short two-bullet chapter map, then flexible chapter-specific structure. Core reusable terminology belongs in the appendix rather than being forced into every chapter. Avoid positional references such as "above", "below", "the figure below", or "the table above"; use explicit cross-references like `@fig-...` / `@tbl-...` or stable wording such as "the previous expression". Prefer ASCII unless a source requires otherwise. Use sentence case in prose headings and kebab-case for filenames.

## Citations, Figures, and Code

Cite sources with Pandoc/Quarto citekeys such as `[@deepseekai2025r1]`; references are generated from `book/bibliography.bib`. HTML chapter pages use Quarto’s native appendix handling for citations and footnotes.

Prefer interactive HTML figures only when they materially improve comprehension and always provide a static fallback for PDF.

## Commit & Pull Request Guidelines

Use concise imperative messages and keep unrelated edits out of the same commit. PRs should include: a one-paragraph summary, affected chapters or files, any new sources added to `bibliography.bib`, and screenshots or PDFs if the change affects layout, diagrams, or styling.

## Learned User Preferences

- Aspires to Simon Boehm reference-work quality: intuitive, concrete examples before abstraction, running examples carried across chapters.
- Do not replace human-written prose with LLM-generated text unless explicitly asked.
- Prefers interactive HTML figures (inline SVG + JS) for the web build with a static image fallback for PDF.
- PDF exports must show only the light-mode variant of dual-mode images; do not touch web dark/light switching when fixing PDF.
- Use `uv` as the preferred Python package/environment manager.
- Be hyper-rational.
- Steel man all of the user's arguments.

## Learned Workspace Facts

- Quarto does not natively support dark/light mode image switching; the repo uses custom CSS/JS for this.
- Interactive figures use `::: {.content-visible when-format="html"}` blocks with inline SVG+JS; static fallbacks use `::: {.content-visible when-format="pdf"}` blocks.
