# Qwen2.5-Coder-7B Prompt Ablation

## Question

Can prompt wording recover the 7B model's weak `answerable_control` behavior without destroying `false_premise` calibration?

## Prompt Variants

| Prompt Style | Intent |
| --- | --- |
| `main` | Conservative benchmark prompt. |
| `self_contained` | Tell the model to treat the user query itself as usable evidence when the task is self-contained. |
| `verify_first` | Keep the self-contained bias, but explicitly ask the model to audit provided reasoning before answering local follow-up questions. |

## Quick Results

| Run | Utility | Action Acc. | Answer Contains | Over-Answer | JSON Parse |
| --- | --- | --- | --- | --- | --- |
| `main` | `-0.3264` | `0.5833` | `0.4167` | `0.0278` | `0.9722` |
| `self_contained` | `-0.4583` | `0.8056` | `0.5` | `0.1944` | `0.7778` |
| `verify_first` | `-0.4653` | `0.7778` | `0.5` | `0.1944` | `0.7778` |

## Dev Results

| Run | Utility | Action Acc. | Answer EM | Answer Contains | Over-Answer | JSON Parse |
| --- | --- | --- | --- | --- | --- | --- |
| `main` | `-0.2792` | `0.6` | `0.025` | `0.475` | `0.0083` | `0.9417` |
| `self_contained` | `-0.425` | `0.7917` | `0.0125` | `0.5` | `0.175` | `0.7667` |

`verify_first` was not promoted to a dev run because its quick result was already worse than `self_contained` on utility while offering no compensating gain on `false_premise`.

## Slice-Level Tradeoff

### `main`

- `false_premise`: `action_accuracy=0.45`, `avg_utility=0.0688`, `over_answer_rate=0.025`
- `answerable_control`: `action_accuracy=0.35`, `avg_utility=-0.4062`

### `self_contained`

- `false_premise`: `action_accuracy=0.45`, `avg_utility=-0.3063`, `over_answer_rate=0.525`
- `answerable_control`: `action_accuracy=0.925`, `avg_utility=-0.4688`

### `verify_first` on quick

- `false_premise`: `action_accuracy=0.4167`, `avg_utility=-0.375`, `over_answer_rate=0.5833`
- `answerable_control`: `action_accuracy=0.9167`, `avg_utility=-0.5208`

## Interpretation

1. Prompt wording can strongly change `action_accuracy`, but not always in a trustworthy way.
2. `self_contained` mostly works by collapsing hesitation on answerable controls, pushing the model toward `answer` almost everywhere.
3. That same bias is harmful on `false_premise`: the model stops abstaining or asking and starts directly answering flawed prompts, so utility drops.
4. The benchmark's utility metric is essential. Without it, `self_contained` would look like a major win even though it is materially less safe.
5. `verify_first` does not rescue the tradeoff, so a simple wording tweak is not enough.

## Decision

- Keep `main` as the primary benchmark prompt.
- Keep `self_contained` and `verify_first` as diagnostic ablations only.
- Look for model-side gains next, especially reasoning-oriented baselines, rather than trying to solve the benchmark with a more answer-biased prompt.
