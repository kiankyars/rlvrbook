# Introduction

Reinforcement learning from verifiable rewards studies how models can improve by learning from reward signals derived from checkable task outcomes, executable feedback, formal validation, or other reliable forms of verification. This book is a reference on that paradigm. It is not organized around optimizer fashions or a timeline of papers. Its purpose is to explain what kinds of rewards can be made verifiable, what those rewards actually train, where the paradigm has been most successful, and where it breaks.

## Chapter Map

- Define RLVR as learning from verifiable reward signals and explain which tasks admit them.
- Explain why RLVR became central to reasoning models and preview the structure of the book.

**Key distinction.** "Verifiable" means that some aspect of task performance can be checked well enough to produce useful reward. It does not mean that the reward captures everything we care about.

## Origins of RLVR

In one sense RLVR is the oldest paradigm in reinforcement learning, since it learns from direct reward rather than preference comparison; what is new is its explicit application to language models through verifiers that can check answers, code, proofs, and traces.

RLVR and reasoning gohandinhand, but they are different. The former is a verifier-centered method, and the later is a capabilkity: multi-step break down, search, planning, tool use, etc. The marriage between the two occurs because the most successful reasoning domains are exactly the ones with strong verifiers: math, code, proofs, some grounded QA.

I personally reflect back on the advent of reasoning models and reinforcement learning through a strange amnesia of an idea so simple with hindsight, but which took two years after ChatGPT to discover. This assessment, however, is unfair in the sense that the idea to make models think step by step long predates the 2024 reasoning-model wave.[^ch1-step-by-step] The broader prompting paradigm emerged across late 2021 and early 2022: scratchpads for intermediate computation appeared first, chain-of-thought prompting then formalized the use of intermediate reasoning traces, and the exact zero-shot prompt "Let's think step by step" was popularized a few months later.

Before the reasoning-model wave of 2024, code generation had already explored reinforcement learning against executable verifiers: CodeRL (July 5, 2022), PPOCoder (January 31, 2023), and RLTF (July 10, 2023) all trained language models using unit tests or execution feedback as objective reward signals.[^ch1-code-priors]

DeepSeekMath, published on February 5, 2024, was the first major open paper to apply this verifier-driven RL pattern to mathematical reasoning at LLM scale via GRPO.

Things heated up in September 2024, when openai published "Learning to Reason with LLMs", indicating that they had used a train-time and test-time compute strategy to enhance model reasoning through reinforcement learning in math, and coding tasks.[^ch1-openai-o1] The name "Reinforcement Learning with Verifiable Rewards" (RLVR) was coined in the Tulu 3 paper, submitted on November 22, 2024.[^ch1-deepseekmath-rlvr-name] Finally, there was Deep Seek R1, which demonstarted the the entire formula verifier-driven RL to bootstrap reasoning models.[^ch1-deepseek-r1] To quote someone describing the atmosphere at Meta after R1 launched, “Engineers are moving frantically to dissect DeepSeek and copy anything and everything we can from it.” and according to Fortune, there were war rooms assembled to understand how a Chinese lab with substanitally less resources was beating them.[^ch1-meta-reaction]

The above trend is that model improvement increasingly depended on checkable interfaces.

## Objective, States, and Rewards

At its core, reinforcement learning optimizes the expected discounted return of trajectories in a Markov decision process:

$$
\mathcal M=(\mathcal S,\mathcal A,P,R,\gamma).
$$

For a policy $\pi$, the objective is:

$$
J(\pi)=\mathbb E_{\tau\sim \pi}\!\left[\sum_{t=0}^{T-1}\gamma^{t}r(s_t,a_t)\right].
$$

where $\tau=(s_0,a_0,s_1,a_1,\dots)$.

For **single-turn LLM inference/training with one prompt-to-completion interaction**, this collapses to a contextual bandit view: one initial state $s_0$ (the prompt), one action $a$ (the sampled
completion), and then termination:

$$
s_0=x,\quad a=y,\quad s_1=\text{terminal},\quad r=r_\phi(x,y).
$$

So the objective becomes:

$$
J(\pi_\theta)=\mathbb E_{x\sim p_{\text{data}}}\left[\mathbb E_{y\sim \pi_\theta(\cdot\mid x)}\,r_\phi(x,y)\right].
$$

For **multi-turn settings** we retain the full trajectory form with state as dialogue/context history:

$$
s_t=(x,y_{<t}),\qquad a_t=y_t,\qquad s_{t+1}= (x,y_{\le t}).
$$

The trajectory distribution factorizes as:

$$
\pi_\theta(y_{1:T}\mid x)=\prod_{t=1}^{T}\pi_\theta(y_t\mid x,y_{<t}),
$$

and the return is:

$$
J(\pi_\theta)=\mathbb E_{x\sim p_{\text{data}}}\!\left[\mathbb E_{y_{1:T}\sim\pi_\theta(\cdot\mid x)}
\left[\sum_{t=1}^{T}\gamma^{t-1}r_t(s_t,y_t)\right]\right].
$$
In many verifier-driven setups, $r_t\approx 0$ for $t<T$ and a scalar terminal reward $r_T=R_\phi(x,y_{1:T})$ carries the verification signal from the environment.

In this book, we use (x) for prompts and (y) for generated outputs (or turn-level outputs), and we write the verifier/environment as a score function (R_\phi) (or (r_\phi)) that maps prompts and completions (or trajectories) to reward.

## What RLVR Is

RLVR is reinforcement learning on tasks where the reward does not need to be guessed from preference comparisons alone because some meaningful part of correctness can be checked directly. Sometimes that check is exact, as in symbolic math or formal proof. Sometimes it is executable, as in code generation with tests. Sometimes it is partial, as in grounded question answering or tool-using agents where only some parts of the trajectory can be reliably scored. The unifying idea is not a specific optimizer. It is the availability of a reward channel tied to some checkable notion of task success.

This is why RLVR should not be reduced to "RLHF but more objective," nor to a single algorithm such as PPO or GRPO. It is a broader learning setup. Once a task can expose useful correctness signals, reinforcement learning can optimize against them, search can exploit them at inference time, and systems can often improve far beyond what static supervised fine-tuning alone would produce.

## What Kinds of Tasks Admit Verifiable Rewards

Tasks admit verifiable rewards when they expose an interface that can separate better behavior from worse behavior at acceptable cost. The strongest cases are the familiar ones. Math problems often allow answer checking up to normalization. Code can be run against visible and hidden tests. Formal proof systems can accept or reject proof states under explicit rules. These domains became central not because they exhaust the meaning of reasoning, but because they expose unusually clean signals.

Other tasks are weaker but still useful. Long-context question answering may permit citation checks, evidence matching, or entailment-style grading. Tool-using agents may expose environment transitions, task completion criteria, or execution traces. These signals are often noisier, more expensive, and easier to exploit, but they can still support learning if the reward channel is informative enough.

The practical lesson is that RLVR does not apply uniformly across all tasks. It is strongest where correctness is legible and weakest where the reward channel is sparse, ambiguous, or only loosely coupled to the capability we actually want.

## Why RLVR Became Central to Reasoning Models

RLVR matters so much now because many of the tasks that most visibly stress reasoning also admit unusually strong reward signals. Mathematical problem solving, code synthesis, and formal proof all reward multi-step behavior, yet all expose interfaces that allow the system to tell success from failure with relatively high confidence. That combination is rare. It means the same domains that demand search, decomposition, and iterative refinement are also the domains where reinforcement learning has the cleanest chance to work.

This is also why RLVR and reasoning are easy to conflate. They are not the same concept. Reasoning is a capability family; RLVR is a training paradigm. But in current LLM practice, the overlap is large because verifier-friendly domains have been the best places to scale reasoning performance. The result is that some of the most important progress in reasoning models has come from learning against verifiable rewards rather than from preference optimization alone.

## Verifiable Does Not Mean Complete

Even strong reward signals remain proxies. A clean checker is not the same thing as complete task understanding. A math reward may depend on brittle extraction. A code harness may miss behaviors outside the test suite. A proof system may validate a derivation without telling us whether the model's decomposition was insightful or robust. A grounded QA reward may verify some citations without guaranteeing that the answer used evidence faithfully.

That is not a criticism of RLVR so much as a statement of its operating conditions. The important questions are always: what is being checked, what is being missed, how expensive the check is, and how easily the signal can be gamed. Much of the rest of the book is about that gap between a usable reward signal and the fuller competence we actually want.

## What This Book Covers

The next chapters move from the general paradigm to the main reward regimes in practice. Chapters 2 through 4 cover outcome rewards, process rewards, and learned or hybrid verification pipelines. Chapter 5 asks when a check becomes useful learning signal rather than merely a filter. Chapter 6 turns to search and test-time verification, since RLVR in modern systems is inseparable from inference-time compute. Chapters 7 and 8 focus on the main failure modes: reward hacking, proxy misspecification, faithfulness, confidence, and the limits of what verification can certify. Chapters 9 and 10 compare the paradigm across its strongest and most difficult domains. Chapter 11 closes with the open problems.

[^ch1-step-by-step]: A useful compressed lineage runs from scratchpads in late 2021, to chain-of-thought prompting in January 2022, to the exact zero-shot prompt "Let's think step by step" in May 2022 [@nye2021show; @wei2022chain; @kojima2022zeroshot].
[^ch1-code-priors]: CodeRL was submitted on July 5, 2022 and used unit tests and a critic model to guide program synthesis [@le2022coderl]. PPOCoder was submitted on January 31, 2023 and used execution-based feedback with PPO [@shojaee2023ppocoder]. RLTF was submitted on July 10, 2023 and used online unit-test feedback of multiple granularities for code LLMs [@liu2023rltf].
[^ch1-deepseekmath-rlvr-name]: DeepSeekMath introduced GRPO and used RL to improve mathematical reasoning in an open model [@shao2024deepseekmath]. Tulu 3 later introduced the name "Reinforcement Learning with Verifiable Rewards (RLVR)" for this broader training pattern [@lambert2024tulu3].
[^ch1-openai-o1]: OpenAI's writeup states that `o1` performance improved with both more reinforcement learning, which they describe as train-time compute, and more time spent thinking at test time [@openai2024o1].
[^ch1-deepseek-r1]: DeepSeek-R1 argues that reasoning abilities can be incentivized through pure reinforcement learning on verifiable tasks such as mathematics, coding competitions, and STEM fields [@deepseekai2025r1].
[^ch1-meta-reaction]: The quoted line was reported as an anonymous Teamblind post summarized by TMTPOST, while the claim that Meta created four "war rooms" was reported by Fortune, citing The Information [@tmtpost2025deepseek; @quirozgutierrez2025warrooms].

## References

::: {#refs}
:::
