# EMNLP 2026 Numeric Claim Audit

Date: 2026-05-06

Status: current submission-freeze audit after DeepSeek-R1-Distill-Qwen-7B completion, manuscript macro wiring, story-flow lock, responsible-NLP preflight, slice-balanced stress-split scoping, and final lock gate.

## Audit Principle

Paper-facing numbers should come from generated artifacts whenever possible. The main development-scale model numbers are exposed through `paper/tables/day1_scale_reasoning_macros.tex`, quick+stale model numbers are exposed through `paper/tables/day1_quick_stale_macros.tex`, and intervention numbers are exposed through `paper/tables/qwen25_15b_quick_plus_stale_intervention_macros.tex`. These files are copied from `experiments/day1/tables/` by `scripts/sync_paper_assets.sh` and checked by the final submission lock gate.

## Final-Push Result Claim Sync

This pass covers paper-facing and reviewer-facing edits started on 2026-05-06:

- Abstract first-move framing: `paper/sections/00_abstract.tex` now leads with answer quality being incomplete without choosing the right first move. This is a framing claim, not a new numeric result.
- Reviewer-response seed synchronization: `docs/emnlp2026_reviewer_response_seed_memo.md` now preserves the same answer-quality-incomplete and right-first-move frame. This introduces no new metric.
- Oral/best-paper gap closure plan: `docs/emnlp2026_oral_best_paper_gap_closure_plan.md` reuses existing audit-backed quantities: `560` paper-facing examples, `61/61` active validation rows, `10` model rows, `6` figures, `35` bibliography entries, `600` stress split, and the internal `3.1 / 5` readiness estimate from `docs/emnlp2026_oral_best_paper_sprint_plan.md`.

Current result-claim status: no post-2026-05-06 prose edit promotes a new paper-facing numeric result beyond the macro-, metric-, audit-, or lock-backed rows below. Re-run this sync after any Results, Limitations, table, figure, abstract, or reviewer-response edit that introduces or reframes a number.

## Main Manuscript Numbers

| Claim / Number | Manuscript Location | Source Artifact | Status |
| --- | --- | --- | --- |
| Best completed instruct baseline is Qwen2.5-1.5B-Instruct. | Abstract, Introduction, Results | `experiments/day1/tables/day1_scale_reasoning_macros.tex` | macro-backed |
| Qwen2.5-1.5B-Instruct dev action accuracy `0.7667`. | Results | `\DayOneScaleReasoningFrontierActionAcc` | macro-backed |
| Qwen2.5-1.5B-Instruct dev utility `-0.2229`. | Results | `\DayOneScaleReasoningFrontierUtility` | macro-backed |
| Qwen2.5-Coder-7B-Instruct dev action accuracy `0.6000`, utility `-0.2792`. | Results | `\DayOneScaleReasoningQwenCoderSevenBActionAcc`; `\DayOneScaleReasoningQwenCoderSevenBUtility` | macro-backed |
| DeepSeek-R1-Distill-Qwen-7B dev action accuracy `0.3667`. | Abstract, Introduction, Results | `\DayOneScaleReasoningLargestMatchedReasoningActionAcc` | macro-backed |
| DeepSeek-R1-Distill-Qwen-7B dev utility `-0.4313`. | Abstract, Introduction, Results | `\DayOneScaleReasoningLargestMatchedReasoningUtility` | macro-backed |
| DeepSeek-R1-Distill-Qwen-7B dev predicted actions: `69` abstain, `46` answer, `5` challenge out of `120`. | Results | `\DayOneScaleReasoningLargestMatchedReasoningPred*Count`; `\DayOneScaleReasoningLargestMatchedReasoningNumExamples` | macro-backed |
| DeepSeek-R1-Distill-Qwen-7B dev false-premise action accuracy `0.1000`. | Results | `\DayOneScaleReasoningLargestMatchedReasoningFalsePremiseAcc` | macro-backed |
| DeepSeek-R1-Distill-Qwen-7B dev answerable-control action accuracy `0.2000`. | Results | `\DayOneScaleReasoningLargestMatchedReasoningAnswerableAcc` | macro-backed |
| Human validation queue `61/61`. | Benchmark Construction | `_assets/human_validation_work_queue_summary.md`; validator command | validated |
| Day-1 dev split `120` examples with three 40-example slices. | Benchmark Construction | `data/processed/day1_dev_manifest.json` | artifact-backed |
| Quick+stale split `40` examples with four stale-premise cases. | Benchmark Construction | `data/processed/day1_quick_plus_stale_manifest.json` | artifact-backed |
| Decision-first quick+stale utility `-0.1375`, action accuracy `0.8500`, over-answer rate `0.0000`, answer-supported accuracy `0.7500`, and defective-premise accuracy `1.0000`. | Intervention | `paper/tables/qwen25_15b_quick_plus_stale_intervention_macros.tex`; `outputs/day1/interventions/qwen25_15b_day1_quick_plus_stale_decision_first_metrics.json` | macro-backed |
| DeepSeek-R1-Distill-Qwen-7B quick+stale action accuracy `0.4500`, utility `-0.4750`. | Results and dashboard docs | `\DayOneQuickStaleDeepSeekSevenBActionAcc`; `\DayOneQuickStaleDeepSeekSevenBUtility` | macro-backed |
| DeepSeek-R1-Distill-Qwen-7B stale-premise action accuracy `0.2500`, over-answer rate `0.7500`. | Results | `\DayOneQuickStaleDeepSeekSevenBStalePremiseAcc`; `\DayOneQuickStaleDeepSeekSevenBStalePremiseOverAnswer` | macro-backed |
| Full pytest suite passes under the final artifact package lock. | Reproducibility / submission-support docs | `./scripts/run_submission_lock_checks.sh`; `submission_lock_checks_ok` | lock-gate-backed |
| Expanded paper-facing split: `560` unique examples with `answer=200`, `ask=80`, `challenge=200`, `abstain=80`; residual slice gaps `answerable_control=14`, `conflicting_evidence=26`. | Oral sprint planning | `experiments/emnlp2026/expanded_dev_with_answer_topup_coverage_audit.json`; `data/processed/emnlp2026_expanded_dev_with_answer_topup_manifest.json` | generated-audit-backed |
| Slice-balanced 600 stress split now has frontier/high/medium/low API rows with bootstrap intervals: gpt-5-chat-latest, qwen-plus-latest, gpt-4.1-mini, and qwen-turbo all have positive action-accuracy point deltas under full-minus-canonical comparison, but the delta intervals overlap zero; gpt-5-chat-latest adds `Δaction=+0.0047`, `Δutility=-0.0363`. | Results / oral sprint planning | `outputs/day1/aihubmix_gpt5chatlatest_day1_expanded_dev_with_full_answer_topup_metrics.json`; `experiments/day1/tables/day1_full_split_sensitivity.tex`; `docs/emnlp2026_oral_best_paper_quality_audit.json` | generated-audit-backed |
| Candidate pipeline: `160` accepted rows were promoted; canonical paper-facing split is now `560` examples. | Oral sprint planning | `data/candidates/emnlp2026_ask_abstain_seed_candidates_manifest.json`; `_assets/emnlp2026_expansion_candidate_validation_queue.csv`; `experiments/emnlp2026/ask_abstain_candidate_coverage_audit.json`; `scripts/promote_validated_expansion_candidates.py`; `data/processed/emnlp2026_expanded_dev_with_answer_topup.jsonl` | generated-audit-backed |
| Oral/best-paper quality audit marks the artifact not oral-ready: `560` paper-facing examples, `10` main model rows, `6` figures, and `35` bibliography entries. | Oral sprint planning | `docs/emnlp2026_oral_best_paper_quality_audit.json`; `scripts/audit_oral_best_paper_readiness.py` | generated-audit-backed |

## Remaining Numeric Risks

| Risk | Mitigation |
| --- | --- |
| Intervention prose could drift if variants are renamed or if guardrail metrics are regenerated. | Keep `scripts/export_intervention_pilot_tables.py` as the only source for the intervention table and macro file; report utility together with action accuracy, over-answer rate, answer-supported accuracy, and defective-premise accuracy. Keep the external claim scoped to quick+stale unless a stronger controller result lands. |
| Dashboard and process-doc numbers can drift from regenerated artifacts. | Keep submission-facing numbers in generated LaTeX macros or tables; use docs only as trace notes. |
| Human-validation counts are prose-backed rather than macro-backed. | Acceptable for now because the validator is a blocking command; final appendix can include a generated summary table. |
| Page count may change as text is edited. | `paper/README.md` should be updated only after final build checks. |
| Final-push planning docs may repeat audit-backed quantities out of context. | Keep `docs/emnlp2026_oral_best_paper_gap_closure_plan.md`, `docs/emnlp2026_final_push_todo.md`, and reviewer-response seeds tied to this audit whenever they quote `560`, `600`, `61/61`, model rows, figure counts, bibliography counts, or readiness estimates. |

## Required Final Audit Command Block

```bash
./scripts/run_submission_lock_checks.sh
```

The lock gate syncs paper assets, checks scale/reasoning artifacts, requires the complete human-validation queue, runs the full test suite, builds the paper PDF, scans LaTeX logs, builds the anonymous review package, and scans that package for aux/log files or internal paths.
