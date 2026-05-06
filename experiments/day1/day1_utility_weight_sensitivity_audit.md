# Day-1 Utility Weight Sensitivity Audit

Status: generated utility-weight sensitivity audit from saved prediction JSONL files.

Interpretation: this audit checks whether the main model-comparison story depends on one utility weighting. It does not replace the paper's default metric.

| Scheme | Best Overall | Best Instruct | Best Reasoning | Best Reasoning - Best Instruct |
| --- | --- | --- | --- | ---: |
| paper_default | Qwen2.5-1.5B-Instruct | Qwen2.5-1.5B-Instruct | DeepSeek-R1-Distill-Qwen-7B | -0.2084 |
| overanswer_heavy | Qwen2.5-1.5B-Instruct | Qwen2.5-1.5B-Instruct | DeepSeek-R1-Distill-Qwen-7B | -0.1917 |
| caution_heavy | Qwen2.5-1.5B-Instruct | Qwen2.5-1.5B-Instruct | DeepSeek-R1-Distill-Qwen-7B | -0.2354 |
| flat_action | Qwen2.5-1.5B-Instruct | Qwen2.5-1.5B-Instruct | DeepSeek-R1-Distill-Qwen-7B | -0.6 |

## Per-Scheme Rankings

### paper_default

| Rank | Run | Family | Avg Utility |
| ---: | --- | --- | ---: |
| 1 | Qwen2.5-1.5B-Instruct | instruct | -0.2229 |
| 2 | Qwen2.5-Coder-7B-Instruct | instruct | -0.2792 |
| 3 | DeepSeek-R1-Distill-Qwen-7B | reasoning | -0.4313 |
| 4 | Qwen2.5-0.5B-Instruct | instruct | -0.4354 |
| 5 | DeepSeek-R1-Distill-Qwen-1.5B | reasoning | -0.5125 |

### overanswer_heavy

| Rank | Run | Family | Avg Utility |
| ---: | --- | --- | ---: |
| 1 | Qwen2.5-1.5B-Instruct | instruct | -0.2271 |
| 2 | Qwen2.5-Coder-7B-Instruct | instruct | -0.2554 |
| 3 | DeepSeek-R1-Distill-Qwen-7B | reasoning | -0.4188 |
| 4 | Qwen2.5-0.5B-Instruct | instruct | -0.4267 |
| 5 | DeepSeek-R1-Distill-Qwen-1.5B | reasoning | -0.5583 |

### caution_heavy

| Rank | Run | Family | Avg Utility |
| ---: | --- | --- | ---: |
| 1 | Qwen2.5-1.5B-Instruct | instruct | -0.2792 |
| 2 | Qwen2.5-Coder-7B-Instruct | instruct | -0.3333 |
| 3 | Qwen2.5-0.5B-Instruct | instruct | -0.5146 |
| 4 | DeepSeek-R1-Distill-Qwen-7B | reasoning | -0.5146 |
| 5 | DeepSeek-R1-Distill-Qwen-1.5B | reasoning | -0.5833 |

### flat_action

| Rank | Run | Family | Avg Utility |
| ---: | --- | --- | ---: |
| 1 | Qwen2.5-1.5B-Instruct | instruct | -0.3333 |
| 2 | Qwen2.5-Coder-7B-Instruct | instruct | -0.6667 |
| 3 | DeepSeek-R1-Distill-Qwen-7B | reasoning | -0.9333 |
| 4 | DeepSeek-R1-Distill-Qwen-1.5B | reasoning | -0.9833 |
| 5 | Qwen2.5-0.5B-Instruct | instruct | -1 |

## Reading Guide

- `paper_default` matches the paper's current asymmetric utility scheme.
- `overanswer_heavy` penalizes direct answers on non-answer gold examples more strongly.
- `caution_heavy` penalizes unnecessary ask/abstain/challenge on answerable examples more strongly.
- `flat_action` ignores graded harm and rewards only action correctness.
- If the best reasoning row overtakes the best instruct row under a scheme, the reasoning-model claim needs to be weakened or reanalyzed.
