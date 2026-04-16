# Open Problems

![M. C. Escher, _Alfedena Abruzzi_ (1929).](../escher/10-alfedena-abruzzi.jpg){width="80%" fig-align="center"}

## Chapter Map

- Capability gains can hide support concentration, memorized mappings, and verifier shortcuts.
- Long rollouts need denser credit; weak domains need coverage estimates, calibrated abstention, and audited verifier changes.

## Problem 1: capability expansion versus shortcut amplification

A higher RLVR score can come from probability reallocation. The model can put more mass on solution templates the base model could sample, memorized answer mappings, or outputs that satisfy the verifier's surface rules.

Capability expansion requires evidence that the model reaches solution families the base policy assigned little probability to and that those families transfer outside the training distribution. Shortcut amplification appears when reward selects memorized mappings, shallow templates, or verifier-specific formats.

Yan et al. give the sharp example: under spurious or incorrect rewards, RLVR can activate memorization shortcuts, including a "Perplexity Paradox" where answer-token perplexity falls while prompt-side coherence degrades.[@yan2026spurious] A reader who reads the endpoint score alone cannot tell whether the model learned robust reasoning or found a shortcut.

Researchers need to distinguish capability expansion from precision sharpening. A run should report whether the model solves new problem families, transfers out of distribution, preserves solution diversity, and remains correct under independent verifier checks.

Measure support movement for a solution family $S$ under policy $\pi_t$:

$$
m_t(S)
=
\Pr_{x\sim \mathcal D,\,y\sim \pi_t(\cdot\mid x)}
\left[y\in S\right].
$$ {#eq-ch10-support-mass}

If $m_t(S)$ rises for common patterns, RLVR may be a precision enhancer. If it rises for rare valid strategies that transfer to clean held-out tasks, the run gives stronger evidence of capability expansion. The same evaluation should include contamination audits, partial-prompt checks, and shortcut stress tests.

## Problem 2: sparse rewards and delayed credit

Outcome rewards can be correct and still weak. The verifier may know that a final answer is wrong without knowing which earlier decision made it wrong.

For a trajectory with history $h_t$, action $a_t$, and scalar advantage $\hat A$, the update signal for a token or action at time $t$ is:

$$
g_t
=
\hat A\,\nabla_\theta \log \pi_\theta(a_t\mid h_t).
$$ {#eq-ch10-token-credit-signal}

Track the sparse-credit problem with the signal-to-noise ratio:

$$
\mathrm{SNR}_t
=
\frac{
\left\|\mathbb E[g_t]\right\|
}{
\sqrt{\mathrm{Var}(g_t)}
}.
$$ {#eq-ch10-credit-snr}

In long trajectories, $\mathrm{SNR}_t$ can collapse where the model needs guidance: evidence selection, file search, tool choice, subgoal selection, and recovery after failed attempts. The terminal reward may be accurate. It arrives too late to tell the policy which earlier actions helped.

Chapters 2 and 3 give one remedy: process rewards. Long-context grounding rewards, executable subgoal checks, trajectory-level rubrics, unit-test deltas, search trace audits, and environment feedback can also act as intermediate verifiable signals.

Chen et al.'s LongRLVR shows the failure mode. They argue that final-answer reward alone gives too little signal for long-context grounding; their method adds a verifiable context reward for selecting relevant evidence and reports large gains over standard RLVR on long-context benchmarks.[@chen2026longrlvr]

Researchers need intermediate signals that help without turning reward into a hidden teacher. A context reward is verifiable if the dataset contains gold evidence. A learned subgoal judge gives weaker evidence. A guidance generator can leak solution structure. When an auxiliary signal provides too much structure, evaluators must check that the system still learns the task rather than distilling a proxy.

## Problem 3: verifier fidelity beyond math and code

RLVR works when the verifier checks an exact artifact: a normalized math answer, a passing test suite, or a proof object accepted by a kernel. Harder domains expose a slice of the target behavior to the verifier.

In long-context QA, answer-evidence checks can miss unsupported synthesis. In multimodal search, final-answer and tool-format rewards can miss visual grounding. In agentic software tasks, tests can miss maintainability, security, minimality, and user intent. In instruction following, many constraints require semantic judgment rather than exact checking.[@peng2025verif; @brown2025verifiers; @tan2025rllm]

Medical and scientific tasks raise the cost of proxy rewards. A verifier may check a final label, citation, or structured field while missing whether the model used the right evidence, respected uncertainty, or made a decision a clinician would trust. Med-RLVR matters here because it pushes RLVR into a domain with partial verifiability and higher task risk.[@zhang2025medrlvr]

Learned judges extend coverage when programmatic checks fail. They also import judge bias, calibration gaps, and attack surfaces.[@zheng2023judging; @lambert2024rewardbench] Training systems need audit procedures for these weaker reward channels.

Define verifier coverage as:

$$
\kappa(V; \mathcal T)
=
\Pr_{(x,y)\sim \mathcal T}
\left[V \text{ observes the property that determines task success}\right].
$$ {#eq-ch10-verifier-coverage}

Math and formal proof have high $\kappa$ for their target artifacts. Long-context QA, multimodal agents, and instruction-following systems often have lower $\kappa$: the verifier sees a proxy, not the whole property. A system that leaves math and code must raise $\kappa$, estimate it, or design training objectives that still work when $\kappa<1$.

## Problem 4: verifier uncertainty, abstention, and risk-limited RLVR

Binary correctness rewards make accepted answers look safe by default. They do not tell the model when to abstain, ask for more evidence, or treat the verifier itself as uncertain. Kadavath et al. found that language models can estimate the probability that a proposed answer is true, and Tian et al. found that verbalized confidence can be more informative than raw token probabilities after RLHF.[@kadavath2022language; @tian2023just]

Calibration is distributional. If the model emits confidence $p(X)\in[0,1]$ and correctness is $C\in\{0,1\}$, perfect calibration means:

$$
\mathbb E[C \mid p(X)=p] = p.
$$ {#eq-ch10-calibration}

Finite-data evaluations approximate calibration with bins:

$$
\mathbb E[C \mid p(X)\in B_j]
\approx
\mathbb E[p(X) \mid p(X)\in B_j].
$$ {#eq-ch10-calibration-bins}

A single verified answer cannot certify confidence. Calibration relates stated probabilities to empirical frequencies across many examples.

RLVR needs calibration terms that do not overwhelm the task reward. If $C(x,y)\in\{0,1\}$ is the correctness label and $p_\theta(x,y)$ is the model's stated probability of correctness, a calibrated reward should use a proper scoring rule instead of a correctness bit.[@gneiting2007strictly] Two standard examples are the Brier loss:

$$
S_{\mathrm{Brier}}(p,C) = (p-C)^2
$$ {#eq-ch10-brier}

and the log loss:

$$
S_{\log}(p,C)
=
- C \log p - (1-C)\log(1-p).
$$ {#eq-ch10-log-loss}

A calibrated reward can then include the proper-scoring term:

$$
r(x,y,p_\theta)
=
r_{\mathrm{task}}(x,y)
-
\lambda S(p_\theta, C(x,y)).
$$ {#eq-ch10-calibrated-rlvr}

This reward assumes the verifier's correctness label is reliable. In harder systems, the verifier should also have uncertainty. Let $q_V(x,y)$ be the verifier's confidence that its own label is correct. A risk-limited update can downweight uncertain reward:

$$
\hat A_i^{\mathrm{risk}}
=
q_V(x_i,y_i)\,\hat A_i.
$$ {#eq-ch10-risk-weighted-advantage}

Designers should put uncertainty on the verifier side. RLVR systems should not give a brittle parser, a flaky unit test, a weak learned judge, and a formal proof checker the same authority.

Correctness rewards alone can push models to answer when they should abstain. Tu et al. argue for protocols that co-optimize accuracy, grounding, and calibrated abstention in RLVR evaluation.[@tu2025hiddenrlvr]

## Problem 5: adaptive verifier-policy systems

Adaptive RLVR systems co-evolve the policy, verifier, curriculum, task distribution, and deployment harness. Measurement has to survive those changes.

Write the loop as:

$$
(\pi_t, V_t, \mathcal D_t, \mathcal H_t)
\longrightarrow
(\pi_{t+1}, V_{t+1}, \mathcal D_{t+1}, \mathcal H_{t+1}),
$$ {#eq-ch10-adaptive-system}

where $\pi_t$ is the policy, $V_t$ the verifier stack, $\mathcal D_t$ the task distribution, and $\mathcal H_t$ the harness. A stronger policy finds verifier holes. A hardened verifier changes which tasks are learnable. A filtered curriculum changes the state distribution. A production harness changes the reward surface.

These feedback loops break static claims about RLVR. Harder tasks may produce zero reward and no gradient. A learned judge may become the target. A better verifier may move the policy to the boundary of what the verifier checks. A curriculum may improve average reward while narrowing the distribution of practiced skills.

Motivation-enhanced reinforcement finetuning shows how a small interface change can alter training. Zhang et al. inject a natural-language description of the reward specification into the prompt so the model sees the objective during generation.[@zhang2025merf] The prompt now carries reward specification, so the policy can reason over the verifier's objective.

Adaptive RLVR needs audit logs. Researchers should report what changed, when it changed, and whether the evaluation changed with it. If researchers update the verifier after discovering an exploit, report the exploit and the patch. If the curriculum tracks model competence, report the estimator and its failure modes. If engineers change the harness because production behavior changed, report the instrumentation delta.
