# Turning Checks into Training Signal

![M. C. Escher, _The Drowned Cathedral_ (1929).](../art/escher/05-the-drowned-cathedral.jpg){width="80%" fig-align="center"}

## Chapter Map

- Explain how a checker becomes useful learning signal rather than a brittle scoreboard.
- Keep the focus on signal quality, task shaping, and curriculum rather than optimizer taxonomy.

## Main Argument

The same verifier can be useful or useless depending on how its outputs are turned into signal. Binary versus graded scoring, task selection, filtering, rollout grouping, and curriculum decisions all change the effective optimization landscape before any optimizer-specific choice matters.

This chapter should stay narrowly focused on signal design: how to make checks teachable, how to prevent verifier noise from dominating learning, and how to decide when simple rejection or search-based selection already captures most of the gain.

## Post-training harnesses as separate infrastructure

A common shorthand in this area is “post-training on a harness.” The harness is the structured system that turns verifiable checks into rewards and then into updates. It has five moving parts:

- A task source: prompts and target data.
- A response contract: response format and extraction rules.
- A reward bank: correctness and quality terms over extracted artifacts.
- A signal policy: filtering, clipping, scaling, and schedule decisions.
- A trainer configuration: rollout counts, clipping, entropy terms, and optimization settings.

For practical implementations, this means you can change the same objective while changing only one harness component, and the behavior changes substantially. That is why it is more precise to say practitioners are changing the harness, not “just changing one hyperparameter.”

For a concrete end-to-end script, the full Brown-style GRPO reference is in [Appendix D](../appendices/d-brown-grpo-reference.md).[^ch5-brown-grpo-150line]

## Canonical Examples

- Moving from binary pass/fail to graded reward in a math domain with partial structure.
- Filtering tasks to keep the model inside the competence band where signal is informative.
- Using hidden tests or harder variants to keep signal quality from collapsing late in training.

## Failure Modes

- Over-rewarding trivial formatting wins.
- Using a sparse reward regime with no viable path to exploration.
- Smuggling optimizer detail into what should be a chapter about checker design.

## What the Verifier Sees

The verifier sees the same artifacts as before; the new design question is how those outputs are transformed into reward, filtering, or acceptance decisions.

## What the Verifier Misses

It still misses off-policy exploration quality, latent competence, and any capability that the selected signal proxy does not capture.

## Research Notes

- Which signal transformations are robust across domains?
- When is graded reward genuinely better than carefully designed binary reward?
- How can task filtering avoid turning the curriculum into a hidden benchmark hack?

[^ch5-brown-grpo-150line]: Brown’s compact GRPO implementation is a practical reference for harness-level RLVR post-training with explicit parsing and reward components.[@brown2025grpo]
