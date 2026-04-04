# RLVR Book

This repo should have one source-of-truth manuscript tree, with one Markdown file per chapter and a build pipeline that emits both HTML and PDF. The right shape is closer to a publishing repo than a research dump: keep prose, figures, citations, code, and generated artifacts cleanly separated.

## Proposed Repo Layout

```text
rlvrbook/
├── README.md
├── summary.md
├── .gitignore
├── book/
│   ├── _quarto.yml
│   ├── metadata.yml
│   ├── bibliography.bib
│   ├── glossary.yml
│   ├── styles/
│   │   ├── pdf.scss
│   │   └── html.scss
│   ├── frontmatter/
│   │   ├── title-page.md
│   │   ├── preface.md
│   │   └── notation.md
│   ├── chapters/
│   │   ├── 01-the-verifier-lens.md
│   │   ├── 02-what-can-be-verified.md
│   │   ├── 03-outcome-verifiers.md
│   │   ├── 04-process-verifiers.md
│   │   ├── 05-hybrid-verifiers.md
│   │   ├── 06-turning-checks-into-signal.md
│   │   ├── 07-search-and-test-time-verification.md
│   │   ├── 08-reward-hacking-and-robustness.md
│   │   ├── 09-faithfulness-and-confidence.md
│   │   ├── 10-math-code-and-formal-proof.md
│   │   ├── 11-long-context-multimodal-and-agentic-rlvr.md
│   │   └── 12-open-problems.md
│   ├── appendices/
│   │   ├── a-minimal-rl-background.md
│   │   ├── b-benchmarks-evals-and-contamination.md
│   │   └── c-verifier-design-checklist.md
│   ├── diagrams/
│   │   ├── 01-verifier-lens-overview.svg
│   │   ├── 03-outcome-verifier-pipeline.svg
│   │   ├── 04-process-verifier-taxonomy.svg
│   │   ├── 08-reward-hacking-failure-modes.svg
│   │   └── ...
│   └── templates/
│       ├── chapter-template.md
│       └── figure-template.svg
├── code/
│   ├── math/
│   ├── code/
│   ├── proof/
│   ├── agentic/
│   └── shared/
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
├── scripts/
│   ├── build-book
│   ├── lint-book
│   ├── render-figures
│   └── check-citations
├── build/
│   ├── html/
│   └── pdf/
```

## Why This Layout

- Keep all publishable manuscript source inside `book/`; that avoids the split-brain structure many research repos end up with.
- Keep each chapter as a single `.md` file in `book/chapters/`; this is the easiest unit for review, citation passes, and PDF compilation.
- Keep all diagrams in a single flat `book/diagrams/` folder and prefix each filename with its chapter number; that keeps lookup simple without creating unnecessary nesting.
- Keep executable code and datasets outside `book/`; textbook builds should not depend on the prose tree staying import-safe.
- Treat `build/` as generated output only; PDF and HTML should be reproducible artifacts, not hand-edited source.

## Writing Plan

1. Freeze the table of contents and the chapter contract for each file.
2. Draft the backbone chapters first: verifier lens, outcome/process verifiers, reward hacking, canonical domains.
3. Build figures, glossary entries, and citations in parallel with chapter drafting.
4. Run a technical review pass chapter-by-chapter before expanding frontier material.
5. Freeze prose, then render and polish the HTML/PDF edition.
