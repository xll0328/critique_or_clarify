# Day-1 Integrity Dashboard

This dashboard tracks whether the current day-1 evidence is ready to support paper-facing claims.

## Blocking Gates

| Gate | State | Detail |
| --- | --- | --- |
| Human validation | pass | 61 / 61 rows completed |
| Human decision labels | pass | 0 invalid non-empty labels |
| DeepSeek-R1-Distill-Qwen-7B metrics | pass | dev and quick+stale metrics required for final scale/reasoning comparison |

## Model And Report Status

| Artifact | State | Progress | Detail |
| --- | --- | --- | --- |
| Qwen2.5-1.5B model | ready | 100.0% | 2.9 GB / 2.9 GB |
| DeepSeek-R1-Qwen-7B shard1 | ready | 100.0% | 8.0 GB / 8.0 GB |
| DeepSeek-R1-Qwen-7B shard2 | ready | 100.0% | 6.2 GB / 6.2 GB |
| Qwen2.5-1.5B dev metrics | ready | acc=0.7667 | utility=-0.2229 |
| Qwen2.5-1.5B quick+stale metrics | ready | acc=0.7750 | utility=-0.2188 |
| DeepSeek-R1-Qwen-7B dev metrics | ready | acc=0.3667 | utility=-0.4313 |
| DeepSeek-R1-Qwen-7B quick+stale metrics | ready | acc=0.4500 | utility=-0.4750 |
| Scale/reasoning report | comparison | Day-1 Scale And Reasoning Comparison | - |
| Scale/reasoning CI report | comparison | Day-1 Scale And Reasoning Comparison Bootstrap Confidence Intervals | - |
| Quick+stale report | comparison | Day-1 Quick Plus Stale Comparison | - |

## Paper-Facing Assets

| Asset | State | Path |
| --- | --- | --- |
| Scale/reasoning comparison | ready | `experiments/day1/day1_scale_reasoning_comparison.md` |
| Scale/reasoning CI report | ready | `experiments/day1/day1_scale_reasoning_ci.md` |
| Expanded stale-pool pilot | ready | `experiments/day1/day1_expanded_stale_pool_pilot.md` |
| Expanded stale-pool LaTeX table | ready | `experiments/day1/tables/day1_expanded_stale_pool_pilot_main.tex` |
| Action-label audit | ready | `experiments/day1/day1_expanded_stale_action_label_audit.md` |
| Action-label audit LaTeX table | ready | `experiments/day1/tables/day1_expanded_stale_action_label_audit_main.tex` |
| Human-validation queue | ready | `_assets/human_validation_work_queue.csv` |
| Human-validation packet index | ready | `_assets/human_validation_packets/index.md` |
| Codex expert validation review | ready | `_assets/codex_expert_validation_review.md` |
| Codex multi-pass validation review | ready | `_assets/codex_multipass_validation_review/summary.md` |
| Human-validation protocol | ready | `docs/human_validation_protocol.md` |

## Human Validation

- Active work queue: `61 / 61` rows completed.
- Pending rows: `0`.
- Invalid non-empty `human_decision` labels: `0`.
- Codex expert review: `61 / 61` rows accepted in `_assets/codex_expert_validation_review.csv`.
- Codex multi-pass review: `61 / 61` rows consensus-accepted across six passes.
- Human-validation is complete for the active queue; all rows have recorded human decisions.
