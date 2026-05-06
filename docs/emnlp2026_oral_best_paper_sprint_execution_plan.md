# EMNLP 2026 Oral / Best Paper Sprint Execution Plan

Date: 2026-04-28

Status: execution plan for upgrading the current locked Day-1 artifact from a submission-freeze candidate into an oral-level evidence bundle. This plan is intentionally stricter than "can submit"; it targets the evidence depth needed for serious oral/best-paper consideration.

## Hard Assessment

The current artifact is a credible EMNLP-main submission candidate, but not yet an oral/best-paper-grade evidence package.

Locked strengths:

- The paper has a clean central object: next-action selection under defective inputs.
- Human validation is complete for the active queue: `61/61`.
- DeepSeek-R1-Distill-Qwen-7B metrics are complete.
- The manuscript compiles to 13 pages and the full lock gate passes.
- The benchmark/evaluation claim is scoped and no longer depends on pending 7B artifacts.

Main gap:

- The unique evidence bundle is now large enough for size targets, but slice balance and frontier-depth risk remain (notably `answerable_control=106`, `conflicting_evidence=94` in the canonical split).
- The current evidence package has enough visual breadth and citation breadth for the core claim (`6` figures, `35` bibliography entries), and the frontier/high/medium/low API stress rows are present; remaining oral-level risk is mainly confidence estimation, final human PDF sign-off, and claim discipline around canonical-vs-stress split scope.

Generated audit:

- `experiments/day1/benchmark_expansion_coverage_audit.md`
- `experiments/day1/benchmark_expansion_coverage_audit.json`
- Candidate-augmented audit: `experiments/emnlp2026/ask_abstain_candidate_coverage_audit.md`
- Candidate-augmented audit JSON: `experiments/emnlp2026/ask_abstain_candidate_coverage_audit.json`
- Oral/best-paper quality audit: `docs/emnlp2026_oral_best_paper_quality_audit.md`
- Oral/best-paper quality audit JSON: `docs/emnlp2026_oral_best_paper_quality_audit.json`

Current unique audited coverage:

- Unique examples: `560`
- Actions: `answer=200`, `challenge=200`, `ask=80`, `abstain=80`
- Slices: `answerable_control=106`, `false_premise=120`, `stale_premise=80`, `conflicting_evidence=94`, `ambiguous_intent=80`, `insufficient_evidence=80`

Current candidate coverage:

- Candidate file: `data/candidates/emnlp2026_ask_abstain_seed_candidates.jsonl`
- Candidate manifest: `data/candidates/emnlp2026_ask_abstain_seed_candidates_manifest.json`
- Candidate validation queue: `_assets/emnlp2026_expansion_candidate_validation_queue.csv`
- Promotion tool: `scripts/promote_validated_expansion_candidates.py`
- Added paper-facing examples: `160`, with `ask=80`, `abstain=80`, `ambiguous_intent=80`, `insufficient_evidence=80`
- Candidate-augmented unique examples: `560`; total gap to the oral target: `0` (met at canonical split level)

Oral-level planning target:

- Unique examples: at least `500`
- Actions: `answer>=200`, `challenge>=200`, `ask>=80`, `abstain>=80`
- Slices: `answerable_control>=120`, `false_premise>=120`, `stale_premise>=80`, `conflicting_evidence>=120`, `ambiguous_intent>=80`, `insufficient_evidence>=80`

## Execution Rules

1. No paper-facing claim may outrun a generated artifact, metric JSON, macro, validation queue, or lock-gate result.
2. Every new slice must have an explicit boundary rule before examples are added.
3. Every new example enters a validation queue before it becomes paper-facing evidence.
4. Every new result must be regenerated into tables/figures/macros, then pass `./scripts/run_submission_lock_checks.sh`.
5. The intervention remains a calibration probe unless it improves action calibration across models and preserves answer-supported behavior.

## Sprint A: Benchmark Expansion

Goal: make the benchmark hard to dismiss as a small mixed pilot.

Deliverables:

- Add `ambiguous_intent` examples for `ask`.
- Add `insufficient_evidence` / irreconcilable-evidence examples for `abstain`.
- Expand stale-premise examples from `15` unique to at least `80`.
- Expand answerable controls, false premises, and conflicting evidence to at least `120` each.
- Create an expanded split manifest that separates construction source, slice, gold action, and validation status.

Target output:

- `data/processed/emnlp2026_expanded_dev.jsonl`
- `data/processed/emnlp2026_expanded_dev_manifest.json`
- `experiments/emnlp2026/benchmark_expansion_coverage_audit.md`
- `data/candidates/emnlp2026_ask_abstain_seed_candidates.jsonl`
- `_assets/emnlp2026_expansion_candidate_validation_queue.csv`
- `scripts/promote_validated_expansion_candidates.py`
- updated human-validation work queue

Decision gate:

- Do not expand the model matrix until the expanded split has nonzero `ask` and `abstain` coverage and passes split/duplicate/label audits.
- Do not cite candidate counts as benchmark evidence until accepted rows are validated and promoted.

## Sprint B: Validation And Integrity

Goal: make the expanded benchmark reviewer-defensible.

Deliverables:

- Human-validation queue for every new example or sampled high-risk subset, depending on final scale.
- Label-distribution and duplicate-ID audit.
- Near-duplicate prompt audit for stale and false-premise examples.
- Boundary-case memo for `ask` vs `challenge`, `challenge` vs `abstain`, and conflict-but-answerable vs hard abstain.
- Updated responsible-NLP and reproducibility text if data sources change.

Required checks:

```bash
python scripts/audit_benchmark_expansion_coverage.py
python scripts/validate_human_validation_queue.py --queue _assets/human_validation_work_queue.csv --require-complete
./scripts/run_submission_lock_checks.sh
```

## Sprint C: Expanded Model Matrix

Goal: turn a good benchmark into a strong empirical paper.

Minimum matrix:

- Qwen2.5-1.5B-Instruct
- Qwen2.5-Coder-7B-Instruct
- DeepSeek-R1-Distill-Qwen-7B
- at least one stronger non-reasoning instruction checkpoint
- at least one stronger reasoning checkpoint if local resources allow

Robustness checks:

- baseline prompt vs decision-first prompt
- strict JSON parse vs deterministic reparse
- per-slice action accuracy
- over-answer rate on false/stale premises
- over-abstain / over-challenge rate on answerable controls
- bootstrap confidence intervals for headline deltas

Decision gate:

- If reasoning-model weakness disappears under better formatting control, the paper must pivot from "reasoning is weak" to "format and action-binding are the bottleneck."
- If decision-first only works on Qwen2.5-1.5B quick+stale, keep it in analysis rather than selling it as a method.

## Sprint D: Paper Upgrade

Goal: convert larger evidence into a reviewer-readable main paper.

Required manuscript edits:

- Update Table 1 with expanded slice and action coverage.
- Update Table 2 with expanded model matrix.
- Update Figure 2 or add appendix figure for action calibration under expanded split.
- Add one paragraph distinguishing pilot evidence from expanded evidence.
- Update Limitations so it remains honest after expansion.
- Update citation and related-work coverage only if new claims are introduced.

Paper rule:

- The first two pages must still explain the contribution without relying on appendix scale.

## Sprint E: Final Submission Lock

Goal: freeze a clean artifact that is stronger than a "works locally" draft.

Required final gate:

```bash
./scripts/run_submission_lock_checks.sh
```

Final human-only work:

- author list
- affiliation metadata
- reviewer registration
- conflicts of interest
- official responsible-NLP / reproducibility form transfer
- final PDF visual inspection
- submit decision and submit click

## Immediate Commands

Start every sprint cycle with coverage and lock status:

```bash
python scripts/audit_benchmark_expansion_coverage.py
python scripts/check_scale_reasoning_status.py
./scripts/run_submission_lock_checks.sh
```

Then build the next data slice in this order:

1. `ask`: ambiguous intent, missing user-provided details.
2. `abstain`: missing or irreconcilably conflicting evidence.
3. `challenge`: larger stale and false-premise pools.
4. `answer`: matched answerable controls for calibration.

## Current Sprint Decision

The next implementation task remains benchmark and model coverage hardening, not another paper polish pass. The canonical expanded evidence audit is `experiments/emnlp2026/expanded_dev_with_answer_topup_coverage_audit.md`, and the `ask` / `abstain` candidate intake remains at `data/candidates/emnlp2026_ask_abstain_seed_candidates.jsonl`.

Current candidate status:

- `160/160` `ask` / `abstain` candidate rows are signed and completed in `_assets/emnlp2026_expansion_candidate_validation_queue.csv`.
- `181/181` `answer` / `challenge` candidate rows are signed and completed in `_assets/emnlp2026_answer_challenge_candidate_validation_queue.csv`.
- `60/60` `answer` top-up candidate rows are signed and completed in `_assets/emnlp2026_answer_topup_candidate_validation_queue.csv`.
- `40/40` slice-completion top-up candidate rows are signed and completed in `_assets/emnlp2026_answer_topup_slice_completion_candidate_validation_queue.csv`.
- Codex review packets are generated for all candidate queues, and multipass consensus marks all rows as `accept`: `_assets/human_validation_packets/ask_abstain_candidates/consensus_review.csv`, `_assets/human_validation_packets/answer_challenge_candidates/consensus_review.csv`, `_assets/human_validation_packets/answer_topup_candidates/consensus_review.csv`, and `_assets/human_validation_packets/answer_topup_slice_completion_candidates/consensus_review.csv`.
- Combined coverage is tracked in `experiments/emnlp2026/full_candidate_coverage_audit.md` with `500` unique examples (`answer=140`, `challenge=200`, `ask=80`, `abstain=80`).
- A paper-facing top-up variant is written as `data/processed/emnlp2026_expanded_dev_with_answer_topup.jsonl` (`560` rows) with `experiments/emnlp2026/expanded_dev_with_answer_topup_coverage_audit.md`. This closes action-level targets and leaves slice gaps `answerable_control=14`, `conflicting_evidence=26`.
- A slice-balanced follow-on variant is written as `data/processed/emnlp2026_expanded_dev_with_full_answer_topup.jsonl` (`600` rows) with `experiments/emnlp2026/expanded_dev_with_full_answer_topup_coverage_audit.md`. This has `answerable_control=120` and `conflicting_evidence=120`, but `answer` is `240` (above the 200 target), so it is intentionally non-canonical relative to the fixed-500 target schema.
- The 600-row follow-on now has frontier/high/medium/low API stress coverage in `experiments/day1/tables/day1_full_split_sensitivity.tex`: gpt-5-chat-latest, qwen-plus-latest, gpt-4.1-mini, and qwen-turbo are evaluated under matched `decision_first`, `max_tokens=64`, temperature 0 settings. Treat these rows as stress evidence, not as a replacement for the canonical 560 benchmark.
- Promotion artifacts are now written:
  - `data/processed/emnlp2026_expanded_ask_abstain_dev.jsonl` (`319` rows)
  - `data/processed/emnlp2026_expanded_dev.jsonl` (`500` rows)
  - `data/processed/emnlp2026_expanded_dev_with_answer_topup.jsonl` (`560` rows)
  - `experiments/emnlp2026/expanded_dev_coverage_audit.md`
  - `experiments/emnlp2026/expanded_dev_with_answer_topup_coverage_audit.md`
  - `experiments/emnlp2026/expanded_dev_with_full_answer_topup_coverage_audit.md`

The current milestone has a clean, human-signed canonical split at `560` rows (`data/processed/emnlp2026_expanded_dev_with_answer_topup.jsonl`) and an optional slice-balanced `600`-row variant (`data/processed/emnlp2026_expanded_dev_with_full_answer_topup.jsonl`) if you choose to accept additional `answer` examples.
