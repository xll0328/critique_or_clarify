# Paper Draft

This directory contains the current ACL/ARR-style review draft scaffold.

## Build

```bash
cd paper
./build.sh
```

Current build output:

- `main.pdf`
- 13 pages
- No fatal LaTeX errors
- No overfull boxes reported in the latest log scan

## Included Assets

- Figure 1: `figures/figure1_task_schematic.pdf`
- Figure 2: `figures/figure2_action_calibration.pdf`
- Figure 3: `figures/figure3_scale_reasoning.pdf`
- Figure 4: `figures/figure4_coverage_overview.pdf`
- Figure 5: `figures/figure5_boundary_failures.pdf`
- Figure 6: `figures/figure6_api_baseline_comparison.pdf`
- Table 1: `tables/day1_dataset_slice_summary.tex`
- Table 2: `tables/day1_scale_reasoning_main.tex`
- API baseline table: `tables/day1_api_baseline_dev.tex`
- API baseline CI table: `tables/day1_api_baseline_ci_main.tex`
- Table/result macros: `tables/day1_scale_reasoning_macros.tex`
- Quick+stale macros: `tables/day1_quick_stale_macros.tex`
- Per-slice table: `tables/day1_scale_reasoning_per_slice.tex`
- Intervention table: `tables/qwen25_15b_quick_plus_stale_intervention_main.tex`
- Intervention macros: `tables/qwen25_15b_quick_plus_stale_intervention_macros.tex`
- Qualitative examples table: `tables/qualitative_action_examples.tex`
- Bibliography: `references.bib`

## Reproducibility Checks

```bash
cd ..
./scripts/run_submission_lock_checks.sh
```

## Current Gaps

- Related Work has a first verified-citation pass, including selective QA / abstention coverage.
- Abstract, Introduction, Figure 1 caption, and Task Definition now share the same first-move action-decision framing; `tests/test_paper_story_flow.py` locks the running example, unified action-decision record, and Related Work handoff.
- Results and qualitative prose have a first polish pass tying Table 2, Figure 2, and examples to the shared action ontology.
- The intervention section is scoped as an exploratory calibration probe; Section 6 now reports the answer-supported and defective-premise guardrail alongside the `decision_first` gain.
- Responsible NLP and reproducibility preflights are current for this artifact freeze; submission-support drafts live in `../docs/emnlp2026_responsible_nlp_checklist.md` and `../docs/emnlp2026_reproducibility_appendix.md`.
- The clean review package is generated at `../_review_package/critique_or_clarify_emnlp2026_review.zip`.
