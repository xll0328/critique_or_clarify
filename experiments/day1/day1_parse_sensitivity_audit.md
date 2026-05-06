# Day-1 Parse Sensitivity Audit

Status: generated parse/protocol sensitivity audit from saved raw prediction JSONL files.

Interpretation: this audit quantifies how much the current deterministic fallback parser changes metrics relative to a strict JSON-or-abstain rule. It does not remove protocol confounding or justify broader model-family claims.

| Run | N | JSON Parse | Current Acc. | Strict JSON-or-Abstain Acc. | Delta Acc. | Current Utility | Strict Utility | Delta Utility | Fallback Rows | Fallback Acc. | Action Changes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen2.5-0.5B-Instruct | 120 | 0.0667 | 0.35 | 0.0167 | +0.3333 | -0.4354 | -0.4146 | -0.0208 | 112 | 0.3571 | 85 |
| Qwen2.5-1.5B-Instruct | 120 | 0.8083 | 0.7667 | 0.6333 | +0.1334 | -0.2229 | -0.2646 | +0.0417 | 23 | 0.6957 | 23 |
| DeepSeek-R1-Distill-Qwen-1.5B | 120 | 0.0083 | 0.3833 | 0 | +0.3833 | -0.5125 | -0.4229 | -0.0896 | 119 | 0.3866 | 70 |
| Qwen2.5-Coder-7B-Instruct | 120 | 0.9417 | 0.6 | 0.5667 | +0.0333 | -0.2792 | -0.2875 | +0.0083 | 7 | 0.5714 | 6 |
| DeepSeek-R1-Distill-Qwen-7B | 120 | 0.0583 | 0.3667 | 0.05 | +0.3167 | -0.4313 | -0.4229 | -0.0084 | 113 | 0.3363 | 44 |

## Reading Guide

- `Current Acc.` is the metric used by the current deterministic parser.
- `Strict JSON-or-Abstain Acc.` treats any non-JSON or malformed-action output as `abstain`.
- `Fallback Acc.` reports action accuracy only on rows that were not strict JSON under the current parser.
- Large deltas mean the row is protocol-sensitive and should not support broad model-intrinsic claims.

## Artifact Paths

- `Qwen2.5-0.5B-Instruct`: `outputs/day1/qwen25_05b_day1_dev.jsonl` on `data/processed/day1_dev.jsonl`
- `Qwen2.5-1.5B-Instruct`: `outputs/day1/qwen25_15b_day1_dev.jsonl` on `data/processed/day1_dev.jsonl`
- `DeepSeek-R1-Distill-Qwen-1.5B`: `outputs/day1/deepseek_r1_qwen15b_day1_dev_useronlyfixed_reparsed.jsonl` on `data/processed/day1_dev.jsonl`
- `Qwen2.5-Coder-7B-Instruct`: `outputs/day1/qwen25_coder_7b_day1_dev.jsonl` on `data/processed/day1_dev.jsonl`
- `DeepSeek-R1-Distill-Qwen-7B`: `outputs/day1/deepseek_r1_qwen7b_day1_dev_useronlyfixed_reparsed.jsonl` on `data/processed/day1_dev.jsonl`
