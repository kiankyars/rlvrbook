# Outcome Rewards

![M. C. Escher, _Castrovalva_ (1930).](../art/escher/02-castrovalva.jpg){width="80%" fig-align="center"}

## Chapter Map

- Explain how strong outcome verifiers are built.
- Show why answer extraction, canonicalization, and hidden brittleness matter more than the apparent simplicity suggests.

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

The verifier reads the checked artifact from `<answer>...</answer>`, canonicalizes it to the task's answer representation, and checks it against the ground-truth set.[^ch2-deepseek-r1-template]

$$
r(x,y)=
\begin{cases}
1 & \text{if } \operatorname{canon}\!\bigl(\operatorname{extract}_{\mathrm{ans}}(y)\bigr)=\{2,3\},\\
0 & \text{otherwise.}
\end{cases}
$$ {#eq-ch2-binary-check}

If the model fails the output contract (for example, omits `<answer>...</answer>`, changes surface form in a way the canonicalizer does not handle, or adds extraneous text that breaks parsing), the verifier can assign an incorrect reward even when the underlying solution is algebraically correct.

## How outcome verifiers are implemented

Current RLVR libraries do not expose a formal `extract -> normalize -> compare -> score` interface. In practice, one usually writes or selects a task-specific reward function: in TRL, a `reward_func`; in veRL, a scoring function or reward manager.[@vonwerra2020trl; @sheng2024hybridflow] For math-style tasks, those reward functions often delegate most of the work to answer-verification libraries such as Math-Verify, whose documented grading architecture is explicit: answer extraction, conversion to a common representation, and gold comparison.[@kydlicek2025mathverify]

A useful abstraction of what these implementations do is:

$$
\begin{aligned}
a(y) &= \operatorname{extract}(y),\\
\tilde{a}(y) &= \operatorname{canon}\!\bigl(a(y)\bigr),\\
v(x,y) &= \operatorname{verify}(\tilde{a}(y), g(x)),\\
r(x,y) &= \operatorname{reward}\!\bigl(v(x,y)\bigr),
\qquad r(x,y)\in[0,1].
\end{aligned}
$$ {#eq-ch2-pipeline}

Not every verifier makes each stage explicit. Some collapse canonicalization and checking into one call, and some omit canonicalization almost entirely. Code execution often has very little to canonicalize; formal proof pushes most of the verification step into the proof assistant. But the same practical pieces recur often enough that the decomposition is useful.

It is useful to compress the same object into function composition:

$$
r(x,y)=\rho\!\bigl(\operatorname{verify}(\operatorname{canon}(\operatorname{extract}(y)), g(x))\bigr).
$$ {#eq-ch2-pipeline-compressed}

Each stage does different work:

1. **Extract.** Parse the model's raw text to isolate the checked artifact. This depends on the output contract: the `<answer>` tags in our scaffold, `\boxed{}` in many math benchmarks, the final code block in a generation task, or the proof term in a formal system.

2. **Canonicalize.** Map the extracted artifact to a representation that is stable under harmless surface variation. In math this can mean parsing `(2,3)`, `{3,2}`, and `x=2, x=3` into the same set object.

3. **Verify.** Check the candidate against the reference or external environment. This can be string equality, set equality, symbolic equivalence via a CAS, execution against a test suite, or acceptance by a proof kernel.

4. **Reward.** Map the verification outcome to a reward value. The simplest version is binary: 1 if correct, 0 otherwise. Graded alternatives exist — partial credit for passing some but not all tests, or a continuous score from a symbolic similarity metric — but they introduce their own failure modes, which we return to later.

## A minimal outcome verifier in code

The core implementation can be very small. A toy math verifier for the quadratic example looks like this:

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

def verify_answer(candidate: tuple[str, ...], gold: tuple[str, ...]) -> bool:
    return candidate == gold

def outcome_reward(completion: str, gold: tuple[str, ...] = ("2", "3")) -> float:
    answer = extract_answer(completion)
    if answer is None:
        return 0.0
    candidate = canonicalize_answer(answer)
    return float(verify_answer(candidate, gold))
```

This is intentionally simple, but it already exhibits the whole chapter: extraction, canonicalization, verification, and reward. Production-grade verifiers differ mostly in how robust each stage becomes, not in whether those stages exist.

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

Where the engineering difficulty concentrates is strongly domain-dependent. In math-style RLVR, verifier design often hinges on answer-format contracts and canonicalization for deterministic parsing; in code, correctness depends heavily on the quality and coverage of the test suite; in formal proof, the core acceptance check is delegated to the proof assistant. The pieces stay similar, but the bottleneck shifts across domains.[^ch2-domain-bottlenecks]

## Outcome check, full-trajectory update

Although the verifier checks the outcome only, the optimizer updates the entire trajectory. In REINFORCE-style algorithms (including GRPO), the scalar reward from the outcome check is used to upweight or downweight the log-probability of every token in the completion. If the answer is correct, the whole chain of reasoning that produced it becomes more likely. If it is wrong, the whole chain becomes less likely.

This is the blunt instrument at the heart of outcome-based RLVR. The verifier has no opinion about which tokens in the reasoning trace were helpful and which were noise — it assigns a single number to the whole sequence. The optimizer then spreads that number uniformly across all token-level decisions. This works surprisingly well in practice, because over many rollouts and many problems, tokens that consistently appear in correct trajectories get reinforced and tokens that appear in incorrect trajectories get suppressed. But it also means that outcome rewards cannot isolate a specific reasoning step as good or bad. That distinction is exactly what process rewards (Chapter 3) provide.

## Three canonical cases: math, code, and proof

The practical verifier structure in Equation @eq-ch2-pipeline is the same across the main RLVR domains. A model emits a completion, the system extracts the checked artifact, canonicalizes it when needed, verifies it against a reference or executable criterion, and maps the result to a scalar reward. What changes from domain to domain is not the existence of these pieces, but where the real engineering difficulty sits.

In math, extraction and canonicalization dominate. The checked object is usually a final answer rather than a full derivation, so the verifier lives or dies by whether it can reliably map many surface forms onto one mathematical object. Boxed-answer conventions, XML answer tags, and task-specific output contracts are not cosmetic; they are there to make deterministic parsing possible at scale.[@shao2024deepseekmath; @deepseekai2025r1] In our toy quadratic example, `(2,3)`, `{3,2}`, and `x \in \{2,3\}` should all receive the same reward if the task asks for the solution set. A weak canonicalizer turns semantic equivalence into reward noise.

In code, the picture is almost inverted. Once the model has produced a code block, extraction is comparatively easy and canonicalization is usually minimal. The hard part is verification, because "is this program correct?" is answered by running it in a sandbox against tests, timeouts, and resource limits. Outcome-based RL for code has therefore focused on execution feedback and test-derived reward signals.[@le2022coderl; @shojaee2023ppocoder; @liu2023rltf] But execution is only as strong as the test suite and evaluation environment: limited suites can certify incorrect programs, and richer suites can change model rankings substantially.[@liu2023evalplus] The verifier is grounded, but never exhaustive.

In formal proof, the final acceptance check is strongest of all. The model outputs a proof script or term, and the proof assistant kernel either accepts it or rejects it. Recent theorem-proving systems exploit exactly this property: the endpoint check is high-fidelity, deterministic, and much harder to fake than natural-language grading.[@xin2024deepseekprover; @xin2024deepseekproverv15] But that does not mean the whole task is solved. "Valid proof of the stated theorem" is a narrow objective. The hard part shifts away from final checking and toward theorem selection, search, decomposition, and interaction with the formal environment.

## Where the apparent simplicity breaks

Outcome rewards look trivial only when the plumbing is hidden. Written as a scalar function, `r(x,y)` seems to say: take the answer, check it, assign 0 or 1. Implemented as a system, each stage becomes its own proxy with its own failure modes. An extractor can reward obedience to formatting conventions more than correctness. A canonicalizer can fail to merge equivalent answers, or worse, collapse distinct answers into one canonical form. A verifier can be perfectly implemented and still evaluate the wrong capability because the benchmark itself admits shortcuts.

This is why outcome verification should be thought of as interface design, not just scoring. The checker only sees whatever survives the interface between the model and the environment. If that interface is brittle, the model is trained against parser quirks. If the benchmark is narrow, the model is trained against benchmark regularities. If the score is graded rather than binary, the model can optimize partial credit in ways that do not track the underlying task. In code, that can mean passing easy visible tests while failing edge cases. In math, it can mean learning answer-shape regularities without robust symbolic competence. In any domain, a badly chosen partial-credit scheme can become an exploit surface rather than a better learning signal.

The central lesson is that outcome reward design is easiest to reason about when the checked artifact is both high-fidelity and hard to fake. Formal proof is close to that ideal. Code is somewhat weaker because tests are incomplete. Math is often weaker still because the final answer is a lossy projection of the reasoning that produced it. The more lossy the endpoint, the more care is required in the pipeline around it.

## What the verifier sees and misses

An outcome verifier sees only the final artifact that survives extraction: an answer string, a program, a proof term, a cited span set, or some other structured endpoint. It does not see how the model arrived there, so different trajectories that land on the same checked object are indistinguishable, while brittle interfaces can still split equivalent endpoints into different rewards.

That blindness is not automatically a defect. If the endpoint is already a strong operationalization of the task, endpoint supervision may be enough. But when the endpoint is lossy, sparse, or delayed, a correct final answer says little about whether the reasoning was robust or causally responsible for success. That is the transition to process verifiers: asking whether some intermediate structure in the path can also be checked.

## Open questions

- When is binary scoring enough, and when does graded outcome feedback improve learning enough to justify the extra exploit surface it creates?
- How should hidden tests and evaluation setups be designed so that repeated training does not simply overfit to a static benchmark?
- Which output contracts and normalization schemes remain stable across model families, prompting styles, and generations of post-trained models?
- When should equivalence be defined syntactically for reproducibility, and when is semantic comparison worth the added complexity?

[^ch2-deepseek-r1-template]: DeepSeek-R1 uses `<think>`/`<answer>` separators and applies task-specific response-shape constraints for reward parsing, including boxed final outputs when useful for deterministic math verification.[@deepseekai2025r1]
[^ch2-domain-bottlenecks]: This point is best supported domain by domain rather than as a single universal statistic. DeepSeek-R1 uses task-specific output-shape constraints for deterministic reward parsing in math-style reasoning tasks [@deepseekai2025r1]. EvalPlus shows that limited test suites can miss substantial amounts of incorrect code and even mis-rank models, making test quality and coverage central to code verification [@liu2023evalplus]. For formal theorem proving, DeepSeek-Prover describes proof assistants such as Lean as providing high-accuracy, reliable proof verification, which shifts the engineering difficulty away from the final acceptance check itself [@xin2024deepseekprover].
