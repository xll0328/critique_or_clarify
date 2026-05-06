# Qwen2.5-Coder-7B-Instruct on Day-1

## Run Metadata

| Field | Value |
| --- | --- |
| Date | `2026-04-23` |
| Model | `Qwen/Qwen2.5-Coder-7B-Instruct` |
| GPUs | `CUDA_VISIBLE_DEVICES=2` |
| Prompt format | action-selection JSON |
| Max new tokens | `140` |
| Temperature | `0.0` |
| Local snapshot | `/data/sony/.cache/modelscope/hub/models/Qwen/Qwen2___5-Coder-7B-Instruct` |

## Main Metrics

| Split | N | Utility | Action Acc. | Answer EM | Answer Contains | Over-Answer | JSON Parse |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `day1_quick` | `36` | `-0.3264` | `0.5833` | `0.0` | `0.4167` | `0.0278` | `0.9722` |
| `day1_dev` | `120` | `-0.2792` | `0.6` | `0.025` | `0.475` | `0.0083` | `0.9417` |

## Per-Slice Metrics on `day1_dev`

| Slice | Count | Utility | Action Acc. | Answer EM | Answer Contains | Over-Answer Rate | JSON Parse Rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `false_premise` | `40` | `0.0688` | `0.45` | `0.0` | `0.0` | `0.025` | `0.95` |
| `conflicting_evidence` | `40` | `-0.5` | `1.0` | `0.0` | `0.75` | `0.0` | `1.0` |
| `answerable_control` | `40` | `-0.4062` | `0.35` | `0.05` | `0.2` | `0.0` | `0.875` |

## Progression vs Earlier Baselines on `day1_dev`

| Run | Action Acc. | Utility | JSON Parse | False Premise Acc. | Conflicting Evidence Acc. | Answerable Control Acc. |
| --- | --- | --- | --- | --- | --- | --- |
| `smollm2_135m_day1_dev` | `0.0` | `-0.4167` | `0.0` | `0.0` | `0.0` | `0.0` |
| `qwen25_05b_day1_dev` | `0.35` | `-0.4354` | `0.0667` | `0.0` | `0.625` | `0.425` |
| `qwen25_coder_7b_day1_dev` | `0.6` | `-0.2792` | `0.9417` | `0.45` | `1.0` | `0.35` |

## Confusion Notes

- `pred_action_counts`: `{"abstain": 32, "answer": 55, "challenge": 19, "ask": 14}`
- `answer -> answer`: `54`
- `answer -> abstain`: `21`
- `answer -> ask`: `4`
- `challenge -> challenge`: `18`
- `challenge -> abstain`: `11`
- `challenge -> ask`: `10`

## Qualitative Read

1. This is the first model that is no longer bottlenecked by output formatting. Almost every prediction is valid JSON, so the remaining errors are mostly policy or content errors rather than parser failures.
2. `false_premise` is now partially recovered. The model reaches `0.45` action accuracy and even positive average utility on that slice, which means direct challenge is no longer absent from the behavior.
3. `conflicting_evidence` becomes an action-selection success story but not a final-answer success story. The model chooses `answer` correctly on every dev item in that slice, yet strict `answer_em` stays at `0.0`; the new `answer_contains_rate=0.75` shows many of those are still short-answer matching misses rather than total factual collapse.
4. `answerable_control` remains a major weakness. Even at 7B, the model often abstains on solvable math-style prompts instead of completing the derivation or extracting the final answer.
5. Over-answering is nearly gone, so the residual challenge is not reckless answering but excessive hesitation on answerable items and incomplete recovery on false premises.

## Answerable-Control Error Audit

- All `26` action errors on `answerable_control` come from `PCBench`.
- The failure mode is overwhelmingly hesitation: `21` errors are `abstain`, `4` are `ask`, and only `1` is an incorrect `challenge`.
- The misses are mostly dense symbolic prompts: `23/26` contain heavy LaTeX, and several are long proof-style or combinatorics items.
- Partial-solution scaffolding appears to help. Among the `14` correct answerable-control items, `12` include a `Part of My Solution` or `### Solution` segment, while only `8/26` of the wrong items do.
- Chinese prompts are somewhat overrepresented among the misses (`8/26` wrong versus `4/14` correct), but the stronger signal is mathematical-density plus missing solution scaffolding.

## Representative Failures

1. `false_premise`: the model still sometimes answers the local question instead of objecting to the broken solution setup, e.g. `pcbench-challenge-962`.
2. `false_premise`: on harder proof-style prompts it can retreat to `abstain` rather than commit to a correction, e.g. `pcbench-challenge-249`.
3. `answerable_control`: several long math or theorem-completion items are treated as missing-evidence problems instead of solvable tasks, e.g. `pcbench-answer-501`.

## Interpretation

- The benchmark signal is now clearly substantive: better models improve both JSON compliance and `challenge` behavior without any prompt change.
- `false_premise` remains hard even after the formatting problem is nearly solved, which strengthens its value as the benchmark's main differentiating slice.
- The next model comparison should focus on whether reasoning-oriented models can push `false_premise` above `0.45` while also reducing unnecessary abstention on LaTeX-heavy answerable controls.
- Strict `answer_em` should not be the only answer-quality metric in reporting. For short factual answers, `answer_contains_rate` is a necessary companion metric.
