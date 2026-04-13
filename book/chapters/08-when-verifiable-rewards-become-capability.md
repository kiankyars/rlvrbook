# When Verifiable Rewards Become Capability

![M. C. Escher, _Morano Calabria_ (1930).](../escher/08-morano-calabria.jpg){width="80%" fig-align="center"}

## Chapter Map

- Treat public RLVR recipes as proxies for the tacit training knowledge that frontier labs rarely publish in full.
- Separate real pass@1 policy improvement from search, verifier overfitting, contamination, and recipe scaffolding.

## Public recipes as tacit-knowledge proxies

The central capabilities question is not whether RLVR can raise benchmark scores. Chapter 6 already showed how search and verifier-guided selection can do that. The harder question is whether RLVR changes the model itself: after training, with no extra test-time search and no privileged verifier at inference, does the policy solve more problems?

The best labs have tacit knowledge here: task filters, rollout budgets, batch construction, stop conditions, entropy management, code paths for long generations, and failure modes discovered only after expensive runs. We should not pretend that public reports expose all of that knowledge. Tulu 3 states the transparency problem directly: post-training data and recipes are both central and underreported in the open literature.[@lambert2024tulu3]

But public reports are still useful proxies. DeepSeek-R1, Kimi k1.5, Open-Reasoner-Zero, DAPO, Skywork-OR1, MiMo, Qwen3, OLMo 3, and later scaling studies expose enough recurring structure to teach the reader what the public frontier has learned.[@deepseekai2025r1; @team2025kimi; @hu2025openreasonerzero; @yu2025dapo; @he2025skyworkor1; @xia2025mimo; @yang2025qwen3; @teamolmo2025olmo3; @khatri2025scalerl; @tan2025scalingbehaviors] The point of this chapter is to compress those recipes into a capability model.

## The capability claim

A clean RLVR capability claim should look like:

$$
\Delta_{\mathrm{policy}}
=
\mathrm{Score}_{V'}(\pi_{\mathrm{RL}}, N=1)
-
\mathrm{Score}_{V'}(\pi_{0}, N=1),
$$ {#eq-ch8-policy-gain}

where $\pi_0$ is the starting policy, $\pi_{\mathrm{RL}}$ is the trained policy, $N=1$ means no best-of-$N$ search, and $V'$ is an evaluation verifier that is independent from the training verifier when possible.

This is stricter than "the system score improved." A score can improve because the policy improved, because more samples were drawn, because the verifier was used at test time, because extraction changed, because the benchmark leaked, or because the model learned the evaluator's quirks. Chapter 10 turns that into a research agenda. Here we ask what has to be true for the first term in @eq-ch8-policy-gain to be large.

The short answer is: RLVR improves capability when the base model can occasionally find useful trajectories, the task distribution keeps enough prompts in the learnable band, the verifier remains valid on policy samples, and the optimizer preserves enough exploration to avoid premature collapse.

## The simple loop is not the recipe

The visible RLVR loop is simple:

1. Sample multiple completions.
2. Extract, canonicalize, and reward each completion.
3. Increase the probability of completions that scored well.
4. Repeat on related prompts.

That loop is accurate, but it hides the hard engineering. The same loop can produce capability, format overfitting, reward hacking, or no learning at all. The difference is the recipe around the loop.

Current open recipes repeatedly expose six control surfaces:

| Control surface | Capability role | Typical public proxy |
|---|---|---|
| Starting policy | Determines which solution families can be sampled at all | Base model versus instruct model; small versus large model |
| Task filter | Keeps prompts inside the learnable band | Offline difficulty filtering and data resampling |
| Online curriculum | Keeps the batch useful as the policy improves | Per-batch filtering, difficulty schedules, and repeated data |
| Exploration control | Prevents premature convergence to one answer mode | Entropy management, dynamic sampling, relaxed clipping, and novelty rewards |
| Auxiliary rewards | Stabilize the interface without becoming the main target | Format, language-consistency, length, and search-use rewards |
| Reporting protocol | Separates policy improvement from system improvement | pass@1, pass@$N$, independent verifier, and contamination checks |

: The public recipe surfaces that most directly determine whether RLVR becomes capability. {#tbl-ch8-recipe-surfaces}

## The competence band

With binary outcome rewards, a prompt gives little learning signal if every sampled completion fails or every sampled completion succeeds. For a prompt $x$, sample $K$ completions and assign binary rewards $r_1,\ldots,r_K$. The empirical success rate is:

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

The previous expression is zero when $\widehat p_x=0$ or $\widehat p_x=1$, and largest near $\widehat p_x=1/2$. That is the mathematical version of the folk recipe: train on problems the model sometimes solves.

This is why difficulty filtering is not a minor data-cleaning step. It is a precondition for gradient signal. The public reasoning recipes repeatedly use variants of offline filtering, online filtering, data resampling, curriculum scheduling, or repeated high-quality data reuse.[@team2025kimi; @hu2025openreasonerzero; @xia2025mimo; @tan2025scalingbehaviors] ScaleRL sharpens the point: many recipe choices change compute efficiency more than the asymptotic performance ceiling, which means a technique can matter enormously even when it is not the ultimate source of capability.[@khatri2025scalerl]

## The support problem

RLVR does not magically create trajectories the policy never samples. If a useful solution family has probability $p$ under the current policy and we draw $K$ rollouts, the chance of seeing it at least once is:

$$
1-(1-p)^K.
$$ {#eq-ch8-sample-support}

If $p$ is tiny, the reward function may be perfect and still never touch that behavior. RLVR can strongly reinforce rare good behaviors once they appear, but it is constrained by the policy's support and by the sampling budget.

This is the strongest skeptical reading of current RLVR. The Invisible Leash paper argues that RLVR often improves pass@1 by amplifying high-reward answers already accessible to the base model, while answer-level diversity can shrink under training.[@wu2025invisibleleash] That does not make RLVR fake. It says the first-order mechanism is reweighting sampled behavior, not unconstrained invention.

Open recipes respond to this support problem in different ways. DAPO exposes dynamic sampling and decoupled clipping as part of a reproducible large-scale RL recipe.[@yu2025dapo] Skywork-OR1 studies entropy collapse directly and reports that mitigating premature collapse is important for test performance.[@he2025skyworkor1] EVOL-RL, in a label-free setting, explicitly adds novelty pressure because majority-only self-confirmation can collapse diversity.[@zhou2025evolrl] Kimi k1.5 emphasizes long-context scaling and policy optimization rather than tree search or PRMs, making longer rollouts part of the exploration substrate.[@team2025kimi]

The capability lesson is precise: if RLVR improves a model, it usually does so by changing which already-sampleable behaviors become reliable. Expanding the boundary requires enough exploration, enough prompt diversity, or enough auxiliary structure to seed probability mass into useful regions that were previously too rare.

## Scaffolding is not the same as capability

Many public recipe details are scaffolds. They can be necessary without being the capability itself.

Format rewards make extraction stable. Language-consistency rewards make multilingual thinking predictable. Length penalties and thinking budgets control overlong or underlong reasoning. Batch-level normalization changes which examples dominate the update. KL removal or relaxed clipping allows larger movement away from the reference policy. Off-policy or asynchronous generation changes throughput when completions are long and variable.

These details should not be described as separate theories of intelligence. They are capability plumbing. DeepSeek-R1 uses simple accuracy and format-style rewards to make pure RL workable before adding cold-start and distillation stages.[@deepseekai2025r1] Qwen3 exposes thinking and non-thinking modes plus a thinking budget as a user-facing way to trade latency against reasoning effort.[@yang2025qwen3] MiMo combines verifiable math and programming data with a test-difficulty-driven code reward and strategic resampling to reduce sparse-reward problems.[@xia2025mimo]

The reader should learn a sharper distinction:

| Recipe component | What it can improve | What it does not prove |
|---|---|---|
| Format reward | Parseability and stable reward assignment | Better reasoning |
| Length penalty | Token budget and overthinking control | Correctness at fixed budget |
| Difficulty filtering | Gradient density | Generalization beyond the filtered distribution |
| Entropy control | Exploration and delayed collapse | Discovery of solutions outside policy support |
| Repeated data reuse | More optimization over scarce high-quality prompts | Independence from the training set |
| pass@$N$ reporting | Search-scaled system performance | Amortized pass@1 policy improvement |

: Recipe scaffolds are often necessary for capability training but should not be mistaken for the capability claim. {#tbl-ch8-scaffolds}

## What would persuade us?

The cleanest positive evidence is boring: pass@1 improves under fixed decoding on clean held-out tasks, the training verifier is not reused as the only evaluation authority, the result survives contamination audits, and adjacent capabilities do not collapse.

Several public results are useful because they stress different parts of that test. Tulu 3 reports RLVR as one stage of a broad post-training recipe and emphasizes unseen evaluations and decontamination.[@lambert2024tulu3] Open-Reasoner-Zero reports a minimalist PPO recipe with rule-based rewards and no KL regularization, plus analyses of training dynamics and repetition.[@hu2025openreasonerzero] Skywork-OR1 and DAPO make the recipe itself more reproducible by releasing code, data, and ablations.[@he2025skyworkor1; @yu2025dapo] ScaleRL and the mathematical-reasoning scaling study turn scattered recipes into scaling questions about compute, data reuse, model size, and performance ceilings.[@khatri2025scalerl; @tan2025scalingbehaviors]

The skeptical evidence is equally important. Reasoning-or-Memorization argues that some surprising RL gains on common math benchmarks are unreliable under contamination, and recommends clean generated benchmarks plus multiple model families.[@wu2025reasoningmemorization] The Invisible Leash warns that pass@1 gains can coincide with shrinking answer support.[@wu2025invisibleleash] Those results are not anti-RLVR. They define the burden of proof for a capabilities chapter.

## Beyond math

The public frontier started with math and code because they expose dense enough verifiable artifacts. But a capabilities-first book should not imply that RLVR is only competition math.

Med-RLVR studies medical multiple-choice reasoning and reports that RLVR can match SFT in distribution while improving out-of-distribution generalization by 8 points.[@zhang2025medrlvr] VerIF studies instruction following with verification engineering, combining rule-based code verification with LLM-based verification and reporting generalization to unseen constraints.[@peng2025verif] Chapter 9 moves the same question into long-context, multimodal, and agentic settings where the reward becomes a harness rather than a single answer checker.

These examples matter because they test the abstraction. If RLVR is merely exact-match math fine-tuning, it is narrow. If it is a way to turn reliable feedback from a task environment into amortized policy improvement, it is a broader capability method. The limiting factor is the verifier surface: what the system can check cheaply, repeatedly, and robustly while the policy changes.

## The compressed lesson

The public frontier suggests a careful claim:

RLVR can create real capability gains, but not because a binary reward is magic. It works when the model already has enough latent competence to occasionally sample correct behavior, the task distribution keeps producing discriminative rewards, the optimizer does not destroy exploration too early, and the evaluation separates policy learning from search and contamination.

This is the tacit recipe in its most useful public form. The verifier supplies the score, but the capability comes from the whole training system around the score.

## Open questions

- Which recipe choices shift the asymptotic capability ceiling, and which only improve compute efficiency?
- How should we measure expansion of model support rather than only reweighting within existing support?
- What is the right difficulty estimator when the training domain is not math or code?
- How much auxiliary scaffolding can be added before the result is no longer clean RLVR?
- Which contamination audits are sufficient for modern reasoning benchmarks?

## What comes next

Chapter 9 applies the capability frame to long-context, multimodal, and agentic RLVR. In those settings, the verifier is no longer just an answer checker; it becomes a harness that observes tools, files, environments, retrieved evidence, and long trajectories.
