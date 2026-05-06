# DeepSeek-R1-Qwen1.5B Reparse Audit

## Scope

This note records the metric changes after repairing the fallback parser so it prioritizes explicit final-response cues before scanning literal action words. No model generations were rerun. All numbers below compare the original metric files against the reparsed canonical files.

## Main Deltas

| Run | Old Action Acc. | New Action Acc. | Delta | Old Utility | New Utility | Delta | Old Over-Answer | New Over-Answer |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `day1_quick_useronlyfixed` | `0.3333` | `0.4444` | `+0.1111` | `-0.4514` | `-0.5139` | `-0.0625` | `0.0833` | `0.1667` |
| `day1_quick_useronlyfixed_compact` | `0.2778` | `0.3056` | `+0.0278` | `-0.4097` | `-0.4444` | `-0.0347` | `0.0` | `0.0556` |
| `day1_dev_useronlyfixed` | `0.2917` | `0.3833` | `+0.0916` | `-0.4458` | `-0.5125` | `-0.0667` | `0.0667` | `0.15` |
| `day1_quick_plus_stale_useronlyfixed` | `0.325` | `0.425` | `+0.1` | `-0.4688` | `-0.525` | `-0.0562` | `0.15` | `0.225` |
| `stale_seed_grounded_useronlyfixed` | `0.2857` | `0.2857` | `0.0` | `-0.5714` | `-0.5714` | `0.0` | `0.7143` | `0.7143` |

## Interpretation

- The repaired parser consistently converts many former `abstain` decisions into `answer`, especially on the corrected DeepSeek user-only runs.
- Action accuracy rises because those extra `answer` labels recover many answerable examples.
- Utility falls because the same shift also increases unsafe answering on `false_premise` and `stale_premise`.
- The grounded stale seed run does not change, which is a useful sanity check: its dominant failure mode was already explicit enough for the original parser.

## Canonical Files

- `outputs/day1/deepseek_r1_qwen15b_day1_quick_useronlyfixed_reparsed_metrics.json`
- `outputs/day1/deepseek_r1_qwen15b_day1_quick_useronlyfixed_compact_reparsed_metrics.json`
- `outputs/day1/deepseek_r1_qwen15b_day1_dev_useronlyfixed_reparsed_metrics.json`
- `outputs/day1/deepseek_r1_qwen15b_day1_quick_plus_stale_useronlyfixed_reparsed_metrics.json`
- `outputs/day1/deepseek_r1_qwen15b_stale_seed_grounded_useronlyfixed_reparsed_metrics.json`
