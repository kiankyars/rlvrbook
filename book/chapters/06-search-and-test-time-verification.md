# Search and Test Time Verification

![M. C. Escher, _Calanques de Piana_ (1928).](../escher/06-calanques-de-piana.jpg){width="80%" fig-align="center"}

## Chapter Map

- A verifier can improve a system without parameter updates.
- Disambiguating test vs train time compute.

## Test Time

Chapters 2 through 5 treated the verifier as a source of training signal. The model generates rollouts, the verifier scores them, and the optimizer updates parameters. Test time verifier use is split up into the two groups, we'll start with selection:

## Selection

| Technique | Decision rule | Verifier use | Best when | Main limitation |
| --- | --- | --- | --- | --- |
| Best-of-$N$ with an ORM [@cobbe2021training] | Score each completed candidate and return the top one | Post-hoc scoring over full outputs | Cheap parallel reranking is enough | Can only filter samples the policy already produced |
| Best-of-$N$ with a PRM [@lightman2023letsverify] | Rank candidates by process quality rather than just final outcome | Step-level or intermediate scoring folded into a final rank | Harder problems where reasoning quality matters | Higher scoring cost per candidate |
| Self-consistency [@wang2022selfconsistency] | Sample multiple paths and vote or cluster by agreement | No external verifier; agreement acts as the signal | Answers can be canonicalized and consensus is informative | Correlated errors can still dominate |

When a PRM is used to rank complete solutions, the stepwise outputs must be reduced to one solution-level score:

$$
\text{Score}(x, y) = \operatorname{Agg}\bigl(\text{PRM}(s_1 \mid x), \ldots, \text{PRM}(s_K \mid x, s_{<K})\bigr).
$$

Lightman et al. showed why this reduction matters at test time: on the MATH benchmark, PRM-based reranking in a best-of-$N$ setting outperformed ORM-based reranking, with the gap widening as the number of candidates increased.[@lightman2023letsverify]

The remaining design choice is how to collapse step scores into a trajectory score. Math-Shepherd uses the minimum step score when reranking full solutions, reflecting the intuition that one invalid step can sink an otherwise plausible derivation.[@wang2024mathshepherd]

The basic arithmetic behind best-of-$N$ is powerfully simple. Let $p$ be the probability that a single sample is correct; therefore, a single sample is wrong with probability $1 - p$. If we assume sample independence, the probability that all $N$ samples are wrong is the product of those failure probabilities: $(1 - p)^N$. We can write the complement, which is at least one correct sample, as:
$$
1 - (1 - p)^N.
$$ {#eq-ch6-pass-n-idealized}
pass@$N$ sampling helps because repeated draws compound failure probability downward. Even a weak policy with $p = 0.1$ has
$$
1 - 0.9^{10} \approx 0.65
$$
chance of producing at least one correct solution among $N = 10$ samples, and
$$
1 - 0.9^{20} \approx 0.88
$$
among $N = 20$. Real model samples are not truly independent, so the formula is an idealization rather than an exact law, but it captures the core reason best-of-$N$ can buy large gains from modest per-sample competence.

### pass@$k$

Chen et al. defined pass@$k$: the probability that at least one of $k$ samples passes all tests.[@chen2021codex] This metric quantifies how much the reported result depends on the evaluation protocol rather than the model. For example, the original Codex paper reported 28.8% pass@1 on HumanEval but 70.2% pass@100 from sampling alone.[@chen2021codex]

::: {#fig-ch6-pass-at-k}

::: {.content-visible when-format="html"}

```{=html}
<div class="sva-widget" id="sva-widget">
  <div class="sva-controls">
    <div class="sva-slider-row">
      <span class="sva-label">Budget (candidates):</span>
      <input type="range" id="sva-budget" min="0" max="2" step="1" value="2">
      <span id="sva-budget-val" class="sva-label">16</span>
    </div>
  </div>

  <svg class="sva-svg" viewBox="0 0 600 360" aria-label="Search vs Amortization: accuracy as a function of test time compute budget.">
    <line x1="60" y1="20" x2="60" y2="300" stroke="var(--bs-border-color, #aaa)" stroke-width="1"/>
    <line x1="60" y1="300" x2="580" y2="300" stroke="var(--bs-border-color, #aaa)" stroke-width="1"/>

    <text x="30" y="165" text-anchor="middle" transform="rotate(-90,30,165)" fill="var(--bs-body-color, #333)" font-size="12">Accuracy (%)</text>
    <text x="320" y="345" text-anchor="middle" fill="var(--bs-body-color, #333)" font-size="12">Test time budget (candidates)</text>

    <g id="sva-yticks"></g>
    <g id="sva-xticks"></g>

    <polyline id="sva-base-line" fill="none" stroke="#6c757d" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    <polyline id="sva-rl-line" fill="none" stroke="var(--bs-primary, #2c7be5)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>

    <g id="sva-base-dots"></g>
    <g id="sva-rl-dots"></g>

    <text x="445" y="150" fill="#6c757d" font-size="11" font-weight="600">Baseline model</text>
    <text id="sva-rl-label" x="445" y="70" fill="var(--bs-primary, #2c7be5)" font-size="11" font-weight="600">After RLVR</text>
  </svg>

  <div class="sva-summary" id="sva-summary" aria-live="polite"></div>
</div>

<script>
(() => {
  const budgets = [1, 8, 16];
  const baseAcc = [28.9, 53.6, 62.5];
  const rlAcc  = [40.0, 68.0, 70.0];

  const xMin = 60, xMax = 580, yMin = 20, yMax = 300;
  function xPos(i) { return xMin + (i / (budgets.length - 1)) * (xMax - xMin); }
  function yPos(v) { return yMax - ((v - 20) / 60) * (yMax - yMin); }

  function drawTicks() {
    let yt = document.getElementById("sva-yticks"); yt.innerHTML = "";
    for (let v = 20; v <= 80; v += 10) {
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

  function fmt(v) {
    return v.toFixed(1);
  }

  function render(maxIdx) {
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
    document.getElementById("sva-rl-line").setAttribute("points", pts(rlAcc));
    dots(rlAcc, "sva-rl-dots", "var(--bs-primary, #2c7be5)");

    const b = budgets[maxIdx];
    const ba = baseAcc[maxIdx], ra = rlAcc[maxIdx];
    document.getElementById("sva-budget-val").textContent = b;
    let s = "At budget\u00A0=\u00A0" + b + ": baseline " + fmt(ba) + "% (search gain +" +
      fmt(ba - baseAcc[0]) + "), RLVR-trained " + fmt(ra) + "% (search gain +" + fmt(ra - rlAcc[0]) +
      "). Training gain: +" + fmt(rlAcc[0] - baseAcc[0]) + " at pass@1 and +" + fmt(ra - ba) + " at this budget.";
    document.getElementById("sva-summary").textContent = s;
  }

  drawTicks();
  const slider = document.getElementById("sva-budget");
  function update() { render(parseInt(slider.value)); }
  slider.addEventListener("input", update);
  update();
})();
</script>
```
:::

::: {.content-visible when-format="pdf"}

| Budget (candidates) | Baseline model | RLVR-trained model | Training gain |
|:-------------------:|:----------:|:----------------:|:-------------:|
| 1 (pass@1) | 28.9% | 40.0% | +11.1 |
| 8 | 53.6% | 68.0% | +14.4 |
| 16 | 62.5% | 70.0% | +7.5 |

: Exact AIME24 pass@k values for DeepScaleR-1.5B-Preview before and after micro-budget RLVR. Both models improve with more candidates, but the RLVR-trained model starts higher at pass@1 and needs less help from additional search.[@khan2026plasticity]

:::

Exact AIME24 pass@k values for DeepScaleR-1.5B-Preview before and after micro-budget RLVR.[@khan2026plasticity]
:::
  
### Selection under verifier noise

@eq-ch6-pass-n-idealized assumes that the checker is the target property; nevertheless, that may not always be the case, even in RLVR, e.g. a code patch that passes unit tests but silently removes input validation on an endpoint the tests never hit. We will model this discrepancy in this section.

Let $C \in \{0,1\}$ denote true correctness and $V \in \{0,1\}$ denote whether the verifier accepts a sample. If a single rollout has true success probability $p = \Pr(C=1)$, then the following are true:

- Verifier true-positive rate $\beta = \Pr(V=1 \mid C=1)$;
- Verifier false-positive rate $\alpha = \Pr(V=1 \mid C=0)$;
- Then the probability of at least one accepted candidate among $N$ samples is:

The verifier-acceptance equation @eq-ch6-verifier-acceptance answers a narrow question: after sampling $N$ times, what is the chance that the verifier accepts at least one candidate?

$$
\Pr(\exists i : V_i = 1)
= 1 - \bigl(1 - \beta p - \alpha(1-p)\bigr)^N.
$$ {#eq-ch6-verifier-acceptance}

Acceptance and correctness come apart here. The accepted pool contains both true positives and false positives, so the next quantity asks what fraction of the accepted pool is genuinely correct.

This is not the same as the probability that the returned answer is correct. The verifier tail has its own precision:

$$
\Pr(C=1 \mid V=1)
=
\frac{\beta p}{\beta p + \alpha(1-p)}.
$$

The numerator is "correct and accepted." The denominator is "accepted for any reason," including mistakes that slipped through.

When $p$ is small, even a low false-positive rate can dominate the accepted set because most samples are incorrect. This is a base-rate problem: if almost every rollout is wrong, a small leak in the checker can still pollute the accepted tail. For a hard problem with $p=0.05$, $\beta=0.9$, and $\alpha=0.01$, the verifier-accepted tail is only

$$
\frac{0.9 \cdot 0.05}{0.9 \cdot 0.05 + 0.01 \cdot 0.95}
\approx 0.83
$$

correct. If $\alpha$ rises to $0.05$, tail precision drops to

$$
\frac{0.9 \cdot 0.05}{0.9 \cdot 0.05 + 0.05 \cdot 0.95}
\approx 0.49.
$$

Best-of-$N$ therefore depends on the verifier's precision in the selected tail, not merely on its average accuracy. This bridges us to Chapter 7, where we discuss how more search increases both the chance of finding a correct sample and the surface area for finding a false positive that the verifier cannot reject.

### Compute-optimal selection

One question which naturally arises from verification is the exploration/exploitation argument, with exploration corresponding to more generations and exploitation corresponding to more time spent on verification. Snell et al. asked: given a fixed compute budget, how should you split it between generating more candidates and spending more on verification?[@snell2024scaling] Their conclusion is that the optimal allocation depends on problem difficulty. For hard problems where per-sample success is rare, PRM-guided selection can be 4x more efficient than naive best-of-$N$, and a smaller model with more search can match or exceed the performance of a 14x larger model at matched compute.

## Search: verifier as controller

| Technique | Control loop | Verifier use | Best when | Main limitation |
| --- | --- | --- | --- | --- |
| PRM-guided beam search | Expand or prune partial branches online | Score intermediate states during generation | The verifier is fast enough to sit on the inner loop | Latency dominates if scoring is expensive |
| Draft-and-check loops | Generate, test, backtrack, retry | Gate progress with tests, compilation, or checkpoints | Code and agentic tasks allow cheap external checks | Retries can be slow and brittle |
| Tool-gated continuation | Call a tool, inspect the result, revise the next step | Treat tool outputs as live verification signals | Tool use grounds the next action | Behavior depends on tool quality and availability |
| MCTS with exact verification [@trinh2025alphaproof] | Search a tree of actions under verifier feedback | Check each step exactly with a formal system | A deployable step-level verifier exists | Mostly limited to formal domains |

The difference here from selection is that search changes the output distribution, while selection only filters. A model that uses a verifier to prune branches, backtrack, and redirect can explore parts of the solution space that no single forward pass would reach. Search is more powerful, but also more expensive and more sensitive to verifier latency and accuracy.

For this chapter, only deployable test time verification counts. Test suites, proof kernels, live environments, and some learned judges can actually be run by the system at serving time.[@chen2021codex; @liu2023evalplus; @xin2024deepseekprover; @xin2024deepseekproverv15; @trinh2025alphaproof] Benchmark-only answer-key grading in math is useful for measuring proposal quality, but it is not a deployable verifier and should not be confused with real test time capability.[@kydlicek2025mathverify; @shao2024deepseekmath; @deepseekai2025r1]

### Search as controlled verification

Selection can be written as follows: generate complete candidates, score them after generation is over, and return the top one.

$$
y^\star = \arg\max_{y_i \sim \pi_\theta(\cdot \mid x)} v(x,y_i),
\qquad i = 1,\ldots,N,
$$

where the verifier only acts after the model has produced complete candidates. Nothing in this formulation changes the path mid-stream; it only ranks finished products. Search is different because verifier outputs alter the future trajectory. A simple abstraction is a history-dependent controller:

$$
h_t = (x, a_1, o_1, \ldots, a_{t-1}, o_{t-1}), \qquad
a_t \sim \pi_{\mathrm{search}}(\cdot \mid h_t),
$$

Here $h_t$ is just the running record of what the system has tried and what the environment or verifier has said back so far. Observations $o_t$ can include compiler errors, unit-test failures, proof-state feedback, retrieved documents, or learned verifier scores.

Once the verifier sits inside the loop, the objective is no longer "sample $N$ and choose the best." It is closer to "steer a sequence of actions toward high final utility while paying separately for generation and checking":

$$
\max_{\pi_{\mathrm{search}}}
\mathbb{E}\!\left[
U(s_T)
- \lambda_g \sum_{t=1}^{T} c_{\mathrm{gen}}(a_t)
- \lambda_v \sum_{t=1}^{T} c_{\mathrm{verify}}(o_t)
\right],
$$

where $U(s_T)$ is final utility, and the two costs represent generation and verification. This is why verifier latency matters. A verifier that is excellent but slow can be a good post-hoc ranker and a bad inner-loop controller. A cheap noisy verifier can be useful for pruning but dangerous if its errors compound across steps.

## Amortization

If best-of-$N$ plus a test suite is so powerful, why bother with RL at all?

**Latency.** Search requires generating and scoring multiple candidates. An RL-trained model that has internalized the verified patterns produces a similar output in a single forward pass.

**Cost.** At deployment, compute is money. A model that has amortized search gains into its weights serves cheaper per query than one that requires $N$ candidates and $N$ verifier calls.

**Amortized transfer.** Search helps only when the verifier is available. A code model that learned robust patterns from RL on test-suite-verified tasks will generalize, at least partially, to coding tasks where no test suite exists; pure search cannot do this.

**Exploration.** Search over the current policy's sampling distribution can only find solutions the policy can already almost produce. RL reinforces strategies that lead to verified success and suppresses strategies that do not, shifting the model's probability mass toward better solutions.

## Reporting results

A fair model report makes the policy, the verifier, and the test time compute budget legible as separate sources of performance:

**Matched test time compute.** The fairest comparison is the RL-trained model at pass@1 against the base model with search at the same total FLOP budget, amortizing the RL model's training cost over all queries it will serve.

**Explicit verifier access.** State whether the reported result uses a verifier the deployed system could actually run at test time.

**Separation of gains.** Report pass@1 (no search), pass@$N$ (selection), and search-guided results separately. This lets the reader see how much improvement comes from the policy, how much from selection, and how much from active search. A model with high pass@1 and modest pass@$N$ has internalized most of the capability. A model with low pass@1 and high pass@$N$ is leaning on search.

## Open questions

- How should test time compute budgets scale with problem difficulty, model size, and verifier cost?
- Can learned verifiers be made fast enough for online search?
- How should the field standardize reporting to separate training gains from search gains?
- When does test time search amplify reward hacking rather than competence?

## What comes next

Chapter 7 asks what happens when the verifier becomes the attack surface and optimization finds ways to satisfy the checker without solving the task.
