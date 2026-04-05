# The Verifier Lens

RLVR is about building learning systems around checkers. A model proposes answers, steps, programs, proofs, tool calls, or trajectories; a verifier inspects some exposed evidence and returns a score. Everything else follows from that interface. What can be improved depends on what can be checked. What gets rewarded depends on what the scorer can see. What breaks depends on the gap between the task and the proxy the verifier implements. We will not survey every optimization method used in modern post-training, we will focus instead on the more stable object: the verifier itself.

## Origins of RLVR

In one sense RLVR is the oldest paradigm in reinforcement learning, since it learns from direct reward rather than preference comparison, but its explicit application to large language models through verifiers is novel.

RLVR and reasoning gohandinhand, but they are different. The former is a verifier-centered method, and the later is a capabilkity: multi-step break down, search, planning, tool use, etc. The marriage between the two occurs because the most successful reasoning domains are exactly the ones with strong verifiers: math, code, proofs, some grounded QA.

I personally reflect back on the advent of reasoning models and reinforcement learning through a strange amnesia of an idea so simple with hindsight, but which took two years after ChatGPT to discover. This assessment, however, is unfair in the sense that the idea to make models think step by step long predates the 2024 reasoning-model wave.[^ch1-step-by-step] The broader prompting paradigm emerged across late 2021 and early 2022: scratchpads for intermediate computation appeared first, chain-of-thought prompting then formalized the use of intermediate reasoning traces, and the exact zero-shot prompt "Let's think step by step" was popularized a few months later.

Before the reasoning-model wave of 2024, code generation had already explored reinforcement learning against executable verifiers: CodeRL (July 5, 2022), PPOCoder (January 31, 2023), and RLTF (July 10, 2023) all trained language models using unit tests or execution feedback as objective reward signals.[^ch1-code-priors]

DeepSeekMath, published on February 5, 2024, was the first major open paper to apply this verifier-driven RL pattern to mathematical reasoning at LLM scale via GRPO.

Things heated up in September 2024, when openai published "Learning to Reason with LLMs", indicating that they had used a train-time and test-time compute strategy to enhance model reasoning through reinforcement learning in math, and coding tasks.[^ch1-openai-o1] The name "Reinforcement Learning with Verifiable Rewards" (RLVR) was coined in the Tulu 3 paper, submitted on November 22, 2024.[^ch1-deepseekmath-rlvr-name] Finally, there was Deep Seek R1, which demonstarted the the entire formula verifier-driven RL to bootstrap reasoning models.[^ch1-deepseek-r1] To quote someone describing the atmosphere at Meta after R1 launched, “Engineers are moving frantically to dissect DeepSeek and copy anything and everything we can from it.” and according to Fortune, there were war rooms assembled to understand how a Chinese lab with substanitally less resources was beating them.[^ch1-meta-reaction]

This section should eventually explain how these systems made a verifier-first vocabulary necessary. For now, the key point is narrower: once model performance started depending heavily on whether answers could be checked, reranked, filtered, or iteratively repaired, the checker stopped being implementation detail and became the central design object.

## Objective, states, and rewards

At its core, reinforcement learning optimizes the expected discounted return of trajectories in a Markov decision process
\[
\mathcal M=(\mathcal S,\mathcal A,P,R,\gamma).
\]
For a policy \(\pi\), the objective is
\[
J(\pi)=\mathbb E_{\tau\sim \pi}\!\left[\sum_{t=0}^{T-1}\gamma^{t}r(s_t,a_t)\right],
\]
where \(\tau=(s_0,a_0,s_1,a_1,\dots)\).

For **single-turn LLM inference/training with one prompt-to-completion interaction**, this collapses to a contextual bandit view: one initial state \(s_0\) (the prompt), one action \(a\) (the sampled
completion), and then termination.
\[
s_0=x,\quad a=y,\quad s_1=\text{terminal},\quad r=r_\phi(x,y).
\]
So the objective becomes
\[
J(\pi_\theta)=\mathbb E_{x\sim p_{\text{data}}}\left[\mathbb E_{y\sim \pi_\theta(\cdot\mid x)}\,r_\phi(x,y)\right].
\]

For **multi-turn settings** we retain the full trajectory form with state as dialogue/context history:
\[
s_t=(x,y_{<t}),\qquad a_t=y_t,\qquad s_{t+1}= (x,y_{\le t}).
\]
The trajectory distribution factorizes as
\[
\pi_\theta(y_{1:T}\mid x)=\prod_{t=1}^{T}\pi_\theta(y_t\mid x,y_{<t}),
\]
and the return is
\[
J(\pi_\theta)=\mathbb E_{x\sim p_{\text{data}}}\!\left[\mathbb E_{y_{1:T}\sim\pi_\theta(\cdot\mid x)}
\left[\sum_{t=1}^{T}\gamma^{t-1}r_t(s_t,y_t)\right]\right].
\]
In many verifier-driven setups, \(r_t\approx 0\) for \(t<T\) and a scalar terminal reward \(r_T=R_\phi(x,y_{1:T})\) carries the verification signal from the environment.

In this book, we use (x) for prompts and (y) for generated outputs (or turn-level outputs), and we write the verifier/environment as a score function (R_\phi) (or (r_\phi)) that maps prompts and completions (or trajectories) to reward.

## Chapter Map

This chapter is organized around three questions:

1. What is a verifier, and why is it the central design object in RLVR?
2. What makes a task verifiable, and how does that shape what RLVR can learn?
3. Why does verifier design determine the power and limits of RLVR?

**Key distinction.** "Verifiable" describes a checking regime and its evidence, not a guarantee that the reward captures everything we care about.

**Core terms.**

- **Verifier**: A procedure that maps an output or trajectory to a score using checkable evidence.
- **Evidence**: The object the verifier actually consumes, such as an answer string, execution result, proof state, citation set, tool trace, or environment transition.
- **Interface**: The part of the task exposed for checking. The verifier can only act on this interface, not on latent competence outside it.
- **Layered verification**: A setting where exact checks, approximate checks, and learned checks coexist in one stack.

## The Verifier Comes First

A verifier-first framing begins from a practical observation. If two teams use similar models and similar optimizers, but one team has a stronger checker, the team with the stronger checker often makes faster progress. It can generate more useful signal from the same rollouts, reject more junk, search more effectively at test time, and expose failure modes sooner. By contrast, a better optimizer cannot rescue a reward that is silent, brittle, or misaligned with the task.

That is why RLVR should be defined first by the checking problem. Before asking how a model is updated, we should ask four more basic questions. What object is being checked? What evidence is available? At what granularity is the check applied? How faithful is the resulting score to the competence we actually want? Those questions are stable across domains. They apply to boxed math answers, unit-tested code, formally checked proofs, citation-grounded synthesis, and agent trajectories in external environments. They also remain the same when the optimizer changes. A field organized around the verifier therefore has more conceptual shelf life than a field organized around whichever update rule is currently popular.

This framing also clarifies why RLVR is not merely "RLHF with objective labels." In many successful systems, the important design work is not replacing a human preference judgment with an automatic grade. It is redesigning the task so that useful evidence becomes checkable at all. That may require answer extraction, step instrumentation, hidden tests, proof states, structured tool traces, retrieval traces, or environment-level logging. The reward is downstream of those design choices. The verifier is where the task becomes operational.

## What Makes a Task Verifiable

A task is verifiable when it admits a checking interface strong enough to separate better trajectories from worse ones with acceptable cost and error. That definition is intentionally operational. It does not require perfect objectivity, complete observability, or a checker that never fails. It only requires that the checking regime produce enough signal to support filtering, search, or learning.

Verifiability therefore comes in degrees. Some tasks have exact final-answer checks. A symbolic math problem may reduce to extracting the final expression and comparing it to a gold target up to normalization. Some tasks have executable checks. Generated code can be run against visible and hidden tests, with the harness returning structured outcomes. Some tasks have formal checks. A proof assistant can accept or reject each proposed step against a rigid logical system. Others are weaker. A long-context question-answering task may allow support verification against retrieved passages, but only approximately, because relevance and entailment are not fully captured by citation format alone. Agentic tasks often expose environment feedback, but that feedback may be sparse, delayed, and vulnerable to loopholes in the task specification.

The important implication is that RLVR does not learn an unconstrained notion of "reasoning." It learns to do better under the available checker. Where the checker is strong, RLVR can drive striking gains. Where the checker is weak, partial, or expensive, improvement becomes narrower and more fragile. This is why math, code, and formal proof became canonical domains so quickly: not because they exhaust the meaning of reasoning, but because they provide unusually strong verification interfaces. The domain did not matter only because of its content. It mattered because it offered a reliable way to tell good from bad behavior.

## A First Taxonomy of Verifiers

The rest of the book will refine the taxonomy, but the opening chapter needs a first pass.

Outcome verifiers score completed outputs. They look at the final answer, final program, final proof artifact, or final environment result. They are attractive because they are simple and often robust, but they can be sparse and may fail to distinguish lucky success from systematic competence.

Process verifiers score intermediate reasoning or behavior. They examine steps, subgoals, proof states, traces, or partial plans. They promise denser feedback, but only when the intermediate object is itself coherent enough to check.

Executable verifiers run something. Unit tests, symbolic evaluators, tool invocations, simulators, and formal systems belong here. They are often the strongest practical checkers because they bind the model to externally grounded behavior.

Grounded verifiers inspect evidence use. They ask whether a cited passage supports a claim, whether a retrieved document was relevant, whether a tool result was used correctly, or whether a policy consulted the right state before acting.

Learned verifiers judge outputs using another model. These can extend RLVR into regimes where exact checks are unavailable, but they introduce a second learned system with its own calibration problems, biases, and attack surface.

In practice, important verifier stacks are often layered. A code task may combine syntax checks, unit tests, hidden tests, execution traces, and a learned reviewer. A long-context task may combine citation extraction, lexical grounding, entailment checks, and a judge model. The chapter-level lesson is that "the verifier" is often not a single function. It is a stack of interfaces, filters, and graders that jointly determine what the model is rewarded for.

## Why Verifier Design Determines Both Power and Limits

Verifier design determines power because it decides what useful differences the system can detect. A reward that cleanly distinguishes valid from invalid proof steps can support capabilities that a loose final-answer check cannot. A hidden test suite can force robustness that visible tests alone will not induce. A citation checker can pressure a model to expose its evidence instead of fabricating support. In each case, the checker changes the learning problem by changing which behavioral distinctions are legible.

The same design choices also determine the limits. A verifier can only reward what passes through its interface. If correctness depends on hidden reasoning quality, omitted evidence, or unobserved search choices, then a narrow checker may certify outputs that look right for the wrong reasons. If a verifier is brittle, models may learn extraction hacks rather than task competence. If the score is sparse, learning may depend more on search budget than on durable policy improvement. If the verifier is learned, the system inherits the judge's blind spots. Better optimization may intensify these effects rather than solve them.

This is the central asymmetry of RLVR. Stronger optimization amplifies the signal that the verifier provides. It does not decide whether that signal is the right one. A good optimizer applied to a bad checker is often a faster route to reward hacking.

## Verifiable Does Not Mean Complete

One of the easiest mistakes in this area is to slide from "this task has a clean checker" to "this task is solved objectively." The inference does not hold. Exactness at the verification interface is narrower than correctness in the full task.

A math checker may depend on brittle extraction rules. A code harness may miss important behaviors outside the test suite. A proof checker may validate formal derivations while saying nothing about whether the problem decomposition was insightful or reusable. A citation checker may confirm that some support was cited without proving that the answer was appropriately selective, calibrated, or faithful to the underlying evidence. Even in the cleanest settings, operational verification is a proxy.

That is not an argument against RLVR. It is an argument for precision. The right question is never simply whether a task is verifiable. The right question is what exactly is being verified, through which evidence, at what granularity, with what error profile, and against which likely exploits.

## Preview of the Book

The next chapters unpack the verifier more systematically. Chapters 2 through 4 separate outcome, process, and hybrid verification regimes. Chapter 5 asks when a checker becomes useful training signal rather than merely a post hoc filter. Chapter 6 moves to search and test-time verification, where the verifier shapes inference as much as training. Chapters 7 and 8 treat the main limitations directly: reward hacking, proxy misspecification, faithfulness, confidence, and the widening gap between what a checker certifies and what we actually want from a reasoning system. Chapters 9 and 10 ground the discussion in the domains where RLVR is strongest and in the frontier settings where verification becomes more indirect. Chapter 11 closes with the research agenda.

If the book does its job, the reader should leave this chapter with one stable mental model. RLVR is not best understood as a family of optimizers looking for tasks. It is best understood as a family of tasks and interfaces that become learnable once verification is strong enough to guide search and training.

[^ch1-step-by-step]: A useful compressed lineage runs from scratchpads in late 2021, to chain-of-thought prompting in January 2022, to the exact zero-shot prompt "Let's think step by step" in May 2022 [@nye2021show; @wei2022chain; @kojima2022zeroshot].
[^ch1-code-priors]: CodeRL was submitted on July 5, 2022 and used unit tests and a critic model to guide program synthesis [@le2022coderl]. PPOCoder was submitted on January 31, 2023 and used execution-based feedback with PPO [@shojaee2023ppocoder]. RLTF was submitted on July 10, 2023 and used online unit-test feedback of multiple granularities for code LLMs [@liu2023rltf].
[^ch1-deepseekmath-rlvr-name]: DeepSeekMath introduced GRPO and used RL to improve mathematical reasoning in an open model [@shao2024deepseekmath]. Tulu 3 later introduced the name "Reinforcement Learning with Verifiable Rewards (RLVR)" for this broader training pattern [@lambert2024tulu3].
[^ch1-openai-o1]: OpenAI's writeup states that `o1` performance improved with both more reinforcement learning, which they describe as train-time compute, and more time spent thinking at test time [@openai2024o1].
[^ch1-deepseek-r1]: DeepSeek-R1 argues that reasoning abilities can be incentivized through pure reinforcement learning on verifiable tasks such as mathematics, coding competitions, and STEM fields [@deepseekai2025r1].
[^ch1-meta-reaction]: The quoted line was reported as an anonymous Teamblind post summarized by TMTPOST, while the claim that Meta created four "war rooms" was reported by Fortune, citing The Information [@tmtpost2025deepseek; @quirozgutierrez2025warrooms].

## References

::: {#refs}
:::
