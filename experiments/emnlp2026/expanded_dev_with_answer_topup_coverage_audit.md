# Benchmark Expansion Coverage Audit

Status: generated coverage audit for upgrading the Day-1 pilot into an oral-level evidence bundle. Targets are planning thresholds, not claims that the data already exists.

## Current Split Coverage

| Split | Rows | Unique IDs | Actions | Slices |
| --- | ---: | ---: | --- | --- |
| `data/processed/emnlp2026_expanded_dev_with_answer_topup.jsonl` | 560 | 560 | `answer`=200, `ask`=80, `challenge`=200, `abstain`=80 | `answerable_control`=106, `false_premise`=120, `stale_premise`=80, `conflicting_evidence`=94, `ambiguous_intent`=80, `insufficient_evidence`=80 |

## Combined Unique Coverage

- Input rows across audited splits: `560`
- Unique example IDs: `560`
- Duplicate IDs across audited splits: `0`
- Action coverage: `answer`=200, `ask`=80, `challenge`=200, `abstain`=80
- Slice coverage: `answerable_control`=106, `false_premise`=120, `stale_premise`=80, `conflicting_evidence`=94, `ambiguous_intent`=80, `insufficient_evidence`=80

## Oral-Level Expansion Gaps

- Unique-example target: `500`; current `560`; gap `0`.

### Action Gaps

| Action | Current | Target | Gap |
| --- | ---: | ---: | ---: |
| `answer` | 200 | 200 | 0 |
| `ask` | 80 | 80 | 0 |
| `challenge` | 200 | 200 | 0 |
| `abstain` | 80 | 80 | 0 |

### Slice Gaps

| Slice | Current | Target | Gap |
| --- | ---: | ---: | ---: |
| `answerable_control` | 106 | 120 | 14 |
| `false_premise` | 120 | 120 | 0 |
| `stale_premise` | 80 | 80 | 0 |
| `conflicting_evidence` | 94 | 120 | 26 |
| `ambiguous_intent` | 80 | 80 | 0 |
| `insufficient_evidence` | 80 | 80 | 0 |

## Priority Build Queue

| Priority | Dimension | Name | Current | Target | Gap |
| ---: | --- | --- | ---: | ---: | ---: |
| 1 | slice | `conflicting_evidence` | 94 | 120 | 26 |
| 2 | slice | `answerable_control` | 106 | 120 | 14 |

## Interpretation

- Candidate-augmented scale reaches the current 500-example planning target, but remains non-paper-facing until human validation and promotion.
- Action-level candidate targets are currently met across all four actions.
- The next expansion sprint should focus on `conflicting_evidence` (slice gap `26`), then continue down the priority queue.
