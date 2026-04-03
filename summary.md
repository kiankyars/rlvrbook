# Reinforcement Learning from Verifiable Rewards

_Working summary for the book design_  
_Last updated: April 3, 2026_

## Core Thesis

This book should treat RLVR as the study of verifiers, not as a subcase of reinforcement learning and not as a chronology of optimizer papers. The central object is the verifier: what it can check, what evidence it consumes, what proxy it induces, how it interacts with search, and how it fails. Policy optimization matters, but it belongs in the background. If the book is successful, a reader should come away thinking more clearly about verifier design, verifier limits, and verifier-driven post-training than about any particular policy-gradient variant.

The intended audience is not a beginner RL class. The audience is frontier-lab researchers, post-training engineers, eval researchers, and technically ambitious readers who need a precise reference for building and reasoning about verifiable training loops. The book should be durable across optimizer fashions and model generations.

## Editorial Stance

This is not a general RL textbook with an RLVR unit added near the end. It is also not a broad "reasoning models" book where RLVR is one tool among many. It is a focused treatment of verifiers as the bottleneck, enabler, and failure mode of modern reasoning post-training.

Three editorial choices should drive the whole manuscript:

1. Verifier-first. Every major chapter should be organized around what is being verified, how verification is implemented, and what training or inference behavior that verification induces.
2. Failure-aware. Reward hacking, proxy misspecification, calibration failures, and unfaithful reasoning should appear early and often, not as a cleanup chapter after the exciting material.
3. Domain-grounded. The book should stay concrete by repeatedly returning to math, code, formal proof, long-context grounding, and agentic tool use.

## Proposed Table of Contents

### Part I. Foundations

#### 1. The Verifier Lens

The opening chapter should define the field at a high level: what "verifiable" means, why RLVR became central to reasoning post-training, and why the verifier is the right unit of analysis. This chapter should explain the shift from preference-heavy post-training toward domains where correctness can be checked more directly, while being careful not to pretend that "verifiable" means "solved" or "objective" in a naive sense. It should also define the core triad of task, trajectory, and verifier, because most of the later design questions reduce to how those three pieces fit together.

This chapter should leave the reader with one durable idea: RLVR succeeds when the verifier captures enough of the capability we care about to make optimization useful, and fails when the verifier is too weak, too narrow, or too gameable.

#### 2. What Can Be Verified?

This chapter should build a taxonomy of verifiable objectives. It should distinguish final-answer verification, intermediate-step verification, execution-based checks, proof-based checks, retrieval-grounded checks, simulation- or environment-based checks, and hybrid schemes that combine several signals. The goal is to give the reader a language for asking, before any training begins, what aspects of a task are actually checkable and at what granularity.

This is also where the book should introduce the idea that verification is not binary across tasks but layered. Some domains allow exact outcome checks, some allow only partial checks, and some allow strong checks only after instrumentation or decomposition. That distinction is foundational and should be treated as such.

### Part II. Verifier Design

#### 3. Outcome Verifiers

This chapter should study verifiers that score completed solutions: exact-match checkers, extraction pipelines, unit tests, theorem checkers, symbolic evaluators, hidden tests, and domain-specific graders. The emphasis should be on the design details that determine whether outcome verification is actually informative in practice: answer normalization, format constraints, ambiguity handling, partial credit, adversarial examples, and benchmark hygiene.

The chapter should make clear that outcome verifiers are appealing because they are simple and scalable, but they push enormous weight onto representation choices. A badly designed output format or checker can turn a seemingly crisp reward into noise or into a reward-hacking invitation.

#### 4. Process Verifiers

This chapter should cover process supervision and stepwise verification in a serious way. It should explain when intermediate reasoning can be labeled or checked, how process rewards differ from outcome rewards, and why dense signals can help when final-answer rewards are too sparse or too weak. It should also engage directly with the subtle point that a process verifier is only useful when the notion of a "good step" is itself coherent and operationalizable.

A strong version of this chapter would treat process verifiers not as a moral preference for readable reasoning, but as an engineering response to credit assignment. That framing keeps the discussion grounded and helps separate genuinely useful process supervision from cosmetic chain-of-thought preference shaping.

#### 5. Learned, Programmatic, and Hybrid Verifiers

Many real systems do not rely on a single hand-written checker. This chapter should explain the spectrum from purely programmatic verifiers to learned judges and composite pipelines that mix rule-based checks, model-based judgments, retrieval, execution, and appeals. The key questions are reliability, bias, calibration, attack surface, and how errors compound when multiple imperfect components are wired together.

This chapter is where the book should teach readers to think in terms of verifier stacks rather than single rewards. In practice, frontier systems increasingly use layered verification pipelines, and the book should give a principled vocabulary for designing and auditing those stacks.

### Part III. From Verifiers to Capability

#### 6. Turning Checks into Training Signal

This chapter should answer the practical question: once a verifier exists, how does it become a useful learning signal? The emphasis should stay on signal quality rather than optimizer novelty. Topics should include sparse versus dense rewards, binary versus graded rewards, data curation, problem selection, rollout filtering, curriculum design, trajectory grouping, and when simple rejection sampling or best-of-N already captures much of the value.

The optimizer discussion should be intentionally restrained here. The reader needs just enough machinery to understand how verifier outputs shape policy updates, but the chapter should keep returning to the more important issue: different verifiers induce different optimization landscapes, and most practical wins come from better signal design rather than from exotic update rules.

#### 7. Search and Test-Time Verification

RLVR is not just about training-time rewards. This chapter should explain how verification interacts with inference-time compute: self-consistency, reranking, deliberation, draft-and-check loops, tool-augmented checking, and more structured search over candidate solutions. In many domains, the verifier matters as much at test time as it does during training, and the book should make that connection explicit.

This chapter should also clarify the relationship between learning and search. Search can expose what a verifier makes possible before the model fully internalizes the behavior, while training can amortize search into policy competence. That interplay is central to modern reasoning systems and deserves its own chapter rather than a side discussion.

### Part IV. Failure Modes

#### 8. Reward Hacking, Proxy Misspecification, and Verifier Robustness

This should be one of the core chapters of the book, not a cautionary appendix. It should cover classical reward hacking, exploitation of checker bugs, overfitting to benchmark artifacts, format gaming, verifier over-optimization, spurious intermediate steps, and failures caused by imperfect or biased judge models. It should also discuss practical mitigations: verifier ensembles, hidden tests, adversarial audits, regularization, abstention, uncertainty estimates, and checker hardening.

The chapter should repeatedly stress a hard truth: a verifier is not merely an evaluation function but an attack surface. Any serious RLVR reference that does not build this mindset into the reader early will age badly.

#### 9. Faithfulness, Confidence, and What Verification Misses

Not everything that matters is verifiable from outputs alone. This chapter should address the gap between correct answers and trustworthy reasoning, the limits of chain-of-thought observability, self-verification failures, confidence miscalibration, and cases where a model learns to satisfy the verifier without developing the intended internal competence. The point is not to dismiss RLVR, but to define its frontier and its blind spots.

This chapter is important because it keeps the book intellectually honest. Frontier readers will rightly distrust any manuscript that implies verifiable success is equivalent to robust reasoning or aligned cognition. The book should state those distinctions clearly.

### Part V. Domains and Frontiers

#### 10. Canonical Domains: Math, Code, and Formal Proof

This chapter should serve as the main concrete case-study chapter for the book. Math belongs here because it was the canonical early domain for large-scale RLVR. Code belongs here because executable rewards, hidden tests, and flaky sandboxes create a different but equally important verifier regime. Formal proof belongs here because proof assistants give perhaps the cleanest strong verifier available, while also surfacing decomposition and search challenges in unusually sharp form.

The point of putting these together is not to collapse them into one task family, but to show the reader how verifier design changes when the object being checked changes. These three domains together provide the right backbone for the book.

#### 11. Long-Context, Multimodal, and Agentic RLVR

This chapter should cover the frontier where verification becomes more indirect and more operationally interesting. Long-context tasks require verifying grounded use of evidence rather than only final answers. Multimodal tasks introduce perceptual ambiguity and partial observability into the verifier. Agentic settings bring tool use, environment feedback, temporal credit assignment, and execution traces into play.

This chapter should be written carefully, because it is where hype pressure will be strongest. The goal is not to claim that all agentic behavior is now neatly verifiable. The goal is to show how far the verifier framework stretches, where it remains powerful, and where it starts to crack.

#### 12. Open Problems and the Research Agenda

The final chapter should describe the unresolved questions that are likely to matter over the next several years. How should we design stronger process verifiers without leaking brittle heuristics? When do learned judges become useful enough to trust, and when do they merely add another failure layer? How do we distinguish genuine reasoning gains from search amplification or benchmark exploitation? How should RLVR interact with safety, abstention, uncertainty, and alignment constraints?

This chapter should not read like a miscellaneous list. It should synthesize the argument of the book: progress in RLVR depends less on discovering the next optimizer tweak and more on building richer, harder-to-game, better-instrumented verifier ecosystems.

## Appendices

### Appendix A. Minimal RL and Post-Training Background

This appendix should provide the minimum reinforcement learning material needed to read the main text: trajectories, returns, KL regularization, policy gradients, PPO-style clipping, group-relative baselines, and the difference between rejection sampling, search, and policy optimization. It should exist to support the main book, not to compete with standard RL textbooks.

### Appendix B. Benchmarks, Evals, and Contamination

This appendix should collect benchmark design issues that would otherwise interrupt the flow of the main chapters: leakage, contamination, train-test overlap, benchmark saturation, extraction protocol mismatches, hidden tests, and pass@k-style reporting pitfalls.

### Appendix C. Practical Verifier Design Checklist

This appendix should be a compact field manual. Given a new domain, what should a researcher ask before deploying RLVR? What is the target object of verification? What evidence is available? Where are the obvious attack surfaces? Which failures are silent? What audits are required before the reward is trusted? This appendix is the kind of material people should actually paste into internal docs and Slack threads.

## Recommended Chapter Template

If this is meant to become a standard reference, each chapter should have a consistent internal structure. That structure should be optimized for fast retrieval, not only for linear reading.

Each main chapter should contain:

1. A one-page chapter map that states the central question, the key distinction, and the main failure mode.
2. A precise terminology section that fixes vocabulary before examples start.
3. One or two canonical design patterns drawn from real domains.
4. A failure analysis section with concrete anti-patterns.
5. A short "what the verifier sees and does not see" section.
6. A closing research notes section that points to open questions rather than only summarizing prior work.

## What This Book Is Not

This book should not be organized around a timeline of papers. It should not spend disproportionate space on optimizer variants. It should not assume that reasoning quality is fully legible from surface chains of thought. And it should not overfit itself to a single benchmark family just because math happened to be the first clean domain where RLVR scaled well.

If the book stays disciplined on those points, it has a real chance to become the reference document people send around when they need to get serious about verifier-driven post-training.
