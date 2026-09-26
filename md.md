Round of September 26, second pass. Line numbers are the current ones. Delete entries as you handle them; this file goes away at the end of the review.

### Chapter 10

- **L85 to L103:** your gateway figure is in as `fig-ch10-gateway`, split into light and dark PNGs, referenced from the gateway sentence.
- **L105:** your sentence on the black-box interface enabling training across many harnesses closes the black-box paragraph. Move or cut it if you meant it elsewhere.

### Chapter 11

- **L56:** the dense-reward version of the sentence is in the grokking bullet: "with that dense reward, the gains were largest exactly where the base model was weakest".
- **L57 to L59:** the SFT detail is a footnote.
- **L61:** noted on "fine-grained"; the text stays as it is, since it now says what the update needs.
- **L75:** you cut the reasoning-judge sentence, which carried the only citation for the judge sweep; the citation is back on the sweep sentence.
- **L112 and L124 (Anthropic on monitorability):** yes. The Claude Opus 4.8 system card (May 28, 2026, section 6.6.3) reports a white-box probe finding grader-oriented reasoning in the activations, unprompted and never verbalized, in around 5% of sampled RL episodes, and offers it "as an indication that chain-of-thought alone may not be sufficient to allow robust monitoring of frontier models for grader awareness". Later cards dropped the hint-based faithfulness metric for behavioral audits. It is now a footnote after the Astra sentence, with a bibliography entry.
- **L154:** the caption you asked about (it was L128 in the file you annotated; it moved when the SemiAnalysis figure went in above it).
- **L158 to L160:** the eight reverted choices are a footnote; the generation-length result is now only in the ceiling list, with "at the cost of slower early progress", and the takeaway sentence ends at the figure reference.
- **L187:** ProRL's citation is on its own sentence; the DeepSeek connection is stated: both are ways of restarting a run that has stopped improving, which is what one would do if plasticity were being lost, but neither measures it.
- **L215:** your rubric sentence is restored with only "possibilities" and "criterion" fixed.
- **L222 (Guru):** no controlled evidence at larger scale either way. Guru tested 7B and 32B; the frontier reasoning models that do well on logic puzzles have unknown training mixes, so they settle nothing. The sentence now says "tested at 7B and 32B" and "whether larger models close that gap on their own is untested", which keeps the evidence without overclaiming.
- **L228:** the INTUITOR example is gone and the next sentence reads "Given this result".
- **L236:** pseudo-labels are defined in a footnote.
- **L248:** your freeze remark is a footnote in your words.

### Appendix D

- **L7 (MaxRL):** agreed that one solved sample answers the existence question. The sentence now says the result is "the closest existing answer to the question", notes that MaxRL uses a maximum-likelihood objective rather than a plain binary reward, and drops the reliability framing. The experiment still scores pass@1 and pass@4096 separately, which is where the reliable-versus-rare distinction belongs.
- **L7 (TTT-Discover):** "reusing earlier solutions" is spelled out: its search starts each new attempt from the best solutions found so far instead of from scratch, and the ablation shows that search, not the weight updates, accounts for most of the gap over best-of-N.
- **Line numbers:** the ones in the last file referred to the appendix before the reformat, which is why they no longer matched. Everything else you listed there is in the text as described; nothing further to do.

### Your other requests

- **AGENTS.md:** cut back to four added lines (italic titles, no em dashes, asides in footnotes, third-party figures only by license or permission), and the layout line now names `scripts/`. The review-workflow section and the rest are gone.
- **Code and scripts:** `code/figures/` moved to `scripts/figures/`; `code/` no longer exists. Docstrings, LICENSE, and AGENTS updated.
- **Gao figure:** your generated Figure 2 diagram was already placed last round as `fig-ch7-gold-proxy-setup`; the roadmap item is removed.
- **PDF (you allowed a TeX install):** TinyTeX is installed through Quarto and the PDF renders. Fixed while I was there: the bibliography now has a References heading and a table-of-contents entry, figures and tables are numbered per chapter as on the web, the two-digit subsection numbers no longer collide with their titles in the table of contents, and the two code lines that ran off the page are split. One thing to know: deleting the "Start Here" heading from the landing page made Quarto number the landing page as chapter 1, so every chapter shifted by one in both formats (Chapter 11 became 12, its figures 12.x, and the sidebar entry went blank). The heading is back, unnumbered; your removal of the two links under it stands, since the sidebar already has the PDF download and the repository link.
- **Index, LLM-use paragraph:** "that I dictated" restores the grammar of your sentence. The bullet list after it still says the main contributions were structure, scaffold, and diagrams, which now sits oddly next to "Claude drafted Chapters 8, 10, and 11"; a fourth bullet or a cut is yours to make.

### V1

- **Ready, in my view, once you push:** the notice about rewriting Chapters 10 and 11 is gone from the README, the changelog covers the September 24 to 26 work, the roadmap is rewritten as a contributor task list with a pointer from the README and CONTRIBUTING, the license is in, the PDF builds, and both formats render without unresolved references.
- **Still yours before tagging:** the LLM-use bullets above; the license commit, if you want a different choice; and whether "Start Here" is the landing-page title you want.
- **Not blocking, left in the roadmap:** everything else, including the mobile overflow (item 5), dark-mode contrast (7), figure regeneration scripts (15), the Chapter 1 to 4 factual items, the coverage gaps, and the glossary.

### Commits in this pass

1. Address the second-pass review notes in Chapters 10 and 11 and Appendix D.
2. Consolidate scripts and trim AGENTS.md.
3. Prepare the v1 release: changelog, roadmap for contributors, References page, PDF fixes.
