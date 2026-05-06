# EMNLP 2026 Claim Ledger

Date: 2026-04-27

This ledger separates paper claims that are already supportable from claims that remain pending or should be avoided. It reflects the current submission-freeze state after the 7B, human-validation, story-flow, responsible-NLP, numeric-audit, and final lock gates.

## Claim Status Legend

- `supported`: can be used in the paper with current artifacts.
- `promising`: pilot evidence is positive, but the claim needs dev-scale confirmation.
- `pending`: likely useful, but requires a running job or artifact not yet complete.
- `weak`: can guide internal thinking, but should not be a main paper claim yet.
- `avoid`: do not claim.

## Core Claims

| ID | Claim | Status | Evidence | Needed Next |
| --- | --- | --- | --- | --- |
| C1 | The project defines a unified action-selection problem over `answer`, `ask`, `challenge`, and `abstain`. | supported | `docs/action_ontology.md`, `docs/annotation_rubric.md`, `docs/reporting_template.md` | Turn into Section 3 formal task definition. |
| C2 | The benchmark is not saturated by current open baselines. | supported | `experiments/day1/day1_results_snippets.md`, `experiments/day1/day1_scale_reasoning_comparison.md`, `paper/sections/05_results.tex` | Keep macro-backed result prose stable. |
| C3 | Current models show slice-specific failures rather than one uniform failure mode. | supported | `experiments/day1/day1_error_bucket_audit.md`, `experiments/day1/day1_snapshot_takeaways.md`, `paper/sections/07_qualitative.tex` | Keep qualitative examples focused on action-boundary failures. |
| C4 | Human validation has completed for the active queue. | supported | `_assets/human_validation_work_queue_summary.md`, `experiments/day1/day1_integrity_dashboard.md`, `docs/emnlp2026_data_quality_section_v0.md`, `paper/sections/03_benchmark.tex` | Keep wording narrow: active labels and paper-facing arithmetic under the ontology. |
| C5 | The grounded stale-premise slice provides a useful defect type beyond false premise and conflicting evidence. | supported | `experiments/day1/day1_expanded_stale_pool_pilot.md`, `experiments/day1/day1_expanded_stale_action_label_audit.md` | Keep wording narrow until all main models are run on expanded stale pool. |
| C6 | The completed reasoning-style checkpoints underperform the strongest instruct baselines on Day-1 action selection. | supported | `experiments/day1/day1_scale_reasoning_comparison.md`, `experiments/day1/day1_quick_plus_stale_grounded_comparison.md`, `experiments/day1/deepseek_r1_qwen7b_day1_report.md` | Phrase as completed local checkpoint evidence, not a universal claim about all reasoning models. |
| C7 | Reasoning-style outputs do not reliably interrupt defective premises and can also over-abstain on clean answerable items. | supported | `experiments/day1/deepseek_r1_qwen7b_day1_report.md`, `experiments/day1/day1_scale_reasoning_comparison.md`, `experiments/day1/day1_quick_plus_stale_grounded_comparison.md` | Use 7B failure examples plus confusion notes; avoid claiming a single uniform failure mode. |
| C8 | DeepSeek-R1-Distill-Qwen-7B closes the Day-1 scale/reasoning gate. | supported | `outputs/day1/deepseek_r1_qwen7b_day1_dev_useronlyfixed_reparsed_metrics.json`, `outputs/day1/deepseek_r1_qwen7b_day1_quick_plus_stale_useronlyfixed_reparsed_metrics.json`, `experiments/day1/day1_integrity_dashboard.md` | Keep the row in main result tables and mention low JSON parse as part of the finding. |
| C9 | A lightweight decision-first intervention can reduce over-answering while preserving answer-supported behavior on quick+stale. | promising, scoped | `experiments/day1/interventions/qwen25_15b_quick_plus_stale_intervention_pilot.md`, `experiments/day1/interventions/qwen25_15b_quick_plus_stale_intervention_summary.md`, `experiments/day1/tables/qwen25_15b_quick_plus_stale_intervention_main.tex`, `experiments/day1/interventions/qwen25_15b_dev_decision_first_intervention.md`, `paper/tables/qwen25_15b_quick_plus_stale_intervention_macros.tex`, `paper/sections/06_intervention.tex` | Keep as an exploratory calibration probe unless a stronger controller lands; keep `critique_first`, `decision_first_guarded`, and `decision_first_balanced` as negative ablations. Do not claim broad assistant helpfulness. |
| C10 | The paper has a plausible oral-level empirical surprise: larger/reasoning-style checkpoints do not automatically improve next-action calibration. | supported as framing, not as award prediction | C6-C9, especially `experiments/day1/day1_scale_reasoning_comparison.md`, `experiments/day1/deepseek_r1_qwen7b_day1_report.md`, `paper/sections/01_introduction.tex`, and `paper/sections/05_results.tex` | Keep the first-two-page story and reviewer-facing scope tests passing. |

## Claims To Avoid

| Claim | Reason |
| --- | --- |
| "Reasoning models are worse than instruct models in general." | Current support is limited to completed local checkpoints and prompt formats. |
| "The benchmark measures general safety." | The task is action calibration under defective inputs, not broad safety. |
| "The intervention improves assistant helpfulness broadly." | Must be bounded to this benchmark unless external validation is added. |
| "Human validation proves the benchmark is objective." | Human validation supports quality; it does not remove all ontology judgment. |

## Paper-Ready Claim Wording

Safe wording now:

> We study next-action selection under defective user inputs, where an assistant must decide whether to answer, ask a clarification, challenge a false or stale premise, or abstain under insufficient evidence.

Safe wording now:

> On the current day-1 development snapshot, models show different calibration failures across false-premise, stale-premise, answerable-control, and conflicting-evidence slices, suggesting that pooled answer accuracy alone hides the central behavior.

Safe wording now:

> Human validation is complete for the active validation queue used by the current day-1 evidence bundle.

Safe wording now:

> In the completed Day-1 local checkpoint matrix, the reasoning-style DeepSeek-R1-Distill-Qwen checkpoints do not improve next-action calibration over the strongest instruct baselines; the 7B reasoning checkpoint reaches `0.3667` dev action accuracy and `-0.4313` dev utility, with low JSON adherence and weak false-premise interruption.

Promising but not final wording:

> On the Qwen2.5-1.5B quick+stale split, a decision-first prompt improves utility and action accuracy while reducing over-answering to zero and preserving answer-supported accuracy; dev-scale evidence is directionally useful but too small for a broad method claim.

Final lock wording:

> The current artifact freeze passes `./scripts/run_submission_lock_checks.sh`, including scale/reasoning checks, complete human validation, the full test suite, paper build, LaTeX log scan, anonymous review-package build, and package hygiene scan.
