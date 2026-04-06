# Search and Test-Time Verification

![M. C. Escher, _Calanques de Piana_ (1928).](../art/escher/06-calanques-de-piana.jpg){width="80%" fig-align="center"}

## Chapter Map

- A verifier can improve a system without any parameter update; this chapter covers what that looks like and why it matters.
- Most reported reasoning-model results conflate gains from training with gains from search; this chapter separates them.

## This is not RL, and that matters

Chapters 2 through 5 treated the verifier as a source of training signal. The model generates rollouts, the verifier scores them, and the optimizer updates parameters. That is reinforcement learning from verifiable rewards.

This chapter is not about reinforcement learning. It is about what verifiers do at inference time, without any parameter update at all.

Best-of-$N$ reranking with a reward model is not RL. Majority voting over sampled reasoning paths is not RL. PRM-guided beam search is not RL. These are inference-time strategies that use the same verifier object — the same $r(x, y)$ — to improve outputs by generating multiple candidates and exploiting the checker to select or guide among them. They require no gradient, no replay buffer, no training loop.

The distinction matters because many reported results reflect both mechanisms simultaneously. When a paper states that an RL-trained model achieves 90% on MATH using best-of-64 selection with an ORM, the number reflects both the training-time gain (the policy is better than it was before RL) and the inference-time gain (the best of 64 candidates is better than a single sample). A reader who cannot separate the two cannot evaluate the claim.

This chapter studies the verifier's inference-time role. Not because it is RLVR, but because understanding it is necessary to evaluate RLVR honestly.

## A running example in code

The earlier chapters used a quadratic equation as a running example. This chapter switches to code, because code generation is the domain where inference-time verification is most naturally deployable: the test suite is the verifier, it runs without a known answer, and pass@$k$ was invented specifically to measure how much sampling helps.[@chen2021codex]

The task: generate a Python function that finds the longest substring without repeating characters. The problem admits multiple correct implementations — a brute-force approach with nested loops, a sliding-window approach with a set, a hash-map approach that tracks last-seen positions — and several plausible-looking implementations that fail on edge cases (empty strings, single-character strings, strings where every character repeats).

A test suite is the verifier. Five visible tests check basic behavior: `"abcabcbb"` returns 3, `"bbbbb"` returns 1, `"pwwkew"` returns 3, `""` returns 0, `"a"` returns 1. A hidden suite of 50 tests covers edge cases, Unicode, and adversarial inputs. The visible suite is cheap and fast; the hidden suite is more thorough but expensive.

## Selection: the verifier as ranker

The simplest inference-time use of a verifier: generate $N$ candidate solutions, score all of them, pick the best.

### Best-of-$N$ with an outcome verifier

Cobbe et al. introduced the verifier-as-ranker setup for math: generate $N$ solutions, score each with a trained verifier, return the highest-scoring one.[@cobbe2021training] The same idea applies directly to code: generate $N$ implementations, run each against the test suite, return one that passes all tests. If multiple candidates pass, a learned judge or secondary metric can break ties.

Best-of-$N$ is embarrassingly parallel — all candidates can be generated and scored independently — and surprisingly powerful. The probability that at least one of $N$ independent samples is correct grows as $1 - (1 - p)^N$, where $p$ is the per-sample success rate. Even a weak policy with $p = 0.1$ has a 65% chance of producing at least one correct solution among $N = 10$ samples, and 88% among $N = 20$.

For the running example, suppose the model generates 16 candidate implementations. At pass@1, the model succeeds 45% of the time. Among 16 samples, 10 pass the visible test suite. Best-of-16 with visible tests picks one of the 10 — a substantial gain from pure sampling plus a cheap verifier.

### Best-of-$N$ with a process verifier

Lightman et al. showed that scoring by the minimum step-level PRM probability outperforms ORM-based scoring on harder math problems.[@lightman2023letsverify] The intuition transfers to code: a process-aware verifier that evaluates intermediate reasoning (plan, implementation strategy, edge-case handling) can distinguish between a solution that passes tests by accident and one that passes them for the right reasons. Best-of-$N$ with a PRM is more expensive per candidate — the verifier scores each step — but it selects more robustly.

### Self-consistency

Wang et al. showed that sampling multiple reasoning paths and taking a majority vote over their answers improves accuracy without any external verifier.[@wang2022selfconsistency] In code, self-consistency means: generate $N$ implementations, cluster them by algorithm (sliding window, hash map, brute force), and pick the algorithm that the most candidates converge on. If 11 of 16 candidates implement a sliding-window approach and all produce the same outputs, the agreement pattern is evidence of correctness — even without running a single test.

### pass@$k$ and the evaluation concept

Chen et al. defined pass@$k$: the probability that at least one of $k$ samples passes all tests.[@chen2021codex] This metric cleanly separates the policy's intrinsic capability from the amplification that sampling provides. pass@1 measures the policy. pass@100 measures the policy plus selection. The gap between them quantifies how much inference-time compute helps — and how much the reported result depends on the evaluation protocol rather than the model.

The gap can be large. The original Codex paper reported 28.8% pass@1 on HumanEval but 70.2% pass@100 — a 2.4x multiplier from sampling alone.[@chen2021codex] An RL-trained model that achieves 70% pass@1 is genuinely stronger than a base model at 70% pass@100, even though the headline number is the same, because the first number reflects internalized capability and the second reflects search.

### Compute-optimal selection

Snell et al. extended the analysis to ask: given a fixed compute budget, how should you split it between generating more candidates and spending more on verification?[@snell2024scaling] Their key result is that the optimal allocation depends on problem difficulty. For easy problems where the per-sample success rate is already high, additional samples provide little marginal benefit and the budget is better spent on harder problems. For hard problems where success is rare, PRM-guided selection can be 4x more efficient than naive best-of-$N$, and a smaller model with more search can match or exceed the performance of a 14x larger model at matched compute.

This is the result that makes the amortization question urgent: if a small model plus heavy search can match a large RL-trained model at pass@1, what exactly did the RL training buy?

## Search: the verifier as controller

Selection scores completed outputs. Search uses the verifier *during* generation to shape the trajectory.

**PRM-guided beam search.** At each reasoning step, expand only the branches whose PRM score exceeds a threshold. Prune low-scoring branches early. The search tree fans out at high-confidence steps and narrows at ambiguous ones. The verifier's latency is coupled to the generation process — every step requires a scoring call — so this approach is practical only when the verifier is fast (a small PRM, a cached classifier, or a formal checker with near-zero latency).

**Draft-and-check loops.** Generate a full draft solution, then run the verifier on checkpoints: does the code compile? Do the visible tests pass? Does the static analyzer flag anything? If a checkpoint fails, backtrack to the last verified state and retry. This is the pattern behind many code-generation agents: generate, test, debug, regenerate. The verifier is not scoring partial steps but gating the generation loop.

**Tool-gated continuation.** The model calls an external tool — a code interpreter, a calculator, a retrieval system — and the tool's output is itself a verification signal. If the code interpreter raises an exception, the generation backtracks. If the retrieved document contradicts the current answer, the model revises. The verifier is embedded in the generation loop as an environment that responds to the model's actions.

**MCTS with verifier scoring.** AlphaProof-style search over formal proof space uses Monte Carlo tree search where the proof kernel provides exact step-level verification and the search algorithm explores the tree.[@trinh2025alphaproof] Each tactic application is checked by the kernel immediately. This is the strongest form of search-with-verification: exact, per-step, and online. It is also the most domain-restricted, because it requires a deployable step-level verifier — which limits it to formal systems.

The key difference from selection: **search changes the distribution of outputs** the system produces, while selection only filters a fixed sample. A model that generates 16 independent candidates and picks the best one can only recover solutions that the model already had some probability of producing. A model that uses a verifier to prune branches, backtrack, and redirect can explore parts of the solution space that no single forward pass would reach. Search is more powerful, but also more expensive and more sensitive to verifier latency and accuracy.

For the running example: selection generates 16 complete implementations and picks the one that passes the most tests. Search generates one implementation step by step, testing after each function or block, backtracking when tests fail, and producing a single, iteratively refined solution. Selection parallelizes easily. Search adapts in real time.

## Oracle verification vs. deployable verification

Not all verifiers that work at evaluation time work at deployment time. This is the most important distinction in the chapter.

**Oracle verification** requires information that is unavailable in production. A math answer checker that compares the model's answer to a known ground truth is oracle: at deployment, you do not have the ground truth. An answer key for multiple-choice questions is oracle. Any verifier that needs the correct answer to produce a score is oracle.

**Deployable verification** works without the ground truth. A test suite runs the model's code and checks whether the outputs match expected behavior — the test author specified the expectations in advance, and the suite runs without any privileged knowledge at serving time. A proof kernel accepts or rejects a proof term against axioms. An environment returns success or failure when an agent acts. A learned judge scores the output using only the prompt and the response.

The distinction matters for three reasons.

First, oracle search inflates benchmark numbers. When a math evaluation reports best-of-64 accuracy using a ground-truth answer checker, the system's reported score includes verifier access that a deployed system would not have. The number measures "how often does the model produce the right answer somewhere in 64 samples, given that we know which one is right?" That is a useful research metric, but it is not a deployment capability.

Second, deployable verifiers are the real product feature. A code generation system that runs its own tests before presenting a solution to the user is deployable. A proof assistant that rejects invalid proofs at serving time is deployable. A math tutor that checks the student's answer against a known solution is oracle — fine for education, where you have the answer key, but not generalizable.

Third, the gap between oracle and deployable search performance measures how much the system depends on the verifier's privileged access. If oracle best-of-64 achieves 95% and deployable best-of-64 (using a learned judge instead of the answer key) achieves 75%, the 20-point gap quantifies verification quality loss when the gold label is removed.

Code is the domain where this distinction is most favorable. The test suite is a deployable verifier by construction: you write the tests before you see the model's solution, and you run them without any privileged knowledge. This is why code generation results are often more credible than math results at comparable headline numbers — the evaluation protocol is closer to the deployment protocol.

## The flagship figure: search vs. amortization

::: {#fig-ch6-search-vs-amortization}

::: {.content-visible when-format="html"}

```{=html}
<div class="sva-widget" id="sva-widget">
  <p class="sva-hint">Drag the budget slider to see how accuracy changes with inference-time compute. Toggle the RL-trained curve to compare.</p>

  <div class="sva-controls">
    <label class="sva-toggle-label">
      <input type="checkbox" id="sva-toggle-rl" checked>
      Show RL-trained model
    </label>
    <div class="sva-slider-row">
      <span class="sva-label">Budget (candidates):</span>
      <input type="range" id="sva-budget" min="0" max="6" step="1" value="6">
      <span id="sva-budget-val" class="sva-label">64</span>
    </div>
  </div>

  <svg class="sva-svg" viewBox="0 0 600 360" aria-label="Search vs Amortization: accuracy as a function of inference-time compute budget.">
    <line x1="60" y1="20" x2="60" y2="300" stroke="var(--bs-border-color, #aaa)" stroke-width="1"/>
    <line x1="60" y1="300" x2="580" y2="300" stroke="var(--bs-border-color, #aaa)" stroke-width="1"/>

    <text x="30" y="165" text-anchor="middle" transform="rotate(-90,30,165)" fill="var(--bs-body-color, #333)" font-size="12">Accuracy (%)</text>
    <text x="320" y="345" text-anchor="middle" fill="var(--bs-body-color, #333)" font-size="12">Inference-time budget (candidates)</text>

    <g id="sva-yticks"></g>
    <g id="sva-xticks"></g>

    <polyline id="sva-base-line" fill="none" stroke="#6c757d" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    <polyline id="sva-rl-line" fill="none" stroke="var(--bs-primary, #2c7be5)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>

    <g id="sva-base-dots"></g>
    <g id="sva-rl-dots"></g>

    <text x="480" y="195" fill="#6c757d" font-size="11" font-weight="600">Base + search</text>
    <text id="sva-rl-label" x="480" y="95" fill="var(--bs-primary, #2c7be5)" font-size="11" font-weight="600">RL + search</text>
  </svg>

  <div class="sva-summary" id="sva-summary" aria-live="polite"></div>
</div>

<style>
.sva-widget { max-width: 640px; margin: 1.2em auto; font-family: var(--bs-body-font-family, system-ui, sans-serif); }
.sva-hint { font-size: 0.88em; color: var(--bs-secondary-color, #6c757d); margin-bottom: 0.5em; }
.sva-controls { display: flex; flex-wrap: wrap; gap: 1em; align-items: center; margin-bottom: 0.6em; }
.sva-toggle-label { font-size: 0.9em; cursor: pointer; display:flex; align-items:center; gap:0.4em; }
.sva-slider-row { display:flex; align-items:center; gap:0.5em; }
.sva-label { font-size: 0.9em; }
.sva-svg { width: 100%; height: auto; }
.sva-summary { margin-top: 0.5em; padding: 0.6em 0.8em; border-radius: 6px;
  background: var(--bs-tertiary-bg, #f8f9fa); font-size: 0.88em; line-height: 1.5; }
</style>

<script>
(() => {
  const budgets = [1, 2, 4, 8, 16, 32, 64];
  const baseAcc = [28, 38, 48, 56, 63, 68, 72];
  const rlAcc  = [52, 60, 67, 73, 78, 82, 85];

  const xMin = 60, xMax = 580, yMin = 20, yMax = 300;
  function xPos(i) { return xMin + (i / 6) * (xMax - xMin); }
  function yPos(v) { return yMax - ((v - 20) / 70) * (yMax - yMin); }

  function drawTicks() {
    let yt = document.getElementById("sva-yticks"); yt.innerHTML = "";
    for (let v = 20; v <= 90; v += 10) {
      const y = yPos(v);
      let t = document.createElementNS("http://www.w3.org/2000/svg","text");
      t.setAttribute("x", 55); t.setAttribute("y", y + 4);
      t.setAttribute("text-anchor","end"); t.setAttribute("font-size","10");
      t.setAttribute("fill","var(--bs-body-color,#555)"); t.textContent = v;
      yt.appendChild(t);
      let l = document.createElementNS("http://www.w3.org/2000/svg","line");
      l.setAttribute("x1", 58); l.setAttribute("x2", xMax);
      l.setAttribute("y1", y); l.setAttribute("y2", y);
      l.setAttribute("stroke","var(--bs-border-color,#e0e0e0)"); l.setAttribute("stroke-width","0.5");
      yt.appendChild(l);
    }
    let xt = document.getElementById("sva-xticks"); xt.innerHTML = "";
    budgets.forEach((b, i) => {
      const x = xPos(i);
      let t = document.createElementNS("http://www.w3.org/2000/svg","text");
      t.setAttribute("x", x); t.setAttribute("y", 318);
      t.setAttribute("text-anchor","middle"); t.setAttribute("font-size","10");
      t.setAttribute("fill","var(--bs-body-color,#555)"); t.textContent = b;
      xt.appendChild(t);
    });
  }

  function render(maxIdx, showRL) {
    function pts(arr) {
      return arr.slice(0, maxIdx+1).map((v,i) => xPos(i)+","+yPos(v)).join(" ");
    }
    function dots(arr, gId, color) {
      const g = document.getElementById(gId); g.innerHTML = "";
      arr.slice(0, maxIdx+1).forEach((v,i) => {
        let c = document.createElementNS("http://www.w3.org/2000/svg","circle");
        c.setAttribute("cx", xPos(i)); c.setAttribute("cy", yPos(v));
        c.setAttribute("r", 4); c.setAttribute("fill", color);
        g.appendChild(c);
      });
    }
    document.getElementById("sva-base-line").setAttribute("points", pts(baseAcc));
    dots(baseAcc, "sva-base-dots", "#6c757d");

    const rlLine = document.getElementById("sva-rl-line");
    const rlLabel = document.getElementById("sva-rl-label");
    if (showRL) {
      rlLine.setAttribute("points", pts(rlAcc));
      rlLine.style.display = ""; rlLabel.style.display = "";
      dots(rlAcc, "sva-rl-dots", "var(--bs-primary, #2c7be5)");
    } else {
      rlLine.style.display = "none"; rlLabel.style.display = "none";
      document.getElementById("sva-rl-dots").innerHTML = "";
    }

    const b = budgets[maxIdx];
    const ba = baseAcc[maxIdx], ra = rlAcc[maxIdx];
    document.getElementById("sva-budget-val").textContent = b;
    let s = "At budget\u00A0=\u00A0" + b + ": base model " + ba + "%";
    if (showRL) s += ", RL-trained " + ra + "%. Training gain at pass@1: " +
      (rlAcc[0] - baseAcc[0]) + " points. Marginal search gain (RL): " + (ra - rlAcc[0]) + " points.";
    else s += ".";
    document.getElementById("sva-summary").textContent = s;
  }

  drawTicks();
  const slider = document.getElementById("sva-budget");
  const toggle = document.getElementById("sva-toggle-rl");
  function update() { render(parseInt(slider.value), toggle.checked); }
  slider.addEventListener("input", update);
  toggle.addEventListener("change", update);
  update();
})();
</script>
```
:::

::: {.content-visible when-format="pdf"}

| Budget (candidates) | Base model | RL-trained model | Training gain |
|:-------------------:|:----------:|:----------------:|:-------------:|
| 1 (pass@1) | 28% | 52% | +24 |
| 4 | 48% | 67% | +19 |
| 16 | 63% | 78% | +15 |
| 64 | 72% | 85% | +13 |

: As inference-time budget increases, both models improve. The RL-trained model starts higher (better pass@1) and the marginal gain from additional search is smaller, because training has already amortized much of what search provides. The training gain (right column) shrinks at higher budgets because search partly substitutes for training.

:::

Accuracy as a function of inference-time compute budget. The RL-trained model starts higher and rises more slowly: training has amortized some of the gain that search would otherwise provide. Numbers are illustrative, synthesized from the patterns in Snell et al. and Chen et al.[@snell2024scaling; @chen2021codex]
:::

## Why RL still matters: amortization

If best-of-$N$ plus a test suite is so powerful, why bother with RL at all?

**Latency.** Search requires generating and scoring multiple candidates. An RL-trained model that has internalized the verified patterns produces a better output in a single forward pass. At serving time, the difference between one generation and 64 is the difference between 200ms and 13 seconds.

**Cost.** At deployment, compute is money. A model that has amortized search gains into its weights serves cheaper per query than one that requires $N$ candidates and $N$ verifier calls. If inference-time search costs 64x more compute, the RL-trained model's pass@1 is the more relevant number for production.

**Coverage.** Search helps only when the verifier is available. A code model that learned robust patterns from RL on test-suite-verified tasks will generalize, at least partially, to coding tasks where no test suite exists — code review, refactoring, documentation generation. The RL-trained policy has internalized patterns from verified tasks that transfer to unverified settings. Pure search cannot do this: it requires the verifier to be present at inference time.

**Exploration.** Search over the current policy's sampling distribution can only find solutions the policy can already almost produce. RL changes the sampling distribution itself. It reinforces strategies that lead to verified success and suppresses strategies that do not, shifting the model's probability mass toward better solutions. After RL, even pass@1 reflects a better distribution, not just a better selection from the old one.

**Expert iteration as the explicit bridge.** STaR makes the amortization loop explicit: generate solutions, filter by verifier, fine-tune on successes, repeat.[@zelikman2022star] Each round distills the search-assisted distribution into the policy's parameters. The model gets better, so the next round of search starts from a higher baseline. RLVR via GRPO or PPO is a more continuous version of the same loop — the amortization happens at every gradient step rather than in discrete rounds.

## Reporting results fairly

The confound between training gains and search gains creates a practical problem for the reader of any RLVR paper. Four principles help.

**Matched test-time compute.** Compare the RL-trained model at pass@1 against the base model with search at the same total FLOP budget. If the RL model gets a single generation while the base model gets 64, the comparison is fair only if the total compute is matched. A base model at pass@64 uses roughly 64x the inference compute of a single pass; the RL model's training cost must also be accounted for, but amortized over all queries it will serve.

**Explicit verifier access.** State whether the verifier used at evaluation is oracle (requires the ground-truth answer) or deployable (works without it). State whether it is the same verifier used during training. A model evaluated with an oracle verifier it was also trained against has a structural advantage that does not transfer to deployment.

**Separation of gains.** Report pass@1 (no search), pass@$N$ (selection), and search-guided results separately. This lets the reader see how much improvement comes from the policy, how much from selection, and how much from active search. A model with high pass@1 and modest pass@$N$ has internalized most of the capability. A model with low pass@1 and high pass@$N$ is leaning on search.

**The Snell et al. framework.** Compute-optimal allocation between inference-time search and training depends on problem difficulty.[@snell2024scaling] On easy problems, the base model's per-sample accuracy is already high and additional search provides diminishing returns — the budget is better spent on training or on harder problems. On hard problems, search is essential and a smaller model plus heavy search can outperform a larger model at pass@1. Difficulty determines the optimal split.

## What verification at inference time sees and misses

The verifier sees whatever it sees in Chapters 2 through 4, amplified by sampling diversity. Multiple samples explore different solution strategies — different algorithms, different edge-case handling, different code structures — increasing the chance that at least one candidate falls in the verifier's checkable core. If the test suite covers the relevant behaviors and any of the 16 candidates implements them correctly, selection will find it.

It misses three things.

First, systematic model biases that all samples share. If the model always makes the same off-by-one error on a particular class of inputs, 64 samples of that error do not help. Selection provides diversity over the model's sampling distribution; it does not repair systematic gaps in that distribution. This is exactly the gap that RL training can close, by shifting the distribution itself.

Second, capabilities that exist in no sample from the current policy. Search cannot find what the policy cannot generate. If the model has never seen a particular algorithm and has zero probability of producing it, no amount of search will discover it. RL, by contrast, can shift probability mass toward novel strategies if they are reinforced by the verifier — though this requires the strategies to appear at least occasionally in rollouts.

Third, the distinction between "the best sample passes the verifier" and "the system reliably solves the task." Best-of-$N$ selection has high variance on small benchmarks. The best candidate might pass all tests, but if you resampled, a different set of 16 candidates might not contain a correct solution. pass@$N$ reports an expected probability, not a guarantee. Selection creates the illusion of capability at the instance level while the underlying policy remains unreliable.

## Open questions

- When is additional search a better investment than additional training, and how should the tradeoff be evaluated across difficulty levels and domains?
- How should inference-time compute budgets scale with problem difficulty, model size, and verifier cost?
- Can learned verifiers be made fast enough for online search — step-level scoring during generation — or are they limited to post-hoc selection over completed outputs?
- How should the field standardize reporting to separate training gains from search gains? Is there a consensus protocol emerging?
- When does inference-time search amplify reward hacking rather than competence? Sampling more candidates increases the chance of finding one that exploits the verifier — a point we return to in Chapter 7.

Selection and search exploit the verifier's signal to improve outputs at inference time. RL exploits the same signal to improve the policy itself. Both assume the signal is trustworthy. Chapter 7 asks what happens when it is not — when the verifier becomes the attack surface and optimization finds ways to satisfy the checker without solving the task.
