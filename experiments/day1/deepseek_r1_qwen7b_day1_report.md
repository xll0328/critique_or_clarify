# DeepSeek-R1-Distill-Qwen-7B on Day-1

## Run Metadata

| Field | Value |
| --- | --- |
| Date | `unknown` |
| Model | `DeepSeek-R1-Distill-Qwen-7B` |
| GPUs | `CUDA_VISIBLE_DEVICES=2` |
| Prompt format | corrected user-only action-selection JSON |
| Max new tokens | `180` |
| Temperature | `0.6` |
| Local snapshot | `/data/sony/model_cache_reasoning/DeepSeek-R1-Distill-Qwen-7B` |

## Main Metrics

| Split | N | Utility | Action Acc. | Answer EM | Answer Contains | Over-Answer | JSON Parse |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `day1_quick` | `36` | `-0.4583` | `0.4722` | `0` | `0.4167` | `0.0833` | `0.0833` |
| `day1_dev` | `120` | `-0.4313` | `0.3667` | `0` | `0.3125` | `0.05` | `0.0583` |

## Per-Slice Metrics on `day1_dev`

| Slice | Count | Utility | Action Acc. | Answer EM | Answer Contains | Over-Answer Rate | JSON Parse Rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `false_premise` | `40` | `-0.2875` | `0.1` | `0` | `0` | `0.15` | `0.025` |
| `conflicting_evidence` | `40` | `-0.5` | `0.8` | `0` | `0.575` | `0` | `0.15` |
| `answerable_control` | `40` | `-0.5062` | `0.2` | `0` | `0.05` | `0` | `0` |

## Confusion Notes

- `pred_action_counts`: `{"abstain": 69, "answer": 46, "challenge": 5}`
- `answer -> abstain`: `39`
- `challenge -> abstain`: `30`
- `challenge -> answer`: `6`
- `answer -> challenge`: `1`

## Qualitative Read

1. Output formatting is still a major bottleneck: most predictions are parsed through the fallback path rather than valid JSON.
2. `false_premise` remains a key calibration test: dev action accuracy is `0.1` with over-answer rate `0.15`.
3. `conflicting_evidence` is easier than defective-premise correction here, reaching `0.8` action accuracy on `day1_dev`.
4. `answerable_control` is still not saturated: dev action accuracy is `0.2`, which means the model still hesitates on clean answerable items.
5. Relative to `day1_quick`, the dev split changes action accuracy by `-0.1055` and keeps the same qualitative ranking across slices, so the pattern is not a tiny-subset artifact.

## Representative Failures

1. `false_premise`: the model predicted `abstain` instead of `challenge` on `pcbench-challenge-844`.
2. `conflicting_evidence`: the model chose the correct action `answer` on `qacc-dev-287`, but the sampled row still failed a content or parsing criterion.
3. `answerable_control`: the model predicted `abstain` instead of `answer` on `pcbench-answer-501`.

## Interpretation

- The main dev decision metric is `avg_utility=-0.4313` with `action_accuracy=0.3667`, so this run is informative even when strict answer exact match stays low.
- The central tradeoff is between defective-premise calibration and clean-answer willingness: `false_premise` sits at `0.1` action accuracy while `answerable_control` sits at `0.2`.
- Because both quick and dev are available, this report can distinguish stable behavior from subset noise without relying only on the tiny split.
