# aihubmix_qwenturbo_day1_dev on Day-1

## Run Metadata

| Field | Value |
| --- | --- |
| Date | `unknown` |
| Model | `qwen-turbo` |
| GPUs | `unknown` |
| Prompt format | decision_first |
| Max new tokens | `64` |
| Temperature | `0.0` |

## Main Metrics

| Split | N | Utility | Action Acc. | Answer EM | Answer Contains | Over-Answer | JSON Parse |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `day1_quick` | `36` | `-0.4236` | `0.7222` | `0` | `0.5417` | `0.1389` | `0.5` |
| `day1_dev` | `120` | `-0.4396` | `0.6583` | `0` | `0.5125` | `0.1333` | `0.6` |

## Per-Slice Metrics on `day1_dev`

| Slice | Count | Utility | Action Acc. | Answer EM | Answer Contains | Over-Answer Rate | JSON Parse Rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `false_premise` | `40` | `-0.325` | `0.3` | `0` | `0` | `0.4` | `0.5` |
| `conflicting_evidence` | `40` | `-0.5` | `1` | `0` | `0.825` | `0` | `0.825` |
| `answerable_control` | `40` | `-0.4938` | `0.675` | `0` | `0.2` | `0` | `0.475` |

## Confusion Notes

- `pred_action_counts`: `{"challenge": 13, "answer": 83, "abstain": 21, "ask": 3}`
- `challenge -> answer`: `16`
- `challenge -> abstain`: `11`
- `answer -> abstain`: `10`
- `answer -> ask`: `2`
- `challenge -> ask`: `1`
- `answer -> challenge`: `1`

## Qualitative Read

1. Output formatting is partially recovered but still nontrivial, so policy quality and format-following are still entangled.
2. `false_premise` remains a key calibration test: dev action accuracy is `0.3` with over-answer rate `0.4`.
3. `conflicting_evidence` is easier than defective-premise correction here, reaching `1` action accuracy on `day1_dev`.
4. `answerable_control` is still not saturated: dev action accuracy is `0.675`, which means the model still hesitates on clean answerable items.
5. Relative to `day1_quick`, the dev split changes action accuracy by `-0.0639` and keeps the same qualitative ranking across slices, so the pattern is not a tiny-subset artifact.

## Interpretation

- The main dev decision metric is `avg_utility=-0.4396` with `action_accuracy=0.6583`, so this run is informative even when strict answer exact match stays low.
- The central tradeoff is between defective-premise calibration and clean-answer willingness: `false_premise` sits at `0.3` action accuracy while `answerable_control` sits at `0.675`.
- Because both quick and dev are available, this report can distinguish stable behavior from subset noise without relying only on the tiny split.
