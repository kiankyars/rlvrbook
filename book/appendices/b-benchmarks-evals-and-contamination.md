# Benchmarks, Evals, and Contamination

## Purpose

This appendix collects evaluation hygiene issues that would otherwise interrupt the main chapters. The goal is not to survey every benchmark. The goal is to make benchmark claims legible: what changed, what was measured, what may have leaked, and how much of the result came from the policy rather than the evaluation protocol.

## What a result can be measuring

Chapter 10 used the following accounting frame:

$$
\Delta_{\mathrm{reported}}
=
\Delta_{\mathrm{policy}}
+
\Delta_{\mathrm{search}}
+
\Delta_{\mathrm{eval}}
+
\Delta_{\mathrm{leakage}}
-
\Delta_{\mathrm{tax}}.
$$

This is not a causal theorem. It is a discipline for reading numbers. $\Delta_{\mathrm{policy}}$ is the improvement amortized into the model weights. $\Delta_{\mathrm{search}}$ is the gain from extra samples, reranking, tool use, or verifier-guided inference. $\Delta_{\mathrm{eval}}$ is the gain induced by metric choices, extraction rules, prompt formats, or grading choices. $\Delta_{\mathrm{leakage}}$ is apparent improvement from contamination or benchmark familiarity. $\Delta_{\mathrm{tax}}$ is the cost paid elsewhere: calibration loss, instruction-following regressions, refusal regressions, latency, verifier spend, or human audit burden.

The point is not that benchmark gains are fake. The point is that a benchmark number is often a mixture. Tu et al. argue for parity-controlled evaluation, contamination checks, and tax-aware protocols for RLVR because real progress can be overstated when those terms are left implicit.[@tu2025hiddenrlvr]

## Metric hygiene

pass@1 and pass@$N$ answer different questions. pass@1 measures the single-sample policy under the specified decoding setup. pass@$N$ measures whether at least one of $N$ samples passes the checker. Chen et al. introduced pass@$k$ in the Codex evaluation setting, where the gap between pass@1 and pass@100 showed how much sampling alone can change the reported number.[@chen2021codex]

That distinction matters for RLVR because the same verifier can play several roles:

| Use of verifier | What it means for the result |
|---|---|
| Training reward | The policy distribution changed. |
| Rejection filter | The accepted data or rollout set changed. |
| Best-of-$N$ selector | The answer improved through sampling and ranking. |
| Search controller | The generation procedure changed. |
| Benchmark grader | The score changed, but the deployed system may not have that verifier. |

A clean report separates these roles. If the RLVR model is evaluated at pass@1 and the base model is evaluated at pass@1, the result is closer to a policy comparison. If the RLVR model is evaluated with best-of-64 and a verifier reranker, the result is policy plus search plus verifier access. That may be a useful system result, but it should not be described as only an amortized policy gain.

The strongest reports state the generation budget and verification budget explicitly: samples, tokens, search steps, tool calls, unit-test executions, judge calls, proof checks, wall-clock time, and cost. Without that accounting, the reader cannot tell whether a smaller model learned a better policy or simply spent more work at test time.

## Verifier and benchmark mismatch

A benchmark score is only as clean as the interface between model output and grader. In math-style RLVR, the interface includes extraction and canonicalization: did the model put the answer in a parseable location, and did the grader treat equivalent mathematical forms as equivalent? Math-Verify makes this explicit by separating answer extraction, conversion, and comparison.[@kydlicek2025mathverify]

In code, the interface is usually a test suite. A passing program may still be wrong if the tests miss the relevant behavior. EvalPlus is the canonical warning for this book: augmenting HumanEval with many more tests revealed false positives and changed model rankings.[@liu2023evalplus] Hidden tests reduce direct overfitting to a known suite, but hidden tests are still finite. They do not prove correctness, security, maintainability, or generalization outside the tested contract.

Learned judges add a different mismatch. An LLM-as-a-judge score can be useful in open-ended settings, but the judge may prefer style, verbosity, confidence, or familiar reasoning patterns rather than the target property.[@zheng2023judging] If a learned judge is used for training and the same judge is used for evaluation, the report should say so. An independent judge, human audit, programmatic checker, or stronger evaluation harness is needed to test whether the policy learned the task or learned the judge.

Benchmark-only answer-key grading is also different from deployable verification. A math benchmark may have a private answer key, but a deployed solver usually does not. A coding agent can often run tests, a proof agent can ask a proof kernel, and a search agent can query an environment. Reports should distinguish "the benchmark can grade this" from "the system can verify this while solving the task."

## Contamination and shortcut learning

Contamination is not just exact train-test overlap. For RLVR, the relevant leakage surface includes prompts, answers, partial prompts, solution traces, tests, generated variants, and benchmark-specific formatting conventions. A model that has seen a problem family can exploit shallow cues even when the exact item is absent.

The spurious-reward failure mode is sharper than ordinary memorization. Yan et al. argue that RLVR can activate memorization shortcuts under spurious or incorrect rewards in contaminated settings.[@yan2026spurious] The mechanism matters: the endpoint score can rise while the model's route to the answer becomes less like the capability the benchmark was meant to measure.

A useful contamination audit should therefore ask:

1. Could the model have seen the prompt, answer, or near-duplicate during pretraining, SFT, preference training, RL data construction, or synthetic data generation?
2. Could the verifier leak the answer through formatting constraints, test names, exception messages, public hidden-test discussions, or generated test artifacts?
3. Does performance persist under paraphrased prompts, perturbed constants, new test generators, independent graders, or fresh held-out problem sources?
4. Does the gain remain when test-time search and verifier access are matched?

## Honest RLVR reporting checklist

| Report item | What it isolates |
|---|---|
| Base model and checkpoint | The starting policy. |
| RLVR model and checkpoint | The trained policy being claimed. |
| Training verifier | The reward surface the policy optimized. |
| Evaluation verifier | The grader used for the reported number. |
| Independent audit verifier | Robustness to overfitting the training verifier. |
| pass@1 | Amortized single-sample policy quality. |
| pass@$N$ | Policy plus sampling. |
| Search-guided score | Policy plus active test-time control. |
| Generation budget | Samples, tokens, tool calls, and search steps. |
| Verification budget | Tests, judge calls, proof checks, and environment runs. |
| Hidden-test status | Whether the policy trained against the same tests being reported. |
| Contamination audit | Prompt, answer, partial-prompt, trace, and test leakage checks. |
| Regression tax | Calibration, abstention, refusal, safety, latency, and cost regressions. |

The minimum standard is simple: do not make the reader infer the source of the gain. If the result is a better policy, report it as a better policy. If the result is a better system because the policy is paired with search and a verifier, report it as a better system.
