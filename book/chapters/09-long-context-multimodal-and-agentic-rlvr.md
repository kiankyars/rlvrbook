# Long-context, multimodal, and agentic RLVR

![M. C. Escher, _Cimino Barbarano_ (1929).](../escher/09-cimino-barbarano.jpg){width="80%" fig-align="center"}

## Chapter Map

- Move from single reward functions to harnesses: the verifier now includes context selection, tools, environment state, and trajectory logs.
- Compare three frontier cases: long-context evidence rewards, multimodal search rewards, and software-agent rewards.

## From reward functions to harnesses

Long-context and tool-using settings break the clean RLVR picture from earlier chapters, where a compact GRPO script could show the whole loop because the task interface was narrow. A rollout may now include repository state, browser state, images, shell transcripts, tool arguments, observations, generated files, runtime failures, partial progress markers, and a termination decision.

Prime Intellect's Verifiers library gives a compact abstraction of an agentic environment which contains a dataset of task inputs, a model harness with tools, sandboxes, and context management, and a reward function or rubric.[@brown2025verifiers] rLLM describes the same idea from the training side: run the agent, collect traces, compute rewards, and update the model.[@tan2025rllm]

Operationally, a harness is the part of the RL loop that decides what the policy is allowed to observe, what actions it can take, what state changes get logged, and which artifacts become reward-bearing. In a math problem, this surface can be tiny: prompt in, final answer out, exact checker at the end. In long-context, multimodal, and agentic tasks, the harness becomes the task interface itself. It may log evidence spans, retrieved images, browser actions, shell output, patches, timeouts, and tool failures. It may check only a final answer, a selected evidence set, a tool trace, or a test suite. Everything outside those checks is verifier-blind.

::: {#fig-ch9-agentic-harness-stack fig-cap="An agentic RLVR harness makes the trajectory, environment state, and verifier stack part of the training interface."}

::: {.content-visible when-format="html"}
![](../diagrams/09-agentic-harness-stack.png){.light-content}

![](../diagrams/09-agentic-harness-stack-dark.png){.dark-content}
:::

::: {.content-visible when-format="pdf"}
![](../diagrams/09-agentic-harness-stack.png)
:::

:::

## Long-context QA

Long-context RLVR looks at first like ordinary answer checking with a larger prompt. The failure is that a final answer reward often cannot teach grounding. If the model reads a 100K-token context and answers incorrectly, the terminal reward says nothing about whether it failed to find the right chunk, failed to use it, or found it and reasoned badly from it.

LongRLVR makes the intermediate evidence selection reward-bearing. Before the final answer, the model emits identifiers for the context chunks it relied on. The verifier checks those identifiers against ground-truth evidence and combines that dense context reward with the final answer reward.[@chen2026longrlvr] The point is not merely to add another score. It changes the object being optimized from "eventually say the right answer" to "first localize the right evidence, then answer from it." That is still RLVR because the context reward is exactly checkable; it is process-like without relying on a learned process reward model.

The open problem is semantic synthesis. A model can select the right chunks and still overclaim, ignore qualifiers, or combine evidence incorrectly. Long-context RLVR therefore separates two problems that a final-answer checker collapses: evidence localization, which can often be verified, and faithful synthesis, which usually cannot.

## Multimodal search

Multimodal RLVR adds a different kind of harness pressure: the policy must decide when perception is enough and when it needs external search. MMSearch-R1 trains large multimodal models to use image and text search tools in multi-turn Internet environments, guided by an outcome reward plus a search penalty.[@wu2025mmsearchr1] The reward does two jobs at once. It pushes the model toward correct answers on knowledge-intensive visual questions, and it penalizes unnecessary search so the model learns on-demand tool use rather than a reflex to search every time.

This is a useful midpoint between long-context QA and software agents. The state is richer than a static prompt because the model can query external tools, but the action space is narrower than a coding harness. The verifier can often check the final VQA answer and count tool calls, yet the hard behavior is visual grounding: did the model search because the image genuinely required outside knowledge, and did the returned evidence attach to the right visual object? A scalar outcome reward can improve behavior while leaving that grounding residual mostly unmeasured.

## DeepSWE

DeepSWE is a software coding agent trained with the rLLM platform. It uses Qwen3-32B as the policy inside the harness and is trained with GRPO, resulting in 42.2% Pass@1, 71.0% Pass@16, and 59.0% when hybrid test-time scaling selects among 16 rollouts.[@agentica2025deepswe]

The training environment is a subset of R2E-Gym (an alternative to Verifiers), i.e. dockerized and executable software-engineering tasks with natural-language task descriptions, repositories, unit tests, and reward calculation by running tests; 512 parallel Docker containers are used for training.[@jain2025r2egym]

A DeepSWE-style rollout has this shape:

1. The task is a natural-language issue against a repository at a fixed commit.
2. The model searches for relevant symbols and files.
3. The model views code and accumulates local evidence in a long context window.
4. The model edits or creates files.
5. The model executes commands or tests and observes failures.
6. The model revises the patch until it stops or hits the step limit.
7. The harness records the trajectory, output patch, exit reason, timeout state, and reward.
8. The RL trainer filters unusable trajectories and updates the policy from successful or informative rollouts.

The crux here is that the harness itself shapes the policy through returned observations, tool names, action syntax, timeout rules, and the reward boundary. A model trained in one equivalent-looking coding harness has learned that harness's traces: which search results look useful, how editor actions are phrased, when command output appears, and what "submit" means. Changing only tool names or action syntax can therefore be a real distribution shift, not a cosmetic wrapper change.

Agentic coding is a concrete example of RL over long context, because the model needs to decide which parts of a repository matter, which files to inspect, which error messages to remember, and which earlier edits constrain the next action. The context acts as working memory over a changing environment. The verifier still sees the task through a narrow field of view: we can check that tests passed, but we cannot readily verify that the model understood the codebase, found the minimal fix, preserved maintainability, or avoided untested regressions.

Conventional RLVR becomes brittle in agentic settings because terminal rewards are sparse: long multi-step tasks fail at almost every attempt, and most trajectories collapse to the same zero signal.[@da2025agentrlvr] Agent-RLVR proposes guidance as a fix. Guidance is a training-time retry mechanism, not a new test-time search rule: the agent first attempts the software-engineering task, unit tests grade the trajectory, cues such as plans, error messages, and environment observations are fed back into the context, and the same task is attempted again before the gradient step. On SWE-Bench Verified, the method lifts Qwen-2.5-72B-Instruct from 9.4% to 22.4% Pass@1.[@da2025agentrlvr]

Across the three cases, the lesson is the same. Scaling RLVR beyond math and short code is less about finding one bigger reward function than about designing the harness boundary. The boundary decides which intermediate objects are visible, which are checked, which are merely logged for audit, and which remain outside the verifier's field of view.
