# Qwen2.5-1.5B Quick+Stale Intervention Summary

Generated from metric JSON artifacts. Deltas are relative to the first row.

| Variant | Utility | Delta Utility | Action Acc. | Delta Acc. | Over-Answer | Answer-Supported Acc. | Defective-Premise Acc. | JSON Parse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `baseline` | -0.2188 | 0 | 0.775 | 0 | 0.05 | 0.7083 | 0.875 | 0.825 |
| `decision_first` | -0.1375 | +0.0813 | 0.85 | +0.075 | 0 | 0.75 | 1 | 0.85 |
| `critique_first` | -0.2812 | -0.0624 | 0.4 | -0.375 | 0.025 | 0.0416 | 0.9375 | 0.875 |
| `decision_first_guarded` | -0.1812 | +0.0376 | 0.625 | -0.15 | 0 | 0.5 | 0.8125 | 0.875 |
| `decision_first_balanced` | -0.1313 | +0.0875 | 0.375 | -0.4 | 0 | 0 | 0.9375 | 0.8 |

Answer-supported accuracy pools `answerable_control` and `conflicting_evidence`; defective-premise accuracy pools `false_premise` and `stale_premise`.
