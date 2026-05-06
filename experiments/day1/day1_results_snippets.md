# Day-1 Results Snippets

These snippets are auto-generated from the completed day-1 development checkpoints and are intentionally claim-disciplined.

## Results Lead

On the current day-1 dev snapshot, `Qwen2.5-1.5B-Instruct` is the strongest open baseline, reaching `action_accuracy=0.7667`, `avg_utility=-0.2229`, and `challenge_precision=0.5909`. The slice pattern is still far from saturated: average action accuracy is lowest on `false_premise` (`0.305`) and highest on `conflicting_evidence` (`0.81`), while the frontier model itself remains weakest on `answerable_control` (`0.35`).

## Scale Paragraph

Within instruct models, the strongest currently observed scale step is `Qwen2.5-0.5B-Instruct -> Qwen2.5-1.5B-Instruct`, which changes action accuracy by `+0.4167`, utility by `+0.2125`, and JSON parse rate by `+0.7416`. The largest slice gain is `False Premise +0.975`, while the largest slice drop is `Answerable -0.075`, so scaling currently helps challenge calibration more than it fixes clean-answer hesitation.

## Reasoning Paragraph

At the largest currently available size-matched contrast (`7B`), `DeepSeek-R1-Distill-Qwen-7B` changes action accuracy by `-0.2333`, utility by `-0.1521`, over-answer rate by `+0.0417`, and JSON parse rate by `-0.8834` relative to `Qwen2.5-Coder-7B-Instruct`. The style difference is therefore measurable at matched scale rather than inferred from cross-size comparisons.

## Intro Preview Sentence

- Across completed open baselines, `Qwen2.5-1.5B-Instruct` currently leads the dev snapshot, while the matched-size instruct-vs-reasoning contrast shows that `false_premise` remains the core calibration bottleneck.

## Results Bridge Sentence

- The strongest current scale step (`Qwen2.5-0.5B-Instruct -> Qwen2.5-1.5B-Instruct`) improves `false_premise` much more than `answerable_control`, indicating that the main remaining difficulty is calibrated challenge rather than mere output formatting.
