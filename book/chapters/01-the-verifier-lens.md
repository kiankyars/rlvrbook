# The Verifier Lens

## Chapter Map

- Central question: What changes when RLVR is defined by the verifier rather than by the optimizer?
- Key distinction: "Verifiable" describes the checking regime and its evidence, not a guarantee that the reward captures everything we care about.
- Main failure mode: Treating a clean checker as if it were the same thing as full task correctness.

## Core Terms

- Verifier: A procedure that maps an output or trajectory to a score using checkable evidence.
- Evidence: The object the verifier actually consumes, such as an answer string, execution trace, proof state, citation set, or environment transition.
- Layered verification: A setting where exact checks, approximate checks, and learned checks coexist in one stack.

## Main Argument

RLVR should be introduced through the checker. The useful first question is not "which optimizer are we using?" but "what can be checked, at what granularity, against which evidence, and with what failure modes?" Once that frame is fixed, the rest of the book becomes legible.

This opening chapter should merge conceptual framing with a taxonomy of what can be verified: final answers, intermediate steps, executable behavior, formal proofs, retrieval-grounded claims, and environment interactions. The goal is to give the rest of the manuscript a stable vocabulary.

## Canonical Examples

- A math checker that extracts a final boxed answer and compares it against the gold target.
- A unit-test harness that executes generated code against hidden and visible tests.
- A proof assistant that validates each accepted proof step against formal rules.
- A long-context verifier that checks whether cited passages actually support the claimed answer.

## Failure Modes

- Confusing exact verification in a narrow interface with full task correctness.
- Overstating objectivity when the checker depends on brittle extraction or formatting conventions.
- Ignoring the difference between what is theoretically checkable and what is operationally checked in a production stack.

## What the Verifier Sees

The verifier sees only the instrumented interface: outputs, traces, evidence sets, or environment transitions that have been exposed for checking.

## What the Verifier Misses

The verifier misses latent competence, hidden reasoning quality, unobserved evidence selection, and any behavior that the task interface does not surface.

## Research Notes

- Which domains admit strong verification with minimal task redesign?
- When does layered verification outperform a single strong checker?
- How much instrumentation is worth adding before the task becomes artificial?
