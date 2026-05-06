# Day-1 API Slice Breakdown

Date: 2026-05-06

Status: generated from saved metric JSON artifacts only. No new API calls, model runs, or human-validation fields are used.

## Takeaways

- This audit supports API-section integration, not a fine-grained model ranking. The paper-facing use is the coarse pattern that high pooled accuracy can still hide premise/evidence-boundary errors.
- All API rows have their weakest slice on a boundary slice (`all_hardest_slices_are_boundary=True`): `{"conflicting_evidence": 2, "false_premise": 3}`.
- The top pooled-accuracy row is `gpt-5-chat-latest` (`action_accuracy=0.9286`), but its weakest slice is `false_premise` (`action_accuracy=0.6750`).

## Overall Rows

| Model | N | Action Acc. | Avg Utility | JSON Parse | Over-answer | Boundary Over-answer | Hardest Slice | Hardest Acc. | Hardest Over-answer | Predicted Actions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | --- |
| `qwen-turbo` | 560 | 0.8393 | 0.0353 | 0.7625 | 0.0500 | 0.0953 | `false_premise` | 0.7000 | 0.1667 | `answer=190, ask=96, challenge=173, abstain=101` |
| `gpt-4o-mini` | 560 | 0.7679 | 0.0799 | 0.8946 | 0.0089 | 0.0170 | `conflicting_evidence` | 0.3617 | 0.0000 | `answer=108, ask=141, challenge=227, abstain=84` |
| `gpt-4.1-mini` | 560 | 0.8857 | 0.0558 | 0.8500 | 0.0411 | 0.0782 | `false_premise` | 0.7500 | 0.1750 | `answer=197, ask=101, challenge=188, abstain=74` |
| `qwen-plus-latest` | 560 | 0.8571 | 0.1571 | 0.8054 | 0.0304 | 0.0578 | `conflicting_evidence` | 0.7447 | 0.0000 | `answer=168, ask=102, challenge=199, abstain=91` |
| `gpt-5-chat-latest` | 560 | 0.9286 | 0.0442 | 0.8554 | 0.0625 | 0.1191 | `false_premise` | 0.6750 | 0.2917 | `answer=234, ask=85, challenge=161, abstain=80` |

## Per-Slice Action Accuracy

| Model | `answerable_control` | `false_premise` | `stale_premise` | `conflicting_evidence` | `ambiguous_intent` | `insufficient_evidence` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `qwen-turbo` | 0.8396 | 0.7000 | 0.9000 | 0.7766 | 1.0000 | 0.9000 |
| `gpt-4o-mini` | 0.6509 | 0.7250 | 1.0000 | 0.3617 | 1.0000 | 1.0000 |
| `gpt-4.1-mini` | 0.9057 | 0.7500 | 0.9750 | 0.8298 | 1.0000 | 0.9250 |
| `qwen-plus-latest` | 0.7642 | 0.7667 | 0.9750 | 0.7447 | 1.0000 | 0.9875 |
| `gpt-5-chat-latest` | 0.9906 | 0.6750 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

## Boundary-Slice Over-answer Rates

| Model | `false_premise` | `stale_premise` | `conflicting_evidence` |
| --- | ---: | ---: | ---: |
| `qwen-turbo` | 16.67% | 10.00% | 0.00% |
| `gpt-4o-mini` | 4.17% | 0.00% | 0.00% |
| `gpt-4.1-mini` | 17.50% | 2.50% | 0.00% |
| `qwen-plus-latest` | 12.50% | 2.50% | 0.00% |
| `gpt-5-chat-latest` | 29.17% | 0.00% | 0.00% |

## Source Artifacts

- `outputs/day1/aihubmix_qwenturbo_day1_expanded_dev_with_answer_topup_metrics.json`
- `outputs/day1/aihubmix_gpt4omini_day1_expanded_dev_with_answer_topup_metrics.json`
- `outputs/day1/aihubmix_gpt41mini_day1_expanded_dev_with_answer_topup_metrics.json`
- `outputs/day1/aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_metrics.json`
- `outputs/day1/aihubmix_gpt5chatlatest_day1_expanded_dev_with_answer_topup_metrics.json`
