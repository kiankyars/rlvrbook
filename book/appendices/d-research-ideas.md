# Research Ideas {#sec-research-ideas}

This appendix collects experiments that the open problems of Chapter 11 call for. Each entry states the question, what the closest published work already covers as of September 2026, and an experiment that would close the remaining gap. They are sized for a research group rather than a frontier lab, and each one would move a question that the book currently has to leave open.

## Outcome-only RL on problems the base model never solves

**Question.** Can RL with a binary outcome reward, and no hints, teacher data, or curriculum, turn natural problems the base model never solves into reliably solved ones?

**Closest work.** The pieces exist separately. On a code family the base model never solves, standard RL with binary rewards stalled; a dense per-test warm-up, or a well-matched curriculum, unlocked it, though the warm-up failed on a harder family [@sun2025rlgrokking]. On AIME 2025, a 4B model trained with a maximum-likelihood objective solved three problems that neither the base model nor GRPO solved in 4,096 attempts, though "solved" there means at least one success [@tajwar2026maxrl]. Test-time RL on single open problems already compares against a best-of-$N$ baseline with the same sampling budget, but uses continuous rewards [@yuksekgonul2026discover]. MATH-Beyond supplies natural math problems that open models up to 8B fail even with 1,024 samples [@mayilvahanan2025mathbeyond].

**Experiment.** Take problems with base-model pass@4096 of zero, for example from MATH-Beyond. Train with a pure binary outcome reward at two or more model scales, and compare held-out pass@4096 against base-model sampling plus the same verifier with the same total compute. The result separates three outcomes: RL fails without signal, RL finds rare solutions but not reliable ones, or RL makes them reliable.

## An over-optimization law for rubric and judge rewards

**Question.** Does the gap between a learned grader's reward and the true objective follow a predictable law, as Gao et al. found for preference reward models [@gao2023scaling]?

**Closest work.** Gold-versus-proxy curves for judge rewards now exist. Larger non-reasoning judges delay reward hacking, but every policy in one judge-size sweep hacked by the end of training [@liu2026reasoningjudges]; in rubric RL, the training judge's score keeps climbing while a stronger gold judge's score peaks and falls [@yang2026rubricdropout]; and stronger rubric verifiers reduce exploitation without eliminating it [@mahmoud2026rubrichacking]. None of these fits a functional form.

**Experiment.** Train one policy family against rubric judges of graded strength, with a frozen panel of stronger judges as gold. Plot gold and proxy reward against the KL divergence from the initial policy, fit Gao's functional forms, and test whether the fitted coefficients scale with judge size and with verifier recall measured independently. A law of this kind would give practitioners the stopping criterion Chapter 11 says they lack.

## Credit assignment across horizons

**Question.** At what horizon does episode-level credit stop working, and which alternative takes over?

**Closest work.** Method papers compare credit rules at a fixed horizon. Sandbox snapshots with forked sibling rollouts beat PPO, RLOO, GRPO, and VinePPO at matched compute, with the largest gains on the longest tasks [@he2026bpo], and grouping actions by shared environment states gives step-level advantages without extra rollouts [@feng2025gigpo]. A pre-registered comparison warns that "comparisons of credit rules must match effective sample size, or they measure dose, not credit" [@zhang2026creditaudit]. No study varies the horizon.

**Experiment.** On one long-horizon software suite, hold rollout compute fixed and vary the step limit from 50 to 500. Compare episode-level credit, Monte Carlo values from restored sandbox checkpoints, and state-grouped advantages, and score each against Monte Carlo ground truth, matching effective sample size across arms.

## The generation-verification gap as a collapse predictor

**Question.** Does a self-reward loop collapse when the model stops being better at judging answers than at producing them [@song2024mindgap]?

**Closest work.** Collapse under self-rewards is well documented [@shafayat2025selftrain; @zhang2025nofreelunch]. Its timing depends on how well the model's initial confidence tracks correctness, and pseudo-label accuracy declines before performance does [@he2026urlvr; @wang2026rlavr]. Song et al. tracked the gap across a few rounds of offline iterative self-improvement and found that it shrinks toward zero as gains saturate [@song2024mindgap], but no study tracks it on checkpoints of an online self-reward RL run or tests whether its decline predicts when collapse begins.

**Experiment.** Train base models from at least three families with majority-vote, self-certainty, and entropy-minimization rewards on clean, procedurally generated problems, for several times the usual number of steps. At every checkpoint, measure how well the model's own scores separate its correct from its incorrect answers, and test whether the shrinking gap predicts the onset of collapse across families.

## Monitorability of each reward term in a production reward

**Question.** When a reward combines correctness, format, length, and judge terms, which terms erode chain-of-thought monitorability?

**Closest work.** In controlled settings this is largely answered. In toy environments, reward terms on the chain of thought that conflict with the output reward, such as some length penalties and chain-of-thought monitors, reduce monitorability [@kaufmann2026aligned], and at the strongest compression target, 30% of the original reasoning length, length penalties alone cut hint faithfulness by 35% to 39% [@little2026lengthpenalty]. What is missing is attribution inside one realistic multi-term reward at scale.

**Experiment.** Run a multi-domain RLVR recipe with its full reward, then ablate one term at a time, including format rewards, which so far appear only as controls. Track monitorability with a fixed evaluation suite at every checkpoint and attribute the change to each term.

## Frontier-scale verifier audits for agentic tasks

**Question.** How often does an agentic verifier accept outputs that an independent audit would reject, and does that rate grow as the policy learns?

**Closest work.** The method exists at small scale. In math, a stronger model scoring 1,000 sampled queries at each checkpoint exposed a fine-tuned model-based verifier being exploited during RL, while other verifiers stayed aligned with the oracle [@huang2025verifiers]. In code, a preregistered study of GRPO on MBPP found that the rate of rewarded false positives did not grow within its training horizon, and a post-hoc audit of every rewarded false positive found that about half were genuinely wrong code [@zhang2026leakysuite]. Static audits of small samples already find that roughly a quarter of software tasks accept an incorrect patch [@rajan2026auditing].

**Experiment.** During an agentic software RL run, sample accepted trajectories at each checkpoint and audit them with an independent, more expensive check, such as held-out tests written after the fact plus human review of a subsample. Report the false-positive rate over training with confidence intervals, split by task family.
