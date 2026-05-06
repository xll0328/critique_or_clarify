# Benchmark Expansion Coverage Audit

Status: generated coverage audit for upgrading the Day-1 pilot into an oral-level evidence bundle. Targets are planning thresholds, not claims that the data already exists.

## Current Split Coverage

| Split | Rows | Unique IDs | Actions | Slices |
| --- | ---: | ---: | --- | --- |
| `data/processed/emnlp2026_expanded_dev.jsonl` | 500 | 500 | `answer`=140, `ask`=80, `challenge`=200, `abstain`=80 | `answerable_control`=76, `false_premise`=120, `stale_premise`=80, `conflicting_evidence`=64, `ambiguous_intent`=80, `insufficient_evidence`=80 |

## Combined Unique Coverage

- Input rows across audited splits: `500`
- Unique example IDs: `500`
- Duplicate IDs across audited splits: `0`
- Action coverage: `answer`=140, `ask`=80, `challenge`=200, `abstain`=80
- Slice coverage: `answerable_control`=76, `false_premise`=120, `stale_premise`=80, `conflicting_evidence`=64, `ambiguous_intent`=80, `insufficient_evidence`=80

## Oral-Level Expansion Gaps

- Unique-example target: `500`; current `500`; gap `0`.

### Action Gaps

| Action | Current | Target | Gap |
| --- | ---: | ---: | ---: |
| `answer` | 140 | 200 | 60 |
| `ask` | 80 | 80 | 0 |
| `challenge` | 200 | 200 | 0 |
| `abstain` | 80 | 80 | 0 |

### Slice Gaps

| Slice | Current | Target | Gap |
| --- | ---: | ---: | ---: |
| `answerable_control` | 76 | 120 | 44 |
| `false_premise` | 120 | 120 | 0 |
| `stale_premise` | 80 | 80 | 0 |
| `conflicting_evidence` | 64 | 120 | 56 |
| `ambiguous_intent` | 80 | 80 | 0 |
| `insufficient_evidence` | 80 | 80 | 0 |

## Priority Build Queue

| Priority | Dimension | Name | Current | Target | Gap |
| ---: | --- | --- | ---: | ---: | ---: |
| 1 | action | `answer` | 140 | 200 | 60 |
| 2 | slice | `conflicting_evidence` | 64 | 120 | 56 |
| 3 | slice | `answerable_control` | 76 | 120 | 44 |

## Interpretation

- Candidate-augmented scale reaches the current 500-example planning target, but remains non-paper-facing until human validation and promotion.
- The largest remaining action deficit is `answer` with a gap of `60` examples.
- The next expansion sprint should focus on `conflicting_evidence` (slice gap `56`), then continue down the priority queue.
