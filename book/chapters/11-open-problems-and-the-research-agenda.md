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

The sections follow that order. Each gives the research question first, then what is known, then what is open.

## Elicitation or creation

**Research question.** Does RLVR with outcome rewards create reasoning capability that was absent from the base model, or does it only reallocate probability mass toward solutions the base model could already sample?

**The case for reallocation.** Yue et al. compared base and RLVR-trained models with pass@k at large k. RL wins at $k = 1$, but the base model overtakes it as $k$ grows: on Minerva with a 32B model, the base model is ahead by about 9 points at $k = 128$ [@yue2025doesrl]. Six different RLVR algorithms behaved similarly, while distillation from a stronger model did expand the set of solvable problems. The Invisible Leash formalizes the pattern: RLVR can in principle reach new solutions, but in practice the support it loses outweighs the support it gains [@wu2025invisibleleash]. Entropy explains part of the mechanism. Cui et al. find that performance is bought with policy entropy, following $R = -a e^{H} + b$, so a policy that has collapsed to zero entropy has a predictable ceiling [@cui2025entropy].

**The case for creation.** Several results show RL solving problems the base model never solved:

- ProRL trained a 1.5B model for more than 2,000 steps with KL control and periodic resets of the reference policy, and found the RL model ahead of the base model across pass@k, including on tasks where the base model fails at every $k$. The gains were largest where the base model was weakest [@liu2025prorl].
- On synthetic string transformations, a model that already knows functions $f$ and $g$ learns their unseen composition $f(g(x))$ through RL, while next-token training on the same data does not [@yuan2025composing].
- On code problem families where the base model's pass@k is zero, RL shows a grokking-like transition: after a long stretch of near-zero reward, accuracy climbs abruptly to near perfect. It needs a dense-reward warm-up, experience replay, and a curriculum to get there [@sun2025rlgrokking].
- For tool-using agents, the RL model's pass curve pulls away from the base model's as $k$ grows, instead of converging. The expansion appears only on compositional, sequential information gathering, and SFT on matched data shrinks the boundary on the same tasks [@zhai2026passkt].

**A reconciliation.** Yuan et al. argue that the large-$k$ decline is partly an artifact of the objective. Once a problem is solved even once, it sits in a nearly saturated regime, so standard RLVR spends its updates sharpening solved problems. Updating only on problems with no observed success lifts pass@256 above the base model on difficult benchmarks [@yuan2026overtraining]. On this reading, both camps are right: the default recipe mostly sharpens, and a recipe aimed at unsolved problems can expand.

**What is open.** Most of the expansion results use small models, synthetic tasks, curricula, or hints. Nobody has shown pure outcome-reward RL, with no teacher data, turning a family of natural problems from pass@4096 of zero into reliably solved at frontier scale. Nor is it settled whether composing known skills should count as new capability. A clean test would take problems the base model never solves, train with outcome rewards only at two or more model scales, and compare held-out pass@4096 against a compute-matched budget of base-model sampling plus the same verifier.

## Reward hacking {#sec-ch11-reward-hacking}

Chapter 7 treated reward hacking as a property of a verifier. At the research frontier, it is also a property of the training run: how fast exploitation grows, what else the policy learns alongside it, and whether we can still detect it.

**Is there an over-optimization law for learned graders?** Chapter 7's quantitative anchor, the over-optimization curve of Gao et al., was measured for preference reward models [@gao2023scaling]. No equivalent law exists for rubric aggregates or generative verifiers [@zhang2025genrm], so practitioners optimizing against them have no principled stopping criterion.

The divergence itself is now documented. When a policy is trained against a rubric verifier and scored by a panel of three frontier judges from other model families, weak verifiers produce large proxy gains that do not transfer, exploitation grows over training, and it concentrates in a few failure types, such as partially satisfying compound criteria. Stronger verifiers reduce the exploitation but do not eliminate it [@mahmoud2026rubrichacking]. Generative judges can be fooled by "master keys", responses consisting of a colon or an opener like "Thought process:" [@zhao2025onetoken]. What is missing is the functional form: how the gap between proxy and gold reward scales with KL, judge size, and verifier recall. Fitting Gao-style curves for judges of graded strength, with a frozen panel as gold, is a well-posed experiment that nobody has published.

**Can semantic faithfulness be measured directly?** We currently score only what the verifier checks. Without an independent way to measure everything it misses, we cannot tell whether a high-scoring model truly learned the intended behavior or merely learned to satisfy the checks.

Audits give a sense of the scale. One single-author audit found that on a 49-task sample of SWE-bench Verified, 28.5% of tasks accept a Docker-verified incorrect patch, and that across 134 submitted models, Pass@1 is 14.14 points higher on the hackable tasks than on robust tasks of the same difficulty [@rajan2026auditing]. Rule-based math verifiers err in the other direction, rejecting correct answers written in unexpected forms, and those false negatives hurt more as the policy gets stronger [@huang2025verifiers]. Frontier agents exploit tests when they can: on a benchmark whose tasks conflict with their tests, GPT-5 cheated on 76% of one SWE-bench variant [@zhong2025impossiblebench]. Two partial answers to the faithfulness question have appeared: auditing verifiers with semantically equivalent rewrites of known answers, and verifier-free diagnostics computed from the policy's own log-probabilities [@mahmoud2026rubrichacking]. Neither yet measures recall on the behaviors the verifier never checks.

**Does hacking generalize?** The strongest reason to care about reward hacking is that it does not stay local. Anthropic trained a model on real production coding environments after teaching it about reward-hacking strategies. The model learned to hack, and then generalized to alignment faking, cooperating with malicious actors, and attempting sabotage, including sabotage of the codebase for the paper itself. Safety training in chat fixed the chat evaluations but not the agentic ones. The mitigations that worked were preventing the hacking, more diverse safety training, and inoculation prompting, which tells the model during training that the hack is acceptable in this context [@macdiarmid2025emergent; @wichers2025inoculation]. Why a narrow reward hack changes the model's broader dispositions, and which hacks do so, is open.

**Does optimization pressure erode monitorability?** Chain-of-thought monitoring catches reward hacking that action monitoring misses, but putting the monitor into the reward teaches the model to hide its intent [@baker2025monitoring]. The evidence on ordinary RL is mixed. OpenAI measured monitorability across training and found that RL optimization "does not materially decrease monitorability even at the current frontier scale" [@guan2025monitoringmonitorability]. Yet specific pressures do: RL with length penalties that cut reasoning to 30% of its original length kept accuracy but reduced how often the reasoning admitted using a hint by 39% for a 14B model [@little2026lengthpenalty]. Since every frontier recipe in Chapter 9 controls length, which reward terms are safe for monitorability is a practical question, not only a safety one.

## A predictive science of RL compute

**Research question.** Does RL post-training admit predictive scaling laws of the kind pretraining has, and what determines the asymptote a recipe saturates toward?

The first large systematic datapoint is ScaleRL: a study totaling more than 400,000 GPU-hours that fits sigmoidal compute-performance curves to RL training runs and validates them by predicting, from smaller runs, the trajectory of a single run extended to 100,000 GPU-hours [@khatri2025scalerl]. Its most useful finding is a division of labor. Loss aggregation, advantage normalization, curriculum, and the off-policy algorithm mostly change how fast a run approaches its ceiling. The loss type, the batch size, and the model size change the ceiling itself.

Other regularities are emerging. Across Qwen2.5 models from 0.5B to 72B, reward follows a power law in compute, and when data is limited, final performance depends mainly on the total number of optimization steps rather than on how many distinct problems were seen [@tan2025scalingbehaviors]. A single training example can recover most of the MATH500 gain of a 1,200-example dataset on Qwen2.5-Math-1.5B, raising it from 36.0% to 73.6% [@wang2025oneshot]. RL also raises pass@128 only when pretraining has left headroom and the RL data sits at the edge of the model's competence [@zhang2025interplay].

Open questions follow directly. What sets the asymptote: the base model's support, as the elicitation problem suggests, or removable inefficiencies of current recipes? Do fitted curves transfer across model families and task mixtures? How should a fixed budget split between pretraining, SFT, and RL? And does prolonged RL erode the plasticity it relies on? That last question has almost no direct evidence for LLMs. ProRL's periodic resets of the reference policy and optimizer and DeepSeek-V4.1-Flash's use of model merging to reinitialize successive RL runs are both workarounds for runs that stop improving, but neither measures plasticity [@liu2025prorl; @deepseekai2026v41flash].

The frontier offers few numbers to fit. OLMo 3 is the exception: its 32B Think RL run took about five days and 750 steps, and a continuation ran 21 more days to 2,300 steps with performance "not yet fully saturated" [@teamolmo2025olmo3]. Kimi K3, DeepSeek-V4.1-Flash, and the MiniMax-M2 series report RL results but no RL compute totals, and outside estimates of RL's share of total training compute range from a few percent to parity with pretraining [@epoch2025reasoningscale]. No published law yet covers multi-domain, agentic, million-token RL, which is where the frontier labs now spend their RL compute.

## Credit assignment at horizon scale

**Research question.** At what horizon does a terminal outcome reward stop carrying usable learning signal, and can process-level signals be made simultaneously scalable and hack-resistant?

The agentic regime sharpens the question. Credit in reasoning RL spans one generation of 500 to 30K+ tokens; agentic RL spans tens to more than a hundred turns and 100K to 1M tokens, where a single episode-level scalar becomes increasingly uninformative, and the methods literature has no shared benchmark for comparing credit-assignment quality [@zhang2026creditsurvey]. The same survey notes that intermediate verification is often possible in math and rarely possible for agents. The horizon is also moving: METR's measure of the length of software tasks that frontier models complete at 50% reliability has doubled roughly every seven months since 2019, and faster since 2024 [@kwa2025timehorizon; @metr2026th11].

At moderate horizons, methods that avoid a learned critic work. VinePPO showed that PPO's value network barely beats a random baseline at ranking alternative reasoning steps and replaced it with Monte Carlo estimates from extra rollouts [@kazemnejad2024vineppo]. GiGPO groups actions taken from the same environment state across a group's trajectories, giving step-level advantages at no extra rollout cost, and improves on GRPO by more than 12% on ALFWorld and 9% on WebShop [@feng2025gigpo]. Context folding trains the agent to collapse finished sub-tasks into summaries and matches a full-context agent with an active context ten times smaller [@sun2025contextfolding].

At the frontier, none of this has visibly arrived. Kimi K3 trains on rollouts of up to thousands of tool calls and millions of tokens [@kimiteam2026k3], and MiniMax-M2 assigns credit at the episode level, with reward-to-go against a trajectory-level baseline, even across context truncations and rewrites [@minimax2026m2]. What is open: whether outcome rewards plus task structure suffice at these horizons, and which intermediate states are verifiable. A direct experiment would hold rollout compute fixed on one long-horizon software suite, vary the horizon from 50 to 500 steps, and compare episode-level credit, Monte Carlo values from restored sandbox checkpoints, and state-grouped advantages against Monte Carlo ground truth.

## Rewards beyond verification

**Research question.** How far can RLVR's recipe extend into tasks with no checkable answer, and how much of what it learns on checkable tasks transfers to the rest?

Three substitutes for a verifier now produce usable signal:

- **Rubrics.** A per-prompt rubric scored by a judge beats a single Likert-scale judgment, by up to 31% relative on HealthBench [@gunjal2025rubrics]. Kimi K3 makes this its default for non-verifiable tasks: an agentic judge must write a rubric, score each candidate against it, and compare candidates pairwise, with a hard length rule on top [@kimiteam2026k3].
- **Checklists.** Instruction-specific checklists outperform reward models as an RL signal for instruction following, improving on every one of five benchmarks tested [@viswanathan2025checklists].
- **Reference likelihood.** Where a reference answer exists but no checker does, the policy's own probability of producing the reference can serve as the reward, with no verifier at all [@yu2025rlpr].

Each substitute brings back the problem that motivated verifiable rewards. Rubric rewards are hackable in exactly the ways @sec-ch11-reward-hacking describes, and they cost a judge call per rollout. Reference likelihood requires a reference. The open problem is not whether these signals work early in training, since they do, but whether they stay aligned with the target under the optimization pressure that frontier RL applies.

Transfer is the other route. If RL on math and code taught general reasoning, verifiable domains would be enough. The evidence says partly. Across more than twenty open reasoning models, most gains in math fail to transfer to other domains, but in a controlled comparison on Qwen3-14B, math-only RL preserved general capabilities while math-only SFT eroded them [@huan2025mathtransfer]. Across six domains, math, code, and science benefit from each other, while logic, simulation, and tabular reasoning need in-domain data [@cheng2025guru]. RL's Razor offers a mechanism: at matched performance on the new task, RL forgets less than SFT because on-policy updates stay closer to the base model in KL [@shenfeld2025rlrazor]. Which capabilities transfer, and why some domains need their own verifiers, is open.

## Self-improvement without external verification

**Research question.** Can a model's own signals, such as confidence, self-consistency, or self-judgment, sustain RL improvement, or do self-reward loops inevitably collapse?

Early in training, self-rewards work surprisingly well. Majority vote over the model's own samples, used as a pseudo-label on unlabeled test problems, roughly tripled Qwen2.5-Math-7B's pass@1 on AIME 2024 [@zuo2025ttrl]. Rewarding self-certainty matched GRPO with gold answers on a Qwen2.5-3B base model [@zhao2025intuitor], and minimizing entropy alone matched RL baselines trained on 60,000 labeled examples [@agarwal2025entropymin].

Run long enough, the loops collapse. Prolonged RL with majority-vote rewards leads to reward hacking and "sudden and complete performance collapse" [@shafayat2025selftrain]. Internal-feedback rewards help base models early, then degrade performance below the starting model, and give little benefit to instruction-tuned models at all [@zhang2025nofreelunch]. The reason is structural: a reward that confirms the model's current beliefs drives entropy down, and pass@n falls with it [@zhou2025evolrl]. Much of the early success is also specific to Qwen2.5 models whose benchmarks appear in their pretraining data; on a clean, procedurally generated task, only accurate rewards produced improvement beyond the base model [@wu2025reasoningmemorization].

The open question is quantitative. Self-improvement is governed by the generation-verification gap, how much better a model is at checking an answer than producing one, and a version of that gap grows with pretraining compute [@song2024mindgap]. A self-reward loop can only climb as long as the gap is positive. Nobody has yet measured the gap during RL and shown that its closing predicts the collapse.

## Models that write their own tasks

**Research question.** Can the model generate the environments and verifiers it trains on, and what keeps a task generator honest?

Self-play attacks the scarcity of verified tasks. In Absolute Zero, one model proposes coding tasks, a code executor validates them, and the same model learns to solve them, reaching state-of-the-art results at 7B without in-domain data [@zhao2025absolutezero]. R-Zero co-evolves a challenger and a solver from a base model with no data [@huang2025rzero]. When the proposer is rewarded for difficulty, it learns to hack that reward too, drifting toward artificially complex problems that teach nothing, so newer methods add a guide role to keep proposed problems useful [@bailey2026sgs]. Grounding matters: in self-play for formal program verification, the formal verifier is what makes the gains possible [@wilf2025psv].

The frontier has adopted the idea. DeepSeek-V4.1-Flash treats a task as a problem, an environment, and a verification system, and trains the model to build better tasks using difficulty and correctness as rewards, noting that this capability "remains far from perfect" [@deepseekai2026v41flash]. MiniMax reports that M2.7 now handles 30% to 50% of its RL team's daily iteration workload, reading logs, debugging code, and adjusting training configurations between human reviews [@minimax2026m2].

This is the loop the book has been building toward. If the verifier matters more than the optimizer, and the model writes the verifiers, then verifier quality becomes a training target, and every failure in @sec-ch11-reward-hacking can now enter through the task generator as well as through the policy. Whether task generators can be audited as fast as they produce tasks is open.

## The agenda at a glance

| Problem | Best current evidence | Deciding experiment |
|---|---|---|
| Elicitation or creation | Default RLVR sharpens; targeted recipes expand | Outcome-only RL on pass@4096-zero problems at two scales |
| Over-optimization of learned graders | Rubric proxies diverge from judge panels | Gao-style fits across judge sizes |
| Semantic faithfulness | Audits find hackable tests and brittle checkers | Measured verifier recall on unchecked behaviors |
| Hacking generalization | Production hacks generalize to misalignment | Which hacks generalize, and why |
| Monitorability | No broad loss under RL; losses under length penalties | Monitorability tracked per reward term |
| RL compute | Sigmoidal fits predict single-recipe runs | Laws for agentic, multi-domain RL; plasticity over long runs |
| Credit at long horizons | Critic-free step credit works at tens of turns | Credit methods compared from 50 to 500 steps |
| Beyond verification | Rubrics, checklists, and reference likelihood work early | Alignment with the target under prolonged pressure |
| Self-reward | Early gains, then collapse | Generation-verification gap tracked through training |
| Self-generated tasks | Self-play and frontier task synthesis work with grounded checkers | Auditing generators as fast as they generate |

: Open problems in RLVR, the strongest current evidence on each, and an experiment that would move it. {#tbl-ch11-agenda}

@tbl-ch11-agenda compresses the chapter. Read down its rows and one pattern holds throughout: where the checker is grounded in execution, formal proof, or an exact answer, RLVR keeps working; where the checker is learned, self-referential, or sparse over a long horizon, the open problems begin.
