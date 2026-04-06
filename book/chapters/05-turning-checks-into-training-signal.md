# Turning Checks into Training Signal

![M. C. Escher, _The Drowned Cathedral_ (1929).](../art/escher/05-the-drowned-cathedral.jpg){width="80%" fig-align="center"}

## Chapter Map

- Explain how a checker becomes useful learning signal rather than a brittle scoreboard.
- Keep the focus on signal quality, task shaping, and curriculum rather than optimizer taxonomy.

## Main Argument

The same verifier can be useful or useless depending on how its outputs are turned into signal. Binary versus graded scoring, task selection, filtering, rollout grouping, and curriculum decisions all change the effective optimization landscape before any optimizer-specific choice matters.

This chapter should stay narrowly focused on signal design: how to make checks teachable, how to prevent verifier noise from dominating learning, and how to decide when simple rejection or search-based selection already captures most of the gain.

## A compact outcome-RLVR training script

Will Brown's public GRPO script is a good reference point because it shows the smallest complete loop from verifiable check to parameter update.[^ch5-brown-grpo-150line] It is an outcome-RLVR training script, not a process verifier and not what this book will call a frontier coding harness. The rewards inspect the final extracted answer and response format; they do not verify whether the intermediate reasoning steps are logically valid.

For this chapter, the important point is structural. A compact training script has five moving parts:

- A task source: prompts and target data.
- A response contract: response format and extraction rules.
- A reward bank: correctness and quality terms over extracted artifacts.
- A signal policy: filtering, clipping, scaling, and schedule decisions.
- A trainer configuration: rollout counts, clipping, entropy terms, and optimization settings.

For practical implementations, this means you can change the same objective while changing only one component of the script, and the behavior changes substantially. That is why it is often more precise to say practitioners are changing the reward plumbing, not “just changing one hyperparameter.” Frontier coding harnesses are a different object: long-horizon, environment-backed rollout systems over repositories, shells, tools, and hidden graders. Those belong in Chapter 10.

An excerpted Brown-style script makes the distinction concrete:

```python
import re
import torch
from datasets import load_dataset, Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
from trl import GRPOConfig, GRPOTrainer

SYSTEM_PROMPT = """
Respond in the following format:

<reasoning>
...
</reasoning>
<answer>
...
</answer>
"""

def extract_xml_answer(text: str) -> str:
    answer = text.split("<answer>")[-1]
    answer = answer.split("</answer>")[0]
    return answer.strip()

def extract_hash_answer(text: str) -> str | None:
    if "####" not in text:
        return None
    return text.split("####")[1].strip().replace(",", "").replace("$", "")

def get_gsm8k_questions(split="train") -> Dataset:
    data = load_dataset("openai/gsm8k", "main")[split]
    return data.map(lambda x: {
        "prompt": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": x["question"]},
        ],
        "answer": extract_hash_answer(x["answer"]),
    })

def correctness_reward_func(prompts, completions, answer, **kwargs) -> list[float]:
    responses = [completion[0]["content"] for completion in completions]
    extracted = [extract_xml_answer(r) for r in responses]
    return [2.0 if r == a else 0.0 for r, a in zip(extracted, answer)]

def strict_format_reward_func(completions, **kwargs) -> list[float]:
    pattern = r"^<reasoning>\n.*?\n</reasoning>\n<answer>\n.*?\n</answer>\n$"
    responses = [completion[0]["content"] for completion in completions]
    matches = [re.match(pattern, r, flags=re.DOTALL) for r in responses]
    return [0.5 if match else 0.0 for match in matches]

training_args = GRPOConfig(
    output_dir="outputs/Qwen-1.5B-GRPO",
    run_name="Qwen-1.5B-GRPO-gsm8k",
    learning_rate=5e-6,
    bf16=True,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    num_generations=16,
    max_prompt_length=256,
    max_completion_length=786,
    num_train_epochs=1,
)

model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-1.5B-Instruct",
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
).to("cuda")

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")
tokenizer.pad_token = tokenizer.eos_token

trainer = GRPOTrainer(
    model=model,
    processing_class=tokenizer,
    reward_funcs=[strict_format_reward_func, correctness_reward_func],
    args=training_args,
    train_dataset=get_gsm8k_questions(),
)

trainer.train()
```

This script is exactly why the Brown reference belongs in Chapter 5. It shows how outcome checks become training signal in a real RLVR loop. It does not introduce a process reward model, and it does not yet look like the frontier agentic coding systems discussed later in the book.

## Canonical Examples

- Moving from binary pass/fail to graded reward in a math domain with partial structure.
- Filtering tasks to keep the model inside the competence band where signal is informative.
- Using hidden tests or harder variants to keep signal quality from collapsing late in training.

## Failure Modes

- Over-rewarding trivial formatting wins.
- Using a sparse reward regime with no viable path to exploration.
- Smuggling optimizer detail into what should be a chapter about checker design.

## What the Verifier Sees

The verifier sees the same artifacts as before; the new design question is how those outputs are transformed into reward, filtering, or acceptance decisions.

## What the Verifier Misses

It still misses off-policy exploration quality, latent competence, and any capability that the selected signal proxy does not capture.

## Research Notes

- Which signal transformations are robust across domains?
- When is graded reward genuinely better than carefully designed binary reward?
- How can task filtering avoid turning the curriculum into a hidden benchmark hack?

[^ch5-brown-grpo-150line]: Brown’s compact GRPO implementation is a practical reference for outcome-RLVR training with explicit parsing and reward components.[@brown2025grpo]
