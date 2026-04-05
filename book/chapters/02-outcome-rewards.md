# Outcome Rewards

## Chapter Map

- Explain how strong outcome verifiers are built.
- Show why extraction, representation, and hidden brittleness matter more than the apparent simplicity suggests.

## Starting scaffold

**Prompt.**

Solve the equation: $x^2-5x+6=0$.

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
r(x,y)=\mathbb{I}[\text{normalize}(\text{extract\_ans}(y))=\{2,3\}]
$$

If the model fails the output contract (for example, omits `<answer>...</answer>`, changes order without normalization, or adds extraneous text that breaks parsing), the reward drops to 0 even if the algebra is correct.

[^ch2-deepseek-r1-template]: DeepSeek-R1 uses `<think>`/`<answer>` separators and applies task-specific response-shape constraints for reward parsing, including boxed final outputs when useful for deterministic math verification.[@deepseekai2025r1]

## Recommended build

This should be the first chapter where the book starts to feel technical. It should probably be the first chapter with real artifacts on the page: one or two equations, two or three diagrams, and one running example carried through the whole chapter.

The cleanest running example is math. Start with a concrete checked answer, then widen to code and formal proof. The point is to make outcome rewards feel operational before they feel abstract.

- Open with one concrete example: model output, extraction, normalization, and final check.
- Define the object: an outcome verifier checks the final artifact, not the path used to produce it.
- Add the minimal math: start with `r(x,y)=V(\mathrm{extract}(y), x)` and then make clear that the practical reward is a pipeline rather than a single comparison.
- Move to the three canonical cases: math, code, and proof.
- End by showing where the apparent simplicity breaks: brittle parsing, unstable benchmarks, exploitable partial credit, and checker quirks.

The core engineering tension of the chapter is that outcome rewards look simple only if the plumbing is ignored. In practice, the chapter is really about building a reliable final-output-to-reward map: output contract, extraction, normalization, correctness check, and grading granularity.

The most useful figures for this chapter would be:

- Outcome verifier pipeline: prompt -> model output -> extraction -> normalization -> checked artifact -> reward.
- Same task, many surface forms: several answer strings collapsing to one normalized mathematical object.
- Outcome versus process preview: chapter 2 checks the endpoint, while later chapters ask what can be said about the path.

## Main Argument

Outcome verifiers are the natural entry point for RLVR because they are operationally simple and often highly scalable. They become useful when the mapping from model output to checked object is stable, unambiguous, and hard to exploit.

This chapter should focus on answer normalization, format design, theorem checking, executable grading, partial credit, and benchmark hygiene. The hard part is often not the final comparison rule but the interface contract that determines what is being compared.

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
