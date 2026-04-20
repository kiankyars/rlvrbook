# RLVR Book

This repository contains **Reinforcement Learning from Verifiable Rewards**, a reference book on RLVR as a paradigm for learning from verifiable reward signals.

## Book Style

- One Markdown file per chapter and appendix, compiled with Quarto to HTML and PDF.
- Every main chapter opens with an M. C. Escher image.
- Every main chapter begins with a short two-bullet chapter map.

## Commands

- `quarto render book`
- `scripts/check-citations`
- `scripts/check-diagrams`

## Review status

- [x] 1. Introduction
- [x] 2. Outcome Rewards
- [x] 3. Process Rewards
- [x] 4. Learned, Programmatic, and Hybrid Verifiers
- [x] 5. Turning Checks into Training Signal
- [x] 6. Search and Test-Time Verification (still need to verify equations)
- [x] 7. Reward Hacking (still need to verify equations)
- [x] 8. A Frontier Recipe
- [] 9. Long-Context, Multimodal, and Agentic RLVR (openenv)
- [] 10. Open Problems
- [x] a
- [x] b
- [x] c
- [x] Review subagents on every chapter
      **Findings**
- [01-introduction.md:12](/Users/kian/Developer/rlvrbook/book/chapters/01-introduction.md#L12): the book’s core object is unstable. Chapter 1 defines RLVR via directly checkable rewards, then folds `LLM-as-judge` into the same native map, which conflicts with Chapter 4’s narrower claim that learned verifiers are boundary cases rather than verifiable rewards in the strict sense. What do you recommend I do in this case, because LLM as a judge is used in the literature as a surrogate for RLVR, which is why I have included it; however, I understand that it is not verifiable in the canonical sense?
- [01-introduction.md:33](/Users/kian/Developer/rlvrbook/book/chapters/01-introduction.md#L33): “RLVR is the oldest paradigm in reinforcement learning” teaches the wrong abstraction boundary. It collapses classical RL into the much more specific LLM post-training regime this book is actually about. This point is moot since I demonstrate that this is not the same in the next sentence.
- [02-outcome-rewards.md:121](/Users/kian/Developer/rlvrbook/book/chapters/02-outcome-rewards.md#L121): the “full-trajectory update” explanation is slightly wrong. It speaks as if raw reward uniformly pushes every token up or down, but the actual training object is advantage-weighted log-probability on the sampled trajectory; that distinction matters later in Chapters 5 and 6. So here I'm trying to generalize to reinforce the algorithms, which do not all use advantage-weighted log probability. Therefore, I'd like your advice on whether I should make this nuance clear in the sentence for the case of GRPO or otherwise.
- [03-process-rewards.md:33](/Users/kian/Developer/rlvrbook/book/chapters/03-process-rewards.md#L33): the two motivating rollout examples are referred to in reverse order. That is a real teaching error because it flips false negative versus self-correction at the point where the chapter is establishing why process supervision exists. Has been corrected. Thank you for noting this error.
- [03-process-rewards.md:63](/Users/kian/Developer/rlvrbook/book/chapters/03-process-rewards.md#L63): the Monte Carlo section conflates step correctness with expected downstream success from a prefix. That is the central conceptual distinction of the chapter, so it needs to be exact. I don't see the connection. We are saying that to estimate whether step T is correct, we perform n rollouts from that step and then take some aggregate over the rollouts to determine the estimated correctness.
- [04-learned-programmatic-and-hybrid-verifiers.md:12](/Users/kian/Developer/rlvrbook/book/chapters/04-learned-programmatic-and-hybrid-verifiers.md#L12): the chapter never states crisply that it changes axes. The reader needs one explicit sentence that Chapters 2–3 classify where signal attaches, while Chapter 4 classifies how the verifier is implemented. This is addressed in line 12.
- [04-learned-programmatic-and-hybrid-verifiers.md:35](/Users/kian/Developer/rlvrbook/book/chapters/04-learned-programmatic-and-hybrid-verifiers.md#L35): the LLM-as-a-judge section overclaims from RLHF/judge literature and blurs preference evaluation with verification. This weakens the book’s RLVR-specific ontology. Once again, this is in relation to the previous note you made on RLHF. How do you suppose that I address this, because in fact LLMs are used in RLVR, or at least in the RLVR section, along with math and other verifiable domains (for example, to test instruction following). In other words, did the model give you two paragraphs with one bolded word, et cetera, if that's what you requested? It's literally in the old paper, and therefore I will include this. The question is how should I include this such that it does not blur preference evaluation with verification?
- [05-turning-checks-into-training-signal.md:446](/Users/kian/Developer/rlvrbook/book/chapters/05-turning-checks-into-training-signal.md#L446): there is a semantic inversion. The text says the reported numbers show why filtering, rollout budget, and shaping are “not” important, but the surrounding argument says the opposite. Fixed.
- [05-turning-checks-into-training-signal.md:389](/Users/kian/Developer/rlvrbook/book/chapters/05-turning-checks-into-training-signal.md#L389): the GRPO paragraph teaches the wrong optimizer mental model by conflating clipping, LoRA parameterization, and group normalization with trust-region style control. Are you saying that whether or not you use KL divergence is completely orthogonal to having a value function versus an estimation based on the advantage of a group rollout? In which case I agree, and I think perhaps we just delete all of the sentences after the first one in line 395.
- [06-search-and-test-time-verification.md:181](/Users/kian/Developer/rlvrbook/book/chapters/06-search-and-test-time-verification.md#L181): the math models the wrong object for most of the chapter’s own methods. The chapter reduces selection to binary accept/reject, but much of the actual discussion is about score-based reranking and tail misranking. I, to be completely honest, just wanted to add some mathematical motivation for this chapter, and this is what I came up with. If you have a suggestion on how I should change this, then please go ahead. Also, I made this section much more limpid in terms of its comprehensibility, so maybe that will make you change your mind. Don't just agree with me to satisfy me, because you should be a steel man.
- [07-reward-hacking-and-verifier-robustness.md:189](/Users/kian/Developer/rlvrbook/book/chapters/07-reward-hacking-and-verifier-robustness.md#L189): the PDF fallback for the overoptimization figure uses exact numeric values that appear schematic, not empirical. Unless marked illustrative, it teaches false quantitative beliefs. Fixed.
- [07-reward-hacking-and-verifier-robustness.md:240](/Users/kian/Developer/rlvrbook/book/chapters/07-reward-hacking-and-verifier-robustness.md#L240): hidden tests are stated too absolutely. They reduce direct overfitting to visible checks; they do not guarantee robustness. Fixed.

- [08-a-frontier-recipe.md:15](/Users/kian/Developer/rlvrbook/book/chapters/08-a-frontier-recipe.md#L15): Chapter 8 blurs strict RLVR with a broader hybrid post-training stack without saying so. It also promises a “recipe” but mostly gives a component inventory rather than a carried-through prompt-to-update pipeline.
- [09-long-context-multimodal-and-agentic-rlvr.md:1](/Users/kian/Developer/rlvrbook/book/chapters/09-long-context-multimodal-and-agentic-rlvr.md#L1): the title promises three frontiers, but the content is almost entirely agentic coding. That is the sharpest mismatch between title and delivered content in the book.
- [09-long-context-multimodal-and-agentic-rlvr.md:31](/Users/kian/Developer/rlvrbook/book/chapters/09-long-context-multimodal-and-agentic-rlvr.md#L31): the DeepSWE metrics are not reported precisely enough to distinguish training quality from reranked inference quality.
- [10-open-problems-and-the-research-agenda.md:9](/Users/kian/Developer/rlvrbook/book/chapters/10-open-problems-and-the-research-agenda.md#L9): this is not yet an open-problems chapter. It is a short epilogue fragment, not a research agenda with named problems, examples, and crisp invariants.

**Cross-chapter diagnosis**

- The main recurring problem is taxonomy drift. The book needs one early three-axis frame and then strict reuse of it: checked object (`outcome` vs `process`), verifier implementation (`programmatic` vs `learned` vs `hybrid`), and deployment setting (`train-time` vs `test-time`).
- The second recurring problem is pedagogy drift. The book is strongest when it starts from a concrete checked interface, then abstracts. Chapters 1, 8, 9, and 10 violate that pattern most often.
- The third recurring problem is frontier honesty. Chapters 2, 5, and 6 are close to reference-work quality. Chapters 8, 9, and 10 are materially weaker and either need more scope or narrower titles.
- `scripts/check-citations` and `scripts/check-diagrams` pass, so the dominant issues are conceptual and pedagogical, not repository hygiene.

**Chapter-by-chapter revision direction**

- Chapter 1: stabilize the ontology, fix the causal sentence in “verifiable tasks,” and seed the same running example later used in Chapters 2 and 3.
- Chapter 2: tighten the `extract -> canonicalize -> reward` interface and correct the trajectory-update language so it matches later optimizer chapters.
- Chapter 3: fix the reversed example, separate step validity from prefix value, and make the PRM object more typed and explicit.
- Chapter 4: narrow the learned-verifier claims, make the axis change explicit, and fix the hybrid-stack formalization so it is conceptually well-typed.
- Chapter 5: repair the factual errors, separate correctness vs shaping vs graded partial credit, and give a pre-code walkthrough of one prompt-to-update cycle.
- Chapter 6: start from one concrete test-time workflow and either inherit Chapter 7’s tail-score formulation or clearly label the binary model as a simplification.
- Chapter 7: center the chapter on high-pressure tail behavior, not average verifier accuracy, and mark any invented numbers as illustrative.
- Chapter 8: turn it into an explicitly scoped case study of a hybrid frontier stack, not a universal RLVR recipe.
- Chapter 9: either broaden it to truly cover long-context and multimodal verification or rename it to an agentic harness chapter.
- Chapter 10: rebuild it as 4–6 named open problems, each with a concrete example and a statement of what progress would look like.

**Staged plan**

1. Fix the real factual/teaching errors first: Chapter 3 example inversion, Chapter 5 line 446, Chapter 5 optimizer explanation, Chapter 6 selection math framing, Chapter 7 schematic numbers, Chapter 9 metric ambiguity.
2. Do one taxonomy pass across [01-introduction.md](/Users/kian/Developer/rlvrbook/book/chapters/01-introduction.md), [04-learned-programmatic-and-hybrid-verifiers.md](/Users/kian/Developer/rlvrbook/book/chapters/04-learned-programmatic-and-hybrid-verifiers.md), [06-search-and-test-time-verification.md](/Users/kian/Developer/rlvrbook/book/chapters/06-search-and-test-time-verification.md), [08-a-frontier-recipe.md](/Users/kian/Developer/rlvrbook/book/chapters/08-a-frontier-recipe.md), and [09-long-context-multimodal-and-agentic-rlvr.md](/Users/kian/Developer/rlvrbook/book/chapters/09-long-context-multimodal-and-agentic-rlvr.md).
3. Rebuild the frontier block: make Chapter 8 a case study, make Chapter 9 honest about scope, and make Chapter 10 a real agenda chapter.
4. Then do the copy-edit sweep for typos and sentence-level roughness, especially in Chapters 1, 4, 8, and 9.
5. Revalidate with `scripts/check-citations`, `scripts/check-diagrams`, and a full `quarto render` for HTML and PDF.

No files were changed.
