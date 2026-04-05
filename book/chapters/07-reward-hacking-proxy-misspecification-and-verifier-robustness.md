# Reward Hacking, Proxy Misspecification, and Verifier Robustness

![M. C. Escher, _Fiumara, Calabria_ (1930).](../art/escher/07-fiumara-calabria.jpg){width="80%" fig-align="center"}

## Chapter Map

- Explain how verifier-driven optimization fails under pressure.
- Treat the checker as an attack surface, not just as an evaluator.

## Main Argument

Any serious RLVR book must treat reward hacking as first-class content. Checker bugs, extraction exploits, benchmark artifacts, weak hidden tests, and biased learned judges all create opportunities for optimization to go in the wrong direction while still looking successful under the nominal reward.

This chapter should teach readers to think adversarially about verifiers: how they are exploited, how those exploits are discovered, and which hardening moves are worth the added complexity.

## Canonical Examples

- Formatting hacks that pass an answer extractor while avoiding the intended reasoning task.
- Unit-test overfitting in code generation.
- Judge-model exploitation through stylistic cues or adversarial phrasing.

## Failure Modes

- Treating benchmark score gains as evidence that the verifier is sound.
- Adding complexity to the stack without improving auditability.
- Leaving hidden tests too close to visible tests.

## What the Verifier Sees

The verifier sees the narrow interface it was designed to score and any auxiliary evidence explicitly exposed to it.

## What the Verifier Misses

It misses behavior outside that interface, including subtle exploit strategies that preserve nominal correctness on the checked slice while breaking the intended task.

## Research Notes

- Which verifier-hardening techniques generalize across domains?
- How should robustness be evaluated before large-scale optimization begins?
- When do learned verifiers create more attack surface than they remove?
