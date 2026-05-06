# Codex Multi-Pass Validation Review

This is a six-pass Codex expert pre-review of the active validation queue. It does not fill `human_decision`; it is intended for the human reviewer to inspect and sign off.

Pass-level CSV: `_assets/codex_multipass_validation_review/pass_level_review.csv`
Consensus CSV: `_assets/codex_multipass_validation_review/consensus_review.csv`

## Consensus

- Reviewed rows: `61`.
- Consensus accepted: `61`.
- Consensus follow-up rows: `0`.

| Consensus decision | Rows |
| --- | --- |
| accept | 61 |
| fix | 0 |
| needs_second_pass | 0 |
| reject | 0 |

## Pass Counts

| Pass | Accept | Fix | Needs second pass | Reject |
| --- | --- | --- | --- | --- |
| ontology_boundary | 61 | 0 | 0 | 0 |
| artifact_and_source_presence | 61 | 0 | 0 | 0 |
| gold_answer_or_response_quality | 61 | 0 | 0 | 0 |
| claim_arithmetic_recompute | 61 | 0 | 0 | 0 |
| failure_audit_specificity | 61 | 0 | 0 | 0 |
| consensus_stress_pass | 61 | 0 | 0 | 0 |

## Review Lenses

1. `ontology_boundary`: action label versus slice and action ontology.
2. `artifact_and_source_presence`: local artifacts, passages, and source metadata.
3. `gold_answer_or_response_quality`: non-empty answers and explicit correction responses.
4. `claim_arithmetic_recompute`: regenerated queue rows versus current artifacts.
5. `failure_audit_specificity`: stale/failure audit and metric-specific checks.
6. `consensus_stress_pass`: combined disagreement check over the first five lenses.
