# Reasoning model recipes

![M. C. Escher, _Morano Calabria_ (1930).](../escher/08-morano-calabria.jpg){width="80%" fig-align="center"}

## Chapter Map

- Public reasoning-model reports reveal recipe surfaces, not complete recipes.
- The recurring recipe is to keep reward variation, sampled support, verifier interfaces, exploration, and reporting discipline healthy long enough for RLVR to improve the policy.

## Why recipes matter

RLVR is not a magic phrase for "use a verifier." A verifier supplies a reward. A recipe makes that reward useful.

The recipe decides which checkpoint starts training, which prompts enter the run, how many completions are sampled, how long they can think, which auxiliary rewards are added, how aggressively the policy moves, how stragglers are handled, whether reasoning traces are distilled, and how the final capability claim is reported.

Tulu 3 states the transparency problem directly: post-training data and recipes shape model quality, and papers often omit both.[@lambert2024tulu3] That does not make public reports useless. It means the reader should treat them as partial traces of tacit post-training knowledge.

| Recipe surface | Question it answers | Public proxy to inspect |
|---|---|---|
| Starting policy | What behavior can the model already sample before RL? | Base versus instruct checkpoint, size, prior math/code/proof training |
| Task band | Which prompts create reward variation? | Offline filtering, accepted success-rate range, resampling policy |
| Rollout budget | How often does the batch contain rare correct traces? | Samples per prompt, max completion length, long-context budget |
| Update rule | How far can the policy move before exploration collapses? | KL choice, clipping rule, entropy trend, normalization rule |
| Verifier interface | What must be stabilized before correctness can train? | Format rewards, extractors, language rewards, length filters |
| Systems pipeline | Where is rollout compute wasted? | Asynchronous generation, off-policy tolerance, straggler handling |
| Lifecycle | Does RL create the final model or create training data for the next model? | Cold start, RL stage, filtered traces, distillation stage |
| Reporting | Did the policy improve, or did the surrounding system improve? | pass@1, pass@$N$, verifier reuse, contamination audit |

: Public reasoning-model reports expose recipe surfaces more often than full recipes. {#tbl-ch8-recipe-surfaces}

The useful habit is to ask what hidden engineering problem forced each surface in @tbl-ch8-recipe-surfaces.

## The lineage before R1

The reasoning-model wave did not begin from nothing. STaR bootstrapped rationales by generating reasoning traces, keeping traces that led to correct answers, and training on them.[@zelikman2022star] Quiet-STaR extended the same broad idea by letting the model generate latent thoughts before prediction.[@Zelikman2024QuietSTaRLM] TRICE treated chain-of-thought as a latent variable and trained through latent-variable inference rather than direct imitation alone.[@hoffman2023training] VinePPO moved closer to modern RL recipes by using PPO-style updates with binary correctness rewards for math reasoning.[@VinePPO]

Code and proof systems supplied another line of evidence. CodeRL, PPOCoder, and RLTF trained against executable feedback from tests.[@le2022coderl; @shojaee2023ppocoder; @liu2023rltf] DeepSeek-Prover used proof-assistant feedback in formal mathematics.[@xin2024deepseekproverv15] These systems already had the central RLVR ingredient: a checker that can score generated work without asking humans for a preference label.

DeepSeekMath, Tulu 3, o1, and DeepSeek-R1 made the recipe feel new because they connected that old ingredient to stronger base models, larger rollout budgets, and post-training systems that preserved general ability while improving reasoning.[@shao2024deepseekmath; @lambert2024tulu3; @openai2024o1; @deepseekai2025r1]

The historical lesson is narrow: R1 did not invent verifier-driven reasoning training. It showed that a verifier-driven recipe could be scaled into a broadly useful reasoning model.

## The minimal training loop

Strip away the systems work and the loop is simple:

1. Sample multiple completions for each prompt.
2. Extract the candidate answer.
3. Score the answer with a verifier.
4. Compute an advantage from the rewards in the sampled group.
5. Increase the probability of completions that scored better than the group baseline.
6. Repeat on the same or resampled task distribution.

That loop is enough to explain why RLVR can work. It is not enough to make a large run work.

The rest of this chapter is the recipe around the loop: keep prompts in the learning band, make useful traces appear in the batch, stop the policy from collapsing onto one mode, stabilize the verifier interface, and report the gain without hiding behind search.

## Keeping tasks in the competence band

A prompt teaches only when sampled completions differ in reward. If every completion fails, the verifier cannot distinguish better behavior from worse behavior. If every completion passes, the prompt no longer exerts useful pressure.

For a prompt $x$, sample $K$ completions and assign binary rewards $r_1,\ldots,r_K$. The empirical success rate is:

$$
\widehat p_x
=
\frac{1}{K}
\sum_{j=1}^{K} r_j.
$$ {#eq-ch8-empirical-success-rate}

For group-relative updates, the useful within-prompt variation is:

$$
\widehat{\mathrm{Var}}(r \mid x)
=
\widehat p_x(1-\widehat p_x).
$$ {#eq-ch8-reward-variance}

Equation @eq-ch8-reward-variance reaches zero when $\widehat p_x=0$ or $\widehat p_x=1$, and it peaks near $\widehat p_x=1/2$. This is the cleanest reason difficulty filtering matters: train on problems the current policy sometimes solves.

Offline filtering estimates this band before training. A recipe samples several completions from the starting policy, verifies them, and keeps prompts with mixed outcomes. Open-Reasoner-Zero, MiMo, Skywork-OR1, and other open reports expose variants of this filtering logic.[@hu2025openreasonerzero; @xia2025mimo; @he2025skyworkor1]

Online filtering handles the moving target. As the policy improves, yesterday's useful prompt can become too easy. Kimi k1.5, DAPO, MiMo, and OLMo 3 all make data selection, resampling, curriculum, or dynamic sampling part of the recipe rather than a detail outside the method.[@team2025kimi; @yu2025dapo; @xia2025mimo; @teamolmo2025olmo3]

The phrase "curriculum" is easy to overuse. In RLVR, the operational question is concrete: does the next batch still contain prompts whose rollouts produce different verified outcomes?

## Sampling support and thinking budgets

RLVR reinforces behavior the policy samples. A perfect verifier cannot reward a solution family absent from the rollout batch.

If a useful solution family has probability $p$ under the current policy and the trainer draws $K$ independent rollouts, the chance of seeing that family at least once is:

$$
1-(1-p)^K.
$$ {#eq-ch8-sample-support}

Equation @eq-ch8-sample-support separates two controls that are often blended together.

More parallel samples increase the chance that the batch contains a rare successful trace. Longer completion budgets let a single sampled trace spend more tokens decomposing, checking, backtracking, or using scratch work before it answers. OpenAI's o1 report explicitly framed reasoning performance as improving with both train-time RL compute and test-time thinking.[@openai2024o1] Kimi k1.5 puts long-context scaling and long rollouts near the center of its recipe.[@team2025kimi] Qwen3 exposes thinking and non-thinking modes, plus a user-facing thinking budget.[@yang2025qwen3]

The training lesson is not "longer is better." The lesson is that rollout budget creates support. If the budget never samples a useful trace, the verifier has nothing useful to reinforce. If the budget samples many long but low-value traces, the run pays for tokens without buying learning signal.

Chapter 6 treats search and test-time verification as inference procedures. Chapter 8 uses the same budget idea at train time: how much sampled behavior does the optimizer get to learn from?

## Preserving exploration during RL

A reasoning run can look successful while becoming brittle. The verifier score rises, but the policy collapses onto one style of answer, one brittle template, or one narrow solution family.

This is why public recipes discuss KL penalties, clipping rules, entropy, dynamic sampling, repeated data, and novelty pressure. These knobs do not define RLVR. They decide how quickly the policy can move away from the starting model and how much variation survives the move.

DAPO makes this layer explicit with dynamic sampling, token-level policy-gradient loss, and clipping changes.[@yu2025dapo] Skywork-OR1 treats entropy collapse as a central training problem.[@he2025skyworkor1] Open-Reasoner-Zero exposes repetition and stability issues under a lean rule-based setup.[@hu2025openreasonerzero] Work on R1-Zero-like training argues that normalization and optimization details can create length or difficulty biases that are easy to miss when only final reward is inspected.[@liu2025understanding]

The Invisible Leash gives the skeptical version of the mechanism. Wu et al. argue that RLVR can improve pass@1 while reducing answer-level diversity, meaning the policy may be redistributing probability over behavior it already had rather than expanding its support.[@wu2025invisibleleash]

The practical rule is simple: reward is not enough. A recipe also needs measurements that show whether useful alternatives still exist.

## Stabilizing the verifier interface

Auxiliary rewards are not automatically suspicious. Often they protect the interface through which correctness is measured.

| Scaffold | What it protects | Failure if omitted |
|---|---|---|
| Format reward | The extractor can find the answer | Correct work receives zero reward because parsing failed |
| Language-consistency reward | The reasoning trace stays in the intended language | The model drifts into mixed-language traces that are hard to evaluate or use |
| Length penalty or overlong filter | The run pays for useful thinking rather than unlimited verbosity | The model learns to spend tokens because the verifier does not price token cost |
| Invalid-completion filter | Broken completions do not dominate batches | The optimizer learns from parser artifacts instead of task behavior |
| Tool-use cost | External calls are rationed when tools are available | The model uses search or execution as an unpriced crutch |

: Scaffold rewards usually protect the reward interface rather than define the task. {#tbl-ch8-scaffold-rewards}

DeepSeek-R1 used accuracy rewards with format-style constraints before adding cold-start and distillation stages for readability and usability.[@deepseekai2025r1] Open-Reasoner-Zero keeps the reward interface intentionally sparse, which makes repetition and formatting failures easier to see.[@hu2025openreasonerzero] MiMo combines verifiable math and programming data with difficulty-aware data reuse.[@xia2025mimo]

The boundary is whether the scaffold supports the task reward or replaces it. A format reward is acceptable when it lets the verifier see the final answer. It becomes dangerous when the model can earn most of its reward by looking right while being wrong.

## Systems bottlenecks in long-reasoning RL

Long reasoning changes the systems problem. Completion length becomes highly variable. One prompt may finish quickly; another may consume the full context window. Synchronous batches then wait for stragglers, wasting accelerator time.

This is why large recipes care about rollout scheduling, packing, asynchronous generation, off-policy tolerance, and framework throughput. veRL and OpenRLHF are not just software conveniences; they exist because post-training runs are limited by generation, scoring, communication, and update scheduling as much as by the policy-gradient formula.[@sheng2024hybridflow; @hu2024openrlhf]

Long completions also interact with the objective. If a loss is normalized per token, per sequence, per group, or per batch, the run can put different pressure on short and long solutions. Understanding R1-Zero-like training highlights that these choices can introduce length and difficulty biases even when the reward function itself is unchanged.[@liu2025understanding]

The systems lesson is not a separate topic from capability. A recipe that wastes rollout compute sees fewer attempts, fewer rare successes, and fewer useful gradients.

## Distillation and lifecycle

Reasoning models are rarely just "RL on a base model, then ship." Public recipes often form a lifecycle:

1. Start from a capable base or instruction model.
2. Add cold-start traces or supervised reasoning data if raw RL produces unreadable behavior.
3. Run RLVR on verifiable tasks.
4. Filter the stronger model's traces.
5. Distill those traces into another model.
6. Optionally run more RL on the distilled model.

DeepSeek-R1 made this lifecycle explicit by separating pure RL, cold-start data, and distilled models.[@deepseekai2025r1] Qwen3 and OLMo 3 expose similar staged post-training patterns in different forms.[@yang2025qwen3; @teamolmo2025olmo3] OpenThoughts is useful because it focuses on data recipes for reasoning models rather than presenting RL as the only object of interest.[@guha2025openthoughts]

Distillation changes what the reader should infer. If RL produces high-quality traces and another model learns them by supervised training, the final capability may be downstream of RL without being produced by RL in the final checkpoint.

That is not a problem. It is the recipe.

## Reporting capability gains

A good reasoning report separates policy learning from search, verifier reuse, and evaluation artifacts.

A clean pass@1 policy-gain claim has this shape:

$$
\Delta_{\mathrm{policy}}
=
\mathrm{Score}_{V'}(\pi_{\mathrm{RL}}, N=1)
-
\mathrm{Score}_{V'}(\pi_{0}, N=1),
$$ {#eq-ch8-policy-gain}

where $\pi_0$ is the starting policy, $\pi_{\mathrm{RL}}$ is the trained policy, $N=1$ means no best-of-$N$ selection, and $V'$ is an evaluation verifier that does not reuse the training verifier when the task permits it.

The report should then say what happens when $N$ increases. That is a system result, not the same claim as pass@1 policy improvement. It should also state the generation budget, verifier budget, decoding setup, contamination checks, and whether the training verifier is reused at evaluation.

Tulu 3 emphasizes unseen evaluations and decontamination as part of a broad post-training report.[@lambert2024tulu3] Reasoning-or-Memorization warns that common math benchmark gains can become unreliable under contamination and recommends clean generated benchmarks plus multiple model families.[@wu2025reasoningmemorization] Invisible Leash adds a second burden: higher pass@1 can coincide with reduced answer support.[@wu2025invisibleleash]

The benchmark number is not the explanation. The recipe is the explanation.

## The compressed lesson

The public reasoning-model recipe is:

Start from a policy that can sometimes sample useful reasoning, keep prompts in the competence band, allocate enough rollout budget to expose rare successes, preserve exploration while updating, stabilize the verifier interface with narrow scaffolds, handle long-completion systems costs, and report policy gains separately from test-time search.

That sentence is the reading guide for public RLVR reasoning reports.

## Open questions

- Recipe ceilings: which choices raise the final capability ceiling, and which only save rollout compute?
- Support expansion: how should reports measure new solution families rather than probability shifts inside old support?
- Normalization: how should reports disclose length, difficulty, and loss-normalization effects?
- Lifecycle attribution: when a final model is distilled from an RL model, how much credit belongs to RL, filtering, and supervised imitation?
- Hidden teachers: how much scaffolding can a recipe add before RLVR becomes supervised learning through an auxiliary proxy?

## What comes next

Chapter 9 applies the recipe view to long-context, multimodal, and agentic RLVR. In those settings, the verifier becomes part of a harness that observes tools, files, environments, retrieved evidence, and long trajectories.
