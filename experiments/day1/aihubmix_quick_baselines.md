# AIHubMix Quick Baselines (Budget-Oriented)

Date: 2026-04-27

This report summarizes low-cost API runs on `data/processed/day1_quick.jsonl` (36 examples).

| Model | Input Price | Output Price | Utility | Action Acc. | Answer Contains | Over-Answer | JSON Parse |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `qwen-turbo` | `0.046` | `0.092` | `-0.4236` | `0.7222` | `0.5417` | `0.1389` | `0.5` |
| `ernie-4.5-0.3b` | `0.0136` | `0.0544` | `-0.5208` | `0.4722` | `0.1667` | `0.1944` | `0.3889` |

## Notes

- Both runs used `decision_first` prompt style and `max_tokens=64` to control cost.
- `qwen-turbo` is stronger on action accuracy than `ernie-4.5-0.3b` on this split.
- Free-tier models were rate-limited by quota; paid low-cost models remained available.
