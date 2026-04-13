# Faithfulness, Confidence, and What Verification Misses

![M. C. Escher, _Morano Calabria_ (1930).](../escher/08-morano-calabria.jpg){width="80%" fig-align="center"}

## Chapter Map

- Identify three properties that no verifier in Chapters 2 through 6 can certify by default: faithful reasoning, calibrated confidence, and genuine understanding.
- Explain why these are structural limits of the verification paradigm rather than engineering failures, and how that should constrain claims about RLVR systems.

## The verification ceiling

Chapter 7 described failures under optimization pressure. The model found a gap in the verifier, exploited the gap, and satisfied the checker without satisfying the task. Those failures are serious, but they have an engineering flavor: better hidden tests, better extractors, debiased judges, KL constraints, red-teaming, and early stopping can push the failure surface outward.

This chapter is about a different boundary. A verifier checks externalized behavior: a final answer, a proof term, a program, a citation set, a reasoning trace, a tool call, or a confidence expression. Faithfulness, calibration, and understanding are not just properties of those artifacts. They are properties of the relationship between external behavior and the model's internal state. The verifier can inspect the artifact. It cannot directly inspect the computation that produced it.

That is the verification ceiling. It is not a reason to abandon RLVR. RLVR works because many useful capabilities expose checkable behavioral signals. But honest deployment requires knowing what those signals certify. A model can pass a verifier without its written reasoning being faithful, without its confidence being calibrated, and without the capability generalizing beyond the tested regime.

## Correct answer, wrong mechanism

Consider a model trained with RLVR on competition math. On a number theory problem, it produces a clean solution: recognize the problem type, apply modular arithmetic, simplify, and report the correct final answer. The outcome verifier returns `1`. A process reward model scores each step as valid. A hybrid stack agrees that the answer and the visible reasoning look good.

Now suppose the model did not derive the method from the problem. It matched the problem to a near-duplicate in pretraining and then produced a plausible derivation after the fact. Change one number so that the memorized pattern no longer applies, and the same model gives a confident, well-structured chain of thought leading to a wrong answer.

Every verifier in the stack saw what it was designed to see: a correct final answer, valid-looking steps, and confident delivery. Nothing went wrong at the interface. The missing property sits below the interface, in the relationship between the written trace and the computation that actually drove the answer.

This example runs through the rest of the chapter. The trace may not be faithful. The confidence may not be calibrated. The behavior may look like understanding on one distribution while relying on a brittle mechanism that fails under small distribution shifts.

## Faithfulness: when the trace is not the reason

A reasoning trace is faithful when it is causally involved in producing the answer. In the strongest version, intervening on the trace changes the model's conclusion. In the weaker version, at least some of the written steps reflect information the model actually used, rather than serving as a plausible reconstruction after the decision was already determined.

Turpin et al. showed that chain-of-thought explanations can systematically hide the factors that influenced the model's answer.[@turpin2023language] They introduced biasing features, such as answer-position artifacts in multiple-choice prompts. When those features pushed models toward the wrong answer, models often produced plausible chain-of-thought explanations that rationalized the biased answer without mentioning the bias. The verifier sees an explanation. It does not see the latent feature that moved the model.

Lanham et al. tested faithfulness more directly by intervening on chain-of-thought reasoning.[@lanham2023measuring] They truncated reasoning, inserted mistakes, paraphrased traces, and measured how much the model's final answer depended on the trace. Their result is not that chain of thought is always useless. It is sharper: faithfulness varies by task and model, and larger models became less faithful on many of the tasks they studied. Better traces can therefore become less reliable as evidence of the mechanism that produced them.

This matters for RLVR because process rewards make visible reasoning an optimization target. A process verifier rewards steps that look valid. A model under that reward learns to produce trace-shaped evidence that the verifier likes. That may improve reasoning. It may also improve the model's ability to write plausible reasoning that is not causally responsible for the answer.

The key point is not that process rewards are bad. The key point is that process rewards certify the trace, not the hidden computation. A perfect process verifier over written steps can still miss the fact that the answer was produced by a shortcut, memory, or latent feature that never appears in the trace.

### Faithfulness as an intervention problem

The hard version of faithfulness is causal, not textual. Let $X$ be the prompt, $R$ the written reasoning trace, $Y$ the final answer, and $H$ the hidden computation that produced both. An outcome verifier observes $(X,Y)$. A process verifier observes $(X,R,Y)$. Neither directly observes $H$.

The artifact-level question is:

$$
\Pr(Y \text{ correct} \mid X,R).
$$

That asks whether the trace is compatible with a correct answer. The causal question is different:

$$
\Pr(Y=y \mid \operatorname{do}(R=r), X)
\quad \text{versus} \quad
\Pr(Y=y \mid \operatorname{do}(R=r'), X).
$$

If replacing the reasoning trace with a counterfactual trace $r'$ barely changes the final answer, then the displayed trace was weak evidence about the mechanism. If corrupting a key step changes the answer in the predicted direction, the trace is more plausibly involved in the computation. This is why interventions on reasoning traces are stronger evidence than simply grading the trace.

The identifiability problem is the deeper point. Two systems can have the same observable distribution $\Pr(R,Y \mid X)$ and different hidden mechanisms $H$. One system may compute the answer through the trace; another may compute the answer first and rationalize afterward. Any verifier restricted to $(X,R,Y)$ cannot separate those mechanisms in general. It can only add tests that make the shortcut less likely.

## Calibration: knowing what you know

Correctness verifiers check whether an answer is right. They do not automatically check whether the model knows how confident it should be. A model that is right 70 percent of the time and says "I am certain" every time has a calibration problem, but the problem is not visible from the correct cases alone.

Kadavath et al. studied whether language models can evaluate the validity of their own claims.[@kadavath2022language] They found that models can estimate `P(True)`, the probability that a proposed answer is correct, and can predict a task-level `P(IK)`, the probability that they know the answer. This is real self-knowledge, not pure noise. But it is bounded: performance and calibration vary across task formats, open-ended settings, and distribution shifts.

Tian et al. studied calibration in RLHF-trained models and found an important split.[@tian2023just] Conditional probabilities from RLHF-trained models can be poorly calibrated, while verbalized confidence can be more informative: asking the model to state a confidence score often improves calibration relative to using its token probabilities directly. That result is useful, but it also sharpens the problem for RLVR. Confidence is itself an output artifact. It can be elicited, scored, and trained, but it is not guaranteed by answer correctness.

Binary RLVR gives almost no direct signal about uncertainty. If the model says "the answer is 7" and it is correct, it receives the same endpoint reward whether it was appropriately uncertain or wildly overconfident. If the model abstains or hedges when the benchmark expects a single final answer, it often receives no correctness reward at all. Unless the reward function explicitly includes calibration, the default incentive is to answer, not to know when not to answer.

Graded rewards can encode calibration in principle. A system could reward accurate confidence intervals, penalize overconfidence on wrong answers, and reward abstention when the model is genuinely uncertain. But that requires another verifier: a calibration evaluator that sees enough examples to compare stated confidence to empirical accuracy. Calibration is therefore not free. It is a separate signal-design problem layered on top of correctness.

### Calibration as a scoring problem

Calibration is distributional. If the model emits a confidence $p(x) \in [0,1]$ and correctness is $C(x) \in \{0,1\}$, perfect calibration means

$$
\mathbb{E}[C \mid p(X)=p] = p.
$$

In finite data, this is usually approximated by bins:

$$
\mathbb{E}[C \mid p(X) \in B_j]
\approx
\mathbb{E}[p(X) \mid p(X) \in B_j].
$$

This immediately shows why a single verified answer cannot certify confidence. Calibration is a relationship between stated probabilities and empirical frequencies across many examples.

If we want RLVR to train confidence, the reward should use a proper scoring rule, not just a correctness bit.[@gneiting2007strictly] Two standard examples are the Brier loss

$$
S_{\mathrm{Brier}}(p,C) = (p-C)^2
$$

and the log loss

$$
S_{\log}(p,C)
=
- C \log p - (1-C)\log(1-p).
$$

A calibrated RLVR reward could then take the form

$$
r(x,y,p)
=
r_{\mathrm{correct}}(x,y)
- \lambda S(p, C(x,y)),
$$

where $C(x,y)$ is the verifier's correctness label. The tradeoff is real: increasing $\lambda$ teaches confidence and abstention, but it also changes the optimization target away from pure task success. That is not a reason to avoid calibration rewards. It is a reason to report them separately from correctness gains.

## Behavioral correctness is not the same as understanding

Suppose a model passes every verifier we can afford: correct final answers, valid reasoning steps, calibrated confidence, passing tests, and no obvious reward hacking. Does it understand the task?

There are two defensible answers.

The behavioral answer says that understanding is not separately testable beyond behavior. If the model generalizes correctly across a wide enough distribution, then its behavior is what matters. On this view, asking for "genuine understanding" beyond robust behavioral competence adds a metaphysical demand that cannot guide engineering.

The skeptical answer says that fixed-distribution behavioral success is not enough. A model can pass the verifier on the measured distribution while relying on a brittle mechanism: memorized templates, shallow heuristics, dataset artifacts, or a shortcut that disappears under a small shift. The verifier cannot distinguish "correct by robust mechanism" from "correct by brittle mechanism" when both produce the same checked artifact on the tested inputs.

The operational position for RLVR is simple: verification certifies behavior under a defined interface and distribution. It does not certify mechanism, transfer, or robustness beyond that distribution. Saying "the model understands number theory" is stronger than saying "the model solves these verified number theory problems." The second claim can be supported by RLVR. The first requires evidence beyond the verifier's usual interface.

## The verification lens

::: {#fig-ch8-verification-lens fig-cap="Different verifier stacks certify different visible properties, but some epistemic properties remain outside the default verification interface."}

::: {.content-visible when-format="html"}

```{=html}
<div class="vl-widget" id="vl-widget">
  <p class="vl-hint">Select a verifier configuration. The rows show which properties the configuration can certify from the visible artifact.</p>

  <div class="vl-tabs" role="tablist" aria-label="Verifier configurations">
    <button class="vl-tab vl-active" role="tab" aria-selected="true" data-mode="outcome">Outcome verifier</button>
    <button class="vl-tab" role="tab" aria-selected="false" data-mode="process">Process verifier</button>
    <button class="vl-tab" role="tab" aria-selected="false" data-mode="hybrid">Hybrid stack</button>
    <button class="vl-tab" role="tab" aria-selected="false" data-mode="ensemble">Ensemble verification</button>
    <button class="vl-tab" role="tab" aria-selected="false" data-mode="mech">Mechanistic interpretability</button>
  </div>

  <div class="vl-grid">
    <div class="vl-response">
      <div class="vl-title">Visible model output</div>
      <div class="vl-card">
        <p><strong>Reasoning trace:</strong> identify the congruence class, reduce the expression, and report the residue.</p>
        <p><strong>Final answer:</strong> correct.</p>
        <p><strong>Confidence:</strong> "I am confident."</p>
      </div>
      <div class="vl-note">The verifier sees this artifact, not the hidden computation that produced it.</div>
    </div>

    <div class="vl-properties" id="vl-properties"></div>
  </div>

  <div class="vl-summary" id="vl-summary" aria-live="polite"></div>
</div>

<script>
(() => {
  const rows = [
    "Correct final answer",
    "Valid reasoning steps",
    "Calibrated confidence",
    "Faithful reasoning",
    "Genuine understanding"
  ];

  const states = {
    outcome: {
      values: ["yes", "no", "no", "no", "no"],
      summary: "<strong>Outcome verifier.</strong> It certifies the checked endpoint. It says nothing about the trace, confidence, faithfulness, or understanding."
    },
    process: {
      values: ["yes", "yes", "no", "no", "no"],
      summary: "<strong>Process verifier.</strong> It adds evidence about the visible steps, but it still does not certify whether the trace caused the answer."
    },
    hybrid: {
      values: ["yes", "yes", "partial", "no", "no"],
      summary: "<strong>Hybrid stack.</strong> More components can improve coverage and catch disagreement. They still inspect artifacts, not the full hidden computation."
    },
    ensemble: {
      values: ["yes", "yes", "partial", "no", "no"],
      summary: "<strong>Ensemble verification.</strong> Agreement across verifiers is stronger evidence, not proof. Shared blind spots remain possible."
    },
    mech: {
      values: ["yes", "yes", "partial", "partial", "no"],
      summary: "<strong>Mechanistic interpretability.</strong> In principle it can give partial evidence about causal computation. Today this is a research frontier, not a general-purpose verifier."
    }
  };

  function render(mode) {
    const state = states[mode];
    const box = document.getElementById("vl-properties");
    box.innerHTML = '<div class="vl-title">What this configuration can certify</div>';
    rows.forEach((row, idx) => {
      const status = state.values[idx];
      const el = document.createElement("div");
      el.className = "vl-row";
      el.innerHTML = '<div class="vl-prop">' + row + '</div><div class="vl-status vl-' + status + '">' + status + '</div>';
      box.appendChild(el);
    });
    document.getElementById("vl-summary").innerHTML = state.summary;

    document.querySelectorAll(".vl-tab").forEach((button) => {
      const active = button.dataset.mode === mode;
      button.classList.toggle("vl-active", active);
      button.setAttribute("aria-selected", active ? "true" : "false");
    });
  }

  document.querySelectorAll(".vl-tab").forEach((button) => {
    button.addEventListener("click", () => render(button.dataset.mode));
  });

  render("outcome");
})();
</script>
```
:::

::: {.content-visible when-format="pdf"}

| Property | Outcome verifier | Process verifier | Hybrid stack | Ensemble verification | Mechanistic interpretability |
| --- | --- | --- | --- | --- | --- |
| Correct final answer | yes | yes | yes | yes | yes |
| Valid reasoning steps | no | yes | yes | yes | yes |
| Calibrated confidence | no | no | partial | partial | partial |
| Faithful reasoning | no | no | no | no | partial |
| Genuine understanding | no | no | no | no | no |

:::

:::

## What richer verification regimes might reach

The verification ceiling is not fixed forever. It says what the usual verifier interface cannot certify, not what future methods could never measure.

Causal faithfulness tests are the most direct extension. Perturb, truncate, corrupt, or swap a reasoning trace and ask whether the answer changes. If the answer is stable under severe trace edits, the trace was probably not doing much causal work. If the answer changes in the predicted way, the trace is more likely to be involved. These tests are expensive because they require multiple forward passes and careful interventions, but they turn faithfulness into an operational question rather than a vibe.

Calibration training is more immediately implementable. A reward function can penalize overconfidence on wrong answers and underconfidence on right answers, or reward abstention when the model is genuinely uncertain. The catch is that calibration is distributional: you need enough examples to compare stated confidence against empirical accuracy. A single verified answer does not tell you whether a confidence statement is calibrated.

Mechanistic interpretability is the farthest frontier. In principle, it could connect the written trace to internal computation. In practice, current methods do not provide a general-purpose verifier for frontier-scale reasoning. The right stance is neither dismissal nor overclaiming: mechanistic tools may eventually narrow the faithfulness gap, but they do not currently erase it.

## What this chapter sees and misses

This chapter diagnoses structural limits of the verification paradigm. Better engineering can harden a verifier against exploitation, but it cannot automatically turn a checked artifact into a certificate of faithful reasoning, calibrated uncertainty, or robust understanding.

It does not provide a solution to those limits. It also does not catalog every domain-specific version of them. The point is the common structure: the verifier sees behavior through an interface, and some properties live in the relation between that behavior and the hidden mechanism that produced it.

## Open questions

- Under what conditions is chain-of-thought reasoning faithful enough to treat as evidence rather than illustration?
- Can calibration be trained directly without conflicting with correctness reward?
- When does the gap between behavioral correctness and genuine understanding become operationally relevant in deployment?
- Does RLVR training systematically degrade faithfulness by rewarding reasoning-shaped traces, and can this be measured during training?
- What is the minimal mechanistic interpretability capability needed to partially verify faithfulness?

Chapters 7 and 8 describe the two sides of the failure landscape: exploitability under optimization pressure and structural limits of observability. Chapter 9 applies that frame to long-context, multimodal, and agentic RLVR, where verification becomes broader, noisier, and more dependent on instrumentation.
