# Results Section Draft

Status: prose draft from completed Day-1 metrics. Verify final table/figure numbering after LaTeX assembly.

## Main Results Paragraph

Table X shows that next-action selection remains far from saturated across the completed Day-1 model matrix. The best completed instruct baseline, Qwen2.5-1.5B-Instruct, reaches `0.7667` action accuracy and `-0.2229` utility on `day1_dev`, while Qwen2.5-Coder-7B-Instruct reaches `0.6000` action accuracy and `-0.2792` utility. In contrast, the reasoning-style DeepSeek-R1-Distill-Qwen checkpoints do not improve the action-selection objective under the current prompt protocol: the 1.5B checkpoint reaches `0.3833` action accuracy and `-0.5125` utility, and the 7B checkpoint reaches `0.3667` action accuracy and `-0.4313` utility. These results support a scoped conclusion: explicit reasoning traces are not sufficient to decide whether an assistant should answer, challenge, or abstain under defective inputs.

Figure 2 visualizes the same pattern across overall accuracy, per-slice calibration, and defective-premise over-answering. The key visual result is that the 7B reasoning checkpoint is not simply more conservative in a beneficial way: it remains weak on false-premise interruption while also abstaining heavily on answerable controls.

## Scale / Reasoning Readout

The 7B reasoning checkpoint closes the scale/reasoning gate but does not reverse the Day-1 pattern. On `day1_dev`, DeepSeek-R1-Distill-Qwen-7B predicts `abstain` for 69/120 examples, `answer` for 46/120, and `challenge` for only 5/120. Its false-premise action accuracy is `0.1000`, compared with `0.9750` for Qwen2.5-1.5B-Instruct and `0.4500` for Qwen2.5-Coder-7B-Instruct. At the same time, its answerable-control accuracy is only `0.2000`, indicating that the model is not merely safer on defective inputs; it also fails to answer many clean supported questions.

## Quick+Stale Readout

The quick+stale split exposes the stale-premise failure more directly. DeepSeek-R1-Distill-Qwen-7B reaches `0.4500` action accuracy and `-0.4750` utility, below Qwen2.5-1.5B-Instruct (`0.7750`, `-0.2188`) and Qwen2.5-Coder-7B-Instruct (`0.6250`, `-0.2437`). On the stale-premise slice, the 7B reasoning checkpoint has `0.2500` action accuracy and `0.7500` over-answer rate, meaning that it often answers through an outdated premise instead of challenging it.

## Format-Following Caveat

The DeepSeek runs also show low JSON adherence: `0.0583` on `day1_dev` and `0.0750` on quick+stale after reparse. We treat this as part of the measured assistant behavior under the protocol, not as a hidden preprocessing error, because the benchmark requires an explicit action decision. However, broad claims about reasoning models should remain scoped to this prompt and parsing setup unless future format-control runs show the same pattern.

## Intervention Bridge

The intervention results suggest that action-selection failures are not fixed simply by adding more critique language. On Qwen2.5-1.5B quick+stale, `decision_first` improves utility from `-0.2188` to `-0.1375`, action accuracy from `0.7750` to `0.8500`, and over-answer rate from `0.0500` to `0.0000`. The gain is paired with an answerability guardrail: answer-supported accuracy changes from `0.7083` to `0.7500`, while defective-premise accuracy rises from `0.8750` to `1.0000`. In contrast, `critique_first`, `decision_first_guarded`, and `decision_first_balanced` either over-challenge answerable items or collapse answer-supported accuracy. This supports a narrow method claim: making the action decision explicit can help, but longer or more cautious prompts are not automatically better.

## Evidence Pointers

- Main comparison: `experiments/day1/day1_scale_reasoning_comparison.md`
- Main result figure: `experiments/day1/figures/emnlp2026_figure2_action_calibration.pdf`
- Quick+stale comparison: `experiments/day1/day1_quick_plus_stale_grounded_comparison.md`
- 7B model report: `experiments/day1/deepseek_r1_qwen7b_day1_report.md`
- Intervention table: `experiments/day1/tables/qwen25_15b_quick_plus_stale_intervention_main.tex`
- Dashboard: `experiments/day1/day1_integrity_dashboard.md`
