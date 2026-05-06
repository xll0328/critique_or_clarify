#!/usr/bin/env bash
set -euo pipefail

cd /data/sony/emnlp2026_critique_or_clarify

MODEL_DIR=/data/sony/model_cache/Qwen2.5-1.5B-Instruct
GPU_ID=${CUDA_VISIBLE_DEVICES:-2}
EXPECTED_BYTES=3087467144

if [[ ! -f "$MODEL_DIR/model.safetensors" ]]; then
  echo "missing_model path=$MODEL_DIR/model.safetensors" >&2
  echo "Run scripts/fetch_qwen25_15b.sh first." >&2
  exit 1
fi

if [[ "$(stat -c '%s' "$MODEL_DIR/model.safetensors")" -ne "$EXPECTED_BYTES" ]]; then
  echo "incomplete_model path=$MODEL_DIR/model.safetensors expected=$EXPECTED_BYTES" >&2
  exit 1
fi

run_split() {
  local split_name=$1
  local data_path=$2
  local fail_per_slice=$3
  local output_stem=$4

  CUDA_VISIBLE_DEVICES="$GPU_ID" python scripts/run_baseline.py \
    --backend transformers \
    --model "$MODEL_DIR" \
    --local-files-only \
    --data "$data_path" \
    --output "outputs/day1/${output_stem}.jsonl" \
    --eval-json "outputs/day1/${output_stem}_metrics.json" \
    --max-new-tokens 140 \
    --temperature 0.0

  python scripts/sample_failures.py \
    --data "$data_path" \
    --predictions "outputs/day1/${output_stem}.jsonl" \
    --per-slice "$fail_per_slice" > "experiments/day1/${output_stem}_failures.txt"
}

run_split "day1_quick" "data/processed/day1_quick.jsonl" 2 "qwen25_15b_day1_quick"
run_split "day1_quick_plus_stale" "data/processed/day1_quick_plus_stale.jsonl" 2 "qwen25_15b_day1_quick_plus_stale_grounded"
run_split "day1_dev" "data/processed/day1_dev.jsonl" 2 "qwen25_15b_day1_dev"

python scripts/summarize_metrics.py \
  outputs/day1/qwen25_15b_day1_quick_metrics.json \
  outputs/day1/qwen25_15b_day1_quick_plus_stale_grounded_metrics.json \
  outputs/day1/qwen25_15b_day1_dev_metrics.json

python scripts/build_day1_model_report.py \
  --quick-metrics outputs/day1/qwen25_15b_day1_quick_metrics.json \
  --dev-metrics outputs/day1/qwen25_15b_day1_dev_metrics.json \
  --dev-failures experiments/day1/qwen25_15b_day1_dev_failures.txt \
  --output experiments/day1/qwen25_15b_day1_report.md \
  --model-id Qwen/Qwen2.5-1.5B-Instruct \
  --local-snapshot "$MODEL_DIR" \
  --gpu "CUDA_VISIBLE_DEVICES=$GPU_ID" \
  --max-new-tokens 140 \
  --temperature 0.0

./scripts/make_day1_quick_plus_stale_comparison.sh
./scripts/make_day1_scale_reasoning_comparison.sh
