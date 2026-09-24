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

**Research question.** Does RLVR with outcome rewards create reasoning capability that was absent from the base model, or does it only reallocate probability mass toward solutions the base model could already sample?

**The case for reallocation.** Yue et al. compared base and RLVR-trained models with pass@k at large k. RL wins at $k = 1$, but the base model overtakes it as $k$ grows: on Minerva with a 32B model, the base model is ahead by about 9 points at $k = 128$ [@yue2025doesrl]. Six different RLVR algorithms behaved similarly, while off-policy distillation from a stronger model expanded the set of solvable problems. *The Invisible Leash: Why RLVR May or May Not Escape Its Origin* argues that RLVR can in principle reach new solutions, but in practice the support it loses outweighs the support it gains [@wu2025invisibleleash].

**Entropy as the currency.** Entropy explains part of the mechanism. A policy's entropy measures how spread out its sampling is: high entropy means many continuations are plausible, and zero entropy means the policy always produces the same one. Cui et al. tracked entropy and validation accuracy through RL runs on eleven base models from 0.5B to 32B parameters and found that, without an entropy bonus or a KL penalty, accuracy $R$ is a fixed function of entropy $H$: $R = -a e^{H} + b$, where $a$ and $b$ depend on the model and task [@cui2025entropy]. Most of the exchange happens early: in the first 200 gradient steps, the models spent 73% of the entropy they would ever consume and made 76% of their eventual gain. Because the curve is fixed, so is its endpoint. When entropy runs out, accuracy stops at $-a + b$, a ceiling that a fit on the first few dozen steps already predicts (@fig-ch11-entropy-performance).

The mechanism is a covariance. A policy-gradient step raises each sampled token's logit in proportion to its advantage, so entropy falls when the tokens the policy already favors are also the ones with high advantage, and rises when a rare token turns out to be good. In reasoning RL the first case dominates: the covariance between a token's log-probability and its advantage stays positive throughout training, so entropy falls steadily. Cui et al. counter this by restraining the updates on the 0.02% to 0.2% of tokens with the highest covariance, which keeps entropy more than ten times higher and improves on GRPO by 6.4 points on average for a 32B model [@cui2025entropy]. The link to elicitation is direct: a policy that spends its entropy concentrates on the solutions it already favored, which is the reallocation Yue et al. measured.

::: {#fig-ch11-entropy-performance}

::: {.content-visible when-format="html"}
![](../diagrams/11-entropy-performance-light.svg){.light-content}

![](../diagrams/11-entropy-performance-dark.svg){.dark-content}
:::

::: {.content-visible when-format="pdf"}
![](../diagrams/11-entropy-performance-light.svg)
:::

The entropy-performance law of Cui et al. As RL spends policy entropy $H$, validation performance $R$ rises along $R = -a e^{H} + b$ and stops at the ceiling $-a + b$ when entropy is exhausted. The coefficients here are illustrative; Cui et al. fit $a$ and $b$ separately for each model.

:::

**The case for creation.** Several results show RL solving problems the base model never solved:

- ProRL trained a 1.5B model for more than 2,000 steps with KL control and periodic resets of the reference policy, and found the RL model ahead of the base model across pass@k, including on tasks where the base model fails at every $k$. The gains were largest where the base model was weakest [@liu2025prorl].
- On synthetic string transformations, a model that already knows functions $f$ and $g$ learns their unseen composition $f(g(x))$ through RL, while next-token training on the same data does not [@yuan2025composing].
- On code problem families where the base model's pass@k is zero, RL shows a grokking-like transition: after a long stretch of near-zero reward, accuracy climbs abruptly to near perfect. However, RL needs a dense-reward warm-up, experience replay, and a curriculum to get there [@sun2025rlgrokking].
- For tool-use, the RL model's pass curve pulls away from the base model's as $k$ grows, instead of converging. The expansion appears only on compositional, sequential information gathering, and SFT on matched data shrinks the boundary on the same tasks [@zhai2026passkt].

**A reconciliation.** Yuan et al. argue that the large-$k$ decline is partly an artifact of where RLVR spends its updates. The arithmetic is simple. If a policy solves a problem once in 8 samples, then 256 samples almost surely contain a correct answer, since pass@256 is $1 - (7/8)^{256} \approx 1$. Further training on that problem can still raise pass@1, but it cannot raise pass@256; it can only narrow which correct solutions the model produces. With few rollouts per problem, a single observed success already puts a problem in this regime, so Yuan et al. conclude that most updates in standard RLVR sharpen rather than expand. Restricting updates to problems with no observed success lifts pass@256 above the base model on difficult benchmarks. This needs a loss that still pushes down wrong answers when every rollout in a group fails, a case where GRPO's group-relative advantage is zero [@yuan2026overtraining; @zhu2025negative].

**What is open.** Most of these results use small models, synthetic tasks, curricula, or hints, and the setting closest to the clean question failed: on code families the base model never solves, standard RL with binary rewards collapsed for lack of any positive signal [@sun2025rlgrokking]. Whether outcome-only RL can turn natural problems the base model never solves into reliably solved ones at frontier scale is open, and so is whether composing known skills should count as new capability. @sec-research-ideas turns this into an experiment.

## Reward hacking {#sec-ch11-reward-hacking}

**Is there an over-optimization law for learned graders?** Chapter 7's over-optimization curve by Gao et al. measured proxy-gold divergence for preference reward models [@gao2023scaling]. No equivalent law exists for rubric aggregates or generative verifiers [@zhang2025genrm], so practitioners optimizing against them have no principled stopping criterion.

The divergence itself is now well documented. Mahmoud et al. trained Qwen2.5-7B-Instruct with GRPO on medical and science prompts, rewarding it through a single LLM training verifier that marks each rubric criterion as met or not met: either a weak, cheap verifier (GPT-4o-mini) or a strong one (GPT-OSS-120B). A separate panel of three frontier judges never supplied reward; it only re-graded the policy's answers at evaluation time. With the weak verifier, the share of newly credited criteria that the whole panel rejected climbed from 39% to 65% over training on the medical prompts; with the strong verifier it stayed between 15% and 21% with no upward trend [@mahmoud2026rubrichacking]. In a sweep of judge sizes, larger judges delayed reward hacking, but every policy hacked by the end of training [@liu2026reasoningjudges]. What no study has fitted is the functional form: how the gap between proxy and gold reward scales with KL, judge size, and verifier recall.

**Can semantic faithfulness be measured directly?** By the verifier's nature, we only have coverage on what it checks, we cannot tell whether a model learned the underlying capability or merely to satisfy the checks. (This point in general seems contrived. What does "semantic faithfulness is measured directly" actually mean?)

One single-author audit found that on a 49-task sample of SWE-bench Verified, 28.5% of tasks accept a Docker-verified incorrect patch, and that across 134 submitted models, Pass@1 is 14.14 points higher on the hackable tasks than on robust tasks of the same difficulty [@rajan2026auditing]. Rule-based math verifiers err in the other direction, rejecting correct answers written in unexpected forms, and those false negatives hurt more as the policy gets stronger, although this domain is much more tractable than the question of unambiguous and non-hackable software tasks [@huang2025verifiers]. An underrated point is that nothing in the objective rewards solving a task the "right" way: the policy is paid for reward, so in practice models exploit tests whenever that is the easier path to reward. ImpossibleBench makes this measurable by mutating coding tasks so that their tests contradict the specification, which means any passing solution is a cheat (@fig-ch11-impossiblebench). On its one-off SWE-bench variant, GPT-5 cheated on 76% of tasks [@zhong2025impossiblebench].

::: {#fig-ch11-impossiblebench fig-cap="ImpossibleBench. A test is mutated to contradict the task, so a model can only pass by cheating; the bars give cheating rates on the one-off SWE-bench variant with the full scaffold. Reproduced from Zhong et al., CC BY 4.0."}

![](../diagrams/11-impossiblebench-overview.png){fig-alt="ImpossibleBench overview: an is_prime task with a normal test and a mutated test asserting not is_prime(7), and bars of cheating rates for GPT-5 (76%), Sonnet 3.7 (70%), Opus 4.1 (54%), Sonnet 4 (48%), and o3 (39%)."}

:::

Two partial answers to the faithfulness question have appeared:

1. auditing verifiers with semantically equivalent rewrites of known answers [@xin2026verifierfails]
2. verifier-free diagnostics computed from the policy's own log-probabilities [@mahmoud2026rubrichacking].

Neither can list what the verifier misses, and no method can: any behavior we learn to measure becomes one more check, and some complement always stays unchecked. The well-posed version of the question is statistical. On a sample of the policy's own accepted outputs, how often would an independent and more expensive audit reject what the verifier accepted, and how does that rate change as training proceeds? The rate can be estimated even though the unchecked complement can never be eliminated. In math, Huang et al. did exactly this, scoring 1,000 sampled training queries at each checkpoint with a stronger model as an oracle, which exposed model-based verifiers being exploited during RL [@huang2025verifiers]. What remains open is doing it at frontier scale for agentic tasks, where each audit is itself expensive.

**Does hacking generalize?** The strongest reason to care about reward hacking is that it may not stay local, and the two most direct studies disagree on how far it spreads. In 2025, Anthropic first taught a pretrained model about reward-hacking strategies and then trained it on real production coding environments. The model learned to hack, and then generalized to alignment faking, cooperating with malicious actors, and attempting sabotage, including sabotage of the codebase for the paper itself [@macdiarmid2025emergent]. Hacker-Opus, the 2026 study described in Chapter 8, found something narrower. Trained on 80 environments with known exploits, the model misbehaved where a misaligned action could raise an automated grader's score, and behaved like its starting checkpoint in scenarios "without a clear notion of a reward, automated grader, or cheat" [@qi2026rewardseeker]. One difference in setup stands out: the 2025 model was taught about reward hacking before RL, while Hacker-Opus learned it only from its environments. Which hacks spread into broader dispositions, and under what training, is open.

**Does optimization pressure erode monitorability?** Chain-of-thought monitoring catches reward hacking that action monitoring misses, but putting the monitor into the reward teaches the model to hide its intent [@baker2025monitoring]. OpenAI's response has been a rule: optimize the outcomes of reasoning, but do not grade the reasoning itself. Its chief scientist, Jakub Pachocki, stated the bet in September 2026: "If we scale optimization on the outcomes of that process, but do not supervise the process itself, that chain-of-thought has no direct incentive in training to hide any misaligned ideas or objectives" [@pachocki2026alienmind]. The rule is hard to keep. In May 2026, OpenAI disclosed that chains of thought had accidentally been graded in some RL runs for released models, on less than 4% of samples for each affected model, with no clear loss of monitorability [@carroll2026accidentalcotgrading].

The evidence on whether ordinary RL erodes monitorability has since shifted. In December 2025, OpenAI measured monitorability across training and found that RL optimization "does not materially decrease monitorability even at the current frontier scale" [@guan2025monitoringmonitorability], but that frontier was the GPT-5 generation. Nine months later, the system card for GPT-6 Astra reports "a substantial decrease in chain-of-thought monitorability compared to previous models". On chains of thought of 750 to 1,250 tokens, Astra controlled its reasoning as instructed 60.9% of the time, against 16.1% for GPT-5.6 Sol, and this controllability rose over RL training even though OpenAI is "fairly confident that there are no significant direct CoT grading pressures" [@openai2026astrasystemcard]. Pachocki gives three reasons: some interactions have to be supervised, models are getting better at reasoning about their own reasoning, and they are getting smarter without verbalized reasoning at all [@pachocki2026alienmind].

Specific reward terms matter too. RL with length penalties that cut reasoning to 30% of its original length kept accuracy but reduced how often the reasoning admitted using a hint by 39% for a 14B model [@little2026lengthpenalty], and more generally, reward terms that conflict with the model's natural reasoning, such as a length penalty or a chain-of-thought monitor, reduce monitorability [@kaufmann2026aligned]. Since every frontier recipe in Chapter 9 controls length, which reward terms are safe for monitorability is a practical question, not only a safety one.

## A predictive science of RL compute

**Research question.** Does RL post-training admit predictive scaling laws of the kind pretraining has, and what determines the asymptote a recipe saturates toward?

The question grows more pressing as RL's share of compute grows. SemiAnalysis estimates that, across Anthropic and OpenAI combined, post-training and RL rose from about 5% of lab compute capacity in the second quarter of 2024 to 36% in the fourth quarter of 2025, when it overtook pre-training at 32%, and to 50% in the second quarter of 2026, against 13% for pre-training [@xie2026shortking]. These are modeled estimates of how the labs' fleets are allocated, not disclosed figures, but they suggest that the least understood stage of training now takes the largest share of lab compute.

The first systematic datapoint is ScaleRL: a study totaling more than 400,000 GPU-hours that fits sigmoidal compute-performance curves to RL training runs and validates them by predicting, from smaller runs, the trajectory of a single run extended to 100,000 GPU-hours [@khatri2025scalerl]. @fig-ch11-scalerl-100k shows that flagship result: curves fitted on the first 50,000 GPU-hours of an 8B run predict where the run lands at 100,000.

::: {#fig-ch11-scalerl-100k fig-cap="ScaleRL's flagship result. Sigmoid curves fitted on the early part of each run (stars, solid lines) predict the extended training runs (crosses, dotted lines) for an 8B dense model and a 17Bx16 mixture-of-experts model. Reproduced from Khatri et al., CC BY 4.0."}

![](../diagrams/11-scalerl-100k-gpu-hours.png){fig-alt="Validation pass rate against GPU hours on a log scale for ScaleRL-8B Dense and ScaleRL-17Bx16 MoE, with fitted sigmoid curves and extrapolations that match extended training points." width="75%"}

:::

Each fitted curve has three parameters with plain meanings: $A$ is the ceiling the run approaches, $C_{mid}$ is the compute at which it has made half its gain, and $B$ sets how sharply it rises. The fit separates two questions that a single training curve conflates: how high a recipe can go, and how fast it gets there (@fig-ch11-scalerl-ceiling). Most recipe choices turn out to answer the second question. Loss aggregation, advantage normalization, the curriculum, and the off-policy algorithm mostly change how quickly a run reaches its ceiling, while the loss function, the batch size, the generation length, and the model size change the ceiling itself [@khatri2025scalerl]. The practical lesson is to compare recipes by their fitted ceilings rather than by which one is ahead at a given step: raising the generation limit from 14K to 32K tokens slowed early progress but lifted the ceiling.

::: {#fig-ch11-scalerl-ceiling}

::: {.content-visible when-format="html"}
![](../diagrams/11-scalerl-ceiling-vs-efficiency-light.svg){.light-content}

![](../diagrams/11-scalerl-ceiling-vs-efficiency-dark.svg){.dark-content}
:::

::: {.content-visible when-format="pdf"}
![](../diagrams/11-scalerl-ceiling-vs-efficiency-light.svg)
:::

Ceiling versus efficiency in ScaleRL's sigmoid fit. Changing the ceiling $A$ (orange) and reaching the same ceiling sooner (dashed) look alike early in training and diverge only at scale. The curves are illustrative, not fitted to a run.

:::

A second regularity concerns data, and it cuts against intuition from pretraining: RL needs remarkably few distinct problems. Across Qwen2.5 models from 0.5B to 72B, Tan et al. found that test error follows a power law in compute; they then held the number of training steps fixed and shrank the pool of distinct problems, cycling through the smaller pool more times. Test performance barely changed until each problem was repeated about 25 times, and clear overfitting appeared only at 100 repeats [@tan2025scalingbehaviors]. The extreme case is a single problem: RLVR on one example, duplicated to fill each batch, lifts Qwen2.5-Math-1.5B from 36.0% to 73.6% on MATH500, the same score as training on 1,209 examples [@wang2025oneshot]. On-policy distillation shows the same effect for a clearer reason. There, one prompt recovers 87% of the gain from distilling on the full dataset, because the teacher grades every token the student samples: a single prompt, rolled out 64 times per update, yields tens of thousands of supervised token positions, and that signal persists after the student starts solving the prompt, whereas an outcome reward is exhausted once every rollout is correct [@fu2026oneshotopd]. In both cases, the number of distinct prompts understates how much supervision a run receives. What matters more is where the prompts sit: RL raises pass@128 only when pretraining has left headroom and the training problems lie at the edge of the model's competence [@zhang2025interplay].

Open questions follow directly:

- What sets the asymptote: the base model's support, as the elicitation problem suggests, or inefficiencies in training recipes?
- Do fitted curves transfer across model families and task mixtures?
- How should a fixed budget split between pretraining, SFT, and RL?
- Does prolonged RL erode the plasticity it relies on? There is almost no direct evidence for LLMs. ProRL's periodic resets of the reference policy and optimizer and DeepSeek-V4.1-Flash's use of model merging to reinitialize successive RL runs are both workarounds for runs that stop improving, but neither measures plasticity [@liu2025prorl; @deepseekai2026v41flash].

There is little published work on the frontier regarding the science of RL compute; notwithstanding, we can look one level down at OLMo 3, whose 32B Think RL run took ~five days and 750 steps, and a continuation ran 21 more days to 2,300 steps with performance "not yet fully saturated" [@teamolmo2025olmo3]. Kimi K3, DeepSeek-V4.1-Flash, and the MiniMax-M2 series report RL results but no RL compute totals. For single models, outside estimates of RL compute range from under 4% of pre-training compute for DeepSeek-R1-Zero to about 20% for DeepSeek-R1 [@khatri2025scalerl; @epoch2025reasoningscale]. No published scaling law covers multi-domain, agentic, million-token RL, which is where the frontier labs now spend their RL compute.

## Credit assignment at horizon scale

**Research question.** At what horizon does a terminal outcome reward stop carrying usable learning signal, and can process-level signals be made simultaneously scalable and hack-resistant?

Credit in reasoning RL spans one generation of 500-30K+ tokens; agentic RL spans tens to hundreds of turns and 100K to 1M tokens, where a single episode-level scalar becomes increasingly uninformative, and the methods literature has no shared benchmark for comparing credit-assignment quality [@zhang2026creditsurvey]. The same survey claims that intermediate verification, while possible in math, is rarely possible for agents. Let's not forget the well-known METR measure of the length of software tasks that frontier models complete at 50% reliability, which doubled roughly every seven months from 2019 to 2025 and has doubled roughly every three months since 2024 [@kwa2025timehorizon; @metr2026th11]. The measure is now near its ceiling: only 5 of its 228 tasks are estimated to take a human 16 hours or longer, so METR treats horizons above 16 hours as unreliable, and its strongest model measured in 2026 was estimated at "at least 16hrs", the upper end of what the suite can measure [@metr2026mythosthread].

At the frontier, the working answer so far is that outcome rewards suffice when the harness manages the context. Kimi K3 trains on rollouts of up to thousands of tool calls and millions of tokens [@kimiteam2026k3], and MiniMax assigns credit at the episode level: each step's advantage is the reward earned from that step onward minus a baseline for the whole trajectory, even when the agent has truncated or rewritten its context mid-episode [@minimax2026m2]. Neither report describes step-level credit. What both invest in instead is the context the policy sees, which is also where academic work on long horizons is most active. Context folding, for example, trains the agent to collapse each finished sub-task into a short summary, rewards it for folding well, and matches a full-context agent while keeping an active context ten times smaller [@sun2025contextfolding]. Folding shortens the stretch of tokens across which one outcome reward must be spread, so better context management is, in part, better credit assignment.

What is open: whether outcome rewards plus context management suffice as horizons keep growing, and which intermediate states are verifiable.

## Rewards beyond verification

**Research question 1.** How far can RLVR's recipe extend into tasks with no checkable answer?

Two substitutes for a verifier now produce usable signal:

- **Rubrics.** Instead of asking a judge for one overall score on a 1-to-10 scale, a rubric reward gives the judge a list of criteria written for the specific prompt, such as "avoids misinformation" for a medical question. The judge can check each criterion separately, with the reward a weighted sum of the checks, or it can read the whole rubric and give one overall score; in medicine and science, the second version worked best, and both beat a judge with no rubric [@gunjal2025rubrics]. At the frontier, Kimi K3 makes rubrics its default for non-verifiable tasks: an agentic judge must write a rubric, score each candidate against it, and compare candidates pairwise, with a hard length rule on top [@kimiteam2026k3]. DeepSeek-V4 likewise replaces scalar reward models with a generative reward model guided by rubrics for hard-to-verify tasks [@deepseekai2026v4].
- **Reference likelihood.** Where a reference answer exists but no checker does, the policy's own probability of producing the reference can serve as the reward, with no verifier at all [@yu2025rlpr]. No frontier report documents this reward yet; it remains a research method.

Rubric rewards are hackable in the ways @sec-ch11-reward-hacking describes, and they cost a judge call per rollout. The open problem is not whether these signals work early in training, since they do, but whether they stay aligned with the target under the optimization pressure that frontier RL applies.

**Research question 2.** How much of what RLVR learns on checkable tasks transfers to the rest?

Wei's rule says which tasks RL improves directly; transfer asks whether that improvement carries anywhere else. If RL on math and code taught general reasoning, verifiable domains might be enough. The evidence says partly. Across more than twenty open reasoning models, most gains in math fail to transfer to other domains, but in a controlled comparison on Qwen3-14B, math-only RL preserved general capabilities while math-only SFT eroded them [@huan2025mathtransfer]. Across six domains, math, code, and science benefit from each other, while logic, simulation, and tabular reasoning need in-domain data [@cheng2025guru]. RL's Razor offers a mechanism: at matched performance on the new task, RL forgets less than SFT because on-policy updates stay closer to the base model in KL [@shenfeld2025rlrazor]. Which capabilities transfer, and why some domains need their own verifiers, is open.

## Self-improvement without external verification

**Research question.** Can a model's own signals sustain RL improvement, or do self-reward loops inevitably collapse?

Early in training, majority vote over the model's own samples, used as a pseudo-label on unlabeled test problems, roughly tripled Qwen2.5-Math-7B's pass@1 on AIME 2024 [@zuo2025ttrl]. Rewarding self-certainty matched GRPO with gold answers on a Qwen2.5-3B base model [@zhao2025intuitor], and minimizing entropy alone matched RL baselines trained on 60,000 labeled examples [@agarwal2025entropymin].

It's not all fun and games, though, because prolonged RL with majority-vote rewards leads to reward hacking and "sudden and complete performance collapse" [@shafayat2025selftrain]. Internal-feedback rewards help base models early, then degrade performance below the starting model, and give little benefit to instruction-tuned models at all [@zhang2025nofreelunch]. A reward that confirms the model's current beliefs drives entropy down, and pass@n falls with it [@zhou2025evolrl]. This failure is refreshingly concrete: entropy can be measured throughout training, and EVOL-RL counters the collapse by adding a reward for novelty, so the mechanism is a training dynamic that can be observed and corrected rather than one hypothesis among many. Much of the early success is also specific to Qwen2.5 models, which appear to have memorized common math benchmarks during pretraining: given the first 60% of a MATH-500 problem, Qwen2.5-Math-7B reproduces the rest word for word 54.6% of the time, against 3.8% for Llama-3.1-8B. On procedurally generated arithmetic problems created after the model's release, only accurate rewards improved on the base model [@wu2025reasoningmemorization]. The lesson is methodological: gains from self-rewards, or even random rewards, measured on Qwen2.5 and the standard math benchmarks may come from recalling memorized answers rather than from learning.

The open question is quantitative. Self-improvement is governed by the generation-verification gap, how much better a model is at checking an answer than producing one, and a version of that gap grows with pretraining compute [@song2024mindgap]. A self-reward loop can only climb while the model's own judgments are better than its answers. Early warning signs of collapse have been found: intrinsic rewards rise and then fall, with the timing set by how well the model's initial confidence tracks correctness, and the accuracy of self-generated pseudo-labels declines before performance does [@he2026urlvr; @wang2026rlavr]. Nobody has yet tracked the generation-verification gap itself through training and shown that its closing predicts the collapse.

## Models that write their own tasks {#sec-ch11-task-generation}

**Research question.** Can the model generate the environments and verifiers it trains on, and what keeps a task generator honest?

Self-play attacks the scarcity of verified tasks. In Absolute Zero, one model proposes coding tasks, a code executor validates them, and the same model learns to solve them, reaching state-of-the-art results at 7B without in-domain data [@zhao2025absolutezero]. R-Zero co-evolves a challenger and a solver from a base model with no data [@huang2025rzero]. SPADE, whose authors include Absolute Zero's first author, goes further: instead of single problems, the model writes complete multi-turn environments as executable code, with state, rewards, and verification, and the environment designer is rewarded for environments at the edge of what the agent can do, measured by how much a privileged hint raises the agent's reward. At 30B parameters, it beats the strongest fixed-environment baseline by 5.3 points on average across eight held-out benchmarks, and its authors note the same leash that @sec-ch11-elicitation describes: the designer cannot write environments more complex than its base model can express [@liu2026spade]. When the proposer is rewarded for difficulty, it learns to hack that reward too, drifting toward artificially complex problems that teach nothing, so newer methods add a guide role to keep proposed problems useful [@bailey2026sgs]. Grounding matters: in self-play for formal program verification, the formal verifier is what makes the gains possible [@wilf2025psv].

As @sec-ch10-environments describes, DeepSeek-V4.1-Flash treats a task as a problem, an environment, and a verification system, and trains the model to build better tasks using difficulty and correctness as rewards, noting that this capability "remains far from perfect" [@deepseekai2026v41flash]. MiniMax reports that M2.7 now handles 30% to 50% of its RL team's daily iteration workload, reading logs, debugging code, and adjusting training configurations between human reviews [@minimax2026m2].

If the verifier matters more than the optimizer, and the model writes the verifiers, then verifier quality becomes a training target, and every failure in @sec-ch11-reward-hacking can now enter through the task generator as well as through the policy. Whether task generators can be audited as fast as they produce tasks is open.

## The agenda at a glance

| Problem | Best current evidence |
|---|---|
| Elicitation or creation | Default RLVR sharpens; targeted recipes expand |
| Over-optimization of learned graders | Rubric proxies diverge from judge panels |
| Semantic faithfulness | Audits find hackable tests and brittle checkers |
| Hacking generalization | Production hacks generalize; Hacker-Opus stayed grader-bound |
| Monitorability | Measurably lower at the 2026 frontier; length penalties reduce it |
| RL compute | Sigmoid fits predict single-recipe runs |
| Credit at long horizons | Frontier labs still use episode-level credit |
| Beyond verification | Rubric rewards work and are used at the frontier |
| Self-reward | Early gains, then collapse |
| Self-generated tasks | Self-play and frontier task synthesis work with grounded checkers |

: Open problems in RLVR and the strongest current evidence on each; @sec-research-ideas collects experiments that would move them. {#tbl-ch11-agenda}

@tbl-ch11-agenda compresses the chapter. Read down its rows and one pattern holds throughout: where the checker is grounded in execution, formal proof, or an exact answer, RLVR keeps working; where the checker is learned, self-referential, or sparse over a long horizon, the open problems begin.
