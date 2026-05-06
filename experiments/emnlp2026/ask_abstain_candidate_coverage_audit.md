# Benchmark Expansion Coverage Audit

Status: generated coverage audit for upgrading the Day-1 pilot into an oral-level evidence bundle. Targets are planning thresholds, not claims that the data already exists.

## Current Split Coverage

| Split | Rows | Unique IDs | Actions | Slices |
| --- | ---: | ---: | --- | --- |
| `data/processed/day1_dev.jsonl` | 120 | 120 | `answer`=80, `challenge`=40 | `answerable_control`=40, `false_premise`=40, `conflicting_evidence`=40 |
| `data/processed/day1_quick_plus_stale_pool.jsonl` | 51 | 51 | `answer`=24, `challenge`=27 | `answerable_control`=12, `false_premise`=12, `stale_premise`=15, `conflicting_evidence`=12 |
| `data/processed/stale_fact_pool.jsonl` | 15 | 15 | `challenge`=15 | `stale_premise`=15 |
| `data/candidates/emnlp2026_ask_abstain_seed_candidates.jsonl` | 160 | 160 | `ask`=80, `abstain`=80 | `ambiguous_intent`=80, `insufficient_evidence`=80 |

## Combined Unique Coverage

- Input rows across audited splits: `346`
- Unique example IDs: `319`
- Duplicate IDs across audited splits: `27`
- Action coverage: `answer`=92, `ask`=80, `challenge`=67, `abstain`=80
- Slice coverage: `answerable_control`=52, `false_premise`=52, `stale_premise`=15, `conflicting_evidence`=40, `ambiguous_intent`=80, `insufficient_evidence`=80

## Oral-Level Expansion Gaps

- Unique-example target: `500`; current `319`; gap `181`.

### Action Gaps

| Action | Current | Target | Gap |
| --- | ---: | ---: | ---: |
| `answer` | 92 | 200 | 108 |
| `ask` | 80 | 80 | 0 |
| `challenge` | 67 | 200 | 133 |
| `abstain` | 80 | 80 | 0 |

### Slice Gaps

| Slice | Current | Target | Gap |
| --- | ---: | ---: | ---: |
| `answerable_control` | 52 | 120 | 68 |
| `false_premise` | 52 | 120 | 68 |
| `stale_premise` | 15 | 80 | 65 |
| `conflicting_evidence` | 40 | 120 | 80 |
| `ambiguous_intent` | 80 | 80 | 0 |
| `insufficient_evidence` | 80 | 80 | 0 |

## Priority Build Queue

| Priority | Dimension | Name | Current | Target | Gap |
| ---: | --- | --- | ---: | ---: | ---: |
| 1 | action | `challenge` | 67 | 200 | 133 |
| 2 | action | `answer` | 92 | 200 | 108 |
| 3 | slice | `conflicting_evidence` | 40 | 120 | 80 |
| 4 | slice | `answerable_control` | 52 | 120 | 68 |
| 5 | slice | `false_premise` | 52 | 120 | 68 |
| 6 | slice | `stale_premise` | 15 | 80 | 65 |

## Interpretation

- The current bundle is strong enough for a locked pilot, but not enough for a best-paper-level benchmark claim.
- The largest scientific deficit is action coverage for `ask` and `abstain`; the largest scale deficit is total unique examples.
- The next data-building sprint should add ambiguous-intent examples for `ask`, insufficient/irreconcilable-evidence examples for `abstain`, and a larger stale-premise pool before expanding the model matrix.
