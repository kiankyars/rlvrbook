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

The verifier extracts the final artifact from `<answer>...</answer>`, normalizes order, and checks against the ground-truth set. DeepSeek-R1 uses `<think>` and `<answer>` tags in its response template; for deterministic math tasks it can also add format constraints (for example, boxed expressions) when the reward parser needs a stricter extraction rule.[^ch2-deepseek-r1-template]

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

An outcome verifier checks the final artifact. It does not see the reasoning trace, the search tree, or any intermediate computation. It receives a candidate output and returns a scalar. That is the defining constraint of this chapter: everything that matters must be readable from the endpoint.

The scaffold above makes this look like a single comparison, but in practice the reward is a pipeline with at least four stages:

$$
r(x,y) = \text{score}\!\Big(\text{compare}\!\big(\text{normalize}(\text{extract}(y)),\;\text{gold}(x)\big)\Big)
$$

Each stage does different work:

1. **Extract.** Parse the model's raw text to isolate the answer artifact. This depends on the output contract: the `<answer>` tags in our scaffold, `\boxed{}` in many math benchmarks, the final code block in a generation task, or the proof term in a formal system.

2. **Normalize.** Map the extracted artifact to a canonical form so that surface variation does not affect grading. In math this can mean parsing `(2,3)`, `{3,2}`, and `x=2, x=3` into the same set object.

3. **Compare.** Check the normalized candidate against the reference. This can be string equality, set equality, symbolic equivalence via a CAS, execution against a test suite, or acceptance by a proof kernel. The comparison function is where most people's intuition about "verification" lives, but it is often the least error-prone stage.

4. **Score.** Map the comparison outcome to a reward value. The simplest version is binary: 1 if correct, 0 otherwise. Graded alternatives exist — partial credit for passing some but not all tests, or a continuous score from a symbolic similarity metric — but they introduce their own failure modes, which we return to later.

Most real failures in outcome reward systems happen before comparison. The comparison rule is often straightforward once the inputs are clean; the fragility is in the interface contract, extraction logic, and normalization layer. This is also why outcome verification is domain-dependent: math stresses normalization, code stresses execution cost and test coverage, and formal proof often delegates most of the work to the proof assistant. The stages stay the same, but the bottleneck shifts across domains.

## Outcome check, full-trajectory update

A common misreading of "outcome reward" is that only the final token gets a training signal. That is not how the update works. The verifier checks the outcome, but the optimizer updates the entire trajectory. In REINFORCE-style algorithms (including GRPO), the scalar reward from the outcome check is used to upweight or downweight the log-probability of every token in the completion. If the answer is correct, the whole chain of reasoning that produced it becomes more likely. If it is wrong, the whole chain becomes less likely.

This is the blunt instrument at the heart of outcome-based RLVR. The verifier has no opinion about which tokens in the reasoning trace were helpful and which were noise — it assigns a single number to the whole sequence. The optimizer then spreads that number uniformly across all token-level decisions. This works surprisingly well in practice, because over many rollouts and many problems, tokens that consistently appear in correct trajectories get reinforced and tokens that appear in incorrect trajectories get suppressed. But it also means that outcome rewards cannot isolate a specific reasoning step as good or bad. That distinction is exactly what process rewards (Chapter 3) attempt to provide.

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

- Outcome verifier pipeline: prompt → model output → extraction → normalization → checked artifact → reward.
- Same task, many surface forms: several answer strings collapsing to one normalized mathematical object.
- Outcome versus process preview: Chapter 2 checks the endpoint; later chapters ask what can be said about the path.

### Open questions

- When is binary scoring enough, and when is graded outcome feedback worth the complexity?
- How should hidden tests be designed to reduce benchmark gaming without drifting away from the task?
- Which extraction conventions are stable across model families?
