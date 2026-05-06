# Day-1 Snapshot Takeaways

This note compresses the current day-1 snapshot into the few claims that are already stable enough to guide the paper narrative.

## Claims We Can Already Defend

- The current frontier open baseline is `Qwen2.5-1.5B-Instruct` with `action_accuracy=0.7667`, `avg_utility=-0.2229`, and `challenge_precision=0.5909`.
- The hardest slice in the current snapshot is `false_premise` with mean action accuracy `0.305` across the available runs; the easiest is `conflicting_evidence` at `0.81`.
- The best current reasoning baseline (`DeepSeek-R1-Distill-Qwen-7B`) is still worse than the best current instruct baseline (`Qwen2.5-1.5B-Instruct`) on both utility (`-0.4313` vs. `-0.2229`) and over-answer rate (`0.05` vs. `0.0083`).
- Reasoning has not solved formatting here: the best reasoning checkpoint's `json_parse_rate=0.0583`, compared with `0.8083` for the best current instruct baseline.

## Current Blockers

- Even the strongest current model is still weakest on `answerable_control` (`action_accuracy=0.35`), so the benchmark is not close to saturation.
- The weakest current model by formatting is `DeepSeek-R1-Distill-Qwen-1.5B`, which means part of the story is still instruction compliance rather than pure action policy.
- All planned day-1 scale/reasoning checkpoints are present, so remaining blockers are about robustness, slice coverage, and statistical support rather than missing rows.

## Immediate Writing Use

- Use this note to anchor the first paragraph of the Results section and the final sentence of the Introduction's experimental-preview paragraph.
- The comparison can now be written as a completed day-1 snapshot, while avoiding broader claims until robustness runs and larger stale-premise coverage are complete.
