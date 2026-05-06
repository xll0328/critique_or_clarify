# Day-1 Dataset Slice Summary

This table summarizes the active Day-1 splits used by the EMNLP sprint.

| Split | Total | Slice | Count | Gold Actions | Sources |
| --- | ---: | --- | ---: | --- | --- |
| `emnlp2026_expanded_dev_with_answer_topup.jsonl` | 560 | Answerable control | 106 | answer=106 | PCBench=52, synthetic-expansion-candidate=54 |
| `emnlp2026_expanded_dev_with_answer_topup.jsonl` | 560 | False premise | 120 | challenge=120 | PCBench=52, synthetic-expansion-candidate=68 |
| `emnlp2026_expanded_dev_with_answer_topup.jsonl` | 560 | Stale premise | 80 | challenge=80 | stale-fact-seed=15, synthetic-expansion-candidate=65 |
| `emnlp2026_expanded_dev_with_answer_topup.jsonl` | 560 | Conflicting evidence | 94 | answer=94 | QACC=40, synthetic-expansion-candidate=54 |
| `emnlp2026_expanded_dev_with_answer_topup.jsonl` | 560 | Ambiguous intent | 80 | ask=80 | synthetic-expansion-candidate=80 |
| `emnlp2026_expanded_dev_with_answer_topup.jsonl` | 560 | Insufficient evidence | 80 | abstain=80 | synthetic-expansion-candidate=80 |
| `day1_dev.jsonl` | 120 | Answerable control | 40 | answer=40 | PCBench=40 |
| `day1_dev.jsonl` | 120 | False premise | 40 | challenge=40 | PCBench=40 |
| `day1_dev.jsonl` | 120 | Conflicting evidence | 40 | answer=40 | QACC=40 |
| `day1_quick_plus_stale_pool.jsonl` | 51 | Answerable control | 12 | answer=12 | PCBench=12 |
| `day1_quick_plus_stale_pool.jsonl` | 51 | False premise | 12 | challenge=12 | PCBench=12 |
| `day1_quick_plus_stale_pool.jsonl` | 51 | Stale premise | 15 | challenge=15 | stale-fact-seed=15 |
| `day1_quick_plus_stale_pool.jsonl` | 51 | Conflicting evidence | 12 | answer=12 | QACC=12 |
