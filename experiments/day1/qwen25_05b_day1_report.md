# Qwen2.5-0.5B-Instruct on Day-1

## Run Metadata

| Field | Value |
| --- | --- |
| Date | `2026-04-23` |
| Model | `Qwen/Qwen2.5-0.5B-Instruct` |
| GPUs | `CUDA_VISIBLE_DEVICES=2` |
| Prompt format | action-selection JSON |
| Max new tokens | `140` |
| Temperature | `0.0` |
| Local snapshot | `/data/sony/.cache/huggingface/hub/models--Qwen--Qwen2.5-0.5B-Instruct/snapshots/7ae557604adf67be50417f59c2c2f167def9a775` |

## Main Metrics

| Split | N | Utility | Action Acc. | Answer EM | Over-Answer | JSON Parse |
| --- | --- | --- | --- | --- | --- | --- |
| `day1_quick` | `36` | `-0.5278` | `0.4444` | `0.0` | `0.1667` | `0.0833` |
| `day1_dev` | `120` | `-0.4354` | `0.35` | `0.0` | `0.075` | `0.0667` |

## Per-Slice Metrics on `day1_dev`

| Slice | Count | Utility | Action Acc. | Answer EM | Over-Answer Rate | JSON Parse Rate |
| --- | --- | --- | --- | --- | --- | --- |
| `false_premise` | `40` | `-0.4188` | `0.0` | `0.0` | `0.225` | `0.125` |
| `conflicting_evidence` | `40` | `-0.4688` | `0.625` | `0.0` | `0.0` | `0.0` |
| `answerable_control` | `40` | `-0.4188` | `0.425` | `0.0` | `0.0` | `0.075` |

## Confusion Notes

- `pred_action_counts`: `{"abstain": 29, "ask": 40, "answer": 51}`
- `answer -> answer`: `42`
- `answer -> ask`: `18`
- `answer -> abstain`: `20`
- `challenge -> ask`: `22`
- `challenge -> answer`: `9`
- `challenge -> abstain`: `9`

## Qualitative Read

1. This is the first model that clears the "total collapse" floor baseline. It produces a meaningful mix of `answer`, `ask`, and `abstain` instead of defaulting to one action.
2. The benchmark is already separating error types. `conflicting_evidence` reaches `0.625` action accuracy on `day1_dev`, while `false_premise` remains at `0.0`, which means the model is much more willing to hedge than to directly challenge a bad premise.
3. Output formatting is still unreliable. More than `90%` of examples are parsed through the fallback path rather than valid JSON, so format-following remains a major bottleneck below the 1B scale.
4. `answerable_control` is only partially recovered. The model often chooses `ask` or `abstain` even when the item is straightforwardly answerable, especially on longer math prompts.
5. `over_answer_rate` drops relative to the quick split, but that is not a sign of strong calibration because the model still misses many answerable items and does not challenge false premises when it should.

## Representative Failures

1. `false_premise`: the model often answers the embedded sub-question instead of objecting to the faulty solution setup, e.g. `pcbench-challenge-962`.
2. `conflicting_evidence`: factual QA prompts can trigger fluent but corrupted answers with repeated tokens or fabricated entities, e.g. `qacc-dev-287`.
3. `answerable_control`: some clean math items are answered in prose but still miss the required action structure, or drift into low-quality repetition, e.g. `pcbench-answer-501`.

## Interpretation

- The task is not merely an instruction-format benchmark. Once the model is strong enough to move beyond total collapse, the `challenge` decision itself becomes a clear source of failure.
- `false_premise` looks like the hardest slice so far and is a strong candidate for the benchmark's core novelty claim.
- A stronger next baseline should test whether the gap is mainly capability, calibration, or reluctance to contradict the user.

## Next Moves

- Add a stronger instruct baseline in the `1.5B-3B` range.
- Add a reasoning-style baseline to test whether explicit deliberation helps `challenge` behavior.
- Keep fallback parsing in the evaluator, but report JSON parse rate prominently because format failure still masks policy quality for small models.
