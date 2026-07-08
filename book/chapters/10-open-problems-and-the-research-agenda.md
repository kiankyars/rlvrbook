# Open Problems

![M. C. Escher, _Alfedena Abruzzi_ (1929).](../escher/10-alfedena-abruzzi.jpg){width="80%" fig-align="center"}

## Chapter Map

- Open problems in RLVR.

## Elicitation or creation

**Research question.** Does RLVR with outcome rewards create reasoning capability that was absent from the base model, or does it only reallocate probability mass toward solutions the base model could already sample?

## Reward-hacking

**Is there an over-optimization law for learned graders?** Chapter 7's quantitative anchor, the over-optimization curve of Gao et al., was measured for preference reward models.[@gao2023scaling] No equivalent law exists for rubric aggregates or generative verifiers,[@zhang2025genrm] so practitioners optimizing against them have no principled stopping criterion.

**Can semantic faithfulness be measured directly?** We currently score only what the verifier checks. Without an independent way to measure everything it misses, we cannot tell whether a high-scoring model truly learned the intended behavior or merely learned to satisfy the checks.
