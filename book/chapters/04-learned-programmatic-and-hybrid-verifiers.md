# Learned, Programmatic, and Hybrid Verifiers

![M. C. Escher, _Dolphins_ (1923).](../escher/04-dolphins.jpg){width="80%" fig-align="center"}

## Chapter Map

- Distinguish the programmatic verifier core of RLVR from learned verifiers.
- Explain how hybrid stacks combine checks, and the failure modes introduced.

## Programmatic versus Learned Verifiers

Recall the quadratic example from Chapters 2 and 3: a model correctly finds both roots of $x^2-5x+6=0$, then reports only $x=2$. A programmatic checker can reject the incomplete final answer. A learned process verifier can separately assess the four correct intermediate steps. Combining them raises a different question from where to place the reward: which component checks which property, and how should their verdicts be combined?

Chapters 2 and 3 classify verifiers by whether they apply on the final artifact or on intermediate steps in the rollout. This chapter changes axes, as we discuss how the verifier itself is implemented:

**Programmatic verifiers** are deterministic, auditable, and brittle. Examples include: regex-based answer extraction, symbolic equivalence checking (as in Math-Verify), unit-test execution in a sandbox, static analysis and linting, proof-kernel acceptance, and format-validation rules [@kydlicek2025mathverify; @le2022coderl].

**Learned verifiers** are flexible, soft-scored, and opaque. They are not verifiable rewards in the narrow sense; instead, a model is trained or prompted to judge another model's output. This covers ambiguity, open-endedness and edge cases, but inherits the biases and blind spots of the judge model.

## Programmatic verifiers

| Domain | Programmatic checks | Checkable core |
|:-------|:-------------------|:--------------|
| Math | Answer extraction, canonicalization, symbolic equivalence | Closed-form answers with known ground truth |
| Code | Sandbox execution, test suites, linters, static analysis | Functional behavior covered by tests |
| Proof | Kernel acceptance (Lean, Coq, Isabelle) | Validity of the submitted proof under the formal system's assumptions |
| Format | Regex, XML schema, JSON schema, tag-structure validation | Output-contract compliance |

: Programmatic verifiers by domain. {#tbl-ch4-programmatic}

Programmatic verifiers have explicit, auditable acceptance rules, although their implementations and test coverage can still have blind spots. For example, a symbolic equivalence checker either recognizes two expressions as equal or it does not, and a unit test either passes or fails. A passing test establishes the behavior covered by that test, not every correctness property of the program [@liu2023evalplus]. In Lean, tactics construct proof terms for the kernel to check; kernel acceptance is not a separate judgment that every tactic was appropriate or that the formal statement captures the intended task.

## Learned verifiers

### LLM-as-a-Judge

The simplest form of learned verification is prompting a strong LLM to evaluate a weaker model's output. Zheng et al. called the paradigm LLM-as-a-Judge [@zheng2023judging]. An LLM takes the output and produces a judgment: e.g. a scalar score, a classification, etc. We use the output as reward signal or selection criterion, Zheng et al. found that GPT-4 agreed with human preferences in over 80% of comparisons on MT-Bench and Chatbot Arena when ties were excluded, but this only measures preference agreement, not correctness on arbitrary tasks.

A simple extension to this approach is sampling multiple judges to get a majority vote over trajectories; GenRM-CoT samples multiple verification rationales from one verifier and averages their "Yes" token probabilities, rather than polling independently trained judges [@zhang2025genrm]. Compellingly, James Evans described an empirical accuracy benefit from using an odd number of judges in work by Google's Paradigms of Intelligence team [@kim2026societies].[^ch4-pi]

[^ch4-pi]: The observation about the number of judges was shared in direct conversation between the book's author and James Evans, a coauthor of the cited paper.

Nevertheless, agreement rates hide systematic biases, of which Zheng et al. identified four:

1. position bias (the judge prefers whichever response appears first)
2. verbosity bias (longer responses are rated higher regardless of quality)
3. self-enhancement bias (a model rates its own outputs higher than a different model's outputs of equal quality)
4. limited mathematical reasoning (the judge makes errors when evaluating mathematical correctness that a symbolic checker would catch trivially)

Of note that models of today's capability likely do not suffer such biases.

### Reward model ensembles

Ensembles are the simplest hybrid stacks, combining multiple judgments homogeneously without layering different verification modalities. Coste et al. studied ensembles of reward models for RLHF and found that they mitigate but do not eliminate reward hacking [@coste2023rewardensemble]. Ensembles that differ in pretraining seeds generalize better than those that differ only in fine-tuning seeds, because the former have more diverse internal representations, and less-overlapping blind spots.

### The calibration problem

Learned surrogate verifiers produce scores, but those scores need not be calibrated probabilities of correctness. A judge that outputs 0.8 does not mean the solution has an 80% chance of being correct; it means 0.8 is the number the judge's training objective learned to assign to solutions with that surface profile. Lambert et al. documented this systematically in RewardBench, showing that reward models exhibit large accuracy gaps across domains, and that different training methods (classifier-based, DPO-based, generative) have different calibration profiles [@lambert2024rewardbench].

For verifier-stack design, the calibration gap means that raw scores from a learned component cannot be compared directly to outputs from a programmatic component. If a symbolic checker returns "match" (effectively certainty) and a learned judge returns 0.7, the arbitration logic must account for the fact that 0.7 from the judge does not carry the same epistemic weight as a deterministic pass from the checker. In other words, treating both as commensurable scalars and averaging them is a mistake.

## Hybrid stacks

Hybrid stacks layer verifier components together to robustify reward signal. Unit tests can check functional correctness and specific security properties, but cannot establish general security or judge readability. By the same token, a proof kernel checks validity, but it does not judge whether the theorem was worth proving. Therefore, we combine multiple verifiers together.

One mental model is to think of each verifier as producing a useful signal over a subset of inputs in some high-dimensional vector space. Outside that subset, it may return confident errors rather than remain silent. Stacking verifiers can extend this coverage, and the design problem in a hybrid stack is to determine how to compose rewards commensurately, and how failure modes interact when composed.

OpenAI's public reinforcement fine-tuning API exposes this pattern as multigrader composition, where string checks, score-model graders, and Python execution can be combined into a single grader [@openai2026graders]. In agent evaluation, Anthropic similarly describes verifiers ranging from exact string comparison to enlisting Claude to judge a response [@anthropic2025writingtools].

::: {#fig-ch4-outcome-hybrid}

::: {.content-visible when-format="html"}

```{=html}
<div class="oph-widget" id="oph-widget">
  <p class="oph-hint">Click a tab to see how each verification regime scores the same trajectory.</p>

  <div class="oph-tabs" role="tablist">
    <button class="oph-tab oph-active" role="tab" aria-selected="true" data-mode="outcome">Outcome</button>
    <button class="oph-tab" role="tab" aria-selected="false" data-mode="hybrid">Hybrid Stack</button>
  </div>

  <table class="oph-table">
    <thead>
      <tr>
        <th class="oph-step-col">Step</th>
        <th class="oph-reasoning-col">Reasoning</th>
        <th class="oph-score-col">Score</th>
        <th class="oph-source-col">Source</th>
      </tr>
    </thead>
    <tbody id="oph-body">
    </tbody>
  </table>

  <div class="oph-summary" id="oph-summary" aria-live="polite"></div>
</div>

<script>
(() => {
  const steps = [
    { id: 1, text: "Factor: x\u00B2 \u2212 5x + 6 = (x\u22122)(x\u22123)", correct: true },
    { id: 2, text: "Set first factor to zero: x = 2", correct: true },
    { id: 3, text: "Set second factor to zero: x = 3", correct: true },
    { id: 4, text: "Collect solution set: {2, 3}", correct: true },
    { id: 5, text: "Report: \u27E8answer\u27E9x = 2\u27E8/answer\u27E9", correct: false }
  ];

  const modes = {
    outcome: {
      scores: [
        { s: "\u2014", c: "oph-na", src: "\u2014" },
        { s: "\u2014", c: "oph-na", src: "\u2014" },
        { s: "\u2014", c: "oph-na", src: "\u2014" },
        { s: "\u2014", c: "oph-na", src: "\u2014" },
        { s: "r = 0", c: "oph-fail", src: "Symbolic" }
      ],
      summary: "<strong>Outcome only.</strong> The verifier checks the final answer against the ground truth. It returns r\u00A0=\u00A00 because the extracted answer is incomplete. The four correct reasoning steps are not assessed separately."
    },
    hybrid: {
      scores: [
        { s: "\u2713", c: "oph-pass", src: "PRM" },
        { s: "\u2713", c: "oph-pass", src: "PRM" },
        { s: "\u2713", c: "oph-pass", src: "PRM" },
        { s: "\u2713", c: "oph-pass", src: "PRM" },
        { s: "r = 0", c: "oph-fail", src: "Symbolic" }
      ],
      summary: "<strong>Hybrid stack.</strong> The programmatic checker catches the incomplete answer (r\u00A0=\u00A00). The PRM marks steps 1\u20134 as correct."
    }
  };

  function render(mode) {
    const m = modes[mode];
    const tbody = document.getElementById("oph-body");
    tbody.innerHTML = "";
    steps.forEach((step, i) => {
      const sc = m.scores[i];
      const tr = document.createElement("tr");
      tr.innerHTML =
        "<td>" + step.id + "</td>" +
        "<td>" + step.text + "</td>" +
        '<td class="oph-score-col ' + sc.c + '">' + sc.s + "</td>" +
        '<td class="oph-source-col">' + sc.src + "</td>";
      tbody.appendChild(tr);
    });
    document.getElementById("oph-summary").innerHTML = m.summary;
  }

  document.querySelectorAll(".oph-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".oph-tab").forEach(t => { t.classList.remove("oph-active"); t.setAttribute("aria-selected", "false"); });
      tab.classList.add("oph-active");
      tab.setAttribute("aria-selected", "true");
      render(tab.dataset.mode);
    });
  });

  render("outcome");
})();
</script>
```
:::

::: {.content-visible when-format="pdf"}

| Step | Reasoning | Outcome | Hybrid |
|:-----|:----------|:-------:|:------:|
| 1 | Factor: $x^2-5x+6=(x-2)(x-3)$ | --- | $\checkmark$ (PRM) |
| 2 | $x-2=0 \implies x=2$ | --- | $\checkmark$ (PRM) |
| 3 | $x-3=0 \implies x=3$ | --- | $\checkmark$ (PRM) |
| 4 | Solution set: $\{2,3\}$ | --- | $\checkmark$ (PRM) |
| 5 | Report: `<answer>x = 2</answer>` | $r=0$ | $r=0$ (Symbolic) |

: Outcome verification scores only the endpoint. The hybrid stack uses a programmatic checker for the endpoint and a PRM for intermediate steps.

:::

The same trajectory scored by two verification regimes. The PRM assessments are illustrative; how they become training credit depends on the reward construction and optimizer discussed in Chapter 5.
:::

## Formalization

A verifier stack with $K$ components can be written as:

$$
r_{\text{stack}}(x, y) = \operatorname{Arb}\bigl(v_1(x, y),\, v_2(x, y),\, \ldots,\, v_K(x, y)\bigr)
$$ {#eq-ch4-stack}

where each $v_i$ is a verifier component that may return a score, a categorical verdict, a vector of step assessments, or a null (indicating abstention), and $\operatorname{Arb}$ maps these outputs to the final reward, including when components abstain.

Common arbitration patterns include:

- **Priority cascade**: check $v_1$ first; if it returns a verdict, use it; otherwise check $v_2$, and so on.
- **Weighted aggregation**: map outputs to numeric scores $s_i(x, y)$ on a common reward scale, then compute $r = \sum_{i \in A} w_i \, s_i(x, y)$ over the non-abstaining components $A$. Define a fallback if all components abstain. This constructs a reward, not a calibrated probability of correctness.
- **Gated routing**: a classifier decides which component to invoke based on input features.
- **Unanimous agreement**: require all components to agree before assigning a positive reward.

The choice of arbitration pattern determines the stack's effective false-positive and false-negative rates. Priority cascade is biased toward the first component's failure modes. Weighted aggregation can dilute strong signals with weak ones. Gated routing's errors depend on the routing model. Unanimous agreement can suppress correct outputs; there is no universally correct choice.

### Hybrid verifier in code

This code snippet reuses Chapter 2's answer-extraction and canonicalization helpers; `gold` is the reference answer in canonicalized form. A parsed mismatch returns zero, and a learned fallback receives both the problem and the complete reference answer.

```python
def symbolic_reward(completion: str, gold: tuple[str, ...]) -> float | None:
    answer = extract_answer(completion)
    if answer is None:
        return None
    candidate = canonicalize_answer(answer)
    return float(candidate == gold)

def hybrid_reward(
    problem: str,
    completion: str,
    gold: tuple[str, ...],
    judge,
    *,
    threshold: float,
) -> float:
    if not 0.0 < threshold <= 1.0:
        raise ValueError("threshold must be in (0, 1]")

    exact = symbolic_reward(completion, gold)
    if exact is not None:
        return exact

    judge_score = judge(
        problem=problem,
        completion=completion,
        reference_answer=gold,
        rubric=(
            "Score final-answer correctness from 0 to 1 against the complete "
            "reference answer for this problem. Reject missing or incomplete "
            "answers; do not infer omitted answers from intermediate reasoning."
        ),
    )
    if not 0.0 <= judge_score <= 1.0:
        raise ValueError("judge score must be finite and in [0, 1]")
    return float(judge_score >= threshold)
```

`threshold` can be thought of as a value tuned by a task expert or arrived at by balancing false accepts against false rejects.

## Limitations

Adding components to a verifier stack can amplify errors rather than cancel them.

**Silent disagreement.** Two stack components can return conflicting verdicts on the same input.

**Correlated failures.** Components can fail on the same hard input, so do not assume that error probabilities multiply as if the components were independent.

**Excessive complexity.** Adding a component can improve average performance while increasing stack complexity and interpretability costs.

## Open questions

- When should learned judges be first-class stack components that score every output, rather than fallbacks invoked only on the programmatic residual?
- What is the ceiling on stacking beyond which debugging costs exceed the gains?
- Can the marginal value of each stack component be quantified before deployment, or must it be measured empirically on the target task distribution?

## What comes next

The verifier stack defines what gets checked and how, not how those checks become training signal. A stack returning binary outcomes, one returing graded scores, and one returing step-level annotations will produce very different learning dynamics even if they agree on output correctness. Transforming verifier outputs into something an optimizer can use is the subject of Chapter 5.
