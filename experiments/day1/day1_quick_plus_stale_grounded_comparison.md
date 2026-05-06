# Day-1 Quick Plus Stale Comparison

This report is auto-generated from the current four-slice quick metrics for the available instruct and reasoning checkpoints.

## Main Table

| Model | Family | Style | Overall Utility | Action Acc. | Answer EM | Answer Contains | Over-Answer Rate | Ask Prec. | Challenge Prec. | Abstain Prec. | JSON Parse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen2.5-0.5B-Instruct | Qwen2.5 | instruct | -0.5375 | 0.4 | 0 | 0 | 0.2 | 0 | 0 | 0 | 0.075 |
| Qwen2.5-1.5B-Instruct | Qwen2.5 | instruct | -0.2188 | 0.775 | 0 | 0.4583 | 0.05 | 0 | 0.6667 | 0 | 0.825 |
| Qwen2.5-Coder-7B-Instruct | Qwen2.5-Coder | instruct | -0.2437 | 0.625 | 0 | 0.4167 | 0.025 | 0 | 1 | 0 | 0.975 |
| DeepSeek-R1-Distill-Qwen-1.5B | DeepSeek/Qwen | reasoning | -0.525 | 0.425 | 0 | 0.2083 | 0.225 | 0 | 1 | 0 | 0 |
| DeepSeek-R1-Distill-Qwen-7B | DeepSeek/Qwen | reasoning | -0.475 | 0.45 | 0 | 0.4167 | 0.15 | 0 | 1 | 0 | 0.075 |

## Per-Slice Table

| Model | Answerable | False Premise | Stale Premise | Conflicting Evidence |
| --- | --- | --- | --- | --- |
| Qwen2.5-0.5B-Instruct | -0.4583 / 0.75 | -0.625 / 0 | -0.625 / 0 | -0.5 / 0.5833 |
| Qwen2.5-1.5B-Instruct | -0.6458 / 0.4167 | 0.375 / 0.9167 | 0.125 / 0.75 | -0.5 / 1 |
| Qwen2.5-Coder-7B-Instruct | -0.4792 / 0.3333 | 0 / 0.4167 | 0.5 / 1 | -0.5 / 1 |
| DeepSeek-R1-Distill-Qwen-1.5B | -0.5 / 0.5833 | -0.5625 / 0.0833 | -0.625 / 0.25 | -0.4792 / 0.6667 |
| DeepSeek-R1-Distill-Qwen-7B | -0.5 / 0.3333 | -0.375 / 0.0833 | -0.625 / 0.25 | -0.5 / 1 |

## Confusion Tables

### Qwen2.5-0.5B-Instruct (`qwen25_05b_day1_quick_plus_stale_grounded`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 16 | 2 | 0 | 6 |
| ask | 0 | 0 | 0 | 0 |
| challenge | 8 | 7 | 0 | 1 |
| abstain | 0 | 0 | 0 | 0 |

### Qwen2.5-1.5B-Instruct (`qwen25_15b_day1_quick_plus_stale_grounded`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 17 | 0 | 7 | 0 |
| ask | 0 | 0 | 0 | 0 |
| challenge | 2 | 0 | 14 | 0 |
| abstain | 0 | 0 | 0 | 0 |

### Qwen2.5-Coder-7B-Instruct (`qwen25_coder_7b_day1_quick_plus_stale_grounded`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 16 | 1 | 0 | 7 |
| ask | 0 | 0 | 0 | 0 |
| challenge | 1 | 2 | 9 | 4 |
| abstain | 0 | 0 | 0 | 0 |

### DeepSeek-R1-Distill-Qwen-1.5B (`deepseek_r1_qwen15b_day1_quick_plus_stale_useronlyfixed_reparsed`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 15 | 1 | 0 | 8 |
| ask | 0 | 0 | 0 | 0 |
| challenge | 9 | 0 | 2 | 5 |
| abstain | 0 | 0 | 0 | 0 |

### DeepSeek-R1-Distill-Qwen-7B (`deepseek_r1_qwen7b_day1_quick_plus_stale_useronlyfixed_reparsed`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 16 | 0 | 0 | 8 |
| ask | 0 | 0 | 0 | 0 |
| challenge | 6 | 0 | 2 | 8 |
| abstain | 0 | 0 | 0 | 0 |
