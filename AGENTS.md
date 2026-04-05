# Repository Guidelines

## Project Structure & Module Organization

The manuscript lives in [`book/`](/Users/kian/Developer/rlvrbook/book). Use [`book/index.md`](/Users/kian/Developer/rlvrbook/book/index.md) for the landing page, [`book/chapters/`](/Users/kian/Developer/rlvrbook/book/chapters) for numbered chapter files (`01-...md` through `11-...md`), and [`book/appendices/`](/Users/kian/Developer/rlvrbook/book/appendices) for appendices (`a-...md`, `b-...md`, `c-...md`). Put shared references in [`book/bibliography.bib`](/Users/kian/Developer/rlvrbook/book/bibliography.bib). Store visual assets in the flat [`book/diagrams/`](/Users/kian/Developer/rlvrbook/book/diagrams) directory with chapter-prefixed names such as `01-verifier-stack.png`. Generated output belongs in [`build/html/`](/Users/kian/Developer/rlvrbook/build/html) and [`build/pdf/`](/Users/kian/Developer/rlvrbook/build/pdf). Keep experiments or supporting artifacts in [`code/`](/Users/kian/Developer/rlvrbook/code) and [`data/`](/Users/kian/Developer/rlvrbook/data), not inside the manuscript tree.

## Build, Test, and Development Commands

- `quarto render book` builds the book locally.
- `scripts/build-book` runs the repo’s build wrapper.
- `scripts/lint-book` verifies chapter and appendix ordering against `book/_quarto.yml`.
- `scripts/check-citations` ensures all citekeys used in Markdown exist in `bibliography.bib`.
- `scripts/check-diagrams` enforces diagram naming conventions.

Run the three `scripts/check-*` commands before opening a PR.

## Coding Style & Naming Conventions

Do not replace any human-text with llm-text unless explicitly instructed to. Write in plain Markdown with short paragraphs and explicit headings. Each chapter may use a different structure. Prefer ASCII unless a source requires otherwise. Use sentence case in prose headings and kebab-case for filenames. Cite sources with Pandoc/Quarto citekeys such as `[@deepseekai2025r1]`; references are generated from `book/bibliography.bib`.

## Testing Guidelines

This repo does not use a unit-test framework. Validation is structural and bibliographic: run `scripts/lint-book`, `scripts/check-citations`, and `scripts/check-diagrams`. If you change rendering behavior or styles, also run `quarto render book` and confirm both HTML and PDF output still build. For equation/math edits, run `scripts/build-book` and ensure the PDF step has zero `LaTeX Error` in logs.

## Commit & Pull Request Guidelines

Use concise imperative messages and keep unrelated edits out of the same commit. PRs should include: a one-paragraph summary, affected chapters or files, any new sources added to `bibliography.bib`, and screenshots or PDFs if the change affects layout, diagrams, or styling.

## Learned User Preferences

- Aspires to Simon Bohm reference-work quality: intuitive, concrete examples before abstraction, running examples carried across chapters.
- Do not replace human-written prose with LLM-generated text unless explicitly asked.
- Prefers interactive HTML figures (inline SVG + JS) for the web build with a static image fallback for PDF.
- PDF exports must show only the light-mode variant of dual-mode images; do not touch web dark/light switching when fixing PDF.
- Use `uv` as the preferred Python package/environment manager.

## Learned Workspace Facts

- `book/.gitignore` doubles as the chapter outline/plan file — it contains recommended build notes and section plans, not actual gitignore patterns.
- Quarto does not natively support dark/light mode image switching; the repo uses custom CSS/JS for this.
- Interactive figures use `::: {.content-visible when-format="html"}` blocks with inline SVG+JS; static fallbacks use `::: {.content-visible when-format="pdf"}` blocks.
- tldraw MCP (`@talhaorak/tldraw-mcp`) is configured in `.cursor/mcp.json`; `.tldr` source files live in `book/diagrams/tldraw/`.
- tldraw MCP-generated `.tldr` files may need migration-safe schema fixes; validate with `parseTldrawJsonFile` from the `tldraw` npm package.
- `rg` (ripgrep) may not be available in all shell contexts; `scripts/lint-book` depends on it.
