# Practical Verifier Design Checklist

## Purpose

The checklist is organized around four passes. The design pass asks what the verifier sees. The robustness pass asks how the policy could exploit it. The agentic pass asks how tools, state, and environments enter the reward surface. The deployment pass asks what must be logged, versioned, and audited once the verifier is used outside a toy benchmark.

## Design pass

1. **What exact object is being verified?** Name the artifact: final answer, code patch, proof term, citation set, tool trace, environment state, or complete trajectory. A verifier that checks only the final artifact should not be described as checking the reasoning path.

2. **What evidence does the verifier consume?** Write down every input: prompt, model output, extracted answer, tests, hidden tests, tool logs, retrieved documents, proof state, judge rubric, or environment outcome.

3. **What is the output contract?** Specify the accepted format and the extraction rule. For math, this may be a boxed answer or parsed expression. For code, it may be a patch applied to a repository. For agents, it may be a sequence of tool calls and a final state.

4. **What normalization is applied?** State how equivalent answers are merged and how invalid outputs are handled. In math, this is canonicalization. In code, it may include dependency setup, timeout policy, and test discovery. In learned judging, it may include rubric parsing and score calibration.

5. **What reward scale reaches the optimizer?** Record whether the signal is binary, graded, dense, sparse, clipped, normalized within a group, or combined with penalties. The reward signal is what the optimizer sees, not what the verifier designer intended.

6. **Which important properties remain off-screen?** List the properties the verifier cannot inspect: reasoning faithfulness, security, maintainability, latency, user satisfaction, abstention quality, hidden side effects, or robustness outside the benchmark distribution.

## Robustness pass

1. **Search for high-score false positives.** Red-team the verifier for outputs that score high while failing the real task. Average held-out accuracy is not enough once best-of-$N$ or RL will select the high-reward tail.

2. **Separate visible and hidden checks.** If the policy trains against visible tests, keep an independent hidden suite or audit suite. Hidden tests do not prove correctness, but they make direct memorization harder.

3. **Test extraction and formatting attacks.** Try malformed tags, multiple answers, answer after refusal text, adversarial units, special numeric forms, skipped tests, early exits, and rubric-triggering phrases.

4. **Track verifier drift across checkpoints.** Re-evaluate the verifier on samples from $\pi_0$, intermediate checkpoints, and the final policy. RLVR changes the output distribution, so verifier validity can decay during optimization.

5. **Audit the high-reward tail.** Sample from the accepted tail: best-of-$N$ winners, search-selected candidates, and high-reward training rollouts. Chapter 7's tail-precision argument applies directly here.

6. **Patch and re-audit.** If a loophole is found, version the verifier patch and rerun the audit. OpenAI's reported unit-test escape hatches show why verifier bugs can become systemic under optimization pressure.[@baker2025monitoring]

## Agentic harness pass

Agentic RLVR makes the verifier larger than a scoring function. The harness includes tools, environment state, context windows, resets, execution sandboxes, and logging. Prime Intellect's Verifiers library and rLLM's DeepSWE example make this abstraction explicit: the reward is produced by a dataset, an environment, a harness, and a reward function or rubric, not by an isolated scalar function.[@brown2025verifiers; @rllm2026deepswe]

For an agentic harness, answer these before training:

1. **What is the action space?** Name every allowed action: search, view, edit, create, execute, browse, call tool, ask user, or stop. Invalid actions need a deterministic reward and logging policy.

2. **What state persists between actions?** Record files, editor state, retrieved documents, tool outputs, caches, conversation history, and environment variables. State leaks are reward leaks.

3. **How are resets handled?** Specify whether each rollout starts from a clean environment and whether failed tool calls, partial file writes, or dependency installs persist.

4. **What produces reward and when?** State whether reward comes from final tests, incremental tests, retrieval grounding, judge rubrics, user feedback, tool success, or a weighted mixture.

5. **Which tool failures are silent?** Timeouts, skipped tests, empty search results, swallowed exceptions, and sandbox failures should not be confused with task success.

6. **Can the agent game the instrumentation?** Look for reward from asking unnecessary clarification questions, avoiding risky actions, producing unparsable tool calls, triggering early termination, or optimizing for latency instead of correctness.

R2E-Gym is a useful reference point because it treats software-engineering tasks as executable environments with repositories, tests, and hybrid verifiers.[@jain2025r2egym] That is the right level of specificity for an agentic RLVR harness audit.

## Deployment and reporting pass

1. **Version the verifier.** A verifier update is part of the experiment. Record the code, prompt, rubric, test suite, judge model, environment image, dependency lockfile, and timeout policy.

2. **Log enough to debug reward.** Store the raw model output, extracted artifact, verifier inputs, verifier outputs, tool traces, errors, timing, and final reward. Without these, reward hacks become anecdotes rather than debuggable failures.

3. **Define escalation triggers.** Decide when a sample needs human review, independent verifier review, stronger-model review, or rollback: high reward with low independent score, sudden score jumps, rising invalid-output rate, or distribution shift in traces.

4. **Report the compute path.** Distinguish training reward, rejection filtering, best-of-$N$, search, reranking, and final benchmark grading. Appendix B gives the corresponding reporting checklist.

5. **Check the tax.** Run targeted regressions for calibration, abstention, refusal behavior, instruction following, safety, latency, and verifier cost. A verifier can improve the measured task while worsening the surrounding product behavior.

## One-page checklist

| Question | Why it matters | Failure if ignored | Book anchor |
|---|---|---|---|
| What object is verified? | Fixes the reward interface. | The claim exceeds the evidence. | Chapter 2 |
| What evidence is consumed? | Makes the verifier auditable. | Hidden inputs shape reward silently. | Chapter 2 |
| What remains off-screen? | Bounds the claim. | The model optimizes unmeasured behavior. | Chapters 7, 10 |
| Is the reward binary, graded, or dense? | Determines credit assignment. | Correct checks become weak training signal. | Chapters 3 and 5 |
| Are extraction and normalization specified? | Prevents format reward. | Formatting becomes the task. | Chapters 2 and 4 |
| Are hidden tests or audit checks separate? | Reduces direct overfitting. | The policy learns the test suite. | Chapter 7 |
| Has the high-reward tail been audited? | Tests optimizer-selected outputs. | Best-of-$N$ amplifies exploits. | Chapters 6 and 7 |
| Is verifier drift tracked across checkpoints? | Measures validity under optimization. | The verifier is only valid for the base policy. | Chapter 10 |
| Are tools and environment state logged? | Makes agentic reward debuggable. | Harness bugs become reward hacks. | Chapter 9 |
| Is the verifier versioned? | Makes results reproducible. | Patches cannot be tied to behavior changes. | Chapters 7 and 10 |
| Is test-time search separated from policy gain? | Clarifies what improved. | A system gain is misreported as model learning. | Chapters 6 and 10 |
| Are tax regressions checked? | Prevents narrow benchmark optimization. | Accuracy rises while deployment quality falls. | Chapter 10 |
