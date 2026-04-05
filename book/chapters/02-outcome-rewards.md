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

1. **Extract.** Parse the model's raw text to isolate the answer artifact. This depends on the output contract: the `<answer>` tags in our scaffold, `\boxed{}` in many math benchmarks, the final code block in a generation task, or the proof term in a formal system. If extraction fails, the reward is typically zero regardless of what the model actually produced.

2. **Normalize.** Map the extracted string to a canonical form so that surface variation does not affect grading. For math this means parsing `(2,3)` and `{3, 2}` and `x=2, x=3` into the same set object. For code it means nothing — the test harness operates on execution, not string form. For proofs, normalization is usually trivial because the proof assistant's own type checker is the canonical form.

3. **Compare.** Check the normalized candidate against the reference. This can be string equality, set equality, symbolic equivalence via a CAS, execution against a test suite, or acceptance by a proof kernel. The comparison function is where most people's intuition about "verification" lives, but it is often the least error-prone stage.

4. **Score.** Map the comparison outcome to a reward value. The simplest version is binary: 1 if correct, 0 otherwise. Graded alternatives exist — partial credit for passing some but not all tests, or a continuous score from a symbolic similarity metric — but they introduce their own failure modes, which we return to later.

The important observation is that most real failures in outcome reward systems happen in stages 1 and 2, not in stage 3. The comparison rule is usually straightforward once the inputs are clean. The fragility is in the interface contract and the normalization layer. A model that solves the problem but wraps its answer in the wrong tags scores zero. A normalizer that handles fractions but not mixed numbers silently misclassifies correct responses. These are engineering failures, not conceptual ones, but they dominate the practical difficulty of building outcome verifiers.

This pipeline framing also explains why outcome verification is domain-dependent even when the final comparison looks similar. In math, the hard part is normalization: how many surface forms can you reliably map to a single mathematical object? In code, extraction and normalization are trivial (the code is the code), but comparison is expensive (you must execute it) and incomplete (you only test what you wrote tests for). In formal proof, the entire pipeline collapses to a single call: the proof assistant either accepts the term or it does not. The stages are the same, but where the difficulty concentrates shifts across domains.

## Canonical Examples

- Exact-match grading for math problems with normalized final answers.
- Code execution against a test suite with hidden tests.
- Formal theorem acceptance in a proof assistant.
- Symbolic evaluation for structured tasks where multiple surface forms represent the same answer.

## Failure Modes

- Checker errors induced by fragile extraction or formatting assumptions.
- Benchmarks that reward shortcuts rather than the intended capability.
- Partial-credit schemes that leak exploitable heuristics.

## What the Verifier Sees

The verifier sees the final artifact: answer string, code file, proof object, or structured output that survives extraction.

## What the Verifier Misses

It misses how the artifact was produced, whether intermediate reasoning was valid, and whether success came from true competence or from exploiting narrow regularities.

## Research Notes

- When is binary scoring enough, and when is graded outcome feedback worth the complexity?
- How should hidden tests be designed to reduce benchmark gaming without drifting away from the task?
- Which extraction conventions are stable across model families?
