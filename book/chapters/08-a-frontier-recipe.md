# A Frontier Recipe

![M. C. Escher, _Morano Calabria_ (1930).](../escher/08-morano-calabria.jpg){width="80%" fig-align="center"}

## Chapter Map

- Describe OLMo 3 Think's RLVR recipe.

## Setup

We pick OLMo 3, because it explains the complete pipeline of training frontier models. The starting point is from OLMo 3 Base. Ai2 trains that base model through pretraining on broad language, code, math, and knowledge domains. Midtraining adds a 100B-token capability-focused mix. There is then a long-context extension phase that lets the model handle contexts up to roughly 65K tokens, before Post-training.[@teamolmo2025olmo3; @ai22025olmo3blog]

## Post-training

1. Think SFT trains the model to produce structured reasoning traces.
2. Think DPO tunes the model with contrastive preference data.
3. Think RLVR updates the model with outcome rewards from verifiers and LM judges.

If we zoom into the RLVR recipe specifically, we get the following sequence:

1. Initialize the policy from the Think DPO checkpoint.
2. Draw training prompts from the Dolci-Think-RL dataset.
3. Use asynchronous actor-learner infrastructure to sample long reasoning rollouts from the DPO-initialized policy.
4. Score each rollout with a domain-specific reward function.
5. Keep prompt groups with non-zero reward variation.
6. Update the policy with OlmoRL, Ai2's GRPO-based trainer, using each rollout's reward minus the same-prompt group mean as the advantage.

## GRPO

The following modifications are made to vanilla GRPO:

1. Any rollout where all samples have the same reward are removed to avoid training on samples that provide zero gradient.
2. No KL loss to prevent restrictive policy updates.
3. A token-level loss is used despite the reward being outcome based; the reason for this is to normalize the loss by the total number of tokens across the batch, rather than per sample, to avoid over-weighting long rollouts.
    - Suppose one model response is 10 tokens long and another is 100 tokens long. If you normalize loss per sample and both samples had the same reward, the longer response would contribute 10× more to the total loss.
4. GRPO already limits how much one update can change token probabilities, and the clipping is tweaked to be asymmetric, such that the positive limit is larger than the negative limit, meaning high-reward tokens are reinforced more than low-reward tokens.
5. The advantage calculation uses a simplified group-relative advantage $A_i = r_i - \bar r$ instead of $A_i = (r_i - \bar r) / \sigma_r$, because dividing by a tiny within-group standard deviation can artificially magnify prompts where all completions had almost the same reward.
6. Truncated importance sampling played an important role too, its purpose is to discount or upweight tokens produced by an older policy by a capped ratio $\operatorname{clip}(\pi_{\mathrm{current}}(a_t\mid h_t)/\pi_{\mathrm{old}}(a_t\mid h_t))$. The result is that asynchronous rollouts remain usable without stale samples biasing the update.

## Rewards

OLMo 3 Think is trained on four reward domains:

- Math uses a rule-based verifier that normalizes the model's final answer and performs a symbolic check through SymPy to determine if the model answer symbolically matches the correct answer. It returns 1 when the answer matches and 0 otherwise.

- code is checked against test cases with two rewards: percentage of tests passed, or a binary reward that returns 1 only when all tests pass.

- Instruction following uses constraint functions to verify the response satisfies the prompt's listed constraints, e.g. "were there two paragraphs?" The reward is 1 if the response satisfies all constraints and 0 otherwise.

- LLM-as-a-Judge with Qwen3 32B as the judge is used in two scenarios.[^ch8-chat-judge-example]

    1. Reference-based chat, where the judge compares the model response with a provided reference answer.
    2. Open-ended chat; the judge scores the response without a reference.

## Filtering and data mixing

Prompt filtering is the first step, where eight rollouts are sampled per prompt from the initial DPO checkpoint, and any prompts with pass rate greater than 62.5% are removed from the dataset. This is done offline before RL, and then the model is trained over the filtered prompts

Second, in spite of the aforementioned filtering of zero-gradient groups, a consistent batch size is maintained by actively sampling and filtering rollouts until the desired batch size is reached, importantly all of those groups having non-homogenous reward, providing a better signal.

The data mixture between the four domains is non trivial in determining downstream performance. Since every mixture could not be tested with a full run, a 500 to 1000 step probe tested which domains improved or regressed based on the mixture. The result was a mixed-domain batch with extra weight on math and instruction following.[@teamolmo2025olmo3]

## The rollout system

These final reasoner rollouts with maximum length 32K tokens and average generations more than 10K tokens.[@teamolmo2025olmo3] Because of the long sequences, static batching results in actors having to wait for the slowest link, which can be up to 32K-tokens, wasting compute. Continuous batching backfills finished rollouts, and the report estimates that static batching wastes up to 54% of compute at a 32K generation length.

Training uses a fully asynchronous setup, where we prompt actors served on vLLM to generate responses. The current policy trains from the samples the actors return, with inferencing using much more compute than training: for the 32B reasoner, there were 20 nodes for inference and 8 H100 nodes for training, while the 7B reasoner had 7 inference nodes and 2 learner nodes.

## PipelineRL

RLVR must both generate rollouts and train a policy, and similar to the computation vs communication tradeoff, we want to overlap the two operations to the greatest extent possible in order to saturate compute to the greatest extent. PipelineRL runs generation and training concurrently, then sends in-flight weight updates to the generation engines so actors keep generating with fresher weights.[@piche2025pipelinerl]

Concretely:

1. Run an optimizer step on the current policy and get new weights.
4. The current policy broadcasts the new parameter tensors.
5. The actors copies those tensors into the existing GPU weight buffers.
6. The actors resume the same generation queue.

The weird part is the KV cache. The technical report states despite the prefix cache being computed under the older weights, they **do not invalidate/clear the KV cache** when swapping in the new weights, because empirically they found it worked and gave a large throughput gain.[^ch8-inflight-update-boundary] Truncated importance sampling provides a great marriage to PipelineRL's by preventing biased updates because the actors that generated a rollout may differ from the current policy that trains on it. In fact, the initial 7B Think RLVR run without PipelineRL or truncated importance sampling took 15 days, and the addition of the two methods reached the same performance in 6 days.[@teamolmo2025olmo3]

## Takeaways

The technical report compares RL from SFT versus RL from DPO, and the result was that the latter gives a better resujlt than the former. The second lesson is that mixed-domain RL prevents over-optimization as ooposed to single-domain RL. Interestlym reward curves are not causual on performance, the report states that even though the train reward was lower for the mixed run than the single-domain one, downstream performance is still superior for a mixed dataset, i.e. a higher training reward can mean over-optimization to a narrower distribution.

[^ch8-chat-judge-example]: A prompt can be: "Explain the moon landing to a 6-year-old in a few sentences." In both reference-based and open-ended chat, the judge is prompted to score the response in $[0,1]$.

[^ch8-inflight-update-boundary]: Inflight updates do **not** update weights while a GPU kernel is mid-matmul. The actors pause at a safe boundary between decode steps, overwrite their model-weight tensors with the learner's newer weights, then resume generation.
