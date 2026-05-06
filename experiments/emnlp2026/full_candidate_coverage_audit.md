# Benchmark Expansion Coverage Audit

Status: generated coverage audit for upgrading the Day-1 pilot into an oral-level evidence bundle. Targets are planning thresholds, not claims that the data already exists.

## Current Split Coverage

| Split | Rows | Unique IDs | Actions | Slices |
| --- | ---: | ---: | --- | --- |
| `data/processed/day1_dev.jsonl` | 120 | 120 | `answer`=80, `challenge`=40 | `answerable_control`=40, `false_premise`=40, `conflicting_evidence`=40 |
| `data/processed/day1_quick_plus_stale_pool.jsonl` | 51 | 51 | `answer`=24, `challenge`=27 | `answerable_control`=12, `false_premise`=12, `stale_premise`=15, `conflicting_evidence`=12 |
| `data/processed/stale_fact_pool.jsonl` | 15 | 15 | `challenge`=15 | `stale_premise`=15 |
| `data/candidates/emnlp2026_ask_abstain_seed_candidates.jsonl` | 160 | 160 | `ask`=80, `abstain`=80 | `ambiguous_intent`=80, `insufficient_evidence`=80 |
| `data/candidates/emnlp2026_answer_challenge_seed_candidates.jsonl` | 181 | 181 | `answer`=48, `challenge`=133 | `answerable_control`=24, `false_premise`=68, `stale_premise`=65, `conflicting_evidence`=24 |

## Combined Unique Coverage

- Input rows across audited splits: `527`
- Unique example IDs: `500`
- Duplicate IDs across audited splits: `27`
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
