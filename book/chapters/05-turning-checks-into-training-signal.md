# Turning Checks into Training Signal

## Chapter Map

- Explain how a checker becomes useful learning signal rather than a brittle scoreboard.
- Keep the focus on signal quality, task shaping, and curriculum rather than optimizer taxonomy.

## Main Argument

The same verifier can be useful or useless depending on how its outputs are turned into signal. Binary versus graded scoring, task selection, filtering, rollout grouping, and curriculum decisions all change the effective optimization landscape before any optimizer-specific choice matters.

This chapter should stay narrowly focused on signal design: how to make checks teachable, how to prevent verifier noise from dominating learning, and how to decide when simple rejection or search-based selection already captures most of the gain.

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
