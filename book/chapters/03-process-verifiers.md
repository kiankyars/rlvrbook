# Process Verifiers

![M. C. Escher, _The Bridge_ (1930).](../art/escher/03-the-bridge.jpg){width="80%" fig-align="center"}

## Chapter Map

- Explain when intermediate verification improves credit assignment beyond final-answer rewards alone.
- Show the main risk: rewarding reasoning-shaped traces that correlate weakly with actual competence.

## The credit assignment problem

Chapter 2 elucidated that the scorer assigns a single scalar to the entire trajectory, and the optimizer spreads that scalar across every token. If the answer is correct, every step in the reasoning trace gets reinforced equally. If the answer is wrong, every step gets suppressed equally. The verifier has no opinion about which steps helped.

Consider two ways the quadratic example from Chapter 2 can blur credit assignment:

In the first scenario, the model starts down a wrong branch: it factors $x^2-5x+6$ as $(x-1)(x-6)$, then notices on expansion that this gives $x^2-7x+6$ rather than $x^2-5x+6$, restarts, and correctly factors as $(x-2)(x-3)$. The final answer is still $\{2, 3\}$, so the outcome verifier returns $r = 1$. But the rewarded trajectory now contains both a bad factoring attempt and a good recovery. Over many training iterations, outcome-only credit assignment cannot cleanly reinforce the recovery while suppressing the wrong intermediate move.

In the second scenario, the model reasons correctly through every step — factoring, solving, collecting — but then writes only the first root in the final `<answer>` tag, for example `<answer>x = 2</answer>`, instead of the full solution set $\{2,3\}$. The outcome verifier returns $r = 0$. Five correct reasoning steps are suppressed because the final reported artifact is incomplete. The optimizer cannot distinguish a five-step correct trajectory with a bad endpoint from a five-step incorrect trajectory.

Both scenarios compress distinct kinds of signal. The second is a clear false negative: correct reasoning is suppressed because the final reported answer is incomplete. The first is more subtle. It is not a wholly bad trajectory, because the restart and recovery are exactly the kind of self-correction we may want the model to learn. But outcome reward still reinforces the failed factoring attempt and the successful recovery together, even though they should not receive the same effective update. This is one of the main motivations for process supervision. Uesato et al. found that process-based feedback produced substantially cleaner reasoning traces than outcome-based feedback even when final-answer accuracy was similar, and Lightman et al. later showed that process reward models outperform outcome-only reward models on harder math reasoning tasks.[@uesato2022solving; @lightman2023letsverify] We return in Chapter 5 to the harder question of how training systems can weight partially good trajectories without rewarding every token in the rollout equally.

Instead of scoring only the final artifact, a process verifier assigns a label or score to each intermediate step. The hope is that denser feedback gives the optimizer better information about which parts of a trajectory to reinforce and which to suppress. But this hope is only warranted when two conditions hold: the intermediate steps must be externalized (written down in a form the verifier can read), and the notion of a "correct step" must be definable with enough fidelity to be useful.

## A step-level rollout

Return to the quadratic from Chapter 2. The two tables below make the two failure patterns explicit at step level.

| Step | Reasoning | Label |
|:-----|:----------|:-----:|
| 1 | Recognize the quadratic and decide to factor: $x^2 - 5x + 6 = (x-2)(x-3)$ | $\checkmark$ |
| 2 | Set first factor to zero: $x - 2 = 0 \implies x = 2$ | $\checkmark$ |
| 3 | Set second factor to zero: $x - 3 = 0 \implies x = 3$ | $\checkmark$ |
| 4 | Collect the full solution set: $\{2, 3\}$ | $\checkmark$ |
| 5 | Report the final artifact as `<answer>x = 2</answer>` | $\times$ |

: A trajectory whose internal reasoning is correct but whose final reported artifact is incomplete. An outcome verifier assigns $r = 0$ because the checked answer is wrong. A process verifier can still preserve positive signal on the earlier correct steps. {#tbl-ch3-correct-rollout}

Now consider a subtly flawed version of the same trajectory:

| Step | Reasoning | Label |
|:-----|:----------|:-----:|
| 1 | Recognize the quadratic and attempt to factor: $x^2 - 5x + 6 = (x-1)(x-6)$ | $\times$ |
| 2 | Expand to check: $(x-1)(x-6) = x^2 - 7x + 6$, so this branch cannot be right | $\checkmark$ |
| 3 | Restart and correctly factor as $(x-2)(x-3)$ | $\checkmark$ |
| 4 | Solve to get $\{2, 3\}$ | $\checkmark$ |

: A trajectory where step 1 is incorrect but the model explicitly detects the mismatch and recovers. The outcome verifier assigns $r = 1$ because the final answer is right. A process verifier labels the initial factoring move as wrong while preserving positive signal for the diagnostic and recovery steps. {#tbl-ch3-flawed-rollout}

The two trajectories fail in opposite directions. In the first, outcome verification suppresses a mostly good rollout because the final reported answer is incomplete. In the second, it rewards a mixed rollout because the final answer is right. The process verifier distinguishes both cases. It can preserve signal on the correct intermediate reasoning in the first table while suppressing the bad initial factoring move and reinforcing the recovery in the second. This is the credit assignment advantage of process verification: it can separate the good parts of a trajectory from the bad parts even when endpoint-only reward cannot.

## What a process reward model computes

An outcome reward model (ORM) is a function of the complete trajectory:

$$
\text{ORM}(x, y) \in [0, 1]
$$ {#eq-ch3-orm}

A process reward model (PRM) is more naturally defined at the level of steps, not whole trajectories. Given a prompt $x$ and a stepwise solution with segments $s_1,\dots,s_K$, a PRM outputs a score for each step boundary:

$$
\text{PRM}(s_t \mid x, s_{<t})
$$ {#eq-ch3-prm}

In the human-labeled formulations of Uesato et al. and Lightman et al., this score is trained to predict whether the current step is good, bad, or neutral, or equivalently the probability that the step is valid given the preceding context.[^ch3-prm-formulation] In Math-Shepherd, the step score is instead estimated from rollouts: a step is scored by how often continuations from that partial solution reach the correct final answer.[@uesato2022solving; @lightman2023letsverify; @wang2024mathshepherd]

If a downstream system needs a single score for an entire solution, that requires an additional reduction over step scores:

$$
\text{Score}(x, y) = \operatorname{Agg}\bigl(\text{PRM}(s_1 \mid x), \ldots, \text{PRM}(s_K \mid x, s_{<K})\bigr).
$$ {#eq-ch3-prm-trajectory}

That aggregation is not unique. Math-Shepherd uses the minimum step score when reranking full solutions in a best-of-$N$ verification setting, reflecting the intuition that one invalid step can sink an otherwise plausible derivation.[@wang2024mathshepherd] Other uses keep the step scores separate: process-supervised training can apply labels at each step boundary, and stepwise RL can deliver reward incrementally rather than collapsing the whole trajectory to one number.

The connection to credit assignment is direct. In Chapter 2, the outcome reward was a single scalar spread across all tokens. A PRM replaces that single scalar with a step-level signal. When used to train a policy or to select among candidates, these scores tell the system where the reasoning went right and where it went wrong. The optimizer no longer has to guess which parts of a rewarded trajectory were actually responsible for the reward.

One can write the interface as a simple loop over step boundaries:

```python
from dataclasses import dataclass

@dataclass
class Step:
    text: str

def score_steps(prm, prompt: str, steps: list[Step]) -> list[float]:
    prefix: list[str] = []
    scores: list[float] = []
    for step in steps:
        scores.append(prm(prompt=prompt, prefix=prefix, step=step.text))
        prefix.append(step.text)
    return scores

def rerank_score(step_scores: list[float]) -> float:
    return min(step_scores)
```

The key change from Chapter 2 is the interface, not the optimizer. An ORM scores the whole solution once. A PRM is queried repeatedly at step boundaries, and only afterward does a downstream system decide whether to keep the per-step scores separate or reduce them to one trajectory score. Here the reduction is `min(...)` because best-of-$N$ reranking is one common use case, not because every PRM must aggregate that way.

[^ch3-prm-formulation]: Lightman et al. formalize PRM training as step-level classification with labels such as positive, negative, and neutral.[@lightman2023letsverify] The key point is that the core object is the per-step prediction, while any solution-level score is a separate reduction chosen for a particular use case.

## How step labels are obtained

The PRM formulation assumes access to step-level correctness labels. Where do these come from? There are four broad regimes, ordered roughly by label fidelity and cost.

### Human annotation

Lightman et al. collected PRM800K: approximately 800,000 step-level human labels on model-generated math solutions.[@lightman2023letsverify] Annotators judged each step as positive (mathematically valid), negative (contains an error), or neutral (ambiguous or uncheckable). This is the gold standard for label quality. The annotators could verify whether a specific algebraic manipulation was correct, whether an inference followed from the previous step, and whether the solution strategy was sound.

The limitation is cost. Each solution requires a trained annotator to read every step and make a judgment. The cost scales with the number of steps, the number of solutions, and the difficulty of the domain. PRM800K was feasible for competition-math-level problems where each solution has 5–15 steps. For longer trajectories (agentic tasks with hundreds of steps) or faster-moving domains (code with evolving APIs), human annotation does not scale.

### Monte Carlo rollout estimation

Wang et al. introduced an automated alternative in Math-Shepherd.[@wang2024mathshepherd] The idea: to estimate whether step $t$ is correct, complete the trajectory from step $t$ many times (using the model itself) and measure what fraction of completions reach the correct final answer. If most completions from step $t$ succeed, the step is probably correct. If most fail, the step probably introduced an error.

$$
\hat{P}(\text{step } t \text{ correct}) \approx \frac{1}{K} \sum_{k=1}^{K} \mathbb{I}\bigl[\text{rollout}_k(y_{1:t}) \text{ reaches correct answer}\bigr]
$$ {#eq-ch3-mc-estimate}

This is elegant because it requires no human labels at all — only an outcome verifier and the ability to generate completions. But the estimates are noisy. A step can be labeled "correct" because the model is good at recovering from errors downstream, or "incorrect" because the remaining steps are hard even from a correct intermediate state. The signal reflects the model's completion ability as much as the step's logical validity.

At code level, the idea is short enough to sketch directly if we assume the Chapter 2 `outcome_reward` is already available:

```python
def estimate_step_value(model, prefix_steps, gold_answer, K=8) -> float:
    successes = 0
    for _ in range(K):
        completion = model.complete_from(prefix_steps)
        if outcome_reward(completion, gold_answer) == 1.0:
            successes += 1
    return successes / K
```

This is why rollout-estimated process supervision sits somewhere between outcome and process reward. The final check is still outcome-based; what changes is that the outcome verifier is applied to many continuations from a partial solution rather than once at the end of a complete trajectory.

### Outcome-propagated pseudo-labels

The roughest variant takes only the trajectory-level outcome and propagates it to the steps inside the trajectory. If a sampled solution reaches the correct final answer, all of its steps are treated as positive; if it fails, all of its steps are treated as negative. This is the heuristic you had in mind. It is attractive because it is almost free once final-answer labels already exist, and recent work has explored more careful versions of it under the banner of weak supervision.[@sun2025freeprm]

The weakness is obvious. A failed trajectory can contain many locally correct steps, and a successful trajectory can contain early mistakes that are later repaired. Naively copying the final outcome onto every step therefore injects severe label noise in exactly the cases where process supervision is supposed to help most. FreePRM is not just the naive heuristic; it starts from outcome-derived pseudo labels and then adds debiasing to reduce that noise.[@sun2025freeprm] But conceptually it belongs in this fourth bucket: process labels inferred directly from endpoint correctness rather than from human annotation, rollout-based continuation estimates, or formal step checking.

### Formal step checking

In proof assistants such as Lean and Coq, each tactic application is checked by the kernel. If the tactic produces a valid proof state, it is correct; if it does not, the assistant rejects it immediately. This is process verification in its purest form: each step is checked against a formal specification, the check is exact, and it costs nothing beyond the kernel call.[@xin2024deepseekproverv15]

The limitation is domain restriction. Formal step checking only works when the reasoning is expressed in a formal language with a decidable step-level validity criterion. Math written in natural language does not qualify. Code written in Python does not qualify (though individual function calls can be tested). The domains where formal step checking applies — theorem proving, type checking, certain program verification tasks — are exactly the domains where process verification is cheapest and most reliable.

These four regimes define a tradeoff:

| Method | Label quality | Cost per step | Domain scope |
|:-------|:-------------|:-------------|:------------|
| Human annotation | High | High | Any domain humans can judge |
| MC rollout estimation | Medium (noisy) | Medium (compute) | Any domain with an outcome verifier |
| Outcome-propagated pseudo-labels | Low to medium (very noisy) | Low | Any domain with trajectory-level correctness labels |
| Formal step checking | Exact | Near zero | Formal systems only |

: The annotation bottleneck in process verification. No single method is both high-quality and broadly applicable. {#tbl-ch3-annotation-tradeoff}

## ORM vs PRM: when does step-level signal change the picture?

The question is not whether process rewards are theoretically better than outcome rewards. They obviously provide more information. The question is whether that extra information translates into measurably better models or better selection, given the cost of obtaining step-level labels.

The empirical evidence is more nuanced than the theory might suggest.

::: {#fig-ch3-process-vs-outcome-orm-vs-prm}

::: {.content-visible when-format="html"}
![](../diagrams/03-process-vs-outcome-light.png){.light-content}

![](../diagrams/03-process-vs-outcome-dark.png){.dark-content}
:::

::: {.content-visible when-format="pdf"}
![](../diagrams/03-process-vs-outcome-light.png)
:::

The empirical question is not whether step-level feedback exists in principle, but when that extra granularity changes selection or learning enough to justify its cost.
:::

Uesato et al. published the first systematic comparison in November 2022.[@uesato2022solving] Their finding was surprising: outcome-based and process-based feedback achieved similar final-answer accuracy on GSM8K. But process supervision dramatically reduced trace-level errors — from 14.0% to 3.4%. In other words, both methods got the right answer at similar rates, but the process-supervised model was far more likely to get the right answer for the right reasons. This distinction matters for robustness, interpretability, and downstream trust, even when the headline accuracy numbers look comparable.

Lightman et al. sharpened the picture in May 2023.[@lightman2023letsverify] On the MATH benchmark, which is substantially harder than GSM8K, PRM-based reranking in a best-of-N setting significantly outperformed ORM-based reranking. The gap widened with more candidates: when the model generated many candidate solutions, the PRM was better at identifying which one was actually correct. This makes intuitive sense. An ORM scores the whole trajectory and can be fooled by a confident-sounding wrong answer. A PRM checks each step and is more likely to flag the specific point where the reasoning breaks down.

Snell et al. extended the analysis to test-time compute scaling in August 2024.[@snell2024scaling] Their key result: the optimal allocation of test-time compute depends on problem difficulty. For easy problems, simple majority voting suffices. For hard problems, PRM-guided beam search is far more efficient — a compute-optimal strategy using a PRM can be 4x more efficient than best-of-N, and can enable a smaller model to match or exceed the performance of a 14x larger model under matched compute budgets. The PRM's value is largest precisely where it is hardest to get right: on problems where many candidate trajectories contain partial progress that an outcome-only verifier cannot distinguish from complete failure.

The pattern across these results: PRMs help most when used for test-time selection or search rather than for training alone, and the benefit scales with problem difficulty. On easy problems where most trajectories succeed, the extra annotation cost buys little. On hard problems where trajectories frequently contain partial progress, step-level scoring is substantially more informative than endpoint scoring.

## Process rewards as a new proxy

Process verification solves one problem — sparse credit assignment — by introducing another: the step-level label is itself a proxy that can be gamed, misspecified, or noisy.

**Rewarding reasoning shape over reasoning substance.** A PRM trained on human labels of "good steps" learns what correct reasoning looks like in the training distribution. If that distribution is narrow — say, competition math solutions with a particular style — the PRM may reward well-formatted, confident-sounding steps that correlate with correctness but do not cause it. The model learns to produce reasoning that is checkable-looking rather than checkable. This is the process-level analogue of the outcome-level problem where models learn answer-format regularities rather than the underlying capability. The process verifier shifts the proxy from the endpoint to the path, but it does not eliminate the proxy.

**Annotation noise compounds.** MC rollout estimates have high variance. A step can be labeled "correct" because the model is good at recovering from errors, or "incorrect" because downstream steps are intrinsically hard. Human annotators disagree on whether an intermediate step is valid, especially when the step involves an unjustified leap that happens to be mathematically sound. Both noise sources create systematic biases. A model trained against noisy step labels can learn to exploit the noise — for example, by producing steps that are easy for the MC estimator to complete rather than steps that are logically strong.

**The implicit-PRM blur.** Recent work challenges the assumption that explicit process supervision is necessary. Yuan et al. showed that an ORM trained with a log-likelihood-ratio parameterization contains an implicit PRM that can be extracted without any step-level labels, and that this implicit PRM outperforms Math-Shepherd using less than 1/38 of the training data.[@yuan2024free] Sullivan and Koller went further, proving that GRPO with an ORM is mathematically equivalent to a PRM-aware RL objective with an implicit Monte Carlo PRM.[@sullivan2025grpo] These results do not mean explicit PRMs are useless — they may still help in specific regimes — but they do mean the clean conceptual boundary between outcome and process supervision is blurrier than the early literature suggested. The question shifts from "should we use a PRM?" to "when does explicit process annotation provide enough marginal value over what outcome-based methods already capture implicitly?"

## What the process verifier sees and misses

The process verifier sees externalized intermediate states: reasoning steps written in the chain of thought, subgoal completions in a proof, partial execution results in a code trace, cited evidence in a grounded answer. Its visibility is limited to what the model writes down.

It misses three things.

First, latent cognition. Language models perform computation internally that is never externalized in the chain of thought. A model may "see" that a factoring approach will work without writing down the trial-and-error that led to that recognition. A process verifier that scores only the written steps cannot reward or penalize the internal computation that produced them. If the model compresses useful reasoning into a single externalized step, the verifier scores that step but has no visibility into whether the compression was sound.

Second, beneficial shortcuts. Not all good reasoning follows the annotated step structure. A model that skips two intermediate steps because it recognizes a pattern is penalized by a strict process verifier that expects those steps to be present. The process labels encode a particular decomposition of the task; any decomposition that deviates from the labeled structure — even a better one — is invisible or penalized.

Third, strategic value versus logical validity. A step can be logically correct but strategically useless — a valid algebraic manipulation that leads nowhere. A step can be logically questionable but strategically brilliant — an unjustified heuristic that consistently leads to the right answer. The process verifier scores logical validity (or its proxy). It does not score whether a step was the right move in the context of solving the problem.

## Open questions

- Which tasks admit stable step-level labels without excessive annotation overhead, and how can we identify them before investing in annotation infrastructure?
- How do process rewards interact with hidden reasoning or compressed internal computation that the model does not externalize?
- When should process checks be strict (hard correctness labels that gate the reward) versus advisory (soft preferences that nudge the policy)?
- Given the implicit-PRM results, when is explicit process supervision worth the marginal cost over well-designed outcome supervision with sufficient rollout diversity?
- Can process verifiers be designed to reward strategic value rather than only logical validity, and what would the labeling scheme look like?

The boundary between outcome and process verification is not as sharp as the early literature suggested. Outcome rewards contain implicit step-level signal; process rewards introduce new proxies. When neither pure regime is sufficient — when outcome rewards are too sparse but process labels are too noisy or too expensive — the next move is to combine them, to learn the verifier itself, or to build layered verification stacks. That is the subject of Chapter 4.
