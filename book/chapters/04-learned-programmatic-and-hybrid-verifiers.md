# Learned, Programmatic, and Hybrid Verifiers

![M. C. Escher, _Dolphins_ (1923).](../art/escher/04-dolphins.jpg){width="80%" fig-align="center"}

## Chapter Map

- Explain how to build verifier stacks when a single hard-coded checker is not enough.
- Show the main risk: combining imperfect signals without understanding where their errors compound.

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
