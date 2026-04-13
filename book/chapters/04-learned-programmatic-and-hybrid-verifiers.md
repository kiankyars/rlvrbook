# Learned, Programmatic, and Hybrid Verifiers

![M. C. Escher, _Dolphins_ (1923).](../escher/04-dolphins.jpg){width="80%" fig-align="center"}

## Chapter Map

- Distinguish the programmatic verifier core of RLVR from learned verifiers.
- Explain why production systems use hybrid stacks, and the failure modes introduced.

## Programmatic versus Learned Verifiers

Chapters 2 and 3 organized verifiers by where they apply across a rollout: either on the final artifact or on intermediate steps. This chapter changes axes, we will discuss how the verifier itself is implemented, and on this axis, we have two types:

**Programmatic verifiers** are deterministic, auditable, and brittle. They are the native RLVR object: regex-based answer extraction, symbolic equivalence checking (as in Math-Verify), unit-test execution in a sandbox, static analysis and linting, proof-kernel acceptance, and format-validation rules.[@kydlicek2025mathverify; @le2022coderl]

**Learned verifiers** are flexible, soft-scored, and opaque. They are not verifiable rewards in the narrow sense. Instead, they are learned surrogate signals: a model is trained or prompted to judge another model's output when no direct checker can carry the whole burden. This covers ambiguity, open-endedness and edge cases, but inherits the biases and blind spots of the judge model.

## Programmatic verifiers

| Domain | Programmatic checks | Checkable core |
|:-------|:-------------------|:--------------|
| Math | Answer extraction, canonicalization, symbolic equivalence | Closed-form answers with known ground truth |
| Code | Sandbox execution, test suites, linters, static analysis | Functional behavior covered by tests |
| Proof | Kernel acceptance (Lean, Coq, Isabelle) | Formal validity of each tactic or proof term |
| Format | Regex, XML schema, JSON schema, tag-structure validation | Output-contract compliance |

: Programmatic verifiers by domain. {#tbl-ch4-programmatic}

One shared property of this table is that programmatic verifiers never hallucinate. Their failure modes are enumerable, e.g. a symbolic equivalence checker either recognizes two expressions as equal or it does not, a unit test either passes or fails. While the above property is a positive, one limitation of these approaches is their susecpibtiltiy to miss edge cases, security vulnerabilities, and correctness properties that no test covers.[@liu2023evalplus]

## Learned verifiers

### LLM-as-a-Judge

The simplest form of learned verification is prompting a strong LLM to evaluate a weaker model's output. Zheng et al. formalized this as the LLM-as-a-Judge paradigm.[@zheng2023judging] An LLM takes the output and produces a judgment: e.g. a scalar score, a classification, etc. We use the output as reward signal or selection criterion. The work claims that strong judges agree with human preferences ~80% of the time, matching the rate at which human annotators agree with each other. This makes LLM-as-a-Judge viable in domains where programmatic checking is impossible. A simple extension to this approach is sampling multiple judges to get a majority vote over trajectories.[@hosseini2024genrm]


Nevertheless, agreement rates hide systematic biases, of which Zheng et al. identified four:

1. position bias (the judge prefers whichever response appears first)
2. verbosity bias (longer responses are rated higher regardless of quality)
3. self-enhancement bias (a model rates its own outputs higher than a different model's outputs of equal quality)
4. limited mathematical reasoning (the judge makes errors when evaluating mathematical correctness that a symbolic checker would catch trivially)

### Reward model ensembles

Ensembles are the simplest hybrid stacks, combining multiple judgments homogeneously without layering different verification modalities. Coste et al. studied ensembles of reward models for RLHF and found that they mitigate but do not eliminate reward hacking.[@coste2023rewardensemble] Ensembles that differ in pretraining seeds generalize better than those that differ only in fine-tuning seeds, because the former have more diverse internal representations, and less-overlapping blind spots.

### The calibration problem

Learned surrogate verifiers produce scores, but those scores are not calibrated probabilities of correctness. A judge that outputs 0.8 does not mean the solution has an 80% chance of being correct; it means 0.8 is the number the judge's training objective learned to assign to solutions with that surface profile. Lambert et al. documented this systematically in RewardBench, showing that reward models exhibit large accuracy gaps across domains, and that different training methods (classifier-based, DPO-based, generative) have different calibration profiles.[@lambert2024rewardbench]

For verifier-stack design, the calibration gap means that raw scores from a learned component cannot be compared directly to outputs from a programmatic component. If a symbolic checker returns "match" (effectively certainty) and a learned judge returns 0.7, the arbitration logic must account for the fact that 0.7 from the judge does not carry the same epistemic weight as a deterministic pass from the checker. Treating both as commensurable scalars and averaging them is a mistake.

## Hybrid stacks

Production RLVR systems layer verifier components together to robustify reward signal. Unit tests can check functional correctness, but can't judge code security or readability. By the same token, a proof kernel checks validity, but it does not judge whether the theorem was worth proving. Therefore, we combine multiple verifiers together. A useful mental image is to think of each verifier as producing a useful signal over a subset of inputs in some high-dimensional vector space, with the signal being silent in that subset's complement. Stacking verifiers can reduce this complement, and the design problem in a hybrid stack is to determine how to compose rewards comenseratuly, and how failure modes interact when composed.

OpenAI's public reinforcement fine-tuning API exposes this pattern as multigrader composition, where string checks, score-model graders, and Python execution can be nested into a single grader; Anthropic similarly frames agent evaluation verifiers as ranging from exact string comparison to enlisting Claude to judge a response.[@openai2026graders; @anthropic2025writingtools]

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
      summary: "<strong>Outcome only.</strong> The verifier checks the final answer against the ground truth. It returns r\u00A0=\u00A00 because the extracted answer is incomplete. Five correct reasoning steps receive no credit."
    },
    hybrid: {
      scores: [
        { s: "\u2713", c: "oph-pass", src: "PRM" },
        { s: "\u2713", c: "oph-pass", src: "PRM" },
        { s: "\u2713", c: "oph-pass", src: "PRM" },
        { s: "\u2713", c: "oph-pass", src: "PRM" },
        { s: "r = 0", c: "oph-fail", src: "Symbolic" }
      ],
      summary: "<strong>Hybrid stack.</strong> The programmatic checker catches the incomplete answer (r\u00A0=\u00A00). The PRM preserves credit on steps 1\u20134."
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

: Outcome verification scores only the endpoint and suppresses the entire trajectory. The hybrid stack uses a programmatic checker for the endpoint and a PRM for intermediate steps.

:::

The same trajectory scored by two verification regimes.
:::

## Formalization

A verifier stack with $K$ components can be written as:

$$
r_{\text{stack}}(x, y) = \operatorname{Arb}\bigl(v_1(x, y),\, v_2(x, y),\, \ldots,\, v_K(x, y)\bigr)
$$ {#eq-ch4-stack}

where each $v_i$ is a verifier component that may return a score, a categorical verdict, or a null (indicating it has no opinion), and $\operatorname{Arb}$ is the arbitration function.

Common arbitration patterns include:

- **Priority cascade**: check $v_1$ first; if it returns a verdict, use it; otherwise check $v_2$, and so on.
- **Weighted aggregation**: compute $r = \sum_i w_i \, v_i(x, y)$ for learned weights $w_i$.
- **Gated routing**: a classifier decides which component to invoke based on input features.
- **Unanimous agreement**: require all components to agree before assigning a positive reward.

The choice of arbitration pattern determines the stack's effective false-positive and false-negative rates. Priority cascade is biased toward the first component's failure modes. Weighted aggregation can dilute strong signals with weak ones. Gated routing's errors depend on the routing model. Unanimous agreement can suppress correct outputs; there is no universally correct choice.

### Hybrid verifier in code

```python
def symbolic_reward(completion: str, gold: tuple[str, ...]) -> float | None:
    answer = extract_answer(completion)
    if answer is None:
        return None
    candidate = canonicalize_answer(answer)
    return float(candidate == gold)

def hybrid_reward(completion: str, gold: tuple[str, ...], judge) -> float:
    exact = symbolic_reward(completion, gold)
    if exact is not None:
        return exact

    judge_score = judge(
        completion=completion,
        rubric="Is the final answer complete and consistent with the reasoning?"
    )
    if judge_score >= 0.8:
        return 1.0
    if judge_score <= 0.2:
        return 0.0
    return 0.0
```
::: {.column-margin}
`symbolic_reward` returns `None` when the symbolic checker fails.
:::

## Limitations

Adding components to a verifier stack can amplify errors rather than cancel them.

**Silent disagreement.** Two stack components can return conflicting verdicts on the same input.

**Correlated failures.** Components often fail on the same hard residual inputs, so stack error can remain close to the weakest component rather than shrinking like an independent product.

**Excessive complexity.** Adding a component can improve average performance while increasing stack complexity and interpretability costs.

## Open questions

- When should learned judges be first-class stack components that score every output, rather than fallbacks invoked only on the programmatic residual?
- What is the ceiling on stacking beyond which debugging costs exceed the gains?
- Can the marginal value of each stack component be quantified before deployment, or must it be measured empirically on the target task distribution?

## What comes next

The verifier stack defines what gets checked and how, not how those checks become training signal. A stack returning binary outcomes, one returing graded scores, and one returing step-level annotations will produce very different learning dynamics even if they agree on output correctness. Transforming verifier outputs into something an optimizer can use is the subject of Chapter 5.
