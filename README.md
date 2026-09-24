Sep 24, 2026 at 14:51Important notice: I'm currently in the process of rewriting chapters 10 to 11, so if you read them and find many errors, please wait until I resolve them before you commit. (change to all caps please)

# RLVR Book

This repository contains **Reinforcement Learning from Verifiable Rewards**, a reference book on RLVR as a paradigm for learning from verifiable reward signals.

## Book Style

- One Markdown file per chapter and appendix, compiled with Quarto to HTML and PDF.
- Every main chapter opens with an M. C. Escher image.
- Every main chapter begins with a short chapter map.

## Commands

- `quarto render book`
- `scripts/check-citations`
- `scripts/check-diagrams`

## Optional linting

- `npx prettier . --write '!book/**/*.md'`
    - We cannot use Prettier over the book source because Quarto uses Pandoc markdown syntax as opposed to CommonMark

## Remaining action items

- Add image-gen diagrams to textbook
