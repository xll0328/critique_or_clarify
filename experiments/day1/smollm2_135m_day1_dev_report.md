# SmolLM2-135M on Day-1 Dev

## Run Metadata

| Field | Value |
| --- | --- |
| Date | `2026-04-23` |
| Model | `HuggingFaceTB/SmolLM2-135M-Instruct` |
| GPUs | `CUDA_VISIBLE_DEVICES=2` |
| Data | `data/processed/day1_dev.jsonl` |
| Prompt format | action-selection JSON |
| Max new tokens | `120` |
| Temperature | `0.0` |

## Main Metrics

| Metric | Value |
| --- | --- |
| Overall utility | `-0.4167` |
| Action accuracy | `0.0` |
| Answer EM | `0.0` |
| Over-answer rate | `0.0` |
| JSON parse rate | `0.0` |

## Per-Slice Metrics

| Slice | Count | Utility | Action Acc. | Answer EM | Over-Answer Rate | JSON Parse Rate |
| --- | --- | --- | --- | --- | --- | --- |
| answerable_control | `40` | `-0.5` | `0.0` | `0.0` | `0.0` | `0.0` |
| false_premise | `40` | `-0.25` | `0.0` | `0.0` | `0.0` | `0.0` |
| conflicting_evidence | `40` | `-0.5` | `0.0` | `0.0` | `0.0` | `0.0` |

## Confusion Notes

- `answer -> abstain`: `80`
- `challenge -> abstain`: `40`
- `pred_action_counts`: `{"abstain": 120}`

## Qualitative Failures

1. Every output was parsed via the fallback route rather than valid JSON.
2. Raw generations were repetitive degenerate text such as `such as such as ...`.
3. The collapse was identical on clean controls and defect cases, so the model never reached task-specific reasoning.
4. Zero `over_answer_rate` here is not a sign of calibration; it is a side effect of total abstention collapse.
5. This run is a floor baseline for instruction following, not a competitive task baseline.

## Interpretation

- The benchmark is clearly non-trivial for weak models.
- The current prompt is strong enough to expose instruction-following collapse.
- The next informative comparison is a stronger instruct model that can at least emit structured outputs.

## Decision

- Continue as planned
- Pivot model choice upward before drawing any conclusion about action policy
- Keep the main prompt protocol, but consider a compact diagnostic prompt for weak-model ablations
