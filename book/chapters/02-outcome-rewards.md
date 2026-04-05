# Outcome Rewards

## Chapter Map

- Explain how strong outcome verifiers are built.
- Show why extraction, representation, and hidden brittleness matter more than the apparent simplicity suggests.

## A Rollout

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

The verifier extracts the final artifact from `<answer>...</answer>`, normalizes order, and checks against the ground-truth set.[^ch2-deepseek-r1-template]

$$
r(x,y)=
\begin{cases}
1 & \text{if } \text{normalize}(\text{extract\_ans}(y))=\{2,3\},\\
0 & \text{otherwise.}
\end{cases}
$$

If the model fails the output contract (for example, omits `<answer>...</answer>`, changes order without normalization, or adds extraneous text that breaks parsing), the verifier can assign an incorrect reward even when the underlying solution is algebraically correct.

[^ch2-deepseek-r1-template]: DeepSeek-R1 uses `<think>`/`<answer>` separators and applies task-specific response-shape constraints for reward parsing, including boxed final outputs when useful for deterministic math verification.[@deepseekai2025r1]

## The outcome verifier pipeline

An outcome verifier receives a candidate output and returns a scalar, i.e. everything that matters must be readable from the endpoint. In practice the reward is a pipeline with at least four stages:

$$
r(x,y)=\mathrm{score}\!\Big(\mathrm{compare}\!\big(\mathrm{normalize}(\mathrm{extract}(y)),\; g(x)\big)\Big),
\qquad r(x,y)\in[0,1].
$$

It is useful to compress the same object into function composition:

$$
r(x,y)=s\!\big(c(n(e(y)),\,g(x))\big).
$$

Each stage does different work:

1. **Extract.** Parse the model's raw text to isolate the answer artifact. This depends on the output contract: the `<answer>` tags in our scaffold, `\boxed{}` in many math benchmarks, the final code block in a generation task, or the proof term in a formal system.

2. **Normalize.** Map the extracted artifact to a canonical form so that surface variation does not affect grading. In math this can mean parsing `(2,3)`, `{3,2}`, and `x=2, x=3` into the same set object.

3. **Compare.** Check the normalized candidate against the reference. This can be string equality, set equality, symbolic equivalence via a CAS, execution against a test suite, or acceptance by a proof kernel. The comparison function is where most people's intuition about "verification" lives, but it is often the least error-prone stage.

4. **Score.** Map the comparison outcome to a reward value. The simplest version is binary: 1 if correct, 0 otherwise. Graded alternatives exist — partial credit for passing some but not all tests, or a continuous score from a symbolic similarity metric — but they introduce their own failure modes, which we return to later.

::: {#fig-answer-normalization}
![](../diagrams/02-answer-normalization-light.png){.light-content}

![](../diagrams/02-answer-normalization-dark.png){.dark-content}

If normalization fails, algebraically correct answers can receive the wrong reward. The practical work is to parse the answer region, strip surface variation, and canonicalize set structure or ordering before comparison.
:::

Where the engineering difficulty concentrates is strongly domain-dependent. In math-style RLVR, verifier design often hinges on answer-format contracts and normalization for deterministic parsing; in code, correctness depends heavily on the quality and coverage of the test suite; in formal proof, the core acceptance check is delegated to the proof assistant. The stages stay the same, but the bottleneck shifts across domains.[^ch2-domain-bottlenecks]

[^ch2-domain-bottlenecks]: This point is best supported domain by domain rather than as a single universal statistic. DeepSeek-R1 uses task-specific output-shape constraints for deterministic reward parsing in math-style reasoning tasks [@deepseekai2025r1]. EvalPlus shows that limited test suites can miss substantial amounts of incorrect code and even mis-rank models, making test quality and coverage central to code verification [@liu2023evalplus]. For formal theorem proving, DeepSeek-Prover describes proof assistants such as Lean as providing high-accuracy, reliable proof verification, which shifts the engineering difficulty away from the final acceptance check itself [@xin2024deepseekprover].

## Outcome check, full-trajectory update

Although the verifier checks the outcome only, the optimizer updates the entire trajectory. In REINFORCE-style algorithms (including GRPO), the scalar reward from the outcome check is used to upweight or downweight the log-probability of every token in the completion. If the answer is correct, the whole chain of reasoning that produced it becomes more likely. If it is wrong, the whole chain becomes less likely.

This is the blunt instrument at the heart of outcome-based RLVR. The verifier has no opinion about which tokens in the reasoning trace were helpful and which were noise — it assigns a single number to the whole sequence. The optimizer then spreads that number uniformly across all token-level decisions. This works surprisingly well in practice, because over many rollouts and many problems, tokens that consistently appear in correct trajectories get reinforced and tokens that appear in incorrect trajectories get suppressed. But it also means that outcome rewards cannot isolate a specific reasoning step as good or bad. That distinction is exactly what process rewards (Chapter 3) provide.

## Remaining sections

The following sections still need to be expanded into full prose. The plan and the current stubs are merged here as a writing guide.

### Three canonical cases: math, code, and proof

Each case should show what the outcome verifier pipeline looks like concretely in that domain — where extraction, normalization, and comparison concentrate their difficulty — and carry the running math example forward where possible.

- **Math.** Exact-match grading with normalized final answers. The hard part is normalization: how many surface forms can you map to a single mathematical object? Symbolic evaluation for structured tasks where `(2,3)`, `{3,2}`, and `x ∈ {2,3}` must all resolve to the same set. SymPy equivalence vs string match. Boxed-answer conventions and their brittleness.
- **Code.** Execution against a test suite with visible and hidden tests. Extraction and normalization are trivial (the code is the code), but comparison is expensive (execution) and incomplete (you only test what you wrote tests for). Sandboxing, timeout handling, and the gap between "passes tests" and "is correct."
- **Formal proof.** Theorem acceptance in a proof assistant (Lean, Coq). The entire pipeline collapses to a single call: the proof kernel either accepts the term or it does not. The signal is binary and unfakeable, but "valid proof" ≠ "interesting theorem."

### Where the apparent simplicity breaks

This is the chapter's payoff: outcome rewards look simple only if the plumbing is ignored. Each failure mode should connect back to a specific pipeline stage.

- Checker errors induced by fragile extraction or formatting assumptions (stages 1–2).
- Benchmarks that reward shortcuts rather than the intended capability (stage 3 — the comparison is correct but the task is not testing what we think).
- Partial-credit schemes that leak exploitable heuristics (stage 4).
- Brittle parsing, unstable benchmarks, exploitable partial credit, and checker quirks as recurring themes.

### What the verifier sees and misses

The verifier sees the final artifact: answer string, code file, proof object, or structured output that survives extraction. It misses how the artifact was produced, whether intermediate reasoning was valid, and whether success came from true competence or from exploiting narrow regularities. This section should set up the transition to process rewards in Chapter 3.

### Figures needed

- Answer normalization: several surface-form answers collapsing to one canonical checked object, with the failure mode that a correct answer can still receive the wrong reward if parsing or normalization fails.


### Open questions

- When is binary scoring enough, and when is graded outcome feedback worth the complexity?
- How should hidden tests be designed to reduce benchmark gaming without drifting away from the task?
- Which extraction conventions are stable across model families?
