# Day-1 External API Baselines (Expanded Canonical Split)

## Main Table

| Model | Family | Style | Overall Utility | Action Acc. | Answer EM | Answer Contains | Over-Answer Rate | Ask Prec. | Challenge Prec. | Abstain Prec. | JSON Parse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen-turbo | Qwen API | api | 0.0353 | 0.8393 | 0 | 0.655 | 0.05 | 0.8333 | 0.9017 | 0.7129 | 0.7625 |
| gpt-4o-mini | OpenAI API | api | 0.0799 | 0.7679 | 0 | 0.45 | 0.0089 | 0.5674 | 0.7357 | 0.9524 | 0.8946 |
| gpt-4.1-mini | OpenAI API | api | 0.0558 | 0.8857 | 0 | 0.67 | 0.0411 | 0.7921 | 0.8936 | 1 | 0.85 |
| qwen-plus-latest | Qwen API | api | 0.1571 | 0.8571 | 0.16 | 0.62 | 0.0304 | 0.7843 | 0.8543 | 0.8681 | 0.8054 |
| gpt-5-chat-latest | OpenAI API | api | 0.0442 | 0.9286 | 0 | 0.765 | 0.0625 | 0.9412 | 1 | 1 | 0.8554 |

## Per-Slice Table

| Model | Answerable | False Premise | Stale Premise | Conflicting Evidence | Ambiguous Intent | Insufficient Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| qwen-turbo | -0.5 / 0.8396 | 0.15 / 0.7 | 0.35 / 0.9 | -0.5027 / 0.7766 | 0.5 / 1 | 0.425 / 0.9 |
| gpt-4o-mini | -0.4269 / 0.6509 | 0.2625 / 0.725 | 0.5 / 1 | -0.6543 / 0.3617 | 0.5 / 1 | 0.5 / 1 |
| gpt-4.1-mini | -0.4953 / 0.9057 | 0.1812 / 0.75 | 0.4625 / 0.975 | -0.5372 / 0.8298 | 0.5 / 1 | 0.4437 / 0.925 |
| qwen-plus-latest | -0.4835 / 0.7642 | 0.2313 / 0.7667 | 0.4625 / 0.975 | -0.0505 / 0.7447 | 0.5 / 1 | 0.4906 / 0.9875 |
| gpt-5-chat-latest | -0.4976 / 0.9906 | 0.0375 / 0.675 | 0.5 / 1 | -0.5 / 1 | 0.5 / 1 | 0.5 / 1 |

## Confusion Tables

### qwen-turbo (`aihubmix_qwenturbo_day1_expanded_dev_with_answer_topup`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 162 | 11 | 12 | 15 |
| ask | 0 | 80 | 0 | 0 |
| challenge | 28 | 2 | 156 | 14 |
| abstain | 0 | 3 | 5 | 72 |

### gpt-4o-mini (`aihubmix_gpt4omini_day1_expanded_dev_with_answer_topup`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 103 | 33 | 60 | 4 |
| ask | 0 | 80 | 0 | 0 |
| challenge | 5 | 28 | 167 | 0 |
| abstain | 0 | 0 | 0 | 80 |

### gpt-4.1-mini (`aihubmix_gpt41mini_day1_expanded_dev_with_answer_topup`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 174 | 7 | 19 | 0 |
| ask | 0 | 80 | 0 | 0 |
| challenge | 23 | 9 | 168 | 0 |
| abstain | 0 | 5 | 1 | 74 |

### qwen-plus-latest (`aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 151 | 12 | 28 | 9 |
| ask | 0 | 80 | 0 | 0 |
| challenge | 17 | 10 | 170 | 3 |
| abstain | 0 | 0 | 1 | 79 |

### gpt-5-chat-latest (`aihubmix_gpt5chatlatest_day1_expanded_dev_with_answer_topup`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 199 | 1 | 0 | 0 |
| ask | 0 | 80 | 0 | 0 |
| challenge | 35 | 4 | 161 | 0 |
| abstain | 0 | 0 | 0 | 80 |
