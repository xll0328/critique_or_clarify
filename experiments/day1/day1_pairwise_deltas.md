# Day-1 Pairwise Deltas

This note turns the current scale/reasoning snapshot into pairwise deltas that are easier to cite in the paper than raw tables alone.

## Frontier Steps

### Instruct Frontier

| From | To | Delta Utility | Delta Action Acc. | Delta Over-Answer | Delta JSON Parse | Biggest Slice Gain | Biggest Slice Drop |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen2.5-0.5B-Instruct | Qwen2.5-1.5B-Instruct | +0.2125 | +0.4167 | -0.0667 | +0.7416 | False Premise +0.975 | Answerable -0.075 |
| Qwen2.5-1.5B-Instruct | Qwen2.5-Coder-7B-Instruct | -0.0563 | -0.1667 | 0 | +0.1334 | Conflicting Evidence +0.025 | False Premise -0.525 |

Interpretation:
- From `Qwen2.5-0.5B-Instruct` to `Qwen2.5-1.5B-Instruct`, action accuracy changes by `+0.4167`, utility by `+0.2125`, and JSON parse by `+0.7416`.
- From `Qwen2.5-1.5B-Instruct` to `Qwen2.5-Coder-7B-Instruct`, action accuracy changes by `-0.1667`, utility by `-0.0563`, and JSON parse by `+0.1334`.

### Reasoning Frontier

| From | To | Delta Utility | Delta Action Acc. | Delta Over-Answer | Delta JSON Parse | Biggest Slice Gain | Biggest Slice Drop |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DeepSeek-R1-Distill-Qwen-1.5B | DeepSeek-R1-Distill-Qwen-7B | +0.0812 | -0.0166 | -0.1 | +0.05 | Conflicting Evidence +0.15 | Answerable -0.3 |

Interpretation:
- From `DeepSeek-R1-Distill-Qwen-1.5B` to `DeepSeek-R1-Distill-Qwen-7B`, action accuracy changes by `-0.0166`, utility by `+0.0812`, and JSON parse by `+0.05`.

## Scale-Matched Style Contrasts

| Size | Instruct | Reasoning | Reasoning Minus Instruct Utility | Action Acc. | Over-Answer | JSON Parse | Biggest Slice Gain For Reasoning | Biggest Slice Drop For Reasoning |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1.5B | Qwen2.5-1.5B-Instruct | DeepSeek-R1-Distill-Qwen-1.5B | -0.2896 | -0.3834 | +0.1417 | -0.8 | Answerable +0.15 | False Premise -0.975 |
| 7B | Qwen2.5-Coder-7B-Instruct | DeepSeek-R1-Distill-Qwen-7B | -0.1521 | -0.2333 | +0.0417 | -0.8834 | No gain | False Premise -0.35 |

Interpretation:
- At `1.5B`, `DeepSeek-R1-Distill-Qwen-1.5B` changes utility by `-0.2896`, action accuracy by `-0.3834`, and over-answer by `+0.1417` relative to `Qwen2.5-1.5B-Instruct`.
- At `7B`, `DeepSeek-R1-Distill-Qwen-7B` changes utility by `-0.1521`, action accuracy by `-0.2333`, and over-answer by `+0.0417` relative to `Qwen2.5-Coder-7B-Instruct`.

## Immediate Writing Use

- Use the frontier-step lines when describing scale effects; they are direct deltas, not eyeballed differences from the markdown table.
- Use the size-matched contrast lines for instruct-vs-reasoning claims, because they isolate style at the same approximate parameter scale.
- The current strongest available instruct step is `Qwen2.5-0.5B-Instruct -> Qwen2.5-1.5B-Instruct` by action accuracy, so that is the cleanest scale sentence to foreground.
