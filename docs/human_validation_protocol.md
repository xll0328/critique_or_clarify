# Human Validation Protocol

This protocol defines how to use `_assets/human_validation_work_queue.csv` without confusing AI-assisted triage with human validation.

## Scope

The active queue has two row types:

- `example_gold_label`: verify the gold action label and answer/response for each example in `data/processed/day1_quick_plus_stale_pool.jsonl`.
- Claim rows: verify paper-facing metrics, deltas, split counts, and action-label audit claims derived from the current day-1 artifacts.

## Required Human Fields

Each row starts as `status=pending`. A row becomes human-validated only when a person fills:

- `human_decision`: one of `accept`, `fix`, `reject`, or `needs_second_pass`.
- `human_notes`: required for `fix`, `reject`, and `needs_second_pass`; optional for `accept`.

AI-generated `ai_prefill` is only a pointer to the current artifact state. It is not evidence that the row has been checked by a person.

`_assets/codex_expert_validation_review.csv` is a separate Codex expert-review aid. It can help triage rows before a human pass, but its `codex_expert_decision` values are not `human_decision` values and must not be described as completed human validation.

`_assets/codex_multipass_validation_review/` contains a stronger six-pass pre-review. Its `consensus_review.csv` is the preferred sign-off aid because each row has been checked through ontology, artifact/source, gold-label, arithmetic, failure-audit, and consensus-stress lenses.

After a human reviewer has reviewed and accepted the Codex expert review, promote it into the active queue with:

```bash
python scripts/promote_codex_review_to_human_decisions.py \
  --codex-review _assets/codex_multipass_validation_review/consensus_review.csv \
  --reviewer "<name-or-initials>" \
  --confirm-reviewed
```

This copies `codex_expert_decision` into `human_decision`, records the reviewer sign-off in `human_notes`, and marks rows completed. Existing non-empty human decisions are preserved unless `--overwrite` is provided.

Run `python scripts/validate_human_validation_queue.py --queue _assets/human_validation_work_queue.csv` after editing the CSV. For a submission-blocking check, add `--require-complete`; that mode fails until every row has a valid `human_decision`.

## Review Rules

For `example_gold_label` rows, inspect the prompt, passages if present, gold action, gold answer, and gold response. Confirm whether the best action should be `answer`, `ask`, `challenge`, or `abstain` under `docs/action_ontology.md`.

For stale-premise rows, confirm that the premise is actually outdated and that the corrected fact is supported by the cited source metadata. If the source is inaccessible or ambiguous, mark `needs_second_pass`.

For claim rows, recompute or spot-check the referenced metric/report before accepting. If the report is numerically correct but the wording overclaims, mark `fix` and describe the safer wording.

## Reporting Boundary

The paper may say that rows are human-validated only for rows with a completed human decision. Until then, the queue should be described as an active human-validation work queue, not as completed human annotation.
