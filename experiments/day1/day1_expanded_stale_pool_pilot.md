# Expanded Stale-Premise Pool Pilot

This pilot uses `data/processed/day1_quick_plus_stale_pool.jsonl`. It is not part of the main day-1 comparison table until all reported models are rerun on this same expanded split.

## Split

| Split | N | Answerable | False Premise | Stale Premise | Conflicting Evidence |
| --- | --- | --- | --- | --- | --- |
| day1_quick_plus_stale_pool.jsonl | 51 | 12 | 12 | 15 | 12 |

## Results

| Model | Style | N | Utility | Action Acc. | Over-Answer | JSON Parse | Stale Acc. | Stale Utility | Stale Over-Answer |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen2.5-0.5B-Instruct | instruct | 51 | -0.6324 | 0.3137 | 0.3725 | 0.0196 | 0 | -0.85 | 0.8 |
| Qwen2.5-1.5B-Instruct | instruct | 51 | -0.1863 | 0.7255 | 0.1176 | 0.8627 | 0.7333 | 0.1 | 0.2667 |
| DeepSeek-R1-Distill-Qwen-1.5B | reasoning | 51 | -0.402 | 0.2157 | 0.1373 | 0 | 0.2667 | -0.3 | 0.3333 |

## Bootstrap 95% CIs

| Model | Utility (95% CI) | Action Acc. (95% CI) | Over-Answer (95% CI) | Stale Acc. (95% CI) | Stale Over-Answer (95% CI) |
| --- | --- | --- | --- | --- | --- |
| Qwen2.5-0.5B-Instruct | -0.6324 [-0.7157, -0.5539] | 0.3137 [0.1961, 0.451] | 0.3725 [0.2549, 0.5098] | 0 [0, 0] | 0.8 [0.6, 1] |
| Qwen2.5-1.5B-Instruct | -0.1863 [-0.348, -0.0294] | 0.7255 [0.5882, 0.8431] | 0.1176 [0.0392, 0.2157] | 0.7333 [0.5333, 0.9333] | 0.2667 [0.0667, 0.5333] |
| DeepSeek-R1-Distill-Qwen-1.5B | -0.402 [-0.4951, -0.3088] | 0.2157 [0.1176, 0.3333] | 0.1373 [0.0588, 0.2353] | 0.2667 [0.0667, 0.4667] | 0.3333 [0.1333, 0.6] |

## Qwen Scale Signal

- From Qwen2.5-0.5B to Qwen2.5-1.5B, overall action accuracy changes by `+0.4118` and utility by `+0.4461`.
- On stale premises, action accuracy changes by `+0.7333` and over-answer rate changes by `-0.5333`.
- This makes the expanded stale pool useful as a scale-sensitive diagnostic rather than a saturated hand-written probe.

## Matched 1.5B Contrast

- Overall, DeepSeek-R1-Distill-Qwen-1.5B changes action accuracy by `-0.5098` and utility by `-0.2157` relative to Qwen2.5-1.5B-Instruct.
- On stale premises, DeepSeek-R1-Distill-Qwen-1.5B changes action accuracy by `-0.4666` and over-answer rate by `+0.0666`.
- The expanded pool therefore strengthens the current caution: reasoning traces do not by themselves produce the desired `challenge` action under stale premises.

## Failure Pattern

- The expanded stale pool remains diagnostic: failures persist even when the update passage states the corrected fact directly.
- Qwen2.5-0.5B mostly fails stale premises by direct over-answering, which is the low-capability anchor for the scale story.
- Qwen2.5-1.5B often knows the corrected fact but labels the response as `answer` rather than `challenge`, which isolates action selection from factual retrieval.
- DeepSeek-R1-Distill-Qwen-1.5B mostly fails through fallback-format reasoning, `ask`, or `abstain`, so its weakness is both instruction compliance and action policy.
