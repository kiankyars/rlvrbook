# Core Terminology {#sec-core-terminology}

## Reward and verifier terms

- **Verifiable reward**: A reward signal derived from an outcome, execution, proof state, trace, or other artifact that can be checked with reasonable reliability.
- **Verifier**: The mechanism that performs that check, whether symbolic, executable, formal, learned, or hybrid.
- **Reward signal**: The scalar or graded feedback that learning actually sees after verification.
- **Interface**: The part of the task exposed to checking, such as a final answer, a program, a proof state, a citation set, or an environment trajectory.
- **Outcome verifier**: A checker that scores a completed solution rather than its intermediate steps.
- **Process reward**: A reward signal attached to intermediate reasoning, subgoals, or partial traces rather than only the final artifact.
- **Programmatic verifier**: A rule-based checker implemented through deterministic logic, execution, or formal constraints.
- **Learned verifier**: A model-based judge that predicts correctness, quality, or consistency.
- **Verifier stack**: A layered pipeline that combines multiple checks before producing a reward or decision.
- **Signal quality**: How informative, stable, and hard to game the reward is for the capability of interest.

## Evaluation and robustness terms

- **Training verifier**: The verifier whose score is used as reward during RLVR.
- **Evaluation verifier**: The verifier or benchmark grader used to report results after training.
- **Audit suite**: A held-out set of checks, examples, adversarial probes, or human review items used to test the verifier itself.
- **High-reward tail**: The region of outputs selected by best-of-$N$, search, or gradient optimization because the verifier scores them highly.
- **Faithfulness**: The extent to which an externalized explanation tracks the causal basis of the model's answer.
- **Calibration**: The relationship between expressed confidence and actual correctness.

## Agentic terms

- **Harness**: The environment-backed interface that turns a model rollout into trainable and auditable data, including task inputs, tool access, state, execution, logging, and reward computation.
- **Deployment interface**: The real interface the system will use at serving time, including tools, state, latency limits, user inputs, and logging.
