# Day-1 Scale And Reasoning Comparison

This report is auto-generated from the current dev metrics for the scale-matched instruct and reasoning checkpoints.

## Main Table

| Model | Family | Style | Overall Utility | Action Acc. | Answer EM | Answer Contains | Over-Answer Rate | Ask Prec. | Challenge Prec. | Abstain Prec. | JSON Parse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen2.5-0.5B-Instruct | Qwen2.5 | instruct | -0.4354 | 0.35 | 0 | 0.05 | 0.075 | 0 | 0 | 0 | 0.0667 |
| Qwen2.5-1.5B-Instruct | Qwen2.5 | instruct | -0.2229 | 0.7667 | 0.0125 | 0.475 | 0.0083 | 0 | 0.5909 | 0 | 0.8083 |
| DeepSeek-R1-Distill-Qwen-1.5B | DeepSeek/Qwen | reasoning | -0.5125 | 0.3833 | 0.0125 | 0.15 | 0.15 | 0 | 0 | 0 | 0.0083 |
| Qwen2.5-Coder-7B-Instruct | Qwen2.5-Coder | instruct | -0.2792 | 0.6 | 0.025 | 0.475 | 0.0083 | 0 | 0.9474 | 0 | 0.9417 |
| DeepSeek-R1-Distill-Qwen-7B | DeepSeek/Qwen | reasoning | -0.4313 | 0.3667 | 0 | 0.3125 | 0.05 | 0 | 0.8 | 0 | 0.0583 |

## Per-Slice Table

| Model | Answerable | False Premise | Conflicting Evidence |
| --- | --- | --- | --- |
| Qwen2.5-0.5B-Instruct | -0.4188 / 0.425 | -0.4188 / 0 | -0.4688 / 0.625 |
| Qwen2.5-1.5B-Instruct | -0.625 / 0.35 | 0.4625 / 0.975 | -0.5062 / 0.975 |
| DeepSeek-R1-Distill-Qwen-1.5B | -0.4688 / 0.5 | -0.5875 / 0 | -0.4813 / 0.65 |
| Qwen2.5-Coder-7B-Instruct | -0.4062 / 0.35 | 0.0688 / 0.45 | -0.5 / 1 |
| DeepSeek-R1-Distill-Qwen-7B | -0.5062 / 0.2 | -0.2875 / 0.1 | -0.5 / 0.8 |

## Confusion Tables

### Qwen2.5-1.5B-Instruct (`qwen25_15b_day1_dev`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 53 | 0 | 27 | 0 |
| ask | 0 | 0 | 0 | 0 |
| challenge | 1 | 0 | 39 | 0 |
| abstain | 0 | 0 | 0 | 0 |

### DeepSeek-R1-Distill-Qwen-1.5B (`deepseek_r1_qwen15b_day1_dev_useronlyfixed_reparsed`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 46 | 4 | 2 | 28 |
| ask | 0 | 0 | 0 | 0 |
| challenge | 18 | 1 | 0 | 21 |
| abstain | 0 | 0 | 0 | 0 |

### Qwen2.5-Coder-7B-Instruct (`qwen25_coder_7b_day1_dev`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 54 | 4 | 1 | 21 |
| ask | 0 | 0 | 0 | 0 |
| challenge | 1 | 10 | 18 | 11 |
| abstain | 0 | 0 | 0 | 0 |

### DeepSeek-R1-Distill-Qwen-7B (`deepseek_r1_qwen7b_day1_dev_useronlyfixed_reparsed`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 40 | 0 | 1 | 39 |
| ask | 0 | 0 | 0 | 0 |
| challenge | 6 | 0 | 4 | 30 |
| abstain | 0 | 0 | 0 | 0 |
