# Search and Test-Time Verification

## Chapter Map

- Explain what verifiers enable at inference time, not just during training.
- Distinguish immediate gains from search and reranking from gains that are actually amortized into the policy.

## Main Argument

Modern RLVR is inseparable from inference-time compute. Self-consistency, reranking, draft-and-check loops, tool-augmented checking, and structured search all change what the verifier makes possible before the model has fully internalized the behavior.

This chapter should make the training-versus-search boundary explicit. Readers should leave able to separate gains from better policies, better search, and better verifiers.

## Canonical Examples

- Best-of-N math solution selection with an exact answer checker.
- Multi-candidate code generation with unit-test reranking.
- Tool-using agents that query external systems and verify intermediate tool outputs before continuing.

## Failure Modes

- Reporting test-time-search gains as if they were pure policy improvements.
- Ignoring latency and cost when verifier-heavy search is deployed.
- Building search around a weak verifier and amplifying the wrong behavior.

## What the Verifier Sees

The verifier sees multiple candidate outputs, revisions, search nodes, or tool traces rather than a single final sample.

## What the Verifier Misses

It still misses counterfactual search paths not explored and any capability not expressed through the chosen candidate set.

## Research Notes

- Which verifier regimes benefit most from search before training?
- How should evaluations separate amortized capability from search-assisted capability?
- When does search amplify reward hacking rather than competence?
