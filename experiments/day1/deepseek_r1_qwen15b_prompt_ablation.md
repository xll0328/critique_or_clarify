# DeepSeek-R1-Qwen1.5B Prompt Ablation

## Question

Can a more compact user-only prompt reduce DeepSeek-R1-Distill-Qwen-1.5B's over-answering on defective-premise items without collapsing the rest of the benchmark?

## Prompt Variants

| Prompt Style | Intent |
| --- | --- |
| `main` | Corrected user-only protocol with the full benchmark instructions in the user message. |
| `compact` | Compress the same user-only protocol to reduce formatting overhead and make the action schema more salient. |

## Quick Results

| Run | Utility | Action Acc. | Answer Contains | Over-Answer | JSON Parse |
| --- | --- | --- | --- | --- | --- |
| `main` | `-0.5139` | `0.4444` | `0.2083` | `0.1667` | `0.0` |
| `compact` | `-0.4444` | `0.3056` | `0.2083` | `0.0556` | `0.0` |

## Dev Results

| Run | Utility | Action Acc. | Answer EM | Answer Contains | Over-Answer | JSON Parse |
| --- | --- | --- | --- | --- | --- | --- |
| `main` | `-0.5125` | `0.3833` | `0.0125` | `0.15` | `0.15` | `0.0083` |
| `compact` | `-0.4646` | `0.325` | `0.0125` | `0.225` | `0.0917` | `0.0083` |

For the dev compact run, reparsed metrics are identical to the original metrics, so the shift is behavioral rather than a parser artifact.

## Slice-Level Tradeoff

### Quick `main`

- `false_premise`: `action_accuracy=0.0833`, `avg_utility=-0.5625`, `over_answer_rate=0.5`
- `answerable_control`: `action_accuracy=0.5833`, `avg_utility=-0.5`
- `conflicting_evidence`: `action_accuracy=0.6667`, `avg_utility=-0.4792`

### Quick `compact`

- `false_premise`: `action_accuracy=0.0`, `avg_utility=-0.375`, `over_answer_rate=0.1667`
- `answerable_control`: `action_accuracy=0.1667`, `avg_utility=-0.5`
- `conflicting_evidence`: `action_accuracy=0.75`, `avg_utility=-0.4583`

### Dev `main`

- `false_premise`: `action_accuracy=0.0`, `avg_utility=-0.5875`, `over_answer_rate=0.45`
- `answerable_control`: `action_accuracy=0.5`, `avg_utility=-0.4688`
- `conflicting_evidence`: `action_accuracy=0.65`, `avg_utility=-0.4813`

### Dev `compact`

- `false_premise`: `action_accuracy=0.025`, `avg_utility=-0.4375`, `over_answer_rate=0.275`
- `answerable_control`: `action_accuracy=0.325`, `avg_utility=-0.5`
- `conflicting_evidence`: `action_accuracy=0.625`, `avg_utility=-0.4562`

## Interpretation

1. `compact` helps for the reason we care about most: it makes the model answer less aggressively on defective-premise items.
2. That gain is real on both quick and dev. The strongest signal is the dev `false_premise` over-answer drop from `0.45` to `0.275`.
3. The cost is also real: `compact` makes the model more abstention-prone on clean answerable controls, so action accuracy falls.
4. The utility gain survives that accuracy drop because DeepSeek's biggest error mode is unsafe answering, not excessive caution.
5. JSON adherence does not improve. `compact` is a calibration change, not an output-format fix.
6. Qualitative failures remain consistent with the metric story: on `false_premise`, the model often still explains the flawed solution instead of directly challenging it; on `answerable_control`, it now abstains on many hard PCBench math items that the main prompt at least attempts.

## Decision

- Keep the corrected `main` protocol as the canonical DeepSeek baseline for apples-to-apples reporting.
- Keep `compact` as a meaningful prompt ablation because it improves utility and reduces unsafe answering.
- Do not promote `compact` to the main protocol: the answerability hit is too large, and JSON formatting remains unsolved.
