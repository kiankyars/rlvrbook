# Turning Checks into Training Signal

![M. C. Escher, _The Drowned Cathedral_ (1929).](../art/escher/05-the-drowned-cathedral.jpg){width="80%" fig-align="center"}

## Talking Points

- Moving from binary pass/fail to graded reward in a math domain with partial structure.
- Filtering tasks to keep the model inside the competence band where signal is informative.
- Using hidden tests or harder variants to keep signal quality from collapsing late in training.
- Over-rewarding trivial formatting wins.
- Using a sparse reward regime with no viable path to exploration.

## Case study: bits per sample

Dwarkesh Patel's "bits per sample" framing is a useful way to see why this chapter matters so much.[@patel2025bitspersample] The usual complaint about RL is that it is sample-inefficient because one must unroll a long trajectory to get a reward. But in RLVR there is a second problem: even once the rollout is complete, the reward may still contain very little information. A long reasoning trace that ends in a single binary outcome gives the optimizer only a thin summary of what happened. In that sense, a verifier can be perfectly real and still be a poor teacher.

This is why signal design is not a secondary implementation detail. RLVR works best when tasks sit in a competence band where pass/fail outcomes are genuinely informative, and when the training setup raises information density through shaping, filtering, curriculum, or other structure. The lesson is not that RLVR is useless; it is that a verifiable reward becomes powerful only when the surrounding system turns it into a signal dense enough to learn from.

## Research Notes

- Which signal transformations are robust across domains?
- When is graded reward genuinely better than carefully designed binary reward?
- How can task filtering avoid turning the curriculum into a hidden benchmark hack?

## A compact outcome-RLVR training script

[Will Brown's](https://x.com/willccbb/status/1886788410351796232) legendary GRPO script shows the smallest complete loop from verifiable check on outcome rewards to parameter update.[^ch5-brown-grpo-150line] Let's go through it with a fine-toothed comb.

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
System prompt and XML format with proper templating.
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
The above functions are for extraction:
1. Extracting XML from the above XML COT format
2. Extracting the text suceeding ###
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
There are in total six reward functions, so let's go through them two at a time. The first one is a reward function that simply checks whether the language model gets the correct answer, using the Extract XML answer function. Notice that in this function we are checking for exact matching, whereas in `int_or_reward_func` we're not even checking if the answer is correct, but rather, is there a digit in the answer? In which case we give 0.5 as a partial reward, as opposed to 2 if the output is correct.
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
Now these two reward functions are simply concerned with the formatting, which is to say, did the models use the reasoning and answer tags correctly? There is both a strict and a soft format function. In the strict one, we use the caret sign at the beginning of the pattern, which simply means that the string must begin with the reasoning tag and there must be nothing before it. Furthermore, there is the constraint of having new lines in between the tags in the strict one, whereas that same constraint is not in the soft format reward function. Finally, we have the dollar sign anchor tag at the end of the strict reward function regex matching pattern, which means that there should be nothing after the final answer tag, but this is not required for the soft format reward function.
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
These last two are perhaps the simplest of the word functions. In fact, these two combine into one, which is to say we're just counting whether or not there are reasoning and answer tags within the response. The only nuance here is the subtraction statement in both of the answer conditional statements, which is essentially saying we are going to give a negative reward for however many tokens occur after the last answer tag.
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
Here we are choosing our LLM and then simply configuring our GRPO optimizer with the applicable learning rate, weight decay, data formats, etc., as well as our Lora config, which is the head that we will train on top of our language model.
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
Now we initialize our model with the standard auto model for causal LLM from Hugging Face Transformers with Flash Attention, as well as our tokenizer. We then create our trainer with the grpo-trainer class with all of the relevant reward functions, and finally run trainer.train. It's as simple as that.
:::

[^ch5-brown-grpo-150line]: Brown’s compact GRPO implementation is a practical reference for outcome-RLVR training with explicit parsing and reward components.[@brown2025grpo]
