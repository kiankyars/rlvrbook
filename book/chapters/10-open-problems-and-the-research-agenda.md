# Open Problems and the Research Agenda

![M. C. Escher, _Alfedena Abruzzi_ (1929).](../escher/10-alfedena-abruzzi.jpg){width="80%" fig-align="center"}

## Chapter Map

- Define real RLVR progress under clean measurement, beyond higher reported benchmark scores.
- Turn the book into a research agenda for verifier validity, credit assignment, test-time separation, and deployment-scale feedback.

## What would count as progress?

RLVR can raise benchmark numbers. The hard question is whether the gain came from policy improvement against the task we care about, or from a mixture of policy improvement, extra test-time compute, evaluation artifacts, contamination, and unmeasured costs.

A useful diagnostic decomposition is:

$$
\Delta_{\mathrm{reported}}
=
\Delta_{\mathrm{policy}}
+
\Delta_{\mathrm{search}}
+
\Delta_{\mathrm{eval}}
+
\Delta_{\mathrm{leakage}}
-
\Delta_{\mathrm{tax}}.
$$ {#eq-ch10-reported-gain-decomposition}

Treat this as accounting discipline, not a theorem. $\Delta_{\mathrm{policy}}$ is the capability improvement amortized into the model weights. $\Delta_{\mathrm{search}}$ is the gain from sampling, reranking, tool use, or verifier-guided inference. $\Delta_{\mathrm{eval}}$ is the change induced by metric choices, extraction rules, grader choices, or prompt formats. $\Delta_{\mathrm{leakage}}$ is the apparent improvement from contamination or benchmark familiarity. $\Delta_{\mathrm{tax}}$ is the cost paid elsewhere: calibration loss, refusal loss, instruction-following regression, safety degradation, latency, verifier spend, or human audit burden.

Tu et al. argue that RLVR progress is real, while headline gaps can shrink or disappear under parity-controlled evaluation, contamination checks, and tax-aware protocols.[@tu2025hiddenrlvr] Chapter 10 takes that as the standard. A frontier-grade RLVR claim should say what improved, which verifier produced the signal, which compute path produced the answer, what contamination audit was run, and which capabilities were checked for regressions.

That standard sets the research agenda.

## Problem 1: verifier validity under optimization pressure

A verifier has validity relative to a distribution of model outputs. RLVR changes that distribution.

Let $C(x,y)$ denote the latent correctness property we care about and $V(x,y)$ the verifier's judgment. The relevant error rate is policy-dependent:

$$
\epsilon_V(\pi)
=
\Pr_{x\sim \mathcal D,\,y\sim\pi(\cdot\mid x)}
\left[V(x,y)\ne C(x,y)\right].
$$ {#eq-ch10-policy-dependent-verifier-error}

The usual benchmark report estimates something closer to $\epsilon_V(\pi_0)$, where $\pi_0$ is the base model or an initial checkpoint. RLVR needs $\epsilon_V(\pi_t)$ during training and $\epsilon_V(\pi_\star)$ after optimization. These error rates can diverge. The policy discovers output regions outside the verifier's design range: unusual formats, lucky shortcuts, shallow test-passing strategies, judge-preferred rhetoric, or memorized benchmark mappings.

Chapter 7 framed this as Goodhart's Law. The open problem is measurement during training. A serious verifier-evaluation protocol should track the verifier on policy samples across checkpoints, rather than static held-out examples alone. It should include adversarial false positives, independent verifier disagreement, distributional drift in completions, and human or stronger-system audits at the high-reward tail.

Spurious-reward results make the problem sharper. Yan et al. report that RLVR can activate memorization shortcuts under spurious or incorrect rewards in settings where benchmark items may be contaminated, including a "Perplexity Paradox" where answer-token perplexity falls while prompt-side coherence degrades.[@yan2026spurious] A verifier can appear to improve reasoning while the mechanism of improvement shifts toward a shortcut invisible to the endpoint score.

Track this drift:

$$
\frac{d}{dt}\epsilon_V(\pi_t)
\quad \text{under RLVR optimization.}
$$ {#eq-ch10-verifier-error-drift}

If verifier error grows with optimization pressure, the training run should report it. If it grows in specific subdomains, the curriculum should expose it. If it grows in the accepted high-reward tail, the evaluation should catch it. A mature RLVR science needs verifier drift curves alongside model accuracy curves.

## Problem 2: credit assignment when the reward is correct but too late

Outcome rewards can be correct and still weak. The verifier may know that a final answer is wrong without knowing which earlier decision made it wrong.

For a trajectory with history $h_t$, action $a_t$, and scalar advantage $\hat A$, the update signal for a token or action at time $t$ is:

$$
g_t
=
\hat A\,\nabla_\theta \log \pi_\theta(a_t\mid h_t).
$$ {#eq-ch10-token-credit-signal}

A simple way to state the credit-assignment problem is the signal-to-noise ratio:

$$
\mathrm{SNR}_t
=
\frac{
\left\|\mathbb E[g_t]\right\|
}{
\sqrt{\mathrm{Var}(g_t)}
}.
$$ {#eq-ch10-credit-snr}

Long trajectories make $\mathrm{SNR}_t$ collapse at the place where the model needs guidance: evidence selection, file search, tool choice, subgoal selection, and recovery after failed attempts. The terminal reward may be accurate. It arrives too late to tell the policy which earlier actions helped.

The outcome/process distinction from Chapters 2 and 3 does not end the story. Process rewards are one answer. Long-context grounding rewards, executable subgoal checks, trajectory-level rubrics, unit-test deltas, search trace audits, and environment feedback can also act as intermediate verifiable signals.

LongRLVR gives the cleanest current example. Chen et al. argue that RLVR with final-answer reward alone falters in long-context tasks because the signal is too sparse to guide contextual grounding; they add a verifiable context reward for selecting relevant evidence and report large gains over standard RLVR on long-context benchmarks.[@chen2026longrlvr] The lesson extends beyond that method: when a task requires the model to find the evidence before reasoning over it, final-answer correctness gives an incomplete training signal.

Researchers need intermediate signals that help without becoming hidden teachers. A context reward that checks whether the model cited the right chunk is verifiable if the dataset contains gold evidence. A learned subgoal judge gives weaker evidence. A guidance generator can help while leaking solution structure. As the signal becomes more helpful, evaluators should ask whether the system still trains RLVR over the task or distills through an auxiliary proxy.

## Problem 3: separating train-time learning from test-time search

RLVR systems often combine policy training with test-time verification. The combination creates a reporting problem.

The same verifier can update a policy during training, filter samples during data construction, rank candidates during inference, stop a search procedure, or rerank a tree of partial solutions. Those uses create different sources of improvement. A final score alone cannot tell the reader whether RLVR improved the policy, search improved the output, or the authors used the verifier more at test time.

A minimal frontier-grade report should include:

| Quantity | What it isolates |
|---|---|
| Base pass@1 | The starting policy before RLVR |
| RLVR pass@1 | The amortized policy gain |
| RLVR pass@$N$ | The combined policy-plus-sampling gain |
| Independent-verifier pass@$N$ | Robustness to verifier-specific overfitting |
| Generation compute | How many rollouts, tokens, tool calls, or search steps were used |
| Verification compute | How much scoring, execution, judging, or proof checking was used |
| Contamination status | Whether prompt, answer, and partial-prompt leakage were audited |
| Tax report | Calibration, refusal, instruction-following, safety, latency, or cost regressions |

Snell et al. showed that test-time compute can substitute for model scale depending on problem difficulty.[@snell2024scaling] Chapter 6 used that result to explain search. Chapter 10 uses it as a reporting constraint: if test-time compute is part of the result, it should be budgeted and labeled.

A clean comparison reports four quantities:

$$
\mathrm{score}(\pi_0, N=1),
\quad
\mathrm{score}(\pi_{\mathrm{RLVR}}, N=1),
\quad
\mathrm{score}(\pi_{\mathrm{RLVR}}, N>1),
\quad
\mathrm{score}_{V'}(\pi_{\mathrm{RLVR}}, N>1),
$$ {#eq-ch10-search-reporting}

where $V'$ is an independent or stronger verifier. This separates learned capability from inference-time selection and verifier-specific overfitting. It also makes a weak policy harder to hide behind a strong search budget.

## Problem 4: verifier uncertainty, abstention, and risk-limited RLVR

Binary correctness rewards make accepted answers look safe by default. They do not tell the model when to abstain, when to ask for more evidence, or when the verifier itself is uncertain. Kadavath et al. found that language models can estimate the probability that a proposed answer is true, and Tian et al. found that verbalized confidence can be more informative than raw token probabilities after RLHF.[@kadavath2022language; @tian2023just] Answer correctness alone does not guarantee that behavior.

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

The open problem is to make calibration part of RLVR without destroying the task reward. If $C(x,y)\in\{0,1\}$ is the correctness label and $p_\theta(x,y)$ is the model's stated probability of correctness, a calibrated reward should use a proper scoring rule instead of a correctness bit.[@gneiting2007strictly] Two standard examples are the Brier loss:

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

That still assumes the verifier's correctness label is reliable. In harder systems, the verifier should also have uncertainty. Let $q_V(x,y)$ be the verifier's confidence that its own label is correct. A risk-limited update can downweight uncertain reward:

$$
\hat A_i^{\mathrm{risk}}
=
q_V(x_i,y_i)\,\hat A_i.
$$ {#eq-ch10-risk-weighted-advantage}

Risk weighting moves the problem to verifier calibration, where it belongs. RLVR systems should not give a brittle parse, a flaky unit test, a weak learned judge, and a formal proof checker the same authority.

Abstention remains open. A model trained on correctness alone may learn to answer more often, with worse judgment. Tu et al. argue for protocols that co-optimize accuracy, grounding, and calibrated abstention in RLVR evaluation.[@tu2025hiddenrlvr] For deployed systems, this determines whether the policy learns to abstain, request another tool call, escalate to a human, or emit a wrong answer because the benchmark rewarded decisiveness.

## Problem 5: adaptive verifier-policy systems

The hardest RLVR problem is co-evolving the policy, verifier, curriculum, data distribution, search procedure, and deployment harness without losing measurement.

A realistic system looks like:

$$
(\pi_t, V_t, \mathcal D_t, \mathcal H_t)
\longrightarrow
(\pi_{t+1}, V_{t+1}, \mathcal D_{t+1}, \mathcal H_{t+1}),
$$ {#eq-ch10-adaptive-system}

where $\pi_t$ is the policy, $V_t$ the verifier stack, $\mathcal D_t$ the task distribution, and $\mathcal H_t$ the harness. Each component changes the others. A stronger policy finds verifier holes. A hardened verifier changes which tasks are learnable. A filtered curriculum changes the state distribution. A production harness changes the reward surface. A test-time search policy changes which answers the verifier sees.

Many simple claims about RLVR break in this setting. Harder tasks may produce zero reward and no gradient. A learned judge may become the target. More search may improve answers without improving the policy. A better verifier may move the policy to the boundary of what the verifier checks.

Motivation-enhanced reinforcement finetuning shows how fast the design space changes. Zhang et al. inject a natural-language description of the reward specification into the prompt so the model sees the objective during generation.[@zhang2025merf] That can improve learning efficiency, and it also changes the interface: the reward becomes part of the context the policy reasons over. The verifier specification itself becomes an input channel.

The research agenda should make adaptive systems auditable. Every adaptive RLVR run should report what changed, when it changed, and whether the evaluation changed with it. If the verifier is updated after discovering an exploit, report the exploit and the patch. If the curriculum tracks model competence, report the competence estimator and its failure modes. If the harness changes because production behavior changed, report the instrumentation delta. Frontier systems will be adaptive; reports need to make the adaptivity legible.

## Research program

The table condenses the book's research agenda.

| Open problem | Why it is hard | Minimum credible experiment | Frontier-lab bar | Relevant chapters |
|---|---|---|---|---|
| Verifier drift | RLVR changes the output distribution the verifier sees | Measure $\epsilon_V(\pi_t)$ across checkpoints with an independent audit set | Live verifier-drift monitoring on policy samples, including the accepted high-reward tail | Chapters 4, 7 |
| Credit assignment | Correct terminal rewards can be too delayed to guide initial actions | Compare final-answer reward alone with one verifiable intermediate signal under matched compute | SNR-style diagnostics for evidence selection, tool use, and recovery actions | Chapters 2, 3, 5, 9 |
| Search separation | Test-time verification can hide weak amortized policy gains | Report pass@1, pass@$N$, independent-verifier pass@$N$, generation compute, and verifier compute | Standard scorecards that separate policy quality, search quality, and verifier quality | Chapters 5, 6 |
| Contamination | RLVR can activate memorized shortcuts that look like reasoning gains | Partial-prompt audits and clean held-out sets before and after RLVR | Mechanistic or behavioral contamination dashboards during training | Chapters 1, 7, 8 |
| Calibration and abstention | Correctness rewards omit abstention | Add proper scoring or abstention rewards and report accuracy-calibration tradeoffs | Risk-limited updates weighted by verifier confidence and task risk | Chapters 4, 6 |
| Harness validity | Agentic RLVR turns the whole environment into the reward surface | Ablate tools, timeouts, filters, and rerankers while holding the task distribution fixed | Full harness provenance: tools, sandboxes, filters, rewards, patches, and production instrumentation | Chapter 9 |
| Adaptive RLVR | Policy, verifier, curriculum, and harness co-evolve | Log each verifier/curriculum change and evaluate pre/post on a stable audit suite | Treat verifier updates like model updates: versioned, audited, and stress-tested | Chapters 4, 5, 7, 9 |

## Closing

RLVR works because many important capabilities expose checkable artifacts. The hard work begins after the system finds that artifact.

The hard version of RLVR asks five questions at once: what the verifier checks, how that score becomes a policy update, how the policy changes the distribution seen by the checker, how much of the result comes from search rather than learning, and what breaks when deployment turns the harness into part of the reward surface.

This book treats RLVR as the study of learning from verifiable reward signals. The next stage is making those signals remain trustworthy when researchers optimize them, scale them, search over them, attack them, and embed them in real systems.
