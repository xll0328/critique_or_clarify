# Human Validation Work Queue Summary

Queue: `_assets/human_validation_work_queue.csv`

Active work queue: `61 / 61` rows completed.

This summary tracks real human decisions only. AI prefill remains triage and is not a substitute for completed human validation.

## By Validation Type

| Validation Type | Rows |
| --- | --- |
| action_label_failure_claim | 2 |
| example_gold_label | 51 |
| matched_style_delta_claim | 2 |
| metric_claim | 3 |
| scale_delta_claim | 2 |
| split_accounting_claim | 1 |

## By Priority

| Priority | Rows |
| --- | --- |
| high | 37 |
| medium | 24 |

## Label Hygiene

- Invalid non-empty `human_decision` labels: `0`.
- Allowed labels: `accept, fix, needs_second_pass, reject`.
