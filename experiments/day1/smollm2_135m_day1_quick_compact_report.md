# SmolLM2-135M on Day-1 Quick with Compact Prompt

## Run Metadata

| Field | Value |
| --- | --- |
| Date | `2026-04-23` |
| Model | `HuggingFaceTB/SmolLM2-135M-Instruct` |
| GPUs | `CUDA_VISIBLE_DEVICES=7` |
| Data | `data/processed/day1_quick.jsonl` |
| Prompt format | compact action-selection JSON |
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
| answerable_control | `12` | `-0.5` | `0.0` | `0.0` | `0.0` | `0.0` |
| false_premise | `12` | `-0.25` | `0.0` | `0.0` | `0.0` | `0.0` |
| conflicting_evidence | `12` | `-0.5` | `0.0` | `0.0` | `0.0` | `0.0` |

## Confusion Notes

- `answer -> abstain`: `24`
- `challenge -> abstain`: `12`
- `pred_action_counts`: `{"abstain": 36}`
- `parsed_as_counts`: `{"fallback": 36}`

## Interpretation

- Compact prompting did not improve structure following or action prediction at all.
- The weakest baseline fails before meaningful policy selection, even when prompt verbosity is reduced.
- This makes the `135M` result a genuine lower bound rather than an artifact of prompt length.
