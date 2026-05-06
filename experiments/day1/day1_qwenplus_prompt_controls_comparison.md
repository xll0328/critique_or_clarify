# Qwen-Plus-Latest Prompt-Style Controls (Expanded 560)

## Main Table

| Model | Family | Style | Overall Utility | Action Acc. | Answer EM | Answer Contains | Over-Answer Rate | Ask Prec. | Challenge Prec. | Abstain Prec. | JSON Parse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen-plus-latest | Qwen API | api | 0.1571 | 0.8571 | 0.16 | 0.62 | 0.0304 | 0.7843 | 0.8543 | 0.8681 | 0.8054 |
| qwen-plus-latest | Qwen API | api | 0.0576 | 0.8804 | 0 | 0.725 | 0.0357 | 0.8391 | 0.9759 | 0.7339 | 0.4036 |
| qwen-plus-latest | Qwen API | api | 0.0786 | 0.875 | 0 | 0.69 | 0.0214 | 0.7407 | 0.886 | 0.9012 | 0.3821 |

## Per-Slice Table

| Model | Answerable | False Premise | Stale Premise | Conflicting Evidence | Ambiguous Intent | Insufficient Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| qwen-plus-latest | -0.4835 / 0.7642 | 0.2313 / 0.7667 | 0.4625 / 0.975 | -0.0505 / 0.7447 | 0.5 / 1 | 0.4906 / 0.9875 |
| qwen-plus-latest | -0.4882 / 0.8019 | 0.1875 / 0.7167 | 0.425 / 0.95 | -0.5027 / 0.9894 | 0.4344 / 0.9125 | 0.5 / 1 |
| qwen-plus-latest | -0.4858 / 0.7358 | 0.2437 / 0.7583 | 0.5 / 1 | -0.516 / 0.9362 | 0.5 / 1 | 0.4344 / 0.9125 |

## Confusion Tables

### qwen-plus-latest (`aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 151 | 12 | 28 | 9 |
| ask | 0 | 80 | 0 | 0 |
| challenge | 17 | 10 | 170 | 3 |
| abstain | 0 | 0 | 1 | 79 |

### qwen-plus-latest (`aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_decision_first_guarded`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 178 | 8 | 4 | 10 |
| ask | 0 | 73 | 0 | 7 |
| challenge | 20 | 6 | 162 | 12 |
| abstain | 0 | 0 | 0 | 80 |

### qwen-plus-latest (`aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_critique_first`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 166 | 15 | 15 | 4 |
| ask | 0 | 80 | 0 | 0 |
| challenge | 12 | 13 | 171 | 4 |
| abstain | 0 | 0 | 7 | 73 |
