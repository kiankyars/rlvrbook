# Introduction

![M. C. Escher, _Tower of Babel_ (1928).](../art/escher/01-tower-of-babel.jpg){width="80%" fig-align="center"}

## Chapter Map

- Define RLVR as learning from verifiable reward signals and explain which tasks admit them.
- Explain why RLVR became central to reasoning models and preview the structure of the book.

## What RLVR Is

RLVR is reinforcement learning on tasks where the reward does not need to be guessed from preference comparisons alone because some meaningful part of correctness can be checked directly. Sometimes that check is exact, as in symbolic math or formal proof. Sometimes it is executable, as in code generation with tests. Sometimes it is partial, as in grounded question answering or tool-using agents where only some parts of the trajectory can be reliably scored. The unifying idea is not a specific optimizer. It is the availability of a notion of task success. Once a task can expose useful correctness signals, reinforcement learning can optimize against them, search can exploit them at inference time, and systems can often improve far beyond what static supervised fine-tuning alone would produce.

::: {#fig-verifier-stack}
![](../diagrams/01-verifier-stack-light.png){.light-content}

![](../diagrams/01-verifier-stack-dark.png){.dark-content}

RLVR is defined by learning from verifiable reward signals; the optimizer can vary.
:::

## Origins of RLVR

In one sense RLVR is the oldest paradigm in reinforcement learning, since it learns from direct reward rather than preference comparison; what is new is its explicit application to language models through verifiers that can check answers, code, proofs, and traces.

I personally reflect back on the advent of reasoning models and reinforcement learning through a strange amnesia of an idea so simple with hindsight, but which took two years after ChatGPT to discover. This assessment, however, is unfair in the sense that the idea to make models think step by step long predates the 2024 reasoning-model wave.[^ch1-step-by-step] The broader prompting paradigm emerged across late 2021 and early 2022: scratchpads for intermediate computation appeared first, chain-of-thought prompting then formalized the use of intermediate reasoning traces, and the exact zero-shot prompt "Let's think step by step" was popularized a few months later.

Before the reasoning-model wave of 2024, code generation had already explored reinforcement learning against executable verifiers: CodeRL (July 5, 2022), PPOCoder (January 31, 2023), and RLTF (July 10, 2023) all trained language models using unit tests or execution feedback as objective reward signals.[^ch1-code-priors]

DeepSeekMath, published on February 5, 2024, was the first major open paper to apply this verifier-driven RL pattern to mathematical reasoning at LLM scale via GRPO.

Things heated up in September 2024, when OpenAI published "Learning to Reason with LLMs", indicating that they had used a train-time and test-time compute strategy to enhance model reasoning through reinforcement learning in math, and coding tasks.[^ch1-openai-o1] The name "Reinforcement Learning with Verifiable Rewards" (RLVR) was coined in the Tulu 3 paper, submitted on November 22, 2024.[^ch1-deepseekmath-rlvr-name] Finally, there was DeepSeek-R1, which demonstrated the full verifier-driven RL formula for bootstrapping reasoning models.[^ch1-deepseek-r1] To quote someone describing the atmosphere at Meta after R1 launched, “Engineers are moving frantically to dissect DeepSeek and copy anything and everything we can from it.” and according to Fortune, there were war rooms assembled to understand how a Chinese lab with substantially less resources was beating them.[^ch1-meta-reaction]

The trend we can extract from this short history is that model improvement increasingly depended on checkable interfaces.

## What Kinds of Tasks Admit Verifiable Rewards
Tasks admit verifiable rewards when they expose an interface that can separate better behavior from worse behavior at acceptable cost. The strongest cases are the familiar ones. Math problems often allow answer checking up to normalization. Code can be run against visible and hidden tests. Formal proof systems can accept or reject proof states under explicit rules. These domains became central not because they exhaust the meaning of reasoning, but because they expose unusually clean signals.

Other tasks are weaker but still useful. Long-context question answering may permit citation checks, evidence matching, or entailment-style grading. Tool-using agents may expose environment transitions, task completion criteria, or execution traces. These signals are often noisier, more expensive, and easier to exploit, but they can still support learning if the reward channel is informative enough.

The practical lesson is that RLVR does not apply uniformly across all tasks. It is strongest where correctness is legible and weakest where the reward channel is sparse, ambiguous, or only loosely coupled to the capability we want.

A useful way to see the space is as a domain map. One axis is verification strength: how cleanly the checker separates better behavior from worse behavior. The other is verification granularity: whether the checked object is a coarse final artifact, a partially grounded intermediate object, or a fine-grained trajectory. The placements in Figure @fig-domain-map are a schematic synthesis of current verifier interfaces rather than a single measured benchmark score.[@shao2024deepseekmath; @liu2023rltf; @xin2024deepseekproverv15; @zhang2024longcite; @lu2023mathvista; @zhou2023webarena; @xie2024osworld]

::: {#fig-domain-map}
::: {.content-visible when-format="html"}
```{=html}
<div class="dm" data-default-domain="math">
  <p class="dm-hint">Click a domain to see what its verifier checks, where it can be gamed, and what it misses.</p>

  <svg class="dm-svg" viewBox="0 0 700 420" aria-label="RLVR domain map: six domains plotted by verification strength and granularity.">
    <rect class="dm-bg" x="80" y="10" width="590" height="370" rx="6" />

    <g class="dm-grid">
      <line x1="80" y1="103" x2="670" y2="103" />
      <line x1="80" y1="196" x2="670" y2="196" />
      <line x1="80" y1="289" x2="670" y2="289" />
      <line x1="277" y1="10" x2="277" y2="380" />
      <line x1="473" y1="10" x2="473" y2="380" />
    </g>

    <g class="dm-axes">
      <line x1="80" y1="380" x2="670" y2="380" />
      <line x1="80" y1="380" x2="80" y2="10" />
    </g>

    <g class="dm-labels">
      <text x="375" y="410" text-anchor="middle">Verification strength</text>
      <text x="110" y="400">Weak</text>
      <text x="630" y="400">Strong</text>
      <text x="28" y="200" transform="rotate(-90 28 200)">Verification granularity</text>
      <text x="72" y="375" text-anchor="end" class="dm-tick">Coarse</text>
      <text x="72" y="20" text-anchor="end" class="dm-tick">Fine</text>
    </g>

    <g class="dm-point" data-domain="proof" tabindex="0" role="button" aria-label="Proof">
      <circle class="dm-halo" cx="610" cy="55" r="28" />
      <circle class="dm-dot dm-c-proof" cx="610" cy="55" r="14" />
      <text class="dm-name" x="610" y="90" text-anchor="middle">Proof</text>
    </g>
    <g class="dm-point" data-domain="agentic" tabindex="0" role="button" aria-label="Agentic">
      <circle class="dm-halo" cx="210" cy="100" r="28" />
      <circle class="dm-dot dm-c-agentic" cx="210" cy="100" r="14" />
      <text class="dm-name" x="210" y="135" text-anchor="middle">Agentic</text>
    </g>
    <g class="dm-point" data-domain="code" tabindex="0" role="button" aria-label="Code">
      <circle class="dm-halo" cx="540" cy="185" r="28" />
      <circle class="dm-dot dm-c-code" cx="540" cy="185" r="14" />
      <text class="dm-name" x="540" y="220" text-anchor="middle">Code</text>
    </g>
    <g class="dm-point" data-domain="long_context_qa" tabindex="0" role="button" aria-label="Long-context QA">
      <circle class="dm-halo" cx="370" cy="225" r="28" />
      <circle class="dm-dot dm-c-lcqa" cx="370" cy="225" r="14" />
      <text class="dm-name" x="370" y="260" text-anchor="middle">Long-context QA</text>
    </g>
    <g class="dm-point" data-domain="multimodal" tabindex="0" role="button" aria-label="Multimodal">
      <circle class="dm-halo" cx="270" cy="280" r="28" />
      <circle class="dm-dot dm-c-multi" cx="270" cy="280" r="14" />
      <text class="dm-name" x="270" y="315" text-anchor="middle">Multimodal</text>
    </g>
    <g class="dm-point" data-domain="math" tabindex="0" role="button" aria-label="Math">
      <circle class="dm-halo" cx="570" cy="330" r="28" />
      <circle class="dm-dot dm-c-math" cx="570" cy="330" r="14" />
      <text class="dm-name" x="570" y="365" text-anchor="middle">Math</text>
    </g>
  </svg>

  <div class="dm-detail" aria-live="polite">
    <h5 class="js-dm-title">Math</h5>
    <p class="dm-summary js-dm-summary"></p>
    <dl class="dm-facts">
      <dt>Checked object</dt>  <dd class="js-dm-checked"></dd>
      <dt>Attack surface</dt>  <dd class="js-dm-attack"></dd>
      <dt>Blind spot</dt>      <dd class="js-dm-blind"></dd>
    </dl>
  </div>
</div>

<script>
(() => {
  const D = {
    math: {
      title: "Math",
      summary: "Symbolic normalization makes math unusually verifier-friendly, but most rewards still score the endpoint rather than the reasoning path.",
      checked: "Final answer, normalized expression, or equivalence class (set, boxed value, symbolic form).",
      attack: "Brittle extraction, formatting hacks, alternate-but-unparseable surface forms, and benchmark leakage.",
      blind: "Whether the reasoning was faithful, reusable, or causally responsible for the final answer."
    },
    code: {
      title: "Code",
      summary: "Execution against tests gives sharper feedback than most language tasks, but the verifier only sees behavior on the covered cases.",
      checked: "Program outputs, execution traces, unit-test outcomes, and sometimes compiler/runtime signals.",
      attack: "Overfitting to the visible suite, hard-coded answers, environment quirks, and shallow patches that satisfy narrow tests.",
      blind: "Untested behaviors, reliability under distribution shift, efficiency, security, and maintainability outside the harness."
    },
    proof: {
      title: "Proof",
      summary: "Proof assistants offer the cleanest verifier because each step is checked against a formal kernel rather than a soft proxy.",
      checked: "Theorem statement, sequence of proof states, and final proof object accepted by Lean, Coq, or similar.",
      attack: "Mis-specified theorems, unsafe assumptions, helper-lemma leakage, and automation exploitation.",
      blind: "Informal explanatory value, theorem selection, and whether the proof strategy transfers outside the formalization."
    },
    long_context_qa: {
      title: "Long-context QA",
      summary: "Citation-aware QA makes more of the answer checkable, but evidence presence does not guarantee faithful synthesis.",
      checked: "Sentence-level citations, retrieved spans, support sets, and answer-evidence alignment over long documents.",
      attack: "Citation stuffing, irrelevant but plausible evidence, sentence-boundary mismatch, and borrowed support without faithful use.",
      blind: "Hidden hallucinations between supported sentences, causal use of evidence, and global consistency."
    },
    multimodal: {
      title: "Multimodal",
      summary: "Multimodal benchmarks often expose exact answers, but perception ambiguity keeps the checker weaker than symbolic domains.",
      checked: "Final answer and sometimes auxiliary structure: bounding boxes, chart values, OCR strings, or grounded references.",
      attack: "Answer priors, shortcut cues, OCR artifacts, annotation ambiguity, and rewarding text without visual grounding pressure.",
      blind: "Whether the model truly used the visual evidence and whether failures came from perception, grounding, or reasoning."
    },
    agentic: {
      title: "Agentic",
      summary: "Agents expose rich trajectories, but the success signal is brittle because environments are open-ended and easy to game.",
      checked: "Tool calls, environment transitions, intermediate state changes, and task-completion scripts over long horizons.",
      attack: "Reward hacking, simulator exploits, degenerate loops, and policies that succeed in the sandbox but not in practice.",
      blind: "Side effects, robustness, safety, human acceptability, and transfer from benchmark scripts to real tasks."
    }
  };

  document.querySelectorAll(".dm").forEach(root => {
    const pts = [...root.querySelectorAll(".dm-point")];
    const el = (s) => root.querySelector(s);

    const show = (name) => {
      const d = D[name]; if (!d) return;
      pts.forEach(p => p.classList.toggle("is-active", p.dataset.domain === name));
      el(".js-dm-title").textContent = d.title;
      el(".js-dm-summary").textContent = d.summary;
      el(".js-dm-checked").textContent = d.checked;
      el(".js-dm-attack").textContent = d.attack;
      el(".js-dm-blind").textContent = d.blind;
    };

    pts.forEach(p => {
      const n = p.dataset.domain;
      p.addEventListener("mouseenter", () => show(n));
      p.addEventListener("focus", () => show(n));
      p.addEventListener("click", () => show(n));
    });

    show(root.dataset.defaultDomain || "math");
  });
})();
</script>
```
:::

::: {.content-visible when-format="pdf"}
The six domains, from strongest to weakest verification signal: **Proof** (formally accepted proof state; attack surface: theorem mis-specification; blind spot: informal usefulness). **Code** (execution against tests; attack surface: suite overfitting; blind spot: untested behavior). **Math** (normalized final answer; attack surface: parser brittleness; blind spot: reasoning faithfulness). **Long-context QA** (answer plus evidence alignment; attack surface: citation stuffing; blind spot: faithful synthesis). **Multimodal** (answer with partial grounding; attack surface: shortcut cues; blind spot: visual grounding). **Agentic** (trajectory plus task completion; attack surface: reward hacking; blind spot: real-world transfer).
:::

What can be verified? A schematic domain map of RLVR by verification strength and verification granularity. The axes summarize common verifier interfaces in current practice rather than a single benchmark-derived score.
:::

## Why RLVR Became Central to Reasoning Models

RLVR and reasoning go hand in hand, but they are different. The former is a training paradigm, and the latter is a capability: multi-step breakdown, search, planning, tool use, etc. The marriage between the two occurs because the most successful reasoning domains are exactly the ones with strong verifiers: math, code, proofs, some grounded QA. That combination is rare. It means the same domains that demand search, decomposition, and iterative refinement are also the domains where reinforcement learning has the cleanest chance to work.

This is also why RLVR and reasoning are easy to conflate, and the overlap is large because verifier-friendly domains have been the best places to scale reasoning performance. The result is that some of the most important progress in reasoning models has come from learning against verifiable rewards.

## Verifiable Does Not Mean Complete

Even strong reward signals remain proxies. A math reward may depend on brittle extraction. A code harness may miss behaviors outside the test suite. A proof system may validate a derivation without telling us whether the model's decomposition was insightful or robust. A grounded QA reward may verify some citations without guaranteeing that the answer used evidence faithfully.

That is not a criticism of RLVR so much as a statement of its operating conditions. The important questions are always: what is being checked, what is being missed, how expensive the check is, and how easily the signal can be gamed. Much of the rest of the book is about that gap between a usable reward signal and the fuller competence we actually want.

## What This Book Covers

The next chapters move from the general paradigm to the main reward regimes in practice. Chapters 2 through 4 cover outcome rewards, process rewards, and learned or hybrid verification pipelines. Chapter 5 asks when a check becomes useful learning signal rather than merely a filter. Chapter 6 turns to search and test-time verification, since RLVR in modern systems is inseparable from inference-time compute. Chapters 7 and 8 focus on the main failure modes: reward hacking, proxy misspecification, faithfulness, confidence, and the limits of what verification can certify. Chapters 9 and 10 compare the paradigm across its strongest and most difficult domains. Chapter 11 closes with the open problems.

[^ch1-step-by-step]: A useful compressed lineage runs from scratchpads in late 2021, to chain-of-thought prompting in January 2022, to the exact zero-shot prompt "Let's think step by step" in May 2022 [@nye2021show; @wei2022chain; @kojima2022zeroshot].
[^ch1-code-priors]: CodeRL was submitted on July 5, 2022 and used unit tests and a critic model to guide program synthesis [@le2022coderl]. PPOCoder was submitted on January 31, 2023 and used execution-based feedback with PPO [@shojaee2023ppocoder]. RLTF was submitted on July 10, 2023 and used online unit-test feedback of multiple granularities for code LLMs [@liu2023rltf].
[^ch1-deepseekmath-rlvr-name]: DeepSeekMath introduced GRPO and used RL to improve mathematical reasoning in an open model [@shao2024deepseekmath]. Tulu 3 later introduced the name "Reinforcement Learning with Verifiable Rewards (RLVR)" for this broader training pattern [@lambert2024tulu3].
[^ch1-openai-o1]: OpenAI's writeup states that `o1` performance improved with both more reinforcement learning, which they describe as train-time compute, and more time spent thinking at test time [@openai2024o1].
[^ch1-deepseek-r1]: DeepSeek-R1 argues that reasoning abilities can be incentivized through pure reinforcement learning on verifiable tasks such as mathematics, coding competitions, and STEM fields [@deepseekai2025r1].
[^ch1-meta-reaction]: The quoted line was reported as an anonymous Teamblind post summarized by TMTPOST, while the claim that Meta created four "war rooms" was reported by Fortune, citing The Information [@tmtpost2025deepseek; @quirozgutierrez2025warrooms].
