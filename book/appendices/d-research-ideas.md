# Research Ideas {#sec-research-ideas}

This appendix collects accomplishable ideas from Chapter 11, i.e. sized for a research group rather than a frontier lab. Each idea starts from a question the chapter leaves open, says what the closest published work has and has not shown, and ends with an experiment that would settle it.

## Outcome-only RL on problems the base model never solves

Can RL with a binary outcome reward, and no hints, teacher data, or curriculum, solve problems the base model never solves? The grokking result in @sec-ch11-elicitation needed a warm-up or a matched curriculum to get going [@sun2025rlgrokking], and two other results sit close to the setting without answering it. A 4B model trained with MaxRL, a maximum-likelihood objective rather than a plain binary reward, solved three AIME 2025 problems at pass@4096 that neither the base model nor GRPO solved, and AIME 2025 was not in its training data, which is the closest existing answer to the question [@tajwar2026maxrl]. TTT-Discover keeps updating the model's weights with RL while it attempts a single open problem, and with the same 25,600 samples from gpt-oss-120b it beat best-of-$N$ on every problem where the paper reports that baseline; its best kernel for the GPUMode TriMul task ran in 1,161 microseconds on an H100 against 5,390 for best-of-$N$ and 1,371 for the best human entry. It uses continuous rewards rather than a binary one, though, and its own ablation shows that most of the gap over best-of-$N$ comes from its search, which starts each new attempt from the best solutions found so far instead of from scratch, and that updating the weights adds the rest [@yuksekgonul2026discover].

The experiment:

1. Take problems with base-model pass@4096 of zero, for example MATH-Beyond problems, which no open model of up to 8B parameters solves in any of 1,024 attempts [@mayilvahanan2025mathbeyond], re-screened at 4,096 samples for the chosen base model, and split them into training and held-out sets.
2. Train with GRPO as the control: every rollout fails at first, so its advantage is zero and it should learn nothing. Compare it, at two or more model scales, with a loss that still learns from groups in which every rollout fails, such as negative-sample reinforcement [@zhu2025negative].
3. Score pass@1 and pass@4096 on both sets against a fresh base-model draw with the same verifier and the same total sampling compute.

The result separates three outcomes: RL fails without signal, RL finds rare solutions but not reliable ones, or RL makes them reliable.

## An over-optimization law for rubric and judge rewards

Does the gap between a learned grader's reward and the true objective follow a predictable law, as Gao et al. found for preference reward models [@gao2023scaling]? The judge-size and verifier-strength studies in @sec-ch11-reward-hacking track the gap over training steps [@liu2026reasoningjudges; @mahmoud2026rubrichacking], as does a rubric-RL study in which the training judge's score keeps climbing while a stronger gold judge's score peaks and falls [@yang2026rubricdropout]. None of them fits a law: no study plots gold reward against the KL divergence from the initial policy and fits a functional form to it, which is what made Gao et al.'s result a law rather than an observation.

The experiment:

1. Train one policy family against rubric judges of graded strength, with a frozen panel of stronger judges as gold.
2. Plot gold and proxy reward against the KL divergence from the initial policy and fit Gao et al.'s functional forms.
3. Test whether the fitted coefficients scale with judge size and with verifier recall measured independently.

A law of this kind would let practitioners predict when to stop, instead of finding out by monitoring a held-out judge.

## Credit assignment across horizons

At what horizon does episode-level credit stop working, and which alternative takes over? @sec-ch11-credit-assignment covers the frontier approaches; the method papers compare credit rules only at a fixed horizon. Branching Policy Optimization snapshots the sandbox mid-episode and forks sibling rollouts from the snapshot to estimate each step's value; it beat PPO, RLOO, GRPO, and VinePPO at matched compute, with the largest gains on the longest tasks [@he2026bpo]. GiGPO instead groups actions by shared environment states to get step-level advantages without extra rollouts [@feng2025gigpo]. A pre-registered comparison warns that "comparisons of credit rules must match effective sample size, or they measure dose, not credit" [@zhang2026creditaudit].

The experiment:

1. On one long-horizon software suite, hold rollout compute fixed and vary the step limit from 50 to 500.
2. Compare episode-level credit, Monte Carlo values from restored sandbox checkpoints, and state-grouped advantages, matching effective sample size across arms.
3. Score each against Monte Carlo ground truth at every horizon.

## The generation-verification gap as a collapse predictor

Does the closing of the generation-verification gap predict when a self-reward loop collapses? @sec-ch11-self-improvement establishes that such loops do collapse, and that in offline self-improvement the gap shrinks toward zero within two or three rounds [@song2024mindgap]. What no study has tested is whether the gap's decline, measured during training, predicts the collapse before it happens.

The experiment:

1. Train base models from at least three families with majority-vote and self-certainty rewards on procedurally generated problems the models cannot have memorized, for several times the usual number of steps.
2. At every checkpoint, measure how well the model's own scores separate its correct from its incorrect answers.
3. Test whether the shrinking gap predicts the onset of collapse across families.

## Monitorability of each reward term in a production reward

When a reward combines correctness, length, and judge terms, which terms erode chain-of-thought monitorability? The controlled results in @sec-ch11-reward-hacking test one conflicting reward term at a time, in toy environments with models up to 27B parameters and, for length penalties alone, on Qwen3-14B [@kaufmann2026aligned; @little2026lengthpenalty]. No study ablates the terms of a production reward.

The experiment:

1. Run a multi-domain RLVR recipe with its full reward.
2. Ablate one term at a time, and track monitorability with a fixed evaluation suite at every checkpoint.
3. Attribute the change in monitorability to each term.

## Frontier-scale verifier audits for agentic tasks

How often does an agentic verifier accept outputs that an independent audit would reject, and does that rate grow as the policy learns? @sec-ch11-reward-hacking describes two precedents: oracle audits during RL in math, which exposed an exploited model-based verifier [@huang2025verifiers], and static audits of software tasks [@rajan2026auditing]. In code, a preregistered study trained 1B to 1.5B models with GRPO on MBPP, a benchmark of short Python problems each checked by about three test cases, and counted the rewarded false positives: solutions that passed those three tests, and so earned reward, but failed the roughly one hundred extra tests per problem of MBPP+. Their share of rewarded rollouts did not grow over 400 to 800 training steps, and an audit of every one of them found that about half were genuinely wrong code that the three tests had let through, while the rest were faults of the stricter suite, such as defective extra tests or inputs outside the task's contract [@zhang2026leakysuite].

The experiment:

1. During an agentic software RL run, sample accepted trajectories at each checkpoint.
2. Audit them with an independent, more expensive check: held-out tests written after the fact plus human review of a subsample, or a frontier model of the next generation as the auditor, on tasks the previous generation had already saturated.
3. Report the false-positive rate over training with confidence intervals, split by task family.
