**Verdict.** Chapters 5–11 hold up well after our rounds. The rest of the book has five kinds of remaining problems:
- **Factual errors in Chapters 1–4 and the bibliography.** Two cited papers have invented titles and authors.
- **Missing links between parts of the book.** No chapter points to Appendices A–C, the glossary describes an older version of Chapter 11, Chapter 9 references no other chapter, and the Chapter 1 roadmap is out of date.
- **Rendered-site bugs.** Pages overflow sideways on phones, and link previews show no image on every chapter page.
- **Five coverage gaps worth a paragraph or section each.**

Findings are in book order, and each is tagged high, med or low.

### Site, PDF, repository

4. **[med] Ch 7's over-optimization figure** (September 26: it has the id `fig-ch7-overoptimization`, Ch 11 references it, and the PDF plots Gao et al.'s functional form from `code/figures/07-overoptimization-curve.py`; the author's own version of the figure is still to come):
   - The PDF reproduces Gao et al.'s plot, and its arXiv license grants no reuse, unlike the CC BY figures in Ch 11.
   - It has no figure id, so it's unnumbered in both formats and can't be cross-referenced.
   - Web and PDF show different content.
   - Fix: one `#fig-ch7-overoptimization` div. For the PDF, either get permission or plot Gao's published functional form with a script.
   For this one, I'm not sure if the precedent here is to exclusively cite everything. If we don't ever refer to the figure, then we don't need to give it a figure ID, but if we do, then let us do that. I have the impression that we did cite it in certain places, and if that's the case, then we must have somehow used a figure ID. I'm kind of confused: what's going on here?
   And then, for the PDF, let us either plot the Gauss published functional form with the script or adapt the web version somehow for the PDF.
Also, figure 2 in the paper is extremely informative, so I have added my own generated version of it, please substitute my versions for the PDF as well as the web version.

5. **[med] 13 of 16 pages scroll sideways at phone width.** Display equations are cut off (Ch 3 eq 3.2, Appendix A, Ch 7), and tables and long URLs overflow too. Fix: three CSS rules, tested, plus splitting one inline equation in a Ch 6 footnote.
7. **[med] Dark-mode contrast.** Ch 7's Goodhart widget axes and ticks are at 1.6:1 contrast, and Ch 2 and Ch 4 widget labels at about 2.2:1. Fix: dark overrides in `custom.css`.
8. **[med] The PDF bibliography has no heading and no table-of-contents or bookmark entry.** It runs straight on from D.6. Fix: a References page with `{#refs}`.
9. **[low] PDF and web number figures differently.** The PDF counts through the whole book ("Figure 8") while the web numbers per chapter ("Figure 5.2"). Fix: `\counterwithin`, tested.
10. **[low] Two PDF table-of-contents glitches:**
    - The entry reads "11.10The agenda at a glance", with no space.
    - The "Start Here" entry jumps to the title page.
    - Both fixes are tested.
11. **[low] Two PDF code lines overflow.** The Ch 5 `target_modules` line is cut off at the page edge, and a Ch 2 line runs into the margin. Fix: split the two source lines.
12. **[low] Neither the PDF nor the site shows an edition date.** Fix: `date: last-modified`.
13. **[low] The Tower of Babel opener is 4.9 MB, about 35% of the PDF.** I left it unchanged today. Downscale it to 1,600 px in gray, like the others.
14. **[low] Diagrams with real content have no alt text** describing what they show.
15. **[med] Most figures can't be regenerated.**
    - Only the ScaleRL figure has a generator script.
    - Six Matplotlib pairs whose numbers the prose quotes have none: the Ch 5 entropy band, Ch 7 accepted-pool precision, three in Ch 9, and Ch 11 entropy.
    - The Ch 5 total-reward chart is hand-written SVG, and the Ch 1 and Ch 2 Excalidraw sources are missing.
    - The Ch 5 run has no logged data committed, and its format-share plot hides the negative values at the start.
16. **[low] CI doesn't pin Quarto.** It installs 1.10.18 while you have 1.9.36 locally, and the PDF filter relies on a Quarto internal. Pin the version.
17. **[low] Repo tidiness:**
    - `book/siboehm-cuda-mmm/` holds 9.4 MB of unused third-party images.
    - README lists no prerequisites: TinyTeX with koma-script, rsvg-convert, ripgrep, uv.
    - AGENTS.md's layout rules are out of date.
19. **[low] Heading case.** AGENTS.md asks for sentence case. Ch 1's section headings, Appendix A, every "Chapter Map" and the landing-page headings are Title Case. Chapter titles are also mixed: ten in Title Case, Ch 10 in sentence case, and Appendix B unlike A, C and D. Decide one convention.
20. **[low] Spelling drift:** "test time" used as a modifier, as in Ch 6's title (the rest was normalized on September 26).

### Landing page

21. **[med] L31 is out of date:**
    - The reading paths predate Chapter 8: Ch 3, 6 and 8 are in no path, and Ch 9 isn't in the builders' path.
    - Nothing points to Appendix A (RL background) or Appendix C (terms).
22. **[low] Dead links in the PDF.** The "Open PDF" link and the `.md` chapter links don't work from inside the PDF.
24. **[low] The LLM-use statement vs the git history.** It lists only planning, scaffolding and diagrams, but Ch 8, Ch 11, Appendix D and much of Ch 10 were drafted by Claude and then edited by you. Only you can word this.
### Chapter 1

26. **[med] L39: DeepSeekMath is called the "first paper to apply critic-free RL to mathematical reasoning at LLM scale".** Uesato et al. (2022) already ran final-answer RL on a 70B model, and ReST-EM followed in 2023. DeepSeekMath's own GRPO run also used a learned reward model, not a verifier. Fix: drop "first".
27. **[med] L233's roadmap is stale:**
    - "Chapter 10 compares the paradigm across its strongest and most difficult domains" no longer describes Chapter 10.
    - The appendices go unmentioned.
    - The book's thesis (the verifier and environment matter more than the optimizer) is first called "this book's thesis" at Ch 9:185 and never stated in Ch 1 or the abstract.
28. **[low] The domain map promises checks the book never delivers.** It promises citation and evidence checks for long context, and "shortcut cues" and OCR noise for multimodal, but no later chapter returns to them.
29. **[med] Coverage: instruction following.** It's one of RLVR's founding domains (Tulu 3 used GSM8K, MATH and IFEval) and 29% of Ch 9's prompts, but it's missing from Ch 2's domain table. IFBench shows the failure: once the constraints are removed, a judge scores the RL-trained outputs 6.4 against 7.0 for the base model. It also shows the fix: a reward model applied only after the constraint check passes.

### Chapter 2

30. **[med] L118, L328 and the footnote: "final acceptance is strong" for proofs overstates it.**
    - The Lean harness itself has loopholes. `sorry` counts as an axiom, axioms can be injected, and `native_decide` extends trust to the compiler.
    - A Lean bug before 4.20 let at least three DeepSeek-Prover-V2 proofs pass without normal kernel checking (ICML 2026 audit).
    - Formal statements often don't match the problem: in miniF2F the two disagree on more than half the problems.
    - Suggested homes: a qualifier here, a proof-harness exploit case in Ch 7, and DeepSeekMath-V2's learned proof verifier in Ch 4.
31. **[low] L122 is the first use of GRPO and "advantage", with no pointer to Appendix A.**

### Chapter 3

32. **[med] L57–75: Math-Shepherd's labelling is misdescribed.**
    - It uses a separate completer model (LLemma-7B, 8 rollouts per step).
    - Its PRM trains on hard labels: a step is good if any rollout succeeds, not "most".
    - The code also uses `K` for rollouts, while K means steps at L39.
33. **[med] L115: the Uesato summary leaves out the result that matters most for RLVR.** RL directly on final-answer correctness, from a few-shot start, left much higher trace error: 19.8% (12.4% with reranking) against about 3.5–3.8% for process supervision. The 3.4%/3.8% the book quotes both include reranking.
34. **[med] "ORM vs PRM" never reconciles with Ch 6 or with R1.**
    - Ch 6 reports Lightman's result that PRMs beat ORMs as rerankers.
    - DeepSeek-R1 lists PRMs among its unsuccessful attempts: they caused reward hacking and cost too much in RL.
    - That "rerank yes, train no" split is the missing bridge to why Ch 9's recipes use outcome rewards only.

### Chapter 4

37. **[med] L50: "today's models likely do not suffer such biases to the same extent" is undercut by the paper cited next.** Yang (2026) finds capability often uncorrelated, or even negatively correlated, with low self-preference bias. Scope the hedge.
38. **[low] L58: RewardBench is credited with calibration results it never measured.** It measures pairwise accuracy.
39. **[low] L39: the odd-number-of-judges result is cited to a paper that doesn't contain it.** It's also majority-vote arithmetic: with random tie-breaking, 2k judges are no more accurate than 2k−1.
40. **[low] L176 and L258–260 promise that Ch 5 shows how step-level scores become credit.** Ch 5 is outcome-only. Point these at Appendix A's token weights and Ch 11's credit section instead.

### Chapter 5

41. **[med] The GRPO objective is never written out anywhere.** Ch 3, Ch 7 and Ch 9 all modify or allude to its terms (ratio, clip, per-sample weight, KL, std normalization). The L409 heading "Group normalization versus KL penalty" also misnames two things that are independent. Fix: write DeepSeekMath's Eq. 3 once in Appendix A, rename the heading, and link to it from Ch 7:270 and Ch 9:31.
42. **[med] Coverage: binary reward trains guessing.** At L218–220 binary reward is presented as sufficient, but under 1/0 scoring "I don't know" earns the same as a wrong answer, so RLVR trains abstention away (RLCR; Kalai et al. 2025). One paragraph and a two-line derivation would cover it, and it connects to Ch 8's lesson on rewarding "this task is impossible".

### Chapter 6

43. **[med] Coverage: what outcome RLVR does to outputs.** The book never covers longer chains of thought, or self-verification and backtracking (R1's length curve; these behaviors already exist in base models, per Liu et al. and Gandhi et al.).
    - Ch 6 treats test-time compute only as parallel sampling, although its map promises to separate test-time from train-time compute.
    - Ch 9 then shows 10K-token rollouts, and Ch 9 and Ch 11 discuss length control as if it had been introduced.
    - Suggested home: a short section before "Amortization".
44. **[med] Coverage: "Reporting results" has no controls.** It should ask for:
    - format-only and random-reward baselines
    - a second model family
    - a contamination check
    - several seeds

    Related: Ch 11:152 still cites the Qwen2.5-Math one-shot jump from 36.0% to 73.6%, but a format-only reward alone reaches 65.0% (the paper's own "8.6 points beyond format correction"). That cuts against your a78fd8b note about Qwen examples.

45. **[low] L287** calls Yue et al. "contested" without linking Ch 11's elicitation section.
46. **[low] Optional coverage: search where the verifier's score is the objective.** AlphaEvolve's 48-multiplication result, and its hazard: Sakana's CUDA engineer bypassed the correctness check.

### Chapter 7

47. **[med] "Reward hacking" is never defined, and the taxonomy lacks tampering with the environment or grader.** The chapter's own examples (`exit(0)`, SkipTest, a patched verifier, shadowing pandas) and all of Ch 8's cases belong to that missing class.
48. **[med] L88 says "The same dynamics hold" for programmatic verifiers, with no evidence.** Hedge it.
49. **[med] L52–70 ("Mechanism gaps") uses the do-operator with no explanation and no example.** A Turpin or Lanham example would fix it; you'd want to write those sentences yourself.
### Chapter 8

### Chapter 9

52. **[med] Ch 9 references no other chapter, though it depends on several:**
    - Zero-gradient filtering is Ch 5's DAPO mechanism.
    - The 62.5% cutoff isn't related to Ch 5's 20–80% band.
    - Dropping std normalization is the payoff of Ch 5's small-gap example.
    - "No KL loss" sits unreconciled with Ch 7's hardening advice. OLMo gives the reason: removing KL didn't cause over-optimization in their mixed-domain setting.
53. **[low] L71, L125 and L164 present truncated importance sampling as part of OLMo 3 Think's recipe.** The 7B run the chapter walks through didn't use it; the 32B run did, with a cap of 2.0.

### Chapter 10 (for the rewrite)

54. **[med] L32 "keeps the verifier unchanged" is incomplete.** An outcome-only reward starves evidence selection: LongRLVR adds a grounding reward and gains 73.17 → 88.90. The citation is already in your bibliography, and adding it would deliver Ch 1's domain-map promise.
55. **[low] "Harness" means two things.** It's the reward-bearing interface at L14 and in Appendix C, but a product like Claude Code at L7 and L81; L85 calls the same thing "an agent, also called a scaffold". Add an "agent scaffold" entry to Appendix C.
56. **[low] The harness-diversity argument is split** between the Kimi paragraph and the one-paragraph DeepSeek section. Optionally add a paragraph on search agents: Search-R1 masks retrieved tokens out of the loss.

### Chapter 11

57. **[med] The L8 map line contradicts the chapter.** "RLVR improves a model exactly as far as verification reaches" doesn't match L186's conclusion that transfer happens, nor Ch 6:285. Suggested: "most directly where verification reaches; transfer beyond it is partial."
58. **[low] The RL compute section (group 1) sits after reward hacking (group 2).** Move it to follow elicitation.
59. **[low] Missing links back:**
    - The credit-assignment section never cites Ch 3's PRMs.
    - L67 never cites Ch 5's all-fail groups.
    - L73 names "Chapter 7's over-optimization curve" in prose; it can become a figure reference once item 4 is done.
60. **[low] Coverage: DeepSeekMath-V2.** It scales verification compute "to maintain the generation-verification gap", which is direct frontier evidence for the gap argument at L196.

### Appendix A

62. **[low] Appendix A:** the "multi-turn" state (L31–41) has no tool or environment observations (the other three points were fixed on September 26).

### Appendix B

63. **[low] Rows 14 and 16 are stale since July's Ch 11 rebuild.** Versioning (row 14) and "tax regressions" (row 16) point to chapters with no such content. Row 15 should point to Ch 6 only.

### Appendix C

64. **[med] The glossary is from the pre-July Chapter 11:**
    - About 12 terms are used nowhere (training, evaluation and audit verifier, the budgets, regression tax, and others).
    - The book's actual vocabulary is missing: rollout (98 uses), GRPO (57), advantage and entropy (38 each), PRM, pass@k, KL, reward hacking, Goodhart's law, competence band.
    - The entry is "pass@N" while Ch 6 defines pass@k.
    - PPO, DPO, KL, MCTS, RLHF and ORM are never spelled out.
    - No chapter links here.

**Checked and dropped:**

- Part groupings: a one-chapter Foundations part is a normal choice.
- Rewriting the chapter maps: they're house style.
- Varied chapter endings: you removed Ch 7's bridge and Ch 11's conclusion on purpose.
- Escher caption word order ("Corte, Corsica"): optional polish.
- Exercises: not needed for a reference book.

**Suggested order:**

2. The factual errors: 26, 32, 33.
3. The cheap site fixes: 5.
4. The links between parts: 21, 27, 64, 41, 52.
5. The coverage additions: 43, 44, 42, 30, 29, 54.
6. Everything else.

**Not checked:** Ch 5–11 correctness beyond our earlier rounds, Ch 8's incident sources, any legal determination beyond publication dates and arXiv licenses, and real phones or screen readers (mobile was emulated at 375 px).

### Author's items (moved from the README)

- Add image-gen diagrams to the textbook where there is a clear clarity gain.
- Chapter 11, "A reconciliation" paragraph (elicitation section): rewritten and retitled in the September 26 round; the author's sign-off is pending.
