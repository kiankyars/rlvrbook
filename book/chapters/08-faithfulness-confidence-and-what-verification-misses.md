# Faithfulness, Confidence, and What Verification Misses

## Chapter Map

- Explain what important properties remain off-screen even when a verifier is strong.
- Show why verified success does not imply faithful reasoning or calibrated uncertainty.

## Main Argument

RLVR can produce correct answers without guaranteeing faithful reasoning, transparent internal computation, or calibrated confidence. That is not a reason to abandon RLVR. It is a reason to specify the limits of verification clearly and resist overclaiming.

This chapter should give the reader a principled way to talk about what verifiers cannot see, even when they are strong at the task they were built for.

## Canonical Examples

- Correct final answers paired with misleading chain-of-thought traces.
- Self-verification loops that sound confident while remaining wrong.
- Agents that satisfy tool-based checks while remaining brittle under minor environment changes.

## Failure Modes

- Treating visible reasoning as if it were complete access to model cognition.
- Conflating confidence expression with calibrated belief.
- Using process traces as evidence of truth without checking whether they are causally relevant.

## What the Verifier Sees

The verifier sees externalized answers, explanations, traces, and confidence expressions that have been explicitly surfaced.

## What the Verifier Misses

It misses hidden reasoning, latent uncertainty, and any mismatch between narrated reasoning and actual causal computation.

## Research Notes

- Which faithfulness claims are empirically defensible in verifier-heavy systems?
- How should confidence be trained or evaluated when correctness is verifiable but uncertainty is not?
- Can richer verifier stacks reduce blind spots without pretending to eliminate them?
