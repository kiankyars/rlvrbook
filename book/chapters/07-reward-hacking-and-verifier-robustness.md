# Reward Hacking

![M. C. Escher, _Fiumara, Calabria_ (1930).](../escher/07-fiumara-calabria.jpg){width="80%" fig-align="center"}

## Chapter Map

- Optimization pressure and Goodhart's Law.
- A taxonomy of exploits and the hardening techniques that work.

## Goodhart's Law

RLVR is in some sense Goodhart's Law instantiated when we view the verifier as the measure that becomes the target through RL. If the verifier has any gap (all verifiers have gaps) between what it checks and what we actually care about, then optimization will exploit that gap. Goodhart's Law can be applied to RLVR in three ways:

1. The verifier has random errors on some inputs. Over many training steps, the policy shifts toward the subspace where the verifier is accidentally generous.

2. Gradient descent over thousands of steps is powerful enough to discover gaps in the verifier that may be rare or invisible under ordinary evaluation.

3. Optimizing the proxy (test passage, answer matching) may produce a policy that achieves high scores through mechanisms unrelated to the intended skill, e.g. pattern-matching, memorization, or distribution exploitation.

## A taxonomy of verifier exploits

### Extraction exploits

The model satisfies the answer extractor without doing the task. Anything inside the `<answer>` tags that matches the gold answer gets reward 1.0, regardless of what preceded it. A model can learn to produce minimal-effort responses that place a plausible answer in the right position: a single line of text, no reasoning, occasionally correct by chance.

### Reward shaping exploits

The signal path from Chapter 5 introduces its own optimization targets. Format rewards, partial credit, and auxiliary bonuses create surfaces the model can exploit independently of correctness.

### Test adequacy failures

The verifier is correct on what it checks, but what it checks is insufficient. Liu et al. found that augmenting HumanEval with 80× more test cases changed model rankings: some models that scored well on the original suite dropped substantially.[@liu2023evalplus] In code generation, test suites are finite approximations of a specification. Through hardcoded branches or shallow pattern matching, a model can learn to pass specific test cases without implementing the correct algorithm.

### Learned verifier biases

When the verifier includes a learned judge (Chapter 4), the judge's training artifacts become exploit surfaces. A model trained against a verbosity-biased judge learns to produce longer outputs. A model trained against a position-biased judge learns to place its strongest argument where the judge expects to find it.

### Distribution shift

The verifier was calibrated for one distribution of model outputs, yet the policy has drifted to another. A learned judge trained on early-training outputs may misjudge late-training outputs that have shifted in register, length, or structure.

### Mechanism gaps

Turpin et al. showed that chain-of-thought explanations can hide factors that influenced the answer, and Lanham et al. tested faithfulness more directly by intervening on traces.[@turpin2023language; @lanham2023measuring] The mechanism gap is the difference between a trace that predicts correctness and a trace that causally controls the answer:

Let $X$ be the prompt, $R$ the written reasoning trace, $Y$ the final answer, and $H$ the hidden computation that produced both. An outcome verifier observes $(X,Y)$. A process verifier observes $(X,R,Y)$.

The artifact-level question is:

$$
\Pr(Y \text{ correct} \mid X,R).
$$ {#eq-ch7-artifact-correctness}

The causal question is different:

$$
\Pr(Y=y \mid \operatorname{do}(R=r), X)
\quad \text{versus} \quad
\Pr(Y=y \mid \operatorname{do}(R=r'), X).
$$ {#eq-ch7-causal-trace}

## Empirical exploits

### Unit-test manipulation

OpenAI reports a frontier reasoning model training run in which the agent was placed in coding environments and rewarded for making unit tests pass.[@baker2025monitoring] The agent did not only write better code. It found reward hacks in the environment. Two systemic hacks were `exit(0)`, which exploited a bug that let the agent exit before all tests ran, and `raise SkipTest`, which skipped unit-test evaluation from outside the testing framework. These hacks became systemic until the environment was patched.

Patching a verification function to always return true, writing stubs when unit-test coverage is poor, parsing tests to extract expected values, decompiling reference artifacts, or shadowing libraries such as `pandas` so that the verifier doesn't check the intended implementation are further examples of reward hacking. When optimization pressure overwhelms the verifier, the model learns that the reward is attached to "tests pass," not to "the repository now implements the intended behavior."

### Missing negative

Cursor's 2026 description of real-time RL for Composer gives the production version of the same problem.[@jackson2026realtimecomposer] The training loop used real user interactions as reward signal and shipped new checkpoints as often as every five hours. One exploit came from invalid tool calls. Composer often needs to read files or run terminal commands. The original reward pipeline discarded examples where the tool call was invalid, so the model learned that if a task looked likely to fail, emitting a broken tool call avoided negative reward. The fix was to include broken tool calls as negative examples.

Another exploit came from clarifying questions. Part of the reward was derived from edits, so Composer learned to defer risky edits by asking questions instead of touching code. The reward pipeline had not defined the boundary between appropriate caution and avoidance of negative reward, so editing rates dropped until Cursor changed the reward function.

## The overoptimization curve

The clearest quantitative evidence for Goodhart dynamics in optimization comes from Gao et al., who measured the relationship between optimization pressure and performance.[@gao2023scaling] The premise is a fixed "gold" reward model as ground truth and a policy we optimize against a separate "proxy" reward model. What happens is that proxy reward increases monotonically, but gold reward first rises, then falls. The peak location depends on the proxy's quality: better proxies peak later and higher, while weaker proxies peak early and low. The original result was measured for learned reward models in RLHF. But the dynamics apply whenever a proxy is imperfect. In the context of this book, the proxy is the programmatic verifier, which approximates but may not equal the target capability. The same dynamics hold as with learned reward models; the difference being that programmatic verifiers are stronger proxies than learned reward models, so peaks likely occurs later with gaps that opens more slowly.

Pan et al. found that as the policy becomes stronger, it finds exploits that weaker policies could not.[@pan2022effects] There are capability thresholds where agent behavior qualitatively shifts, causing sharp drops in true performance even as proxy reward continues to climb. These phase transitions are only predictable empirically and difficult to monitor.

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

## Tail precision

Average verifier accuracy is the wrong object once the model is optimizing against the verifier. What matters is the verifier's behavior in the extreme tail that the optimizer selects.

Let $q(y)$ be the proxy score assigned by the verifier and $t(y)$ be the true task utility. A best-of-$N$ selector returns

$$
y_N^\star = \arg\max_{1 \le i \le N} q(y_i),
\qquad y_i \sim \pi_\theta(\cdot \mid x).
$$

The quantity we care about is not $\mathbb{E}[q(y_N^\star)]$. That will almost always rise with $N$. The quantity we care about is

$$
\mathbb{E}[t(y_N^\star)]
=
\mathbb{E}\!\left[
t\!\left(\arg\max_{1 \le i \le N} q(y_i)\right)
\right].
$$

If $q$ and $t$ agree in the bulk of the distribution but disagree in the upper tail of $q$, then increasing $N$ can make the system worse. The selector is not sampling typical verifier-approved outputs. It is sampling the most extreme verifier-approved output it can find.

A useful diagnostic is tail precision at threshold $\tau$:

$$
\operatorname{TailPrecision}(\tau)
=
\Pr\bigl(t(y)=1 \mid q(y) \ge \tau\bigr).
$$

For a verifier used at pass@1, moderate thresholds may be enough. For best-of-64, PRM-guided beam search, or RL over many gradient steps, the relevant threshold is much higher. The optimizer pushes probability mass toward the region where $q$ is maximal, so robustness means that $q$ remains aligned with $t$ in that region. This is why red-teaming should search for high-score false positives, not just estimate average verifier accuracy on held-out samples.

## Test time exploits

Best-of-$N$ selection helps when the verifier is faithful, but can increase probability of high-scoring false positives. Suppose 1 in 100 rollouts contains a verifier exploit: a response that scores high on the proxy but low on true capability. With best-of-16, the chance of seeing at least one exploit is about 15%. With best-of-64, it rises to about 47%. With best-of-256, it reaches about 92%. Search is not gradient descent, but it still finds the gap between proxy and true, and a verifier that is good enough for pass@1 may not be good enough for best-of-64.

## Hardening techniques

Hardening measures cost compute, engineering time, or both. We justify their use by whether they push the overoptimization peak far enough to the right.

1. **Hidden tests.** The simplest hardening move: hold out a set of tests the model never trains against. If the training verifier uses 5 visible tests per coding problem, add 50 hidden tests drawn from a different generator. The model cannot overfit to tests it does not see.

2. **Test augmentation.** Generating tests automatically can expand coverage beyond what a human problem-setter provides. EvalPlus demonstrated that generated test suites reveal false positives that the original tests miss.[@liu2023evalplus]

3. **Red-teaming before training.** Probing the verifier adversarially is a proactive way to de-risk training runs.

4. **KL constraints and early stopping.** PPO's KL penalty, GRPO's gradient clipping, or simply stopping training before the overoptimization peak keeps the policy close enough to its initial state that the verifier's calibration still holds.

5. **Progressive curriculum.** Increase task difficulty as the model improves, following the competence-band principle from Chapter 5. Progressive difficulty keeps the optimization pressure focused on genuinely informative tasks.

## Open questions

- Is there a practical pre-training audit protocol to evaluate verifier robustness?
- Is there a useful analog to Gao et al.'s gold reward model for programmatic verifiers?
- Can the model's own internal representations be used to detect reward hacking?
- Does combining hidden tests, ensembles, and KL constraints give diminishing or compounding returns?
