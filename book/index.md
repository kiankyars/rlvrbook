---
title: "Start Here"
number-sections: false
---

[<i class="bi bi-file-earmark-pdf"></i> Open PDF](rlvrbook.pdf)  
[<i class="bi bi-github"></i> GitHub](https://github.com/kiankyars/rlvrbook)

Reinforcement learning from verifiable rewards studies how models can improve by learning from reward signals derived from checkable task outcomes, executable feedback, formal validation, or other reliable forms of verification. This book is a reference on that paradigm. It is not organized around optimizer fashions or a timeline of papers. Its purpose is to explain what kinds of rewards can be made verifiable, what those rewards actually train, where the paradigm has been most successful, and where it breaks.

## New to RLVR

Read [Chapter 1](chapters/01-introduction.md), [Chapter 2](chapters/02-outcome-rewards.md), and [Chapter 7](chapters/07-reward-hacking-proxy-misspecification-and-verifier-robustness.md).

## Building Systems

Read [Chapter 4](chapters/04-learned-programmatic-and-hybrid-verifiers.md), [Chapter 5](chapters/05-turning-checks-into-training-signal.md), [Chapter 7](chapters/07-reward-hacking-proxy-misspecification-and-verifier-robustness.md), and [Chapter 9](chapters/09-canonical-domains-math-code-and-formal-proof.md).

## Frontier Research

Read [Chapter 8](chapters/08-faithfulness-confidence-and-what-verification-misses.md), [Chapter 10](chapters/10-long-context-multimodal-and-agentic-rlvr.md), and [Chapter 11](chapters/11-open-problems-and-the-research-agenda.md).

## Flagship Figure

The RLVR pipeline can be read as a stack from objective definition to policy/search updates.
Placeholder for the RLVR Verifier Stack figure.

## LLM Use

Fortunately, we live in a world where AI slop writing is still *very* intelligible from genuine human text. It is knowing this fact, and also knowing that a textbook is still very much a human-lead endeavor that I write almost all of the sections on my own, or rather use Wispr Flow to dictate them and then edit them. The main contributions of Codex to this project were:
- helping me plan out the structure
- giving me the initial boilerplate/skeleton scaffold of the textbook itself
- creating the diagrams and equations, since this is much more effecient, in particular given my lack of LaTex scripting skills, and is inherently much lower-entropy than writing english, not requiring the same human creativity

## Target Audience

## How to Use This Book

## Acknowledgments

I shamelessly take inspiration from Nathan Lambert's [RLHF book](https://rlhfbook.com), and I am well aware that his textbook treats the subject of RLVR in quite some detail; notwithstanding, as he notes himself, this particular sub-field of ML is evolving so fast that much of the RLHF book's RLVR content will become outdated, and this book is intended to maintain pace with progress.

## Citation

You can cite this book directly with this BibTeX.

```{=html}
<div class="citation-copy-box" style="position: relative; max-width: 100%;">
  <button id="copy-bibtex-button" class="btn btn-sm btn-outline-secondary" style="position: absolute; top: 0.45rem; right: 0.45rem;" type="button">Copy</button>
  <pre id="bibtex-entry-text" style="white-space: pre; overflow: auto; padding-right: 4.5rem;"><code>@online{kyars2026rlvrbook,
  title  = {Reinforcement Learning from Verifiable Rewards},
  author = {Kyars, Kian},
  year   = {2026},
  url    = {https://github.com/kiankyars/rlvrbook},
  urldate = {2026-04-05}
}</code></pre>
</div>
<script>
(() => {
  const button = document.getElementById("copy-bibtex-button");
  const code = document.getElementById("bibtex-entry-text");
  if (!button || !code) return;
  button.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(code.textContent || "");
      const previous = button.textContent;
      button.textContent = "Copied";
      setTimeout(() => { button.textContent = previous; }, 1200);
    } catch (err) {
      button.textContent = "Failed";
      setTimeout(() => { button.textContent = "Copy"; }, 1200);
    }
  });
})();
</script>
```
