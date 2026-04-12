# RLVR Book

This repository contains **Reinforcement Learning from Verifiable Rewards**, a reference book on RLVR as a paradigm for learning from verifiable reward signals. The book is not organized around optimizer fashions or a general RL survey structure. Its purpose is to explain what kinds of rewards can be made verifiable, how those rewards are implemented in practice, how they become useful training signal, where the paradigm has been strongest, and where it breaks.

## Current Framing

The current manuscript treats RLVR as the study of **learning from verifiable reward signals**. The reward channel is the durable object of study. Optimizers matter, but they are supporting machinery rather than the spine of the book.

This book is not:

- a general reinforcement learning textbook
- a survey organized around optimizer variants
- a pure paper timeline
- a generic RLHF book with some RLVR chapters added on top

## Review status

[x] 1. Introduction
[x] 2. Outcome Rewards
[x] 3. Process Rewards
[x] 4. Learned, Programmatic, and Hybrid Verifiers (need to look at git diff)
[x] 5. Turning Checks into Training Signal
[] 6. Search and Test-Time Verification
[] 7. Reward Hacking, Proxy Misspecification, and Verifier Robustness
[] 8. Faithfulness, Confidence, and What Verification Misses
[] 9. Canonical Domains: Math, Code, and Formal Proof
[] 10. Long-Context, Multimodal, and Agentic RLVR
[] 11. Open Problems and the Research Agenda

## Book Style

- One Markdown file per chapter and appendix, compiled with Quarto to HTML and PDF.
- Every main chapter opens with an M. C. Escher image.
- Every main chapter begins with a short two-bullet chapter map.
- Chapter structure is flexible beyond that; the book does not use a rigid universal template.
- Core reusable terminology belongs in the appendix rather than being forced into every chapter.
- HTML chapters use Quarto's native appendix handling for references and footnotes.

## Code Layer

The manuscript uses a graduated code plan:

- Chapter 2: minimal outcome verifier
- Chapter 3: small process-reward snippets
- Chapter 4: small hybrid-verifier snippet
- Chapter 5: one larger worked outcome-RLVR training script
- Chapter 10: frontier coding harnesses as a distinct later topic

## Figure Program

- Chapter 1 already has the RLVR verifier stack and the interactive domain map.
- Chapter 2 has answer normalization.
- Chapter 3 has process-vs-outcome visualization.
- Chapter 4 is intended to open with the verifier-stack residual diagram.

The guiding visual language is technically rigorous diagrams, Escher chapter art, and light HTML interactivity where it materially improves comprehension.

## Commands

- `quarto render book`
- `scripts/build-book`
- `scripts/lint-book`
- `scripts/check-citations`
- `scripts/check-diagrams`

## Outreach

Planned launch channels:

- Hacker News
- Discord
- Unsloth
- NL
- discuss all of the aspects of the reasoning in Nathan Lambert's book, which is to say talk about the curriculum and all of these techniques from his reasoning chapter.
- Add code to every chapter?
- Upweighting: Warren