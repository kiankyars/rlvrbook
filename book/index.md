# Start Here {.unnumbered}

[<i class="bi bi-file-earmark-pdf"></i> Open PDF](rlvrbook.pdf)  
[<i class="bi bi-github"></i> GitHub](https://github.com/kiankyars/rlvrbook)

![M. C. Escher, _Corsica Corte_ (1929).](escher/00-corsica-corte.jpg){width="80%" fig-align="center"}

Reinforcement learning from verifiable rewards studies how models can improve by learning from reward signals derived from checkable task outcomes, executable feedback, formal validation, or other reliable forms of verification. This book's purpose is to explain what kinds of rewards can be made verifiable, what those rewards actually train, where the paradigm has been most successful, and where it breaks.

## New to RLVR

Read [Chapter 1](chapters/01-introduction.md), [Chapter 2](chapters/02-outcome-rewards.md), and [Chapter 7](chapters/07-reward-hacking-and-verifier-robustness.md).

## Building Systems

Read [Chapter 4](chapters/04-learned-programmatic-and-hybrid-verifiers.md), [Chapter 5](chapters/05-turning-checks-into-training-signal.md), and [Chapter 9](chapters/09-long-context-multimodal-and-agentic-rlvr.md).

## Frontier Research

Read [Chapter 8](chapters/08-a-frontier-recipe.md), [Chapter 9](chapters/09-long-context-multimodal-and-agentic-rlvr.md), and [Chapter 10](chapters/10-open-problems-and-the-research-agenda.md).

## LLM Use

Fortunately, we live in a world where AI slop writing is still *very* intelligible from genuine human text. It is knowing this fact, and also knowing that a textbook is still very much a human-lead endeavor, that I write (I can guarantee you there are no EM dashes in the entire book) most sections on my own, or rather use Wispr Flow to dictate them and then edit them. The main contributions of Codex to this project were:

- helping me plan out the structure
- giving me the initial boilerplate/skeleton scaffold of the textbook itself
- creating the diagrams and equations, since this is much more effecient, in particular given my lack of LaTex scripting skills, and is inherently much lower-entropy than writing english, not requiring the same human creativity

## Target Audience

I wrote this book with the intent to cater to the largest audience possible. With that in mind, I increase difficulty as a function of the chapters such that if you are new to RLVR, you are best served in the beginning. If you are already experienced, you will gain the most from the later chapters.

## How to Use This Book

Each chapter has a TL;DR at the beginning. Although the chapters do minimally build off of each other, they can still read alone. Feel free to use the search function on the web version or Command F on the PDF to find what you wish directly. The citations are plentiful to facilitate further research if there's a specific theme which captivates you.

## Changelog

- 2026-04-16: Officially announced v0 of the book!

## Acknowledgments

I shamelessly take inspiration from Nathan Lambert's [RLHF book](https://rlhfbook.com), and I am well aware that his textbook treats the subject of RLVR in detail; notwithstanding, as he notes himself, this particular sub-field of ML is evolving so fast that much of the RLHF book's RLVR content will become outdated, and this book is intended to maintain pace with progress.

I also acknowledge the wonderful developers of Exclaidraw, which I used for this book's figures. Thanks to M.C. Escher for being the artisitic soul of the book (FYI all art contained in this textbook is published at the latest in 1930, which means it's in the public domain in the United States). Thanks to Simon Boehm for creating amazing educational content and establishing the target I strive to reach (same for Colah from distillpub)! Lastly, thanks to the quarto devs for making the software this book is based on!

## [Github Contributors](https://github.com/kiankyars/rlvrbook?tab=contributing-ov-file)

- Get your name here by reviewing/improving the book!

## Citation

You can cite this book directly with this BibTeX.

```bibtex
@online{kyars2026rlvrbook,
  title   = {Reinforcement Learning from Verifiable Rewards},
  author  = {Kyars, Kian},
  year    = {2026},
  url     = {https://rlvrbook.com},
}
```
