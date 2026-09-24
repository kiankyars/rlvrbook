# Long-context, multimodal, and agentic RLVR

![M. C. Escher, _Cimino Barbarano_ (1929).](../escher/10-cimino-barbarano.jpg){width="80%" fig-align="center"}

## Chapter Map

- Move from single reward functions to harnesses.
- What long context and images change in RLVR, and DeepSWE as a worked agentic example.

## From reward functions to harnesses

Long-context and tool-using settings break the clean RLVR picture from earlier chapters. A rollout may now include repository state, browser state, images, shell transcripts, tool arguments, observations, generated files, runtime failures, partial progress markers, and a termination decision.

The harness decides what the policy is allowed to observe, what actions it can take, what state changes get logged, and which artifacts become reward-bearing. In a math problem, this surface can be tiny: prompt in, final answer out, exact checker at the end. In long-context, multimodal, and agentic tasks, the harness becomes central. It may log evidence spans, retrieved images, browser actions, shell output, patches, timeouts, and tool failures.

::: {#fig-ch9-agentic-harness-stack fig-cap="An agentic RLVR harness makes the trajectory, environment state, and verifier stack part of the training interface."}

::: {.content-visible when-format="html"}
![](../diagrams/10-agentic-harness-stack.png){.light-content}

![](../diagrams/10-agentic-harness-stack-dark.png){.dark-content}
:::

::: {.content-visible when-format="pdf"}
![](../diagrams/10-agentic-harness-stack.png)
:::

:::

## Long context

Long-context RLVR keeps the verifier unchanged, since, WLOG, final answer verification is context-length independent; nevertheless, it stretches everything before as the evidence the model needs sits somewhere in tens of thousands of reasoning tokens. QwenLong-L1 found that applying RL directly to long inputs trains inefficiently and unstably, so it adapts a short-context reasoning model in stages: a supervised warm-up, then RL phases on progressively longer inputs, with hard examples from earlier phases sampled again later [@wan2025qwenlongl1]. Kimi K3 grows its context window in stages during pre-training, from 8K to 1M tokens, and its RL environments then run agents over hundreds or thousands of tool calls and millions of accumulated context tokens [@kimiteam2026k3].

## Multimodal

Multimodal RLVR also tends to keep the verifier textual: the image is part of the prompt, and the reward still checks a final answer. Vision-R1 first fine-tuned on 200K multimodal chain-of-thought examples, then trained with GRPO and a strict format-and-answer reward on 10K multimodal math problems, reaching 73.5% on MathVista with a 7B model [@huang2025visionr1]. The harder case puts vision inside the loop rather than only in the prompt, which Kimi K3 trains through multimodal reasoning with vision-in-the-loop tool use [@kimiteam2026k3].

## DeepSWE

DeepSWE is a software coding agent trained with the rLLM platform. It uses Qwen3-32B as the policy inside the harness and is trained with GRPO++, Agentica's modified GRPO that drops the KL loss, raises the upper clip bound, and uses a leave-one-out baseline. Training took six days on 64 H100 GPUs, and on SWE-Bench-Verified the result is 42.2% Pass@1, 71.0% Pass@16, and 59.0% when hybrid test-time scaling selects among 16 rollouts [@agentica2025deepswe].

The training environment is a subset of R2E-Gym, i.e. dockerized and executable software-engineering tasks with natural-language task descriptions, repositories, unit tests, and reward calculation by running tests [@jain2025r2egym]. DeepSWE used 4,500 of these tasks, after removing any drawn from the same repositories as SWE-Bench-Verified to avoid contamination, and each RL iteration spawned 512 Docker containers in parallel: a batch of 64 tasks with 8 rollouts each [@agentica2025deepswe].

A DeepSWE-style rollout has this shape:

1. The task is a natural-language issue against a repository at a fixed commit.
2. The model searches for relevant symbols and files.
3. The model views code and accumulates local evidence in a long context window.
4. The model edits or creates files.
5. The model executes commands or tests and observes failures.
6. The model revises the patch until it stops or hits the step limit.
7. The harness records the trajectory, output patch, exit reason, timeout state, and reward.
8. The RL trainer masks the loss for trajectories that hit the maximum context length, a 20-minute generation timeout, or the step limit, and updates the policy from the rest.

The crux here is that the harness itself shapes the policy (the Qwen model we are post-training) through the observations it returns, unique tools, valid action syntax, and timeout rules. That is to say, putting the post-trained model in an equivalent harness that only had different tool names would lead to worse results, since the tokens the model would need to generate in order to call tools would be farther out of distribution. Kimi K3's report makes the same observation: training in a single fixed harness can make a model overfit to its tool schema, system prompt, context management, and interaction protocol. Given Kimi is a model which is used across many harnesses and cannot afford to be overfit to one harness in the same sense that claude code and codex can, K3 is therefore trained across many harness configurations, including ones that mimic Claude Code and Codex [@kimiteam2026k3].
