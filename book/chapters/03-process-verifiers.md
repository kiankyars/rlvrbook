# Process Verifiers

## Chapter Map

- Explain when intermediate verification improves credit assignment beyond final-answer rewards alone.
- Show the main risk: rewarding reasoning-shaped traces that correlate weakly with actual competence.

FIGURE- Outcome versus process preview: Chapter 2 checks the endpoint; later chapters ask what can be said about the path.

## Main Argument

Process verifiers matter when final-answer rewards are too sparse, too delayed, or too weak to shape behavior reliably. They are not justified by default. A process signal is only helpful if the notion of a "good step" can be defined operationally and checked with enough fidelity.

This chapter should explain how intermediate checks change the learning problem, when they stabilize training, and when they instead create a new proxy that is easier to game than the original task.

## Canonical Examples

- Stepwise checking in mathematical derivations.
- Subgoal validation in formal proofs.
- Intermediate execution checks in long programs or tool-using agents.
- Evidence-selection checks in long-context grounded reasoning.

## Failure Modes

- Rewarding stylistic chains of thought instead of useful intermediate progress.
- Overfitting to the local process checker while harming global task performance.
- Treating process supervision as universally better than outcome supervision.

## What the Verifier Sees

The verifier sees instrumented intermediate states: reasoning steps, subgoal states, partial executions, or cited evidence selections.

## What the Verifier Misses

It misses latent cognition that is not externalized and any beneficial shortcut that bypasses the annotated step structure without harming the final answer.

## Research Notes

- Which tasks admit stable intermediate labels without excessive annotation overhead?
- How do process rewards interact with hidden reasoning or compressed internal computation?
- When should process checks be strict versus advisory?
