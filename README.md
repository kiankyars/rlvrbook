**SEP 24, 2026: IMPORTANT NOTICE: I'M CURRENTLY IN THE PROCESS OF REWRITING CHAPTERS 9-11, SO IF YOU READ THEM AND FIND MANY ERRORS, PLEASE WAIT UNTIL I RESOLVE THEM BEFORE YOU COMMIT.**

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

- Add image-gen diagrams to textbook where there is clear clarity gain
