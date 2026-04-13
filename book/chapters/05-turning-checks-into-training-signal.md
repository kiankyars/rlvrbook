# Turning Checks into Training Signal

![M. C. Escher, _The Drowned Cathedral_ (1929).](../escher/05-the-drowned-cathedral.jpg){width="80%" fig-align="center"}

## Chapter Map

- A complete outcome-RLVR training loop, annotated line by line, to show how verifier verdicts become parameter updates.
- Reward shaping, task filtering, rollout budget, and baseline design demonstrate that a poorly shaped reward produces bad training under any optimizer.

## A compact outcome-RLVR training script

[Will Brown's](https://x.com/willccbb/status/1886788410351796232) legendary GRPO script shows the smallest complete loop from verifiable check on outcome rewards to parameter update on a 1.5B model.[^ch5-brown-grpo-150line] Let's go through it with a fine-toothed comb.

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
These two functions:

1. Extract XML from the CoT format used by `extract_xml_answer`
2. Extract the text succeeding `####`
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
A lambda function to load our Grade School Math 8K (GSM8K, a benchmark of math word problems for grade school arithmetic) dataset into the corresponding question and answer fields on the train split of the dataset, along with the system prompt.
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
`correctness_reward_func` checks whether the language model gets the correct answer, using the Extract XML answer function. Notice the function checks for exact matching, whereas `int_reward_func` checks only for digit presence. Both of these are binary outcome rewards, and rewarding `2.0` versus `0.5` is a design choice.
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
These reward functions are concerned with whether the models used the reasoning and answer tags correctly. There is both a strict and a soft format function. The strict function uses the caret sign `^` at the beginning of the pattern, enforcing that the string begins with the reasoning tag. Furthermore, the strict function demands `\n` between the tags. Finally, we have the anchor tag `$` at the end of the strict reward function regex matching pattern, which means that there should be nothing after the final answer tag.
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
Counts over reasoning and answer tags within the response. The only nuance is the subtraction statement in both of the answer conditional statements, which gives a negative reward proportional to extraneous tokens after the closing answer tag. One must be careful with the reward for format rewards, lest they distract from correctness.
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
LLM selection and configurtion of the GRPO optimizer with the applicable learning rate, weight decay, data formats, etc., as well as our Lora config, which is the adapter trained on top of the language model. For this chapter, the most important choices are `num_generations=16`, which sets the rollout budget and therefore the variance-compute tradeoff. `max_grad_norm=0.1`, helps control policy drift.
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

That script embeds answers to five design questions that most practitioners encounter, let's discuss them.

### Binary versus graded reward

`correctness_reward_func` is a binary outcome reward of 2.0 for exact match and 0.0 otherwise, in opposition to a partial reward for partial solution. DeepSeek-R1 used binary correctness reward throughout training and achieved state-of-the-art results, demonstrating that binary reward plus sufficient rollout diversity can substitute for graded scoring.[@deepseekai2025r1]

### Reward decomposition and weighting

The script passes five reward functions to `GRPOTrainer`, which sums their outputs. The correctness function returns up to 2.0, and each of the four format functions returns up to 0.5, meaning correctness and formatting have equal weight at the ceiling. Since GRPO normalizes rewards within the group of 16 trajectories, an incorrect response with good formatting can land close to the group mean and receive near-zero gradient, which is counterproductive.

@tbl-ch5-reward-comparison demonstrates this edge case with eight rollouts scored under two regimes for a single prompt having three correct and five incorrect outcomes.

::: {#tbl-ch5-reward-comparison}
::: {.content-visible when-format="html"}

<div class="rsp-widget" id="rsp-widget">
<div class="rsp-tabs" role="tablist">
<button class="rsp-tab rsp-tab-active" role="tab" data-tab="binary" aria-selected="true">Correctness</button>
<button class="rsp-tab" role="tab" data-tab="format" aria-selected="false">Correctness + format</button>
</div>
<table class="rsp-table">
<thead><tr><th>#</th><th>Correctness</th><th>Format</th><th>Reward</th><th>Advantage</th><th style="width:40%">Signal</th></tr></thead>
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
        {id:1,correctness:'\u2713',format:'N/A',reward:'2.0',adv:1.29},
        {id:2,correctness:'\u2713',format:'N/A',reward:'2.0',adv:1.29},
        {id:3,correctness:'\u2713',format:'N/A',reward:'2.0',adv:1.29},
        {id:4,correctness:'\u2717',format:'N/A',reward:'0.0',adv:-0.77},
        {id:5,correctness:'\u2717',format:'N/A',reward:'0.0',adv:-0.77},
        {id:6,correctness:'\u2717',format:'N/A',reward:'0.0',adv:-0.77},
        {id:7,correctness:'\u2717',format:'N/A',reward:'0.0',adv:-0.77},
        {id:8,correctness:'\u2717',format:'N/A',reward:'0.0',adv:-0.77}
      ],
      mean:0.75,
      summary:'Clean signal: all correct rollouts reinforced equally (+1.29), all incorrect suppressed equally (\u22120.77). Advantage sign matches correctness.'
    },
    format:{
      rows:[
        {id:1,correctness:'\u2713',format:'\u2713',reward:'3.8',adv:1.43},
        {id:2,correctness:'\u2713',format:'\u2713',reward:'3.5',adv:1.21},
        {id:3,correctness:'\u2713',format:'~',reward:'3.0',adv:0.84},
        {id:4,correctness:'\u2717',format:'\u2713',reward:'1.8',adv:-0.04},
        {id:5,correctness:'\u2717',format:'\u2713',reward:'1.5',adv:-0.26},
        {id:6,correctness:'\u2717',format:'~',reward:'1.0',adv:-0.62},
        {id:7,correctness:'\u2717',format:'\u2717',reward:'0.2',adv:-1.21},
        {id:8,correctness:'\u2717',format:'\u2717',reward:'0.0',adv:-1.36}
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
      tr.innerHTML='<td>'+r.id+'</td><td>'+r.correctness+'</td><td>'+r.format+'</td><td>'+r.reward+'</td><td>'+sign+r.adv.toFixed(2)+'</td><td class="rsp-bar-cell"><div class="rsp-bar '+cls+'" style="width:'+mag+'%"></div></td>';
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

**Correctness only** (3 correct, 5 incorrect out of 8 rollouts):

| Rollout | Correctness | Format | Reward | Advantage |
|---------|-------------|--------|--------|-----------|
| 1–3     | Correct     | N/A    | 2.0    | +1.29     |
| 4–8     | Wrong       | N/A    | 0.0    | −0.77     |

Group mean: 0.75. Signal is clean — advantage sign matches correctness for every rollout.

**Correctness + format rewards** (same eight rollouts):

| Rollout | Correctness | Format | Reward | Advantage |
|---------|-------------|--------|--------|-----------|
| 1       | Correct     | ✓      | 3.8    | +1.43     |
| 2       | Correct     | ✓      | 3.5    | +1.21     |
| 3       | Correct     | ~      | 3.0    | +0.84     |
| 4       | Wrong       | ✓      | 1.8    | **−0.04** |
| 5       | Wrong       | ✓      | 1.5    | −0.26     |
| 6       | Wrong       | ~      | 1.0    | −0.62     |
| 7       | Wrong       | ✗      | 0.2    | −1.21     |
| 8       | Wrong       | ✗      | 0.0    | −1.36     |

Group mean: 1.85. Signal is diluted — rollout 4 is incorrect but barely suppressed.

:::

Comparison of eight rollouts under correctness versus correctness & format design.
:::

The correctness component should dominate such that auxiliary rewards do not determine the advantage sign for incorrect rollouts. The script sits at the boundary (2.0 vs 2.0), this works on GSM8K because the model learns formatting quickly enough that they become constant across rollouts and vanish from the advantage. On harder tasks where formatting takes longer to learn, this balance can fail.

### Task filtering and the competence band

The script calls `get_gsm8k_questions()` and trains on every problem in the split without filtering or a curriculum.

This works for GSM8K because a 1.5B instruct model sits at roughly the right competence level: it solves some problems but not most, so reward variance across rollouts is high enough to produce informative gradients. But this is a coincidence of model size and dataset difficulty, not a general property. (cite the numbers)

If the model already solves 95% of training tasks, most rollout groups will be all-correct. After group normalization, advantages are determined by format differences alone, so we're effectively training on formatting. Converslet, a model that can only solve 5% of problems produces groups where most rollouts are incorrect, giving a weak learning signal.

The optimal regime in RL is the band where the solve rate is roughly 20–80% per prompt. DeepSeek-R1 and DeepSeekMath both filter tasks through rejection sampling to maintain this band.[^ch5-rejection-sampling][@shao2024deepseekmath][@deepseekai2025r1] Adaptive filtering keeps reward variance high, but because curriculum learning deliberately reweights the training distribution over time, gains should be checked on the original difficulty range rather than only on the moving band used for training.[@bengio2009curriculum]

### Group normalization versus KL penalty

The script uses `GRPOConfig`, which implements group relative policy optimization from DeepSeekMath.[@shao2024deepseekmath] Instead of training a value function $V(s)$ to estimate expected reward (as in PPO), GRPO estimates the baseline from the current batch. The advantage of rollout $i$ in a group is:

$$\hat{A}_i = \frac{r_i - \mu_{\text{group}}}{\sigma_{\text{group}}}$$

This eliminates the value model, and in fact, Ahmadian et al. showed that REINFORCE-style methods (no learned value function) match PPO when reward design and hyperparameters are tuned carefully.[@ahmadian2024back] The drawback here is no explicit constraint on policy drift. PPO's clipped surrogate or KL penalty keeps the policy close to a reference. GRPO relies on implicit regularization — `max_grad_norm=0.1` clips gradient magnitude, the LoRA adapter constrains the rank of parameter updates, and group normalization centers the expected gradient at zero within each group. This works for short training runs on well-filtered tasks. For longer runs, the policy can drift far enough that the verifier's scores become unreliable — the model has left the distribution the reward functions were designed for. This is a specific failure mode covered in Chapter 7.

### Rollout budget and variance

The script sets `num_generations=16`: sixteen rollouts per prompt. GRPO computes the group-relative advantage from the mean and standard deviation of rewards within this group. The rollout budget controls the quality of that estimate.

If we consider the extremes, with $N = 2$, the group baseline is the mean of the two rollout rewards: $\mu = (r_1 + r_2)/2$. This gives extreme variance since the unnormalized advantages are $A_1 = r_1 - \mu$ and $A_2 = r_2 - \mu$, each determined almost entirely by its difference from the other rollout rather than by a stable estimate of expected reward for the given prompt. As $N \to \infty$, the group baseline approaches a more stable estimate, but with diminishing returns in estimate quality at linear scaling in compute cost.

If the model's solve rate on a prompt is 10%, then in a group of 16, on average 1.6 are correct. This implies that groups with no correct trajectories contribute no useful correctness gradient, and those with only one correct rollout concentrate the entire positive advantage on a single sample. Higher $N$ tolerates lower solve rates by increasing the chance that at least some rollouts in every group succeed, but good task filtering means a moderate $N$ like 16 is sufficient.

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

## Open questions

- Is there a principled way to set reward weights, or is it always empirical search on a held-out set?
- How should adaptive task filtering be evaluated so that a curriculum tracking the model's competence improves the target distribution rather than overfitting to the moving filter?
- Is there a compute-optimal $N$ analogous to scaling laws for model size?
- Should format rewards phase out as training progresses, or does removing them cause regression?
- Which signal transformations are robust across domains?
- When is graded reward genuinely better than carefully designed binary reward?

## What comes next

Every design choice in this chapter assumes the same structure: generate rollouts, score them, compute advantages, update parameters. That is the training loop. But the same verifier that scores training rollouts can also improve outputs at test time, without updating any parameters. Sampling multiple candidates and selecting the best, guiding search with step-level scores, or voting across reasoning paths — these all use the verifier, and they all produce gains that are routinely reported alongside training gains without separating the two. The verifier's test time role is the subject of Chapter 6.

[^ch5-brown-grpo-150line]: Brown's compact GRPO implementation is a practical reference for outcome-RLVR training with explicit parsing and reward components.[@brown2025grpo]
[^ch5-rejection-sampling]: Rejection sampling means sampling candidate problems or candidate rollouts, scoring them with the verifier, and keeping only the ones that meet a target criterion, e.g. example prompts whose rollouts are sometimes but not always correct.
