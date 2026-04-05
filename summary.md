# Reinforcement Learning from Verifiable Rewards

## Core Thesis

This book treats RLVR as the study of verifiers. The central object is not the optimizer but the checker: what it can observe, what evidence it consumes, what proxy it induces, how it shapes search and learning, and how it fails under pressure. The intended reader is a frontier-lab researcher or engineer who wants a durable reference for verifier-driven post-training.

## Editorial Stance

Three choices define the manuscript:

1. Verifier-first. Organize the book around what is being verified and how that verification is implemented.
2. Failure-aware. Treat reward hacking, proxy misspecification, and epistemic blind spots as core material.
3. Domain-grounded. Return repeatedly to math, code, formal proof, long-context grounding, and agentic settings.

## Locked Table of Contents

### 1. Introduction

Define RLVR through the verifier rather than through reinforcement learning alone. Merge the opening conceptual framing with the taxonomy of what can be verified: outcome checks, process checks, executable checks, proof checks, retrieval-grounded checks, environment feedback, and layered verification.

### 2. Outcome Rewards

Study final-answer and completed-solution checkers: exact match, extraction pipelines, unit tests, theorem checkers, symbolic evaluators, hidden tests, and domain-specific graders. Emphasize representation choices, normalization, ambiguity handling, and checker brittleness.

### 3. Process Verifiers

Cover stepwise verification, process supervision, and dense credit assignment. Keep the focus on when intermediate reasoning is coherent enough to check and when process rewards genuinely improve capability rather than only surface presentation.

### 4. Learned, Programmatic, and Hybrid Verifiers

Explain the implementation spectrum from hard-coded checkers to judge models to layered verifier stacks. Center the chapter on reliability, calibration, error compounding, and attack surface.

### 5. Turning Checks into Training Signal

Bridge verifier design to learning behavior without turning the chapter into optimizer taxonomy. Cover sparse versus dense rewards, binary versus graded scoring, filtering, curriculum, and other signal-quality choices that determine whether a verifier is actually useful.

### 6. Search and Test-Time Verification

Show how verifiers shape inference-time compute: reranking, self-consistency, draft-and-check loops, tool-augmented checking, and more structured search. Make the case that RLVR is as much about amortizing verification-enabled search as it is about training.

### 7. Reward Hacking, Proxy Misspecification, and Verifier Robustness

Treat the verifier as an attack surface. Cover checker exploits, benchmark gaming, spurious intermediate steps, judge-model bias, and practical hardening strategies such as hidden tests, ensembles, and adversarial audits.

### 8. Faithfulness, Confidence, and What Verification Misses

Address the gap between satisfying a verifier and developing the intended competence. Cover unfaithful reasoning, limits of chain-of-thought observability, self-verification failures, and confidence miscalibration.

### 9. Canonical Domains: Math, Code, and Formal Proof

Use the strongest current domains to compare verifier regimes. Math, code, and proof assistants should serve as the canonical examples for clean answers, executable rewards, and formal correctness.

### 10. Long-Context, Multimodal, and Agentic RLVR

Cover the frontier where verification becomes more indirect. Focus on grounded evidence use, perceptual ambiguity, tool traces, environment feedback, and the point at which verifier design starts to crack.

### 11. Open Problems and the Research Agenda

Close by identifying the unresolved bottlenecks: stronger process verifiers, trusted learned judges, distinguishing reasoning gains from search amplification, and integrating RLVR with abstention, uncertainty, safety, and alignment constraints.

## Appendices

- **A. Minimal RL and Post-Training Background**: the smallest RL appendix needed to support the main text.
- **B. Benchmarks, Evals, and Contamination**: benchmark hygiene, extraction mismatch, leakage, hidden tests, and reporting pitfalls.
- **C. Practical Verifier Design Checklist**: a compact field manual for designing a new verifier stack.

## Flagship Figures

### 1. The RLVR Verifier Stack

Place this on the homepage and in chapter 1. It should show task, trajectory, evidence, verifier, reward, and policy or search in one layered stack. The HTML version should let the reader toggle which evidence is exposed to the verifier and see how the failure mode changes. The PDF version should be a clean static stack with annotated variants.

### 2. What Can Be Verified?

Use this in chapter 1 as a domain map. Plot math, code, proof, long-context QA, multimodal tasks, and agentic settings by verification strength and verification granularity. The HTML version should reveal the checked object, attack surface, and blind spot for each point. The PDF version should use numbered callouts on the same map.

### 3. Outcome vs Process vs Hybrid

Use this across chapters 2 through 4. Show the same example scored three ways: outcome-only, process, and hybrid stack. The HTML version should step through a single trajectory and show which verifier fires where. The PDF version should be a static three-column walkthrough.

### 4. Reward Hacking Sandbox

Use this in chapter 7. Let the reader change extractor rules, hidden tests, or judge strictness and watch a strategy move from "correct" to "high reward but wrong." The PDF version should show a small set of fixed scenarios with before-and-after outcomes.

### 5. Search vs Amortization

Use this in chapter 6. Show how verifier-assisted search improves results immediately and how training amortizes some of that gain into the policy. The HTML version should expose search-budget and before-versus-after toggles. The PDF version should be a static curve panel with a few representative budgets.

## Chapter Contract

The book should use a small set of chapter archetypes rather than one universal template.

### Core Concept Chapters

Use for chapters that define concepts, distinctions, or design problems. These chapters should usually include:

1. A chapter map.
2. Core terms.
3. A main argument.
4. Design patterns or canonical examples.
5. Limits, failure modes, or open questions where they matter.

### Domain Chapters

Use for comparative chapters centered on task families or applied settings. These chapters should usually include:

1. A chapter map.
2. A domain overview.
3. A verifier-regime comparison.
4. Canonical cases.
5. Comparative lessons and open questions.

### Appendices

Use for reference material, checklists, and background support. These should stay utilitarian rather than imitating the main-text chapter shape.

## What This Book Is Not

This is not a timeline of RLVR papers, not a general RL textbook, and not a survey organized around optimizer variants. It should stay disciplined about the verifier as the primary object of study.
