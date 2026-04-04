# Process Verifiers

## Chapter Map

- Central question: When is it useful to verify intermediate reasoning rather than only completed solutions?
- Key distinction: Process verification is valuable when it improves credit assignment, not merely when it makes outputs look nicer.
- Main failure mode: Rewarding surface-form reasoning traces that correlate poorly with actual competence.

## Core Terms

- Process verifier: A checker that scores intermediate steps, subgoals, or partial traces.
- Credit assignment: The problem of deciding which parts of a trajectory deserve reward or blame.
- Dense signal: A reward regime where useful feedback appears before the end of the trajectory.

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
