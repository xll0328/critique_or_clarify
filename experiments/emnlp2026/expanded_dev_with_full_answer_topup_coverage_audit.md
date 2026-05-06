# Benchmark Expansion Coverage Audit

Status: generated coverage audit for upgrading the Day-1 pilot into an oral-level evidence bundle. Targets are planning thresholds, not claims that the data already exists.

## Current Split Coverage

| Split | Rows | Unique IDs | Actions | Slices |
| --- | ---: | ---: | --- | --- |
| `data/processed/emnlp2026_expanded_dev_with_full_answer_topup.jsonl` | 600 | 600 | `answer`=240, `ask`=80, `challenge`=200, `abstain`=80 | `answerable_control`=120, `false_premise`=120, `stale_premise`=80, `conflicting_evidence`=120, `ambiguous_intent`=80, `insufficient_evidence`=80 |

## Combined Unique Coverage

- Input rows across audited splits: `600`
- Unique example IDs: `600`
- Duplicate IDs across audited splits: `0`
- Action coverage: `answer`=240, `ask`=80, `challenge`=200, `abstain`=80
- Slice coverage: `answerable_control`=120, `false_premise`=120, `stale_premise`=80, `conflicting_evidence`=120, `ambiguous_intent`=80, `insufficient_evidence`=80

## Oral-Level Expansion Gaps

- Unique-example target: `500`; current `600`; gap `0`.

### Action Gaps

| Action | Current | Target | Gap |
| --- | ---: | ---: | ---: |
| `answer` | 240 | 200 | 0 |
| `ask` | 80 | 80 | 0 |
| `challenge` | 200 | 200 | 0 |
| `abstain` | 80 | 80 | 0 |

### Slice Gaps

| Slice | Current | Target | Gap |
| --- | ---: | ---: | ---: |
| `answerable_control` | 120 | 120 | 0 |
| `false_premise` | 120 | 120 | 0 |
| `stale_premise` | 80 | 80 | 0 |
| `conflicting_evidence` | 120 | 120 | 0 |
| `ambiguous_intent` | 80 | 80 | 0 |
| `insufficient_evidence` | 80 | 80 | 0 |

## Priority Build Queue

| Priority | Dimension | Name | Current | Target | Gap |
| ---: | --- | --- | ---: | ---: | ---: |

## Interpretation

- Candidate-augmented scale reaches the current 500-example planning target, but remains non-paper-facing until human validation and promotion.
- Action-level candidate targets are currently met across all four actions.
- Slice-level candidate targets are currently met across all tracked slices.
