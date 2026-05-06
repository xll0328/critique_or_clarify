# Day-1 Scale And Reasoning Comparison Bootstrap Confidence Intervals

Bootstrap 95% percentile intervals computed from per-example outcomes with `2000` resamples per run.

## Main Table

| Model | Utility (95% CI) | Action Acc. (95% CI) | Over-Answer (95% CI) | n |
| --- | --- | --- | --- | --- |
| Qwen2.5-0.5B-Instruct | -0.4354 [-0.4729, -0.402] | 0.35 [0.2667, 0.4333] | 0.075 [0.0333, 0.125] | 120 |
| Qwen2.5-1.5B-Instruct | -0.2229 [-0.3167, -0.1271] | 0.7667 [0.6917, 0.8417] | 0.0083 [0, 0.025] | 120 |
| DeepSeek-R1-Distill-Qwen-1.5B | -0.5125 [-0.5583, -0.4624] | 0.3833 [0.2998, 0.4669] | 0.15 [0.0917, 0.2167] | 120 |
| Qwen2.5-Coder-7B-Instruct | -0.2792 [-0.3458, -0.2062] | 0.6 [0.5083, 0.6833] | 0.0083 [0, 0.025] | 120 |
| DeepSeek-R1-Distill-Qwen-7B | -0.4313 [-0.4729, -0.3896] | 0.3667 [0.2833, 0.4583] | 0.05 [0.0167, 0.0917] | 120 |

## Per-Slice Action Accuracy

| Model | Answerable | False Premise | Conflicting Evidence |
| --- | --- | --- | --- |
| Qwen2.5-0.5B-Instruct | 0.425 [0.275, 0.575] | 0 [0, 0] | 0.625 [0.475, 0.775] |
| Qwen2.5-1.5B-Instruct | 0.35 [0.2, 0.5] | 0.975 [0.925, 1] | 0.975 [0.925, 1] |
| DeepSeek-R1-Distill-Qwen-1.5B | 0.5 [0.35, 0.65] | 0 [0, 0] | 0.65 [0.5, 0.7756] |
| Qwen2.5-Coder-7B-Instruct | 0.35 [0.2, 0.5] | 0.45 [0.3, 0.6] | 1 [1, 1] |
| DeepSeek-R1-Distill-Qwen-7B | 0.2 [0.075, 0.325] | 0.1 [0.025, 0.2] | 0.8 [0.675, 0.925] |
