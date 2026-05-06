#!/usr/bin/env bash
set -euo pipefail

cd /data/sony/emnlp2026_critique_or_clarify

if [[ -z "${AIHUBMIX_API_KEY:-}" ]]; then
  echo "Missing AIHUBMIX_API_KEY. Export it first, then rerun." >&2
  echo "Example: export AIHUBMIX_API_KEY=..." >&2
  exit 1
fi

DATA_PATH=data/processed/emnlp2026_expanded_dev_with_answer_topup.jsonl
PROMPT_STYLE=decision_first
MAX_TOKENS=64
TEMPERATURE=0.0

run_model() {
  local model_id=$1
  local stem=$2
  echo "=== running ${model_id} on canonical expanded split ==="
  python scripts/run_aihubmix_baseline.py \
    --model "${model_id}" \
    --data "${DATA_PATH}" \
    --output "outputs/day1/${stem}_day1_expanded_dev_with_answer_topup.jsonl" \
    --eval-json "outputs/day1/${stem}_day1_expanded_dev_with_answer_topup_metrics.json" \
    --prompt-style "${PROMPT_STYLE}" \
    --max-tokens "${MAX_TOKENS}" \
    --temperature "${TEMPERATURE}"
}

run_model "qwen-turbo" "aihubmix_qwenturbo"
run_model "gpt-4o-mini" "aihubmix_gpt4omini"
run_model "gpt-4.1-mini" "aihubmix_gpt41mini"
run_model "qwen-plus-latest" "aihubmix_qwenpluslatest"
run_model "gpt-5-chat-latest" "aihubmix_gpt5chatlatest"

python scripts/compare_runs.py \
  outputs/day1/aihubmix_qwenturbo_day1_expanded_dev_with_answer_topup_metrics.json \
  outputs/day1/aihubmix_gpt4omini_day1_expanded_dev_with_answer_topup_metrics.json \
  outputs/day1/aihubmix_gpt41mini_day1_expanded_dev_with_answer_topup_metrics.json \
  outputs/day1/aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_metrics.json \
  outputs/day1/aihubmix_gpt5chatlatest_day1_expanded_dev_with_answer_topup_metrics.json \
  --title "Day-1 External API Baselines (Expanded Canonical Split)" \
  --confusion-for 1 --confusion-for 2 --confusion-for 3 --confusion-for 4 --confusion-for 5 \
  --output experiments/day1/day1_api_expanded_baseline_comparison.md

python scripts/export_scale_reasoning_bootstrap.py \
  outputs/day1/aihubmix_qwenturbo_day1_expanded_dev_with_answer_topup_metrics.json \
  outputs/day1/aihubmix_gpt4omini_day1_expanded_dev_with_answer_topup_metrics.json \
  outputs/day1/aihubmix_gpt41mini_day1_expanded_dev_with_answer_topup_metrics.json \
  outputs/day1/aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_metrics.json \
  outputs/day1/aihubmix_gpt5chatlatest_day1_expanded_dev_with_answer_topup_metrics.json \
  --output-md experiments/day1/day1_scale_reasoning_api_ci.md \
  --output-dir experiments/day1/tables \
  --prefix day1_scale_reasoning_api_ci

python scripts/plot_emnlp2026_figure6_api_baseline_comparison.py \
  --metric-paths \
  outputs/day1/aihubmix_qwenturbo_day1_expanded_dev_with_answer_topup_metrics.json \
  outputs/day1/aihubmix_gpt4omini_day1_expanded_dev_with_answer_topup_metrics.json \
  outputs/day1/aihubmix_gpt41mini_day1_expanded_dev_with_answer_topup_metrics.json \
  outputs/day1/aihubmix_qwenpluslatest_day1_expanded_dev_with_answer_topup_metrics.json \
  outputs/day1/aihubmix_gpt5chatlatest_day1_expanded_dev_with_answer_topup_metrics.json \
  --output-prefix paper/figures/figure6_api_baseline_comparison

echo "Canonical expanded API baseline refresh complete."
