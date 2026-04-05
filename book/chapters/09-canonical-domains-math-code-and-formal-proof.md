# Canonical Domains: Math, Code, and Formal Proof

## Chapter Map

- Compare how verifier regimes differ across math, code, and formal proof.
- Show why strong checkability does not mean the same reward interface or the same failure modes.

## Domain Overview

Math, code, and formal proof should anchor the book because they expose different strengths and weaknesses of verifiable training. Math offers clean final answers, code offers executable rewards with brittle infrastructure, and proof assistants offer the strongest formal checks but demand more structure and search.

This chapter should compare the verifier interface across the three domains rather than merely survey results.

## Verifier Regime

- Math verifier: A checker centered on answer extraction, symbolic equivalence, or structured derivation validity.
- Code verifier: A checker centered on execution, tests, static constraints, and runtime behavior.
- Formal proof verifier: A checker centered on proof objects and proof-assistant acceptance.

Each regime exposes a different checked object and a different set of bottlenecks. Math emphasizes clean targets and extraction. Code emphasizes execution realism and infrastructure quality. Proof emphasizes decomposition, search, and formal acceptance.

## Canonical Cases

- Final-answer math grading with normalized extraction.
- Unit-test-based code verification with hidden tests and flaky-environment controls.
- Lean or other proof-assistant verification of generated proof steps.

## Comparative Lessons

- Borrowing evaluation intuitions from math and applying them unchanged to code or proof is usually a mistake.
- Executable domains make verifier quality depend heavily on infrastructure rather than only on scoring logic.
- Formal proof exposes the strongest clean verifier but also the sharpest decomposition and search constraints.
- Process verification plays a different role in each domain and should not be ported mechanically.

## Research Notes

- Which lessons from proof systems transfer back to less formal domains?
- How should code verifiers be hardened against flaky or underspecified tests?
- When should math domains use process verification instead of answer-only checks?
