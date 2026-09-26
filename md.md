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