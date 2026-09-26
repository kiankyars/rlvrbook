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
- Preserve the main-chapter house style: an Escher image, a short chapter map, then flexible chapter-specific structure. Put reusable terminology in an appendix rather than repeating it in every chapter.
- Write plain Markdown with short paragraphs and explicit headings. Use sentence case for prose headings, kebab-case for filenames, and ASCII unless a source requires otherwise.
- Avoid positional references such as "above" or "the figure below". Use explicit cross-references such as `@fig-...` and `@tbl-...`, or stable wording.
- A work named by its title is italicized; otherwise name works by system or benchmark name, by "Surname et al.", or by organization.
- No em dashes anywhere, including rendered output such as appendix titles and table cells.
- A bold run-in title whose body runs to several sentences becomes a `###` heading; a short run-in title, and the "Research question." label, stays bold.
- Author asides such as reading recommendations and opinions go in footnotes, not parentheses.
- Do not add a sentence whose only job is to introduce a figure; the cross-reference and caption carry it.
- Define a benchmark, method, or acronym at first use, and state a result with its numbers.
- Fix only typos in the author's sentences; propose anything larger in `md.md` instead of applying it.
- State a claim as its source states it, verified against the primary source, and quote sources word for word; the author's own inferences read as his view, not as the source's.
- Say each result, quote, or explanation once, in the chapter where it belongs, and cross-reference it with `@sec-...` elsewhere; delete one-off facts that connect to nothing and "no study has" closers.
- Do not add summaries, bridges, or "what comes next" sections to chapters that lack them.
- When the author's note asks a question, answer it with evidence, including when the answer is no.

## Citations and Figures

- Cite sources with Pandoc/Quarto citekeys such as `[@deepseekai2025r1]`; references come from `book/bibliography.bib`.
- Put parenthetical citations before sentence punctuation, with a space before the citation: `claim [@key].`, not `claim.[@key]`.
- Use interactive HTML figures only when they materially improve comprehension. Follow the existing `content-visible` HTML/PDF pattern and provide a static PDF fallback.
- For dual-mode images, preserve web light/dark switching and use only the light-mode variant in PDF output.
- Reproduce a third-party figure only under a license that allows it or with written permission; otherwise plot it from the published data or functional form with a script in `code/figures/` that regenerates the light and dark SVGs.
- Fix PDF layout with general rules in `book/filters/pdf-figures.lua` and `book/includes/pdf-figures.tex`, never by formatting one figure, table, or heading.
- Chapter openers are Escher works published by 1930, cropped to the printed image, in neutral gray, at most 1,600 px on the long side, stored as `book/escher/NN-title.jpg`.

## Contributions

Use concise imperative commit messages and keep unrelated edits separate. PRs should summarize the change, identify affected chapters or files and new bibliography entries, and include screenshots or PDFs for layout, diagram, or styling changes.

## Review workflow

- `ROADMAP.md` is the ledger of pending book-wide changes; address only the items the author has commented on, plus fixes that need no follow-up, in separate commits.
- An agent's review responses go in `md.md`, one entry per point keyed by chapter and line, so the author can delete each entry as it is handled; keep the chat reply to the essentials.
- The author's inline notes stay in the manuscript until addressed; each is removed when handled, and the rationale goes in the commit body, not the manuscript.
