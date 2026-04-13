# Outcome Rewards

![M. C. Escher, _Castrovalva_ (1930).](../escher/02-castrovalva.jpg){width="80%" fig-align="center"}

## Chapter Map

- Explain how strong outcome verifiers are built.
- Show why answer extraction, canonicalization, and hidden brittleness matter.

## A Rollout

A rollout is a sample from the current policy on a prompt: the model receives an input, generates a completion or trajectory, and that sampled output is what the verifier scores.

**Prompt**

Solve the equation: $x^2-5x+6=0$.

**Completion**

```text
<think>
We can factor the quadratic: x^2 - 5x + 6 = (x-2)(x-3).
Set each factor to zero:
x - 2 = 0 -> x = 2
x - 3 = 0 -> x = 3
The final answer is the ordered tuple (2,3).
</think>

<answer>
(2,3)
</answer>
```

**Outcome reward check (for RLVR).**

The verifier reads the checked artifact from `<answer>...</answer>`, normalizes to standard form (canonicalizes) the task's answer representation, and checks it against the ground-truth set.[^ch2-deepseek-r1-template]

$$
r(x,y)=
\begin{cases}
1 & \text{if } \operatorname{canon}\!\bigl(\operatorname{extract}_{\mathrm{ans}}(y)\bigr)=\{2,3\},\\
0 & \text{otherwise.}
\end{cases}
$$ {#eq-ch2-binary-check}

If the model fails the output contract (for example, omits `<answer>...</answer>`, changes surface form in a way the canonicalizer does not handle, or adds extraneous text that breaks parsing), the verifier can assign an incorrect reward even when the underlying solution is algebraically correct.

## How outcome verifiers are implemented

A useful abstraction of outcome-verification pipelines is in three steps:

1. **Extract.** Parse the model's raw text to isolate the checked artifact. This depends on the output contract: the `<answer>` tags in our scaffold, `\boxed{}` in many math benchmarks, the final code block in a generation task, or the proof term in a formal system.

2. **Canonicalize.** Map the extracted artifact to a representation that is stable under harmless surface variation. In math this can mean parsing `(2,3)`, `{3,2}`, and `x=2, x=3` into the same set object.

3. **Reward.** Assign a reward value. The simplest version is binary: 1 if correct, 0 otherwise. Graded alternatives exist — partial credit for passing some but not all tests, or a continuous score from a symbolic similarity metric — but they introduce their own failure modes, which we return to later.

Current RLVR libraries do not have an agreed upon `extract -> canonicalize -> reward` interface. In practice, one usually writes or selects a task-specific reward function: in Transformer Reinforcement Learning (TRL), a `reward_func`; in veRL (Volcano Engine Reinforcement Learning for LLMs), a scoring function or reward manager.[@vonwerra2020trl; @sheng2024hybridflow] For math-style tasks, those reward functions often delegate most of the work to answer-verification libraries such as Math-Verify, whose documented grading architecture is explicit: answer extraction, conversion to a common representation, and gold comparison.[@kydlicek2025mathverify]

A useful abstraction of what these implementations do is:

$$
\begin{aligned}
a(y) &= \operatorname{extract}(y),\\
\tilde{a}(y) &= \operatorname{canon}\!\bigl(a(y)\bigr),\\
r(x,y) &= \operatorname{reward}\!\bigl(\tilde{a}(y), g(x)\bigr),
\end{aligned}
$$ {#eq-ch2-pipeline}

## A minimal outcome verifier

A toy math verifier for the quadratic example looks like this:

```python
import re

ANSWER_RE = re.compile(r"<answer>\s*(.*?)\s*</answer>", re.DOTALL)

def extract_answer(completion: str) -> str | None:
    match = ANSWER_RE.search(completion)
    return None if match is None else match.group(1).strip()

def canonicalize_answer(answer: str) -> tuple[str, ...]:
    text = answer.strip()
    for ch in "{}()":
        text = text.replace(ch, "")
    pieces = []
    for raw in text.split(","):
        piece = raw.strip().replace("x =", "").replace("x=", "")
        if piece:
            pieces.append(piece)
    return tuple(sorted(pieces))

def outcome_reward(completion: str, gold: tuple[str, ...] = ("2", "3")) -> float:
    answer = extract_answer(completion)
    if answer is None:
        return 0.0
    candidate = canonicalize_answer(answer)
    return float(candidate == gold)
```

::: {#fig-answer-normalization}

::: {.content-visible when-format="html"}
![](../diagrams/02-answer-normalization-light.png){.light-content}

![](../diagrams/02-answer-normalization-dark.png){.dark-content}
:::

::: {.content-visible when-format="pdf"}
![](../diagrams/02-answer-normalization-light.png)
:::

If canonicalization fails, algebraically correct answers can receive the wrong reward. The practical work is to parse the answer region, strip surface variation, and canonicalize set structure or ordering before verification.
:::

Where the engineering difficulty concentrates is strongly domain-dependent. In math-style RLVR, verifier design often hinges on answer-format contracts and canonicalization for deterministic parsing; in code, correctness depends heavily on the quality and coverage of the test suite; in formal proof, the core acceptance check is delegated to the proof assistant.[^ch2-domain-bottlenecks]

## Outcome check, full-trajectory update

Although the verifier only checks the outcome, the optimizer updates the entire trajectory. In REINFORCE-style algorithms (including GRPO), the scalar reward from the outcome check is used to upweight or downweight the log-probability of every token in the completion. If the answer is correct, the whole chain of reasoning that produced it becomes more likely. If it is wrong, the whole chain becomes less likely.

This is the blunt instrument at the heart of outcome-based RLVR. The verifier has no opinion about which tokens in the reasoning trace were helpful and which were noise — it assigns a single number to the whole sequence. The optimizer then spreads that number uniformly across all token-level decisions. This works surprisingly well in practice, because over many rollouts and many problems, tokens that consistently appear in correct trajectories get reinforced and tokens that appear in incorrect trajectories get suppressed. But it also means that outcome rewards cannot isolate a specific reasoning step as good or bad. That distinction is exactly what process rewards (Chapter 3) provide.

::: {#fig-ch2-outcome-full-trajectory-update fig-cap="Outcome verification checks only the extracted endpoint, but the update is applied across the entire sampled trajectory."}

::: {.content-visible when-format="html"}

```{=html}
<div class="ds-widget" id="ds-widget">
  <div class="ds-head">
    <p class="ds-hint">Each slot is one sampled token group. The verifier checks only the final slot, but the policy update moves the sampled option in every slot.</p>

    <div class="ds-controls">
      <div class="ds-tabs" role="tablist" aria-label="Outcome update examples">
        <button class="ds-tab ds-active" role="tab" aria-selected="true" data-mode="success">Success</button>
        <button class="ds-tab" role="tab" aria-selected="false" data-mode="failure">Failure</button>
      </div>
      <div class="ds-reward-badge" id="ds-reward-badge" aria-live="polite"></div>
    </div>
  </div>

  <div class="ds-chain" id="ds-chain"></div>

  <div class="ds-legend">
    <span class="ds-legend-item"><span class="ds-swatch ds-swatch-sampled"></span> sampled option</span>
    <span class="ds-legend-item"><span class="ds-swatch ds-swatch-other"></span> unsampled options</span>
  </div>

  <div class="ds-summary" id="ds-summary" aria-live="polite"></div>
</div>

<style>
.ds-widget { max-width: 980px; margin: 1.2em auto; font-family: var(--bs-body-font-family, system-ui, sans-serif); }
.ds-head { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 0.85rem; margin-bottom: 0.9rem; }
.ds-hint { margin: 0; max-width: 680px; font-size: 0.9em; color: var(--bs-secondary-color, #6c757d); line-height: 1.45; }
.ds-controls { display: flex; flex-wrap: wrap; align-items: center; gap: 0.7rem; }
.ds-tabs { display: inline-flex; border: 1px solid var(--bs-border-color, #dee2e6); border-radius: 999px; overflow: hidden; }
.ds-tab { background: transparent; border: none; padding: 0.45em 0.95em; cursor: pointer; font-size: 0.9em; color: var(--bs-body-color, #212529); }
.ds-tab:hover { background: var(--bs-tertiary-bg, #f8f9fa); }
.ds-tab.ds-active { background: var(--bs-primary, #2c7be5); color: #fff; }
.ds-reward-badge { padding: 0.42em 0.8em; border-radius: 999px; font-size: 0.84em; font-weight: 600; border: 1px solid transparent; }
.ds-reward-success { color: #166534; background: rgba(22, 101, 52, 0.10); border-color: rgba(22, 101, 52, 0.18); }
.ds-reward-failure { color: #b91c1c; background: rgba(185, 28, 28, 0.08); border-color: rgba(185, 28, 28, 0.18); }
.ds-chain { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 0.9rem; align-items: start; }
.ds-slot { min-width: 0; }
.ds-slot-title { margin-bottom: 0.35rem; font-size: 0.83em; font-weight: 600; color: var(--bs-body-color, #212529); }
.ds-chart {
  position: relative;
  height: 182px;
  border: 1px solid var(--bs-border-color, #dee2e6);
  border-radius: 14px;
  background:
    linear-gradient(to top, rgba(148, 163, 184, 0.08), rgba(148, 163, 184, 0.02)),
    repeating-linear-gradient(
      to top,
      transparent 0,
      transparent 23%,
      rgba(148, 163, 184, 0.18) 23%,
      rgba(148, 163, 184, 0.18) 24%
    );
  padding: 0.8rem 0.55rem 0.55rem;
}
.ds-slot.ds-checked .ds-chart {
  border: 2px dashed var(--bs-primary, #2c7be5);
  background:
    linear-gradient(to top, rgba(44, 123, 229, 0.10), rgba(44, 123, 229, 0.02)),
    repeating-linear-gradient(
      to top,
      transparent 0,
      transparent 23%,
      rgba(148, 163, 184, 0.18) 23%,
      rgba(148, 163, 184, 0.18) 24%
    );
}
.ds-bars { position: absolute; inset: 0.95rem 0.6rem 0.6rem; display: flex; align-items: flex-end; gap: 0.42rem; }
.ds-bar {
  flex: 1;
  min-height: 8px;
  border-radius: 12px 12px 5px 5px;
  background: #cbd5e1;
  transition: height 220ms ease, background-color 220ms ease, transform 220ms ease, opacity 220ms ease;
}
.ds-bar.is-sampled {
  background: #2563eb;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.28);
}
.ds-sampled-row { display: flex; align-items: center; gap: 0.45rem; margin-top: 0.55rem; min-width: 0; }
.ds-update-arrow { font-size: 1.05em; font-weight: 700; line-height: 1; }
.ds-update-up { color: #166534; }
.ds-update-down { color: #b91c1c; }
.ds-sampled-label {
  min-width: 0;
  font-size: 0.8em;
  line-height: 1.35;
  color: var(--bs-body-color, #212529);
  overflow-wrap: anywhere;
}
.ds-slot-note { margin-top: 0.22rem; font-size: 0.74em; color: var(--bs-secondary-color, #6c757d); }
.ds-check-label {
  position: absolute;
  top: 0.45rem;
  right: 0.5rem;
  padding: 0.18rem 0.45rem;
  border-radius: 999px;
  font-size: 0.67em;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: var(--bs-primary, #2c7be5);
  background: rgba(44, 123, 229, 0.12);
}
.ds-legend { display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 0.8rem; font-size: 0.82em; color: var(--bs-secondary-color, #6c757d); }
.ds-legend-item { display: inline-flex; align-items: center; gap: 0.45rem; }
.ds-swatch { width: 14px; height: 14px; border-radius: 4px; border: 1px solid var(--bs-border-color, #dee2e6); }
.ds-swatch-sampled { background: #2563eb; border-color: rgba(37, 99, 235, 0.35); }
.ds-swatch-other { background: #cbd5e1; border-color: rgba(148, 163, 184, 0.35); }
.ds-summary {
  margin-top: 0.75rem;
  padding: 0.8rem 0.95rem;
  border-radius: 12px;
  border: 1px solid var(--bs-border-color, #dee2e6);
  background: var(--bs-tertiary-bg, #f8f9fa);
  font-size: 0.89em;
  line-height: 1.5;
}
@media (max-width: 980px) {
  .ds-chain { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 620px) {
  .ds-chain { grid-template-columns: 1fr; }
}
</style>

<script>
(() => {
  const states = {
    success: {
      rewardText: "Reward = 1",
      rewardClass: "ds-reward-success",
      direction: "up",
      summary: "The sampled option in every token group is pushed up together.",
      slots: [
        { title: "1. factor", sampled: "(x-2)(x-3)", sampledIndex: 3, probs: [0.12, 0.10, 0.15, 0.63] },
        { title: "2. first root", sampled: "x = 2", sampledIndex: 0, probs: [0.61, 0.12, 0.14, 0.13] },
        { title: "3. second root", sampled: "x = 3", sampledIndex: 2, probs: [0.14, 0.11, 0.60, 0.15] },
        { title: "4. collect", sampled: "{2,3}", sampledIndex: 1, probs: [0.16, 0.58, 0.11, 0.15] },
        { title: "5. answer", sampled: "<answer>{2,3}</answer>", sampledIndex: 0, probs: [0.63, 0.12, 0.13, 0.12], checked: true }
      ]
    },
    failure: {
      rewardText: "Reward = 0",
      rewardClass: "ds-reward-failure",
      direction: "down",
      summary: "The sampled option in every token group is pushed down together, including earlier groups that may have been locally good.",
      slots: [
        { title: "1. factor", sampled: "(x-2)(x-3)", sampledIndex: 3, probs: [0.18, 0.17, 0.21, 0.44] },
        { title: "2. first root", sampled: "x = 2", sampledIndex: 0, probs: [0.41, 0.19, 0.21, 0.19] },
        { title: "3. second root", sampled: "x = 3", sampledIndex: 2, probs: [0.20, 0.18, 0.41, 0.21] },
        { title: "4. collect", sampled: "{2,3}", sampledIndex: 1, probs: [0.19, 0.45, 0.17, 0.19] },
        { title: "5. answer", sampled: "<answer>x = 2</answer>", sampledIndex: 1, probs: [0.19, 0.45, 0.18, 0.18], checked: true }
      ]
    }
  };

  const chain = document.getElementById("ds-chain");
  const slotEls = [];

  states.success.slots.forEach(() => {
    const slot = document.createElement("div");
    slot.className = "ds-slot";

    const title = document.createElement("div");
    title.className = "ds-slot-title";

    const chart = document.createElement("div");
    chart.className = "ds-chart";

    const checkLabel = document.createElement("div");
    checkLabel.className = "ds-check-label";
    checkLabel.textContent = "Verifier";
    chart.appendChild(checkLabel);

    const barsWrap = document.createElement("div");
    barsWrap.className = "ds-bars";
    const bars = [];
    for (let i = 0; i < 4; i += 1) {
      const bar = document.createElement("div");
      bar.className = "ds-bar";
      barsWrap.appendChild(bar);
      bars.push(bar);
    }
    chart.appendChild(barsWrap);

    const sampledRow = document.createElement("div");
    sampledRow.className = "ds-sampled-row";

    const arrow = document.createElement("div");
    arrow.className = "ds-update-arrow";

    const sampledLabel = document.createElement("div");
    sampledLabel.className = "ds-sampled-label";

    sampledRow.appendChild(arrow);
    sampledRow.appendChild(sampledLabel);

    const note = document.createElement("div");
    note.className = "ds-slot-note";

    slot.appendChild(title);
    slot.appendChild(chart);
    slot.appendChild(sampledRow);
    slot.appendChild(note);
    chain.appendChild(slot);

    slotEls.push({ slot, title, bars, sampledLabel, arrow, note, checkLabel });
  });

  function render(mode) {
    const state = states[mode];
    slotEls.forEach((slotEl, idx) => {
      const slot = state.slots[idx];
      slotEl.title.textContent = slot.title;
      slotEl.sampledLabel.textContent = slot.sampled;
      slotEl.arrow.textContent = state.direction === "up" ? "↑" : "↓";
      slotEl.arrow.className = "ds-update-arrow " + (state.direction === "up" ? "ds-update-up" : "ds-update-down");
      slotEl.note.textContent = slot.checked ? "checked by verifier" : "updated, not checked directly";
      slotEl.slot.classList.toggle("ds-checked", Boolean(slot.checked));
      slotEl.checkLabel.style.display = slot.checked ? "inline-flex" : "none";

      slotEl.bars.forEach((bar, barIdx) => {
        bar.style.height = `${slot.probs[barIdx] * 100}%`;
        bar.classList.toggle("is-sampled", barIdx === slot.sampledIndex);
        bar.style.opacity = barIdx === slot.sampledIndex ? "1" : "0.72";
        bar.style.transform = barIdx === slot.sampledIndex ? "translateY(-1px)" : "none";
      });
    });

    const badge = document.getElementById("ds-reward-badge");
    badge.textContent = state.rewardText;
    badge.className = "ds-reward-badge " + state.rewardClass;

    document.getElementById("ds-summary").innerHTML = state.summary;

    document.querySelectorAll(".ds-tab").forEach((button) => {
      const active = button.dataset.mode === mode;
      button.classList.toggle("ds-active", active);
      button.setAttribute("aria-selected", active ? "true" : "false");
    });
  }

  document.querySelectorAll(".ds-tab").forEach((button) => {
    button.addEventListener("click", () => render(button.dataset.mode));
  });

  render("success");
})();
</script>
```
:::

::: {.content-visible when-format="pdf"}

```text
Successful trajectory
factor as (x-2)(x-3) -> set x = 2 -> set x = 3 -> collect {2,3} -> <answer>{2,3}</answer>
                                                                  checked artifact: PASS
update over sampled token groups:  ↑  ↑  ↑  ↑  ↑

Unsuccessful trajectory
factor as (x-2)(x-3) -> set x = 2 -> set x = 3 -> collect {2,3} -> <answer>x = 2</answer>
                                                                  checked artifact: FAIL
update over sampled token groups:  ↓  ↓  ↓  ↓  ↓
```
:::

:::

## Domain specific considerations

The verifier structure in Equation @eq-ch2-pipeline is the same across the main RLVR domains. Let's discuss the domain-dependent difficulties:

| Domain | Checked object | Typical verifier | Main bottleneck | What it misses |
|---|---|---|---|---|
| Math | Final answer or structured mathematical object | Answer extraction, canonicalization, symbolic equivalence, or reference comparison [@shao2024deepseekmath; @deepseekai2025r1] | Output contracts and normalization | Reasoning faithfulness and benchmark shortcuts |
| Code | Program, patch, or execution result | Sandboxed tests, hidden tests, timeouts, and optional static checks [@le2022coderl; @shojaee2023ppocoder; @liu2023rltf] | Test coverage and flaky infrastructure | Untested behavior, security, and maintainability |
| Formal proof | Proof term, tactic trace, or proof state | Proof-assistant kernel acceptance [@xin2024deepseekprover; @xin2024deepseekproverv15] | Search, decomposition, and formalization burden | Informal usefulness, theorem choice, and proof-strategy quality |

The point is that the engineering bottlenecks depend on what the verifier can inspect. In math, `(2,3)`, `{3,2}`, and `x \in \{2,3\}` should receive the same reward when the task asks for the solution set. In code, limited suites can certify incorrect programs and richer suites can change model rankings substantially.[@liu2023evalplus] In formal proof, final acceptance is strong, but the difficulty shifts toward theorem selection, search, decomposition, and interaction with the formal environment.

## Brittleness

Each outcome reward stage has its own failure modes. An extractor can reward obedience to formatting conventions more than correctness. A canonicalizer can fail to merge equivalent answers or merge distinct answers into one canonical form. A verifier can evaluate the wrong capability because the benchmark itself admits shortcuts. In this lens, outcome verification can be thought of as interface design, since the checker only sees whatever survives the interface between the model and the environment. 

A brittle interface can mean the model is trained against parser quirks. If the reward is graded, the model can optimize partial credit in ways that do not track the underlying task. In code, that can mean passing easy visible tests while failing edge cases. When applied to math, that's learning answer-shape regularities without robust symbolic competence. In any domain, a badly chosen partial-credit scheme can become an exploit rather than a better learning signal. The central lesson is that outcome reward design is easiest to reason about when the checked artifact is high-fidelity and hard to hack.

## What the verifier misses

But when the endpoint is lossy, sparse, or delayed, a correct final answer says little about whether the reasoning was robust or causally responsible for success. That is the transition to process rewards: asking whether some intermediate structure in the path can also be checked.

## Open questions

- When is binary scoring enough, and when does graded outcome feedback improve learning enough to justify the extra exploit surface it creates?
- How should hidden tests and evaluation setups be designed so that repeated training does not simply overfit to a static benchmark?
- Which output contracts and normalization schemes remain stable across model families, prompting styles, and generations of post-trained models?
- When should equivalence be defined syntactically for reproducibility, and when is semantic comparison worth the added complexity?

[^ch2-deepseek-r1-template]: DeepSeek-R1 uses `<think>`/`<answer>` separators and applies task-specific response-shape constraints for reward parsing, including boxed final outputs when useful for deterministic math verification.[@deepseekai2025r1]
[^ch2-domain-bottlenecks]: This point is best supported domain by domain rather than as a single universal statistic. DeepSeek-R1 uses task-specific output-shape constraints for deterministic reward parsing in math-style reasoning tasks [@deepseekai2025r1]. EvalPlus shows that limited test suites can miss substantial amounts of incorrect code and even mis-rank models, making test quality and coverage central to code verification [@liu2023evalplus]. For formal theorem proving, DeepSeek-Prover describes proof assistants such as Lean as providing high-accuracy, reliable proof verification, which shifts the engineering difficulty away from the final acceptance check itself [@xin2024deepseekprover].
