# Reinforcement Learning from Verifiable Rewards {.unnumbered}

This book is a verifier-first reference for RLVR. It is not organized around optimizer fashions or a chronology of papers. Its purpose is to explain what can be verified, how verifier stacks are built, how they shape capability, and where they fail.

[Read the book](chapters/01-the-verifier-lens.md)  
[Download the PDF](rlvrbook.pdf)

## Start Here

### New to RLVR

Read [Chapter 1](chapters/01-the-verifier-lens.md), [Chapter 2](chapters/02-outcome-verifiers.md), and [Chapter 7](chapters/07-reward-hacking-proxy-misspecification-and-verifier-robustness.md).

### Building Systems

Read [Chapter 4](chapters/04-learned-programmatic-and-hybrid-verifiers.md), [Chapter 5](chapters/05-turning-checks-into-training-signal.md), [Chapter 7](chapters/07-reward-hacking-proxy-misspecification-and-verifier-robustness.md), and [Chapter 9](chapters/09-canonical-domains-math-code-and-formal-proof.md).

### Frontier Research

Read [Chapter 8](chapters/08-faithfulness-confidence-and-what-verification-misses.md), [Chapter 10](chapters/10-long-context-multimodal-and-agentic-rlvr.md), and [Chapter 11](chapters/11-open-problems-and-the-research-agenda.md).

## Flagship Figure

The homepage should eventually open with **The RLVR Verifier Stack**: a layered diagram showing task, trajectory, evidence, verifier, reward, and policy/search, with an HTML-only interactive version and a static PDF fallback.

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

## Appendices

- [A. Minimal RL and Post-Training Background](appendices/a-minimal-rl-and-post-training-background.md)
- [B. Benchmarks, Evals, and Contamination](appendices/b-benchmarks-evals-and-contamination.md)
- [C. Practical Verifier Design Checklist](appendices/c-practical-verifier-design-checklist.md)
