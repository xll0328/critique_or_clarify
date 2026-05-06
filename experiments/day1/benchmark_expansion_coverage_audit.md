# Benchmark Expansion Coverage Audit

Status: generated coverage audit for upgrading the Day-1 pilot into an oral-level evidence bundle. Targets are planning thresholds, not claims that the data already exists.

## Current Split Coverage

| Split | Rows | Unique IDs | Actions | Slices |
| --- | ---: | ---: | --- | --- |
| `data/processed/day1_dev.jsonl` | 120 | 120 | `answer`=80, `challenge`=40 | `answerable_control`=40, `false_premise`=40, `conflicting_evidence`=40 |
| `data/processed/day1_quick_plus_stale.jsonl` | 40 | 40 | `answer`=24, `challenge`=16 | `answerable_control`=12, `false_premise`=12, `stale_premise`=4, `conflicting_evidence`=12 |
| `data/processed/day1_quick_plus_stale_pool.jsonl` | 51 | 51 | `answer`=24, `challenge`=27 | `answerable_control`=12, `false_premise`=12, `stale_premise`=15, `conflicting_evidence`=12 |
| `data/processed/stale_fact_pool.jsonl` | 15 | 15 | `challenge`=15 | `stale_premise`=15 |

## Combined Unique Coverage

- Input rows across audited splits: `226`
- Unique example IDs: `159`
- Duplicate IDs across audited splits: `67`
- Action coverage: `answer`=92, `challenge`=67
- Slice coverage: `answerable_control`=52, `false_premise`=52, `stale_premise`=15, `conflicting_evidence`=40

## Oral-Level Expansion Gaps

- Unique-example target: `500`; current `159`; gap `341`.

### Action Gaps

| Action | Current | Target | Gap |
| --- | ---: | ---: | ---: |
| `answer` | 92 | 200 | 108 |
| `ask` | 0 | 80 | 80 |
| `challenge` | 67 | 200 | 133 |
| `abstain` | 0 | 80 | 80 |

### Slice Gaps

| Slice | Current | Target | Gap |
| --- | ---: | ---: | ---: |
| `answerable_control` | 52 | 120 | 68 |
| `false_premise` | 52 | 120 | 68 |
| `stale_premise` | 15 | 80 | 65 |
| `conflicting_evidence` | 40 | 120 | 80 |
| `ambiguous_intent` | 0 | 80 | 80 |
| `insufficient_evidence` | 0 | 80 | 80 |

## Priority Build Queue

| Priority | Dimension | Name | Current | Target | Gap |
| ---: | --- | --- | ---: | ---: | ---: |
| 1 | action | `challenge` | 67 | 200 | 133 |
| 2 | action | `answer` | 92 | 200 | 108 |
| 3 | action | `abstain` | 0 | 80 | 80 |
| 4 | action | `ask` | 0 | 80 | 80 |
| 5 | slice | `ambiguous_intent` | 0 | 80 | 80 |
| 6 | slice | `conflicting_evidence` | 40 | 120 | 80 |
| 7 | slice | `insufficient_evidence` | 0 | 80 | 80 |
| 8 | slice | `answerable_control` | 52 | 120 | 68 |
| 9 | slice | `false_premise` | 52 | 120 | 68 |
| 10 | slice | `stale_premise` | 15 | 80 | 65 |

## Interpretation

- The current candidate-augmented bundle is still `341` examples short of the 500-example planning target.
- The largest remaining action deficit is `challenge` with a gap of `133` examples.
- The next expansion sprint should focus on `ambiguous_intent` (slice gap `80`), then continue down the priority queue.
