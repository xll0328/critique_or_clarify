#!/usr/bin/env bash
set -euo pipefail

cd /data/sony/emnlp2026_critique_or_clarify

OUTPUT_PATH=experiments/day1/day1_quick_plus_stale_grounded_comparison.md

declare -a CANDIDATE_PATHS=(
  outputs/day1/qwen25_05b_day1_quick_plus_stale_grounded_metrics.json
  outputs/day1/qwen25_15b_day1_quick_plus_stale_grounded_metrics.json
  outputs/day1/qwen25_coder_7b_day1_quick_plus_stale_grounded_metrics.json
  outputs/day1/deepseek_r1_qwen15b_day1_quick_plus_stale_useronlyfixed_reparsed_metrics.json
  outputs/day1/deepseek_r1_qwen7b_day1_quick_plus_stale_useronlyfixed_reparsed_metrics.json
)
declare -a CANDIDATE_LABELS=(
  Qwen2.5-0.5B-Instruct
  Qwen2.5-1.5B-Instruct
  Qwen2.5-Coder-7B-Instruct
  DeepSeek-R1-Distill-Qwen-1.5B
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
  echo "Skipping quick-plus-stale report: only ${#AVAILABLE_PATHS[@]} metric file(s) available." >&2
  exit 0
fi

TITLE='Day-1 Quick Plus Stale Snapshot'
if [[ ${#AVAILABLE_PATHS[@]} -eq ${#CANDIDATE_PATHS[@]} ]]; then
  TITLE='Day-1 Quick Plus Stale Comparison'
fi

declare -a CONFUSION_FLAGS=()
for ((i = 1; i <= ${#AVAILABLE_PATHS[@]}; i++)); do
  CONFUSION_FLAGS+=(--confusion-for "$i")
done

TMP_REPORT=$(mktemp)
python scripts/compare_runs.py \
  "${AVAILABLE_PATHS[@]}" \
  --title "$TITLE" \
  "${CONFUSION_FLAGS[@]}" > "$TMP_REPORT"

{
  printf '# %s\n\n' "$TITLE"
  if [[ ${#PENDING_LABELS[@]} -gt 0 ]]; then
    echo "This is the current four-slice quick snapshot from the checkpoints that have already finished locally. Missing rows will be added automatically when the pending runs complete."
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
    echo "This report is auto-generated from the current four-slice quick metrics for the available instruct and reasoning checkpoints."
    echo
  fi
  tail -n +3 "$TMP_REPORT"
} > "$OUTPUT_PATH"

rm -f "$TMP_REPORT"

python scripts/build_day1_error_bucket_audit.py \
  "${AVAILABLE_PATHS[@]}" \
  --data data/processed/day1_quick_plus_stale.jsonl \
  --title "Day-1 Quick Plus Stale Error Bucket Audit" \
  --intro "This audit condenses the current four-slice quick snapshot into a few failure buckets that are directly useful for the stale-premise narrative." \
  --output experiments/day1/day1_quick_plus_stale_error_bucket_audit.md > /dev/null

python scripts/export_quick_stale_macros.py \
  "${AVAILABLE_PATHS[@]}" \
  --output experiments/day1/tables/day1_quick_stale_macros.tex > /dev/null

echo "Wrote $OUTPUT_PATH using ${#AVAILABLE_PATHS[@]} run(s)." >&2
