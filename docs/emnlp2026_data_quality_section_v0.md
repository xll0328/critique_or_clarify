# Data Quality And Human Validation Section Draft

Status: manuscript-ready draft text, pending final placement and citation cleanup.

## Short Version For Main Paper

To reduce subjectivity in the action labels, we maintained a human-validation work queue for the active Day-1 evidence bundle. The queue contains 61 checks: 51 example-level gold-label checks and 10 artifact-level checks covering split accounting, headline metrics, scale/style deltas, and stale-premise failure-audit claims. Each row records the source artifact, validation question, AI prefill used only for triage, the human decision, and reviewer notes when needed. The active queue is complete: 61/61 rows have recorded human decisions, and the validation script reports zero invalid decision labels. We use this validation pass as evidence that the current benchmark slice labels and paper-facing arithmetic are internally consistent, while still treating the action ontology as a modeling choice rather than an objective ground truth.

## Longer Version For Appendix

The benchmark combines heterogeneous sources, so we separate automatic artifact generation from human acceptance. We first generate a work queue from the active split, metric files, and prediction files. Example rows ask whether the prompt and evidence support the gold action (`answer`, `ask`, `challenge`, or `abstain`); claim rows ask whether reported split counts, metrics, deltas, and stale-premise failure-audit statements match the current artifacts. The queue also includes Codex-assisted prefill and multi-pass review outputs, but these are treated as triage aids rather than human validation. A row is counted as human-validated only after a human reviewer records a `human_decision`.

For the current Day-1 bundle, the completed queue contains 37 high-priority rows and 24 medium-priority rows. By validation type, it includes 51 example-label checks, 3 metric-claim checks, 2 scale-delta checks, 2 matched-style-delta checks, 2 action-label failure-claim checks, and 1 split-accounting check. The validator passes with `--require-complete`, confirming that all 61 rows are completed and that all non-empty human decisions are drawn from the allowed label set: `accept`, `fix`, `needs_second_pass`, and `reject`.

We use this process to support two narrow claims. First, the current reported split counts, metric summaries, and validation status are reproducible from the checked artifacts. Second, the active labels have received human sign-off under the documented action ontology. We do not claim that the ontology is the only possible one, or that human validation removes all borderline judgment; instead, we report boundary rules, per-slice results, and failure examples so readers can inspect where the task definition matters.

## Evidence Pointers

- Queue: `_assets/human_validation_work_queue.csv`
- Queue summary: `_assets/human_validation_work_queue_summary.md`
- Validation protocol: `docs/human_validation_protocol.md`
- Integrity dashboard: `experiments/day1/day1_integrity_dashboard.md`
- Validation command: `python scripts/validate_human_validation_queue.py --queue _assets/human_validation_work_queue.csv --require-complete`
