[Read the book](chapters/01-the-verifier-lens.md)  
[Download the PDF](rlvrbook.pdf)  
[View on GitHub](https://github.com/kiankyars/rlvrbook)

## Start Here

### New to RLVR

Read [Chapter 1](chapters/01-the-verifier-lens.md), [Chapter 2](chapters/02-outcome-verifiers.md), and [Chapter 7](chapters/07-reward-hacking-proxy-misspecification-and-verifier-robustness.md).

### Building Systems

Read [Chapter 4](chapters/04-learned-programmatic-and-hybrid-verifiers.md), [Chapter 5](chapters/05-turning-checks-into-training-signal.md), [Chapter 7](chapters/07-reward-hacking-proxy-misspecification-and-verifier-robustness.md), and [Chapter 9](chapters/09-canonical-domains-math-code-and-formal-proof.md).

### Frontier Research

Read [Chapter 8](chapters/08-faithfulness-confidence-and-what-verification-misses.md), [Chapter 10](chapters/10-long-context-multimodal-and-agentic-rlvr.md), and [Chapter 11](chapters/11-open-problems-and-the-research-agenda.md).

## Flagship Figure

The RLVR pipeline can be read as a stack from objective definition to policy/search updates.

::: {.content-visible when-format="html"}
<div class="rlvr-stack-widget" id="rlvr-stack-widget">
  <svg viewBox="0 0 1100 720" role="img" aria-labelledby="rlvrStackTitle rlvrStackDesc">
    <title id="rlvrStackTitle">The RLVR Verifier Stack</title>
    <desc id="rlvrStackDesc">Layered stack: Task, Trajectory, Evidence, Verifier, Reward, and Policy/Search.</desc>
    <defs>
      <marker id="stackArrow" markerWidth="12" markerHeight="8" refX="11" refY="4" orient="auto">
        <polygon points="0 0, 12 4, 0 8" fill="#374151"></polygon>
      </marker>
    </defs>

    <text x="550" y="55" text-anchor="middle" style="font: 700 32px Inter, Arial, sans-serif; fill: #111827;">The RLVR Verifier Stack</text>

    <g class="stack-layer" data-layer="task">
      <rect x="140" y="95" width="820" height="80" rx="14" fill="#dbeafe" stroke="#1d4ed8" stroke-width="2.5"></rect>
      <text x="180" y="143" style="font: 700 24px Inter, Arial, sans-serif; fill: #111827;">Task / Spec</text>
      <text x="510" y="143" style="font: 400 17px Inter, Arial, sans-serif; fill: #1f2937;">Define success criteria and what is checkable</text>
    </g>
    <g class="stack-layer" data-layer="trajectory">
      <rect x="140" y="190" width="820" height="80" rx="14" fill="#dcfce7" stroke="#15803d" stroke-width="2.5"></rect>
      <text x="180" y="238" style="font: 700 24px Inter, Arial, sans-serif; fill: #111827;">Trajectory</text>
      <text x="510" y="238" style="font: 400 17px Inter, Arial, sans-serif; fill: #1f2937;">Candidate reasoning trace, program, or action sequence</text>
    </g>
    <g class="stack-layer" data-layer="evidence">
      <rect x="140" y="285" width="820" height="80" rx="14" fill="#fef3c7" stroke="#b45309" stroke-width="2.5"></rect>
      <text x="180" y="333" style="font: 700 24px Inter, Arial, sans-serif; fill: #111827;">Evidence</text>
      <text x="510" y="333" style="font: 400 17px Inter, Arial, sans-serif; fill: #1f2937;">Tests, references, tools, constraints, and environment signals</text>
    </g>
    <g class="stack-layer" data-layer="verifier">
      <rect x="140" y="380" width="820" height="80" rx="14" fill="#ede9fe" stroke="#6d28d9" stroke-width="2.5"></rect>
      <text x="180" y="428" style="font: 700 24px Inter, Arial, sans-serif; fill: #111827;">Verifier</text>
      <text x="510" y="428" style="font: 400 17px Inter, Arial, sans-serif; fill: #1f2937;">Outcome, process, learned, or hybrid check function</text>
    </g>
    <g class="stack-layer" data-layer="reward">
      <rect x="140" y="475" width="820" height="80" rx="14" fill="#fee2e2" stroke="#b91c1c" stroke-width="2.5"></rect>
      <text x="180" y="523" style="font: 700 24px Inter, Arial, sans-serif; fill: #111827;">Reward</text>
      <text x="510" y="523" style="font: 400 17px Inter, Arial, sans-serif; fill: #1f2937;">Scalar score plus uncertainty and diagnostics</text>
    </g>
    <g class="stack-layer" data-layer="policy">
      <rect x="140" y="570" width="820" height="80" rx="14" fill="#e0f2fe" stroke="#0369a1" stroke-width="2.5"></rect>
      <text x="180" y="618" style="font: 700 24px Inter, Arial, sans-serif; fill: #111827;">Policy / Search</text>
      <text x="510" y="618" style="font: 400 17px Inter, Arial, sans-serif; fill: #1f2937;">Learn updates or choose best candidate at inference time</text>
    </g>

    <line x1="550" y1="176" x2="550" y2="190" stroke="#374151" stroke-width="3" marker-end="url(#stackArrow)"></line>
    <line x1="550" y1="271" x2="550" y2="285" stroke="#374151" stroke-width="3" marker-end="url(#stackArrow)"></line>
    <line x1="550" y1="366" x2="550" y2="380" stroke="#374151" stroke-width="3" marker-end="url(#stackArrow)"></line>
    <line x1="550" y1="461" x2="550" y2="475" stroke="#374151" stroke-width="3" marker-end="url(#stackArrow)"></line>
    <line x1="550" y1="556" x2="550" y2="570" stroke="#374151" stroke-width="3" marker-end="url(#stackArrow)"></line>
    <path d="M958 610 C1025 610, 1025 230, 958 230" fill="none" stroke="#0369a1" stroke-width="3.5" marker-end="url(#stackArrow)"></path>
    <text x="860" y="420" text-anchor="end" style="font: 500 15px Inter, Arial, sans-serif; fill: #374151;">resample / refine loop</text>
  </svg>
  <p class="rlvr-stack-detail" data-role="detail"></p>
</div>
<script>
(() => {
  const root = document.getElementById("rlvr-stack-widget");
  if (!root) return;

  const detail = root.querySelector("[data-role='detail']");
  const layers = Array.from(root.querySelectorAll(".stack-layer"));
  const copy = {
    task: "Task / Spec: sets the target behavior and determines which correctness signals are valid.",
    trajectory: "Trajectory: candidate reasoning, plans, actions, or code produced by the model/system.",
    evidence: "Evidence: external or internal artifacts used to evaluate the trajectory (tests, tools, references).",
    verifier: "Verifier: maps trajectory and evidence into pass/fail, partial credit, or richer judgments.",
    reward: "Reward: converts verifier outputs into a training or selection signal.",
    policy: "Policy / Search: updates parameters or picks trajectories, then loops back for more candidates."
  };

  function activate(layerKey) {
    layers.forEach((layer) => {
      layer.classList.toggle("is-active", layer.dataset.layer === layerKey);
    });
    if (detail) detail.textContent = copy[layerKey] || "";
  }

  layers.forEach((layer) => {
    const key = layer.dataset.layer;
    layer.addEventListener("mouseenter", () => activate(key));
    layer.addEventListener("click", () => activate(key));
  });

  activate("verifier");
})();
</script>
:::

::: {.content-visible when-format="pdf"}
![The RLVR Verifier Stack: Task/Spec, Trajectory, Evidence, Verifier, Reward, and Policy/Search with iterative feedback loops.](){#fig-rlvr-verifier-stack fig-alt="The RLVR Verifier Stack with layered flow from task to policy/search and looped refinement."}
:::

## Table of Contents

### Foundations

- [1. The Verifier Lens](chapters/01-the-verifier-lens.md)

### Verifier Design

- [2. Outcome Verifiers](chapters/02-outcome-verifiers.md)
- [3. Process Verifiers](chapters/03-process-verifiers.md)
- [4. Learned, Programmatic, and Hybrid Verifiers](chapters/04-learned-programmatic-and-hybrid-verifiers.md)

### From Verifiers to Capability

- [5. Turning Checks into Training Signal](chapters/05-turning-checks-into-training-signal.md)
- [6. Search and Test-Time Verification](chapters/06-search-and-test-time-verification.md)

### Failure Modes

- [7. Reward Hacking, Proxy Misspecification, and Verifier Robustness](chapters/07-reward-hacking-proxy-misspecification-and-verifier-robustness.md)
- [8. Faithfulness, Confidence, and What Verification Misses](chapters/08-faithfulness-confidence-and-what-verification-misses.md)

### Domains and Frontiers

- [9. Canonical Domains: Math, Code, and Formal Proof](chapters/09-canonical-domains-math-code-and-formal-proof.md)
- [10. Long-Context, Multimodal, and Agentic RLVR](chapters/10-long-context-multimodal-and-agentic-rlvr.md)
- [11. Open Problems and the Research Agenda](chapters/11-open-problems-and-the-research-agenda.md)

### Appendices

- [A. Minimal RL and Post-Training Background](appendices/a-minimal-rl-and-post-training-background.md)
- [B. Benchmarks, Evals, and Contamination](appendices/b-benchmarks-evals-and-contamination.md)
- [C. Practical Verifier Design Checklist](appendices/c-practical-verifier-design-checklist.md)

## LLM Use

Fortunately, we live in a world where AI slop writing is still *very* intelligible from genuine human text. It is knowing this fact, and also knowing that a textbook is still very much a human-lead endeavor that I write almost all of the sections on my own, or rather use Wispr Flow to dictate them and then edit them. The main contributions of Codex to this project were:
- helping me plan out the structure
- giving me the initial boilerplate/skeleton scaffold of the textbook itself
- creating the diagrams and equations, since this is much more effecient, in particular given my lack of LaTex scripting skills, and is inherently much lower-entropy than writing english, not requiring the same human creativity

## Acknowledgments

- I shamelessly take inspiration from Nathan Lambert's [RLHF book](https://rlhfbook.com), and I am well aware that his textbook treats the subject of RLVR in quite some detail; notwithstanding, as he notes himself, this particular sub-field of ML is evolving so fast that much of the RLHF book's RLVR content will become outdated, and this book is intended to maintain pace with progress.
