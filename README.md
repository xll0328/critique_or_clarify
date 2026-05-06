# EMNLP 2026: Critique or Clarify

Research repo for a project tentatively titled:

**Critique-or-Clarify: When should LLMs answer, ask a follow-up question, challenge a false premise, or abstain?**

The strategic plan lives in [docs/research_master_plan.md](/data/sony/emnlp2026_critique_or_clarify/docs/research_master_plan.md). The short version is that this repo is not trying to be "just another benchmark"; it is trying to formalize **action selection under defective inputs**.

The current action definitions and boundary rules live in [docs/action_ontology.md](/data/sony/emnlp2026_critique_or_clarify/docs/action_ontology.md).

The current EMNLP 2026 sprint package lives in:

- [paper/README.md](/data/sony/emnlp2026_critique_or_clarify/paper/README.md)
- [paper/main.tex](/data/sony/emnlp2026_critique_or_clarify/paper/main.tex)
- [paper/main.pdf](/data/sony/emnlp2026_critique_or_clarify/paper/main.pdf)
- [docs/emnlp2026_oral_best_paper_sprint_plan.md](/data/sony/emnlp2026_critique_or_clarify/docs/emnlp2026_oral_best_paper_sprint_plan.md)
- [docs/emnlp2026_final_push_todo.md](/data/sony/emnlp2026_critique_or_clarify/docs/emnlp2026_final_push_todo.md)
- [docs/emnlp2026_oral_best_paper_gap_closure_plan.md](/data/sony/emnlp2026_critique_or_clarify/docs/emnlp2026_oral_best_paper_gap_closure_plan.md)
- [docs/emnlp2026_final_pdf_human_review_worksheet.md](/data/sony/emnlp2026_critique_or_clarify/docs/emnlp2026_final_pdf_human_review_worksheet.md)
- [docs/emnlp2026_claim_ledger.md](/data/sony/emnlp2026_critique_or_clarify/docs/emnlp2026_claim_ledger.md)
- [docs/emnlp2026_paper_skeleton.md](/data/sony/emnlp2026_critique_or_clarify/docs/emnlp2026_paper_skeleton.md)
- [docs/emnlp2026_introduction_v0.md](/data/sony/emnlp2026_critique_or_clarify/docs/emnlp2026_introduction_v0.md)
- [docs/emnlp2026_data_quality_section_v0.md](/data/sony/emnlp2026_critique_or_clarify/docs/emnlp2026_data_quality_section_v0.md)
- [docs/emnlp2026_boundary_case_table.md](/data/sony/emnlp2026_critique_or_clarify/docs/emnlp2026_boundary_case_table.md)
- [docs/emnlp2026_reviewer_attack_memo.md](/data/sony/emnlp2026_critique_or_clarify/docs/emnlp2026_reviewer_attack_memo.md)
- [docs/emnlp2026_qualitative_examples_shortlist.md](/data/sony/emnlp2026_critique_or_clarify/docs/emnlp2026_qualitative_examples_shortlist.md)
- [docs/emnlp2026_results_section_v0.md](/data/sony/emnlp2026_critique_or_clarify/docs/emnlp2026_results_section_v0.md)
- [docs/emnlp2026_figure_plan.md](/data/sony/emnlp2026_critique_or_clarify/docs/emnlp2026_figure_plan.md)
- [docs/emnlp2026_figure2_audit.md](/data/sony/emnlp2026_critique_or_clarify/docs/emnlp2026_figure2_audit.md)
- [docs/emnlp2026_manuscript_gap_list.md](/data/sony/emnlp2026_critique_or_clarify/docs/emnlp2026_manuscript_gap_list.md)
- [docs/emnlp2026_submission_readiness_checklist.md](/data/sony/emnlp2026_critique_or_clarify/docs/emnlp2026_submission_readiness_checklist.md)
- [docs/emnlp2026_numeric_claim_audit.md](/data/sony/emnlp2026_critique_or_clarify/docs/emnlp2026_numeric_claim_audit.md)

Current submission-freeze status:

- Human validation is complete: `61 / 61` rows in `_assets/human_validation_work_queue.csv`.
- The DeepSeek-R1-Distill-Qwen-7B Day-1 dev and quick+stale metrics are complete.
- The paper builds to a 13-page ACL review PDF.
- The anonymized review package is rebuilt by `scripts/build_review_package.sh`.
- Numeric and claim-scope audits are current for the submission freeze.
- The one-command final gate is:

```bash
./scripts/run_submission_lock_checks.sh
```

The annotation process, first model matrix, and first reporting format live in:

- [docs/annotation_rubric.md](/data/sony/emnlp2026_critique_or_clarify/docs/annotation_rubric.md)
- [docs/adjudication_protocol.md](/data/sony/emnlp2026_critique_or_clarify/docs/adjudication_protocol.md)
- [docs/initial_model_matrix.md](/data/sony/emnlp2026_critique_or_clarify/docs/initial_model_matrix.md)
- [docs/reporting_template.md](/data/sony/emnlp2026_critique_or_clarify/docs/reporting_template.md)

## Why This Project

Current LLM evaluation often assumes the user query is well-formed and the retrieved evidence is internally consistent. Real usage is messier:

- users ask underspecified questions
- prompts contain false or outdated premises
- retrieval returns conflicting passages

The working hypothesis is that strong instruction and reasoning models still over-answer in these settings, and that a lightweight action policy can improve user utility without requiring large-scale continued pretraining.

## Day-0 Goal

Build a minimal but runnable benchmark and evaluation loop that supports four actions:

1. `answer`
2. `ask`
3. `challenge`
4. `abstain`

This repo starts with:

- a unified JSONL schema
- a smoke dataset for quick iteration
- a heuristic baseline
- a local `transformers` inference baseline
- an evaluation script with a utility-style metric

## Quickstart

Create the smoke dataset:

```bash
cd /data/sony/emnlp2026_critique_or_clarify
python scripts/prepare_smoke_data.py
```

Convert the QACC conflicting-context benchmark into the shared JSONL schema:

```bash
python scripts/prepare_qacc.py \
  --input data/raw/external/qa-with-conflicting-context/data/ConflictQA_Dataset.json \
  --output data/processed/qacc_dev.jsonl \
  --split dev
```

Convert PCBench into the shared JSONL schema:

```bash
python scripts/prepare_pcbench.py \
  --variant paired \
  --output data/processed/pcbench_paired.jsonl
```

Create the initial stale-fact seed slice:

```bash
python scripts/prepare_stale_fact_seed.py
```

Run the heuristic baseline:

```bash
python scripts/run_baseline.py \
  --backend heuristic \
  --data data/samples/smoke.jsonl \
  --output outputs/day0/heuristic_predictions.jsonl \
  --eval-json outputs/day0/heuristic_metrics.json
```

Run a local Hugging Face model:

```bash
python scripts/run_baseline.py \
  --backend transformers \
  --model Qwen/Qwen2.5-7B-Instruct \
  --data data/samples/smoke.jsonl \
  --output outputs/day0/qwen25_7b_smoke.jsonl \
  --eval-json outputs/day0/qwen25_7b_smoke_metrics.json \
  --max-new-tokens 180 \
  --temperature 0.0
```

Run one loaded backend across multiple splits when model loading dominates:

```bash
python scripts/run_baseline_batch.py \
  --backend transformers \
  --model /path/to/local/model \
  --job data/processed/day1_quick.jsonl=outputs/day1/model_quick.jsonl=outputs/day1/model_quick_metrics.json \
  --job data/processed/day1_dev.jsonl=outputs/day1/model_dev.jsonl=outputs/day1/model_dev_metrics.json
```

The local inference path defaults to `safetensors` checkpoints. That is intentional: this machine currently has `torch 2.5.1`, and recent `transformers` releases block some `.bin` weight loading paths on older torch versions. Prefer modern checkpoints that publish `safetensors`.

Inspect metrics:

```bash
python scripts/evaluate.py \
  --data data/samples/smoke.jsonl \
  --predictions outputs/day0/heuristic_predictions.jsonl
```

Create a manual audit sheet from a real split:

```bash
python scripts/sample_audit_set.py \
  --data data/processed/qacc_dev.jsonl \
  --output experiments/day0/qacc_dev_audit_sample.tsv \
  --sample-size 40 \
  --seed 42
```

Create a blind adjudication sheet for premise-critique items:

```bash
python scripts/create_adjudication_sheet.py \
  --data data/processed/pcbench_challenge.jsonl \
  --output experiments/day0/pcbench_challenge_adjudication.tsv \
  --sample-size 40 \
  --seed 42
```

Prefetch a model snapshot and verify that weight files actually exist:

```bash
python scripts/prefetch_model.py \
  --repo-id HuggingFaceTB/SmolLM2-135M-Instruct
```

Create the balanced quick diagnostic split used for cheap first-signal runs:

```bash
python scripts/make_day1_dev_subset.py \
  --qacc-size 12 \
  --pcbench-pairs 12 \
  --output data/processed/day1_quick.jsonl \
  --manifest data/processed/day1_quick_manifest.json
```

Create a stale-augmented variant without overwriting the original day-1 split:

```bash
python scripts/make_day1_dev_subset.py \
  --stale-size 7 \
  --output data/processed/day1_dev_plus_stale.jsonl \
  --manifest data/processed/day1_dev_plus_stale_manifest.json
```

Create the larger stale-premise candidate pool and non-overwriting pool splits:

```bash
python scripts/prepare_stale_fact_seed.py \
  --include-expansion \
  --output data/processed/stale_fact_pool.jsonl

python scripts/make_day1_dev_subset.py \
  --stale data/processed/stale_fact_pool.jsonl \
  --stale-size 15 \
  --output data/processed/day1_dev_plus_stale_pool.jsonl \
  --manifest data/processed/day1_dev_plus_stale_pool_manifest.json

python scripts/make_day1_dev_subset.py \
  --qacc-size 12 \
  --pcbench-pairs 12 \
  --stale data/processed/stale_fact_pool.jsonl \
  --stale-size 15 \
  --output data/processed/day1_quick_plus_stale_pool.jsonl \
  --manifest data/processed/day1_quick_plus_stale_pool_manifest.json

./scripts/make_day1_expanded_stale_pool_pilot.sh
```

The expanded stale-pool bundle emits
`experiments/day1/day1_expanded_stale_pool_pilot.md` and
`experiments/day1/tables/day1_expanded_stale_pool_pilot_main.tex`, plus the
action-label audit at
`experiments/day1/day1_expanded_stale_action_label_audit.md` and
`experiments/day1/tables/day1_expanded_stale_action_label_audit_main.tex`, which
separate wrong actions that still mention the corrected update from pure
retrieval misses.

Check and advance the scale/reasoning pipeline without duplicating active jobs:

```bash
./scripts/ensure_scale_reasoning_progress.sh --dry-run
./scripts/ensure_scale_reasoning_progress.sh
```

The ensure script prints `scripts/check_scale_reasoning_status.py`, restarts
missing/stalled model fetches when no matching fetch process is active, and
launches the corresponding day-1 runner only after model files have exact
expected sizes.

Generate the active human-validation work queue:

```bash
./scripts/make_day1_integrity_bundle.sh

python scripts/validate_human_validation_queue.py \
  --queue _assets/human_validation_work_queue.csv
```

Current active work queue: `61 / 61` rows completed after human sign-off. The
CSV is a triage aid and is not a substitute for real human validation: rows with
AI prefill can only be called human-validated after a person records
`human_decision` and, when needed, `human_notes`. The protocol lives in
`docs/human_validation_protocol.md`, and the current progress summary lives in
`_assets/human_validation_work_queue_summary.md`. The combined paper-readiness
view lives in `experiments/day1/day1_integrity_dashboard.md`.
The review packets live under `_assets/human_validation_packets/` and expand
the pending rows into human-readable batches.
The Codex expert-review aid lives at `_assets/codex_expert_validation_review.md`
and `_assets/codex_expert_validation_review.csv`; it is useful for triage but
does not count as completed human validation.
The six-pass pre-review lives under
`_assets/codex_multipass_validation_review/`; use its consensus file for
final human sign-off.
After a human reviewer has checked that review, promote it into the active queue
with:

```bash
python scripts/promote_codex_review_to_human_decisions.py \
  --codex-review _assets/codex_multipass_validation_review/consensus_review.csv \
  --reviewer "<name-or-initials>" \
  --confirm-reviewed
```

Summarize one or more run metrics as a comparison table:

```bash
python scripts/summarize_metrics.py \
  outputs/day1/smollm2_135m_day1_dev_metrics.json \
  outputs/day1/smollm2_135m_day1_quick_compact_metrics.json
```

Sample representative failures from a run:

```bash
python scripts/sample_failures.py \
  --data data/processed/day1_dev.jsonl \
  --predictions outputs/day1/smollm2_135m_day1_dev.jsonl \
  --per-slice 2
```

Use a compact prompt only for weak-model diagnostics:

```bash
python scripts/run_baseline.py \
  --backend transformers \
  --model /data/sony/.cache/huggingface/hub/models--HuggingFaceTB--SmolLM2-135M-Instruct/snapshots/12fd25f77366fa6b3b4b768ec3050bf629380bac \
  --local-files-only \
  --prompt-style compact \
  --data data/processed/day1_quick.jsonl \
  --output outputs/day1/smollm2_135m_day1_quick_compact.jsonl \
  --eval-json outputs/day1/smollm2_135m_day1_quick_compact_metrics.json
```

Resume a flaky mirror download until the expected byte count is reached:

```bash
scripts/resume_download.sh \
  https://hf-mirror.com/Qwen/Qwen2.5-0.5B-Instruct/resolve/main/model.safetensors \
  /data/sony/.cache/huggingface/hub/models--Qwen--Qwen2.5-0.5B-Instruct/blobs/fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe.incomplete \
  988097824
```

Run the full `Qwen2.5-0.5B-Instruct` day-1 pipeline once the mirror is reachable:

```bash
CUDA_VISIBLE_DEVICES=2 scripts/run_qwen25_05b_pipeline.sh
```

## Repo Layout

- `configs/`: run configs and command templates
- `data/samples/`: tiny smoke data committed to git
- `docs/`: project framing and experiment plan
- `experiments/day0/`: manual logs for the first working session
- `experiments/day1/`: baseline reports and early-model notes
- `scripts/`: CLI entrypoints
- `src/coc/`: package code (`coc` = critique-or-clarify)
- `tests/`: lightweight unit tests

## Immediate Next Steps

- Treat `./scripts/run_submission_lock_checks.sh` as the blocking pre-submission gate after every paper-facing change.
- Keep claims scoped to the completed Day-1 evidence: answer-vs-challenge calibration, 61-row human validation, and the local scale/reasoning checkpoint matrix.
- Re-read the first two pages and qualitative examples after any layout change; the current target is a crisp EMNLP oral/best-paper story, not a broader benchmark claim than the evidence supports.
- Convert the responsible NLP checklist into the active venue format when the EMNLP 2026 submission form is available.
