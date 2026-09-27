Third pass. Delete entries as you handle them.

### Chapter 11

- **L61 (fine-grained):** your intuition is one of the two ways out, so the sentence now names both: when every rollout fails, the update needs "either a finer reward, such as the per-test pass rate the grokking recipe used as a warm-up, or a penalty on the failed answers themselves". The first is your fine-grained route; the second is what the overtraining paper used.
- **L75 (citation):** the judge-sweep sentence is itself that paper's result (the Qwen3 1.7B to 14B non-reasoning judges are Liu et al.'s sweep), so the citation has to stay unless the sentence goes too. Appendix D also cites it for judge size. Nothing else about reasoning judges remains.
- **L187:** "rejuvenating a run that has plateaued", and the rest of your sentence with the typos fixed.
- **L222 (Guru):** frontier models do well on logic and tabular benchmarks, but that is not evidence of transfer from math and code, because their RL mixes include those domains: DeepSeek-R1 trained on logic puzzles with rule-based rewards, Qwen3 and Kimi list logic and puzzle data, and none of them report a math-only ablation. So the open question is whether math and code alone would get there at scale, and no lab has published that test. The sentence stays with the scale qualifier.
- **Figure references:** removed every reference that immediately precedes its figure (Chapters 5, 7, 9, and 11, ten in all). Three stay because they carry information rather than announce a figure: Chapter 5's sentence naming which 200-step run the three GRPO figures show (yours), Chapter 6's back-reference to the pass@k figure, and Chapter 11's pointer to the Chapter 7 curve.

### Appendix D

- **L7:** now "the difference from the experiment below is that MaxRL uses a maximum-likelihood objective rather than a plain binary reward", and nothing about reliability. TTT-Discover is cut.

### Landing page and index

- **No title:** the web page now shows the Escher image first, then the abstract; the heading is hidden with `title-block-style: none`, and in the PDF the filter drops it, so the PDF opens on the image and abstract as well. The heading itself has to stay in the source, invisible, because it is what keeps the page unnumbered.
- **Changelog:** one line per date; your two September 23 lines are merged too.
- **LLM use:** "Chapters 8, 10, and 11 and Appendix D started from drafts assembled by Claude from my notes and sources and then went through many rounds of my rewriting", and the list is introduced with "Beyond those drafts, the main contributions ... were", so the three bullets follow.

### README, roadmap

- **README** is back to its state before the release commit, notice included; the contributor pointer lives only in CONTRIBUTING.md, which also keeps "one chapter per PR".
- **Roadmap:** the empty Chapter 8 section is gone.
