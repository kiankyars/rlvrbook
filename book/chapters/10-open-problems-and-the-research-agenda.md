# Open Problems

![M. C. Escher, _Alfedena Abruzzi_ (1929).](../escher/10-alfedena-abruzzi.jpg){width="80%" fig-align="center"}

## Chapter Map

- Open problems in RLVR.

## Elicitation or creation

**Research question.** Does RLVR with outcome rewards create reasoning capability that was absent from the base model, or does it only reallocate probability mass toward solutions the base model could already sample?

## Reward-hacking

**Is there an over-optimization law for learned graders?** Chapter 7's quantitative anchor, the over-optimization curve of Gao et al., was measured for preference reward models [@gao2023scaling]. No equivalent law exists for rubric aggregates or generative verifiers [@zhang2025genrm], so practitioners optimizing against them have no principled stopping criterion.

**Can semantic faithfulness be measured directly?** We currently score only what the verifier checks. Without an independent way to measure everything it misses, we cannot tell whether a high-scoring model truly learned the intended behavior or merely learned to satisfy the checks.

## A predictive science of RL compute

**Research question.** Does RL post-training admit predictive scaling laws of the kind pretraining has, and what determines the asymptote a recipe saturates toward?

The first large systematic datapoint is ScaleRL: a study totaling more than 400,000 GPU-hours that fits sigmoidal compute-performance curves to RL training runs and validates them by predicting, from smaller runs, the trajectory of a single run extended to 100,000 GPU-hours [@khatri2025scalerl].

Open questions follow directly. What sets the asymptote: the base model's support, as the elicitation problem suggests, or removable inefficiencies of current recipes? Do fitted curves transfer across model families and task mixtures? How should a fixed budget split between pretraining, SFT, and RL? And does prolonged RL erode the plasticity it relies on [@khan2026plasticity]?

## Credit assignment at horizon scale

**Research question.** At what horizon does a terminal outcome reward stop carrying usable learning signal, and can process-level signals be made simultaneously scalable and hack-resistant?

The agentic regime sharpens the question. Credit in reasoning RL spans one generation of 500 to 30K+ tokens; agentic RL spans hundreds of turns and 100K to 1M tokens, where a single episode-level scalar becomes increasingly uninformative, and the methods literature has no shared benchmark for comparing credit-assignment quality [@zhang2026creditsurvey]. What is open: whether outcome rewards plus task structure suffice at these horizons, and which intermediate states are verifiable.

## Self-improvement without external verification

**Research question.** Can a model's own signals, such as confidence, self-consistency, or self-judgment, sustain RL improvement, or do self-reward loops inevitably collapse?
