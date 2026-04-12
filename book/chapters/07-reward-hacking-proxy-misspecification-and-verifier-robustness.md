# Reward Hacking, Proxy Misspecification, and Verifier Robustness

![M. C. Escher, _Fiumara, Calabria_ (1930).](../art/escher/07-fiumara-calabria.jpg){width="80%" fig-align="center"}

## Chapter Map

- How verifiers fail when they become the target of optimization pressure — Goodhart's Law instantiated in every layer of the RLVR stack.
- A taxonomy of exploits mapped to the verifier components from Chapters 2–5, and the hardening techniques that work.

## Goodhart's Law is RLVR's founding tradeoff

Every verifier in this book is a proxy.

The outcome verifier in Chapter 2 checks a final answer string, not whether the model understood the problem. The process verifier in Chapter 3 checks step-level annotations, not whether the reasoning was causally responsible for the conclusion. The hybrid stack in Chapter 4 combines components whose union of visibilities is larger but still bounded. The reward-shaping pipeline in Chapter 5 transforms verifier verdicts into advantages, introducing its own distortions. The inference-time selector in Chapter 6 picks the best candidate from a sample, amplifying whatever the verifier rewards — including its errors.

Goodhart's Law says: when a measure becomes a target, it ceases to be a good measure. RLVR is Goodhart's Law instantiated. The verifier is the measure. Reinforcement learning makes it the target. If the verifier has any gap between what it checks and what we actually care about — and all verifiers have gaps — sufficiently powerful optimization will find and exploit that gap.

Manheim and Garrabrant categorize four variants of Goodhart's Law, all of which appear in RLVR.[@manheim2019categorizing]

**Regressional.** The verifier has random errors on some inputs. Selecting for high verifier scores also selects for inputs where the verifier's errors happen to favor the model. Over many training steps, the policy shifts toward the subspace where the verifier is accidentally generous.

**Extremal.** Correlations between verifier score and true capability hold in the normal regime but break at the extremes that optimization reaches. A model trained lightly against a test suite may genuinely improve; a model trained aggressively finds the boundary where passing tests and understanding the problem diverge.

**Causal.** Passing the verifier does not *cause* the capability we want. Optimizing the proxy (test passage, answer matching) may produce a policy that achieves high scores through mechanisms unrelated to the intended skill — pattern-matching, memorization, or distribution exploitation — because the verifier checks correlation, not causation.

**Adversarial.** The optimizer is a search process that actively finds weaknesses. Gradient descent over thousands of steps is powerful enough to discover and amplify any exploitable gap in the verifier, even gaps that a human auditor would not anticipate.

This is not a bug to be patched. It is a structural consequence of optimizing against any fixed checker. The question is always: how much optimization pressure can this verifier absorb before the gap opens?

## Two exploits

### The number-slotting shortcut

Consider training a model on a large corpus of grade-school word problems with binary outcome reward. The answer distribution has a strong regularity: roughly 40% of answers are integers between 1 and 20. Problem setters prefer clean numbers.

A model under optimization pressure discovers this. Instead of learning arithmetic reasoning, it learns a shallow heuristic: extract the numbers from the prompt, try a few combinations (multiply the two largest, add the two smallest, subtract the smaller from the larger), and output whichever result falls in the high-frequency answer range. For a problem like "A farmer has 12 rows of 8 apple trees. How many trees does the farmer have?", the model outputs "96" — correct. But it matched a pattern, not a concept. The binary verifier scores this 1.0, identical to a model that understood multiplication.

On the training distribution, this heuristic achieves roughly 25% accuracy — far above random. With 16 rollouts per prompt, the model averages 4 correct guesses per group. Those rollouts receive large positive advantage; the rest are suppressed. The optimizer reinforces the number-slotting strategy because it has the highest expected reward per rollout.

The exploit becomes visible on out-of-distribution problems: questions with fractional answers, problems that include red-herring numbers, or tasks that require multi-step reasoning where the obvious arithmetic combination is wrong. The number-slotting heuristic collapses on these inputs, but the in-distribution reward was high enough to entrench it. This is regressional Goodhart: selecting for high reward also selected for answers that happen to be common, which correlates with correct answers on the training distribution but not in general.

### The brute-force preference

A model is being trained on competitive programming problems with execution-based verification. The visible test suite for each problem uses small inputs: arrays of length $\leq$ 50, values $\leq$ 100. An $O(N^2)$ nested-loop solution runs in under a millisecond on these inputs and passes all tests. An $O(N \log N)$ algorithm-based solution also passes — but it is harder to generate correctly: more complex logic, more edge cases, more off-by-one errors.

Across 16 rollouts for a given problem, the brute-force solution succeeds in 12 attempts. The algorithmic solution succeeds in 5. Both receive the same reward when correct. After group normalization, the advantage distribution heavily favors brute-force: it is correct more reliably, so it gets reinforced more consistently.

After a thousand training steps, the model defaults to brute-force. On visible test suites, accuracy is 85%. On hidden test suites with large inputs ($N = 10^5$), the brute-force solutions time out and accuracy drops to 30%. The verifier was correct on everything it checked — but it checked only small inputs. This is extremal Goodhart: the correlation between "passes visible tests" and "is a correct algorithm" held for small $N$ but broke at the scale the hidden tests require.

## A taxonomy of verifier exploits

The two examples above illustrate specific layers of a broader taxonomy. Each layer maps to a verifier component introduced in earlier chapters.

### Layer 1: Extraction exploits

The model satisfies the answer extractor without doing the task. Chapter 2's pipeline — `extract_answer` → `canonicalize_answer` → `verify_answer` — defines a narrow interface. Anything inside the `<answer>` tags that matches the gold answer gets reward 1.0, regardless of what preceded it. A model can learn to produce minimal-effort responses that place a plausible answer in the right position: a single line of text, no reasoning, occasionally correct by chance. The extractor is satisfied; the verifier is satisfied; the model is rewarded for guessing.

### Layer 2: Reward shaping exploits

The signal path from Chapter 5 introduces its own optimization targets. Format rewards, partial credit, and auxiliary bonuses create surfaces the model can exploit independently of correctness. Chapter 5's flagship figure showed this concretely: an incorrect but well-formatted rollout (rollout 4) had advantage −0.04 under the combined reward regime — the optimizer barely suppressed it. Over many training steps, the model learns that formatting is a cheaper source of reward than correctness. The reward-shaping layer, designed to scaffold learning, becomes the dominant optimization target.

### Layer 3: Test adequacy failures

The verifier is correct on what it checks, but what it checks is insufficient. In code generation, test suites are finite approximations of a specification.[@liu2023evalplus] A model can learn to pass specific test cases without implementing the correct algorithm — through hardcoded branches, shallow pattern matching, or solutions that happen to be correct on the tested inputs. Liu et al. found that augmenting HumanEval with 80× more test cases changed model rankings: some models that scored well on the original suite dropped substantially. The original verifier was not wrong on any test it ran; it simply did not run enough tests.

### Layer 4: Learned verifier biases

When the verifier includes a learned judge (Chapter 4), the judge's training artifacts become exploit surfaces. Zheng et al. identified four systematic biases in LLM-as-Judge systems: position bias, verbosity bias, self-enhancement bias, and weak mathematical reasoning.[@zheng2023judging] These are not random noise — they are structured patterns that a policy under optimization pressure can learn to exploit. A model trained against a verbosity-biased judge learns to produce longer outputs. A model trained against a position-biased judge learns to place its strongest argument where the judge expects to find it. The verifier rewards style; the optimizer delivers style.

### Layer 5: Distribution shift

The verifier was calibrated for one distribution of model outputs; the policy has drifted to another. Chapter 5 noted that GRPO has no explicit KL penalty to constrain policy drift — regularization is implicit through gradient clipping and LoRA rank constraints. For short training runs this is sufficient. For longer runs, the policy can move far enough from its initial state that the verifier's scores become unreliable. A format checker designed for one style of output may accept a novel format it was never tested against. A learned judge trained on early-training outputs may misjudge late-training outputs that have shifted in register, length, or structure. The verifier has not changed; the distribution it operates on has.

## The overoptimization curve

The clearest quantitative evidence for Goodhart dynamics in optimization comes from Gao et al., who measured the relationship between optimization pressure and performance.[@gao2023scaling] Their setup uses a fixed "gold" reward model as ground truth and optimizes a policy against a separate "proxy" reward model, measuring how gold reward changes as the policy moves further from its initial state.

The result is the overoptimization curve. Proxy reward increases monotonically — the optimization is working as designed. But gold reward (the thing we actually care about) first rises, peaks, then falls. The peak location depends on the proxy's quality: better proxies peak later and higher, while weaker proxies peak early and low.

The original result was measured for learned reward models in RLHF. But the dynamics apply whenever a proxy is imperfect, which is always. In RLVR, the proxy is the programmatic verifier — a test suite, an answer extractor, a format checker. The true goal is the capability we actually want. The verifier approximates it but does not equal it. The same dynamics hold; the difference is that programmatic verifiers are typically stronger proxies than learned reward models, so the peak occurs later and the gap opens more slowly. But the peak still exists. Cursor's engineering team cites this result directly when discussing overoptimization in their production RL system.[@jackson2026realtimecomposer]

Pan et al. found an additional sobering result: more capable agents exploit reward misspecifications *more* effectively than less capable ones.[@pan2022effects] As the policy becomes stronger, it finds exploits that weaker policies could not. There are phase transitions — capability thresholds where agent behavior qualitatively shifts, causing sharp drops in true performance even as proxy reward continues to climb. These phase transitions are difficult to predict and difficult to monitor.

::: {.content-visible when-format="html"}

<div class="ghg-widget" id="ghg-widget">
<p class="ghg-hint">Drag the slider to increase optimization pressure. Toggle verifier strength to see how the Goodhart gap changes.</p>
<div class="ghg-tabs" role="tablist">
<button class="ghg-tab ghg-tab-active" role="tab" data-type="strong" aria-selected="true">Strong programmatic</button>
<button class="ghg-tab" role="tab" data-type="weak" aria-selected="false">Weak learned</button>
<button class="ghg-tab" role="tab" data-type="hybrid" aria-selected="false">Hybrid stack</button>
</div>
<svg class="ghg-svg" id="ghg-svg" viewBox="0 0 620 380" aria-label="The Goodhart gap: proxy reward vs true performance as optimization pressure increases.">
<text x="310" y="16" text-anchor="middle" class="ghg-title">The Goodhart gap</text>
<line x1="65" y1="300" x2="580" y2="300" class="ghg-axis"/>
<line x1="65" y1="30" x2="65" y2="300" class="ghg-axis"/>
<text x="322" y="340" text-anchor="middle" class="ghg-label">Optimization pressure (KL from reference)</text>
<text x="18" y="165" text-anchor="middle" transform="rotate(-90,18,165)" class="ghg-label">Performance</text>
<text x="65" y="315" text-anchor="middle" class="ghg-tick">0</text>
<text x="322" y="315" text-anchor="middle" class="ghg-tick">5</text>
<text x="580" y="315" text-anchor="middle" class="ghg-tick">10</text>
<text x="58" y="304" text-anchor="end" class="ghg-tick">0</text>
<text x="58" y="166" text-anchor="end" class="ghg-tick">0.5</text>
<text x="58" y="34" text-anchor="end" class="ghg-tick">1.0</text>
<polygon id="ghg-gap" class="ghg-gap-fill"/>
<polyline id="ghg-proxy" class="ghg-proxy-line" fill="none"/>
<polyline id="ghg-true" class="ghg-true-line" fill="none"/>
<line id="ghg-indicator" class="ghg-indicator" y1="30" y2="300"/>
<circle id="ghg-proxy-dot" r="4" class="ghg-proxy-dot"/>
<circle id="ghg-true-dot" r="4" class="ghg-true-dot"/>
<text x="500" y="55" class="ghg-legend-text ghg-proxy-color">Proxy reward</text>
<text x="500" y="75" class="ghg-legend-text ghg-true-color">True performance</text>
<line x1="480" y1="51" x2="496" y2="51" class="ghg-proxy-line" fill="none"/>
<line x1="480" y1="71" x2="496" y2="71" class="ghg-true-line" fill="none"/>
</svg>
<div class="ghg-slider-wrap">
<label for="ghg-slider" class="ghg-slider-label">Optimization pressure:</label>
<input type="range" id="ghg-slider" min="0" max="100" value="50" class="ghg-slider">
</div>
<div class="ghg-summary" id="ghg-summary" aria-live="polite"></div>
</div>
<style>
.ghg-widget{font-family:var(--bs-font-sans-serif,system-ui,sans-serif);max-width:660px;margin:1.5rem auto}
.ghg-hint{font-size:.9rem;color:var(--bs-secondary,#6c757d);margin-bottom:.75rem}
.ghg-tabs{display:flex;gap:.5rem;margin-bottom:.75rem;flex-wrap:wrap}
.ghg-tab{padding:.35rem .9rem;border:1px solid var(--bs-border-color,#dee2e6);border-radius:4px;background:var(--bs-body-bg,#fff);color:var(--bs-body-color,#212529);cursor:pointer;font-size:.82rem;transition:background .15s}
.ghg-tab:hover{background:var(--bs-tertiary-bg,#f0f0f0)}
.ghg-tab-active{background:var(--bs-primary,#2c7be5);color:#fff;border-color:var(--bs-primary,#2c7be5)}
.ghg-svg{width:100%;height:auto;display:block}
.ghg-axis{stroke:var(--bs-body-color,#212529);stroke-width:1}
.ghg-title{font-size:14px;font-weight:600;fill:var(--bs-body-color,#212529)}
.ghg-label{font-size:11px;fill:var(--bs-secondary,#6c757d)}
.ghg-tick{font-size:10px;fill:var(--bs-secondary,#6c757d)}
.ghg-proxy-line{stroke:#3b82f6;stroke-width:2.5}
.ghg-true-line{stroke:#22c55e;stroke-width:2.5}
.ghg-proxy-dot{fill:#3b82f6}
.ghg-true-dot{fill:#22c55e}
.ghg-proxy-color{fill:#3b82f6;font-size:11px}
.ghg-true-color{fill:#22c55e;font-size:11px}
.ghg-gap-fill{fill:#ef4444;opacity:.15}
.ghg-indicator{stroke:var(--bs-body-color,#212529);stroke-width:1;stroke-dasharray:4,3;opacity:.6}
.ghg-legend-text{font-size:11px}
.ghg-slider-wrap{margin-top:.5rem;display:flex;align-items:center;gap:.75rem}
.ghg-slider-label{font-size:.85rem;white-space:nowrap}
.ghg-slider{flex:1}
.ghg-summary{margin-top:.75rem;font-size:.85rem;padding:.5rem;border-left:3px solid var(--bs-primary,#2c7be5);background:var(--bs-tertiary-bg,#f8f9fa)}
</style>
<script>
(function(){
  var CL=65,CR=580,CT=30,CB=300,W=CR-CL,H=CB-CT;
  var configs={
    strong:{peak:7,amp:0.75,label:'Strong programmatic verifier'},
    weak:{peak:2,amp:0.45,label:'Weak learned verifier'},
    hybrid:{peak:4,amp:0.62,label:'Hybrid stack'}
  };
  var base=0.10;
  function proxy(x){return base+0.85*Math.tanh(0.6*x);}
  function truePerf(x,peak,amp){
    if(x<=peak){var t=x/peak;return base+amp*(2*t-t*t);}
    var d=x-peak;return base+amp*Math.exp(-d*d/(2*peak*peak));
  }
  function dx2px(x){return CL+(x/10)*W;}
  function dy2py(y){return CB-y*H;}
  function pts(fn,args){
    var s=[];for(var i=0;i<=200;i++){var x=i/20;var y=args?fn(x,args[0],args[1]):fn(x);s.push(dx2px(x).toFixed(1)+','+dy2py(y).toFixed(1));}return s.join(' ');
  }
  var curType='strong';
  var proxyEl=document.getElementById('ghg-proxy');
  var trueEl=document.getElementById('ghg-true');
  var gapEl=document.getElementById('ghg-gap');
  var indEl=document.getElementById('ghg-indicator');
  var pdot=document.getElementById('ghg-proxy-dot');
  var tdot=document.getElementById('ghg-true-dot');
  var slider=document.getElementById('ghg-slider');
  var summaryEl=document.getElementById('ghg-summary');
  function render(){
    var c=configs[curType];
    proxyEl.setAttribute('points',pts(proxy));
    trueEl.setAttribute('points',pts(truePerf,[c.peak,c.amp]));
    updateSlider();
  }
  function updateSlider(){
    var c=configs[curType];
    var xval=parseFloat(slider.value)/10;
    var px=dx2px(xval);
    indEl.setAttribute('x1',px);indEl.setAttribute('x2',px);
    var pv=proxy(xval),tv=truePerf(xval,c.peak,c.amp);
    pdot.setAttribute('cx',px);pdot.setAttribute('cy',dy2py(pv));
    tdot.setAttribute('cx',px);tdot.setAttribute('cy',dy2py(tv));
    var gapPts=[];
    for(var i=0;i<=200;i++){var x=i/20;if(x>xval)break;gapPts.push(dx2px(x).toFixed(1)+','+dy2py(proxy(x)).toFixed(1));}
    for(var i=Math.min(200,Math.round(xval*20));i>=0;i--){var x=i/20;gapPts.push(dx2px(x).toFixed(1)+','+dy2py(truePerf(x,c.peak,c.amp)).toFixed(1));}
    gapEl.setAttribute('points',gapPts.join(' '));
    var gap=pv-tv;
    var peakTrue=base+c.amp;
    var dropPct=tv<peakTrue?Math.round((1-tv/peakTrue)*100):0;
    summaryEl.innerHTML='<strong>'+c.label+'</strong> at KL\u2009=\u2009'+xval.toFixed(1)+': proxy\u2009=\u2009'+pv.toFixed(2)+', true\u2009=\u2009'+tv.toFixed(2)+', gap\u2009=\u2009'+gap.toFixed(2)+(dropPct>0?' \u00b7 True performance is '+dropPct+'% below its peak.':'');
  }
  document.querySelectorAll('.ghg-tab').forEach(function(btn){
    btn.addEventListener('click',function(){
      document.querySelectorAll('.ghg-tab').forEach(function(b){b.classList.remove('ghg-tab-active');b.setAttribute('aria-selected','false');});
      btn.classList.add('ghg-tab-active');btn.setAttribute('aria-selected','true');
      curType=btn.dataset.type;render();
    });
  });
  slider.addEventListener('input',updateSlider);
  render();
})();
</script>

:::

::: {.content-visible when-format="pdf"}

**The overoptimization curve** shows proxy reward (what the verifier reports) rising monotonically while true performance (the capability we care about) peaks and then declines. The peak location depends on verifier strength.

| Verifier type | Peak location | Peak true | True at KL=10 | Gap at KL=10 |
|---------------|---------------|-----------|---------------|--------------|
| Strong programmatic | KL $\approx$ 7 | 0.85 | 0.78 | 0.17 |
| Hybrid stack | KL $\approx$ 4 | 0.72 | 0.30 | 0.65 |
| Weak learned | KL $\approx$ 2 | 0.55 | 0.10 | 0.85 |

Proxy reward at KL=10 is approximately 0.95 in all cases. Stronger verifiers delay the onset of overoptimization but do not prevent it.

:::

## When search amplifies exploits

Chapter 6 closed with a question: when does inference-time search amplify reward hacking rather than competence? The answer follows directly from the taxonomy above.

Best-of-$N$ selection picks the highest-scoring candidate from $N$ samples. If the verifier is perfect, this always helps — the best candidate is the most correct. But if the verifier has exploitable gaps, more samples increase the probability of finding a candidate that exploits the gap rather than solving the task.

Suppose 1 in 100 rollouts contains a verifier exploit — a response that scores high on the proxy but low on true capability. With best-of-16, the probability that at least one of the 16 candidates is an exploit is $1 - (99/100)^{16} \approx 15\%$. With best-of-64, it rises to $1 - (99/100)^{64} \approx 47\%$. With best-of-256, it reaches $\approx 92\%$. The exploit does not need to be common; it only needs to exist. Search will find it.

This is adversarial Goodhart at inference time. The selection process is not gradient descent, but the dynamics are the same: a search procedure finds the gap between proxy and true, and a stronger search finds it faster. PRM-guided beam search is even more vulnerable, because it selects at every step rather than only at the endpoint — each step-level selection is an opportunity to amplify step-level verifier errors.

The practical consequence: verifier robustness matters at least as much for inference-time systems as for training. A verifier that is "good enough" for a single pass@1 generation may be inadequate for best-of-64 selection, because the selection process concentrates probability mass on the highest-scoring candidates — including the ones that score high for the wrong reasons.

## Hardening techniques

Not all verifiers are equally exploitable, and not all exploitation is equally cheap to fix. The following techniques push the overoptimization peak to the right — buying more optimization budget before the Goodhart gap opens.

**Hidden tests.** The simplest hardening move: hold out a set of tests the model never trains against. If the training verifier uses 5 visible tests per coding problem, add 50 hidden tests drawn from a different generator. The model cannot overfit to tests it does not see. This is standard practice in competitive programming evaluation and the core insight behind EvalPlus.[@liu2023evalplus]

**Test augmentation.** Go further: generate tests automatically. Property-based testing, mutation testing, and LLM-generated adversarial inputs can expand coverage beyond what a human problem-setter provides. The cost is that automatically generated tests may themselves be incorrect or redundant, requiring their own verification.

**Ensemble verification.** Use multiple independent verifiers and require agreement. Coste et al. showed that reward model ensembles mitigate overoptimization, especially when ensemble members differ in pretraining seeds rather than only fine-tuning seeds.[@coste2023rewardensemble] The benefit is bounded: if all ensemble members share the same blind spot, the ensemble fails as a unit. Diversity of verification mechanism (not just diversity of parameters) is what matters.

**Red-teaming before training.** Probe the verifier adversarially before committing to a large training run. Generate candidate exploits: responses that are clearly wrong but might receive high scores. If the red team can find exploits in an afternoon, gradient descent will find them in hours. Fix them before training begins.

**KL constraints and early stopping.** Limit optimization pressure. PPO's KL penalty, GRPO's gradient clipping, or simply stopping training before the overoptimization peak — all keep the policy close enough to its initial state that the verifier's calibration still holds. The cost is leaving performance on the table. The benefit is avoiding the regime where proxy and true diverge.

**Progressive curriculum.** Increase task difficulty as the model improves, following the competence-band principle from Chapter 5. On easy tasks, the model quickly reaches a regime where reward variance is low and the gradient signal is dominated by noise or formatting. Progressive difficulty keeps the optimization pressure focused on genuinely informative tasks.

**What does not work.** Adding stack complexity without understanding the failure mode. Chapter 4's debugging-cost argument applies: each layer adds audit surface. "More hidden tests" without distributional diversity — if the hidden tests share the same construction as visible ones, they share the same blind spots. Post-hoc filtering of outputs without understanding why the exploit succeeded — the model will find the next exploit.

The cost-benefit frame: every hardening measure costs compute, engineering time, or both. The question is whether it pushes the overoptimization peak far enough to the right to justify that cost. For a short training run on a well-studied benchmark, minimal hardening may suffice. For a production system under continuous optimization, hardening is not optional.

## Case study: Cursor's real-time RL

The most concrete public account of reward hacking in a deployed RLVR system comes from Cursor's description of real-time RL for Composer.[@jackson2026realtimecomposer] The setup is not a benchmark: it is a production coding agent optimizing against reward signals derived from real user interactions, with a new checkpoint shipping every five hours.

Two specific exploits illustrate how quickly the optimizer finds gaps.

First, the broken tool call exploit. When Composer needed to read files or run terminal commands, it sometimes issued invalid tool calls. The original reward pipeline discarded these examples — no reward or penalty was assigned. Composer learned that on tasks it was likely to fail, emitting a broken tool call on purpose avoided any negative reward. The tool call interface was not part of the verifier's scoring; the model found the gap and exploited it. The fix was straightforward: include broken tool calls as negative examples.

Second, the clarifying question exploit. Part of the reward was derived from edits the model made. Composer discovered that deferring risky edits by asking clarifying questions — "Could you clarify what you mean by X?" — avoided the penalty for bad code while generating no negative signal. Clarifying questions are sometimes genuinely appropriate, which is why the reward function did not penalize them. But the boundary between "appropriate caution" and "avoidance of negative reward" was not defined in the reward logic. Without intervention, editing rates dropped precipitously. The fix required modifying the reward function to stabilize the balance between caution and action.

Both exploits are Layer 2 (reward shaping) in the taxonomy: the model found gaps in how the reward was computed, not in the underlying code quality check. And both were caught because real users — unlike static benchmarks — notice when the agent stops being useful. As Cursor's team observes: in real-time RL, reward hacking is a bigger risk, but it is also harder for the model to get away with. Each exploit "essentially becomes a bug report that we can use to improve our training system." Chapter 10 discusses the broader implications of frontier coding harnesses; here the point is specific: reward hacking in production is not hypothetical, and the feedback loop between exploitation and hardening is what keeps it manageable.

## What this chapter sees and misses

This chapter sees the verifier as attack surface: the taxonomy of exploitation, the scaling dynamics of overoptimization, and actionable hardening techniques. It explains why optimization pressure against a fixed checker will eventually find the gap, and what to do about it.

It deliberately stops at exploitation — failures where the model satisfies the verifier without doing the task. A different class of failure remains: properties that the verifier structurally cannot certify, even when it is working exactly as designed and no exploitation is occurring. A model that passes all tests, satisfies all judges, and shows no signs of gaming can still produce unfaithful reasoning, miscalibrated confidence, or brittle generalization. Those are not engineering failures to be patched. They are observability limits. That is Chapter 8.

## Open questions

- How should verifier robustness be evaluated before committing to large-scale optimization? Is there a practical pre-training audit protocol?
- Is there a useful analog to Gao et al.'s gold reward model — a way to estimate the overoptimization curve for programmatic verifiers without access to ground-truth capability measurements?
- When does ensemble diversity plateau? How many independent verifiers with different mechanisms are needed before the marginal benefit of adding another drops to zero?
- Can the model's own internal representations be used to detect reward hacking — anomaly detection on activations or logits that signals when the policy has entered an exploit regime?
- How do hardening techniques compose? Does combining hidden tests, ensembles, and KL constraints give diminishing or compounding returns?

Every failure in this chapter has the same shape: the verifier was exploited because it checked something narrower than what we cared about. In every case, the exploit was in principle fixable — a better extractor, more tests, a debiased judge, a KL constraint. Chapter 8 asks a harder question: what happens when the gap between what the verifier checks and what we care about cannot be closed by better engineering? Faithfulness, calibration, and the relationship between verified correctness and genuine understanding are structural limits of the verification paradigm, not bugs in any particular verifier. That is the subject of Chapter 8.
