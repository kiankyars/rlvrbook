[Read the book](chapters/01-the-verifier-lens.md)  
[Download the PDF](rlvrbook.pdf)  
[View on GitHub](https://github.com/kiankyars/rlvrbook)

## Start Here

### New to RLVR

Read [Chapter 1](chapters/01-the-verifier-lens.md), [Chapter 2](chapters/02-outcome-verifiers.md), and [Chapter 7](chapters/07-reward-hacking-proxy-misspecification-and-verifier-robustness.md).

### Building Systems

Read [Chapter 4](chapters/04-learned-programmatic-and-hybrid-verifiers.md), [Chapter 5](chapters/05-turning-checks-into-training-signal.md), [Chapter 7](chapters/07-reward-hacking-proxy-misspecification-and-verifier-robustness.md), and [Chapter 9](chapters/09-canonical-domains-math-code-and-formal-proof.md).

### Frontier Research

Read [Chapter 8](chapters/08-faithfulness-confidence-and-what-verification-misses.md), [Chapter 10](chapters/10-long-context-multimodal-and-agentic-rlvr.md), and [Chapter 11](chapters/11-open-problems-and-the-research-agenda.md).

## Flagship Figure

The RLVR pipeline can be read as a stack from objective definition to policy/search updates.
Placeholder for the RLVR Verifier Stack figure.

## Table of Contents

### Foundations

- [1. The Verifier Lens](chapters/01-the-verifier-lens.md)

### Verifier Design

- [2. Outcome Verifiers](chapters/02-outcome-verifiers.md)
- [3. Process Verifiers](chapters/03-process-verifiers.md)
- [4. Learned, Programmatic, and Hybrid Verifiers](chapters/04-learned-programmatic-and-hybrid-verifiers.md)

### From Verifiers to Capability

- [5. Turning Checks into Training Signal](chapters/05-turning-checks-into-training-signal.md)
- [6. Search and Test-Time Verification](chapters/06-search-and-test-time-verification.md)

### Failure Modes

- [7. Reward Hacking, Proxy Misspecification, and Verifier Robustness](chapters/07-reward-hacking-proxy-misspecification-and-verifier-robustness.md)
- [8. Faithfulness, Confidence, and What Verification Misses](chapters/08-faithfulness-confidence-and-what-verification-misses.md)

### Domains and Frontiers

- [9. Canonical Domains: Math, Code, and Formal Proof](chapters/09-canonical-domains-math-code-and-formal-proof.md)
- [10. Long-Context, Multimodal, and Agentic RLVR](chapters/10-long-context-multimodal-and-agentic-rlvr.md)
- [11. Open Problems and the Research Agenda](chapters/11-open-problems-and-the-research-agenda.md)

### Appendices

- [A. Minimal RL and Post-Training Background](appendices/a-minimal-rl-and-post-training-background.md)
- [B. Benchmarks, Evals, and Contamination](appendices/b-benchmarks-evals-and-contamination.md)
- [C. Practical Verifier Design Checklist](appendices/c-practical-verifier-design-checklist.md)

## LLM Use

Fortunately, we live in a world where AI slop writing is still *very* intelligible from genuine human text. It is knowing this fact, and also knowing that a textbook is still very much a human-lead endeavor that I write almost all of the sections on my own, or rather use Wispr Flow to dictate them and then edit them. The main contributions of Codex to this project were:
- helping me plan out the structure
- giving me the initial boilerplate/skeleton scaffold of the textbook itself
- creating the diagrams and equations, since this is much more effecient, in particular given my lack of LaTex scripting skills, and is inherently much lower-entropy than writing english, not requiring the same human creativity

## Acknowledgments

- I shamelessly take inspiration from Nathan Lambert's [RLHF book](https://rlhfbook.com), and I am well aware that his textbook treats the subject of RLVR in quite some detail; notwithstanding, as he notes himself, this particular sub-field of ML is evolving so fast that much of the RLHF book's RLVR content will become outdated, and this book is intended to maintain pace with progress.
