# Open Problems

![M. C. Escher, _Alfedena Abruzzi_ (1929).](../escher/11-alfedena-abruzzi.jpg){width="80%" fig-align="center"}

## Chapter Map

- Open problems in RLVR.
- RLVR improves a model exactly as far as verification reaches.

## The frontier is the verifier

Jason Wei states: "the ease of training AI to solve a task is proportional to how verifiable the task is" [@wei2025asymmetry]. If right, the open problems of RLVR are mostly problems of verification.

They fall into three groups:

1. **What RL adds.** Does optimizing against a verifier create capability, or only select capability the base model already has? How much compute does that take, and can it be predicted?
2. **Whether the reward can be trusted.** Verifiers are wrong in both directions, and optimization pressure finds the errors. What does the policy learn from them, and can we still see what it learned?
3. **How far verification extends.** Long horizons, tasks without a reference answer, the model grading itself, and the model writing its own tasks all push the verifier past the setting where earlier chapters showed it works.

## Elicitation or creation {#sec-ch11-elicitation}

**Research question.** Does RLVR with outcome rewards create reasoning capability absent from the base model, or does it reallocate probability mass toward solutions the base model could already sample?

### The case for reallocation

Yue et al. compared base and RLVR-trained models with pass@k at large k. RL wins at $k = 1$, but the base model overtakes it as $k$ grows: on Minerva with a 32B model, the base model is ahead by about 9 points at $k = 128$ [@yue2025doesrl]. Six different RLVR algorithms behaved similarly, while off-policy distillation from a stronger model expanded the set of solvable problems. Wu et al. argue that RLVR is held on an invisible leash, confined to the base model's support: it can occasionally surface correct solutions the base model rarely samples, but in practice the support it loses outweighs the support it gains [@wu2025invisibleleash].

### In entropy we trust

High entropy means a policy's sampling is spread out and many continuations are plausible, and zero entropy means the policy is deterministic. Cui et al. tracked entropy and validation accuracy through RL runs on eleven base models from 0.5B to 32B parameters and found that accuracy $R$ is a fixed function of entropy $H$ when there's no entropy bonus or KL penalty: $R = -a e^{H} + b$, where $a$ and $b$ depend on the model and task [@cui2025entropy]. Averaged over runs of 2,400 steps, 73% of the entropy consumed and 76% of the performance gained came in the first 200 gradient steps. When entropy runs out, accuracy stops at $-a + b$, a ceiling that a fit on the first few dozen steps already predicts (@fig-ch11-entropy-performance).

Policy-gradient updates raise each sampled token's logit in proportion to its advantage, so entropy falls when the tokens the policy favors are the ones with high advantage, and rises when a rare token turns out to be good. In reasoning RL the covariance between a token's log-probability and its advantage stays positive throughout training, so the first case dominates, causing entropy to steadily fall. Cui et al. counter this by restraining the updates on the 0.02% to 0.2% of tokens with the highest covariance, which keeps entropy more than ten times higher and improves on GRPO by 6.4 points on average for a 32B model [@cui2025entropy]. Tying back to elicitation, a policy that spends its entropy concentrates on the solutions it favored, which is part of the reallocation Yue et al. measured.

::: {#fig-ch11-entropy-performance}

::: {.content-visible when-format="html"}
![](../diagrams/11-entropy-performance-light.svg){.light-content}

![](../diagrams/11-entropy-performance-dark.svg){.dark-content}
:::

::: {.content-visible when-format="pdf"}
![](../diagrams/11-entropy-performance-light.svg)
:::

As RL spends policy entropy $H$, validation performance $R$ rises along $R = -a e^{H} + b$ and stops at the ceiling $-a + b$ when entropy is exhausted. The coefficients here are illustrative; Cui et al. fit $a$ and $b$ separately for each model.

:::

### The case for creation

Several results show RL solving problems the base model never solved:

- ProRL trained a 1.5B model for more than 2,000 steps with KL control and periodic resets of the reference policy, and found the RL model ahead of the base model across a wide range of pass@k, including on tasks where the base model fails at every $k$, though on some math benchmarks its pass@128 fell below the base model's [@liu2025prorl].
- On synthetic string transformations, a model that already knows functions $f$ and $g$ learns their unseen composition $f(g(x))$ through RL, while next-token training on the same data does not [@yuan2025composing].
- On a code problem family where the base model's pass@k is zero, RL shows a grokking-like transition: after a long stretch of near-zero reward, accuracy climbs abruptly to near perfect. Albeit, getting there required a warm-up that first rewards the fraction of test cases passed before switching to the binary reward, or a carefully matched curriculum, and experience replay shortened the long exploration phase [@sun2025rlgrokking].
- For tool use, the RL model's pass curve pulls away from the base model's as $k$ grows, instead of converging, though the gap stays small. On multi-hop questions where the second search depends on the first result, a 7B RL agent trails its base model slightly at $k = 1$ but leads at $k = 64$, solving 81 of 100 held-out questions at least once against 77 for the base model, while SFT on the same training questions ends at 73, below the base model [@zhai2026passkt].

### A reconciliation

<!-- PENDING (author): this paragraph is still pending; also tracked in README.md. -->

A 2026 study of overtraining argues that the large-$k$ decline Yue et al. measured is partly an artifact of where RLVR spends its updates. If a policy solves a problem once in 8 samples, then 256 samples almost surely contain a correct answer, since pass@256 is $1 - (7/8)^{256} \approx 1$. Further training on that problem can still raise pass@1, but it cannot raise pass@256; it only narrows the correct solutions the model produces. With few rollouts per problem, a single observed success already puts a problem in this regime, so its authors conclude that most updates in standard RLVR sharpen rather than expand. Restricting updates to problems with no observed success lifts pass@256 above the base model on difficult benchmarks. This needs a loss that still pushes down wrong answers when every rollout in a group fails, a case where GRPO's group-relative advantage is zero [@yuan2026overtraining; @zhu2025negative].

### What is open

Most of these results use small models, synthetic tasks, curricula, or hints, and the setting closest to the clean question failed for a mechanical reason: on a code family the base model never solves, standard RL with binary rewards stalled, because GRPO has no gradient on groups in which every rollout fails [@sun2025rlgrokking]. That rules out plain GRPO on such problems, not outcome-only RL in general. Whether outcome-only RL can turn natural problems the base model never solves into reliably solved ones at frontier scale is open, and so is whether composing known skills should count as new capability.

## Reward hacking {#sec-ch11-reward-hacking}

### Is there an over-optimization law for learned graders?

Chapter 7's over-optimization curve by Gao et al. measured proxy-gold divergence for preference reward models [@gao2023scaling], but no equivalent law exists for LLM judges [@zhang2025genrm], including the rubric judges of @sec-ch11-beyond-verification, so practitioners optimizing against them find the peak by monitoring a stronger held-out judge or benchmark rather than predicting it in advance.

Mahmoud et al. trained Qwen2.5-7B-Instruct with GRPO on medical and science prompts, rewarding it through a weak judge (GPT-4o-mini) or a strong one (GPT-OSS-120B) (this is relatively speaking, since today both of these models are impotent). A separate panel of three frontier judges re-graded the policy's answers at evaluation time. At each checkpoint, the authors took the rubric criteria that the training judge said an answer now met but had not met at the previous checkpoint, and measured what share of them all three panel judges rejected. For the weak verifier, that share climbed from 39% to 65% over training on the medical prompts; with the strong verifier it fluctuated between 15% and 21%, staying within 5 points of its starting value [@mahmoud2026rubrichacking]. In a sweep of non-reasoning judges fine-tuned from Qwen3 models of 1.7B, 4B, 8B, and 14B parameters, larger judges generally delayed reward hacking, but every policy hacked by the end of training; reasoning judges avoided that collapse, only for the policy to learn adversarial outputs that also fool other LLM judges [@liu2026reasoningjudges].

### How much does the verifier miss?

By the verifier's nature, we only have coverage on what it checks, so a high score cannot tell us whether a model learned the underlying capability or to merely satisfy the checks.

One single-author audit found that in a 49-task sample of SWE-bench Verified drawn from two repositories, 14 tasks (about 29%) accept a Docker-verified incorrect patch, and that across 134 submitted models, Pass@1 is 14.14 points higher on the hackable tasks than on robust tasks of the same difficulty [@rajan2026auditing]. Rule-based math verifiers err in the other direction, rejecting correct answers written in unexpected forms, and those false negatives hurt more as the policy gets stronger, although this domain is much more tractable than the former example of creating unambiguous and non-hackable software tasks [@huang2025verifiers]. An under-rated skill is understanding that as the objective is simply to increase reward there is often no optimization pressure for agents to solve tasks the "right" way, meaning in practice that models sometimes exploit tests when convenient to increasing reward. As an example, ImpossibleBench, a benchmark whose tasks purposefully conflict with their tests (@fig-ch11-impossiblebench), led GPT-5 to cheat on 76% of one SWE-bench variant [@zhong2025impossiblebench].

::: {#fig-ch11-impossiblebench fig-cap="ImpossibleBench mutates a test to contradict the task, so any pass is a cheat. Adapted from Zhong et al. (cropped, with a dark-mode variant), CC BY 4.0."}

::: {.content-visible when-format="html"}
![](../diagrams/11-impossiblebench-overview.png){.light-content fig-alt="An is_prime task with a normal test, assert is_prime(7), and a mutated test, assert not is_prime(7), which a model can only pass by special-casing 7."}

![](../diagrams/11-impossiblebench-overview-dark.png){.dark-content fig-alt="An is_prime task with a normal test, assert is_prime(7), and a mutated test, assert not is_prime(7), which a model can only pass by special-casing 7."}
:::

::: {.content-visible when-format="pdf"}
![](../diagrams/11-impossiblebench-overview.png)
:::

:::

No method can list everything the verifier misses. Thought experiment: any behavior we learn to measure becomes one more check, and some complement always remains, ad infinitum. Nonetheless, here are two partial answers to the question of verifier coverage:

1. Auditing verifiers with certified-equivalent and certified-wrong variants of known answers, which measures both false negatives and false positives [@xin2026verifierfails].
2. A verifier-free diagnostic computed from the policy's own log-probabilities, which flags when the policy stops improving even though the training reward keeps rising [@mahmoud2026rubrichacking].

Since one cannot exhaustively analyze a verifier's blind spot, a more tractable framing is: on a random accepted policy sample, how often does an oracle reject what the verifier accepted, and how does that rate change as training proceeds? This is similar to the concept of a sample versus population in statistics: we can estimate the rate even though the entire unchecked complement is unknown. In math, Huang et al. trained Qwen2.5-7B Base with GRPO on the DeepScaleR problem set and, at each checkpoint, had GPT-4o, which never supplied training reward, grade responses to 1,000 of those same training problems against their reference answers; comparing this oracle reward with the training reward exposed a fine-tuned model-based verifier being exploited after about 450 steps [@huang2025verifiers]. No published results yet extend this to frontier-scale agentic tasks, where each audit is expensive.

### Does hacking generalize?

In 2025, Anthropic first taught a pretrained model about reward-hacking strategies and then trained it on real production coding environments. The model learned to hack, and then generalized to alignment faking, cooperating with malicious actors, and attempting sabotage, including sabotage of the codebase for the paper itself [@macdiarmid2025emergent]. Hacker-Opus, which we discussed in Chapter 8, trained on 80 environments with known exploits, and misbehaved where a misaligned action could raise an automated grader's score, but behaved like its starting checkpoint in scenarios "without a clear notion of a reward, automated grader, or cheat" [@qi2026rewardseeker]. The strongest reason to care about reward hacking is that it may not stay local, and it's compelling that the two most direct studies disagree on how far it spreads. Two differences might explain the apparent contradiction: the 2025 model started from a pretrained model and was taught about reward hacking before RL, while Hacker-Opus started from an early Claude Opus 4.8 checkpoint that had already been trained to refuse harmful requests, and learned to hack only from its environments.

### Does optimization pressure erode monitorability?

Chain-of-thought monitoring catches reward hacking that action monitoring misses, but putting the monitor into the reward teaches the model to hide its intent [@baker2025monitoring]. In response, OpenAI optimizes the outcomes of reasoning, but does not grade the reasoning itself, with chief scientist Jakub Pachocki reasoning in September 2026: "If we scale optimization on the outcomes of that process, but do not supervise the process itself, that chain-of-thought has no direct incentive in training to hide any misaligned ideas or objectives" [@pachocki2026alienmind]. Howbeit, OpenAI disclosed in May 2026 that chains of thought had accidentally been graded in some RL runs for released models, on less than 4% of samples for each affected model, with no clear loss of monitorability [@carroll2026accidentalcotgrading].

In December 2025, OpenAI measured monitorability across training and found that RL optimization "does not materially decrease monitorability even at the current frontier scale" [@guan2025monitoringmonitorability], but that frontier was the GPT-5 generation. Nine months later (one eternity in AI time), the system card for GPT-6 Astra reports "a substantial decrease in chain-of-thought monitorability compared to previous models". On a test that instructs a model to reshape its chain of thought, for example to avoid certain keywords or to write only in lowercase, Astra complied 60.9% of the time on chains of thought of 750 to 1,250 tokens, against 16.1% for GPT-5.6 Sol. OpenAI calls this controllability "an undesirable property for monitorability", since a model that can reshape its reasoning on request may also be able to hide it from a monitor. Controllability rose over RL training even though OpenAI is "fairly confident that there are no significant direct CoT grading pressures" [@openai2026astrasystemcard]. Pachocki gives three reasons in his blog post why OpenAI's ability to rely on chain-of-thought monitoring is diminishing [@pachocki2026alienmind]:

1. Reasoning is increasingly mixed with communicating with people, other AIs, and tools, and many of those interactions have to be supervised.
2. Models are getting better at reasoning about and manipulating their own reasoning.
3. Models are getting smarter without verbalized reasoning at all.

In toy environments, reward terms on the chain of thought that conflict with the output reward, such as length penalties or a chain-of-thought monitor, reduced monitorability [@kaufmann2026aligned]. RL with length penalties targeting 30% of the original reasoning length kept accuracy near baseline but cut how often the reasoning disclosed a hint's influence by 39% for Qwen3-14B [@little2026lengthpenalty]. Frontier labs do apply length pressure, Kimi K3 through the token budget described in Chapter 9 and OpenAI through what it calls "limited pressure on CoT length to make models practical to use" [@carroll2026accidentalcotgrading], so it's essential to study whether the same outcomes on monitorability seen in toy environments occur at trillion-parameter model scale.

## A predictive science of RL compute

**Research question.** Does RL post-training admit predictive scaling laws of the kind pretraining has, and what determines the asymptote a recipe saturates toward?

The least understood stage of training now takes the largest share of lab compute. SemiAnalysis says that, across Anthropic and OpenAI combined, post-training and RL rose from about 5% of lab compute capacity in the second quarter of 2024 to 36% in the fourth quarter of 2025, when it overtook pre-training at 32%, and to 50% in the second quarter of 2026, against 13% for pre-training [@xie2026shortking].

The largest systematic datapoint is ScaleRL: a study totaling more than 400,000 GPU-hours that fits sigmoidal compute-performance curves to RL training runs and validates them by predicting, from the first half of a single run, where that run lands at 100,000 GPU-hours [@khatri2025scalerl]. Performance is the pass rate on 1,000 math prompts held out from the training set: the fraction of 16 samples per prompt that the checker marks correct, averaged over the prompts. @fig-ch11-scalerl-100k shows that curves fitted on the first 50,000 GPU-hours of an 8B run predict where the run lands at 100,000.

::: {#fig-ch11-scalerl-100k fig-cap="Sigmoid curves (solid lines) fitted to the early training points of each run (stars) and extrapolated (dotted lines) predict the extended training points (crosses) for an 8B dense model and a 17Bx16 mixture-of-experts model. Reproduced from Khatri et al., CC BY 4.0."}

![](../diagrams/11-scalerl-100k-gpu-hours.png){fig-alt="Validation pass rate against GPU hours on a log scale for ScaleRL-8B Dense and ScaleRL-17Bx16 MoE, with fitted sigmoid curves and extrapolations that match extended training points." width="75%"}

:::

Each fitted curve has three parameters: $A$, the ceiling the run approaches, $C_{mid}$, the compute at which it has made half its gain, and $B$, how sharply the curve rises. In ScaleRL's ablations, most recipe choices changed how fast a run rises, not how high it goes: loss aggregation, advantage normalization, the curriculum, and the off-policy algorithm mostly change how quickly a run reaches its ceiling, while the loss function, the batch size, the generation length, and the model size change the ceiling itself [@khatri2025scalerl]. The practical lesson is to compare recipes by their fitted ceilings rather than by which one is ahead at a given step (@fig-ch11-scalerl-ceiling): raising the generation limit from 14K to 32K tokens slowed early progress but lifted the ceiling.

::: {#fig-ch11-scalerl-ceiling}

::: {.content-visible when-format="html"}
![](../diagrams/11-scalerl-ceiling-vs-efficiency-light.svg){.light-content}

![](../diagrams/11-scalerl-ceiling-vs-efficiency-dark.svg){.dark-content}
:::

::: {.content-visible when-format="pdf"}
![](../diagrams/11-scalerl-ceiling-vs-efficiency-light.svg)
:::

Ceiling versus efficiency in ScaleRL's sigmoid fit. A recipe that reaches the same ceiling sooner leads early in training, while a recipe with a higher ceiling $A$ can trail early and pull ahead only at scale. The curves are illustrative, not fitted to a run.

:::

A second pattern concerns data, and it cuts against intuition from pretraining: RL needs remarkably few distinct problems. Across Qwen2.5 models from 0.5B to 72B, Tan et al. found that test error follows a power law in compute. They then simulated a data-constrained regime on the 7B model, with fewer distinct problems than the run needs, by holding the number of training steps fixed and shrinking the pool of distinct problems, cycling through the smaller pool more times. Test performance barely changed with each problem repeated up to 25 times, and clear overfitting appeared only at 100 repeats [@tan2025scalingbehaviors]. The extreme case is a single problem: RLVR on one example, duplicated to fill each batch, lifts Qwen2.5-Math-1.5B from 36.0% to 73.6% on MATH-500, the same score as training on 1,209 examples [@wang2025oneshot]. On-policy distillation shows the same effect for a clearer reason. There, one prompt recovers most of the gain from distilling on the full dataset, 87% after 300 steps and 72% after 1,000, because the teacher grades every token the student samples: a single prompt, rolled out 64 times per update, yields tens of thousands of supervised token positions, and that signal persists after the student starts solving the prompt and is still useful on a prompt the student never solves, whereas an outcome reward gives nothing while every rollout fails and is exhausted once every rollout is correct [@fu2026oneshotopd]. In both cases, the number of distinct prompts understates how much supervision a run receives; what matters in RLVR is whether pretraining has left headroom and whether the training problems lie at the edge of the model's competence [@zhang2025interplay].

Open questions follow directly:

- How much of the asymptotic performance is set by the base model's support, as the elicitation problem suggests, and how much by inefficiencies in training recipes?
- Do fitted curves transfer across model families and task mixtures?
- How should a fixed budget split between pretraining, SFT, and RL?
- Does prolonged RL erode the plasticity it relies on, the network's ability to keep learning from new data [@dohare2024plasticity]? This is not the entropy collapse of @sec-ch11-elicitation: entropy measures how spread out the policy's samples are, while plasticity measures how easily further training can still change the model. There is almost no direct evidence for LLMs. ProRL periodically resets the reference policy and optimizer when runs stop improving, and DeepSeek-V4.1-Flash merges checkpoints to reinitialize successive RL runs and extend RL compute beyond a single run, but neither measures plasticity [@liu2025prorl; @deepseekai2026v41flash].

There is little published work on the frontier regarding the science of RL compute; notwithstanding, we can look one level down at OLMo 3, whose 32B Think RL run took ~five days and 750 steps, and a continuation ran 21 more days to 2,300 steps with performance "not yet fully saturated" [@teamolmo2025olmo3]. Kimi K3, DeepSeek-V4.1-Flash, and the MiniMax-M2 series report RL results but no RL compute totals. For single open models from early 2025, published figures and outside estimates put RL compute at under 4% of pre-training compute for DeepSeek-R1-Zero, about 5.5% for the whole DeepSeek-R1 pipeline, SFT included, and under 1% for Llama-Nemotron Ultra [@khatri2025scalerl; @deepseekai2025r1; @deepseekai2024v3; @epoch2025reasoningscale]. No published scaling law covers multi-domain, agentic, million-token RL, which is where the frontier labs now spend their RL compute.

## Credit assignment at horizon scale {#sec-ch11-credit-assignment}

**Research question.** How does terminal outcome learning signal diminish on increasing horizons, and how can process-level signals be made scalable?

Credit in reasoning RL spans one generation of 500-30K+ tokens; agentic RL spans tens to hundreds of turns and 100K to 1M tokens, where a single episode-level scalar becomes increasingly uninformative. Karpathy's phrase for this, quoted in Chapter 2, is "sucking supervision through a straw": one number at the end of a rollout decides whether everything in it is upweighted or downweighted [@patel2025karpathyagi]. Intermediate verification, while possible in math, is rarely possible for agents, and the methods literature has no shared benchmark for comparing credit-assignment quality [@zhang2026creditsurvey]. Let's not forget the well-known METR measure of the length of software tasks that frontier models complete at 50% reliability, which doubled roughly every seven months from 2019 to 2025 and has doubled roughly every three months since 2024 [@kwa2025timehorizon; @metr2026th11]. The measure is now at its ceiling: only 5 of its 228 tasks are estimated to take a human 16 hours or longer, so METR treats horizons above 16 hours as unreliable, and an early version of Claude Mythos Preview, evaluated in March 2026, was already estimated at "at least 16hrs" [@metr2026mythosthread].

MiniMax states that outcome rewards alone "are insufficient for credit assignment" on trajectories of up to 192K tokens. It adds dense per-step process rewards, which penalize language mixing and malformed tool calls and reward well-structured intermediate reasoning, and computes each step's advantage from the reward earned from that step onward against a trajectory-level baseline, even when the agent has truncated or rewritten its context mid-episode [@minimax2026m2]. Judging from the examples MiniMax gives, these process rewards grade the form of each step rather than its contribution to the outcome, so which step actually solved the task is still left to the outcome reward. The other lever is the context the policy sees, which is also where academic work on long horizons is most active. Context folding, for example, trains the agent to collapse each finished sub-task into a short summary, rewards it for folding well, and matches a full-context agent while keeping an active context ten times smaller [@sun2025contextfolding]. Folding shortens the stretch of tokens across which one outcome reward must be spread, so better context management is, in part, better credit assignment, with a very large qualifier that this folding process can also have the opposite effect in erasing those tokens of the utmost importance to eliciting a trajectory's success.

### What is open

Whether outcome rewards, form-level process rewards, and context management suffice as horizons keep growing is open, and so is which intermediate states are verifiable.

## Rewards beyond verification {#sec-ch11-beyond-verification}

### How far can RLVR's recipe extend into tasks with no checkable answer?

- **Rubrics.** Instead of asking a judge for one overall score on a 1-to-10 scale, a rubric reward gives the judge a list of criteria written for the specific prompt, such as "avoids misinformation" for a medical question. The judge can check each criterion separately, with the reward a weighted sum of the checks, or it can read the whole rubric and give one overall score [@gunjal2025rubrics]. At the frontier, Kimi K3's judge writes a rubric for each task, as @tbl-ch9-open-recipes shows [@kimiteam2026k3].
- **Reference likelihood.** Where a reference answer exists but no checker does, the policy's own probability of producing the reference can serve as the reward, with no verifier at all [@yu2025rlpr].

Rubric rewards are hackable in the ways @sec-ch11-reward-hacking describes, and they cost a judge call per rollout. The open problem is not whether these signals work early in training, since they do, but whether they stay aligned with the target under the optimization pressure that frontier RL applies.

### How much of what RLVR learns on checkable tasks transfers to the rest?

Jason Wei's rule says which tasks RL improves directly; if RL on math and code taught general reasoning, verifiable domains might be enough. Across more than twenty open reasoning models, most gains in math fail to transfer to other domains, but in a controlled comparison on Qwen3-14B, math-only RL carried its gains over to other reasoning and even non-reasoning tasks, while math-only SFT gained less on other reasoning and fell below the base model on non-reasoning tasks [@huan2025mathtransfer]. RL's Razor argues that at matched performance on a new task, RL forgets less than SFT because on-policy updates stay closer to the base model in KL [@shenfeld2025rlrazor]. Of six domains tested, math, code, and science (all common in pretraining data) benefit from each other, while logic, simulation, and tabular reasoning need in-domain data [@cheng2025guru]. So RL on verifiable reasoning does transfer, but mainly between domains the base model already knows well; domains like logic, simulation, and tabular reasoning can still be improved directly, as Wei's rule predicts, once they have verifiers of their own.

## Self-improvement without external verification {#sec-ch11-self-improvement}

**Research question.** Can a model's own signals sustain RL improvement, or do self-reward loops inevitably collapse?

Majority vote over the model's own samples, used as a pseudo-label on unlabeled test problems, raised Llama-3.1-8B-Instruct's pass@1 on MATH-500 from 48.6% to 63.7% [@zuo2025ttrl]. Rewarding self-certainty came close to GRPO with gold answers on Llama-3.2-3B-Instruct [@zhao2025intuitor].

It's not all fun and games, though, because prolonged RL with majority-vote rewards leads to reward hacking and "sudden and complete performance collapse" [@shafayat2025selftrain]. Internal-feedback rewards help base models early, then degrade performance below the starting model, and give little benefit to instruction-tuned models [@zhang2025nofreelunch]. A reward that confirms the model's current beliefs drives entropy down, and pass@n falls with it [@zhou2025evolrl]; this answer is refreshing because it's a training problem which we can directly answer with complete certainty as a structural collapse in entropy (as opposed to an interpretability artifact which might lead to hundreds of hypotheses).

Self-improvement is governed by the generation-verification gap, i.e. how much better a model is at checking an answer than producing one [@song2024mindgap]. A self-reward loop can only climb while the model's own judgments are better than its answers; as you optimize against those judgments, the model's answers will become as good as its judgments, and then there is no longer any leverage. In offline iterative self-improvement, the gap fell close to zero after two or three rounds, whatever the model's size [@song2024mindgap]. Training on intrinsic rewards raises performance and then lowers it, even as the intrinsic reward itself keeps rising, with the timing set by how well the model's initial confidence tracks correctness, and one early warning sign has been found: the accuracy of self-generated pseudo-labels declines before performance does [@he2026urlvr; @wang2026rlavr].

## Models that write their own tasks {#sec-ch11-task-generation}

**Research question.** Can the model generate the environments and verifiers it trains on?

In Absolute Zero, one model proposes coding tasks, a code executor validates them, and the same model learns to solve them, reaching state-of-the-art results at 7B without in-domain data [@zhao2025absolutezero]. SPADE, whose authors include Absolute Zero's first author, goes further: instead of single problems, the model writes complete multi-turn environments as executable code, with state, rewards, and verification, and the environment designer is rewarded for environments at the edge of what the agent can do, measured by how much a privileged hint raises the agent's reward. There needs to be some external input, such that the model does not collapse; think of it as analogous to the real workflows that DeepSeek brought into its environment creation pipeline (@sec-ch10-environments). SPADE seeds each environment with a document sampled from a pretraining corpus, and without it the designer produced one rotating-maze environment 41 times in a row. At 30B parameters, SPADE beats the strongest fixed-environment baseline by 5.3 points on average across eight held-out benchmarks, and its authors note a version of the leash that @sec-ch11-elicitation describes: the designer cannot write environments more complex than its base model can express [@liu2026spade]. When the proposer is rewarded for difficulty, it learns to hack that reward too, drifting toward artificially complex problems that teach nothing, such as theorem statements padded with long chains of "or" clauses [@bailey2026sgs]. The most contrived examples would be large multiplication or problems which involve a random number generator, which, by design, can only be solved 50% of the time. Self-Guided Self-Play counters this with a guide, a frozen copy of the initial model, that scores each proposed problem by its relevance to unsolved target problems and by how clean and natural it is [@bailey2026sgs]. The pattern one notices in self-play is the necessity of grounding; another example is formal program verification, where the formal verifier makes the gains possible [@wilf2025psv].

As @sec-ch10-environments describes, DeepSeek-V4.1-Flash treats a task as a problem, an environment, and a verification system, and trains the model to build better tasks using difficulty and correctness as rewards, noting that this capability "remains far from perfect" [@deepseekai2026v41flash].

If the verifier matters more than the optimizer, and the model writes the verifiers, then verifier quality becomes a training target, and every failure in @sec-ch11-reward-hacking can now enter through the task generator as well as through the policy. Whether task generators can be audited as fast as they produce tasks is open, although frontier labs run closed systems for this: Anthropic runs an automated review of all environments before and during training runs, yet by spring 2026 it was producing RL environments "faster than our systems could vet them", and in April it froze all changes to its production RL environments for roughly a month [@anthropic2026alignmentsecurity].

## The agenda at a glance

| Problem | Best current evidence |
|---|---|
| Elicitation or creation | Default RLVR sharpens; targeted recipes expand |
| Over-optimization of learned graders | Weak rubric verifiers diverge from judge panels; strong ones reduce but do not eliminate hacking |
| What the verifier misses | Audits find hackable tests and brittle checkers |
| Hacking generalization | Production hacks generalize; Hacker-Opus stayed grader-bound |
| Monitorability | Measurably lower at the 2026 frontier; length penalties reduce it |
| RL compute | Sigmoid fits predict single-recipe runs |
| Credit at long horizons | Trajectory-level rewards plus context management; MiniMax adds per-step format rewards |
| Beyond verification | Rubric rewards work and are used at the frontier |
| Self-reward | Early gains, then collapse |
| Self-generated tasks | Self-play and frontier task synthesis work with grounded checkers |

: Open problems in RLVR and the strongest current evidence on each; @sec-research-ideas lists experiments inspired by this table. {#tbl-ch11-agenda}