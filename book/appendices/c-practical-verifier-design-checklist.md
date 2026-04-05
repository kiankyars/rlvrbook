# Practical Verifier Design Checklist

## Purpose

This appendix should read like a field manual that can be pasted into internal docs or shared directly in lab discussions.

## Core Terms

- **Verifiable reward**: A reward signal derived from an outcome, execution, proof state, trace, or other artifact that can be checked with reasonable reliability.
- **Verifier**: The mechanism that performs that check, whether symbolic, executable, formal, learned, or hybrid.
- **Reward signal**: The scalar or graded feedback that learning actually sees after verification.
- **Interface**: The part of the task exposed to checking, such as a final answer, a program, a proof state, a citation set, or an environment trajectory.
- **Outcome verifier**: A checker that scores a completed solution rather than its intermediate steps.
- **Process verifier**: A checker that scores intermediate reasoning, subgoals, or partial traces.
- **Programmatic verifier**: A rule-based checker implemented through deterministic logic, execution, or formal constraints.
- **Learned verifier**: A model-based judge that predicts correctness, quality, or consistency.
- **Verifier stack**: A layered pipeline that combines multiple checks before producing a reward or decision.
- **Signal quality**: How informative, stable, and hard to game the reward is for the capability of interest.
- **Faithfulness**: The extent to which an externalized explanation tracks the causal basis of the model's answer.
- **Calibration**: The relationship between expressed confidence and actual correctness.

## Checklist

1. What exact object is being verified?
2. What evidence does the verifier actually consume?
3. Which important properties remain off-screen?
4. Where are the obvious attack surfaces?
5. Which failures are silent rather than visible?
6. How will robustness be audited before large-scale optimization?
7. What deployment constraints shape the acceptable verifier stack?
