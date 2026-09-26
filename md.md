Understood on the naming rule, and on that composer text: it's the cloud session's auto-prompt, not a draft of yours. Updating my memory note so I don't raise it again.

The book spans 11 chapters and 4 appendices (~38K words, 45 diagrams, 175 bibliography entries). I'll read the landing page next to establish the reader, thesis, and scope before auditing the rest.

I've already spotted a few issues: chapters use a "Chapter Map" instead of the promised TL;DR, headings mix Title Case despite the sentence-case guideline, and a stray folder from another project is tracked in the repo. Now launching a seven-part audit workflow covering structure, consistency, coverage, correctness, rendering, reproducibility, and front matter, with each reviewer's findings cross-checked by a skeptic—no edits will be made to the book itself.

The whole-book audit is running in the background. Seven reviewers are each covering one area, with a skeptic checking each one's findings. When it finishes, or at the 15:22 fallback check, I'll send you a single report of the confirmed findings. I won't edit anything in the book.

The audit produced 86 findings: the skeptics confirmed 36, partly confirmed 46, and refuted 4. Reading them all so I can adjudicate before writing the report.

I've reviewed all 86 findings. Now I'll independently verify the highest-impact claims—the favicon date, the invented bibliography authors, and the Coste/Eisenstein misattribution—before reporting.

The favicon is confirmed as *Hand with Reflecting Sphere* (1935). The arXiv API returned nothing, so I'm retrying via the abstract pages.

The whole-book audit is done. I've changed nothing in the book. Fourteen agents did the work: seven reviewers each covered one area, and a separate skeptic tried to refute each reviewer's findings. I then checked the highest-stakes claims myself: the favicon's date, the bibliography author errors, and the ensemble misattribution. 86 raw findings merge into the 64 below; I dropped 4 refuted ones and a few that don't matter.

**Verdict.** Chapters 5–11 hold up well after our rounds. The rest of the book has five kinds of remaining problems:

- **Copyright exposure.** One Escher image is definitely not public domain, and two more may not be.
- **Factual errors in Chapters 1–4 and the bibliography.** Two cited papers have invented titles and authors.
- **Missing links between parts of the book.** No chapter points to Appendices A–C, the glossary describes an older version of Chapter 11, Chapter 9 references no other chapter, and the Chapter 1 roadmap is out of date.
- **Rendered-site bugs.** Pages overflow sideways on phones, and link previews show no image on every chapter page.
- **Five coverage gaps worth a paragraph or section each.**

Findings are in book order, and each is tagged high, med or low.

### Site, PDF, repository
1. **[high] The favicon is Escher's *Hand with Reflecting Sphere*, from 1935** (`_quarto.yml:15`). That contradicts the landing page's claim that all the art was "published at the latest in 1930". It stays under US copyright through 2030, and it appears on every page. Fix: use a crop of a 1930-or-earlier opener, and delete `escher/escher.jpg`.
2. **[high] The Ch 6 and Ch 11 openers may not be public domain.** "Calanques de Piana (1928)" and "Alfedena Abruzzi (1929)" aren't in Escher's catalogue of prints. They look like dated drawings with no known publication before 1931, and unpublished works stay protected in the US until 2042. Today's rescans didn't change this, since they're the same works. Fix: document a publication date, swap in catalogued 1930-or-earlier prints (for example Bonifacio 1928, Calvi 1928, Street in Scanno 1930), or narrow the claim.
3. **[med] The repo has no license at all**, though it's public, invites contributions, and publishes your review skill. Pick licenses for text and code, and list the third-party exceptions.
4. **[med] Ch 7's over-optimization figure:**
   - The PDF reproduces Gao et al.'s plot, and its arXiv license grants no reuse, unlike the CC BY figures in Ch 11.
   - It has no figure id, so it's unnumbered in both formats and can't be cross-referenced.
   - Web and PDF show different content.
   - Fix: one `#fig-ch7-overoptimization` div. For the PDF, either get permission or plot Gao's published functional form with a script.
5. **[med] 13 of 16 pages scroll sideways at phone width.** Display equations are cut off (Ch 3 eq 3.2, Appendix A, Ch 7), and tables and long URLs overflow too. Fix: three CSS rules, tested, plus splitting one inline equation in a Ch 6 footnote.
6. **[med] Link previews show no image on every chapter page, on the live site.** `og:image` resolves to `/chapters/escher/...`, which returns 404. Fix: a leading slash in `_quarto.yml` lines 16, 20 and 24.
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
18. **[med] Bibliography errors:**
    - **PPOCoder:** the entry's title doesn't exist, and 5 of 6 authors are wrong. The real paper is "Execution-based Code Generation using Deep Reinforcement Learning" by Shojaee, Jain, Tipirneni and Reddy; I checked this on arXiv.
    - **RLTF:** the authors are wrong; the real first author is Jiate Liu.
    - **Other author lists:** Nye et al. lists 5 people who aren't authors, Wei et al. is missing Ichter, and the Codex entry has "Chanez" for "Chantzis".
    - **Dead sources for Ch 1's Meta quotes:** the Fortune URL returns 404, though a working one exists. The TMTPost URL also returns 404; a live page (en.tmtpost.com/post/7436962) contains the quote but has a different title.
    - **Venues:** R1 is still listed as a preprint (it's Nature 2025), and so is Yue et al. (NeurIPS 2025).
    - **Low priority:** 31 entries are never cited, and arXiv-only papers use two entry styles.
19. **[low] Heading case.** AGENTS.md asks for sentence case. Ch 1's section headings, Appendix A, every "Chapter Map" and the landing-page headings are Title Case. Chapter titles are also mixed: ten in Title Case, Ch 10 in sentence case, and Appendix B unlike A, C and D. Decide one convention.
20. **[low] Spelling drift:**
    - "pre-training" at Ch 11:124 and 161.
    - "test time" used as a modifier, as in Ch 6's title.
    - "pass@n" at Ch 11:194, and "Pass@1" in Ch 10 and 11.

### Landing page
21. **[med] L31 is out of date:**
    - It promises a "TL;DR" per chapter, but chapters open with a chapter map.
    - The reading paths predate Chapter 8: Ch 3, 6 and 8 are in no path, and Ch 9 isn't in the builders' path.
    - Nothing points to Appendix A (RL background) or Appendix C (terms).
22. **[low] Dead links in the PDF.** The "Open PDF" link and the `.md` chapter links don't work from inside the PDF.
23. **[low] The "no EM dashes" guarantee is false in the rendered output.** Quarto titles appendices "Appendix A — …", and the Ch 4 table's `---` cells become em dashes. Fix: `crossref: appendix-delim: ":"` (tested) and "n/a" in those cells.
24. **[low] The LLM-use statement vs the git history.** It lists only planning, scaffolding and diagrams, but Ch 8, Ch 11, Appendix D and much of Ch 10 were drafted by Claude and then edited by you. Only you can word this.
25. **[low] Typos:**
    - "intelligble"
    - "can still read alone"
    - "Exclaidraw"
    - "artisitic"
    - "Github"

    The changelog also lacks Ch 10, Ch 11 and Appendix D, but that's expected until the rewrite lands.

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
35. **[med] L54: the ensemble findings belong to a different paper.** "Mitigate but do not eliminate" and "pretraining seeds generalize better" are from Eisenstein et al. (arXiv 2312.09244). Coste et al., the paper cited, found that conservative ensembles "practically eliminate" over-optimization. I checked both abstracts.
36. **[med] L200–223: the hybrid-verifier code rewards dropping the answer tags.**
    - An answer with no tag goes to the judge.
    - A tagged answer that can't be parsed gets 0.
    - Fix: `if not candidate: return None`, and adjust the sentence at L200.
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
50. **[low] `R` means both the true reward (L24) and the reasoning trace (L56).**

### Chapter 8
51. **[med] L90: "Chapter 7 described how optimizing against a monitor can teach a model to hide its intent" points to nothing.** Ch 7 never says this; it's at Ch 11:110. Four reviewers found this independently. Fix: cite the result directly, or add one sentence to Ch 7 after L76, since it's the same Baker et al. run.

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
61. **[med] L62 says the baseline is "how we bootstrap RL to improve".** That's wrong: a baseline that doesn't depend on the sampled answer leaves the expected update unchanged and only reduces variance. "Bootstrap" is also a different RL term.
62. **[low] Smaller errors in Appendix A:**
    - The "multi-turn" state (L31–41) has no tool or environment observations.
    - The weight `w_i` is defined but never used.
    - L52 claims the book uses `R_φ`, but the chapters use `r(x,y)` and `v(x,y)`.
    - L115 is garbled.

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
1. Items 1–2 (rights).
2. The factual errors: 18, 26, 32, 33, 35, 36, 61, 51.
3. The cheap site fixes: 6 and 5.
4. The links between parts: 21, 27, 64, 41, 52.
5. The coverage additions: 43, 44, 42, 30, 29, 54.
6. Everything else.

**Not checked:** Ch 5–11 correctness beyond our earlier rounds, Ch 8's incident sources, any legal determination beyond publication dates and arXiv licenses, and real phones or screen readers (mobile was emulated at 375 px).

That was the scheduled fallback check. The audit had already finished, and my previous message is the full whole-book report: 64 verified findings in book order. I haven't edited anything since.

Tell me which items you want done and I'll start with those. By default I'd go in the suggested order: the copyright items (1–2) first, then the factual errors.

Fast mode unavailable: Fast mode is not available in the Agent SDK

Research complete: the PDF agent resolved caption/heading issues, better scans exist for 10 of 12 Eschers, the Karpathy quote has 17 small discrepancies with the published transcript, only Chapter 3's bold titles warrant heading conversion, and a clearer gateway draft was found. Starting now with the in-passing commit, beginning with Chapter 2's quote.

Applying the 17 word differences to your existing Chapter 2 quote one span at a time, rather than pasting the transcript in.

The quote now matches the published transcript word for word (223 of 223). Next is Chapter 8's typo and positional reference.

The staged Chapter 8 file also carries the italic-title change, which belongs in a different commit. Splitting it out.

In-passing fixes are committed. Next is the PDF commit. First I'm checking the Chapter 5 table the PDF agent flagged: its two tables both carry the same caption, and the ✓/✗ marks print blank.

Confirmed Chapter 5's table prints twice as Table 5 and Table 6 under one caption. I'm testing a fix in a scratch copy that merges them into sub-tables (a) and (b) under a single caption.

The fix works: one Table 5 with parts (a) and (b), and the ✓/✗ marks now print. Applying it to Chapter 5 and committing all the PDF fixes together.

Committed. Next I'll check the Escher scan candidates, crop each to the printed image, convert to matching neutral gray, and compare old vs. new before replacing anything.

Castrovalva's new crop keeps a thin strip of white paper along its top edge. Trimming that, then checking file sizes before replacing the images.

Escher images are committed. Now I'll finish the Chapter 10 notes: removing "optionally" since DeepSeek uses both mechanisms, keeping "LLM judges" since K3's web-dev judging lacks a rubric, and rewriting the gateway paragraph to open with the problem it solves.

The title-italics commit message says "two author asides" but only one was restored. Correcting it before pushing.

No orphaned headings and no duplicate captions in the new PDF. Spot-checking two of the new Escher openers on the page.

Both openers look right. Pushing.

Pushed. Getting final line numbers so every report item can quote exact text.

I've pushed six commits on top of your snapshot `002c1bb`. That snapshot is your uncommitted edits, committed exactly as you left them, so these links show only my changes: [Ch 10](https://github.com/kiankyars/rlvrbook/compare/002c1bb...05b7076#diff-b29d02d04a517615e43206a9947652fe8e5020bf27e0ce173b0d2928831f7042), [Ch 11](https://github.com/kiankyars/rlvrbook/compare/002c1bb...05b7076#diff-df40f55128b53f6af0f05e7ba758892005142a9f222e36cfdecf7f75ba3f82a4), [Ch 2](https://github.com/kiankyars/rlvrbook/compare/002c1bb...05b7076#diff-417070fd5b8ff33f7862831add28705483f57af5f0b9e51478bcb5fa0052865e), [Ch 5](https://github.com/kiankyars/rlvrbook/compare/002c1bb...05b7076#diff-67c52a497a303dff89ba5c1d859d001473bd57ac5ee00d7f74a96f234a6686bd), [Ch 9](https://github.com/kiankyars/rlvrbook/compare/002c1bb...05b7076#diff-2c49ad54869e62ea1bbd56b719188d74acebc5e1dfe0499df7b0f158ec3d8a39). HTML and PDF both render, the check scripts pass, and a page-by-page scan of the PDF finds no heading left alone at the bottom of a page and no figure with two captions.

### PDF
- **Double captions.** Your guess was close, but the HTML/PDF switching works fine. The problem was inside the PDF-only blocks:
  - In Ch 4 and Ch 6, the static table had its own `: …` caption line inside a figure that already had a caption, so the PDF printed both. I deleted those two table-caption lines.
  - Ch 6 loses one PDF-only sentence that the web version never showed: "Both models improve with more candidates, but the RLVR-trained model starts higher at pass@1 and needs less help from additional search."
  - Ch 5 had the same bug in another form: one caption printed twice, as Tables 5 and 6. The two tables are now parts (a) and (b) of one Table 5, and the ✓/✗ marks, which printed blank, now show.
- **Orphaned heading.** Yes, there's a general rule, and LaTeX already keeps headings with the text or list after them. Tables were the only exception. I added one line to the PDF settings: if a table directly follows a heading and fewer than 8 lines remain on the page, the heading moves to the next page with it. No individual heading is formatted.
- **Escher scans.**
  - Ten openers are replaced with the same works from Boston Public Library, Escher in Het Paleis, and WikiArt. Each is cropped to the printed image and kept gray. They now print at about 125–390 ppi, up from 57–94.
  - Tower of Babel was already fine. Dolphins had no better scan, so I only trimmed its frame.
  - The scan edge lines and the "TWON" marks (not Escher's) are gone, except on Dolphins, where "TWON" sits inside the image.
  - **Rights caveat:** Calanques de Piana and Alfedena Abruzzi aren't on the official list of Escher's prints and may be drawings. A drawing never published before 1931 would still be under US copyright until 2042. Both images were already in the book; worth checking before V1.

### Found in passing (one commit)
- **Ch 2 L126:** the Karpathy quote now matches the published transcript word for word. It differed in 17 places, for example "It's crazy." became "It's just stupid and crazy.", and it's split into the transcript's three paragraphs.
- **Ch 8 L58:** "seeming to explain the last paragrpah's closing sentence" → "seeming to explain why Hacker-Opus scored almost exactly like its starting checkpoint on the broad alignment audit."
- **Ch 9 L171:** "DeepSeek audits each synthesized task…" → "each synthesized *coding* task… that looks for flaws, including ways to hack it." The report describes that inspection agent only for coding environments.
- **Ch 9 L172–174:** each technique now has a one-clause explanation:
  - The per-token regularizer is "a penalty on each token that keeps the updated policy close to the one that sampled it."
  - The quantization scheme is "the low-precision format it is served in (4-bit expert weights, 8-bit activations)."
  - "Too stale" means "sampled from a checkpoint too far behind the current one," and keeping the KV cache means "an interrupted rollout resumes where it stopped."
- **Ch 9 L165:** DeepSeek's "Length control" cell said "Early short samples discarded", but that fixes batching, not length. It now says "Length penalty that shrinks with requested effort."

### Chapter 10
- **L34:** "and optionally (your note) discarding" → "and discarding". DeepSeek lists both as "two mechanisms" it employs. The report never shows a separate hero-run setting.
- **L56, L60:** the two "Vision in…" titles are now `###` headings, and both of your notes are removed. For the other chapters, I converted only Chapter 3's three limitations. The short run-in titles in Ch 4, 6 and 9 would become one-sentence sections or break a list after a colon, so they stay bold.
- **L62:** your note asked for "rubric judges" if there's a rubric; there isn't. K3's web-dev reward uses "an internal reward model", and its rubric protocol is only for non-verifiable general tasks. So "LLM judges" stays.
- **L85:** since you still didn't get the gateway, I rewrote the paragraph to start from the problem:
  - The model runs inside an agent program (like Claude Code) that rewrites the prompt between calls.
  - To train, you need the exact prompt and response of every call, and each agent rewrites prompts its own way.
  - The gateway is a logging proxy: the agent calls it like any model API, and it forwards each call to the model being trained and saves the exact prompt and response.
  - L89: "how much of this" → "how much of this rewriting".
- **L97, your question:** you originally wrote "DeepSWE trained on 4,500 human-made environments" to show that hand-built environments are costly. In fact R2E-Gym built them semi-automatically from GitHub commits, so the example now shows automation already happening. It no longer illustrates the cost of building environments by hand. The sentence still reads fine; I'm only pointing out that its role changed.
- **L119:** "As is standard in reinforcement learning environment creation, for general agents DeepSeek builds mocked tools that reproduce, at train time, …" is back.
- **L119, your question:** your original was "Anchoring task generation in real workflows and real failures is one way how the process avoids model collapse." I had hedged "avoids" to "may guard against", because DeepSeek never mentions model collapse. It's your inference, not their claim. Your new "is one clever way to guard against" reads as your view, which is fine.

### Chapter 11
- **"Research question." labels:** I kept them bold. A heading has to head something, and in those sections the question is itself the content, with the section's subheadings below it. The two-question section is different because each question heads its own body.
- **L26:** your note is removed, and the sentence again reads "*The Invisible Leash: Why RLVR May or May Not Escape Its Origin* argues that…". The book-wide rule is now that a work named by its title is italicized, so Ch 1 L41 and Ch 8 L54 name their works by italic title too.
- **L152:** "(really worth reading this paper)" is back. The "(this is relatively speaking…)" aside at L75 stays as written.

Here's the rest of Chapter 11, with quotes this time:
- **L32:** "…which is the reallocation Yue et al. measured" → "…which is **part of** the reallocation…". In this section, elicitation and reallocation are the same side; the other side is creation. So yes, plain RLVR looks like reallocation. But that evidence is Yue's pass@k, not Cui's entropy law, so it's "part of."
- **L54:** you removed "The gains were largest where the base model was weakest." I didn't restore it. I only think it isn't self-evident: RL learns only from successes, so you'd expect it to help *least* where the base model is weakest.
- **L56:** "On code problem families" → "On a code problem family" (the paper shows one). "a dense-reward warm-up" → "a warm-up that first rewards the fraction of test cases passed before switching to the binary reward". "experience replay was needed to shorten" → "experience replay shortened".
- **L57:** your "converging or diverging?" note is replaced by: RL "trails its base model slightly at k = 1 but leads at k = 64, solving 81 of 100 … against 77 …, while SFT … ends at 73". The gap widens with k.
- **L61:** an HTML comment tags "A reconciliation" as pending; the README lists it too.
- **L63:** "the large-k (your note) decline" → "the large-k decline **Yue et al. measured**". "narrowes" → "narrows".
- **L67:** "…failed(your note): … collapsed for lack of any positive signal" → "…failed for a mechanical reason: … stalled, because GRPO has no gradient on groups in which every rollout fails. That rules out plain GRPO on such problems, not outcome-only RL in general."
- **L73:** "rubric aggregates or generative verifiers … have no principled stopping criterion" → "LLM judges, including the rubric judges of Section 11.6, so practitioners optimizing against them find the peak by monitoring a stronger held-out judge or benchmark rather than predicting it in advance".
- **L75:**
  - "the share of newly credited criteria…" now spells out the metric: of the criteria the training judge newly marks as met at each checkpoint, the share all three panel judges reject. The strong verifier "fluctuated between 15% and 21%, staying within 5 points of its starting value". That's a band, not a trend.
  - "larger (your note) judges" → "non-reasoning judges fine-tuned from Qwen3 models of 1.7B, 4B, 8B, and 14B parameters, larger judges…".
  - Removed "What no study has fitted is the functional form…", since it's idea 2 in Appendix D.
- **L81:** ", ," and "Purposefully" fixed.
- **L97:** your "two partial answers to the question of verifier coverage" is kept. My opinion: "coverage" is jargon here.
- **L99–100:** items capitalized with periods. Item 2, "verifier-free diagnostics…", now says what it does: it "flags when the policy stops improving even though the training reward keeps rising."
- **L102:**
  - "scored 1,000 sampled training queries (your note)" → "trained Qwen2.5-7B Base with GRPO on the DeepScaleR problem set and, at each checkpoint, had GPT-4o, which never supplied training reward, grade responses to 1,000 of those same training problems…" What's held out is the grader, not the problems.
  - "unkown" → "unknown". Your "No published results yet extend this…" stays.
- **L110:** "but do not grade" → "but does not grade".
- **L112:**
  - "Astra controlled its reasoning as instructed" → a test "that instructs a model to reshape its chain of thought, for example to avoid certain keywords or to write only in lowercase". Then OpenAI's words: "an undesirable property for monitorability". Your reading was right.
  - Pachocki's list is numbered, with "many" (not "some") interactions and "reasoning about and manipulating" their own reasoning. Your "in his blog post" is kept.
- **L118:** "studying" → "study", "monotibility" → "monitorability". Your wording is otherwise untouched.
- **L124:** "the least understood … compute.; emiAnalysis says" → "The least understood … compute. SemiAnalysis says".
- **L126:** new sentence defining pass rate: "the fraction of 16 samples per prompt that the checker marks correct, averaged over the prompts". The book never defined it before.
- **L134:** "Most recipe choices turn out to answer the second question (your note)" → "In ScaleRL's ablations, most recipe choices changed how fast a run rises, not how high it goes:". The basis: reverting any one of eight choices from the final recipe left the fitted ceiling within noise.
- **L148:** the figure is redrawn with a legend. The old caption, "look alike early… diverge only at scale", was false for the old curves. It now reads "A recipe that reaches the same ceiling sooner leads early in training, while a recipe with a higher ceiling A can trail early and pull ahead only at scale."
- **L152, the scarce regime:**
  - "A second regularity (your note)" → "A second pattern".
  - "…data-constrained regime on the 7B model, with fewer distinct problems than the run needs": Tan et al.'s term, which I had deleted. So yes, every problem is repeated, and the finding is that up to 25 repeats hardly matter.
  - "(And even when the student strictly fails! …)" → "and is still useful on a prompt the student never solves".
- **L156:** "Does the base model's support establish the asymptotic perfoamcne… (your note)" → "How much of the asymptotic performance is set by the base model's support…, and how much by inefficiencies in training recipes?" Both matter.
- **L158:** your note is removed; this question isn't asked anywhere else in the book.
- **L159:** "Does prolonged RL erode the plasticity it relies on (your note)?" gains a definition, "the network's ability to keep learning from new data", and "This is not the entropy collapse of Section 11.3…".
- **L161:** "about 20% for DeepSeek-R1" → "about 5.5% for the whole DeepSeek-R1 pipeline, SFT included". DeepSeek's own numbers replaced an outside estimate.
- **L165:** "increasining" → "increasing".
- **L167:**
  - Added "Karpathy's phrase for this, quoted in Chapter 2, is 'sucking supervision through a straw'…".
  - "The same survey claims that…" became a sentence of its own, keeping your "while possible in math".
  - "Mythos is Anpril" → "an early version of Claude Mythos Preview, evaluated in March 2026".
  - Deleted the pasted Opus text and "At the frontier, Kimi K3 trains on rollouts…".
- **L169:** only "ewith", "important" and "trajetoreis" are fixed; your "very large qualifier" wording is kept.
- **L171:** "What is open: whether…" → a `### What is open` heading, matching L65.
- **L179:**
  - "Rubric" is defined only here, so the first sentence stays.
  - Cut "; in medicine and science, the second version worked best, and both beat a judge with no rubric".
  - Kimi is shortened to "Kimi K3's judge writes a rubric for each task, as Table 9.2 shows".
  - The DeepSeek-V4 sentence is removed. It wasn't a repeat of L204, though: V4's rubric reward model and V4.1-Flash's task synthesis are different reports.
- **L180:** removed "No frontier report documents this reward yet; it remains a research method."
- **L186:**
  - "math-only RL preserved general capabilities while math-only SFT eroded them" → "carried its gains over to other reasoning and even non-reasoning tasks, while math-only SFT gained less on other reasoning and fell below the base model on non-reasoning tasks".
  - RL's Razor now sits right after that result.
  - "…is open. (your note)" → "So RL on verifiable reasoning does transfer, but mainly between domains the base model already knows well; domains like logic, simulation, and tabular reasoning can still be improved directly, as Wei's rule predicts, once they have verifiers of their own."
- **L192:** the Qwen2.5 examples are replaced by Llama results (TTRL: MATH-500 48.6% → 63.7%; self-certainty close to GRPO), and "minimizing entropy alone matched…" is dropped. Your take on it was broadly right.
- **L194:** your sentence "this answer is refreshing because it's a training problem which we can directly answer with complete certainty…" is restored verbatim, typos fixed. "Much of the early success is also specific to Qwen2.5 models…" is gone, per your proposal.
- **L196:** removed "a version of that gap grows with pretraining compute". Added your conclusion in your words, "as you optimize against those judgments, the model's answers will become as good as its judgments, and then there is no longer any leverage", plus Song's finding that the gap reached about zero after two or three rounds.
- **L202:**
  - Your analogy is in text: "There needs to be some external input, such that the model does not collapse; think of it as analogous to the real workflows that DeepSeek brought into its environment creation pipeline." SPADE's own evidence follows: the same maze 41 times without its corpus.
  - Your example: "The most contrived examples would be large multiplication or problems which involve a random number generator…".
  - SGS's guide is explained as "a frozen copy of the initial model".
  - Deleted the "MiniMax reports that M2.7 now handles 30% to 50%…" sentence (a one-off).
- **L206:** "…Anthropic's is called X" → "…is open, although frontier labs run closed systems for this: Anthropic runs an automated review of all environments…, yet by spring 2026 it was producing RL environments 'faster than our systems could vet them'…". Anthropic gives the system no name.
- **L214:** "Semantic faithfulness" row → "What the verifier misses".

### Appendix D
- **L9:**
  - "a cold start (your note)" → "a warm-up, in which RL first rewards the fraction of test cases passed…". It isn't R1-style; that explanation now lives in Ch 11 L56.
  - "'solved' there means at least one success (your note)" → "solved three AIME 2025 problems at pass@4096…, though … only 15 of its 12,288 samples on those three were correct".
  - "Test-time (your note)" → "TTT-Discover, which keeps updating the model's weights with RL…, is the closest test of whether RL finds what sampling from the frozen model does not".
- **L11:** your 80/20 note is removed. At pass@4096 = 0 every rollout fails and GRPO learns nothing, so there's nothing to overfit. The experiment now uses GRPO as the control against a loss that learns from all-fail groups.
- **L17:** "only partially?" Yes: all three studies track the gap over training steps; none fits a law against KL the way Gao et al. did. That's the experiment itself.
- **L19:** "the stopping criterion Chapter 11 says they lack" → "predict when to stop, instead of finding out by monitoring a held-out judge".
- **L25, L33, L41, L49:** "Closest work" now points to the Chapter 11 section and keeps only works Chapter 11 doesn't cover. Closers removed: "No study varies the horizon.", "but no study tracks it…", "What is missing is attribution…".
- **L35:** "entropy-minimization rewards on clean, procedurally generated problems" → "majority-vote and self-certainty rewards on procedurally generated problems the models cannot have memorized".

Still open from before: should I remove the naming rule from `scripts/check-diagrams`, as in your unsent draft in the cloud session? If so, I'll also update the line in AGENTS.md that says the check verifies naming.

That scheduled check had nothing left to do. Everything from that round is on `origin/main` at `05b7076` and the working tree is clean; my previous message is the full report.

One decision is still yours: should I remove the diagram-naming rule from `scripts/check-diagrams`, as in your unsent cloud-session draft? If yes, I'll also update the line in AGENTS.md that says the check verifies naming.