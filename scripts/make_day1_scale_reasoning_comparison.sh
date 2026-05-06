#!/usr/bin/env bash
set -euo pipefail

cd /data/sony/emnlp2026_critique_or_clarify

OUTPUT_PATH=experiments/day1/day1_scale_reasoning_comparison.md

declare -a CANDIDATE_PATHS=(
  outputs/day1/qwen25_05b_day1_dev_metrics.json
  outputs/day1/qwen25_15b_day1_dev_metrics.json
  outputs/day1/deepseek_r1_qwen15b_day1_dev_useronlyfixed_reparsed_metrics.json
  outputs/day1/qwen25_coder_7b_day1_dev_metrics.json
  outputs/day1/deepseek_r1_qwen7b_day1_dev_useronlyfixed_reparsed_metrics.json
)
declare -a CANDIDATE_LABELS=(
  Qwen2.5-0.5B-Instruct
  Qwen2.5-1.5B-Instruct
  DeepSeek-R1-Distill-Qwen-1.5B
  Qwen2.5-Coder-7B-Instruct
  DeepSeek-R1-Distill-Qwen-7B
)

declare -a AVAILABLE_PATHS=()
declare -a PENDING_LABELS=()
for ((i = 0; i < ${#CANDIDATE_PATHS[@]}; i++)); do
  path=${CANDIDATE_PATHS[$i]}
  if [[ -f "$path" ]]; then
    AVAILABLE_PATHS+=("$path")
  else
    PENDING_LABELS+=("${CANDIDATE_LABELS[$i]}")
  fi
done

if [[ ${#AVAILABLE_PATHS[@]} -lt 2 ]]; then
  echo "Skipping scale/reasoning report: only ${#AVAILABLE_PATHS[@]} metric file(s) available." >&2
  exit 0
fi

TITLE='Day-1 Scale And Reasoning Snapshot'
if [[ ${#AVAILABLE_PATHS[@]} -eq ${#CANDIDATE_PATHS[@]} ]]; then
  TITLE='Day-1 Scale And Reasoning Comparison'
fi

declare -a CONFUSION_FLAGS=()
if [[ ${#AVAILABLE_PATHS[@]} -eq 2 ]]; then
  CONFUSION_FLAGS+=(--confusion-for 1 --confusion-for 2)
else
  for ((i = 2; i <= ${#AVAILABLE_PATHS[@]}; i++)); do
    CONFUSION_FLAGS+=(--confusion-for "$i")
  done
fi

TMP_REPORT=$(mktemp)
python scripts/compare_runs.py \
  "${AVAILABLE_PATHS[@]}" \
  --title "$TITLE" \
  "${CONFUSION_FLAGS[@]}" > "$TMP_REPORT"

{
  printf '# %s\n\n' "$TITLE"
  if [[ ${#PENDING_LABELS[@]} -gt 0 ]]; then
    echo "This is the current dev-scale snapshot from the checkpoints that have already finished locally. Missing rows will be added automatically when the pending runs complete."
    echo
    printf 'Pending checkpoints: '
    for ((i = 0; i < ${#PENDING_LABELS[@]}; i++)); do
      printf '`%s`' "${PENDING_LABELS[$i]}"
      if [[ $i -lt $((${#PENDING_LABELS[@]} - 1)) ]]; then
        printf ', '
      fi
    done
    printf '.\n\n'
  else
    echo "This report is auto-generated from the current dev metrics for the scale-matched instruct and reasoning checkpoints."
    echo
  fi
  tail -n +3 "$TMP_REPORT"
} > "$OUTPUT_PATH"

rm -f "$TMP_REPORT"

python scripts/plot_day1_scale_reasoning.py \
  "${AVAILABLE_PATHS[@]}" \
  --title "$TITLE" \
  --output-prefix experiments/day1/figures/day1_scale_reasoning > /dev/null

python scripts/export_scale_reasoning_tables.py \
  "${AVAILABLE_PATHS[@]}" \
  --output-dir experiments/day1/tables \
  --prefix day1_scale_reasoning > /dev/null

python scripts/export_scale_reasoning_bootstrap.py \
  "${AVAILABLE_PATHS[@]}" \
  --title "$TITLE Bootstrap Confidence Intervals" \
  --output-md experiments/day1/day1_scale_reasoning_ci.md \
  --output-dir experiments/day1/tables \
  --prefix day1_scale_reasoning_ci > /dev/null

python scripts/export_scale_reasoning_macros.py \
  "${AVAILABLE_PATHS[@]}" \
  --output experiments/day1/tables/day1_scale_reasoning_macros.tex > /dev/null

python scripts/export_scale_reasoning_snippets_tex.py \
  "${AVAILABLE_PATHS[@]}" \
  --output experiments/day1/day1_results_snippets.tex \
  --macros-path experiments/day1/tables/day1_scale_reasoning_macros.tex > /dev/null

python scripts/build_day1_error_bucket_audit.py \
  "${AVAILABLE_PATHS[@]}" \
  --data data/processed/day1_dev.jsonl \
  --output experiments/day1/day1_error_bucket_audit.md > /dev/null

python scripts/build_day1_snapshot_takeaways.py \
  "${AVAILABLE_PATHS[@]}" \
  --output experiments/day1/day1_snapshot_takeaways.md > /dev/null

python scripts/build_day1_pairwise_deltas.py \
  "${AVAILABLE_PATHS[@]}" \
  --output experiments/day1/day1_pairwise_deltas.md > /dev/null

python scripts/build_day1_results_snippets.py \
  "${AVAILABLE_PATHS[@]}" \
  --output experiments/day1/day1_results_snippets.md > /dev/null

echo "Wrote $OUTPUT_PATH using ${#AVAILABLE_PATHS[@]} run(s)." >&2
