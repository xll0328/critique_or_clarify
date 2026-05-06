# Qwen2.5-1.5B-Instruct on Day-1

## Run Metadata

| Field | Value |
| --- | --- |
| Date | `unknown` |
| Model | `Qwen/Qwen2.5-1.5B-Instruct` |
| GPUs | `CUDA_VISIBLE_DEVICES=2` |
| Prompt format | action-selection JSON |
| Max new tokens | `140` |
| Temperature | `0.0` |
| Local snapshot | `/data/sony/model_cache/Qwen2.5-1.5B-Instruct` |

## Main Metrics

| Split | N | Utility | Action Acc. | Answer EM | Answer Contains | Over-Answer | JSON Parse |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `day1_quick` | `36` | `-0.2569` | `0.7778` | `0` | `0.4583` | `0.0278` | `0.8056` |
| `day1_dev` | `120` | `-0.2229` | `0.7667` | `0.0125` | `0.475` | `0.0083` | `0.8083` |

## Per-Slice Metrics on `day1_dev`

| Slice | Count | Utility | Action Acc. | Answer EM | Answer Contains | Over-Answer Rate | JSON Parse Rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `false_premise` | `40` | `0.4625` | `0.975` | `0` | `0` | `0.025` | `0.775` |
| `conflicting_evidence` | `40` | `-0.5062` | `0.975` | `0` | `0.75` | `0` | `0.975` |
| `answerable_control` | `40` | `-0.625` | `0.35` | `0.025` | `0.2` | `0` | `0.675` |

## Confusion Notes

- `pred_action_counts`: `{"challenge": 66, "answer": 54}`
- `answer -> challenge`: `27`
- `challenge -> answer`: `1`

## Qualitative Read

1. Output formatting is partially recovered but still nontrivial, so policy quality and format-following are still entangled.
2. `false_premise` remains a key calibration test: dev action accuracy is `0.975` with over-answer rate `0.025`.
3. `conflicting_evidence` is easier than defective-premise correction here, reaching `0.975` action accuracy on `day1_dev`.
4. `answerable_control` is still not saturated: dev action accuracy is `0.35`, which means the model still hesitates on clean answerable items.
5. Relative to `day1_quick`, the dev split changes action accuracy by `-0.0111` and keeps the same qualitative ranking across slices, so the pattern is not a tiny-subset artifact.

## Representative Failures

1. `false_premise`: the model predicted `answer` instead of `challenge` on `pcbench-challenge-671`.
2. `conflicting_evidence`: the model predicted `answer` instead of `answer` on `qacc-dev-287`.
3. `answerable_control`: the model predicted `answer` instead of `answer` on `pcbench-answer-671`.

## Interpretation

- The main dev decision metric is `avg_utility=-0.2229` with `action_accuracy=0.7667`, so this run is informative even when strict answer exact match stays low.
- The central tradeoff is between defective-premise calibration and clean-answer willingness: `false_premise` sits at `0.975` action accuracy while `answerable_control` sits at `0.35`.
- Because both quick and dev are available, this report can distinguish stable behavior from subset noise without relying only on the tiny split.
