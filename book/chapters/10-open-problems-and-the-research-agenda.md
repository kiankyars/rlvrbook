# Open Problems

![M. C. Escher, _Alfedena Abruzzi_ (1929).](../escher/10-alfedena-abruzzi.jpg){width="80%" fig-align="center"}

## Chapter Map

- Name six open problems that decide whether RLVR generalizes beyond its current strongholds.
- For each problem: the research question, the strongest evidence on each side, and what an answer would have to show.

Earlier chapters each closed with open questions scoped to their own machinery. This chapter promotes six of those threads into research problems in their own right. The selection criterion is disagreement: each problem below has credible evidence pointing in both directions, and resolving it would change how the techniques of Chapters 2 through 9 get applied.

## Elicitation or creation

**Research question.** Does RLVR with outcome rewards create reasoning capability that was absent from the base model, or does it only reallocate probability mass toward solutions the base model could already sample?

The case for elicitation starts with sampling budgets. Yue et al. evaluate RLVR models and their base models at pass@k for large k, the coverage measure from Chapter 6. RL-trained models win at pass@1, but as k grows the base models catch up and overtake: with k up to 1,024 on AIME24 and AMC23, base models match or exceed their RL counterparts, and on Minerva a 32B base model beats its RL version by roughly 9 points at k=128. Perplexity analysis shows the RL model's solutions already sit in the base model's high-likelihood set, and the gap between an RL model's pass@1 and the base model's pass@256 ceiling stays above 40 points on the in-domain test set across PPO, GRPO, Reinforce++, RLOO, ReMax, and DAPO. Distillation from a stronger teacher, by contrast, lifts the entire pass@k curve.[@yue2025limitrlvr] The Invisible Leash supplies the theoretical frame: a verifier can only reward what the policy actually samples, so RLVR is support-constrained optimization, and empirically the shrinkage of the sampled support outweighs its expansion.[@wu2025invisibleleash]

The case for creation attacks both the training budget and the metric. ProRL trains a 1.5B model for more than 2,000 RL steps over 136K problems in five domains, using KL control and periodic reference-policy resets, and reports pass@k gains across the whole range of k, including tasks where the base model solves nothing at any sampling budget while the trained model reaches a 100% pass rate; expansion is strongest exactly where the base model starts weakest.[@liu2025prorl] Wen et al. argue that plain pass@k at large k is the wrong capacity measure because it credits lucky guesses: under CoT-Pass@K, which requires the reasoning chain and the answer to both be correct, RLVR models dominate at every k.[@wen2025cotpassk]

A confound cuts across the whole debate: how much of the measured gain reflects the training signal at all? On Qwen2.5-Math-7B, GRPO with random rewards improves MATH-500 pass@1 by 21.4 points, close to the 29.1-point gain from ground-truth rewards, while the same spurious rewards do nothing for Llama 3 or OLMo 2; the gain comes from amplifying a code-reasoning behavior already frequent in the base model.[@shao2025spurious] Follow-up work traces the mechanism to memorization shortcuts activated by RLVR.[@yan2026spurious] On a synthetic benchmark built to be contamination-free, only accurate rewards produce steady improvement, suggesting that part of the literature's signal is leakage from pretraining.[@wu2025reasoningmemorization]

An answer would have to settle three things: a capacity measure both sides accept, since the elicitation result is only as valid as large-k pass@k; contamination-robust evaluations, since prior-amplification mimics learning; and enough training compute to distinguish a hard ceiling from a slow climb, which is the next problem.

## Semantic faithfulness under weak endpoint proxies

In long-context QA, answer-evidence checks can miss unsupported synthesis. In multimodal search, final-answer and tool-format rewards can miss visual grounding. In agentic software tasks, tests can miss maintainability, security, minimality, and user intent. In instruction following, many constraints require semantic judgment rather than exact checking.[@peng2025verif; @brown2025verifiers; @tan2025rllm] RLVR has even been used in medicine, where a verifier may check a final label, citation, or structured field while missing whether the model used the right evidence, respected uncertainty, or made a decision a clinician would trust.[@zhang2025medrlvr]

The invariant problem across these domains is not "no verifier exists" but that the available verifier checks an endpoint proxy that is semantically weaker than the target behavior. That reframing turns a domain list into three research questions.

**Can rubric decomposition make weak-proxy domains trainable?** Rubrics as Rewards replaces a single judge score with instance-specific, expert-guided rubrics whose items are checked separately and aggregated into a reward for on-policy RL. Against Likert-scale LLM-judge rewards, it reports relative improvements of up to 31% on HealthBench, a rubric-scored benchmark, and 7% on GPQA-Diamond, measured as mean accuracy on verifiable multiple-choice answers.[@gunjal2025rubrics] Grading infrastructure has been productized: string checks, text similarity, score and label models, custom code, and weighted multigraders.[@openai2026graders] What is open is who writes rubrics at scale, whether synthetic rubric generation preserves their robustness, and whether decomposition changes the over-optimization game or merely delays it.

**Is there an over-optimization law for learned graders?** Chapter 7's quantitative anchor, the over-optimization curve of Gao et al., was measured for preference reward models.[@gao2023scaling] No equivalent law exists for rubric aggregates or generative verifiers,[@zhang2025genrm] so practitioners optimizing against them have no principled stopping criterion.

**Can semantic faithfulness be measured directly?** Today the verifier-blind residual is exactly the part of behavior nobody scores. Absent a measurement, a policy that satisfies every rubric item while drifting semantically is indistinguishable from one that generalizes.

## A predictive science of RL compute

**Research question.** Does RL post-training admit predictive scaling laws of the kind pretraining has, and what determines the asymptote a recipe saturates toward?

The first large systematic datapoint is ScaleRL: a study totaling more than 400,000 GPU-hours that fits sigmoidal compute-performance curves to RL training runs and validates them by predicting, from smaller runs, the trajectory of a single run extended to 100,000 GPU-hours. The fits separate design choices into those that shift the asymptote and those that only change compute efficiency along the way; loss aggregation, advantage normalization, data curriculum, and the off-policy scheme land in the efficiency class.[@khatri2025scalerl] The performance metric is the pass rate on a held-out slice of the training distribution, which leaves the transfer question untouched: a predictable in-distribution sigmoid does not yet predict downstream capability.[@tan2025scalingbehaviors]

Information economics makes the stakes concrete. A binary outcome reward delivers at most a few bits per episode, orders of magnitude less per FLOP than the supervised signal of pretraining, an argument Chapter 5 develops quantitatively.[@patel2025bitspersample] If RL compute keeps scaling, either those bits must get cheaper to extract, or the recipe must change what it learns from each episode.

Open questions follow directly. What sets the asymptote: the base model's support, as the elicitation problem suggests, or removable inefficiencies of current recipes? Do fitted curves transfer across model families and task mixtures? How should a fixed budget split between pretraining, SFT, and RL? And does prolonged RL erode the very plasticity it relies on?[@khan2026plasticity]

## Credit assignment at horizon scale

**Research question.** At what horizon does a terminal outcome reward stop carrying usable learning signal, and can process-level signals be made simultaneously scalable and hack-resistant?

Chapter 3 set up the trade: process rewards buy credit assignment at the cost of new proxies. The frontier moved both directions at once. VinePPO showed that PPO's learned value networks barely outperform a random baseline at ranking alternative reasoning steps, and that unbiased Monte Carlo value estimates beat PPO with up to 9x fewer gradient updates on MATH and GSM8K.[@kazemnejad2024vineppo] Yet the flagship reasoning models dropped process rewards entirely, citing reward hacking and annotation cost, and won with outcome-only signals.[@deepseekai2025r1]

The long-context result from Chapter 9 shows why the outcome-only position cannot be the end state: with answer-only rewards, the gradient for learning to ground on the right evidence provably vanishes early in training, and a dense, exactly-checkable intermediate reward on evidence selection repairs it.[@chen2026longrlvr] That is an existence proof that process-level signals can be verifiable rather than learned, sidestepping the PRM proxy problem for tasks whose intermediate state admits exact checks.

The agentic regime sharpens the question. Credit in reasoning RL spans one generation of 500 to 30K+ tokens; agentic RL spans hundreds of turns and 100K to 1M tokens, where a single episode-level scalar becomes increasingly uninformative, and the methods literature has no shared benchmark for comparing credit-assignment quality.[@zhang2026creditsurvey] What is open: whether outcome rewards plus task structure suffice at these horizons, which intermediate states across domains admit verifiable checks the way evidence chunks do, and whether process signals at scale reimport the over-optimization dynamics of Chapter 7.

## Self-improvement without external verification

**Research question.** Can a model's own signals, such as confidence, self-consistency, or self-judgment, sustain RL improvement, or do self-reward loops inevitably collapse?

The positive evidence is striking. Intuitor uses self-certainty, the average KL divergence from a uniform distribution to the model's next-token distribution over the output, as the sole reward in GRPO, with no gold answers and no test cases, and matches gold-reward GRPO on in-domain math while generalizing better to out-of-domain code generation.[@zhao2025intuitor] Evolutionary variants use majority agreement for selection and novelty for variation, holding diversity open by construction.[@zhou2025evolrl]

The negative evidence is just as clear. Training on majority-vote self-rewards initially improves both performance and the quality of the vote itself, but prolonged training ends in reward hacking of the pseudo-reward with sudden and complete performance collapse, and noising the vote with fewer generations per prompt only delays it.[@shafayat2025selftrain] The elicitation problem bounds the upside from the other direction: spurious and internal signals work mostly on models whose priors already contain the target behavior, and fail to transfer across model families.[@shao2025spurious]

What is open is whether internal signals ever carry task information beyond eliciting priors, whether collapse can be predicted from observables before it happens rather than diagnosed after, and whether any self-improvement loop can exceed the majority-vote ceiling without at least intermittent external grounding.

## Measurement

**Research question.** Given a claimed RLVR result, what evidence suffices to know the capability is real, attributable to the training signal, and free of unpriced costs?

Every previous problem leaks into this one. Contamination can manufacture elicitation results.[@wu2025reasoningmemorization] Apparent algorithmic gains can come from evaluation and normalization artifacts rather than learning.[@liu2025understanding] A position paper cataloging the field's practices finds systematic hidden costs and measurement gaps: undisclosed selection budgets, inconsistent baselines, and regressions outside the target benchmarks that go unreported.[@tu2025hiddenrlvr] Chapter 6 gave the reporting standard for separating policy gains from selection and search gains; Appendix C's regression tax and contamination audit name what a complete report owes beyond that.

Monitoring adds a measurement surface with its own failure mode. A weaker model reading a stronger model's chain of thought catches reward hacking far better than watching actions alone, but using that monitor as a training signal teaches obfuscated hacking, where intent disappears from the trace while the behavior persists.[@baker2025monitoring] A cross-lab position paper argues monitorability is real but fragile, and should be tracked as a first-class property of training decisions.[@korbak2025monitorability] Faithfulness of the trace, in Appendix C's sense, is thus not only an interpretability concern but a precondition for measurement.

What is open: reporting norms with teeth, benchmarks that survive their own popularity, audit protocols priced for optimization pressure rather than average-case error, and a way to keep the evaluation verifier meaningfully independent of the training verifier as both become learned systems.

## The co-adaptation frame

Adaptive RLVR is not one technique. It is a family of updates to the training loop: reweighting prompts to keep them in the model's competence band, hardening verifiers after exploits, changing harness rules after bad trajectories, and updating the policy itself. Written as a state transition, the fully adaptive loop is:

$$
(\pi_t, V_t, \mathcal D_t, \mathcal H_t)
\longrightarrow
(\pi_{t+1}, V_{t+1}, \mathcal D_{t+1}, \mathcal H_{t+1}),
$$ {#eq-ch10-adaptive-system}

where $\pi_t$ is the policy, $V_t$ the verifier stack, $\mathcal D_t$ the task distribution, and $\mathcal H_t$ the harness.

Each component's update is already deployed somewhere, with a concrete signal and a concrete failure mode it repairs:

| Component | Adapts on | Repairs | Seen in |
|---|---|---|---|
| $\mathcal D_t$ task distribution | per-prompt solve rates | zero-gradient groups, drifting competence band | filtering and active sampling (Chapters 5, 8) |
| $V_t$ verifier stack | discovered exploits, audit failures | reward hacking | hardening and red-teaming (Chapter 7) |
| $\mathcal H_t$ harness | logged trajectories, timeout and tool-use statistics | harness-shaped artifacts | agentic training (Chapter 9) |
| $\pi_t$ policy | the reward signal itself | the capability gap | every chapter |

: What adapts, on what signal, to repair which failure mode. {#tbl-ch10-adaptation}

What does not exist is a theory of the joint loop. Each adaptation is stabilizing in isolation; together they form a nonstationary game in which the policy optimizes against a verifier that is being rewritten, on a distribution that is being refiltered, inside a harness that is being repaired. None of the convergence intuitions from static-reward RL apply, and the measurement problem is the only instrument available for telling co-adaptive progress from co-adaptive drift.

That is a fitting place for the book to end, because it is Chapter 1's gap restated at the level of the whole system: every component of the loop is a proxy for something we cannot check directly, and making the loop adaptive multiplies the proxies. The book's wager is that this gap is an engineering surface, not a dead end, and the six problems in this chapter are where that wager gets settled.
