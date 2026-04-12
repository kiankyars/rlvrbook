# Turning Checks into Training Signal

![M. C. Escher, _The Drowned Cathedral_ (1929).](../art/escher/05-the-drowned-cathedral.jpg){width="80%" fig-align="center"}

## Chapter Map

- A complete outcome-RLVR training loop, annotated line by line, to show how verifier verdicts become parameter updates.
- The design space around that loop: reward shaping, task filtering, rollout budget, and baseline design — the decisions that determine whether a strong verifier produces a strong training signal.

## A compact outcome-RLVR training script

The shortest path from verifier to parameter update is a single script. [Will Brown's](https://x.com/willccbb/status/1886788410351796232) GRPO implementation trains a 1.5B-parameter model on grade school math with nothing but string-matching reward functions and a group-relative optimizer.[^ch5-brown-grpo-150line] It is one instantiation of a larger design space — the choices it makes about reward structure, task selection, rollout count, and baseline design are examined in the sections that follow.

The script contains five components:

- A task source: prompts and target data.
- A response contract: response format and extraction rules.
- A reward bank: correctness and quality terms over extracted artifacts.
- A signal policy: filtering, clipping, scaling, and schedule decisions.
- A trainer configuration: rollout counts, clipping, entropy terms, and optimization settings.

```py
import re
import torch
from datasets import load_dataset, Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig
from trl import GRPOConfig, GRPOTrainer
```

::: {.column-margin}
Importing the relevant packages, including Hugging Face Transformer Reinforcement Learning, Transformers and parameter efficient fine tuning.
:::

```py
SYSTEM_PROMPT = """
Respond in the following format:

<reasoning>
...
</reasoning>
<answer>
...
</answer>
"""

XML_COT_FORMAT = """\
<reasoning>
{reasoning}
</reasoning>
<answer>
{answer}
</answer>
"""
```

::: {.column-margin}
System prompt and XML (for downstream format rewards) with templating.
:::

```py
def extract_xml_answer(text: str) -> str:
    answer = text.split("<answer>")[-1]
    answer = answer.split("</answer>")[0]
    return answer.strip()

def extract_hash_answer(text: str) -> str | None:
    if "####" not in text:
        return None
    return text.split("####")[1].strip().replace(",", "").replace("$", "")
```

::: {.column-margin}
The above functions:
1. Extract XML from the above XML COT format
2. Extract the text suceeding `####`
:::


```py
def get_gsm8k_questions(split = "train") -> Dataset:
    data = load_dataset('openai/gsm8k', 'main')[split] # type: ignore
    data = data.map(lambda x: {
        'prompt': [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': x['question']}
        ],
        'answer': extract_hash_answer(x['answer'])
    }) # type: ignore
    return data # type: ignore

dataset = get_gsm8k_questions()
```
::: {.column-margin}
A lambda function to load our Grade School Math 8K (GSM8K, a benchmark of math word problems for grade school arithmetic) dataset into the corresponding question and answer fields on the train split of the dataset, along with the system prompt. Note for later this chapter that we do no filtering, competence-band selection, or curriculum.
:::

```py
def correctness_reward_func(prompts, completions, answer, **kwargs) -> list[float]:
    responses = [completion[0]['content'] for completion in completions]
    extracted_responses = [extract_xml_answer(r) for r in responses]
    return [2.0 if r == a else 0.0 for r, a in zip(extracted_responses, answer)]

def int_reward_func(completions, **kwargs) -> list[float]:
    responses = [completion[0]['content'] for completion in completions]
    extracted_responses = [extract_xml_answer(r) for r in responses]
    return [0.5 if r.isdigit() else 0.0 for r in extracted_responses]
```
::: {.column-margin}
`correctness_reward_func` checks whether the language model gets the correct answer, using the Extract XML answer function. Notice the function checks for exact matching, whereas `int_reward_func` checks: is there a digit in the answer? Both of these are binary outcome rewards, and rewarding `2.0` versus `0.5` is a reward design choice.
:::

```py
def strict_format_reward_func(completions, **kwargs) -> list[float]:
    pattern = r"^<reasoning>\n.*?\n</reasoning>\n<answer>\n.*?\n</answer>\n$"
    responses = [completion[0]["content"] for completion in completions]
    matches = [re.match(pattern, r, flags=re.DOTALL) for r in responses]
    return [0.5 if match else 0.0 for match in matches]

def soft_format_reward_func(completions, **kwargs) -> list[float]:
    pattern = r"<reasoning>.*?</reasoning>\s*<answer>.*?</answer>"
    responses = [completion[0]["content"] for completion in completions]
    matches = [re.match(pattern, r, flags=re.DOTALL) for r in responses]
    return [0.5 if match else 0.0 for match in matches]
```
::: {.column-margin}
These reward functions are simply concerned with the formatting, which is to say, did the models use the reasoning and answer tags correctly? There is both a strict and a soft format function. The strict function uses the caret sign `^` at the beginning of the pattern, enforcing that the string begins with the reasoning tag. Furthermore, the strict function demands `\n`s in between the tags. Finally, we have the anchor tag `$` at the end of the strict reward function regex matching pattern, which means that there should be nothing after the final answer tag.
:::

```py
def count_xml(text) -> float:
    count = 0.0
    if text.count("<reasoning>\n") == 1:
        count += 0.125
    if text.count("\n</reasoning>\n") == 1:
        count += 0.125
    if text.count("\n<answer>\n") == 1:
        count += 0.125
        count -= len(text.split("\n</answer>\n")[-1]) * 0.001
    if text.count("\n</answer>") == 1:
        count += 0.125
        count -= (len(text.split("\n</answer>")[-1]) - 1) * 0.001
    return count

def xmlcount_reward_func(completions, **kwargs) -> list[float]:
    contents = [completion[0]["content"] for completion in completions]
    return [count_xml(c) for c in contents]
```
::: {.column-margin}
Counts over reasoning and answer tags within the response. The only nuance here is the subtraction statement in both of the answer conditional statements, which gives a negative reward for however many tokens occur after the last answer tag. As an aside, one must be careful with the reward for auxiliary contract rewards, because they can dominate and distract from correctness.
:::

```py
model_name = "Qwen/Qwen2.5-1.5B-Instruct"
output_dir = "outputs/Qwen-1.5B-GRPO"
run_name = "Qwen-1.5B-GRPO-gsm8k"

training_args = GRPOConfig(
    output_dir=output_dir,
    run_name=run_name,
    learning_rate=5e-6,
    adam_beta1 = 0.9,
    adam_beta2 = 0.99,
    weight_decay = 0.1,
    warmup_ratio = 0.1,
    lr_scheduler_type='cosine',
    logging_steps=1,
    bf16=True,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    num_generations=16,
    max_prompt_length=256,
    max_completion_length=786,
    num_train_epochs=1,
    save_steps=100,
    max_grad_norm=0.1,
    report_to="wandb",
    log_on_each_node=False,
)

peft_config = LoraConfig(
    r=16,
    lora_alpha=64,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "up_proj", "down_proj", "gate_proj"],
    task_type="CAUSAL_LM",
    lora_dropout=0.05,
)
```
::: {.column-margin}
LLM selection and configurtion of the GRPO optimizer with the applicable learning rate, weight decay, data formats, etc., as well as our Lora config, which is the adapter trained on top of the language model. For this chapter, the most important choices are `num_generations=16`, which sets the rollout budget and therefore the variance-compute tradeoff, the group-relative normalization built into `GRPOConfig`, and conservative settings such as `max_grad_norm=0.1`, which help control policy drift once reward becomes update.
:::

```py
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
    device_map=None
).to("cuda")

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

trainer = GRPOTrainer(
    model=model,
    processing_class=tokenizer,
    reward_funcs=[
        xmlcount_reward_func,
        soft_format_reward_func,
        strict_format_reward_func,
        int_reward_func,
        correctness_reward_func],
    args=training_args,
    train_dataset=dataset,
    peft_config=peft_config
)

trainer.train()
```
::: {.column-margin}
Tokenizer and Model initialization with Hugging Face Transformers and Flash Attention. Trainer instantiation with the `GRPOTrainer` class with the reward functions, and finally run `trainer.train()`.
:::

## The design space

The script works. But it embeds specific answers to five design questions that most practitioners encounter. Changing any one — the reward scale, the balance between correctness and format, which tasks enter the training set, how many rollouts per prompt, or how the baseline is computed — can change whether the same verifier produces useful training signal or noise.

### Binary versus graded reward

The script's `correctness_reward_func` returns 2.0 for an exact match and 0.0 otherwise — a binary outcome reward. The alternative is graded partial credit: intermediate scores for answers that are close, structurally correct, or partially right.

Graded reward helps when partial structure is checkable and the task has meaningful intermediate states. A response that correctly factors $x^2 - 5x + 6$ into $(x-2)(x-3)$ but reports the roots as $x = 2, 4$ has done real work. A binary verifier scores this the same as "$x = \pi$" — both get 0.0. A graded verifier that checks intermediate steps can distinguish them.

Graded reward hurts when the partial scores are noisy or create hackable shortcuts. If the graded component comes from a learned judge, the model can learn to produce responses that score well on the rubric without being more correct. DeepSeek-R1 used binary correctness reward throughout training and achieved state-of-the-art results, demonstrating that binary reward plus sufficient rollout diversity can substitute for graded scoring.[@deepseekai2025r1]

The practical question is not "binary or graded" in the abstract, but whether the graded component introduces more signal than noise for the specific task distribution and verifier stack.

### Reward decomposition and weighting

The script defines five reward functions and passes them to `GRPOTrainer`, which sums their outputs. The correctness function returns up to 2.0. Each of the four format functions returns up to 0.5. Maximum correctness: 2.0. Maximum total format: also 2.0. Correctness and formatting have equal weight at the ceiling.

This matters because GRPO normalizes rewards within the group: the advantage of each rollout depends on where it falls relative to the group mean. When format rewards are large enough, an incorrect response with good formatting can land close to the group mean and receive near-zero gradient. The optimizer barely suppresses it.

The figure below shows this concretely. Eight rollouts for a single prompt — three correct, five incorrect — scored under two regimes. Under binary-only scoring, every incorrect rollout gets the same negative advantage. Under the combined regime, an incorrect but well-formatted rollout (rollout 4) has advantage −0.04: the optimizer effectively ignores it.

::: {.content-visible when-format="html"}

<div class="rsp-widget" id="rsp-widget">
<p class="rsp-hint">Click a tab to see how reward design changes the training signal for the same eight rollouts.</p>
<div class="rsp-tabs" role="tablist">
<button class="rsp-tab rsp-tab-active" role="tab" data-tab="binary" aria-selected="true">Binary only</button>
<button class="rsp-tab" role="tab" data-tab="format" aria-selected="false">With format rewards</button>
</div>
<table class="rsp-table">
<thead><tr><th>#</th><th>Outcome</th><th>Reward</th><th>Advantage</th><th style="width:40%">Signal</th></tr></thead>
<tbody id="rsp-body"></tbody>
</table>
<div class="rsp-summary" id="rsp-summary" aria-live="polite"></div>
</div>
<style>
.rsp-widget{font-family:var(--bs-font-sans-serif,system-ui,sans-serif);max-width:640px;margin:1.5rem auto}
.rsp-hint{font-size:.9rem;color:var(--bs-secondary,#6c757d);margin-bottom:.75rem}
.rsp-tabs{display:flex;gap:.5rem;margin-bottom:1rem}
.rsp-tab{padding:.4rem 1rem;border:1px solid var(--bs-border-color,#dee2e6);border-radius:4px;background:var(--bs-body-bg,#fff);color:var(--bs-body-color,#212529);cursor:pointer;font-size:.85rem;transition:background .15s}
.rsp-tab:hover{background:var(--bs-tertiary-bg,#f0f0f0)}
.rsp-tab-active{background:var(--bs-primary,#2c7be5);color:#fff;border-color:var(--bs-primary,#2c7be5)}
.rsp-table{width:100%;border-collapse:collapse;font-size:.85rem}
.rsp-table th,.rsp-table td{padding:.35rem .5rem;border-bottom:1px solid var(--bs-border-color,#dee2e6);text-align:left}
.rsp-table th{font-weight:600}
.rsp-bar-cell{position:relative}
.rsp-bar{height:16px;border-radius:2px;transition:width .3s ease}
.rsp-bar-pos{background:#22c55e}
.rsp-bar-neg{background:#ef4444}
.rsp-bar-warn{background:#f59e0b}
.rsp-summary{margin-top:.75rem;font-size:.85rem;padding:.5rem;border-left:3px solid var(--bs-primary,#2c7be5);background:var(--bs-tertiary-bg,#f8f9fa)}
</style>
<script>
(function(){
  var data={
    binary:{
      rows:[
        {id:1,outcome:'\u2713',reward:'2.0',adv:1.29},
        {id:2,outcome:'\u2713',reward:'2.0',adv:1.29},
        {id:3,outcome:'\u2713',reward:'2.0',adv:1.29},
        {id:4,outcome:'\u2717',reward:'0.0',adv:-0.77},
        {id:5,outcome:'\u2717',reward:'0.0',adv:-0.77},
        {id:6,outcome:'\u2717',reward:'0.0',adv:-0.77},
        {id:7,outcome:'\u2717',reward:'0.0',adv:-0.77},
        {id:8,outcome:'\u2717',reward:'0.0',adv:-0.77}
      ],
      mean:0.75,
      summary:'Clean signal: all correct rollouts reinforced equally (+1.29), all incorrect suppressed equally (\u22120.77). Advantage sign matches correctness.'
    },
    format:{
      rows:[
        {id:1,outcome:'\u2713 fmt\u2713',reward:'3.8',adv:1.43},
        {id:2,outcome:'\u2713 fmt\u2713',reward:'3.5',adv:1.21},
        {id:3,outcome:'\u2713 fmt~',reward:'3.0',adv:0.84},
        {id:4,outcome:'\u2717 fmt\u2713',reward:'1.8',adv:-0.04},
        {id:5,outcome:'\u2717 fmt\u2713',reward:'1.5',adv:-0.26},
        {id:6,outcome:'\u2717 fmt~',reward:'1.0',adv:-0.62},
        {id:7,outcome:'\u2717 fmt\u2717',reward:'0.2',adv:-1.21},
        {id:8,outcome:'\u2717 fmt\u2717',reward:'0.0',adv:-1.36}
      ],
      mean:1.85,
      summary:'Diluted signal: rollout 4 is incorrect but its advantage is \u22120.04 \u2014 the optimizer barely suppresses it. Format rewards mask the correctness error.'
    }
  };
  var maxMag=1.5;
  var body=document.getElementById('rsp-body');
  var summaryEl=document.getElementById('rsp-summary');
  function render(tab){
    var d=data[tab];
    body.innerHTML='';
    d.rows.forEach(function(r){
      var tr=document.createElement('tr');
      var mag=Math.min(Math.abs(r.adv)/maxMag,1)*100;
      var cls=r.adv>0.1?'rsp-bar-pos':r.adv<-0.1?'rsp-bar-neg':'rsp-bar-warn';
      var sign=r.adv>0?'+':'';
      tr.innerHTML='<td>'+r.id+'</td><td>'+r.outcome+'</td><td>'+r.reward+'</td><td>'+sign+r.adv.toFixed(2)+'</td><td class="rsp-bar-cell"><div class="rsp-bar '+cls+'" style="width:'+mag+'%"></div></td>';
      body.appendChild(tr);
    });
    summaryEl.innerHTML='<strong>Group mean:</strong> '+d.mean.toFixed(2)+' &middot; '+d.summary;
  }
  document.querySelectorAll('.rsp-tab').forEach(function(btn){
    btn.addEventListener('click',function(){
      document.querySelectorAll('.rsp-tab').forEach(function(b){b.classList.remove('rsp-tab-active');b.setAttribute('aria-selected','false');});
      btn.classList.add('rsp-tab-active');
      btn.setAttribute('aria-selected','true');
      render(btn.dataset.tab);
    });
  });
  render('binary');
})();
</script>

:::

::: {.content-visible when-format="pdf"}

**Binary correctness only** (3 correct, 5 incorrect out of 8 rollouts):

| Rollout | Outcome | Reward | Advantage |
|---------|---------|--------|-----------|
| 1–3     | Correct | 2.0    | +1.29     |
| 4–8     | Wrong   | 0.0    | −0.77     |

Group mean: 0.75. Signal is clean — advantage sign matches correctness for every rollout.

**Correctness + format rewards** (same eight rollouts):

| Rollout | Outcome     | Reward | Advantage |
|---------|-------------|--------|-----------|
| 1       | Correct, fmt ✓ | 3.8 | +1.43     |
| 2       | Correct, fmt ✓ | 3.5 | +1.21     |
| 3       | Correct, fmt ~ | 3.0 | +0.84     |
| 4       | Wrong, fmt ✓   | 1.8 | **−0.04** |
| 5       | Wrong, fmt ✓   | 1.5 | −0.26     |
| 6       | Wrong, fmt ~   | 1.0 | −0.62     |
| 7       | Wrong, fmt ✗   | 0.2 | −1.21     |
| 8       | Wrong, fmt ✗   | 0.0 | −1.36     |

Group mean: 1.85. Signal is diluted — rollout 4 is incorrect but barely suppressed.

:::

The heuristic: the correctness component should dominate so that the sign of the advantage reliably tracks correctness. A common ratio is correctness weight $\geq$ 2–4× the sum of auxiliary weights. The script sits at the boundary (2.0 vs 2.0), which works on GSM8K because the model learns formatting quickly — at which point format rewards become constant across rollouts and vanish from the advantage. On harder tasks where formatting takes longer to learn, this balance can fail.

### Task filtering and the competence band

The script calls `get_gsm8k_questions()` and trains on every problem in the split. No filtering, no curriculum, no difficulty staging.

This works for GSM8K because a 1.5B instruct model sits at roughly the right competence level: it solves some problems but not most, so reward variance across rollouts is high enough to produce informative gradients. But this is a coincidence of model size and dataset difficulty, not a general property.

If the model already solves 95% of training tasks, most rollout groups will be all-correct. After group normalization, advantages are determined by format differences alone — the optimizer trains on formatting, not reasoning. If the model solves only 5%, most groups are all-incorrect and the gradient is noise.

The informative regime is the band where the solve rate is roughly 20–80% per prompt. DeepSeek-R1 filters tasks to maintain this band, dropping problems that are too easy or too hard for the current checkpoint.[@deepseekai2025r1] DeepSeekMath uses rejection sampling to select tasks where the model can sometimes but not always succeed.[@shao2024deepseekmath]

The risk: adaptive filtering creates a non-stationary curriculum. If the filter is too aggressive — keeping only problems at the boundary of the model's competence — the curriculum can overfit to difficulty rather than capability. The model becomes good at medium-hard problems in the filtered distribution and brittle on easy problems it stopped seeing.

### Rollout budget and variance

The script sets `num_generations=16`: sixteen rollouts per prompt. GRPO computes the group-relative advantage from the mean and standard deviation of rewards within this group. The rollout budget controls the quality of that estimate.

With $N = 2$, the baseline is the other rollout's reward — high variance. The advantage is $\pm|r_1 - r_2|$ regardless of whether either rollout is actually good. With $N = 64$, the baseline estimate is stable, but compute is 4× higher than $N = 16$ for diminishing returns in estimate quality.

The budget interacts with reward sparsity. If the model's solve rate on a prompt is 10%, then in a group of 16, on average 1.6 are correct. Groups where none are correct contribute no useful correctness gradient — the advantage is driven entirely by format noise. Groups with exactly one correct rollout concentrate the entire positive advantage on a single sample.

This is why task filtering and rollout budget are not independent. Higher $N$ tolerates lower solve rates by increasing the chance that at least some rollouts in every group succeed. Good task filtering (solve rate 30–60%) means a moderate $N$ like 16 is sufficient.

### Group normalization versus KL penalty

The script uses `GRPOConfig`, which implements group relative policy optimization from DeepSeekMath.[@shao2024deepseekmath] The design choice is the baseline: instead of training a value function $V(s)$ to estimate expected reward (as in PPO), GRPO estimates the baseline from the current batch. The advantage of rollout $i$ in a group is:

$$\hat{A}_i = \frac{r_i - \mu_{\text{group}}}{\sigma_{\text{group}}}$$

This eliminates the value model — one fewer network to train, one fewer source of approximation error. Ahmadian et al. showed more broadly that REINFORCE-style methods match PPO when reward design and hyperparameters are tuned carefully, validating the simpler infrastructure.[@ahmadian2024back]

The tradeoff: no explicit constraint on policy drift. PPO's clipped surrogate or KL penalty keeps the policy close to a reference. GRPO relies on implicit regularization — `max_grad_norm=0.1` clips gradient magnitude, the LoRA adapter constrains the rank of parameter updates, and group normalization centers the expected gradient at zero within each group.

This works for short training runs on well-filtered tasks. For longer runs, the policy can drift far enough that the verifier's scores become unreliable — the model has left the distribution the reward functions were designed for. This is a specific failure mode covered in Chapter 7.

## What this chapter sees and misses

This chapter sees the full signal path from verifier output to parameter update, and the design decisions that shape it: binary versus graded, reward weighting, task filtering, rollout budget, baseline computation. These are the engineering choices that determine whether a strong verifier produces a strong training signal.

It deliberately treats the optimizer as a black box that consumes shaped reward. GRPO, PPO, REINFORCE, and their variants differ in how they compute gradients from advantages, but the signal-design layer sits upstream of all of them. A poorly shaped reward produces bad training under any optimizer.

It misses two things that belong to later chapters. First, what happens when the verifier operates at test time without any parameter update — that is Chapter 6. Second, what happens when the signal path itself becomes the attack surface — when the model learns to exploit the reward function, the format bonuses, or the task filter rather than learning the intended capability — that is Chapter 7.

## Open questions

- Is there a principled way to set reward weights, or is it always empirical search on a held-out set?
- Can task filtering be made adaptive — the curriculum tracks the model's improving competence — without introducing instability or overfitting to the filter?
- When does the marginal rollout stop paying for itself? Is there a compute-optimal $N$ analogous to scaling laws for model size?
- Should format rewards phase out as training progresses, or does removing them cause regression?
- How do these design choices interact with the verifier stack from Chapter 4? A hybrid stack that returns richer verdicts may tolerate different reward-shaping decisions than a binary outcome checker.

Every design choice in this chapter assumes the same structure: generate rollouts, score them, compute advantages, update parameters. That is the training loop. But the same verifier that scores training rollouts can also improve outputs at test time, without updating any parameters. Sampling multiple candidates and selecting the best, guiding search with step-level scores, or voting across reasoning paths — these all use the verifier, and they all produce gains that are routinely reported alongside training gains without separating the two. The verifier's test time role is the subject of Chapter 6.

[^ch5-brown-grpo-150line]: Brown's compact GRPO implementation is a practical reference for outcome-RLVR training with explicit parsing and reward components.[@brown2025grpo]





- Moving from binary pass/fail to graded reward in a math domain with partial structure.
- Filtering tasks to keep the model inside the competence band where signal is informative.
- Using hidden tests or harder variants to keep signal quality from collapsing late in training.
- Over-rewarding trivial formatting wins.
- Using a sparse reward regime with no viable path to exploration.

## Case study: bits per sample

Dwarkesh Patel's "bits per sample" framing is a useful way to see why this chapter matters so much.[@patel2025bitspersample] 
The usual complaint about RL is that it is sample-inefficient because one must unroll a long trajectory to get a reward. But 
in RLVR there is a second problem: even once the rollout is complete, the reward may still contain very little information. A 
long reasoning trace that ends in a single binary outcome gives the optimizer only a thin summary of what happened. In that 
sense, a verifier can be perfectly real and still be a poor teacher.

This is why signal design is not a secondary implementation detail. RLVR works best when tasks sit in a competence band where 
pass/fail outcomes are genuinely informative, and when the training setup raises information density through shaping, 
filtering, curriculum, or other structure. The lesson is not that RLVR is useless; it is that a verifiable reward becomes 
powerful only when the surrounding system turns it into a signal dense enough to learn from.

## Research Notes

- Which signal transformations are robust across domains?
- When is graded reward genuinely better than carefully designed binary reward?
- How can task filtering avoid turning the curriculum into a hidden benchmark hack?
