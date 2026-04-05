# Outcome Rewards

## Chapter Map

- Explain how strong outcome verifiers are built.
- Show why extraction, representation, and hidden brittleness matter more than the apparent simplicity suggests.

## Starting scaffold

**Prompt.**

Solve the equation: $x^2-5x+6=0$.

```text
<think>
We can factor the quadratic: x^2 - 5x + 6 = (x-2)(x-3).
Set each factor to zero:
x - 2 = 0 -> x = 2
x - 3 = 0 -> x = 3
The final answer is the ordered tuple (2,3).
</think>

<answer>
(2,3)
</answer>
```

**Outcome reward check (for RLVR).**

The verifier extracts the final artifact from `<answer>...</answer>`, normalizes order, and checks against the ground-truth set. DeepSeek-R1 uses `<think>` and `<answer>` tags in its response template; for deterministic math tasks it can also add format constraints (for example, boxed expressions) when the reward parser needs a stricter extraction rule.[^ch2-deepseek-r1-template]

$$
r(x,y)=\mathbb{I}[\text{normalize}(\text{extract\_ans}(y))=\{2,3\}]
$$

If the model fails the output contract (for example, omits `<answer>...</answer>`, changes order without normalization, or adds extraneous text that breaks parsing), the reward drops to 0 even if the algebra is correct.

[^ch2-deepseek-r1-template]: DeepSeek-R1 uses `<think>`/`<answer>` separators and applies task-specific response-shape constraints for reward parsing, including boxed final outputs when useful for deterministic math verification.[@deepseekai2025r1]

## Recommended build

This should be the first chapter where the book starts to feel technical. It should probably be the first chapter with real artifacts on the page: one or two equations, two or three diagrams, and one running example carried through the whole chapter.

The cleanest running example is math. Start with a concrete checked answer, then widen to code and formal proof. The point is to make outcome rewards feel operational before they feel abstract.

- Open with one concrete example: model output, extraction, normalization, and final check.
- Define the object: an outcome verifier checks the final artifact, not the path used to produce it.
- Add the minimal math: start with `r(x,y)=V(\mathrm{extract}(y), x)` and then make clear that the practical reward is a pipeline rather than a single comparison.
- Move to the three canonical cases: math, code, and proof.
- End by showing where the apparent simplicity breaks: brittle parsing, unstable benchmarks, exploitable partial credit, and checker quirks.

The core engineering tension of the chapter is that outcome rewards look simple only if the plumbing is ignored. In practice, the chapter is really about building a reliable final-output-to-reward map: output contract, extraction, normalization, correctness check, and grading granularity.

The most useful figures for this chapter would be:

- Outcome verifier pipeline: prompt -> model output -> extraction -> normalization -> checked artifact -> reward.
- Same task, many surface forms: several answer strings collapsing to one normalized mathematical object.
- Outcome versus process preview: chapter 2 checks the endpoint, while later chapters ask what can be said about the path.

## Main Argument

Outcome verifiers are the natural entry point for RLVR because they are operationally simple and often highly scalable. They become useful when the mapping from model output to checked object is stable, unambiguous, and hard to exploit.

This chapter should focus on answer normalization, format design, theorem checking, executable grading, partial credit, and benchmark hygiene. The hard part is often not the final comparison rule but the interface contract that determines what is being compared.

## Harness-aware post-training with GRPO

The phrase "post-training on a harness" is usually this three-object tuple:

- A dataset of prompts and target outputs.
- A response contract that turns model text into structured candidates (for example `<reasoning>...</reasoning><answer>...</answer>`).
- A reward bank that maps those structured candidates to scalar objectives.

In other words, post-training is not abstract; it is mostly "wiring the same model into a reward protocol." That protocol is what people call the harness.

A useful concrete reference is a compact GRPO training script from William Brown. It is intentionally short, and it exposes the reward machinery directly: dataset shaping, response parsing, format shaping, correctness checks, and optimizer wiring are all visible in one place.[^ch2-brown-grpo-150line]

```python
# train_grpo.py
#
# See https://github.com/willccbb/verifiers for ongoing developments
#
import re
import torch
from datasets import load_dataset, Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig
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

XML_COT_FORMAT = """\
<reasoning>
{reasoning}
</reasoning>
<answer>
{answer}
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

def correctness_reward_func(prompts, completions, answer, **kwargs) -> list[float]:
    responses = [completion[0]['content'] for completion in completions]
    q = prompts[0][-1]['content']
    extracted_responses = [extract_xml_answer(r) for r in responses]
    return [2.0 if r == a else 0.0 for r, a in zip(extracted_responses, answer)]

def int_reward_func(completions, **kwargs) -> list[float]:
    responses = [completion[0]['content'] for completion in completions]
    extracted_responses = [extract_xml_answer(r) for r in responses]
    return [0.5 if r.isdigit() else 0.0 for r in extracted_responses]

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
    # peft_config=peft_config
)

trainer.train()
```

The harness in this script has five parts:

- the prompt template (`SYSTEM_PROMPT`) and task-specific contract.
- the conversion layer (`extract_*`) from raw text to answer string.
- reward modules for format quality and correctness.
- the generator configuration that controls sampling behavior and update cadence (`GRPOConfig`).
- the trainer (`GRPOTrainer`) that repeatedly turns rewards into parameter updates.

When people say “Anthropic/OpenAI post-train the model on their harness,” they mean they are changing one or more of these five parts over multiple rounds, not just changing one number in `GRPOConfig`.

## Canonical Examples

- Exact-match grading for math problems with normalized final answers.
- Code execution against a test suite with hidden tests.
- Formal theorem acceptance in a proof assistant.
- Symbolic evaluation for structured tasks where multiple surface forms represent the same answer.

## Failure Modes

- Checker errors induced by fragile extraction or formatting assumptions.
- Benchmarks that reward shortcuts rather than the intended capability.
- Partial-credit schemes that leak exploitable heuristics.

## What the Verifier Sees

The verifier sees the final artifact: answer string, code file, proof object, or structured output that survives extraction.

## What the Verifier Misses

It misses how the artifact was produced, whether intermediate reasoning was valid, and whether success came from true competence or from exploiting narrow regularities.

## Research Notes

- When is binary scoring enough, and when is graded outcome feedback worth the complexity?
- How should hidden tests be designed to reduce benchmark gaming without drifting away from the task?
- Which extraction conventions are stable across model families?

[^ch2-brown-grpo-150line]: Brown’s compact 150-line GRPO implementation is a practical reference for harness-level RLVR post-training with explicit parsing and reward components.[@brown2025grpo]
