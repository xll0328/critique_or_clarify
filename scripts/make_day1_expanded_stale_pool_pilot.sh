#!/usr/bin/env bash
set -euo pipefail

cd /data/sony/emnlp2026_critique_or_clarify

declare -a METRIC_PATHS=(
  outputs/day1/qwen25_05b_day1_quick_plus_stale_pool_metrics.json
  outputs/day1/qwen25_15b_day1_quick_plus_stale_pool_metrics.json
  outputs/day1/deepseek_r1_qwen15b_day1_quick_plus_stale_pool_useronlyfixed_reparsed_metrics.json
)

declare -a PREDICTION_PATHS=(
  outputs/day1/qwen25_05b_day1_quick_plus_stale_pool.jsonl
  outputs/day1/qwen25_15b_day1_quick_plus_stale_pool.jsonl
  outputs/day1/deepseek_r1_qwen15b_day1_quick_plus_stale_pool_useronlyfixed_reparsed.jsonl
)

missing=0
for path in "${METRIC_PATHS[@]}" "${PREDICTION_PATHS[@]}"; do
  if [[ ! -f "$path" ]]; then
    echo "missing_expanded_stale_artifact path=$path" >&2
    missing=1
  fi
done

if [[ "$missing" -ne 0 ]]; then
  echo "Skipping expanded stale-pool pilot refresh until all required artifacts exist." >&2
  exit 0
fi

python scripts/build_stale_pool_pilot_report.py "${METRIC_PATHS[@]}"

python scripts/build_stale_action_label_audit.py \
  "${PREDICTION_PATHS[@]}" \
  --data data/processed/day1_quick_plus_stale_pool.jsonl \
  --output experiments/day1/day1_expanded_stale_action_label_audit.md \
  --tex-output experiments/day1/tables/day1_expanded_stale_action_label_audit_main.tex

echo "Wrote expanded stale-pool pilot reports using ${#METRIC_PATHS[@]} run(s)." >&2
