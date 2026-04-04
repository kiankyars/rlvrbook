# Learned, Programmatic, and Hybrid Verifiers

## Chapter Map

- Central question: How should verifier stacks be built when a single hard-coded checker is not enough?
- Key distinction: Outcome versus process describes what is checked; learned versus programmatic describes how the checker is implemented.
- Main failure mode: Combining multiple imperfect signals without understanding how their errors compound.

## Core Terms

- Programmatic verifier: A rule-based checker implemented through deterministic logic, execution, or formal constraints.
- Learned verifier: A model-based judge that predicts correctness, quality, or consistency.
- Verifier stack: A layered pipeline that combines multiple checks before producing a reward or decision.

## Main Argument

Many real RLVR systems rely on a stack, not a single verifier. Programmatic checks bring precision, learned judges bring flexibility, and hybrid pipelines make partial verification regimes practical. The design problem is deciding where to trust each layer and how to audit the stack as a whole.

This chapter should center reliability, calibration, appeals, arbitration logic, and how to prevent judge-model weaknesses from becoming the dominant attack surface.

## Canonical Examples

- A programmatic math checker backed by a learned fallback judge for ambiguous outputs.
- A code verifier that combines execution, linting, and judge-model review of unsafe behavior.
- A long-context verifier that mixes citation matching, retrieval consistency, and learned entailment checks.

## Failure Modes

- Silent disagreement between stack components.
- Learned judges inheriting benchmark artifacts or stylistic bias.
- Excessive verifier complexity that makes audits harder than the original task.

## What the Verifier Sees

The stack sees a union of artifacts, traces, retrieved evidence, execution results, and model-judged summaries.

## What the Verifier Misses

It still misses behavior that never enters the instrumented pipeline, along with any systematic blind spots shared by the stack components.

## Research Notes

- When should learned judges be first-class components rather than fallbacks?
- What are the right interfaces for appeals and verifier arbitration?
- How can verifier-stack audits remain tractable as systems grow more layered?
