#!/usr/bin/env bash
set -euo pipefail

cd /data/sony/emnlp2026_critique_or_clarify

if [[ -z "${AIHUBMIX_API_KEY:-}" ]]; then
  echo "Missing AIHUBMIX_API_KEY. Export it first, then rerun." >&2
  echo "Example: export AIHUBMIX_API_KEY=..." >&2
  exit 1
fi

run_model() {
  local model_id=$1
  local stem=$2
  local quick_metrics=$3

  echo "=== running ${model_id} day1_dev ==="
  python scripts/run_aihubmix_baseline.py \
    --model "${model_id}" \
    --data data/processed/day1_dev.jsonl \
    --output "outputs/day1/${stem}_day1_dev.jsonl" \
    --eval-json "outputs/day1/${stem}_day1_dev_metrics.json" \
    --prompt-style decision_first \
    --max-tokens 64 \
    --temperature 0.0

  python scripts/build_day1_model_report.py \
    --dev-metrics "outputs/day1/${stem}_day1_dev_metrics.json" \
    --quick-metrics "${quick_metrics}" \
    --output "experiments/day1/${stem}_day1_report.md" \
    --model-id "${model_id}" \
    --prompt-format "decision_first" \
    --max-new-tokens 64 \
    --temperature 0.0
}

run_model "qwen-turbo" "aihubmix_qwenturbo" "outputs/day1/aihubmix_qwenturbo_day1_quick_metrics.json"
run_model "ernie-4.5-0.3b" "aihubmix_ernie45_03b" "outputs/day1/aihubmix_ernie45_03b_day1_quick_metrics.json"

echo "AIHubMix day1_dev API baseline generation complete."
