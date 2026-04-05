# Outcome Verifiers

## Chapter Map

- Explain how strong outcome verifiers are built for completed solutions.
- Show why extraction, representation, and hidden brittleness matter more than the apparent simplicity suggests.

## Main Argument

Outcome verifiers are the natural entry point for RLVR because they are operationally simple and often highly scalable. They become useful when the mapping from model output to checked object is stable, unambiguous, and hard to exploit.

This chapter should focus on answer normalization, format design, theorem checking, executable grading, partial credit, and benchmark hygiene. The hard part is often not the final comparison rule but the interface contract that determines what is being compared.

## Canonical Examples

- Exact-match grading for math problems with normalized final answers.
- Code execution against a test suite with hidden tests.
- Formal theorem acceptance in a proof assistant.
- Symbolic evaluation for structured tasks where multiple surface forms represent the same answer.

## Failure Modes

- Checker errors induced by fragile extraction or formatting assumptions.
- Benchmarks that reward shortcuts rather than the intended capability.
- Partial-credit schemes that leak exploitable heuristics.

## What the Verifier Sees

The verifier sees the final artifact: answer string, code file, proof object, or structured output that survives extraction.

## What the Verifier Misses

It misses how the artifact was produced, whether intermediate reasoning was valid, and whether success came from true competence or from exploiting narrow regularities.

## Research Notes

- When is binary scoring enough, and when is graded outcome feedback worth the complexity?
- How should hidden tests be designed to reduce benchmark gaming without drifting away from the task?
- Which extraction conventions are stable across model families?
