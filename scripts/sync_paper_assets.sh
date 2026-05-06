#!/usr/bin/env bash
set -euo pipefail

cd /data/sony/emnlp2026_critique_or_clarify

mkdir -p paper/figures paper/tables paper/styles

cp experiments/day1/figures/emnlp2026_figure1_task_schematic.pdf \
  paper/figures/figure1_task_schematic.pdf
cp experiments/day1/figures/emnlp2026_figure2_action_calibration.pdf \
  paper/figures/figure2_action_calibration.pdf
cp experiments/day1/figures/day1_scale_reasoning.pdf \
  paper/figures/figure3_scale_reasoning.pdf
cp experiments/day1/figures/emnlp2026_figure4_coverage_overview.pdf \
  paper/figures/figure4_coverage_overview.pdf
cp experiments/day1/figures/emnlp2026_figure5_boundary_failures.pdf \
  paper/figures/figure5_boundary_failures.pdf
cp experiments/day1/figures/figure6_api_baseline_comparison.pdf \
  paper/figures/figure6_api_baseline_comparison.pdf

cp experiments/day1/tables/day1_dataset_slice_summary.tex \
  paper/tables/day1_dataset_slice_summary.tex
cp experiments/day1/tables/day1_scale_reasoning_main.tex \
  paper/tables/day1_scale_reasoning_main.tex
cp experiments/day1/tables/day1_scale_reasoning_per_slice.tex \
  paper/tables/day1_scale_reasoning_per_slice.tex
cp experiments/day1/tables/day1_scale_reasoning_ci_main.tex \
  paper/tables/day1_scale_reasoning_ci_main.tex
cp experiments/day1/tables/day1_scale_reasoning_macros.tex \
  paper/tables/day1_scale_reasoning_macros.tex
cp experiments/day1/tables/day1_quick_stale_macros.tex \
  paper/tables/day1_quick_stale_macros.tex
cp experiments/day1/tables/day1_api_baseline_dev.tex \
  paper/tables/day1_api_baseline_dev.tex
cp experiments/day1/tables/day1_api_baseline_ci_main.tex \
  paper/tables/day1_api_baseline_ci_main.tex
cp experiments/day1/tables/day1_full_split_sensitivity.tex \
  paper/tables/day1_full_split_sensitivity.tex
cp experiments/day1/tables/qwen25_15b_quick_plus_stale_intervention_main.tex \
  paper/tables/qwen25_15b_quick_plus_stale_intervention_main.tex
cp experiments/day1/tables/qwen25_15b_quick_plus_stale_intervention_macros.tex \
  paper/tables/qwen25_15b_quick_plus_stale_intervention_macros.tex

if [[ -f /tmp/acl-style-files-emnlp2026-coc/acl.sty ]]; then
  cp /tmp/acl-style-files-emnlp2026-coc/acl.sty paper/styles/acl.sty
  cp /tmp/acl-style-files-emnlp2026-coc/acl_natbib.bst paper/styles/acl_natbib.bst
  cp /tmp/acl-style-files-emnlp2026-coc/anthology.bib.txt paper/styles/anthology.bib.txt
fi

echo "Synced paper assets."
