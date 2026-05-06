# Qwen-Plus-Latest Prompt Controls Bootstrap CIs

Bootstrap 95% percentile intervals computed from per-example outcomes with `2000` resamples per run.

## Main Table

| Model | Utility (95% CI) | Action Acc. (95% CI) | Over-Answer (95% CI) | n |
| --- | --- | --- | --- | --- |
| qwen-plus-latest | 0.1571 [0.1121, 0.2045] | 0.8571 [0.8286, 0.8857] | 0.0304 [0.0179, 0.0446] | 560 |
| qwen-plus-latest | 0.0576 [0.0161, 0.0996] | 0.8804 [0.8536, 0.9054] | 0.0357 [0.0214, 0.0518] | 560 |
| qwen-plus-latest | 0.0786 [0.0402, 0.1187] | 0.875 [0.8464, 0.9018] | 0.0214 [0.0107, 0.0339] | 560 |

## Per-Slice Action Accuracy

| Model | Answerable | False Premise | Stale Premise | Conflicting Evidence | Ambiguous Intent | Insufficient Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| qwen-plus-latest | 0.7642 [0.6792, 0.8396] | 0.7667 [0.6917, 0.8417] | 0.975 [0.9375, 1] | 0.7447 [0.6489, 0.8298] | 1 [1, 1] | 0.9875 [0.9625, 1] |
| qwen-plus-latest | 0.8019 [0.7264, 0.8774] | 0.7167 [0.6333, 0.7917] | 0.95 [0.9, 0.9875] | 0.9894 [0.9681, 1] | 0.9125 [0.85, 0.9625] | 1 [1, 1] |
| qwen-plus-latest | 0.7358 [0.6509, 0.8113] | 0.7583 [0.6833, 0.8333] | 1 [1, 1] | 0.9362 [0.883, 0.9787] | 1 [1, 1] | 0.9125 [0.8497, 0.9625] |
