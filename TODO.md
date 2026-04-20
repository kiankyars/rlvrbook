# Remaining action items

## Chapter 8

- [08-a-frontier-recipe.md:15](/Users/kian/Developer/rlvrbook/book/chapters/08-a-frontier-recipe.md#L15): scope the chapter explicitly as a hybrid frontier post-training case study rather than a pure RLVR recipe.
- [08-a-frontier-recipe.md:21](/Users/kian/Developer/rlvrbook/book/chapters/08-a-frontier-recipe.md#L21): carry one prompt through the full pipeline: dataset -> actor rollout group -> reward vector -> filtering -> advantage computation -> learner update -> refreshed actors.
- [08-a-frontier-recipe.md:67](/Users/kian/Developer/rlvrbook/book/chapters/08-a-frontier-recipe.md#L67): state the stale-policy or off-policy problem before introducing PipelineRL and truncated importance sampling, so the systems machinery is motivated by an actual failure mode.

## Chapter 9

- [09-long-context-multimodal-and-agentic-rlvr.md:1](/Users/kian/Developer/rlvrbook/book/chapters/09-long-context-multimodal-and-agentic-rlvr.md#L1): either rename the chapter to match what it actually is, an agentic harness chapter, or broaden it so it really covers long-context and multimodal verification with one concrete example each.
- [09-long-context-multimodal-and-agentic-rlvr.md:13](/Users/kian/Developer/rlvrbook/book/chapters/09-long-context-multimodal-and-agentic-rlvr.md#L13): define the harness operationally, not just visually. Spell out what is logged, what is checked, what becomes reward-bearing, and what remains verifier-blind.
- [09-long-context-multimodal-and-agentic-rlvr.md:31](/Users/kian/Developer/rlvrbook/book/chapters/09-long-context-multimodal-and-agentic-rlvr.md#L31): clarify the DeepSWE numbers, especially what the `59.2` figure is. It should be obvious whether this is verifier-reranked pass@1 from 16 candidates or some other evaluation object.
- [09-long-context-multimodal-and-agentic-rlvr.md:50](/Users/kian/Developer/rlvrbook/book/chapters/09-long-context-multimodal-and-agentic-rlvr.md#L50): define `guidance` precisely enough that the reader knows whether it is a training-time rollout modification, a data-construction procedure, auxiliary supervision, or test-time retry/search.

## Chapter 10

- [10-open-problems-and-the-research-agenda.md:9](/Users/kian/Developer/rlvrbook/book/chapters/10-open-problems-and-the-research-agenda.md#L9): rebuild this as an actual agenda chapter with 4-6 named open problems, one section per problem.
- [10-open-problems-and-the-research-agenda.md:9](/Users/kian/Developer/rlvrbook/book/chapters/10-open-problems-and-the-research-agenda.md#L9): turn "verifier fidelity beyond math and code" into actual research questions rather than a domain list. The invariant problem is semantic faithfulness under weak endpoint proxies.
- [10-open-problems-and-the-research-agenda.md:15](/Users/kian/Developer/rlvrbook/book/chapters/10-open-problems-and-the-research-agenda.md#L15): if `adaptive RLVR` stays, define what is adapting, verifier, data distribution, harness, or curriculum, on what signal, and to solve which failure mode. Otherwise cut the generic state-evolution equation.
