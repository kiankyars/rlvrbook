# RLVR Book

This repo is the source tree for *Reinforcement Learning from Verifiable Rewards*.
Do a case study at Will Brown code
What does it really mean to post-train a harness?
## Implemented Layout

```text
rlvrbook/
├── README.md
├── summary.md
├── .gitignore
├── book/
│   ├── _quarto.yml
│   ├── index.md
│   ├── bibliography.bib
│   ├── styles/
│   │   └── html.scss
│   ├── chapters/
│   │   ├── 01-introduction.md
│   │   ├── 02-outcome-verifiers.md
│   │   ├── 03-process-verifiers.md
│   │   ├── 04-learned-programmatic-and-hybrid-verifiers.md
│   │   ├── 05-turning-checks-into-training-signal.md
│   │   ├── 06-search-and-test-time-verification.md
│   │   ├── 07-reward-hacking-proxy-misspecification-and-verifier-robustness.md
│   │   ├── 08-faithfulness-confidence-and-what-verification-misses.md
│   │   ├── 09-canonical-domains-math-code-and-formal-proof.md
│   │   ├── 10-long-context-multimodal-and-agentic-rlvr.md
│   │   └── 11-open-problems-and-the-research-agenda.md
│   ├── appendices/
│   │   ├── a-minimal-rl-and-post-training-background.md
│   │   ├── b-benchmarks-evals-and-contamination.md
│   │   └── c-practical-verifier-design-checklist.md
│   ├── diagrams/
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
│   ├── check-diagrams
│   └── check-citations
└── build/
    ├── html/
    └── pdf/
```

## Locked Main Text

1. Introduction
2. Outcome Verifiers
3. Process Verifiers
4. Learned, Programmatic, and Hybrid Verifiers
5. Turning Checks into Training Signal
6. Search and Test-Time Verification
7. Reward Hacking, Proxy Misspecification, and Verifier Robustness
8. Faithfulness, Confidence, and What Verification Misses
9. Canonical Domains: Math, Code, and Formal Proof
10. Long-Context, Multimodal, and Agentic RLVR
11. Open Problems and the Research Agenda

Appendices:

- Minimal RL and Post-Training Background
- Benchmarks, Evals, and Contamination
- Practical Verifier Design Checklist

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
