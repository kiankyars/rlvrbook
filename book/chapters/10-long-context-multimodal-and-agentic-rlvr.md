# Long-Context, Multimodal, and Agentic RLVR

![M. C. Escher, _Cimino Barbarano_ (1929).](../art/escher/10-cimino-barbarano.jpg){width="80%" fig-align="center"}

## Chapter Map

- Examine how RLVR stretches into long-context, multimodal, and agentic settings.
- Show why frontier tasks remain partially verifiable but become noisier, broader, and easier to misread.

## Domain Overview

This chapter should show how RLVR stretches beyond the cleanest domains without pretending the frontier is neat. Once evidence selection, perception, and environment interaction matter, the verifier often becomes a stack of partial checks rather than a single decisive rule.

The point is to show where verifier-first thinking still works and where it starts to fray.

## Verifier Regime

- Long-context verification: Checking grounded use of evidence over extended context windows.
- Multimodal verification: Checking outputs that depend on visual, auditory, or other non-textual evidence.
- Agentic verification: Checking behavior that unfolds through tool use, environment interaction, and temporal traces.

These settings move the field away from single clean checkers and toward partial, layered, and instrumented verification. The central design question becomes how much of the real task the verifier stack actually captures.

## Canonical Cases

- Citation-grounded long-context question answering.
- Vision-language tasks with verifiable perceptual subgoals.
- Tool-using agents whose traces can be checked for execution validity and grounded progress.

## Frontier coding harnesses

This is the place in the book where *harness* should become a first-class term. A frontier coding harness is not a compact GSM8K training script with a few reward functions. It is an environment-backed system for long-horizon rollouts: a repository state, a shell, tools, tests, hidden graders, task termination criteria, and instrumentation over the full trajectory.

That distinction matters because the verifier interface changes. In Chapter 5, the Brown-style script turns a final extracted answer into reward. In a coding harness, the checked object is much larger: file edits, command traces, test outcomes, runtime failures, partial progress markers, and the final repository state. Reward is usually assembled from several checks rather than one exact comparison.

This is also why frontier coding harnesses belong here rather than in the foundational verifier chapters. They are domain-specific systems for agentic RLVR, not the minimal template for the paradigm as a whole. Their difficulty is not just learning from a verifier; it is building an instrumented environment whose checks remain informative over long trajectories and resist benchmark gaming.

## Comparative Lessons

- Long-context tasks force a distinction between answer correctness and grounded evidence use.
- Multimodal tasks make perceptual ambiguity a first-class verifier problem.
- Agentic settings make temporal traces and environment instrumentation part of the verifier interface.
- Partial verification is often still useful, but it should not be oversold as full evaluation.

## Research Notes

- What is the right unit of verification for agentic trajectories?
- How can long-context tasks separate answer correctness from grounded evidence use?
- Which multimodal checks are robust enough to train against rather than only evaluate with?
