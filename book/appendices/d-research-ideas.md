# Research Ideas {#sec-research-ideas}

This appendix collects accomplishable ideas from Chapter 11, i.e. sized for a research group rather than a frontier lab.

## Outcome-only RL on problems the base model never solves

**Question.** Can RL with a binary outcome reward, and no hints, teacher data, or curriculum, solve problems the base model never solves?

**Closest work.** Beyond the grokking result in @sec-ch11-elicitation [@sun2025rlgrokking], two results sit close to the clean setting. On AIME 2025, which it was not trained on, a 4B model trained with a maximum-likelihood objective solved three problems at pass@4096 that neither the base model nor GRPO solved, though only 15 of its 12,288 samples on those three were correct [@tajwar2026maxrl]. Test-time RL, which keeps updating the model's weights while it attempts a single open problem, already compares against a best-of-$N$ baseline with the same sampling budget, but uses continuous rewards [@yuksekgonul2026discover].

**Experiment.** Split problems with base-model pass@4096 of zero, for example from MATH-Beyond [@mayilvahanan2025mathbeyond], into training and held-out sets. Because every training rollout fails at first, GRPO gets zero advantage and serves as the control; compare it, at two or more model scales, with a loss that still learns from groups where every rollout fails, such as negative-sample reinforcement [@zhu2025negative], and score pass@1 and pass@4096 on both sets against a fresh base-model draw with the same verifier and the same total sampling compute. The result separates three outcomes: RL fails without signal, RL finds rare solutions but not reliable ones, or RL makes them reliable.

## An over-optimization law for rubric and judge rewards

**Question.** Does the gap between a learned grader's reward and the true objective follow a predictable law, as Gao et al. found for preference reward models [@gao2023scaling]?

**Closest work.** The judge-size and verifier-strength studies in @sec-ch11-reward-hacking track the gap over training steps [@liu2026reasoningjudges; @mahmoud2026rubrichacking], as does rubric RL in which the training judge's score keeps climbing while a stronger gold judge's score peaks and falls [@yang2026rubricdropout].

**Experiment.** Train one policy family against rubric judges of graded strength, with a frozen panel of stronger judges as gold. Plot gold and proxy reward against the KL divergence from the initial policy, fit Gao et al.'s functional forms, and test whether the fitted coefficients scale with judge size and with verifier recall measured independently. A law of this kind would let practitioners predict when to stop, instead of finding out by monitoring a held-out judge.

## Credit assignment across horizons

**Question.** At what horizon does episode-level credit stop working, and which alternative takes over?

**Closest work.** Beyond the frontier approaches in @sec-ch11-credit-assignment, method papers compare credit rules at a fixed horizon. Sandbox snapshots with forked sibling rollouts beat PPO, RLOO, GRPO, and VinePPO at matched compute, with the largest gains on the longest tasks [@he2026bpo], and grouping actions by shared environment states gives step-level advantages without extra rollouts [@feng2025gigpo]. A pre-registered comparison warns that "comparisons of credit rules must match effective sample size, or they measure dose, not credit" [@zhang2026creditaudit].

**Experiment.** On one long-horizon software suite, hold rollout compute fixed and vary the step limit from 50 to 500. Compare episode-level credit, Monte Carlo values from restored sandbox checkpoints, and state-grouped advantages, and score each against Monte Carlo ground truth, matching effective sample size across arms.

## The generation-verification gap as a collapse predictor

**Question.** Does a self-reward loop collapse when the model stops being better at judging answers than at producing them [@song2024mindgap]?

**Closest work.** @sec-ch11-self-improvement reviews the collapse results and the offline finding that the gap shrinks toward zero within two or three rounds of self-improvement.

**Experiment.** Train base models from at least three families with majority-vote, self-certainty, and entropy-minimization rewards on clean, procedurally generated problems, for several times the usual number of steps. At every checkpoint, measure how well the model's own scores separate its correct from its incorrect answers, and test whether the shrinking gap predicts the onset of collapse across families.

## Monitorability of each reward term in a production reward

**Question.** When a reward combines correctness, format, length, and judge terms, which terms erode chain-of-thought monitorability?

**Closest work.** The controlled results in @sec-ch11-reward-hacking test one conflicting reward term at a time, in toy environments and at 14B parameters [@kaufmann2026aligned; @little2026lengthpenalty].

**Experiment.** Run a multi-domain RLVR recipe with its full reward, then ablate one term at a time, including format rewards, which so far appear only as controls. Track monitorability with a fixed evaluation suite at every checkpoint and attribute the change to each term.

## Frontier-scale verifier audits for agentic tasks

**Question.** How often does an agentic verifier accept outputs that an independent audit would reject, and does that rate grow as the policy learns?

**Closest work.** @sec-ch11-reward-hacking describes the method in math, where oracle audits during RL exposed an exploited model-based verifier [@huang2025verifiers], and static audits of software tasks [@rajan2026auditing]. In code, a preregistered study of GRPO on MBPP found that the rate of rewarded false positives did not grow within its training horizon, and a post-hoc audit of every rewarded false positive found that about half were genuinely wrong code [@zhang2026leakysuite].

**Experiment.** During an agentic software RL run, sample accepted trajectories at each checkpoint and audit them with an independent, more expensive check, such as held-out tests written after the fact plus human review of a subsample. Report the false-positive rate over training with confidence intervals, split by task family.
