# Qwen2.5-1.5B Quick+Stale Intervention Pilot

This pilot compares the original Qwen2.5-1.5B quick+stale run with four lightweight prompt interventions on the same 40-example split.

## Readout

- `decision_first` is the only intervention that should remain in the main sprint: it improves utility from `-0.2188` to `-0.1375`, action accuracy from `0.775` to `0.85`, and over-answer rate from `0.05` to `0.0`.
- `critique_first` is a negative ablation: it over-challenges answerable and conflicting-evidence examples, dropping action accuracy to `0.4`.
- `decision_first_guarded` and `decision_first_balanced` show that adding more boundary rules is not automatically better. Both reduce over-answering, but both damage answerable/control or conflict handling too much for promotion.
- Current conclusion: the paper can claim a promising decision-first calibration lever, but not a solved method. The next method attempt should be a controller or reranker, not another longer prompt.

## Main Table

| Model | Family | Style | Overall Utility | Action Acc. | Answer EM | Answer Contains | Over-Answer Rate | Ask Prec. | Challenge Prec. | Abstain Prec. | JSON Parse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen2.5-1.5B-Instruct | Qwen2.5 | instruct | -0.2188 | 0.775 | 0 | 0.4583 | 0.05 | 0 | 0.6667 | 0 | 0.825 |
| Qwen2.5-1.5B-Instruct | Qwen2.5 | instruct | -0.1375 | 0.85 | 0 | 0.4583 | 0 | 0 | 0.7273 | 0 | 0.85 |
| Qwen2.5-1.5B-Instruct | Qwen2.5 | instruct | -0.2812 | 0.4 | 0 | 0 | 0.025 | 0 | 0.3947 | 0 | 0.875 |
| Qwen2.5-1.5B-Instruct | Qwen2.5 | instruct | -0.1812 | 0.625 | 0 | 0.3333 | 0 | 0 | 0.7222 | 0 | 0.875 |
| Qwen2.5-1.5B-Instruct | Qwen2.5 | instruct | -0.1313 | 0.375 | 0 | 0 | 0 | 0 | 0.5357 | 0 | 0.8 |

## Per-Slice Table

| Model | Answerable | False Premise | Stale Premise | Conflicting Evidence |
| --- | --- | --- | --- | --- |
| Qwen2.5-1.5B-Instruct | -0.6458 / 0.4167 | 0.375 / 0.9167 | 0.125 / 0.75 | -0.5 / 1 |
| Qwen2.5-1.5B-Instruct | -0.625 / 0.5 | 0.5 / 1 | 0.5 / 1 | -0.5 / 1 |
| Qwen2.5-1.5B-Instruct | -0.7292 / 0.0833 | 0.375 / 0.9167 | 0.5 / 1 | -0.75 / 0 |
| Qwen2.5-1.5B-Instruct | -0.5417 / 0.1667 | 0.3125 / 0.75 | 0.5 / 1 | -0.5417 / 0.8333 |
| Qwen2.5-1.5B-Instruct | -0.625 / 0 | 0.4375 / 0.9167 | 0.5 / 1 | -0.4167 / 0 |

## Confusion Tables

### Qwen2.5-1.5B-Instruct (`qwen25_15b_day1_quick_plus_stale_grounded`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 17 | 0 | 7 | 0 |
| ask | 0 | 0 | 0 | 0 |
| challenge | 2 | 0 | 14 | 0 |
| abstain | 0 | 0 | 0 | 0 |

### Qwen2.5-1.5B-Instruct (`qwen25_15b_day1_quick_plus_stale_decision_first`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 18 | 0 | 6 | 0 |
| ask | 0 | 0 | 0 | 0 |
| challenge | 0 | 0 | 16 | 0 |
| abstain | 0 | 0 | 0 | 0 |

### Qwen2.5-1.5B-Instruct (`qwen25_15b_day1_quick_plus_stale_critique_first`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 1 | 0 | 23 | 0 |
| ask | 0 | 0 | 0 | 0 |
| challenge | 1 | 0 | 15 | 0 |
| abstain | 0 | 0 | 0 | 0 |

### Qwen2.5-1.5B-Instruct (`qwen25_15b_day1_quick_plus_stale_decision_first_guarded`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 12 | 1 | 5 | 6 |
| ask | 0 | 0 | 0 | 0 |
| challenge | 0 | 1 | 13 | 2 |
| abstain | 0 | 0 | 0 | 0 |

### Qwen2.5-1.5B-Instruct (`qwen25_15b_day1_quick_plus_stale_decision_first_balanced`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 0 | 11 | 13 | 0 |
| ask | 0 | 0 | 0 | 0 |
| challenge | 0 | 1 | 15 | 0 |
| abstain | 0 | 0 | 0 | 0 |
