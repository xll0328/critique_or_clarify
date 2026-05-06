# Day-1 Baseline Comparison

## Main Table

| Model | Family | Style | Overall Utility | Action Acc. | Answer EM | Answer Contains | Over-Answer Rate | Ask Prec. | Challenge Prec. | Abstain Prec. | JSON Parse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SmolLM2-135M-Instruct | SmolLM2 | instruct | -0.4167 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Qwen2.5-0.5B-Instruct | Qwen2.5 | instruct | -0.4354 | 0.35 | 0 | 0.05 | 0.075 | 0 | 0 | 0 | 0.0667 |
| Qwen2.5-Coder-7B-Instruct | Qwen2.5-Coder | instruct | -0.2792 | 0.6 | 0.025 | 0.475 | 0.0083 | 0 | 0.9474 | 0 | 0.9417 |
| DeepSeek-R1-Distill-Qwen-1.5B | DeepSeek/Qwen | reasoning | -0.5125 | 0.3833 | 0.0125 | 0.15 | 0.15 | 0 | 0 | 0 | 0.0083 |

## External API Baseline (decision_first, max_tokens=64)

### Quick / Day1 Dev (Legacy Local Split)

| Model | Data | Overall Utility | Action Acc. | Answer Contains | Over-Answer Rate | JSON Parse | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `qwen-turbo` | `day1_quick` | `-0.4236` | `0.7222` | `0.5417` | `0.1389` | `0.5` | baseline complete |
| `ernie-4.5-0.3b` | `day1_quick` | `-0.5208` | `0.4722` | `0.1667` | `0.1944` | `0.3889` | baseline complete |
| `qwen-turbo` | `day1_dev` | `-0.4396` | `0.6583` | `0.5125` | `0.1333` | `0.6` | baseline complete |
| `ernie-4.5-0.3b` | `day1_dev` | `-0.5813` | `0.4917` | `0.1125` | `0.2667` | `0.3167` | baseline complete |

### Canonical Expanded Split (`emnlp2026_expanded_dev_with_answer_topup`, n=560)

| Model | Input Price | Output Price | Overall Utility | Action Acc. | Answer Contains | Over-Answer Rate | JSON Parse | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `qwen-turbo` | `0.046` | `0.092` | `0.0353` | `0.8393` | `0.6550` | `0.0500` | `0.7625` | canonical complete |
| `gpt-4o-mini` | `0.1500` | `0.6000` | `0.0799` | `0.7679` | `0.4500` | `0.0089` | `0.8946` | canonical complete |
| `gpt-4.1-mini` | `0.1500` | `0.6000` | `0.0558` | `0.8857` | `0.6700` | `0.0411` | `0.8500` | canonical complete |
| `qwen-plus-latest` | `0.1100` | `0.2750` | `0.1571` | `0.8571` | `0.6200` | `0.0304` | `0.8054` | canonical complete |

See `experiments/day1/day1_api_expanded_baseline_comparison.md` for per-slice and confusion details.

## Per-Slice Table

| Model | Answerable | False Premise | Conflicting Evidence |
| --- | --- | --- | --- |
| SmolLM2-135M-Instruct | -0.5 / 0 | -0.25 / 0 | -0.5 / 0 |
| Qwen2.5-0.5B-Instruct | -0.4188 / 0.425 | -0.4188 / 0 | -0.4688 / 0.625 |
| Qwen2.5-Coder-7B-Instruct | -0.4062 / 0.35 | 0.0688 / 0.45 | -0.5 / 1 |
| DeepSeek-R1-Distill-Qwen-1.5B | -0.4688 / 0.5 | -0.5875 / 0 | -0.4813 / 0.65 |
| qwen-turbo (day1_dev) | -0.4938 / 0.675 | -0.325 / 0.3 | -0.5 / 1 |
| ernie-4.5-0.3b (day1_dev) | -0.4875 / 0.925 | -0.85 / 0 | -0.4062 / 0.55 |

## Confusion Tables

### Qwen2.5-Coder-7B-Instruct (`qwen25_coder_7b_day1_dev`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 54 | 4 | 1 | 21 |
| ask | 0 | 0 | 0 | 0 |
| challenge | 1 | 10 | 18 | 11 |
| abstain | 0 | 0 | 0 | 0 |

### DeepSeek-R1-Distill-Qwen-1.5B (`deepseek_r1_qwen15b_day1_dev_useronlyfixed_reparsed`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 46 | 4 | 2 | 28 |
| ask | 0 | 0 | 0 | 0 |
| challenge | 18 | 1 | 0 | 21 |
| abstain | 0 | 0 | 0 | 0 |

### qwen-turbo (`aihubmix_qwenturbo_day1_dev`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 67 | 2 | 1 | 10 |
| ask | 0 | 0 | 0 | 0 |
| challenge | 16 | 1 | 12 | 11 |
| abstain | 0 | 0 | 0 | 0 |

### ernie-4.5-0.3b (`aihubmix_ernie45_03b_day1_dev`)

| Gold \\ Pred | answer | ask | challenge | abstain |
| --- | --- | --- | --- | --- |
| answer | 59 | 17 | 0 | 4 |
| ask | 0 | 0 | 0 | 0 |
| challenge | 32 | 6 | 0 | 2 |
| abstain | 0 | 0 | 0 | 0 |
