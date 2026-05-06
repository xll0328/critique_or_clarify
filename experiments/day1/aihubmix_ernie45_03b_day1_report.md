# aihubmix_ernie45_03b_day1_dev on Day-1

## Run Metadata

| Field | Value |
| --- | --- |
| Date | `unknown` |
| Model | `ernie-4.5-0.3b` |
| GPUs | `unknown` |
| Prompt format | decision_first |
| Max new tokens | `64` |
| Temperature | `0.0` |

## Main Metrics

| Split | N | Utility | Action Acc. | Answer EM | Answer Contains | Over-Answer | JSON Parse |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `day1_quick` | `36` | `-0.5208` | `0.4722` | `0` | `0.1667` | `0.1944` | `0.3889` |
| `day1_dev` | `120` | `-0.5813` | `0.4917` | `0` | `0.1125` | `0.2667` | `0.3167` |

## Per-Slice Metrics on `day1_dev`

| Slice | Count | Utility | Action Acc. | Answer EM | Answer Contains | Over-Answer Rate | JSON Parse Rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `false_premise` | `40` | `-0.85` | `0` | `0` | `0` | `0.8` | `0.125` |
| `conflicting_evidence` | `40` | `-0.4062` | `0.55` | `0` | `0.125` | `0` | `0.5` |
| `answerable_control` | `40` | `-0.4875` | `0.925` | `0` | `0.1` | `0` | `0.325` |

## Confusion Notes

- `pred_action_counts`: `{"ask": 23, "answer": 91, "abstain": 6}`
- `challenge -> answer`: `32`
- `answer -> ask`: `17`
- `challenge -> ask`: `6`
- `answer -> abstain`: `4`
- `challenge -> abstain`: `2`

## Qualitative Read

1. Output formatting is partially recovered but still nontrivial, so policy quality and format-following are still entangled.
2. `false_premise` remains a key calibration test: dev action accuracy is `0` with over-answer rate `0.8`.
3. `conflicting_evidence` is easier than defective-premise correction here, reaching `0.55` action accuracy on `day1_dev`.
4. `answerable_control` is still not saturated: dev action accuracy is `0.925`, which means the model still hesitates on clean answerable items.
5. Relative to `day1_quick`, the dev split changes action accuracy by `0.0195` and keeps the same qualitative ranking across slices, so the pattern is not a tiny-subset artifact.

## Interpretation

- The main dev decision metric is `avg_utility=-0.5813` with `action_accuracy=0.4917`, so this run is informative even when strict answer exact match stays low.
- The central tradeoff is between defective-premise calibration and clean-answer willingness: `false_premise` sits at `0` action accuracy while `answerable_control` sits at `0.925`.
- Because both quick and dev are available, this report can distinguish stable behavior from subset noise without relying only on the tiny split.
