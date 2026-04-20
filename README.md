# RLVR Book

This repository contains **Reinforcement Learning from Verifiable Rewards**, a reference book on RLVR as a paradigm for learning from verifiable reward signals.

## Book Style

- One Markdown file per chapter and appendix, compiled with Quarto to HTML and PDF.
- Every main chapter opens with an M. C. Escher image.
- Every main chapter begins with a short two-bullet chapter map.

## Commands

- `quarto render book`
- `scripts/check-citations`
- `scripts/check-diagrams`

## Optional linting

- `npx prettier . --write '!book/**/*.md'`
      - We cannot use Prettier over the book source because Quarto uses Pandoc markdown syntax as opposed to CommonMark
